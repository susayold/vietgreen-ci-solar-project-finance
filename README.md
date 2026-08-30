# Vietnam C&I Solar Portfolio — Lender-Informed, Audit-Ready

Educational / simulated project-finance case for a multi-offtaker Vietnam C&I rooftop-solar portfolio.

Model date: 2026-08-31
Master seed: 260831
Core release: 1.0.0-candidate
Storage: GitHub + Google Drive only; no project data is written to the user's local workspace.

## Snapshot
- Eligible shortlist: 12
- Selected portfolio: 9 projects / 11.1 MWp
- Sponsor equity used: 148.68953 BVND of 150.00 BVND
- Provisional pooled debt: 87.18547 BVND
- Aggregate portfolio DSCR: 1.476303x
- Base sponsor NPV: -109.81579 BVND; conditional repricing is required

## Core implemented
- 20-project synthetic pipeline with hard gates.
- PVOUT-aware P50/P90 and shortlist-only 8,760 architecture.
- Three-sided PPA frontier, CAPEX/OPEX/tax/WC/CFADS.
- Debt sizing/sculpting, LLCR/PLCR, DSRA/waterfall, VND/USD FX paths.
- Standalone vs pooled financing, concentration, value-density allocation.
- External validation, red-team scenarios, release manifests and remote QA.

## Claim boundary
This is not lender-approved, bank-certified, formally audited, legally compliant or a bankable P90 transaction model. Financing terms, credit grades, PPA clauses, covenant thresholds and security terms are simulated/assumption unless directly evidenced.

## Remote execution
GitHub Actions runs the Python model and tests on an ephemeral hosted runner. Declared outputs are uploaded as workflow artifacts; no project data is persisted to the user's device.

Repository: https://github.com/susayold/vietgreen-ci-solar-project-finance
