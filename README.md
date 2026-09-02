# VietGreen CI Solar Project Finance — V5.1.3

Current authoritative branch: `v5.1.3-final-closure`. Planned final tag: `v5.1.3-recruiter-final`.

V5.1.3 is the final closure of the real-data reconstruction: 54 candidate projects, 441 preserved observations, 20 selected projects, 19 economics-ready records and one technically blocked physical outlier. It separates observed facts, derived calculations, benchmark assumptions, analyst overlays and scenarios.

Physical QA uses a generic 900–1,600 kWh/kWp screening band and a 2.0x extreme-outlier firewall. Arisudhana’s source-reported ~30.5 GWh / ~14,593 kWh/kWp observation is preserved, flagged for engineering validation, excluded from direct base economics, and never silently normalized.

PPA mode is FRONTIER_ONLY. Exact PPA price, lender terms, confidential load, site, tax and engineering data are not claimed. P90/P99 are screening factors on valid modeled P50 (0.90 / 0.80), not observed quantiles. The decision boundary is INDETERMINATE_MISSING_COMMERCIAL_DATA.

Recruiter-ready is not transaction-ready, lender-ready, bankable, IC-approved, legal, tax or technical approval. All project-derived artifacts are generated ephemerally in CI and retained remotely in GitHub artifacts/releases; no project data is stored in the local workspace.

## Contractual Debt Stress Policy

Base underwriting sizes and sculpts debt once. P90, COD-delay, OPEX-inflation and nonpayment stresses preserve the contractual base schedule. CAPEX-overrun, termination and combined downside also preserve the contractual principal schedule and permit no new debt. Floating-rate shocks reprice interest only.
