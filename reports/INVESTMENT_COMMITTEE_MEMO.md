# Investment Committee Memo — V4.1.3 Final Synthetic Candidate

Release ID: V4.1.3-RECRUITER-FINAL
Date: 2026-09-01
Source of truth: https://github.com/susayold/vietgreen-ci-solar-project-finance
Control index: https://docs.google.com/document/d/1koSgbc1Akic6cVDFD1svmuVN9gSq8qSGUw2obfHYN80/edit

## V4.1.3 governance status

CURRENT_TERMS_DECISION=NO_DEPLOYMENT
SELECTED_COUNT=4
SELECTED_IDS=VG-005|VG-010|VG-011|VG-012
RECRUITER_READY=TRUE
TRANSACTION_EVIDENCE_STATUS=OPEN
BANKABLE_TRANSACTION_READY=FALSE
EXTERNAL_GATE_COUNT_OPEN=8
SELECTED_DEBT_BVND=55.946104
SELECTED_CFADS_Y1_BVND=12.003384
POOLED_MIN_DSCR=1.300
IC_APPROVAL_STATUS=NOT_IC_APPROVAL

## Recommendation

Current Terms: NO_DEPLOYMENT. All 20 Current Terms rows remain below sponsor Equity NPV hurdle (0 positive rows). Negotiated Terms are a hypothetical remediation case, not executed terms.

Exposure-constrained negotiated screening selects 4 projects: VG-005, VG-010, VG-011, VG-012. Equity required is 30.124825 BVND, debt is 55.946104 BVND and Year-1 CFADS is 12.003384 BVND. Proceed only with conditions and only after external gates are closed; this is not IC approval.

## Economics

- Base Project NPV: 5.262393 BVND; Base Equity NPV: 5.942277 BVND.
- Base Project IRR: 12.732%; Base Equity IRR: 15.929%; pooled Min DSCR: 1.300x.
- P90 Equity NPV: -1.177896 BVND.
- CAPEX overrun Equity NPV: -3.179160 BVND.
- COD-delay Min DSCR: 0.000x.
- Combined-downside Equity NPV: -38.814456 BVND; Min DSCR: 0.000x.

## Required conditions

1. Confirm billed tariff and implementation chain; model-only avoided tariff is not an invoice.
2. Obtain independent model review, site/technical diligence, lender/legal/tax evidence, executed PPA/security package and financing terms.
3. Re-run the V4 formula workbook and Python reconciliation when controlled evidence is available.
4. Treat negative stress outputs as decision inputs, not as hidden or averaged-away downside.

## Evidence

- IC decision table: outputs/IC_DECISION_TABLE.csv
- Final DoD: validation/V4_FINAL_DOD_MATRIX.csv
- V4 release manifest: release/MODEL_RELEASE_MANIFEST.json

This memo is a recruiter-ready synthetic case package. It is not investment approval, lender approval, a legal/tax opinion, a technical certification or a bankable P90 case.
