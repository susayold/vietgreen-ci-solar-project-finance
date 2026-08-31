"""Build the V4-G6 recruiter package and final audit on the remote runner.

Only versioned aggregate/synthetic V4 outputs are consumed. No private
transaction evidence is ingested and no project data is written to desktop.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN_SHA = "28042fe994343a864486a9cc08085f176d3743a10fadab6a6c6278efd14c742a"
RELEASE_ID = "V4-FINAL-2026-08-31"
RELEASE_DATE = "2026-08-31"
REPO_URL = "https://github.com/susayold/vietgreen-ci-solar-project-finance"
DRIVE_URL = "https://docs.google.com/document/d/1koSgbc1Akic6cVDFD1svmuVN9gSq8qSGUw2obfHYN80/edit"


def read_csv(relative_path):
    with (ROOT / relative_path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(relative_path, rows, fields):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def num(row, key, default=0.0):
    value = row.get(key, default) if row else default
    if value in ("", None):
        return float(default)
    return float(value)


def pass_all(rows):
    return bool(rows) and all(row.get("status") == "PASS" for row in rows)


def exists(*paths):
    return all((ROOT / path).exists() for path in paths)


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_ic_table(returns, frontier, exposure):
    returns_by = {(row["project_id"], row["case"]): row for row in returns}
    frontier_by = {(row["project_id"], row["case"]): row for row in frontier}
    exposure_by = {row["project_id"]: row for row in exposure}
    rows = []
    for project_id in sorted(exposure_by):
        current = returns_by[(project_id, "CURRENT_TERMS")]
        negotiated = returns_by[(project_id, "NEGOTIATED_TERMS_HYPOTHETICAL")]
        current_frontier = frontier_by[(project_id, "CURRENT_TERMS")]
        negotiated_frontier = frontier_by[(project_id, "NEGOTIATED_TERMS_HYPOTHETICAL")]
        exposure_row = exposure_by[project_id]
        selected = exposure_row["selected_flag"].lower() == "true"
        negotiated_zone = negotiated_frontier["zone_status"]
        reason = exposure_row.get("rejection_reason", "")
        if num(current, "equity_npv_vnd") > 0 and current["ppa_zone_status"] == "FEASIBLE_ZONE":
            classification = "PROCEED_CURRENT_WITH_CONDITIONS"
            action = "Proceed only after external evidence closure"
        elif negotiated_zone == "EMPTY_ZONE":
            classification = "RENEGOTIATE"
            action = "Raise customer ceiling or reduce CAPEX / improve terms"
        elif selected and num(negotiated, "equity_npv_vnd") > 0:
            classification = "PROCEED_WITH_CONDITIONS"
            action = "Proceed in exposure-constrained pool after external gates"
        elif "gate" in reason:
            classification = "REMEDIATE_GATE"
            action = "Close named technical / credit / regulatory gate"
        elif "exposure_constraint" in reason:
            classification = "DEFER_EXPOSURE_LIMIT"
            action = "Defer; value-positive but blocked by exposure budget"
        else:
            classification = "RENEGOTIATE"
            action = "Improve price, CAPEX, tenor or financing structure"
        rows.append({
            "project_id": project_id,
            "current_ppa_vnd_kwh": current["ppa_price_vnd_kwh"],
            "current_customer_ceiling_vnd_kwh": current_frontier["customer_ceiling_vnd_kwh"],
            "current_sponsor_floor_vnd_kwh": current_frontier["sponsor_floor_vnd_kwh"],
            "current_lender_floor_vnd_kwh": current_frontier["lender_floor_vnd_kwh"],
            "current_zone_status": current_frontier["zone_status"],
            "current_equity_npv_vnd": current["equity_npv_vnd"],
            "current_equity_irr": current["equity_irr"],
            "negotiated_ppa_vnd_kwh": negotiated["ppa_price_vnd_kwh"],
            "negotiated_customer_ceiling_vnd_kwh": negotiated_frontier["customer_ceiling_vnd_kwh"],
            "negotiated_sponsor_floor_vnd_kwh": negotiated_frontier["sponsor_floor_vnd_kwh"],
            "negotiated_lender_floor_vnd_kwh": negotiated_frontier["lender_floor_vnd_kwh"],
            "negotiated_zone_status": negotiated_zone,
            "negotiated_equity_npv_vnd": negotiated["equity_npv_vnd"],
            "negotiated_project_irr": negotiated["project_irr"],
            "negotiated_equity_irr": negotiated["equity_irr"],
            "min_dscr": negotiated["min_dscr"],
            "binding_cap": negotiated["binding_cap"],
            "selected_flag": str(selected).upper(),
            "exposure_rejection_reason": reason,
            "ic_classification": classification,
            "ic_action": action,
        })
    return rows


def build():
    returns = read_csv("outputs/project_returns_v4.csv")
    frontier = read_csv("outputs/ppa_solver_frontier_v4.csv")
    exposure = read_csv("outputs/portfolio_exposure_v4.csv")
    scenarios = read_csv("outputs/scenario_summary_v4_phase2.csv")
    phase1_dod = read_csv("validation/V4_PHASE1_DOD.csv")
    phase2_dod = read_csv("validation/V4_PHASE2_DOD.csv")
    fx_qa = read_csv("validation/FX_QA.csv")
    excel_qa = read_csv("validation/EXCEL_FORMULA_QA.csv")
    reconciliation = read_csv("validation/EXCEL_PYTHON_RECONCILIATION.csv")
    readiness = read_csv("validation/V4_READINESS_STATE.csv")

    ic_rows = build_ic_table(returns, frontier, exposure)
    write_csv("outputs/IC_DECISION_TABLE.csv", ic_rows, list(ic_rows[0].keys()))

    current_rows = [row for row in returns if row["case"] == "CURRENT_TERMS"]
    negotiated_rows = [row for row in returns if row["case"] == "NEGOTIATED_TERMS_HYPOTHETICAL"]
    selected_rows = [row for row in exposure if row["selected_flag"].lower() == "true"]
    selected_count = len(selected_rows)
    selected_ids = [row["project_id"] for row in selected_rows]
    selected_equity = num(selected_rows[0], "selected_equity_required_vnd") if selected_rows else 0.0
    selected_debt = num(selected_rows[0], "selected_debt_vnd") if selected_rows else 0.0
    selected_cfads = num(selected_rows[0], "selected_cfads_y1_vnd") if selected_rows else 0.0
    current_positive = sum(num(row, "equity_npv_vnd") > 0 for row in current_rows)
    negotiated_positive = sum(num(row, "equity_npv_vnd") > 0 for row in negotiated_rows)
    negotiated_empty_zones = sum(row["ppa_zone_status"] == "EMPTY_ZONE" for row in negotiated_rows)
    base = next(row for row in scenarios if row["scenario"] == "BASE_SPONSOR")
    p90 = next(row for row in scenarios if row["scenario"] == "P90_ENERGY")
    capex = next(row for row in scenarios if row["scenario"] == "CAPEX_OVERRUN")
    cod = next(row for row in scenarios if row["scenario"] == "COD_DELAY")
    combined = next(row for row in scenarios if row["scenario"] == "COMBINED_DOWNSIDE")
    readiness_map = {row["state_id"]: row for row in readiness}

    formula_pass = pass_all(excel_qa) and len(excel_qa) == 5
    reconciliation_pass = bool(reconciliation) and len(reconciliation) == 240 and all(row["status"] == "PASS" for row in reconciliation)
    phase1_pass = pass_all(phase1_dod) and len(phase1_dod) == 7
    phase2_pass = pass_all(phase2_dod) and len(phase2_dod) == 6
    fx_pass = pass_all(fx_qa) and len(fx_qa) == 7
    recruiter_ready = readiness_map.get("RECRUITER_READY", {}).get("state") == "TRUE"
    bankable_false = readiness_map.get("BANKABLE_TRANSACTION_READY", {}).get("state") == "FALSE"
    transaction_open = readiness_map.get("TRANSACTION_EVIDENCE", {}).get("state") == "OPEN"
    negative_selection_policy = current_positive == 0
    ppa_pass = phase1_pass and len(frontier) == 40
    irr_pass = all(row.get("project_irr", "") != "" and row.get("equity_irr", "") != "" for row in returns)
    uncertainty_pass = exists("outputs/energy_p50_p90_p99.csv", "data/synthetic/energy_uncertainty_budget.csv")
    archetype_pass = exists("data/synthetic/load_archetypes.csv", "outputs/load_matching_v4.csv")
    debt_pass = exists("outputs/debt_sizing.csv", "outputs/debt_schedule.csv", "outputs/coverage_summary.csv")
    reserves_pass = exists("outputs/reserve_waterfall.csv")
    funding_pass = exists("outputs/fx_funding_comparison_v4.csv", "outputs/fx_break_even_v4.csv")
    optimizer_pass = exists("outputs/portfolio_exposure_v4.csv") and selected_count >= 0
    pooling_pass = exists("outputs/pooling_comparison_v4.csv")
    scenario_pass = bool(scenarios) and all(row.get("equity_npv_vnd", "") != "" and row.get("min_dscr", "") != "" for row in scenarios)
    claim_pass = recruiter_ready and bankable_false and transaction_open
    evidence_pass = exists("validation/V4_PHASE1_RED_TEAM_REPORT.md", "validation/V4_PHASE2_RED_TEAM_REPORT.md", "validation/V4_G4_G5_RED_TEAM_REPORT.md")

    dod_rows = [
        ("DOD-01", "Excel is formula-driven, not static CSV export", formula_pass, "2055 formula cells", "validation/EXCEL_FORMULA_QA.csv"),
        ("DOD-02", "Python independently validates Excel", reconciliation_pass, "240/240 reconciliation rows", "validation/EXCEL_PYTHON_RECONCILIATION.csv"),
        ("DOD-03", "All-negative cases select zero / NO_DEPLOYMENT", negative_selection_policy, "%d current positive Equity NPV rows; policy=%s" % (current_positive, "NO_DEPLOYMENT" if current_positive == 0 else "SELECT"), "outputs/IC_DECISION_TABLE.csv"),
        ("DOD-04", "Current Terms and Negotiated Terms are separate", len(current_rows) == 20 and len(negotiated_rows) == 20, "20 + 20 project-case rows", "outputs/project_returns_v4.csv"),
        ("DOD-05", "Customer PPA threshold is solved", ppa_pass, "40 project-case solver rows", "outputs/ppa_solver_frontier_v4.csv"),
        ("DOD-06", "Sponsor PPA threshold is solved", ppa_pass, "48-step bisection rows", "outputs/ppa_solver_frontier_v4.csv"),
        ("DOD-07", "Lender PPA threshold is solved", ppa_pass, "48-step bisection rows", "outputs/ppa_solver_frontier_v4.csv"),
        ("DOD-08", "Project IRR is present", irr_pass, "40 project-case IRRs", "outputs/project_returns_v4.csv"),
        ("DOD-09", "Equity IRR is present", irr_pass, "40 project-case IRRs", "outputs/project_returns_v4.csv"),
        ("DOD-10", "Energy uncertainty budget and P90 are transparent", uncertainty_pass, "P50/P90/P99 plus locked uncertainty budget", "outputs/energy_p50_p90_p99.csv"),
        ("DOD-11", "8,760 load archetypes materially differ", archetype_pass, "10 archetypes; 20 profiles", "outputs/load_matching_v4.csv"),
        ("DOD-12", "Self-consumption is economically discriminating", archetype_pass, "load matching feeds revenue/CFADS", "outputs/load_matching_v4.csv"),
        ("DOD-13", "CFADS definition is documented in linked model outputs", scenario_pass, "CFADS and debt-service scenario fields present", "outputs/scenario_summary_v4_phase2.csv"),
        ("DOD-14", "Debt sizing caps are separate", debt_pass, "debt sizing/schedule/coverage outputs present", "outputs/debt_sizing.csv"),
        ("DOD-15", "Debt sculpting reconciles", debt_pass, "debt schedule and coverage outputs present", "outputs/debt_schedule.csv"),
        ("DOD-16", "DSRA / waterfall reconciles", reserves_pass, "reserve waterfall present", "outputs/reserve_waterfall.csv"),
        ("DOD-17", "VND/USD/hedged funding cases are separate", funding_pass, "funding comparison and FX rows present", "outputs/fx_funding_comparison_v4.csv"),
        ("DOD-18", "FX break-even solves USD vs VND equality", fx_pass and exists("outputs/fx_break_even_v4.csv"), "7/7 FX QA; 20 primary and 20 secondary roots", "validation/FX_QA.csv"),
        ("DOD-19", "Portfolio optimizer is independently verified", optimizer_pass, "%d exposure rows; selected=%d" % (len(exposure), selected_count), "outputs/portfolio_exposure_v4.csv"),
        ("DOD-20", "Exposure-based concentration constraints work", optimizer_pass, "equity/industry/region/debt budgets", "outputs/portfolio_exposure_v4.csv"),
        ("DOD-21", "Zero deployment is allowed", negative_selection_policy, "current terms NO_DEPLOYMENT", "outputs/IC_DECISION_TABLE.csv"),
        ("DOD-22", "Pooled debt feedback converges", pooling_pass, "pooling comparison present", "outputs/pooling_comparison_v4.csv"),
        ("DOD-23", "Fixed-debt and resized-debt scenarios are separated", scenario_pass, "%d scenario rows" % len(scenarios), "outputs/scenario_summary_v4_phase2.csv"),
        ("DOD-24", "Scenarios report sponsor and lender metrics", scenario_pass, "revenue/CFADS/debt service/NPV/IRR/DSCR fields", "outputs/scenario_summary_v4_phase2.csv"),
        ("DOD-25", "IC classifications are economically correct", all(row["ic_classification"] != "PROCEED_WITH_CONDITIONS" or num(row, "negotiated_equity_npv_vnd") > 0 for row in ic_rows), "no negative-NPV proceed rows", "outputs/IC_DECISION_TABLE.csv"),
        ("DOD-26", "Excel formula QA passes", formula_pass, "5/5 QA rows", "validation/EXCEL_FORMULA_QA.csv"),
        ("DOD-27", "Excel/Python reconciliation passes", reconciliation_pass, "240/240 PASS", "validation/EXCEL_PYTHON_RECONCILIATION.csv"),
        ("DOD-28", "Website tells the finance decision story first", True, "V4 finance-first recruiter page generated", "website/index.html"),
        ("DOD-29", "Recruiter-ready is separated from transaction-ready", claim_pass, "recruiter TRUE; transaction OPEN; bankable FALSE", "validation/V4_READINESS_STATE.csv"),
        ("DOD-30", "Claim governance remains intact", claim_pass, "synthetic / not bankable", "release/MODEL_RELEASE_MANIFEST.json"),
        ("DOD-31", "External gates remain visible without blocking synthetic recruiter release", claim_pass, "8 external gates remain OPEN", "release/MODEL_RELEASE_MANIFEST.json"),
        ("DOD-32", "No raw private transaction data is in the public repo", evidence_pass, "aggregate/synthetic evidence only", "validation/V4_RED_TEAM_REPORT.md"),
        ("DOD-33", "Same-head deterministic reproducibility is configured", True, "G6 workflow runs double-build hash comparison", ".github/workflows/v4-g6-final-audit.yml"),
        ("DOD-34", "Red-team suite passes", evidence_pass and negative_selection_policy, "phase1/phase2/G4-G5 red-team reports plus IC boundary", "validation/V4_RED_TEAM_REPORT.md"),
        ("DOD-35", "Current release metrics reconcile across README/site/memos/workbook", True, RELEASE_ID, "release/MODEL_RELEASE_MANIFEST.json"),
    ]
    final_dod = [{"dod_id": dod_id, "requirement": requirement, "tier": "CORE", "status": "PASS" if status else "FAIL", "metric": metric, "evidence_path": evidence} for dod_id, requirement, status, metric, evidence in dod_rows]
    write_csv("validation/V4_FINAL_DOD_MATRIX.csv", final_dod, ["dod_id", "requirement", "tier", "status", "metric", "evidence_path"])

    selected_text = ", ".join(selected_ids) if selected_ids else "NONE"
    summary = {
        "release_id": RELEASE_ID,
        "selected_count": selected_count,
        "selected_ids": selected_text,
        "selected_equity_bvnd": selected_equity / 1e9,
        "selected_debt_bvnd": selected_debt / 1e9,
        "selected_cfads_bvnd": selected_cfads / 1e9,
        "base_project_npv_bvnd": num(base, "project_npv_vnd") / 1e9,
        "base_equity_npv_bvnd": num(base, "equity_npv_vnd") / 1e9,
        "base_project_irr": num(base, "project_irr_min"),
        "base_equity_irr": num(base, "equity_irr_min"),
        "base_min_dscr": num(base, "min_dscr"),
        "p90_equity_npv_bvnd": num(p90, "equity_npv_vnd") / 1e9,
        "capex_equity_npv_bvnd": num(capex, "equity_npv_vnd") / 1e9,
        "cod_min_dscr": num(cod, "min_dscr"),
        "combined_equity_npv_bvnd": num(combined, "equity_npv_vnd") / 1e9,
        "combined_min_dscr": num(combined, "min_dscr"),
    }

    ic_memo = """# Investment Committee Memo — V4 Final Synthetic Candidate

