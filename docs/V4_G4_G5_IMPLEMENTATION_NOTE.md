# V4 G4/G5 implementation note

The V4 workbook is a separate formula-driven candidate model generated on the remote GitHub Actions runner. It contains linked input, cash-flow, debt-service, returns, scenario and dashboard sheets, explicit year-zero project/equity cash flows, automatic/full recalculation flags, switches, and an aggregate Equity NPV chart.

After build, LibreOffice recalculates the workbook on the remote runner. A separate Python validation module reconstructs V4 ledgers from versioned synthetic inputs and compares P50 energy, Year-1 CFADS, Project NPV/IRR and Equity NPV/IRR against workbook cached values. Formula errors or reconciliation differences fail the workflow. The workbook remains synthetic screening evidence and does not claim bankability or external transaction readiness.
