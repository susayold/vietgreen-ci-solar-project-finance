from pathlib import Path


def patch(path: str, old: str, new: str, count: int = 1) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    found = text.count(old)
    if found != count:
        raise SystemExit(
            f"{path}: expected {count} occurrence(s), found {found}: {old[:140]!r}"
        )
    p.write_text(text.replace(old, new), encoding="utf-8")


# Page 1 — preserve the independent-audit boundary in recruiter-facing wording.
patch(
    "app/page.tsx",
    "inside one auditable analytical framework.",
    "inside one traceable analytical framework.",
)

# Page 2 — lineage is reproducible/traceable; it is not an independent audit.
patch(
    "app/projects/page.tsx",
    "Every reduction in the dataset is explicit and auditable.",
    "Every reduction in the dataset is explicit and traceable.",
)

# Page 3 — distinguish modeled surplus from an evidenced grid-export right.
patch(
    "app/energy/page.tsx",
    "Hourly self-consumption priority: Onsite → Export → Grid",
    "Hourly flow logic: onsite use first; modeled surplus and grid purchase follow from residuals",
)
patch(
    "app/energy/page.tsx",
    "Self-consumption, export, grid purchase",
    "Self-consumption, modeled surplus and grid purchase",
)
patch(
    "app/energy/page.tsx",
    "Audit-ready and reproducible",
    "Traceable and reproducible",
)

# Page 4 — a threshold can be unresolved, so do not imply a complete tariff range.
patch(
    "app/economics/page.tsx",
    "Reference tariff range and commercial constraints",
    "Resolved reference tariff thresholds and commercial constraints",
)
patch(
    "app/economics/page.tsx",
    "<h3>COMMERCIAL FEASIBILITY STATUS</h3>",
    "<h3>MODELED COMMERCIAL STATUS</h3>",
)

# Page 5 — standardized model debt must not read like an executed lender contract.
patch(
    "app/debt/page.tsx",
    "selects the binding debt capacity, then rebuilds the contractual\n              debt schedule from the cash flow the project can actually support.",
    "selects the binding debt capacity, then rebuilds a modeled debt\n              schedule under standardized credit assumptions.",
)
patch(
    "app/debt/page.tsx",
    "Four independent constraints compete to determine supportable opening debt.",
    "Four standardized constraints compete to determine supportable opening debt.",
)
patch(
    "app/debt/page.tsx",
    "CFADS must cover contractual debt service.",
    "CFADS is tested against modeled debt service.",
)
patch(
    "app/debt/page.tsx",
    'title="Contractual Debt Schedule"',
    'title="Modeled Debt Schedule"',
)
patch(
    "app/debt/page.tsx",
    'note="The schedule is rebuilt from supportable opening debt."',
    'note="The schedule is rebuilt from supportable opening debt under standardized credit assumptions."',
)

# Page 6 — retain the fixed-schedule semantics while making clear the schedule is model-defined.
patch(
    "app/risk/page.tsx",
    "DOWNSIDE RISK · CONTRACTUAL DEBT · COVERAGE STRESS",
    "DOWNSIDE RISK · MODEL-DEFINED DEBT SCHEDULE · COVERAGE STRESS",
)
patch(
    "app/risk/page.tsx",
    "while contractual debt\n              semantics prevent downside from being hidden by automatic\n              principal re-sculpting.",
    "while model-defined fixed-schedule\n              semantics prevent downside from being hidden by automatic\n              principal re-sculpting.",
)
patch(
    "app/risk/page.tsx",
    "CONTRACTUAL SCHEDULE SEMANTICS",
    "MODEL-DEFINED FIXED-SCHEDULE SEMANTICS",
)
patch(
    "app/risk/page.tsx",
    'title="Contractual Debt Under Stress"',
    'title="Model-Defined Debt Schedule Under Stress"',
)
patch(
    "app/risk/page.tsx",
    'note="Downside coverage is tested against the base contractual schedule."',
    'note="Downside coverage is tested against the base model-defined schedule."',
)
patch(
    "app/risk/page.tsx",
    "contractual debt service before operating CFADS.",
    "modeled debt service before operating CFADS.",
    count=3,
)
patch(
    "app/risk/page.tsx",
    "cash available for contractual debt service.",
    "cash available for modeled debt service.",
)
patch(
    "app/risk/page.tsx",
    "<Check /> Contractual debt treatment",
    "<Check /> Model-defined fixed-schedule debt treatment",
)
patch(
    "app/risk/page.tsx",
    "<b>CONTRACTUAL</b>",
    "<b>MODEL-DEFINED SCHEDULE</b>",
)
patch(
    "app/risk/page.tsx",
    "A downside model is credible only when the debt contract stays\n              visible.",
    "A downside model is credible only when the model-defined debt schedule stays\n              visible.",
)
patch(
    "app/risk/page.tsx",
    "Contractual schedule preservation",
    "Model-defined schedule preservation",
)
patch(
    "app/risk/page.tsx",
    "const availableProjects = projects.slice(0, 19);",
    "const availableProjects = projects;",
)
patch(
    "app/risk/page.tsx",
    "<b>9</b>",
    "<b>{SCENARIOS.length}</b>",
)
patch(
    "app/risk/page.tsx",
    "<b>171</b>",
    "<b>{riskRows.length}</b>",
)
patch(
    "app/risk/page.tsx",
    "<b>3</b>",
    "<b>{new Set(SCENARIOS.map((scenario) => scenario.mode)).size}</b>",
)
patch(
    "app/risk/page.tsx",
    '<RiskKpi icon={Gauge} value="9" label="Governed Scenarios" />',
    '<RiskKpi icon={Gauge} value={String(SCENARIOS.length)} label="Governed Scenarios" />',
)
patch(
    "app/risk/page.tsx",
    '<RiskKpi icon={Landmark} value="3" label="Debt Modes" />',
    '<RiskKpi icon={Landmark} value={String(new Set(SCENARIOS.map((scenario) => scenario.mode)).size)} label="Debt Modes" />',
)
patch(
    "app/risk/page.tsx",
    'note="19 economics-ready projects × 9 governed scenarios = 171 unique rows."',
    'note={`${availableProjects.length} economics-ready projects × ${SCENARIOS.length} governed scenarios = ${riskRows.length} unique rows.`}',
)

