"""Local-currency CAPEX/construction/IDC engine."""
def build_capex_summary(project, construction_periods=2, idc_rate=0.0, vat_rate=0.0):
    capex=float(project["capex_local"]); net=capex/(1+vat_rate) if vat_rate else capex; vat=capex-net
    idc=sum(capex/construction_periods*(1+idc_rate)**i-capex/construction_periods for i in range(construction_periods)) if idc_rate else 0.0
    return {"currency":project["currency"],"total_uses_local":capex+idc,"construction_capex_gross_local":capex,"depreciable_basis_local":net,"vat_local":vat,"idc_local":idc,"construction_periods":construction_periods}
