'use client';

import {
  AlertTriangle,
  ArrowDown,
  ArrowRight,
  BadgeCheck,
  BarChart3,
  Building2,
  Check,
  CircleAlert,
  Database,
  FileCheck2,
  FileSearch,
  Filter,
  Globe2,
  LockKeyhole,
  Search,
  ShieldCheck,
  ShieldX,
  SlidersHorizontal,
  Target,
  X,
} from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';

const PROJECTS_URL = '/data/projects.json';
const SUMMARY_URL = '/data/summary.json';
const FROZEN_SHA = 'ff69e15d211ff1abc88200574242ed2f1db49074';

type PhysicalStatus =
  | 'PASS_WITHIN_SCREENING_BAND'
  | 'LOW_YIELD_REVIEW'
  | 'EXTREME_OUTLIER_BLOCK_BASE';

type ProjectRecord = {
  projectId: string;
  projectName: string;
  country: string;
  developer: string;
  offtaker: string;
  city: string;
  businessModel: string;
  capacityMw: number;
  generationGwh: number;
  yield: number;
  physicalStatus: PhysicalStatus;
  economicsStatus: 'READY_FOR_ECONOMICS' | 'TECHNICAL_DATA_BLOCKED';
  evidenceGrade: string;
  sourceQualityGrade: string;
  sourceId: string;
};

type RemoteProject = {
  project_id: string;
  project_name: string;
  country: string;
  capacity_kwp_observed: string;
  generation_kwh_observed: string;
  observedGenerationGwh?: number;
  capacityMw?: number;
  specificYieldKwhKwp?: number;
  developer?: string;
  offtaker?: string;
  city?: string;
  subnational_region?: string;
  business_model?: string;
  evidence_grade?: string;
  source_quality_grade?: string;
  physicalStatus: PhysicalStatus;
  technicalDataBlocked: boolean;
  source_id: string;
};

type Summary = {
  candidateHistory: number;
  rawObservations: number;
  selectedProjects: number;
  economicsReadyRecords: number;
  technicalBlockedRecords: number;
};

type ProjectPayload = { projects: RemoteProject[] };

const EMPTY_SUMMARY: Summary = {
  candidateHistory: 54,
  rawObservations: 441,
  selectedProjects: 20,
  economicsReadyRecords: 19,
  technicalBlockedRecords: 1,
};

const STATUS_LABEL: Record<PhysicalStatus, string> = {
  PASS_WITHIN_SCREENING_BAND: 'PASS',
  LOW_YIELD_REVIEW: 'LOW-YIELD REVIEW',
  EXTREME_OUTLIER_BLOCK_BASE: 'EXTREME BLOCK',
};

const COUNTRIES = [
  'All countries',
  'France',
  'India',
  'Italy',
  'Slovakia',
  'Vietnam',
  'Spain',
  'Poland',
];
const PHYSICAL_FILTERS = [
  'All',
  'Within screening band',
  'Low-yield review',
  'Extreme technical block',
];
const ECONOMICS_FILTERS = ['All', 'Economics-ready', 'Technical-data-blocked'];

const formatNumber = (value: number, digits = 0) =>
  value.toLocaleString('en-US', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });

function normalizeRecords(projects: RemoteProject[]): ProjectRecord[] {
  return projects.map((project) => {
    const capacity = Number(project.capacityMw ?? Number(project.capacity_kwp_observed) / 1000);
    const generation = Number(project.observedGenerationGwh ?? Number(project.generation_kwh_observed) / 1_000_000);
    const specificYield = capacity ? (generation * 1000) / capacity : 0;
    return {
      projectId: project.project_id,
      projectName: project.project_name,
      country: project.country,
      developer: project.developer || 'Not disclosed',
      offtaker: project.offtaker || 'Not disclosed',
      city: project.city || project.subnational_region || '—',
      businessModel: project.business_model || '—',
      capacityMw: capacity,
      generationGwh: generation,
      yield: Number(project.specificYieldKwhKwp ?? specificYield),
      physicalStatus: project.physicalStatus || 'PASS_WITHIN_SCREENING_BAND',
      economicsStatus: project.technicalDataBlocked
        ? 'TECHNICAL_DATA_BLOCKED'
        : 'READY_FOR_ECONOMICS',
      evidenceGrade: project.evidence_grade || '—',
      sourceQualityGrade: project.source_quality_grade || '—',
      sourceId: project.source_id || '—',
    };
  });
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(
      `Project master unavailable (${response.status}). See Model & Evidence for release status.`,
    );
  }
  return response.json() as Promise<T>;
}