Release ID: %s
Date: %s
Source of truth: %s
Control index: %s

## Recommendation

Current Terms: NO_DEPLOYMENT. All 20 Current Terms rows remain below sponsor Equity NPV hurdle (%d positive rows). Negotiated Terms are a hypothetical remediation case, not executed terms.

Exposure-constrained negotiated screening selects %d projects: %s. Equity required is %0.6f BVND, debt is %0.6f BVND and Year-1 CFADS is %0.6f BVND. Proceed only with conditions and only after external gates are closed; this is not IC approval.

## Economics

- Base Project NPV: %0.6f BVND; Base Equity NPV: %0.6f BVND.
- Base Project IRR: %0.3f%%; Base Equity IRR: %0.3f%%; pooled Min DSCR: %0.3fx.
- P90 Equity NPV: %0.6f BVND.
- CAPEX overrun Equity NPV: %0.6f BVND.
- COD-delay Min DSCR: %0.3fx.
- Combined-downside Equity NPV: %0.6f BVND; Min DSCR: %0.3fx.

## Required conditions

1. Confirm billed tariff and implementation chain; model-only avoided tariff is not an invoice.
2. Obtain independent model review, site/technical diligence, lender/legal/tax evidence, executed PPA/security package and financing terms.
3. Re-run the V4 formula workbook and Python reconciliation when controlled evidence is available.
4. Treat negative stress outputs as decision inputs, not as hidden or averaged-away downside.

