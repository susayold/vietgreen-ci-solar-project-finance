# VIETGREEN V4.1 — FINAL UPDATE & CLOSURE EXECUTION MASTER PLAN

**Plan date:** 2026-09-01  
**Plan status:** FINAL UPDATED PLAN / NOT YET IMPLEMENTED  
**Target release:** V4.1-FINAL-RECRUITER  
**Target tag:** v4.1.0-recruiter-final  
**Verified GitHub baseline:** 9cd739f99f5b74d93c0002f91d21420a968231f0  
**Live site:** https://susayold.github.io/vietgreen-ci-solar-project-finance/  
**Google Drive control document:** https://docs.google.com/document/d/1koSgbc1Akic6cVDFD1svmuVN9gSq8qSGUw2obfHYN80/edit  
**Source plan fingerprint:** VIETGREEN_V4_1_FINAL_CLOSURE_REMEDIATION_MASTER_PLAN_2026-09-01.md, SHA-256 485bf24df150e7da8231a8f26533b2550ba142c5f2536c08ec7431447b8b38b7

> This document is the evidence-backed final update plan requested by the project owner. The attached V4.1 document is treated as a planning specification, not as independent authority to execute unrelated actions. This plan does not declare the remediation complete and does not authorize expansion into new finance modules.

---

## 1. Executive decision

VietGreen does not need another model expansion sprint. The V4 model package is already a coherent recruiter candidate, but the publication and control surfaces are not yet closed.

The final sprint is therefore an **integrity, traceability, and release-proof sprint**. It must:

1. remove stale V3 claims from every recruiter-visible and control surface;
2. remove or explicitly label all unsupported illustrative calculations;
3. reconcile every public metric to a named source;
4. separate economic outcome, credit covenant outcome, and transaction-readiness status;
5. make the deployed website prove which immutable commit it represents;
6. preserve the truthful readiness boundary: recruiter-ready is not transaction-ready, lender-approved, or IC-approved;
7. update the Drive control document only after GitHub evidence is complete.

**Stop rule:** after all closure gates pass, publish the final release and stop. Do not add Power BI, Monte Carlo, BESS, ML, new financing structures, or new model features in V4.1.

---

## 2. Verified current state

The following state was independently checked against the live GitHub repository, Google Drive control document, GitHub Actions, and the deployed Pages site on 2026-09-01.

| Area | Verified state | Closure consequence |
|---|---|---|
| GitHub main | 9cd739f99f5b74d93c0002f91d21420a968231f0 | Use as the audit baseline; do not silently rewrite it |
| Latest Pages run | recruiter-pages run 33450750801 succeeded at the baseline SHA | Historical workflow success is not live-SHA proof |
| Latest core run | core-validation run 33450750750 succeeded at the baseline SHA | Existing validation remains useful but does not cover V4.1 closure |
| Live site | Root and shared-summary.json return HTTP 200 | Site is online |
| Live release metadata | website/data/release-meta.json returns HTTP 404 | Deployed commit cannot be proven from the public site |
| Release manifest | V4-FINAL-2026-08-31, version 4.0.0-recruiter-candidate | Valid source for current candidate metrics |
| GitHub releases | No GitHub Release exists | Final tag/release evidence still missing |
| Repository rulesets | No repository ruleset observed | Release protections must be explicitly established or documented |
| Branch protection | Status unavailable through the current integration | Do not claim protected or unprotected without direct verification |
| Drive control | Title still says V3 Execution Control | Rename and append V4.1 evidence after closure |
| Drive freshness | Contains package commit 2ccd872 but not baseline 9cd739f | Drive is not the current execution index |
| External gates | 8 gates remain OPEN | Must remain OPEN unless primary evidence closes them |

### 2.1 Authoritative candidate facts

These facts are the baseline that all public and control surfaces must reproduce:

| Metric / status | Authoritative value |
|---|---:|
| Current-terms viable sites | 0 of 20 |
| Negotiated hypothetical positive Equity NPV sites | 19 of 20 |
| Selected site IDs | VG-005, VG-010, VG-011, VG-012 |
| Selected site count | 4 |
| Selected equity | 30.124825 BVND |
| Selected debt | 55.946104 BVND |
| Year-1 CFADS | 12.003384 BVND |
| Pooled minimum DSCR | 1.300000x |
| Base Project NPV | 5.262393 BVND |
| Base Equity NPV | 5.942277 BVND |
| Base Project IRR | 12.732% |
| Base Equity IRR | 15.929% |
| P90 Equity NPV | -1.177896 BVND |
| CAPEX stress Equity NPV | -3.179160 BVND |
| Combined stress Equity NPV | -38.814456 BVND |
| Recruiter-ready | true |
| Bankable transaction ready | false |
| Lender approval ready | false |
| IC approval ready | false |
| Open external gates | 8 |