# Page 7 — use traceability language and bind release counts to loaded canonical records.
patch(
    "app/diligence/page.tsx",
    "Structured, auditable analysis across physical, commercial,\n                credit and downside lenses.",
    "Structured, traceable analysis across physical, commercial,\n                credit and downside lenses.",
)
patch(
    "app/diligence/page.tsx",
    '<Kpi icon={ClipboardCheck} value="19" label="Diligence Records" />',
    '<Kpi icon={ClipboardCheck} value={String(financeRecords.length)} label="Diligence Records" />',
)
patch(
    "app/diligence/page.tsx",
    '<Kpi icon={Zap} value="1" label="Technical Validation Track" />',
    '<Kpi icon={Zap} value={String(technicalRecord ? 1 : 0)} label="Technical Validation Track" />',
)
patch(
    "app/diligence/page.tsx",
    "<Check size={15} /> 20 selected = 19 diligence + 1 technical track",
    "<Check size={15} /> {projects.length} selected = {financeRecords.length} diligence + {technicalRecord ? 1 : 0} technical track",
)
patch(
    "app/diligence/page.tsx",
    "<Check size={15} /> 19 economics-ready records",
    "<Check size={15} /> {financeRecords.length} economics-ready records",
)
patch(
    "app/diligence/page.tsx",
    "{filteredRecords.length} of 19 records",
    "{filteredRecords.length} of {financeRecords.length} records",
)
patch(
    "app/diligence/page.tsx",
    "Total universe: 19 diligence records · Technical track",
    "Total universe: {financeRecords.length} diligence records · Technical track",
)
patch(
    "app/diligence/page.tsx",
    "<Check size={16} /> 1 technical-validation record · not present in\n            the 19-row finance shortlist · no replacement benchmark invented.",
    "<Check size={16} /> {technicalRecord ? 1 : 0} technical-validation record · not present in\n            the {financeRecords.length}-row finance shortlist · no replacement benchmark invented.",
)
patch(
    "app/diligence/page.tsx",
    'value="19"\n                label="Ready diligence records"',
    'value={String(financeRecords.length)}\n                label="Ready diligence records"',
)
patch(
    "app/diligence/page.tsx",
    "['Economics modelable?', 'YES · 19 records', 'green']",
    "['Economics modelable?', `YES · ${financeRecords.length} records`, 'green']",
)

# Extend browser regression coverage for the newly tightened claim boundaries.
test_path = Path("tests/v5_1_3_website_browser.spec.mjs")
test_text = test_path.read_text(encoding="utf-8")
addition = r'''

test('final claim-boundary wording avoids unsupported transaction implications', async ({page, request}) => {
  await page.goto(`${base}/`, {waitUntil:'networkidle'});
  await expect(page.locator('main')).toContainText('traceable analytical framework');
  await expect(page.locator('main')).not.toContainText('auditable analytical framework');

  await page.goto(`${base}/projects`, {waitUntil:'networkidle'});
  await expect(page.locator('main')).toContainText('explicit and traceable');

  await page.goto(`${base}/energy`, {waitUntil:'networkidle'});
  await expect(page.locator('#boundaries')).toContainText('Self-consumption, modeled surplus and grid purchase');
  await expect(page.locator('.energy-takeaway')).toContainText('Traceable and reproducible');
  await expect(page.locator('main')).not.toContainText('Audit-ready and reproducible');

  await page.goto(`${base}/economics`, {waitUntil:'networkidle'});
  await expect(page.locator('main')).toContainText('Resolved reference tariff thresholds and commercial constraints');
  await expect(page.locator('main')).toContainText('MODELED COMMERCIAL STATUS');

  await page.goto(`${base}/debt`, {waitUntil:'networkidle'});
  await expect(page.locator('main')).toContainText('Four standardized constraints compete');
  await expect(page.locator('#schedule')).toContainText('Modeled Debt Schedule');

  const risk = await (await request.get(`${base}/data/risk.json`)).json();
  await page.goto(`${base}/risk`, {waitUntil:'networkidle'});
  await expect(page.locator('.risk-hero-card')).toContainText(String(risk.rows.length));
  await expect(page.locator('main')).toContainText('MODEL-DEFINED FIXED-SCHEDULE SEMANTICS');
  await expect(page.locator('main')).not.toContainText('CONTRACTUAL SCHEDULE SEMANTICS');

  const diligence = await (await request.get(`${base}/data/diligence.json`)).json();
  await page.goto(`${base}/diligence`, {waitUntil:'networkidle'});
  await expect(page.locator('.diligence-hero-kpis')).toContainText(String(diligence.rows.length));
  await expect(page.locator('main')).toContainText('Structured, traceable analysis');
  await expect(page.locator('main')).not.toContainText('Structured, auditable analysis');
});
'''
if "final claim-boundary wording avoids unsupported transaction implications" in test_text:
    raise SystemExit("browser claim-boundary test already exists")
test_path.write_text(test_text + addition, encoding="utf-8")
