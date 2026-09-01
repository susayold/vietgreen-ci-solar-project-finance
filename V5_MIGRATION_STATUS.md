# V5 Migration Status — V5.1.1

Status: FINAL_RELEASE_CLOSED on `v5.1.1-data-model-content-rebuild`.

The exact release head, CI run, artifact IDs and digests are sealed at runtime by the V5.1.1 validation workflow in `release/V5_RUNTIME_RELEASE_MANIFEST.json` and the uploaded release artifacts. The Drive control index records the same remote evidence after readback.

Completed: selected-data and yield audits, observed-vs-overlay model contract, tax engine, PPA frontier, leveraged Sponsor/Lender floors, LLCR/PLCR separation, explicit debt/timing scenarios, common-USD diligence shortlist, 26-sheet workbook, 14 required outputs including 20 × 8,760 rows, current report/website migration, runtime manifests and G0-G9 controls.

PPA remains FRONTIER_ONLY. Exact PPA, lender terms, site rights, customer telemetry, engineering yield validation and bankability remain open. V4.1.3 and V5.1.0 are preserved as immutable history. No project data is written to local storage; CI artifacts are remote and ephemeral.