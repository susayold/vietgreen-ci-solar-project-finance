import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

// Vinext places prefixed chunks under basePath. Pages mounts dist/client at
// that basePath already, so the deployment root needs the same _next tree.
const nested='dist/client'+(process.env.SITE_BASE_PATH || '/vietgreen-ci-solar-project-finance')+'/_next';
if(fs.existsSync(nested)) fs.cpSync(nested,'dist/client/_next',{recursive:true});

// Keep the deterministic native workbook untouched. Build the recruiter-facing
// presentation derivative with classic project-finance workings and styling.
const sourceWorkbook='model/vietgreen_core_model.xlsx';
const generatedWorkbook='dist/recruiter-workbook/vietgreen_core_model.xlsx';
const downloads='dist/client/downloads';
if(!fs.existsSync(sourceWorkbook)) throw new Error(`Missing native workbook: ${sourceWorkbook}`);
fs.mkdirSync(path.dirname(generatedWorkbook),{recursive:true});
execFileSync('python',[
  'scripts/build_classic_project_finance_workbook_entry.py',
  sourceWorkbook,
  generatedWorkbook,
],{stdio:'inherit'});

// The original native Control sheet remains only as a hidden formula-support
// sheet. Remove legacy recruiter-skill-demo wording from the published file.
execFileSync('python',['-c',[
  'from openpyxl import load_workbook',
  `p=${JSON.stringify(generatedWorkbook)}`,
  'wb=load_workbook(p)',
  "ws=wb['00_Control'] if '00_Control' in wb.sheetnames else None",
  "ws.sheet_state='hidden' if ws else None",
  "[(setattr(c,'value','MODEL REVIEW NOTES')) for row in ws.iter_rows() for c in row if isinstance(c.value,str) and 'SKILLS DEMONSTRATED' in c.value.upper()] if ws else None",
  'wb.save(p)',
].join(';')],{stdio:'inherit'});

fs.mkdirSync(downloads,{recursive:true});
fs.copyFileSync(generatedWorkbook,path.join(downloads,'vietgreen_core_model.xlsx'));

// Office Online caches workbook previews aggressively by source URL. The workbook
// is rebuilt on every Pages deployment, so give both the embedded viewer and the
// download link a release-specific URL. Also keep visible workbook copy aligned
// with the current 12 review sheets + 22 support/data tabs (34 sheets total).
const workbookUrl='https://susayold.github.io/vietgreen-ci-solar-project-finance/downloads/vietgreen_core_model.xlsx';
const workbookVersion=process.env.GITHUB_SHA || 'local-build';
const versionedWorkbookUrl=`${workbookUrl}?v=${workbookVersion}`;
const replacements=[
  [encodeURIComponent(workbookUrl),encodeURIComponent(versionedWorkbookUrl)],
  [workbookUrl,versionedWorkbookUrl],
  ['EXCEL MODEL · 22-SHEET ARCHITECTURE · FORMULA TRACEABILITY','EXCEL MODEL · 34-SHEET CLASSIC PROJECT FINANCE MODEL · FORMULA TRACEABILITY'],
  ['Native 22-sheet Project Finance review workbook','12 review sheets + 22 support/data tabs'],
  ['22 sheets','34 sheets'],
];

function patchBuiltText(dir){
  if(!fs.existsSync(dir)) return;
  for(const entry of fs.readdirSync(dir,{withFileTypes:true})){
    const file=path.join(dir,entry.name);
    if(entry.isDirectory()){
      patchBuiltText(file);
      continue;
    }
    if(!/\.(?:html|js)$/i.test(entry.name)) continue;
    let text=fs.readFileSync(file,'utf8');
    const before=text;
    for(const [from,to] of replacements) text=text.split(from).join(to);
    if(text!==before) fs.writeFileSync(file,text,'utf8');
  }
}

patchBuiltText('dist/client');
