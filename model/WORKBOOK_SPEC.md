# Native workbook specification

The native workbook is model/vietgreen_core_model.xlsx.

## Build rule

GitHub Actions executes analytics/build_native_workbook.py on an ephemeral runner. The builder reads remote repository CSV outputs and evidence, writes a valid OOXML workbook, and validates it before publishing the artifact and committing the refreshed workbook to main. The Python and CSV logic remains the source of truth.

## Sheet set

The current workbook contains 22 sheets covering cover, assumptions, regulatory/tariff/source registers, energy/load/PPA, capex/sources-and-uses, cash flow, debt sizing/schedule/coverage, reserves, returns, FX, scenarios, concentration, selection, IC decisions, QA and release controls.

## Integrity controls

- Release candidate: 1.2.0.
- Workflow run: 33354033001 / job 99372662335.
- Workflow source commit: 95af3267ebfc615e194323f1fa503c2d13bad5bb.
- Workbook refresh commit: bc5d8207814cb43b645199b0b4d23921bc3606aa.
- Artifact digest: sha256:c7a9ddd43d97a414603e5ba693fc0559208857e86ca7996ae6786850980bde9d.
- Workbook validation: 31 checks, 0 failures.
- Workbook blob: a9ff3f3bcb6207588dd9b6c20c6768dc5fad60df.
- Workbook size: 116230 bytes.
- Remote 8,760 artifact index: validation/REMOTE_8760_INDEX.csv; two streams with 175,200 rows each.

## Use boundary

The workbook is a review artifact, not a substitute for an independent model audit, bankable P90, executed PPA, lender data-room or legal/tax/technical diligence.
