# Data-room index

## Remote-only location

Repository: https://github.com/susayold/vietgreen-ci-solar-project-finance

The project data-room is represented by the repository, the workflow artifact and the one linked Google Drive execution-control document. No project-data copy is intentionally retained in the local workspace.

## Latest release evidence

- Source register: SR-1.10-tax-tariff-watch; latest live evidence row: SRC-REFRESH-EVN-20260831; tariff-chain legal dependency: SRC-TAR-278.

- Release candidate: 1.2.0.
- Workflow source commit: b7ac7ab507487d4ba021064c8cdeadb29fcefc44.
- Workbook refresh commit: b7ac7ab507487d4ba021064c8cdeadb29fcefc44.
- Workflow run: 33362871604.
- Workflow job: 99397534044.
- Artifact: vietgreen-core-outputs, ID 9747272913.
- Artifact digest: sha256:d98e61282a9fbc564bc5078a805d64009ef1f2906a288cb3ec541f4704db93d6.
- Native workbook: 22 sheets, 116807 bytes, SHA-256 e01406f644ab6a9d810ca6dd5c31d240ec2ed99ff7f73e593d0f756cae2ff03a; current blob is recorded in release/MODEL_RELEASE_MANIFEST.json.
- Data quality: 20 checks, 0 failures.
- Dynamic remote QA: 20 checks, 0 failures.
- Workbook validation: 31 checks, 0 failures.
- Hidden truth: 5 cases, 5 classification matches, 0 false negatives.
- Automated tests: 7 passed.
- Mechanical release controls: 13 PASS, 1 WARN.
- External gate tracker: 8 open transaction/evidence gates; no gate is closed by synthetic data alone.
- Official source refresh: `.github/workflows/source-refresh.yml` crawls the controlled public URLs remotely and commits metadata only to `evidence/REMOTE_SOURCE_LIVE_CHECK.csv`. Latest run 33362227008: 9 PASS / 2 non-blocking WARNs (MOIT runner network-unreachable; NREL DNS); raw snapshots FALSE.
- Locked input hashes: PASS.
- Remote 8,760 artifact streams: 175,200 rows each in plan-specified Parquet plus CSV.GZ compatibility format; local_storage NONE.
- Same-head remote comparator: 33363289510 / job 99398752408; 6/6 target files matched, comparison metadata artifact 9747403047, raw artifact contents not stored.

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
