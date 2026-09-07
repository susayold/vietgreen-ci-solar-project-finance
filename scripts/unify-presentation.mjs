// One-time mechanical migration: isolate legacy page CSS and reuse the navigation.
import fs from 'node:fs';
import path from 'node:path';
import postcss from 'postcss';
const pages=['overview','projects','energy','economics','debt','risk','diligence','model-evidence'];
for(const page of pages){
 const file=page==='overview'?'app/page.tsx':`app/${page}/page.tsx`;
 let text=fs.readFileSync(file,'utf8');
 if(!text.includes("import SiteHeader")) {
  text=text.replace(/(<header\b[\s\S]*?<\/header>)/,`<SiteHeader active="${page==='overview'?'/':'/'+page}" />`);
  text=text.replace(/('use client';)/,"$1\nimport SiteHeader from '@/lib/site-header';");
 }
 text=text.replace(/Model: V5\.1\.3(?: \(Frozen\))?/g,'Solar Project Finance').replace(/V5\.1\.3 · Frozen model · /g,'').replace(/>Frozen Model</g,'>Methodology & Evidence<');
 fs.writeFileSync(file,text);
 if(page==='overview') continue;
 const scope=page==='model-evidence'?'model':page;
 for(const name of fs.readdirSync(`app/${page}`).filter(f=>f.endsWith('.css'))){
  const cssFile=path.join('app',page,name); const root=postcss.parse(fs.readFileSync(cssFile,'utf8'));
  root.walkRules(rule=>{
   if(rule.parent?.type==='atrule' && /keyframes$/.test(rule.parent.name))return;
   rule.selectors=rule.selectors.map(sel=>sel.includes(`.${scope}-page`)?sel:`.${scope}-page ${sel}`);
  }); fs.writeFileSync(cssFile,root.toString());
 }
}
