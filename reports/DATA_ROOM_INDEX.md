# Data-room index

## Remote-only location

Repository: https://github.com/susayold/vietgreen-ci-solar-project-finance

The project data-room is represented by the repository, the workflow artifact and the one linked Google Drive execution-control document. No project-data copy is intentionally retained in the local workspace.

## Latest release evidence

- Source register: SR-1.9-tax-tariff-watch; latest live evidence row: SRC-REFRESH-EVN-20260831; tariff-chain legal dependency: SRC-TAR-278.

- Release candidate: 1.2.0.
- Workflow source commit: d2fd8835bb0591bc850a90b13cb37f3b5ec2310b.
- Workbook refresh commit: d2fd8835bb0591bc850a90b13cb37f3b5ec2310b.
- Workflow run: 33360401233.
- Workflow job: 99390501627.
- Artifact: vietgreen-core-outputs, ID 9746487203.
- Artifact digest: sha256:3396dce1eee9420c8c16532c30e38d7be33d4fbdf0c8da4e317af75b6a4b6f2b.
- Native workbook: 22 sheets; current blob is recorded in release/MODEL_RELEASE_MANIFEST.json.
- Data quality: 20 checks, 0 failures.
- Dynamic remote QA: 20 checks, 0 failures.
- Workbook validation: 31 checks, 0 failures.
- Hidden truth: 5 cases, 5 classification matches, 0 false negatives.
- Automated tests: 7 passed.
- Mechanical release controls: 13 PASS, 1 WARN.
- External gate tracker: 8 open transaction/evidence gates; no gate is closed by synthetic data alone.
- Official source refresh: `.github/workflows/source-refresh.yml` crawls the controlled public URLs remotely and commits metadata only to `evidence/REMOTE_SOURCE_LIVE_CHECK.csv`.
- Locked input hashes: PASS.
- Remote 8,760 artifact streams: 175,200 rows each in plan-specified Parquet plus CSV.GZ compatibility format; local_storage NONE.

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
