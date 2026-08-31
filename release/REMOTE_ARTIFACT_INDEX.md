# Remote artifact index

Release candidate: 1.2.0
Date: 2026-08-31
Source register: SR-1.9-tax-tariff-watch (latest live source: SRC-REFRESH-EVN-20260831; latest tax watch: SRC-REFRESH-TAX-20260831)
Repository: https://github.com/susayold/vietgreen-ci-solar-project-finance
Workflow source commit: d2fd8835bb0591bc850a90b13cb37f3b5ec2310b
Workbook/remote-output refresh commit: d2fd8835bb0591bc850a90b13cb37f3b5ec2310b
Workflow run: 33360401233
Workflow job: 99390501627
Artifact: vietgreen-core-outputs, ID 9746487203
Artifact digest: sha256:3396dce1eee9420c8c16532c30e38d7be33d4fbdf0c8da4e317af75b6a4b6f2b

## Gate summary

- Data-quality: 20 checks, 0 failures.
- Dynamic remote QA: 20 checks, 0 failures.
- Workbook: 31 checks, 0 failures.
- Hidden truth: 5 cases, 5 matches, 0 false negatives.
- Automated tests: 7 passed.
- Release controls: 13 mechanical PASS, 1 candidate WARN for post-run manifest linkage.
- External validation: 9 registered rows; tax amendment watch added without changing effective model inputs.
- Native workbook: 22 sheets, 116798 bytes; blob 4021117f54806736cad5d213ad307a7e31738550.
- Construction schedule: 240 rows; capitalised IDC proxy rate 8.5%; sources and uses reconciled.
- Portfolio: 11 selected projects, 13.10 MWp, pooled DSCR 1.300x, sponsor NPV -66.202345 BVND.
- Remote 8,760 streams: four artifact-only streams, each 175,200 rows: Parquet load/solar plus deterministic CSV.GZ compatibility streams; index validation PASS.
- Remote index SHA-256: d5f0e3822b126239c85756feda029fc40c793aa28f707cec0fd40b081e338cc0.
- File-level reproducibility: push run 33360401233 and independent workflow_dispatch run 33360504910 / job 99390787043 matched the index, native workbook bytes and all four hourly stream bytes (6/6 compared files).
- Tariff: WATCH pending billed implementation confirmation.
- Tax: WATCH for the official 2026-08-28 draft amendment; current registered tax rules remain unchanged in the model.
- Release status: candidate.
- recruiter_ready: false.

The artifact is remote-only and contains synthetic inputs, aggregate validation, controlled outputs and review streams. It excludes credentials and private hidden raw truth. Hourly streams are available through the workflow artifact, not the desktop workspace.

Live recruiter site (aggregate-only): https://susayold.github.io/vietgreen-ci-solar-project-finance/

## Official source live check

- Remote metadata-only crawl: workflow 33361780986 / job 99394389541; artifact official-source-live-check ID 9746924931, digest sha256:95aa484f7a2ac8db0cc1679ad865f8ffe64eb50cb1e3355eb7307f73cd48f00e.
- 10 controlled official URLs were checked in memory: 9 PASS and 1 non-blocking WARN for the NREL comparator endpoint DNS; raw_snapshot_stored=FALSE for every row. Live-check SHA-256: 749c4ebf52ef3e640c7973d9d470f991c80fdf3e1acb80d3f993f0cda97c0701.
