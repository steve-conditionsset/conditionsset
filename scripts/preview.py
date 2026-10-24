"""Build a clearly labeled fictional preview; never used by the deploy workflow.

Run: python -m scripts.preview
Then: python -m http.server 8765 --bind 127.0.0.1 --directory .local/preview
"""

import copy
import json
import shutil
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from conditions.forecast import TIMEZONE, build_dataset
from conditions.refresh import ROOT, load_locations, write_dataset


def main():
    generated_at = datetime.now(timezone.utc)
    today = generated_at.astimezone(TIMEZONE).date()
    fixture = json.loads((ROOT / "tests" / "fixtures" / "daily.json").read_text())
    amounts = {"wolf-creek-pass": 16, "jackson-hole": 12, "taos": 5,
               "little-cottonwood": 8.3, "snowy-range": 2, "ski-santa-fe": 1.9,
               "steamboat": 0, "berthoud-pass": 3.4, "crested-butte": 6.2,
               "powder-mountain": 4.1, "la-sal-mountains": 0.05, "ski-apache": 0.4}
    locations = load_locations()

    def fictional_forecast(location):
        response = copy.deepcopy(fixture)
        offset = next(i for i, place in enumerate(locations) if place["id"] == location["id"]) % 5
        for index, day in enumerate(response["daily"]):
            date = today + timedelta(days=index)
            day["dt"] = datetime(date.year, date.month, date.day, 12, tzinfo=TIMEZONE).timestamp()
            amount_mm = Decimal(str(amounts[location["id"]])) * Decimal("25.4") / 2
            day["snow"] = float(amount_mm) if index in (offset, offset + 1) else 0
            day["clouds"] = 10
            day["wind_speed"] = 3
            day["pop"] = 0
        return response

    dataset = build_dataset(locations, fictional_forecast, generated_at)
    dataset["example"] = True
    destination = ROOT / ".local" / "preview"
    shutil.copytree(ROOT / "site", destination, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("data"))
    write_dataset(destination / "data" / "forecast.json", dataset)
    print(f"Fictional preview written to {destination}. No weather API requests made.")


if __name__ == "__main__":
    main()
