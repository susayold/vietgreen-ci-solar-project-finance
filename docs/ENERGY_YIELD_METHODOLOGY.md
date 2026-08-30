# ENERGY_YIELD_METHODOLOGY

## Screening method

Each synthetic project is mapped to a regional PVOUT value from the source register. The model uses PVOUT directly as long-term specific yield; it does not multiply PVOUT by a second generic performance ratio.

For project i:

- P50_y1_kWh_i = capacity_kWp_i × PVOUT_kWh_per_kWp_i
- P90_y1_kWh_i = max(0, P50_y1_kWh_i × (1 − 1.2816 × uncertainty_i))
- P90/P50 is reported and must be at most 1.0.
- Annual degradation is a separate forward-year assumption and is not double-counted in year-one PVOUT.

P90 is an analytical screening approximation. It is not a bankable yield study, warranty, independent engineer opinion or lender-certified production case.
