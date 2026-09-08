"""Presentation adapter only: verify frozen artifact hashes before importing outputs.

Usage: python scripts/import_verified_release.py <extracted CI artifact>
Never runs or changes the model. Negative capacity and IRR sentinel remain disclosed.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'public/data'
SOURCE = Path(sys.argv[1])
SHA = 'ff69e15d211ff1abc88200574242ed2f1db49074'
REVISED = '--revision' in sys.argv
manifest = json.loads((SOURCE / 'release/V5_1_3_RUNTIME_RELEASE_MANIFEST.json').read_text())
if REVISED:
    assert manifest['revision'] == '2026-09-08-r1'
    SHA = manifest['source_sha']
else:
    assert manifest['source_sha'] == SHA
for path, expected in manifest['output_hashes'].items():
    assert hashlib.sha256((SOURCE / path).read_bytes()).hexdigest() == expected, path

def read(name):
    return list(csv.DictReader((SOURCE / f'outputs/v5_1_3_{name}.csv').open(encoding='utf-8-sig')))
def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))
def save(name, obj):
    (DATA / f'{name}.json').write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
def num(row, key):
    return float(row[key]) if row.get(key) not in ('', None) else None
def yes(row, key):
    return row.get(key, '').upper() == 'TRUE'
def pack(rows):
    return dict(version='2026-09-08-r1' if REVISED else '5.1.3', sourceSha=SHA, sourceArtifactId=None if REVISED else 9846347737, rows=rows)

econ = read('project_economics')
assert len(econ) == 19 and len({r['project_id'] for r in econ}) == 19
inputs = {r['project_id']: r for r in read('model_input_view')}
cash = {(r['project_id'], int(r['year'])): r for r in read('cash_flow')}
schedule = defaultdict(list)
for r in read('debt_schedule'):
    schedule[r['project_id']].append(r)
by_id = {r['project_id']: r for r in econ}
vnd_fx = num(by_id['VN-GY-GOMALL'], 'fx_local_per_usd')
debts, economics = [], []
for r in econ:
    pid = r['project_id']
    fx = num(r, 'fx_local_per_usd')
    convert = vnd_fx / fx
    identity = dict(projectId=pid, projectName=r['project_name'], country=r['country'])
    raw_debt = num(r, 'debt_capacity_usd')
    debt = max(0, raw_debt)
    capex = num(r, 'capex_usd')
    rows = []
    for s in schedule[pid]:
        year = int(s['year'])
        rows.append(dict(year=year, **{key: num(s, field)*convert for key, field in
            [('openingDebt','opening'),('principal','principal'),('interest','interest'),('debtService','debt_service'),('closingDebt','closing')]},
            cfads=num(cash[(pid, year)], 'cfads_local')*convert, dscr=num(s, 'dscr')))
    ratios = [s['dscr'] for s in rows if s['dscr'] is not None]
    debts.append(dict(**identity, capexUsd=capex, debtCapacityUsd=debt,
        rawDebtCapacityUsd=raw_debt, sourceIssue='NEGATIVE_MODEL_CAPACITY' if raw_debt < 0 else None,
        equityRequirementUsd=capex-debt, leverage=debt/capex, bindingConstraint=r['binding_debt_constraint'],
        debtRate=num(inputs[pid],'debt_rate')/100, debtTenorYears=int(inputs[pid]['debt_tenor_years']),
        dscrTarget=1.35, llcrMin=1.3, plcrMin=1.2, maxLeverage=.7,
        minimumDscr=min(ratios) if ratios else None,
        rawMinimumDscr=num(r,'dscr_min'), llcr=num(r,'llcr_loan_life') if debt else None,
        plcr=num(r,'plcr_project_life') if debt else None, schedule=rows,
        displayCurrency='VND', originalCurrency=r['currency'], fxLocalPerUsd=fx, fxVndPerUsd=vnd_fx))
    tariffs = {key: (num(r, field)*convert if num(r, field) is not None else None) for key,field in [
        ('customerCeilingVndKwh','customer_ceiling_local_per_kwh'),('sponsorFloorVndKwh','sponsor_floor_local_per_kwh'),
        ('lenderFloorVndKwh','lender_floor_local_per_kwh'),('negotiationLowerVndKwh','negotiation_lower_local_per_kwh'),
        ('negotiationUpperVndKwh','negotiation_upper_local_per_kwh')]}
    year1 = {key:num(cash[(pid,1)], field)*convert for key,field in [('revenue','gross_revenue_local'),('opex','opex_local'),('tax','tax_local'),('cfads','cfads_local')]}
    year1['debtService'] = rows[0]['debtService']
    year1['equityCashFlow'] = year1['cfads']-year1['debtService']
    economics.append(dict(**identity, **tariffs, referenceCase=r['reference_case'], ppaMode=r['ppa_mode'],
        negotiationGapVndKwh=(tariffs['negotiationLowerVndKwh']-tariffs['negotiationUpperVndKwh']) if tariffs['sponsorFloorVndKwh'] is not None else None,
        ppaStatus=r['negotiation_status'], capexUsd=capex, capexLocal=num(r,'capex_local'),
        projectNpvUsd=num(r,'project_npv_usd_at_reference'), equityNpvUsd=num(r,'equity_npv_usd_at_reference'),
        projectIrr=None if num(r,'project_irr_at_reference') == -.99 else num(r,'project_irr_at_reference'),
        equityIrr=None if num(r,'equity_irr_at_reference') == -.99 else num(r,'equity_irr_at_reference'),
        irrStatus='MODEL_SENTINEL_NO_VIABLE_IRR' if num(r,'project_irr_at_reference') == -.99 else 'MODEL_OUTPUT',
        year1=year1, decision=r['decision'], dataStatus='MODEL_OUTPUT', displayCurrency='VND',
        originalCurrency=r['currency'], fxLocalPerUsd=fx, fxVndPerUsd=vnd_fx))
save('debt', pack(debts))
save('economics', pack(economics))
risk = load('risk')
risk['rows'] = []
for r in read('scenarios'):
    fx = num(by_id[r['project_id']], 'fx_local_per_usd')
    risk['rows'].append(dict(projectId=r['project_id'], scenarioId=r['scenario_id'], debtMode=r['debt_mode'],
        minimumDscr=num(r,'min_dscr'), llcr=num(r,'llcr'), plcr=num(r,'plcr'),
        openingDebtUsd=num(r,'scenario_debt_local')/fx, additionalDebtUsd=num(r,'additional_debt_local')/fx,
        incrementalCapexUsd=num(r,'incremental_capex_local')/fx,
        principalPreserved=yes(r,'principal_schedule_preserved'), interestRepriced=yes(r,'interest_repricing_policy_applied'),
        sourceStatus='MODEL_OUTPUT', sourceFile='outputs/v5_1_3_scenarios.csv',
        metricStatus='NO_POSITIVE_BASE_DEBT' if num(r,'base_debt_local') <= 0 else 'MODEL_OUTPUT'))
risk['sourceArtifactId'] = 9846347737
risk['rowCount'] = len(risk['rows'])
assert risk['rowCount'] == 171
save('risk', risk)

hourly = defaultdict(list)
for r in read('8760'):
    if len(hourly[r['project_id']]) < 24:
        hourly[r['project_id']].append(dict(hour=len(hourly[r['project_id']]), loadKw=num(r,'load_kwh'),
            solarKw=num(r,'solar_kwh'), selfConsumedKw=num(r,'self_consumed_kwh'), exportKw=num(r,'export_kwh'),
            gridPurchaseKw=num(r,'load_kwh')-num(r,'self_consumed_kwh')))
energy = load('energy')
for e in energy['projects']:
    r = by_id[e['projectId']]
    for key, field in [('p50Gwh','generation_p50_kwh_modeled'),('p90Gwh','generation_p90_kwh'),('p99Gwh','generation_p99_kwh'),
                       ('annualLoadGwh','annual_load_kwh_modeled'),('selfConsumedGwh','self_consumed_kwh_p50'),('exportedGwh','export_kwh_p50')]:
        e[key] = num(r,field)/1e6
    e.update(gridPurchaseGwh=e['annualLoadGwh']-e['selfConsumedGwh'], selfConsumptionShare=e['selfConsumedGwh']/e['p50Gwh'],
        solarCoverageShare=e['selfConsumedGwh']/e['annualLoadGwh'], loadEvidenceLevel=r['load_evidence_level'],
        specificYieldKwhKwp=num(r,'specific_yield_p50_kwh_kwp'), representativeDay=hourly[e['projectId']],
        profileSource='Frozen model: first 24 hours of profile year 2027; not measured telemetry', profileHours=8760)
save('energy', energy)
diligence = load('diligence')
projects = {r['project_id']: r for r in load('projects')['projects']}
for r in diligence['rows']:
    p = projects[r['projectId']]
    d = next(d for d in debts if d['projectId'] == r['projectId'])
    r['physicalStatus'] = p['physicalStatus']
    r['creditStatus'] = 'MODEL_REVIEW' if d['debtCapacityUsd'] <= 0 else 'MODEL_OK'
    r['commercialStatus'] = by_id[r['projectId']]['negotiation_status']
save('diligence', diligence)
save('source-audit', dict(modelSha=SHA, artifactId=9846347737, outputHashes=manifest['output_hashes'],
    findings=[
        'Latest remediation-plan financial targets do not match the authoritative frozen CI artifact. Website uses the artifact, not unverified plan targets.',
        'Negative raw model debt capacities are retained as source issues; usable debt is floored at zero and coverage is N/A where no debt service exists.',
        'The model IRR sentinel -0.99 is not displayed as a genuine -99% return.',
        'The frozen GO Mall schedule repays in year 1; later-year CFADS remains present. No replacement amortization was invented.',
        'Model reconciliation does not establish accuracy of underlying commercial assumptions or transaction readiness.'
    ]))
print('Verified artifact hashes; imported 19 economics, 19 debt, 171 scenario and 19 energy records.')
