# V4 Phase 1 red-team report

- Run boundary: GitHub Actions only; no local project-data staging.
- Input class: synthetic/aggregate-only; transaction evidence remains OPEN_EXTERNAL_GATE.
- Deterministic seed: 260831.
- Projects: 20; archetypes: 10; full three-sided PPA roots: 40.
- Profile QA: PASS; uncertainty order QA: PASS; self-consumption dispersion QA: PASS.
- Portfolio policy QA: PASS (a project is never selected when Equity NPV <= 0).

## Deliberate red-team checks

1. Negative-NPV selection: tested through the explicit positive Equity NPV gate; an empty portfolio is an allowed result.
2. Solver integrity: customer ceiling, sponsor floor, and lender floor are independently solved with fixed 48-step bisection where a root is bracketed; boundary cases are labelled BOUNDARY_NO_ROOT.
3. Load matching: hourly shapes vary by archetype, weekday/weekend, seasonality, and project-specific cloud phase; only hashes and aggregates are exported.
4. Uncertainty: resource, availability, degradation, and clipping components are combined by root-sum-square; no single scalar is silently reused as the whole budget.
5. External evidence firewall: no transaction, invoice, utility bill, credit file, or contract is inferred or fabricated.

## Gate interpretation

- V4-G1 is evidence-ready only for the synthetic model mechanics listed in validation/V4_PHASE1_DOD.csv.
- This does not close external transaction gates, legal billing confirmation, lender term confirmation, or bankability.
