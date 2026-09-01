# Executive Summary — V5.1.1

## Outcome

V5.1.1 rebuilds the real-data model contract and current content surfaces. The selected set remains 20 projects across the preserved 54-candidate / 441-observation research history. All project facts remain traceable to source IDs; modeled load, self-consumption, CAPEX, tax, rates, FX and discount rates are explicit overlay inputs.

## Economics boundary

The engine reports customer ceiling, leveraged Sponsor Floor, explicit Lender Floor, debt constraints, loan-life LLCR, project-life PLCR and scenario results. It does not invent an exact PPA price. Every frontier result carries REFERENCE_CASE_NOT_ACTUAL_PPA and INDETERMINATE_MISSING_COMMERCIAL_DATA.

## Remediation completed

- Tax-loss carryforward is a positive balance and cannot create tax in a loss year.
- Sponsor Floor is solved on leveraged equity NPV at the equity hurdle.
- Lender Floor is solved against a stated standardized leverage target.
- LLCR uses loan-life CFADS; PLCR uses project-life CFADS.
- FIXED_DEBT_SCHEDULE, NO_NEW_DEBT and RESIZED_DEBT have explicit scenario semantics.
- COD delay shifts operating timing; interest shocks respect fixed/floating debt treatment.
- Portfolio output is a common-USD diligence shortlist with budget and exposure controls, not an investment approval.

The output is recruiter-ready analysis, not bankability, IC approval, lender credit approval, legal/tax advice or technical sign-off.
