# Launch acceptance

Implementation and automated tests can be verified locally. Live API and deployment
checks require existing account access. Do not mark these complete from fixture tests.

- [x] Confirm map placement of the twelve representative points (USGS topo review, October 23, 2026).
- [ ] Run `python -m conditions.refresh --verify-one` with the existing One Call 3.0 key.
- [ ] Confirm the account's public-display license; provider attribution is already included.
- [ ] Create/push the GitHub repository and configure Actions secrets/variable.
- [ ] Create Cloudflare Pages Direct Upload project with production branch `main`.
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
