# Recruiter Package — V4 Project Finance Case

Release ID: V4-FINAL-2026-08-31
Date: 2026-08-31
Repository: https://github.com/susayold/vietgreen-ci-solar-project-finance
Recruiter site: https://susayold.github.io/vietgreen-ci-solar-project-finance/

## Positioning

Recruiter-ready synthetic Vietnam C&I rooftop-solar project-finance model. The package separates recruiter readiness from transaction readiness: RECRUITER_READY=TRUE, TRANSACTION_EVIDENCE=OPEN, BANKABLE_TRANSACTION_READY=FALSE.

## Defensible bullets

- Built a formula-driven Excel Project Finance model linking synthetic 8,760 load matching, P50/P90 energy, CFADS, debt sizing and Project/Equity NPV/IRR.
- Solved customer ceiling, sponsor floor and lender floor with explicit bisection roots and residual/interval evidence.
- Compared VND, unhedged USD and hedged USD funding and solved primary/secondary FX break-even conditions.
- Optimized a negotiated hypothetical portfolio under equity, parent, industry, region and debt exposure constraints; reconciled standalone versus pooled financing in Python.
- Automated Excel formula QA, remote recalculation, Python parity, red-team tests and release governance on GitHub Actions.

## What is not claimed

No executed transaction, lender approval, legal/tax opinion, technical certification, site diligence or bankable P90 claim. All transaction evidence gates remain visible in the release manifest and Drive control document.

## Traceability

- IC memo: reports/INVESTMENT_COMMITTEE_MEMO.md
- Lender memo: reports/LENDER_CREDIT_MEMO.md
- IC table: outputs/IC_DECISION_TABLE.csv
- Formula workbook: model/vietgreen_v4_formula_model.xlsx
- Final DoD: validation/V4_FINAL_DOD_MATRIX.csv
- Release manifest: release/MODEL_RELEASE_MANIFEST.json
- CV bullets: reports/CV_BULLETS_V4.md