function Brand() {
  return (
    <Link className="projects-brand" href="/" aria-label="VietGreen Overview">
      <span className="projects-brand-mark">
        <BarChart3 size={19} />
      </span>
      <span>
        <strong>VietGreen</strong>
        <small>C&amp;I Solar Project Finance</small>
      </span>
    </Link>
  );
}

function Header() {
  const items = [
    ['Overview', '/'],
    ['Projects & Data', '/projects'],
    ['Energy & Physical', '/energy'],
    ['Finance', '/economics'],
    ['Diligence', '/diligence'],
    ['Model & Evidence', '/model-evidence'],
  ];
  return (
    <header className="projects-header">
      <Brand />
      <nav className="projects-nav" aria-label="Primary navigation">
        {items.map(([label, href]) => (
          <a
            className={label === 'Projects & Data' ? 'active' : ''}
            href={href}
            key={label}
          >
            {label}
          </a>
        ))}
      </nav>
      <span className="projects-release">V5.1.3 · Frozen Model</span>
    </header>
  );
}

function SectionTitle({
  number,
  title,
  note,
}: {
  number: string;
  title: string;
  note?: string;
}) {
  return (
    <div className="projects-section-title">
      <div>
        <span className="projects-section-number">{number}</span>
        <h2>{title}</h2>
      </div>
      {note ? <p>{note}</p> : null}
    </div>
  );
}