The source of record for the values above is release/MODEL_RELEASE_MANIFEST.json together with the locked V4 outputs and validation evidence. Website JSON, prose documents, and the Drive control document are consumers, not independent sources.

---

## 3. Gap register

| ID | Severity | Observed gap | Evidence | Required disposition |
|---|---|---|---|---|
| GAP-01 | P0 | EXECUTIVE_SUMMARY.md still contains V3 selection and capital values | 11 sites, 13.10 MWp, 138.143294 BVND equity, 152.457008 BVND debt, -66.202345 BVND sponsor NPV | Regenerate or rewrite from V4 sources and validate |
| GAP-02 | P0 | BUSINESS_CASE.md contains the same stale V3 claims | Same stale portfolio and capital facts | Regenerate or rewrite from V4 sources and validate |
| GAP-03 | P0 | fixedVsResized is heuristic, not model-backed | build_website_data.py multiplies debt by 0.85, fixes DSCR at 1.55, and flips the P90 Equity NPV sign | Remove from public contract, or replace only with traceable model output |
| GAP-04 | P0 | Stale-claim scanner covers only website files | scripts/check_stale_v3_claims.py omits root docs, reports, release, validation, and control metadata | Replace with recruiter-surface inventory and fail-closed scanning |
| GAP-05 | P0 | No public deployment SHA proof | release-meta.json absent on live Pages site | Generate, deploy, fetch, and compare release SHA |
| GAP-06 | P0 | Release candidate SHA may mutate after validation | core-validation.yml can commit refreshed outputs and push to main | Split mutation from validation; release validation must be read-only |
| GAP-07 | P1 | Scenario PASS is credit-only but rendered as general green status | P90 and CAPEX rows have negative Equity NPV while source status is PASS | Publish separate economicStatus and creditStatus |
| GAP-08 | P1 | PPA zone geometry is hard-coded | app.js uses fixed 23%, 49%, and 79% marker positions | Derive marker positions from shared bounds and unit-test the math |
| GAP-09 | P1 | Cross-artifact reconciliation and metric lineage are absent | Expected scripts/reports/CSV files do not exist | Add machine-readable lineage and validators |
| GAP-10 | P1 | EXT-008 evidence text contains obsolete -66.202345 BVND value | validation/OPEN_EXTERNAL_GATES.csv | Rewrite evidence without closing the gate |
| GAP-11 | P1 | Pages workflow lacks post-deployment validation and durable evidence | recruiter-pages.yml ends after deploy | Add live verification and evidence artifact |
| GAP-12 | P1 | Pages upload action is behind the current official example | upload-pages-artifact@v3 | Upgrade to v4 after compatibility check |
| GAP-13 | P1 | Drive control is stale | V3 title; missing latest baseline, workflow run, and V4.1 section | Update only after GitHub closure |
| GAP-14 | P2 | Automated accessibility and visual closure are incomplete | No V4.1 AA evidence package | Add critical-route keyboard, focus, contrast, and responsive checks |
| GAP-15 | P2 | Final release provenance is absent | No release, final tag, or immutable release evidence | Publish an immutable GitHub Release tied to the verified SHA |

---

## 4. Source and claim governance

### 4.1 Source hierarchy

Use this precedence order whenever two surfaces disagree:

1. locked model and deterministic build inputs;
2. release/MODEL_RELEASE_MANIFEST.json;
3. validation outputs generated from the same locked commit;
4. generated website JSON and generated reports;
5. narrative documents;
6. Google Drive control index;
7. visual labels and presentation text.

Lower layers must never override higher layers. Any mismatch is a release blocker.

### 4.2 Public claim classes

Every public claim must be assigned one class:

- **MODEL_OUTPUT** — calculated by the locked model and linked to source file, field, unit, and commit;
- **SOURCE_FACT** — copied from an official external source with source date and URL;
- **MANAGEMENT_ASSUMPTION** — explicitly labeled and stored in an assumption register;
- **ILLUSTRATIVE** — allowed only when clearly labeled, excluded from model conclusions, and not presented as a decision result;
- **PROHIBITED** — unsupported, stale, ambiguous, or fabricated.

