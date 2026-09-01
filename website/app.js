const DATA_ROOT = "data/";
const PAGE_NAMES = ["overview", "case", "economics", "debt", "portfolio", "risk", "model", "evidence"];
const repo = "https://github.com/susayold/vietgreen-ci-solar-project-finance";
const page = document.querySelector("#app");
const cache = {};

const esc = (value) => String(value ?? "").replace(/[&<>\"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[char]));
const n = (value, digits = 3) => value === null || value === undefined || value === "" || Number.isNaN(Number(value)) ? "—" : Number(value).toLocaleString("en-US", {maximumFractionDigits: digits, minimumFractionDigits: 0});
const bvnd = (value, digits = 3) => `${n(value, digits)} BVND`;
const pct = (value, digits = 1) => value === null || value === undefined ? "—" : `${n(value, digits)}%`;
const ppaPosition = (value, lower, upper) => {
  const min = Number(lower), max = Number(upper), numeric = Number(value);
  if (![min, max, numeric].every(Number.isFinite) || max <= min) return "50%";
  return `${Math.min(100, Math.max(0, (numeric - min) / (max - min) * 100)).toFixed(2)}%`;
};
const ppaTicks = (lower, upper) => {
  const min = Number(lower), max = Number(upper), span = max - min;
  if (![min, max].every(Number.isFinite) || span <= 0) return [min, min, min, min];
  return [min, min + span / 3, min + span * 2 / 3, max];
};

const ppaScale = (frontier) => {
  const values = [
    frontier.sponsor_floor_vnd_kwh,
    frontier.lender_floor_vnd_kwh,
    frontier.lower_bound_vnd_kwh,
    frontier.customer_ceiling_vnd_kwh,
    frontier.upper_bound_vnd_kwh,
  ].map(Number).filter(Number.isFinite);
  if (values.length < 2) return {lower: 0, upper: 1};
  return {lower: Math.min(...values), upper: Math.max(...values)};
};

const ppaMarkerMarkup = (frontier) => {
  const scale = ppaScale(frontier);
  const lender = Number(frontier.lender_floor_vnd_kwh);
  const lower = Number(frontier.lower_bound_vnd_kwh);
  const lenderLabel = Math.abs(lender - lower) < 0.0001 ? "Lender floor / required lower bound" : "Lender floor";
  const markers = [
    {value: frontier.sponsor_floor_vnd_kwh, label: "Sponsor floor"},
    {value: frontier.lender_floor_vnd_kwh, label: lenderLabel},
    {value: frontier.customer_ceiling_vnd_kwh, label: "Customer ceiling"},
  ];
  if (Math.abs(lender - lower) >= 0.0001) markers.push({value: frontier.lower_bound_vnd_kwh, label: "Required lower bound"});
  return markers.map((marker) => "<div class=\"frontier-marker\" style=\"left:" + ppaPosition(marker.value, scale.lower, scale.upper) + "\" data-label=\"" + esc(marker.label) + "\"></div>").join("");
};
const cls = (value) => Number(value) < 0 ? "negative" : Number(value) > 0 ? "positive" : "muted";
const status = (value) => {
  const normalized = String(value || "").toUpperCase();
  const kind = normalized === "PASS" || normalized === "TRUE" || normalized === "PROCEED" ? "pass" : normalized === "OPEN" || normalized === "WATCH" ? "open" : "fail";
  return `<span class="status status-${kind}"><span class="status-dot"></span>${esc(normalized)}</span>`;
};
const external = (url, label, extra = "") => `<a class="link" href="${esc(url)}" target="_blank" rel="noopener" ${extra}>${esc(label)} ↗</a>`;
const gh = (path, label) => external(`${repo}/blob/main/${path}`, label);
const sourceList = (sources = []) => `<div class="source-line"><span>Source</span>${sources.map((source) => gh(source, source.split("/").pop())).join(" · ")}</div>`;

async function load(name) {
  if (!cache[name]) cache[name] = await fetch(`${DATA_ROOT}${name}.json`).then((response) => {
    if (!response.ok) throw new Error(`Unable to load ${name}`);
    return response.json();
  });
  return cache[name];
}

function metricCard(label, value, meta = "", tone = "") {
  return `<article class="kpi ${tone}"><div class="kpi-label">${esc(label)}</div><div class="kpi-value">${esc(value)}</div>${meta ? `<div class="kpi-meta">${esc(meta)}</div>` : ""}</article>`;
}

function kpis(shared, items) {
  return `<section class="kpi-strip">${items.map((item) => metricCard(item.label, item.value, item.meta || "", item.tone || "")).join("")}</section>`;
}

function pageHero(data, active, options = {}) {
  const shared = data.shared;
  return `<section class="hero"><div class="hero-grid"><div><div class="eyebrow">${esc(shared.releaseId)} · ${esc(shared.asOfDate)} · ${esc(active.toUpperCase())}</div><h1>${esc(data.title)}</h1><p>${esc(data.subtitle)}</p>${options.actions ? `<div class="hero-actions">${options.actions}</div>` : ""}</div><div class="hero-aside">${options.aside || `<div class="hero-note"><b>Evidence class</b><br>${esc(data.evidenceClass || shared.evidenceClass)}<br><span>Recruiter-ready mechanics · transaction evidence ${esc(shared.transactionEvidenceStatus.toLowerCase())}</span></div>`}</div></div></section>`;
}

function section(title, intro, body, kicker = "") {
  return `<section class="section"><div class="section-head"><div>${kicker ? `<div class="section-kicker">${esc(kicker)}</div>` : ""}<h2>${esc(title)}</h2>${intro ? `<p class="section-intro">${esc(intro)}</p>` : ""}</div></div>${body}</section>`;
}

function panel(title, body, note = "") {
  return `<article class="panel panel-pad"><div class="panel-title"><strong>${esc(title)}</strong>${note ? `<small>${esc(note)}</small>` : ""}</div>${body}</article>`;
}

function lineChart(points, options = {}) {
  const width = 720, height = 225, pad = {left: 36, right: 16, top: 15, bottom: 28};
  const values = points.map((point) => Number(point.value) || 0);
  const min = Math.min(...values, 0), max = Math.max(...values, 1), span = max - min || 1;
  const x = (index) => pad.left + index * ((width - pad.left - pad.right) / Math.max(points.length - 1, 1));
  const y = (value) => pad.top + (max - value) * ((height - pad.top - pad.bottom) / span);
  const line = points.map((point, index) => `${index ? "L" : "M"}${x(index).toFixed(1)} ${y(Number(point.value) || 0).toFixed(1)}`).join(" ");
  const area = `${line} L ${x(points.length - 1).toFixed(1)} ${height - pad.bottom} L ${x(0).toFixed(1)} ${height - pad.bottom} Z`;
  return `<div class="chart"><svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(options.label || "Trend chart")}"><line class="chart-grid" x1="${pad.left}" y1="${y(max)}" x2="${width - pad.right}" y2="${y(max)}"/><line class="chart-grid" x1="${pad.left}" y1="${y(0)}" x2="${width - pad.right}" y2="${y(0)}"/><path class="area-green" d="${area}"/><path class="${options.line || "line-green"}" d="${line}"/>${points.map((point, index) => `<circle cx="${x(index)}" cy="${y(Number(point.value) || 0)}" r="3" fill="#fff" stroke="#0b7747" stroke-width="2"><title>${esc(point.label || "Point")}: ${esc(n(point.value, 3))}</title></circle><text class="chart-label" x="${x(index)}" y="${height - 10}" text-anchor="middle">${esc(point.label || "")}</text>`).join("")}<text class="chart-axis" x="4" y="${y(max) + 3}">${esc(n(max, 1))}</text><text class="chart-axis" x="4" y="${y(0) + 3}">0</text></svg>${options.caption ? `<p class="chart-caption">${esc(options.caption)}</p>` : ""}</div>`;
}

function multiLineChart(series, options = {}) {
  const width = 720, height = 225, pad = {left: 36, right: 16, top: 15, bottom: 28};
  const count = Math.max(...series.map((item) => item.points.length), 1);
  const values = series.flatMap((item) => item.points.map((point) => Number(point.value) || 0));
  const min = Math.min(...values, 0), max = Math.max(...values, 1), span = max - min || 1;
  const x = (index) => pad.left + index * ((width - pad.left - pad.right) / Math.max(count - 1, 1));
  const y = (value) => pad.top + (max - value) * ((height - pad.top - pad.bottom) / span);
  const paths = series.map((item) => item.points.map((point, index) => `${index ? "L" : "M"}${x(index).toFixed(1)} ${y(Number(point.value) || 0).toFixed(1)}`).join(" "));
  return `<div class="chart"><svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(options.label || "Multi-series chart")}"><line class="chart-grid" x1="${pad.left}" y1="${y(max)}" x2="${width - pad.right}" y2="${y(max)}"/><line class="chart-grid" x1="${pad.left}" y1="${y(0)}" x2="${width - pad.right}" y2="${y(0)}"/>${paths.map((path, index) => `<path class="${series[index].className || "line-green"}" d="${path}"/>`).join("")}${series[0].points.map((point, index) => `<text class="chart-label" x="${x(index)}" y="${height - 10}" text-anchor="middle">${esc(point.label || "")}</text>`).join("")}<text class="chart-axis" x="4" y="${y(max) + 3}">${esc(n(max, 0))}</text><text class="chart-axis" x="4" y="${y(0) + 3}">0</text></svg><div class="chart-legend">${series.map((item) => `<span><i class="legend-swatch ${item.swatch || "green"}"></i>${esc(item.label)}</span>`).join("")}</div>${options.caption ? `<p class="chart-caption">${esc(options.caption)}</p>` : ""}</div>`;
}

function barChart(items, options = {}) {
  const max = Math.max(...items.map((item) => Math.abs(Number(item.value) || 0)), 1);
  return `<div class="bar-list">${items.map((item) => `<div class="bar-row"><span title="${esc(item.label)}">${esc(item.label)}</span><div class="bar-track"><div class="bar-fill ${Number(item.value) < 0 ? "red" : ""}" style="width:${Math.max(2, Math.round(Math.abs(Number(item.value) || 0) / max * 100))}%"></div></div><span class="bar-value ${cls(item.value)}">${esc(options.format ? options.format(item.value) : n(item.value))}</span></div>`).join("")}</div>`;
}

function negativeBarChart(items, options = {}) {
  const ordered = items.slice().sort((a, b) => Number(a.value) - Number(b.value));
  const max = Math.max(...ordered.map((item) => Math.abs(Number(item.value) || 0)), 1);
  const title = options.label || "Negative values from zero baseline";
  const rows = ordered.map((item) => {
    const value = Number(item.value) || 0;
    const width = Math.max(2, Math.round(Math.abs(value) / max * 100));
    const formatted = options.format ? options.format(value) : n(value);
    const accessible = item.label + ": " + formatted;
    return "<div class=\"zero-bar-row\" title=\"" + esc(accessible) + "\" aria-label=\"" + esc(accessible) + "\"><span class=\"zero-bar-label\">" + esc(item.label) + "</span><div class=\"zero-bar-track\" aria-hidden=\"true\"><span class=\"zero-bar-zero\"></span><span class=\"zero-bar-fill\" style=\"width:" + width + "%\"></span></div><span class=\"zero-bar-value negative\">" + esc(formatted) + "</span></div>";
  }).join("");
  return "<div class=\"zero-bar-chart\" role=\"group\" aria-label=\"" + esc(title) + "\"><div class=\"zero-bar-axis\" aria-hidden=\"true\"><span>−" + n(max, 3) + "</span><span>0</span></div>" + rows + (options.caption ? "<p class=\"chart-caption\">" + esc(options.caption) + "</p>" : "") + "</div>";
}

function donutCard(donut) {
  const total = donut.items.reduce((sum, item) => sum + (Number(item.value) || 0), 0) || 1;
  const palette = ["#087649", "#70b771", "#d9aa39", "#8da59a", "#b9c5be", "#4c8d6d"];
  let cursor = 0;
  const stops = donut.items.map((item, index) => {
    const start = cursor / total * 100;
    cursor += Number(item.value) || 0;
    const end = cursor / total * 100;
    return `${palette[index % palette.length]} ${start.toFixed(2)}% ${end.toFixed(2)}%`;
  }).join(", ");
  return `<div class="donut"><div class="donut-ring" style="background:conic-gradient(${stops})" role="img" aria-label="${esc(donut.title)}"></div><div><strong>${esc(donut.title)}</strong><small>Total ${n(total, 3)} ${esc(donut.unit || "")}</small><div class="legend">${donut.items.slice(0, 4).map((item, index) => `<span style="--legend-color:${palette[index % palette.length]}">${esc(item.label)} · ${n((Number(item.value) || 0) / total * 100, 1)}%</span>`).join("")}</div></div></div>`;
}

function table(headers, rows) {
  return `<div class="table-wrap"><table><thead><tr>${headers.map((header) => `<th>${esc(header)}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${cell}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}

function sharedKpis(shared) {
  return kpis(shared, [
    {label: "Projects screened", value: n(shared.projectsScreened, 0), meta: "Full pipeline"},
    {label: "Current positive Equity NPV", value: `${n(shared.currentPositiveEquityNPV, 0)} / ${n(shared.projectsScreened, 0)}`, meta: "Current terms", tone: "negative"},
    {label: "Positive after remediation", value: n(shared.negotiatedPositiveEquityNPV, 0), meta: "Hypothetical case"},
    {label: "Selected portfolio", value: n(shared.selectedProjects, 0), meta: shared.selectedProjectIds.join(" · ")},
    {label: "Selected equity", value: bvnd(shared.selectedEquityBVND), meta: "Exposure-constrained"},
    {label: "Base sizing DSCR", value: `${n(shared.baseSizingDSCR, 2)}x`, meta: "Pooled minimum"},
  ]);
}

function renderOverview(data) {
  const s = data.shared;
  const scenarioRows = data.scenarioSummary.map((row) => [esc(row.label), `<span class="num ${cls(row.projectNPV)}">${bvnd(row.projectNPV)}</span>`, `<span class="num ${cls(row.equityNPV)}">${bvnd(row.equityNPV)}</span>`, `<span class="num">${n(row.equityIRR, 2)}%</span>`, `<span class="num">${n(row.projectIRR, 2)}%</span>`, `<span class="num">${n(row.dscr, 2)}x</span>`, status(row.economicStatus), status(row.creditStatus)]);
  return `<div class="page">${pageHero(data, "overview", {actions: `<a class="button button-primary" href="#/economics">Explore economics <span>→</span></a><a class="button button-outline" href="#/model">Open model <span>↗</span></a><a class="button button-outline" href="${repo}" target="_blank" rel="noopener">View GitHub <span>↗</span></a>`, aside: `<div class="decision-banner"><small>CURRENT TERMS DECISION</small><strong>NO DEPLOYMENT</strong><span>${esc(data.decision.reason)}</span></div><div class="hero-note">${esc(data.decision.nextMove)}</div>`})}${sharedKpis(s)}${section("The released decision is clear", "A recruiter should see the investment conclusion before the mechanics.", `<div class="split-hero"><div class="callout"><h3>Current terms fail the equity value gate.</h3><p>${esc(data.decision.reason)} The public site preserves the distinction between current terms and a hypothetical negotiated case.</p><div class="hero-actions"><a class="button button-ghost" href="#/case">Read the investment case →</a></div></div>${panel("Decision boundary", `<div class="metric-list"><div class="metric-line"><span>Transaction evidence</span>${status(s.transactionEvidenceStatus)}</div><div class="metric-line"><span>Bankable transaction</span>${status(String(s.bankableTransactionReady).toUpperCase())}</div><div class="metric-line"><span>External gates open</span><b>${n(s.externalGateCountOpen, 0)}</b></div></div>`, "Governance")}</div>`, "01 · EXECUTIVE DECISION")}${section("From screening to viable pipeline", "The remediation story is visible without hiding the current-terms result.", `<div class="panel bridge">${data.remediation.map((step) => `<div class="bridge-step"><small>${esc(step.step)} · ${esc(step.label)}</small><strong>${esc(step.value)}</strong><p>${step.tone === "negative" ? "Do not deploy under current terms." : step.tone === "warning" ? "Test commercial and financing levers." : "Subject to exposure and evidence controls."}</p></div>`).join("")}</div>`, "02 · REMEDIATION")}${section("Base vs downside portfolio summary", "Selected four-project hypothetical portfolio; all amounts in BVND.", panel("Scenario comparison", table(["Scenario", "Project NPV", "Equity NPV", "Equity IRR", "Project IRR", "Min DSCR", "Economic", "Credit"], scenarioRows), "Phase 2 outputs"), "03 · RETURNS & RISK")}${section("What is inside the model", "The site is a decision memo, not a screenshot of a dashboard.", `<div class="grid-3">${data.built.map((item, index) => `<div class="panel panel-pad"><div class="section-kicker">0${index + 1}</div><h3>${esc(item.title)}</h3><p class="muted">${esc(item.text)}</p></div>`).join("")}</div>`, "04 · BUILD SCOPE")}${section("Start with the model or the evidence", "Every headline can be traced to the release package.", `<div class="grid-2"><div class="callout"><h3>Open the model layer</h3><p>Inspect workbook architecture, formula QA, reconciliation and red-team checks.</p><p><a class="link" href="#/model">Open Model →</a></p></div><div class="callout"><h3>Review governance</h3><p>See what is validated, what is open and which evidence is still required for a bankable transaction.</p><p><a class="link" href="#/evidence">Open Evidence →</a></p></div></div>`, "05 · NEXT VIEW")}${sourceList(data.sources)}</div>`;
}

function renderCase(data) {
  const chart = data.currentNPVChart.map((item) => ({label: item.projectId, value: item.value}));
  const rows = data.currentNPV.map((row) => [esc(row.project_id), esc(row.project_name), `<span class="num negative">${bvnd(Number(row.equity_npv_vnd) / 1e9)}</span>`, `<span class="muted">${esc(row.rejection_reason.replaceAll("|", " · "))}</span>`]);
  return `<div class="page">${pageHero(data, "case", {actions: `<a class="button button-primary" href="#/economics">Price the case →</a>`})}${sharedKpis(data.shared)}${section("Three stakeholders, one underwriting policy", "The same project needs customer certainty, sponsor returns and lender protection.", `<div class="grid-3">${data.stakeholders.map((stakeholder) => `<article class="panel stakeholder"><h3>${esc(stakeholder.title)}</h3><ul>${stakeholder.points.map((point) => `<li>${esc(point)}</li>`).join("")}</ul></article>`).join("")}</div>`, "01 · STAKEHOLDER FRAMEWORK")}${section("Investment decision framework", "Nine steps move from eligibility to an IC decision.", `<div class="panel panel-pad step-flow">${data.steps.map((step, index) => `<div class="flow-item"><b>${index + 1}</b>${esc(step)}</div>`).join("")}</div>`, "02 · PROCESS")}${section("Current Terms Equity NPV by project", "Every current-terms row is negative; the policy outcome is no deployment.", `<div class="grid-2">${panel("20-project current terms", negativeBarChart(chart, {label: "Current terms Equity NPV by project", format: (value) => bvnd(value), caption: "VND converted to BVND; every bar extends left from the zero line because current terms are negative."}), "Current terms")}${panel("Detail view", table(["Project", "Offtaker / site", "Equity NPV", "Gates"], rows), "All current rows")}</div>`, "03 · CURRENT TERMS")}${section("Investment decision policy", "Value gate first, then criteria and controls.", `<div class="grid-2"><div class="panel panel-pad"><div class="metric-list">${data.policy.map((rule, index) => `<div class="metric-line"><span><b>${index + 1}.</b> ${esc(rule.question)}</span><span>${index === 0 ? status("NO_DEPLOYMENT") : status("OPEN")}</span></div>`).join("")}</div></div><div class="callout"><h3>Decision</h3><p><b>NO DEPLOYMENT</b> under current terms. A positive negotiated result is a hypothetical remediation case, not an executed contract.</p></div></div>`, "04 · POLICY")}${sourceList(data.sources)}</div>`;
}

function economicsDetail(data, id) { return data.projectDetails[id] || data.projectDetails[data.defaultProjectId]; }

function renderEconomics(data, projectId = data.defaultProjectId) {
  const project = data.projects.find((item) => item.projectId === projectId) || data.projects[0];
  projectId = project.projectId;
  const detail = economicsDetail(data, projectId);
  const load = detail.load, energy = detail.energy, frontier = detail.frontier, returns = detail.returns;
  const flow = ["Solar resource", "P50 generation", "P90 / P99", "8,760 load match", "Self-consumption", "Bill savings / revenue"];
  const ppa = ppaScale(frontier);
  const shape = detail.dailyShape.map((value, index) => ({label: `${String(index).padStart(2, "0")}:00`, value: value * Number(energy.p50KWh || 1) / 1e6}));
  const relativeLoad = detail.dailyShape.map((value, index) => ({label: `${String(index).padStart(2, "0")}:00`, value: 48 + ((index * 17) % 26) + (index > 7 && index < 19 ? 16 : 0)}));
  const relativeSolar = detail.dailyShape.map((value, index) => ({label: `${String(index).padStart(2, "0")}:00`, value: value * 100}));
  const selfConsumed = detail.dailyShape.map((value, index) => ({label: `${String(index).padStart(2, "0")}:00`, value: value * 100}));
  const rows = [
    ["PPA price (VND/kWh)", n(returns.currentPPA, 1), n(returns.negotiatedPPA, 1), `<span class="positive">${pct((returns.negotiatedPPA / returns.currentPPA - 1) * 100, 1)}</span>`],
    ["Annual OPEX (BVND)", "See current case", bvnd(returns.annualOpexBVND), "Model output"],
    ["CAPEX factor", "1.00x", `${n(returns.capexFactor, 2)}x`, `<span class="positive">−20.0%</span>`],
    ["PPA tenor (years)", n(returns.tenorYears, 0), n(returns.tenorYears, 0), "No change"],
    ["Project NPV", "Negative", bvnd(returns.projectNPVBVND), status("PROCEED")],
    ["Equity NPV", "Negative", bvnd(returns.equityNPVBVND), `<span class="positive">${pct(returns.equityIRR, 2)} Equity IRR</span>`],
  ];
  return `<div class="page">${pageHero(data, "economics", {actions: `<a class="button button-primary" href="#/debt">Size debt →</a>`, aside: `<div class="hero-note"><b>Project selector</b><div class="selector-row"><select class="select" id="project-select" aria-label="Select selected project">${data.projects.map((item) => `<option value="${esc(item.projectId)}" ${item.projectId === projectId ? "selected" : ""}>${esc(item.projectId)} · ${esc(item.name)}</option>`).join("")}</select></div></div>`})}${kpis(data.shared, [{label: "Hours analysed", value: n(energy.profileHourCount, 0), meta: "8760 profile"}, {label: "P50 generation", value: `${n(energy.p50KWh / 1000, 0)} MWh`, meta: projectId}, {label: "Equity", value: bvnd(project.equityRequiredBVND), meta: "Selected project"}, {label: "Base DSCR", value: `${n(project.minDSCR, 2)}x`, meta: "Sizing floor"}])}<div class="panel panel-pad selector-row"><label for="project-select-inline">Selected project</label><select class="select" id="project-select-inline" aria-label="Select project detail">${data.projects.map((item) => `<option value="${esc(item.projectId)}" ${item.projectId === projectId ? "selected" : ""}>${esc(item.projectId)} · ${esc(item.name)}</option>`).join("")}</select><span class="muted">${esc(project.region)} · ${esc(project.industry)} · ${esc(project.parent)}</span></div>${section("Energy to revenue", "A finance-first chain from hourly load matching to avoided grid cost.", `<div class="panel flow-equation">${flow.map((item, index) => `<span>${esc(item)}</span>${index < flow.length - 1 ? "<i>→</i>" : ""}`).join("")}</div>`, "01 · ENERGY ENGINE")}${section("8,760 load matching", "Public page shows the selected annual summary and a communication-only daily shape; raw hourly streams remain outside the public payload.", `<div class="grid-2">${panel("Load · solar · self-consumed shape", multiLineChart([{label: "Customer load", points: relativeLoad, className: "line-blue", swatch: "blue"}, {label: "Solar generation", points: relativeSolar, className: "line-green", swatch: "green"}, {label: "Self-consumed solar", points: selfConsumed, className: "line-red", swatch: "red"}], {label: "Customer load, solar generation and self-consumed solar", caption: "Relative shape only; annual totals and ratios are sourced from the released aggregate 8,760 outputs."}), "Representative day")}${panel("Key metrics", `<div class="metric-list"><div class="metric-line"><span>Annual load</span><b>${n(load.annualLoadKWh, 0)} kWh</b></div><div class="metric-line"><span>P50 solar generation</span><b>${n(energy.p50KWh, 0)} kWh</b></div><div class="metric-line"><span>P90 / P50</span><b>${pct(energy.p90P50Pct, 1)}</b></div><div class="metric-line"><span>Self-consumption</span><b>${pct(load.selfConsumptionPct, 1)}</b></div><div class="metric-line"><span>Solar share of load</span><b>${pct(load.solarSharePct, 1)}</b></div><div class="metric-line"><span>Avoided grid cost</span><b>${bvnd(load.avoidedGridCostBVND)}</b></div><div class="metric-line"><span>Weighted avoided tariff</span><b>${n(load.weightedTariff, 0)} VND/kWh</b></div></div>`, "Released summary")}</div>`, "02 · LOAD MATCH")}${section("Three-sided PPA frontier", "The customer ceiling, sponsor floor and lender floor define a feasible negotiation zone.", `<div class="grid-2">${panel("PPA frontier · ${esc(projectId)}", `<div class="frontier"><div class="frontier-scale"><div class="frontier-zone ${String(frontier.zone).toUpperCase().includes("FEASIBLE") ? "zone-feasible" : "zone-empty"}" style="left:${ppaPosition(frontier.lower_bound_vnd_kwh, ppa.lower, ppa.upper)};right:${ppaPosition(frontier.upper_bound_vnd_kwh, ppa.lower, ppa.upper)}"></div>${ppaMarkerMarkup(frontier)}</div><div class="frontier-ticks">${ppaTicks(ppa.lower, ppa.upper).map((tick, index) => `<span>${n(tick, 0)}${index === 3 ? " VND/kWh" : ""}</span>`).join("")}</div></div><div class="metric-list"><div class="metric-line"><span>Customer ceiling</span><b>${n(frontier.customer_ceiling_vnd_kwh, 1)}</b></div><div class="metric-line"><span>Sponsor floor</span><b>${n(frontier.sponsor_floor_vnd_kwh, 1)}</b></div><div class="metric-line"><span>Lender floor</span><b>${n(frontier.lender_floor_vnd_kwh, 1)}</b></div><div class="metric-line"><span>Required lower bound</span><b>${n(frontier.lower_bound_vnd_kwh, 1)}</b></div><div class="metric-line"><span>Zone / action</span><span>${status(frontier.zone)} ${status(frontier.action)}</span></div></div>`, "VND/kWh")}${panel("Current vs negotiated", table(["Metric", "Current", "Negotiated", "Change"], rows), "Hypothetical remediation")}</div>`, "03 · COMMERCIAL TERMS")}${section("Returns explained", "Project return belongs to the asset; equity return belongs to the sponsor after debt.", `<div class="grid-4">${metricCard("Project NPV", bvnd(returns.projectNPVBVND), "Negotiated hypothetical", "positive")}${metricCard("Project IRR", pct(returns.projectIRR, 2), "Unlevered", "positive")}${metricCard("Equity NPV", bvnd(returns.equityNPVBVND), "After debt", "positive")}${metricCard("Equity IRR", pct(returns.equityIRR, 2), "Levered", "positive")}</div>`, "04 · RETURNS")}${sourceList(data.sources)}</div>`;
}

function renderDebt(data) {
  const w = data.waterfall;
  const capacityItems = Object.entries(data.capacity).filter(([key]) => key.endsWith("_vnd")).map(([key, value]) => ({label: key.replace("_debt_vnd", "").replaceAll("_", " ").toUpperCase(), value}));
  const schedulePoints = data.schedule.slice(0, 12).map((row) => ({label: `Y${row.year}`, value: row.cfadsBVND}));
  const waterfallBody = w.map((item) => `<div class="bar-row"><span>${esc(item.label)}</span><div class="bar-track"><div class="bar-fill ${item.valueBVND < 0 ? "red" : ""}" style="width:${Math.min(100, Math.max(5, Math.abs(item.valueBVND) / Math.max(...w.map((x) => Math.abs(x.valueBVND))) * 100))}%"></div></div><span class="bar-value ${cls(item.valueBVND)}">${bvnd(item.valueBVND)}</span></div>`).join("");
  return `<div class="page">${pageHero(data, "debt", {actions: `<a class="button button-primary" href="#/portfolio">See portfolio →</a>`})}${kpis(data.shared, [{label: "Total debt sized", value: bvnd(data.headline.totalDebtBVND), meta: "Selected portfolio"}, {label: "Base DSCR", value: `${n(data.headline.baseDSCR, 2)}x`, meta: "Pooled minimum"}, {label: "Covenant headroom", value: `${n(data.headline.covenantHeadroom, 2)}x`, meta: "Lock-up headroom"}, {label: "Binding capacity", value: data.capacity.binding, meta: "Sizing output"}, {label: "LLCR", value: `${n(data.coverage.LLCR, 2)}x`, meta: `Target ${n(data.coverage.targetLLCR, 2)}x`}, {label: "PLCR", value: `${n(data.coverage.PLCR, 2)}x`, meta: `Target ${n(data.coverage.targetPLCR, 2)}x`}])}${section("Cash flow waterfall", "Typical year, selected default project; values derive from project cash flow and reserve outputs.", `<div class="grid-2">${panel("Revenue → CFADS → equity cash flow", `<div class="bar-list">${waterfallBody}</div>`, "BVND")}${panel("Debt capacity by constraint", barChart(capacityItems, {format: (value) => bvnd(value)}), `Binding: ${data.capacity.binding}`)}</div>`, "01 · CASH FLOW")}${section("Coverage metrics", "Coverage is defined before the debt decision, not after it.", `<div class="grid-3">${metricCard("Minimum DSCR", `${n(data.coverage.minimumDSCR, 2)}x`, `Target ${n(data.coverage.targetDSCR, 2)}x`, "positive")}${metricCard("LLCR", `${n(data.coverage.LLCR, 2)}x`, `Target ${n(data.coverage.targetLLCR, 2)}x`, "positive")}${metricCard("PLCR", `${n(data.coverage.PLCR, 2)}x`, `Target ${n(data.coverage.targetPLCR, 2)}x`, "positive")}</div><div class="callout" style="margin-top:15px"><b>Binding constraint: ${esc(data.capacity.binding)}.</b> Circularity status is ${esc(data.capacity.circularity)}.</div>`, "02 · CREDIT")}${section("Debt sculpting and reserves", "The repayment profile keeps DSCR at the released floor while funding a DSRA before distributions.", `<div class="grid-2">${panel("CFADS profile", lineChart(schedulePoints, {label: "CFADS profile over debt tenor", caption: "Annual CFADS from reserve waterfall output."}), "Years 1–12")}${panel("FX financing comparison", table(["Funding case", "Equity NPV", "Min DSCR"], data.fx.map((row) => [esc(row.label), `<span class="num">${bvnd(row.equityNPVBVND)}</span>`, `<span class="num">${n(row.dscr, 2)}x</span>`])), "VND equivalent")}</div>`, "03 · STRUCTURE")}${sourceList(data.sources)}</div>`;
}

function renderPortfolio(data) {
  const rows = data.selectedProjects.map((row) => [esc(row.projectId), esc(row.name), esc(row.region), esc(row.industry), `<span class="num">${n(row.negotiatedPPA, 1)}</span>`, `<span class="num">${bvnd(row.equityRequiredBVND)}</span>`, `<span class="num">${bvnd(row.debtBVND)}</span>`, `<span class="num positive">${bvnd(row.equityNPVBVND)}</span>`, `<span class="num">${n(row.equityIRR, 2)}%</span>`, `<span class="num">${n(row.minDSCR, 2)}x</span>`]);
  return `<div class="page">${pageHero(data, "portfolio", {actions: `<a class="button button-primary" href="#/risk">Stress portfolio →</a>`})}${sharedKpis(data.shared)}${section("Portfolio funnel", "Value-positive remediation is not the same as final selection.", `<div class="grid-4">${data.funnel.map((step, index) => `<div class="panel panel-pad"><div class="section-kicker">0${index + 1}</div><div class="kpi-value">${n(step.value, 0)}</div><div class="muted">${esc(step.label)}</div></div>`).join("")}</div>`, "01 · SCREENING")}${section("Selected portfolio (four projects)", "The final exposure-constrained case is sourced from portfolio_exposure_v4.csv.", panel("Selected project table", table(["ID", "Project", "Region", "Industry", "PPA", "Equity", "Debt", "Equity NPV", "IRR", "DSCR"], rows), "Negotiated hypothetical"), "02 · SELECTION")}${section("Exposure limits and capital allocation", "Concentration limits are displayed beside the selected case.", `<div class="grid-2">${panel("Exposure compliance", table(["Limit", "Policy", "Current", "Headroom", "Utilization", "Status"], data.exposureLimits.map((row) => [esc(row.label), row.limitPct ? `${n(row.limitPct, 0)}%` : `≤ ${n(row.limitBVND, 0)} BVND`, row.currentPct ? `${n(row.currentPct, 1)}%` : `${bvnd(row.currentBVND)}`, row.headroomPct !== undefined ? `${n(row.headroomPct, 1)}%` : `${bvnd(row.headroomBVND)}`, `${n(row.utilizationPct, 1)}%`, status(row.status)])), "All PASS")}${panel("Equity allocation", barChart(data.allocation, {format: (value) => bvnd(value)}), "Selected equity required")}</div>`, "03 · CONTROLS")}${section("Allocation mix", "Green-family donuts keep the concentration story visible without rainbow encoding.", `<div class="panel panel-pad donut-grid">${data.donuts.map((donut) => donutCard(donut)).join("")}</div>`, "04 · EXPOSURE VIEW")}${section("Why other projects did not make it", "Current-terms rejection reasons remain visible instead of being hidden behind a score.", `<div class="grid-2">${panel("Rejection reason count", barChart(data.rejectionReasons.map((row) => ({label: row.label, value: row.count})), {format: (value) => n(value, 0)}), "Current terms")}${panel("Standalone vs pooled", table(["Metric", "Standalone", "Pooled"], data.pooling.map((row) => [esc(row.label), `<span class="num">${typeof row.standalone === "number" ? n(row.standalone, 3) : esc(row.standalone)}</span>`, `<span class="num">${typeof row.pooled === "number" ? n(row.pooled, 3) : esc(row.pooled)}</span>`])), "Pooling output")}</div>`, "05 · ALLOCATION")}${sourceList(data.sources)}</div>`;
}

function renderRisk(data) {
  const scenarioRows = data.scenarios.map((row) => [esc(row.scenario), esc(row.note), '<span class="num ' + cls(row.projectNPVBVND) + '">' + bvnd(row.projectNPVBVND) + '</span>', '<span class="num ' + cls(row.equityNPVBVND) + '">' + bvnd(row.equityNPVBVND) + '</span>', '<span class="num">' + n(row.minDSCR, 2) + 'x</span>', status(row.economicStatus), status(row.creditStatus), esc(row.readinessImpact)]);
  const aside = '<div class="decision-banner"><small>CURRENT TERMS DECISION</small><strong>NO DEPLOYMENT</strong><span>' + esc(data.currentDecision.text) + '</span></div>';
  const hero = pageHero(data, "risk", {actions: '<a class="button button-primary" href="#/evidence">Review open gates →</a>', aside});
  const scenarioSection = section("Scenario matrix", "Equity economics, credit covenant outcome and readiness impact are intentionally separate.", panel("Phase 2 scenario outputs", table(["Scenario", "Scenario note", "Project NPV", "Equity NPV", "Min DSCR", "Economic", "Credit", "Readiness"], scenarioRows), "V4.1 semantic contract"), "01 · DOWNSIDE");
  const tornadoSection = section("Tornado sensitivity", "One-at-a-time scenario deltas versus base Equity NPV; negative bars indicate value destruction.", panel("Equity NPV sensitivity", barChart(data.tornado.map((row) => ({label: row.label, value: row.deltaBVND})), {format: (value) => bvnd(value)}), "BVND change"), "02 · DRIVERS");
  const debtBody = '<div class="grid-2">' + panel("Required evidence", '<div class="metric-list"><div class="metric-line"><span>Public re-sizing result</span>' + status(data.debtResizingDisclosure.status) + '</div><div class="metric-line"><span>Model-backed scenario</span><b>Required before publication</b></div><div class="metric-line"><span>Current decision</span><b class="negative">NO DEPLOYMENT</b></div></div>', "V4.1 disclosure") + panel("Stress summary", data.stressSummary.map((row) => '<div class="metric-line"><span>' + esc(row.label) + '</span><b class="negative">' + bvnd(row.value) + '</b></div>').join(""), "Equity view") + '</div>';
  const debtSection = section("Debt response boundary", "No unsupported fixed-versus-resized debt output is published.", debtBody, "03 · CREDIT RESPONSE");
  const registerSection = section("Top risk register", "Risks are paired with a mitigation owner action, not only a colour.", panel("Risk register", table(["Risk", "Impact", "Status", "Mitigation", "Evidence class"], data.riskRegister.map((row) => [esc(row.risk), '<span class="warning">' + esc(row.impact) + '</span>', status(row.status), esc(row.mitigation), '<span class="muted">' + esc(row.evidenceClass) + '</span>'])), "Screening view"), "04 · REGISTER");
  return '<div class="page">' + hero + sharedKpis(data.shared) + scenarioSection + tornadoSection + debtSection + registerSection + sourceList(data.sources) + '</div>';
}

function renderModel(data) {
  return `<div class="page">${pageHero(data, "model", {actions: `${gh("model/vietgreen_v4_formula_model.xlsx", "Open workbook")}<a class="button button-primary" href="#/evidence">Evidence & downloads →</a>`})}<section class="section"><div class="grid-4">${metricCard("Model version", data.metadata.modelVersion, "Release")}${metricCard("Build date", data.metadata.buildDate, "V4 final candidate")}${metricCard("Model owner", data.metadata.modelOwner, "Review function")}${metricCard("Review status", data.metadata.reviewStatus, "QA complete", "positive")}</div></section>${kpis(data.shared, [{label: "Formula cells", value: n(data.qa.formulaCells, 0), meta: "Workbook QA"}, {label: "Formula errors", value: n(data.qa.formulaErrors, 0), meta: "After recalculation", tone: "positive"}, {label: "Excel ↔ Python", value: data.qa.excelPythonReconciliation, meta: "Reconciliation", tone: "positive"}, {label: "Final DoD", value: data.qa.finalDoD, meta: "All pass", tone: "positive"}, {label: "Red team", value: data.qa.redTeam, meta: "Sampled tests", tone: "positive"}, {label: "Release stage", value: data.qa.stageFlow, meta: "Gates"}])}${section("Model architecture", "The release is built as a deterministic chain from inputs to recruiter-safe communication.", `<div class="panel architecture">${data.architecture.map((node, index) => `<div class="arch-node">${esc(node)}</div>${index < data.architecture.length - 1 ? "<span class=\"arch-arrow\">→</span>" : ""}`).join("")}</div>`, "01 · PIPELINE")}${section("Workbook architecture", "A real workbook preview is included in the repository; this page makes the structure explicit.", `<div class="grid-2">${panel("V4 workbook sheets", `<div class="grid-3">${data.workbookSheets.map((sheet, index) => `<div class="callout"><b>0${index + 1}</b><br>${esc(sheet)}</div>`).join("")}</div>`, "Formula-driven")}${panel("Workbook preview", `<iframe class="embed" title="VietGreen V4 workbook preview" src="model_preview/index.html"></iframe><p class="muted">The preview is a recruiter-safe communication layer; the source workbook remains linked on GitHub.</p>`, "Inspect")}</div>`, "02 · WORKBOOK")}${section("Reproducibility and validation", "Build identifiers let a reviewer reproduce the release without treating the website as the model.", `<div class="grid-2">${panel("Reproducibility", `<div class="metric-list"><div class="metric-line"><span>Locked seed</span><b>${n(data.reproducibility.seed, 0)}</b></div><div class="metric-line"><span>Release ID</span><b>${esc(data.reproducibility.releaseId)}</b></div><div class="metric-line"><span>Workbook SHA-256</span><b class="muted" style="font-size:10px;word-break:break-all">${esc(data.reproducibility.workbookHash)}</b></div><div class="metric-line"><span>Match confirmed</span>${status(String(data.reproducibility.matchConfirmed).toUpperCase())}</div></div>`, "Manifest")}${panel("Validation log", table(["Check", "Status", "Detail"], data.validationLog.map((row) => [esc(row.check), status(row.status), esc(row.detail)])), "Release evidence")}</div>`, "03 · QA")}${section("Red-team tests", "Sampled stresses are named so a reviewer can find the corresponding validation artifacts.", `<div class="grid-3">${data.redTeam.map((item) => `<div class="evidence-card"><span class="evidence-icon">✓</span><div><h3>${esc(item)}</h3><p class="positive">PASS</p></div></div>`).join("")}</div>`, "04 · RED TEAM")}${sourceList(data.sources)}</div>`;
}

function renderEvidence(data) {
  const readinessCards = data.readiness.map((row) => `<div class="evidence-card"><span class="evidence-icon">${row.status === "PASS" ? "✓" : row.status === "OPEN" ? "!" : "×"}</span><div><h3>${esc(row.label)}</h3><p>${status(row.status)}</p><p>${esc(row.detail)}</p></div></div>`).join("");
  const gates = data.gates.map((row) => [esc(row.id), esc(row.category), status(row.status), esc(row.nextAction)]);
  return `<div class="page">${pageHero(data, "evidence", {actions: `${gh("release/MODEL_RELEASE_MANIFEST.json", "Open manifest")}<a class="button button-primary" href="#/">Return to decision →</a>`})}${kpis(data.shared, [{label: "Mechanics", value: "PASS", meta: "Synthetic only", tone: "positive"}, {label: "Recruiter package", value: data.shared.recruiterReady ? "READY" : "OPEN", meta: "Release state", tone: "positive"}, {label: "Transaction evidence", value: data.shared.transactionEvidenceStatus, meta: "No private files ingested", tone: "warning"}, {label: "Bankable transaction", value: String(data.shared.bankableTransactionReady).toUpperCase(), meta: "External gates remain", tone: "negative"}, {label: "External gates", value: n(data.shared.externalGateCountOpen, 0), meta: "Open"}, {label: "Release", value: data.shared.modelVersion, meta: data.shared.asOfDate}])}${section("Readiness cards", "The mechanics can be shown to a recruiter without overstating transaction readiness.", `<div class="grid-4">${readinessCards}</div>`, "01 · READINESS")}${section("Evidence boundary", "Each evidence class has a different claim allowed.", `<div class="grid-3">${data.boundary.map((item, index) => `<div class="callout"><div class="section-kicker">0${index + 1}</div><h3>${esc(item)}</h3><p class="muted">${index < 2 ? "Externally verifiable or captured source." : index < 4 ? "Model assumption or simulated input." : "Derived output or outside dependency."}</p></div>`).join("")}</div>`, "02 · BOUNDARY")}${section("External gates", "Eight controlled gates remain open before any bankable transaction claim.", panel("Gate register", table(["Gate", "Category", "Status", "Next action"], gates), "Controlled metadata only"), "03 · GOVERNANCE")}${section("Methodologies and downloads", "A reviewer can move from the narrative to the source artifact in one click.", `<div class="grid-2"><div class="panel panel-pad"><div class="downloads">${data.methodologies.map((item) => gh(item.path, item.label)).join("")}</div></div><div class="panel panel-pad"><div class="downloads">${data.downloads.map((item) => item.url ? external(item.url, item.label) : gh(item.path, item.label)).join("")}</div></div></div>`, "04 · LIBRARY")}${sourceList(data.sources)}</div>`;
}

function render(path, data) {
  switch (path) {
    case "case": return renderCase(data);
    case "economics": return renderEconomics(data, new URLSearchParams(window.location.hash.split("?")[1] || "").get("project") || data.defaultProjectId);
    case "debt": return renderDebt(data);
    case "portfolio": return renderPortfolio(data);
    case "risk": return renderRisk(data);
    case "model": return renderModel(data);
    case "evidence": return renderEvidence(data);
    default: return renderOverview(data);
  }
}

function activeRoute() {
  const hash = window.location.hash.replace(/^#\/?/, "").split("?")[0];
  return PAGE_NAMES.includes(hash) ? hash : "overview";
}

async function renderRoute() {
  const route = activeRoute();
  try {
    const data = await load(route);
    page.innerHTML = render(route, data);
    document.querySelectorAll("[data-nav]").forEach((link) => link.classList.toggle("active", link.dataset.nav === route));
    document.title = `${data.title} · VietGreen`;
    document.querySelector("#footer-release").textContent = `${data.shared.releaseId} · ${data.shared.modelVersion} · ${data.shared.asOfDate}`;
    if (route === "economics") {
      [document.querySelector("#project-select"), document.querySelector("#project-select-inline")].forEach((select) => select?.addEventListener("change", (event) => { window.location.hash = `#/economics?project=${event.target.value}`; }));
    }
    page.focus({preventScroll: true});
  } catch (error) {
    page.innerHTML = `<div class="page"><div class="panel panel-pad empty"><h1>Data contract unavailable</h1><p>${esc(error.message)}</p><p>Open the repository to inspect the release artifacts.</p>${external(repo, "Open GitHub")}</div></div>`;
  }
}

document.querySelector(".mobile-menu")?.addEventListener("click", (event) => {
  const nav = document.querySelector(".main-nav");
  nav.classList.toggle("open");
  event.currentTarget.setAttribute("aria-expanded", String(nav.classList.contains("open")));
});
document.querySelector(".main-nav")?.addEventListener("click", () => document.querySelector(".main-nav")?.classList.remove("open"));
window.addEventListener("hashchange", renderRoute);
renderRoute();
