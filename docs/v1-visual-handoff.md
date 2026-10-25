# Conditions Set V1 visual handoff

Implemented locally October 25, 2026. No deployment performed.

## Visible changes

- Small text-only Conditions Set header, followed by the dataset's actual forecast
  period and last successful update in Mountain time. Removed the hero and tagline.
- Requested dark palette, muted green-gray cards, locally hosted IBM Plex Sans and
  IBM Plex Mono with `font-display: swap` and system fallbacks.
- User-supplied Board.jpg copied unchanged to `site/assets/usgs-topo.jpg`. An
  independent, noninteractive pseudo-element renders it at 6% opacity. CSS custom
  properties control the asset, opacity, repeat, and scale. Initial settings use
  `no-repeat` and `cover` to avoid repeating the supplied image's white outer frame.
  The solid background remains usable if the image cannot load.
- Four columns above 1100px, two from 581–1100px, one at 580px and below.
  Each sorted state has its own grid, so partial rows stay within their state.
- Area and state share the top line with an accessible signal dot at the right;
  dominant bold snowfall and compact date/2-DAY SNOW metadata follow. Displayed
  rank numbers removed. Clearing indicators retained when supplied by the data.
- Ranking explanation and signal legend follow the complete collection. The four
  supplied paragraphs are reproduced exactly; the entire safety paragraph is bold.
  Existing OpenWeather attribution text, link, logo, dimensions, and alt text retained
  immediately afterward.

No framework, build step, production dependency, or additional network request for
weather was introduced. Changes are confined to presentation, static assets, one
date formatting test, and documentation. Python calculations, fetching, publication,
sorting, thresholds, precision, coverage, and clearing rules remain unchanged.

## Forecast window and specification differences

`conditions/forecast.py` defines `DAYS = 7`, constructs offsets 0–6 from the current
Mountain date, and selects the largest of six consecutive two-day pairs. Published
`evaluation_start` is today and `evaluation_end` is today + 6. The displayed period
uses those published fields. This matches the supplied “today and the next six days”
prose. The earlier “seven full days excluding today” description conflicts with the
implementation and remains a product decision; no forecast-window change was made.

The application explicitly uses green >=12 inches, yellow >=2 and <12 inches, and
neutral <2 inches. It has no red signal or existing red color. The legend therefore
preserves neutral instead of inventing a red category. Signals still use unrounded
values, so a yellow card can display a rounded 12 inches.

The supplied texture's original USGS provenance is unverified: no source map, URL,
or credit metadata was supplied. This is recorded in `site/assets/CREDITS.md` along
with font source and license information.

## Verification

- 17 existing Python unit tests passed using the bundled Python runtime.
- 12 JavaScript tests passed, including unchanged sorting, precision, stale timing,
  and dataset validation tests plus month/year boundary display cases.
- Browser reviewed using clearly labeled fictional preview data at 1440×1000,
  800×1000, 390×844, and 320×800. Confirmed 4/2/1 columns, no horizontal overflow,
  readable long names, zero and trace totals, partial state rows, and clearing flags.
- DOM inspection confirmed 12 labeled signal dots, all four exact paragraphs,
  disclaimer weight 700, loaded fonts, and independent texture opacity 0.06.
- Missing-data route showed “Forecast period unavailable” and “Forecast unavailable”
  without fabricating an update timestamp. A stale fixture retained all 12 cards,
  its original successful timestamp, and the overdue notice.
- Visually reviewed the explanation and unchanged attribution on narrow mobile.
- `git diff --check` passed. Local review screenshots are saved in ignored
  `.local/v1-desktop.png` and `.local/v1-mobile.png`.

Preview: run `python -m scripts.preview`, then serve `.local/preview` on localhost.
The system `python` alias is unavailable on this machine; verification used
`C:/Users/steph/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.
