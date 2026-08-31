# Assumptions and limitations

## Purpose

This file defines what the release candidate actually calculates, what is synthetic, and what remains outside the evidence boundary.

## Data and lineage

All project rows are synthetic and generated from the locked master seed 260831. Source-register rows carry input IDs and provenance fields. Public repository content excludes credentials, hidden truth, proprietary raw data, and personal information.

The repository is the remote source of truth. The native workbook is generated remotely by GitHub Actions; no local project-data copy is required.

## Energy and tariff

The engine creates an 8,760-hour synthetic load and PV shape for each project, with P50 and P90 energy cases. Loss components are kept separate from the PV shape. The tariff engine uses model-only simulated components linked to ASM-TARIFF-BASE and ASM-TARIFF-DAY-PREMIUM. These are explicitly not legal price claims.

Decision 963 is captured as legally effective time-window metadata. Price applicability and billed implementation are not treated as confirmed: the model remains WATCH pending documentary confirmation under Circular 60 and the EVN/Cục Điện lực implementation notice.

## Cash flow

Cash flow includes construction-period capex, IDC proxy, VAT split, depreciation, loss carryforward proxy, tax, working capital through DSO, major maintenance, debt service, DSRA/reserve waterfall, and a zero terminal-value branch. Annual CFADS is derived from the 8,760 energy simulation, but the credit case is not a bank-certified hourly model.

## Debt and portfolio

Standalone debt is constrained by DSCR, LLCR, PLCR, leverage and tail rules. Pooled debt is resized from aggregate CFADS and a feedback loop; it is not copied from a fixed portfolio debt assumption. In this candidate the endogenous pooled debt equals the displayed standalone sum because the current terms are linear and the portfolio cap is non-binding.

The candidate uses annual debt service for screening. It does not represent lender-specific sculpting conventions, hedging documentation, reserve-account control agreements, intercreditor terms, or covenant definitions.

## Scenario limitations

Scenario isolation passes for the implemented factors. A DSO case changes working-capital timing; because final working capital is released at the end of the modeled life, total-life CFADS can look less sensitive than annual liquidity timing. COD delay currently removes first-year service alignment and is intentionally flagged as a screening case, not a construction schedule claim.

## External gates

Before an investment, credit, or recruiter-ready claim, obtain:

1. Billed tariff confirmation and final legal applicability.
2. Independent model review and source-to-model reconciliation.
3. Lender, legal, tax, technical and site diligence.
4. Bankable P90, financing terms, security package and executed PPA evidence.

