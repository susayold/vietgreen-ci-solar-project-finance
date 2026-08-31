# V4 Phase 2 implementation note

Phase 2 extends the remote-only V4 remediation without changing the user boundary or external-evidence policy. The engine compares VND, unhedged USD and hedged USD funding from explicit cash-flow vectors including initial equity, solves primary and secondary FX break-even definitions, applies exposure-based portfolio constraints, and reconciles standalone versus pooled debt.

The USD primary break-even is reported in a common unit: USD Equity NPV under the FX path is translated at base FX and compared with the VND reference Equity NPV. Secondary break-even solves USD MinDSCR against the covenant. Both root and boundary statuses are retained.

The optimizer uses explicit equity/debt budgets and parent, industry and regional exposure shares; it does not rely only on project counts. Sponsor NPV/IRR and DSCR remain present in stress scenario outputs. Phase 2 is still synthetic screening evidence. Transaction evidence, bankable readiness and recruiter readiness remain open/false until real controlled evidence is validated.
