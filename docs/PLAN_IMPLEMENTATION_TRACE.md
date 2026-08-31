# Master-plan implementation trace

## A. Evidence and regulatory lineage

Implemented: material synthetic inputs carry IDs through evidence/INPUT_LINEAGE_MATRIX.csv; tariff legal, current billed reference and model-only price components are separate; Decision 963, Circular 60, EVN implementation, MOIT current-practice, tax and foreign-borrowing rows are registered. The live recheck note is remote and raw_snapshot_path remains NOT_STORED_LOCAL.

Status: PASS WITH BILLING WATCH. Billed tariff and final legal applicability remain external gates.

## B. Synthetic data and hidden truth

Implemented: locked seed 260831; locked input hashes; rerunable deterministic pipeline; cross-field QA; operational-outage hidden-truth cases stored only as aggregate labels; no raw truth in the public repository.

Status: PASS. Five cases matched with zero false negatives.

## C. Energy, PPA and 8,760

Implemented: hourly in-memory profiles for all 20 projects, P50/P90, P90 no greater than P50, separated loss/load matching, Decision 963 midpoint mapping, current billed reference mapping, PPA frontier and customer/sponsor/lender gates. Full derived streams are uploaded as remote workflow artifacts.

Status: PASS for implemented synthetic mechanics; external PPA and site evidence remain open.

## D. CAPEX, tax, VAT, WC and terminal

Implemented: bottom-up synthetic capex, sources-and-uses reconciliation, IDC proxy, VAT, depreciation/loss-carryforward tax proxy, DSO working capital, major maintenance and zero-terminal branch.

Status: PASS for internal mechanics; tax/accounting certification remains open.

## E. Debt

Implemented: registered LLCR/PLCR discount rates, DSCR, LLCR, PLCR, leverage, backward sizing, forward rebuild, debt close, tail, DSRA/reserve waterfall and pooled feedback.

Status: PASS for automated controls; lender term confirmation remains open.

## F. FX and portfolio

Implemented: period-by-period FX sensitivity, crawl and one-off shocks, break-even FX, aggregate DSCR, pooled resize, concentration and common-factor cases.

Status: PASS for implemented synthetic mechanics; hedge/portfolio-correlation evidence remains open.

## G. Allocation and IC

Implemented: eligibility gates before ranking, fixed budget allocation, additive equity NPV register, sponsor/lender split and portfolio IC decision table.

Current candidate: 12 selected projects; 14.95 MWp; equity 145.275160 BVND; pooled debt 172.412340 BVND; DSCR 1.30x; base sponsor NPV -63.922321 BVND.

Status: PASS WITH NEGATIVE BASE SPONSOR NPV; conditions are recorded.

## H. Validation and release

Implemented: unit/reconciliation/boundary/monotonicity/isolation checks, 18/18 DQ, 18/18 dynamic remote QA, hidden-truth classification, 31/31 workbook validation, 5/5 tests, locked input hashes, remote 8,760 index and release controls.

## I. Open gates

Independent final review; billed tariff confirmation; lender/legal/tax/technical/site diligence; bankable P90 and executed PPA/security evidence.

## J. Release classification

Release 1.2.0 is a candidate with PASS_WITH_LIMITATIONS. recruiter_ready is false.
