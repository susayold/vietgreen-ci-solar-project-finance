"""Cross-surface arithmetic, provenance and missing-value checks (no plan-number fixtures)."""
import json
import math
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'public/data'


def load(name):
    return json.loads((DATA / (name + '.json')).read_text(encoding='utf-8'))


def close(a, b):
    assert math.isclose(a, b, rel_tol=1e-6, abs_tol=1e-4), (a, b)


summary = load('summary')
assert summary['candidateHistory'] == summary['candidateProjects']
assert summary['rawObservations'] == summary['observations']
assert summary['selectedProjects'] == summary['selectedRecords']
assert summary['economicsReadyRecords'] == summary['economicsReadyProjects']
assert summary['technicalBlockedRecords'] == summary['technicalBlockedProjects']

projects = load('projects')['projects']
physical = load('physical')
band = physical['screeningBand']
assert len(projects) == 20
expected_low = {
    'EU-GY-STELLANTIS-CAEN',
    'EU-GY-STELLANTIS-CHARLEVILLE',
    'EU-GY-STELLANTIS-VALENCIENNES',
    'EU-GY-STELLANTIS-SLOVAKIA',
}
actual_low = set()
actual_block = set()
project_by_id = {}
for p in projects:
    project_by_id[p['project_id']] = p
    capacity = float(p['capacityMw'])
    generation = float(p['observedGenerationGwh'])
    specific_yield = generation * 1000 / capacity
    close(specific_yield, float(p['specificYieldKwhKwp']))
    if specific_yield > band['extremeUpperKwhKwp']:
        expected = 'EXTREME_OUTLIER_BLOCK_BASE'
    elif specific_yield < band['minKwhKwp'] or specific_yield > band['maxKwhKwp']:
        expected = 'LOW_YIELD_REVIEW'
    else:
        expected = 'PASS_WITHIN_SCREENING_BAND'
    assert p['physicalStatus'] == expected, (p['project_id'], specific_yield, p['physicalStatus'], expected)
    if expected == 'LOW_YIELD_REVIEW':
        actual_low.add(p['project_id'])
    if expected == 'EXTREME_OUTLIER_BLOCK_BASE':
        actual_block.add(p['project_id'])
assert actual_low == expected_low, (actual_low, expected_low)
assert actual_block == {'IN-FPEL-ARISUDHANA'}
assert physical['distribution'] == {
    'PASS_WITHIN_SCREENING_BAND': 15,
    'LOW_YIELD_REVIEW': 4,
    'EXTREME_OUTLIER_BLOCK_BASE': 1,
}

econ = {r['projectId']: r for r in load('economics')['rows']}
debt = {r['projectId']: r for r in load('debt')['rows']}
assert len(econ) == len(debt) == 19 and econ.keys() == debt.keys()
assert len(load('source-audit')['outputHashes']) == 15
for pid, d in debt.items():
    assert d['debtCapacityUsd'] >= 0
    e = econ[pid]
    close(d['capexUsd'], e['capexUsd'])
    close(d['debtCapacityUsd'] + d['equityRequirementUsd'], d['capexUsd'])
    close(d['schedule'][0]['openingDebt'] / d['fxVndPerUsd'], d['debtCapacityUsd'])
    ratios = []
    for i, s in enumerate(d['schedule']):
        close(s['openingDebt'] - s['principal'], s['closingDebt'])
        close(s['principal'] + s['interest'], s['debtService'])
        if i:
            close(d['schedule'][i - 1]['closingDebt'], s['openingDebt'])
        if s['debtService'] > 0:
            close(s['cfads'] / s['debtService'], s['dscr'])
            ratios.append(s['dscr'])
        else:
            assert s['dscr'] is None
    close(d['schedule'][-1]['closingDebt'], 0)
    if ratios:
        close(d['minimumDscr'], min(ratios))
    else:
        assert d['minimumDscr'] is None
    y = e['year1']
    close(y['revenue'] - y['opex'] - y['tax'], y['cfads'])
    close(y['cfads'], d['schedule'][0]['cfads'])
    assert e['projectIrr'] != -.99 and e['equityIrr'] != -.99
    if d['debtCapacityUsd'] > 0:
        assert d['minimumDscr'] >= d['dscrTarget'] - 1e-6
        assert d['llcr'] >= d['llcrMin'] - 1e-6 and d['plcr'] >= d['plcrMin'] - 1e-6

risk = load('risk')['rows']
assert len(risk) == len({(r['projectId'], r['scenarioId']) for r in risk}) == 171
risk_by_project = {}
for r in risk:
    assert r['sourceStatus'] == 'MODEL_OUTPUT' and r['sourceFile'].endswith('scenarios.csv')
    risk_by_project.setdefault(r['projectId'], {})[r['scenarioId']] = r
    if r['scenarioId'] == 'BASE':
        d = debt[r['projectId']]
        close(max(0, r['openingDebtUsd']), d['debtCapacityUsd'])
        if d['minimumDscr'] is not None:
            close(r['minimumDscr'], d['minimumDscr'])

for r in load('energy')['projects']:
    close(r['p50Gwh'], r['selfConsumedGwh'] + r['exportedGwh'])
    close(r['annualLoadGwh'], r['selfConsumedGwh'] + r['gridPurchaseGwh'])
    assert len(r['representativeDay']) == 24 and r['profileHours'] == 8760
    for h in r['representativeDay']:
        close(h['solarKw'], h['selfConsumedKw'] + h['exportKw'])
        close(h['loadKw'], h['selfConsumedKw'] + h['gridPurchaseKw'])

diligence = load('diligence')
assert len(diligence['rows']) == 19
assert len(diligence['technicalValidationTrack']) == 1
assert diligence['technicalValidationTrack'][0]['projectId'] == 'IN-FPEL-ARISUDHANA'
assert 'ENGINEERING_VALIDATION' in diligence['technicalValidationTrack'][0]['nextActions']
for row in diligence['rows']:
    pid = row['projectId']
    assert row['physicalStatus'] == project_by_id[pid]['physicalStatus']
    assert row['economicsStatus'] == 'READY_FOR_ECONOMICS'
    assert row['evidenceStatus'] == 'OPEN'
    assert row['capitalAllocatedUsd'] == 0
    assert row['nextActions'] and row['nextActions'][-1] == 'TRANSACTION_EVIDENCE'
    if row['physicalStatus'] == 'LOW_YIELD_REVIEW':
        assert 'ENGINEERING_VALIDATION' in row['nextActions']
    if row['commercialStatus'] == 'EMPTY_NEGOTIATION_ZONE':
        assert 'PPA_RESTRUCTURING' in row['nextActions']
    nonpayment = risk_by_project[pid]['OFFTAKER_NONPAYMENT']['minimumDscr']
    if nonpayment is not None and nonpayment < 1.0:
        assert row['riskStatus'] == 'COUNTERPARTY_COVERAGE_BREACH'
        assert 'COUNTERPARTY_DILIGENCE' in row['nextActions']
    capex = risk_by_project[pid]['CAPEX_OVERRUN']
    if capex['incrementalCapexUsd'] > 0:
        assert 'SPONSOR_SUPPORT_REVIEW' in row['nextActions']

print('PASS: canonical/compat summary, exact physical QA IDs, 19 projects, 285 debt years, 171 scenarios, 19+1 diligence records and 456 hourly chart points reconcile.')
