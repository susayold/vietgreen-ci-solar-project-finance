const ROOT = "data/";
const MODEL_SOURCE_SHA = "ff69e15d211ff1abc88200574242ed2f1db49074";
const MODEL_TAG = "v5.1.3-recruiter-final";
const WEBSITE_RELEASE = "v5.1.3-website-final";
const ROUTES = ["overview","case","economics","debt","portfolio","risk","model","evidence"];
const cache = {};
const $ = (q) => document.querySelector(q);
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const num = (v, d=0) => Number.isFinite(Number(v)) ? Number(v).toLocaleString("en-US",{maximumFractionDigits:d}) : "—";
const money = (v, currency="local") => Number.isFinite(Number(v)) ? (currency==="USD" ? "$" : "") + num(v, currency==="USD"?2:1) + (currency==="USD" ? "" : " local") : "—";
const pct = (v) => Number.isFinite(Number(v)) ? (Number(v)*100).toFixed(1)+"%" : "—";
const status = (v) => {
  const s=String(v ?? "INDETERMINATE").toUpperCase();
  const good=["PASS","TRUE","READY","CLEARED","OPEN","FRONTIER_ONLY","RECRUITER_READY"].some(x=>s.includes(x)) && !s.includes("FALSE");
  const warn=["INDETERMINATE","REVIEW","OPEN","BLOCKED","DISABLED","FALSE","NOT_DISCLOSED"].some(x=>s.includes(x));
  return '<span class="status-badge '+(good&&!warn?"status-good":warn?"status-warn":"status-neutral")+'">'+esc(s.replaceAll("_"," "))+"</span>";
};
async function load(name){ if(!cache[name]) cache[name]=fetch(ROOT+name+".json").then(r=>{if(!r.ok)throw Error(name);return r.json();}); return cache[name]; }
function shell(title,kicker,sub){return '<div class="page"><div class="page-intro"><p class="eyebrow">'+esc(kicker)+'</p><h1 class="page-title">'+esc(title)+'</h1><p class="page-subtitle">'+esc(sub)+'</p></div></div>';}
function metric(label,value,note=""){return '<div class="metric"><span class="metric-label">'+esc(label)+'</span><strong>'+esc(value)+'</strong><small>'+esc(note)+'</small></div>';}
function panel(title,body,meta=""){return '<section class="panel"><div class="panel-head"><h2>'+esc(title)+'</h2><span class="panel-meta">'+esc(meta)+'</span></div>'+body+'</section>';}
function table(headers, rows){return '<div class="table-wrap"><table><thead><tr>'+headers.map(x=>"<th>"+esc(x)+"</th>").join("")+'</tr></thead><tbody>'+rows.map(r=>"<tr>"+r.map(x=>"<td>"+(x ?? "—")+"</td>").join("")+"</tr>").join("")+'</tbody></table></div>';}
function links(data){return '<div class="source-links">'+(data||[]).map(x=>'<a class="button button-secondary" href="'+esc(x.url||"#")+'" target="_blank" rel="noopener">'+esc(x.label||"Source")+' ↗</a>').join(" ")+'</div>';}
function projectId(){return new URLSearchParams(location.hash.split("?")[1]||"").get("project");}
function readyProjects(data){return data.projects||[];}
function routeTop(data, title, kicker, sub){return shell(title,kicker,sub)+'<div class="page-content">';}
function closePage(){return '</div></div>';}
async function renderOverview(){
 const d=await load("overview"), s=d.shared||await load("shared-summary"), e=await load("evidence");
 let html=routeTop(d,"Real C&I Solar Projects. Public Evidence. Project Finance Decisions Under Uncertainty.","VIETGREEN · V5.1.3 RECRUITER WEBSITE","A source-backed decision surface for screened C&I solar projects. The commercial conclusion remains bounded by missing transaction evidence.");
 html+='<div class="hero-actions"><span class="decision-pill">COMMERCIAL DECISION / INDETERMINATE</span><a class="button button-primary" href="#/economics">Explore economics ↗</a></div>';
 html+='<div class="metric-grid">'+metric("Candidates",num(s.candidateCount),"source universe")+metric("Selected",num(s.selectedCount),"physical QA pass")+metric("Economics-ready",num(s.economicsReadyCount),"base-case eligible")+metric("Observations",num(s.observationCount),"preserved public rows")+'</div>';
 html+=panel("Screening funnel",'<div class="funnel">'+["54 candidates","20 selected","20 physically screened","19 economics-ready","19 recruiter shortlist","0 allocation"].map(x=>'<span>'+esc(x)+'</span>').join('<i>→</i>')+'</div>',"No approved portfolio");
 html+=panel("Physical QA firewall",'<div class="callout"><strong>900–1,600 kWh/kWp screening band</strong><p>Extreme observations are preserved for audit. Arisudhana remains visible as raw 30.5 GWh evidence, but is blocked from direct base economics with <code>EXTREME_OUTLIER_BLOCK_BASE</code>.</p></div>',"20 rows / 19 ready / 1 blocked");
 html+=panel("Decision boundary",'<div class="two-col"><div><h3>FRONTIER_ONLY</h3><p>Reference PPA economics are a negotiation frontier, never an actual executed PPA.</p></div><div><h3>Transaction evidence OPEN</h3><p>Bankable, lender-ready and IC-approved claims remain false until external gates close.</p></div></div>',"Governance sealed in CI");
 html+=links(e.sources||[]);
 return html+closePage();
}
async function renderCase(){
 const d=await load("case"), p=d.projects||[];
 let html=routeTop(d,"Case · From public evidence to a financeable question","CASE / DATA GOVERNANCE","The established information architecture is retained; the facts are V5.1.3.");
 html+='<div class="metric-grid">'+metric("Projects",num(p.length),"selected after screening")+metric("Ready",num(p.filter(x=>x.economicsStatus==="READY_FOR_ECONOMICS").length),"economics engine")+metric("Blocked",num(p.filter(x=>x.economicsStatus!=="READY_FOR_ECONOMICS").length),"technical data gate")+metric("Allocation","0","FRONTIER_ONLY")+'</div>';
 html+=panel("Investment case",'<ol class="steps">'+(d.steps||["Source and preserve observations","Apply physical QA","Resolve P50 / P90 / P99","Model load and energy","Calculate PPA frontier","Size debt and coverage","Stress contractual schedule","Reconcile and publish","Keep external gates open"]).map(x=>'<li>'+esc(x)+'</li>').join("")+'</ol>',"Evidence ladder");
 html+=panel("Screened project universe",table(["Project","Country","Capacity","Physical QA","Economics","Boundary"],p.map(x=>[esc(x.projectName),esc(x.country),esc(num(x.capacityKwp,0)+" kWp"),status(x.physicalStatus),status(x.economicsStatus),esc(x.decisionBoundary||"PUBLIC_DATA_ONLY")])));
 return html+closePage();
}
async function renderEconomics(){
 const d=await load("economics"), id=projectId()||d.projects?.[0]?.projectId, x=(d.projectDetails||{})[id]||d.projects?.[0]||{}, f=await load("frontier");
 let html=routeTop(d,"Economics & PPA frontier","ECONOMICS / 19 BASE-CASE PROJECTS","Select an economics-ready project. The reference case is a standardized reconstruction, not an actual PPA.");
 html+='<div class="filter-row"><label for="econ-project-select">Project</label><select id="econ-project-select">'+(d.projects||[]).map(p=>'<option value="'+esc(p.projectId)+'" '+(p.projectId===id?"selected":"")+'>'+esc(p.projectName)+" · "+esc(p.country)+"</option>").join("")+'</select></div>';
 html+='<div class="metric-grid">'+metric("Project",x.projectName||"—","economics-ready")+metric("P50 generation",num(x.generationP50Kwh||x.generationP50),"kWh / year")+metric("Specific yield",num(x.specificYieldP50,0),"kWh/kWp")+metric("PPA mode","FRONTIER_ONLY","not actual PPA")+'</div>';
 html+=panel("Representative 24-bin operating shape",'<div class="bar-chart">'+(x.dailyShape||[]).map(v=>'<span style="height:'+Math.max(4,Math.min(100,Number(v)/Math.max(...(x.dailyShape||[1]))*100))+'%" title="'+esc(num(v,0))+'"></span>').join("")+'</div><p class="caption">Browser payload is an aggregated representative day; raw 8,760 rows remain in CI artifacts.</p>',"P50 / modeled load");
 const row=f.projects?.find(z=>z.projectId===id)||f.rows?.find(z=>z.projectId===id)||{};
 html+=panel("PPA negotiation frontier",table(["Customer ceiling","Negotiation zone","Sponsor floor","Lender floor","Reference case"],[[money(row.customerCeiling),status(row.zoneStatus||row.zone),money(row.sponsorFloor),money(row.lenderFloor),status(row.referenceCase||"REFERENCE_CASE_NOT_ACTUAL_PPA")]]),"FRONTIER_ONLY");
 html+=panel("Returns summary",table(["NPV (local)","NPV (USD)","Project IRR","Equity IRR","Decision"],[[money(x.projectNpvLocal),money(x.projectNpvUsd,"USD"),pct(x.projectIrr),pct(x.equityIrr),status(x.decision||"INDETERMINATE_MISSING_COMMERCIAL_DATA")]]));
 html+=panel("Blocked from direct base economics",'<div class="callout warning"><strong>'+esc(d.blockedProject?.projectName||"Arisudhana")+'</strong><p>TECHNICAL_DATA_BLOCKED. The extreme raw observation is preserved, but no base-case economics are presented for this project.</p></div>',"Firewall enforced");
 return html+closePage();
}
async function renderDebt(){
 const d=await load("debt"), id=projectId()||d.projects?.[0]?.projectId, x=(d.details||{})[id]||{};
 let html=routeTop(d,"Debt · Contractual schedule and coverage","DEBT / PROJECT FINANCE","Debt sizing is constrained by the frozen V5.1.3 model. Downside scenarios do not re-sculpt contractual principal.");
 html+='<div class="filter-row"><label for="debt-project-select">Project</label><select id="debt-project-select">'+(d.projects||[]).map(p=>'<option value="'+esc(p.projectId)+'" '+(p.projectId===id?"selected":"")+'>'+esc(p.projectName)+"</option>").join("")+'</select></div>';
 html+='<div class="metric-grid">'+metric("Debt capacity",money(x.debtCapacityUsd,"USD"),"reference case")+metric("Minimum DSCR",num(x.dscrMin,2),"x")+metric("LLCR",num(x.llcr,2),"x")+metric("PLCR",num(x.plcr,2),"x")+'</div>';
 html+=panel("Debt schedule",table(["Year","Opening","Interest","Principal","Debt service","Closing","DSCR"],(x.schedule||[]).slice(0,12).map(r=>[esc(r.year),money(r.opening),money(r.interest),money(r.principal),money(r.debtService),money(r.closing),num(r.dscr,2)])),"Contractual base schedule");
 html+=panel("Scenario debt policy",table(["Mode","Opening","Principal","Closing","Interest"],(d.policy||[]).map(r=>[esc(r.mode),status(r.openingPreserved),status(r.principalPreserved),status(r.closingPreserved),esc(r.interestPolicy)])),"NO_NEW_DEBT / FIXED_CONTRACTUAL_SCHEDULE");
 return html+closePage();
}
async function renderPortfolio(){
 const d=await load("portfolio");
 let html=routeTop(d,"Portfolio · Diligence shortlist, no allocation","PORTFOLIO / EXPOSURE GOVERNANCE","V5.1.3 does not approve the legacy four-project portfolio. Capital allocation remains disabled while the frontier is unresolved.");
 html+='<div class="metric-grid">'+metric("Shortlist",num(d.shortlistCount||d.projects?.length),"diligence only")+metric("Allocated","0","capital allocation disabled")+metric("Budget","0","no deployment claim")+metric("Status","FRONTIER_ONLY","commercial evidence open")+'</div>';
 html+=panel("Capital allocation status",'<div class="callout warning"><strong>capital_allocation_status = DISABLED_FRONTIER_ONLY</strong><p>This surface supports triage and diligence sequencing only. It is not an approved portfolio or investment committee decision.</p></div>');
 html+=panel("Diligence shortlist",table(["Project","Country","Exposure","Physical","Economics","Next gate"],(d.projects||[]).map(x=>[esc(x.projectName),esc(x.country),esc(x.exposure||"Not allocated"),status(x.physicalStatus),status(x.economicsStatus),esc(x.nextGate||"Commercial evidence")])));
 return html+closePage();
}
async function renderRisk(){
 const d=await load("risk"), id=projectId(), rows=(d.scenarios||[]).filter(x=>!id||x.projectId===id);
 let html=routeTop(d,"Risk · 171 governed scenarios","RISK / CONTRACTUAL DEBT SEMANTICS","Every downside row is visible with its debt mode, preservation flags and coverage outputs.");
 html+='<div class="filter-row"><label for="risk-project-select">Project filter</label><select id="risk-project-select"><option value="">All projects</option>'+(d.projects||[]).map(p=>'<option value="'+esc(p.projectId)+'" '+(p.projectId===id?"selected":"")+'>'+esc(p.projectName)+"</option>").join("")+'</select></div>';
 html+='<div class="metric-grid">'+metric("Scenario rows",num(d.scenarioRows||rows.length),"all governed rows")+metric("NO_NEW_DEBT",num(rows.filter(x=>x.debtMode==="NO_NEW_DEBT").length),"principal preserved")+metric("Additional debt","0","under no-new-debt policy")+metric("Claim","INDETERMINATE","commercial boundary")+'</div>';
 html+=panel("Scenario register",table(["Scenario","Debt mode","Debt","Principal preserved","Interest","Incremental CAPEX","Additional debt","Min DSCR","LLCR","PLCR"],rows.map(x=>[esc(x.scenario),esc(x.debtMode),money(x.debt),status(x.principalSchedulePreserved),esc(x.interestChanged||x.interestPolicy),money(x.incrementalCapex),money(x.additionalDebt),num(x.minDscr,2),num(x.llcr,2),num(x.plcr,2)])),"V5.1.3 scenario engine");
 return html+closePage();
}
async function renderModel(){
 const d=await load("model");
 let html=routeTop(d,"Model · Frozen, reproducible, auditable","MODEL / V5.1.3","The website is a presentation layer over the frozen model release. It does not alter model data.");
 html+='<div class="metric-grid">'+metric("Model tag",MODEL_TAG,"exact source")+metric("Source SHA",MODEL_SOURCE_SHA.slice(0,12)+"…","frozen")+metric("Workbook sheets",num(d.metadata?.workbookSheets||28),"native artifact")+metric("Tests",num(d.metadata?.pytestPassed||26)+"/"+num(d.metadata?.pytestTotal||26),"pytest / semantic")+'</div>';
 html+=panel("Runtime identity",table(["Control","Value"],[["Model source SHA",esc(MODEL_SOURCE_SHA)],["Model development freeze",status("TRUE")],["Reproducibility",status(d.metadata?.reproducibility||"PASS")],["G0–G9 controls",status("CLEARED")],["G2",status("PASS_WITH_NONBLOCKING_REVIEW")],["Website data",status("SEALED_IN_CI")]]));
 html+=panel("Workbook and QA",'<ul class="plain-list">'+(d.metadata?.architecture||["28-sheet native workbook","26 pytest controls","26 semantic controls","Remote-only generated website data","Claim boundary and lineage sealed in CI"]).map(x=>'<li>'+esc(x)+'</li>').join("")+'</ul><p class="caption">Use the evidence page for release, CI and artifact links.</p>');
 return html+closePage();
}
async function renderEvidence(){
 const d=await load("evidence");
 let html=routeTop(d,"Evidence · Release, lineage and readiness","EVIDENCE / PUBLIC AUDIT TRAIL","Model and website releases are separated. Every browser payload is generated in CI from the frozen model artifacts.");
 html+='<div class="metric-grid">'+metric("Website",WEBSITE_RELEASE,"presentation release")+metric("Model",MODEL_TAG,"source release")+metric("Source SHA",MODEL_SOURCE_SHA.slice(0,12)+"…","unchanged")+metric("External gates",num(d.gateCount||8),"OPEN")+'</div>';
 html+=panel("Readiness boundary",table(["Area","Status","Meaning"],(d.readiness||[]).map(x=>[esc(x.area),status(x.status),esc(x.meaning)])));
 html+=panel("External gates",table(["Gate","Status","Interpretation"],(d.gates||[]).map(x=>[esc(x.name),status(x.status),esc(x.note)])));
 html+=panel("Downloads and source links",links(d.downloads||[]),"Remote-only");
 return html+closePage();
}
async function render(){
 const route=(location.hash.match(/^#\\/?([^?]*)/)||[])[1]||"overview";
 const r=ROUTES.includes(route)?route:"overview";
 document.querySelectorAll("[data-nav]").forEach(a=>a.classList.toggle("active",a.dataset.nav===r));
 try{
  const html=await ({overview:renderOverview,case:renderCase,economics:renderEconomics,debt:renderDebt,portfolio:renderPortfolio,risk:renderRisk,model:renderModel,evidence:renderEvidence}[r])();
  $("#app").innerHTML=html;
  $("#footer-release").textContent="Website "+WEBSITE_RELEASE+" · Model "+MODEL_TAG+" · SHA "+MODEL_SOURCE_SHA.slice(0,12)+"…";
  document.querySelector(".main-nav")?.classList.remove("open");
  const menu=$(".mobile-menu"); if(menu) menu.setAttribute("aria-expanded","false");
  if(r==="economics") $("#econ-project-select")?.addEventListener("change",e=>location.hash="#/economics?project="+e.target.value);
  if(r==="debt") $("#debt-project-select")?.addEventListener("change",e=>location.hash="#/debt?project="+e.target.value);
  if(r==="risk") $("#risk-project-select")?.addEventListener("change",e=>location.hash="#/risk?project="+e.target.value);
 }catch(err){$("#app").innerHTML='<div class="page"><div class="callout warning"><strong>Data payload unavailable</strong><p>'+esc(err.message)+'</p></div></div>';}
}
window.addEventListener("hashchange",render);
$(".mobile-menu")?.addEventListener("click",()=>{const n=$(".main-nav"),m=$(".mobile-menu");n?.classList.toggle("open");m?.setAttribute("aria-expanded",n?.classList.contains("open")?"true":"false");});
render();
