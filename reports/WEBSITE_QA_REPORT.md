# Website QA report

V4.1 candidate QA contract. This report is generated/verified by the recruiter-pages workflow and remains OPEN for final release until live deployment SHA proof passes.

- Data build: PASS when scripts/build_website_data.py and scripts/write_release_meta.py complete.
- Data contract: PASS when all route JSON files and release-meta.json validate.
- Recruiter surface reconciliation: PASS only when README, Executive Summary, Business Case, selected reports, release metadata and declared website surfaces reconcile to the V4 manifest.
- Stale V3 blocker: fail-closed scan covers the declared recruiter/control inventory; historical reference artifacts are not treated as current recruiter claims.
- Scenario semantics: economicStatus, creditStatus and readinessImpact are separate; no ambiguous legacy status is published.
- PPA zone math: marker positions and ticks are derived from the source frontier bounds.
- JavaScript syntax: checked with node --check website/app.js.
- Local HTTP smoke: index, shared-summary.json, release-meta.json, all route contracts and workbook preview must return HTTP 200.
- Public boundary: no private paths, credentials, localhost or hidden validation payload.
- Current terms boundary: 0 / 20 positive Equity NPV and NO_DEPLOYMENT.
- Negotiated hypothetical: 19 positive Equity NPV rows; four selected IDs VG-005, VG-010, VG-011 and VG-012.
- Transaction boundary: evidence OPEN, bankable transaction FALSE, eight external gates open.
- Final release status: OPEN until live release-meta.gitSha equals GITHUB_SHA and the evidence artifact is uploaded.

The Pages workflow is the only publication path. Core validation is read-only for candidate SHA control.
