# Website QA report

V4.1 final recruiter website QA contract. The Pages workflow is the only publication path and the release is frozen only after live SHA proof.

- Data build: PASS when scripts/build_website_data.py and scripts/write_release_meta.py complete.
- Data contract: PASS when all route JSON files and release-meta.json validate.
- Recruiter surface reconciliation: PASS only when README, Executive Summary, Business Case, selected reports, release metadata and declared website surfaces reconcile to the V4 manifest.
- Stale V3 blocker: fail-closed scan covers the declared recruiter/control inventory; historical reference artifacts are not treated as current recruiter claims.
- Scenario semantics: economicStatus, creditStatus and readinessImpact are separate; no ambiguous legacy status is published.
- PPA zone math: marker positions, required lower bound and ticks are derived from the source frontier bounds; overlapping equivalent bounds are combined into one label.
- Current NPV visual: all current-terms Equity NPV values render as sorted negative horizontal bars extending left from a visible zero line; project ID and value are available as row labels/tooltips.
- Link / asset contract: all local HTML references, hash routes and required JSON/CSS/JS/preview assets are checked before staging.
- Responsive/accessibility critical contract: viewport, language, skip link, keyboard focus, mobile navigation, route focus management, table overflow, reduced motion, responsive breakpoints, image alt text and non-colour status cues are checked statically at 390/430/768/1024/1440 QA widths.
- JavaScript syntax: checked with node --check website/app.js.
- Local HTTP smoke: index, shared-summary.json, release-meta.json, all route contracts and workbook preview must return HTTP 200.
- Public boundary: no private paths, credentials, localhost or hidden validation payload.
- Current terms boundary: 0 / 20 positive Equity NPV and NO_DEPLOYMENT.
- Negotiated hypothetical: 19 positive Equity NPV rows; four selected IDs VG-005, VG-010, VG-011 and VG-012.
- Transaction boundary: evidence OPEN, bankable transaction FALSE, eight external gates open.
- Deployment evidence: live release-meta.gitSha equals GITHUB_SHA and the evidence artifact is uploaded.

The final recruiter release does not imply investment approval, lender approval, IC approval, legal/tax opinion, technical certification, site diligence or bankable P90.
