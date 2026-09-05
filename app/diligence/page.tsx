'use client';

import Image from 'next/image';
import Link from 'next/link';
import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Check,
  CircleAlert,
  CircleCheck,
  ClipboardCheck,
  Database,
  FileCheck2,
  FileSearch,
  FolderOpen,
  Gauge,
  Globe2,
  Handshake,
  Landmark,
  LockKeyhole,
  MapPin,
  ShieldAlert,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Target,
  WalletCards,
  X,
  Zap,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { loadWebsiteData } from '@/lib/data';
const GO_MALL = 'VN-GY-GOMALL';
const ARISUDHANA = 'IN-FPEL-ARISUDHANA';

type RemoteProject = {
  project_id: string;
  project_name: string;
  country: string;
  capacity_kwp_observed: string;
  generation_kwh_observed: string;
  physicalStatus: string;
  engineeringReviewRequired?: string;
  technicalDataBlocked?: boolean;
  ppa_mode?: string;
  decision?: string;
  diligencePriority?: string;
  commercialStatus?: string;
  creditStatus?: string;
  riskStatus?: string;
  evidenceStatus?: string;
  nextActions?: string[];
  capitalAllocatedUsd?: number;
};

type DiligenceRecord = RemoteProject & {
  capacityMw: number;
  generationGwh: number;
  yield: number;
  technicalLabel: string;
  commercialLabel: string;
  creditLabel: string;
  riskLabel: string;
  evidenceLabel: string;
  nextAction: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
};

const ACTIONS = [
  'ENGINEERING_VALIDATION',
  'COMMERCIAL_EVIDENCE',
  'PPA_RESTRUCTURING',
  'CREDIT_RESTRUCTURING',
  'COUNTERPARTY_DILIGENCE',
  'COD_TIMING_REVIEW',
  'SPONSOR_SUPPORT_REVIEW',
  'TRANSACTION_EVIDENCE',
  'READY_FOR_NEXT_DILIGENCE_STAGE',
] as const;

const FUNNEL_STEPS: [string, string, typeof Gauge][] = [
  ['20', 'Selected records', FileSearch],
  ['20', 'Physical QA', ShieldCheck],
  ['19', 'Economics-ready', BarChart3],
  ['19', 'Diligence shortlist', ClipboardCheck],
];

const formatNumber = (value: number, digits = 0) =>
  value.toLocaleString('en-US', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });

function StatusPill({ value, tone = '' }: { value: string; tone?: string }) {
  const readable = value.replaceAll('_', ' ');
  return <span className={`diligence-status ${tone}`}>{readable}</span>;
}

