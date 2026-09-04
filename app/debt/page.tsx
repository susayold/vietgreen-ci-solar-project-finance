'use client';

export const dynamic = 'force-static';

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

const SHA = 'ff69e15d211ff1abc88200574242ed2f1db49074';
const RAW = `https://raw.githubusercontent.com/susayold/vietgreen-ci-solar-project-finance/${SHA}`;
const GO_MALL = 'VN-GY-GOMALL';
type Project = {
  project_id: string;
  project_name: string;
  country: string;
  technicalDataBlocked?: boolean;
};

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

function DebtChart() {
  const values = [
    34.832, 27.4, 23, 20.5, 18.8, 17.3, 16.3, 15.3, 14.4, 13.5, 12.8, 12.2,
    11.6, 11.1, 10.7,
  ];
  const bars = [
    14.633, 11.2, 8.1, 5.8, 3.2, 1.5, 0.7, 0.3, 0.1, 0, 0, 0, 0, 0, 0,
  ];
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

function ScheduleChart() {
  const opening = [13.549, 0, 0, 0, 0, 0, 0, 0];
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
  const [selectedId, setSelectedId] = useState(() =>
    typeof window === 'undefined'
      ? GO_MALL
      : (new URLSearchParams(window.location.search).get('project') ?? GO_MALL),
  );
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    void fetch(`${RAW}/website/data/projects.json`)
      .then((response) => response.json())
      .then((raw) => {
        const projectPayload = raw as { projects?: Project[] };
        const available = (projectPayload.projects ?? []).filter(
          (project) => !project.technicalDataBlocked,
        );
        setProjects(available);
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
  const isGoMall = selected?.project_id === GO_MALL;
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
          <Link href="/model">Model</Link>
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
              <b>~$0.529m</b>
            </div>
            <div>
              <span>BINDING</span>
              <b>PLCR</b>
            </div>
            <div>
              <span>MIN DSCR</span>
              <b>2.380x</b>
            </div>
            <div>
              <span>PLCR</span>
              <b>1.336x</b>
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
            <span>🇻🇳 Vietnam</span>
            <span>♨ GreenYellow</span>
            <span>◉ 9.000 MW</span>
            <span>▣ $11.250m CAPEX</span>
            <b className="green-badge">READY_FOR_ECONOMICS</b>
            <b className="gold-badge">STANDARDIZED_CREDIT_CASE</b>
          </div>
          <div className="debt-kpi-grid">
            <KPI
              icon={WalletCards}
              value={isGoMall ? '~$0.529m' : 'NOT AVAILABLE'}
              label="Supportable Debt"
            />
            <KPI
              icon={Percent}
              value={isGoMall ? '~4.7%' : 'NOT AVAILABLE'}
              label="Supportable Leverage"
            />
            <KPI
              icon={ShieldAlert}
              value={isGoMall ? 'PLCR' : 'NOT AVAILABLE'}
              label="Binding Constraint"
            />
            <KPI
              icon={Gauge}
              value={isGoMall ? '2.380x' : 'NOT AVAILABLE'}
              label="Minimum DSCR"
            />
            <KPI
              icon={LineChart}
              value={isGoMall ? '2.232x' : 'NOT AVAILABLE'}
              label="LLCR"
            />
            <KPI
              icon={LineChart}
              value={isGoMall ? '1.336x' : 'NOT AVAILABLE'}
              label="PLCR"
            />
          </div>
          <div className="debt-strip">
            <span>
              8.0%<small>Debt Rate</small>
            </span>
            <span>
              15 years<small>Debt Tenor Policy</small>
            </span>
            <span>
              1.35x<small>DSCR Sculpting Target</small>
            </span>
            <span>
              1.30x<small>LLCR Minimum</small>
            </span>
            <span>
              1.20x<small>PLCR Minimum</small>
            </span>
            <span>
              70%<small>Maximum Leverage</small>
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
                  <b>70% MAXIMUM LEVERAGE ≠ 4.7% SUPPORTABLE LEVERAGE</b>
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
                <strong>1.336x</strong>
                <small>Minimum requirement 1.20x</small>
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
            <DebtChart />
            <div className="chart-side-stats">
              <span>
                YEAR 1 CFADS<b>~VND 34.832bn</b>
              </span>
              <span>
                YEAR 1 DEBT SERVICE<b>~VND 14.633bn</b>
              </span>
              <span>
                YEAR 1 DSCR<b>2.380x</b>
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
                <ScheduleChart />
              </div>
              <div>
                <b>B. Principal vs Interest</b>
                <div className="principal-visual">
                  <span className="principal-bar" />
                  <span className="interest-bar" />
                  <b>13.549</b>
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
                <tr>
                  <td>1</td>
                  <td>13.549</td>
                  <td>1.084</td>
                  <td>13.549</td>
                  <td>14.633</td>
                  <td>0</td>
                  <td>2.380x</td>
                </tr>
                <tr>
                  <td>2–15</td>
                  <td>0</td>
                  <td>0</td>
                  <td>0</td>
                  <td>0</td>
                  <td>0</td>
                  <td>N/A</td>
                </tr>
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
                actual="2.380x"
                threshold="1.35x"
                tone="dscr"
              />
              <RatioCard
                name="LLCR"
                definition="PV(Loan-Life CFADS) / Opening Debt"
                actual="2.232x"
                threshold="1.30x"
                tone="llcr"
              />
              <RatioCard
                name="PLCR"
                definition="PV(Project-Life CFADS) / Opening Debt"
                actual="1.336x"
                threshold="1.20x"
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
                    Year 1 DSCR of 2.380x is well above the 1.35x target,
                    indicating strong early cash-flow capacity.
                  </small>
                </span>
              </div>
              <div>
                <BarChart3 />
                <span>
                  <b>Low Supportable Leverage</b>
                  <small>
                    Only ~4.7% leverage is supportable, far below the 70% policy
                    maximum.
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
                  <tr>
                    <td>GO Mall</td>
                    <td>Vietnam</td>
                    <td>$0.529m</td>
                    <td>4.7%</td>
                    <td>PLCR</td>
                    <td>2.380x</td>
                    <td>2.232x</td>
                    <td>1.336x</td>
                  </tr>
                  <tr>
                    <td>PO Mall</td>
                    <td>Vietnam</td>
                    <td>$0.412m</td>
                    <td>4.2%</td>
                    <td>PLCR</td>
                    <td>2.120x</td>
                    <td>1.985x</td>
                    <td>1.228x</td>
                  </tr>
                  <tr>
                    <td>Industrial RTL</td>
                    <td>India</td>
                    <td>$0.730m</td>
                    <td>8.6%</td>
                    <td>LLCR</td>
                    <td>1.520x</td>
                    <td>1.301x</td>
                    <td>1.115x</td>
                  </tr>
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
              For the GO Mall reference case, the model supports only ~$0.529m
              of standardized debt against $11.250m of CAPEX. PLCR is the
              binding constraint, while base minimum DSCR remains approximately
              2.380x.
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
