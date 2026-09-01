# V5 Implementation Trace — 2026-09-01

## Authority boundary

The user request controls the remote-only operating boundary: GitHub is code/source-of-truth; Google Drive is control/audit index; the local workspace is not a project-data store.

The attached V5 master plan is treated as an implementation specification and Definition of Done. It does not authorize inventing project facts, importing unrelated Drive folders, closing transaction gates or overwriting the V4.1.3 historical release.

## Current baseline inspected

- GitHub repository: https://github.com/susayold/vietgreen-ci-solar-project-finance
- V4.1.3 final commit preserved: 42f2e7216c09a2a0dc4c5500b7239fde4fb97745
- V4.1.3 tag/release: v4.1.3-recruiter-final
- V5 branch: v5-global-real-data
- Drive control document: https://docs.google.com/document/d/1koSgbc1Akic6cVDFD1svmuVN9gSq8qSGUw2obfHYN80/edit
- Drive inspection found no asset-level VietGreen C&I solar source pack. Unrelated finance-risk and private-credit folders were excluded.

## Completed from the V5 plan

- Separate data/public/ from the preserved data/synthetic/.
- Add evidence-class, source-tier and public-data source-register contracts.
- Add portfolio/candidate/entity/assumption schemas.
- Add country benchmark, tax, risk, FX, rate and tariff registers for Vietnam, India, US, EU, Singapore and Australia.
- Add outcome-blind freeze and blocked release manifests.
- Add dynamic portfolio limits (15 minimum / 20 target / 25 maximum) without hard-coded exactly-20 logic.
- Add a failed-closed V5 model interface with project-specific horizon fields.
- Add modular tariff-engine interfaces without default numeric tariffs.
- Add metadata-only source refresh which never saves raw snapshots.
- Add generated recruiter-surface templates with no independent manual economic numbers.
- Add V5 data-validation and monthly source-refresh workflow contracts.

## Public evidence currently accepted

1. IFC Project 46362 — Fourth Partner Energy Private Limited, India. The official ESRS discloses a C&I distributed portfolio, estimated project cost and financing components, but not site-level PPA prices, load, production or debt schedules.
2. IFC Project 49109 — Candi Solar AG, India and South Africa. The official ESRS discloses platform capacity and financing scope, but not country allocation or asset-level project identities.

Both remain candidate/portfolio-level records. They are not frozen V5 project-universe rows for economics.

## Explicit blockers before phases E–O can close

- At least 15 asset-identifiable real project records, with evidence grade at least ACCEPTABLE and no unresolved critical conflict.
- Country-specific tariff, tax, FX and debt inputs refreshed at build time.
- Asset-level capacity, load/generation, PPA mode/price treatment and site/offtaker evidence.
- Outcome-blind selection and release/V5_INPUT_FREEZE_MANIFEST.json with hashes and code SHA.
- Dynamic engine outputs, Excel/reconciliation, reports and website generated from the same V5 manifest.
- G0–G9 validation and claim-boundary checks.

## Do not do

Do not use V4 synthetic rows as V5 real projects. Do not manufacture site names, coordinates, PPA price, actual lender terms, tax applicability, offtaker ratings, generation series or bankable claims.
