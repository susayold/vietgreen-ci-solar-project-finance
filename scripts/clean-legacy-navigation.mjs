import fs from 'node:fs';
import ts from 'typescript';
for(const [file,names] of [['app/page.tsx',['Logo','navItems']],['app/projects/page.tsx',['Brand','items']],['app/diligence/page.tsx',['items']]]){
 let source=fs.readFileSync(file,'utf8'); const ast=ts.createSourceFile(file,source,ts.ScriptTarget.Latest,true,ts.ScriptKind.TSX); const ranges=[];
 function walk(node){if(ts.isFunctionDeclaration(node)&&names.includes(node.name?.text)){ranges.push([node.getFullStart(),node.end]);return;}if(ts.isVariableStatement(node)&&node.declarationList.declarations.some(d=>names.includes(d.name.getText(ast)))){ranges.push([node.getFullStart(),node.end]);return;}ts.forEachChild(node,walk);}walk(ast);
 for(const [a,b] of ranges.sort((a,b)=>b[0]-a[0]))source=source.slice(0,a)+source.slice(b);
 if(!source.includes("import SiteHeader"))source="import SiteHeader from '@/lib/site-header';\n"+source;
 fs.writeFileSync(file,source);
}
