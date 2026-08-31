# VietGreen recruiter-facing website

This is the V4 recruiter communication layer for the VietGreen C&I solar project-finance study. It follows the supplied website build plan: dark forest-green narrative shell, white analytical panels, finance-first navigation and an explicit evidence boundary.

## Data contract

`website/data/*.json` is generated from authoritative release artifacts — portfolio exposure, current/negotiated returns, phase-2 scenarios, debt sizing, load matching, FX, QA and the release manifest. Do not edit the generated JSON by hand.

```text
python scripts/build_website_data.py
python scripts/validate_website_data.py
python scripts/check_stale_v3_claims.py
```

The public payload contains aggregate model outputs only. Raw hourly streams and private transaction evidence are intentionally not embedded. The model is synthetic and recruiter-ready; transaction evidence is `OPEN` and bankable transaction readiness is `FALSE`.

## Routes

`#/` Overview · `#/case` Investment case · `#/economics` Economics & PPA · `#/debt` Debt · `#/portfolio` Portfolio · `#/risk` Risk · `#/model` Model · `#/evidence` Evidence.

## Source and deployment

- Source of truth: [VietGreen GitHub repository](https://github.com/susayold/vietgreen-ci-solar-project-finance)
- Live GitHub Pages site: [susayold.github.io/vietgreen-ci-solar-project-finance](https://susayold.github.io/vietgreen-ci-solar-project-finance/)
- Workbook preview: [model_preview/index.html](model_preview/index.html)
- The `recruiter-pages` workflow rebuilds and validates the data contract on every release-output or website change before publishing Pages.
