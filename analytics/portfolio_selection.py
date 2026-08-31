"""Hard-gated, budgeted and concentration-aware portfolio selection."""

from __future__ import annotations


def select_by_value_density(
    projects,
    equity_budget,
    max_parent=2,
    max_industry=4,
    max_region=8,
):
    eligible = [
        project
        for project in projects
        if bool(project.get("shortlist_flag"))
        and float(project.get("equity_required_vnd", 0.0)) > 0.0
    ]
    ordered = sorted(
        eligible,
        key=lambda project: (
            float(project.get("equity_npv_vnd", 0.0))
            / float(project.get("equity_required_vnd", 1.0)),
            float(project.get("equity_npv_vnd", 0.0)),
        ),
        reverse=True,
    )
    selected = []
    used = 0.0
    parents = {}
    industries = {}
    regions = {}
    for project in ordered:
        parent = project.get("parent_group_id", "")
        industry = project.get("industry", "")
        region = project.get("region", "")
        if parents.get(parent, 0) >= max_parent:
            continue
        if industries.get(industry, 0) >= max_industry:
            continue
        if regions.get(region, 0) >= max_region:
            continue
        if used + float(project["equity_required_vnd"]) > equity_budget:
            continue
        selected.append(project)
        used += float(project["equity_required_vnd"])
        parents[parent] = parents.get(parent, 0) + 1
        industries[industry] = industries.get(industry, 0) + 1
        regions[region] = regions.get(region, 0) + 1
    return selected, used
