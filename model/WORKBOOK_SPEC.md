# WORKBOOK_SPEC

## Purpose

The workbook is the decision interface for the Vietnam C&I solar portfolio case. It is a 22-sheet structure; the public GitHub repository stores the sheet map, synthetic inputs, Python engine, generated outputs and release metadata. A native workbook binary remains a separate release gate and must be generated and hash-locked on a remote runner.

## Sheet contract

| No. | Sheet | Grain | Primary inputs | Required outputs / controls |
|---:|---|---|---|---|
| 00 | Control_ModelMap | release | versions, seed, scenario | stale flags, run ID, release status |
| 01 | Assumptions | assumption | assumption register | observed/derived/simulated/assumption classification |
| 02 | Evidence_Regulatory | source/rule | source and regulatory registers | effective vs billed tariff switch, recheck flag |
| 03 | Project_Pipeline | project | project master | 20-project population and hard gates |
| 04 | Offtakers_Credit_Site | project/offtaker/site | customer, credit, roof-right | parent, credit, continuity and E&S gates |
| 05 | Solar_Energy | project | solar resource | PVOUT, loss tree, P50, P90, P90/P50 |
| 06 | Load_PPA | project-hour / project | 8,760 profile, tariff, PPA | self-consumption, tariff value, three-sided frontier |
| 07 | CAPEX_Construction | project/component | CAPEX component table | sources/uses, VAT and construction timing |
| 08 | OPEX | project/year | O&M assumptions | fixed/variable O&M and replacements |
| 09 | Tax_VAT_WC | project/year | tax rules, DSO, VAT | cash tax, VAT, AR/AP and delta NWC |
| 10 | Project_CF_CFADS | project/year | operating and funding inputs | revenue, opex, tax, WC, CFADS |
| 11 | Debt_Terms | facility | debt terms | rate, spread, DSCR/LLCR/leverage terms |
| 12 | Debt_Sculpting | facility/year | CFADS, debt terms | backward sizing and forward roll-forward |
| 13 | Reserves_Waterfall | facility/year | DSRA, debt service | funding, cash trap, distributions, release |
| 14 | Coverage | project/portfolio | CFADS and debt schedule | DSCR, LLCR, PLCR, covenant/lock-up |
| 15 | Returns_Discount | project/portfolio | equity cash flow | NPV, return register and discount provenance |
| 16 | FX_Financing | facility/scenario | VND/USD terms | crawl and one-off translation, legal checklist |
| 17 | Scenarios_Sensitivity | scenario/project | deterministic shocks | downside, reverse stress and isolation checks |
| 18 | Portfolio | portfolio/project | standalone outputs | pooled re-sizing, concentration, allocation |
| 19 | IC_Bankability | project/portfolio | sponsor/lender tests | divergent decisions and action class |
| 20 | External_Validation | benchmark | source register | comparator grade and exception rationale |
| 21 | QA_Audit | test/release | QA and DQ results | pass/fail, severity, hash/release gates |

## Formula contract

- P50 = installed kWp × source PVOUT (kWh/kWp).
- P90 = P50 × (1 − 1.2816 × uncertainty); P90 cannot exceed P50.
- Shortlist-only 8,760 matching is executed after hard gates; screening rows do not receive a false hourly precision claim.
- CFADS = revenue − cash O&M − cash tax − change in working capital. Debt service is not deducted from CFADS.
- Debt = minimum of DSCR capacity, LLCR capacity and leverage capacity.
- PPA feasible zone = [max(sponsor floor, lender floor), customer ceiling]; an empty interval is a renegotiation gate.
- Pooled debt is re-sized from aggregate portfolio CFADS and terms; it is not the sum of standalone debt.
- Residual/terminal value is zero unless explicitly evidenced; contract tail and removal/transfer branches remain visible.

## Release controls

A release cannot be called recruiter-ready while any required source recheck, independent review, native-workbook hash, hidden-truth reconciliation, or blocker QA is unresolved.
