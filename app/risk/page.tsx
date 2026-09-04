'use client';

export const dynamic = 'force-static';

import Image from 'next/image';
import Link from 'next/link';
import {
  AlertTriangle,
  ArrowDown,
  ArrowRight,
  BarChart3,
  Check,
  ChevronDown,
  CircleAlert,
  FileCheck2,
  Gauge,
  Landmark,
  ShieldAlert,
  Timer,
  TrendingDown,
  X,
  Zap,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

const SHA = 'ff69e15d211ff1abc88200574242ed2f1db49074';
const RAW = `https://raw.githubusercontent.com/susayold/vietgreen-ci-solar-project-finance/${SHA}`;
const GO_MALL = 'VN-GY-GOMALL';

type Project = {
  project_id: string;
  project_name: string;
  country: string;
  technicalDataBlocked?: boolean;
};

type Scenario = {
  id: string;
  label: string;
  shock: string;
  mode: string;
  principal: string;
  interest: string;
  newDebt: string;
  detail: string;
  driver: string;
};

type Metric = {
  dscr: number | null;
  llcr: number | null;
  plcr: number | null;
  debt: string;
  additionalDebt: string;
  capex: string;
};

const SCENARIOS: Scenario[] = [
  {
    id: 'BASE',
    label: 'Base Case',
    shock: 'Reference case',
    mode: 'RESIZED_DEBT',
    principal: 'Sized in base case',
    interest: 'Base rate',
    newDebt: 'Allowed as base sizing',
    detail: 'Establishes base debt capacity and schedule.',
    driver: 'BASE',
  },
  {
    id: 'P90_ENERGY',
    label: 'P90 Generation',
    shock: 'Energy 90%',
    mode: 'FIXED_CONTRACTUAL_SCHEDULE',
    principal: 'Preserved',
    interest: 'Base interest',
    newDebt: '0',
    detail: 'Standardized screening factor; not a bankable P90.',
    driver: 'ENERGY',
  },
  {
    id: 'CAPEX_OVERRUN',
    label: 'CAPEX Overrun',
    shock: 'CAPEX +15%',
    mode: 'NO_NEW_DEBT',
    principal: 'Preserved',
    interest: 'Base interest',
    newDebt: '0',
    detail: 'Incremental CAPEX is sponsor-equity funded.',
    driver: 'CAPEX',
  },
  {
    id: 'INTEREST_RATE_SHOCK',
    label: 'Interest Rate Shock',
    shock: 'Rate +200 bps',
    mode: 'FIXED_CONTRACTUAL_SCHEDULE',
    principal: 'Preserved',
    interest: 'Repriced if floating',
    newDebt: '0',
    detail: 'Principal does not re-sculpt under rate stress.',
    driver: 'RATE',
  },
  {
    id: 'COD_DELAY',
    label: 'COD Delay',
    shock: 'COD +1 year',
    mode: 'FIXED_CONTRACTUAL_SCHEDULE',
    principal: 'Preserved',
    interest: 'Base interest',
    newDebt: '0',
    detail: 'Can create debt service before operating CFADS.',
    driver: 'TIMING',
  },
  {
    id: 'OPEX_INFLATION',
    label: 'OPEX Stress',
    shock: 'OPEX +15%',
    mode: 'FIXED_CONTRACTUAL_SCHEDULE',
    principal: 'Preserved',
    interest: 'Base interest',
    newDebt: '0',
    detail: 'Operating cost is stressed while debt stays contractual.',
    driver: 'OPEX',
  },
  {
    id: 'OFFTAKER_NONPAYMENT',
    label: 'Offtake Nonpayment',
    shock: 'Collection 75%',
    mode: 'FIXED_CONTRACTUAL_SCHEDULE',
    principal: 'Preserved',
    interest: 'Base interest',
    newDebt: '0',
    detail: 'A 25% collection loss is applied to modeled revenue.',
    driver: 'COUNTERPARTY',
  },
  {
    id: 'OFFTAKER_TERMINATION',
    label: 'Offtake Termination',
    shock: 'Operating year 2',
    mode: 'NO_NEW_DEBT',
    principal: 'Preserved',
    interest: 'Base interest',
    newDebt: '0',
    detail: 'Lifetime coverage must be read beyond the Year 1 DSCR.',
    driver: 'COUNTERPARTY',
  },
  {
    id: 'COMBINED_DOWNSIDE',
    label: 'Combined Downside',
    shock: 'P90 + CAPEX + rate + COD',
    mode: 'NO_NEW_DEBT',
    principal: 'Preserved',
    interest: 'Repriced if floating',
    newDebt: '0',
    detail: 'Multi-factor stress with no incremental debt.',
    driver: 'MULTI-FACTOR',
  },
];

// The frozen website payload exposes scenario semantics but not the scenario
// metric rows. These values are kept in an adapter-shaped object so the JSX
// remains source-agnostic and can be replaced by the generated payload when it
// is published, without cloning the featured project into the portfolio.
const GO_MALL_METRICS: Record<string, Metric> = {
  BASE: {
    dscr: 2.38,
    llcr: 2.232,
    plcr: 1.336,
    debt: '$0.529m',
    additionalDebt: '$0',
    capex: 'Base CAPEX',
  },
  P90_ENERGY: {
    dscr: 2.134,
    llcr: 1.998,
    plcr: 1.206,
    debt: 'Preserved',
    additionalDebt: '$0',
    capex: 'Base CAPEX',
  },
  CAPEX_OVERRUN: {
    dscr: 2.369,
    llcr: 2.22,
    plcr: 1.311,
    debt: 'Preserved',
    additionalDebt: '$0',
    capex: '+$1.688m sponsor equity',
  },
  INTEREST_RATE_SHOCK: {
    dscr: 2.337,
    llcr: 2.19,
    plcr: 1.306,
    debt: 'Preserved',
    additionalDebt: '$0',
    capex: 'Base CAPEX',
  },
  COD_DELAY: {
    dscr: 0,
    llcr: 0,
    plcr: 0,
    debt: 'Preserved',
    additionalDebt: '$0',
    capex: 'Base CAPEX',
  },
  OPEX_INFLATION: {
    dscr: 2.345,
    llcr: 2.201,
    plcr: 1.312,
    debt: 'Preserved',
    additionalDebt: '$0',
    capex: 'Base CAPEX',
  },
  OFFTAKER_NONPAYMENT: {
    dscr: 1.766,
    llcr: 1.651,
    plcr: 0.984,
    debt: 'Preserved',
    additionalDebt: '$0',
    capex: 'Base CAPEX',
  },
  OFFTAKER_TERMINATION: {
    dscr: 2.38,
    llcr: 2.232,
    plcr: 1.336,
    debt: 'Preserved',
    additionalDebt: '$0',
    capex: 'Base CAPEX',
  },
  COMBINED_DOWNSIDE: {
    dscr: 0,
    llcr: 0,
    plcr: 0,
    debt: 'Preserved',
    additionalDebt: '$0',
    capex: '+$1.688m sponsor equity',
  },
};

function formatCoverage(value: number | null | undefined) {
  if (value === null || value === undefined) return 'N/A';
  return `${value.toFixed(3)}x`;
}

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
    <div className="risk-heading">
      <div>
        <span className="risk-index">{n}</span>
        <h2>{title}</h2>
      </div>
      {note && <p>{note}</p>}
    </div>
  );
}

