# LOAD_MATCHING_METHODOLOGY

## Population and grain

The model keeps a 20-project screening population and runs deterministic 8,760
profiles for every project in memory on the GitHub Actions runner. Final
decision outputs are controlled CSV summaries. Full derived hourly vectors are
exported only to remote workflow artifacts:
remote_derived/load_8760.csv.gz and remote_derived/solar_8760.csv.gz.
No project data is written to the desktop workspace.

## Deterministic profile

The synthetic hourly load and solar shapes are scaled to annual load and P50/P90
solar output. daytime_load_share changes the daytime/night load shape and is
reconciled to the annual load. For every one-hour interval:
- self-consumed energy = min(load, solar)
- excess energy = max(solar - load, 0)
- grid purchase and export treatment are separate
- hourly totals reconcile to annual inputs

## Tariff mapping

Decision 963 legal periods and the current billed reference are mapped to every
hour using interval midpoints, making 17:30 and 22:30 reproducible. Schedule
hash and period counts are carried into outputs. Numeric tariff components remain
SIMULATED_MODEL_INPUT and are never presented as a billed tariff. Billing stays
WATCH. No generic PR is layered on source PVOUT.
