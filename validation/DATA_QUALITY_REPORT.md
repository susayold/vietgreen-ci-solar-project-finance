# DATA_QUALITY_REPORT

Remote-only quality checks for the synthetic pipeline. Grain is one row per project except CAPEX, which is six components per project.

- Checks run: 13
- Passed: 13
- Failed: 0
- Data class: synthetic / simulated; no real customer data.
- Freshness: source-register dates and regulatory/tariff recheck flags govern release; no local snapshot is used.

## Interpretation

The checks cover completeness, uniqueness, foreign-key coverage, source/assumption lineage, cross-table reconciliation, and domain validity. A failure is a release blocker until the source or transformation is corrected.
