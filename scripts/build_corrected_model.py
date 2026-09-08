"""Recalculate the corrected model from hash-verified baseline inputs; publish only after checks."""
import csv
import hashlib
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model.recruiter_revision.analytics import build_v5_1_3_economics as engine

BASE_SHA = 'ff69e15d211ff1abc88200574242ed2f1db49074'
REVISION = '2026-09-08-r1'
BASE = Path(sys.argv[1]).resolve()
MODEL = ROOT / 'model/recruiter_revision'
OUT = ROOT / 'artifacts/recruiter_revision'
DATA = ROOT / 'public/data'


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def table(name, rows):
    path = OUT / f'outputs/v5_1_3_{name}.csv'
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def close(a, b):
    assert math.isclose(a, b, rel_tol=1e-8, abs_tol=1e-4), (a, b)


manifest = json.loads((BASE / 'release/V5_1_3_RUNTIME_RELEASE_MANIFEST.json').read_text())
assert manifest['source_sha'] == BASE_SHA
for path, digest in manifest['output_hashes'].items():
    assert hashlib.sha256((BASE / path).read_bytes()).hexdigest() == digest, path

# Public input CSVs are the original source, not a new benchmark or synthetic dataset.
freeze = json.loads((BASE / 'release/V5_1_3_INPUT_FREEZE_MANIFEST.json').read_text())
for path in ['data/public/project_master_real.csv', 'data/public/project_assumption_overlay.csv']:
    expected = freeze['input_sha256'][path]
    assert hashlib.sha256((MODEL / path).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == expected, path

(MODEL / 'validation').mkdir(exist_ok=True)
shutil.copyfile(BASE / 'validation/V5_1_3_PHYSICAL_QA.csv', MODEL / 'validation/V5_1_3_PHYSICAL_QA.csv')
result = engine.run(MODEL, OUT / 'working')
again = engine.run(MODEL, OUT / 'repeat')
assert result == again, 'Deterministic repeat-build mismatch'
assert len(result['economics']) == 19 and len(result['scenarios']) == 171
assert len(result['hourly']) == 19 * 8760

econ = {r['project_id']: r for r in result['economics']}
cash = {(r['project_id'], r['year']): r for r in result['cash_flow']}
debt = {}
for r in result['debt_schedule']:
    debt.setdefault(r['project_id'], []).append(r)
scenarios = {}
for r in result['scenarios']:
    scenarios.setdefault(r['project_id'], {})[r['scenario_id']] = r

checks = []


def checked(name):
    checks.append({'check': name, 'status': 'PASS'})


close(engine._rate(.5), .005)
close(engine._rate(1), .01)
checked('Percentage units: 0.5% = 0.005; 1% = 0.01')
close(engine._irr([-100, 110]), .1)
assert engine._irr([-100, -20]) == '' and engine._irr([-100, 230, -132]) == ''
checked('IRR: known root, no-return and non-conventional cash flows')
capacity, _, _ = engine.capacity_constraints([-10, -10], .08, 1.35, 1.3, 1.2, .7, 100)
assert capacity == 0
checked('Negative cash flow cannot create negative borrowing capacity')

for pid, e in econ.items():
    close(cash[pid, 2]['generation_kwh'] / cash[pid, 1]['generation_kwh'], .995)
    assert e['debt_capacity_local'] >= 0
    opening = e['debt_capacity_local']
    for r in debt[pid]:
        close(opening, r['opening'])
        close(r['opening'] - r['principal'], r['closing'])
        close(r['principal'] + r['interest'], r['debt_service'])
        if r['debt_service'] > 0:
            close(cash[pid, r['year']]['cfads_local'] / r['debt_service'], r['dscr'])
        else:
            assert r['dscr'] is None
        opening = r['closing']
    close(opening, 0)
    if e['debt_capacity_local'] > 0:
        assert e['dscr_min'] >= 1.35 - 1e-7
        assert e['llcr_loan_life'] >= 1.3 - 1e-7
        assert e['plcr_project_life'] >= 1.2 - 1e-7
    checked(pid + ': generation decay, nonnegative capacity, debt roll-forward, maturity and coverage')

for r in result['scenarios']:
    if r['debt_mode'] != 'RESIZED_DEBT':
        assert r['principal_schedule_preserved'] == 'TRUE'
        assert r['opening_schedule_preserved'] == 'TRUE'
        assert r['closing_schedule_preserved'] == 'TRUE'
        assert r['additional_debt_local'] == 0
    if r['scenario_id'] == 'OFFTAKER_TERMINATION':
        assert r['min_dscr'] == 0
        assert r['plcr'] <= econ[r['project_id']]['plcr_project_life'] + 1e-7
checked('171 scenarios: contractual preservation, no new debt and termination downside')
checked('Repeat calculation: identical outputs')

# Recompute website physical labels from source-reported capacity/generation and the
# single published screening rule. This prevents row-order/status carry-over errors.
projects = json.loads((DATA / 'projects.json').read_text(encoding='utf-8'))
physical = json.loads((DATA / 'physical.json').read_text(encoding='utf-8'))
band = physical['screeningBand']
for p in projects['projects']:
    capacity_mw = float(p.get('capacityMw') or (float(p['capacity_kwp_observed']) / 1000))
    generation_gwh = float(p.get('observedGenerationGwh') or (float(p['generation_kwh_observed']) / 1_000_000))
    specific_yield = generation_gwh * 1000 / capacity_mw if capacity_mw else 0.0
    if specific_yield > band['extremeUpperKwhKwp']:
        status = 'EXTREME_OUTLIER_BLOCK_BASE'
    elif specific_yield < band['minKwhKwp'] or specific_yield > band['maxKwhKwp']:
        status = 'LOW_YIELD_REVIEW'
    else:
        status = 'PASS_WITHIN_SCREENING_BAND'
    p['capacityMw'] = capacity_mw
    p['observedGenerationGwh'] = generation_gwh
    p['specificYieldKwhKwp'] = specific_yield
    p['physicalStatus'] = status
    p['technicalDataBlocked'] = status == 'EXTREME_OUTLIER_BLOCK_BASE'
    p['engineeringReviewRequired'] = 'FALSE' if status == 'PASS_WITHIN_SCREENING_BAND' else 'TRUE'

project_by_id = {p['project_id']: p for p in projects['projects']}
low_yield_ids = {p['project_id'] for p in projects['projects'] if p['physicalStatus'] == 'LOW_YIELD_REVIEW'}
expected_low_yield_ids = {
    'EU-GY-STELLANTIS-CAEN',
    'EU-GY-STELLANTIS-CHARLEVILLE',
    'EU-GY-STELLANTIS-VALENCIENNES',
    'EU-GY-STELLANTIS-SLOVAKIA',
}
assert low_yield_ids == expected_low_yield_ids, (low_yield_ids, expected_low_yield_ids)
blocked_ids = {p['project_id'] for p in projects['projects'] if p['physicalStatus'] == 'EXTREME_OUTLIER_BLOCK_BASE'}
assert blocked_ids == {'IN-FPEL-ARISUDHANA'}, blocked_ids
assert sum(p['physicalStatus'] == 'PASS_WITHIN_SCREENING_BAND' for p in projects['projects']) == 15
checked('Physical QA: exact 15 pass / 4 low-yield / 1 extreme project mapping')

# Rebuild Diligence from corrected physical, commercial, credit and scenario outputs.
def unique(items):
    return list(dict.fromkeys(items))


def scenario(pid, scenario_id):
    return scenarios[pid][scenario_id]


def ratio_below(row, threshold):
    value = row.get('min_dscr')
    return value is not None and float(value) < threshold


diligence_rows = []
for pid in econ:
    p = project_by_id[pid]
    e = econ[pid]
    commercial_status = e['negotiation_status']
    credit_ok = (
        e['debt_capacity_local'] > 0
        and e['dscr_min'] >= 1.35 - 1e-7
        and e['llcr_loan_life'] >= 1.3 - 1e-7
        and e['plcr_project_life'] >= 1.2 - 1e-7
    )
    credit_status = 'MODEL_OK' if credit_ok else 'MODEL_REVIEW'
    nonpayment = scenario(pid, 'OFFTAKER_NONPAYMENT')
    p90 = scenario(pid, 'P90_ENERGY')
    rate = scenario(pid, 'INTEREST_RATE_SHOCK')
    opex = scenario(pid, 'OPEX_INFLATION')
    cod = scenario(pid, 'COD_DELAY')
    termination = scenario(pid, 'OFFTAKER_TERMINATION')
    capex_overrun = scenario(pid, 'CAPEX_OVERRUN')

    if ratio_below(nonpayment, 1.0):
        risk_status = 'COUNTERPARTY_COVERAGE_BREACH'
    elif any(ratio_below(x, 1.35) for x in [p90, rate, opex]):
        risk_status = 'BELOW_STANDARDIZED_TARGET'
    else:
        risk_status = 'TESTED'

    actions = []
    if p['physicalStatus'] == 'LOW_YIELD_REVIEW':
        actions.append('ENGINEERING_VALIDATION')
    if e['sponsor_floor_local_per_kwh'] == '':
        actions.append('SPONSOR_FLOOR_EVIDENCE')
    if commercial_status == 'EMPTY_NEGOTIATION_ZONE':
        actions.append('PPA_RESTRUCTURING')
    elif commercial_status == 'INSUFFICIENT_DATA':
        actions.append('COMMERCIAL_EVIDENCE')
    elif commercial_status == 'FEASIBLE_NEGOTIATION_ZONE':
        actions.append('PPA_TERM_SHEET')
    if not credit_ok:
        actions.append('CREDIT_RESTRUCTURING')
    if ratio_below(nonpayment, 1.0):
        actions.append('COUNTERPARTY_DILIGENCE')
    if float(cod.get('min_dscr') or 0) == 0:
        actions.append('COD_TIMING_REVIEW')
    if float(capex_overrun.get('incremental_capex_local') or 0) > 0 and capex_overrun['debt_mode'] == 'NO_NEW_DEBT':
        actions.append('SPONSOR_SUPPORT_REVIEW')
    if float(termination.get('min_dscr') or 0) == 0:
        actions.append('COUNTERPARTY_DILIGENCE')
    actions.append('TRANSACTION_EVIDENCE')
    actions = unique(actions)

    if p['physicalStatus'] == 'LOW_YIELD_REVIEW' or not credit_ok or ratio_below(nonpayment, 1.0):
        priority = 'HIGH'
    elif commercial_status in {'EMPTY_NEGOTIATION_ZONE', 'INSUFFICIENT_DATA'} or float(cod.get('min_dscr') or 0) == 0:
        priority = 'MEDIUM'
    else:
        priority = 'LOW'

    diligence_rows.append({
        'projectId': pid,
        'projectName': p['project_name'],
        'country': p['country'],
        'capacityMw': p['capacityMw'],
        'physicalStatus': p['physicalStatus'],
        'economicsStatus': 'READY_FOR_ECONOMICS',
        'commercialStatus': commercial_status,
        'creditStatus': credit_status,
        'riskStatus': risk_status,
        'evidenceStatus': 'OPEN',
        'nextActions': actions,
        'diligencePriority': priority,
        'decision': 'INDETERMINATE_MISSING_COMMERCIAL_DATA',
        'capitalAllocatedUsd': 0,
    })

blocked = project_by_id['IN-FPEL-ARISUDHANA']
technical_track = [{
    'projectId': blocked['project_id'],
    'projectName': blocked['project_name'],
    'country': blocked['country'],
    'capacityMw': blocked['capacityMw'],
    'physicalStatus': 'EXTREME_OUTLIER_BLOCK_BASE',
    'economicsStatus': 'TECHNICAL_DATA_BLOCKED',
    'commercialStatus': 'NOT ASSESSED',
    'creditStatus': 'NOT ASSESSED',
    'riskStatus': 'TECHNICAL_BLOCK',
    'evidenceStatus': 'OPEN',
    'nextActions': ['ENGINEERING_VALIDATION', 'TRANSACTION_EVIDENCE'],
    'diligencePriority': 'TECHNICAL',
    'decision': 'INDETERMINATE_MISSING_COMMERCIAL_DATA',
    'capitalAllocatedUsd': 0,
}]

diligence = {
    'version': REVISION,
    'budgetUsd': 0,
    'approvedAllocationsUsd': 0,
    'rows': diligence_rows,
    'technicalValidationTrack': technical_track,
    'sourceArtifactId': None,
    'baselineInputSha': BASE_SHA,
}
assert len(diligence_rows) == 19 and len(technical_track) == 1
for row in diligence_rows:
    assert row['physicalStatus'] == project_by_id[row['projectId']]['physicalStatus']
    assert row['nextActions'] and row['nextActions'][-1] == 'TRANSACTION_EVIDENCE'
checked('Diligence: 19 + 1 split, project-level physical reconciliation and multi-factor next actions')

for name, rows in {
    'project_economics': result['economics'],
    'cash_flow': result['cash_flow'],
    'debt_schedule': result['debt_schedule'],
    'scenarios': result['scenarios'],
    'energy': result['economics'],
    'load_summary': result['economics'],
    '8760': result['hourly'],
    'debt_sizing': result['economics'],
    'coverage': result['economics'],
    'returns': result['economics'],
    'ppa_frontier': result['economics'],
    'reconciliation': checks,
}.items():
    table(name, rows)

# Input evidence and capital-allocation policy are unchanged; keep their exact source records.
for name in ['model_input_view', 'portfolio_control']:
    shutil.copyfile(BASE / f'outputs/v5_1_3_{name}.csv', OUT / f'outputs/v5_1_3_{name}.csv')
table('diligence_shortlist', diligence['rows'])

files = sorted((MODEL / 'analytics').glob('*.py')) + sorted((MODEL / 'data/public').glob('*.csv')) + [Path(__file__)]
source_hashes = {
    str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
    for p in files
}
model_digest = hashlib.sha256(json.dumps(source_hashes, sort_keys=True).encode()).hexdigest()
output_hashes = {
    str(p.relative_to(OUT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted((OUT / 'outputs').glob('*.csv'))
}
assert len(output_hashes) == 15
revision = dict(
    revision=REVISION,
    source_sha=model_digest,
    baselineInputSha=BASE_SHA,
    source_hashes=source_hashes,
    output_hashes=output_hashes,
    checks=checks,
)
dump(OUT / 'release/V5_1_3_RUNTIME_RELEASE_MANIFEST.json', revision)
subprocess.run([sys.executable, str(ROOT / 'scripts/import_verified_release.py'), str(OUT), '--revision'], check=True)

dump(DATA / 'diligence.json', diligence)
for name in ['risk', 'energy', 'economics', 'debt', 'diligence']:
    obj = json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))
    obj.update(version=REVISION, sourceSha=model_digest, sourceArtifactId=None, baselineInputSha=BASE_SHA)
    dump(DATA / f'{name}.json', obj)


def payback(values):
    balance = values[0]
    for year, value in enumerate(values[1:], 1):
        if balance < 0 and balance + value >= 0:
            return year - 1 + (-balance / value)
        balance += value
    return None


overlays = engine._assumptions(engine._read_csv(MODEL / 'data/public/project_assumption_overlay.csv'))
for pid, a in overlays.items():
    for key in [
        'tax_rate', 'debt_all_in_rate', 'opex_percent_of_capex', 'project_discount_rate',
        'equity_hurdle_rate', 'customer_discount_rate', 'llcr_discount_rate',
        'plcr_discount_rate', 'inflation_rate', 'degradation'
    ]:
        if key in a:
            assert a[key]['unit'].startswith('percent'), (pid, key, a[key]['unit'])

economic_data = json.loads((DATA / 'economics.json').read_text(encoding='utf-8'))
for r in economic_data['rows']:
    pid = r['projectId']
    e = econ[pid]
    a = overlays[pid]
    cf = [c['cfads_local'] for c in result['cash_flow'] if c['project_id'] == pid]
    services = [d['debt_service'] for d in debt[pid]] + [0] * max(0, len(cf) - len(debt[pid]))
    project_cf = [-e['capex_local']] + cf
    equity_cf = [-e['capex_local'] + e['debt_capacity_local']] + [c - s for c, s in zip(cf, services)]
    r.update(
        projectPaybackYears=payback(project_cf),
        equityPaybackYears=payback(equity_cf),
        projectDiscountRate=engine._rate(engine._v(a, 'project_discount_rate', 10)),
        equityHurdleRate=engine._rate(engine._v(a, 'equity_hurdle_rate', 14)),
        operatingHorizonYears=len(cf),
        ppaTenorYears=int(engine._v(a, 'ppa_tenor_years', 20)),
        equityShare=1 - e['debt_capacity_local'] / e['capex_local'],
        dscrAverage=sum(d['dscr'] for d in debt[pid] if d['dscr'] is not None) / max(1, sum(d['dscr'] is not None for d in debt[pid])),
    )
dump(DATA / 'economics.json', economic_data)

baseline_econ = {r['project_id']: r for r in engine._read_csv(BASE / 'outputs/v5_1_3_project_economics.csv')}
comparison = [
    dict(
        projectId=pid,
        previousDebtUsd=float(baseline_econ[pid]['debt_capacity_usd']),
        debtUsd=e['debt_capacity_usd'],
        previousProjectNpvUsd=float(baseline_econ[pid]['project_npv_usd_at_reference']),
        projectNpvUsd=e['project_npv_usd_at_reference'],
    )
    for pid, e in econ.items()
]
audit = dict(
    modelRevision=REVISION,
    modelDigest=model_digest,
    baselineInputSha=BASE_SHA,
    outputHashes=output_hashes,
    beforeAfter=comparison,
    corrections=[
        'Percentage-point conversion: degradation 0.5% per year, not 50%.',
        'Debt is nonnegative; coverage sizing uses documented discount rates.',
        'Sponsor tariff sensitivity preserves base contractual debt service.',
        'IRR is returned only for a bracketed conventional cash-flow root.',
        'Website physical QA is keyed to calculated project yield, preventing status carry-over between projects.',
        'Diligence priorities and next actions are regenerated from corrected physical, commercial, credit and stress outputs.',
    ],
    limitations=[
        'Reference tariff applied to all generation; not an executed PPA or export entitlement.',
        'Public inputs and analyst assumptions; no independent engineering or lender approval.',
        'Cash-sweep sculpting can repay before the maximum tenor; no maturity is forced.',
    ],
    checks=checks,
)
dump(DATA / 'source-audit.json', audit)
dump(DATA / 'model-revision.json', revision)

summary = json.loads((DATA / 'summary.json').read_text(encoding='utf-8'))
summary.update(version=REVISION, modelTag=REVISION, modelSha=model_digest, calculationChecks=len(checks))
for key in ['regressionTests', 'semanticControls', 'workbookSheets']:
    summary.pop(key, None)
# Keep canonical fields and explicit Page-2 compatibility aliases in one generated contract.
summary.update(
    candidateHistory=summary['candidateProjects'],
    rawObservations=summary['observations'],
    selectedProjects=summary['selectedRecords'],
    economicsReadyRecords=summary['economicsReadyProjects'],
    technicalBlockedRecords=summary['technicalBlockedProjects'],
)
dump(DATA / 'summary.json', summary)

release = dict(
    modelVersion=REVISION,
    modelDigest=model_digest,
    baselineInputSha=BASE_SHA,
    calculationChecks=len(checks),
    deterministicBuild='PASS',
    outputArtifacts=len(output_hashes),
)
dump(DATA / 'release.json', release)
dump(DATA / 'model.json', dict(version=REVISION, release=release, rows=economic_data['rows']))
dump(DATA / 'reconciliation.json', dict(version=REVISION, rows=checks))
dump(DATA / 'audit-trail.json', dict(version=REVISION, corrections=audit['corrections'], baselineInputSha=BASE_SHA))
dump(DATA / 'gates.json', dict(version=REVISION, gates=[
    {'label': 'Recalculation checks', 'status': 'PASS'},
    {'label': 'Third-party technical review', 'status': 'OPEN'},
    {'label': 'PPA and lender terms', 'status': 'OPEN'},
    {'label': 'Investment approval', 'status': 'NOT_GRANTED'},
]))
dump(DATA / 'sources.json', dict(version=REVISION, sources=[
    {'path': 'model/recruiter_revision/data/public/project_master_real.csv', 'purpose': 'Public project facts'},
    {'path': 'model/recruiter_revision/data/public/project_assumption_overlay.csv', 'purpose': 'Assumptions with units and source references'},
    {'path': 'model/recruiter_revision/analytics', 'purpose': 'Corrected calculation code'},
    {'path': 'scripts/build_corrected_model.py', 'purpose': 'Input verification, calculation and checks'},
    {'path': 'public/data/model-revision.json', 'purpose': 'Source and result fingerprints'},
]))

# Publish corrected project-level QA and regenerated diligence back into the website contract.
diligence_by_id = {r['projectId']: r for r in diligence['rows']}
technical_by_id = {r['projectId']: r for r in diligence['technicalValidationTrack']}
for p in projects['projects']:
    if p['project_id'] in diligence_by_id:
        p['diligence'] = diligence_by_id[p['project_id']]
    elif p['project_id'] in technical_by_id:
        p['diligence'] = technical_by_id[p['project_id']]
projects.update(version=REVISION, sourceSha=model_digest, baselineInputSha=BASE_SHA)
dump(DATA / 'projects.json', projects)

physical.update(version=REVISION, sourceSha=model_digest, baselineInputSha=BASE_SHA)
physical['distribution'] = {
    'PASS_WITHIN_SCREENING_BAND': sum(p['physicalStatus'] == 'PASS_WITHIN_SCREENING_BAND' for p in projects['projects']),
    'LOW_YIELD_REVIEW': sum(p['physicalStatus'] == 'LOW_YIELD_REVIEW' for p in projects['projects']),
    'EXTREME_OUTLIER_BLOCK_BASE': sum(p['physicalStatus'] == 'EXTREME_OUTLIER_BLOCK_BASE' for p in projects['projects']),
}
dump(DATA / 'physical.json', physical)

print(json.dumps({
    'revision': REVISION,
    'checks': len(checks),
    'GO_MALL': econ['VN-GY-GOMALL'],
    'positive_debt_projects': sum(e['debt_capacity_local'] > 0 for e in econ.values()),
    'low_yield_projects': sorted(low_yield_ids),
}, indent=2))
