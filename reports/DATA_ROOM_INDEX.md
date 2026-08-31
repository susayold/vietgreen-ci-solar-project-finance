# Data-room index

## Remote-only location

Repository: https://github.com/susayold/vietgreen-ci-solar-project-finance

The project data-room is represented by the repository, the workflow artifact and the one linked Google Drive execution-control document. No project-data copy is intentionally retained in the local workspace.


## Plan provenance

- The user-provided Master Plan V3 was read in memory; only its SHA-256/size metadata is recorded in `evidence/PLAN_SOURCE_MANIFEST.csv`. No raw plan copy was stored by the agent.

## Latest release evidence

- Source register: SR-1.15-alternate-source-recheck; latest live evidence row: SRC-IRENA-2024-PUBLICATION; corroborating EVNSPC rows: SRC-REFRESH-EVNSPC-20260715, SRC-REFRESH-EVNSPC-PRICING-20260831, SRC-REFRESH-EVNSPC-TRAINING-20260527 and SRC-REFRESH-EVNSPC-IT-20260525; tariff-chain legal dependency: SRC-TAR-278; rolling tax/FX references: SRC-TAX-067, SRC-TAX-320, SRC-TAX-141, SRC-TAX-020, SRC-FX-008 and SRC-FX-019.

- Release candidate: 1.2.0.
- Workflow source commit: b7ac7ab507487d4ba021064c8cdeadb29fcefc44.
- Workbook refresh commit: 02b3fc9bc9c39728b5796db34184ddd7778e5edb.
- Workflow run: 33367160495.
- Workflow job: 99410087552.
- Artifact: vietgreen-core-outputs, ID 9748676847.
- Artifact digest: sha256:3f1f7c193192ca4bd652a131e453e9bd7cd996592f0f2343b081664618fdba70.
- Native workbook: 22 sheets, 117493 bytes, SHA-256 9e72588fd7a084282befa74dd0f97036f15e1f306aac6080fc86fdd75f605c5f; current blob is recorded in release/MODEL_RELEASE_MANIFEST.json.
- Data quality: 20 checks, 0 failures.
- Dynamic remote QA: 20 checks, 0 failures.
- Workbook validation: 31 checks, 0 failures.
- Hidden truth: 5 cases, 5 classification matches, 0 false negatives.
- Automated tests: 7 passed.
- Mechanical release controls: 13 PASS, 1 WARN.
- External gate tracker: 8 open transaction/evidence gates; no gate is closed by synthetic data alone.
- Official source refresh: `.github/workflows/source-refresh.yml` crawls 26 controlled public URLs remotely and commits metadata only to `evidence/REMOTE_SOURCE_LIVE_CHECK.csv`; a weekly recheck is scheduled for Monday 02:00 UTC. Latest run 33371147810 / job 99422352549: 20 PASS / 6 non-blocking WARNs (two MOIT runner network-unreachable pages, NREL DNS and IRENA HTTP 403); artifact 9750130974, digest sha256:24d20a3bf9ee66f5eb94af620a40c3cc1352856ea97dcc413af02b4304d5b972; raw snapshots FALSE.
- Locked input hashes: PASS.
- Remote 8,760 artifact streams: 175,200 rows each in plan-specified Parquet plus CSV.GZ compatibility format; local_storage NONE.
- Same-head remote comparator: 33367293807 / job 99410490341; 6/6 target files matched, baseline artifact 9748676847 and repeat artifact 9748704397; comparison metadata artifact 9748718166, raw artifact contents not stored.
- Full Master Plan V3 DoD audit: 65 rows, 62 PASS, 2 PARTIAL and 1 PENDING; workflow 33371476512 / job 99423375898 passed all 190 evidence-path checks. See validation/PLAN_DOD_AUDIT.csv.


## External gate intake

- Remote-only intake register: `validation/EXTERNAL_GATE_INTAKE.csv`.
- Acceptance contract: `evidence/EXTERNAL_GATE_INTAKE_TEMPLATE.md`.
- Submission schema: `validation/EXTERNAL_GATE_SUBMISSIONS.csv`; remote validator: `.github/workflows/external-gate-validation.yml`.
- External-gate validator run 33371508632 / job 99423466049 passed with 8 gate rows and 0 submissions; all gates remain OPEN.
- These files contain metadata and acceptance rules only; private transaction documents must remain in controlled Drive storage and are not uploaded to this public repository.

## Candidate economics

- 20 synthetic projects evaluated; 15 eligibility-pass; 11 selected after IDC-inclusive uses.
- Selected capacity: 13.10 MWp.
- Equity used: 138.143294 BVND.
- Endogenous pooled debt: 152.457008 BVND.
- Pooled DSCR: 1.30x.
- Base sponsor NPV: -66.202345 BVND.
- Tariff: WATCH pending billed implementation confirmation.
- Tax: current registered rules retained; 2026-08-28 draft amendment is WATCH-only and not treated as effective law.
- CAPEX: six-category bottom-up base plus 12-month synthetic construction curve and 8.5% capitalised IDC proxy.

## Evidence map

- evidence/: source, assumption, tariff, regulatory, discount-rate, input-lineage, source-fetch and remote live-check registers.
- data/synthetic/: locked synthetic project, offtaker, solar, PPA, debt, CAPEX and construction inputs.
- outputs/: energy, load, PPA, CAPEX/IDC, debt, cash-flow, reserve, returns, FX, scenarios, selection, concentration and IC outputs.
- validation/: data-quality, hidden-truth, remote QA, release-control, 8,760-index, DOD matrix, workbook-validation outputs and the external-gate tracker.
- model/: native workbook and workbook specification.
- docs/: methodology and plan trace.
- release/: remote artifact, backend and release manifests/notes.
- reports/: IC, lender, financing, recruiter and data-room memos.
- website/: aggregate-only recruiter-facing landing page.

Live recruiter site (aggregate-only): https://susayold.github.io/vietgreen-ci-solar-project-finance/
