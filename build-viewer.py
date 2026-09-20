#!/usr/bin/env python3
"""Generate a self-contained monochrome viewer from a sector JSON export.
Usage: python3 build-viewer.py <rows.json> <out.html> "<Sector Title>"
List view + full-page company detail ("tab"). Reusable for any sector."""
import json, sys

src, out_path = sys.argv[1], sys.argv[2]
title = sys.argv[3] if len(sys.argv) > 3 else "India Companies"
rows = json.load(open(src))
data = json.dumps(rows, ensure_ascii=False, separators=(',', ':'))

tpl = r'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ — __N__ companies</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500&display=swap');
:root{--bg:#fff;--ink:#0a0a0a;--sub:#6b6b6b;--line:#e6e6e6;--line2:#d4d4d4;--hover:#f6f6f6;--chip:#f0f0f0;--panel:#fafafa}
@media(prefers-color-scheme:dark){:root{--bg:#0a0a0a;--ink:#f2f2f2;--sub:#9a9a9a;--line:#242424;--line2:#363636;--hover:#161616;--chip:#1c1c1c;--panel:#121212}}
*{box-sizing:border-box}html,body{margin:0}
body{font-family:'Geist',system-ui,-apple-system,BlinkMacSystemFont,sans-serif;font-size:13px;line-height:1.45;background:var(--bg);color:var(--ink);height:100vh;display:flex;flex-direction:column;overflow:hidden}
.mono,.num,.score{font-family:'Geist Mono','Geist',ui-monospace,monospace;font-variant-numeric:tabular-nums}
.view{flex:1;display:flex;flex-direction:column;min-height:0}
.hidden{display:none!important}
.topbar{flex:none;height:52px;background:var(--bg);border-bottom:1px solid var(--line2);display:flex;align-items:center;gap:14px;padding:0 20px}
.topbar h1{font-size:15px;font-weight:600;margin:0;white-space:nowrap}.topbar h1 span{color:var(--sub);font-weight:400}
.tools{display:flex;gap:8px;margin-left:auto;align-items:center}
input,select{font-family:inherit;font-size:13px;padding:7px 10px;border:1px solid var(--line2);border-radius:6px;background:var(--bg);color:var(--ink)}
input[type=search]{min-width:240px}input:focus,select:focus{outline:none;border-color:var(--ink)}
.btn{font-family:inherit;font-size:13px;padding:7px 12px;border:1px solid var(--line2);border-radius:6px;background:var(--bg);color:var(--ink);cursor:pointer}
.btn:hover{background:var(--hover)}
.meta{flex:none;display:flex;flex-wrap:wrap;gap:22px;padding:12px 20px;border-bottom:1px solid var(--line);background:var(--panel)}
.meta div{font-size:11px;color:var(--sub);text-transform:uppercase;letter-spacing:.5px}
.meta b{display:block;font-size:16px;color:var(--ink);font-weight:600;letter-spacing:0;text-transform:none}
.wrap{flex:1;overflow:auto}
table{border-collapse:collapse;width:100%;min-width:1180px;background:var(--bg);table-layout:fixed}
th,td{text-align:left;padding:7px 12px;border-bottom:1px solid var(--line);vertical-align:middle;overflow:hidden;text-overflow:ellipsis}
.co{overflow:hidden}.co>div{min-width:0;overflow:hidden}
.co .nm,.co .wb{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
thead th{position:sticky;top:0;z-index:10;background:var(--bg);border-bottom:1px solid var(--line2);cursor:pointer;user-select:none;font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.5px;color:var(--sub);white-space:nowrap}
thead th:hover{color:var(--ink)}thead th.sorted{color:var(--ink);font-weight:600}
thead th.sorted::after{content:" \2191"}thead th.sorted.desc::after{content:" \2193"}
tbody tr.row{cursor:pointer;height:52px}tbody tr.row:hover{background:var(--hover)}tr.spacer{background:none!important}
.co{display:flex;align-items:center;gap:10px;min-width:210px}
.av{width:26px;height:26px;border-radius:5px;object-fit:contain;background:#fff;border:1px solid var(--line2);flex:none;filter:grayscale(1)}
.av.ph{display:flex;align-items:center;justify-content:center;background:var(--ink);color:var(--bg);font-weight:600;font-size:12px;border:none;filter:none}
.co .nm{font-weight:600}.co .wb{font-size:11px;color:var(--sub)}
.score{font-weight:600}
.desc{color:var(--sub);max-width:440px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.chip{display:inline-block;padding:2px 9px;border:1px solid var(--line2);border-radius:999px;background:var(--chip);font-size:11px;white-space:nowrap}
.num{text-align:right;white-space:nowrap}.xc{font-weight:600;font-size:11px;letter-spacing:.3px}
a{color:var(--ink);text-decoration:underline;text-underline-offset:2px;text-decoration-color:var(--line2)}a:hover{text-decoration-color:var(--ink)}
.muted{color:var(--sub)}
/* detail page */
.dtop{flex:none;height:52px;border-bottom:1px solid var(--line2);display:flex;align-items:center;gap:14px;padding:0 20px}
.dtop .dn{font-size:15px;font-weight:600}.dtop .dm{color:var(--sub);font-size:12px}
.dtop .lk{margin-left:auto;display:flex;gap:14px;font-size:12px}
.dscroll{flex:1;overflow:auto;padding:22px 26px 60px}
.dinner{max-width:1100px;margin:0 auto}
.dhero{display:flex;align-items:center;gap:14px;margin-bottom:18px}
.dhero .av{width:46px;height:46px}.dhero h2{margin:0;font-size:22px;font-weight:600}
.dhero .sub{color:var(--sub);font-size:13px;margin-top:3px}
.kpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:16px 0 24px}
.kpi div{padding:12px 14px;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}
.kpi div .k{font-size:10px;text-transform:uppercase;letter-spacing:.5px;color:var(--sub)}
.kpi div .v{font-weight:600;margin-top:3px;font-size:15px}
.dgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:16px 34px}
.sec{grid-column:1/-1;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.6px;color:var(--sub);margin:18px 0 4px;padding-bottom:7px;border-bottom:1px solid var(--line)}
.fld{margin:2px 0}.fld .k{font-size:10px;text-transform:uppercase;letter-spacing:.5px;color:var(--sub)}
.fld .v{white-space:pre-wrap;word-break:break-word;margin-top:2px}
</style></head><body>
<div class="view" id="listView">
  <div class="topbar">
    <h1>__TITLE__ <span>· <span id="shown">__N__</span>/__N__</span></h1>
    <div class="tools">
      <input type="search" id="q" placeholder="Search name, description, investor, CIN…">
      <select id="sector"><option value="">All sectors</option></select>
      <select id="stage"><option value="">All stages</option></select>
      <select id="city"><option value="">All cities</option></select>
      <select id="sortsel">
        <option value="tracxn_score">Sort · Tracxn Score</option><option value="name">Sort · Name</option>
        <option value="founded_year">Sort · Founded Year</option><option value="latest_revenue_inr">Sort · Revenue</option>
        <option value="investor_count">Sort · Investors</option>
      </select>
    </div>
  </div>
  <div class="meta" id="meta"></div>
  <div class="wrap"><table><colgroup>
    <col style="width:230px"><col style="width:150px" id="colSector"><col style="width:96px"><col style="width:340px">
    <col style="width:120px"><col style="width:120px"><col style="width:96px"><col style="width:130px"><col style="width:86px"><col style="width:96px">
  </colgroup><thead><tr>
    <th data-k="name">Company</th><th data-k="sector_group" id="thSector">Sector</th><th data-k="tracxn_score" class="num">Tracxn Score</th>
    <th data-k="short_description">Description</th><th data-k="stage">Stage</th><th data-k="hq_city">HQ City</th>
    <th data-k="latest_revenue_inr" class="num">Revenue ₹Cr</th><th data-k="latest_funding_round">Last Round</th>
    <th data-k="investor_count" class="num">Investors</th><th data-k="xcorn">X-corn</th>
  </tr></thead><tbody id="tb"></tbody></table></div>
</div>
<div class="view hidden" id="detailView">
  <div class="dtop">
    <button class="btn" id="backBtn">← Back</button>
    <span class="dn" id="dtopName"></span>
    <span class="lk" id="dtopLinks"></span>
  </div>
  <div class="dscroll"><div class="dinner" id="dbody"></div></div>
</div>
<script>
const DATA=__DATA__;
const esc=s=>{const d=document.createElement('div');d.textContent=(s==null?'':String(s));return d.innerHTML;};
const att=s=>(s==null?'':String(s)).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const cr=v=>{const n=parseFloat(v);return isNaN(n)?'':(n/1e7).toLocaleString('en-IN',{maximumFractionDigits:1});};
const initAv=r=>{const init=((r.name||'?').trim()[0]||'?').toUpperCase();
  return r.logo?`<img class="av" src="${esc(r.logo)}" alt="" onerror="this.outerHTML='<span class=&quot;av ph&quot;>${esc(init)}</span>'">`:`<span class="av ph">${esc(init)}</span>`;};
const byId={};DATA.forEach(r=>byId[r.tracxn_id]=r);
const $=id=>document.getElementById(id);
const listView=$('listView'),detailView=$('detailView'),tb=$('tb'),q=$('q'),stg=$('stage'),cty=$('city'),sec=$('sector'),sortsel=$('sortsel'),shown=$('shown');
const SECTORS=[...new Set(DATA.map(r=>r.sector_group).filter(Boolean))].sort();
SECTORS.forEach(s=>sec.add(new Option(s,s)));
if(SECTORS.length<2){sec.style.display='none';const st=document.createElement('style');st.textContent='#thSector,.secCell{display:none}#colSector{width:0}';document.head.appendChild(st);}
[...new Set(DATA.map(r=>r.stage).filter(Boolean))].sort().forEach(s=>stg.add(new Option(s,s)));
[...new Set(DATA.map(r=>r.hq_city).filter(Boolean))].sort().forEach(s=>cty.add(new Option(s,s)));
(function(){const funded=DATA.filter(r=>r.stage&&!/Unfunded|Deadpooled/.test(r.stage)).length,withRev=DATA.filter(r=>r.latest_revenue_inr).length,cin=DATA.filter(r=>r.cin).length,uni=DATA.filter(r=>r.xcorn==='UNICORN').length;
 $('meta').innerHTML=`<div><b>__N__</b>Companies</div><div><b>${funded}</b>Funded</div><div><b>${withRev}</b>With revenue</div><div><b>${cin}</b>With CIN</div><div><b>${uni}</b>Unicorns</div>`;})();
let sortK='tracxn_score',sortDir=-1;
function row(r){return `<tr class="row" data-id="${esc(r.tracxn_id)}">
  <td><div class="co">${initAv(r)}<div><div class="nm" title="${att(r.name)}">${esc(r.name)}</div>${r.website?`<div class="wb"><a href="${esc(r.website)}" target="_blank" rel="noopener" title="${att(r.website)}" onclick="event.stopPropagation()">${esc(r.website.replace(/^https?:\/\//,'').replace(/\/$/,''))}</a></div>`:''}</div></div></td>
  <td class="secCell" title="${att(r.sector_group)}">${r.sector_group?`<span class="chip">${esc(r.sector_group)}</span>`:''}</td>
  <td class="num"><span class="score">${r.tracxn_score?Math.round(parseFloat(r.tracxn_score)):'<span class=muted>—</span>'}</span></td>
  <td title="${att(r.short_description)}"><div class="desc">${esc(r.short_description)||'<span class=muted>—</span>'}</div></td>
  <td title="${att(r.stage)}">${r.stage?`<span class="chip">${esc(r.stage)}</span>`:'<span class=muted>—</span>'}</td>
  <td title="${att(r.hq_city)}">${esc(r.hq_city)||'<span class=muted>—</span>'}</td>
  <td class="num" title="${r.latest_revenue_inr?'₹'+cr(r.latest_revenue_inr)+' Cr':''}">${cr(r.latest_revenue_inr)||'<span class=muted>—</span>'}</td>
  <td title="${att([r.latest_funding_round,r.latest_funding_date].filter(Boolean).join(' · '))}">${esc(r.latest_funding_round)||'<span class=muted>—</span>'}</td>
  <td class="num">${r.investor_count&&r.investor_count!=='0'?esc(r.investor_count):'<span class=muted>—</span>'}</td>
  <td><span class="xc">${esc(r.xcorn)||'<span class=muted>—</span>'}</span></td></tr>`;}
function detailHtml(r){const A=(u,t)=>u?`<a href="${esc(u)}" target="_blank" rel="noopener">${esc(t||u)}</a>`:'';
 const F=(l,v)=>`<div class="fld"><div class="k">${l}</div><div class="v">${v!=null&&v!==''?v:'<span class=muted>—</span>'}</div></div>`;
 const K=(l,v)=>`<div><div class="k">${l}</div><div class="v">${v!=null&&v!==''?v:'—'}</div></div>`;
 return `<div class="dhero">${initAv(r)}<div><h2>${esc(r.name)}</h2><div class="sub">${r.sector_group?esc(r.sector_group)+' · ':''}${[esc(r.hq_city),esc(r.hq_state),esc(r.hq_country)].filter(Boolean).join(', ')||'—'} · Founded ${esc(r.founded_year)||'—'}</div></div></div>
  <div class="kpi">${K('Tracxn Score',r.tracxn_score?Math.round(parseFloat(r.tracxn_score)):'—')}${K('Stage',esc(r.stage))}${K('X-corn',esc(r.xcorn))}${K('Revenue',r.latest_revenue_inr?('₹'+cr(r.latest_revenue_inr)+' Cr'):'—')}${K('Investors',esc(r.investor_count))}${K('Last round',esc(r.latest_funding_round))}</div>
  <div class="dgrid">
   <div class="sec">Overview</div>${F('Short description',esc(r.short_description))}${F('Detailed description',esc(r.detailed_description))}
   <div class="sec">Location &amp; Legal</div>${F('Registered address',esc(r.registered_address))}${F('Pincode',esc(r.pincode))}${F('Legal entity',esc(r.legal_entity_name))}${F('CIN',esc(r.cin))}${F('Entity type',esc(r.entity_type))}${F('Registrar',esc(r.registrar))}
   <div class="sec">People</div>${F('Founders',esc(r.founders))}${F('Founder DINs',esc(r.founder_dins))}${F('Key people',esc(r.key_people))}${F('Female founder',esc(r.has_female_founder))}${F('Emails',esc(r.emails))}
   <div class="sec">Funding &amp; Investors</div>${F('Last round',[r.latest_funding_round,r.latest_funding_date].filter(Boolean).map(esc).join(' · '))}${F('Total equity funding (USD)',esc(r.total_equity_funding_usd))}${F('Investors ('+esc(r.investor_count)+')',esc(r.investors))}${F('Lead investors',esc(r.lead_investors))}${F('Incubators',esc(r.incubators))}
   <div class="sec">Financials</div>${F('Latest revenue',r.latest_revenue_inr?('₹'+cr(r.latest_revenue_inr)+' Cr'):'')}${F('Revenue as on',esc(r.revenue_as_on))}${F('Rev. growth 1Y %',esc(r.revenue_growth_1y_pct))}${F('Net profit as on',esc(r.net_profit_as_on))}${F('EBITDA as on',esc(r.ebitda_as_on))}
   <div class="sec">Taxonomy &amp; Meta</div>${F('Sectors',esc(r.sectors))}${F('Feeds',esc(r.feeds))}${F('Editor rating',esc(r.editor_rating))}${F('Status',esc(r.status))}${F('Last updated',esc(r.last_updated))}
  </div>`;}
function openCompany(id){const r=byId[id];const A=(u,t)=>u?`<a href="${esc(u)}" target="_blank" rel="noopener">${esc(t)}</a>`:'';
 $('dtopName').textContent=r.name;
 $('dtopLinks').innerHTML=[A(r.website,'Website'),A(r.linkedin,'LinkedIn'),A(r.tracxn_url,'Tracxn ↗')].filter(Boolean).join(' · ');
 $('dbody').innerHTML=detailHtml(r);
 listView.classList.add('hidden');detailView.classList.remove('hidden');detailView.querySelector('.dscroll').scrollTop=0;}
function backToList(){detailView.classList.add('hidden');listView.classList.remove('hidden');}
$('backBtn').addEventListener('click',backToList);
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!detailView.classList.contains('hidden'))backToList();});
const wrapEl=document.querySelector('.wrap');const ROWH=52;let filtered=[];
function render(){const term=q.value.trim().toLowerCase(),fs=stg.value,fc=cty.value,fsec=sec.value;
 filtered=DATA.filter(r=>{if(fsec&&r.sector_group!==fsec)return false;if(fs&&r.stage!==fs)return false;if(fc&&r.hq_city!==fc)return false;
  if(term){const b=(r.name+' '+r.short_description+' '+r.detailed_description+' '+r.investors+' '+r.founders+' '+r.cin+' '+r.hq_city+' '+(r.sector_group||'')).toLowerCase();if(!b.includes(term))return false;}return true;});
 filtered.sort((a,b)=>{let x=a[sortK],y=b[sortK];const nx=parseFloat(x),ny=parseFloat(y);
  if(!isNaN(nx)&&!isNaN(ny)){x=nx;y=ny;}else{x=(x||'').toString().toLowerCase();y=(y||'').toString().toLowerCase();}return x<y?-sortDir:x>y?sortDir:0;});
 shown.textContent=filtered.length;wrapEl.scrollTop=0;renderWindow();
 document.querySelectorAll('thead th').forEach(th=>{th.classList.toggle('sorted',th.dataset.k===sortK);th.classList.toggle('desc',th.dataset.k===sortK&&sortDir===-1);});}
function renderWindow(){const st=wrapEl.scrollTop,h=wrapEl.clientHeight||700;
 const start=Math.max(0,Math.floor(st/ROWH)-8),end=Math.min(filtered.length,Math.ceil((st+h)/ROWH)+8);
 let html=start>0?`<tr class="spacer" style="height:${start*ROWH}px"></tr>`:'';
 for(let i=start;i<end;i++)html+=row(filtered[i]);
 const bot=filtered.length-end;if(bot>0)html+=`<tr class="spacer" style="height:${bot*ROWH}px"></tr>`;
 tb.innerHTML=html;}
let _sched=false;wrapEl.addEventListener('scroll',()=>{if(_sched)return;_sched=true;requestAnimationFrame(()=>{_sched=false;renderWindow();});});
tb.addEventListener('click',e=>{const tr=e.target.closest('tr.row');if(!tr)return;openCompany(tr.dataset.id);});
document.querySelectorAll('thead th').forEach(th=>th.addEventListener('click',()=>{const k=th.dataset.k;if(k===sortK)sortDir*=-1;else{sortK=k;sortDir=(k==='name'||k==='hq_city'||k==='stage')?1:-1;}if([...sortsel.options].some(o=>o.value===k))sortsel.value=k;render();}));
sortsel.addEventListener('change',()=>{sortK=sortsel.value;sortDir=(sortK==='name')?1:-1;render();});
[q,stg,cty,sec].forEach(el=>el.addEventListener('input',()=>render()));
render();
</script></body></html>'''

out = tpl.replace('__DATA__', data).replace('__TITLE__', title).replace('__N__', str(len(rows)))
open(out_path, 'w').write(out)
print(f"wrote {out_path} | {len(rows)} rows | {round(len(out)/1024)} KB")
