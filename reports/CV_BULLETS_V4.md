# V4 CV Bullets — VietGreen CI Solar Project Finance

Release ID: V4-FINAL-2026-08-31
Repository: https://github.com/susayold/vietgreen-ci-solar-project-finance

- Built a formula-driven Excel Project Finance model for a synthetic Vietnam C&I rooftop-solar pipeline, linking 8,760 load matching, P50/P90 energy, CFADS, debt sizing and Project/Equity NPV/IRR.
- Solved customer ceiling, sponsor floor and lender floor with explicit bisection roots, residuals and interval evidence.
- Compared VND, unhedged USD and hedged USD funding and solved primary and secondary FX break-even conditions.
- Optimized a negotiated hypothetical portfolio under equity, parent, industry, region and debt exposure constraints; reconciled standalone versus pooled financing in Python.
- Automated formula QA, remote recalculation, Excel/Python parity, red-team tests and release governance on GitHub Actions.
- Current Terms correctly returns NO_DEPLOYMENT; the exposure-constrained negotiated sensitivity selects 4 projects (VG-005, VG-010, VG-011, VG-012) with base Equity NPV 5.942277 BVND and P90 Equity NPV -1.177896 BVND.

Claim boundary: recruiter-ready synthetic case only; not investment approval, lender approval, legal/tax opinion, technical certification, site diligence or bankable P90.
