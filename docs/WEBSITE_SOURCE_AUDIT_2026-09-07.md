# Website source audit — 7 September 2026

## Authority

Drive closure control identifies frozen model SHA ff69e15d211ff1abc88200574242ed2f1db49074, tag v5.1.3-recruiter-final, CI run 33629919973.
Source artifact 9846347737 was available at audit time. Its runtime manifest's 15 output hashes were checked before import. No frozen model code or tag was changed.

## Material corrections

- Replaced invented/relabeled risk rows with all 171 actual artifact rows.
- Replaced replacement amortization with all 285 contractual debt-year rows; retained later-year CFADS. Reconciled opening USD with VND-equivalent schedule and frozen FX.
- Restored economics outputs for all 19 projects, rather than showing 18 empty records.
- Replaced estimated energy balances and illustrative hourly values with artifact outputs for 19 projects. The chart shows 1 January 2027, not a verified typical sunny day.
- Removed unsupported diligence percentage scores, site verification and all-metrics-OK claims.
- Fixed chart currency labels, dynamic scales, missing sponsor markers and hardcoded cross-project identity.
- Removed destructive global runtime URL rewriting. Export uses configured basePath and document navigation, with a narrow, checked Vinext prerender workaround.

## Important source limitations

The latest remediation-plan targets conflict with the authoritative artifact. GO Mall artifact debt is USD 529,056.7499, not USD 7,875,000; binding constraint PLCR, not leverage. Project NPV is USD -10,361,886 and equity NPV USD -10,035,912. Sponsor solver is unresolved; lender floor is VND 16,159.0387/kWh. The website follows the artifact, not the conflicting plan.

Seventeen raw model debt capacities are negative. The website preserves raw values and flags these as source anomalies; usable debt is zero and ratios without debt service are N/A. This presentation rule does not validate or fix the model. Model IRR sentinel -0.99 is not represented as a real -99% return.

Passing model tests proves the model's tested invariants, not that its assumptions or commercial facts are correct. The model's negative capacities and unusual amortization require a separately authorized model review before claims of economic reliability. Public-data reconstruction is not investment, lender, engineering, tax or legal approval.

## Verification

Run import_verified_release.py against the frozen artifact, validate_verified_snapshot.py, TypeScript checking, lint, build and Playwright. Browser checks cover eight routes at 390/768/1440 pixels, selectors, non-default handoff/reload and all 19 economics selections. CI repeats import, source validation and browser tests before publishing.

The audit is source reconciliation, not a claim of 100% factual accuracy. Evidence remains OPEN and allocation remains disabled.
