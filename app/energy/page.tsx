'use client';
import SiteHeader from '@/lib/site-header';

import Image from '@/lib/site-image';
import Link from '@/lib/site-link';
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
import { loadWebsiteData } from '@/lib/data';

type Project = {
  project_id: string;
  project_name: string;
  country: string;
  capacity_kwp?: string;
  capacity_kwp_observed?: string;
  observedGenerationKwh?: string;
  baseGenerationP50Kwh?: string;
  technicalDataBlocked?: boolean;
  capacityMw?: number;
};
type EnergyProject = {
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
  representativeDay: Array<{
    loadKw: number;
    solarKw: number;
    selfConsumedKw: number;
    exportKw: number;
    gridPurchaseKw: number;
  }>;
};

const fmt = (value: number, digits = 3) =>
  value.toLocaleString('en-US', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
const gwh = (value: number) => fmt(value / 1_000_000, 3);
const kwpYield = (generationKwh: number, capacityKwp: number) =>
  capacityKwp ? generationKwh / capacityKwp : 0;

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
  const max = Math.max(1, ...load, ...solar, ...self, ...exportPower)*1.05;
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
      {[0, .25, .5, .75, 1].map(f => Math.round(f*max)).map((tick) => (
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
  const [energyRows, setEnergyRows] = useState<EnergyProject[]>([]);
  const [selectedId, setSelectedId] = useState(() =>
    typeof window === 'undefined'
      ? 'VN-GY-GOMALL'
      : new URLSearchParams(window.location.search).get('project') ??
        'VN-GY-GOMALL',
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      loadWebsiteData<{ projects?: Project[] }>('projects'),
      loadWebsiteData<{ projects?: EnergyProject[] }>('energy'),
    ])
      .then(([projectJson, energyJson]) => {
        setProjects(
          (projectJson.projects ?? []).filter(
            (project) => !project.technicalDataBlocked,
          ),
        );
        setEnergyRows(energyJson.projects ?? []);
      })
      .catch(() => setError('Energy data unavailable for this release.'))
      .finally(() => setLoading(false));
  }, []);

  const selected = useMemo(
    () =>
      projects.find((project) => project.project_id === selectedId) ??
      projects.find((project) => project.project_id === 'VN-GY-GOMALL'),
    [projects, selectedId],
  );
  const selectedEnergy = energyRows.find(
    (row) => row.projectId === selected?.project_id,
  );
  const capacityKwp =
    (selectedEnergy?.capacityMw ?? selected?.capacityMw ?? 0) * 1000;
  const p50 = (selectedEnergy?.p50Gwh ?? 0) * 1_000_000;
  const p90 = (selectedEnergy?.p90Gwh ?? 0) * 1_000_000;
  const p99 = (selectedEnergy?.p99Gwh ?? 0) * 1_000_000;
  const annualLoad = (selectedEnergy?.annualLoadGwh ?? 0) * 1_000_000;
  const portfolio = energyRows.filter(row => row.capacityMw > 0).map(row => ({
    ...row, yield: row.p50Gwh * 1000 / row.capacityMw,
    country: projects.find(project => project.project_id === row.projectId)?.country ?? 'Not available',
  })).sort((a, b) => a.yield - b.yield);
  const totalCapacity = portfolio.reduce((sum, row) => sum + row.capacityMw, 0);
  const totalGeneration = portfolio.reduce((sum, row) => sum + row.p50Gwh, 0);
  const medianYield = portfolio.length ? (portfolio[Math.floor((portfolio.length - 1) / 2)].yield + portfolio[Math.floor(portfolio.length / 2)].yield) / 2 : 0;
  const profile = selectedEnergy?.representativeDay ?? [];
  const solar = profile.map((point) => point.solarKw);
  const load = profile.map((point) => point.loadKw);
  const self = profile.map((point) => point.selfConsumedKw);
  const exportPower = profile.map((point) => point.exportKw);
  const selfConsumed = (selectedEnergy?.selfConsumedGwh ?? 0) * 1_000_000;
  const exported = (selectedEnergy?.exportedGwh ?? 0) * 1_000_000;
  const gridPurchase = (selectedEnergy?.gridPurchaseGwh ?? 0) * 1_000_000;
  const yieldValue = kwpYield(p50, capacityKwp);

  return (
    <main className="energy-page">
      <SiteHeader active="/energy" />
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
            <h1>From Annual Solar Evidence to 8,760 Hourly Flows</h1>
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
            <p>{selected?.country ?? 'Loading project'}</p>
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
                Self-Consumption (modeled){' '}
                <b>{fmt((selectedEnergy?.selfConsumptionShare ?? 0) * 100, 1)}%</b>
              </span>
              <span>
                Load Evidence <b>{selectedEnergy?.loadEvidenceLevel ?? 'NOT AVAILABLE'} ⓘ</b>
              </span>
            </div>
          </aside>
        </div>
        <div className="energy-hero-metrics">
          <MiniMetric
            icon={Gauge}
            value={loading ? '—' : String(energyRows.length)}
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
            value={`${fmt((selectedEnergy?.selfConsumptionShare ?? 0) * 100, 1)}%`}
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
              onChange={(event) => {
                const value = event.target.value;
                setSelectedId(value);
                window.history.replaceState(
                  null,
                  '',
                  `${window.location.pathname}?project=${encodeURIComponent(value)}`,
                );
              }}
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
                <li>Annual P50 generation distributed across a normalized solar profile</li>
                <li>Matched with a deterministic weekday load profile</li>
                <li>
                  Hourly self-consumption priority: Onsite → Export → Grid
                </li>
                <li>Deterministic model; no stochastic simulation</li>
              </ul>
              <div className="formula">
                G<sub>t</sub> = E<sub>P50</sub> × w<sub>t</sub> / Σw
              </div>
              <p>
                <i>
                  G<sub>t</sub>
                </i>
                : solar generation at hour t<br />
                E<sub>P50</sub>: annual source-based generation<br />
                w<sub>t</sub>: deterministic hourly solar weight<br />
                Annual load is distributed using weekday and daytime weights; the profile is not measured telemetry.
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
              24-HOUR MODEL PROFILE <small>(1 JAN 2027 · kW · NOT MEASURED TELEMETRY)</small>
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
                  {fmt((selectedEnergy?.selfConsumptionShare ?? 0) * 100, 1)}%
                  <small>of generation</small>
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
                  {fmt((p50 ? exported / p50 : 0) * 100, 1)}%
                  <small>of generation</small>
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
                  {fmt((annualLoad ? gridPurchase / annualLoad : 0) * 100, 1)}%
                  <small>of load</small>
                </strong>
              </div>
            </div>
            <div className="donut-row">
              <div>
                <i className="donut green" />
                <b>{fmt((selectedEnergy?.selfConsumptionShare ?? 0) * 100, 1)}%</b>
                <span>Solar self-consumption</span>
              </div>
              <div>
                <i className="donut teal" />
                <b>{fmt((selectedEnergy?.solarCoverageShare ?? 0) * 100, 1)}%</b>
                <span>Load covered by solar</span>
              </div>
            </div>
          </div>
        </section>
        <section className="energy-section context-section">
          <SectionHeading
            n="2"
            title="Two different measures of solar use"
            note="Both are modeled results: one uses generation as its denominator, the other uses annual load."
          />
          <div className="context-grid">
            <div className="energy-panel distinction">
              <h3>IMPORTANT DISTINCTION</h3>
              <div>
                <span>LOAD COVERED BY SOLAR</span>
                <b>{fmt((selectedEnergy?.solarCoverageShare ?? 0) * 100, 1)}%</b>
                <small>
                  SELF-CONSUMED ENERGY
                  <br />
                  DIVIDED BY ANNUAL LOAD
                </small>
              </div>
              <strong>≠</strong>
              <div>
                <span>MODELED RESULT</span>
                  <b>{fmt((selectedEnergy?.selfConsumptionShare ?? 0) * 100, 1)}%</b>
                <small>
                  SELF-CONSUMPTION
                  <br />
                  FROM 8,760 MODEL
                </small>
              </div>
              <p>
                <CircleHelp size={14} />
                The displayed ratio is generated from the selected project data;
                it is not a transaction or production guarantee.
              </p>
            </div>
            <div className="energy-panel portfolio-context">
              <h3>PORTFOLIO PHYSICAL CONTEXT ({portfolio.length} PROJECTS)</h3>
              <div className="context-stats">
                <span>
                  Capacity DC
                  <b>
                    {fmt(totalCapacity)} <small>MWp</small>
                  </b>
                </span>
                <span>
                  Total P50 Generation
                  <b>
                    {fmt(totalGeneration)} <small>GWh/year</small>
                  </b>
                </span>
                <span>
                  Median Yield
                  <b>
                    {fmt(medianYield, 0)} <small>kWh/kWp</small>
                  </b>
                </span>
                <span>
                  Yield Range<b>{fmt(portfolio[0]?.yield ?? 0, 0)} – {fmt(portfolio.at(-1)?.yield ?? 0, 0)}</b>
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
                  {portfolio.slice(0, 4).map(row => <tr key={row.projectId}>
                    <td>{row.projectId}</td><td>{row.country}</td>
                    <td>{fmt(row.capacityMw)}</td><td>{fmt(row.yield, 0)}</td>
                  </tr>)}
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
                  Verified long-term degradation performance
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
            <p>KEY TAKEAWAY</p>
            <h2>
              This page proves we understand solar physics, load behavior, and
              how to convert them into bankable energy metrics that drive
              financial outcomes.
            </h2>
            <ul>
              <li>Deterministic &amp; transparent</li>
              <li>8,760-hour modeled profiles</li>
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
        <span>Solar Project Finance</span>
        <span>Public sources and documented assumptions</span>
        <span>
          <Database size={14} /> Methodology &amp; Evidence
        </span>
        <span>
          <FileCheck2 size={14} /> Evidence: OPEN
        </span>
      </footer>
    </main>
  );
}
