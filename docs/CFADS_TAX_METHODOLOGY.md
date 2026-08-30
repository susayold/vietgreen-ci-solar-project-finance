# CFADS_TAX_METHODOLOGY

## Cash flow

The remote annual schedule uses one row per project-year. Year zero contains CAPEX uses and debt/equity sources. Operating years contain revenue, O&M, cash tax, working-capital balance, change in working capital and CFADS.

CFADS = revenue − cash O&M − cash tax − delta NWC

Working capital is driven by DSO and revenue. Tax is a synthetic cash-tax proxy and must not be mistaken for a tax opinion. VAT, tax-loss carryforward, depreciation and incentive treatment remain separately registered assumptions and must be refreshed before a real transaction.

Sources/uses must reconcile to zero within the configured absolute tolerance. Debt service is not deducted from CFADS; it is tested downstream in DSCR/LLCR/PLCR.
