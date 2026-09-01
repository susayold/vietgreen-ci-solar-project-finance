# V5 Migration Status — V5.1.1

Status: FINAL_RELEASE_CLOSED on `v5.1.1-data-model-content-rebuild`.

Validated exact release source: `14fe1e5e19ab0ecdd67f79be6be4d0aa5c59f2cb`. CI run `33546474139` passed the full suite, reproducibility comparison, current-surface scan, 56 pytest tests and 12 semantic checks. Pages run `33546532792` passed exact-SHA deployment and live route verification.

Completed: selected-data and yield audits, observed-vs-overlay model contract, tax engine, PPA frontier, leveraged Sponsor/Lender floors, LLCR/PLCR separation, explicit debt/timing scenarios, common-USD diligence shortlist, 26-sheet workbook, 14 required outputs including 20 × 8,760 rows, current report/website migration, runtime manifests and G0-G9 controls.

PPA remains FRONTIER_ONLY. Exact PPA, lender terms, site rights, customer telemetry, engineering yield validation and bankability remain open. V4.1.3 and V5.1.0 are preserved as immutable history. No project data is written to local storage; CI artifacts are remote and ephemeral.