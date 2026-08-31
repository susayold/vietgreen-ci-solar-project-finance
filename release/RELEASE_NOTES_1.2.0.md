# Release notes - 1.2.0 candidate

Date: 2026-08-31

## Added

- Locked 240-row, 12-month construction spend curve on GitHub.
- Monthly construction gross/net/VAT and capitalised IDC schedule.
- IDC-inclusive total uses and depreciable basis in project cash flow.
- Explicit CAPEX/VAT/IDC reconciliation and year-zero no-debt check.
- PPA negotiation-zone helper with explicit RENEGOTIATE_OR_REJECT action for empty zones, covered by a boundary test.
- Pairwise-swap improvement pass after hard-gated value-density selection.
- Remote source-fetch log, DOD status matrix, boundary tests, latest EVN billing-status refresh and recruiter-safe package.
- Plan-specified Parquet hourly streams plus CSV.GZ compatibility streams in the remote-only GitHub Actions artifact.

## Verified

- Workflow run 33356405815 / job 99379325568.
- 20/20 data-quality checks; 20/20 dynamic remote QA checks.
- 31/31 workbook checks; 7/7 automated tests.
- 13/13 mechanical release controls pass; 1 candidate-manifest warning.
- Artifact vietgreen-core-outputs, ID 9745267596, digest sha256:b98a6c21209a644dfd0a32509d5ee008b928e409fdae825873e053366a319b53.
- Independent workflow_dispatch run 33356485956 / job 99379546146 succeeded with matching native workbook SHA-256.

## Economics

The IDC-inclusive run selects 11 projects at 13.10 MWp, with 138.143294 BVND equity, 152.457008 BVND pooled debt, 1.30x base DSCR and -66.202345 BVND base sponsor NPV.

## Release boundary

Status remains candidate / PASS_WITH_LIMITATIONS. Billed tariff implementation, transaction-specific legal/tax/foreign-borrowing review, independent model review, lender/technical/site diligence, bankable P90, executed PPA and security evidence remain open.
