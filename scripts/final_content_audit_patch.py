from pathlib import Path


def patch(path: str, old: str, new: str, count: int = 1) -> None:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    found = text.count(old)
    if found != count:
        raise SystemExit(f'{path}: expected {count} occurrence(s), found {found}: {old[:120]!r}')
    p.write_text(text.replace(old, new), encoding='utf-8')


# Page 1 — CTA must open Page 8, not an overview anchor.
patch(
    'app/page.tsx',
    '<Link className="button button-secondary" href="#model-evidence">Model &amp; Evidence</Link>',
    '<Link className="button button-secondary" href="/model-evidence">Model &amp; Evidence</Link>',
)

# Page 2 — the Energy CTA must actually navigate to Page 3.
patch(
    'app/projects/page.tsx',
    "import Image from '@/lib/site-image';\nimport { useEffect, useMemo, useState } from 'react';",
    "import Image from '@/lib/site-image';\nimport Link from '@/lib/site-link';\nimport { useEffect, useMemo, useState } from 'react';",
)
patch(
    'app/projects/page.tsx',
    '''            <a className="projects-button primary" href="#physical-qa">\n              Continue to Energy &amp; Physical Model <ArrowRight size={15} />\n            </a>''',
    '''            <Link className="projects-button primary" href="/energy">\n              Continue to Energy &amp; Physical Model <ArrowRight size={15} />\n            </Link>''',
)

# Page 3 — align wording with the actual screening model and revenue boundary.
patch(
    'app/energy/page.tsx',
    '''              We translate annual solar evidence, system design and load\n              patterns into hourly energy flows: self-consumption, export and\n              grid purchases across an entire year.''',
    '''              We translate annual solar evidence, installed capacity and modeled load\n              patterns into hourly energy flows: self-consumption, modeled surplus and\n              grid purchases across an entire year.''',
)
patch(
    'app/energy/page.tsx',
    '''                  <b>Export to Grid</b>\n                  <span>Excess solar generation exported to the grid.</span>''',
    '''                  <b>Modeled Surplus / Export</b>\n                  <span>Excess modeled solar after onsite load; grid-export entitlement is not evidenced.</span>''',
)
patch('app/energy/page.tsx', '<span className="export">Export</span>', '<span className="export">Modeled Surplus</span>')
patch(
    'app/energy/page.tsx',
    '''                  Export to Grid\n                  <b>''',
    '''                  Modeled Surplus / Export\n                  <b>''',
)
patch(
    'app/energy/page.tsx',
    '                  Capacity-weighted portfolio context',
    '                  Portfolio capacity, generation and yield context',
)
patch(
    'app/energy/page.tsx',
    '''                  Hourly energy flows → CFADS calculation\n                </li>\n                <li>\n                  <Check />\n                  P50 / P90 / P99 → scenario definitions\n                </li>\n                <li>\n                  <Check />\n                  Load coverage → PPA structuring\n                </li>\n                <li>\n                  <Check />\n                  Export profile → merchant revenue (if any)''',
    '''                  Annual P50 generation → reference-case revenue / CFADS\n                </li>\n                <li>\n                  <Check />\n                  P50 → base case; P90 screening factor → energy downside scenario\n                </li>\n                <li>\n                  <Check />\n                  Load and self-consumption → commercial diligence context\n                </li>\n                <li>\n                  <Check />\n                  Modeled surplus → unmonetized unless separate export evidence exists''',
)
patch(
    'app/energy/page.tsx',
    '''              This page proves we understand solar physics, load behavior, and\n              how to convert them into bankable energy metrics that drive\n              financial outcomes.''',
    '''              This page demonstrates a transparent screening model for solar generation,\n              load matching and finance-relevant energy metrics — without claiming\n              bankable production evidence.''',
)

