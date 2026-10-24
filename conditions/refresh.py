"""Run with: python -m conditions.refresh. Existing output survives any failure."""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from conditions.forecast import ForecastError, build_dataset
from conditions.retrieval import fetch_forecast

ROOT = Path(__file__).resolve().parents[1]


def load_locations(path=ROOT / "config" / "locations.json"):
    locations = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(locations, list) or len(locations) != 12:
        raise ForecastError("Exactly twelve configured locations are required.")
    ids = set()
    for location in locations:
        if not isinstance(location, dict):
            raise ForecastError("Invalid location configuration.")
        for field in ("id", "name", "state", "point"):
            if not isinstance(location.get(field), str) or not location[field].strip():
                raise ForecastError(f"Missing location {field}.")
        if location["state"] not in ("CO", "UT", "WY", "NM"):
            raise ForecastError("Invalid location state.")
        if location["id"] in ids:
            raise ForecastError("Duplicate location identifier.")
        ids.add(location["id"])
        for field, low, high in (("lat", 30, 46), ("lon", -115, -102)):
            value = location.get(field)
            if type(value) not in (int, float) or not low <= value <= high:
                raise ForecastError(f"Invalid Mountain West {field}.")
    return locations


def write_dataset(path, dataset):
    """Replace JSON atomically, only after the complete dataset serializes."""
    content = json.dumps(dataset, indent=2, allow_nan=False) + "\n"
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def refresh(output, fetch, generated_at=None):
    generated_at = generated_at or datetime.now(timezone.utc)
    locations = load_locations()
    dataset = build_dataset(locations, fetch, generated_at)
    write_dataset(output, dataset)
    return dataset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "site" / "data" / "forecast.json")
    parser.add_argument("--verify-one", action="store_true", help="Check Berthoud without writing output.")
    args = parser.parse_args()
    api_key = os.environ.get("OPENWEATHER_API_KEY", "").strip()
    if not api_key:
        print("Refresh failed: set OPENWEATHER_API_KEY; previous forecast unchanged.", file=sys.stderr)
        return 1
    try:
        fetch = lambda location: fetch_forecast(location, api_key)
        if args.verify_one:
            from conditions.forecast import TIMEZONE, calculate_location
            location = load_locations()[0]
            result = calculate_location(location, fetch(location), datetime.now(TIMEZONE).date())
            print(json.dumps(result, indent=2))
        else:
            result = refresh(args.output, fetch)
            print(f"Published JSON for {len(result['locations'])} locations at {result['generated_at']}.")
    except ForecastError as error:
        print(f"Refresh failed: {error} Previous forecast unchanged.", file=sys.stderr)
        return 1
    except (OSError, ValueError):
        # Messages from unknown exceptions/files can contain secret values; keep logs safe.
        print("Refresh failed: forecast unavailable or invalid; previous forecast unchanged.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
