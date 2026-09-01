# Business case

## Decision framing

The case tests whether a synthetic Vietnam C&I rooftop-solar portfolio can be screened through an auditable energy, cash-flow, debt and portfolio workflow. It is a screening and communication package, not a claim that the synthetic portfolio is financeable in the market.

## V4.1.3 governance status

CURRENT_TERMS_DECISION=NO_DEPLOYMENT
SELECTED_COUNT=4
SELECTED_IDS=VG-005|VG-010|VG-011|VG-012
RECRUITER_READY=TRUE
TRANSACTION_EVIDENCE_STATUS=OPEN
BANKABLE_TRANSACTION_READY=FALSE
EXTERNAL_GATE_COUNT_OPEN=8
NEGOTIATED_CASE_TYPE=HYPOTHETICAL

## Current Terms decision

The current-terms gate is NO_DEPLOYMENT: 0 / 20 projects have positive Equity NPV. This result is kept visible and is not replaced by a later negotiated sensitivity.

## Negotiated hypothetical case

The negotiated case is a commercial and financing sensitivity, not an executed transaction. It produces 19 / 20 positive Equity NPV rows. The released exposure-constrained selection contains four projects: VG-005, VG-010, VG-011 and VG-012.

The selected case uses 30.124825 BVND of equity, 55.946104 BVND of debt and 12.003384 BVND of Year-1 CFADS at a pooled minimum DSCR of 1.300x. The base hypothetical case produces 5.262393 BVND Project NPV, 5.942277 BVND Equity NPV, 12.732% Project IRR and 15.929% Equity IRR.

## Downside and credit boundary

P90 Equity NPV is -1.177896 BVND, CAPEX-overrun Equity NPV is -3.179160 BVND and combined-downside Equity NPV is -38.814456 BVND. A P90 or CAPEX row can retain a credit-status PASS at the DSCR floor while remaining economically negative. The release therefore exposes economicStatus and creditStatus as separate fields.

No fixed-versus-resized debt result is published in V4.1 unless a deterministic model-backed debt-sizing output is added with lineage. The public package does not infer a new DSCR or Equity NPV from a multiplier or sign flip.

## Value levers and open evidence

The model supports controlled tests of tariff, CAPEX, COD, DSO, P90 energy, interest rate, FX, default termination, site events and common factors. The next commercial levers are customer-specific tariff confirmation, repricing, CAPEX/vendor validation, construction schedule, PPA/security package and lender terms.

Recruiter-ready mechanics remain separate from transaction evidence. Regulatory/billing, tax, legal, independent review, technical/site, executed PPA/security, lender financing and sponsor/IC evidence remain open until primary evidence is supplied and reconciled.

Any change to assumptions or external-gate status must be recorded on GitHub, linked from the Google Drive control index and rerun through the release workflow.
