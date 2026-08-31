# Master-plan implementation trace

## A. Evidence and regulatory lineage

Plan provenance: the user-provided Master Plan V3 was read in memory and fingerprinted as SHA-256 `77e1709bc8d33ed0fa3a991b52d3a372f11322064f22a93f5272456e58d75c15` (128,145 bytes); only metadata is stored remotely in `evidence/PLAN_SOURCE_MANIFEST.csv`.

Implemented: material inputs carry source/assumption IDs through the lineage matrix; legal tariff windows, current billed references and model-only price components are separate; tax and foreign-borrowing rules are registered with effective dates and recheck flags; the remote source-fetch log records the 2026-08-31 refresh without storing raw snapshots locally. The source-refresh workflow now has a weekly Monday 02:00 UTC metadata-only recheck with concurrency protection.

Status: PASS WITH BILLING/TAX WATCH. Decision 963 legal windows are mapped, Decree 278/2026/ND-CP is registered as a legal dependency in the average-retail-price adjustment chain, but billed implementation/invoice cutover and final transaction applicability remain external gates; the 2026-08-28 draft amendment to Decree 320/2025 is monitored without changing effective tax inputs.

Latest benchmark refresh: IRENA 2025 official utility-scale solar PV cost context remains comparator-only; the IRENA 2024 URL was rechecked but returned HTTP 403 and is not used as certification evidence. Latest tariff-chain evidence: EVN Bulletin No. 16/2026, Decree 278/2026/ND-CP, EVN's Decision 963 republication and four EVNSPC implementation/readiness pages; none is treated as invoice-cutover proof. Official tax/FX references were also rechecked remotely.

## B. Synthetic data, hidden truth and reproducibility

Implemented: locked master seed 260831; hashes for all synthetic inputs including the 240-row construction curve; deterministic generation; cross-field DQ; hidden-truth cases isolated to aggregate labels; no customer data or raw hidden truth in the public repository.

Status: PASS. 20/20 DQ, 5/5 hidden-truth classifications and locked hashes.

## C. Energy, PPA and 8,760

Implemented: 20 in-memory 8,760 load/solar profiles, P50/P90 flow-through, P90 <= P50, separate loss and load matching, legal tariff midpoint mapping, current billed-reference mapping, three-sided PPA frontier, explicit empty-zone action and remote artifact export.

Status: PASS for synthetic mechanics; external PPA, site, technical-yield and billed-tariff evidence remain open.

Remote-format note: the plan names Parquet for hourly deliverables; the remote-only implementation publishes Parquet streams plus deterministic CSV.GZ compatibility streams in the GitHub Actions artifact with an explicit schema/index. No hourly stream is retained in the desktop workspace.

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

Latest core remote run: 33367160495 / job 99410087552; latest source-refresh run: 33370454210 / job 99420130285; 20/20 DQ; 20/20 dynamic remote QA; 31/31 workbook checks; 7/7 tests; 13/13 mechanical release controls plus 1 candidate-manifest warning; 240 construction schedule rows; 9 external-validation rows; 24 official URLs returned 20 PASS and 4 non-blocking WARNs; four remote 8,760 streams (Parquet plus deterministic CSV.GZ compatibility) remain artifact-only with local_storage NONE.

## I. Recruiter-facing communication

Implemented: aggregate-only recruiter-facing landing page and workbook model preview under `website/`, linked from README; only frozen aggregate metrics and remote links are shown.

Status: PASS for communication scope; no raw 8,760 streams, hidden truth, credentials or project-sensitive data are embedded.

Live deployment verified at https://susayold.github.io/vietgreen-ci-solar-project-finance/ via Pages workflow 33360824385 / job 99391696231; website boundary check PASS.

## J. Master Plan V3 DoD audit

Implemented: checkbox-level audit for all 65 requirements in DoD 42.1–42.9, with evidence paths, validation basis, limitation/blocker and next action. Remote workflow 33369402509 / job 99416840692 passed 65/65 row identity checks and 190/190 evidence-path checks; status counts are 62 PASS, 2 PARTIAL and 1 PENDING.

## J. Open gates

Independent final model review; billed tariff confirmation; transaction-specific tax and foreign-borrowing advice; lender/legal/technical/site diligence; bankable P90; executed PPA; security, insurance, reserve and hedge evidence; sponsor hurdle resolution. These are tracked in validation/OPEN_EXTERNAL_GATES.csv; no synthetic or public comparator evidence closes them.


## K. External gate intake

A remote-only intake register and acceptance template now map each of EXT-001–EXT-008 to the required document, verifier, model reconciliation and storage boundary. A fail-closed GitHub Actions validator checks submission metadata against the gate tracker and manifest; run 33370201444 / job 99419321412 passed with 8 gate rows and 0 submissions. The register does not close any gate; it prevents comparator, readiness or synthetic evidence from being mislabeled as transaction proof.

## L. Release classification

Release 1.2.0 remains candidate with PASS_WITH_LIMITATIONS. recruiter_ready remains false until the external gates are closed.

Reproducibility control: remote push run 33367160495 and same-head workflow_dispatch run 33367239508 / job 99410324360 both succeeded and produced identical native workbook SHA-256 9e72588fd7a084282befa74dd0f97036f15e1f306aac6080fc86fdd75f605c5f; comparator run 33367293807 / job 99410490341 compared the index, native workbook and all four hourly streams with 6/6 matches; comparison metadata artifact 9748718166 was recorded without raw artifact contents; reproducibility_check_status=PASS.

## M. Final remote output refresh

The final push-triggered core rebuild completed in workflow 33367160495 / job 99410087552; the repository workbook is now regenerated against SR-1.14 with SHA-256 9e72588fd7a084282befa74dd0f97036f15e1f306aac6080fc86fdd75f605c5f and 117493 bytes. Same-head run 33367239508 / job 99410324360 and comparator 33367293807 / job 99410490341 matched 6/6 files.