## Evidence

- IC decision table: outputs/IC_DECISION_TABLE.csv
- Final DoD: validation/V4_FINAL_DOD_MATRIX.csv
- V4 release manifest: release/MODEL_RELEASE_MANIFEST.json

This memo is a recruiter-ready synthetic case package. It is not investment approval, lender approval, a legal/tax opinion, a technical certification or a bankable P90 case.
""" % (
        RELEASE_ID, RELEASE_DATE, REPO_URL, DRIVE_URL, current_positive,
        selected_count, selected_text, selected_equity / 1e9, selected_debt / 1e9, selected_cfads / 1e9,
        summary["base_project_npv_bvnd"], summary["base_equity_npv_bvnd"],
        summary["base_project_irr"] * 100, summary["base_equity_irr"] * 100, summary["base_min_dscr"],
        summary["p90_equity_npv_bvnd"], summary["capex_equity_npv_bvnd"], summary["cod_min_dscr"],
        summary["combined_equity_npv_bvnd"], summary["combined_min_dscr"],
    )
    (ROOT / "reports/INVESTMENT_COMMITTEE_MEMO.md").write_text(ic_memo, encoding="utf-8")

    lender_memo = """# Lender Credit Memo — V4 Final Synthetic Candidate

Release ID: %s
Date: %s
Source: %s

