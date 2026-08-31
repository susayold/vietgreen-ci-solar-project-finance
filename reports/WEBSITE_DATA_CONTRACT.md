# Website data contract

`scripts/build_website_data.py` is the single build-time adapter between released V4 outputs and the static website. It converts VND to BVND, percentages to display units, and attaches the source paths and evidence class to every page contract.

The shared contract is the cross-page spine: release ID, selected IDs, current-terms decision, selected equity/debt/CFADS, DSCR, recruiter readiness and the transaction/bankability boundary. Page JSON files contain only route-specific derived views.

The public payload intentionally excludes raw 8,760 streams, private transaction files, credentials and hidden validation results. A deterministic daily shape on Economics is explicitly labelled as communication-only; annual energy and load values are sourced from the released aggregate summaries.
