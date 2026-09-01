# Website QA Report — V5.1.1

The Pages workflow is the publication path for the V5.1.1 recruiter surface. The deployed site is frozen only after live SHA proof.

- Data build and route contract: PASS for the seven required JSON datasets plus the HTML entry point.
- Current surface reconciliation: PASS against the V5.1.1 model/content contract.
- Claim governance: PASS; observed facts, derived values, benchmark assumptions, analyst assumptions and scenarios remain distinct.
- PPA contract: PASS; FRONTIER_ONLY and exact commercial PPA data is not presented as observed.
- Model boundary: PASS; recruiter-ready does not mean bankable, transaction-ready, lender-approved, IC-approved, legal, tax or technical sign-off.
- Responsive browser QA: PASS at 390, 430, 768, 1024 and 1440px using headless Chrome.
- Live deployment: PASS; Pages run `33546532792` verified `https://susayold.github.io/vietgreen-ci-solar-project-finance/` and `website/data/release-meta.json` reported SHA `14fe1e5e19ab0ecdd67f79be6be4d0aa5c59f2cb`.
- Static QA remains a communication-layer check; the workbook, outputs, validation registers and CI runtime manifest remain authoritative for model evidence.