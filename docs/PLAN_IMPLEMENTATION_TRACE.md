# Master-plan implementation trace

## A. Evidence and regulatory lineage

Implemented: material synthetic inputs carry IDs; tariff legal and billing fields are separate; Decision 963, Circular 60, EVN implementation, tax and foreign-borrowing rows are registered; model-only tariff assumptions are marked as such.

Status: PASS WITH BILLING WATCH. Billed tariff and final legal applicability remain external gates.

## B. Synthetic data and hidden truth

Implemented: locked seed 260831; rerunable generation; cross-field QA; operational-outage hidden-truth cases stored only as aggregate labels; no raw truth in the public repository.

Status: PASS. Five cases matched with zero false negatives.

## C. Energy, PPA and 8,760

Implemented: hourly in-memory profiles, P50/P90, P90 no greater than P50, separated loss/load matching, PPA frontier and customer/sponsor/lender gates.

Status: PASS for implemented synthetic mechanics; external PPA and site evidence remain open.

## D. CAPEX, tax, VAT, WC and terminal

Implemented: bottom-up synthetic capex, sources-and-uses reconciliation, IDC proxy, VAT, depreciation/loss carryforward tax proxy, DSO working capital, major maintenance and zero-terminal branch.

Status: PASS for internal mechanics; tax/accounting certification remains open.

## E. Debt

Implemented: DSCR, LLCR, PLCR, leverage, forward rebuild, debt close, tail, DSRA/reserve waterfall and pooled feedback.

Status: PASS for automated controls; lender term confirmation remains open.

## F. FX and portfolio

Implemented: period-by-period FX sensitivity, crawl and one-off shocks, break-even FX, aggregate DSCR, pooled resize, concentration and common-factor cases.

Status: PASS for implemented synthetic mechanics; hedge/portfolio correlation evidence remains open.

## G. Allocation and IC

Implemented: eligibility gates before ranking, budget allocation, additive equity NPV register, sponsor/lender split and portfolio IC decision table.

Status: PASS WITH NEGATIVE BASE SPONSOR NPV; conditions are recorded.

## H. Validation and release

Implemented: unit/reconciliation/boundary/monotonicity/isolation checks, remote QA, hidden-truth classification, native workbook structural validation, artifact and manifest controls.

Latest: 18/18 data-quality, 31/31 workbook, 5/5 hidden truth, 5/5 tests.

## I. Current candidate

11 selected projects; 13.4 MWp; equity 131.869565 BVND; pooled debt 152.880435 BVND; DSCR 1.30x; base sponsor NPV -59.736498 BVND.

## J. Open gates

Independent final review; billed tariff confirmation; lender/legal/tax/technical/site diligence; bankable P90 and executed PPA/security evidence.

## K. Release classification

Release 1.1.0 is a candidate with PASS_WITH_LIMITATIONS. recruiter_ready is false.