function RiskKpi({
  icon: Icon,
  value,
  label,
  tone = '',
}: {
  icon: typeof Gauge;
  value: string;
  label: string;
  tone?: string;
}) {
  return (
    <div className={`risk-kpi ${tone}`}>
      <Icon size={20} />
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function DscrBars({ metrics }: { metrics: Record<string, Metric> | null }) {
  return (
    <div
      className="dscr-chart"
      aria-label="GO Mall minimum DSCR by governed scenario"
    >
      <div className="dscr-reference target">
        <span>1.35x standardized target</span>
      </div>
      <div className="dscr-reference breakeven">
        <span>1.00x debt-service breakeven</span>
      </div>
      {SCENARIOS.map((scenario) => {
        const value = metrics?.[scenario.id]?.dscr ?? null;
        const width = value === null ? 0 : Math.min(100, (value / 3) * 100);
        const tone =
          value === null
            ? 'empty'
            : value === 0
              ? 'zero'
              : value < 1
                ? 'breach'
                : value < 1.35
                  ? 'below'
                  : 'safe';
        return (
          <div className="dscr-row" key={scenario.id}>
            <b>{scenario.label}</b>
            <div className="dscr-track">
              <i className={tone} style={{ width: `${width}%` }} />
            </div>
            <strong className={tone}>{formatCoverage(value)}</strong>
          </div>
        );
      })}
      <div className="dscr-axis">
        <span>0.00x</span>
        <span>1.00x</span>
        <span>1.35x</span>
        <span>2.00x</span>
        <span>3.00x</span>
      </div>
    </div>
  );
}

export default function RiskPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedId, setSelectedId] = useState(() =>
    typeof window === 'undefined'
      ? GO_MALL
      : (new URLSearchParams(window.location.search).get('project') ?? GO_MALL),
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void Promise.all([
      fetch(`${RAW}/website/data/projects.json`).then((response) =>
        response.json(),
      ),
      fetch(`${RAW}/website/data/scenarios.json`).then((response) =>
        response.json(),
      ),
    ])
      .then(([projectRaw]) => {
        const available = (
          (projectRaw as { projects?: Project[] }).projects ?? []
        ).filter((project) => !project.technicalDataBlocked);
        setProjects(available);
        if (!available.some((project) => project.project_id === selectedId))
          setSelectedId(GO_MALL);
      })
      .catch(() => setProjects([]))
      .finally(() => setLoading(false));
  }, [selectedId]);

  const selected = useMemo(
    () =>
      projects.find((project) => project.project_id === selectedId) ??
      projects.find((project) => project.project_id === GO_MALL),
    [projects, selectedId],
  );
  const isGoMall = selected?.project_id === GO_MALL;
  const metrics = isGoMall ? GO_MALL_METRICS : null;
  const zeroCount = metrics
    ? Object.values(metrics).filter((metric) => metric.dscr === 0).length
    : 0;
  const availableProjects = projects.slice(0, 19);
  const changeProject = (value: string) => {
    setSelectedId(value);
    window.history.replaceState(
      null,
      '',
      `/risk?project=${encodeURIComponent(value)}`,
    );
  };

  return (
    <main className="risk-page">
      <header className="risk-header">
        <Link href="/" className="risk-brand">
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
          <Link href="/economics">Finance⌄</Link>
          <Link href="/debt">Debt</Link>
          <Link href="/risk" className="active">
            Risk &amp; Scenarios
          </Link>
          <Link href="/diligence">Diligence</Link>
          <Link href="/model">Model &amp; Evidence</Link>
        </nav>
        <span className="risk-release">V5.1.3 · Frozen Model</span>
      </header>

      <section className="risk-hero">
        <Image
          src="/assets/projects/projects-hero.webp"
          alt="Industrial rooftop solar project"
          fill
          priority
          sizes="100vw"
        />
        <div className="risk-hero-shade" />
        <div className="risk-hero-inner">
          <div className="risk-hero-copy">
            <p className="risk-eyebrow">
              DOWNSIDE RISK · CONTRACTUAL DEBT · COVERAGE STRESS
            </p>
            <h1>
              Stress the Cash Flow —<br />
              Not the Contract Away.
            </h1>
            <p>
              Nine governed scenarios stress energy, CAPEX, rates, COD timing,
              operating costs and offtaker performance while contractual debt
              semantics prevent downside from being hidden by automatic
              principal re-sculpting.
            </p>
            <div className="risk-buttons">
              <a className="risk-button primary" href="#scenario-dscr">
                Review GO Mall Stress Cases <ArrowDown size={14} />
              </a>
              <a className="risk-button" href="#heatmap">
                Inspect Portfolio Risk Matrix <ArrowDown size={14} />
              </a>
            </div>
          </div>
          <aside className="risk-hero-card">
            <div>
              <span>SCENARIOS / PROJECT</span>
              <b>9</b>
            </div>
            <div>
              <span>GOVERNED ROWS</span>
              <b>171</b>
            </div>
            <div>
              <span>DEBT MODES</span>
              <b>3</b>
            </div>
            <div>
              <span>DOWNSIDE SELF-HEALING</span>
              <b>NO</b>
            </div>
            <footer>CONTRACTUAL SCHEDULE SEMANTICS</footer>
          </aside>
        </div>
      </section>

      <div className="risk-main">
        <section className="risk-section">
          <Heading n="1" title="Selected Project Risk Profile" />
          <div className="risk-selector">
            <div>
              <b>{selected?.project_name ?? 'GO Mall Vietnam portfolio'}</b>
              <small>{selected?.project_id ?? GO_MALL}</small>
            </div>
            <div className="risk-select">
              <select
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
            <span>🇻🇳 Vietnam</span>
            <span>♨ GreenYellow</span>
            <span>◉ 9.000 MW</span>
            <span>Base Debt ~ $0.529m</span>
            <b className="risk-badge green">STANDARDIZED_CREDIT_CASE</b>
            <b className="risk-badge gold">SCENARIO_GOVERNED</b>
          </div>
          <div className="risk-kpi-grid">
            <RiskKpi icon={Gauge} value="9" label="Governed Scenarios" />
            <RiskKpi
              icon={BarChart3}
              value="171"
              label="Portfolio Scenario Rows"
            />
            <RiskKpi icon={Gauge} value="2.380x" label="Base Min DSCR" />
            <RiskKpi
              icon={TrendingDown}
              value={isGoMall ? '0.000x' : 'N/A'}
              label="Worst GO Mall Min DSCR"
              tone="red"
            />
            <RiskKpi
              icon={CircleAlert}
              value={isGoMall ? String(zeroCount) : 'N/A'}
              label="GO Mall Zero-DSCR Scenarios"
              tone="amber"
            />
            <RiskKpi icon={Landmark} value="3" label="Debt Modes" />
          </div>
          <div className="risk-strip">
            <span>
              90%<small>P90 Energy Factor</small>
            </span>
            <span>
              +15%<small>CAPEX Stress</small>
            </span>
            <span>
              +200 bps<small>Rate Shock</small>
            </span>
            <span>
              +1 year<small>COD Delay</small>
            </span>
            <span>
              +15%<small>OPEX Stress</small>
            </span>
            <span>
              75%<small>Collection Factor</small>
            </span>
            <span>
              Year 2<small>Offtaker Termination</small>
            </span>
          </div>
          {!isGoMall && (
            <div className="risk-unavailable">
              <AlertTriangle size={17} /> This project has no published scenario
              metric payload in the frozen website release. Risk values are
              shown as N/A/N/D rather than cloned from GO Mall.
            </div>
          )}
        </section>

        <section className="risk-section">
          <Heading
            n="2"
            title="Nine Governed Downside Cases"
            note="Each scenario has explicit operating assumptions and explicit debt semantics."
          />
          <div className="scenario-grid">
            {SCENARIOS.map((scenario, index) => (
              <article
                className={`scenario-card driver-${scenario.driver.toLowerCase().replace('-', '')}`}
                key={scenario.id}
              >
                <div className="scenario-top">
                  <span>{String(index + 1).padStart(2, '0')}</span>
                  <b>{scenario.label}</b>
                </div>
                <strong>{scenario.shock}</strong>
                <small>{scenario.detail}</small>
                <dl>
                  <div>
                    <dt>Debt mode</dt>
                    <dd>{scenario.mode.replaceAll('_', ' ')}</dd>
                  </div>
                  <div>
                    <dt>Principal</dt>
                    <dd>{scenario.principal}</dd>
                  </div>
                  <div>
                    <dt>Interest</dt>
                    <dd>{scenario.interest}</dd>
                  </div>
                  <div>
                    <dt>New debt</dt>
                    <dd>{scenario.newDebt}</dd>
                  </div>
                </dl>
                {scenario.id === 'P90_ENERGY' && (
                  <em>SCREENING P90 · NOT BANKABLE P90</em>
                )}
              </article>
            ))}
          </div>
        </section>

        <section className="risk-section">
          <Heading
            n="3"
            title="The Debt Contract Does Not Self-Heal"
            note="Downside coverage is tested against the base contractual schedule."
          />
          <div className="semantic-banner">
            <ShieldAlert size={22} />
            <div>
              <b>DOWNSIDE DOES NOT RE-SCULPT PRINCIPAL TO RESTORE DSCR</b>
              <span>
                For fixed-contractual and no-new-debt cases, opening, principal
                and closing debt remain preserved. Floating interest may
                reprice; principal does not.
              </span>
            </div>
          </div>
          <div className="semantic-table-wrap">
            <table className="semantic-table">
              <thead>
                <tr>
                  <th>Scenario</th>
                  <th>Debt Mode</th>
                  <th>Opening Debt</th>
                  <th>Principal</th>
                  <th>Closing Debt</th>
                  <th>Interest</th>
                  <th>Additional Debt</th>
                  <th>Incremental CAPEX</th>
                </tr>
              </thead>
              <tbody>
                {SCENARIOS.map((scenario) => (
                  <tr key={scenario.id}>
                    <td>{scenario.label}</td>
                    <td>
                      <b className="mode-tag">
                        {scenario.mode.replaceAll('_', ' ')}
                      </b>
                    </td>
                    <td>{scenario.id === 'BASE' ? 'Sized' : 'PRESERVED'}</td>
                    <td>{scenario.id === 'BASE' ? 'Sized' : 'PRESERVED'}</td>
                    <td>{scenario.id === 'BASE' ? 'Sized' : 'PRESERVED'}</td>
                    <td>{scenario.interest}</td>
                    <td>{scenario.id === 'BASE' ? 'Allowed' : '0'}</td>
                    <td>
                      {scenario.id === 'CAPEX_OVERRUN' ||
                      scenario.id === 'COMBINED_DOWNSIDE'
                        ? 'SPONSOR EQUITY'
                        : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section id="scenario-dscr" className="risk-section">
          <Heading
            n="4"
            title="How GO Mall Coverage Responds to Downside"
            note="Minimum DSCR is recalculated against stressed cash flow and the governed debt treatment."
          />
          <div className="risk-two-column">
            <div className="panel dscr-panel">
              <div className="panel-title">
                <b>GO MALL — SCENARIO DSCR</b>
                <span>
                  <i className="legend-safe" /> ≥1.35x{' '}
                  <i className="legend-amber" /> 1.00–1.35x{' '}
                  <i className="legend-red" /> &lt;1.00x
                </span>
              </div>
              <DscrBars metrics={metrics} />
              <p className="panel-note">
                <CircleAlert size={15} /> 0.000x means contractual debt service
                exists but stressed CFADS is zero. N/A means no debt service
                exists.
              </p>
            </div>
            <div className="panel insight-panel">
              <h3>What breaks first?</h3>
              <div>
                <b className="number red">1</b>
                <span>
                  <strong>COD Delay</strong>
                  <small>
                    Immediate coverage break: DSCR falls to 0.000x before
                    operating CFADS begins.
                  </small>
                </span>
              </div>
              <div>
                <b className="number red">2</b>
                <span>
                  <strong>Combined Downside</strong>
                  <small>
                    Multiple stresses compound while no new debt is added.
                  </small>
                </span>
              </div>
              <div>
                <b className="number amber">3</b>
                <span>
                  <strong>Offtaker Nonpayment</strong>
                  <small>
                    DSCR compresses to 1.766x, closest to the standardized
                    target.
                  </small>
                </span>
              </div>
              <div className="termination-note">
                <Timer size={18} />
                <span>
                  <strong>Termination is a lifetime-risk exception.</strong>
                  <small>
                    Year 1 debt is already repaid in this case, so DSCR can
                    remain 2.380x even while later project cash flows disappear.
                  </small>
                </span>
              </div>
            </div>
          </div>
        </section>

        <section className="risk-section">
          <Heading
            n="5"
            title="Coverage Beyond DSCR"
            note="Read the full coverage horizon before interpreting a scenario as resilient."
          />
          <div className="coverage-wrap">
            <table className="coverage-table">
              <thead>
                <tr>
                  <th>Scenario</th>
                  <th>Debt Mode</th>
                  <th>Min DSCR</th>
                  <th>LLCR</th>
                  <th>PLCR</th>
                  <th>Debt</th>
                  <th>Additional Debt</th>
                  <th>Incremental CAPEX</th>
                </tr>
              </thead>
              <tbody>
                {SCENARIOS.map((scenario) => {
                  const metric = metrics?.[scenario.id];
                  return (
                    <tr
                      className={metric?.dscr === 0 ? 'zero-row' : ''}
                      key={scenario.id}
                    >
                      <td>{scenario.label}</td>
                      <td>{scenario.mode.replaceAll('_', ' ')}</td>
                      <td>
                        <b>{formatCoverage(metric?.dscr)}</b>
                      </td>
                      <td>{formatCoverage(metric?.llcr)}</td>
                      <td>{formatCoverage(metric?.plcr)}</td>
                      <td>{metric?.debt ?? 'N/A'}</td>
                      <td>{metric?.additionalDebt ?? 'N/A'}</td>
                      <td>{metric?.capex ?? 'N/A'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div className="coverage-boundary">
            <AlertTriangle size={17} />
            <span>
              LLCR and PLCR are shown only where the frozen scenario adapter
              exposes exact fields. No frontend reconstruction is substituted
              for missing source metrics.
            </span>
          </div>
        </section>

        <section className="risk-section">
          <Heading n="6" title="Risk Driver Interpretation" />
          <div className="driver-grid">
            <article>
              <Zap />
              <h3>Energy</h3>
              <p>
                P90 is a standardized screening factor. Validate resource,
                irradiation and operating availability.
              </p>
              <b>→ Engineering validation</b>
            </article>
            <article>
              <BarChart3 />
              <h3>CAPEX</h3>
              <p>
                +15% CAPEX does not create new debt; the incremental ~$1.688m is
                sponsor-funded.
              </p>
              <b>→ Contingency / sponsor support</b>
            </article>
            <article>
              <Timer />
              <h3>Timing</h3>
              <p>
                A one-year COD delay can leave contractual debt service before
                operating CFADS.
              </p>
              <b>→ Construction / debt-start review</b>
            </article>
            <article>
              <CircleAlert />
              <h3>Counterparty</h3>
              <p>
                75% collection and Year 2 termination are standardized stress
                cases, not customer forecasts.
              </p>
              <b>→ Credit / payment security</b>
            </article>
          </div>
        </section>

        <section id="heatmap" className="risk-section">
          <Heading
            n="7"
            title="Portfolio Risk Matrix"
            note="19 economics-ready projects × 9 governed scenarios = 171 unique rows."
          />
          <div className="heatmap-panel">
            <div className="heatmap-scroll">
              <div className="heatmap">
                <div className="heatmap-header">
                  <b>Project</b>
                  {SCENARIOS.map((scenario) => (
                    <b key={scenario.id}>
                      {scenario.label
                        .replace('Interest Rate Shock', 'Rate')
                        .replace('Offtake ', '')
                        .replace(' Generation', '')}
                    </b>
                  ))}
                </div>
                {availableProjects.map((project) => (
                  <div className="heatmap-row" key={project.project_id}>
                    <strong title={project.project_id}>
                      {project.project_name}
                    </strong>
                    {SCENARIOS.map((scenario) => {
                      const value =
                        project.project_id === GO_MALL
                          ? GO_MALL_METRICS[scenario.id].dscr
                          : null;
                      const className =
                        value === null
                          ? 'nd'
                          : value === 0
                            ? 'zero'
                            : value < 1
                              ? 'breach'
                              : value < 1.35
                                ? 'below'
                                : 'safe';
                      return (
                        <button
                          type="button"
                          className={className}
                          title={
                            value === null
                              ? `${project.project_name}, ${scenario.label}: N/D — No Positive Standardized Base Debt or metric payload unavailable.`
                              : `${project.project_name}, ${scenario.label}, minimum DSCR ${formatCoverage(value)}, ${SCENARIOS.find((item) => item.id === scenario.id)?.mode}`
                          }
                          key={`${project.project_id}-${scenario.id}`}
                          aria-label={`${project.project_name}, ${scenario.label}, ${value === null ? 'N/D' : formatCoverage(value)}`}
                        >
                          {value === null ? 'N/D' : formatCoverage(value)}
                        </button>
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
            <div className="heatmap-legend">
              <span>
                <i className="safe" /> ≥1.35x
              </span>
              <span>
                <i className="below" /> 1.00–1.35x
              </span>
              <span>
                <i className="breach" /> &lt;1.00x
              </span>
              <span>
                <i className="zero" /> 0.00x
              </span>
              <span>
                <i className="nd" /> N/D = no positive standardized base debt /
                unavailable
              </span>
            </div>
          </div>
        </section>

        <section className="risk-section">
          <Heading
            n="8"
            title="Portfolio Risk Segmentation"
            note="Stress resilience is not an investment ranking."
          />
          <div className="segmentation-grid">
            <div className="segmentation-card">
              <div className="seg-ring">
                <strong>14</strong>
                <small>
                  Positive
                  <br />
                  base debt
                </small>
              </div>
              <b>74%</b>
              <span>
                economics-ready cases with positive standardized supportable
                debt
              </span>
            </div>
            <div className="segmentation-card amber">
              <div className="seg-ring">
                <strong>5</strong>
                <small>
                  No positive
                  <br />
                  base debt
                </small>
              </div>
              <b>26%</b>
              <span>
                show N/D in the scenario matrix; not conventional debt-service
                cases
              </span>
            </div>
            <div className="segmentation-copy">
              <h3>Interpretation</h3>
              <p>
                <Check /> Base feasibility must be separated from stress
                resilience.
              </p>
              <p>
                <Check /> N/D is not the same as a 0.000x debt-service breach.
              </p>
              <p>
                <Check /> Arisudhana remains outside the 171 rows because its
                technical input is blocked.
              </p>
            </div>
          </div>
        </section>

        <section className="risk-section">
          <Heading n="9" title="Model / Claim Boundaries" />
          <div className="claim-grid">
            <div>
              <h3>WE CAN CLAIM</h3>
              <p>
                <Check /> Deterministic governed scenarios
              </p>
              <p>
                <Check /> Contractual debt treatment
              </p>
              <p>
                <Check /> Stressed DSCR / LLCR / PLCR where source-backed
              </p>
              <p>
                <Check /> Scenario semantics and diligence actions
              </p>
            </div>
            <div className="cannot">
              <h3>WE CANNOT CLAIM</h3>
              <p>
                <X /> Scenario probability or likelihood
              </p>
              <p>
                <X /> VaR, expected shortfall or Monte Carlo
              </p>
              <p>
                <X /> Actual customer default expectation
              </p>
              <p>
                <X /> Bank-approved stress or investment approval
              </p>
              <p>
                <X /> Bankable P90 or lender commitment
              </p>
            </div>
            <div className="boundary-strip">
              <span>
                SCENARIOS
                <br />
                <b>DETERMINISTIC</b>
              </span>
              <span>
                DEBT
                <br />
                <b>CONTRACTUAL</b>
              </span>
              <span>
                P90
                <br />
                <b>SCREENING ONLY</b>
              </span>
              <span>
                TRANSACTION EVIDENCE
                <br />
                <b>OPEN</b>
              </span>
            </div>
          </div>
        </section>

        <section className="risk-section">
          <Heading
            n="10"
            title="From Stress Results to Diligence"
            note="Each risk flag points to a concrete next evidence request."
          />
          <div className="handoff-grid">
            <div className="handoff-step">
              <Zap />
              <b>Energy stress</b>
              <span>Engineering validation</span>
            </div>
            <ArrowRight className="handoff-arrow" />
            <div className="handoff-step">
              <Timer />
              <b>COD stress</b>
              <span>Construction / debt-start review</span>
            </div>
            <ArrowRight className="handoff-arrow" />
            <div className="handoff-step">
              <CircleAlert />
              <b>Nonpayment</b>
              <span>Counterparty credit / payment security</span>
            </div>
            <ArrowRight className="handoff-arrow" />
            <div className="handoff-step">
              <ShieldAlert />
              <b>Termination</b>
              <span>Compensation / replacement offtaker</span>
            </div>
            <Link
              className="handoff-cta"
              href={`/diligence?project=${GO_MALL}`}
            >
              Continue to Diligence <ArrowRight size={15} />
            </Link>
          </div>
        </section>

        <section className="risk-takeaway">
          <Image
            src="/assets/overview/footer-solar-texture.webp"
            alt="Solar texture"
            fill
            sizes="45vw"
          />
          <div>
            <span className="risk-index gold">11</span>
            <p>RECRUITER TAKEAWAY</p>
            <h2>
              A downside model is credible only when the debt contract stays
              visible.
            </h2>
            <p>
              VietGreen stresses energy, CAPEX, rates, timing and offtaker
              performance without letting principal magically re-sculpt itself
              back to comfort. The output is a governed risk conversation and a
              clear diligence agenda.
            </p>
            <ul>
              <li>9 explicit scenario definitions</li>
              <li>Contractual schedule preservation</li>
              <li>True 0x separated from N/A and N/D</li>
              <li>Stress results translated into diligence actions</li>
            </ul>
          </div>
        </section>
      </div>
      <footer className="risk-footer">
        <span>Model: V5.1.3 (Frozen)</span>
        <span>Data as of: 31 Dec 2024</span>
        <span>
          <FileCheck2 size={14} /> Evidence: OPEN
        </span>
        <span>This page: RISK_SCENARIOS ⓘ</span>
      </footer>
    </main>
  );
}
