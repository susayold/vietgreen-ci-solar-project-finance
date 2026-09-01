# Data Room Index — V5.1.1

## Current remote-only data room

Repository: https://github.com/susayold/vietgreen-ci-solar-project-finance

This is the current V5.1.1 recruiter-final data room. Canonical project data and derived artifacts are stored on GitHub; CI workspaces are ephemeral and no project data is retained in the local workspace.

## Current authoritative scope

- Release: `v5.1.1-recruiter-final`
- Candidate history preserved: 54
- Selected projects: 20
- Raw observations: 441
- Selected field audit and yield sanity audit: retained in `validation/`
- Arisudhana: preserved as an observed high-yield claim, explicitly flagged for engineering review; not silently normalized or promoted to a benchmark.

## Data and model map

- Inputs: `data/public/`, `evidence/`, `research/`
- Model and outputs: `analytics/`, `outputs/`, `artifacts/v5_1_1_model/`
- Validation: `validation/V5_1_1_SELECTED_PROJECT_DATA_AUDIT.csv`, `validation/V5_1_1_YIELD_SANITY_AUDIT.csv`, current-surface reconciliation, content migration matrix, remediation register, final DoD and freeze manifest
- Workbook: `artifacts/v5_1_1_model/vietgreen_v5_1_1_model.xlsx`
- Website data: `website/data/`
- Current reports: IC memo, lender memo, recruiter package, CV bullets, standardized underwriting terms and recruiter surface reconciliation

## Economic and claim boundary

PPA mode is `FRONTIER_ONLY`; exact PPA price is not disclosed or claimed. Sponsor Floor is leveraged equity NPV at the equity hurdle. Lender Floor is the minimum tariff supporting target standardized leverage. Debt separates DSCR, loan-life LLCR and project-life PLCR. Fixed-debt, no-new-debt and resized-debt scenario semantics are explicit.

Decision boundary: `INDETERMINATE_MISSING_COMMERCIAL_DATA`. Transaction evidence is `OPEN`; `BANKABLE_TRANSACTION_READY=FALSE`. This is standardized public-data screening/diligence evidence, not lender commitment, IC approval, legal, tax, technical or bankability sign-off.

## Release evidence

After the final CI and Pages runs, the GitHub Release and linked Drive control header record the exact tag, source SHA, workflow run/job, primary and runtime artifact IDs/digests, freeze timestamp, workbook hash, G0-G9, test counts, website proof and live SHA. The runtime manifest artifact is authoritative for run-specific identifiers.

Historical `v5.1.0-recruiter-final` and `v4.1.3-recruiter-final` remain preserved and are not rewritten.

Website: https://susayold.github.io/vietgreen-ci-solar-project-finance/
