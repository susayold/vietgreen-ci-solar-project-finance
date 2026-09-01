# VietGreen CI Solar Project Finance — V5 Global Real-Data Migration

V5 branch: v5-global-real-data
V5 status: INPUT_DATA_BLOCKED — research/evidence baseline only
V4.1.3 historical recruiter release remains preserved on main and v4.1.3-recruiter-final.

V5 is being reconstructed from public evidence across multiple markets. It does not claim confidential PPA terms, actual lender pricing, investment approval, legal/tax/technical certification or bankability. No V4 synthetic economics are reused as V5 facts.

Remote-only control:
- GitHub source of truth: https://github.com/susayold/vietgreen-ci-solar-project-finance/tree/v5-global-real-data
- Google Drive control index: https://docs.google.com/document/d/1koSgbc1Akic6cVDFD1svmuVN9gSq8qSGUw2obfHYN80/edit
- Local project data: NONE

## Current V5 evidence baseline

- Candidate records: 2 portfolio/platform disclosures from official IFC ESRS pages.
- Frozen V5 economics universe: 0.
- Public asset-level projects eligible for economics: 0.
- Transaction evidence: OPEN.
- Recruiter-ready V5 release: FALSE.

The candidate records and all evidence classes are in data/public/, research/ and evidence/. Portfolio-level capacity or financing is never silently converted into an asset-level project.

## V5 build contract

Run on a remote GitHub Actions runner:

python -m analytics.build_v5_release --allow-incomplete

The build produces a metadata-only blocked status. Economics must only be enabled after outcome-blind selection, input freeze, country-pack refresh and G0–G9 reconciliation.

## V4 historical package

# VietGreen CI Solar Project Finance — V4.1.3 Recruiter Final

Release ID: V4.1.3-RECRUITER-FINAL
Date: 2026-09-01
GitHub source of truth: https://github.com/susayold/vietgreen-ci-solar-project-finance
Google Drive control index: https://docs.google.com/document/d/1koSgbc1Akic6cVDFD1svmuVN9gSq8qSGUw2obfHYN80/edit

This is a recruiter-ready synthetic Vietnam C&I rooftop-solar project-finance case. The attached V4.1.3 governance closure plan is the implementation specification; the user request controls the remote-only boundary. The plan source is tracked by SHA-256 (ebf18083c631a023b804a391e096b8593fea02607128d1e16c85513c710fe8c7); no raw plan copy, private transaction file or local project-data copy is stored.

## V4.1.3 governance status

CURRENT_TERMS_DECISION=NO_DEPLOYMENT
SELECTED_COUNT=4
SELECTED_IDS=VG-005|VG-010|VG-011|VG-012
RECRUITER_READY=TRUE
TRANSACTION_EVIDENCE_STATUS=OPEN
BANKABLE_TRANSACTION_READY=FALSE
EXTERNAL_GATE_COUNT_OPEN=8
SELECTED_EQUITY_BVND=30.124825

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

