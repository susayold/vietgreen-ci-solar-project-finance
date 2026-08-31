# Native workbook specification

The native workbook is model/vietgreen_core_model.xlsx.

## Build rule

GitHub Actions executes analytics/build_native_workbook.py on an ephemeral runner. The builder reads remote repository CSV outputs and evidence, writes a valid OOXML workbook, and validates it before publishing the artifact and committing the refreshed workbook to main. The Python and CSV logic remains the source of truth.

## Sheet set

The current workbook contains 22 sheets covering cover, assumptions, regulatory/tariff/source registers, energy/load/PPA, capex/sources-and-uses, cash flow, debt sizing/schedule/coverage, reserves, returns, FX, scenarios, concentration, selection, IC decisions, QA and release controls.

## Integrity controls

- Release candidate: 1.2.0.
- Workflow run: 33357532792 / job 99382430451.
- Workflow source commit: d1f2df2b38c9c3ca183ddcc257bcf9f3914f7def.
- Workbook refresh commit: d50f918d4a4756a78d4e82ae786136cbf3d38ec7.
- Artifact digest: sha256:4a3d6d0953d5265370012bb8936ccfedfd8d09f6a8f9f9954d270bd6729726c2.
- Workbook validation: 31 checks, 0 failures.
- Workbook blob: c160cb5b630f653c68343381a8d0d514faa54b02.
- Workbook size: 116230 bytes.
- Remote 8,760 artifact index: validation/REMOTE_8760_INDEX.csv; two streams with 175,200 rows each.

## Use boundary

The workbook is a review artifact, not a substitute for an independent model audit, bankable P90, executed PPA, lender data-room or legal/tax/technical diligence.
