# Corrected analytical revision — 8 September 2026

Source baseline: `ff69e15d211ff1abc88200574242ed2f1db49074`.
The five Python modules and two public-input CSVs were copied from that commit.
Historical releases are preserved. This revision supersedes their finance results.

Corrections:
- Percentage-point assumptions are always divided by 100. Degradation 0.5 means 0.5%, not 50%.
- Debt capacity cannot be negative; negative discounted cash flow means no supportable debt.
- LLCR and PLCR capacity limits use their own documented discount rates, matching reported ratios.
- Sponsor tariff sensitivity preserves the base contractual debt schedule.
- IRR requires a bracketed, conventional cash-flow root; no sentinel -99% is returned.

Unchanged assumptions include public capacity/generation, CAPEX, annual load proxies,
tariff ceilings, tax assumptions, cash-sweep sculpting and nine stress definitions.
Revenue is an illustrative all-generation-at-reference-tariff case; no actual PPA,
export sale entitlement or lender approval is implied. PPA tenor is not used to
guarantee continuation of the reference tariff over the analytical horizon.

Build: `python scripts/build_corrected_model.py <verified-baseline-artifact-directory>`.
The builder validates original hashes, calculates twice, compares outputs, checks
unit conversion, debt balance/coverage and scenario preservation, then exports
reviewable results and the website data. Do not rerun the old importer afterward.
