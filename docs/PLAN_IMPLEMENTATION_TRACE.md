# Master-plan implementation trace

## A. Evidence and regulatory lineage

Implemented: material inputs carry source/assumption IDs through the lineage matrix; legal tariff windows, current billed references and model-only price components are separate; tax and foreign-borrowing rules are registered with effective dates and recheck flags; the remote source-fetch log records the 2026-08-31 refresh without storing raw snapshots locally.

Status: PASS WITH BILLING WATCH. Decision 963 legal windows are mapped, but billed implementation and final transaction applicability remain external gates.

Latest benchmark refresh: IRENA 2025 official utility-scale solar PV cost context was added to the external benchmark register; it is comparator-only and does not set the C&I rooftop tariff or CAPEX.

## B. Synthetic data, hidden truth and reproducibility

Implemented: locked master seed 260831; hashes for all synthetic inputs including the 240-row construction curve; deterministic generation; cross-field DQ; hidden-truth cases isolated to aggregate labels; no customer data or raw hidden truth in the public repository.

Status: PASS. 20/20 DQ, 5/5 hidden-truth classifications and locked hashes.

## C. Energy, PPA and 8,760

Implemented: 20 in-memory 8,760 load/solar profiles, P50/P90 flow-through, P90 <= P50, separate loss and load matching, legal tariff midpoint mapping, current billed-reference mapping, three-sided PPA frontier, explicit empty-zone action and remote artifact export.

Status: PASS for synthetic mechanics; external PPA, site, technical-yield and billed-tariff evidence remain open.

Remote-format note: the plan names Parquet for hourly deliverables, but the remote-only implementation publishes compressed CSV.GZ streams in the GitHub Actions artifact with an explicit schema/index. No hourly stream is committed to the public repository or desktop workspace.

## D. CAPEX, construction, tax, VAT, WC and terminal

Implemented: six-category bottom-up CAPEX; 12-month construction spend curve; monthly gross/net/VAT/IDC schedule; capitalised IDC proxy at 8.5%; reconciled total uses and depreciable basis; tax/loss-carryforward proxy; DSO working capital; major maintenance; zero-terminal branch; explicit year-zero full-equity no-debt pass.

Status: PASS for internal mechanics; replace the synthetic curve/rate and obtain tax/accounting certification before bankable release.

## E. Debt and reserves

Implemented: separate sizing/sculpting/covenant/lock-up DSCR concepts; LLCR and PLCR with registered discount rates; leverage cap; backward sizing/forward rebuild; debt close; DSRA/reserve waterfall; pooled debt feedback.

Status: PASS for automated controls; lender terms, security, reserves and hedging remain unconfirmed.

## F. FX and portfolio

Implemented: period-by-period FX crawl and one-off shocks, break-even FX, common-factor downside, concentration outputs, hard gates before ranking, budget and concentration caps, and pairwise-swap improvement pass.

Status: PASS for synthetic mechanics; transaction hedge and correlation evidence remain open.

## G. Allocation and IC

Current candidate: 11 selected projects; 13.10 MWp; equity 138.143294 BVND; endogenous pooled debt 152.457008 BVND; pooled DSCR 1.30x; base sponsor NPV -66.202345 BVND.

Status: PASS WITH NEGATIVE BASE SPONSOR NPV; recommendation is conditional and the IC memo is not an approval.

## H. Validation and release

Latest remote run: 33354033001; 20/20 DQ; 20/20 dynamic remote QA; 31/31 workbook checks; 7/7 tests; 13/13 mechanical release controls plus 1 candidate-manifest warning; 240 construction schedule rows; remote 8,760 streams remain artifact-only with local_storage NONE.

## I. Recruiter-facing communication

Implemented: aggregate-only recruiter-facing landing page and workbook model preview under `website/`, linked from README; only frozen aggregate metrics and remote links are shown.

Status: PASS for communication scope; no raw 8,760 streams, hidden truth, credentials or project-sensitive data are embedded.

Live deployment verified at https://susayold.github.io/vietgreen-ci-solar-project-finance/ via Pages workflow 33354984280 / job 99375460077; website boundary check PASS.

## J. Open gates

Independent final model review; billed tariff confirmation; transaction-specific tax and foreign-borrowing advice; lender/legal/technical/site diligence; bankable P90; executed PPA; security, insurance, reserve and hedge evidence; sponsor hurdle resolution.

## K. Release classification

Release 1.2.0 remains candidate with PASS_WITH_LIMITATIONS. recruiter_ready remains false until the external gates are closed.
