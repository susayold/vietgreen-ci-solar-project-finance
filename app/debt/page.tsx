'use client';

import Image from 'next/image';
import Link from 'next/link';
import {
  ArrowDown,
  ArrowRight,
  BarChart3,
  CalendarDays,
  Check,
  ChevronDown,
  FileCheck2,
  Gauge,
  Landmark,
  LineChart,
  Percent,
  Scale,
  ShieldAlert,
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
  technicalDataBlocked?: boolean;
  capacityMw?: number;
};
type DebtRow = {
  projectId: string;
  projectName: string;
  country: string;
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
const ratio = (value?: number | null) =>
  value == null ? 'NOT AVAILABLE' : `${value.toFixed(3)}x`;
const bn = (value?: number | null) =>
  value == null ? 'NOT AVAILABLE' : `VND ${(value / 1e9).toFixed(3)}bn`;
const usdM = (value?: number | null) =>
  value == null ? 'NOT AVAILABLE' : `~$${(value / 1e6).toFixed(3)}m`;

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
    <div className="debt-heading">
      <div>
        <span className="debt-index">{n}</span>
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
  tone = '',
}: {
  icon: typeof Gauge;
  value: string;
  label: string;
  tone?: string;
}) {
  return (
    <div className={`debt-kpi ${tone}`}>
      <Icon size={21} />
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function CreditFlow() {
  const items = [
    ['CFADS', 'Vector'],
    ['DSCR', 'Capacity'],
    ['LLCR', 'Capacity'],
    ['PLCR', 'Capacity'],
    ['Leverage', 'Capacity'],
    ['Minimum', 'Supportable'],
    ['Binding', 'Constraint'],
    ['Initial', 'Debt'],
  ];
  return (
    <div className="credit-flow">
      {items.map(([top, bottom], index) => (
        <div key={top} className={top === 'PLCR' ? 'selected' : ''}>
          <b>{top}</b>
          <span>{bottom}</span>
          {index < items.length - 1 && <ArrowRight size={13} />}
        </div>
      ))}
    </div>
  );
}

function DebtChart({ data }: { data?: DebtRow }) {
  const values = data?.schedule.map((row) => row.cfads / 1e9) ?? [];
  const bars = data?.schedule.map((row) => row.debtService / 1e9) ?? [];
  return (
    <svg
      className="debt-line-chart"
      viewBox="0 0 720 250"
      aria-label="CFADS versus debt service by year"
    >
      <line x1="42" y1="220" x2="700" y2="220" className="chart-axis" />
      {[0, 10, 20, 30, 40].map((tick) => (
        <g key={tick}>
          <line
            x1="42"
            x2="700"
            y1={220 - tick * 4.1}
            y2={220 - tick * 4.1}
            className="chart-grid"
          />
          <text x="0" y={224 - tick * 4.1}>
            {tick}
          </text>
        </g>
      ))}
      {bars.map((value, index) => (
        <rect
          key={index}
          x={54 + index * 43}
          y={220 - value * 4.1}
          width="22"
          height={value * 4.1}
          className="debt-bar"
        />
      ))}
      <polyline
        points={values
          .map((value, index) => `${65 + index * 43},${220 - value * 4.1}`)
          .join(' ')}
        className="debt-polyline"
      />
      {values.map((value, index) => (
        <circle
          key={index}
          cx={65 + index * 43}
          cy={220 - value * 4.1}
          r="3"
          className="debt-point"
        />
      ))}
      {[1, 3, 5, 7, 9, 11, 13, 15].map((year) => (
        <text key={year} x={65 + (year - 1) * 43} y="242">
          {year}
        </text>
      ))}
    </svg>
  );
}

function ScheduleChart({ data }: { data?: DebtRow }) {
  const opening = data?.schedule.map((row) => row.openingDebt / 1e9) ?? [];
  return (
    <div className="schedule-visual">
      <div className="schedule-bars">
        {opening.map((value, index) => (
          <div key={index} className="schedule-year">
            <strong>{value ? value.toFixed(3) : '0'}</strong>
            <i style={{ height: `${Math.max(4, value * 8)}px` }} />
            <span>{index + 1}</span>
          </div>
        ))}
      </div>
      <div className="schedule-legend">
        <span className="opening">Opening Debt</span>
        <span className="closing">Closing Debt</span>
      </div>
    </div>
  );
}

function RatioCard({
  name,
  definition,
  actual,
  threshold,
  tone,
}: {
  name: string;
  definition: string;
  actual: string;
  threshold: string;
  tone: string;
}) {
  return (
    <div className={`ratio-card ${tone}`}>
      <div>
        <span className="ratio-icon">
          {name === 'DSCR' ? '◉' : name === 'LLCR' ? '×' : '↗'}
        </span>
        <b>{name}</b>
        <small>{definition}</small>
      </div>
      <div className="ratio-values">
        <span>
          ACTUAL<strong>{actual}</strong>
        </span>
        <span>
          THRESHOLD<strong>{threshold}</strong>
        </span>
      </div>
      <div className="ratio-track">
        <i />
        <em />
      </div>
      {name === 'PLCR' && <span className="ratio-binding">BINDING</span>}
    </div>
  );
}

export default function DebtPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [debtRows, setDebtRows] = useState<DebtRow[]>([]);
  const [selectedId, setSelectedId] = useState(() =>
    typeof window === 'undefined'
      ? GO_MALL
      : (new URLSearchParams(window.location.search).get('project') ?? GO_MALL),
  );
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    void Promise.all([
      loadWebsiteData<{ projects?: Project[] }>('projects'),
      loadWebsiteData<{ rows?: DebtRow[] }>('debt'),
    ])
      .then(([projectPayload, debtPayload]) => {
        const available = (projectPayload.projects ?? []).filter(
          (project) => !project.technicalDataBlocked,
        );
        setProjects(available);
        setDebtRows(debtPayload.rows ?? []);
        if (!available.some((project) => project.project_id === selectedId))
          setSelectedId(GO_MALL);
      })
      .finally(() => setLoading(false));
  }, [selectedId]);
  const selected = useMemo(
    () =>
      projects.find((project) => project.project_id === selectedId) ??
      projects.find((project) => project.project_id === GO_MALL),
    [projects, selectedId],
  );
  const debt = debtRows.find((row) => row.projectId === selected?.project_id);
  const changeProject = (value: string) => {
    setSelectedId(value);
    window.history.replaceState(
      null,
      '',
      `/debt?project=${encodeURIComponent(value)}`,
    );
  };
  return (
    <main className="debt-page">
      <header className="debt-header">
        <Link href="/" className="debt-brand">
          <span>
            <Landmark size={22} />
          </span>
          <strong>
            VietGreen<small>C&amp;I Solar Project Finance</small>
          </strong>
        </Link>
        <nav>
          <Link href="/">Overview</Link>
          <Link href="/projects">Projects</Link>
          <Link href="/energy">Energy</Link>
          <Link href="/economics">Economics</Link>
          <Link href="/debt" className="active">
            Debt
          </Link>
          <Link href="/risk">Risk</Link>
          <Link href="/diligence">Diligence</Link>
          <Link href="/model-evidence">Model &amp; Evidence</Link>
        </nav>
        <span className="debt-release">V5.1.3 · Frozen Model</span>
      </header>
      <section className="debt-hero">
        <Image
          src="/assets/projects/projects-hero.webp"
          alt="Industrial rooftop solar project"
          fill
          priority
          sizes="100vw"
        />
        <div className="debt-hero-shade" />
        <div className="debt-hero-inner">
          <div className="debt-hero-copy">
            <p className="debt-eyebrow">
              DEBT CAPACITY · COVERAGE RATIOS · CREDIT STRUCTURE
            </p>
            <h1>Debt Sized From CFADS — Not From an Assumed Leverage Ratio.</h1>
            <p>
              The credit layer tests DSCR, LLCR, PLCR and leverage constraints,
              selects the binding debt capacity, then rebuilds the contractual
              debt schedule from the cash flow the project can actually support.
            </p>
            <div className="debt-buttons">
              <a className="debt-button primary" href="#capacity">
                Review Debt Capacity <ArrowDown size={14} />
              </a>
              <a className="debt-button" href="#schedule">
                Inspect Debt Schedule <ArrowDown size={14} />
              </a>
            </div>
          </div>
          <aside className="debt-hero-card">
            <div>
              <span>SUPPORTABLE DEBT</span>
              <b>{usdM(debt?.debtCapacityUsd)}</b>
            </div>
            <div>
              <span>BINDING</span>
              <b>PLCR</b>
            </div>
            <div>
              <span>MIN DSCR</span>
              <b>{ratio(debt?.minimumDscr)}</b>
            </div>
            <div>
              <span>PLCR</span>
              <b>{ratio(debt?.plcr)}</b>
            </div>
            <footer>STANDARDIZED UNDERWRITING · NOT LENDER APPROVAL</footer>
          </aside>
        </div>
      </section>
      <div className="debt-main">
        <section className="debt-section">
          <Heading n="1" title="Selected Project Credit Profile" />
          <div className="debt-selector">
            <div>
              <b>{selected?.project_name ?? 'GO Mall Vietnam portfolio'}</b>
              <small>{selected?.project_id ?? GO_MALL}</small>
            </div>
            <div className="debt-select">
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
            <span>◉ {selected?.country ?? 'NOT AVAILABLE'}</span>
            <span>♨ GreenYellow</span>
            <span>◉ {selected?.capacityMw?.toFixed(3) ?? 'NOT AVAILABLE'} MW</span>
            <span>▣ {usdM(debt?.debtCapacityUsd)}</span>
            <b className="green-badge">
              {selected?.technicalDataBlocked ? 'TECHNICAL_DATA_BLOCKED' : 'READY_FOR_ECONOMICS'}
            </b>
            <b className="gold-badge">STANDARDIZED_CREDIT_CASE</b>
          </div>
          <div className="debt-kpi-grid">
            <KPI
              icon={WalletCards}
              value={usdM(debt?.debtCapacityUsd)}
              label="Supportable Debt"
            />
            <KPI
              icon={Percent}
              value={debt?.leverage == null ? 'NOT AVAILABLE' : `~${(debt.leverage * 100).toFixed(1)}%`}
              label="Supportable Leverage"
            />
            <KPI
              icon={ShieldAlert}
              value={debt?.bindingConstraint ?? 'NOT AVAILABLE'}
              label="Binding Constraint"
            />
            <KPI
              icon={Gauge}
              value={ratio(debt?.minimumDscr)}
              label="Minimum DSCR"
            />
            <KPI
              icon={LineChart}
              value={ratio(debt?.llcr)}
              label="LLCR"
            />
            <KPI
              icon={LineChart}
              value={ratio(debt?.plcr)}
              label="PLCR"
            />
          </div>
          <div className="debt-strip">
            <span>
              {(debt ? debt.debtRate * 100 : 0).toFixed(1)}%<small>Debt Rate</small>
            </span>
            <span>
              {debt?.debtTenorYears ?? 'NOT AVAILABLE'} years<small>Debt Tenor Policy</small>
            </span>
            <span>
              {ratio(debt?.dscrTarget)}<small>DSCR Sculpting Target</small>
            </span>
            <span>
              {ratio(debt?.llcrMin)}<small>LLCR Minimum</small>
            </span>
            <span>
              {ratio(debt?.plcrMin)}<small>PLCR Minimum</small>
            </span>
            <span>
              {debt ? (debt.maxLeverage * 100).toFixed(0) : 'NOT AVAILABLE'}%<small>Maximum Leverage</small>
            </span>
          </div>
          <div className="debt-warning">
            <ShieldAlert size={18} />
            STANDARDIZED UNDERWRITING — NOT ACTUAL LENDER TERMS
          </div>
        </section>
        <section id="capacity" className="debt-section">
          <Heading
            n="2"
            title="How the Model Sizes Debt"
            note="Four independent constraints compete to determine supportable opening debt."
          />
          <div className="capacity-grid">
            <div className="capacity-card">
              <CreditFlow />
              <div className="leverage-callout">
                <Scale size={24} />
                <span>
                  <b>
                    {(debt ? debt.maxLeverage * 100 : 0).toFixed(0)}% MAXIMUM
                    LEVERAGE ≠{' '}
                    {debt?.leverage == null
                      ? 'NOT AVAILABLE'
                      : `${(debt.leverage * 100).toFixed(1)}% SUPPORTABLE LEVERAGE`}
                  </b>
                  <small>
                    The leverage cap is only an upper limit. Cash-flow coverage
                    constraints (DSCR, LLCR, PLCR) limit debt capacity far below
                    that ceiling. The model selects the minimum supportable
                    capacity.
                  </small>
                </span>
              </div>
            </div>
            <div className="binding-card">
              <div className="plcr-box">
                <b>PLCR</b>
                <strong>{ratio(debt?.plcr)}</strong>
                <small>Minimum requirement {ratio(debt?.plcrMin)}</small>
                <span>BINDING CONSTRAINT</span>
              </div>
              <div>
                <h3>Why PLCR Binds the GO Mall Reference Case</h3>
                <p>
                  Project-Life Coverage Ratio is the binding constraint for the
                  frozen GO Mall reference case. Although leverage could go much
                  higher, the life-cycle cash flows only support this level of
                  debt while meeting all credit metrics.
                </p>
              </div>
            </div>
          </div>
        </section>
        <section className="debt-section charts-section">
          <div className="chart-card">
            <Heading
              n="3"
              title="CFADS vs Debt Service"
              note="CFADS must cover contractual debt service."
            />
            <div className="chart-key">
              <span className="cfads-key">CFADS (VND bn)</span>
              <span className="service-key">Debt Service (VND bn)</span>
            </div>
            <DebtChart data={debt} />
            <div className="chart-side-stats">
              <span>
                YEAR 1 CFADS<b>{bn(debt?.schedule[0]?.cfads)}</b>
              </span>
              <span>
                YEAR 1 DEBT SERVICE<b>{bn(debt?.schedule[0]?.debtService)}</b>
              </span>
              <span>
                YEAR 1 DSCR<b>{ratio(debt?.schedule[0]?.dscr)}</b>
              </span>
            </div>
            <p className="chart-footnote">
              After Year 1 debt payoff, debt service is zero for the remainder
              of the term. DSCR is N/A, not 0x.
            </p>
          </div>
          <div id="schedule" className="chart-card">
            <Heading
              n="4"
              title="Contractual Debt Schedule"
              note="The schedule is rebuilt from supportable opening debt."
            />
            <div className="schedule-columns">
              <div>
                <b>A. Opening vs Closing Debt</b>
                <ScheduleChart data={debt} />
              </div>
              <div>
                <b>B. Principal vs Interest</b>
                <div className="principal-visual">
                  <span className="principal-bar" />
                  <span className="interest-bar" />
                  <b>{debt?.schedule[0]?.principal == null ? 'NOT AVAILABLE' : (debt.schedule[0].principal / 1e9).toFixed(3)}</b>
                  <small>Principal · Interest</small>
                </div>
              </div>
            </div>
            <table className="debt-table">
              <thead>
                <tr>
                  <th>Year</th>
                  <th>Opening</th>
                  <th>Interest</th>
                  <th>Principal</th>
                  <th>Debt Service</th>
                  <th>Closing</th>
                  <th>DSCR</th>
                </tr>
              </thead>
              <tbody>
                {(debt?.schedule ?? []).map((row) => (
                  <tr key={row.year}>
                    <td>{row.year}</td>
                    <td>{(row.openingDebt / 1e9).toFixed(3)}</td>
                    <td>{(row.interest / 1e9).toFixed(3)}</td>
                    <td>{(row.principal / 1e9).toFixed(3)}</td>
                    <td>{(row.debtService / 1e9).toFixed(3)}</td>
                    <td>{(row.closingDebt / 1e9).toFixed(3)}</td>
                    <td>{ratio(row.dscr)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="chart-footnote">
              N/A ≠ 0.00x. N/A means there is no debt service to cover after
              payoff.
            </p>
          </div>
        </section>
        <section className="debt-section">
          <Heading
            n="5"
            title="Coverage Ratios Measure Different Credit Horizons"
          />
          <div className="ratio-grid">
            <div>
              <RatioCard
                name="DSCR"
                definition="CFADS / Debt Service"
                actual={ratio(debt?.minimumDscr)}
                threshold={ratio(debt?.dscrTarget)}
                tone="dscr"
              />
              <RatioCard
                name="LLCR"
                definition="PV(Loan-Life CFADS) / Opening Debt"
                actual={ratio(debt?.llcr)}
                threshold={ratio(debt?.llcrMin)}
                tone="llcr"
              />
              <RatioCard
                name="PLCR"
                definition="PV(Project-Life CFADS) / Opening Debt"
                actual={ratio(debt?.plcr)}
                threshold={ratio(debt?.plcrMin)}
                tone="plcr"
              />
            </div>
            <div className="credit-meaning">
              <Heading n="6" title="What the Credit Metrics Mean" />
              <div>
                <CalendarDays />
                <span>
                  <b>Strong Near-Term Coverage</b>
                  <small>
                    Generated Year 1 DSCR is compared with the standardized
                    target from the selected debt payload.
                  </small>
                </span>
              </div>
              <div>
                <BarChart3 />
                <span>
                  <b>Low Supportable Leverage</b>
                  <small>
                    Supportable leverage is compared with the policy maximum;
                    policy is not lender approval.
                  </small>
                </span>
              </div>
              <div>
                <ShieldAlert />
                <span>
                  <b>PLCR Is the Binding Constraint</b>
                  <small>
                    Project-life coverage sets the final debt capacity in this
                    case.
                  </small>
                </span>
              </div>
              <div>
                <Landmark />
                <span>
                  <b>Credit Model ≠ Lender Approval</b>
                  <small>
                    This is standardized credit supportability analysis only;
                    lenders decide differently.
                  </small>
                </span>
              </div>
              <div className="model-supported">MODEL-SUPPORTED DEBT ONLY</div>
            </div>
          </div>
        </section>
        <section className="debt-section portfolio-credit">
          <Heading
            n="7"
            title="Credit Supportability Across the Economics-Ready Universe"
            note="Portfolio counts are presented as a credit-status view, not an investment ranking."
          />
          <div className="portfolio-credit-grid">
            <div className="credit-donut">
              <div className="donut-ring">
                <strong>19</strong>
                <small>Projects</small>
              </div>
              <span>
                <i className="dot green" />
                14 Positive Debt Capacity (74%)
              </span>
              <span>
                <i className="dot amber" />5 No Positive Debt Capacity (26%)
              </span>
            </div>
            <div className="binding-distribution">
              <h3>Binding Constraint Distribution</h3>
              <span>
                <b>PLCR</b>
                <i style={{ width: '92%' }} />
                <strong>11 (58%)</strong>
              </span>
              <span>
                <b>LLCR</b>
                <i style={{ width: '34%' }} />
                <strong>4 (21%)</strong>
              </span>
              <span>
                <b>DSCR</b>
                <i style={{ width: '18%' }} />
                <strong>2 (11%)</strong>
              </span>
              <span>
                <b>Leverage</b>
                <i style={{ width: '18%' }} />
                <strong>2 (10%)</strong>
              </span>
            </div>
            <div className="portfolio-credit-table">
              <table>
                <thead>
                  <tr>
                    <th>Project</th>
                    <th>Country</th>
                    <th>Debt USD</th>
                    <th>Leverage</th>
                    <th>Binding</th>
                    <th>Min DSCR</th>
                    <th>LLCR</th>
                    <th>PLCR</th>
                  </tr>
                </thead>
                <tbody>
                  {debtRows.slice(0, 6).map((row) => (
                    <tr key={row.projectId}>
                      <td>{row.projectName}</td>
                      <td>{row.country}</td>
                      <td>{usdM(row.debtCapacityUsd)}</td>
                      <td>
                        {row.leverage == null
                          ? 'NOT AVAILABLE'
                          : `${(row.leverage * 100).toFixed(1)}%`}
                      </td>
                      <td>{row.bindingConstraint ?? 'NOT AVAILABLE'}</td>
                      <td>{ratio(row.minimumDscr)}</td>
                      <td>{ratio(row.llcr)}</td>
                      <td>{ratio(row.plcr)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <Link href="/projects">
                Explore all 19 economics-ready projects <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        </section>
        <section className="debt-section">
          <Heading
            n="8"
            title="What This Credit Page Can — and Cannot — Claim"
          />
          <div className="claim-grid">
            <div>
              <h3>CAN CLAIM</h3>
              <p>
                <Check />
                Standardized supportable debt capacity
              </p>
              <p>
                <Check />
                Identified binding constraint
              </p>
              <p>
                <Check />
                Frozen base schedule
              </p>
              <p>
                <Check />
                DSCR, LLCR, PLCR metrics
              </p>
              <p>
                <Check />
                Standardized credit-policy assumptions
              </p>
            </div>
            <div className="cannot">
              <h3>CANNOT CLAIM</h3>
              <p>
                <X />
                Bank-approved debt amount
              </p>
              <p>
                <X />
                Executed lender term sheet
              </p>
              <p>
                <X />
                Negotiated margin
              </p>
              <p>
                <X />
                Financial close
              </p>
              <p>
                <X />
                Bankability or approval
              </p>
            </div>
            <div className="handoff-debt">
              <h3>BASE CREDIT IS ONLY THE STARTING POINT</h3>
              <div>
                <span>
                  Base Debt
                  <br />
                  Schedule
                </span>
                <ArrowRight />
                <span>
                  Contractual
                  <br />
                  Preservation
                </span>
                <ArrowRight />
                <span>
                  Downside
                  <br />
                  Cash Flow
                </span>
                <ArrowRight />
                <span>
                  Stressed
                  <br />
                  Coverage
                </span>
              </div>
              <Link href={`/risk?project=${GO_MALL}`}>
                Continue to Risk &amp; Scenarios <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        </section>
        <section className="debt-takeaway">
          <Image
            src="/assets/overview/footer-solar-texture.webp"
            alt="Solar texture"
            fill
            sizes="45vw"
          />
          <div>
            <span className="debt-index gold">9</span>
            <p>RECRUITER TAKEAWAY</p>
            <h2>
              Debt capacity is an output of cash-flow coverage — not a financing
              assumption.
            </h2>
            <p>
              The generated credit payload shows standardized debt capacity and
              coverage for the selected project. It is not lender approval.
            </p>
            <div>
              <b>STANDARDIZED CREDIT CASE</b>
              <b>NOT LENDER APPROVAL</b>
            </div>
          </div>
        </section>
      </div>
      <footer className="debt-footer">
        <span>Model: V5.1.3 (Frozen)</span>
        <span>Data as of: 31 Dec 2024</span>
        <span>
          <FileCheck2 size={14} /> Evidence: OPEN
        </span>
        <span>STANDARDIZED_CREDIT_CASE ⓘ</span>
      </footer>
    </main>
  );
}


