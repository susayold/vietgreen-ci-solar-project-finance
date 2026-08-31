# V4 G4/G5 formula workbook and reconciliation red-team report

- Workbook: model/vietgreen_v4_formula_model.xlsx.
- Boundary: generated and recalculated only on the GitHub Actions runner; no desktop/local project-data copy.
- Formula cells checked: 2055; formula error values: 0; reconciliation rows: 240; reconciliation status: PASS.

## Tests

1. Returns formulas use linked CalcInputs/CashFlows values and Excel NPV/IRR functions; they are not pasted CSV results.
2. CashFlows has explicit project and equity year-zero cash flows, annual CFADS and debt-service links.
3. Dashboard case/scenario switches are linked to Assumptions and a formula-driven decision cell.
4. LibreOffice remote recalculation is required before reconciliation; any formula error fails the gate.
5. Python independently rebuilds the same V4 ledgers from versioned synthetic inputs and compares P50, CFADS, Project NPV/IRR and Equity NPV/IRR.

## Non-claims

This is a formula/reconciliation gate for synthetic screening only. It does not close external transaction evidence, bankability, lender approval or recruiter readiness.