function SectionHeading({
  number,
  title,
  note,
}: {
  number: string;
  title: string;
  note?: string;
}) {
  return (
    <div className="diligence-heading">
      <div>
        <span className="diligence-index">{number}</span>
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
  tone = '',
}: {
  icon: typeof Gauge;
  value: string;
  label: string;
  tone?: string;
}) {
  return (
    <div className={`diligence-kpi ${tone}`}>
      <Icon size={21} />
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function Lens({
  icon: Icon,
  title,
  status,
  tone,
  items,
  value,
}: {
  icon: typeof Gauge;
  title: string;
  status: string;
  tone: string;
  items: string[];
  value: number;
}) {
  return (
    <article className={`diligence-lens ${tone}`}>
      <div className="lens-title">
        <Icon size={20} />
        <strong>{title}</strong>
      </div>
      <b className="lens-status">{status.replaceAll('_', ' ')}</b>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
      <div className="lens-meter">
        <i style={{ width: `${value}%` }} />
        <span>{value}%</span>
      </div>
    </article>
  );
}

function Distribution({
  title,
  rows,
  total,
}: {
  title: string;
  rows: { label: string; value: number; tone: string }[];
  total: number;
}) {
  return (
    <div className="distribution-card">
      <h3>{title}</h3>
      {rows.map((row) => (
        <div className="distribution-row" key={row.label}>
          <span>{row.label}</span>
          <div className="distribution-track">
            <i
              className={row.tone}
              style={{ width: `${total ? (row.value / total) * 100 : 0}%` }}
            />
          </div>
          <b>{row.value}</b>
        </div>
      ))}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="diligence-error" role="alert">
      <CircleAlert size={24} />
      <div>
        <strong>DILIGENCE DATA UNAVAILABLE</strong>
        <p>No fallback recommendation will be generated.</p>
      </div>
    </div>
  );
}

function Header() {
  const items = [
    ['Overview', '/'],
    ['Projects & Data', '/projects'],
    ['Energy & Physical', '/energy'],
    ['Finance⌄', '/economics'],
    ['Diligence', '/diligence'],
    ['Model & Evidence', '#'],
  ];
  return (
    <header className="diligence-header">
      <Link
        className="diligence-brand"
        href="/"
        aria-label="VietGreen Overview"
      >
        <span className="diligence-brand-mark">
          <BarChart3 size={20} />
        </span>
        <span>
          <strong>VietGreen</strong>
          <small>C&amp;I Solar Project Finance</small>
        </span>
      </Link>
      <nav aria-label="Primary navigation">
        {items.map(([label, href]) => (
          <Link
            className={label === 'Diligence' ? 'active' : ''}
            href={href}
            key={label}
          >
            {label}
          </Link>
        ))}
      </nav>
      <span className="diligence-release">V5.1.3 · Frozen Model</span>
    </header>
  );
}

function deriveRecord(project: RemoteProject): DiligenceRecord {
  const capacityMw = Number(project.capacity_kwp_observed) / 1000;
  const generationGwh = Number(project.generation_kwh_observed) / 1_000_000;
  const specificYield = capacityMw ? (generationGwh * 1000) / capacityMw : 0;
  return {
    ...project,
    capacityMw,
    generationGwh,
    yield: specificYield,
    technicalLabel:
      project.physicalStatus === 'EXTREME_OUTLIER_BLOCK_BASE'
        ? 'TECHNICAL_DATA_BLOCKED'
        : 'MODEL_OK',
    commercialLabel: project.commercialStatus ?? 'NOT AVAILABLE',
    creditLabel: project.creditStatus ?? 'NOT AVAILABLE',
    riskLabel: project.riskStatus ?? 'NOT AVAILABLE',
    evidenceLabel: project.evidenceStatus ?? 'NOT AVAILABLE',
    nextAction: project.nextActions?.[0] ?? 'NOT AVAILABLE',
    priority:
      project.diligencePriority === 'TECHNICAL'
        ? 'HIGH'
        : project.diligencePriority === 'HIGH'
          ? 'HIGH'
          : project.diligencePriority === 'MEDIUM'
            ? 'MEDIUM'
            : 'LOW',
  };
}

export default function DiligencePage() {
  const [projects, setProjects] = useState<RemoteProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [country, setCountry] = useState('All countries');
  const [commercial, setCommercial] = useState('All commercial statuses');
  const [action, setAction] = useState('All next actions');
  const [selectedId, setSelectedId] = useState(GO_MALL);
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    let active = true;
    Promise.all([
      loadWebsiteData<{
        rows?: Array<{
        projectId: string;
        projectName: string;
        country: string;
        capacityMw: number;
        physicalStatus: string;
        economicsStatus: string;
        commercialStatus: string;
        creditStatus: string;
        riskStatus: string;
        evidenceStatus: string;
        nextActions: string[];
        diligencePriority: string;
        decision: string;
        capitalAllocatedUsd: number;
        }>;
      }>('diligence'),
      loadWebsiteData<{ projects?: RemoteProject[] }>('projects'),
    ]).then(([payload, projectPayload]) => {
        if (!active) return;
        const rows = (payload.rows ?? []).map((row) => ({
          ...projectPayload.projects?.find(
            (project) => project.project_id === row.projectId,
          ),
          project_id: row.projectId,
          project_name: row.projectName,
          country: row.country,
          capacity_kwp_observed: String(row.capacityMw * 1000),
          generation_kwh_observed:
            projectPayload.projects?.find(
              (project) => project.project_id === row.projectId,
            )?.generation_kwh_observed ?? '0',
          physicalStatus: row.physicalStatus,
          technicalDataBlocked: row.economicsStatus === 'TECHNICAL_DATA_BLOCKED',
          ppa_mode: 'FRONTIER_ONLY',
          decision: row.decision,
          diligencePriority: row.diligencePriority,
          commercialStatus: row.commercialStatus,
          creditStatus: row.creditStatus,
          riskStatus: row.riskStatus,
          evidenceStatus: row.evidenceStatus,
          nextActions: row.nextActions,
          capitalAllocatedUsd: row.capitalAllocatedUsd,
        }));
        setProjects(rows);
        const queryProject = new URLSearchParams(window.location.search).get(
          'project',
        );
        if (
          queryProject &&
          rows.some(
            (project) => project.project_id === queryProject,
          )
        ) {
          setSelectedId(queryProject);
        }
      })
      .catch(() => {
        if (active) setError(true);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const financeRecords = useMemo(
    () =>
      projects
        .filter((project) => !project.technicalDataBlocked)
        .map(deriveRecord),
    [projects],
  );
  const technicalRecord = useMemo(
    () => projects.find((project) => project.project_id === ARISUDHANA),
    [projects],
  );
  const countries = useMemo(
    () => [
      'All countries',
      ...new Set(financeRecords.map((record) => record.country)),
    ],
    [financeRecords],
  );
  const filteredRecords = useMemo(
    () =>
      financeRecords.filter(
        (record) =>
          (country === 'All countries' || record.country === country) &&
          (commercial === 'All commercial statuses' ||
            record.commercialLabel === commercial) &&
          (action === 'All next actions' || record.nextAction === action),
      ),
    [action, commercial, country, financeRecords],
  );
  const selected = useMemo(
    () =>
      financeRecords.find((record) => record.project_id === selectedId) ??
      financeRecords.find((record) => record.project_id === GO_MALL),
    [financeRecords, selectedId],
  );
  const selectedCapacity = financeRecords.reduce(
    (sum, record) => sum + record.capacityMw,
    0,
  );
  const selectedGeneration = financeRecords.reduce(
    (sum, record) => sum + record.generationGwh,
    0,
  );
  const commercialCounts = useMemo(
    () => [
      {
        label: 'INSUFFICIENT_DATA',
        value: financeRecords.filter(
          (record) => record.commercialLabel === 'INSUFFICIENT_DATA',
        ).length,
        tone: 'amber',
      },
      { label: 'FEASIBLE_NEGOTIATION_ZONE', value: 0, tone: 'green' },
      { label: 'EMPTY_NEGOTIATION_ZONE', value: 0, tone: 'red' },
    ],
    [financeRecords],
  );
  const actionCounts = useMemo(
    () =>
      ACTIONS.map((label) => ({
        label,
        value: financeRecords.filter((record) => record.nextAction === label)
          .length,
        tone:
          label === 'COD_TIMING_REVIEW'
            ? 'red'
            : label === 'TRANSACTION_EVIDENCE'
              ? 'amber'
              : 'green',
      })),
    [financeRecords],
  ).filter((row) => row.value > 0);

  const openRecord = (id: string) => {
    setSelectedId(id);
    setDrawerOpen(true);
    window.history.replaceState(null, '', `/diligence?project=${id}`);
  };

  return (
    <main className="diligence-page">
      <Header />
      <section className="diligence-hero">
        <Image
          src="/assets/projects/projects-hero.webp"
          width={1672}
          height={941}
          priority
          alt="Solar campus at golden hour"
        />
        <div className="diligence-hero-overlay" />
        <div className="diligence-hero-inner">
          <div className="diligence-hero-copy">
            <p className="diligence-eyebrow">
              DILIGENCE PRIORITY · COMMERCIAL GAPS · NEXT ACTIONS
            </p>
            <h1>
              Analysis Ends in Questions
              <br />
              Before It Ends in Capital.
            </h1>
            <p>
              We organize due diligence across technical, commercial, credit and
              legal dimensions. Focus every next step on what is truly ready.
            </p>
            <div className="diligence-hero-kpis">
              <Kpi icon={ClipboardCheck} value="19" label="Diligence Records" />
              <Kpi icon={Zap} value="1" label="Technical Validation Track" />
              <Kpi icon={WalletCards} value="$0" label="Equity Budget (USD)" />
              <Kpi icon={LockKeyhole} value="0" label="Approved Allocations" />
            </div>
          </div>
          <aside className="diligence-hero-card">
            <span>SELECTED PROJECT</span>
            <h2>GO Mall Vietnam</h2>
            <p>Ho Chi Minh City, Vietnam</p>
            <div>
              <b>Technical Status</b>
              <strong className="amber-text">△ UNDER_REVIEW</strong>
            </div>
            <div>
              <b>Commercial Status</b>
              <strong className="amber-text">△ INDETERMINATE</strong>
            </div>
            <div>
              <b>Credit Status</b>
              <strong className="green-text">● MODEL_OK</strong>
            </div>
            <div>
              <b>Risk Status</b>
              <strong className="green-text">● TESTED</strong>
            </div>
            <div>
              <b>Evidence Status</b>
              <strong className="amber-text">△ OPEN</strong>
            </div>
            <div className="hero-card-total">
              <b>Overall Diligence</b>
              <strong>IN PROGRESS</strong>
            </div>
          </aside>
        </div>
      </section>

      <div className="diligence-shell">
        <div className="diligence-alert">
          <AlertTriangle size={18} />
          <span>
            This is a diligence shortlist, not an investment recommendation.
            <br />
            <b>Current equity budget = $0, allocations = 0 (FRONTIER_ONLY).</b>
          </span>
          <button type="button">
            Diligence Methodology <ArrowRight size={15} />
          </button>
        </div>

        <section className="diligence-section">
          <SectionHeading
            number="1"
            title="What the Model Can Decide Today"
            note="Screening asks whether an issue exists. Diligence asks what evidence would resolve it."
          />
          <div className="diligence-decision-grid">
            <article className="decision-boundary-card ready">
              <CircleCheck size={22} />
              <h3>RECRUITER-READY</h3>
              <p>
                Structured, auditable analysis across physical, commercial,
                credit and downside lenses.
              </p>
              <b>YES · DILIGENCE WORKPLAN</b>
            </article>
            <article className="decision-boundary-card stop">
              <CircleAlert size={22} />
              <h3>TRANSACTION-READY</h3>
              <p>
                Exact PPA, sponsor, lender, site, legal and tax evidence remains
                unresolved.
              </p>
              <b>NO · OPEN EVIDENCE</b>
            </article>
            <article className="decision-boundary-card neutral">
              <Target size={22} />
              <h3>DECISION BOUNDARY</h3>
              <p>
                FRONTIER_ONLY pricing, standardized debt and governed scenarios
                stay clearly labeled.
              </p>
              <b>INDETERMINATE</b>
            </article>
            <article className="decision-boundary-card capital">
              <WalletCards size={22} />
              <h3>CAPITAL CONTROL</h3>
              <p>
                Capital allocation is deliberately disabled until commercial
                evidence is sufficient.
              </p>
              <b>$0 ALLOCATED</b>
            </article>
          </div>
          <div className="diligence-claim-strip">
            <span>
              <Check size={15} /> 20 selected = 19 diligence + 1 technical track
            </span>
            <span>
              <Check size={15} /> 19 economics-ready records
            </span>
            <span>
              <X size={15} /> NOT AN INVESTMENT RANKING
            </span>
            <span>
              <Check size={15} /> Transaction evidence: OPEN
            </span>
          </div>
        </section>

        <section className="diligence-section">
          <SectionHeading
            number="2"
            title="From 20 Selected Records to the Next Diligence Step"
            note="Every reduction in the universe is explicit and auditable."
          />
          <div className="diligence-funnel-layout">
            <div className="diligence-funnel">
              {FUNNEL_STEPS.map(([value, label, FunnelIcon], index) => {
                return (
                  <div className="funnel-step" key={label}>
                    <strong>{value}</strong>
                    <FunnelIcon size={21} />
                    <span>{label}</span>
                    {index < 3 ? (
                      <ArrowRight className="funnel-arrow" size={17} />
                    ) : null}
                  </div>
                );
              })}
            </div>
            <div className="technical-side-track">
              <span className="track-line" />
              <AlertTriangle size={19} />
              <div>
                <b>1 TECHNICAL VALIDATION TRACK</b>
                <strong>FPEL Arisudhana</strong>
                <small>TECHNICAL_DATA_BLOCKED · ENGINEERING_VALIDATION</small>
              </div>
            </div>
          </div>
        </section>

        <section className="diligence-section">
          <SectionHeading
            number="3"
            title="Four Questions Before a Transaction Decision"
            note="Status is text plus signal; no conclusion is inferred from color alone."
          />
          <div className="diligence-lenses-grid">
            <Lens
              icon={Zap}
              title="Technical"
              status="UNDER_REVIEW"
              tone="technical"
              value={70}
              items={[
                'Resource: Good',
                'Design: Adequate',
                'Site: Verified',
                'Constraints: Pending',
              ]}
            />
            <Lens
              icon={Handshake}
              title="Commercial"
              status="INDETERMINATE"
              tone="commercial"
              value={40}
              items={[
                'PPA Status: Open',
                'Sponsor Floor: Missing',
                'Tariff Frontier: Known',
                'Negotiation: Pending',
              ]}
            />
            <Lens
              icon={Landmark}
              title="Credit"
              status="MODEL_OK"
              tone="credit"
              value={85}
              items={[
                'DSCR: Model OK',
                'LLCR: Model OK',
                'PLCR: Model OK',
                'Leverage: OK',
              ]}
            />
            <Lens
              icon={FolderOpen}
              title="Evidence"
              status="OPEN"
              tone="evidence"
              value={35}
              items={[
                'Missing Docs: 6',
                'Outstanding RFI: 8',
                'Third-party Verify: 0',
                'Data Quality: Good',
              ]}
            />
          </div>
        </section>

        <section className="diligence-section shortlist-section">
          <SectionHeading
            number="4"
            title="Diligence Priority Shortlist"
            note="Analytical shortlist only. Click a record to open its diligence file."
          />
          <div className="diligence-filters" aria-label="Diligence filters">
            <label>
              <Globe2 size={15} /> Country
              <select
                value={country}
                onChange={(event) => setCountry(event.target.value)}
              >
                {countries.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>
            <label>
              <SlidersHorizontal size={15} /> Commercial
              <select
                value={commercial}
                onChange={(event) => setCommercial(event.target.value)}
              >
                <option>All commercial statuses</option>
                <option>INSUFFICIENT_DATA</option>
                <option>FEASIBLE_NEGOTIATION_ZONE</option>
                <option>EMPTY_NEGOTIATION_ZONE</option>
              </select>
            </label>
            <label>
              <Target size={15} /> Next action
              <select
                value={action}
                onChange={(event) => setAction(event.target.value)}
              >
                <option>All next actions</option>
                {ACTIONS.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>
            <span className="filter-result">
              {filteredRecords.length} of 19 records
            </span>
          </div>
          {loading ? (
            <div className="diligence-loading">
              Loading frozen diligence payload…
            </div>
          ) : error ? (
            <EmptyState />
          ) : (
            <div className="shortlist-table-wrap">
              <table className="shortlist-table">
                <caption className="sr-only">
                  Diligence priority shortlist
                </caption>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Project</th>
                    <th>Country</th>
                    <th>
                      Capacity
                      <br />
                      (MW)
                    </th>
                    <th>Technical</th>
                    <th>Commercial</th>
                    <th>Credit</th>
                    <th>Risk</th>
                    <th>Evidence</th>
                    <th>Next action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRecords.map((record, index) => (
                    <tr
                      key={record.project_id}
                      className={
                        record.project_id === GO_MALL ? 'selected-row' : ''
                      }
                    >
                      <td>{index + 1}</td>
                      <td>
                        <button
                          type="button"
                          className="row-open"
                          onClick={() => openRecord(record.project_id)}
                        >
                          <strong>{record.project_name}</strong>
                        </button>
                        <small>{record.project_id}</small>
                      </td>
                      <td>{record.country}</td>
                      <td>{formatNumber(record.capacityMw, 3)}</td>
                      <td>
                        <StatusPill
                          value={record.technicalLabel}
                          tone={
                            record.technicalLabel === 'UNDER_REVIEW'
                              ? 'amber'
                              : 'green'
                          }
                        />
                      </td>
                      <td>
                        <StatusPill
                          value={record.commercialLabel}
                          tone="amber"
                        />
                      </td>
                      <td>
                        <StatusPill
                          value={record.creditLabel}
                          tone={
                            record.creditLabel === 'MODEL_OK'
                              ? 'green'
                              : 'amber'
                          }
                        />
                      </td>
                      <td>
                        <StatusPill
                          value={record.riskLabel}
                          tone={
                            record.riskLabel === 'CRITICAL_STRESS'
                              ? 'red'
                              : 'neutral'
                          }
                        />
                      </td>
                      <td>
                        <StatusPill value={record.evidenceLabel} tone="amber" />
                      </td>
                      <td>
                        <StatusPill
                          value={record.nextAction}
                          tone={
                            record.nextAction === 'COD_TIMING_REVIEW'
                              ? 'red'
                              : record.nextAction === 'TRANSACTION_EVIDENCE'
                                ? 'amber'
                                : 'green'
                          }
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr>
                    <td colSpan={3}>Filtered analytical records</td>
                    <td>
                      {formatNumber(
                        filteredRecords.reduce(
                          (sum, record) => sum + record.capacityMw,
                          0,
                        ),
                        3,
                      )}
                    </td>
                    <td colSpan={6}>
                      Total universe: 19 diligence records · Technical track
                      excluded
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          )}
        </section>

        <section className="diligence-section file-section">
          <SectionHeading
            number="5"
            title="Selected Project Diligence File"
            note="Default selection: GO Mall Vietnam. No finance recomputation in this drawer."
          />
          <div className="diligence-file-layout">
            <div className="diligence-file-card">
              <div className="file-card-heading">
                <div>
                  <span>PROJECT FILE</span>
                  <h3>
                    {selected?.project_name ?? 'GO Mall Vietnam portfolio'}
                  </h3>
                  <small>
                    {selected?.project_id ?? GO_MALL} ·{' '}
                    {selected?.country ?? 'Vietnam'}
                  </small>
                </div>
                <StatusPill value="IN PROGRESS" tone="amber" />
              </div>
              <div className="file-grid">
                <div>
                  <span>Identity</span>
                  <b>GO Mall Vietnam</b>
                  <small>Ho Chi Minh City, Vietnam</small>
                </div>
                <div>
                  <span>Technical</span>
                  <b>PASS_WITHIN_SCREENING_BAND</b>
                  <small>9.000 MW · 13.000 GWh · 1,444.44 kWh/kWp</small>
                </div>
                <div>
                  <span>Commercial</span>
                  <b>INSUFFICIENT_DATA</b>
                  <small>FRONTIER_ONLY · Customer ceiling VND 3,460/kWh</small>
                </div>
                <div>
                  <span>Credit</span>
                  <b>POSITIVE_STANDARDIZED_DEBT</b>
                  <small>Supportable debt ≈ $0.529m · Binding PLCR</small>
                </div>
                <div>
                  <span>Risk</span>
                  <b>CRITICAL_STRESS</b>
                  <small>COD Delay = 0x · Combined Downside = 0x</small>
                </div>
                <div>
                  <span>Evidence</span>
                  <b>OPEN</b>
                  <small>Commercial and transaction evidence incomplete</small>
                </div>
              </div>
              <div className="next-action-box">
                <div>
                  <Target size={18} />
                  <span>Next Action (Primary)</span>
                </div>
                <strong>COD_TIMING_REVIEW</strong>
                <small>
                  Validate operating date, interim debt service and sponsor
                  support before any commitment.
                </small>
              </div>
              <div className="file-links">
                <Link href="/energy">
                  Energy &amp; Physical <ArrowRight size={14} />
                </Link>
                <Link href="/economics?project=VN-GY-GOMALL">
                  Economics &amp; PPA <ArrowRight size={14} />
                </Link>
                <Link href="/debt?project=VN-GY-GOMALL">
                  Debt &amp; Credit <ArrowRight size={14} />
                </Link>
                <Link href="/risk?project=VN-GY-GOMALL">
                  Risk &amp; Scenarios <ArrowRight size={14} />
                </Link>
              </div>
              <button
                className="diligence-primary-button"
                type="button"
                onClick={() => setDrawerOpen(true)}
              >
                Open Project Dossier <ArrowRight size={17} />
              </button>
            </div>
            <div className="diligence-file-side">
              <h3>Traceable Workplan</h3>
              <div>
                <CircleCheck size={17} />
                <span>Technical finding</span>
                <b>physicalStatus</b>
              </div>
              <div>
                <CircleCheck size={17} />
                <span>Commercial gap</span>
                <b>decision + ppa_mode</b>
              </div>
              <div>
                <CircleCheck size={17} />
                <span>Credit boundary</span>
                <b>debt capacity</b>
              </div>
              <div>
                <CircleCheck size={17} />
                <span>Risk trigger</span>
                <b>exact scenarios</b>
              </div>
              <div>
                <CircleCheck size={17} />
                <span>Evidence request</span>
                <b>open transaction data</b>
              </div>
              <div className="side-note">
                <Sparkles size={17} /> Every next action points back to a model
                finding.
              </div>
            </div>
          </div>
        </section>

        <section className="diligence-section evidence-section">
          <SectionHeading
            number="6"
            title="Technical Validation Track"
            note="The blocked record stays outside the economics, credit and risk-ready universe."
          />
          <div className="technical-validation-card">
            <div className="technical-icon">
              <ShieldAlert size={30} />
            </div>
            <div>
              <span>
                FPEL ARISUDHANA · {technicalRecord?.project_id ?? ARISUDHANA}
              </span>
              <h3>{technicalRecord?.project_name ?? 'FPEL Arisudhana'}</h3>
              <p>2.090 MW · 30.500 GWh · ~14,593 kWh/kWp</p>
              <StatusPill value="EXTREME_OUTLIER_BLOCK_BASE" tone="red" />
            </div>
            <div className="technical-validation-meta">
              <b>TECHNICAL_DATA_BLOCKED</b>
              <span>Next action</span>
              <strong>ENGINEERING_VALIDATION</strong>
              <small>
                Source validation, data completeness and sanity check.
              </small>
            </div>
          </div>
          <div className="technical-guardrail">
            <Check size={16} /> 1 technical-validation record · not present in
            the 19-row finance shortlist · no replacement benchmark invented.
          </div>
        </section>

        <section className="diligence-section">
          <SectionHeading
            number="7"
            title="What Evidence Would Change the Decision?"
            note="An open issue becomes useful when its resolving evidence and model impact are explicit."
          />
          <div className="evidence-grid">
            {[
              [
                FileCheck2,
                'PPA / Commercial',
                'PPA term sheet or draft',
                'Could resolve sponsor floor and commercial zone.',
                'Critical',
              ],
              [
                MapPin,
                'Customer / Load',
                'Load profile and offtaker data',
                'Could change self-consumption and tariff feasibility.',
                'Critical',
              ],
              [
                Zap,
                'Engineering / Site',
                'Independent site and design review',
                'Could validate yield and operating assumptions.',
                'High',
              ],
              [
                Landmark,
                'Financing',
                'Debt term sheet and lender feedback',
                'Could refine credit structure, not create approval.',
                'High',
              ],
              [
                LockKeyhole,
                'Legal',
                'Grid, land and contract certificates',
                'Could move evidence from OPEN to transaction-ready.',
                'Medium',
              ],
              [
                WalletCards,
                'Tax / Incentives',
                'VAT, CIT and depreciation policy',
                'Could change cash-flow assumptions and returns.',
                'Medium',
              ],
            ].map(([Icon, title, missing, impact, severity]) => {
              const EvidenceIcon = Icon as typeof Gauge;
              return (
                <article className="evidence-package" key={title as string}>
                  <EvidenceIcon size={20} />
                  <div>
                    <h3>{title as string}</h3>
                    <b>{missing as string}</b>
                    <p>{impact as string}</p>
                  </div>
                  <StatusPill
                    value={severity as string}
                    tone={
                      severity === 'Critical'
                        ? 'red'
                        : severity === 'High'
                          ? 'amber'
                          : 'green'
                    }
                  />
                </article>
              );
            })}
          </div>
        </section>

        <section className="diligence-section capital-section">
          <SectionHeading
            number="8"
            title="Why the Model Allocates $0"
            note="This is an intentional governance stop. It is not a failed allocation model."
          />
          <div className="capital-control-layout">
            <div className="capital-zero">
              <WalletCards size={28} />
              <strong>$0</strong>
              <span>Equity budget</span>
              <small>$0 spent · $0 remaining · 0 selected for allocation</small>
            </div>
            <div className="capital-flow">
              <div>
                <FileSearch size={20} />
                <b>Evidence</b>
                <small>OPEN</small>
              </div>
              <ArrowRight size={19} />
              <div>
                <ShieldCheck size={20} />
                <b>Resolve gaps</b>
                <small>Required</small>
              </div>
              <ArrowRight size={19} />
              <div className="stop-flow">
                <LockKeyhole size={20} />
                <b>Capital</b>
                <small>STOPPED</small>
              </div>
            </div>
            <div className="capital-rules">
              <p>
                <Check size={15} /> PPA mode = FRONTIER_ONLY
              </p>
              <p>
                <Check size={15} /> Decision =
                INDETERMINATE_MISSING_COMMERCIAL_DATA
              </p>
              <p>
                <Check size={15} /> Allocation status = DISABLED_FRONTIER_ONLY
              </p>
            </div>
          </div>
        </section>

        <section className="diligence-section context-section">
          <SectionHeading
            number="9"
            title="A Diligence Shortlist — Not a Portfolio"
            note="No synthetic investment score, top-project ranking or allocation recommendation is created."
          />
          <div className="context-grid">
            <div className="context-kpis">
              <Kpi
                icon={ClipboardCheck}
                value="19"
                label="Ready diligence records"
              />
              <Kpi
                icon={Globe2}
                value={String(
                  new Set(financeRecords.map((record) => record.country))
                    .size || 7,
                )}
                label="Countries"
              />
              <Kpi
                icon={Zap}
                value={formatNumber(selectedCapacity || 129.853, 3) + ' MW'}
                label="Selected capacity"
              />
              <Kpi
                icon={BarChart3}
                value={formatNumber(selectedGeneration || 148.221, 3) + ' GWh'}
                label="Observed generation"
              />
            </div>
            <div className="distributions">
              <Distribution
                title="Commercial status"
                rows={commercialCounts}
                total={financeRecords.length || 19}
              />
              <Distribution
                title="Next actions"
                rows={actionCounts}
                total={financeRecords.length || 19}
              />
            </div>
          </div>
        </section>

        <section className="diligence-section">
          <SectionHeading
            number="10"
            title="Decision Hierarchy"
            note="Recruiter-ready does not mean transaction-ready."
          />
          <div className="decision-hierarchy">
            {[
              [
                'Physical usable?',
                'YES · except separate Arisudhana track',
                'green',
              ],
              ['Economics modelable?', 'YES · 19 records', 'green'],
              ['Commercial resolved?', 'NO · sponsor floor missing', 'amber'],
              ['Debt supportable?', 'GO Mall standardized case only', 'amber'],
              ['Downside breakpoints?', 'COD + combined stress = 0x', 'red'],
              ['Transaction evidence complete?', 'NO · OPEN', 'red'],
              ['Capital approval?', 'NO · $0 allocated', 'neutral'],
            ].map(([question, answer, tone], index) => (
              <div key={question}>
                <span>{index + 1}</span>
                <b>{question}</b>
                <ArrowRight size={16} />
                <strong className={tone}>{answer}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="diligence-section boundaries-section">
          <SectionHeading
            number="11"
            title="Model / Claim Boundaries"
            note="The analytical surface is useful because it states where the evidence stops."
          />
          <div className="claims-grid">
            <article className="claim-card can">
              <h3>
                <Check size={18} /> What we can claim
              </h3>
              <ul>
                <li>Diligence priority shortlist</li>
                <li>Commercial negotiation shortlist</li>
                <li>Open analytical issues and next actions</li>
                <li>Structured physical, credit and risk findings</li>
                <li>$0 allocation and indeterminate decision</li>
              </ul>
            </article>
            <article className="claim-card cannot">
              <h3>
                <X size={18} /> What we cannot claim
              </h3>
              <ul>
                <li>Investment approval or portfolio recommendation</li>
                <li>Lender commitment or bankability</li>
                <li>Actual PPA terms or sponsor approval</li>
                <li>Legal, tax or technical approval</li>
                <li>Realized future performance or losses</li>
              </ul>
            </article>
            <article className="trace-card">
              <h3>
                <Database size={18} /> Can every decision be traced?
              </h3>
              <p>
                <b>Project identity</b> → frozen project master
              </p>
              <p>
                <b>Technical</b> → physical QA status
              </p>
              <p>
                <b>Commercial</b> → PPA mode + decision
              </p>
              <p>
                <b>Credit</b> → debt capacity + coverage
              </p>
              <p>
                <b>Risk</b> → exact governed scenarios
              </p>
              <p>
                <b>Action</b> → controlled taxonomy
              </p>
            </article>
          </div>
        </section>

        <section className="diligence-section handoff-section">
          <SectionHeading
            number="12"
            title="Diligence → Model / Evidence Handoff"
            note="Carry the issue register forward; do not carry an invented investment conclusion."
          />
          <div className="handoff-flow">
            <div>
              <ClipboardCheck size={24} />
              <b>Diligence</b>
              <small>this page</small>
            </div>
            <ArrowRight size={22} />
            <div>
              <Database size={24} />
              <b>Model &amp; Evidence</b>
              <small>page 8</small>
            </div>
            <div className="handoff-list">
              <p>
                <Check size={15} /> Diligence status and evidence register
              </p>
              <p>
                <Check size={15} /> Priority actions and owner questions
              </p>
              <p>
                <Check size={15} /> Technical validation exception
              </p>
            </div>
            <Link href="#top">
              Review traceability <ArrowRight size={15} />
            </Link>
          </div>
        </section>
      </div>

      <section className="diligence-takeaway">
        <div>
          <SectionHeading number="13" title="Recruiter Takeaway" />
          <h2>
            Professional diligence means knowing what the model can say — and
            what evidence must come next.
          </h2>
          <ul>
            <li>Evidence-driven decisioning</li>
            <li>No over-claiming bankability</li>
            <li>Rigorous data governance</li>
            <li>Focus capital only when ready</li>
          </ul>
        </div>
        <Link href="/risk?project=VN-GY-GOMALL">
          Continue to Model &amp; Evidence <ArrowRight size={17} />
        </Link>
      </section>

      {drawerOpen && selected ? (
        <div className="diligence-drawer-backdrop">
          <dialog open className="diligence-drawer" aria-label="Diligence file">
            <button
              type="button"
              className="drawer-close"
              onClick={() => setDrawerOpen(false)}
              aria-label="Close diligence file"
            >
              <X size={20} />
            </button>
            <span className="drawer-kicker">
              DILIGENCE FILE · {selected.country}
            </span>
            <h2>{selected.project_name}</h2>
            <small>{selected.project_id}</small>
            <div className="drawer-status-grid">
              <div>
                <span>Technical</span>
                <b>PASS_WITHIN_SCREENING_BAND</b>
              </div>
              <div>
                <span>Commercial</span>
                <b>INSUFFICIENT_DATA</b>
              </div>
              <div>
                <span>Credit</span>
                <b>{selected.creditLabel}</b>
              </div>
              <div>
                <span>Risk</span>
                <b>{selected.riskLabel}</b>
              </div>
              <div>
                <span>Evidence</span>
                <b>OPEN</b>
              </div>
              <div>
                <span>Next Action</span>
                <b>{selected.nextAction}</b>
              </div>
            </div>
            <h3>What would change this file?</h3>
            <p>
              PPA term sheet, sponsor floor evidence, COD timing support and
              third-party validation are the next controlled inputs.
            </p>
            <div className="drawer-nav">
              <Link href="/energy">
                Energy <ArrowRight size={14} />
              </Link>
              <Link href={`/economics?project=${selected.project_id}`}>
                Economics <ArrowRight size={14} />
              </Link>
              <Link href={`/debt?project=${selected.project_id}`}>
                Debt <ArrowRight size={14} />
              </Link>
              <Link href={`/risk?project=${selected.project_id}`}>
                Risk <ArrowRight size={14} />
              </Link>
            </div>
          </dialog>
        </div>
      ) : null}

      <footer className="diligence-footer">
        <span>Model: V5.1.3 (Frozen)</span>
        <span>Data as of: 31 Dec 2024</span>
        <span>Evidence: OPEN</span>
        <span>THIS PAGE: DILIGENCE · SHORTLIST ONLY</span>
      </footer>
    </main>
  );
}