# Page 4 — remove GO Mall-only text and bind status/currency to the selected project.
patch(
    'app/economics/page.tsx',
    '  ppaStatus?: string;\n};',
    '  ppaStatus?: string;\n  displayCurrency?: string;\n  originalCurrency?: string;\n  fxLocalPerUsd?: number;\n  fxVndPerUsd?: number;\n};',
)
patch(
    'app/economics/page.tsx',
    '''              <small>\n                VND 3,460/kWh is the customer-ceiling benchmark used by the\n                reference case. The exact GO Mall project PPA is not publicly\n                disclosed.\n              </small>''',
    '''              <small>\n                {reference?.customerCeilingVndKwh == null\n                  ? 'The selected project customer-ceiling benchmark is unresolved.'\n                  : `${vnd(reference.customerCeilingVndKwh)}/kWh is the selected project customer-ceiling benchmark. The exact executed PPA is not publicly disclosed.`}\n              </small>''',
)
patch(
    'app/economics/page.tsx',
    '''                Customer, sponsor and lender thresholds are model-resolved, but\n                the reference case does not establish an executable PPA.''',
    '''                Resolved model thresholds are shown above; any missing solver output remains explicitly unresolved.\n                The reference case does not establish an executable PPA.''',
)
patch(
    'app/economics/page.tsx',
    '''            {[\n              'PHYSICAL MODEL|READY',\n              'ECONOMICS|MODELED',\n              'CUSTOMER CEILING|AVAILABLE',\n              'SPONSOR FLOOR|UNRESOLVED',\n              'LENDER FLOOR|AVAILABLE',\n              'NEGOTIATION ZONE|NOT CONCLUSIVE',\n              'DECISION|INDETERMINATE',\n            ].map((item, index) => {\n              const [top, bottom] = item.split('|');''',
    '''            {([\n              ['PHYSICAL MODEL', 'READY'],\n              ['ECONOMICS', reference ? 'MODELED' : 'UNRESOLVED'],\n              ['CUSTOMER CEILING', reference?.customerCeilingVndKwh == null ? 'UNRESOLVED' : 'AVAILABLE'],\n              ['SPONSOR FLOOR', reference?.sponsorFloorVndKwh == null ? 'UNRESOLVED' : 'AVAILABLE'],\n              ['LENDER FLOOR', reference?.lenderFloorVndKwh == null ? 'UNRESOLVED' : 'AVAILABLE'],\n              ['NEGOTIATION ZONE', reference?.ppaStatus ?? 'NOT RESOLVED'],\n              ['DECISION', decision === 'INDETERMINATE_MISSING_COMMERCIAL_DATA' ? 'INDETERMINATE' : decision],\n            ] as const).map(([top, bottom], index) => {''',
)
patch(
    'app/economics/page.tsx',
    "econRows.filter((row) => row.ppaStatus === 'FEASIBLE_ZONE').length",
    "econRows.filter((row) => row.ppaStatus === 'FEASIBLE_NEGOTIATION_ZONE').length",
)
patch('app/economics/page.tsx', '<span>FEASIBLE_ZONE</span>', '<span>FEASIBLE_NEGOTIATION_ZONE</span>')
patch(
    'app/economics/page.tsx',
    '''              <span>\n                Reporting Currency <b>VND</b>\n              </span>\n              <span>\n                Base Currency in Model <b>USD</b>\n              </span>\n              <span>\n                Reference Exchange Rate <b>25,610 VND/USD</b>\n              </span>\n              <small>\n                Local tariffs are shown with currency and are not used as\n                cross-country rankings.\n              </small>''',
    '''              <span>\n                Website Display Currency <b>{reference?.displayCurrency ?? 'VND'}</b>\n              </span>\n              <span>\n                Project Input Currency <b>{reference?.originalCurrency ?? 'NOT AVAILABLE'}</b>\n              </span>\n              <span>\n                Project Local / USD <b>{reference?.fxLocalPerUsd == null ? 'NOT AVAILABLE' : reference.fxLocalPerUsd.toLocaleString('en-US', {maximumFractionDigits: 4})}</b>\n              </span>\n              <span>\n                VND / USD Display FX <b>{reference?.fxVndPerUsd == null ? 'NOT AVAILABLE' : reference.fxVndPerUsd.toLocaleString('en-US', {maximumFractionDigits: 0})}</b>\n              </span>\n              <small>\n                Tariff thresholds are displayed as VND equivalents for comparison; project-local currencies remain explicit and are not ranked across countries.\n              </small>''',
)

