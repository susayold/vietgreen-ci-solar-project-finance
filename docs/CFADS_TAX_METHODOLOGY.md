# CFADS and tax methodology

## Energy to revenue

For each project, the model executes an 8,760-hour synthetic profile. P50 and P90 energy are separately calculated. Hourly generation is matched to hourly load and tariff bands, with loss components kept distinct. Annual revenue is then aggregated into the cash-flow model.

## Cash flow

The project cash flow includes:

- construction capex and IDC proxy;
- VAT split from all-in capex;
- operating costs and major maintenance in years 5 and 10;
- depreciation proxy and tax loss carryforward;
- cash tax;
- DSO-driven accounts receivable and net working capital;
- debt service and reserve movements;
- terminal value set to zero, with modeled working-capital release.

CFADS is the cash available for debt service after operating costs, tax, working-capital movement and major maintenance, before financing flows. The first pass uses a no-debt construction placeholder to derive debt capacity; the final pass rebuilds cash flow with the sized debt and equity.

## Tax and VAT limitation

The tax implementation is a transparent screening proxy tied to the regulatory register. It is not a tax opinion and has not been certified against a project-specific tax ruling, accounting policy or tax-return model.

