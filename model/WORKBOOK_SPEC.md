# Native workbook specification

The native workbook is model/vietgreen_core_model.xlsx.

## Build rule

GitHub Actions executes analytics/build_native_workbook.py on an ephemeral runner. The builder reads remote repository CSV outputs and evidence, writes a valid OOXML workbook, and validates it before publishing the artifact and committing the refreshed workbook to main. The Python and CSV logic remains the source of truth.

## Sheet set

The current workbook contains 22 sheets covering cover, assumptions, regulatory/tariff/source registers, energy/load/PPA, capex/sources-and-uses, cash flow, debt sizing/schedule/coverage, reserves, returns, FX, scenarios, concentration, selection, IC decisions, QA and release controls.

## Integrity controls

- Release candidate: 1.2.0.
- Workflow run: 33352584933 / job 99368667146.
- Workflow source commit: 09a8798d1a11da3ef378fa3989ff5f4085409b40.
- Workbook refresh commit: 5324dbfbc7ec089e8f0b4a277325fa5fda910528.
- Artifact digest: sha256:214ce6e232e3b8423c39a1a1632b844501181a091f844005074c4309d2657ac1.
- Workbook validation: 31 checks, 0 failures.
- Workbook blob: 07b3ac0c7a9c7025932db1685fe21c1d2c0c5b83.
- Workbook size: 115983 bytes.
- Remote 8,760 artifact index: validation/REMOTE_8760_INDEX.csv; two streams with 175,200 rows each.

## Use boundary

The workbook is a review artifact, not a substitute for an independent model audit, bankable P90, executed PPA, lender data-room or legal/tax/technical diligence.
