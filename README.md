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
- Quality gates: 20/20 data-quality checks; 31/31 workbook structural checks; 20/20 dynamic remote QA checks; 5/5 hidden-truth classifications; 7 automated tests; 13/13 mechanical release controls pass, with 1 candidate-manifest warning; official-source live check 20/24 PASS and 4 non-blocking WARNs.

## What is implemented

The candidate implements synthetic-input lineage, locked input hashes, exact Decision 963 midpoint schedule mapping, current billed-reference separation, tax/VAT/working-capital cash flow, 8,760 energy profiles, P50/P90 cases, bottom-up construction CAPEX, a 12-month construction curve, capitalised IDC proxy, standalone debt sizing, registered LLCR/PLCR discount rates, pooled debt re-sizing with feedback, DSCR/LLCR/PLCR/leverage gates, FX sensitivities, scenario isolation, portfolio concentration/common-factor analysis, pairwise-swap improvement, IC and lender views, a hidden-truth firewall, remote 8,760 artifact export, and a native 22-sheet workbook generated on an ephemeral GitHub Actions runner.

The Python and CSV logic is the source of truth. The current construction curve and IDC rate remain synthetic until replaced by EPC drawdown and financing evidence.

## Claim boundary

This is a reviewable candidate, not a lender approval, bankable P90 case, legal opinion, tax opinion, technical certification, site-diligence result, or formally audited model. The open gates are billed-tariff confirmation, independent final review, and lender/legal/tax/technical/site diligence. The release manifest therefore sets recruiter_ready to false.

## Latest remote verification

- Workflow run: https://github.com/susayold/vietgreen-ci-solar-project-finance/actions/runs/33367160495
- Workflow job: 99410087552.
- Workflow source commit: b7ac7ab507487d4ba021064c8cdeadb29fcefc44.
- Workbook refresh commit: 02b3fc9bc9c39728b5796db34184ddd7778e5edb.
- Artifact: vietgreen-core-outputs, ID 9748676847.
- Artifact digest: sha256:3f1f7c193192ca4bd652a131e453e9bd7cd996592f0f2343b081664618fdba70.
- Native workbook: 22 sheets, 117493 bytes; SHA-256 9e72588fd7a084282befa74dd0f97036f15e1f306aac6080fc86fdd75f605c5f; GitHub blob c0d2e2dadf3720a35b9101205efdec108425bec5.
- Same-head reproducibility run: 33367239508 / job 99410324360; remote comparator: 33367293807 / job 99410490341; 6/6 file hashes matched, with raw artifact contents not stored.
- Latest official-source refresh: 33368222168 / job 99413280315; 24 URLs, 20 PASS and 4 non-blocking WARNs; raw snapshots were not stored.
- External-gate validator: 33370201444 / job 99419321412; 8 gate rows, 0 submissions, PASS_EMPTY_SUBMISSIONS; no gate was closed.

## Reproducibility and storage

- Master seed: 260831.
- Plan source fingerprint is recorded in `evidence/PLAN_SOURCE_MANIFEST.csv`; the user-provided plan was read in memory and no raw plan copy was stored by the agent.
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
- [Plan source fingerprint (metadata-only)](evidence/PLAN_SOURCE_MANIFEST.csv)
- [Final DOD status matrix](validation/FINAL_DOD_STATUS_MATRIX.csv)
- [Full Master Plan V3 DoD audit (65 rows; 62 PASS, 2 PARTIAL, 1 PENDING)](validation/PLAN_DOD_AUDIT.csv)
- [Remote source-fetch log](evidence/REMOTE_SOURCE_FETCH_LOG_2026-08-31.csv)
- [Data-room index](reports/DATA_ROOM_INDEX.md)
- [External gate intake register](validation/EXTERNAL_GATE_INTAKE.csv)
- [External gate intake template](evidence/EXTERNAL_GATE_INTAKE_TEMPLATE.md)
- [External gate submissions schema](validation/EXTERNAL_GATE_SUBMISSIONS.csv)
- [Remote external-gate validator](.github/workflows/external-gate-validation.yml)
- [IC decision table](outputs/IC_DECISION_TABLE.csv)
