# V4 master-plan implementation trace

Release ID: V4-FINAL-2026-08-31
Plan fingerprint: SHA-256 28042fe994343a864486a9cc08085f176d3743a10fadab6a6c6278efd14c742a
Remote source of truth: https://github.com/susayold/vietgreen-ci-solar-project-finance
Drive control index: https://docs.google.com/document/d/1koSgbc1Akic6cVDFD1svmuVN9gSq8qSGUw2obfHYN80/edit

## V4 gates

- V4-G0 baseline freeze/register/ADR/tag: PASS.
- V4-G1 energy, load, uncertainty, PPA solver, current-versus-negotiated economics and Project/Equity returns: PASS.
- V4-G2/G3 debt, FX, exposure optimization, pooling and sponsor/lender scenario metrics: PASS.
- V4-G4 formula-driven workbook with linked sheets, switches, chart and remote recalculation: PASS.
- V4-G5 independent Python reconciliation and red-team: PASS; 2,055 formula cells and 240/240 reconciliation rows.
- V4-G6 IC memo, lender memo, recruiter package, CV bullets, finance-first website, workbook preview, final DoD, red-team and release manifest: PASS.

## Final decision surface

Current Terms = NO_DEPLOYMENT because 0/20 current project rows have positive Equity NPV. Negotiated Terms are a hypothetical remediation sensitivity. Exposure-constrained negotiated case selects 4 projects: VG-005, VG-010, VG-011, VG-012; equity 30.124825 BVND; debt 55.946104 BVND; pooled Min DSCR 1.300x. Base Equity NPV is 5.942277 BVND; P90 Equity NPV is -1.177896 BVND; combined downside Equity NPV is -38.814456 BVND and Min DSCR is 0.000x.

## Governance

RECRUITER_READY=TRUE is separate from TRANSACTION_EVIDENCE=OPEN and BANKABLE_TRANSACTION_READY=FALSE. Eight external gates remain open. No private transaction evidence is ingested or fabricated; the raw plan is not copied; local project data is zero. Synthetic screening outputs must not be represented as investment approval, lender approval, legal/tax opinion, technical certification, site diligence or bankable P90.
