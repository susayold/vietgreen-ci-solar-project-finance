# VietGreen CI Solar Project Finance

Release candidate 1.2.0, dated 2026-08-31.

This repository is the remote GitHub source of truth for a synthetic Vietnam commercial-and-industrial solar project-finance model. It executes the attached master plan while respecting the user instruction that project data and project activity remain on remote Drive/GitHub. No project data is intentionally stored in the local workspace.

## Request versus attached-plan instructions

The user request controls the operating boundary: create one new Drive file, create one new GitHub repository, read the plan in detail, and execute it remotely without local project-data storage. The attached Markdown plan is treated as the implementation specification and definition of done; it does not override the remote-only boundary or authorize unsupported claims.

## Current candidate snapshot

- Population: 20 synthetic projects; 15 eligibility-pass; 11 selected after IDC-inclusive uses.
- Selected capacity: 13.10 MWp.
- Equity used: 138.143294 BVND.
- Endogenous pooled debt: 152.457008 BVND.
- Pooled DSCR: 1.300000x.
- Base sponsor NPV: -66.202345 BVND.
- Tariff status: WATCH. Decision 963 legal time windows are mapped separately from the current billed reference; numeric avoided-tariff components remain simulated/model-only.
- Tax status: WATCH for the 2026-08-28 draft amendment to Decree 320/2025; no model-tax change was applied.
- Pooled feedback: converged in 2 iterations.
- 8,760 engine: executed in memory for every project, with P50 and P90 profiles.
- Hourly backend: plan-specified Parquet plus CSV.GZ compatibility streams, remote artifact-only; local_storage is NONE.
- Quality gates: 20/20 data-quality checks; 31/31 workbook structural checks; 20/20 dynamic remote QA checks; 5/5 hidden-truth classifications; 7 automated tests; 13/13 mechanical release controls pass, with 1 candidate-manifest warning.

## What is implemented

The candidate implements synthetic-input lineage, locked input hashes, exact Decision 963 midpoint schedule mapping, current billed-reference separation, tax/VAT/working-capital cash flow, 8,760 energy profiles, P50/P90 cases, bottom-up construction CAPEX, a 12-month construction curve, capitalised IDC proxy, standalone debt sizing, registered LLCR/PLCR discount rates, pooled debt re-sizing with feedback, DSCR/LLCR/PLCR/leverage gates, FX sensitivities, scenario isolation, portfolio concentration/common-factor analysis, pairwise-swap improvement, IC and lender views, a hidden-truth firewall, remote 8,760 artifact export, and a native 22-sheet workbook generated on an ephemeral GitHub Actions runner.

The Python and CSV logic is the source of truth. The current construction curve and IDC rate remain synthetic until replaced by EPC drawdown and financing evidence.

## Claim boundary

This is a reviewable candidate, not a lender approval, bankable P90 case, legal opinion, tax opinion, technical certification, site-diligence result, or formally audited model. The open gates are billed-tariff confirmation, independent final review, and lender/legal/tax/technical/site diligence. The release manifest therefore sets recruiter_ready to false.

## Latest remote verification

- Workflow run: https://github.com/susayold/vietgreen-ci-solar-project-finance/actions/runs/33362871604
- Workflow job: 99397534044.
- Workflow source commit: b7ac7ab507487d4ba021064c8cdeadb29fcefc44.
- Workbook refresh commit: d4e4e2f1e5981509ecc53c5fec4d1db00faaf4c8.
- Artifact: vietgreen-core-outputs, ID 9747272913.
- Artifact digest: sha256:d98e61282a9fbc564bc5078a805d64009ef1f2906a288cb3ec541f4704db93d6.
- Native workbook: 22 sheets, 116807 bytes; SHA-256 e01406f644ab6a9d810ca6dd5c31d240ec2ed99ff7f73e593d0f756cae2ff03a; GitHub blob c45b996de6cc364062966638da73666629179638.
- Same-head reproducibility run: 33362978966 / job 99397849553; remote comparator: 33363289510 / job 99398752408; 6/6 file hashes matched, with raw artifact contents not stored.

## Reproducibility and storage

- Master seed: 260831.
- Synthetic input hashes are locked in config/SYNTHETIC_INPUT_HASHES.csv.
- The workflow creates derived hourly streams on the GitHub-hosted runner and uploads them as remote artifacts; local_storage is NONE.
- No credentials, private hidden truth, proprietary raw data or personal information is part of this public repository.

Key links:

- [Recruiter-facing site](website/index.html)
- [Live recruiter site](https://susayold.github.io/vietgreen-ci-solar-project-finance/)
- [Native workbook](model/vietgreen_core_model.xlsx)
- [Release manifest](release/MODEL_RELEASE_MANIFEST.json)
- [Backend artifact manifest](release/BACKEND_OUTPUT_MANIFEST.csv)
- [Plan implementation trace](docs/PLAN_IMPLEMENTATION_TRACE.md)
- [Final DOD status matrix](validation/FINAL_DOD_STATUS_MATRIX.csv)
- [Remote source-fetch log](evidence/REMOTE_SOURCE_FETCH_LOG_2026-08-31.csv)
- [Data-room index](reports/DATA_ROOM_INDEX.md)
- [IC decision table](outputs/IC_DECISION_TABLE.csv)