The current fixedVsResized panel is PROHIBITED until replaced by a real model-backed debt-sizing result.

### 4.3 Regulatory and billing boundary

Official 2026 sources are not fully aligned on practical application of the revised time-of-use periods. Decision 963/QD-BCT defines new peak periods, while an MOIT Q2 briefing states that the new periods had not yet been applied in practice; an EVNSPC communication describes application from 22 April 2026.

Therefore:

- keep billing_status = WATCH;
- do not change tariff or hourly allocation assumptions solely from public pages;
- require customer-specific invoice, applicable utility confirmation, meter class, and effective-date evidence;
- store the resulting evidence under the relevant external gate;
- preserve the current model until a controlled change request is approved.

---

## 5. Target architecture

The closed release must follow one-way data flow:

**Locked model and source evidence → release manifest → validators and lineage → generated public JSON/docs → Pages artifact → deployed release-meta → live verification → immutable release → Drive control index**

No narrative file or website component may create a financial fact independently.

### 5.1 Required release identity

Every generated release surface must carry:

- release_id;
- model_version;
- git_sha;
- generated_at_utc;
- source_manifest_path;
- source_manifest_sha256;
- data_contract_version;
- readiness boundary;
- open_external_gate_count.

The public website/data/release-meta.json must contain at least release_id, git_sha, built_at_utc, workflow_run_id, and data_contract_version.

---

## 6. Implementation work packages

### WP-0 — Freeze and candidate control

**Objective:** establish one immutable candidate SHA before remediation validation.

Actions:

1. Create a V4.1 closure branch from the verified baseline.
2. Disable auto-push behavior for candidate validation.
3. Separate output refresh into an explicit, reviewable workflow or pre-candidate commit.
4. Make candidate validation read-only: a dirty diff after generation is a failure.
5. Record baseline SHA, candidate SHA, workflow run IDs, and expected artifact hashes.

Exit gate: validation cannot change the commit under review.

### WP-1 — Correct stale narrative surfaces

Files:

- EXECUTIVE_SUMMARY.md
- BUSINESS_CASE.md
- README.md, only if reconciliation requires it
- validation/OPEN_EXTERNAL_GATES.csv, EXT-008 evidence field

Actions:

1. Replace V3 portfolio and capital claims with authoritative V4 facts.
2. State current terms and negotiated hypothetical cases separately.
3. Preserve the distinction between recruiter-ready and transaction-ready.
4. Correct the workbook/source path.
5. Rewrite EXT-008 current evidence to state:
   - current terms: 0/20 positive Equity NPV;
   - negotiated hypothetical base: positive Equity NPV for the selected case;
   - downside economics remain negative;
   - sponsor hurdle and IC evidence are still missing.
6. Do not mark EXT-008 PASS.

Acceptance:

- no stale V3 number or phrase remains in the recruiter-surface inventory;
- every financial number resolves to lineage;
- narrative values equal the release manifest within declared tolerance.

### WP-2 — Remove fabricated remediation economics

Files:

- scripts/build_website_data.py
- website/data/risk.json
- website/app.js
- website/index.html, if panel structure changes
- website/styles.css, if layout changes

Preferred decision: remove fixedVsResized entirely from the public contract and UI.

Alternative decision is permitted only if a deterministic debt-sizing module already produces the values and the lineage validator proves the source. No multiplier, sign flip, or manually fixed DSCR is allowed.

Acceptance:

- no 0.85 debt multiplier;
- no hard-coded 1.55 DSCR;
- no sign-flipped P90 NPV;
- no public “remediation” conclusion without model evidence.

### WP-3 — Recruiter-surface inventory and stale-claim control

Create:

- scripts/validate_recruiter_surfaces.py
- validation/RECRUITER_SURFACE_RECONCILIATION.csv
- reports/RECRUITER_SURFACE_RECONCILIATION.md

The inventory must include at minimum:

- README.md;
- EXECUTIVE_SUMMARY.md;
- BUSINESS_CASE.md;
- reports/**/*.md and reports/**/*.json;
- release/**/*.json;
- validation/**/*.csv and validation/**/*.md;
- website/**/*.html, website/**/*.js, website/**/*.json;
- selected control metadata exported from Drive when available.

Rules:

- scan both known stale literals and semantic patterns;
- compare canonical metrics, IDs, units, precision, release labels, and readiness states;
- fail on missing expected surfaces;
- fail on parse errors;
- never return PASS because the scan scope is empty.

### WP-4 — Metric lineage and cross-artifact reconciliation

Create:

- reports/WEBSITE_METRIC_LINEAGE.csv
- scripts/validate_metric_lineage.py
- scripts/validate_public_claims.py

Minimum lineage columns:

| Column | Meaning |
|---|---|
| metric_id | stable machine-readable ID |
| public_label | label shown to users |
| source_path | authoritative repository path |
| source_field | JSON key, CSV field, cell/range, or calculation ID |
| source_sha256 | source hash |
| source_git_sha | candidate commit |
| unit | BVND, %, x, count, ID list |
| precision | display and comparison precision |
| transform | permitted deterministic transform |
| consumers | docs, JSON, component IDs |
| claim_class | MODEL_OUTPUT, SOURCE_FACT, etc. |
| tolerance | exact or numeric tolerance |

Validator behavior:

- exact match for IDs, statuses, release IDs, and counts;
- explicit tolerance for numeric formatting only;
- unit mismatch is a failure;
- unlabeled transformation is a failure;
- missing consumer or orphan public metric is a failure.

### WP-5 — Scenario semantics

Modify the website data contract so each scenario has distinct fields:

- economicStatus;
- creditStatus;
- readinessImpact;
- equityNPV;
- minDSCR;
- sourceScenarioId.

Required interpretation:

- positive DSCR covenant outcome does not imply positive equity economics;
- negative Equity NPV must display an economic warning even when creditStatus passes;
- readiness remains blocked while external evidence gates are open;
- color must not be the only status signal.

Add contract fixtures and tests for base, P90, CAPEX stress, and combined stress.

### WP-6 — PPA zone calculation

Create:

- tests/test_ppa_zone_math.py, or equivalent repository-native test

Replace fixed CSS percentages with a function based on:

- axis minimum;
- axis maximum;
- current-terms PPA;
- threshold PPA;
- negotiated PPA;
- clamping rules;
- currency/unit metadata.

Test:

- exact boundary values;
- midpoint;
- out-of-range clamping;
- reversed or equal bounds rejected;
- rounding/display does not move the underlying marker;
- mobile and desktop use the same calculation.

### WP-7 — Release metadata and deterministic Pages build

Create:

- scripts/write_release_meta.py
- website/data/release-meta.json during CI
- reports/DEPLOYMENT_EVIDENCE.json
- reports/DEPLOYMENT_EVIDENCE.md

Modify:

- .github/workflows/recruiter-pages.yml
- reports/WEBSITE_RELEASE_MANIFEST.json
- reports/WEBSITE_QA_REPORT.md

Workflow design:

1. checkout the exact candidate SHA;
2. generate website data and release-meta from GITHUB_SHA;
3. run all model, stale-claim, lineage, contract, scenario, and PPA tests;
4. assert no unexpected git diff;
5. run local HTTP smoke tests;
6. upload a Pages artifact with the current supported official action;
7. deploy through the github-pages environment;
8. fetch the deployed release-meta.json;
9. compare live git_sha with GITHUB_SHA;
10. verify root and critical JSON routes;
11. store workflow run ID, candidate SHA, deployment URL, artifact ID/digest where available, HTTP results, and timestamps;
12. fail the workflow if live proof cannot be established.

Permission design:

- build/validation job: contents read;
- deploy job only: pages write and id-token write;
- environment: github-pages;
- no contents write in the release-validation path.

### WP-8 — Accessibility and visual closure

Target WCAG 2.2 Level AA for critical recruiter flows.

Required checks:

- keyboard access and visible focus;
- heading and landmark structure;
- text and non-text contrast;
- status meaning not conveyed by color alone;
- touch target sizing;
- responsive layout at narrow, tablet, and desktop widths;
- zoom/reflow;
- link and control names;
- reduced-motion behavior where animation exists.

Automated checks are evidence, not a complete conformance claim. Complete a short manual keyboard and visual review and record reviewer, date, route, viewport, result, and screenshots/artifact references.

### WP-9 — Drive execution control closure

After GitHub gates pass:

