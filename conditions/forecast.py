"""Pure calculations. No network requests or file writes happen here."""

import math
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("America/Denver")
DAYS = 7
MM_PER_INCH = Decimal("25.4")
YELLOW_INCHES = 2
GREEN_INCHES = 12
BLUEBIRD_CLOUDS_PERCENT = 25
BLUEBIRD_WIND_MPH = 15
BLUEBIRD_POP = 0.20
METERS_PER_SECOND_PER_MPH = 0.44704


class ForecastError(ValueError):
    """A forecast cannot safely produce a complete comparison."""


def number(value, field, maximum=None):
    """Require a finite, nonnegative JSON number (booleans are not numbers)."""
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ForecastError(f"Invalid {field}.")
    if maximum is not None and value > maximum:
        raise ForecastError(f"Invalid {field}.")
    return value


def snowfall_signal(inches):
    if inches >= GREEN_INCHES:
        return "green"
    if inches >= YELLOW_INCHES:
        return "yellow"
    return "neutral"


def read_days(response):
    """Normalize daily records to local dates; reject ambiguous precipitation."""
    if not isinstance(response, dict) or not isinstance(response.get("daily"), list):
        raise ForecastError("Response is missing daily forecasts.")
    days = {}
    for raw in response["daily"]:
        if not isinstance(raw, dict):
            raise ForecastError("Invalid daily record.")
        timestamp = number(raw.get("dt"), "daily timestamp")
        try:
            local_date = datetime.fromtimestamp(timestamp, TIMEZONE).date()
        except (ValueError, OverflowError, OSError):
            raise ForecastError("Invalid daily timestamp.") from None
        if local_date in days:
            raise ForecastError("Duplicate local forecast date.")
        day = {"date": local_date}
        for field in ("snow", "rain"):
            day[field] = number(raw.get(field, 0), field)
        # Missing optional fields disable bluebird detection, not the snow result.
        for field, maximum in (("clouds", 100), ("wind_speed", None), ("pop", 1)):
            value = raw.get(field)
            day[field] = None if value is None else number(value, field, maximum)
        days[local_date] = day
    return days


def is_bluebird(day):
    if day is None or any(day[field] is None for field in ("clouds", "wind_speed", "pop")):
        return False
    return (
        day["clouds"] <= BLUEBIRD_CLOUDS_PERCENT
        and day["wind_speed"] <= BLUEBIRD_WIND_MPH * METERS_PER_SECOND_PER_MPH
        and day["pop"] <= BLUEBIRD_POP
        and day["rain"] == 0
        and day["snow"] == 0
    )


def calculate_location(location, response, today):
    days = read_days(response)
    dates = [today + timedelta(days=offset) for offset in range(DAYS)]
    if any(day not in days for day in dates):
        raise ForecastError("Seven consecutive forecasts starting today are required.")

    # Decimal avoids binary floating-point errors at the exact 2/12-inch boundaries.
    totals = [
        Decimal(str(days[start]["snow"])) + Decimal(str(days[end]["snow"]))
        for start, end in zip(dates, dates[1:])
    ]
    best = max(range(len(totals)), key=lambda index: totals[index])
    inches = totals[best] / MM_PER_INCH
    signal = snowfall_signal(inches)
    following_date = dates[best + 1] + timedelta(days=1)
    bluebird = signal == "green" and is_bluebird(days.get(following_date))
    return {
        "id": location["id"],
        "name": location["name"],
        "state": location["state"],
        "storm_start": dates[best].isoformat(),
        "storm_end": dates[best + 1].isoformat(),
        "snowfall_inches": float(inches),
        "signal": signal,
        "bluebird_date": following_date.isoformat() if bluebird else None,
    }


def build_dataset(locations, fetch, generated_at):
    """Fetch and calculate all locations before returning anything to publish."""
    if generated_at.tzinfo is None:
        raise ForecastError("Generation time must include a timezone.")
    today = generated_at.astimezone(TIMEZONE).date()
    results = []
    for location in locations:
        try:
            results.append(calculate_location(location, fetch(location), today))
        except ForecastError as error:
            raise ForecastError(f"{location['id']}: {error}") from None
    results.sort(key=lambda result: (-result["snowfall_inches"], result["name"].casefold()))
    return {
        "schema_version": 1,
        "generated_at": generated_at.isoformat(),
        "timezone": "America/Denver",
        "evaluation_start": today.isoformat(),
        "evaluation_end": (today + timedelta(days=DAYS - 1)).isoformat(),
        "locations": results,
    }
