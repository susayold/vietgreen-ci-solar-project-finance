# Release notes - 1.2.0 candidate

Date: 2026-08-31

## Added

- Locked 240-row, 12-month construction spend curve on GitHub.
- Monthly construction gross/net/VAT and capitalised IDC schedule.
- IDC-inclusive total uses and depreciable basis in project cash flow.
- Explicit CAPEX/VAT/IDC reconciliation and year-zero no-debt check.
- PPA negotiation-zone helper with explicit RENEGOTIATE_OR_REJECT action for empty zones, covered by a boundary test.
- Pairwise-swap improvement pass after hard-gated value-density selection.
- Remote source-fetch log, DOD status matrix, boundary tests, EVN billing-status refresh and recruiter-safe package.
- Plan-specified Parquet hourly streams plus deterministic CSV.GZ compatibility streams in the remote-only GitHub Actions artifact.
- Tax amendment watch for the official 2026-08-28 draft affecting Decree 320/2025; no effective model tax input was changed.

## Verified

- Workflow run 33358923808 / job 99386362961.
- 20/20 data-quality checks; 20/20 dynamic remote QA checks.
- 31/31 workbook checks; 7/7 automated tests.
- 13/13 mechanical release controls pass; 1 candidate-manifest warning.
- 9 external-validation rows registered.
- Artifact vietgreen-core-outputs, ID 9746043440, digest sha256:5148efc5e4b6461db83736221a500bc926a2764c176e85851c5217283c5d1784.
- Independent workflow_dispatch run 33358955525 / job 99386452901 succeeded.
- Byte-level comparison matched the index and all four hourly streams; native workbook SHA-256 remained identical.

## Economics

The IDC-inclusive run selects 11 projects at 13.10 MWp, with 138.143294 BVND equity, 152.457008 BVND pooled debt, 1.30x base DSCR and -66.202345 BVND base sponsor NPV.

## Release boundary

Status remains candidate / PASS_WITH_LIMITATIONS. Billed tariff implementation, tax counsel/recheck, transaction-specific legal/foreign-borrowing review, independent model review, lender/technical/site diligence, bankable P90, executed PPA and security evidence remain open.
