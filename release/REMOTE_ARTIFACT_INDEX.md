# Remote artifact index

Release candidate: 1.2.0
Date: 2026-08-31
Source register: SR-1.10-tax-tariff-watch (latest live source: SRC-REFRESH-EVN-20260831; corroborating EVN Decision 963 page SRC-REFRESH-EVN-963-20260423; latest tax watch: SRC-REFRESH-TAX-20260831)
Repository: https://github.com/susayold/vietgreen-ci-solar-project-finance
Workflow source commit: b7ac7ab507487d4ba021064c8cdeadb29fcefc44
Workbook/remote-output refresh commit: d4e4e2f1e5981509ecc53c5fec4d1db00faaf4c8
Workflow run: 33362871604
Workflow job: 99397534044
Artifact: vietgreen-core-outputs, ID 9747272913
Artifact digest: sha256:d98e61282a9fbc564bc5078a805d64009ef1f2906a288cb3ec541f4704db93d6

## Gate summary

- Data-quality: 20 checks, 0 failures.
- Dynamic remote QA: 20 checks, 0 failures.
- Workbook: 31 checks, 0 failures.
- Hidden truth: 5 cases, 5 matches, 0 false negatives.
- Automated tests: 7 passed.
- Release controls: 13 mechanical PASS, 1 candidate WARN for post-run manifest linkage.
- External validation: 9 registered rows; tax amendment watch added without changing effective model inputs.
- Native workbook: 22 sheets, 116807 bytes; blob c45b996de6cc364062966638da73666629179638.
- Construction schedule: 240 rows; capitalised IDC proxy rate 8.5%; sources and uses reconciled.
- Portfolio: 11 selected projects, 13.10 MWp, pooled DSCR 1.300x, sponsor NPV -66.202345 BVND.
- Remote 8,760 streams: four artifact-only streams, each 175,200 rows: Parquet load/solar plus deterministic CSV.GZ compatibility streams; index validation PASS.
- Remote index SHA-256: d5f0e3822b126239c85756feda029fc40c793aa28f707cec0fd40b081e338cc0.
- File-level reproducibility: push run 33362871604 and same-head workflow_dispatch run 33362978966 / job 99397849553 were compared by remote comparator run 33363289510 / job 99398752408; the index, native workbook bytes and all four hourly stream bytes matched (6/6 compared files).
- Master Plan V3 DoD audit: 65 rows, 62 PASS, 2 PARTIAL and 1 PENDING; workflow 33364273193 / job 99401598762 passed all evidence-path and status-consistency checks; CSV SHA-256 ce48a0fa0ca91f68538d35d09829ffaebb4367cca62918023196ede422b0153f, blob 063a51a4950b3be8fce07499aa06acb8477c3d0b.
- Reproducibility comparator metadata: artifact 9747403047, digest sha256:6ac16bc4879ef269180cee5032d177a57b05a372dd8bcc69cc45c7adc99bf0a3; CSV SHA-256 eb571d45c45d54babb7e7dc23373d9ce35cec6fdcc2155420bca7546d42f79c0, blob e9885d5a33d94f5fc8169d1121a036e135e68ba8, 1,389 bytes; raw artifact contents were not stored.
- Tariff: WATCH pending billed implementation confirmation.
- Tax: WATCH for the official 2026-08-28 draft amendment; current registered tax rules remain unchanged in the model.
- Release status: candidate.
- recruiter_ready: false.

The artifact is remote-only and contains synthetic inputs, aggregate validation, controlled outputs and review streams. It excludes credentials and private hidden raw truth. Hourly streams are available through the workflow artifact, not the desktop workspace.

Live recruiter site (aggregate-only): https://susayold.github.io/vietgreen-ci-solar-project-finance/

## Master Plan V3 DoD audit

- Full checkbox-level audit: `validation/PLAN_DOD_AUDIT.csv`.
- 65 rows cover DoD 42.1–42.9; 62 PASS, 2 PARTIAL and 1 PENDING.
- Remote validation workflow: 33364273193 / job 99401598762; all 190 evidence-path references were found on the GitHub source of truth.

## Official source live check

- Remote metadata-only crawl: workflow 33362227008 / job 99395656762; artifact official-source-live-check ID 9747079173, digest sha256:736250385f4b4cd684fc7abd1b187cf80f0d2d1a1acd48520816b7bb295e2ee5.
- 11 controlled official URLs were checked in memory: 9 PASS and 1 non-blocking WARN for the NREL comparator endpoint DNS; raw_snapshot_stored=FALSE for every row. Live-check SHA-256: f991a4a071a52432b8486e0800dc79d7750c311c120b7c4b615b4f0ba80267fd.
