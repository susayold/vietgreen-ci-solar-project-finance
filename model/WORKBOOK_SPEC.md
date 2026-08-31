# Native workbook specification

The native workbook is model/vietgreen_core_model.xlsx.

## Build rule

GitHub Actions executes analytics/build_native_workbook.py on an ephemeral runner. The builder reads remote repository CSV outputs and evidence, writes a valid OOXML workbook, and validates it before publishing the artifact and committing the refreshed workbook to main. The Python and CSV logic remains the source of truth.

## Sheet set

The current workbook contains 22 sheets covering cover, assumptions, regulatory/tariff/source registers, energy/load/PPA, capex/sources-and-uses, cash flow, debt sizing/schedule/coverage, reserves, returns, FX, scenarios, concentration, selection, IC decisions, QA and release controls.

## Integrity controls

- Release candidate: 1.2.0.
- Workflow run: 33356405815 / job 99379325568.
- Workflow source commit: c9d7e9712c2b6f868a4eaf042204257a8a2965a8.
- Workbook refresh commit: 669e33324c162955981314d31a8e3b40937aeff9.
- Artifact digest: sha256:b98a6c21209a644dfd0a32509d5ee008b928e409fdae825873e053366a319b53.
- Workbook validation: 31 checks, 0 failures.
- Workbook blob: c160cb5b630f653c68343381a8d0d514faa54b02.
- Workbook size: 116230 bytes.
- Remote 8,760 artifact index: validation/REMOTE_8760_INDEX.csv; two streams with 175,200 rows each.

## Use boundary

The workbook is a review artifact, not a substitute for an independent model audit, bankable P90, executed PPA, lender data-room or legal/tax/technical diligence.
