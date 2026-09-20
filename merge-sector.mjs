import fs from 'node:fs';
import { flattenCompany } from './lib.mjs';
const [slug, name] = [process.argv[2], process.argv[3]];

// combined store is chunked: one JSON.stringify/parse of the whole thing overflows
// V8's max string length past ~300k rows (legacy single combined.json still readable)
const combinedParts = () => fs.readdirSync('.').filter(f => /^combined-part\d+\.json$/.test(f)).sort();
const combined = [];
const pushAll = (list, arr) => { for (const x of arr) list.push(x); };
if (fs.existsSync('combined.json')) pushAll(combined, JSON.parse(fs.readFileSync('combined.json','utf8')));
for (const f of combinedParts()) pushAll(combined, JSON.parse(fs.readFileSync(f,'utf8')));

const kept = combined.filter(r => r.sector_group !== name);
const dir = `data-detail/${slug}`;
const raw = [];
if (fs.existsSync(`${dir}/companies.json`)) pushAll(raw, JSON.parse(fs.readFileSync(`${dir}/companies.json`,'utf8')));
for (const f of fs.readdirSync(dir).filter(f=>/^companies-part\d+\.json$/.test(f)).sort()) pushAll(raw, JSON.parse(fs.readFileSync(`${dir}/${f}`,'utf8')));
const add = raw.map(c => ({ ...flattenCompany(c), logo: c.logo||'', sector_group: name }));
const out = [...kept, ...add];

const CHUNK = 50000;
for (const f of combinedParts()) fs.rmSync(f);
for (let i = 0; i*CHUNK < out.length; i++)
  fs.writeFileSync(`combined-part${String(i).padStart(2,'0')}.json`, JSON.stringify(out.slice(i*CHUNK,(i+1)*CHUNK)));
if (fs.existsSync('combined.json')) fs.rmSync('combined.json');
console.log(`combined: ${combined.length} -> ${out.length} (added ${add.length} ${name})`);
