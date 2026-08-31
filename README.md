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
- Pooled feedback: converged in 2 iterations.
- 8,760 engine: executed in memory for every project, with P50 and P90 profiles.
- Quality gates: 20/20 data-quality checks; 31/31 workbook structural checks; 20/20 dynamic remote QA checks; 5/5 hidden-truth classifications; 7 automated tests; 13/13 mechanical release controls pass, with 1 candidate-manifest warning.

## What is implemented

The candidate implements synthetic-input lineage, locked input hashes, exact Decision 963 midpoint schedule mapping, current billed-reference separation, tax/VAT/working-capital cash flow, 8,760 energy profiles, P50/P90 cases, bottom-up construction CAPEX, a 12-month construction curve, capitalised IDC proxy, standalone debt sizing, registered LLCR/PLCR discount rates, pooled debt re-sizing with feedback, DSCR/LLCR/PLCR/leverage gates, FX sensitivities, scenario isolation, portfolio concentration/common-factor analysis, pairwise-swap improvement, IC and lender views, a hidden-truth firewall, remote 8,760 artifact export, and a native 22-sheet workbook generated on an ephemeral GitHub Actions runner.

The Python and CSV logic is the source of truth. The current construction curve and IDC rate remain synthetic until replaced by EPC drawdown and financing evidence.

## Claim boundary

This is a reviewable candidate, not a lender approval, bankable P90 case, legal opinion, tax opinion, technical certification, site-diligence result, or formally audited model. The open gates are billed-tariff confirmation, independent final review, and lender/legal/tax/technical/site diligence. The release manifest therefore sets recruiter_ready to false.

## Latest remote verification

- Workflow run: https://github.com/susayold/vietgreen-ci-solar-project-finance/actions/runs/33353141725
- Workflow job: 99370175281.
- Workflow source commit: 95af3267ebfc615e194323f1fa503c2d13bad5bb.
- Workbook refresh commit: 1139ba3424d54d0387d24499dd18284e8f79ed72.
- Artifact: vietgreen-core-outputs, ID 9744264357.
- Artifact digest: sha256:18227bd8b766ac664becc7f706849d5382fe4f71ef6d6b97fe9ce303ea136ca8.
- Native workbook blob: see release/MODEL_RELEASE_MANIFEST.json.

## Reproducibility and storage

- Master seed: 260831.
- Synthetic input hashes are locked in config/SYNTHETIC_INPUT_HASHES.csv.
- The workflow creates derived hourly streams on the GitHub-hosted runner and uploads them as remote artifacts; local_storage is NONE.
- No credentials, private hidden truth, proprietary raw data or personal information is part of this public repository.

Key links:

- [Recruiter-facing site](website/index.html)
- [Native workbook](model/vietgreen_core_model.xlsx)
- [Release manifest](release/MODEL_RELEASE_MANIFEST.json)
- [Backend artifact manifest](release/BACKEND_OUTPUT_MANIFEST.csv)
- [Plan implementation trace](docs/PLAN_IMPLEMENTATION_TRACE.md)
- [Final DOD status matrix](validation/FINAL_DOD_STATUS_MATRIX.csv)
- [Remote source-fetch log](evidence/REMOTE_SOURCE_FETCH_LOG_2026-08-31.csv)
- [Data-room index](reports/DATA_ROOM_INDEX.md)
- [IC decision table](outputs/IC_DECISION_TABLE.csv)