function Kpi({
  icon: Icon,
  value,
  label,
}: {
  icon: typeof Search;
  value: string;
  label: string;
}) {
  return (
    <div className="projects-kpi">
      <Icon size={23} />
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function StatusBadge({ status }: { status: PhysicalStatus }) {
  return (
    <span
      className={`projects-status status-${status.toLowerCase()}`}
      title={status}
    >
      {status === 'PASS_WITHIN_SCREENING_BAND' ? (
        <Check size={12} />
      ) : status === 'LOW_YIELD_REVIEW' ? (
        <AlertTriangle size={12} />
      ) : (
        <ShieldX size={12} />
      )}
      {STATUS_LABEL[status]}
    </span>
  );
}

function EconomicsBadge({
  status,
}: {
  status: ProjectRecord['economicsStatus'];
}) {
  return (
    <span
      className={`projects-econ ${status === 'READY_FOR_ECONOMICS' ? 'ready' : 'blocked'}`}
      title={status}
    >
      {status === 'READY_FOR_ECONOMICS' ? (
        <Check size={12} />
      ) : (
        <ShieldX size={12} />
      )}
      {status === 'READY_FOR_ECONOMICS' ? 'READY' : 'BLOCKED'}
    </span>
  );
}

function CountryChart({ records }: { records: ProjectRecord[] }) {
  const countryData = useMemo(() => {
    const groups = new Map<
      string,
      { projects: number; capacity: number; generation: number }
    >();
    records
      .filter((record) => record.economicsStatus === 'READY_FOR_ECONOMICS')
      .forEach((record) => {
        const current = groups.get(record.country) ?? {
          projects: 0,
          capacity: 0,
          generation: 0,
        };
        groups.set(record.country, {
          projects: current.projects + 1,
          capacity: current.capacity + record.capacityMw,
          generation: current.generation + record.generationGwh,
        });
      });
    return [...groups.entries()]
      .map(([country, values]) => ({ country, ...values }))
      .sort((a, b) => b.capacity - a.capacity);
  }, [records]);
  const max = countryData[0]?.capacity || 1;
  return (
    <div
      className="country-chart"
      aria-label="Economics-ready capacity by country horizontal bar chart"
    >
      {countryData.map((item) => (
        <div className="country-row" key={item.country}>
          <span>{item.country}</span>
          <div className="country-bar-track">
            <i
              style={{ width: `${(item.capacity / max) * 100}%` }}
              className={item.country === 'Vietnam' ? 'highlight' : ''}
            />
          </div>
          <strong>{formatNumber(item.capacity, 3)}</strong>
        </div>
      ))}
    </div>
  );
}

function QADonut({ records }: { records: ProjectRecord[] }) {
  const counts = records.length
    ? [
        records.filter(
          (record) => record.physicalStatus === 'PASS_WITHIN_SCREENING_BAND',
        ).length,
        records.filter((record) => record.physicalStatus === 'LOW_YIELD_REVIEW')
          .length,
        records.filter(
          (record) => record.physicalStatus === 'EXTREME_OUTLIER_BLOCK_BASE',
        ).length,
      ]
    : [15, 4, 1];
  const total = Math.max(records.length, 1);
  const circumference = 2 * Math.PI * 43;
  let offset = 0;
  return (
    <div className="qa-donut-wrap">
      <svg
        viewBox="0 0 120 120"
        aria-label={`Physical QA distribution: ${counts[0]} pass, ${counts[1]} review, ${counts[2]} blocked`}
      >
        <circle
          cx="60"
          cy="60"
          r="43"
          fill="none"
          stroke="#e8e3d8"
          strokeWidth="14"
        />
        {counts.map((count, index) => {
          const length = (count / total) * circumference;
          const dash = `${length} ${circumference - length}`;
          const circle = (
            <circle
              key={index}
              cx="60"
              cy="60"
              r="43"
              fill="none"
              stroke={['#12624e', '#d69a2a', '#c83f3d'][index]}
              strokeWidth="14"
              strokeDasharray={dash}
              strokeDashoffset={-offset}
              transform="rotate(-90 60 60)"
            />
          );
          offset += length;
          return circle;
        })}
        <text x="60" y="58" textAnchor="middle" className="donut-total">
          {records.length || 20}
        </text>
        <text x="60" y="73" textAnchor="middle" className="donut-label">
          records
        </text>
      </svg>
      <div className="qa-legend">
        <span>
          <i className="dot-pass" />
          15 <small>Pass</small>
        </span>
        <span>
          <i className="dot-review" />4 <small>Review</small>
        </span>
        <span>
          <i className="dot-block" />1 <small>Block</small>
        </span>
      </div>
    </div>
  );
}

function Scatter({ records }: { records: ProjectRecord[] }) {
  const left = 45;
  const top = 18;
  const width = 510;
  const height = 230;
  const x = (value: number) =>
    left +
    ((Math.log10(Math.max(value, 0.5)) - Math.log10(0.5)) /
      (Math.log10(35) - Math.log10(0.5))) *
      width;
  const y = (value: number) =>
    top + height - (Math.min(value, 3500) / 3500) * height;
  return (
    <div className="scatter-wrap">
      <svg
        viewBox="0 0 610 285"
        aria-label="Capacity versus observed specific yield scatter plot with 900, 1600 and 3200 kWh per kWp screening lines"
      >
        <line
          x1={left}
          y1={y(900)}
          x2={left + width}
          y2={y(900)}
          className="line-pass"
        />
        <line
          x1={left}
          y1={y(1600)}
          x2={left + width}
          y2={y(1600)}
          className="line-review"
        />
        <line
          x1={left}
          y1={y(3200)}
          x2={left + width}
          y2={y(3200)}
          className="line-block"
        />
        <text x="560" y={y(900) + 4} className="chart-label">
          900
        </text>
        <text x="560" y={y(1600) + 4} className="chart-label">
          1,600
        </text>
        <text x="560" y={y(3200) + 4} className="chart-label">
          3,200
        </text>
        {records.map((record) => (
          <circle
            key={record.projectId}
            cx={x(record.capacityMw)}
            cy={y(record.yield)}
            r={record.economicsStatus === 'TECHNICAL_DATA_BLOCKED' ? 5 : 3.8}
            className={
              record.physicalStatus === 'EXTREME_OUTLIER_BLOCK_BASE'
                ? 'point-block'
                : record.physicalStatus === 'LOW_YIELD_REVIEW'
                  ? 'point-review'
                  : 'point-pass'
            }
          >
            <title>{`${record.projectName} · ${record.country} · ${formatNumber(record.capacityMw, 3)} MW · ${formatNumber(record.yield, 2)} kWh/kWp · ${STATUS_LABEL[record.physicalStatus]}`}</title>
          </circle>
        ))}
        <line
          x1={left}
          y1={top + height}
          x2={left + width}
          y2={top + height}
          className="axis"
        />
        <line x1={left} y1={top} x2={left} y2={top + height} className="axis" />
        <text
          x={left + width / 2}
          y="278"
          textAnchor="middle"
          className="axis-label"
        >
          Installed capacity (MW, log scale)
        </text>
        <text
          x="13"
          y="145"
          transform="rotate(-90 13 145)"
          textAnchor="middle"
          className="axis-label"
        >
          Specific yield (kWh/kWp)
        </text>
      </svg>
      <div className="scatter-note">
        <span>
          <i className="dot-pass" />
          Pass
        </span>
        <span>
          <i className="dot-review" />
          Review
        </span>
        <span>
          <i className="dot-block" />
          Block
        </span>
      </div>
    </div>
  );
}

export default function ProjectsPage() {
  const [records, setRecords] = useState<ProjectRecord[]>([]);
  const [summary, setSummary] = useState<Summary>(EMPTY_SUMMARY);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [country, setCountry] = useState('All countries');
  const [developer, setDeveloper] = useState('All developers');
  const [physical, setPhysical] = useState('All');
  const [economics, setEconomics] = useState('All');
  const [selected, setSelected] = useState<ProjectRecord | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([
      fetchJson<ProjectPayload>(PROJECTS_URL),
      fetchJson<Partial<Summary>>(SUMMARY_URL),
    ])
      .then(([projectPayload, summaryPayload]) => {
        const nextRecords = normalizeRecords(projectPayload.projects);
        if (!nextRecords.length || nextRecords.length !== 20)
          throw new Error(
            'DATA RECONCILIATION ERROR — authoritative project count is not 20.',
          );
        if (active) {
          setRecords(nextRecords);
          setSummary({ ...EMPTY_SUMMARY, ...summaryPayload });
          setLoading(false);
        }
      })
      .catch((reason: unknown) => {
        if (active) {
          setError(
            reason instanceof Error
              ? reason.message
              : 'Project master unavailable. See Model & Evidence for release status.',
          );
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  const developers = useMemo(
    () => [
      'All developers',
      ...new Set(records.map((record) => record.developer)),
    ],
    [records],
  );
  const filteredRecords = useMemo(
    () =>
      records
        .filter((record) => {
          const haystack = [
            record.projectName,
            record.projectId,
            record.country,
            record.developer,
            record.offtaker,
          ]
            .join(' ')
            .toLowerCase();
          const physicalMatch =
            physical === 'All' ||
            (physical === 'Within screening band' &&
              record.physicalStatus === 'PASS_WITHIN_SCREENING_BAND') ||
            (physical === 'Low-yield review' &&
              record.physicalStatus === 'LOW_YIELD_REVIEW') ||
            (physical === 'Extreme technical block' &&
              record.physicalStatus === 'EXTREME_OUTLIER_BLOCK_BASE');
          const economicsMatch =
            economics === 'All' ||
            (economics === 'Economics-ready' &&
              record.economicsStatus === 'READY_FOR_ECONOMICS') ||
            (economics === 'Technical-data-blocked' &&
              record.economicsStatus === 'TECHNICAL_DATA_BLOCKED');
          return (
            (!query || haystack.includes(query.toLowerCase())) &&
            (country === 'All countries' || record.country === country) &&
            (developer === 'All developers' ||
              record.developer === developer) &&
            physicalMatch &&
            economicsMatch
          );
        })
        .sort(
          (a, b) =>
            a.country.localeCompare(b.country) || b.capacityMw - a.capacityMw,
        ),
    [records, query, country, developer, physical, economics],
  );

  const qaCounts = useMemo(
    () =>
      records.length
        ? {
            pass: records.filter(
              (record) =>
                record.physicalStatus === 'PASS_WITHIN_SCREENING_BAND',
            ).length,
            review: records.filter(
              (record) => record.physicalStatus === 'LOW_YIELD_REVIEW',
            ).length,
            block: records.filter(
              (record) =>
                record.physicalStatus === 'EXTREME_OUTLIER_BLOCK_BASE',
            ).length,
          }
        : { pass: 15, review: 4, block: 1 },
    [records],
  );
  const selectedCapacity = records.length
    ? records.reduce((sum, record) => sum + record.capacityMw, 0)
    : 131.943;
  const readyCapacity = records.length
    ? records
        .filter((record) => record.economicsStatus === 'READY_FOR_ECONOMICS')
        .reduce((sum, record) => sum + record.capacityMw, 0)
    : 129.853;
  const readyGeneration = records.length
    ? records
        .filter((record) => record.economicsStatus === 'READY_FOR_ECONOMICS')
        .reduce((sum, record) => sum + record.generationGwh, 0)
    : 148.221;

  return (
    <div className="projects-page">
      <Header />
      <div className="projects-status-strip">
        <span>●</span> V5.1.3 · Frozen model · Public-data reconstruction ·
        Projects &amp; Data
      </div>
      <section className="projects-hero">
        <Image
          fill
          priority
          sizes="100vw"
          src="/assets/projects/projects-hero.webp"
          alt="Industrial solar campus with rooftop panels"
        />
        <div className="projects-hero-overlay" />
        <div className="projects-hero-inner">
          <div>
            <p className="projects-eyebrow">
              PROJECT UNIVERSE · DATA LINEAGE · PHYSICAL QA
            </p>
            <h1>
              From 54 Public Solar Candidates
              <br />
              to 20 Controlled Project Records.
            </h1>
            <p>
              The project master preserves source-reported capacity, generation,
              counterparties and evidence lineage, then separates observed facts
              from model overlays before any Project Finance economics are
              calculated.
            </p>
            <div className="projects-actions">
              <a className="projects-button primary" href="#project-master">
                View Project Master <ArrowDown size={15} />
              </a>
              <a className="projects-button secondary" href="#physical-qa">
                See Physical QA <ArrowDown size={15} />
              </a>
            </div>
          </div>
          <aside className="projects-hero-card">
            <MetricLine
              icon={Search}
              value={summary.candidateHistory}
              label="CANDIDATES RESEARCHED"
            />
            <MetricLine
              icon={FileSearch}
              value={summary.selectedProjects}
              label="SELECTED RECORDS"
            />
            <MetricLine
              icon={BarChart3}
              value={summary.economicsReadyRecords}
              label="ECONOMICS-READY"
            />
            <MetricLine
              icon={ShieldX}
              value={summary.technicalBlockedRecords}
              label="TECHNICAL BLOCK"
            />
            <strong className="hero-card-foot">
              <Database size={18} /> {summary.rawObservations} PRESERVED
              OBSERVATIONS
            </strong>
          </aside>
        </div>
      </section>
      <main className="projects-main">
        <section className="projects-section">
          <SectionTitle
            number="1"
            title="Research Universe at a Glance"
            note="The model begins with a research universe, not a pre-cleaned financial dataset."
          />
          <div className="projects-kpi-grid">
            <Kpi
              icon={Search}
              value={String(summary.candidateHistory)}
              label="Candidate projects"
            />
            <Kpi
              icon={Database}
              value={String(summary.rawObservations)}
              label="Preserved observations"
            />
            <Kpi
              icon={FileCheck2}
              value={String(summary.selectedProjects)}
              label="Selected records"
            />
            <Kpi
              icon={BadgeCheck}
              value={String(summary.economicsReadyRecords)}
              label="Economics-ready"
            />
            <Kpi icon={Globe2} value="7" label="Countries" />
            <Kpi icon={Building2} value="5" label="Developers" />
          </div>
          <div className="projects-secondary-strip">
            <span>
              <b>{formatNumber(selectedCapacity, 3)} MW</b>Selected capacity
            </span>
            <span>
              <b>{formatNumber(readyCapacity, 3)} MW</b>Economics-ready capacity
            </span>
            <span>
              <b>{formatNumber(readyGeneration, 3)} GWh</b>Economics-ready
              observed generation
            </span>
            <span className="danger">
              <b>{qaCounts.block}</b>Technical block
            </span>
          </div>
          <p className="projects-note">
            <CircleAlert size={14} /> Ready generation excludes the technically
            blocked Arisudhana observation.
          </p>
        </section>
        <div className="projects-analysis-grid">
          <section className="projects-section lineage-section">
            <SectionTitle
              number="2"
              title="From Research History to Model-Ready Inputs"
              note="Every reduction in the dataset is explicit and auditable."
            />
            <div className="lineage-funnel">
              {[
                ['54', 'Candidate projects', Search],
                ['20', 'Selected records', FileCheck2],
                ['20', 'Physical QA records', ShieldCheck],
                ['19', 'Model-ready records', BadgeCheck],
                ['19', 'Economics / Debt / Scenarios', BarChart3],
                ['19', 'Diligence records', Target],
              ].map(([value, label, Icon], index) => (
                <div className="lineage-node" key={String(label)}>
                  <span>{String(value)}</span>
                  <Icon size={21} />
                  <strong>{String(label)}</strong>
                  {index < 5 && (
                    <ArrowRight className="lineage-arrow" size={14} />
                  )}
                </div>
              ))}
              <div className="lineage-branch">
                <ShieldX size={17} /> <b>1</b> TECHNICAL BLOCK · FPEL Arisudhana
              </div>
              <div className="outcome-blind">
                <Target size={24} />
                <div>
                  <strong>Outcome-Blind Selection</strong>
                  <p>
                    Projects are selected from public evidence and data
                    readiness, not because their modeled economics later appear
                    attractive.
                  </p>
                </div>
              </div>
            </div>
          </section>
          <section className="projects-section footprint-section">
            <SectionTitle
              number="3"
              title="A Cross-Country C&amp;I Solar Universe"
              note="19 economics-ready projects span seven countries, with one selected record held outside economics by the physical QA firewall."
            />
            <div className="footprint-layout">
              <CountryChart records={records} />
              <div className="lineage-side-metrics">
                <b>19</b>
                <span>Ready Projects</span>
                <b>{formatNumber(readyCapacity, 3)} MW</b>
                <span>Economics-ready capacity</span>
                <b>{formatNumber(readyGeneration, 3)} GWh</b>
                <span>Observed generation</span>
                <b>7</b>
                <span>Countries</span>
              </div>
            </div>
            <div className="developer-strip">
              <strong>Developers Represented</strong>
              {developers
                .filter((item) => item !== 'All developers')
                .map((item) => (
                  <span key={item}>{item}</span>
                ))}
            </div>
          </section>
        </div>
        <section className="projects-section evidence-section">
          <SectionTitle
            number="4"
            title="Evidence Is Classified Before It Is Modeled."
            note="Observed facts, calculated fields and assumptions are never presented as the same type of evidence."
          />
          <div className="evidence-grid">
            {[
              [
                'Observed / Source Reported',
                'SOURCE-BACKED',
                'Installed capacity · Published annual generation · Named developer · Named offtaker · Public project status',
                'green',
                FileSearch,
              ],
              [
                'Derived',
                'CALCULATED',
                'Specific yield · Country aggregates · Resolved model fields · Calculated ratios',
                'teal',
                SlidersHorizontal,
              ],
              [
                'Benchmark Assumption',
                'BENCHMARK',
                'Standardized underwriting inputs · Benchmark CAPEX/OPEX · Tax / rate overlays',
                'gold',
                BarChart3,
              ],
              [
                'Analyst Assumption',
                'ANALYST OVERLAY',
                'Standardized operating archetypes · Load proxies · Self-consumption assumptions',
                'neutral',
                Target,
              ],
              [
                'Scenario',
                'STRESS TEST',
                'P90 screening · CAPEX stress · Rate shock · COD delay · Offtaker downside',
                'blue',
                ShieldCheck,
              ],
              [
                'Missing / Not Disclosed',
                'OPEN EVIDENCE',
                'Exact confidential PPA price · Executed financing terms · Site diligence · Engineering validation',
                'red',
                CircleAlert,
              ],
            ].map(([title, badge, copy, color, Icon]) => (
              <article
                className={`evidence-card ${String(color)}`}
                key={String(title)}
              >
                <Icon size={22} />
                <h3>{String(title)}</h3>
                <span>{String(badge)}</span>
                <p>{String(copy)}</p>
              </article>
            ))}
          </div>
          <blockquote className="missing-callout">
            <span>“</span>
            <div>
              <strong>Missing evidence is not converted into a fact.</strong>
              <p>
                The data model carries missingness forward to the decision
                boundary instead of silently filling it.
              </p>
            </div>
          </blockquote>
        </section>
        <section
          id="project-master"
          className="projects-section master-section"
        >
          <SectionTitle
            number="5"
            title="Selected Project Master"
            note="20 source-backed project records form the controlled research universe."
          />
          <div className="filter-toolbar">
            <label>
              <Search size={15} />
              <input
                aria-label="Search project"
                placeholder="Search project, ID, developer, offtaker..."
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
            </label>
            <label>
              <Globe2 size={15} />
              <select
                aria-label="Country filter"
                value={country}
                onChange={(event) => setCountry(event.target.value)}
              >
                {COUNTRIES.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>
            <label>
              <Building2 size={15} />
              <select
                aria-label="Developer filter"
                value={developer}
                onChange={(event) => setDeveloper(event.target.value)}
              >
                {developers.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>
            <label>
              <Filter size={15} />
              <select
                aria-label="Physical QA filter"
                value={physical}
                onChange={(event) => setPhysical(event.target.value)}
              >
                {PHYSICAL_FILTERS.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>
            <label>
              <BadgeCheck size={15} />
              <select
                aria-label="Economics status filter"
                value={economics}
                onChange={(event) => setEconomics(event.target.value)}
              >
                {ECONOMICS_FILTERS.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>
          </div>
          <div className="filter-result">
            <span>
              Showing <b>{filteredRecords.length}</b> of 20 authoritative
              records
            </span>
            <span>Country → capacity descending</span>
          </div>
          {loading ? (
            <div className="projects-loading">
              <div />
              <div />
              <div />
            </div>
          ) : error ? (
            <div className="projects-error">
              <CircleAlert size={22} />
              <strong>{error}</strong>
            </div>
          ) : (
            <>
              <div className="project-table-wrap">
                <table>
                  <caption>
                    Selected Project Master — 20 source-backed project records
                  </caption>
                  <thead>
                    <tr>
                      <th scope="col">Project</th>
                      <th scope="col">Country</th>
                      <th scope="col">Developer</th>
                      <th scope="col">Capacity</th>
                      <th scope="col">Observed generation</th>
                      <th scope="col">Specific yield</th>
                      <th scope="col">Physical QA</th>
                      <th scope="col">Economics</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredRecords.map((record) => (
                      <tr
                        className={
                          record.economicsStatus === 'TECHNICAL_DATA_BLOCKED'
                            ? 'blocked-row'
                            : record.physicalStatus === 'LOW_YIELD_REVIEW'
                              ? 'review-row'
                              : ''
                        }
                        key={record.projectId}
                        onClick={() => setSelected(record)}
                      >
                        <td>
                          <strong>{record.projectName}</strong>
                          <small>{record.projectId}</small>
                        </td>
                        <td>{record.country}</td>
                        <td>{record.developer}</td>
                        <td>{formatNumber(record.capacityMw, 3)} MW</td>
                        <td>{formatNumber(record.generationGwh, 3)} GWh</td>
                        <td>
                          {formatNumber(record.yield, 2)}
                          <small>kWh/kWp</small>
                        </td>
                        <td>
                          <StatusBadge status={record.physicalStatus} />
                        </td>
                        <td>
                          <EconomicsBadge status={record.economicsStatus} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="project-mobile-cards">
                {filteredRecords.map((record) => (
                  <button
                    className={
                      record.economicsStatus === 'TECHNICAL_DATA_BLOCKED'
                        ? 'blocked-row'
                        : ''
                    }
                    key={record.projectId}
                    onClick={() => setSelected(record)}
                  >
                    <strong>{record.projectName}</strong>
                    <small>
                      {record.country} · {record.developer}
                    </small>
                    <span>
                      {formatNumber(record.capacityMw, 3)} MW ·{' '}
                      {formatNumber(record.generationGwh, 3)} GWh ·{' '}
                      {formatNumber(record.yield, 2)} kWh/kWp
                    </span>
                    <em>
                      <StatusBadge status={record.physicalStatus} />
                      <EconomicsBadge status={record.economicsStatus} />
                    </em>
                  </button>
                ))}
              </div>
            </>
          )}
        </section>
        <section id="physical-qa" className="projects-section qa-section">
          <SectionTitle
            number="6"
            title="Physical QA Before Financial Modeling"
            note="The model screens basic engineering plausibility before allowing a project into standardized economics."
          />
          <div className="qa-summary-grid">
            <div>
              <Check size={21} />
              <b>{qaCounts.pass}</b>
              <span>Within screening band</span>
            </div>
            <div>
              <AlertTriangle size={21} />
              <b>{qaCounts.review}</b>
              <span>Low-yield review</span>
            </div>
            <div>
              <ShieldX size={21} />
              <b>{qaCounts.block}</b>
              <span>Extreme technical block</span>
            </div>
          </div>
          <div className="qa-visuals">
            <div className="qa-chart-card">
              <h3>Physical QA Distribution</h3>
              <QADonut records={records} />
            </div>
            <div className="qa-chart-card scatter-card">
              <h3>Capacity vs Observed Specific Yield</h3>
              <Scatter records={records} />
              <p>
                Screening band: <b>900–1,600 kWh/kWp</b> · Extreme firewall:{' '}
                <b>&gt;3,200 kWh/kWp</b>
              </p>
            </div>
          </div>
          <div className="low-yield-panel">
            <strong>Low-yield review — visible, not failed</strong>
            {records
              .filter((record) => record.physicalStatus === 'LOW_YIELD_REVIEW')
              .map((record) => (
                <span key={record.projectId}>
                  {record.projectName} <b>{formatNumber(record.yield, 2)}</b>{' '}
                  kWh/kWp
                </span>
              ))}
          </div>
        </section>
        <section className="projects-section arisudhana-section">
          <SectionTitle
            number="7"
            title="Featured QA Case — FPEL Arisudhana"
            note="A source-reported physical observation is preserved, challenged and blocked rather than silently repaired."
          />
          <div className="arisudhana-flow">
            <div>
              <FileSearch size={25} />
              <strong>SOURCE CLAIM</strong>
              <small>30.500 GWh</small>
            </div>
            <ArrowRight />
            <div>
              <SlidersHorizontal size={25} />
              <strong>DERIVED YIELD</strong>
              <small>~14,593 kWh/kWp</small>
            </div>
            <ArrowRight />
            <div>
              <ShieldCheck size={25} />
              <strong>PHYSICAL FIREWALL</strong>
              <small>&gt;3,200 threshold</small>
            </div>
            <ArrowRight />
            <div className="flow-danger">
              <ShieldX size={25} />
              <strong>BASE ECONOMICS BLOCKED</strong>
              <small>Technical validation required</small>
            </div>
          </div>
          <div className="arisudhana-proof">
            <div>
              <b>2.090 MW</b>
              <span>Capacity</span>
            </div>
            <div>
              <b>30.500 GWh</b>
              <span>Source-reported generation</span>
            </div>
            <div>
              <b>~14,593</b>
              <span>Implied specific yield</span>
            </div>
            <div className="proof-badges">
              <span>EXTREME_OUTLIER_BLOCK_BASE</span>
              <span>TECHNICAL_DATA_BLOCKED</span>
            </div>
          </div>
          <div className="model-does">
            <div>
              <strong>What the model does</strong>
              <p>✓ Preserves source observation</p>
              <p>✓ Preserves evidence lineage</p>
              <p>✓ Prevents direct base-economics use</p>
            </div>
            <div>
              <strong>What the model does not do</strong>
              <p>× Does not normalize 30.5 GWh</p>
              <p>× Does not replace with guessed benchmark</p>
              <p>× Does not call it bankable</p>
            </div>
          </div>
        </section>
        <section className="projects-section governance-section">
          <SectionTitle
            number="8"
            title="A Controlled Dataset, Not a Cleaned Story."
            note="The project preserves uncertainty and source limitations through the entire analytical chain."
          />
          <div className="governance-grid">
            {[
              [
                'Source Lineage',
                'Every current model input can be traced back to a public/source-reported value, a calculation, an explicit overlay or a declared missing field.',
                FileSearch,
              ],
              [
                'Evidence Classes',
                'Observed facts stay separate from derived values, benchmarks, analyst assumptions and scenario stresses.',
                SlidersHorizontal,
              ],
              [
                'Fail-Closed QA',
                'Unsupported or physically extreme inputs are not automatically repaired merely to keep the finance engine running.',
                LockKeyhole,
              ],
              [
                'Frozen Release',
                'The selected universe and evidence boundary are frozen under V5.1.3 before presentation.',
                BadgeCheck,
              ],
            ].map(([title, copy, Icon]) => (
              <article key={String(title)}>
                <Icon size={24} />
                <strong>{String(title)}</strong>
                <p>{String(copy)}</p>
                {title === 'Frozen Release' && (
                  <small>
                    v5.1.3-recruiter-final
                    <br />
                    {FROZEN_SHA.slice(0, 12)}...
                  </small>
                )}
              </article>
            ))}
          </div>
          <div className="governance-strip">
            <b>20</b> Selected <b>20</b> Physical QA <b>19</b> Ready{' '}
            <b className="danger-text">1</b> Blocked <b>441</b> Observations{' '}
            <b>7</b> Countries <b>5</b> Developers
          </div>
        </section>
      </main>
      <section className="projects-takeaway">
        <div className="projects-takeaway-inner">
          <p>RECRUITER TAKEAWAY</p>
          <h2>
            The financial model starts only after the project universe, source
            evidence and physical plausibility have been controlled.
          </h2>
          <span>
            20 selected records enter the data-governance layer. 19 proceed to
            standardized economics. 1 remains visible as evidence — but blocked
            from base finance.
          </span>
          <div>
            <a className="projects-button primary" href="#physical-qa">
              Continue to Energy &amp; Physical Model <ArrowRight size={15} />
            </a>
            <a className="projects-button secondary" href="#project-master">
              View Project Master <ArrowRight size={15} />
            </a>
          </div>
        </div>
      </section>
      {selected && (
        <dialog
          open
          className="project-drawer-backdrop"
          aria-label="Project record details"
        >
          <button
            type="button"
            className="drawer-backdrop-close"
            aria-label="Close project details"
            onClick={() => setSelected(null)}
          />
          <div className="project-drawer">
            <button
              className="drawer-close"
              onClick={() => setSelected(null)}
              aria-label="Close project details"
            >
              <X size={20} />
            </button>
            <p className="drawer-kicker">PROJECT RECORD · {selected.country}</p>
            <h2>{selected.projectName}</h2>
            <small>{selected.projectId}</small>
            <div className="drawer-status">
              <StatusBadge status={selected.physicalStatus} />
              <EconomicsBadge status={selected.economicsStatus} />
            </div>
            <div className="drawer-grid">
              <span>
                <b>Capacity</b>
                {formatNumber(selected.capacityMw, 3)} MW
              </span>
              <span>
                <b>Generation</b>
                {formatNumber(selected.generationGwh, 3)} GWh
              </span>
              <span>
                <b>Specific yield</b>
                {formatNumber(selected.yield, 2)} kWh/kWp
              </span>
              <span>
                <b>Developer</b>
                {selected.developer}
              </span>
              <span>
                <b>Offtaker</b>
                {selected.offtaker}
              </span>
              <span>
                <b>Source ID</b>
                {selected.sourceId}
              </span>
            </div>
            <div className="drawer-evidence">
              <strong>Evidence boundary</strong>
              <p>
                Project identity and operating observations are shown from the
                frozen public-data master. Finance outputs are intentionally
                kept on the Economics, Debt and Risk pages.
              </p>
            </div>
            <a
              className="projects-button primary"
              href="#physical-qa"
              onClick={() => setSelected(null)}
            >
              Open Physical QA <ArrowRight size={15} />
            </a>
          </div>
        </dialog>
      )}
    </div>
  );
}

function MetricLine({
  icon: Icon,
  value,
  label,
}: {
  icon: typeof Search;
  value: number;
  label: string;
}) {
  return (
    <div className="hero-metric">
      <Icon size={19} />
      <b>{value}</b>
      <span>{label}</span>
    </div>
  );
}

