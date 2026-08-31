# VietGreen CI Solar Project Finance — V4 Final Candidate

Release ID: V4-FINAL-2026-08-31
Date: 2026-08-31
GitHub source of truth: https://github.com/susayold/vietgreen-ci-solar-project-finance
Google Drive control index: https://docs.google.com/document/d/1koSgbc1Akic6cVDFD1svmuVN9gSq8qSGUw2obfHYN80/edit

This is a recruiter-ready synthetic Vietnam C&I rooftop-solar project-finance case. The attached V4 master plan is the implementation specification; the user request controls the remote-only boundary. The plan source is tracked by SHA-256 (28042fe994343a864486a9cc08085f176d3743a10fadab6a6c6278efd14c742a); no raw plan copy, private transaction file or local project-data copy is stored.

## Decision in one line

Current Terms = NO_DEPLOYMENT because all 20 Current Terms rows have negative Equity NPV. Negotiated Terms are a hypothetical remediation sensitivity. Under explicit exposure constraints, 4 projects are selected: VG-005, VG-010, VG-011, VG-012.

## Headline economics

- Selected equity: 30.124825 BVND; selected debt: 55.946104 BVND; selected Year-1 CFADS: 12.003384 BVND; pooled Min DSCR: 1.300x.
- Base Project NPV: 5.262393 BVND; Base Equity NPV: 5.942277 BVND; Base Project IRR: 12.732%; Base Equity IRR: 15.929%.
- P90 Equity NPV: -1.177896 BVND; CAPEX-overrun Equity NPV: -3.179160 BVND; COD-delay Min DSCR: 0.000x.
- Combined-downside Equity NPV: -38.814456 BVND; Combined-downside Min DSCR: 0.000x.

## What V4 fixed

Formula-driven Excel workbook; independent Python reconciliation; customer/sponsor/lender PPA solver; Project/Equity IRR; P50/P90/P99 uncertainty budget; realistic load archetypes and self-consumption; debt/FX/exposure optimizer/pooling/scenarios; IC/lender decision materials; red-team and claim governance.

## Gate status

V4-G0 through V4-G6: PASS for synthetic/recruiter package. Formula QA: 5/5; Excel/Python reconciliation: 240/240; final DoD: 35/35 PASS. RECRUITER_READY=TRUE is intentionally separate from TRANSACTION_EVIDENCE=OPEN and BANKABLE_TRANSACTION_READY=FALSE. Eight external gates remain open.

## Remote-only storage

All project code, synthetic inputs, aggregate outputs, validation evidence, manifests and workflow activity are on GitHub; Google Drive is the control/audit index. Hourly arrays exist only ephemerally on GitHub Actions and raw project data is not stored in this local workspace.

## Traceability

- Formula workbook: model/vietgreen_v4_formula_model.xlsx
- IC decision table: outputs/IC_DECISION_TABLE.csv
- IC memo: reports/INVESTMENT_COMMITTEE_MEMO.md
- Lender memo: reports/LENDER_CREDIT_MEMO.md
- Recruiter package: reports/RECRUITER_PACKAGE.md
- Final DoD: validation/V4_FINAL_DOD_MATRIX.csv
- Final red-team: validation/V4_RED_TEAM_REPORT.md
- V4 release manifest: release/MODEL_RELEASE_MANIFEST.json
- G4/G5 validation run: https://github.com/susayold/vietgreen-ci-solar-project-finance/actions/runs/33415906096
- Phase 2 validation run: https://github.com/susayold/vietgreen-ci-solar-project-finance/actions/runs/33416323104
- Drive control document: https://docs.google.com/document/d/1koSgbc1Akic6cVDFD1svmuVN9gSq8qSGUw2obfHYN80/edit
