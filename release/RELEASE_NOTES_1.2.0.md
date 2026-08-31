# Release notes - 1.2.0 candidate

Date: 2026-08-31

## Added

- Locked 240-row, 12-month construction spend curve on GitHub.
- Monthly construction gross/net/VAT and capitalised IDC schedule.
- IDC-inclusive total uses and depreciable basis in project cash flow.
- Explicit CAPEX/VAT/IDC reconciliation and year-zero no-debt check.
- PPA negotiation-zone helper with explicit RENEGOTIATE_OR_REJECT action for empty zones.
- Pairwise-swap improvement pass after hard-gated value-density selection.
- Remote source-fetch log, DOD status matrix and recruiter-safe package.

## Verified

- Workflow run 33349715239 / job 99360547174.
- 20/20 data-quality checks; 20/20 dynamic remote QA checks.
- 31/31 workbook checks; 5/5 automated tests.
- 13/13 mechanical release controls pass; 1 candidate-manifest warning.
- Artifact vietgreen-core-outputs, ID 9743177276, digest sha256:0240d888a49d77469a517e665bc28e76b832735efec7b356782a86853b869b71.

## Economics

The IDC-inclusive run selects 11 projects at 13.10 MWp, with 138.143294 BVND equity, 152.457008 BVND pooled debt, 1.30x base DSCR and -66.202345 BVND base sponsor NPV.

## Release boundary

Status remains candidate / PASS_WITH_LIMITATIONS. Billed tariff implementation, transaction-specific legal/tax/foreign-borrowing review, independent model review, lender/technical/site diligence, bankable P90, executed PPA and security evidence remain open.
