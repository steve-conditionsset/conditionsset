# Launch acceptance

Implementation and automated tests can be verified locally. Live API and deployment
checks require existing account access. Do not mark these complete from fixture tests.

- [x] Confirm map placement of the twelve representative points (USGS topo review, October 23, 2026).
- [x] Run the **Verify one live forecast** workflow with the existing key: https://github.com/steve-conditionsset/conditionsset/actions/runs/40058968026 (success).
- [x] Review OpenWeather's public attribution instructions; required provider text, link, and official logo are included.
- [x] GitHub repository created: https://github.com/steve-conditionsset/conditionsset
- [x] Push the prepared source to the repository (`main`, implementation commit `0e7e7e0`).
- [x] Configure encrypted `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` Actions secrets.
- [x] Configure Actions variable `CLOUDFLARE_PROJECT_NAME` as `conditionsset`.
- [x] Save the existing weather key as encrypted `OPENWEATHER_API_KEY` Actions secret (entered directly by the user).
- [x] Create Cloudflare Pages Direct Upload project `conditionsset` (first deployment will target `main`).
- [x] Complete manual live refresh/deployment: https://github.com/steve-conditionsset/conditionsset/actions/runs/40059109531
- [x] Verify public site: https://conditionsset.pages.dev/
- [x] Check twelve cards, ranking, dates, last-update time, and clearing flags against JSON (current results are neutral; clearing rules also covered by fixtures).
- [x] Confirm production has no fictional-preview banner; JSON contains only documented public fields, and published assets match credential-free local source.
- [x] Confirm mobile/desktop presentation and stale warning behavior locally; verify identical frontend assets are published and the live page renders without overflow.
- [ ] Three consecutive **scheduled** daily runs succeed without intervention:

| Scheduled run | Date | Workflow URL | Published update time checked |
| --- | --- | --- | --- |
| 1 | Pending | Pending | Pending |
| 2 | Pending | Pending | Pending |
| 3 | Pending | Pending | Pending |

After these checks, Phase 1 meets the agreed reliability criterion. No additional monitoring
service or membership/payment infrastructure is required.
