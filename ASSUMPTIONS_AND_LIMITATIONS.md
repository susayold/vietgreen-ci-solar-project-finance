# Assumptions and Limitations — V5.1.2

## Input classes

`OBSERVED_PUBLIC_OR_SOURCE_REPORTED`, `DERIVED`, `BENCHMARK_ASSUMPTION`, `ANALYST_ASSUMPTION` and `SCENARIO` are kept distinct. Missing evidence is not converted into a fact.

## Physical controls

The generic screening band is 900–1,600 kWh/kWp with an extreme threshold at 3,200 kWh/kWp. The Arisudhana source claim is preserved as raw evidence, flagged `EXTREME_OUTLIER_BLOCK_BASE`, and excluded from direct base economics. A replacement benchmark is not invented.

## Model limitations

Annual load and self-consumption are standardized proxies, not customer telemetry. CAPEX, OPEX, tax, rates, FX and discount rates are standardized or benchmark inputs where project-specific evidence is absent. P90/P99 are screening factors on modeled valid P50, not observed measurements. PPA, lender, site, engineering and bankability evidence remains open.
