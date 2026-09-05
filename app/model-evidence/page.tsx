'use client';

import Link from 'next/link';
import {
  Archive,
  ArrowDown,
  ArrowRight,
  BadgeCheck,
  BookOpen,
  Check,
  CheckCircle2,
  ChevronDown,
  CircleAlert,
  ClipboardCheck,
  Cloud,
  Code2,
  Copy,
  Database,
  ExternalLink,
  FileCheck2,
  FileKey2,
  FileText,
  Fingerprint,
  GitBranch,
  GitCommitHorizontal,
  Globe2,
  Info,
  Layers3,
  Link2,
  LockKeyhole,
  Network,
  PackageCheck,
  RefreshCcw,
  ShieldCheck,
  ShieldX,
  Table2,
  TestTube2,
  Workflow,
  XCircle,
  Zap,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { useState } from 'react';
import projectsSource from '../../public/data/projects.json';
import reconciliationSource from '../../public/data/reconciliation.json';

const MODEL_SHA = 'ff69e15d211ff1abc88200574242ed2f1db49074';
const MODEL_TAG = 'v5.1.3-recruiter-final';
const REPO = 'https://github.com/susayold/vietgreen-ci-solar-project-finance';
const DRIVE =
  'https://docs.google.com/document/d/1koSgbc1Akic6cVDFD1svmuVN9gSq8qSGUw2obfHYN80/edit';

type RemoteProject = {
  project_id: string;
  project_name: string;
  country: string;
  technicalDataBlocked?: boolean;
  physicalStatus?: string;
  ppa_mode?: string;
};

type Reconciliation = {
  label: string;
  expected: string;
  actual: string;
  ok: boolean;
};

type IconProps = { icon: LucideIcon; size?: number };

const workbookGroups = {
  Governance: [
    '00_Cover',
    '01_Readme',
    '06_Source_Register',
    '07_Conflict_Register',
    '24_Claim_Governance',
    '25_Release_Gates',
    '26_QA',
    '27_Reconciliation',
  ],
  'Data / Physical': [
    '02_Project_Master',
    '03_Physical_QA',
    '04_Resolved_Input_View',
    '05_Assumption_Overlay',
    '08_Selected_Data_Audit',
    '09_Yield_Audit',
    '10_Load_Match',
  ],
  'Market / Assumptions': [
    '11_Tariff',
    '12_FX',
    '13_Tax',
    '14_Rates',
    '15_Discount_Rates',
    '16_CAPEX',
    '17_OPEX',
  ],
  'Finance / Decision': [
    '18_Base_CFADS',
    '19_Debt_Sizing',
    '20_Debt_Schedule',
    '21_PPA_Frontier',
    '22_Scenarios',
    '23_Portfolio',
  ],
} as const;

const architecture = [
  ['54', 'Candidate history', 'EVIDENCE', Database],
  ['441', 'Preserved observations', 'EVIDENCE', Archive],
  ['20', 'Selected projects', 'PHYSICAL', ClipboardCheck],
  ['19 + 1', 'Physical QA', 'PHYSICAL', ShieldCheck],
  ['19 × 8,760', '166,440 hourly rows', 'FINANCE', Table2],
  ['CFADS', 'Base economics', 'FINANCE', FileCheck2],
  ['Coverage', 'Debt capacity', 'FINANCE', Network],
  ['Frontier', 'PPA terms', 'FINANCE', GitBranch],
  ['171', 'Scenario rows', 'RISK', TestTube2],
  ['19', 'Diligence shortlist', 'DECISION', FileText],
  ['28', 'Workbook + website', 'GOVERNANCE', BookOpen],
  ['QA', 'Reconciliation', 'GOVERNANCE', BadgeCheck],
  ['V5.1.3', 'Frozen release', 'GOVERNANCE', LockKeyhole],
] as const;

const evidenceClasses = [
  [
    'Observed',
    'OBSERVED_PUBLIC_OR_SOURCE_REPORTED',
    'Installed capacity, published generation, developer, offtaker and source lineage.',
    Database,
    'green',
  ],
  [
    'Derived',
    'DERIVED',
    'Specific yield, country aggregates, calculated ratios and resolved fields.',
    Code2,
    'blue',
  ],
  [
    'Benchmark',
    'BENCHMARK_ASSUMPTION',
    'Standardized credit policy, market reference ceiling and underwriting benchmarks.',
    Layers3,
    'gold',
  ],
  [
    'Analyst',
    'ANALYST_ASSUMPTION',
    'Operating archetype, load proxy and disclosed model overlays.',
    Workflow,
    'teal',
  ],
  [
    'Scenario',
    'SCENARIO',
    'P90 screening, CAPEX +15%, rate shock, COD delay, nonpayment and termination.',
    Zap,
    'amber',
  ],
  [
    'Not disclosed',
    'NOT_DISCLOSED',
    'Exact PPA, lender terms, confidential load, legal, tax and engineering evidence.',
    CircleAlert,
    'red',
  ],
] as const;

const controls = [
  [
    'Arisudhana extreme-outlier firewall',
    'Raw evidence preserved; technical review flagged; base economics blocked; no silent normalization.',
    'PHYSICAL_FIREWALL',
    'PASS',
    ShieldX,
    'danger',
  ],
  [
    'P90 / P99 claim control',
    'Screening factors only — not observed quantiles or bankable production guarantees.',
    'SCREENING_LABEL',
    'PASS',
    Info,
    'gold',
  ],
  [
    'Downside principal preservation',
    'Fixed-contractual and no-new-debt cases preserve opening, principal and closing schedules.',
    'PRINCIPAL_INVARIANT',
    'PASS',
    LockKeyhole,
    'green',
  ],
  [
    'Rate-shock interest repricing',
    'Floating interest can reprice while contractual principal stays fixed.',
    'RATE_REPRICING',
    'PASS',
    RefreshCcw,
    'blue',
  ],
  [
    'CAPEX stress funding',
    'CAPEX overrun and combined downside do not create automatic incremental debt.',
    'NO_NEW_DEBT',
    'PASS',
    ShieldCheck,
    'green',
  ],
  [
    'N/A ≠ 0.00x',
    'No debt service yields DSCR N/A; zero stressed CFADS with debt service yields 0.00x.',
    'NULL_SEMANTICS',
    'PASS',
    TestTube2,
    'gold',
  ],
  [
    'Missing sponsor / lender floor',
    'Missing stays missing — no historical fallback and no fake PPA marker.',
    'MISSINGNESS',
    'PASS',
    CircleAlert,
    'amber',
  ],
  [
    'Frontier-only capital control',
    'Equity budget = $0; allocation disabled; no investment recommendation.',
    'CAPITAL_STOP',
    'PASS',
    LockKeyhole,
    'danger',
  ],
] as const;

const gates = [
  ['G0', 'Source and scope frozen', 'CLEARED', 'Internal'],
  ['G1', 'Input freeze and lineage', 'CLEARED', 'Internal'],
  ['G2', 'Physical QA', 'PASS_WITH_NONBLOCKING_REVIEW', 'Internal'],
  ['G3', 'Deterministic model build', 'CLEARED', 'Internal'],
  ['G4', 'Economics / debt semantics', 'CLEARED', 'Internal'],
  ['G5', 'Scenario and claim controls', 'CLEARED', 'Internal'],
  ['G6', 'Reconciliation', 'CLEARED', 'Internal'],
  ['G7', 'Runtime identity', 'CLEARED', 'Internal'],
  ['G8', 'Diligence evidence', 'CLEARED', 'Internal'],
  ['G9', 'Recruiter release', 'CLEARED', 'Internal'],
] as const;

const sources = [
  [
    'Project master',
    'data/public/project_master_real.csv',
    'Observed project identities and source fields',
    Database,
  ],
  [
    'Raw observations',
    'data/public/raw_project_observations.csv',
    'Preserved public/source-reported observations',
    Archive,
  ],
  [
    'Resolved input view',
    'outputs/v5_1_3_model_input_view.csv',
    'Final resolved values and readiness state',
    FileCheck2,
  ],
  [
    'Physical QA',
    'validation/V5_1_3_PHYSICAL_QA.csv',
    'Screening bands and technical firewall',
    ShieldCheck,
  ],
  [
    'Energy / 8760',
    'outputs/v5_1_3_8760.csv',
    'Hourly model output for 19 ready projects',
    Table2,
  ],
  [
    'Economics / debt',
    'outputs/v5_1_3_project_economics.csv',
    'CFADS, returns, debt and coverage outputs',
    Network,
  ],
  [
    'Scenarios',
    'outputs/v5_1_3_scenarios.csv',
    '19 × 9 deterministic scenario rows',
    TestTube2,
  ],
  [
    'Release contract',
    'release/V5_1_3_STATIC_RELEASE_CONTRACT.json',
    'Frozen counts, QA and claim boundaries',
    FileKey2,
  ],
] as const;

const auditRows = [
  [
    '20 selected records',
    'Projects & Data',
    'outputs/v5_1_3_reconciliation.csv',
    'selected_research_records = 20',
    'DERIVED',
    'PASS',
  ],
  [
    '19 economics-ready',
    'Energy / Physical',
    'outputs/v5_1_3_reconciliation.csv',
    'economics_ready_records = 19',
    'DERIVED',
    'PASS',
  ],
  [
    '166,440 hourly rows',
    'Energy / Physical',
    'outputs/v5_1_3_reconciliation.csv',
    '8760_rows = 166440',
    'DERIVED',
    'PASS',
  ],
  [
    '171 scenario rows',
    'Risk & Scenarios',
    'outputs/v5_1_3_reconciliation.csv',
    'scenario_rows = 171',
    'SCENARIO',
    'PASS',
  ],
  [
    'FRONTIER_ONLY',
    'Economics & PPA',
    'outputs/v5_1_3_reconciliation.csv',
    'ppa_mode = FRONTIER_ONLY',
    'BENCHMARK_ASSUMPTION',
    'PASS',
  ],
  [
    'Arisudhana block',
    'Diligence',
    'validation/V5_1_3_PHYSICAL_QA.csv',
    'technicalDataBlocked = true',
    'OBSERVED_PUBLIC_OR_SOURCE_REPORTED',
    'PASS',
  ],
  [
    '$0 allocation',
    'Diligence',
    'CLAIM_GOVERNANCE.md',
    'equity_budget = 0 under frontier-only',
    'ANALYST_ASSUMPTION',
    'PASS',
  ],
] as const;

function Header() {
  return (
    <header className="model-header">
      <Link className="model-brand" href="/">
        <span className="model-brand-mark">▥</span>
        <span>
          <strong>VietGreen</strong>
          <small>C&amp;I Solar Project Finance</small>
        </span>
      </Link>
      <nav aria-label="Primary navigation">
        <Link href="/">Overview</Link>
        <Link href="/projects">Projects &amp; Data</Link>
        <Link href="/energy">Energy &amp; Physical</Link>
        <Link href="/economics">Finance</Link>
        <Link href="/diligence">Diligence</Link>
        <Link className="active" href="/model-evidence">
          Model &amp; Evidence
        </Link>
      </nav>
      <span className="model-release">V5.1.3 · Frozen Model</span>
    </header>
  );
}

function Icon({ icon: IconComponent, size = 20 }: IconProps) {
  return <IconComponent size={size} strokeWidth={1.7} />;
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
    <div className="model-heading">
      <div>
        <span className="model-index">{number}</span>
        <h2>{title}</h2>
      </div>
      {note ? <p>{note}</p> : null}
    </div>
  );
}

