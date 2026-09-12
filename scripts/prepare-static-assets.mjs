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
  'scripts/build_classic_project_finance_workbook.py',
  sourceWorkbook,
  generatedWorkbook,
],{stdio:'inherit'});
fs.mkdirSync(downloads,{recursive:true});
fs.copyFileSync(generatedWorkbook,path.join(downloads,'vietgreen_core_model.xlsx'));
