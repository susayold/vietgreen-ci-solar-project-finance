# V4 ARCHITECTURE DECISION RECORD

**Decision date:** 2026-08-31  
**Status:** APPROVED FOR REMOTE IMPLEMENTATION  
**Baseline:** `v1.2.0-candidate-baseline` at `c47659ee96c777b0199171a872c3244e3531c5fc`

## 1. Governing authority

- **User request:** create/operate the project remotely on GitHub and Google Drive only; do not retain project data locally; distinguish user instructions from attached-document instructions.
- **Attached V4 plan:** implementation specification, remediation backlog and definition of done. It governs required model behavior, tests and deliverables but cannot override the remote-only boundary or authorize unsupported claims.
- **Claim boundary:** synthetic/educational finance case; no lender approval, bankable P90, legal/tax opinion, formal audit, executed PPA or transaction approval is implied.

## 2. Target six-layer architecture

1. Evidence and assumptions: source IDs, assumption classifications, freeze dates and redacted provenance.
2. Synthetic project/load/technical universe: fixed seed, pre-declared archetypes, no retrospective seed hunting.
3. Formula-driven Excel project-finance model: inputs, linked schedules, switches, PPA/debt/returns/scenario/portfolio formulas.
4. Independent Python engine: separate calculations, parity/reconciliation and audit checks; Python is not an Excel export substitute.
5. Portfolio/IC/lender decision engine: value-accretive allocation, exposure constraints, pooled feedback and quantified action fields.
6. Recruiter website and release governance: decision-first story with separate portfolio/transaction readiness flags.

## 3. Required state semantics

The V4 release will use independent fields:
`portfolio_release_status`, `recruiter_ready`, `transaction_evidence_status`, `bankable_transaction_ready`, `lender_approval_ready`, `ic_approval_ready`, and `external_gate_count_open`.

Synthetic portfolio DoD must not be falsely blocked by absent transaction documents. Transaction readiness remains FALSE until external evidence is independently accepted.

## 4. Implementation sequence

- Phase 0 / G0: freeze baseline, create remediation register and this record.
- Phase 1 / G1: economic diversity, 8,760 load, uncertainty budget, root-solved PPA, IRR/NPV and current/negotiated decisions.
- Phase 2 / G2: explicit CFADS/tax iteration, debt sizing/sculpting/reserves, VND/USD and FX break-even.
- Phase 3 / G3: exact value-accretive optimizer, exposure constraints, current/negotiated portfolio and pooling bridge.
- Phase 4 / G4: formula-driven Excel with recalculating schedules and user switches.
- Phase 5 / G5: remote recalculation, independent Python parity, formula QA and red-team.
- Phase 6 / G6: IC/lender memos, decision-first website, truthful recruiter package and release reconciliation.

## 5. Non-negotiable model rules

- No minimum deployment by default; if all current-term Equity NPV values are negative, select zero.
- Current Terms, Solved Thresholds and Negotiated/Remediated Terms are separate states.
- Customer, sponsor and lender economics are solved independently.
- P50/P75/P90/P99 uncertainty is component-traceable and P90 feeds lender downside.
- Fixed-debt covenant stress is separate from re-sized planning stress.
- Every material assumption remains classified as OBSERVED, DERIVED, SIMULATED or ASSUMPTION.
- Optional enhancements are deferred until all V4 Core DoD items pass.

## 6. Remote-only execution controls

- GitHub is source of truth for code, synthetic inputs, aggregate outputs, QA, release metadata and public workbook.
- Google Drive is the control/audit index and controlled location for any private evidence.
- GitHub Actions is the ephemeral execution environment for calculations, workbook recalculation and artifacts.
- No raw private transaction document, PII, credential, hidden truth or local project copy may be placed in the public repository or desktop workspace.