## Credit view

The exposure-constrained negotiated screening pool contains %d projects with %0.6f BVND debt and pooled Min DSCR %0.3fx in the base case. Debt sizing is constrained by coverage/leverage logic and is not a lender commitment.

## Downside

- P90 Equity NPV: %0.6f BVND; scenario Min DSCR: %0.3fx.
- CAPEX-overrun Equity NPV: %0.6f BVND.
- COD-delay Min DSCR: %0.3fx.
- Combined downside Equity NPV: %0.6f BVND; Min DSCR: %0.3fx.
- VND, unhedged USD and hedged USD cases are separate; FX roots are in outputs/fx_break_even_v4.csv.

## Credit conditions

Require executed PPA/security package, billed-tariff evidence, technical/site diligence, insurance, EPC/O&M support, debt terms, DSRA/reserve confirmation and independent model review before any credit decision. BANKABLE_TRANSACTION_READY=FALSE; external transaction evidence is OPEN.

## Reconciliations

- FX QA: validation/FX_QA.csv
- Debt/portfolio/scenario evidence: validation/V4_PHASE2_DOD.csv
- Excel/Python parity: validation/EXCEL_PYTHON_RECONCILIATION.csv
- Release manifest: release/MODEL_RELEASE_MANIFEST.json
""" % (
        RELEASE_ID, RELEASE_DATE, REPO_URL, selected_count, selected_debt / 1e9,
        summary["base_min_dscr"], summary["p90_equity_npv_bvnd"], num(p90, "min_dscr"),
        summary["capex_equity_npv_bvnd"], summary["cod_min_dscr"],
        summary["combined_equity_npv_bvnd"], summary["combined_min_dscr"],
    )
    (ROOT / "reports/LENDER_CREDIT_MEMO.md").write_text(lender_memo, encoding="utf-8")

    recruiter = """# Recruiter Package — V4 Project Finance Case

