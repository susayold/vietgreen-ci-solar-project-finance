# Native workbook specification

The native workbook is model/vietgreen_core_model.xlsx.

## Build rule

GitHub Actions executes analytics/build_native_workbook.py on an ephemeral runner. The builder reads remote repository CSV outputs and evidence, writes a valid OOXML workbook, and validates it before publishing the artifact and committing the refreshed workbook to main. The Python and CSV logic remains the source of truth.

## Sheet set

The current workbook contains 22 sheets covering cover, assumptions, regulatory/tariff/source registers, energy/load/PPA, capex/sources-and-uses, cash flow, debt sizing/schedule/coverage, reserves, returns, FX, scenarios, concentration, selection, IC decisions, QA and release controls.

## Integrity controls

- Release candidate: 1.2.0.
- Workflow run: 33346497581.
- Workflow source commit: 09b91dfcccaa12259df0b5ac87a1fd612f73ba13.
- Workbook refresh commit: 67d341a728cfd6863a89128f2c79a2892715c946.
- Artifact digest: sha256:3fd6cb3507a5bf90241495fca332bb50dc7cfcf67fd37b31a38ae183f93580ef.
- Workbook validation: 31 checks, 0 failures.
- Workbook blob: 2af6371982c35eb117f50dff344dcc0cfae8108f.
- Workbook size: 106636 bytes.
- Remote 8,760 artifact index: validation/REMOTE_8760_INDEX.csv; two streams with 175,200 rows each.

## Use boundary

The workbook is a review artifact, not a substitute for an independent model audit, bankable P90, executed PPA, lender data-room or legal/tax/technical diligence.
