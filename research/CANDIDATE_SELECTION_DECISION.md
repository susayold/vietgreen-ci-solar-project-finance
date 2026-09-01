# V5 Candidate Scoring and Selection Decision — 2026-09-01

## Purpose

This register operationalizes the V5 plan's crawl -> normalize -> resolve -> score -> select -> freeze sequence. The score is a research triage score, not an economic result and not a lender credit rating.

## Current result

- Candidate records: 15.
- Evidence sources: official IFC/World Bank Group disclosures only for this expansion.
- Asset-level candidates with materially useful identity: CAND-005 (Tamil Nadu), CAND-006 (Karnataka reference plant), CAND-008 (Uppal reference asset), and CAND-012 (Gandhinagar).
- Frozen V5 project records: 0.
- Economics-ready records: 0.
- No candidate is promoted into `data/public/project_master_real.csv` until identity, capacity/status, country/site, offtaker, technical yield, tariff treatment, CAPEX/OPEX, tax, FX, debt and terminal evidence pass the controlled gates.

## Scoring interpretation

The 100-point triage uses identity, geography, capacity/status, business-model fit, transaction evidence, source quality and completeness. GOLD/STRONG means research priority, not approval. A facility or portfolio can score well while still being ineligible for asset-level economics.

## Selection decision

- CAND-005 and CAND-012 are the first retrieval priorities because their public records name a project structure, location and commercial counterparty.
- CAND-006 and CAND-008 remain on hold because the public record lacks the offtaker/PPA or legal asset identity needed for a full reconstruction.
- CAND-001, CAND-002, CAND-003, CAND-004, CAND-007, CAND-009 and CAND-010 remain portfolio/platform research leads.
- CAND-011 is excluded from the project universe because it is a Bangladesh risk-sharing facility, not a set of named assets.
- CAND-013 and CAND-014 are retained as Vietnam evidence leads but are not treated as Vietnam asset records.
- CAND-015 is a rooftop-market lead only.

## Required next evidence per priority asset

1. Legal project/SPV and exact site or customer identity.
2. Installed/planned/contracted/operational status with non-conflicting capacity.
3. Offtaker identity and PPA mode; observed price where public or explicit reconstructed/frontier label.
4. Resource coordinates or a documented proxy, with no double-counted generic PR.
5. CAPEX/OPEX evidence class, tax applicability, FX date and debt terms or an explicit frontier-only stop.
6. Site rights, permits, grid connection, insurance, O&M and terminal branch evidence.

Until these fields are obtained, the V5 release remains `INPUT_DATA_BLOCKED` and recruiter outputs remain non-ready.
