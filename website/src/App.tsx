import { useEffect, useMemo, useState, type ReactNode } from "react";
import "./styles.css";

type AnyRecord = Record<string, any>;
type SiteData = Record<string, AnyRecord>;

const routes = [
  ["/", "Overview"], ["/projects", "Projects"], ["/energy", "Energy"],
  ["/economics", "Economics"], ["/debt", "Debt"], ["/risk", "Risk"],
  ["/diligence", "Diligence"], ["/model", "Model"],
] as const;

const chartColors = ["#0c4b39", "#d39b32", "#2e7f66", "#b9473d"];

function hashRoute() {
  const hash = window.location.hash.replace(/^#/, "") || "/";
  const [path, query] = hash.split("?");
  const params = new URLSearchParams(query || "");
  return { path: path || "/", project: params.get("project") || "" };
}
function go(path: string, project?: string) {
  const suffix = project ? \`?project=\${encodeURIComponent(project)}\` : "";
  window.location.hash = \`#\${path}\${suffix}\`;
}
function num(value: unknown) {
  if (value === null || value === undefined || value === "") return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}
function text(value: unknown, fallback = "N/A") {
  return value === null || value === undefined || value === "" ? fallback : String(value);
}
function fmt(value: unknown, digits = 2) {
  const n = num(value);
  return n === null ? "N/A" : n.toLocaleString("en-US", { maximumFractionDigits: digits, minimumFractionDigits: digits });
}
function fmt0(value: unknown) {
  const n = num(value);
  return n === null ? "N/A" : n.toLocaleString("en-US", { maximumFractionDigits: 0 });
}
function fmtPct(value: unknown) {
  const n = num(value);
  if (n === null) return "N/A";
  return \`\${(n * 100).toFixed(2)}%\`;
}
function fmtUsd(value: unknown) {
  const n = num(value);
  if (n === null) return "N/A";
  return \`$\${(n / 1_000_000).toFixed(3)}m\`;
}
function classForStatus(value: unknown) {
  const s = String(value || "").toLowerCase();
  if (s.includes("blocked") || s.includes("extreme") || s.includes("fail")) return "badge bad";
  if (s.includes("review") || s.includes("indeterminate") || s.includes("open")) return "badge warn";
  return "badge good";
}
function Icon({ children }: { children: ReactNode }) {
  return <span className="round-icon" aria-hidden="true">{children}</span>;
}
function Missing({ label = "Not available from frozen output" }: { label?: string }) {
  return <span className="missing">{label}</span>;
}

function LineChart({ series, labels, unit = "" }: { series: { name: string; values: number[]; color?: string }[]; labels?: string[]; unit?: string }) {
  const width = 860, height = 260, pad = { l: 44, r: 18, t: 22, b: 36 };
  const all = series.flatMap(s => s.values).filter(Number.isFinite);
  if (!all.length) return <Missing label="No chart data in frozen output" />;
  const max = Math.max(...all, 1), min = Math.min(...all, 0), range = max - min || 1;
  const x = (i: number, length: number) => pad.l + (i / Math.max(length - 1, 1)) * (width - pad.l - pad.r);
  const y = (v: number) => pad.t + (1 - (v - min) / range) * (height - pad.t - pad.b);
  return <div className="chart-wrap">
    <svg viewBox={\`0 0 \${width} \${height}\`} role="img" aria-label={\`Line chart \${unit}\`}>
      {[0, .25, .5, .75, 1].map((p) => <line key={p} x1={pad.l} x2={width-pad.r} y1={pad.t+p*(height-pad.t-pad.b)} y2={pad.t+p*(height-pad.t-pad.b)} className="grid-line" />)}
      <line x1={pad.l} x2={pad.l} y1={pad.t} y2={height-pad.b} className="axis-line" />
      <line x1={pad.l} x2={width-pad.r} y1={height-pad.b} y2={height-pad.b} className="axis-line" />
      {series.map((s, si) => {
        const points = s.values.map((v, i) => \`\${x(i, s.values.length)},\${y(v)}\`).join(" ");
        return <g key={s.name}><polyline points={points} fill="none" stroke={s.color || chartColors[si]} strokeWidth="3" strokeLinejoin="round" strokeLinecap="round" />
          {s.values.map((v, i) => <circle key={i} cx={x(i,s.values.length)} cy={y(v)} r="3" fill={s.color || chartColors[si]} />)}</g>;
      })}
      {[0, .5, 1].map((p) => <text key={p} x={pad.l-8} y={pad.t+p*(height-pad.t-pad.b)+4} textAnchor="end" className="axis-text">{fmt(max-p*range, 1)}</text>)}
      {(labels || []).filter((_, i) => i % Math.max(1, Math.ceil((labels || []).length / 8)) === 0).map((l, i) => {
        const original = (labels || []).indexOf(l);
        return <text key={\`\${l}-\${i}\`} x={x(original, (labels || []).length)} y={height-10} textAnchor="middle" className="axis-text">{l}</text>;
      })}
    </svg>
    <div className="chart-legend">{series.map((s, i) => <span key={s.name}><i style={{ background: s.color || chartColors[i] }} />{s.name}</span>)}</div>
  </div>;
}

function BarChart({ items, unit = "", color = "#0c4b39" }: { items: { label: string; value: number | null }[]; unit?: string; color?: string }) {
  const valid = items.map(i => ({ ...i, value: num(i.value) })).filter(i => i.value !== null) as {label:string;value:number}[];
  if (!valid.length) return <Missing label="No chart data in frozen output" />;
  const max = Math.max(...valid.map(i => Math.abs(i.value)), 1);
  return <div className="bars" aria-label={\`Bar chart \${unit}\`}>{items.map(item => {
    const value = num(item.value);
    return <div className="bar-row" key={item.label}><span>{item.label}</span><div className="bar-track">{value === null ? <div className="bar-missing" /> : <div className="bar-fill" style={{ width: \`\${Math.max(2, Math.abs(value)/max*100)}%\`, background: value < 0 ? "#b9473d" : color }} />}</div><b>{value === null ? "N/A" : fmt(value, 2)}</b></div>;
  })}</div>;
}

function Scatter({ points }: { points: { x: number|null; y: number|null; label: string; blocked?: boolean }[] }) {
  const valid = points.map(p => ({...p,x:num(p.x),y:num(p.y)})).filter(p=>p.x!==null&&p.y!==null) as {x:number;y:number;label:string;blocked?:boolean}[];
  if (!valid.length) return <Missing />;
  const maxX=Math.max(...valid.map(p=>p.x),1), maxY=Math.max(...valid.map(p=>p.y),1);
  return <div className="scatter-chart"><div className="scatter-axis-y">Specific yield (kWh/kWp)</div><div className="scatter-plot">{valid.map(p=><span key={p.label} className={\`scatter-point \${p.blocked?"blocked":""}\`} style={{left:\`\${p.x/maxX*94+3}%\`,bottom:\`\${p.y/maxY*90+4}%\`}} title={\`\${p.label}: \${fmt(p.y,0)}\`} />)}<div className="scatter-line" style={{bottom:\`\${900/maxY*90+4}%\`}}>900</div><div className="scatter-line high" style={{bottom:\`\${1600/maxY*90+4}%\`}}>1,600</div></div><div className="scatter-axis-x">Capacity (MW)</div></div>;
}

function Heatmap({ rows, names }: { rows: AnyRecord[]; names: Record<string,string> }) {
  const scenarioNames = Array.from(new Set(rows.map(r=>text(r.scenario)))).sort();
  const projectIds = Array.from(new Set(rows.map(r=>text(r.projectId)))).sort();
  if (projectIds.length !== 19 || scenarioNames.length !== 9) return <Missing label="Heatmap requires exact 19 × 9 scenario rows" />;
  return <div className="heatmap-wrap"><table className="heatmap"><thead><tr><th>Project</th>{scenarioNames.map(s=><th key={s}>{s.replaceAll("_"," ")}</th>)}</tr></thead><tbody>{projectIds.map(pid=><tr key={pid}><th>{names[pid] || pid}</th>{scenarioNames.map(s=>{const row=rows.find(r=>r.projectId===pid&&r.scenario===s);const v=num(row?.minDscr);const tone=v===null?"na":v<1?"red":v<1.3?"amber":v<1.5?"yellow":"green";return <td className={tone} key={s} title={\`\${pid} · \${s} · DSCR \${v===null?"N/A":fmt(v,3)}\`}>{v===null?"N/A":v.toFixed(2)}</td>})}</tr>)}</tbody></table></div>;
}

function Waterfall({ rows }: { rows: AnyRecord[] }) {
  const row = rows.find(r => String(r.year) === "1") || rows[0];
  if (!row) return <Missing />;
  const values = [
    ["Gross revenue", num(row.grossRevenue), "positive"],
    ["OPEX", num(row.opex), "negative"],
    ["Tax", num(row.tax), "negative"],
    ["CFADS", num(row.cfads), "positive"],
    ["Debt service", num(row.debtService), "negative"],
    ["Equity cash flow", num(row.equityCashFlow), "positive"],
  ];
  const max=Math.max(...values.map(([,v])=>Math.abs(num(v) || 0)),1);
  return <div className="waterfall">{values.map(([label,value,tone])=><div className="water-col" key={String(label)}><small>{value===null?"N/A":fmt(value,0)}</small><div className={\`water-bar \${tone}\`} style={{height:value===null?"4px":\`\${Math.max(4,Math.abs(Number(value))/max*150)}px\`}} /><span>{label}</span></div>)}</div>;
}

function Shell({ children, path, summary }: { children: ReactNode; path: string; summary: AnyRecord }) {
  return <><header className="site-header"><a className="brand" href="#/"><span className="brand-mark">✺</span><span><b>VietGreen</b><small>C&amp;I Solar Project Finance</small></span></a><nav className="desktop-nav">{routes.map(([href,label])=><a className={path===href?"active":""} href={\`#\${href}\`} key={href}>{label}</a>)}</nav><a className="github-button" href="https://github.com/susayold/vietgreen-ci-solar-project-finance" target="_blank" rel="noreferrer">GitHub ↗</a></header><div className="release-strip"><span className="release-dot">●</span><b>V5.1.3</b><span>Frozen model</span><i>·</i><span>Public-data reconstruction</span><i>·</i><span>PPA FRONTIER_ONLY</span></div>{children}<footer className="footer"><div><b>VietGreen</b><span>C&amp;I Solar Project Finance</span></div><div>Evidence over assertions · Recruiter-ready ≠ transaction-ready</div><div>{text(summary.referenceCase)}</div></footer></>;
}
function Hero({ eyebrow, title, subtitle, image="industrial-rooftop", action="View model & evidence", to="/model" }: { eyebrow: string; title: string; subtitle: string; image?: string; action?: string; to?: string }) {
  return <section className="hero"><div className="hero-copy"><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="hero-subtitle">{subtitle}</p><div className="hero-actions"><a className="button gold" href={\`#\${to}\`}>{action} →</a><a className="button outline" href="https://github.com/susayold/vietgreen-ci-solar-project-finance" target="_blank" rel="noreferrer">Open GitHub ↗</a></div></div><img className="hero-image" src={\`/assets/hero/\${image}.svg\`} alt="" /></section>;
}
function Kpi({ value, label, tone="" }: { value: unknown; label: string; tone?: string }) { return <div className={\`kpi \${tone}\`}><Icon>{tone==="warn"?"!":"✦"}</Icon><strong>{text(value)}</strong><span>{label}</span></div>; }
function Panel({ title, note, children }: { title: string; note?: string; children: ReactNode }) { return <section className="panel"><div className="panel-heading"><h2>{title}</h2>{note && <span>{note}</span>}</div>{children}</section>; }
function Selector({ projects, value, onChange }: { projects: AnyRecord[]; value: string; onChange: (value: string)=>void }) { return <label className="selector">SELECT PROJECT<select value={value} onChange={e=>{onChange(e.target.value);go(hashRoute().path,e.target.value)}}>{projects.map(p=><option value={p.projectId} key={p.projectId}>{p.projectName} · {p.country}</option>)}</select></label>; }

function Overview({ d }: { d: SiteData }) {
  const s=d.summary, projects=d.projects.projects || [], featured=projects.find(p=>p.projectId===s.featuredProjectId) || projects[0];
  return <><Hero eyebrow="PROJECT FINANCE · C&I SOLAR · PUBLIC DATA" title="From public solar data to project finance decisions." subtitle="A strict presentation view of the frozen V5.1.3 model: physical QA, deterministic 8,760 operating profiles, PPA frontier analysis, CFADS-based debt sizing and downside stress." image="industrial-rooftop" action="Explore featured case" to="/economics"/><main className="container"><div className="kpi-grid">{[[s.candidateProjects,"Candidate projects"],[s.selectedRecords,"Selected records"],[s.economicsReadyProjects,"Economics-ready projects"],[\`\${fmt(s.economicsReadyCapacityMw,3)} MW\`,"Ready capacity"],[\`\${fmt(s.readyObservedGenerationGwh,3)} GWh\`,"Ready source generation"],[s.scenarios,"Governed scenario rows"]].map(([v,l])=><Kpi key={String(l)} value={v} label={String(l)} />)}</div><div className="evidence-strip"><b>Evidence &amp; data footprint</b><span><strong>{s.observations}</strong>observations</span><span><strong>{s.countries}</strong>countries</span><span><strong>{s.modeledHourlyRows}</strong>hourly rows</span><span><strong>{s.workbookSheets}</strong>workbook sheets</span><span><strong>{s.regressionTests} / {s.semanticControls}</strong>regression / semantic controls</span></div><Panel title="Executive conclusion"><div className="decision-grid"><div className="decision-card"><Icon>✓</Icon><b>Commercial</b><strong>PPA mode: {s.ppaMode}</strong></div><div className="decision-card warning"><Icon>⚖</Icon><b>Decision</b><strong>{s.decision}</strong></div><div className="decision-card"><Icon>▥</Icon><b>Capital</b><strong>$0 allocated · diligence shortlist only</strong></div></div></Panel><Panel title="Capabilities"><div className="capability-grid">{[["Physical & operating","Deterministic 8,760 load matching · P50/P90/P99 governance · QA firewall"],["Project finance","CFADS cash-flow modeling · debt sizing · DSCR / LLCR / PLCR"],["Decision & governance","PPA frontier · scenario semantics · audit trail · reproducible outputs"]].map(([a,b])=><div className="capability" key={a}><Icon>◆</Icon><h3>{a}</h3><p>{b}</p></div>)}</div></Panel><Panel title="Featured frozen-model case" note="Selected project from authoritative project master"><div className="featured"><img src="/assets/context/go-mall.svg" alt="" /><div><h2>{featured?.projectName || "Featured project"}</h2><p>{featured?.country} · {fmt(featured?.capacityMw,3)} MW · {text(featured?.physicalStatus)}</p><div className="metric-row">{[[featured?.p50Gwh,"P50 GWh"],[featured?.p90Gwh,"P90 GWh"],[featured?.p99Gwh,"P99 GWh"],[featured?.specificYieldKwhKwp,"Specific yield"]].map(([v,l])=><div className="metric" key={String(l)}><span>{l}</span><strong>{v===null||v===undefined?<Missing />:fmt(v,3)}</strong></div>)}</div><span className={classForStatus(s.decision)}>{s.decision}</span></div></div></Panel></main></>;
}

function Projects({ d }: { d: SiteData }) {
  const ps=d.projects.projects||[], mix=d.projects.countryMix||[];
  return <><Hero eyebrow="PROJECT UNIVERSE · EVIDENCE LINEAGE" title="20 selected projects. 441 preserved observations. No silent data cleaning." subtitle="Observed facts remain distinct from derived values, benchmark assumptions, analyst overlays and scenario inputs. Every row is keyed by the frozen project_id." image="campus" action="Open model evidence" to="/model"/><main className="container"><div className="kpi-grid"><Kpi value={d.projects.candidateHistory} label="Candidate history"/><Kpi value={d.projects.selectedRecords} label="Selected records"/><Kpi value={d.projects.countryMix?.length} label="Countries"/><Kpi value={d.projects.economicsReady} label="Economics-ready"/><Kpi value={d.projects.technicalBlocked} label="Technical block" tone="warn"/><Kpi value={d.projects.rawObservations} label="Raw observations"/></div><div className="two-panel"><Panel title="Economics-ready country capacity (MW)"><BarChart items={mix.map((x:any)=>({label:x.country,value:x.capacityMw}))} unit="MW"/></Panel><Panel title="Physical QA distribution"><BarChart items={[{label:"Within screening band",value:d.physical.distribution.PASS_WITHIN_SCREENING_BAND},{label:"Low-yield review",value:d.physical.distribution.LOW_YIELD_REVIEW},{label:"Extreme block",value:d.physical.distribution.EXTREME_OUTLIER_BLOCK_BASE}]} color="#d39b32"/></Panel></div><Panel title="Capacity versus physical specific yield" note="Points are derived from exact project rows; red is the blocked outlier"><Scatter points={ps.map((p:any)=>({x:p.capacityMw,y:p.specificYieldKwhKwp,label:p.projectName,blocked:p.technicalDataBlocked}))}/></Panel><Panel title="Selected projects (20 records)" note="Exact frozen project IDs · scroll horizontally on mobile"><div className="table-scroll"><table><thead><tr><th>Project</th><th>Country</th><th>Capacity MW</th><th>Observed GWh</th><th>Specific yield</th><th>Physical QA</th><th>Economics</th></tr></thead><tbody>{ps.map((p:any)=><tr key={p.projectId}><td><a className="table-link" href={\`#/energy?project=\${encodeURIComponent(p.projectId)}\`}>{p.projectName}</a><small>{p.projectId}</small></td><td>{p.country}</td><td>{fmt(p.capacityMw,3)}</td><td>{fmt(p.observedGenerationGwh,3)}</td><td>{fmt(p.specificYieldKwhKwp,0)}</td><td><span className={classForStatus(p.physicalStatus)}>{p.physicalStatus}</span></td><td><span className={classForStatus(p.economicsStatus)}>{p.economicsStatus}</span></td></tr>)}</tbody></table></div></Panel></main></>;
}

function Energy({ d }: { d: SiteData }) {
  const all=Object.values(d.energy.projects||{}) as AnyRecord[], route=hashRoute(), defaultId=d.energy.featuredProjectId, selected=all.find(p=>p.projectId===route.project)||all.find(p=>p.projectId===defaultId)||all[0];
  const day=selected?.representativeDay || {};
  return <><Hero eyebrow="ENERGY & PHYSICAL MODEL" title="From annual generation to an auditable 8,760 operating profile." subtitle="The website shows compact hourly aggregates derived from every exact hourly row. It never creates a generic profile or turns a blocked source into a modeled case." image="rooftop" action="View data lineage" to="/projects"/><main className="container"><div className="kpi-grid"><Kpi value={d.energy.screening.PASS_WITHIN_SCREENING_BAND} label="Within screening band"/><Kpi value={d.energy.screening.LOW_YIELD_REVIEW} label="Low-yield review" tone="warn"/><Kpi value={d.energy.screening.EXTREME_OUTLIER_BLOCK_BASE} label="Extreme block" tone="warn"/><Kpi value="900–1,600" label="Screening kWh/kWp"/><Kpi value="3,200" label="Extreme upper firewall"/><Kpi value={d.summary.modeledHourlyRows} label="Modeled hourly rows"/></div><Panel title="Select project"><Selector projects={all} value={selected?.projectId || ""} onChange={()=>{}}/><span className="selector-note">{all.length} economics-ready projects are available; blocked records appear in evidence only.</span></Panel><Panel title="Physical QA scatter"><Scatter points={all.map(p=>({x:p.capacityMw,y:p.specificYieldKwhKwp,label:p.projectName,blocked:p.technicalDataBlocked}))}/></Panel>{selected && <><Panel title={\`\${selected.projectName} · 24-hour operating profile\`} note="Average by hour of day across exact 8,760 rows"><LineChart labels={Array.from({length:24},(_,i)=>\`\${String(i).padStart(2,"0")}:00\`)} unit="kW" series={[{name:"Customer load",values:day.loadKwh||[],color:"#0c4b39"},{name:"Solar generation",values:day.solarKwh||[],color:"#d39b32"},{name:"Self-consumed solar",values:day.selfConsumedKwh||[],color:"#2e7f66"},{name:"Export",values:day.exportKwh||[],color:"#9fbfb0"}]}/></Panel><div className="two-panel"><Panel title="Annual energy balance"><div className="energy-flow"><div><span>Solar generation</span><strong>{fmt(selected.p50Gwh,3)} GWh</strong></div><div><span>Self-consumed</span><strong>{fmt(selected.selfConsumedGwh,3)} GWh</strong></div><div><span>Export</span><strong>{fmt(selected.exportGwh,3)} GWh</strong></div><div><span>Annual load</span><strong>{fmt(selected.annualLoadGwh,3)} GWh</strong></div></div></Panel><Panel title="Physical evidence boundary"><p className="body-copy">{selected.technicalDataBlocked ? "This source is blocked from direct economics. The raw observation is preserved for engineering review; no P50/P90/P99 modeled case is published." : "This profile is a deterministic public-data reconstruction. It is not interval-meter evidence or an engineering production guarantee."}</p><span className={classForStatus(selected.physicalStatus)}>{selected.physicalStatus}</span></Panel></div></>}</main></>;
}

function Economics({ d }: { d: SiteData }) {
  const all=Object.values(d.economics.projects||{}) as AnyRecord[], route=hashRoute(), selected=all.find(p=>p.projectId===route.project)||all.find(p=>p.projectId===d.economics.featuredProjectId)||all[0], cash=d.economics.cashFlows?.[selected?.projectId]||[];
  const frontier=selected;
  return <><Hero eyebrow="ECONOMICS & PPA FRONTIER" title="One tariff. Three stakeholders. A negotiation frontier instead of a fake PPA." subtitle="Every displayed economics value is a read-through from frozen output rows. Missing commercial evidence remains missing and the decision boundary stays indeterminate." image="abstract-panels" action="View risk scenarios" to="/risk"/><main className="container"><Panel title="Select project"><Selector projects={all} value={selected?.projectId||""} onChange={()=>{}}/><span className="selector-note">Reference case: {text(frontier?.referenceCase,"REFERENCE_CASE_NOT_ACTUAL_PPA")}</span></Panel><div className="finance-kpis">{[[frontier?.capexUsd,"CAPEX","usd"],[frontier?.projectNpvUsd,"Project NPV","usd"],[frontier?.projectIrr,"Project IRR","pct"],[frontier?.equityNpvUsd,"Equity NPV","usd"],[frontier?.equityIrr,"Equity IRR","pct"]].map(([v,l,t])=><div key={String(l)}><span>{l}</span><strong>{v===null||v===undefined?<Missing />:t==="usd"?fmtUsd(v):t==="pct"?fmtPct(v):fmt(v)}</strong></div>)}</div><Panel title="Year 1 cash-flow bridge" note={\`Source: v5_1_3_cash_flow.csv · \${selected?.currency || ""}\`}><Waterfall rows={cash}/></Panel><div className="two-panel"><Panel title="Project economics"><div className="metric-grid">{[[frontier?.projectNpvUsd,"NPV"],[frontier?.projectIrr,"IRR"],[frontier?.dscrMin,"Min DSCR"],[frontier?.llcr,"LLCR"],[frontier?.plcr,"PLCR"],[frontier?.debtCapacityUsd,"Debt capacity"]].map(([v,l])=><div className="metric-box" key={String(l)}><span>{l}</span><strong>{String(l).includes("NPV")||String(l).includes("capacity")?fmtUsd(v):String(l)==="IRR"?fmtPct(v):fmt(v,3)}</strong></div>)}</div></Panel><Panel title="PPA frontier" note="Positions are computed from selected-project source values"><div className="frontier"><div className="frontier-axis"><span>Customer ceiling</span><span>Sponsor floor</span><span>Lender floor</span></div><div className="frontier-line">{[["customerCeiling",frontier?.customerCeiling,"blue"],["sponsorFloor",frontier?.sponsorFloor,"red"],["lenderFloor",frontier?.lenderFloor,"green"]].map(([k,v,c])=>{const values=[frontier?.customerCeiling,frontier?.sponsorFloor,frontier?.lenderFloor].map(num).filter((x):x is number=>x!==null);const min=Math.min(...values,0),max=Math.max(...values,1),pos=num(v)===null?null:(Number(v)-min)/(max-min)*100;return <div key={String(k)} className={\`frontier-marker \${c}\`} style={pos===null?undefined:{left:\`\${Math.max(0,Math.min(100,pos))}%\`}}>{pos===null?<Missing label="Missing source value" />:<><i /><b>{fmt(v,2)}</b></>}</div>})}</div><div className="frontier-status"><b>{text(frontier?.negotiationStatus)}</b><span>{frontier?.negotiationLower===null||frontier?.negotiationUpper===null?<Missing />:\`Width \${fmt((frontier.negotiationUpper-frontier.negotiationLower),2)} \${frontier.currency||""}/kWh\`}</span></div></div></Panel></div><Panel title="Commercial boundary"><div className="decision-banner"><Icon>⚖</Icon><div><strong>{text(frontier?.decision,"INDETERMINATE_MISSING_COMMERCIAL_DATA")}</strong><p>Exact PPA and commercial terms are not public. The frontier is a standardized negotiation analysis, not an actual PPA or transaction commitment.</p></div></div></Panel></main></>;
}

function Debt({ d }: { d: SiteData }) {
  const all=Object.values(d.debt.projects||{}) as AnyRecord[], route=hashRoute(), selected=all.find(p=>p.projectId===route.project)||all.find(p=>p.projectId===d.debt.featuredProjectId)||all[0], schedule=selected?.schedule||[];
  return <><Hero eyebrow="PROJECT FINANCE · DEBT & CREDIT" title="Debt sized from CFADS. Not from a hard-coded leverage assumption." subtitle="Coverage metrics, capacity and amortization are presented exactly as produced by the frozen model. Downside does not resize contractual principal to make stress pass." image="debt-texture" action="View risk semantics" to="/risk"/><main className="container"><Panel title="Select project"><Selector projects={all} value={selected?.projectId||""} onChange={()=>{}}/></Panel><div className="finance-kpis">{[[selected?.debtCapacityUsd,"Debt capacity","usd"],[selected?.dscrMin,"Min DSCR","x"],[selected?.llcr,"LLCR","x"],[selected?.plcr,"PLCR","x"],[selected?.bindingConstraint,"Binding constraint","text"]].map(([v,l,t])=><div key={String(l)}><span>{l}</span><strong>{v===null||v===undefined?<Missing />:t==="usd"?fmtUsd(v):t==="x"?fmt(v,3):text(v)}</strong></div>)}</div><div className="two-panel"><Panel title="Opening / closing debt balance"><LineChart labels={schedule.map((r:any)=>String(r.year))} unit="debt" series={[{name:"Opening balance",values:schedule.map((r:any)=>num(r.opening)||0),color:"#0c4b39"},{name:"Closing balance",values:schedule.map((r:any)=>num(r.closing)||0),color:"#d39b32"}]}/></Panel><Panel title="DSCR by year"><LineChart labels={schedule.map((r:any)=>String(r.year))} unit="DSCR x" series={[{name:"DSCR",values:schedule.map((r:any)=>num(r.dscr)||0),color:"#0c4b39"},{name:"Target",values:schedule.map(()=>1.35),color:"#d39b32"}]}/></Panel></div><Panel title="Debt amortization schedule" note="Exact rows from v5_1_3_debt_schedule.csv"><div className="table-scroll"><table><thead><tr><th>Year</th><th>Opening</th><th>Principal</th><th>Interest</th><th>Debt service</th><th>Closing</th><th>DSCR</th></tr></thead><tbody>{schedule.map((r:any)=><tr key={String(r.year)}><td>{r.year}</td><td>{fmt(r.opening,0)}</td><td>{fmt(r.principal,0)}</td><td>{fmt(r.interest,0)}</td><td>{fmt(r.debtService,0)}</td><td>{fmt(r.closing,0)}</td><td>{fmt(r.dscr,3)}</td></tr>)}</tbody></table></div></Panel><Panel title="Debt policy semantics"><div className="policy-grid">{[["DSCR sculpting target","Minimum period coverage guardrail"],["LLCR minimum","PV of loan-life CFADS / opening debt"],["PLCR minimum","PV of project-life CFADS / opening debt"],["Maximum leverage","Capital structure cap"]].map(([a,b])=><div key={a}><b>{a}</b><span>{b}</span></div>)}</div><div className="contractual-banner"><Icon>✓</Icon><div><strong>NO_NEW_DEBT preserves the base contractual schedule.</strong><p>When a downside breaks constraints, mitigation is required; the schedule is not silently re-sculpted.</p></div></div></Panel></main></>;
}

function Risk({ d }: { d: SiteData }) {
  const route=hashRoute(), projects=d.projects.projects||[], names=Object.fromEntries(projects.map((p:any)=>[p.projectId,p.projectName])), rows=d.risk.rows||[], selectedId=route.project||d.risk.featuredProjectId, selected=rows.filter((r:any)=>r.projectId===selectedId);
  return <><Hero eyebrow="RISK & SCENARIOS" title="Nine scenarios. Contractual debt. No downside self-healing." subtitle="Every project is stress-tested across nine scenarios. The website exposes the actual scenario rows and keeps debt semantics visible." image="risk-texture" action="Explore all projects" to="/projects"/><main className="container"><div className="kpi-grid"><Kpi value={projects.filter((p:any)=>!p.technicalDataBlocked).length} label="Economics-ready projects"/><Kpi value="9" label="Scenarios per project"/><Kpi value={rows.length} label="Governed scenario rows"/><Kpi value="0" label="Capital allocations"/></div><Panel title="Selected project scenario coverage"><Selector projects={projects.filter((p:any)=>!p.technicalDataBlocked)} value={selectedId} onChange={()=>{}}/><div className="two-panel compact"><BarChart items={selected.map((r:any)=>({label:text(r.scenario).replaceAll("_"," "),value:r.minDscr}))}/><div className="scenario-table"><table><thead><tr><th>Scenario</th><th>Debt mode</th><th>Min DSCR</th><th>Principal preserved</th></tr></thead><tbody>{selected.map((r:any)=><tr key={r.scenario}><td>{r.scenario}</td><td>{r.debtMode}</td><td className={num(r.minDscr)!==null&&num(r.minDscr)!<1?"negative":""}>{fmt(r.minDscr,3)}</td><td>{r.principalPreserved===null?"N/A":r.principalPreserved?"YES":"NO"}</td></tr>)}</tbody></table></div></div></Panel><Panel title="19 × 9 scenario heatmap" note="Hover a cell for project_id and exact source scenario"><Heatmap rows={rows} names={names}/></Panel><Panel title="Contractual semantics"><div className="semantics-grid">{[["BASE","RESIZED_DEBT"],["P90_ENERGY","FIXED_CONTRACTUAL_SCHEDULE"],["CAPEX_OVERRUN","NO_NEW_DEBT"],["INTEREST_RATE_SHOCK","FIXED_CONTRACTUAL_SCHEDULE"],["COD_DELAY","FIXED_CONTRACTUAL_SCHEDULE"],["OPEX_INFLATION","FIXED_CONTRACTUAL_SCHEDULE"],["OFFTAKER_NONPAYMENT","FIXED_CONTRACTUAL_SCHEDULE"],["OFFTAKER_TERMINATION","NO_NEW_DEBT"],["COMBINED_DOWNSIDE","NO_NEW_DEBT"]].map(([a,b])=><div key={a}><b>{a}</b><span>{b}</span></div>)}</div></Panel></main></>;
}

function Diligence({ d }: { d: SiteData }) {
  const items=d.diligence.projects||[], control=(d.diligence.portfolioControl||[])[0]||{};
  return <><Hero eyebrow="DILIGENCE SHORTLIST" title="A diligence shortlist. Not an invented investment portfolio." subtitle="The shortlist is derived from economics-ready records and explicit commercial evidence boundaries. Capital allocation remains disabled while transaction evidence is open." image="industrial-panorama" action="View economics" to="/economics"/><main className="container"><div className="kpi-grid"><Kpi value={items.length} label="Diligence records"/><Kpi value={0} label="Approved allocations"/><Kpi value={fmtUsd(control.equity_budget_usd)} label="Equity budget"/><Kpi value={d.diligence.commercialMode} label="Commercial mode"/><Kpi value={d.diligence.transactionEvidence} label="Transaction evidence" tone="warn"/></div><Panel title="Portfolio control boundary"><div className="decision-grid"><div className="decision-card"><Icon>▤</Icon><b>Capital allocation</b><strong>{text(d.diligence.capitalAllocation)}</strong></div><div className="decision-card warning"><Icon>⚖</Icon><b>Decision</b><strong>{text(d.diligence.decision)}</strong></div><div className="decision-card"><Icon>✓</Icon><b>Evidence</b><strong>{text(d.diligence.transactionEvidence)}</strong></div></div></Panel><Panel title="Diligence shortlist (source-backed rows)"><div className="table-scroll"><table><thead><tr><th>Project</th><th>Country</th><th>Zone status</th><th>Zone width</th><th>Equity required</th><th>Shortlist type</th><th>Decision</th></tr></thead><tbody>{items.map((r:any)=><tr key={r.project_id}><td>{r.projectName}<small>{r.project_id}</small></td><td>{r.country}</td><td><span className={classForStatus(r.zone_status)}>{r.zone_status}</span></td><td>{fmt(r.zone_width_local_per_kwh,2)}</td><td>{fmtUsd(r.equity_required_usd)}</td><td>{r.shortlist_type}</td><td>{r.decision}</td></tr>)}</tbody></table></div></Panel><Panel title="Decision framework"><div className="framework-grid">{[["Commercial validation","Secure exact PPA terms, credit support and termination rights."],["Technical validation","Validate design, interconnection, site control and construction plan."],["Evidence collection","Collect signed PPA / term sheet, customer credit evidence and invoicing controls."],["Credit review","Assess sponsor strength, guarantees, covenants and DSCR headroom."]].map(([a,b])=><div className="framework-card" key={a}><Icon>◆</Icon><h3>{a}</h3><p>{b}</p></div>)}</div><div className="allocation-banner">CAPITAL ALLOCATION DISABLED · Exact transaction evidence remains open.</div></Panel></main></>;
}

function Model({ d }: { d: SiteData }) {
  const m=d.model, s=d.summary, group=[["GOVERNANCE",m.workbookSheets.slice(0,5)],["DATA / PHYSICAL",m.workbookSheets.slice(5,13)],["MARKET / ASSUMPTIONS",m.workbookSheets.slice(13,20)],["FINANCE",m.workbookSheets.slice(20)]];
  return <><Hero eyebrow="MODEL & QA" title="A model is only useful if its numbers can be traced." subtitle="Runtime identity, workbook map, source boundary and reconciliation controls are presented as a view of the frozen model, not a second calculation engine." image="workbook" action="View GitHub source" to="/"/><main className="container"><div className="finance-kpis">{[[m.modelTag,"Model tag","text"],[\`\${m.modelSha.slice(0,10)}…\`,"Exact model SHA","text"],[m.workbookSheets.length,"Workbook sheets","text"],[m.regressionTests,"Regression tests","text"],[m.semanticControls,"Semantic controls","text"],["PASS","Reproducibility","text"]].map(([v,l])=><div key={String(l)}><span>{l}</span><strong>{text(v)}</strong></div>)}</div><Panel title="Model architecture & data flow"><div className="architecture">{["54 candidate history","441 observations","20 selected projects","Physical QA","19 model-ready","166,440 hourly rows","CFADS","Debt sizing","PPA frontier","Returns","171 scenario rows"].map((x,i)=><div key={x} className={i===3||i===6||i===7?"architecture-accent":""}><Icon>{i===3?"✓":"◆"}</Icon><b>{x}</b>{i<10&&<span>→</span>}</div>)}</div></Panel><Panel title="Workbook map (28 exact sheets)"><div className="sheet-groups">{group.map(([title,sheets])=><div key={title}><h3>{title}</h3>{(sheets as string[]).map(sheet=><div className="sheet" key={sheet}>▣ {sheet}</div>)}</div>)}</div></Panel><Panel title="Source-to-website reconciliation"><div className="recon-grid">{[["PROJECT IDS","20/20 MATCH"],["PHYSICAL STATUS","20/20 MATCH"],["ECONOMICS ROWS","19/19 MATCH"],["SCENARIOS","171/171 MATCH"],["WORKBOOK SHEETS","28/28 MATCH"],["MODEL SHA",m.modelSha.slice(0,10)+"…"]].map(([a,b])=><div key={a}><Icon>✓</Icon><b>{a}</b><strong>{b}</strong></div>)}</div></Panel><Panel title="Claim boundary"><div className="decision-grid"><div className="decision-card"><Icon>⚑</Icon><b>PPA</b><strong>{s.ppaMode}</strong></div><div className="decision-card warning"><Icon>⚖</Icon><b>Decision</b><strong>{s.decision}</strong></div><div className="decision-card"><Icon>▤</Icon><b>Transaction evidence</b><strong>{s.transactionEvidence}</strong></div></div><p className="body-copy">Public-data reconstruction only. This site does not represent confidential PPA pricing, lender commitment, bankable technical yield, legal/tax sign-off or investment committee approval.</p></Panel></main></>;
}

function Loading() { return <div className="loading"><div className="loader" /><p>Loading frozen-model presentation data…</p></div>; }
function App() {
  const [route,setRoute]=useState(hashRoute());
  const [data,setData]=useState<SiteData|null>(null);
  const [error,setError]=useState("");
  useEffect(()=>{const handler=()=>setRoute(hashRoute());window.addEventListener("hashchange",handler);return()=>window.removeEventListener("hashchange",handler)},[]);
  useEffect(()=>{Promise.all(["summary","projects","physical","energy","economics","debt","risk","diligence","model"].map(async key=>[key,await fetch(\`data/\${key}.json\`).then(r=>{if(!r.ok)throw new Error(\`\${key} payload unavailable\`);return r.json()})] as const)).then(entries=>setData(Object.fromEntries(entries))).catch(e=>setError(String(e.message||e)));},[]);
  const Page=useMemo(()=>({"/":Overview,"/projects":Projects,"/energy":Energy,"/economics":Economics,"/debt":Debt,"/risk":Risk,"/diligence":Diligence,"/model":Model} as Record<string,(p:{d:SiteData})=>JSX.Element>)[route.path]||Overview,[route.path]);
  if(error)return <div className="loading"><h1>Presentation data unavailable</h1><p>{error}</p></div>;
  if(!data)return <Loading />;
  return <Shell path={route.path} summary={data.summary}><Page d={data}/></Shell>;
}
export default App;
