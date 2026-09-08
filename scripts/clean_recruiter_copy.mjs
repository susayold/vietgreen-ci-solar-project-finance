// One-time, exact-copy migration. Leaves data keys and financial definitions unchanged.
import fs from 'node:fs';
const paths=['app/page.tsx',...['projects','energy','economics','debt','risk','diligence'].map(p=>`app/${p}/page.tsx`)];
const replacements=[
 ['Final Recruiter Takeaway','Key Takeaway'],['Recruiter Takeaway','Key Takeaway'],['RECRUITER TAKEAWAY','KEY TAKEAWAY'],
 ['The Debt Contract Does Not Self-Heal','Contractual Debt Under Stress'],
 ['A Decision Framework — Not a Fabricated Investment Decision','Commercial Analysis and Diligence'],
 ['The Model Does Not Hide Bad Data.','Physical Data Quality'],
 ['The frozen credit payload selects the minimum supportable','The model selects the minimum supportable'],
 ['Generated Year 1 DSCR is compared with the standardized','Year 1 DSCR is compared with the'],
 ['target from the selected debt payload.','selected coverage target.'],
 ['Frozen model CAPEX · USD','CAPEX assumption · USD'],
 ['Frozen model output','Calculated reference case'],['Frozen model output','Calculated reference case'],
 ['Frozen output unavailable','Data unavailable'],['frozen website release','published results'],
 ['Loading frozen diligence payload…','Loading project evidence…'],
 ['frozen project master','project source register'],['frozen public-data master','public-data register'],
 ['frozen economics payload','calculated project results'],
 ['Amounts are VND equivalents using frozen project FX.','Amounts are VND equivalents at the stated exchange rates.'],
 ['Local-currency model thresholds converted using frozen FX.','Thresholds converted at the stated exchange rates.'],
 ['FX Rate (Frozen)','Reference Exchange Rate'],['Frozen base schedule','Base debt schedule'],
 ['8,760-hour real-world modeling','8,760-hour modeled profiles'],
 ['Long-term degradation modeling','Verified long-term degradation performance'],
 ['Data as of: 31 Dec 2024','Public sources and documented assumptions'],
 ['THIS PAGE: DILIGENCE · SHORTLIST ONLY','Diligence workplan'],
 ['RECRUITER-READY','ANALYSIS-READY'],
];
for(const path of paths){let text=fs.readFileSync(path,'utf8');for(const [from,to]of replacements)text=text.replaceAll(from,to);fs.writeFileSync(path,text);}
let home=fs.readFileSync('app/page.tsx','utf8');
home=home.replace("import physicalSource from '../public/data/physical.json';", "import physicalSource from '../public/data/physical.json';\nimport revision from '../public/data/model-revision.json';");
home=home.replace("fmt(summary.workbookSheets),'Workbook sheets'","String(Object.keys(revision.output_hashes).length),'Result tables'")
 .replace("fmt(summary.regressionTests),'Regression tests'","String(revision.checks.length),'Calculation checks'")
 .replace("fmt(summary.semanticControls),'Semantic controls'","'9','Scenarios per project'")
 .replace('All results are presented as a range based on observable market conditions and counterparty profiles.','Reference tariff thresholds use public inputs and explicit return and credit assumptions.')
 .replace('PPA pricing is not inferred.','Executed PPA pricing is not disclosed.')
 .replace('href="#project-glance">Explore all','href="/projects">Explore all');
fs.writeFileSync('app/page.tsx',home);
