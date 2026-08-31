# Release notes - 1.2.0 candidate

Date: 2026-08-31

## Added

- Locked 240-row, 12-month construction spend curve on GitHub.
- Monthly construction gross/net/VAT and capitalised IDC schedule.
- IDC-inclusive total uses and depreciable basis in project cash flow.
- Explicit CAPEX/VAT/IDC reconciliation and year-zero no-debt check.
- PPA negotiation-zone helper with explicit RENEGOTIATE_OR_REJECT action for empty zones, covered by a boundary test.
- Pairwise-swap improvement pass after hard-gated value-density selection.
- Remote source-fetch log, SR-1.13 DOD status matrix, full 65-row DoD audit, boundary tests, EVN and EVNSPC implementation-readiness refresh and recruiter-safe package.
- Plan-specified Parquet hourly streams plus deterministic CSV.GZ compatibility streams in the remote-only GitHub Actions artifact.
- Tax amendment watch for the official 2026-08-28 draft affecting Decree 320/2025; no effective model tax input was changed.
- Added Decree 278/2026/ND-CP as a locked legal dependency in the tariff/billing chain; it does not by itself prove invoice cutover.

## Verified

- Source register advanced to SR-1.13 with EVNSPC customer-facing, meter-training and IT-readiness corroboration; the refresh remains corroborative and does not close the billed-tariff gate.

- Metadata-only official-source crawl 33366510106 / job 99408166781 checked 16 controlled URLs: 13 PASS, 3 non-blocking warnings (MOIT runner network-unreachable on two pages; NREL DNS); no raw source snapshot was stored. Artifact 9748486524, digest sha256:bbafe54b9991fb90b74ce39ca089c6b937855660411c3cfe859da506bff327aa. The MOIT briefing and four EVNSPC pages corroborate the billing-status watch.

- Regulatory refresh: EVN Bulletin No. 16/2026 and Decree 278/2026/ND-CP were registered as current official references; billed implementation remains WATCH.

- Workflow run 33362871604 / job 99397534044.
- 20/20 data-quality checks; 20/20 dynamic remote QA checks.
- 31/31 workbook checks; 7/7 automated tests.
- 13/13 mechanical release controls pass; 1 candidate-manifest warning.
- 9 external-validation rows registered; 16 official source URLs live-checked remotely with raw snapshots disabled.
- Artifact vietgreen-core-outputs, ID 9747272913, digest sha256:d98e61282a9fbc564bc5078a805d64009ef1f2906a288cb3ec541f4704db93d6.
- Independent same-head workflow_dispatch run 33362978966 / job 99397849553 succeeded.
- Remote comparator run 33363289510 / job 99398752408 downloaded both core artifacts in memory and matched the native workbook, 8760 index and all four hourly streams (6/6); comparison metadata artifact 9747403047 was stored without raw artifact contents.

- Comparator metadata: SHA-256 eb571d45c45d54babb7e7dc23373d9ce35cec6fdcc2155420bca7546d42f79c0, 1,389 bytes, GitHub blob e9885d5a33d94f5fc8169d1121a036e135e68ba8; raw_artifact_contents_stored=FALSE.

- Full DoD audit workflow 33366770050 / job 99408939518 passed 65/65 rows and 190/190 evidence-path checks: 62 PASS, 2 PARTIAL and 1 PENDING.

## Economics

The IDC-inclusive run selects 11 projects at 13.10 MWp, with 138.143294 BVND equity, 152.457008 BVND pooled debt, 1.30x base DSCR and -66.202345 BVND base sponsor NPV.

## Release boundary

Status remains candidate / PASS_WITH_LIMITATIONS. Billed tariff implementation, tax counsel/recheck, transaction-specific legal/foreign-borrowing review, independent model review, lender/technical/site diligence, bankable P90, executed PPA and security evidence remain open.


Pages deployment: 33360824385 / job 99391696231; aggregate-only boundary check PASS.
