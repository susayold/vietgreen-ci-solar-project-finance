// Vinext beta5 prerender requests omit configured basePath. Narrow, checked patch;
// no model code or browser runtime is rewritten. Remove when upstream resolves it.
import fs from 'node:fs';
const file='node_modules/vinext/dist/build/prerender.js';
const source=fs.readFileSync(file,'utf8');
const before='${parsed.pathname}${parsed.search}';
const after='${config.basePath || ""}${parsed.pathname}${parsed.search}';
if (!source.includes(after)) {
  if(source.split(before).length !== 2) throw new Error('Unexpected Vinext prerender implementation; review required');
  fs.writeFileSync(file,source.replace(before,after));
}
