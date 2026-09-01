# Lender Credit Memo — V4.1.3 Final Synthetic Candidate

Release ID: V4.1.3-RECRUITER-FINAL
Date: 2026-09-01
Source: https://github.com/susayold/vietgreen-ci-solar-project-finance

## V4.1.3 governance status

CURRENT_TERMS_DECISION=NO_DEPLOYMENT
SELECTED_COUNT=4
SELECTED_IDS=VG-005|VG-010|VG-011|VG-012
RECRUITER_READY=TRUE
TRANSACTION_EVIDENCE_STATUS=OPEN
BANKABLE_TRANSACTION_READY=FALSE
EXTERNAL_GATE_COUNT_OPEN=8
SELECTED_DEBT_BVND=55.946104
POOLED_MIN_DSCR=1.300

## Credit view

The exposure-constrained negotiated screening pool contains 4 projects with 55.946104 BVND debt and pooled Min DSCR 1.300x in the base case. Debt sizing is constrained by coverage/leverage logic and is not a lender commitment.

## Downside

- P90 Equity NPV: -1.177896 BVND; scenario Min DSCR: 1.300x.
- CAPEX-overrun Equity NPV: -3.179160 BVND.
- COD-delay Min DSCR: 0.000x.
- Combined downside Equity NPV: -38.814456 BVND; Min DSCR: 0.000x.
- VND, unhedged USD and hedged USD cases are separate; FX roots are in outputs/fx_break_even_v4.csv.

## Credit conditions

Require executed PPA/security package, billed-tariff evidence, technical/site diligence, insurance, EPC/O&M support, debt terms, DSRA/reserve confirmation and independent model review before any credit decision. BANKABLE_TRANSACTION_READY=FALSE; external transaction evidence is OPEN.

## Reconciliations

- FX QA: validation/FX_QA.csv
- Debt/portfolio/scenario evidence: validation/V4_PHASE2_DOD.csv
- Excel/Python parity: validation/EXCEL_PYTHON_RECONCILIATION.csv
- Release manifest: release/MODEL_RELEASE_MANIFEST.json
