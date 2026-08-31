# Release notes - 1.2.0 candidate

Date: 2026-08-31

## Added

- Locked 240-row, 12-month construction spend curve on GitHub.
- Monthly construction gross/net/VAT and capitalised IDC schedule.
- IDC-inclusive total uses and depreciable basis in project cash flow.
- Explicit CAPEX/VAT/IDC reconciliation and year-zero no-debt check.
- PPA negotiation-zone helper with explicit RENEGOTIATE_OR_REJECT action for empty zones, covered by a boundary test.
- Pairwise-swap improvement pass after hard-gated value-density selection.
- Remote source-fetch log, SR-1.15 DOD status matrix, full 65-row DoD audit, boundary tests, EVN and EVNSPC implementation-readiness refresh and recruiter-safe package.
- Plan-specified Parquet hourly streams plus deterministic CSV.GZ compatibility streams in the remote-only GitHub Actions artifact.
- Tax amendment watch for the official 2026-08-28 draft affecting Decree 320/2025; no effective model tax input was changed.
- Added Decree 278/2026/ND-CP as a locked legal dependency in the tariff/billing chain; it does not by itself prove invoice cutover.
- Added a metadata-only fingerprint of the user-provided Master Plan V3; no raw plan copy was stored by the agent.
- Added a fail-closed remote external-gate submission schema and GitHub Actions validator; no submission is present yet.
- Enabled a weekly Monday 02:00 UTC metadata-only official-source recheck with no raw snapshot storage.
- External-gate validator run 33371508632 / job 99423466049 passed with 8 gate rows and 0 submissions; all eight gates remain OPEN.

## Verified

- Source register advanced to SR-1.15 with EVNSPC customer-facing, meter-training and IT-readiness corroboration plus official tax/FX/benchmark rechecks and alternate NREL/IRENA comparator URLs; the refresh remains corroborative and does not close the billed-tariff gate.

- Metadata-only official-source crawl 33371147810 / job 99422352549 checked 26 controlled URLs: 20 PASS, 6 non-blocking warnings (two MOIT runner network-unreachable pages, original/alternate NREL DNS and original/alternate IRENA HTTP 403); no raw source snapshot was stored. Artifact 9750130974, digest sha256:24d20a3bf9ee66f5eb94af620a40c3cc1352856ea97dcc413af02b4304d5b972. The MOIT briefing and four EVNSPC pages corroborate the billing-status watch.

- Regulatory refresh: EVN Bulletin No. 16/2026 and Decree 278/2026/ND-CP were registered as current official references; billed implementation remains WATCH.

- Workflow run 33367160495 / job 99410087552; artifact 9748676847, digest sha256:3f1f7c193192ca4bd652a131e453e9bd7cd996592f0f2343b081664618fdba70.
- 20/20 data-quality checks; 20/20 dynamic remote QA checks.
- 31/31 workbook checks; 7/7 automated tests.
- 13/13 mechanical release controls pass; 1 candidate-manifest warning.
- 9 external-validation rows registered; 26 official source URLs live-checked remotely with raw snapshots disabled.
- Artifact vietgreen-core-outputs, ID 9748676847, digest sha256:3f1f7c193192ca4bd652a131e453e9bd7cd996592f0f2343b081664618fdba70; native workbook SHA-256 9e72588fd7a084282befa74dd0f97036f15e1f306aac6080fc86fdd75f605c5f, 117493 bytes.
- Independent same-head workflow_dispatch run 33367239508 / job 99410324360 succeeded; artifact 9748704397, digest sha256:714cba930edeb46a34dd780f3b372855e2b39eab646f8328757da6c74dbf8d24.
- Remote comparator run 33367293807 / job 99410490341 downloaded both core artifacts in memory and matched the native workbook, 8760 index and all four hourly streams (6/6); comparison metadata artifact 9748718166 was stored without raw artifact contents.

- Comparator metadata: SHA-256 28b02df8bfa8516586597a374ac11fe02907056f3f787de34675683ab7a9b8df, 1,389 bytes, GitHub blob 987e1605aecdd89525e76a9e29737401e9aa882c; raw_artifact_contents_stored=FALSE.

- Full DoD audit workflow 33371476512 / job 99423375898 passed 65/65 rows and 190/190 evidence-path checks: 62 PASS, 2 PARTIAL and 1 PENDING.

## Economics

The IDC-inclusive run selects 11 projects at 13.10 MWp, with 138.143294 BVND equity, 152.457008 BVND pooled debt, 1.30x base DSCR and -66.202345 BVND base sponsor NPV.

## Release boundary

Status remains candidate / PASS_WITH_LIMITATIONS. Billed tariff implementation, tax counsel/recheck, transaction-specific legal/foreign-borrowing review, independent model review, lender/technical/site diligence, bankable P90, executed PPA and security evidence remain open.


Pages deployment: 33360824385 / job 99391696231; aggregate-only boundary check PASS.