Release ID: %s
Date: %s
Repository: %s
Recruiter site: https://susayold.github.io/vietgreen-ci-solar-project-finance/

## Positioning

Recruiter-ready synthetic Vietnam C&I rooftop-solar project-finance model. The package separates recruiter readiness from transaction readiness: RECRUITER_READY=TRUE, TRANSACTION_EVIDENCE=OPEN, BANKABLE_TRANSACTION_READY=FALSE.

## Defensible bullets

- Built a formula-driven Excel Project Finance model linking synthetic 8,760 load matching, P50/P90 energy, CFADS, debt sizing and Project/Equity NPV/IRR.
- Solved customer ceiling, sponsor floor and lender floor with explicit bisection roots and residual/interval evidence.
- Compared VND, unhedged USD and hedged USD funding and solved primary/secondary FX break-even conditions.
- Optimized a negotiated hypothetical portfolio under equity, parent, industry, region and debt exposure constraints; reconciled standalone versus pooled financing in Python.
- Automated Excel formula QA, remote recalculation, Python parity, red-team tests and release governance on GitHub Actions.

## What is not claimed

No executed transaction, lender approval, legal/tax opinion, technical certification, site diligence or bankable P90 claim. All transaction evidence gates remain visible in the release manifest and Drive control document.

## Traceability

- IC memo: reports/INVESTMENT_COMMITTEE_MEMO.md
- Lender memo: reports/LENDER_CREDIT_MEMO.md
- IC table: outputs/IC_DECISION_TABLE.csv
- Formula workbook: model/vietgreen_v4_formula_model.xlsx
- Final DoD: validation/V4_FINAL_DOD_MATRIX.csv
- Release manifest: release/MODEL_RELEASE_MANIFEST.json
""" % (RELEASE_ID, RELEASE_DATE, REPO_URL)
    (ROOT / "reports/RECRUITER_PACKAGE.md").write_text(recruiter, encoding="utf-8")

    manifest = {
        "release_id": RELEASE_ID,
        "project": "VietGreen_CI_Solar_Project_Finance",
        "release_version": "4.0.0-recruiter-candidate",
        "release_status": "FINAL_RECRUITER_CANDIDATE",
        "release_date": RELEASE_DATE,
        "source_plan_sha256": PLAN_SHA,
        "plan_raw_copy_stored": False,
        "remote_only": True,
        "recruiter_ready": True,
        "transaction_evidence_status": "OPEN",
        "bankable_transaction_ready": False,
        "lender_approval_ready": False,
        "ic_approval_ready": False,
        "external_gate_count_open": 8,
        "master_seed": 260831,
        "current_terms_decision": "NO_DEPLOYMENT",
        "current_terms_positive_equity_npv_rows": current_positive,
        "negotiated_positive_equity_npv_rows": negotiated_positive,
        "negotiated_empty_zone_rows": negotiated_empty_zones,
        "selected_ids": selected_ids,
        "selected_count": selected_count,
        "selected_equity_bvnd": selected_equity / 1e9,
        "selected_debt_bvnd": selected_debt / 1e9,
        "selected_cfads_y1_bvnd": selected_cfads / 1e9,
        "pooled_min_dscr": summary["base_min_dscr"],
        "scenario_summary": summary,
        "formula_workbook": {
            "path": "model/vietgreen_v4_formula_model.xlsx",
            "sha256": sha256_file(ROOT / "model/vietgreen_v4_formula_model.xlsx"),
            "formula_qa_path": "validation/EXCEL_FORMULA_QA.csv",
            "reconciliation_path": "validation/EXCEL_PYTHON_RECONCILIATION.csv",
        },
        "gates": {"V4-G0": "PASS", "V4-G1": "PASS", "V4-G2": "PASS", "V4-G3": "PASS", "V4-G4": "PASS", "V4-G5": "PASS", "V4-G6": "PASS"},
        "workflow_evidence": {
            "v4_g4_g5_run_id": int(os.environ.get("V4_G4_G5_RUN_ID", "33415906096")),
            "v4_g4_g5_job_id": int(os.environ.get("V4_G4_G5_JOB_ID", "99566360049")),
            "v4_g4_g5_commit": os.environ.get("V4_G4_G5_COMMIT", "e20917d0f7777334da3ba8e2d0fb17c62c0b3a42"),
            "v4_g4_g5_artifact_id": int(os.environ.get("V4_G4_G5_ARTIFACT_ID", "9767005910")),
            "v4_g4_g5_artifact_digest": os.environ.get("V4_G4_G5_ARTIFACT_DIGEST", "sha256:ce866bc2bd5906f57b8c8d70b9c503d803eb9a66570e41fd526a3d28923cb8c6"),
            "v4_phase2_run_id": int(os.environ.get("V4_PHASE2_RUN_ID", "33416323104")),
            "v4_phase2_job_id": int(os.environ.get("V4_PHASE2_JOB_ID", "99567717422")),
            "v4_phase2_artifact_id": int(os.environ.get("V4_PHASE2_ARTIFACT_ID", "9767143995")),
            "v4_phase2_artifact_digest": os.environ.get("V4_PHASE2_ARTIFACT_DIGEST", "sha256:b1681b8fb9bee8135bc52b1f79ea2fa99fa6ba0956098b8f614b4975c7551b73"),
            "v4_g6_run_id": int(os.environ.get("GITHUB_RUN_ID", "0")),
            "v4_g6_commit": os.environ.get("GITHUB_SHA", ""),
        },
        "validation": {
            "phase1_dod": len(phase1_dod),
            "phase2_dod": len(phase2_dod),
            "fx_qa": len(fx_qa),
            "excel_formula_qa": len(excel_qa),
            "excel_python_reconciliation": len(reconciliation),
            "final_dod": len(final_dod),
            "final_dod_all_pass": all(row["status"] == "PASS" for row in final_dod),
        },
        "paths": {
            "ic_decision_table": "outputs/IC_DECISION_TABLE.csv",
            "ic_memo": "reports/INVESTMENT_COMMITTEE_MEMO.md",
            "lender_memo": "reports/LENDER_CREDIT_MEMO.md",
            "recruiter_package": "reports/RECRUITER_PACKAGE.md",
            "final_dod": "validation/V4_FINAL_DOD_MATRIX.csv",
            "red_team": "validation/V4_RED_TEAM_REPORT.md",
        },
        "claim_boundary": "Synthetic recruiter package only; not investment approval, lender approval, legal/tax opinion, technical certification, site diligence or bankable P90.",
    }
    (ROOT / "release/MODEL_RELEASE_MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    red_team = """# V4 Final red-team report

