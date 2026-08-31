# Remote artifact index

Release candidate: 1.2.0
Date: 2026-08-31
Source register: SR-1.7-tax-draft-watch (latest live source: SRC-REFRESH-EVN-20260831; latest tax watch: SRC-REFRESH-TAX-20260831)
Repository: https://github.com/susayold/vietgreen-ci-solar-project-finance
Workflow source commit: 59cfa0d5304ecd7e8c05b865d45a1abcc58b8372
Workbook/remote-output refresh commit: d50f918d4a4756a78d4e82ae786136cbf3d38ec7
Workflow run: 33357877259
Workflow job: 99383381558
Artifact: vietgreen-core-outputs, ID 9745707771
Artifact digest: sha256:16addbaafa85aeaecde83ce12a5f3c9513988911d2090d915b29899f0dec607e

## Gate summary

- Data-quality: 20 checks, 0 failures.
- Dynamic remote QA: 20 checks, 0 failures.
- Workbook: 31 checks, 0 failures.
- Hidden truth: 5 cases, 5 matches, 0 false negatives.
- Automated tests: 7 passed.
- Release controls: 13 mechanical PASS, 1 candidate WARN for post-run manifest linkage.
- External validation: 9 registered rows; tax amendment watch added without changing effective model inputs.
- Native workbook: 22 sheets, 116230 bytes; blob c160cb5b630f653c68343381a8d0d514faa54b02.
- Construction schedule: 240 rows; capitalised IDC proxy rate 8.5%; sources and uses reconciled.
- Portfolio: 11 selected projects, 13.10 MWp, pooled DSCR 1.300x, sponsor NPV -66.202345 BVND.
- Remote 8,760 streams: four artifact-only streams, each 175,200 rows: Parquet load/solar plus deterministic CSV.GZ compatibility streams; index validation PASS.
- Remote index SHA-256: d5f0e3822b126239c85756feda029fc40c793aa28f707cec0fd40b081e338cc0.
- File-level reproducibility: push run 33357877259 and independent workflow_dispatch run 33357990799 / job 99383699191 matched the index and all four hourly stream bytes.
- Tariff: WATCH pending billed implementation confirmation.
- Tax: WATCH for the official 2026-08-28 draft amendment; current registered tax rules remain unchanged in the model.
- Release status: candidate.
- recruiter_ready: false.

The artifact is remote-only and contains synthetic inputs, aggregate validation, controlled outputs and review streams. It excludes credentials and private hidden raw truth. Hourly streams are available through the workflow artifact, not the desktop workspace.

Live recruiter site (aggregate-only): https://susayold.github.io/vietgreen-ci-solar-project-finance/
