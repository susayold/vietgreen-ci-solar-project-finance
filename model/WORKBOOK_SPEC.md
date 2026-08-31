# Native workbook specification

The native workbook is model/vietgreen_core_model.xlsx.

## Build rule

GitHub Actions executes analytics/build_native_workbook.py on an ephemeral runner. The builder reads remote repository CSV outputs and evidence, writes a valid OOXML workbook, and validates it before publishing the artifact and committing the refreshed workbook to main. The Python and CSV logic remains the source of truth.

## Sheet set

The current workbook contains 22 sheets covering cover, assumptions, regulatory/tariff/source registers, energy/load/PPA, capex/sources-and-uses, cash flow, debt sizing/schedule/coverage, reserves, returns, FX, scenarios, concentration, selection, IC decisions, QA and release controls.

## Integrity controls

- Workflow run: 33344817775.
- Workflow source commit: 504d6129c3660a02cd3ac71208eddccbd01fae80.
- Workbook refresh commit: 00c99a29629921571dc26cdb39a32a1b2cbf6d7d.
- Artifact digest: sha256:62f6f9b892623d5a81ee9ef10e9aad0b370b0cc707a865a1aad0217000a485fc.
- Workbook validation: 31 checks, 0 failures.
- Workbook blob: 3134dcfdc60b6f3bfa2d75e36179649ca9c1dfa9.
- Workbook size: 105385 bytes.

## Use boundary

The workbook is a review artifact, not a substitute for an independent model audit, bankable P90, executed PPA, lender data-room or legal/tax/technical diligence.
