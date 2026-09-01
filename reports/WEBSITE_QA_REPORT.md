# Website QA Report — V5.1.1

The Pages workflow is the publication path for the V5.1.1 recruiter surface. The deployed site is frozen only after live SHA proof.

- Data build and route contract: PASS for the seven required JSON datasets plus the HTML entry point.
- Current surface reconciliation: PASS against the V5.1.1 model/content contract.
- Claim governance: PASS; observed facts, derived values, benchmark assumptions, analyst assumptions and scenarios remain distinct.
- PPA contract: PASS; FRONTIER_ONLY and exact commercial PPA data is not presented as observed.
- Model boundary: PASS; recruiter-ready does not mean bankable, transaction-ready, lender-approved, IC-approved, legal, tax or technical sign-off.
- Responsive browser QA: PASS at 390, 430, 768, 1024 and 1440px using headless Chrome.
- Live deployment: PASS; the Pages workflow verifies HTTP 200 routes and exact SHA through the runtime deployment check. The exact SHA, run ID, artifact ID and digest are sealed in the CI runtime manifest and Drive control index.
- Static QA remains a communication-layer check; the workbook, outputs, validation registers and CI runtime manifest remain authoritative for model evidence.