# Page 5 — the mini chart is a Year-1 chart and should display both values.
patch('app/debt/page.tsx', '<b>B. Principal vs Interest</b>', '<b>B. Year 1 Principal vs Interest</b>')
patch(
    'app/debt/page.tsx',
    '''                  <b>{debt?.schedule[0]?.principal == null ? 'NOT AVAILABLE' : (debt.schedule[0].principal / 1e9).toFixed(3)}</b>\n                  <small>Principal · Interest</small>''',
    '''                  <b>{debt?.schedule[0]?.principal == null ? 'NOT AVAILABLE' : `${(debt.schedule[0].principal / 1e9).toFixed(3)} · ${(debt.schedule[0].interest / 1e9).toFixed(3)}`}</b>\n                  <small>Principal · Interest (VND bn)</small>''',
)

# Page 6 — all selected-project analysis must follow the selector and avoid a fake ranking.
patch(
    'app/risk/page.tsx',
    'title="How GO Mall Coverage Responds to Downside"',
    "title={`How ${selected?.project_name ?? 'Selected Project'} Coverage Responds to Downside`}",
)
patch(
    'app/risk/page.tsx',
    '<b>GO MALL — SCENARIO DSCR</b>',
    "<b>{(selected?.project_name ?? 'Selected Project').toUpperCase()} — SCENARIO DSCR</b>",
)
patch('app/risk/page.tsx', '<h3>What breaks first?</h3>', '<h3>Key governed stress mechanisms</h3>')
patch('app/risk/page.tsx', '<b className="number red">1</b>', '<b className="number red">A</b>')
patch('app/risk/page.tsx', '<b className="number red">2</b>', '<b className="number red">B</b>')
patch('app/risk/page.tsx', '<b className="number amber">3</b>', '<b className="number amber">C</b>')
patch(
    'app/risk/page.tsx',
    '''                    Immediate coverage break: DSCR falls to 0.000x before\n                    operating CFADS begins.''',
    '''                    Selected minimum DSCR: {formatCoverage(metrics?.COD_DELAY?.dscr)}. A one-year delay can place contractual debt service before operating CFADS.''',
)
patch(
    'app/risk/page.tsx',
    '                    Multiple stresses compound while no new debt is added.',
    '                    Selected minimum DSCR: {formatCoverage(metrics?.COMBINED_DOWNSIDE?.dscr)}. Energy, CAPEX, rate and COD stresses compound while no new debt is added.',
)
patch(
    'app/risk/page.tsx',
    '                    A collection shortfall reduces cash available for debt service. Compare the selected scenario ratios with both coverage thresholds.',
    '                    Selected minimum DSCR: {formatCoverage(metrics?.OFFTAKER_NONPAYMENT?.dscr)}. A collection shortfall reduces cash available for contractual debt service.',
)
patch('app/risk/page.tsx', '<b>Verified base cases</b>', '<b>Model-supported base cases</b>')
patch('app/risk/page.tsx', '<b>Source caution</b>', '<b>No positive standardized base debt</b>')
patch(
    'app/risk/page.tsx',
    '                <Check /> Stressed DSCR / LLCR / PLCR where source-backed',
    '                <Check /> Stressed DSCR / LLCR / PLCR where model-supported',
)

