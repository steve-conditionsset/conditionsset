"""OpenWeather daily retrieval with bounded retries and credential-safe errors."""

import json
import time
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from conditions.forecast import ForecastError

ENDPOINT = "https://api.openweathermap.org/data/3.0/onecall"
TIMEOUT_SECONDS = 20
ATTEMPTS = 3


def fetch_forecast(location, api_key):
    query = urlencode({
        "lat": location["lat"],
        "lon": location["lon"],
        "exclude": "current,minutely,hourly,alerts",
        "units": "metric",
        "appid": api_key,
    })
    request = Request(f"{ENDPOINT}?{query}", headers={"User-Agent": "ConditionsSet/1.0"})
    for attempt in range(ATTEMPTS):
        try:
            with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return json.load(response)
        except HTTPError as error:
            code = error.code
            error.close()
            if code in (401, 403):
                raise ForecastError("OpenWeather authentication/subscription failed.") from None
            if code != 429 and not 500 <= code <= 599:
                raise ForecastError(f"OpenWeather rejected the request (HTTP {code}).") from None
        except (URLError, TimeoutError, OSError, HTTPException):
            # Never print exception text: it can contain the credential-bearing URL.
            pass
        except (ValueError, UnicodeError):
            raise ForecastError("OpenWeather returned invalid JSON.") from None
        if attempt < ATTEMPTS - 1:
            time.sleep(2 ** (attempt + 1))
    raise ForecastError("OpenWeather unavailable after three attempts.")
