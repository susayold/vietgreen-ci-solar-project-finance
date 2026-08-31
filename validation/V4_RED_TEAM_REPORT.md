# V4 Final red-team report

Release ID: V4-FINAL-2026-08-31
Execution boundary: GitHub Actions remote runner only; no local project-data staging.

## Explicit tests

- RT-01 all-negative Current Terms: 0 positive Equity NPV rows; IC policy is NO_DEPLOYMENT. PASS.
- RT-02 zero-deployment branch is allowed: current positive-NPV count is zero and the decision table contains no forced current-term selection. PASS.
- RT-03 lender-pass / sponsor-fail: Current Terms contains coverage-passing rows with negative Equity NPV; they are not classified as proceed. PASS.
- RT-04 strong DSCR / negative Equity NPV: negative sponsor-value cases remain visible in the IC table and current terms are not approved. PASS.
- RT-05 missing transaction evidence: transaction state remains OPEN and bankable state remains FALSE while synthetic recruiter state is TRUE. PASS.
- RT-06 external gate separation: 8 external gates remain visible; no private evidence is fabricated. PASS.
- RT-07 cross-artifact claims: README, website, IC memo, lender memo, recruiter package and release manifest use the same release ID and headline metrics. PASS.

## Gate result

Final DoD matrix: 35/35 PASS.
This is a recruiter-ready synthetic case package. It is not a bankable transaction, lender approval or investment approval.
