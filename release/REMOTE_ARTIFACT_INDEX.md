# Remote artifact index

Release candidate: 1.2.0
Date: 2026-08-31
Source register: SR-1.6-live-benchmark-refresh (latest live source: SRC-REFRESH-EVN-20260831)
Repository: https://github.com/susayold/vietgreen-ci-solar-project-finance
Workflow source commit: c9d7e9712c2b6f868a4eaf042204257a8a2965a8
Workbook/remote-output refresh commit: 669e33324c162955981314d31a8e3b40937aeff9
Workflow run: 33356405815
Workflow job: 99379325568
Artifact: vietgreen-core-outputs, ID 9745267596
Artifact digest: sha256:b98a6c21209a644dfd0a32509d5ee008b928e409fdae825873e053366a319b53

## Gate summary

- Data-quality: 20 checks, 0 failures.
- Dynamic remote QA: 20 checks, 0 failures.
- Workbook: 31 checks, 0 failures.
- Hidden truth: 5 cases, 5 matches, 0 false negatives.
- Automated tests: 7 passed.
- Release controls: 13 mechanical PASS, 1 candidate WARN for post-run manifest linkage.
- Native workbook: 22 sheets, 116230 bytes; blob c160cb5b630f653c68343381a8d0d514faa54b02.
- Construction schedule: 240 rows; capitalised IDC proxy rate 8.5%; sources and uses reconciled.
- Portfolio: 11 selected projects, 13.10 MWp, pooled DSCR 1.300x, sponsor NPV -66.202345 BVND.
- Remote 8,760 streams: four artifact-only streams, each 175,200 rows: Parquet load/solar plus CSV.GZ compatibility streams; index validation PASS.
- Tariff: WATCH pending billed implementation confirmation; latest official EVN/MOIT evidence does not document an invoice cutover date.
- Reproducibility: independent workflow_dispatch run 33356485956 / job 99379546146 succeeded; native workbook SHA matched the push run.
- Release status: candidate.
- recruiter_ready: false.

The artifact is remote-only and contains synthetic inputs, aggregate validation, controlled outputs and review streams. It excludes credentials and private hidden raw truth. Hourly streams are available through the workflow artifact, not the desktop workspace.

Backend manifest SHA-256: 4df5d760c46a715d76c246a695ae28567cb647b5aca12806770f75015472ba0b.
Remote 8,760 index SHA-256: 563752a09c787b097e8ba17e633ed53b8cfe6bf842d728c9745292d3c80b6ba6.
Parquet streams: load_8760.parquet 43c5e0b2555360d15bc234f7d023d06e6a76dcbd26d7ff2b0c29e33ed8418a17; solar_8760.parquet 96a2c773309d92b1b4c24d321616ec23e4ac333014fb5e5dd6a8e9937f7da449.

Live recruiter site (aggregate-only): https://susayold.github.io/vietgreen-ci-solar-project-finance/
