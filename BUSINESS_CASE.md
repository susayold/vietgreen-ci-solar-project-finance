# Business Case — V5.1.1

VietGreen's use case is a source-backed diligence and recruiter-facing comparison of publicly disclosed C&I/distributed solar projects. The value is a transparent common data model and repeatable economics layer, not a claim that confidential transaction data is available.

## Data model

Observed capacity, generation, public PPA status and source lineage are held in project_master_real.csv. Modeled load, self-consumption, project cost and underwriting terms are held in project_assumption_overlay.csv with evidence class, input origin, confidence and effective date. Missing commercial data stays missing.

## Decision outputs

The model creates a negotiation frontier from a customer ceiling and two economic floors. The exact PPA remains unknown. The correct decision for frontier-only cases is INDETERMINATE_MISSING_COMMERCIAL_DATA. Shortlists identify diligence priority and commercial negotiation priority; they are not an investment portfolio.

## Controls

The selected-20 audit, yield sanity audit, load reconstruction register, conflict register, current-surface reconciliation and Excel/Python reconciliation are release gates. The Arisudhana annual generation claim is preserved as a source-confirmed physical outlier and requires engineering validation.
