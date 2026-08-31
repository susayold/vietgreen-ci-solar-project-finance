# V4 Phase 1 implementation note

## Authority and scope

The user request is the controlling instruction: continue the remediation plan, keep project data and project activity on the connected GitHub repository and Google Drive, and do not create a local project-data copy. The attached V4 Markdown plan is treated as a specification and checklist, not as an instruction to override the user or to fabricate missing external evidence.

## Remote-only execution boundary

- Code, synthetic inputs, aggregate outputs, QA reports, and workflow history are versioned in GitHub.
- The V4 engine holds hourly arrays only in memory on the GitHub Actions runner.
- No raw hourly profiles, invoices, utility bills, contracts, credit files, or transaction evidence are created or committed.
- The V4 outputs deliberately retain OPEN_EXTERNAL_GATE labels where a real transaction source is not available.

## Phase 1 delivered

- Ten predeclared load archetypes with weekday/weekend, operating-window, seasonality, and night-baseload parameters.
- Project-specific deterministic cloud phase from the locked seed; only profile hashes and aggregates are exported.
- Component uncertainty budget across resource, availability, degradation, and clipping, combined by root-sum-square.
- P50/P75/P90/P99 generation ordering and P90 load-matching summary.
- Customer ceiling, sponsor floor, and lender floor solved independently through deterministic 48-iteration bisection when bracketed; boundary cases are explicitly labelled.
- Project NPV/IRR and Equity NPV/IRR from explicit annual cash-flow vectors.
- Portfolio selection with hard gates, concentration constraints, positive Equity NPV gate, and valid NO_DEPLOYMENT empty-solution state.

## Deliberate non-claims

This phase does not claim bankability, legal billing confirmation, lender credit approval, transaction readiness, or recruiter readiness. Those gates require external transaction evidence and remain open until uploaded through the controlled evidence process.
