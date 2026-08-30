# MODEL_AUDIT_METHODOLOGY

The audit trail follows source ID → input table → transform → output → decision class.

Remote checks cover:

- expected population and primary-key uniqueness;
- foreign-key coverage across project, offtaker, site, PPA, CAPEX, debt and solar tables;
- source/assumption ID coverage;
- cross-table reconciliation of load, credit, site, tenor, region and CAPEX;
- P90 <= P50 and feasible capacity bounds;
- sources = uses;
- debt roll-forward to zero;
- aggregate DSCR definition;
- scenario isolation and no hidden-truth dependency;
- public claim boundary and release metadata.

A green workflow is evidence that the listed automated checks passed. It is not independent assurance, lender approval, legal advice or a formal audit opinion.
