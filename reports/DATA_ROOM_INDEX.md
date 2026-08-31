# Data-room index

## Remote-only location

Repository: https://github.com/susayold/vietgreen-ci-solar-project-finance

The project data-room is represented by the repository, the workflow artifact and the one linked Google Drive execution-control document. No project-data copy is intentionally retained in the local workspace.

## Latest release evidence

- Source register: SR-1.7-tax-draft-watch; latest live evidence row: SRC-REFRESH-EVN-20260831.

- Release candidate: 1.2.0.
- Workflow source commit: 59cfa0d5304ecd7e8c05b865d45a1abcc58b8372.
- Workbook refresh commit: d50f918d4a4756a78d4e82ae786136cbf3d38ec7.
- Workflow run: 33357877259.
- Workflow job: 99383381558.
- Artifact: vietgreen-core-outputs, ID 9745707771.
- Artifact digest: sha256:16addbaafa85aeaecde83ce12a5f3c9513988911d2090d915b29899f0dec607e.
- Native workbook: 22 sheets; current blob is recorded in release/MODEL_RELEASE_MANIFEST.json.
- Data quality: 20 checks, 0 failures.
- Dynamic remote QA: 20 checks, 0 failures.
- Workbook validation: 31 checks, 0 failures.
- Hidden truth: 5 cases, 5 classification matches, 0 false negatives.
- Automated tests: 7 passed.
- Mechanical release controls: 13 PASS, 1 WARN.
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
