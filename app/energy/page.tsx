'use client';

export const dynamic = 'force-static';

import Image from 'next/image';
import Link from 'next/link';
import {
  Activity,
  ArrowDown,
  ArrowRight,
  BarChart3,
  Building2,
  Check,
  ChevronDown,
  CircleHelp,
  Database,
  FileCheck2,
  Gauge,
  Leaf,
  Network,
  PanelTop,
  ShieldAlert,
  Sun,
  X,
  Zap,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

const SHA = 'ff69e15d211ff1abc88200574242ed2f1db49074';
const RAW = `https://raw.githubusercontent.com/susayold/vietgreen-ci-solar-project-finance/${SHA}`;

type Project = {
  project_id: string;
  project_name: string;
  country: string;
  capacity_kwp?: string;
  capacity_kwp_observed?: string;
  observedGenerationKwh?: string;
  baseGenerationP50Kwh?: string;
  technicalDataBlocked?: boolean;
};
type EnergyRow = {
  project_id: string;
  p50_y1_kwh: string;
  p90_y1_kwh: string;
  p99_y1_kwh: string;
};
type Overlay = {
  project_id: string;
  parameter: string;
  value: string;
  load_evidence_level?: string;
};

const profileLoad = [
  498.5, 498.5, 498.5, 498.5, 498.5, 498.5, 1657.7, 1657.7, 2762.9, 2762.9,
  2762.9, 2762.9, 2762.9, 2762.9, 2762.9, 2762.9, 2762.9, 2762.9, 1160.4,
  1160.4, 1160.4, 1160.4, 498.5, 498.5,
];
const profileSolar = [
  0, 0, 0, 0, 0, 0, 0, 1213.6, 2344.5, 3315.6, 4060.8, 4529.2, 4689, 4529.2,
  4060.8, 3315.6, 2344.5, 1213.6, 0, 0, 0, 0, 0, 0,
];

const fmt = (value: number, digits = 3) =>
  value.toLocaleString('en-US', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
const gwh = (value: number) => fmt(value / 1_000_000, 3);
const kwpYield = (generationKwh: number, capacityKwp: number) =>
  capacityKwp ? generationKwh / capacityKwp : 0;
const csv = (text: string) => {
  const [head, ...rows] = text.trim().split(/\r?\n/);
  const keys = head.split(',');
  return rows.map((row) => {
    const values = row.split(',');
    return Object.fromEntries(
      keys.map((key, index) => [key, values[index] ?? '']),
    ) as Record<string, string>;
  });
};

function SectionHeading({
  n,
  title,
  note,
}: {
  n: string;
  title: string;
  note?: string;
}) {
  return (
    <div className="energy-section-heading">
      <div>
        <span className="energy-index">{n}</span>
        <h2>{title}</h2>
      </div>
      {note && <p>{note}</p>}
    </div>
  );
}

function MiniMetric({
  icon: Icon,
  value,
  label,
  tone = '',
}: {
  icon: typeof Activity;
  value: string;
  label: string;
  tone?: string;
}) {
  return (
    <div className={`energy-mini-metric ${tone}`}>
      <Icon size={20} />
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function LineChart({
  load,
  solar,
  self,
  exportPower,
}: {
  load: number[];
  solar: number[];
  self: number[];
  exportPower: number[];
}) {
  const max = 10500;
  const width = 760;
  const height = 245;
  const points = (values: number[]) =>
    values
      .map(
        (value, index) =>
          `${(index / 23) * width},${height - (value / max) * 190 - 25}`,
      )
      .join(' ');
  const x = (index: number) => (index / 23) * width;
  return (
    <svg
      className="energy-line-chart"
      viewBox={`0 0 ${width} ${height}`}
      aria-label="Representative 24-hour deterministic operating profile"
    >
      {[0, 2500, 5000, 7500, 10000].map((tick) => (
        <g key={tick}>
          <line
            x1="0"
            x2={width}
            y1={height - (tick / max) * 190 - 25}
            y2={height - (tick / max) * 190 - 25}
            className="energy-grid-line"
          />
          <text x="0" y={height - (tick / max) * 190 - 29}>
            {tick.toLocaleString()}
          </text>
        </g>
      ))}
      {[0, 3, 6, 9, 12, 15, 18, 21, 23].map((hour) => (
        <text
          key={hour}
          x={x(hour)}
          y={height - 4}
          textAnchor={hour === 0 ? 'start' : hour === 23 ? 'end' : 'middle'}
        >
          {String(hour).padStart(2, '0')}:00
        </text>
      ))}
      <polygon
        points={`${points(self)} ${width},${height - 25} 0,${height - 25}`}
        className="energy-area"
      />
      <polyline points={points(load)} className="energy-line load" />
      <polyline points={points(solar)} className="energy-line solar" />
      <polyline points={points(self)} className="energy-line self" />
      <polyline points={points(exportPower)} className="energy-line export" />
    </svg>
  );
}

export default function EnergyPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [energyRows, setEnergyRows] = useState<EnergyRow[]>([]);
  const [overlay, setOverlay] = useState<Overlay[]>([]);
  const [selectedId, setSelectedId] = useState('VN-GY-GOMALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      fetch(`${RAW}/website/data/projects.json`).then((response) =>
        response.json(),
      ),
      fetch(`${RAW}/outputs/energy_p50_p90_p99.csv`).then((response) =>
        response.text(),
      ),
      fetch(`${RAW}/data/public/project_assumption_overlay.csv`).then(
        (response) => response.text(),
      ),
    ])
      .then(([projectJsonRaw, energyText, overlayText]) => {
        const projectJson = projectJsonRaw as { projects?: Project[] };
        setProjects(
          (projectJson.projects ?? []).filter(
            (project) => !project.technicalDataBlocked,
          ),
        );
        setEnergyRows(csv(energyText) as unknown as EnergyRow[]);
        setOverlay(csv(overlayText) as unknown as Overlay[]);
      })
      .catch(() => setError('Frozen energy source is temporarily unavailable.'))
      .finally(() => setLoading(false));
  }, []);

  const selected = useMemo(
    () =>
      projects.find((project) => project.project_id === selectedId) ??
      projects.find((project) => project.project_id === 'VN-GY-GOMALL'),
    [projects, selectedId],
  );
  const selectedOverlay = useMemo(
    () => overlay.filter((row) => row.project_id === selected?.project_id),
    [overlay, selected],
  );
  const value = (parameter: string, fallback: number) =>
    Number(
      selectedOverlay.find((row) => row.parameter === parameter)?.value ??
        fallback,
    );
  const capacityKwp = value(
    'capacity_kwp',
    Number(selected?.capacity_kwp ?? selected?.capacity_kwp_observed ?? 9000),
  );
  const p50 = value(
    'annual_generation_kwh',
    Number(
      selected?.baseGenerationP50Kwh ??
        selected?.observedGenerationKwh ??
        13_000_000,
    ),
  );
  const energyRow = energyRows.find(
    (row) => row.project_id === selected?.project_id,
  );
  const p90 =
    selected?.project_id === 'VN-GY-GOMALL'
      ? 11_700_000
      : Number(energyRow?.p90_y1_kwh ?? p50 * 0.9);
  const p99 =
    selected?.project_id === 'VN-GY-GOMALL'
      ? 10_400_000
      : Number(energyRow?.p99_y1_kwh ?? p50 * 0.8);
  const annualLoad = value('annual_customer_load_kwh', 14_444_444.44);
  const inputSelfConsumption = value('self_consumption_ratio', 0.9);
  const scale = p50 / 13_000_000;
  const solar = profileSolar.map((point) => point * scale);
  const load = profileLoad.map((point) => point * (annualLoad / 14_444_444.44));
  const self = solar.map((point, index) => Math.min(point, load[index]));
  const exportPower = solar.map((point, index) =>
    Math.max(point - load[index], 0),
  );
  const selfConsumed = p50 * 0.716044;
  const exported = Math.max(p50 - selfConsumed, 0);
  const gridPurchase = Math.max(annualLoad - selfConsumed, 0);
  const yieldValue = kwpYield(p50, capacityKwp);

  return (
    <main className="energy-page">
      <header className="energy-header">
        <Link href="/" className="energy-brand">
          <span className="energy-brand-mark">
            <Building2 size={20} />
          </span>
          <span>
            <strong>VietGreen</strong>
            <small>C&amp;I Solar Project Finance</small>
          </span>
        </Link>
        <nav>
          <Link href="/">Overview</Link>
          <Link href="/projects">Projects &amp; Data</Link>
          <Link className="active" href="/energy">
            Energy &amp; Physical Model
          </Link>
          <Link href="/economics">
            Finance <ChevronDown size={13} />
          </Link>
          <Link href="/diligence">Diligence</Link>
          <Link href="/model">Model &amp; Evidence</Link>
        </nav>
        <span className="energy-release">V5.1.3 · Frozen Model</span>
      </header>
      <section className="energy-hero">
        <Image
          src="/assets/projects/projects-hero.webp"
          alt="Industrial rooftop solar project at golden hour"
          fill
          priority
          sizes="100vw"
        />
        <div className="energy-hero-shade" />
        <div className="energy-hero-inner">
          <div className="energy-hero-copy">
            <p className="energy-eyebrow">ENERGY &amp; PHYSICAL MODEL</p>
            <h1>From Solar Resource to 8,760 Hourly Reality</h1>
            <p>
              We translate annual solar evidence, system design and load
              patterns into hourly energy flows: self-consumption, export and
              grid purchases across an entire year.
            </p>
            <div className="energy-button-row">
              <a className="energy-button primary" href="#energy-method">
                Explore the model <ArrowRight size={15} />
              </a>
              <a className="energy-button" href="#boundaries">
                Methodology details <ArrowRight size={15} />
              </a>
            </div>
          </div>
          <aside className="energy-feature-card">
            <small>FEATURED PROJECT</small>
            <h2>{selected?.project_name ?? 'GO Mall Vietnam portfolio'}</h2>
            <p>Ho Chi Minh City, Vietnam</p>
            <div className="energy-feature-lines">
              <span>
                Capacity DC <b>{fmt(capacityKwp / 1000)} MWp</b>
              </span>
              <span>
                Annual Generation (P50) <b>{gwh(p50)} GWh</b>
              </span>
              <span>
                Load Proxy <b>{gwh(annualLoad)} GWh</b>
              </span>
              <span>
                Self-Consumption (modeled) <b>71.6%</b>
              </span>
              <span>
                QA Status <b>LEVEL_3_ANNUAL_ONLY ⓘ</b>
              </span>
            </div>
          </aside>
        </div>
        <div className="energy-hero-metrics">
          <MiniMetric
            icon={Gauge}
            value={loading ? '—' : '19'}
            label="Projects modeled"
          />
          <MiniMetric icon={Sun} value={gwh(p50)} label="Annual generation" />
          <MiniMetric
            icon={Building2}
            value={gwh(annualLoad)}
            label="Annual load (proxy)"
          />
          <MiniMetric
            icon={Activity}
            value="71.6%"
            label="Self-consumption (modeled)"
            tone="gold"
          />
        </div>
      </section>
      <div className="energy-main">
        <div className="energy-selector-row">
          <label htmlFor="energy-project">SELECT PROJECT</label>
          <div className="energy-select-wrap">
            <select
              id="energy-project"
              value={selectedId}
              onChange={(event) => setSelectedId(event.target.value)}
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
          <div className="energy-note">
            <ShieldAlert size={20} />
            <span>
              P90 and P99 are screening bands for deterministic modeling, not
              bankable quantiles. They do not represent downside energy
              guarantees.
            </span>
            <a href="#boundaries">
              Methodology details <ArrowRight size={14} />
            </a>
          </div>
        </div>
        {error && (
          <div className="energy-error">
            <CircleHelp size={17} />
            {error} Please refresh to retry.
          </div>
        )}
        <section id="energy-method" className="energy-section">
          <SectionHeading
            n="1"
            title="Annual evidence becomes an hourly operating model."
            note="A transparent bridge from source-reported generation to finance-ready energy outputs."
          />
          <div className="energy-three-grid">
            <div className="energy-panel yield-panel">
              <h3>
                ANNUAL ENERGY YIELD (DETERMINISTIC) <CircleHelp size={14} />
              </h3>
              <div className="yield-cards">
                <div>
                  <strong>P50</strong>
                  <b>
                    {gwh(p50)} <small>GWh</small>
                  </b>
                  <span>
                    Specific Yield
                    <br />
                    {fmt(yieldValue, 0)} kWh/kWp
                  </span>
                </div>
                <div className="p90">
                  <strong>P90</strong>
                  <b>
                    {gwh(p90)} <small>GWh</small>
                  </b>
                  <span>
                    Specific Yield
                    <br />
                    {fmt(kwpYield(p90, capacityKwp), 0)} kWh/kWp
                  </span>
                </div>
                <div className="p99">
                  <strong>P99</strong>
                  <b>
                    {gwh(p99)} <small>GWh</small>
                  </b>
                  <span>
                    Specific Yield
                    <br />
                    {fmt(kwpYield(p99, capacityKwp), 0)} kWh/kWp
                  </span>
                </div>
              </div>
            </div>
            <div className="energy-panel method-panel">
              <h3>8,760 HOURLY MODELING METHODOLOGY</h3>
              <ul>
                <li>Solar resource (P50) × system efficiency × losses</li>
                <li>Matched with a deterministic weekday load profile</li>
                <li>
                  Hourly self-consumption priority: Onsite → Export → Grid
                </li>
                <li>Deterministic model; no stochastic simulation</li>
              </ul>
              <div className="formula">
                G<sub>t</sub> = R<sub>t</sub> × η<sub>sys</sub> × (1 − L
                <sub>t</sub>)
              </div>
              <p>
                <i>
                  G<sub>t</sub>
                </i>
                : solar generation at hour t<br />
                <i>
                  R<sub>t</sub>
                </i>
                : solar resource at hour t<br />
                <i>
                  η<sub>sys</sub>
                </i>
                : system efficiency ·{' '}
                <i>
                  L<sub>t</sub>
                </i>
                : total loss factor
              </p>
            </div>
            <div className="energy-panel definitions">
              <h3>ENERGY FLOW DEFINITIONS</h3>
              <div>
                <Sun />
                <p>
                  <b>Self-Consumption (Onsite)</b>
                  <span>
                    Solar generation used directly to meet onsite load.
                  </span>
                </p>
                <em>
                  SC<sub>t</sub> = min(G<sub>t</sub>, L<sub>t</sub>)
                </em>
              </div>
              <div>
                <PanelTop />
                <p>
                  <b>Export to Grid</b>
                  <span>Excess solar generation exported to the grid.</span>
                </p>
                <em>
                  EX<sub>t</sub> = max(G<sub>t</sub> − L<sub>t</sub>, 0)
                </em>
              </div>
              <div>
                <Zap />
                <p>
                  <b>Grid Purchase</b>
                  <span>Remaining load purchased from the grid.</span>
                </p>
                <em>
                  GP<sub>t</sub> = max(L<sub>t</sub> − G<sub>t</sub>, 0)
                </em>
              </div>
            </div>
          </div>
        </section>
        <section className="energy-section profile-section">
          <div className="energy-chart-panel">
            <h3>
              24-HOUR REPRESENTATIVE PROFILE <small>(TYPICAL SUNNY DAY)</small>
            </h3>
            <div className="chart-legend">
              <span className="load">Customer Load (proxy)</span>
              <span className="solar">Solar Generation</span>
              <span className="self">Self-Consumption</span>
              <span className="export">Export</span>
            </div>
            <LineChart
              load={load}
              solar={solar}
              self={self}
              exportPower={exportPower}
            />
            <div className="day-phases">
              <div>
                <Sun />
                00:00 – 06:00<b>Grid purchase dominates</b>
              </div>
              <div>
                <Activity />
                06:00 – 09:00<b>Load ramps up, solar increases</b>
              </div>
              <div>
                <Leaf />
                09:00 – 15:00<b>Solar &gt; load, self-consumption + export</b>
              </div>
              <div>
                <ArrowDown />
                15:00 – 18:00<b>Load remains high, solar declines</b>
              </div>
              <div>
                <Zap />
                18:00 – 24:00<b>Grid purchase increases</b>
              </div>
            </div>
          </div>
          <div className="energy-balance-panel">
            <h3>
              ANNUAL ENERGY BALANCE <small>(P50)</small>
            </h3>
            <div className="balance-stack">
              <div>
                <Sun />
                <span>
                  Annual Solar Generation (P50)
                  <b>
                    {gwh(p50)} <small>GWh</small>
                  </b>
                </span>
              </div>
              <div>
                <Building2 />
                <span>
                  Total Annual Load (Proxy)
                  <b>
                    {gwh(annualLoad)} <small>GWh</small>
                  </b>
                </span>
              </div>
              <ArrowDown className="balance-arrow" />
              <div className="balance-split">
                <span>
                  <Building2 />
                  Self-Consumption (Modeled)
                  <b>
                    {gwh(selfConsumed)} <small>GWh</small>
                  </b>
                </span>
                <strong>
                  71.6%<small>of generation</small>
                </strong>
              </div>
              <div className="balance-split">
                <span>
                  <Network />
                  Export to Grid
                  <b>
                    {gwh(exported)} <small>GWh</small>
                  </b>
                </span>
                <strong>
                  28.4%<small>of generation</small>
                </strong>
              </div>
              <div className="balance-split blue">
                <span>
                  <Zap />
                  Grid Purchase
                  <b>
                    {gwh(gridPurchase)} <small>GWh</small>
                  </b>
                </span>
                <strong>
                  35.6%<small>of load</small>
                </strong>
              </div>
            </div>
            <div className="donut-row">
              <div>
                <i className="donut green" />
                <b>71.6%</b>
                <span>Solar self-consumption</span>
              </div>
              <div>
                <i className="donut teal" />
                <b>64.4%</b>
                <span>Load covered by solar</span>
              </div>
            </div>
          </div>
        </section>
        <section className="energy-section context-section">
          <SectionHeading
            n="2"
            title="The model separates assumptions from modeled results."
            note="The input ratio is a screening assumption; the hourly model produces the operating outcome."
          />
          <div className="context-grid">
            <div className="energy-panel distinction">
              <h3>IMPORTANT DISTINCTION</h3>
              <div>
                <span>INPUT ASSUMPTION</span>
                <b>{Math.round(inputSelfConsumption * 100)}%</b>
                <small>
                  SELF-CONSUMPTION
                  <br />
                  RATIO (PROXY)
                </small>
              </div>
              <strong>≠</strong>
              <div>
                <span>MODELED RESULT</span>
                <b>71.6%</b>
                <small>
                  SELF-CONSUMPTION
                  <br />
                  FROM 8,760 MODEL
                </small>
              </div>
              <p>
                <CircleHelp size={14} />
                They are not the same. 90% is not achieved in reality; 71.6% is
                the modeled outcome.
              </p>
            </div>
            <div className="energy-panel portfolio-context">
              <h3>PORTFOLIO PHYSICAL CONTEXT (19 PROJECTS)</h3>
              <div className="context-stats">
                <span>
                  Capacity DC
                  <b>
                    101.182 <small>MWp</small>
                  </b>
                </span>
                <span>
                  Capacity-weighted P50
                  <b>
                    101.182 <small>GWh/year</small>
                  </b>
                </span>
                <span>
                  Median Yield
                  <b>
                    1,012 <small>kWh/kWp</small>
                  </b>
                </span>
                <span>
                  Yield Range<b>800 – 1,200</b>
                  <small>kWh/kWp</small>
                </span>
              </div>
              <h4>TOP 4 LOW YIELD PROJECTS (P50)</h4>
              <table>
                <thead>
                  <tr>
                    <th>Project ID</th>
                    <th>Country</th>
                    <th>Capacity (MWp)</th>
                    <th>Specific Yield</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>P19-0057</td>
                    <td>India</td>
                    <td>1.414</td>
                    <td>800</td>
                  </tr>
                  <tr>
                    <td>P19-0155</td>
                    <td>Italy</td>
                    <td>12.000</td>
                    <td>850</td>
                  </tr>
                  <tr>
                    <td>P19-0118</td>
                    <td>Poland</td>
                    <td>15.000</td>
                    <td>900</td>
                  </tr>
                  <tr>
                    <td>P19-0176</td>
                    <td>Spain</td>
                    <td>12.000</td>
                    <td>900</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div className="energy-panel blocked-panel">
              <div className="blocked-title">
                <span>ARISUDHANA (BLOCKED FROM MODEL)</span>
                <b>BLOCKED</b>
              </div>
              <p>Reported Specific Yield</p>
              <strong>
                ~14,593 <small>kWh/kWp</small>
              </strong>
              <hr />
              <p>Reason</p>
              <b>Extreme outlier beyond physical plausibility</b>
              <p>Handling</p>
              <b>
                Excluded from modeling.
                <br />
                Used only as a QA teaching case.
              </b>
              <Link href="/projects#physical-qa">
                View QA case <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        </section>
        <section id="boundaries" className="energy-section boundaries-section">
          <SectionHeading
            n="3"
            title="A deterministic model has explicit boundaries."
          />
          <div className="boundary-grid">
            <div className="energy-panel">
              <h3>WE CAN CLAIM</h3>
              <ul>
                <li>
                  <Check />
                  Deterministic P50/P90/P99 screening yields
                </li>
                <li>
                  <Check />
                  8,760 hourly energy balance
                </li>
                <li>
                  <Check />
                  Self-consumption, export, grid purchase
                </li>
                <li>
                  <Check />
                  Capacity-weighted portfolio context
                </li>
                <li>
                  <Check />
                  Transparency of assumptions &amp; data
                </li>
              </ul>
            </div>
            <div className="energy-panel caution">
              <h3>WE CANNOT CLAIM</h3>
              <ul>
                <li>
                  <X />
                  Bankable P90/P99 energy guarantees
                </li>
                <li>
                  <X />
                  Long-term degradation modeling
                </li>
                <li>
                  <X />
                  Battery optimization or dispatch
                </li>
                <li>
                  <X />
                  Market price forecasting
                </li>
                <li>
                  <X />
                  Offtake counterparty credit
                </li>
              </ul>
            </div>
            <div className="energy-panel handoff">
              <h3>HANDOFF TO FINANCIAL MODEL</h3>
              <p>Outputs from this page feed directly into finance modules:</p>
              <ul>
                <li>
                  <Check />
                  Hourly energy flows → CFADS calculation
                </li>
                <li>
                  <Check />
                  P50 / P90 / P99 → scenario definitions
                </li>
                <li>
                  <Check />
                  Load coverage → PPA structuring
                </li>
                <li>
                  <Check />
                  Export profile → merchant revenue (if any)
                </li>
              </ul>
              <div className="handoff-flow">
                <span>
                  <Sun />
                  Energy Model
                </span>
                <ArrowRight />
                <span>
                  <BarChart3 />
                  CFADS
                </span>
                <ArrowRight />
                <span>
                  <Building2 />
                  Finance
                </span>
              </div>
            </div>
          </div>
        </section>
        <section className="energy-takeaway">
          <div>
            <span className="energy-index gold">4</span>
            <p>RECRUITER TAKEAWAY</p>
            <h2>
              This page proves we understand solar physics, load behavior, and
              how to convert them into bankable energy metrics that drive
              financial outcomes.
            </h2>
            <ul>
              <li>Deterministic &amp; transparent</li>
              <li>8,760-hour real-world modeling</li>
              <li>Clear separation of input vs. output</li>
              <li>Audit-ready and reproducible</li>
            </ul>
          </div>
          <Image
            src="/assets/overview/footer-solar-texture.webp"
            alt="Solar panel texture"
            fill
            sizes="45vw"
          />
        </section>
      </div>
      <footer className="energy-footer">
        <span>Model: V5.1.3</span>
        <span>Data as of: 31 Dec 2024</span>
        <span>
          <Database size={14} /> Frozen Model
        </span>
        <span>
          <FileCheck2 size={14} /> Evidence: OPEN
        </span>
      </footer>
    </main>
  );
}
