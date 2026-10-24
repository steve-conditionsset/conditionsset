# Launch acceptance

Implementation and automated tests can be verified locally. Live API and deployment
checks require existing account access. Do not mark these complete from fixture tests.

- [x] Confirm map placement of the twelve representative points (USGS topo review, October 23, 2026).
- [ ] Run the **Verify one live forecast** workflow (or `python -m conditions.refresh --verify-one`) with the existing One Call 3.0 key.
- [ ] Confirm the account's public-display license; provider attribution is already included.
- [x] GitHub repository created: https://github.com/steve-conditionsset/conditionsset
- [ ] Push the prepared source to the repository.
- [x] Configure encrypted `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` Actions secrets.
- [x] Configure Actions variable `CLOUDFLARE_PROJECT_NAME` as `conditionsset`.
- [ ] Save the existing weather key as encrypted `OPENWEATHER_API_KEY` Actions secret.
- [x] Create Cloudflare Pages Direct Upload project `conditionsset` (first deployment will target `main`).
- [ ] Complete one manual live refresh/deployment; record its workflow and Pages URLs.
- [ ] Check twelve cards, ranking, dates, last-update time, and clearing flags against JSON.
- [ ] Confirm production has no fictional-preview banner and no secrets in published files.
- [ ] Confirm mobile/desktop presentation and stale warning behavior.
- [ ] Three consecutive **scheduled** daily runs succeed without intervention:

| Scheduled run | Date | Workflow URL | Published update time checked |
| --- | --- | --- | --- |
| 1 | Pending | Pending | Pending |
| 2 | Pending | Pending | Pending |
| 3 | Pending | Pending | Pending |

After these checks, Phase 1 meets the agreed reliability criterion. No additional monitoring
service or membership/payment infrastructure is required.