1. rename the control document from V3 Execution Control to V4.1 Final Execution Control;
2. append a dated V4.1 closure section;
3. link the final plan, candidate commit, final tag/release, workflow runs, Pages URL, deployment evidence, and release manifest;
4. state all 8 external gates and their actual status;
5. record the Drive revision ID after the update;
6. do not paste duplicate model data into Drive when a canonical GitHub artifact can be linked;
7. treat Drive as an execution index and approval log, not the financial source of record.

---

## 7. Closure gate matrix

All gates are fail-closed.

| Gate | Requirement | Evidence | Owner |
|---|---|---|---|
| G-WEB-01 | EXECUTIVE_SUMMARY reconciles to V4 | Surface CSV + validator log | Implementation |
| G-WEB-02 | BUSINESS_CASE reconciles to V4 | Surface CSV + validator log | Implementation |
| G-WEB-03 | No fabricated public finance metric | Claim validator | Implementation |
| G-WEB-04 | Recruiter-surface scan covers the declared inventory | Inventory + negative fixture test | QA |
| G-WEB-05 | Every public metric has lineage | Lineage CSV + validator | QA |
| G-WEB-06 | Scenario economics and credit status are separate | Contract tests + visual evidence | Implementation |
| G-WEB-07 | PPA markers are data-driven | Unit tests + rendered checks | Implementation |
| G-WEB-08 | Website contract and source hashes reconcile | Contract validator | QA |
| G-WEB-09 | Release candidate build is deterministic and clean | No-diff assertion | CI |
| G-WEB-10 | Critical local routes and JSON return valid content | HTTP smoke log | CI |
| G-WEB-11 | Critical flows meet the defined accessibility evidence standard | Automated + manual report | QA |
| G-WEB-12 | Release validation is read-only and all required workflows pass at one SHA | Workflow run IDs | Release |
| G-WEB-13 | Deployed release-meta equals candidate SHA | Deployment evidence JSON/MD | Release |
| G-WEB-14 | Final tag, GitHub Release, live SHA, and Drive control all point to one commit | Final closure manifest | Project owner / Release |

A green website alone cannot close any external transaction gate.

---

## 8. Execution sequence and dependencies

### Phase A — Candidate integrity

Complete WP-0. No downstream work may declare PASS until the candidate validation path is non-mutating.

### Phase B — P0 truth correction

Complete WP-1, WP-2, and WP-3. Re-run the stale scanner and public-claim validator after every public-surface change.

### Phase C — P1 traceability and semantics

Complete WP-4 through WP-7. Generate all reports from code where practical; do not hand-edit generated PASS evidence.

### Phase D — P2 presentation closure

Complete WP-8 only after the data contract is stable, so visual QA does not mask data changes.

### Phase E — Release and Drive closure

1. select the final candidate SHA;
2. run the full closure workflow without mutation;
3. verify deployed release-meta against the same SHA;
4. enable GitHub immutable releases if available for the repository;
5. create a draft release for tag v4.1.0-recruiter-final at the verified SHA;
6. attach or link the closure manifest and deployment evidence;
7. publish the release only after G-WEB-01 through G-WEB-14 are satisfied;
8. verify tag target, release target, live SHA, and manifest SHA;
9. update the Google Drive control document and record its new revision ID;
10. freeze V4.1.

If immutable releases cannot be enabled, document that limitation and compensate with a protected tag/ruleset and recorded evidence. Do not claim immutability without proof.

---

## 9. Validation commands and expected outcomes

Repository-native commands may differ, but the final workflow must execute equivalent checks:

- core model validation;
- remote output and locked-hash validation;
- recruiter-surface reconciliation;
- stale-claim scan;
- public-claim governance;
- metric-lineage validation;
- website data-contract validation;
- scenario semantic tests;
- PPA geometry tests;
- local HTTP smoke tests;
- accessibility automation;
- clean-working-tree/no-diff assertion;
- post-deploy live SHA verification.

Expected final outcomes:

- 0 stale V3 claims;
- 0 unsupported public metrics;
- 100% public metrics mapped to lineage;
- 100% declared recruiter surfaces scanned;
- all 14 closure gates PASS;
- 8 external gates remain OPEN unless new primary evidence was actually supplied;
- one final commit SHA is shared by tag, release, Pages metadata, deployment evidence, and Drive control.

---

## 10. Release manifest requirements

Create a V4.1 final closure manifest containing:

