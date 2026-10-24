# Conditions Set

A small winter forecast comparison: twelve fixed mountain areas, their snowiest
two-day windows, and a separate post-storm clearing indicator. Python retrieves
OpenWeather One Call 3.0 once daily; static HTML/CSS/JavaScript displays saved JSON.
There is no database, application server, frontend framework, or browser weather key.

Live website: https://conditionsset.pages.dev/

The first live verification and deployment passed on October 23, 2026. Daily updates
are enabled; three consecutive scheduled runs are still required for launch acceptance.

## Run locally

Use Python 3.12 or newer. Install the Windows timezone dependency if needed:

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
node --test tests/test_display.mjs
```

Node 22 is used for presentation tests and the deployment CLI, not the website runtime.
Linux runners already include the timezone database and need no Python packages.

For a **fictional, clearly labeled preview**, without an API key:

```powershell
python -m scripts.preview
python -m http.server 8765 --bind 127.0.0.1 --directory .local/preview
```

Open <http://127.0.0.1:8765>. Preview data is confined to ignored `.local/preview`;
the production workflow never invokes the preview script.

For real weather, set `OPENWEATHER_API_KEY` in your terminal environment using your
existing key. Never put its value in code, chat, a command argument, or a committed file.
The program does not automatically load `.env` files.

```powershell
python -m conditions.refresh --verify-one
python -m conditions.refresh
python -m http.server 8765 --bind 127.0.0.1 --directory site
```

First verify the one-location output. A full run makes twelve sequential requests,
with up to three attempts per location for transient errors (20-second timeout;
2-second then 4-second backoff). Invalid credentials stop immediately. Errors do not
print request URLs or response bodies. Raw responses are not saved.

## Rules

- Today and the following six days in `America/Denver`, including DST changes.
- Greatest of six adjacent two-day snow totals; earliest pair wins ties.
- Snow inches = OpenWeather `daily.snow` millimeters / 25.4. No snow ratios.
- Green at 12 inches; yellow at 2 to under 12; neutral below 2. Never red.
- Thresholds precede display rounding; backend decimal arithmetic protects exact boundaries.
- Green storms can have a separate clearing flag on the following calendar day:
  clouds ≤25%, wind ≤15 mph, precipitation probability ≤20%, no forecast rain/snow.
  Metric wind is compared with 6.7056 m/s. The eighth daily entry may supply clearing data.
- Missing rain/snow means zero in an otherwise valid daily record. Null or invalid
  precipitation fails the refresh. Missing/null optional bluebird fields disable the flag;
  supplied invalid optional values fail validation.
- All twelve forecasts must succeed before JSON is atomically replaced. Production
  deployment runs only after tests and a successful refresh.
- The site shows retrieval time and a stale warning after 36 hours, without suppressing
  location results. A refresh or deployment failure leaves the previous Pages deployment live.

Configuration: `config/locations.json`. Calculation rules: `conditions/forecast.py`.
Retrieval: `conditions/retrieval.py`. Orchestration: `conditions/refresh.py`.
Presentation: `site/`. Public data contract: [docs/data-format.md](docs/data-format.md).

## First deployment: GitHub Actions + Cloudflare Pages

Repository: https://github.com/steve-conditionsset/conditionsset

The Cloudflare Pages Direct Upload project is named `conditionsset`. Credentials
are not bundled with this checkout. The steps below also document rebuilding the setup.

1. Use the GitHub repository `steve-conditionsset/conditionsset`, with default branch `main`.
   Use a private repository if you prefer; confirm your Actions allowance before enabling
   scheduled runs. Push this source, excluding the reference workbook and local state.
2. In Cloudflare, use the **Pages Direct Upload** project named `conditionsset`, with
   production branch `main`. Use **Workers & Pages → Create application → Pages →
   Direct Upload**, rather than creating a Worker or Git-integrated project.
3. Add GitHub repository Actions secrets:
   - `OPENWEATHER_API_KEY`: the existing One Call 3.0 key.
   - `CLOUDFLARE_API_TOKEN`: a token with Cloudflare Pages Edit for the intended account.
   - `CLOUDFLARE_ACCOUNT_ID`: that account's identifier.
4. Add repository Actions variable `CLOUDFLARE_PROJECT_NAME` = `conditionsset`
   (or the actual available project name).
5. Run **Verify one live forecast** from the Actions tab first. This makes one Berthoud
   Pass request, validates it, and prints only its calculated result; it does not publish.
   Then run **Daily forecast and publish** manually. It runs tests,
   retrieves and validates all locations, then uses Wrangler to upload `site/`.
   This creates the first populated deployment; inspect the workflow's returned Pages URL.
6. Verify cards, dates, clearing flags, last-update time, attribution, and mobile layout.
   Keep the default `pages.dev` address; no domain or analytics setup is needed.

The schedule is `17 8 * * *` UTC, approximately 02:17 MDT / 01:17 MST. GitHub schedules
are best-effort and can be delayed. They run from the default branch. Scheduled workflows
in public repositories can be disabled after 60 days without repository activity;
GitHub's normal workflow status is sufficient for this MVP, without another monitoring service.

The deployment workflow does not run on pull requests, commit forecast updates, or deploy
fictional previews. A separate check workflow tests pushes and pull requests without secrets.
Weather API access happens only within the Python refresh job, never in site visitors' browsers.

## Data source and limitations

Daily forecasts, snowfall units, omitted-phenomenon fields, and metric wind are documented
in [OpenWeather One Call 3.0](https://openweathermap.org/api/one-call-3).
The agreed product treats `daily.snow` directly as forecast snowfall converted to inches.
Daily totals include elapsed hours today; they are not precise rolling 48-hour windows.

The footer includes the required provider text, link, and unmodified official master logo,
downloaded from the logo library linked in the [OpenWeather attribution FAQ](https://openweathermap.org/faq#license).
Confirm the existing account's particular public-display license before launch; subscription
details cannot be established without account access.

Coordinates represent broader mountain areas. See [docs/locations.md](docs/locations.md)
for map references and verification notes. Do not infer elevation corrections or ski access
from a coordinate. The existing `Weather Dashboard Calc.xlsx` was inspected read-only and
is preserved outside version control; its older coordinate list is not the winter configuration.
No Make.com scenario was provided or changed.

Conditions Set identifies weather opportunities, not skiing safety or terrain suitability.
Avalanche conditions, snowpack stability, terrain selection, resort operations, and access
are outside the product.

## Launch acceptance and what follows

Local fixture tests and a preview do not establish a live launch. Phase 1 is accepted only
after live verification and **three consecutive scheduled daily refreshes** without manual
intervention. Record the workflow links/dates in [docs/launch-checklist.md](docs/launch-checklist.md).

After a useful expanded winter product, validate a small paid offering through real purchases.
Summer integration and extensive personalization are not prerequisites. No authentication,
payment, subscription, dynamic forecast, mapping, or activity infrastructure is prebuilt here.
User-defined locations may require an architectural change later.
