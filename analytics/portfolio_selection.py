"""Hard-gated, budgeted and concentration-aware portfolio selection."""
from __future__ import annotations


def _eligible(project):
    return bool(project.get("shortlist_flag")) and float(project.get("equity_required_vnd", 0.0)) > 0.0


def _within_constraints(projects, equity_budget, max_parent, max_industry, max_region):
    if sum(float(project.get("equity_required_vnd", 0.0)) for project in projects) > float(equity_budget) + 1e-6:
        return False
    parents = {}
    industries = {}
    regions = {}
    for project in projects:
        parent = project.get("parent_group_id", "")
        industry = project.get("industry", "")
        region = project.get("region", "")
        parents[parent] = parents.get(parent, 0) + 1
        industries[industry] = industries.get(industry, 0) + 1
        regions[region] = regions.get(region, 0) + 1
    return all(value <= max_parent for value in parents.values()) and all(value <= max_industry for value in industries.values()) and all(value <= max_region for value in regions.values())


def select_by_value_density(projects, equity_budget, max_parent=2, max_industry=4, max_region=8):
    ordered = sorted(
        [project for project in projects if _eligible(project)],
        key=lambda project: (
            float(project.get("equity_npv_vnd", 0.0)) / float(project.get("equity_required_vnd", 1.0)),
            float(project.get("equity_npv_vnd", 0.0)),
        ),
        reverse=True,
    )
    selected = []
    for project in ordered:
        candidate = selected + [project]
        if _within_constraints(candidate, equity_budget, max_parent, max_industry, max_region):
            selected.append(project)
    return selected, sum(float(project["equity_required_vnd"]) for project in selected)


def improve_by_pairwise_swaps(projects, selected, equity_budget, max_parent=2, max_industry=4, max_region=8, max_iterations=20):
    """Improve total equity NPV through transparent one-for-one swaps."""
    selected = list(selected)
    swaps = []
    for _ in range(max_iterations):
        selected_ids = {project["project_id"] for project in selected}
        unselected = [project for project in projects if _eligible(project) and project["project_id"] not in selected_ids]
        current_value = sum(float(project.get("equity_npv_vnd", 0.0)) for project in selected)
        best = None
        for outgoing in selected:
            for incoming in unselected:
                candidate = [project for project in selected if project["project_id"] != outgoing["project_id"]] + [incoming]
                value = sum(float(project.get("equity_npv_vnd", 0.0)) for project in candidate)
                if value <= current_value + 1e-6 or not _within_constraints(candidate, equity_budget, max_parent, max_industry, max_region):
                    continue
                if best is None or value > best[0]:
                    best = (value, outgoing, incoming, candidate)
        if best is None:
            break
        _, outgoing, incoming, selected = best
        swaps.append({"outgoing_project_id": outgoing["project_id"], "incoming_project_id": incoming["project_id"]})
    return selected, sum(float(project["equity_required_vnd"]) for project in selected), swaps