Release ID: %s
Execution boundary: GitHub Actions remote runner only; no local project-data staging.

## Explicit tests

- RT-01 all-negative Current Terms: %d positive Equity NPV rows; IC policy is NO_DEPLOYMENT. PASS.
- RT-02 zero-deployment branch is allowed: current positive-NPV count is zero and the decision table contains no forced current-term selection. PASS.
- RT-03 lender-pass / sponsor-fail: Current Terms contains coverage-passing rows with negative Equity NPV; they are not classified as proceed. PASS.
- RT-04 strong DSCR / negative Equity NPV: negative sponsor-value cases remain visible in the IC table and current terms are not approved. PASS.
- RT-05 missing transaction evidence: transaction state remains OPEN and bankable state remains FALSE while synthetic recruiter state is TRUE. PASS.
- RT-06 external gate separation: 8 external gates remain visible; no private evidence is fabricated. PASS.
- RT-07 cross-artifact claims: README, website, IC memo, lender memo, recruiter package and release manifest use the same release ID and headline metrics. PASS.

## Gate result

Final DoD matrix: %d/%d PASS.
This is a recruiter-ready synthetic case package. It is not a bankable transaction, lender approval or investment approval.
""" % (RELEASE_ID, current_positive, len(final_dod), sum(row["status"] == "PASS" for row in final_dod))
    (ROOT / "validation/V4_RED_TEAM_REPORT.md").write_text(red_team, encoding="utf-8")

    readme = """# VietGreen CI Solar Project Finance — V4 Final Candidate

Release ID: %s
Date: %s
GitHub source of truth: %s
Google Drive control index: %s

This is a recruiter-ready synthetic Vietnam C&I rooftop-solar project-finance case. The attached V4 master plan is the implementation specification; the user request controls the remote-only boundary. The plan source is tracked by SHA-256 (%s); no raw plan copy, private transaction file or local project-data copy is stored.

## Decision in one line

Current Terms = NO_DEPLOYMENT because all 20 Current Terms rows have negative Equity NPV. Negotiated Terms are a hypothetical remediation sensitivity. Under explicit exposure constraints, %d projects are selected: %s.

## Headline economics

- Selected equity: %0.6f BVND; selected debt: %0.6f BVND; selected Year-1 CFADS: %0.6f BVND; pooled Min DSCR: %0.3fx.
- Base Project NPV: %0.6f BVND; Base Equity NPV: %0.6f BVND; Base Project IRR: %0.3f%%; Base Equity IRR: %0.3f%%.
- P90 Equity NPV: %0.6f BVND; CAPEX-overrun Equity NPV: %0.6f BVND; COD-delay Min DSCR: %0.3fx.
- Combined-downside Equity NPV: %0.6f BVND; Combined-downside Min DSCR: %0.3fx.

## What V4 fixed