# Page 7 — current statuses/actions, selected-row state, and fail-closed totals.
patch('app/diligence/page.tsx', "'Tariff Frontier: Known',", "'Tariff frontier: inspect selected project output',")
patch('app/diligence/page.tsx', '<b>decision + ppa_mode</b>', '<b>commercialStatus + PPA frontier</b>')
patch(
    'app/diligence/page.tsx',
    '''                          tone={\n                            record.riskLabel === 'CRITICAL_STRESS'\n                              ? 'red'\n                              : 'neutral'\n                          }''',
    '''                          tone={\n                            record.riskLabel === 'COUNTERPARTY_COVERAGE_BREACH'\n                              ? 'red'\n                              : record.riskLabel === 'BELOW_STANDARDIZED_TARGET'\n                                ? 'amber'\n                                : 'neutral'\n                          }''',
)
patch(
    'app/diligence/page.tsx',
    '''                          tone={\n                            record.nextAction === 'COD_TIMING_REVIEW'\n                              ? 'red'\n                              : record.nextAction === 'TRANSACTION_EVIDENCE'\n                                ? 'amber'\n                                : 'green'\n                          }''',
    '''                          tone={\n                            ['ENGINEERING_VALIDATION', 'CREDIT_RESTRUCTURING', 'COUNTERPARTY_DILIGENCE', 'COD_TIMING_REVIEW'].includes(record.nextAction)\n                              ? 'red'\n                              : ['PPA_RESTRUCTURING', 'COMMERCIAL_EVIDENCE', 'SPONSOR_SUPPORT_REVIEW', 'SPONSOR_FLOOR_EVIDENCE', 'TRANSACTION_EVIDENCE'].includes(record.nextAction)\n                                ? 'amber'\n                                : 'green'\n                          }''',
)
patch(
    'app/diligence/page.tsx',
    "record.project_id === GO_MALL ? 'selected-row' : ''",
    "record.project_id === selected?.project_id ? 'selected-row' : ''",
)
patch(
    'app/diligence/page.tsx',
    "'Could move evidence from OPEN to transaction-ready.',",
    "'Could close legal diligence gaps; transaction readiness still requires the remaining evidence package.',",
)
patch(
    'app/diligence/page.tsx',
    '''            <p>\n              PPA term sheet, sponsor floor evidence, COD timing support and\n              third-party validation are the next controlled inputs.\n            </p>''',
    '''            <p>\n              {selected.nextActions?.length\n                ? `Current controlled actions: ${selected.nextActions.map((item) => item.replaceAll('_', ' ')).join(' · ')}.`\n                : 'No controlled next-action payload is available for this project.'}\n            </p>''',
)
patch(
    'app/diligence/page.tsx',
    '''                  new Set(financeRecords.map((record) => record.country))\n                    .size || 7,''',
    '''                  new Set(financeRecords.map((record) => record.country))\n                    .size,''',
)
patch(
    'app/diligence/page.tsx',
    "value={formatNumber(selectedCapacity || 129.853, 3) + ' MW'}",
    "value={financeRecords.length ? formatNumber(selectedCapacity, 3) + ' MW' : '—'}",
)
patch(
    'app/diligence/page.tsx',
    "value={formatNumber(selectedGeneration || 148.221, 3) + ' GWh'}",
    "value={financeRecords.length ? formatNumber(selectedGeneration, 3) + ' GWh' : '—'}",
)
patch('app/diligence/page.tsx', 'total={financeRecords.length || 19}', 'total={financeRecords.length}', count=2)

# Page 8 — use canonical release counts rather than duplicate literals.
patch(
    'app/model-evidence/page.tsx',
    "import debts from '../../public/data/debt.json';",
    "import debts from '../../public/data/debt.json';\nimport summary from '../../public/data/summary.json';",
)
patch(
    'app/model-evidence/page.tsx',
    '<article><Database/><strong>19</strong><span>Modeled projects</span></article>',
    '<article><Database/><strong>{summary.economicsReadyProjects}</strong><span>Modeled projects</span></article>',
)
patch(
    'app/model-evidence/page.tsx',
    '<article><Code2/><strong>171</strong><span>Scenario results</span></article>',
    '<article><Code2/><strong>{summary.scenarios}</strong><span>Scenario results</span></article>',
)

