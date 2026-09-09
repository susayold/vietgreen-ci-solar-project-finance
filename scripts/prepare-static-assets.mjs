import fs from 'node:fs';
import path from 'node:path';

// Vinext places prefixed chunks under basePath. Pages mounts dist/client at
// that basePath already, so the deployment root needs the same _next tree.
const nested='dist/client'+(process.env.SITE_BASE_PATH || '/vietgreen-ci-solar-project-finance')+'/_next';
if(fs.existsSync(nested)) fs.cpSync(nested,'dist/client/_next',{recursive:true});

// Publish the native Excel review workbook as a first-class website artifact.
// This keeps the recruiter viewer/download on the same static site while the
// workbook remains separately versioned from the frozen V5.1.3 web dataset.
const workbook='model/vietgreen_core_model.xlsx';
const downloads='dist/client/downloads';
if(!fs.existsSync(workbook)) throw new Error(`Missing native workbook: ${workbook}`);
fs.mkdirSync(downloads,{recursive:true});
fs.copyFileSync(workbook,path.join(downloads,'vietgreen_core_model.xlsx'));
