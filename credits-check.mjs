import { chromium } from 'playwright';
const b = await chromium.launch({ headless: true });
const ctx = await b.newContext({ storageState: 'state.json', userAgent:'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36' });
const p = await ctx.newPage();
await p.goto('https://platform.tracxn.com/a/dashboard', { waitUntil:'domcontentloaded', timeout:60000 });
await p.waitForTimeout(2000);
const t = await p.evaluate(async () => { const r=await fetch('https://platform.tracxn.com/api/2.2/credits',{method:'POST',credentials:'include',headers:{'content-type':'application/json'},body:'{}'}); return await r.text(); });
try { const x=JSON.parse(t).result[0]; console.log('SESSION OK — credits used', x.exhaustedCredits, '/', x.creditLimit, '=> remaining', x.creditLimit-x.exhaustedCredits); }
catch { console.log('SESSION RESPONSE:', t.slice(0,200)); }
await b.close();
