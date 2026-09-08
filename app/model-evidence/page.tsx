'use client';
import { useSyncExternalStore, useState } from 'react';
import SiteHeader from '@/lib/site-header';
import Image from '@/lib/site-image';
import Link from '@/lib/site-link';
import { ArrowRight, Database, FileCheck2, ShieldCheck, Code2 } from 'lucide-react';
import revision from '../../public/data/model-revision.json';
import audit from '../../public/data/source-audit.json';
import economics from '../../public/data/economics.json';
import debts from '../../public/data/debt.json';
import summary from '../../public/data/summary.json';

const REPO='https://github.com/susayold/vietgreen-ci-solar-project-finance';
const subscribeLocation=(notify:()=>void)=>{window.addEventListener('popstate',notify);return ()=>window.removeEventListener('popstate',notify);};
const readProject=()=>new URLSearchParams(window.location.search).get('project') || 'VN-GY-GOMALL';
const number=(v:number,d=3)=>v.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
const usd=(v:number)=>`$${number(v/1e6)}m`;
const evidenceClasses=[
  ['Observed facts','Source-reported capacity, generation, developer and project identity.'],
  ['Derived metrics','Specific yield, self-consumption, cash flow and coverage ratios.'],
  ['Benchmark assumptions','Tariff ceilings, CAPEX, OPEX, tax and financing assumptions.'],
  ['Analyst assumptions','Annual load proxy, hourly profile, degradation and return hurdles.'],
  ['Stress scenarios','Energy, cost, rates, timing and counterparty sensitivities.'],
  ['Missing evidence','Executed PPA, measured load, lender terms and independent site validation.'],
];
export default function ModelEvidencePage(){
  const queryId=useSyncExternalStore(subscribeLocation,readProject,()=> 'VN-GY-GOMALL');
  const [selectedId,setId]=useState<string|null>(null);
  const id=selectedId ?? queryId;
  const e=economics.rows.find(r=>r.projectId===id) ?? economics.rows[0];
  const d=debts.rows.find(r=>r.projectId===e.projectId)!;
  return <main className="model-page">
    <SiteHeader active="/model-evidence"/>
    <section className="model-hero">
      <Image src="/assets/projects/projects-hero.webp" alt="Industrial rooftop solar" fill priority sizes="100vw"/>
      <div className="model-hero-shade"/>
      <div className="model-hero-inner"><div className="model-hero-copy">
        <p className="model-eyebrow">MODEL &amp; EVIDENCE</p>
        <h1>Trace the Inputs.<br/>Review the Calculations.</h1>
        <p>Public project evidence, explicit assumptions and reproducible calculations connect all eight pages.</p>
      </div></div>
    </section>
    <div className="evidence-review-shell">
      <div className="evidence-review-kpis">
        <article><Database/><strong>{summary.economicsReadyProjects}</strong><span>Modeled projects</span></article>
        <article><Code2/><strong>{summary.scenarios}</strong><span>Scenario results</span></article>
        <article><FileCheck2/><strong>{Object.keys(revision.output_hashes).length}</strong><span>Versioned output artifacts</span></article>
        <article><ShieldCheck/><strong>{revision.checks.length}</strong><span>Automated checks passed</span></article>
      </div>
      <section className="evidence-review-panel"><h2>1. Analytical workflow</h2>
        <p>Public disclosures → Project registry → Physical QA → Energy &amp; load → Cash flow → Debt sizing → Stress testing → Diligence.</p>
        <p>Twenty selected records enter physical screening. Nineteen enter financial analysis; Arisudhana remains excluded pending validation of its reported generation.</p>
      </section>
      <section className="evidence-review-panel"><h2>2. Evidence and assumptions</h2>
        <div className="evidence-review-grid">{evidenceClasses.map(([title,text])=><article key={title}><h3>{title}</h3><p>{text}</p></article>)}</div>
      </section>
      <section className="evidence-review-panel"><h2>3. Trace a project result</h2>
        <label>Project <select value={id} onChange={event=>{setId(event.target.value);window.history.replaceState(null,'',`${window.location.pathname}?project=${encodeURIComponent(event.target.value)}`);}}>{economics.rows.map(r=><option key={r.projectId} value={r.projectId}>{r.projectName}</option>)}</select></label>
        <div className="evidence-review-table"><table><thead><tr><th>Output</th><th>Value</th><th>Calculation</th></tr></thead><tbody>
          <tr><td>CAPEX</td><td>{usd(e.capexUsd)}</td><td>Project cost assumption, converted to USD.</td></tr>
          <tr><td>Year 1 CFADS</td><td>{number(e.year1.cfads/1e9)} VND bn</td><td>Revenue − operating costs − cash tax.</td></tr>
          <tr><td>Debt capacity</td><td>{usd(d.debtCapacityUsd)}</td><td>Minimum of DSCR, LLCR, PLCR and leverage limits.</td></tr>
          <tr><td>Binding constraint</td><td>{d.bindingConstraint}</td><td>Constraint that sets the maximum supportable debt.</td></tr>
          <tr><td>Project NPV</td><td>{usd(e.projectNpvUsd)}</td><td>Discounted unlevered after-tax project cash flows.</td></tr>
          <tr><td>Equity NPV</td><td>{usd(e.equityNpvUsd)}</td><td>Equity contribution and cash flows after debt service.</td></tr>
        </tbody></table></div>
        <Link href={`/economics?project=${e.projectId}`}>Review assumptions and returns <ArrowRight size={16}/></Link>
      </section>
      <section className="evidence-review-panel"><h2>4. Calculation checks</h2>
        <p>The current calculation is repeated and compared before publication. Checks include percentage units, annual generation decay, debt balances, maturity repayment, coverage constraints and preservation of contractual principal under stress.</p>
        <details><summary>View all {revision.checks.length} checks</summary><ul>{revision.checks.map(c=><li key={c.check}>{c.check} — {c.status}</li>)}</ul></details>
        <p>These are automated model checks, not an independent financial, engineering or legal audit.</p>
      </section>
      <section className="evidence-review-panel"><h2>5. Scope and limitations</h2>
        <ul>{audit.limitations.map(item=><li key={item}>{item}</li>)}</ul>
        <p>P90 and P99 are screening factors, not probabilistic production guarantees. Annual load and hourly profiles are modeled proxies, not customer telemetry. The 25-year reference tariff projection is an analytical assumption, not a contracted post-PPA price.</p>
        <p>Financial outputs support comparison and diligence. Commercial acceptance, investment approval and lender commitment remain outside this project.</p>
      </section>
      <section className="evidence-review-panel"><h2>6. Source files and reproducibility</h2>
        <div className="evidence-review-links">
          <a href={`${REPO}/tree/main/model/recruiter_revision`} target="_blank" rel="noreferrer">Inputs and calculation code <ArrowRight size={16}/></a>
          <a href={`${REPO}/blob/main/scripts/build_corrected_model.py`} target="_blank" rel="noreferrer">Recalculation and validation <ArrowRight size={16}/></a>
          <a href={`${REPO}/tree/main/public/data`} target="_blank" rel="noreferrer">Website output artifacts <ArrowRight size={16}/></a>
          <a href={`${REPO}/actions/workflows/codex-github-pages.yml`} target="_blank" rel="noreferrer">Published calculation runs and full output artifacts <ArrowRight size={16}/></a>
          <a href={`${REPO}/blob/${revision.baselineInputSha}/evidence/GLOBAL_SOURCE_REGISTER.csv`} target="_blank" rel="noreferrer">Public source register <ArrowRight size={16}/></a>
        </div>
        <details><summary>Calculation revision and change history</summary>
          <p>Current revision: {revision.revision}. Historical financial outputs are superseded by this recalculation; original public inputs are retained.</p>
          <p>{Object.keys(revision.output_hashes).length} versioned output artifacts are sealed for the revision. Some artifacts are alternate views of the same underlying calculation layer and should not be read as independent models.</p>
          <ul>{audit.corrections.map(item=><li key={item}>{item}</li>)}</ul>
          <p className="evidence-digest">Calculation fingerprint: {revision.source_sha}</p>
          <a href={`${REPO}/tree/${revision.baselineInputSha}`} target="_blank" rel="noreferrer">Historical source archive</a>
        </details>
      </section>
    </div>
    <footer className="model-footer">VietGreen · C&amp;I Solar Project Finance · Public-data case study</footer>
  </main>;
}