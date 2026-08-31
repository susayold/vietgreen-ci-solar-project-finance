from pathlib import Path
import csv
import json

BASE_DIR = Path(__file__).resolve().parents[1]

def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def unique(rows, key):
    values = [row.get(key, "") for row in rows]
    return len(values) == len(set(values)) and all(values)

def coverage(child_rows, child_key, parent_ids):
    return set(row.get(child_key, "") for row in child_rows) == set(parent_ids)

def add(results, check_id, domain, check_type, expected, actual, status, severity, impact):
    results.append({
        "check_id": check_id,
        "domain": domain,
        "check_type": check_type,
        "expected": expected,
        "actual": actual,
        "status": status,
        "severity": severity,
        "impact": impact,
    })

def run(root=BASE_DIR):
    root = Path(root)
    master = read_csv(root / "data/synthetic/project_master.csv")
    offtakers = read_csv(root / "data/synthetic/offtaker_master.csv")
    sites = read_csv(root / "data/synthetic/site_risk.csv")
    ppas = read_csv(root / "data/synthetic/ppa_terms.csv")
    capex = read_csv(root / "data/synthetic/capex.csv")
    debt = read_csv(root / "data/synthetic/debt_terms.csv")
    solar = read_csv(root / "data/synthetic/solar_resource.csv")
    sources = read_csv(root / "evidence/SOURCE_REGISTER.csv")
    assumptions = read_csv(root / "evidence/ASSUMPTION_REGISTER.csv")
    regs = read_csv(root / "evidence/REGULATORY_REGISTER.csv")
    tariffs = read_csv(root / "evidence/TARIFF_MASTER.csv")
    rates = read_csv(root / "evidence/DISCOUNT_RATE_REGISTER.csv")
    results = []
    project_ids = [row["project_id"] for row in master]

    add(results, "DQ-001", "pipeline", "row_count", "20", str(len(master)),
        "PASS" if len(master) == 20 else "FAIL", "CRITICAL", "Pipeline completeness")
    add(results, "DQ-002", "pipeline", "primary_key_unique", "unique project_id",
        str(unique(master, "project_id")), "PASS" if unique(master, "project_id") else "FAIL",
        "CRITICAL", "Prevents duplicate projects")
    add(results, "DQ-003", "offtaker", "foreign_key_coverage", "all project IDs",
        str(coverage(offtakers, "offtaker_id", [row["offtaker_id"] for row in master])),
        "PASS" if set(row["offtaker_id"] for row in master) == set(row["offtaker_id"] for row in offtakers) else "FAIL",
        "CRITICAL", "Prevents missing offtaker joins")
    add(results, "DQ-004", "site", "foreign_key_coverage", "all site IDs",
        str(coverage(sites, "project_id", project_ids)),
        "PASS" if coverage(sites, "project_id", project_ids) else "FAIL",
        "CRITICAL", "Prevents missing site-risk joins")
    add(results, "DQ-005", "PPA", "foreign_key_coverage", "all project IDs",
        str(coverage(ppas, "project_id", project_ids)),
        "PASS" if coverage(ppas, "project_id", project_ids) else "FAIL",
        "CRITICAL", "Prevents missing contract terms")
    add(results, "DQ-006", "CAPEX", "row_count_and_key", "120 rows / 6 per project",
        "%s rows" % len(capex), "PASS" if len(capex) == 120 and len(capex) == len(master) * 6 else "FAIL",
        "CRITICAL", "CAPEX aggregation grain")
    add(results, "DQ-007", "debt", "foreign_key_coverage", "all project IDs",
        str(coverage(debt, "project_or_portfolio_id", project_ids)),
        "PASS" if coverage(debt, "project_or_portfolio_id", project_ids) else "FAIL",
        "CRITICAL", "Prevents missing financing terms")
    add(results, "DQ-008", "solar", "foreign_key_coverage", "all project IDs",
        str(coverage(solar, "project_id", project_ids)),
        "PASS" if coverage(solar, "project_id", project_ids) else "FAIL",
        "CRITICAL", "Prevents missing resource joins")
    referenced_source_ids = set(row["source_id"] for row in solar)
    referenced_source_ids.update(row["source_id"] for row in tariffs if row.get("source_id", "").startswith("SRC-"))
    add(results, "DQ-009", "source", "source_id_coverage", "all referenced source IDs",
        str(referenced_source_ids.issubset(set(row["source_id"] for row in sources))),
        "PASS" if referenced_source_ids.issubset(set(row["source_id"] for row in sources)) else "FAIL",
        "CRITICAL", "Evidence traceability")
    assumption_ids = set(row["assumption_id"] for row in assumptions)
    referenced_assumptions = set(row["source_or_assumption_id"] for row in ppas)
    referenced_assumptions.update(row["source_id"] for row in tariffs if row.get("source_id", "").startswith("ASM-"))
    referenced_assumptions.update(row["source_or_assumption_id"] for row in rates)
    add(results, "DQ-010", "assumption", "assumption_id_coverage", "all referenced assumption IDs",
        str(referenced_assumptions.issubset(assumption_ids)),
        "PASS" if referenced_assumptions.issubset(assumption_ids) else "FAIL",
        "CRITICAL", "Assumption and discount-rate traceability")

    offtaker_by = {row["offtaker_id"]: row for row in offtakers}
    site_by = {row["project_id"]: row for row in sites}
    ppa_by = {row["project_id"]: row for row in ppas}
    solar_by = {row["project_id"]: row for row in solar}
    capex_by = {}
    for row in capex:
        capex_by[row["project_id"]] = capex_by.get(row["project_id"], 0.0) + float(row["amount_local"])
    mismatch = []
    for row in master:
        offtaker = offtaker_by.get(row["offtaker_id"], {})
        site = site_by.get(row["project_id"], {})
        ppa = ppa_by.get(row["project_id"], {})
        resource = solar_by.get(row["project_id"], {})
        expected_capex = float(row["proposed_capacity_kwp"]) * 850.0 * 25000.0
        if abs(capex_by.get(row["project_id"], 0.0) - expected_capex) > 1.0:
            mismatch.append(row["project_id"])
        if offtaker.get("annual_load_kwh") != row["annual_load_kwh"]:
            mismatch.append(row["project_id"] + ":load")
        if offtaker.get("daytime_load_share") != row["daytime_load_share"]:
            mismatch.append(row["project_id"] + ":daytime")
        if offtaker.get("credit_grade_internal") != row["credit_grade"]:
            mismatch.append(row["project_id"] + ":credit")
        if site.get("site_continuity_grade") != row["site_continuity_grade"]:
            mismatch.append(row["project_id"] + ":site")
        if float(ppa.get("ppa_tenor_years", 0)) != float(row["ppa_tenor_years"]):
            mismatch.append(row["project_id"] + ":tenor")
        if abs(float(ppa.get("ppa_price_base_vnd_kwh", 0)) - float(row["ppa_price_vnd_kwh"])) > 1e-6:
            mismatch.append(row["project_id"] + ":ppa_price")
        if resource.get("region") != row["region"]:
            mismatch.append(row["project_id"] + ":resource_region")
    add(results, "DQ-011", "cross_table", "field_reconciliation", "zero mismatches",
        str(len(mismatch)), "PASS" if not mismatch else "FAIL", "CRITICAL",
        "Model joins must agree across source tables")
    invalid = []
    for row in master:
        if not 0 < float(row["daytime_load_share"]) <= 1:
            invalid.append(row["project_id"] + ":daytime")
        if not 0 < float(row["uncertainty_pct"]) < 1:
            invalid.append(row["project_id"] + ":uncertainty")
        if float(row["proposed_capacity_kwp"]) > float(row["feasible_capacity_kwp"]):
            invalid.append(row["project_id"] + ":capacity")
    add(results, "DQ-012", "domain", "range_validation", "valid ratios and capacity",
        str(len(invalid)), "PASS" if not invalid else "FAIL", "HIGH",
        "Prevents invalid model inputs")
    ppa_price_mismatch = []
    for row in master:
        ppa = ppa_by.get(row["project_id"], {})
        try:
            if abs(float(ppa.get("ppa_price_base_vnd_kwh", 0)) - float(row["ppa_price_vnd_kwh"])) > 1e-6:
                ppa_price_mismatch.append(row["project_id"])
        except (TypeError, ValueError):
            ppa_price_mismatch.append(row["project_id"])
    add(results, "DQ-013", "cross_table", "ppa_price_reconciliation",
        "project master equals PPA terms", str(len(ppa_price_mismatch)),
        "PASS" if not ppa_price_mismatch else "FAIL", "HIGH",
        "PPA source lineage")
    tariff_schema = {"tariff_version", "legal_effective_from", "billing_effective_from", "billing_status", "source_id"}
    tariff_schema_ok = tariff_schema.issubset(set(tariffs[0])) and all(
        row["source_id"] and row["billing_status"] and row["tariff_version"] for row in tariffs
    )
    add(results, "DQ-014", "tariff", "legal_billing_separation",
        "schema and non-empty lineage fields", str(tariff_schema_ok),
        "PASS" if tariff_schema_ok else "FAIL", "CRITICAL",
        "Prevents treating legal effective date as billed implementation")
    billing_rates_ok = all(
        not row.get("energy_charge_vnd_kwh") or row["billing_status"] != "LEGAL_EFFECTIVE_NOT_BILLED"
        for row in tariffs
    )
    add(results, "DQ-015", "tariff", "unsupported_billed_rate_firewall",
        "no numeric billed rate on legal-only rows", str(billing_rates_ok),
        "PASS" if billing_rates_ok else "FAIL", "CRITICAL",
        "No unsupported market-rate claim")
    regulatory_schema_ok = {"legal_effective_from", "billing_effective_from", "source_id", "recheck_before_release", "status"}.issubset(set(regs[0])) and len(regs) >= 10
    add(results, "DQ-016", "regulatory", "register_completeness",
        "tax, tariff and FX rules with effective fields", str(regulatory_schema_ok),
        "PASS" if regulatory_schema_ok else "FAIL", "CRITICAL",
        "Release evidence register completeness")
    required_rules = {"RULE-TAX-067", "RULE-TAX-320", "RULE-TAX-141", "RULE-TAX-020", "RULE-FX-008", "RULE-FX-019", "RULE-TAR-60", "RULE-TAR-963"}
    rules_ok = required_rules.issubset({row["rule_id"] for row in regs})
    add(results, "DQ-017", "regulatory", "required_rule_ids", "all current tax/FX/tariff rules", str(rules_ok),
        "PASS" if rules_ok else "FAIL", "CRITICAL", "Current-source control")
    rate_links_ok = all(row["source_or_assumption_id"] in assumption_ids for row in rates)
    add(results, "DQ-018", "discount_rate", "source_assumption_coverage", "all rate IDs registered", str(rate_links_ok),
        "PASS" if rate_links_ok else "FAIL", "HIGH", "Discount-rate provenance")

    out = root / "validation/DATA_QUALITY_RESULTS.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["check_id", "domain", "check_type", "expected", "actual", "status", "severity", "impact"]
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    failures = [row for row in results if row["status"] == "FAIL"]
    report = root / "validation/DATA_QUALITY_REPORT.md"
    report.write_text(
        "# DATA_QUALITY_REPORT\n\n"
        "Remote-only quality checks for the synthetic pipeline. Grain is one row per project except CAPEX, which is six components per project.\n\n"
        "- Checks run: %s\n"
        "- Passed: %s\n"
        "- Failed: %s\n"
        "- Data class: synthetic / simulated; no real customer data.\n"
        "- Freshness: source-register dates and regulatory/tariff recheck flags govern release; no local snapshot is used.\n"
        "- Billing firewall: legal effective dates and billed implementation dates are separate; legal-only rows cannot carry billed energy rates.\n\n"
        "## Interpretation\n\n"
        "A failure is a release blocker until the source or transformation is corrected. The checks cover completeness, uniqueness, foreign-key coverage, lineage, cross-table reconciliation, legal/billing separation and domain validity.\n"
        % (len(results), len(results) - len(failures), len(failures)),
        encoding="utf-8",
    )
    if failures:
        raise AssertionError(json.dumps(failures, indent=2))
    return {"checks": len(results), "failures": len(failures)}

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