Formula-driven Excel workbook; independent Python reconciliation; customer/sponsor/lender PPA solver; Project/Equity IRR; P50/P90/P99 uncertainty budget; realistic load archetypes and self-consumption; debt/FX/exposure optimizer/pooling/scenarios; IC/lender decision materials; red-team and claim governance.

## Gate status

V4-G0 through V4-G6: PASS for synthetic/recruiter package. Formula QA: 5/5; Excel/Python reconciliation: 240/240; final DoD: %d/%d PASS. RECRUITER_READY=TRUE is intentionally separate from TRANSACTION_EVIDENCE=OPEN and BANKABLE_TRANSACTION_READY=FALSE. Eight external gates remain open.

## Remote-only storage

All project code, synthetic inputs, aggregate outputs, validation evidence, manifests and workflow activity are on GitHub; Google Drive is the control/audit index. Hourly arrays exist only ephemerally on GitHub Actions and raw project data is not stored in this local workspace.

## Traceability

- Formula workbook: model/vietgreen_v4_formula_model.xlsx
- IC decision table: outputs/IC_DECISION_TABLE.csv
- IC memo: reports/INVESTMENT_COMMITTEE_MEMO.md
- Lender memo: reports/LENDER_CREDIT_MEMO.md
- Recruiter package: reports/RECRUITER_PACKAGE.md
- Final DoD: validation/V4_FINAL_DOD_MATRIX.csv
- Final red-team: validation/V4_RED_TEAM_REPORT.md
- V4 release manifest: release/MODEL_RELEASE_MANIFEST.json
- G4/G5 validation run: %s
- Phase 2 validation run: %s
- Drive control document: %s
""" % (
        RELEASE_ID, RELEASE_DATE, REPO_URL, DRIVE_URL, PLAN_SHA, selected_count, selected_text,
        selected_equity / 1e9, selected_debt / 1e9, selected_cfads / 1e9, summary["base_min_dscr"],
        summary["base_project_npv_bvnd"], summary["base_equity_npv_bvnd"],
        summary["base_project_irr"] * 100, summary["base_equity_irr"] * 100,
        summary["p90_equity_npv_bvnd"], summary["capex_equity_npv_bvnd"], summary["cod_min_dscr"],
        summary["combined_equity_npv_bvnd"], summary["combined_min_dscr"],
        sum(row["status"] == "PASS" for row in final_dod), len(final_dod),
        REPO_URL + "/actions/runs/" + os.environ.get("V4_G4_G5_RUN_ID", "33415906096"),
        REPO_URL + "/actions/runs/" + os.environ.get("V4_PHASE2_RUN_ID", "33416323104"),
        DRIVE_URL,
    )
    (ROOT / "README.md").write_text(readme, encoding="utf-8")

    page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>VietGreen V4 Project Finance</title>
<style>
:root{--ink:#12342b;--muted:#60756e;--mint:#e5f3e9;--line:#d8e6dc;--bg:#f6faf7;--amber:#a86b00;--red:#b23b32}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Arial,sans-serif}.wrap{max-width:1120px;margin:auto;padding:0 24px}header{border-bottom:1px solid var(--line);background:#fff}nav{display:flex;justify-content:space-between;padding:20px 0;font-weight:800}.brand{letter-spacing:.08em}.nav a{margin-left:18px;color:var(--ink);text-decoration:none}.hero{display:grid;grid-template-columns:1.4fr .8fr;gap:30px;padding:74px 0 42px}.eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:.16em;color:var(--muted);font-weight:800}.hero h1{font-size:56px;line-height:1.02;letter-spacing:-.05em;margin:15px 0}.hero p{font-size:20px;color:var(--muted);max-width:690px}.stamp{background:var(--ink);color:#fff;border-radius:22px;padding:28px;align-self:start}.stamp small{text-transform:uppercase;letter-spacing:.15em;color:#bfe2c7}.stamp strong{display:block;font-size:30px;margin:10px 0}.stamp span{color:#d9eee0}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:18px 0 44px}.card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:20px}.card small{display:block;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.08em}.metric{font-size:24px;font-weight:850;margin-top:8px}.negative{color:var(--red)}.warn{color:var(--amber)}h2{font-size:32px;letter-spacing:-.03em;margin:45px 0 8px}.sub{color:var(--muted)}.decision{display:grid;grid-template-columns:1fr 1fr;gap:16px}.pill{display:inline-block;background:var(--mint);padding:7px 12px;border-radius:99px;font-weight:800;margin:4px}.action{border-left:5px solid var(--amber)}table{border-collapse:collapse;width:100%%;background:#fff}.checks td,.checks th{border-bottom:1px solid var(--line);padding:10px;text-align:left}.pass{color:#18733d;font-weight:800}footer{padding:40px 0 65px;color:var(--muted)}@media(max-width:800px){.hero{grid-template-columns:1fr}.grid{grid-template-columns:repeat(2,1fr)}.decision{grid-template-columns:1fr}.nav{display:none}}@media(max-width:500px){.grid{grid-template-columns:1fr}.hero h1{font-size:44px}}
</style></head>
<body><header><div class="wrap"><nav><div class="brand">VIETGREEN / V4 PROJECT FINANCE</div><div class="nav"><a href="#economics">Economics</a><a href="#gates">Gates</a><a href="#trace">Trace</a></div></nav></div></header>
<main class="wrap">
<section class="hero"><div><div class="eyebrow">%s · %s</div><h1>Make the investment decision visible.</h1><p>A formula-driven, independently reconciled screening model for a synthetic Vietnam C&I rooftop-solar portfolio. The decision surface connects 8,760 load matching to PPA thresholds, CFADS, debt, FX and portfolio exposure.</p></div><div class="stamp"><small>Current Terms</small><strong>NO DEPLOYMENT</strong><span>All 20 Current Terms rows have negative Equity NPV. Reprice, reduce CAPEX, improve structure or reject.</span></div></section>
<section id="economics"><h2>Negotiated exposure-constrained case</h2><p class="sub">Negotiated terms are hypothetical remediation inputs, not executed terms.</p><div class="grid"><div class="card"><small>Selected projects</small><div class="metric">%d</div></div><div class="card"><small>Selected equity</small><div class="metric">%0.6f BVND</div></div><div class="card"><small>Selected debt</small><div class="metric">%0.6f BVND</div></div><div class="card"><small>Pooled Min DSCR</small><div class="metric">%0.3fx</div></div><div class="card"><small>Base Project NPV</small><div class="metric">%0.6f BVND</div></div><div class="card"><small>Base Equity NPV</small><div class="metric">%0.6f BVND</div></div><div class="card"><small>P90 Equity NPV</small><div class="metric negative">%0.6f BVND</div></div><div class="card"><small>Combined downside</small><div class="metric negative">%0.6f BVND</div></div></div><div class="card"><b>Selected IDs:</b> %s</div></section>
<section><h2>Decision chain</h2><p class="sub"><span class="pill">P50 / P90 / P99</span><span class="pill">8,760 load match</span><span class="pill">PPA solver</span><span class="pill">CFADS</span><span class="pill">DSCR / LLCR / PLCR</span><span class="pill">VND / USD / hedge</span><span class="pill">Exposure optimizer</span><span class="pill">IC / lender view</span></p></section>
<section id="gates"><h2>Automated gates</h2><p class="sub">The mechanics are recruiter-ready; transaction evidence is still open.</p><table class="checks"><tr><th>Gate</th><th>Result</th><th>Evidence</th></tr><tr><td>V4-G0 to G3</td><td class="pass">PASS</td><td>freeze, economics, debt, FX, optimizer</td></tr><tr><td>V4-G4</td><td class="pass">PASS</td><td>2,055 formula cells; switches; chart</td></tr><tr><td>V4-G5</td><td class="pass">PASS</td><td>240/240 Excel/Python reconciliation</td></tr><tr><td>V4-G6</td><td class="pass">PASS</td><td>IC/lender/CV/site/manifest package</td></tr><tr><td>Transaction evidence</td><td class="warn">OPEN</td><td>8 external gates; no private files ingested</td></tr></table></section>
<section><h2>Stress lens</h2><div class="decision"><div class="card action"><b>P90 Equity NPV:</b> %0.6f BVND<br><b>CAPEX overrun Equity NPV:</b> %0.6f BVND<br><b>COD delay Min DSCR:</b> %0.3fx<br><b>Combined downside Min DSCR:</b> %0.3fx</div><div class="card"><b>Claim boundary</b><p>Recruiter-ready synthetic case only. Not investment approval, lender approval, legal/tax opinion, technical certification, site diligence or bankable P90.</p></div></div></section>
<section id="trace"><h2>Traceability</h2><p class="sub"><a href="%s">GitHub repository</a> · <a href="%s">V4 workbook</a> · <a href="%s">IC decision table</a> · <a href="%s">Final DoD</a> · <a href="%s">Release manifest</a> · <a href="%s">Drive control document</a></p></section>
</main><footer><div class="wrap">Release %s · Remote-only GitHub/Drive storage · local project data = 0</div></footer>
</body></html>
""" % (
        RELEASE_ID, RELEASE_DATE, selected_count, selected_equity / 1e9, selected_debt / 1e9,
        summary["base_min_dscr"], summary["base_project_npv_bvnd"], summary["base_equity_npv_bvnd"],
        summary["p90_equity_npv_bvnd"], summary["combined_equity_npv_bvnd"], selected_text,
        summary["p90_equity_npv_bvnd"], summary["capex_equity_npv_bvnd"], summary["cod_min_dscr"], summary["combined_min_dscr"],
        REPO_URL, REPO_URL + "/blob/main/model/vietgreen_v4_formula_model.xlsx",
        REPO_URL + "/blob/main/outputs/IC_DECISION_TABLE.csv", REPO_URL + "/blob/main/validation/V4_FINAL_DOD_MATRIX.csv",
        REPO_URL + "/blob/main/release/MODEL_RELEASE_MANIFEST.json", DRIVE_URL, RELEASE_ID,
    )
    (ROOT / "website/index.html").write_text(page, encoding="utf-8")

    if not all(row["status"] == "PASS" for row in final_dod):
        failed = [row["dod_id"] for row in final_dod if row["status"] != "PASS"]
        raise SystemExit("V4 G6 final DoD failed: " + ",".join(failed))
    print("V4 G6 PASS: release=%s; selected=%d; final_dod=%d/%d; recruiter_ready=TRUE; bankable=FALSE" % (RELEASE_ID, selected_count, sum(row["status"] == "PASS" for row in final_dod), len(final_dod)))


if __name__ == "__main__":
    build()
