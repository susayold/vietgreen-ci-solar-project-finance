# V3 BASELINE FREEZE — V4 REMEDIATION START

**Baseline tag:** `v1.2.0-candidate-baseline`  
**Baseline commit:** `c47659ee96c777b0199171a872c3244e3531c5fc`  
**Release:** `1.2.0-candidate`  
**Freeze date:** 2026-08-31  
**Purpose:** Immutable comparison point for the V4 outstanding-remediation program.

## Authority and storage boundary

The user request controls the operating boundary: project data, code, outputs and activity remain on GitHub/Google Drive; no project data is intentionally stored in the local workspace. The attached V4 plan is an implementation specification and DoD, not authorization to copy private evidence or the plan text into the public repository. The plan fingerprint below is metadata-only.

## Baseline evidence

| Artifact | GitHub blob SHA | SHA-256 of remote UTF-8 bytes / remote binary | Size |
|---|---|---|---:|
| `outputs/returns_register.csv` | `380f27531c9fbadec48b0a73642f1b8b8fbdb3a4` | `a3d0461f4ac7ebb3e1d0dd75dc694b0d5d31e5e013d7f3299dd19aafabfd4cd9` | 2689 |
| `outputs/portfolio_selection.csv` | `2235a4cf3dc75036dbbeb26bde34bf5af3e1d069` | `7cd23fa7ec6c875d1a835ff935194e2a435f1e85cbde14b46a1565f488009409` | 5080 |
| `outputs/ppa_frontier.csv` | `b8faa71d729c5779c901750e1534d79c5b5b566f` | `67add86082c0359364e55766a6b2e588e26b03b8ab167edd85e329ae1f514444` | 3218 |
| `outputs/scenario_summary.csv` | `1ae89fc96fbf06329e936c9841cf73f7c2bef261` | `b24c8994c0840da4f58f4a4ceac8250b96698973fc831aea07f6cae1f52e114b` | 3038 |
| `config/model_config.yml` | `0abf43c9723ef91da1455a348c5f92ea865bb550` | `d543dc348f8033d3d3277746c6b802b03ec937fc1e34d73f786b755bb4421c23` | 474 |
| `evidence/ASSUMPTION_REGISTER.csv` | `c30710e4c3975f6a2a2ef6ce8361c6ea9fdf47bb` | `5199ccdb3b3a1494048881c4a5a6304f32c6c0f9d8c843682d9416f93a10c82f` | 6439 |
| `model/vietgreen_core_model.xlsx` | `c0d2e2dadf3720a35b9101205efdec108425bec5` | `9e72588fd7a084282befa74dd0f97036f15e1f306aac6080fc86fdd75f605c5f` | 117493 |

## V4 plan fingerprint

- Source filename: `VIETGREEN_CI_SOLAR_PROJECT_FINANCE_OUTSTANDING_REMEDIATION_MASTER_PLAN_V4.md`
- Bytes read in memory: 61,530
- SHA-256: `28042fe994343a864486a9cc08085f176d3743a10fadab6a6c6278efd14c742a`
- Raw copy stored by agent: FALSE
- Storage boundary: `USER_PROVIDED_INPUT_READ_IN_MEMORY_ONLY`

## Observed V3 baseline defects

- All 20 return rows are below sponsor hurdle while the greedy/pairwise selector selects 11 projects.
- Base sponsor NPV is approximately -66.202345 BVND.
- PPA floors are multiplier-derived and report one iteration.
- Load matching is generic and baseline self-consumption is approximately 100%.
- P90 is a single uncertainty percentage, not a component budget.
- FX break-even discards the VND NPV comparator and uses a zero-equity-value proxy.
- Workbook structural validation is not formula-model validation.
- Eight external transaction gates remain an honest diligence checklist; they are not input evidence for the synthetic public case.

## Freeze rules

1. V4 changes must be additive or explicitly reconciled; no baseline artifact is silently overwritten.
2. Every V4 output must identify the V4 engine/schema/version and remain reproducible on an ephemeral GitHub Actions runner.
3. Synthetic, derived, simulated and observed values remain labelled.
4. Private transaction evidence must stay in controlled Drive; public GitHub may receive only redacted metadata and hashes.
5. No BESS, AI, Monte Carlo, new geographies or other optional scope before V4 Core DoD passes.
