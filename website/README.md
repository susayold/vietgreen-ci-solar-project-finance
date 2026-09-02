# VietGreen V5.1.3 recruiter website

This is the public presentation layer for the frozen V5.1.3 model release. The
information architecture and visual language follow the established recruiter
surface; all facts, counts, claims and scenario semantics are regenerated in CI
by \`analytics/build_v5_1_3_website_data.py\`.

Routes: overview, case, economics, debt, portfolio, risk, model and evidence.
The browser payload contains aggregate/representative views only. Full model
outputs, native workbook, validation registers and 8,760 rows stay in the
ephemeral GitHub Actions artifact/release chain.

The website is remote-only: no project data is committed as a developer
snapshot and no local source of truth is used. Model source is frozen at
\`v5.1.3-recruiter-final\`; website source and release metadata are separate.

Claim boundary: PUBLIC_DATA_ONLY, PPA mode FRONTIER_ONLY, transaction evidence
OPEN, bankable transaction FALSE, capital allocation DISABLED_FRONTIER_ONLY.
Arisudhana's extreme public observation is preserved and blocked from direct
base economics pending technical review.
