# Remote artifact index

Release candidate: 1.2.0
Date: 2026-08-31
Source register: SR-1.15-alternate-source-recheck (latest live source: SRC-REG-243; corroborating EVNSPC notice SRC-REFRESH-EVNSPC-20260715, pricing portal SRC-REFRESH-EVNSPC-PRICING-20260831, meter-training notice SRC-REFRESH-EVNSPC-TRAINING-20260527 and IT readiness note SRC-REFRESH-EVNSPC-IT-20260525; latest tax watch: SRC-REFRESH-TAX-20260831, plus rolling tax/FX and benchmark rechecks)
Repository: https://github.com/susayold/vietgreen-ci-solar-project-finance
Workflow source commit: b7ac7ab507487d4ba021064c8cdeadb29fcefc44
Workbook/remote-output refresh commit: 02b3fc9bc9c39728b5796db34184ddd7778e5edb
Workflow run: 33367160495
Workflow job: 99410087552
Artifact: vietgreen-core-outputs, ID 9748676847
Artifact digest: sha256:3f1f7c193192ca4bd652a131e453e9bd7cd996592f0f2343b081664618fdba70

## Gate summary

- Data-quality: 20 checks, 0 failures.
- Dynamic remote QA: 20 checks, 0 failures.
- Workbook: 31 checks, 0 failures.
- Hidden truth: 5 cases, 5 matches, 0 false negatives.
- Automated tests: 7 passed.
- Release controls: 13 mechanical PASS, 1 candidate WARN for post-run manifest linkage.
- External validation: 9 registered rows; tax amendment watch added without changing effective model inputs.
- Native workbook: 22 sheets, 117493 bytes; SHA-256 9e72588fd7a084282befa74dd0f97036f15e1f306aac6080fc86fdd75f605c5f; blob c0d2e2dadf3720a35b9101205efdec108425bec5.
- Construction schedule: 240 rows; capitalised IDC proxy rate 8.5%; sources and uses reconciled.
- Portfolio: 11 selected projects, 13.10 MWp, pooled DSCR 1.300x, sponsor NPV -66.202345 BVND.
- Remote 8,760 streams: four artifact-only streams, each 175,200 rows: Parquet load/solar plus deterministic CSV.GZ compatibility streams; index validation PASS.
- Remote index SHA-256: d5f0e3822b126239c85756feda029fc40c793aa28f707cec0fd40b081e338cc0.
- File-level reproducibility: push run 33367160495 and same-head workflow_dispatch run 33367239508 / job 99410324360 were compared by remote comparator run 33367293807 / job 99410490341; baseline artifact 9748676847 and repeat artifact 9748704397 matched the index, native workbook bytes and all four hourly stream bytes (6/6 compared files).
- Master Plan V3 DoD audit: 65 rows, 62 PASS, 2 PARTIAL and 1 PENDING; workflow 33369402509 / job 99416840692 passed all evidence-path and status-consistency checks; CSV SHA-256 ce48a0fa0ca91f68538d35d09829ffaebb4367cca62918023196ede422b0153f, blob 063a51a4950b3be8fce07499aa06acb8477c3d0b.
- Reproducibility comparator metadata: artifact 9748718166, digest sha256:5b445b9ad1b8b292edf19197ca25b7a7ecf7c4204d9d788baaed21afca483b3e; CSV SHA-256 28b02df8bfa8516586597a374ac11fe02907056f3f787de34675683ab7a9b8df, blob 987e1605aecdd89525e76a9e29737401e9aa882c, 1,389 bytes; raw artifact contents were not stored.
- Tariff: WATCH pending billed implementation confirmation.
- Tax: WATCH for the official 2026-08-28 draft amendment; current registered tax rules remain unchanged in the model.
- Release status: candidate.
- recruiter_ready: false.

The artifact is remote-only and contains synthetic inputs, aggregate validation, controlled outputs and review streams. It excludes credentials and private hidden raw truth. Hourly streams are available through the workflow artifact, not the desktop workspace.

Live recruiter site (aggregate-only): https://susayold.github.io/vietgreen-ci-solar-project-finance/

## Master Plan V3 DoD audit

- Full checkbox-level audit: `validation/PLAN_DOD_AUDIT.csv`.
- 65 rows cover DoD 42.1–42.9; 62 PASS, 2 PARTIAL and 1 PENDING.
- Remote validation workflow: 33369402509 / job 99416840692; all 190 evidence-path references were found on the GitHub source of truth.

## Official source live check

- Remote metadata-only crawl: workflow 33371147810 / job 99422352549; artifact official-source-live-check ID 9750130974, digest sha256:24d20a3bf9ee66f5eb94af620a40c3cc1352856ea97dcc413af02b4304d5b972.
- 24 controlled official URLs were checked in memory: 20 PASS and 6 non-blocking WARNs (two MOIT runner network-unreachable pages, NREL DNS and IRENA HTTP 403); raw_snapshot_stored=FALSE for every row. Live-check SHA-256: 81145632b8e45ba53808ba06aa305d7434ef14f3e44ca21141c7c056d0676236; GitHub blob 9a7f78b57e20ebe35502308412f2b0f536fb37fc; 9,561 bytes.
