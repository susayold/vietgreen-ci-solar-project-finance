import fs from 'node:fs';
// Vinext places prefixed chunks under basePath. Pages mounts dist/client at
// that basePath already, so the deployment root needs the same _next tree.
const nested='dist/client/vietgreen-ci-solar-project-finance/_next';
if(fs.existsSync(nested)) fs.cpSync(nested,'dist/client/_next',{recursive:true});
