# Local verification — October 23, 2026

## Completed

- Python: 17 unittest cases passed, with table-driven subcases for thresholds,
  precipitation validation, all six adjacent pairs, bluebird criteria, and DST.
- JavaScript: 4 Node test cases passed for display precision, dates, 36-hour staleness,
  and rejection of malformed/incomplete published data.
- All twelve coordinates visually checked against USGS topographic maps.
- Browser preview shows twelve sorted cards, a fictional-data banner, date range,
  update time, green/yellow/neutral labels, clearing dates, and provider attribution.
- Desktop layout at 1280 CSS pixels: three columns, twelve cards, no horizontal overflow.
- Narrow mobile frame at approximately 375 usable CSS pixels: one column, twelve cards,
  no horizontal overflow; long location names wrap.
- Both local images load, including the official provider logo.
- A 37-hour-old local dataset shows the stale warning while retaining all twelve results.
- An absent local JSON file shows "Forecast unavailable" with no cards or invented values.
- Fictional preview restored after failure-state checks; production JSON remains absent.
- Missing-key CLI smoke check returns exit code 1 with a clear message and preserves
  a pre-existing output file unchanged.

The in-app browser's viewport override did not change the actual viewport. Responsive
checks therefore used fixed-size iframes in ignored local QA pages, loading the same site
assets. These QA pages are not part of `site/` or deployment.

## Live deployment

- Repository: https://github.com/steve-conditionsset/conditionsset
- Public site: https://conditionsset.pages.dev/
- One-location forecast check passed: https://github.com/steve-conditionsset/conditionsset/actions/runs/40058968026
- Full twelve-location refresh, tests, and deployment passed: https://github.com/steve-conditionsset/conditionsset/actions/runs/40059109531
- Published JSON is schema version 1, contains twelve correctly ranked results and only
  documented public fields, and has `Cache-Control: no-store`.
- All six published frontend assets match local source byte-for-byte. Live cards, date
  range, Mountain-time update timestamp, provider images, and no horizontal overflow checked.
- The example-data banner and stale warning are hidden for the fresh live dataset.
- Weather key was entered directly by the user into GitHub's encrypted secret store;
  it was never copied into local code or chat. Cloudflare credentials are encrypted secrets too.
- Official setup actions were updated after the live runner flagged deprecated versions;
  the successful full deployment uses checkout 7.0.1 and setup-python/setup-node 7.1.0.

Still pending: **three consecutive scheduled daily refreshes**. The first successful
deployment was manually triggered and does not count toward that acceptance criterion.

At the end of local implementation, no accounts had been used and no site was published.
No real weather API request was made during local verification.

The user subsequently created both accounts, the public repository
`steve-conditionsset/conditionsset`, and the Cloudflare Pages Direct Upload project
`conditionsset`. The local `origin` now points at that repository and retains its initial
commit. The implementation and deployment workflows have now been pushed to `main`.
The reviewed Cloudflare Pages Write token and account identifier are saved as encrypted
GitHub Actions secrets; the project-name variable is `conditionsset`. No credential values
are stored in this checkout. The user saved the weather key directly into GitHub's encrypted
`OPENWEATHER_API_KEY` secret. One-location live verification passed in
[run 40058968026](https://github.com/steve-conditionsset/conditionsset/actions/runs/40058968026).
Full deployment passed. Scheduled acceptance remains tracked in the launch checklist.
