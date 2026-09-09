# VietGreen recruiter website content map

| Route | Recruiter question | Primary current source |
| --- | --- | --- |
| `/` Overview | What problem does the project solve and how is the analysis structured? | `public/data/summary.json`, `public/data/model-revision.json` |
| `/projects` Projects & Data | Which public project records enter the model and why? | `public/data/projects.json`, `public/data/source-audit.json` |
| `/energy` Energy & Physical | How are capacity, generation, load and modeled surplus handled? | `public/data/energy.json`, `public/data/physical.json` |
| `/economics` Economics & PPA | How do energy and reference commercial assumptions become cash flow and returns? | `public/data/economics.json` |
| `/debt` Debt & Credit | How much debt can cash flow support and what constraint binds? | `public/data/debt.json` |
| `/risk` Risk & Scenarios | What happens to debt-service coverage under downside? | `public/data/risk.json` |
| `/diligence` Diligence | What still needs to be verified before capital is committed? | `public/data/diligence.json`, `public/data/source-audit.json` |
| `/excel-model` Excel Model | Can a recruiter inspect the workbook architecture, formulas and spreadsheet skills directly? | `model/vietgreen_core_model.xlsx`, `model/22_CORE_SHEETS.csv`, current V5.1.3 public data |
| `/model-evidence` Model & Evidence | Can a reviewer trace assumptions, calculations, checks and evidence boundaries? | `public/data/model-revision.json`, `public/data/source-audit.json` |

## Excel model boundary

The native 22-sheet Excel workbook is a separately versioned review artifact and demonstrates spreadsheet architecture, assumptions, cash-flow modeling, debt sizing/sculpting, coverage, returns, scenarios and QA controls. The current recruiter website remains governed by the frozen V5.1.3 calculation release. Historical workbook values must not be represented as the source of current website claims unless explicitly reconciled.

The website is a communication and review layer. It does not replace an independent model audit, executed PPA, actual lender terms, technical/legal/tax diligence or investment approval.
