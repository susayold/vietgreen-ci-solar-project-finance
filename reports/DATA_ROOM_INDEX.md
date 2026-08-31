# Data-room index

## Remote-only location

Repository: https://github.com/susayold/vietgreen-ci-solar-project-finance

The project data-room is represented by the repository, the workflow artifact and the one linked Google Drive execution-control document. No project-data copy is intentionally retained in the local workspace.

## Latest release evidence

- Source register: SR-1.6-live-benchmark-refresh; latest live evidence row: SRC-REFRESH-EVN-20260730.

- Release candidate: 1.2.0.
- Workflow source commit: 95af3267ebfc615e194323f1fa503c2d13bad5bb.
- Workbook refresh commit: bc5d8207814cb43b645199b0b4d23921bc3606aa.
- Workflow run: 33354033001.
- Workflow job: 99372662335.
- Artifact: vietgreen-core-outputs, ID 9744543908.
- Artifact digest: sha256:c7a9ddd43d97a414603e5ba693fc0559208857e86ca7996ae6786850980bde9d.
- Native workbook: 22 sheets; current blob is recorded in release/MODEL_RELEASE_MANIFEST.json.
- Data quality: 20 checks, 0 failures.
- Dynamic remote QA: 20 checks, 0 failures.
- Workbook validation: 31 checks, 0 failures.
- Hidden truth: 5 cases, 5 classification matches, 0 false negatives.
- Automated tests: 7 passed.
- Mechanical release controls: 13 PASS, 1 WARN.
- Locked input hashes: PASS.
- Remote 8,760 artifact streams: 175,200 rows each; local_storage NONE.

## Candidate economics

- 20 synthetic projects evaluated; 15 eligibility-pass; 11 selected after IDC-inclusive uses.
- Selected capacity: 13.10 MWp.
- Equity used: 138.143294 BVND.
- Endogenous pooled debt: 152.457008 BVND.
- Pooled DSCR: 1.30x.
- Base sponsor NPV: -66.202345 BVND.
- Tariff: WATCH pending billed implementation confirmation.
- CAPEX: six-category bottom-up base plus 12-month synthetic construction curve and 8.5% capitalised IDC proxy.

## Evidence map

- evidence/: source, assumption, tariff, regulatory, discount-rate, input-lineage and source-fetch registers.
- data/synthetic/: locked synthetic project, offtaker, solar, PPA, debt, CAPEX and construction inputs.
- outputs/: energy, load, PPA, CAPEX/IDC, debt, cash-flow, reserve, returns, FX, scenarios, selection, concentration and IC outputs.
- validation/: data-quality, hidden-truth, remote QA, release-control, 8,760-index, DOD matrix and workbook-validation outputs.
- model/: native workbook and workbook specification.
- docs/: methodology and plan trace.
- release/: remote artifact, backend and release manifests/notes.
- reports/: IC, lender, financing, recruiter and data-room memos.
- website/: aggregate-only recruiter-facing landing page.

Live recruiter site (aggregate-only): https://susayold.github.io/vietgreen-ci-solar-project-finance/
