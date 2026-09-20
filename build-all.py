import json, subprocess, re, sys, os
SC=sys.argv[1]; DIR=sys.argv[2]
out_dir=os.path.join(DIR,'tracxn-viewers'); os.makedirs(out_dir, exist_ok=True)
rows=[]
if os.path.exists(os.path.join(SC,'combined.json')): rows+=json.load(open(os.path.join(SC,'combined.json')))
for f in sorted(f for f in os.listdir(SC) if re.match(r'combined-part\d+\.json$',f)): rows+=json.load(open(os.path.join(SC,f)))
groups={}
for r in rows: groups.setdefault(r.get('sector_group','Other'),[]).append(r)
slug=lambda s: re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
index=[]
for name in sorted(groups, key=lambda k:-len(groups[k])):
    g=groups[name]; sg=slug(name); jf=os.path.join(SC,f'_split_{sg}.json'); hf=os.path.join(out_dir,f'{sg}.html')
    json.dump(g, open(jf,'w'), separators=(',',':'))
    subprocess.run(['python3', os.path.join(DIR,'build-viewer.py'), jf, hf, f'{name} · India'], check=True)
    funded=sum(1 for r in g if r['stage'] and r['stage'] not in ('Unfunded','Deadpooled'))
    withrev=sum(1 for r in g if r['latest_revenue_inr'])
    size=os.path.getsize(hf)//(1024*1024)
    index.append({'name':name,'file':f'{sg}.html','n':len(g),'funded':funded,'withrev':withrev,'mb':size})
    os.remove(jf)
# index page
total=sum(x['n'] for x in index)
cards=''.join(f'''<a class="card" href="{x['file']}"><div class="nm">{x['name']}</div>
  <div class="st"><b>{x['n']:,}</b> companies</div>
  <div class="sub">{x['funded']:,} funded · {x['withrev']:,} with revenue · {x['mb']} MB</div></a>''' for x in index)
html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tracxn India · Sector Viewers</title>
<style>@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap');
:root{{--bg:#fff;--ink:#0a0a0a;--sub:#6b6b6b;--line:#e6e6e6;--hover:#f6f6f6}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0a0a0a;--ink:#f2f2f2;--sub:#9a9a9a;--line:#242424;--hover:#161616}}}}
*{{box-sizing:border-box}}body{{margin:0;font-family:'Geist',system-ui,sans-serif;background:var(--bg);color:var(--ink);padding:40px 32px}}
h1{{font-size:22px;margin:0 0 4px}}.lead{{color:var(--sub);margin:0 0 28px;font-size:14px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px;max-width:1100px}}
.card{{border:1px solid var(--line);border-radius:12px;padding:18px 18px;text-decoration:none;color:inherit;transition:.12s}}
.card:hover{{background:var(--hover);border-color:var(--ink)}}
.card .nm{{font-weight:600;font-size:15px;margin-bottom:8px}}
.card .st{{font-size:13px;color:var(--sub)}}.card .st b{{font-size:20px;color:var(--ink);font-weight:600}}
.card .sub{{font-size:12px;color:var(--sub);margin-top:6px}}</style></head>
<body><h1>Tracxn India · Company Data</h1>
<p class="lead">{total:,} companies across {len(index)} sectors. Click a sector to open its viewer.</p>
<div class="grid">{cards}</div></body></html>'''
open(os.path.join(out_dir,'index.html'),'w').write(html)
print(f'built {len(index)} sector files + index in {out_dir}')
for x in index: print(f"  {x['name']}: {x['n']:,} ({x['mb']}MB)")
