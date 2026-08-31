# Website QA report

Generated after the V4 recruiter website build.

- Data build: PASS (`python scripts/build_website_data.py`)
- Data contract: PASS (10 JSON contracts, four selected projects, release `V4-FINAL-2026-08-31`)
- Stale V3 blocker: PASS
- JavaScript syntax: PASS (`node --check website/app.js`)
- Current terms boundary: 0 / 20 positive Equity NPV, `NO_DEPLOYMENT`
- Negotiated case: 19 positive Equity NPV rows; four selected IDs `VG-005`, `VG-010`, `VG-011`, `VG-012`
- Model QA carried through: 2,055 formula cells, 0 formula errors, 240 / 240 Excel–Python reconciliation, 35 / 35 Final DoD
- Transaction boundary: evidence `OPEN`, bankable transaction `FALSE`, eight external gates open

The GitHub Pages workflow repeats the build, validation and stale-claim checks before deployment.
