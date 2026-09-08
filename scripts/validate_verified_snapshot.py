"""Cross-surface arithmetic, provenance and missing-value checks (no plan-number fixtures)."""
import json
import math
from pathlib import Path
DATA = Path(__file__).resolve().parents[1] / 'public/data'
def load(n):
    return json.loads((DATA / (n+'.json')).read_text(encoding='utf-8'))
def close(a,b):
    assert math.isclose(a,b,rel_tol=1e-6,abs_tol=1e-4), (a,b)
econ = {r['projectId']:r for r in load('economics')['rows']}
debt = {r['projectId']:r for r in load('debt')['rows']}
assert len(econ) == len(debt) == 19 and econ.keys() == debt.keys()
assert len(load('source-audit')['outputHashes']) == 15
for pid, d in debt.items():
    assert d['debtCapacityUsd'] >= 0
    e = econ[pid]
    close(d['capexUsd'],e['capexUsd'])
    close(d['debtCapacityUsd']+d['equityRequirementUsd'],d['capexUsd'])
    close(d['schedule'][0]['openingDebt']/d['fxVndPerUsd'], d['debtCapacityUsd'])
    ratios = []
    for i,s in enumerate(d['schedule']):
        close(s['openingDebt']-s['principal'],s['closingDebt'])
        close(s['principal']+s['interest'],s['debtService'])
        if i: close(d['schedule'][i-1]['closingDebt'],s['openingDebt'])
        if s['debtService'] > 0:
            close(s['cfads']/s['debtService'],s['dscr'])
            ratios.append(s['dscr'])
        else: assert s['dscr'] is None
    close(d['schedule'][-1]['closingDebt'], 0)
    if ratios: close(d['minimumDscr'],min(ratios))
    else: assert d['minimumDscr'] is None
    y = e['year1']
    close(y['revenue']-y['opex']-y['tax'],y['cfads'])
    close(y['cfads'],d['schedule'][0]['cfads'])
    assert e['projectIrr'] != -.99 and e['equityIrr'] != -.99
    if d['debtCapacityUsd'] > 0:
        assert d['minimumDscr'] >= d['dscrTarget']-1e-6
        assert d['llcr'] >= d['llcrMin']-1e-6 and d['plcr'] >= d['plcrMin']-1e-6
risk = load('risk')['rows']
assert len(risk) == len({(r['projectId'],r['scenarioId']) for r in risk}) == 171
for r in risk:
    assert r['sourceStatus'] == 'MODEL_OUTPUT' and r['sourceFile'].endswith('scenarios.csv')
    if r['scenarioId'] == 'BASE':
        d = debt[r['projectId']]
        close(max(0,r['openingDebtUsd']),d['debtCapacityUsd'])
        if d['minimumDscr'] is not None: close(r['minimumDscr'],d['minimumDscr'])
for r in load('energy')['projects']:
    close(r['p50Gwh'],r['selfConsumedGwh']+r['exportedGwh'])
    close(r['annualLoadGwh'],r['selfConsumedGwh']+r['gridPurchaseGwh'])
    assert len(r['representativeDay']) == 24 and r['profileHours'] == 8760
    for h in r['representativeDay']:
        close(h['solarKw'],h['selfConsumedKw']+h['exportKw'])
        close(h['loadKw'],h['selfConsumedKw']+h['gridPurchaseKw'])
print('PASS: 19 projects, 285 debt years, 171 scenarios, 456 hourly chart points; currency, cash flow, energy and base-case reconciliation.')
