# V4 Phase 2 red-team report

- Execution boundary: GitHub Actions only; no local project-data staging.
- Scope: debt sizing, VND/unhedged USD/hedged USD comparison, primary/secondary FX break-even, exposure optimizer, standalone-vs-pooled financing and sponsor stress metrics.
- USD break-even target: USD Equity NPV translated at base FX equals VND Equity NPV; initial equity is included in every USD cash-flow vector.
- Primary FX roots: 20/20; exposure constraints: PASS; selected negative Equity NPV rows: 0.

## Deliberate checks

1. Zero-depreciation USD rows include the full initial equity investment; the USD funding advantage is measured against the VND-equivalent target and then solved at the primary break-even.
2. Increasing unhedged depreciation is checked for non-improving USD Equity NPV and DSCR.
3. Hedge fraction is explicit and carries a 1.5% service fee; 0%, 50% and 100% USD debt switches are exercised.
4. Exposure limits are applied against an explicit equity/debt budget, not only project counts.
5. Pooling output preserves standalone and pooled sponsor/debt metrics; no pooled benefit is treated as an approval.

## Gate interpretation

- Phase 2 is synthetic screening evidence only.
- External transaction evidence, legal billing, lender confirmation, tax/site diligence and bankability remain open/false; recruiter readiness is intentionally separate and can be TRUE for the synthetic recruiter package.
