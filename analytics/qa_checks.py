"""Reusable invariants and scenario-isolation checks."""

from __future__ import annotations


def assert_project_invariants(projects):
    assert len(projects) == 20, "pipeline must contain 20 projects"
    for project in projects:
        assert project["p90_y1_kwh"] <= project["p50_y1_kwh"] + 1e-6, project["project_id"]
        assert project["proposed_capacity_kwp"] <= project["feasible_capacity_kwp"], project["project_id"]
        ratio = float(project["self_consumption_ratio"])
        assert -1e-9 <= ratio <= 1.0 + 1e-9, "%s ratio=%r self=%r p50=%r" % (
            project["project_id"], ratio, project.get("self_consumption_kwh"), project.get("p50_y1_kwh")
        )
        assert len(project.get("_hourly_profile_hash", "")) == 64, project["project_id"]
        assert len(project.get("_annual_cfads", [])) == 15, project["project_id"]
        assert len(project.get("_p90_annual_cfads", [])) == 15, project["project_id"]
        assert project.get("billing_status") == "WATCH", project["project_id"]
    return True


def scenario_isolation(base, scenario):
    return {key for key in scenario if scenario[key] != base.get(key)}


def assert_sources_uses(rows, tolerance=1.0):
    return all(abs(float(row["sources_uses_balance_vnd"])) <= tolerance for row in rows)


def assert_debt_closes(schedule, tolerance=1.0):
    return not schedule or abs(float(schedule[-1]["closing"])) <= tolerance


def assert_monotonic_nonincreasing(base_values, downside_values, tolerance=1e-9):
    return all(float(downside) <= float(base) + tolerance for base, downside in zip(base_values, downside_values))


def assert_monotonic_non_decreasing(base_values, stressed_values, tolerance=1e-9):
    return all(float(stressed) >= float(base) - tolerance for base, stressed in zip(base_values, stressed_values))
