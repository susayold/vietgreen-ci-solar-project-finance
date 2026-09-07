import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const root = path.resolve('dist/client');
http.createServer((req,res) => {
  let pathname = decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  if(!pathname.startsWith('/vietgreen-ci-solar-project-finance/') && pathname !== '/vietgreen-ci-solar-project-finance') {res.writeHead(404).end();return;}
  pathname = pathname.replace(/^\/vietgreen-ci-solar-project-finance(?=\/|$)/,'');
  const candidate = path.resolve(root,'.'+(pathname || '/'));
  if (!candidate.startsWith(root+path.sep) && candidate !== root) {res.writeHead(403).end();return;}
  const file = [candidate,candidate+'.html',path.join(candidate,'index.html')].find(p => fs.existsSync(p) && fs.statSync(p).isFile());
  if(!file){res.writeHead(404).end();return;}
  const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.webp':'image/webp','.png':'image/png','.rsc':'text/x-component'};
  res.writeHead(200,{'Content-Type':types[path.extname(file)] || 'application/octet-stream'});
  fs.createReadStream(file).pipe(res);
}).listen(8765,'127.0.0.1',()=>console.log('Static QA server http://127.0.0.1:8765/vietgreen-ci-solar-project-finance/'));
