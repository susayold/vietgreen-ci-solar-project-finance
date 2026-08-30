# LOAD_MATCHING_METHODOLOGY

## Population and grain

The model keeps a 20-project screening population. It runs a deterministic 8,760 profile only for projects that pass hard gates and enter the shortlist. Screening-only rows retain annual approximations and are not presented as hourly diligence.

## Deterministic profile

The remote engine creates a synthetic hourly load shape and solar shape, then scales them to the project annual load and P50 solar output. For each hour:

- self-consumed energy = min(load, solar)
- excess energy = max(solar − load, 0)
- grid purchase and export treatment are kept separate
- hourly reconciliation must equal annual load and annual solar within tolerance

The output records scope, self-consumption, solar share of load, avoided grid cost, aggregation-bias diagnostics and a profile hash/reference. No generic PR is layered on top of source PVOUT.