function Status({ value, tone = 'green' }: { value: string; tone?: string }) {
  return (
    <span className={`model-status ${tone}`}>
      <CheckCircle2 size={12} />
      {value.replaceAll('_', ' ')}
    </span>
  );
}

function CopyButton({ value, label }: { value: string; label: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      className="copy-button"
      type="button"
      aria-label={`${label}: copy full value`}
      onClick={() => {
        void navigator.clipboard.writeText(value).then(() => {
          setCopied(true);
          window.setTimeout(() => setCopied(false), 1500);
        });
      }}
    >
      <Copy size={13} />
      {copied ? 'Copied' : label}
    </button>
  );
}

function LinkButton({
  href,
  children,
}: {
  href: string;
  children: React.ReactNode;
}) {
  return (
    <a className="outline-button" href={href} target="_blank" rel="noreferrer">
      {children}
      <ExternalLink size={13} />
    </a>
  );
}

export default function ModelEvidencePage() {
  // Keep the evidence page fully rendered during the build. GitHub Pages has
  // no Vinext server runtime to hydrate a loading shell after deployment.
  const projects = projectsSource.projects as RemoteProject[];
  const reconciliation = reconciliationSource.rows as Reconciliation[];
  const [workbookGroup, setWorkbookGroup] =
    useState<keyof typeof workbookGroups>('Governance');
  const [auditFilter, setAuditFilter] = useState('All');
  const [showAllSources, setShowAllSources] = useState(false);

  const reconciliationPass = reconciliation.every((row) => row.ok);
  const filteredAudit = auditRows.filter(
    (row) => auditFilter === 'All' || row[1] === auditFilter,
  );
  const displayedSources = showAllSources ? sources : sources.slice(0, 5);

  return (
    <main className="model-page">
      <Header />

      <section className="model-hero">
        <div className="model-grid-texture" />
        <div className="model-hero-inner">
          <div className="model-hero-copy">
            <p className="model-eyebrow">
              MODEL GOVERNANCE · EVIDENCE LINEAGE · REPRODUCIBILITY
            </p>
            <h1>
              Trust the Numbers.
              <br />
              Trace the Evidence.
            </h1>
            <p>
              The final control layer links public evidence, resolved model
              inputs, analytical outputs, QA tests and release identity so every
              major recruiter-facing claim can be traced back to the frozen
              V5.1.3 model.
            </p>
            <div className="model-hero-actions">
              <a className="gold-button" href="#architecture">
                Trace the Model <ArrowDown size={15} />
              </a>
              <a className="dark-button" href="#identity">
                Inspect Release Identity <ArrowDown size={15} />
              </a>
            </div>
          </div>
          <div className="model-hero-card">
            <div className="model-card-label">SELECTED RELEASE</div>
            <div className="model-hero-version">
              <strong>V5.1.3</strong>
              <span>FROZEN MODEL</span>
            </div>
            <div className="model-hero-kpis">
              <div>
                <b>28</b>
                <span>WORKBOOK SHEETS</span>
              </div>
              <div>
                <b>26 / 26</b>
                <span>REGRESSION CONTROLS</span>
              </div>
              <div>
                <b>26 / 26</b>
                <span>SEMANTIC CONTROLS</span>
              </div>
            </div>
            <div className="model-hero-pass">
              <CheckCircle2 size={18} />
              <strong>DETERMINISTIC BUILD: PASS</strong>
            </div>
          </div>
        </div>
      </section>

      <div className="model-shell">
        <div className="model-notice">
          <Info size={17} />
          <span>
            This page describes the frozen analytical release and its evidence
            boundaries. Recruiter-ready does not mean transaction-ready.
          </span>
          <span className="notice-tag">REMOTE ONLY</span>
        </div>

        <section className="model-section" id="identity">
          <SectionHeading
            number="1"
            title="One Frozen Analytical Release"
            note="All current analytical pages reconcile to one model identity."
          />
          <div className="identity-grid">
            <article className="model-panel identity-card">
              <div className="panel-kicker">
                <Fingerprint size={19} /> MODEL IDENTITY
              </div>
              <div className="identity-main">
                <div>
                  <span>MODEL VERSION</span>
                  <strong>V5.1.3</strong>
                </div>
                <div>
                  <span>STATUS</span>
                  <Status value="FINAL_RECRUITER_RELEASE" />
                </div>
              </div>
              <div className="identity-row">
                <span>TAG</span>
                <code>{MODEL_TAG}</code>
              </div>
              <div className="identity-row sha-row">
                <span>MODEL SHA</span>
                <code>{MODEL_SHA}</code>
                <CopyButton value={MODEL_SHA} label="Copy SHA" />
              </div>
              <div className="identity-actions">
                <LinkButton href={`${REPO}/commit/${MODEL_SHA}`}>
                  Open Frozen Commit
                </LinkButton>
                <LinkButton href={`${REPO}/releases/tag/${MODEL_TAG}`}>
                  Open Release
                </LinkButton>
              </div>
            </article>
            <article className="model-panel claim-card">
              <div className="panel-kicker">
                <BadgeCheck size={19} /> RELEASE CLAIM BOUNDARY
              </div>
              <div className="claim-grid">
                <div>
                  <span>RECRUITER READY</span>
                  <b className="yes">YES</b>
                </div>
                <div>
                  <span>TRANSACTION READY</span>
                  <b className="no">NO</b>
                </div>
                <div>
                  <span>BANKABLE</span>
                  <b className="no">NO</b>
                </div>
                <div>
                  <span>LENDER APPROVED</span>
                  <b className="no">NO</b>
                </div>
                <div>
                  <span>IC APPROVED</span>
                  <b className="no">NO</b>
                </div>
              </div>
              <p className="boundary-quote">
                Recruiter-ready means the public-data analytical package is
                controlled and auditable. It does not mean the underlying
                transaction has completed commercial, legal, lender, tax or
                technical diligence.
              </p>
            </article>
          </div>
        </section>

        <section className="model-section" id="architecture">
          <SectionHeading
            number="2"
            title="From Public Evidence to a Controlled Decision"
            note="The analytical chain stays visible from source evidence to frozen release."
          />
          <div className="architecture-groups">
            <span>A. EVIDENCE</span>
            <span>B. PHYSICAL</span>
            <span>C. FINANCE</span>
            <span>D. RISK</span>
            <span>E. DECISION</span>
            <span>F. GOVERNANCE</span>
          </div>
          <div className="architecture-flow">
            {architecture.map(([value, label, group, NodeIcon], index) => (
              <div className="architecture-node" key={label}>
                <div className="node-top">
                  <Icon icon={NodeIcon} size={18} />
                  <small>{group}</small>
                </div>
                <strong>{value}</strong>
                <span>{label}</span>
                {index < architecture.length - 1 ? (
                  <ArrowRight className="node-arrow" size={15} />
                ) : null}
              </div>
            ))}
          </div>
          <div className="model-callout">
            <Workflow size={17} />
            <span>
              Every stage preserves its source, class, readiness state and
              consuming page. The release is a controlled decision surface — not
              a raw data dump.
            </span>
          </div>
        </section>

        <section className="model-section">
          <SectionHeading
            number="3"
            title="Evidence Is Typed Before It Is Used"
            note="A model input can be useful without pretending it was observed."
          />
          <div className="evidence-grid">
            {evidenceClasses.map(
              ([title, key, description, EvidenceIcon, tone]) => (
                <article className={`evidence-card ${tone}`} key={key}>
                  <Icon icon={EvidenceIcon} size={22} />
                  <span className="evidence-title">{title}</span>
                  <code>{key}</code>
                  <p>{description}</p>
                </article>
              ),
            )}
          </div>
        </section>

        <section className="model-section">
          <SectionHeading
            number="4"
            title="Every Final Input Has an Origin"
            note="Resolved input view: outputs/v5_1_3_model_input_view.csv"
          />
          <div className="lineage-grid">
            <article className="model-panel lineage-panel">
              <div className="lineage-flow">
                <div>
                  <span>FIELD</span>
                  <strong>Installed Capacity</strong>
                  <small>Observed / source</small>
                </div>
                <ArrowRight size={16} />
                <div>
                  <span>DERIVATION</span>
                  <strong>Resolved input view</strong>
                  <small>Overlay + readiness</small>
                </div>
                <ArrowRight size={16} />
                <div>
                  <span>FINAL VALUE</span>
                  <strong>9.000 MW</strong>
                  <small>GO Mall Vietnam</small>
                </div>
                <ArrowRight size={16} />
                <div>
                  <span>STATUS</span>
                  <Status value="READY" />
                </div>
              </div>
              <div className="lineage-table">
                <div>
                  <span>Annual Generation</span>
                  <b>13.000 GWh</b>
                  <em>OBSERVED</em>
                </div>
                <div>
                  <span>Specific Yield</span>
                  <b>1,444 kWh/kWp</b>
                  <em>DERIVED</em>
                </div>
                <div>
                  <span>Annual Load</span>
                  <b>Analyst-derived proxy</b>
                  <em>ANALYST</em>
                </div>
                <div>
                  <span>P90 / P99</span>
                  <b>Screening bands</b>
                  <em>SCENARIO</em>
                </div>
                <div>
                  <span>Customer Ceiling</span>
                  <b>VND 3,460 /kWh</b>
                  <em>BENCHMARK</em>
                </div>
                <div>
                  <span>Exact PPA</span>
                  <b>Not disclosed</b>
                  <em className="red-text">NOT DISCLOSED</em>
                </div>
              </div>
            </article>
            <article className="model-panel trace-panel">
              <div className="panel-kicker">
                <Link2 size={18} /> FEATURED FAIL-CLOSED TRACE
              </div>
              <h3>FPEL Arisudhana</h3>
              <div className="trace-step">
                <span>Source generation</span>
                <b>30.5 GWh</b>
                <small>Source-reported</small>
              </div>
              <ArrowDown size={15} />
              <div className="trace-step">
                <span>Derived yield</span>
                <b>~14,593 kWh/kWp</b>
                <small>Extreme outlier</small>
              </div>
              <ArrowDown size={15} />
              <div className="trace-step danger-step">
                <span>Physical firewall</span>
                <b>EXTREME OUTLIER</b>
                <small>Technical review required</small>
              </div>
              <ArrowDown size={15} />
              <div className="trace-step">
                <span>Resolved readiness</span>
                <b>TECHNICAL_DATA_BLOCKED</b>
                <small>Economics excluded</small>
              </div>
            </article>
          </div>
        </section>

        <section className="model-section">
          <SectionHeading
            number="5"
            title="28-Sheet Recruiter Model"
            note="The V5.1.3 release workbook mirrors the full analytical chain."
          />
          <div className="workbook-layout">
            <div
              className="workbook-tabs"
              role="tablist"
              aria-label="Workbook groups"
            >
              {Object.keys(workbookGroups).map((group) => (
                <button
                  className={workbookGroup === group ? 'selected' : ''}
                  key={group}
                  type="button"
                  onClick={() =>
                    setWorkbookGroup(group as keyof typeof workbookGroups)
                  }
                >
                  {group}
                  <span>
                    {
                      workbookGroups[group as keyof typeof workbookGroups]
                        .length
                    }
                  </span>
                </button>
              ))}
            </div>
            <div className="sheet-grid">
              {workbookGroups[workbookGroup].map((sheet, index) => (
                <div className="sheet-card" key={sheet}>
                  <small>{String(index + 1).padStart(2, '0')}</small>
                  <strong>{sheet}</strong>
                  <span>{workbookGroup}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="legacy-warning">
            <CircleAlert size={17} />
            <div>
              <strong>LEGACY WORKBOOK BLOCKED</strong>
              <span>
                Do not present the older 22-sheet workbook as current V5.1.3
                evidence. Current frozen release: <b>28 sheets</b>.
              </span>
            </div>
          </div>
        </section>

        <section className="model-section">
          <SectionHeading
            number="6"
            title="The Release Must Reconcile Before It Can Be Presented"
            note="Expected and actual values are checked before a recruiter-facing surface is released."
          />
          <div className="recon-grid">
            {reconciliation.map((row) => (
              <article
                className={`recon-card ${row.ok ? 'ok' : 'fail'}`}
                key={row.label}
              >
                <span>{row.label}</span>
                <div>
                  <b>{row.actual}</b>
                  <small>/ {row.expected}</small>
                </div>
                <Status
                  value={row.ok ? 'PASS' : 'RECONCILIATION_ERROR'}
                  tone={row.ok ? 'green' : 'red'}
                />
              </article>
            ))}
          </div>
          <div className="qa-layout">
            <article className="model-panel qa-panel">
              <div className="qa-big">
                <b>26 / 26</b>
                <span>REGRESSION TESTS</span>
                <Status value="PASS" />
              </div>
              <div className="qa-big">
                <b>26 / 26</b>
                <span>SEMANTIC CONTROLS</span>
                <Status value="PASS" />
              </div>
              <div className="qa-big">
                <b>PASS</b>
                <span>DETERMINISTIC A/B BUILD</span>
                <Status value="PASS" />
              </div>
              <div className="qa-big">
                <b>{reconciliationPass ? 'PASS' : 'HOLD'}</b>
                <span>RELEASE VALIDATION</span>
                <Status
                  value={reconciliationPass ? 'PASS' : 'RECONCILIATION_ERROR'}
                  tone={reconciliationPass ? 'green' : 'red'}
                />
              </div>
            </article>
            <article className="model-panel qa-note">
              <PackageCheck size={25} />
              <h3>Release control</h3>
              <p>
                Selected 20, economics-ready 19, technical block 1, 166,440
                hourly rows, 171 scenarios and FRONTIER_ONLY all reconcile to
                the frozen release contract.
              </p>
              <div className="qa-note-row">
                <Check size={15} />
                No silently substituted zeros
              </div>
              <div className="qa-note-row">
                <Check size={15} />
                No moving model tag
              </div>
            </article>
          </div>
        </section>

        <section className="model-section">
          <SectionHeading
            number="7"
            title="Tests Protect Meaning — Not Just Code Execution"
            note="Eight semantic controls keep outputs from becoming unsupported claims."
          />
          <div className="controls-grid">
            {controls.map(
              ([title, description, invariant, status, ControlIcon, tone]) => (
                <article className={`control-card ${tone}`} key={invariant}>
                  <div className="control-icon">
                    <Icon icon={ControlIcon} size={19} />
                  </div>
                  <div>
                    <h3>{title}</h3>
                    <p>{description}</p>
                    <div className="control-meta">
                      <code>{invariant}</code>
                      <Status value={status} />
                    </div>
                  </div>
                </article>
              ),
            )}
          </div>
        </section>

        <section className="model-section">
          <SectionHeading
            number="8"
            title="Release Gates Separate Model Quality From External Approval"
            note="G0–G9 cleared; G2 is a non-blocking physical review."
          />
          <div className="gates-layout">
            <article className="model-panel gate-panel">
              <div className="gate-timeline">
                {gates.map(([id, label, status]) => (
                  <div
                    className={`gate-row ${id === 'G2' ? 'highlight' : ''}`}
                    key={id}
                  >
                    <span className="gate-id">{id}</span>
                    <div>
                      <strong>{label}</strong>
                      <small>
                        {id === 'G2'
                          ? 'One physical source-reported outlier remains under engineering review.'
                          : 'Internal release gate'}
                      </small>
                    </div>
                    <Status
                      value={status}
                      tone={id === 'G2' ? 'gold' : 'green'}
                    />
                  </div>
                ))}
              </div>
            </article>
            <div className="external-gates">
              <article className="model-panel">
                <div className="panel-kicker">
                  <ShieldX size={18} /> INTERNAL RELEASE GATES
                </div>
                <strong className="gate-headline">
                  CLEARED FOR RECRUITER RELEASE
                </strong>
                <p>
                  Model QA, reconciliation, claim controls and runtime identity
                  are internally cleared.
                </p>
              </article>
              <article className="model-panel external-card">
                <div className="panel-kicker">
                  <CircleAlert size={18} /> EXTERNAL TRANSACTION GATES
                </div>
                <strong className="gate-headline">8 OPEN</strong>
                <p>
                  Commercial terms, lender commitment, technical, legal, tax,
                  regulatory and investment approvals remain open.
                </p>
                <span className="open-strip">
                  REFERENCE CASE · NOT ACTUAL PPA
                </span>
              </article>
            </div>
          </div>
        </section>

        <section className="model-section">
          <SectionHeading
            number="9"
            title="The Release Can Be Traced to One Successful CI Run"
            note="Artifact identity references the frozen analytical release; availability follows retention policy."
          />
          <div className="ci-layout">
            <article className="model-panel ci-card">
              <div className="panel-kicker">
                <GitCommitHorizontal size={18} /> FINAL MODEL CI RUN
              </div>
              <h3>V5.1.3 Final 10/10 Micro-Fix Validation</h3>
              <div className="ci-fields">
                <span>
                  Run <b>33629919973</b>
                </span>
                <span>
                  Job <b>100246555216</b>
                </span>
                <span>
                  Branch <b>v5.1.3-final-micro-fix</b>
                </span>
                <span>
                  Head SHA <b>{MODEL_SHA.slice(0, 18)}…</b>
                </span>
              </div>
              <div className="ci-success">
                <CheckCircle2 size={18} />
                SUCCESS
              </div>
              <div className="ci-steps">
                {[
                  'Checkout frozen branch',
                  'Deterministic V5.1.3 Build A/B',
                  'Contractual-stress validation',
                  'Regression / preserved tests',
                  'Primary artifact upload',
                  'Runtime manifest sealing',
                ].map((step) => (
                  <span key={step}>
                    <Check size={13} />
                    {step}
                  </span>
                ))}
              </div>
            </article>
            <div className="artifact-column">
              <article className="artifact-card primary">
                <div className="artifact-title">
                  <Archive size={18} />
                  <span>PRIMARY RELEASE ARTIFACT</span>
                  <Status value="RETAINED" />
                </div>
                <strong>9846347737</strong>
                <p>vietgreen-v5-1-3-full-data-model-release</p>
                <code>
                  sha256:e11372a40db34a9b27279c6cf0999379f1e5e28d1fbe076e4b6e806982ff640d
                </code>
                <CopyButton
                  value="sha256:e11372a40db34a9b27279c6cf0999379f1e5e28d1fbe076e4b6e806982ff640d"
                  label="Copy digest"
                />
              </article>
              <article className="artifact-card sealed">
                <div className="artifact-title">
                  <LockKeyhole size={18} />
                  <span>SEALED RUNTIME MANIFEST</span>
                  <Status value="SEALED" />
                </div>
                <strong>9846349762</strong>
                <p>vietgreen-v5-1-3-runtime-manifest</p>
                <code>
                  sha256:edab4b6260327e6927e126cef14d895987a554458f4a307d164944e1284b2209
                </code>
                <CopyButton
                  value="sha256:edab4b6260327e6927e126cef14d895987a554458f4a307d164944e1284b2209"
                  label="Copy digest"
                />
              </article>
            </div>
          </div>
          <div className="artifact-candidate">
            <span>PRIMARY RELEASE ARTIFACT</span>
            <ArrowRight size={15} />
            <span>PATCH RUNTIME IDENTITY</span>
            <ArrowRight size={15} />
            <span>
              RUNTIME CANDIDATE <b>9846348722</b>
            </span>
            <ArrowRight size={15} />
            <span>SEALED MANIFEST</span>
          </div>
          <div className="controlled-links">
            <LinkButton href={`${REPO}/commit/${MODEL_SHA}`}>
              Frozen Commit
            </LinkButton>
            <LinkButton href={`${REPO}/releases/tag/${MODEL_TAG}`}>
              Release Tag
            </LinkButton>
            <LinkButton href={`${REPO}/actions/runs/33629919973`}>
              CI Run
            </LinkButton>
            <LinkButton href={REPO}>Repository</LinkButton>
            <LinkButton href={DRIVE}>Drive Control</LinkButton>
          </div>
        </section>

        <section className="model-section">
          <SectionHeading
            number="10"
            title="Sources Are Registered — Not Hidden in the Model"
            note="Audit links use the frozen model SHA, not /main/."
          />
          <div className="source-table model-panel">
            <div className="source-head">
              <span>Source / output</span>
              <span>Frozen repository path</span>
              <span>What it controls</span>
              <span>Link</span>
            </div>
            {displayedSources.map(([label, path, purpose, SourceIcon]) => (
              <div className="source-row" key={path}>
                <span>
                  <Icon icon={SourceIcon} size={16} />
                  {label}
                </span>
                <code>{path}</code>
                <span>{purpose}</span>
                <a
                  href={`${REPO}/blob/${MODEL_SHA}/${path}`}
                  target="_blank"
                  rel="noreferrer"
                  aria-label={`Open ${path}`}
                >
                  <ExternalLink size={14} />
                </a>
              </div>
            ))}
            <button
              className="source-more"
              type="button"
              onClick={() => setShowAllSources((value) => !value)}
            >
              {showAllSources
                ? 'Show fewer sources'
                : 'Show all registered sources'}
              <ChevronDown
                size={15}
                className={showAllSources ? 'rotated' : ''}
              />
            </button>
          </div>
        </section>

        <section className="model-section">
          <SectionHeading
            number="11"
            title="Claim Governance Makes the Boundary Explicit"
            note="Use the model to understand, trace and stress — not to over-claim approval."
          />
          <div className="claim-governance">
            <article className="model-panel claim-column can">
              <h3>
                <CheckCircle2 size={18} /> CAN CLAIM
              </h3>
              {[
                'Public-data model is controlled and versioned.',
                'Evidence classes are explicit.',
                'Physical QA and semantic controls were run.',
                'Outputs reconcile to the frozen release.',
                'Recruiter-ready analytical package.',
              ].map((item) => (
                <p key={item}>
                  <Check size={14} />
                  {item}
                </p>
              ))}
            </article>
            <article className="model-panel claim-column cannot">
              <h3>
                <XCircle size={18} /> CANNOT CLAIM
              </h3>
              {[
                'Actual PPA terms or negotiated price.',
                'Bankability or lender commitment.',
                'Legal, tax or regulatory approval.',
                'Engineering certification.',
                'Investment committee approval.',
              ].map((item) => (
                <p key={item}>
                  <XCircle size={14} />
                  {item}
                </p>
              ))}
            </article>
          </div>
          <div className="claim-boundary-strip">
            <strong>RECRUITER-READY ≠ TRANSACTION-READY</strong>
            <span>
              FRONTIER_ONLY · REFERENCE_CASE_NOT_ACTUAL_PPA ·
              INDETERMINATE_MISSING_COMMERCIAL_DATA · TRANSACTION EVIDENCE OPEN
            </span>
          </div>
        </section>

        <section className="model-section">
          <SectionHeading
            number="12"
            title="Reproducibility Has a Boundary Too"
            note="Remote-only runtime policy separates analytical identity from website identity."
          />
          <div className="repro-grid">
            <article className="model-panel repro-card">
              <div className="panel-kicker">
                <Cloud size={18} /> REMOTE-ONLY POLICY
              </div>
              <h3>Project-derived runtime artifacts remain remote.</h3>
              <p>
                GitHub Actions is ephemeral execution. Google Drive contains the
                control / execution index. Local machine project-data paths are
                not presented as evidence.
              </p>
              <div className="repro-flow">
                <span>Frozen inputs</span>
                <ArrowRight size={15} />
                <span>Remote build</span>
                <ArrowRight size={15} />
                <span>Sealed release</span>
              </div>
            </article>
            <article className="model-panel website-model-card">
              <div className="panel-kicker">
                <Globe2 size={18} /> WEBSITE VS MODEL IDENTITY
              </div>
              <div className="identity-compare">
                <div>
                  <span>MODEL IDENTITY</span>
                  <b>{MODEL_SHA.slice(0, 12)}…</b>
                  <small>Static · must not move</small>
                </div>
                <div>
                  <span>WEBSITE IDENTITY</span>
                  <b>Current deployment</b>
                  <small>Dynamic · website-only update</small>
                </div>
              </div>
              <p className="immutable-note">
                <LockKeyhole size={15} /> The frozen model tag must not move as
                part of website-only updates.
              </p>
            </article>
          </div>
        </section>

        <section className="model-section">
          <SectionHeading
            number="13"
            title="Can Every Decision Be Traced?"
            note="Controlled audit trail from website claim to field, rule, QA and release."
          />
          <div className="audit-toolbar">
            <div>
              <button
                className={auditFilter === 'All' ? 'active' : ''}
                type="button"
                onClick={() => setAuditFilter('All')}
              >
                All
              </button>
              <button
                className={auditFilter === 'Projects & Data' ? 'active' : ''}
                type="button"
                onClick={() => setAuditFilter('Projects & Data')}
              >
                Data
              </button>
              <button
                className={auditFilter === 'Energy / Physical' ? 'active' : ''}
                type="button"
                onClick={() => setAuditFilter('Energy / Physical')}
              >
                Physical
              </button>
              <button
                className={auditFilter === 'Risk & Scenarios' ? 'active' : ''}
                type="button"
                onClick={() => setAuditFilter('Risk & Scenarios')}
              >
                Risk
              </button>
              <button
                className={auditFilter === 'Diligence' ? 'active' : ''}
                type="button"
                onClick={() => setAuditFilter('Diligence')}
              >
                Diligence
              </button>
            </div>
            <span>{filteredAudit.length} trace entries</span>
          </div>
          <div className="audit-table model-panel">
            <div className="audit-head">
              <span>Website claim</span>
              <span>Page</span>
              <span>Source</span>
              <span>Field / rule</span>
              <span>Evidence class</span>
              <span>QA / release</span>
            </div>
            {filteredAudit.map(([claim, page, source, field, evidence, qa]) => (
              <div className="audit-row" key={claim}>
                <strong>{claim}</strong>
                <span>{page}</span>
                <code>{source}</code>
                <span>{field}</span>
                <span className="audit-class">
                  {evidence.replaceAll('_', ' ')}
                </span>
                <Status value={qa} />
              </div>
            ))}
          </div>
        </section>

        <section className="model-takeaway">
          <div className="takeaway-glow" />
          <div className="takeaway-content">
            <div className="model-card-label">RECRUITER TAKEAWAY</div>
            <h2>
              One frozen analytical model.
              <br />
              Clear evidence boundaries.
            </h2>
            <p>
              The value is not only the outputs. It is the controlled chain from
              public evidence to resolved inputs, physical QA, finance, downside
              scenarios, diligence and a reproducible release.
            </p>
            <div className="takeaway-points">
              <span>
                <CheckCircle2 size={15} />
                54 → 441 → 20 → 19
              </span>
              <span>
                <CheckCircle2 size={15} />
                28-sheet controlled workbook
              </span>
              <span>
                <CheckCircle2 size={15} />
                26 / 26 + 26 / 26 QA
              </span>
              <span>
                <CheckCircle2 size={15} />
                RECRUITER-READY · NOT TRANSACTION-READY
              </span>
            </div>
            <div className="takeaway-actions">
              <Link href="/">
                Back to Overview <ArrowRight size={14} />
              </Link>
              <Link href="/projects">
                View Project Data <ArrowRight size={14} />
              </Link>
              <a href={REPO} target="_blank" rel="noreferrer">
                Open Frozen Repository <ExternalLink size={14} />
              </a>
            </div>
          </div>
        </section>
      </div>
      <footer className="model-footer">
        <span>Model: V5.1.3 (Frozen)</span>
        <span>Data as of: 31 Dec 2024</span>
        <span>Evidence: OPEN</span>
        <span>
          This page: MODEL &amp; EVIDENCE <Info size={13} />
        </span>
        <span>VietGreen · C&amp;I Solar Project Finance</span>
      </footer>
    </main>
  );
}
