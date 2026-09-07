'use client';

import Image from '@/lib/site-image';
import Link from '@/lib/site-link';
import {
  ArrowDown,
  ArrowRight,
  BarChart3,
  Building2,
  Check,
  ChevronDown,
  CircleHelp,
  FileCheck2,
  Landmark,
  LineChart,
  Percent,
  Scale,
  ShieldAlert,
  UserRound,
  WalletCards,
  X,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { loadWebsiteData } from '@/lib/data';
const GO_MALL = 'VN-GY-GOMALL';
type Project = {
  project_id: string;
  project_name: string;
  country: string;
  developer?: string;
  capacityMw?: number;
  baseGenerationP50Kwh?: string;
  technicalDataBlocked?: boolean;
};
type EconRow = {
  project_id: string;
  projectId?: string;
  projectName?: string;
  country?: string;
  decision?: string;
  ppa_mode?: string;
  reference_case?: string;
  referenceCase?: string;
  ppaMode?: string;
  customerCeilingVndKwh?: number | null;
  sponsorFloorVndKwh?: number | null;
  lenderFloorVndKwh?: number | null;
  negotiationGapVndKwh?: number | null;
  capexUsd?: number | null;
  projectNpvUsd?: number | null;
  projectIrr?: number | null;
  equityNpvUsd?: number | null;
  equityIrr?: number | null;
  year1?: {
    revenue: number;
    opex: number;
    tax: number;
    cfads: number;
    debtService: number;
    equityCashFlow: number;
  } | null;
  ppaStatus?: string;
};
const usdM = (value?: number | null) =>
  value == null ? 'NOT AVAILABLE' : `$${(value / 1_000_000).toFixed(3)}m`;
const bn = (value?: number | null) =>
  value == null ? 'NOT AVAILABLE' : `${(value / 1_000_000_000).toFixed(3)}bn`;
const vnd = (value?: number | null) =>
  value == null
    ? 'NOT RESOLVED'
    : `VND ${value.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;
const percent = (value?: number | null) =>
  value == null ? 'NO VIABLE IRR / NOT RESOLVED' : `${(value * 100).toFixed(2)}%`;
function Heading({
  n,
  title,
  note,
}: {
  n: string;
  title: string;
  note?: string;
}) {
  return (
    <div className="economics-heading">
      <div>
        <span className="economics-index">{n}</span>
        <h2>{title}</h2>
      </div>
      {note && <p>{note}</p>}
    </div>
  );
}

function KPI({
  icon: Icon,
  value,
  label,
  sub,
  tone = '',
}: {
  icon: typeof WalletCards;
  value: string;
  label: string;
  sub?: string;
  tone?: string;
}) {
  return (
    <div className={`economics-kpi ${tone}`}>
      <Icon size={21} />
      <strong>{value}</strong>
      <span>{label}</span>
      {sub && <small>{sub}</small>}
    </div>
  );
}

function Waterfall({ data }: { data?: EconRow }) {
  if (!data?.year1) {
    return <div className="waterfall-empty">DATA UNAVAILABLE</div>;
  }
  const bars = [
    { label: 'Revenue', value: data.year1.revenue / 1_000_000_000, color: 'green' },
    { label: 'OPEX', value: -data.year1.opex / 1_000_000_000, color: 'amber' },
    { label: 'Tax', value: -data.year1.tax / 1_000_000_000, color: 'red' },
    { label: 'CFADS', value: data.year1.cfads / 1_000_000_000, color: 'green' },
  ];
  const max = Math.max(1, ...bars.map(bar => Math.abs(bar.value)));
  return (
    <div
      className="waterfall"
      aria-label="Annual CFADS bridge from revenue to operating cash flow"
    >
      <div className="waterfall-y">
        <span>
          VND bn
          <br />
          {max.toFixed(1)}
        </span>
        <span>{(max*.75).toFixed(1)}</span>
        <span>{(max*.5).toFixed(1)}</span>
        <span>{(max*.25).toFixed(1)}</span>
        <span>0</span>
      </div>
      <div className="waterfall-bars">
        {bars.map((bar) => (
          <div className="waterfall-item" key={bar.label}>
            <strong className={bar.value < 0 ? 'negative' : ''}>
              {bar.value > 0 ? '' : '−'}
              {Math.abs(bar.value).toFixed(3)}bn
            </strong>
            <i
              className={bar.color}
              style={{
                height: `${Math.max(19, (Math.abs(bar.value) / max) * 160)}px`,
              }}
            />
            <span>{bar.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function Frontier({ data }: { data?: EconRow }) {
  const entries = [
    { label: 'Customer ceiling', value: data?.customerCeilingVndKwh, color: '#197350' },
    { label: 'Sponsor floor', value: data?.sponsorFloorVndKwh, color: '#d89521' },
    { label: 'Lender floor', value: data?.lenderFloorVndKwh, color: '#c93030' },
  ];
  const values = entries.flatMap(e => e.value == null ? [] : [e.value]);
  if (!values.length) return <p>No resolved tariff outputs for this project.</p>;
  const low = Math.min(...values), high = Math.max(...values);
  const padding = Math.max((high-low)*.12, high*.05,1);
  const min = Math.max(0,low-padding), max = high+padding;
  const x = (n:number) => 90+(n-min)/(max-min)*540;
  return <div className="frontier-visual">
    <svg viewBox="0 0 720 170" aria-label="Resolved tariff thresholds, VND equivalents per kWh" style={{width:'100%',height:'auto'}}>
      {entries.map((e,i)=><g key={e.label}>
        <text x="4" y={25+i*42} fontSize="11">{e.label}</text>
        <line x1="90" x2="630" y1={30+i*42} y2={30+i*42} stroke="#d7dfd9"/>
        {e.value != null && <circle cx={x(e.value)} cy={30+i*42} r="5" fill={e.color}/>}
        <text x="638" y={34+i*42} fontSize="10">{e.value == null ? 'Unresolved' : e.value.toFixed(2)}</text>
      </g>)}
      <text x="90" y="150" fontSize="10">{min.toFixed(0)}</text>
      <text x="500" y="150" fontSize="10">{max.toFixed(0)} VND/kWh</text>
    </svg>
    <p>Local-currency model thresholds converted using frozen FX. Missing solver outputs are not plotted as zero.</p>
  </div>;
}

export default function EconomicsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [econRows, setEconRows] = useState<EconRow[]>([]);
  const [selectedId, setSelectedId] = useState(GO_MALL);
  useEffect(() => { const id = new URLSearchParams(window.location.search).get('project'); if(id) queueMicrotask(() => setSelectedId(id)); }, []);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const queryId = new URLSearchParams(window.location.search).get('project');
    void Promise.all([
      loadWebsiteData<{ projects?: Project[] }>('projects'),
      loadWebsiteData<{ rows?: EconRow[] }>('economics'),
    ])
      .then(([projectRaw, econRaw]) => {
        const available = (
          (projectRaw as { projects?: Project[] }).projects ?? []
        ).filter((project) => !project.technicalDataBlocked);
        setProjects(available);
        setEconRows(
          (econRaw.rows ?? []).map((row) => ({
            ...row,
            project_id: row.project_id ?? row.projectId ?? '',
          })),
        );
        if (
          !available.some(
            (project: Project) => project.project_id === (queryId ?? GO_MALL),
          )
        )
          setSelectedId(GO_MALL);
      })
      .finally(() => setLoading(false));
  }, []);

  const selected = useMemo(
    () =>
      projects.find((project) => project.project_id === selectedId) ??
      projects.find((project) => project.project_id === GO_MALL),
    [projects, selectedId],
  );
  const reference = econRows.find(
    (row) =>
      (row.project_id ?? row.projectId) === selected?.project_id,
  );
  const isGoMall = reference != null;
  const decision =
    reference?.decision ??
    'INDETERMINATE_MISSING_COMMERCIAL_DATA';
  const emptyZoneCount = econRows.filter(
    (row) => row.ppaStatus === 'EMPTY_NEGOTIATION_ZONE',
  ).length;
  const unresolvedCount = econRows.filter(
    (row) => row.ppaStatus === 'NOT_RESOLVED' || row.ppaStatus === 'INSUFFICIENT_DATA',
  ).length;
  const changeProject = (value: string) => {
    setSelectedId(value);
    window.history.replaceState(
      null,
      '',
      `${window.location.pathname}?project=${encodeURIComponent(value)}`,
    );
  };

  return (
    <main className="economics-page">
      <header className="economics-header">
        <Link href="/" className="economics-brand">
          <span>
            <Landmark size={22} />
          </span>
          <strong>
            VietGreen<small>C&amp;I Solar Project Finance</small>
          </strong>
        </Link>
        <nav>
          <Link href="/">Overview</Link>
          <Link href="/projects">Projects &amp; Data</Link>
          <Link href="/energy">Energy &amp; Physical</Link>
          <Link href="/economics" className="active">
            Finance <ChevronDown size={13} />
          </Link>
          <Link href="/diligence">Diligence</Link>
          <Link href="/model-evidence">Model &amp; Evidence</Link>
        </nav>
        <span className="economics-release">V5.1.3 · Frozen Model</span>
      </header>
      <section className="economics-hero">
        <Image
          src="/assets/projects/projects-hero.webp"
          alt="Commercial rooftop solar project"
          fill
          priority
          sizes="100vw"
        />
        <div className="economics-hero-shade" />
        <div className="economics-hero-inner">
          <div className="economics-hero-copy">
            <p className="economics-eyebrow">
              PROJECT ECONOMICS · CFADS · PPA FRONTIER
            </p>
            <h1>Where Energy Becomes Project Finance Economics.</h1>
            <p>
              The economics layer converts physical output into revenue, CFADS,
              Project and Equity returns, then tests whether customer, sponsor
              and lender commercial constraints can coexist.
            </p>
            <div className="economics-buttons">
              <a
                className="economics-button primary"
                href="#reference-economics"
              >
                Review Economics <ArrowDown size={14} />
              </a>
              <a className="economics-button" href="#ppa-frontier">
                Inspect PPA Frontier <ArrowDown size={14} />
              </a>
            </div>
          </div>
          <aside className="economics-hero-card">
            <small>REFERENCE CASE</small>
            <h2>{vnd(reference?.customerCeilingVndKwh)} / kWh</h2>
            <div>
              <span>CAPEX</span>
              <b>{usdM(reference?.capexUsd)}</b>
            </div>
            <div>
              <span>PROJECT NPV</span>
              <b className="bad">{usdM(reference?.projectNpvUsd)}</b>
            </div>
            <div>
              <span>PPA STATUS</span>
              <b className="warn">{reference?.ppaStatus ?? 'NOT RESOLVED'}</b>
            </div>
            <footer>FRONTIER_ONLY · NOT ACTUAL PPA</footer>
          </aside>
        </div>
      </section>
      <div className="economics-main">
        <section className="economics-section project-section">
          <Heading
            n="1"
            title="Selected Project Economics"
            note="Reference-case outputs are kept separate from any executed commercial term."
          />
          <div className="economics-selector">
            <label htmlFor="economics-project">SELECT PROJECT</label>
            <div>
              <select
                id="economics-project"
                value={selectedId}
                onChange={(event) => changeProject(event.target.value)}
                disabled={loading}
              >
                {projects.map((project) => (
                  <option key={project.project_id} value={project.project_id}>
                    {project.project_name}
                  </option>
                ))}
              </select>
              <ChevronDown size={15} />
            </div>
            <span className="identity">
              <b>{selected?.project_name ?? 'GO Mall Vietnam portfolio'}</b>
              <small>
                {selected?.project_id ?? GO_MALL} ·{' '}
                {selected?.country ?? 'Not available'} · {selected?.developer ?? 'Not available'} ·{' '}
                {selected?.capacityMw?.toFixed(3)} MW · {selected?.baseGenerationP50Kwh ? (Number(selected.baseGenerationP50Kwh)/1e6).toFixed(3) : 'N/A'} GWh P50
              </small>
            </span>
            <span className="badge ready">READY_FOR_ECONOMICS</span>
            <span className="badge">REFERENCE_CASE_NOT_ACTUAL_PPA</span>
          </div>
          <div className="economics-kpi-grid">
            <KPI
              icon={WalletCards}
              value={isGoMall ? usdM(reference?.capexUsd) : 'NOT AVAILABLE'}
              label="CAPEX"
              sub="Frozen model CAPEX · USD"
            />
            <KPI
              icon={Percent}
              value={isGoMall ? vnd(reference?.customerCeilingVndKwh) + '/kWh' : 'NOT DISCLOSED'}
              label="Reference Tariff"
              sub={
                isGoMall ? 'Customer ceiling benchmark' : 'No project tariff'
              }
            />
            <KPI
              icon={BarChart3}
              value={isGoMall ? usdM(reference?.projectNpvUsd) : 'NOT AVAILABLE'}
              label="Project NPV"
              sub={isGoMall ? 'After-tax · 10%' : 'Frozen output unavailable'}
              tone="negative"
            />
            <KPI
              icon={LineChart}
              value={isGoMall ? percent(reference?.projectIrr) : 'NOT AVAILABLE'}
              label="Project IRR"
              sub={
                isGoMall
                  ? 'Frozen model output'
                  : 'Frozen output unavailable'
              }
              tone="negative"
            />
            <KPI
              icon={UserRound}
              value={isGoMall ? usdM(reference?.equityNpvUsd) : 'NOT AVAILABLE'}
              label="Equity NPV"
              sub={isGoMall ? 'After-tax · 14%' : 'Frozen output unavailable'}
              tone="negative"
            />
            <KPI
              icon={Scale}
              value={isGoMall ? percent(reference?.equityIrr) : 'NOT AVAILABLE'}
              label="Equity IRR"
              sub={
                isGoMall
                  ? 'Frozen model output'
                  : 'Frozen output unavailable'
              }
              tone="negative"
            />
          </div>
          <div className="economics-strip">
            <span>
              10%<small>Project Discount Rate</small>
            </span>
            <span>
              14%<small>Equity Hurdle</small>
            </span>
            <span>
              25 years<small>Operating Horizon</small>
            </span>
            <span>
              20 years<small>Standardized PPA Tenor</small>
            </span>
            <span>
              FRONTIER_ONLY<small>PPA Mode</small>
            </span>
            <span>
              OPEN<small>Transaction Evidence</small>
            </span>
          </div>
          <div className="tariff-warning">
            <ShieldAlert size={18} />
            <span>
              <b>REFERENCE TARIFF ≠ EXECUTED PPA</b>
              <small>
                VND 3,460/kWh is the customer-ceiling benchmark used by the
                reference case. The exact GO Mall project PPA is not publicly
                disclosed.
              </small>
            </span>
          </div>
        </section>
        <section className="economics-section">
          <Heading
            n="2"
            title="How Revenue Becomes CFADS"
            note="The operating case is translated into cash available for debt service before financing is applied."
          />
          <div className="cashflow-grid">
            <div className="cashflow-card">
              <div className="cashflow-head">
                <h3>CFADS COMPONENTS · YEAR 1 · VND bn</h3>
              </div>
              <Waterfall data={reference} />
              <div className="cashflow-totals">
                <span>
                  <b>{bn(reference?.year1?.revenue)}</b>
                  <small>Revenue</small>
                </span>
                <span>
                  <b className="negative">−{bn(reference?.year1?.opex)}</b>
                  <small>OPEX</small>
                </span>
                <span>
                  <b className="negative">−{bn(reference?.year1?.tax)}</b>
                  <small>Tax</small>
                </span>
                <span>
                  <b>{bn(reference?.year1?.cfads)}</b>
                  <small>CFADS · After-Tax</small>
                </span>
                <span>
                  <b>
                    Margin
                    <br />
                    {reference?.year1?.revenue ? `${(reference.year1.cfads/reference.year1.revenue*100).toFixed(1)}%` : 'N/A'}
                  </b>
                </span>
              </div>
            </div>
            <div className="cashflow-detail">
              <h3>ECONOMICS SNAPSHOT</h3>
              <div className="snapshot-cols">
                <div>
                  <b>PROJECT ECONOMICS (After-Tax)</b>
                  <span>
                    NPV (USD)<strong>{usdM(reference?.projectNpvUsd)}</strong>
                  </span>
                  <span>
                    IRR<strong>{percent(reference?.projectIrr)}</strong>
                  </span>
                  <span>
                    Payback<strong>No payback</strong>
                  </span>
                  <span>
                    DSCR (avg)<strong>Reference only</strong>
                  </span>
                </div>
                <div>
                  <b>EQUITY ECONOMICS (After-Tax)</b>
                  <span>
                    NPV (USD)<strong>{usdM(reference?.equityNpvUsd)}</strong>
                  </span>
                  <span>
                    IRR<strong>{percent(reference?.equityIrr)}</strong>
                  </span>
                  <span>
                    Payback<strong>No payback</strong>
                  </span>
                  <span>
                    Equity Share<strong>Not disclosed</strong>
                  </span>
                </div>
              </div>
              <p className="small-note">
                <Check size={14} /> CFADS = Gross Revenue − OPEX − Cash Tax. Tax
                is modeled under frozen benchmark/statutory inputs; this is not
                tax advice.
              </p>
            </div>
          </div>
        </section>
        <section className="economics-section split-section">
          <Heading
            n="3"
            title="Project Economics Are Not Equity Economics"
            note="The model separates unlevered asset returns from sponsor returns after financing."
          />
          <div className="project-equity">
            <div className="return-panel">
              <div className="panel-title">
                <Landmark /> PROJECT ECONOMICS <span>UNLEVERED</span>
              </div>
              <div className="return-grid">
                <span>
                  Project NPV<strong>{usdM(reference?.projectNpvUsd)}</strong>
                </span>
                <span>
                  Project IRR<strong>{percent(reference?.projectIrr)}</strong>
                  <small>Frozen model output</small>
                </span>
                <span>
                  Discount Rate<strong>10%</strong>
                </span>
                <span>
                  Initial CAPEX<strong>{usdM(reference?.capexUsd)}</strong>
                </span>
                <span>
                  Operating CFADS
                  <strong>{bn(reference?.year1?.cfads)} VND</strong>
                </span>
              </div>
              <p className="return-status">
                PROJECT VALUE CREATION · <b>DATA-BOUND REFERENCE CASE</b>
              </p>
              <div className="formula-card">
                Project NPV = PV(Project CFADS) − Initial CAPEX
              </div>
            </div>
            <div className="return-panel equity">
              <div className="panel-title">
                <UserRound /> EQUITY ECONOMICS <span>AFTER DEBT</span>
              </div>
              <div className="return-grid">
                <span>
                  Equity NPV<strong>{usdM(reference?.equityNpvUsd)}</strong>
                </span>
                <span>
                  Equity IRR<strong>{percent(reference?.equityIrr)}</strong>
                  <small>Frozen model output</small>
                </span>
                <span>
                  Equity Hurdle<strong>14%</strong>
                </span>
                <span>
                  Initial Equity<strong>Not disclosed</strong>
                </span>
                <span>
                  Debt Service Handoff<strong>To Debt page</strong>
                </span>
              </div>
              <p className="return-status">
                EQUITY HURDLE · <b>NOT MET AT REFERENCE CASE</b>
              </p>
              <div className="formula-card">
                Equity NPV = PV(CFADS − Debt Service) − Initial Equity
              </div>
            </div>
          </div>
          <div className="explainer">
            <CircleHelp size={19} />
            <span>
              A project can fail the sponsor hurdle even when operating cash
              flow is positive. Financing changes equity cash-flow timing but
              does not repair weak underlying economics.
            </span>
          </div>
        </section>
        <section id="ppa-frontier" className="economics-section">
          <Heading
            n="4"
            title="PPA Frontier"
            note="Commercial viability depends on whether customer, sponsor and lender constraints can overlap."
          />
          <div className="ppa-grid">
            <div className="frontier-panel">
              <div className="stakeholder-definitions">
                <div>
                  <b>CUSTOMER CEILING</b>
                  <span>
                    Highest tariff reference supported by the customer
                    benchmark.
                  </span>
                </div>
                <div>
                  <b>SPONSOR FLOOR</b>
                  <span>
                    Minimum tariff needed for sponsor equity economics to meet
                    the hurdle.
                  </span>
                </div>
                <div>
                  <b>LENDER FLOOR</b>
                  <span>
                    Tariff required for standardized debt capacity under credit
                    constraints.
                  </span>
                </div>
              </div>
              <Frontier data={reference} />
              <div className="frontier-conclusion">
                <Scale size={19} />
                <span>
                  <b>{reference?.ppaStatus ?? 'NOT RESOLVED'}</b>
                  <small>
                    {reference?.sponsorFloorVndKwh == null
                      ? 'Sponsor solver has no resolved output. A full three-party zone cannot be established.'
                      : `Required tariff less customer ceiling: ${vnd(reference?.negotiationGapVndKwh)}/kWh. A positive gap means no overlapping zone.`}
                  </small>
                </span>
              </div>
            </div>
            <div className="commercial-status">
              <h3>COMMERCIAL FEASIBILITY STATUS</h3>
              <strong>{reference?.ppaStatus ?? 'NOT RESOLVED'}</strong>
              <small className="status-decision">{decision}</small>
              <p>
                Customer, sponsor and lender thresholds are model-resolved, but
                the reference case does not establish an executable PPA.
              </p>
              <ul>
                <li>Customer ceiling: {vnd(reference?.customerCeilingVndKwh)}/kWh</li>
                <li>Sponsor floor: {vnd(reference?.sponsorFloorVndKwh)}/kWh</li>
                <li>Lender floor: {vnd(reference?.lenderFloorVndKwh)}/kWh</li>
              </ul>
              <div className="status-chip">
                No viable negotiated PPA conclusion is claimed.
              </div>
            </div>
          </div>
        </section>
        <section className="economics-section">
          <Heading
            n="5"
            title="Three Stakeholders. Three Different Constraints."
          />
          <div className="stakeholder-cards">
            <div className="stakeholder-card customer">
              <UserRound />
              <h3>Customer Ceiling</h3>
              <strong>{vnd(reference?.customerCeilingVndKwh)} / kWh</strong>
              <small>BENCHMARK_ASSUMPTION</small>
              <p>
                Market/reference customer-side ceiling, not a confidential
                executed tariff.
              </p>
            </div>
            <div className="stakeholder-card sponsor">
              <Building2 />
              <h3>Sponsor Floor</h3>
              <strong>{vnd(reference?.sponsorFloorVndKwh)}</strong>
              <small>MODEL-RESOLVED SPONSOR HURDLE</small>
              <p>
                The frozen reference case requires this tariff to meet the 14%
                sponsor hurdle; it is not an executed commercial term.
              </p>
            </div>
            <div className="stakeholder-card lender">
              <Landmark />
              <h3>Lender Floor</h3>
              <strong>{vnd(reference?.lenderFloorVndKwh)} / kWh</strong>
              <small>STANDARDIZED UNDERWRITING OUTPUT</small>
              <p>
                Required by the model frontier for the standardized credit case;
                it is not a lender quote or commitment.
              </p>
            </div>
          </div>
          <blockquote>
            “The commercial problem is not: What PPA should we charge? It is: Is
            there any tariff range that can satisfy customer affordability,
            sponsor returns and lender constraints under the evidence
            available?”
          </blockquote>
        </section>
        <section className="economics-section decision-section">
          <Heading n="6" title="What Can the Model Conclude?" />
          <div className="decision-ladder">
            {[
              'PHYSICAL MODEL|READY',
              'ECONOMICS|MODELED',
              'CUSTOMER CEILING|AVAILABLE',
              'SPONSOR FLOOR|UNRESOLVED',
              'LENDER FLOOR|AVAILABLE',
              'NEGOTIATION ZONE|NOT CONCLUSIVE',
              'DECISION|INDETERMINATE',
            ].map((item, index) => {
              const [top, bottom] = item.split('|');
              return (
                <div
                  key={top}
                  className={
                    bottom === 'UNRESOLVED'
                      ? 'unresolved'
                      : bottom === 'INDETERMINATE'
                        ? 'final'
                        : ''
                  }
                >
                  <span>{String(index + 1).padStart(2, '0')}</span>
                  <b>{top}</b>
                  <strong>{bottom}</strong>
                  {index < 6 && <ArrowDown size={14} />}
                </div>
              );
            })}
          </div>
          <div className="decision-bottom">
            <div>
              <ShieldAlert />
              <span>
                <b>INDETERMINATE_MISSING_COMMERCIAL_DATA</b>
                <small>
                  Sufficient for a standardized operating and finance reference
                  case; insufficient commercial evidence for an executed or
                  supportable negotiated PPA.
                </small>
              </span>
            </div>
            <div className="evidence-needed">
              <b>NEXT EVIDENCE NEEDED</b>
              <span>
                PPA term sheet · Sponsor return requirement · Customer
                billing/tariff evidence · Transaction-specific financing terms
              </span>
            </div>
          </div>
        </section>
        <section className="economics-section portfolio-economics">
          <Heading
            n="7"
            title="Commercial Status Across the Economics-Ready Universe"
            note="Counts are derived from the frozen economics payload; local tariffs are never ranked across currencies."
          />
          <div className="portfolio-grid">
            <div className="portfolio-status">
              <div>
                <i className="dot amber" />
                <b>{unresolvedCount}</b>
                <span>INSUFFICIENT_DATA</span>
              </div>
              <div>
                <i className="dot green" />
                <b>{econRows.filter((row) => row.ppaStatus === 'FEASIBLE_ZONE').length}</b>
                <span>FEASIBLE_ZONE</span>
              </div>
              <div>
                <i className="dot red" />
                <b>{emptyZoneCount}</b>
                <span>EMPTY_NEGOTIATION_ZONE</span>
              </div>
            </div>
            <div className="currency-panel">
              <h3>CURRENCY &amp; FX ASSUMPTION</h3>
              <span>
                Reporting Currency <b>VND</b>
              </span>
              <span>
                Base Currency in Model <b>USD</b>
              </span>
              <span>
                FX Rate (Frozen) <b>25,610 VND/USD</b>
              </span>
              <small>
                Local tariffs are shown with currency and are not used as
                cross-country rankings.
              </small>
            </div>
          </div>
        </section>
        <section className="economics-section boundaries">
          <Heading n="8" title="Claim Boundaries &amp; Handoff to Credit" />
          <div className="boundary-columns">
            <div>
              <h3>WHAT WE CAN CLAIM</h3>
              <p>
                <Check />
                Reference-case Project &amp; Equity NPV/IRR using Customer
                Ceiling
              </p>
              <p>
                <Check />
                CFADS bridge and key financial ratios
              </p>
              <p>
                <Check />
                Commercial feasibility status is INSUFFICIENT_DATA
              </p>
            </div>
            <div className="cannot">
              <h3>WHAT WE CANNOT CLAIM</h3>
              <p>
                <X />
                Actual PPA price or negotiated terms
              </p>
              <p>
                <X />
                Bankable returns or lender approval
              </p>
              <p>
                <X />
                Future results under different assumptions
              </p>
            </div>
            <div className="handoff-credit">
              <h3>HANDOFF TO NEXT MODULE</h3>
              <div>
                <span>
                  Economics
                  <br />
                  &amp; PPA
                </span>
                <ArrowRight />
                <span>
                  Debt
                  <br />
                  &amp; Credit
                </span>
              </div>
              <Link href={`/debt?project=${selectedId}`}>
                Continue to Debt &amp; Credit <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        </section>
        <section className="economics-takeaway">
          <Image
            src="/assets/overview/footer-solar-texture.webp"
            alt="Solar texture"
            fill
            sizes="45vw"
          />
          <div>
            <span className="economics-index gold">9</span>
            <p>RECRUITER TAKEAWAY</p>
            <h2>
              Converts energy to cash with transparent assumptions and clear
              boundaries.
            </h2>
            <ul>
              <li>Separates reference-case returns from PPA terms.</li>
              <li>Uses the PPA frontier to test commercial feasibility.</li>
              <li>Highlights data gaps that drive decisions.</li>
              <li>Finance-first thinking: evidence → decision.</li>
            </ul>
          </div>
        </section>
      </div>
      <footer className="economics-footer">
        <span>Model: V5.1.3 (Frozen)</span>
        <span>Data as of: 31 Dec 2024</span>
        <span>
          <FileCheck2 size={14} /> Evidence: OPEN
        </span>
        <span>REFERENCE_CASE_NOT_ACTUAL_PPA ⓘ</span>
      </footer>
    </main>
  );
}
