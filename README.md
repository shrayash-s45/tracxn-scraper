# Tracxn India company scraper

Sector-by-sector scraper for Tracxn India company profiles. Pulls full company
records from Tracxn's internal API inside an authenticated headless browser
session, one sector at a time, and merges them into a flat store plus a set of
self-contained HTML viewer pages.

> Run this against a Tracxn account **you** are authorised to use. Every company
> row returned costs ~1 credit against that account's daily plan; the driver
> respects the daily budget and resumes the next day. It does not circumvent
> Tracxn's metering.

## Setup

```bash
npm ci
npx playwright install chromium
cp state.json.example state.json   # then fill in your own session cookies
```

To fill `state.json`: log in to platform.tracxn.com in Chrome, open DevTools →
Network, "Copy as cURL" on any `platform.tracxn.com/api/...` request, and copy
the cookie values from its `-b` header into `state.json` (keys shown in the
example). This is a Playwright `storageState` file. Cookies expire every few
days — re-paste when `credits-check.mjs` reports an auth failure.

## Run

```bash
# 1) confirm the session works and see remaining credits
node credits-check.mjs

# 2) scrape one sector (background + wait for the final line)
SLUG=fintech PA_ID=<practiceAreaId> TOP5000=1 nohup node run-giants.mjs > fintech.log 2>&1 &
until grep -q "=== fintech:" fintech.log 2>/dev/null; do sleep 30; done; tail -5 fintech.log
#   final line: "=== fintech: <unique>/<total> unique (COMPLETE|HALTED at budget) ..."
#   HALTED just means the day's credit budget ran out — rerun the SAME command
#   next day; the per-bucket page cache makes the resume free.

# 3) merge the finished sector + rebuild the viewers
node merge-sector.mjs fintech "FinTech"
python3 build-all.py "$PWD" "$PWD"
```

`run-giants.mjs` env vars: `SLUG` (folder/label), `PA_ID` (Tracxn practiceArea
id for the sector), `TOP5000=1` (always). Find a sector's `PA_ID` from the
`practiceAreaId` filter in a company-search request captured from the logged-in
web app.

## How it works

Tracxn's search API returns at most the top 5,000 results of any query, so
sectors larger than that are fetched by **partitioning** into sub-queries that
are each under the cap, then de-duplicating by company id:

1. A top-5,000 relevance pass (catches high-relevance records with no founding year).
2. One query per `foundedYear`.
3. Any year bucket still over ~4,900 is split by `stateId`, then by `cityId`.

`india-states.json` (38) and `india-cities.json` (539) supply the geo split
dimensions. The driver is **budget-aware** (stops when the day's credits are
spent) and **resumable** (each page is cached under `data-detail/<slug>/`, so
reruns skip already-fetched pages for free).

## Files

| File | Role |
|---|---|
| `run-giants.mjs` | main driver — partition, paginate, cache, budget-halt, resume |
| `lib.mjs` | `flattenCompany` — raw API record → flat 46-field row |
| `merge-sector.mjs` | fold a finished sector into `combined-part*.json` |
| `credits-check.mjs` | verify session + print remaining daily credits |
| `build-all.py` | split the combined store into per-sector HTML viewers |
| `build-viewer.py` | single-file viewer generator called by `build-all.py` |
| `india-states.json`, `india-cities.json` | geo partition dimensions |

## Output

- `data-detail/<slug>/` — per-bucket page cache + raw records (full nested JSON).
- `combined-part*.json` — all merged sectors, one flat row per company-sector
  membership (chunked because a single JSON file exceeds V8's string limit past
  ~45k rows).
- `tracxn-viewers/` — `index.html` + one searchable/filterable HTML table per
  sector.
