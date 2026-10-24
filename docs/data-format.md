# Public forecast JSON — version 1

The refresh writes `site/data/forecast.json`, which is intentionally ignored by Git.
The frontend fetches it from the same origin. There is no public dynamic API.
Changes to field meaning or removal require a schema version change.

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | integer | `1` |
| `generated_at` | string | ISO 8601 timestamp with offset; retrieval run start time |
| `timezone` | string | `America/Denver` |
| `evaluation_start` | string | Local run date, `YYYY-MM-DD` |
| `evaluation_end` | string | Start plus six calendar days |
| `locations` | array | Exactly twelve results, sorted by unrounded snow descending, then name |

Every location has:

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Unique stable configuration identifier |
| `name` | string | Display name |
| `state` | string | `CO`, `UT`, `WY`, or `NM` |
| `storm_start` | string | First selected day, `YYYY-MM-DD` |
| `storm_end` | string | Following selected day, `YYYY-MM-DD` |
| `snowfall_inches` | number | Unrounded two-day millimeter total divided by 25.4 |
| `signal` | string | `green`, `yellow`, or `neutral`, assigned before rounding |
| `bluebird_date` | string or null | Day immediately after selected green window, if it passes clearing rules |

All-zero forecasts still select the first pair for consistency; the frontend hides those
storm dates. A zero total is distinct from missing data, which rejects the refresh.
The frontend displays a neutral 1.9-inch total as `1.9″` and "No notable snow".
Rounding can display `12″` on a yellow result just below 12 inches; classification always
uses the actual unrounded total, not its text representation.

Only the developer preview adds `example: true` to the root object, enabling a prominent
fictional-data notice. Production output never includes it. The demo script writes solely
to `.local/preview` and is never part of the deployment workflow.

No coordinates, credentials, API responses, user data, or scoring beyond the agreed rules
are included in the public dataset.
