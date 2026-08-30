def assert_project_invariants(projects):
    assert len(projects)==20, 'pipeline must contain 20 projects'
    for p in projects:
        assert p['p90_y1_kwh'] <= p['p50_y1_kwh'] + 1e-6
        assert p['proposed_capacity_kwp'] <= p['feasible_capacity_kwp']
        assert p['self_consumption_ratio'] >= 0 and p['self_consumption_ratio'] <= 1
    return True

def scenario_isolation(base, scenario):
    changed=set(k for k in scenario if scenario[k]!=base.get(k))
    return changed
