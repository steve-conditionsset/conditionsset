import copy
import io
import json
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from conditions.forecast import (
    ForecastError, TIMEZONE, build_dataset, calculate_location, read_days,
)
from conditions.refresh import load_locations, refresh, write_dataset
from conditions.retrieval import fetch_forecast

FIXTURE = Path(__file__).parent / "fixtures" / "daily.json"
TODAY = date(2026, 10, 23)
GENERATED = datetime(2026, 10, 23, 8, 17, tzinfo=timezone.utc)


class ForecastTests(unittest.TestCase):
    def setUp(self):
        self.response = json.loads(FIXTURE.read_text())
        self.location = load_locations()[0]

    def calculate(self):
        return calculate_location(self.location, self.response, TODAY)

    def set_snow(self, amounts):
        for day, snow in zip(self.response["daily"], amounts):
            day["snow"] = snow

    def test_conversion_today_and_bluebird_boundaries(self):
        result = self.calculate()
        self.assertEqual(result["snowfall_inches"], 12)
        self.assertEqual(result["signal"], "green")
        self.assertEqual(result["storm_start"], "2026-10-23")
        self.assertEqual(result["bluebird_date"], "2026-10-25")

    def test_thresholds_before_rounding(self):
        for mm, signal in [(50.799, "neutral"), (50.8, "yellow"),
                           (304.799, "yellow"), (304.8, "green")]:
            with self.subTest(mm=mm):
                self.set_snow([mm, 0, 0, 0, 0, 0, 0, 0])
                self.assertEqual(self.calculate()["signal"], signal)

    def test_final_pair_and_eighth_day_bluebird(self):
        self.set_snow([0, 0, 0, 0, 0, 152.4, 152.4, 0])
        result = self.calculate()
        self.assertEqual(result["storm_start"], "2026-10-28")
        self.assertEqual(result["storm_end"], "2026-10-29")
        self.assertEqual(result["bluebird_date"], "2026-10-30")
        self.response["daily"].pop()
        self.assertIsNone(self.calculate()["bluebird_date"])

    def test_earliest_tie_and_zero(self):
        self.set_snow([0, 25.4, 0, 0, 0, 0, 0, 0])
        self.assertEqual(self.calculate()["storm_start"], TODAY.isoformat())
        self.set_snow([0] * 8)
        self.assertEqual(self.calculate()["snowfall_inches"], 0)
        self.assertEqual(self.calculate()["signal"], "neutral")

    def test_all_six_pairs(self):
        for index in range(6):
            with self.subTest(index=index):
                snow = [0] * 8
                snow[index:index + 2] = [100, 100]
                self.set_snow(snow)
                self.assertEqual(self.calculate()["storm_start"], (TODAY + timedelta(days=index)).isoformat())

    def test_invalid_precipitation(self):
        for field in ("snow", "rain"):
            for value in (None, -1, "2", True, {}, float("nan"), float("inf")):
                with self.subTest(field=field, value=value):
                    response = copy.deepcopy(self.response)
                    response["daily"][0][field] = value
                    with self.assertRaises(ForecastError):
                        calculate_location(self.location, response, TODAY)

    def test_omitted_precipitation_is_zero(self):
        days = read_days(self.response)
        self.assertEqual(days[TODAY]["rain"], 0)
        self.assertEqual(days[TODAY + timedelta(days=2)]["snow"], 0)

    def test_missing_and_duplicate_dates_rejected(self):
        self.response["daily"].pop(3)
        with self.assertRaises(ForecastError):
            self.calculate()
        self.response["daily"].append(self.response["daily"][0])
        with self.assertRaises(ForecastError):
            self.calculate()

    def test_bluebird_missing_or_above_each_boundary(self):
        clearing = self.response["daily"][2]
        for field, value in (("clouds", 25.01), ("wind_speed", 6.706),
                             ("pop", 0.201), ("rain", 0.001), ("snow", 0.001),
                             ("clouds", None), ("wind_speed", None), ("pop", None)):
            with self.subTest(field=field, value=value):
                original = copy.deepcopy(clearing)
                clearing[field] = value
                self.assertIsNone(self.calculate()["bluebird_date"])
                clearing.clear()
                clearing.update(original)

    def test_blue_bird_only_for_green(self):
        self.set_snow([25.4, 25.4, 0, 0, 0, 0, 0, 0])
        self.assertIsNone(self.calculate()["bluebird_date"])

    def test_timezone_and_daylight_saving(self):
        for start in (date(2026, 3, 7), date(2026, 10, 31)):
            with self.subTest(start=start):
                for index, day in enumerate(self.response["daily"]):
                    local = start + timedelta(days=index)
                    day["dt"] = datetime(local.year, local.month, local.day, 12, tzinfo=TIMEZONE).timestamp()
                result = calculate_location(self.location, self.response, start)
                self.assertEqual(result["storm_end"], (start + timedelta(days=1)).isoformat())
        # UTC October 24 still belongs to October 23 in Denver.
        response = json.loads(FIXTURE.read_text())
        result = build_dataset([self.location], lambda _: response,
                               datetime(2026, 10, 24, 1, tzinfo=timezone.utc))
        self.assertEqual(result["evaluation_start"], "2026-10-23")

    def test_sort_and_twelve_locations(self):
        locations = load_locations()
        dataset = build_dataset(locations, lambda _: self.response, GENERATED)
        self.assertEqual(len(dataset["locations"]), 12)
        self.assertEqual([x["name"] for x in dataset["locations"]], sorted(x["name"] for x in locations))
        def fetch(location):
            response = copy.deepcopy(self.response)
            if location["id"] == "wolf-creek-pass":
                response["daily"][0]["snow"] = 500
            return response
        self.assertEqual(build_dataset(locations, fetch, GENERATED)["locations"][0]["id"], "wolf-creek-pass")

    def test_failed_refresh_preserves_previous_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "forecast.json"
            output.write_text('{"previous": true}')
            def fetch(location):
                if location["id"] == "ski-apache":
                    raise ForecastError("Service unavailable")
                return self.response
            with self.assertRaises(ForecastError):
                refresh(output, fetch, GENERATED)
            self.assertEqual(output.read_text(), '{"previous": true}')
            dataset = refresh(output, lambda _: self.response, GENERATED)
            self.assertEqual(json.loads(output.read_text()), dataset)

    def test_atomic_write_preserves_previous_on_replace_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "forecast.json"
            output.write_text("previous")
            with patch("pathlib.Path.replace", side_effect=OSError("disk error")):
                with self.assertRaises(OSError):
                    write_dataset(output, {"new": True})
            self.assertEqual(output.read_text(), "previous")
            self.assertEqual(list(output.parent.glob("*.tmp")), [])


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.location = load_locations()[0]

    @patch("conditions.retrieval.time.sleep")
    @patch("conditions.retrieval.urlopen")
    def test_transient_failures_bounded_and_secret_not_in_error(self, open_url, sleep):
        open_url.side_effect = URLError("https://example.test/?appid=secret")
        with self.assertRaises(ForecastError) as caught:
            fetch_forecast(self.location, "secret")
        self.assertNotIn("secret", str(caught.exception))
        self.assertEqual(open_url.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    @patch("conditions.retrieval.urlopen")
    def test_authentication_fails_without_retry(self, open_url):
        open_url.side_effect = HTTPError("https://example.test/?appid=secret", 401, "bad", {}, None)
        with self.assertRaises(ForecastError) as caught:
            fetch_forecast(self.location, "secret")
        self.assertNotIn("secret", str(caught.exception))
        self.assertEqual(open_url.call_count, 1)

    @patch("conditions.retrieval.time.sleep")
    @patch("conditions.retrieval.urlopen")
    def test_retry_then_success_and_daily_only_metric_request(self, open_url, sleep):
        stream = io.BytesIO(FIXTURE.read_bytes())
        open_url.side_effect = [HTTPError("url", 503, "unavailable", {}, None), stream]
        self.assertIn("daily", fetch_forecast(self.location, "secret"))
        request = open_url.call_args.args[0]
        self.assertIn("units=metric", request.full_url)
        self.assertIn("current%2Cminutely%2Chourly%2Calerts", request.full_url)
        self.assertEqual(open_url.call_args.kwargs["timeout"], 20)


if __name__ == "__main__":
    unittest.main()
