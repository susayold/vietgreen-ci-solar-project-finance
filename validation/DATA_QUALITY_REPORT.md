# DATA_QUALITY_REPORT

Remote-only quality checks for the synthetic pipeline. Grain is one row per project except CAPEX, which is six components per project.

- Checks run: 18
- Passed: 18
- Failed: 0
- Data class: synthetic / simulated; no real customer data.
- Freshness: source-register dates and regulatory/tariff recheck flags govern release; no local snapshot is used.
- Billing firewall: legal effective dates and billed implementation dates are separate; legal-only rows cannot carry billed energy rates.

## Interpretation

A failure is a release blocker until the source or transformation is corrected. The checks cover completeness, uniqueness, foreign-key coverage, lineage, cross-table reconciliation, legal/billing separation and domain validity.
