'use client';

import SiteHeader from '@/lib/site-header';
import { loadWebsiteData } from '@/lib/data';
import {
  BarChart3,
  BookOpen,
  Calculator,
  CheckCircle2,
  ChevronDown,
  Database,
  Download,
  ExternalLink,
  FileSpreadsheet,
  Landmark,
  LineChart,
  ShieldCheck,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

const GO_MALL = 'VN-GY-GOMALL';
const REPO = 'https://github.com/susayold/vietgreen-ci-solar-project-finance';
const WORKBOOK_BLOB = `${REPO}/blob/main/model/vietgreen_core_model.xlsx`;
const WORKBOOK_RAW = 'https://raw.githubusercontent.com/susayold/vietgreen-ci-solar-project-finance/main/model/vietgreen_core_model.xlsx';
const OFFICE_VIEWER = `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(WORKBOOK_RAW)}`;

type Project = {
  project_id: string;
  project_name: string;
  country: string;
  capacityMw?: number;
  technicalDataBlocked?: boolean;
};

type EnergyRow = {
  projectId: string;
  capacityMw: number;
  p50Gwh: number;
  p90Gwh: number;
  p99Gwh: number;
  annualLoadGwh: number;
  selfConsumedGwh: number;
  exportedGwh: number;
  gridPurchaseGwh: number;
  selfConsumptionShare: number;
  solarCoverageShare: number;
  loadEvidenceLevel?: string;
};

type EconRow = {
  projectId: string;
  projectName: string;
  capexUsd: number | null;
  projectNpvUsd: number | null;
  projectIrr: number | null;
  equityNpvUsd: number | null;
  equityIrr: number | null;
  projectPaybackYears?: number | null;
  equityPaybackYears?: number | null;
  projectDiscountRate?: number;
  equityHurdleRate?: number;
  operatingHorizonYears?: number;
  ppaTenorYears?: number;
  equityShare?: number;
  year1?: {
    revenue: number;
    opex: number;
    tax: number;
    cfads: number;
    debtService: number;
    equityCashFlow: number;
  } | null;
};

type DebtRow = {
  projectId: string;
  debtCapacityUsd: number | null;
  leverage: number | null;
  bindingConstraint: string | null;
  debtRate: number;
  debtTenorYears: number;
  dscrTarget: number;
  llcrMin: number;
  plcrMin: number;
  maxLeverage: number;
  minimumDscr: number | null;
  llcr: number | null;
  plcr: number | null;
  schedule: Array<{
    year: number;
    openingDebt: number;
    principal: number;
    interest: number;
    debtService: number;
    closingDebt: number;
    cfads: number;
    dscr: number | null;
  }>;
};

type RiskRow = {
  projectId: string;
  scenarioId: string;
  debtMode: string;
  minimumDscr: number | null;
  llcr: number | null;
  plcr: number | null;
  openingDebtUsd: number | null;
  additionalDebtUsd: number;
  incrementalCapexUsd: number;
};

type Revision = {
  revision: string;
  source_sha: string;
  checks: Array<{ check: string; status: string }>;
  output_hashes: Record<string, string>;
};

type TabKey =
  | 'map'
  | 'assumptions'
  | 'energy'
  | 'cashflow'
  | 'sizing'
  | 'schedule'
  | 'coverage'
  | 'returns'
  | 'scenarios'
  | 'qa';

const tabs: Array<{ key: TabKey; label: string }> = [
  { key: 'map', label: 'Model Map' },
  { key: 'assumptions', label: 'Assumptions' },
  { key: 'energy', label: 'Energy & Load' },
  { key: 'cashflow', label: 'CFADS' },
  { key: 'sizing', label: 'Debt Sizing' },
  { key: 'schedule', label: 'Debt Schedule' },
  { key: 'coverage', label: 'Coverage' },
  { key: 'returns', label: 'Returns' },
  { key: 'scenarios', label: 'Scenarios' },
  { key: 'qa', label: 'QA / Audit' },
];

const coreSheets = [
  ['00_Control_ModelMap', 'Version, scenario, release and stale-output flags'],
  ['01_Assumptions', 'Central assumptions and IDs'],
  ['02_Evidence_Regulatory', 'Source, regulatory, tariff and tax versions'],
  ['03_Project_Pipeline', 'Opportunity set and hard gates'],
  ['04_Offtakers_Credit_Site', 'Credit, parent and site continuity'],
  ['05_Solar_Energy', 'Resource, loss tree and P50/P90'],
  ['06_Load_PPA', 'Load matching, tariff value and PPA frontier'],
  ['07_CAPEX_Construction', 'CAPEX, sources & uses, construction and IDC'],
  ['08_OPEX', 'O&M and replacement costs'],
  ['09_Tax_VAT_WC', 'Tax, depreciation, VAT and working capital'],
  ['10_Project_CF_CFADS', 'Project cash flow and CFADS'],
  ['11_Debt_Terms', 'Facility terms'],
  ['12_Debt_Sculpting', 'Backward sizing and forward schedule'],
  ['13_Reserves_Waterfall', 'DSRA, reserves and waterfall'],
  ['14_Coverage', 'DSCR, LLCR and PLCR'],
  ['15_Returns_Discount', 'Project/equity returns and discount-rate register'],
  ['16_FX_Financing', 'VND/USD and FX paths'],
  ['17_Scenarios_Sensitivity', 'Downside and reverse stress'],
  ['18_Portfolio', 'Standalone, pooled and allocation views'],
  ['19_IC_Bankability', 'Sponsor/lender decision framing'],
  ['20_External_Validation', 'Benchmarks and exceptions'],
  ['21_QA_Audit', 'Tests and release readiness'],
] as const;

const scenarioLabels: Record<string, string> = {
  BASE: 'Base Case',
  P90_ENERGY: 'P90 Generation',
  CAPEX_OVERRUN: 'CAPEX +15%',
  INTEREST_RATE_SHOCK: 'Rate +200 bps',
  COD_DELAY: 'COD +1 year',
  OPEX_INFLATION: 'OPEX +15%',
  OFFTAKER_NONPAYMENT: 'Offtake collection 75%',
  OFFTAKER_TERMINATION: 'Offtake termination',
  COMBINED_DOWNSIDE: 'Combined downside',
};

const formulaByTab: Record<TabKey, string> = {
  map: '=MODEL_ARCHITECTURE(Inputs → Calculations → Financing → Risk → Decision)',
  assumptions: '=ASSUMPTION_REGISTER(Source, Unit, Value, Evidence_Class, Version)',
  energy: '=Annual_Generation / Installed_Capacity',
  cashflow: '=Revenue - OPEX - Cash_Tax ± Working_Capital_Adjustments',
  sizing: '=MIN(Debt_Leverage, Debt_DSCR, Debt_LLCR, Debt_PLCR)',
  schedule: '=Opening_Debt - Principal = Closing_Debt',
  coverage: '=CFADS / (Principal + Interest)',
  returns: '=XIRR(Project_or_Equity_Cash_Flows, Dates)',
  scenarios: '=BASE_CASE × Scenario_Driver_Shocks',
  qa: '=IF(Reconciliation_Delta=0,"PASS","REVIEW")',
};

const usdM = (value?: number | null) =>
  value == null ? 'N/A' : `$${(value / 1_000_000).toFixed(3)}m`;
const vndBn = (value?: number | null) =>
  value == null ? 'N/A' : `${(value / 1_000_000_000).toFixed(3)}`;
const pct = (value?: number | null, digits = 2) =>
  value == null ? 'N/A' : `${(value * 100).toFixed(digits)}%`;
const ratio = (value?: number | null) =>
  value == null ? 'N/A' : `${value.toFixed(3)}x`;
const number = (value?: number | null, digits = 3) =>
  value == null ? 'N/A' : value.toLocaleString('en-US', { minimumFractionDigits: digits, maximumFractionDigits: digits });

function GridTable({ children, label }: { children: React.ReactNode; label: string }) {
  return <div className="excel-grid-scroll" aria-label={label}><table className="excel-grid">{children}</table></div>;
}

export default function ExcelModelPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [energyRows, setEnergyRows] = useState<EnergyRow[]>([]);
  const [econRows, setEconRows] = useState<EconRow[]>([]);
  const [debtRows, setDebtRows] = useState<DebtRow[]>([]);
  const [riskRows, setRiskRows] = useState<RiskRow[]>([]);
  const [revision, setRevision] = useState<Revision | null>(null);
  const [selectedId, setSelectedId] = useState(GO_MALL);
  const [activeTab, setActiveTab] = useState<TabKey>('map');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const queryId = new URLSearchParams(window.location.search).get('project');
    void Promise.all([
      loadWebsiteData<{ projects?: Project[] }>('projects'),
      loadWebsiteData<{ projects?: EnergyRow[] }>('energy'),
      loadWebsiteData<{ rows?: EconRow[] }>('economics'),
      loadWebsiteData<{ rows?: DebtRow[] }>('debt'),
      loadWebsiteData<{ rows?: RiskRow[] }>('risk'),
      loadWebsiteData<Revision>('model-revision'),
    ])
      .then(([projectPayload, energyPayload, econPayload, debtPayload, riskPayload, revisionPayload]) => {
        const econ = econPayload.rows ?? [];
        const ids = new Set(econ.map((row) => row.projectId));
        const available = (projectPayload.projects ?? []).filter(
          (project) => !project.technicalDataBlocked && ids.has(project.project_id),
        );
        setProjects(available);
        setEnergyRows(energyPayload.projects ?? []);
        setEconRows(econ);
        setDebtRows(debtPayload.rows ?? []);
        setRiskRows(riskPayload.rows ?? []);
        setRevision(revisionPayload);
        if (queryId && available.some((project) => project.project_id === queryId)) {
          setSelectedId(queryId);
        } else if (!available.some((project) => project.project_id === GO_MALL) && available[0]) {
          setSelectedId(available[0].project_id);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  const selectedProject = useMemo(
    () => projects.find((project) => project.project_id === selectedId),
    [projects, selectedId],
  );
  const energy = energyRows.find((row) => row.projectId === selectedId);
  const economics = econRows.find((row) => row.projectId === selectedId);
  const debt = debtRows.find((row) => row.projectId === selectedId);
  const scenarios = riskRows.filter((row) => row.projectId === selectedId);
  const activeSchedule = debt?.schedule.filter(
    (row) => row.openingDebt !== 0 || row.debtService !== 0 || row.closingDebt !== 0,
  ) ?? [];

  const changeProject = (value: string) => {
    setSelectedId(value);
    window.history.replaceState(null, '', `${window.location.pathname}?project=${encodeURIComponent(value)}`);
  };

  return (
    <main className="excel-page">
      <SiteHeader active="/excel-model" />

      <section className="excel-hero">
        <div className="excel-hero-copy">
          <p className="excel-eyebrow">EXCEL MODEL · 22-SHEET ARCHITECTURE · FORMULA TRACEABILITY</p>
          <h1>Open the Workbook.<br />Trace the Project Finance Model.</h1>
          <p>
            A recruiter-facing Excel deep dive that shows how project inputs flow through energy,
            cash flow, debt sizing, coverage, returns, downside scenarios and model controls.
          </p>
          <div className="excel-hero-actions">
            <a href="#workbook-viewer" className="excel-button primary"><FileSpreadsheet size={17} /> View Excel Workbook</a>
            <a href={WORKBOOK_RAW} className="excel-button" target="_blank" rel="noreferrer"><Download size={17} /> Download .xlsx</a>
          </div>
        </div>
        <aside className="excel-hero-card">
          <span>Native workbook</span><strong>22 sheets</strong>
          <span>Current web model</span><strong>{revision?.revision ?? 'V5.1.3'}</strong>
          <span>Model checks</span><strong>{revision?.checks.length ?? '—'}</strong>
          <span>Versioned artifacts</span><strong>{revision ? Object.keys(revision.output_hashes).length : '—'}</strong>
          <footer>EXCEL REVIEW ARTIFACT · NOT LENDER APPROVAL</footer>
        </aside>
      </section>

      <div className="excel-shell">
        <section className="excel-section excel-workbook-section" id="workbook-viewer">
          <div className="excel-section-heading">
            <div><span>1</span><h2>Live Excel Workbook</h2></div>
            <p>Inspect the native workbook directly in the browser.</p>
          </div>
          <div className="excel-filebar">
            <div><FileSpreadsheet size={28} /><span><strong>vietgreen_core_model.xlsx</strong><small>Native 22-sheet Project Finance review workbook</small></span></div>
            <div className="excel-file-actions">
              <a href={WORKBOOK_BLOB} target="_blank" rel="noreferrer">Open on GitHub <ExternalLink size={14} /></a>
              <a href={WORKBOOK_RAW} target="_blank" rel="noreferrer">Download Excel <Download size={14} /></a>
            </div>
          </div>
          <div className="excel-viewer-frame">
            <iframe
              src={OFFICE_VIEWER}
              title="VietGreen native Excel workbook viewer"
              loading="lazy"
              allowFullScreen
            />
          </div>
          <p className="excel-boundary-note">
            Workbook boundary: this native Excel file is a separately versioned review artifact used to demonstrate model architecture and spreadsheet controls. The interactive V5.1.3 walkthrough below reads the current frozen recruiter dataset; historical workbook values should not be treated as the source of current website claims.
          </p>
        </section>

        <section className="excel-section">
          <div className="excel-section-heading">
            <div><span>2</span><h2>Current V5.1.3 Workbook Walkthrough</h2></div>
            <p>Use the selector and tabs as if you were reviewing a financial model.</p>
          </div>

          <div className="excel-review-toolbar">
            <div className="excel-project-select">
              <label htmlFor="excel-project">Selected project</label>
              <div>
                <select id="excel-project" value={selectedId} onChange={(event) => changeProject(event.target.value)} disabled={loading}>
                  {projects.map((project) => <option key={project.project_id} value={project.project_id}>{project.project_name}</option>)}
                </select>
                <ChevronDown size={15} />
              </div>
              <small>{selectedProject?.project_id ?? selectedId} · {selectedProject?.country ?? 'Loading'}</small>
            </div>
            <div className="excel-kpis">
              <article><span>CAPEX</span><strong>{usdM(economics?.capexUsd)}</strong></article>
              <article><span>Debt Capacity</span><strong>{usdM(debt?.debtCapacityUsd)}</strong></article>
              <article><span>Min DSCR</span><strong>{ratio(debt?.minimumDscr)}</strong></article>
              <article><span>Project IRR</span><strong>{pct(economics?.projectIrr)}</strong></article>
              <article><span>Equity IRR</span><strong>{pct(economics?.equityIrr)}</strong></article>
            </div>
          </div>

          <div className="excel-window">
            <div className="excel-ribbon">
              <div className="excel-ribbon-tabs"><b>File</b><span>Home</span><span>Formulas</span><span>Data</span><span>Review</span></div>
              <div className="excel-model-legend">
                <span className="excel-linked">Source-linked</span>
                <span className="excel-input">Assumption / hardcode</span>
                <span className="excel-formula">Formula / derived</span>
                <span className="excel-warning">Warning / unresolved</span>
              </div>
            </div>
            <div className="excel-formula-bar"><span>fx</span><code>{formulaByTab[activeTab]}</code></div>
            <div className="excel-sheet-tabs">
              {tabs.map((tab) => (
                <button type="button" key={tab.key} className={activeTab === tab.key ? 'active' : ''} onClick={() => setActiveTab(tab.key)}>{tab.label}</button>
              ))}
            </div>
            <div className="excel-sheet-body">
              {activeTab === 'map' && (
                <GridTable label="22-sheet workbook architecture">
                  <thead><tr><th>#</th><th>Workbook Sheet</th><th>Primary Purpose</th><th>Model Layer</th></tr></thead>
                  <tbody>{coreSheets.map(([name, purpose], index) => <tr key={name}><td className="excel-row-number">{index + 1}</td><td className="excel-linked">{name}</td><td>{purpose}</td><td className="excel-formula">{index <= 4 ? 'Inputs / Evidence' : index <= 10 ? 'Operating Model' : index <= 17 ? 'Financing / Risk' : 'Decision / Control'}</td></tr>)}</tbody>
                </GridTable>
              )}

              {activeTab === 'assumptions' && (
                <GridTable label="Project Finance assumptions">
                  <thead><tr><th>Assumption</th><th>Value</th><th>Unit</th><th>Model Treatment</th></tr></thead>
                  <tbody>
                    <tr><td>Operating horizon</td><td className="excel-input">{economics?.operatingHorizonYears ?? 'N/A'}</td><td>years</td><td>Analyst / model assumption</td></tr>
                    <tr><td>PPA tenor</td><td className="excel-input">{economics?.ppaTenorYears ?? 'N/A'}</td><td>years</td><td>Reference-case commercial assumption</td></tr>
                    <tr><td>Project discount rate</td><td className="excel-input">{pct(economics?.projectDiscountRate)}</td><td>%</td><td>Discount-rate assumption</td></tr>
                    <tr><td>Equity hurdle rate</td><td className="excel-input">{pct(economics?.equityHurdleRate)}</td><td>%</td><td>Sponsor return hurdle</td></tr>
                    <tr><td>Debt rate</td><td className="excel-input">{pct(debt?.debtRate)}</td><td>% p.a.</td><td>Standardized underwriting assumption</td></tr>
                    <tr><td>Debt tenor</td><td className="excel-input">{debt?.debtTenorYears ?? 'N/A'}</td><td>years</td><td>Standardized underwriting assumption</td></tr>
                    <tr><td>Maximum leverage</td><td className="excel-input">{pct(debt?.maxLeverage, 1)}</td><td>%</td><td>Debt sizing ceiling</td></tr>
                    <tr><td>Target DSCR</td><td className="excel-input">{ratio(debt?.dscrTarget)}</td><td>x</td><td>Debt sculpting target</td></tr>
                    <tr><td>Minimum LLCR</td><td className="excel-input">{ratio(debt?.llcrMin)}</td><td>x</td><td>Credit constraint</td></tr>
                    <tr><td>Minimum PLCR</td><td className="excel-input">{ratio(debt?.plcrMin)}</td><td>x</td><td>Credit constraint</td></tr>
                  </tbody>
                </GridTable>
              )}

              {activeTab === 'energy' && (
                <GridTable label="Energy and load model">
                  <thead><tr><th>Metric</th><th>Value</th><th>Unit</th><th>Formula / Interpretation</th></tr></thead>
                  <tbody>
                    <tr><td>Installed capacity</td><td className="excel-linked">{number(energy?.capacityMw)}</td><td>MWp</td><td>Source-backed project capacity</td></tr>
                    <tr><td>P50 generation</td><td className="excel-formula">{number(energy?.p50Gwh)}</td><td>GWh</td><td>Reference modeled generation</td></tr>
                    <tr><td>P90 screening generation</td><td className="excel-formula">{number(energy?.p90Gwh)}</td><td>GWh</td><td>Standardized screening factor; not bankable P90</td></tr>
                    <tr><td>P99 screening generation</td><td className="excel-formula">{number(energy?.p99Gwh)}</td><td>GWh</td><td>Standardized screening factor</td></tr>
                    <tr><td>Annual load proxy</td><td className="excel-input">{number(energy?.annualLoadGwh)}</td><td>GWh</td><td>Modeled where customer telemetry is unavailable</td></tr>
                    <tr><td>Self-consumed solar</td><td className="excel-formula">{number(energy?.selfConsumedGwh)}</td><td>GWh</td><td>MIN(Solar, Load) by modeled interval</td></tr>
                    <tr><td>Modeled surplus</td><td className="excel-formula">{number(energy?.exportedGwh)}</td><td>GWh</td><td>Physical residual; not proven export entitlement</td></tr>
                    <tr><td>Grid purchase</td><td className="excel-formula">{number(energy?.gridPurchaseGwh)}</td><td>GWh</td><td>MAX(Load - Solar, 0)</td></tr>
                    <tr><td>Self-consumption share</td><td className="excel-formula">{pct(energy?.selfConsumptionShare)}</td><td>%</td><td>Self-consumed solar / solar generation</td></tr>
                    <tr><td>Solar coverage share</td><td className="excel-formula">{pct(energy?.solarCoverageShare)}</td><td>%</td><td>Self-consumed solar / modeled annual load</td></tr>
                  </tbody>
                </GridTable>
              )}

              {activeTab === 'cashflow' && (
                <GridTable label="Year 1 project cash flow and CFADS bridge">
                  <thead><tr><th>Line Item</th><th>Year 1</th><th>Unit</th><th>Excel Logic</th></tr></thead>
                  <tbody>
                    <tr><td>Revenue</td><td className="excel-formula">{vndBn(economics?.year1?.revenue)}</td><td>VND bn</td><td>Energy × reference tariff</td></tr>
                    <tr><td>OPEX</td><td className="excel-formula">({vndBn(economics?.year1?.opex)})</td><td>VND bn</td><td>Operating and maintenance costs</td></tr>
                    <tr><td>Cash tax</td><td className="excel-formula">({vndBn(economics?.year1?.tax)})</td><td>VND bn</td><td>Taxable income → cash tax schedule</td></tr>
                    <tr className="excel-total-row"><td>CFADS</td><td className="excel-formula">{vndBn(economics?.year1?.cfads)}</td><td>VND bn</td><td>Revenue − OPEX − cash tax ± WC adjustments</td></tr>
                    <tr><td>Debt service</td><td className="excel-formula">{vndBn(economics?.year1?.debtService)}</td><td>VND bn</td><td>Principal + interest</td></tr>
                    <tr className="excel-total-row"><td>Equity cash flow</td><td className="excel-formula">{vndBn(economics?.year1?.equityCashFlow)}</td><td>VND bn</td><td>Cash available after modeled debt service</td></tr>
                  </tbody>
                </GridTable>
              )}

              {activeTab === 'sizing' && (
                <div className="excel-two-column">
                  <GridTable label="Debt sizing summary">
                    <thead><tr><th>Debt Metric</th><th>Result</th><th>Interpretation</th></tr></thead>
                    <tbody>
                      <tr><td>Final supportable debt</td><td className="excel-formula">{usdM(debt?.debtCapacityUsd)}</td><td>Minimum supportable amount across constraints</td></tr>
                      <tr><td>Supportable leverage</td><td className="excel-formula">{pct(debt?.leverage, 1)}</td><td>Debt / project CAPEX</td></tr>
                      <tr><td>Binding constraint</td><td className="excel-warning">{debt?.bindingConstraint ?? 'N/A'}</td><td>Constraint setting final debt capacity</td></tr>
                      <tr><td>Maximum leverage policy</td><td className="excel-input">{pct(debt?.maxLeverage, 1)}</td><td>Standardized leverage ceiling</td></tr>
                    </tbody>
                  </GridTable>
                  <div className="excel-formula-card">
                    <Calculator size={28} />
                    <h3>Debt sizing formula</h3>
                    <code>Debt_final = MIN(Debt_Leverage, Debt_DSCR, Debt_LLCR, Debt_PLCR)</code>
                    <p>The model does not assume that a project automatically receives the maximum leverage. It calculates supportable debt under independent credit constraints and selects the lowest amount.</p>
                  </div>
                </div>
              )}

              {activeTab === 'schedule' && (
                <GridTable label="Modeled debt schedule">
                  <thead><tr><th>Year</th><th>Opening Debt</th><th>CFADS</th><th>Interest</th><th>Principal</th><th>Debt Service</th><th>Closing Debt</th><th>DSCR</th></tr></thead>
                  <tbody>{activeSchedule.map((row) => <tr key={row.year}><td className="excel-row-number">{row.year}</td><td>{vndBn(row.openingDebt)}</td><td className="excel-linked">{vndBn(row.cfads)}</td><td>{vndBn(row.interest)}</td><td>{vndBn(row.principal)}</td><td>{vndBn(row.debtService)}</td><td>{vndBn(row.closingDebt)}</td><td className="excel-formula">{ratio(row.dscr)}</td></tr>)}</tbody>
                </GridTable>
              )}

              {activeTab === 'coverage' && (
                <div className="excel-coverage-grid">
                  <article><span>Minimum DSCR</span><strong>{ratio(debt?.minimumDscr)}</strong><code>CFADS / Debt Service</code><p>Period-by-period debt service protection.</p></article>
                  <article><span>LLCR</span><strong>{ratio(debt?.llcr)}</strong><code>PV(CFADS during loan life) / Debt</code><p>Lifetime coverage during the remaining loan tenor.</p></article>
                  <article><span>PLCR</span><strong>{ratio(debt?.plcr)}</strong><code>PV(CFADS during project life) / Debt</code><p>Coverage including cash flow after loan maturity.</p></article>
                  <article className="threshold-card"><span>Credit thresholds</span><strong>{ratio(debt?.dscrTarget)} / {ratio(debt?.llcrMin)} / {ratio(debt?.plcrMin)}</strong><code>DSCR / LLCR / PLCR</code><p>Standardized underwriting constraints, not actual lender terms.</p></article>
                </div>
              )}

              {activeTab === 'returns' && (
                <GridTable label="Project and equity returns">
                  <thead><tr><th>Return Metric</th><th>Result</th><th>Perspective</th><th>Model Logic</th></tr></thead>
                  <tbody>
                    <tr><td>Project NPV</td><td className="excel-formula">{usdM(economics?.projectNpvUsd)}</td><td>Unlevered asset</td><td>Discounted after-tax project cash flows</td></tr>
                    <tr><td>Project IRR</td><td className="excel-formula">{pct(economics?.projectIrr)}</td><td>Unlevered asset</td><td>IRR of project cash flows before financing</td></tr>
                    <tr><td>Project payback</td><td>{economics?.projectPaybackYears == null ? 'N/A' : `${economics.projectPaybackYears.toFixed(2)} years`}</td><td>Unlevered asset</td><td>Cumulative project cash flow recovery</td></tr>
                    <tr><td>Equity NPV</td><td className="excel-formula">{usdM(economics?.equityNpvUsd)}</td><td>Sponsor</td><td>Equity contribution + post-debt cash flows</td></tr>
                    <tr><td>Equity IRR</td><td className="excel-formula">{pct(economics?.equityIrr)}</td><td>Sponsor</td><td>IRR on equity cash-flow stream</td></tr>
                    <tr><td>Equity payback</td><td>{economics?.equityPaybackYears == null ? 'N/A' : `${economics.equityPaybackYears.toFixed(2)} years`}</td><td>Sponsor</td><td>Cumulative equity cash flow recovery</td></tr>
                  </tbody>
                </GridTable>
              )}

              {activeTab === 'scenarios' && (
                <GridTable label="Project downside scenarios">
                  <thead><tr><th>Scenario</th><th>Debt Treatment</th><th>Opening Debt</th><th>Incremental CAPEX</th><th>Additional Debt</th><th>Min DSCR</th><th>LLCR</th><th>PLCR</th></tr></thead>
                  <tbody>{scenarios.map((row) => <tr key={row.scenarioId}><td className="excel-linked">{scenarioLabels[row.scenarioId] ?? row.scenarioId}</td><td>{row.debtMode === 'FIXED_CONTRACTUAL_SCHEDULE' ? 'MODEL-DEFINED FIXED SCHEDULE' : row.debtMode.replaceAll('_', ' ')}</td><td>{usdM(row.openingDebtUsd)}</td><td>{usdM(row.incrementalCapexUsd)}</td><td>{usdM(row.additionalDebtUsd)}</td><td className={row.minimumDscr != null && row.minimumDscr < (debt?.dscrTarget ?? 0) ? 'excel-warning' : 'excel-formula'}>{ratio(row.minimumDscr)}</td><td>{ratio(row.llcr)}</td><td>{ratio(row.plcr)}</td></tr>)}</tbody>
                </GridTable>
              )}

              {activeTab === 'qa' && (
                <div className="excel-qa-layout">
                  <div className="excel-qa-summary">
                    <ShieldCheck size={34} />
                    <strong>{revision?.checks.length ?? '—'} automated checks</strong>
                    <span>{revision ? Object.keys(revision.output_hashes).length : '—'} versioned output artifacts</span>
                    <code>{revision?.source_sha ?? 'Loading calculation fingerprint…'}</code>
                  </div>
                  <div className="excel-grid-scroll">
                    <table className="excel-grid"><thead><tr><th>Check</th><th>Status</th></tr></thead><tbody>{revision?.checks.map((item) => <tr key={item.check}><td>{item.check}</td><td className={item.status === 'PASS' ? 'excel-pass' : 'excel-warning'}>{item.status}</td></tr>)}</tbody></table>
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>

        <section className="excel-section">
          <div className="excel-section-heading">
            <div><span>3</span><h2>What This Excel Project Demonstrates</h2></div>
            <p>Skills I can bring into a Project Finance team.</p>
          </div>
          <div className="excel-skills-grid">
            <article><Calculator /><h3>Financial Modeling</h3><p>Built linked operating and financing logic from project assumptions through project and equity cash flows, rather than treating outputs as isolated calculations.</p></article>
            <article><Landmark /><h3>Debt Sizing & Sculpting</h3><p>Modeled supportable debt using leverage, DSCR, LLCR and PLCR constraints, identified the binding constraint and reviewed the forward amortization schedule.</p></article>
            <article><LineChart /><h3>Scenario & Sensitivity Analysis</h3><p>Connected downside drivers to cash flow and coverage metrics while preserving the modeled debt schedule where the stress test requires it.</p></article>
            <article><Database /><h3>Assumption & Evidence Control</h3><p>Separated source-backed facts, derived metrics, benchmark assumptions and unresolved evidence so spreadsheet outputs do not imply false precision.</p></article>
            <article><ShieldCheck /><h3>Formula QA & Reconciliation</h3><p>Used calculation checks, release controls and cross-surface reconciliation to catch broken formulas, stale outputs and inconsistencies before publication.</p></article>
            <article><BarChart3 /><h3>Decision-Oriented Reporting</h3><p>Turned workbook outputs into lender/sponsor metrics, downside findings and due-diligence actions that can support financing discussions.</p></article>
          </div>
        </section>

        <section className="excel-section excel-learning-section">
          <div className="excel-section-heading">
            <div><span>4</span><h2>What I Learned — and How I Can Contribute</h2></div>
          </div>
          <div className="excel-learning-grid">
            <article>
              <BookOpen size={27} />
              <h3>What I learned</h3>
              <ul>
                <li>Project Finance is not just NPV and IRR; financeability depends on cash-flow timing and debt-service capacity.</li>
                <li>CFADS is the bridge between operating performance and lender repayment.</li>
                <li>Debt should be sized under multiple constraints rather than assumed as a fixed percentage of CAPEX.</li>
                <li>A model is only decision-useful when facts, assumptions and missing evidence are clearly separated.</li>
              </ul>
            </article>
            <article>
              <CheckCircle2 size={27} />
              <h3>What I can contribute</h3>
              <ul>
                <li>Build, review and trace financial-model calculations and assumptions.</li>
                <li>Forecast project cash flow and analyze Project IRR, Equity IRR, NPV and payback.</li>
                <li>Calculate CFADS and assess DSCR, LLCR, PLCR, leverage and debt capacity.</li>
                <li>Run sensitivity/downside analysis and identify the assumptions driving the financing result.</li>
                <li>Translate model outputs into clear risks, questions and next-step diligence for the team.</li>
              </ul>
            </article>
          </div>
          <blockquote className="excel-closing-quote">
            “The skill I want to demonstrate is not only that I can build an Excel model, but that I can trace how an asset creates cash flow, how that cash flow supports debt, how downside changes coverage, and what still needs to be verified before capital is committed.”
          </blockquote>
        </section>
      </div>

      <footer className="excel-footer">VietGreen · Excel Project Finance Model · Public-data case study</footer>
    </main>
  );
}
