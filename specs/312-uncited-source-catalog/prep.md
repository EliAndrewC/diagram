# Prep notes for the implementing session (2026-10-02, written before the feature starts)

Written by the session that landed feature 309, at the GM's request: *"do all the prep work now ... but don't actually
start on the feature"*. Nothing here is a decision the GM has not made; the GM's rulings are in `request.md`.

## What exists to build on (from feature 309 and 288)

- The archive: private `EliAndrewC/diagram-research`, the host's one working copy at `<mirror>/.specify/source-archive/`;
  the manifest at `.claude/skills/diagram/research/archive/<id[:2]>/<id>.json`; the layout and the capture are
  `specs/309-source-archive/plan.md` (D1-D16).
- The uncited list: `scripts/_archive_ops.py:consulted_urls` (the ledger's and the page cache's URLs with no manifest row).
  The run that archives them, `make archive-sources CONSULTED=1`, is HELD and unrun (309 Amendment 2): 312 decides what
  it archives, so the filter goes BEFORE it.
- Archiving at citation: `scripts/_sources.py:archive_reads`, called by `make source-outcome OUTCOME=cited:<key>`;
  `make reserve KIND=registry ... URL=` archives too. `make source-pages` archives nothing.
- The sources-consulted ledger: `<mirror>/.specify/sources-consulted.jsonl`, one line per read
  (`url`, `raw`, `utc`, `feature`, `clone`, `session`, `questions`, `outcome`); `scripts/_sources.py` reads and writes it.
- The page cache (the filter's cheap input): `<mirror>/.specify/page-cache/<h2>/<h>/`, read with
  `_sources.cached(where, url, max_age_days=10_000)`.
- Source tags and sections for the write-ups: `research/source-tags.json`, `research/source-sections.json` (feature 305).
  The new "Uncited sources" part follows the same sections (`request.md`); `works-canon` (the GM's L7R notes) never
  appears in it.

## The uncited pages, measured (observed 2026-10-02, `_archive_ops.consulted_urls` and the ledger)

- **2,843** uncited URLs with no manifest row, plus the 3 captured before the hold (manifest rows with no key and no note).
- **1,200** have saved text in the page cache (median 2,415 characters, 90th percentile 9,394, 103 under 500; 9.5 MB in
  all). The other **1,643** need a fetch for the filter to read them. 309's spec counted 3,072 pages with saved text in all;
  most of those are cited.
- On the ledger: **2,787** name the question they were read for; outcomes are thin - 2,646 `unknown-outcome` (the
  feature-288 import), 133 `pending`, 74 `nothing-found`, 60 `rejected` with a reason, 57 `unreadable`, 33 not on the
  ledger at all (page-cache only). Old ids in `questions` predate feature 303's flat stems (`vegetation/150`);
  `research/moved-303.json` maps them.
- **Mechanically "no substance"** (a rule, no agent): **107** search-result pages (DuckDuckGo, Baidu `s?wd=`,
  `archive.org/advancedsearch`, `?q=` and the like) and **62** API or raw URLs (`/api/`, `action=raw`, `output=json`).
  The regexes used: `duckduckgo|google\.[a-z.]+/search|bing\.com/search|baidu\.com/s\?|search\?|/search/|advancedsearch|[?&](q|query|keyword|kw|wd)=|/results?\b`
  and `/api/|action=raw|output=json|\.json\b`. The two sets may overlap; dedupe before counting.
- Hosts: 937 in all, 696 with one URL. Most: ja.wikipedia 399, kotobank 225, zh.wikipedia 201, J-STAGE 106,
  en.wikipedia 90, zh.wikisource 89, adeac 48, baike.baidu 45, online.bunka.go.jp 41, cir.nii.ac.jp 35, ctext 31.
- **8 URLs the ledger marks `cited:<key>` have no manifest row**: the entry cites a different spelling of the URL (one has
  `):` stuck to its end, one is `action=raw`). Check each is covered by its key's own URL before the filter treats it
  as uncited: ndl-crd-shakkogyu, kashima-kainyo-1987, minzoku-kinkyu-chosa-jawiki, kochi-hantei-jstage, daozuofang,
  qimin-yaoshu-zhongzhu, daqing-luli-yejin, guangdong-xinyu-22.

## Grokipedia and the blocked-domain category

- Today the ban is a written rule only (`docs/research-doctrine.md:30`, the registry's `_front.html`); three citations
  were dropped by hand in feature 143 (`4410-zhengyi-householder-priests`, `4770-jokamachi-zoning`,
  `6610-loess-plateau-enwiki` still mention it in comments). No tooling refuses it.
- No Grokipedia URL is on the ledger or in the archive (grep, 2026-10-02), so the block starts from a clean slate.
- The fetch routes the block must cover: `make source-pages`, `make archive` / `archive-sources`, `make reserve ... URL=`,
  `make source-outcome`, `make quote-verbatim`, and the agents' own WebFetch (a PreToolUse hook on WebFetch is the only
  way to reach those); the record build (`make record CHECK=1`) refuses a citation of one.

## A pitfall from 309

`specs/309-source-archive/measurement/sc002.py` treated every 「...」 run in a registry entry as a quoted passage, and one
of them was the citation's TITLE (`jasaga-hiatari`), which a page's body text does not carry. A write-up check that
looks for an entry's quotes in the archived copy must skip the citation line.

## The 309 leftover done now: the thin partial copies retried (2026-10-02)

The 21 cited URLs archived `partial` with under 200 characters of text were captured again (`make archive URL=`, one at
a time). **6 improved** to an earlier public snapshot: PMC6459177, PMC7898781, PMC7538448, whc.unesco.org/en/list/1002,
pfaf.org Diospyros kaki, l5r.fandom Shinden (TCG). **15 still refuse** an automated fetch (HTTP 403, one 406, one 429):
publisher pages (doi.org x4, ScienceDirect x2, SAGE, PMC12935246, PMC7048742), museumcollection.tokyo, Baidu Baike,
Zhihu, l5r.fandom Seido, the Soka repository PDF, and a Wayback copy of an IRRI page. Five of the 15 are already on the
GM's `TO-DOWNLOAD.md` (by URL); the other ten are not. Coverage after the retry: 2,017 archived, 25 earlier snapshot, 16
GM copy, 36 partial, 14 unreachable (`make archive-sources REPORT=1`).
