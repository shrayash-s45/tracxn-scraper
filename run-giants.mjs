// Giant/any-size India sector driver. foundedYear partition, with RECURSIVE
// sub-partitioning of oversized buckets by stateId then cityId (each filter is a
// fresh <5000 candidate pool). Budget-aware: fills the day's credits then halts
// cleanly; fully resumable via per-bucket page cache. Env: SLUG, PA_ID, TOP5000=1.
import { chromium } from 'playwright';
import fs from 'node:fs';
const IN='57ada2abe4b0e0fbead7d6da', PAGE=100, MAXFROM=4900, RESERVE=600;
const TOP5000=process.env.TOP5000==='1';
const SLUG=process.env.SLUG, PA=process.env.PA_ID;
if(!SLUG||!PA){console.error('set SLUG and PA_ID');process.exit(1);}
const STATES=JSON.parse(fs.readFileSync('india-states.json','utf8'));
const CITIES=JSON.parse(fs.readFileSync('india-cities.json','utf8'));
const YEARS=[]; for(let y=2026;y>=1970;y--) YEARS.push([y]); YEARS.push(Array.from({length:70},(_,i)=>1900+i));
const jitter=(a,b)=>new Promise(r=>setTimeout(r,a+Math.random()*(b-a)));
const log=(...a)=>console.log(new Date().toISOString().slice(11,19),...a);
const dir=`data-detail/${SLUG}`; fs.mkdirSync(dir,{recursive:true});

const b=await chromium.launch({headless:true});
const ctx=await b.newContext({storageState:'state.json',userAgent:'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36'});
const p=await ctx.newPage();
await p.goto('https://platform.tracxn.com/a/dashboard',{waitUntil:'domcontentloaded',timeout:60000}); await p.waitForTimeout(2000);
async function api(path,body){for(let i=0;i<5;i++){try{return await p.evaluate(async({path,body})=>{const r=await fetch('https://platform.tracxn.com'+path,{method:'POST',credentials:'include',headers:{'content-type':'application/json'},body:JSON.stringify(body)});let t='';try{t=await r.text();}catch{}return{status:r.status,text:t};},{path,body});}catch(e){if(i===4)throw e;log(`  [retry ${i+1}] ${String(e.message||e).slice(0,40)}`);await new Promise(r=>setTimeout(r,3000*(i+1)));}}}
const remaining=async()=>{try{const r=await api('/api/2.2/credits',{});const c=JSON.parse(r.text).result[0];return c.creditLimit-c.exhaustedCredits;}catch{return null;}};
const F=extra=>({practiceAreaId:[PA],countryId:[IN],...extra});
const count=async filter=>{const r=await api('/api/4.0/companies/count',{dataset:'query',query:{},filter});try{return JSON.parse(r.text).count;}catch{return -1;}};

let halted=false, approxSpent=0, budget=Infinity;
const rows=new Map();
async function paginate(filter,tag){
  let from=0;
  while(from<=MAXFROM){
    if(halted) return;
    const cache=`${dir}/${tag}-${from}.json`; let data;
    if(fs.existsSync(cache)){ try{ data=JSON.parse(fs.readFileSync(cache,'utf8')); }catch{ try{fs.rmSync(cache);}catch{}; data=undefined; } }
    if(data===undefined){
      if(approxSpent+PAGE>budget){halted=true;log(`  [budget] halting — day's credits used`);return;}
      let r,ok=false;
      for(let t=0;t<3&&!ok;t++){
        r=await api('/api/4.0/companies',{dataset:'query',sort:[{sortField:'relevance',order:'DESC'}],query:{},filter,size:PAGE,from});
        if(r.status===422||r.status!==200) break;
        try{ data=JSON.parse(r.text).result||[]; ok=true; }catch{ log(`  ! ${tag} from=${from} empty resp — retry`); await new Promise(x=>setTimeout(x,2500)); }
      }
      if(r.status===422) break;
      if(!ok){ log(`  ! ${tag} from=${from} status ${r.status} — stop bucket`); break; }
      fs.writeFileSync(cache,JSON.stringify(data)); approxSpent+=data.length; await jitter(500,1100);
    }
    for(const c of data) rows.set(c.id,c);
    if(data.length<PAGE)break; from+=PAGE;
  }
}
// recursive: try to fully page `filter`; if >cap, split by next dim (state->city)
async function fetchBucket(filter,tag,dims){
  if(halted) return;
  const c=await count(filter);
  if(c<=0) return;
  if(c<=MAXFROM){ await paginate(filter,tag); return; }
  if(dims.length===0){ log(`  [warn] ${tag} still ${c}>cap; taking top ${MAXFROM}`); await paginate(filter,tag); return; }
  const [dim,...rest]=dims;
  const items = dim==='state'?STATES:CITIES; const key = dim==='state'?'stateId':'cityId';
  log(`  ${tag} (${c}) -> split by ${dim} (${items.length})`);
  for(const it of items){ if(halted)return; await fetchBucket({...filter,[key]:[it.id]}, `${tag}_${key}${it.id.slice(-5)}`, rest); }
}

const probe=await api('/api/4.0/companies/count',{dataset:'query',query:{},filter:{countryId:[IN]}});
if(probe.status!==200||/notice|login/i.test(probe.text)){log('AUTH FAILED — re-paste cookies');await b.close();process.exit(3);}
const total=await count(F());
const startRem=await remaining(); budget=startRem-RESERVE;
log(`sector=${SLUG} total=${total} creditsRemaining=${startRem} budget=${budget} TOP5000=${TOP5000}`);

const outFile=`${dir}/companies.json`;
const partFiles=()=>fs.readdirSync(dir).filter(f=>/^companies-part\d+\.json$/.test(f)).sort();
if(fs.existsSync(outFile)){for(const c of JSON.parse(fs.readFileSync(outFile,'utf8'))) rows.set(c.id,c);}
for(const f of partFiles()){for(const c of JSON.parse(fs.readFileSync(`${dir}/${f}`,'utf8'))) rows.set(c.id,c);}
if(rows.size) log(`  resuming: ${rows.size} already saved`);

if(total<=MAXFROM){ await paginate(F(),'fwd'); }
else{
  if(TOP5000){ await paginate(F(),'top'); log(`  top-5000 -> unique ${rows.size}`); }
  for(const yrs of YEARS){
    if(halted) break;
    const label = yrs.length===1?`y${yrs[0]}`:'pre1970';
    await fetchBucket({...F(),foundedYear:yrs}, label, ['state','city']);
  }
}
// chunked save: one big JSON.stringify overflows V8's max string length past ~45k raw rows
{
  const all=[...rows.values()], CHUNK=15000;
  for(const f of partFiles()) fs.rmSync(`${dir}/${f}`);
  for(let i=0;i*CHUNK<all.length;i++) fs.writeFileSync(`${dir}/companies-part${String(i).padStart(2,'0')}.json`, JSON.stringify(all.slice(i*CHUNK,(i+1)*CHUNK)));
  if(fs.existsSync(outFile)) fs.rmSync(outFile);
}
log(`=== ${SLUG}: ${rows.size}/${total} unique ${halted?'(HALTED at budget — resume next reset)':'(COMPLETE)'} ; creditsRemaining≈${startRem-approxSpent}`);
await b.close();