- repository;
- baseline SHA;
- final SHA;
- tag;
- GitHub Release URL;
- model release ID and version;
- source-plan fingerprint;
- workflow names, run IDs, conclusions, and timestamps;
- Pages deployment URL;
- live release-meta payload;
- Pages artifact identity/digest where available;
- hashes for all authoritative manifests and generated evidence;
- closure-gate results;
- external-gate results;
- Drive document URL and final revision ID;
- known limitations;
- approver and approval timestamp.

The manifest must distinguish:

- **closure PASS** — public package is internally consistent and traceable;
- **external gates OPEN** — transaction evidence is incomplete;
- **bankable_transaction_ready = false**;
- **lender_approval_ready = false**;
- **ic_approval_ready = false**.

---

## 11. Rollback and incident handling

If a live mismatch is detected:

1. mark the release candidate failed;
2. do not move or reuse the final tag;
3. preserve the failed evidence package;
4. identify whether the mismatch came from source generation, artifact upload, Pages deployment, cache, or post-deploy verification;
5. fix on a new commit;
6. rerun every gate at the new SHA;
7. publish only after live SHA proof passes.

Do not force-update an already published final tag. Prefer a new patch release if a published immutable release needs correction.

---

## 12. Explicit non-goals

V4.1 must not:

- add new project-finance modules;
- revise investment assumptions without approved source evidence;
- close legal, tax, regulatory, technical, lender, PPA, or sponsor gates by inference;
- convert hypothetical negotiated terms into an achieved transaction claim;
- present recruiter readiness as bankability;
- store project working data outside Google Drive or GitHub;
- duplicate the repository locally for implementation.

---

## 13. Definition of done

V4.1 is done only when all statements below are true:

- [ ] P0 and P1 gaps are remediated.
- [ ] P2 visual/accessibility evidence is complete.
- [ ] The final candidate SHA is stable and validation is non-mutating.
- [ ] EXECUTIVE_SUMMARY.md and BUSINESS_CASE.md match the V4 manifest.
- [ ] fixedVsResized is removed or fully model-backed.
- [ ] stale-claim coverage includes all declared recruiter surfaces.
- [ ] metric lineage covers every public metric.
- [ ] scenario economic and credit statuses are separated.
- [ ] PPA geometry is data-driven and tested.
- [ ] release-meta.json is deployed and equals the final SHA.
- [ ] all 14 closure gates pass at that SHA.
- [ ] a final GitHub tag and Release point to that SHA.
- [ ] release provenance/immutability status is evidenced.
- [ ] the Drive control document points to the same release and records its final revision.
- [ ] all open external gates are shown truthfully.
- [ ] no project data was persisted locally.
- [ ] the V4.1 scope is frozen.

---

## 14. Primary research sources

Release and deployment controls:

- GitHub Pages custom workflows: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- GitHub Actions default variables and GITHUB_SHA: https://docs.github.com/en/actions/reference/workflows-and-actions/variables
- GitHub Actions event SHA semantics: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- GitHub immutable releases concept: https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases
- GitHub immutable release enablement: https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/establish-provenance-and-integrity/prevent-release-changes
- actions/upload-artifact: https://github.com/actions/upload-artifact
- WCAG 2.2 Recommendation: https://www.w3.org/TR/WCAG22/

Vietnam regulatory/billing context:

- MOIT Decision 963/QD-BCT page: https://moit.gov.vn/van-ban-phap-luat/quyet-dinh-ve-khung-gio-cao-diem-thap-diem-va-gio-binh-thuong-cua-he-thong-dien-quoc-gia.html
- MOIT Q2 2026 press briefing: https://moit.gov.vn/tin-tuc/bo-cong-thuong-hop-bao-thuong-ky-quy-ii-2026.html
- EVNSPC communication on revised time bands: https://evnspc.vn/bai-viet/ARTICLE26050004/ap-dung-khung-gio-su-dung-dien-moi-tu-22042026-chu-dong-dieu-chinh-thoi-quen-tiet-kiem-chi-phi-bao-ve-he-thong-dien
- Decree 58/2025/ND-CP: https://vanban.chinhphu.vn/?classid=1&docid=213011&orggroupid=2&pageid=27160
- Circular 60/2025/TT-BCT: https://vanban.chinhphu.vn/?classid=1&docid=216125&orggroupid=4&pageid=27160

---

## 15. Plan handoff

This plan is the final updated execution plan, not a completion certificate. The implementation agent must update the gap register and gate matrix with links to exact commits, workflow runs, artifacts, and Drive revision evidence. Any proposed change outside this document requires a separate scope decision.