# Release identity: projects/physical are corrected outputs, not untouched V5.1.3 snapshots.
patch(
    'scripts/build_corrected_model.py',
    '''for p in projects['projects']:\n    if p['project_id'] in diligence_by_id:\n        p['diligence'] = diligence_by_id[p['project_id']]\n    elif p['project_id'] in technical_by_id:\n        p['diligence'] = technical_by_id[p['project_id']]\ndump(DATA / 'projects.json', projects)\n\nphysical['distribution'] = {''',
    '''for p in projects['projects']:\n    if p['project_id'] in diligence_by_id:\n        p['diligence'] = diligence_by_id[p['project_id']]\n    elif p['project_id'] in technical_by_id:\n        p['diligence'] = technical_by_id[p['project_id']]\nprojects.update(version=REVISION, sourceSha=model_digest, baselineInputSha=BASE_SHA)\ndump(DATA / 'projects.json', projects)\n\nphysical.update(version=REVISION, sourceSha=model_digest, baselineInputSha=BASE_SHA)\nphysical['distribution'] = {''',
)
patch(
    'scripts/validate_verified_snapshot.py',
    '''projects = load('projects')['projects']\nphysical = load('physical')\nband = physical['screeningBand']''',
    '''projects_payload = load('projects')\nprojects = projects_payload['projects']\nphysical = load('physical')\nfor payload in (projects_payload, physical):\n    assert payload['version'] == summary['version']\n    assert payload['sourceSha'] == summary['modelSha']\n    assert payload['baselineInputSha'] == 'ff69e15d211ff1abc88200574242ed2f1db49074'\nband = physical['screeningBand']''',
)

# Browser regressions specifically target the mismatches found by this content audit.
test_path = Path('tests/v5_1_3_website_browser.spec.mjs')
test_text = test_path.read_text(encoding='utf-8')
marker = "test('final content audit is project-specific and release-aligned'"
if marker not in test_text:
    test_text += r'''

test('final content audit is project-specific and release-aligned', async ({page, request}) => {
  const summary = await (await request.get(`${base}/data/summary.json`)).json();
  const projects = await (await request.get(`${base}/data/projects.json`)).json();
  const physical = await (await request.get(`${base}/data/physical.json`)).json();
  expect(projects.version).toBe(summary.version);
  expect(projects.sourceSha).toBe(summary.modelSha);
  expect(physical.version).toBe(summary.version);
  expect(physical.sourceSha).toBe(summary.modelSha);

  await page.goto(`${base}/projects`, {waitUntil:'networkidle'});
  const energyCta = page.getByRole('link',{name:/Continue to Energy & Physical Model/});
  await expect(energyCta).toHaveAttribute('href', /\/energy$/);

  await page.goto(`${base}/energy`, {waitUntil:'networkidle'});
  await expect(page.locator('main')).not.toContainText('bankable energy metrics');
  await expect(page.locator('main')).not.toContainText('merchant revenue');
  await expect(page.locator('main')).toContainText('unmonetized unless separate export evidence exists');

  const econ = await (await request.get(`${base}/data/economics.json`)).json();
  await page.goto(`${base}/economics`, {waitUntil:'networkidle'});
  const econSelector = page.locator('#economics-project');
  await econSelector.selectOption({index:1});
  const selectedId = await econSelector.inputValue();
  const selectedRow = econ.rows.find(row => row.projectId === selectedId);
  await expect(page.locator('.tariff-warning')).not.toContainText('GO Mall project PPA');
  if (selectedRow.sponsorFloorVndKwh == null) {
    await expect(page.locator('.decision-ladder')).toContainText('UNRESOLVED');
  } else {
    await expect(page.locator('.decision-ladder')).toContainText('SPONSOR FLOOR');
    await expect(page.locator('.decision-ladder')).toContainText('AVAILABLE');
  }

  await page.goto(`${base}/risk`, {waitUntil:'networkidle'});
  const riskSelector = page.locator('#risk-project');
  await riskSelector.selectOption({index:1});
  const selectedName = await riskSelector.locator('option:checked').textContent();
  await expect(page.locator('#scenario-dscr')).toContainText(selectedName.trim());
  await expect(page.locator('#scenario-dscr')).not.toContainText('GO MALL — SCENARIO DSCR');

  await page.goto(`${base}/diligence`, {waitUntil:'networkidle'});
  await expect(page.locator('.context-kpis')).not.toContainText('NaN');
});
'''
    test_path.write_text(test_text, encoding='utf-8')
