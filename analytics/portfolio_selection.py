def select_by_value_density(projects, equity_budget, max_parent=2):
    eligible=[p for p in projects if p['shortlist_flag']]
    ordered=sorted(eligible,key=lambda p:p['equity_npv_vnd']/p['equity_required_vnd'],reverse=True)
    selected=[]; used=0.0
    for p in ordered:
        if sum(x['parent_group_id']==p['parent_group_id'] for x in selected)>=max_parent: continue
        if used+p['equity_required_vnd']<=equity_budget:
            selected.append(p); used+=p['equity_required_vnd']
    return selected, used
