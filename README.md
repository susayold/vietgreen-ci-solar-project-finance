# VietGreen — C&I Solar Project Finance

[Open the eight-page case study](https://susayold.github.io/vietgreen-ci-solar-project-finance/showcase/)

A public-data project-finance case study connecting project research, physical
screening, hourly energy modeling, economics, debt, scenarios and diligence.

## Current analytical scope

- 54 candidates researched, 441 observations, 20 selected records across 7 countries.
- 19 modeled projects: 129.853 MW and approximately 148.221 GWh annual generation.
- 1 generation outlier is excluded from financial analysis pending technical validation.
- 9 scenarios per project; 171 scenario results.
- Commercial assumptions are disclosed. No actual PPA, lender commitment or investment approval is claimed.

## Current calculation revision

The 8 September 2026 revision corrects a percentage conversion error: the original
0.5% annual degradation assumption was interpreted as 50%. It also enforces
nonnegative debt capacity, uses the stated coverage discount rates, preserves
contractual debt in sponsor sensitivities and validates IRR roots.

The public-input baseline is preserved from
`ff69e15d211ff1abc88200574242ed2f1db49074`. Current financial results supersede
the historical V4 and V5.1.3 outputs; those historical files and releases are not
the current website results. In particular, the old one-year GO Mall repayment
and negative debt-capacity results should not be cited.

## Reproduce and inspect

- [Current model and public inputs](model/recruiter_revision/)
- [Calculation, provenance and checks](scripts/build_corrected_model.py)
- [Current website data](public/data/)
- [Current calculation fingerprint](public/data/model-revision.json)
- [Build and model output artifacts](https://github.com/susayold/vietgreen-ci-solar-project-finance/actions/workflows/codex-github-pages.yml)

The publication workflow downloads the baseline artifact, verifies its hashes,
recalculates the corrected model twice, checks consistency, validates the website
and publishes all eight pages. Full recalculated CSVs are retained in the
`vietgreen-corrected-model` workflow artifact.

For a local rebuild, extract the baseline artifact and run:

```text
python scripts/build_corrected_model.py <baseline-artifact-directory>
npm run test:data
npm run test:claims
npm run build
```

## Important assumptions

Revenue applies the reference tariff to all modeled generation. This is an
illustrative comparison, not an export entitlement or a contracted tariff over
the full analytical horizon. Load profiles, CAPEX, operating costs and financing
terms include analyst/benchmark assumptions. Cash-sweep debt sculpting may repay
before the maximum tenor. Automatic checks support reproducibility but are not
an independent engineering, tax, legal or financial audit.
