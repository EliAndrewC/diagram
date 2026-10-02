# Implementation Plan: Source archive

**Feature**: `309-source-archive` | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)

## Summary

Archive every URL the record cites (registry entries and direct footnote links, FR-001) into the private repository
`EliAndrewC/diagram-research`: the served bytes, the whole page as one offline file, the text and a capture record. Every file of the GM's `academic-sources/` is archived (Amendment 1: the inbox), each matched to the key it copies. One host-wide
working copy of the archive repository, pushed straight to GitHub under a host-wide lock. A per-URL manifest committed here
records every outcome; the record build refuses a cited URL with none, and each source page shows its archived-copy link. A
one-time backfill archives what is already cited; `make reserve ... URL=` archives what is cited from now on.

## Technical Context

- **Language**: Python 3.14, Playwright with its pinned Chromium (already installed for the browser tests), `pdftotext`
  (poppler, installed) for a PDF's text.
- **The ENGINE half** - `l7r/diagram/interactive/record/archive.py` (100% coverage owed): the cited-URL census (every
  URL in a registry entry, its HTML comments included - 23 entries record there the page actually read, the `_pdf`
  behind a J-STAGE article page or the PMC copy behind a DOI, and one entry's only URL is in a comment (plan review
  2026-10-02); and every URL a footnote in `questions/*.notes.html` links, its comments excluded - there they are search
  trails and pages read and not cited), a URL's manifest id, the manifest reader, a registry entry's archived-copy line, and the refusals for a cited URL with no row. `site.py`
  calls it at two points (`Build.entry_html`, `Build.run`); `site.py` is 513 lines and gains ~10.
- **The TOOLING half** - `scripts/_archive.py` (tested in `tests/tooling/test_archive.py` with saved fixtures and a fake
  fetcher that returns them - never a live fetch in a test): the capture, the GM copies, the working copy, the lock and push,
  the backfill and its report. It imports the engine module for the census and the ids, so the build and the archiver agree
  on what is cited by construction. `scripts/reserve-prefix.py --url` calls it after writing the stub.
- **Makefile**: `make archive URL=<u> [KEY=<k>]` (one URL, now), `make archive-sources` (the backfill, resumable;
  `REPORT=1` prints the coverage table and fetches nothing).
- **The manifest**: `.claude/skills/diagram/research/archive/<id[:2]>/<id>.json` (D11), one file per archived URL - every cited URL and any page archived at citation (FR-014) - (`id` = the first 12 hex of
  the SHA-256 of the URL as cited, entity-unescaped and without its fragment): `{url, final_url, keys, notes, outcome, path,
  captured, first, sha256, revision, reason, gm_copies}`. Beside it `gm-copies.json`, the FR-012 match (below).
- **The archive layout** (in diagram-research, D11): `<id[:2]>/<id>/<UTC capture time>/` holding `served.<ext>`, `page.mhtml`
  (a web page), `text.txt` and `capture.json` (which names the keys and notes that cite it); `gm-copies/<file>` for the GM's
  files, a PDF's text beside it as `<file>.txt`; a URL several entries cite is archived once, and every row names it. A file past
  95 MB is written as `<name>.part1..N` with the whole file's SHA-256 in `capture.json`.
- **The working copy**: `<mirror>/.specify/source-archive/` (beside `page-cache/`; one `.gitignore` line), lock
  `<mirror>/.specify/source-archive.lock` (`fcntl`, the `_sources.locked` pattern). Every clone's session writes to the one
  copy (the GM: no per-clone copy). Pushed over HTTPS with the PAT from `l7r.diagram.ci.config.load_secrets(...).github_pat`,
  handed to git as `GIT_CONFIG_*` environment entries (`http.extraHeader`), so the token is never on a command line, in a
  file or in a log (FR-011).
- **Performance**: no generator change; no perf bookends owed. The backfill, measured on a 40-URL random sample
  (`measurement/`, observed 2026-10-02, method: `measurement/samp.py`): 37 of 40 captured, 4.7 s a URL mean, MHTML median
  761 KB, mean 772 KB, max 2.5 MB. Extrapolated to ~2,110 URLs: ~1.6 GB of MHTML (~2 GB with the served bytes and text),
  ~2.8 h sequential; run as 4 worker processes, a host's URLs always in one worker, so ~1 h.

## The GM's downloaded copies (FR-012), measured 2026-10-02

Method: every top-level entry of `/host-l7r-repo/academic-sources/` read at its head (`pdftotext -l 1`, or the text) and
matched by title, DOI or URL against the registry and the question notes (a sonnet extraction agent, its table checked and
committed as `research/archive/gm-copies.json`).

- **42 entries**: 2 are the GM's lists (`TO-DOWNLOAD.md`, `for-the-gm-fetch-list.md`), not sources; 38 files and 2 `_files`
  folders (each belongs with its saved `.html` page) are the 40 matched.
- **33 match a cited source** (31 files and the 2 folders), over 30 keys (counted 2026-10-02 from the committed table: three keys hold two entries each - `yuan-liu-2009` two text files, each `wagner-*` key a saved page and its folder). Only 8 registry entries mention `academic-sources`
  at all, so a marker-based rule would have missed most (spec-fidelity round 2).
- **7 copy no cited source** (keys `[]`), archived all the same under Amendment 1 (FR-013 - before it they were listed and not archived): `FactorsOfSpatialDistribution.txt` (Kim et al. 2018),
  `FenshuiForests.txt` (Chen, Coggins, Minor and Zhang), `asie_0766-1177_2011_num_20_1_1377.pdf` (Goossaert 2011 - named in
  question 0228's notes, no registry entry), `ForestSurroundingTheHouse.txt` and its three page images `-315/-316/-317.jpg`.

## Decisions

- **D1 - The whole page is an MHTML snapshot taken by Chromium** (`Page.captureSnapshot`): one file holding the page as
  rendered - script-built text included - with its images, stylesheets and fonts (RFC 2557); Chrome, Edge and every Chromium
  browser open it offline. Priced alternatives: SingleFile CLI (self-contained HTML, any browser) fails on this host's Node
  (`CloseEvent is not defined`, observed 2026-10-02) and would add an npm dependency that moves; `monolith` is not packaged
  here and runs no scripts, so a script-built page would archive empty. Cost: Firefox opens an MHTML only with an add-on.
  Chosen by the session.
- **D2 - Order for every cited URL** - the live fetch always first, then by how it failed (D10):
  - a DEAD page (spec US1 scenario 3): the newest Wayback snapshot (the availability API, then the raw `id_` capture and
    its MHTML), outcome `archived-earlier-snapshot`; else the GM's copy, `archived-gm-copy`; else `unreachable` with the
    reason, the page-cache text stored as the fallback copy where the cache holds one;
  - a REFUSED page or one that rendered no text (the spec's Edge Cases): the GM's copy first, `archived-gm-copy` (with
    whatever the site served beside it); else the Wayback snapshot; else `partial` - what the site served, with the
    page-cache text beside it.
  INDEPENDENTLY of that order, every file `gm-copies.json` matches to a key is copied to `gm-copies/` whatever the live
  fetch's outcome (FR-012: in addition, never in place). A source page's archived line lists every copy of every URL the
  entry cites (FR-010; 21 entries cite several).
- **D3 - One manifest file per URL**, so concurrent sessions never conflict; about 2,100 small files for the cited URLs, at most ~4,900 if feature 312 keeps every page read (the ledger's 4,903 distinct URLs, observed 2026-10-02), sharded by D11.
- **D4 - Capture time is the version key**: a later capture is a new directory (FR-009); the row points at the latest and
  keeps the first in `first`.
- **D5 - At reserve time a failure never blocks** (FR-006): the outcome is written as it is; a push that fails writes
  `pending-upload`, which the next `make archive-sources` sends. The build counts `pending-upload` as covered for 7 days from
  the capture and then refuses (the same week as the page cache's age rule, `_sources.MAX_AGE_DAYS`).
- **D6 - A footnote's direct URL** is any `href="http..."` in `research/questions/*.notes.html`; the build refuses one with no
  row, naming `make archive URL=<u>`.
- **D7 - Wikipedia revision**: read from the served page's `wgRevisionId` (MediaWiki's page config), stored in `revision`.
- **D8 - Politeness**: one request at a time per host, 1 s between them, a browser user agent; a 429 or 503 waits 30 s and
  retries once.
- **D9 - The backfill pushes every 200 MB** of new captures, so no push nears GitHub's 2 GB push limit and a stopped run
  loses at most one unpushed batch (it stays in the working copy; the next run pushes it).
- **D10 - How a live fetch failed**: REFUSED is a 401, 403, 406, 429 or 451 (the site is there and turns an automated
  reader away), or a web page that rendered no text; DEAD is any other 4xx/5xx, a network error, an empty body, or a
  redirect that lands on the site's root from a deeper path.

## Constitution Check

- I, II: N/A - the source pages gain one line in the existing site; no new page.
- III, IV, V, VII, VIII, IX: N/A - no pool content, no SOURCE block, no in-world writing, no setting detail.
- VI: PASS - every task runs `make quick`; the feature ends on `make done`; SC-002's sample is opened and grepped by a script
  before the closing task is ticked.
- X: PASS - ruff, ruff format, pyrefly; red-green tests; `record/archive.py` at 100%; fixtures and a fake fetcher, not a
  transport mock; no file past 1,000 lines - the housekeeping and lookups went to `_archive_ops.py` when `_archive.py` reached ~770 (D16).
- XII: N/A for map assertions - the feature draws and states nothing about the world; its decisions are in the spec's table
  and here.
- XIII: PASS - the record build gains a refusal; baseline `make record CHECK=1` builds cleanly on HEAD (taken before the
  change); after the backfill it must still build cleanly.

## Project Structure

```text
specs/309-source-archive/   spec.md plan.md tasks.md request.md measurement/
scripts/_archive.py          capture, GM copies, working copy, lock, push, backfill, report
scripts/reserve-prefix.py    --url: archive after the stub
.claude/skills/diagram/l7r/diagram/interactive/record/archive.py   census, ids, manifest, entry line, refusals
.claude/skills/diagram/l7r/diagram/interactive/record/site.py      two call sites
.claude/skills/diagram/research/archive/<id[:2]>/<id>.json, gm-copies.json  the manifest
scripts/_archive_ops.py      the inbox, every page read (urls, consulted), archive-find, the one-time relayout
scripts/_sources.py, scripts/_source_pages.py   archive_reads: a page read is handed to the archiver
.claude/skills/diagram/tests/tooling/test_archive_ops.py
CLAUDE.md, docs/research-record-rules.md, container-scripts/page-session-rules.md, .claude/agents/source-reader.md, quote-check.md   the archive looked in first
.claude/skills/diagram/tests/tooling/test_archive.py
.claude/skills/diagram/tests/interactive/test_record_archive.py
.claude/skills/diagram/Makefile                                     archive, archive-sources
.claude/skills/diagram/research/CLAUDE.md, docs/research-doctrine.md   one paragraph each: a cited page is archived
```

## Amendment 1 (2026-10-02: the inbox, every page read, the lookup, the sharded layout)

- **D11 - Sharded by the URL id's first two hex digits** (FR-003, the GM's question): captures `<id[:2]>/<id>/<time>/`, rows
  `research/archive/<id[:2]>/<id>.json` (`record/archive.py:ROW_GLOB`, `_archive.py:capture_base`); one level of 256 holds
  about 19 each at the ledger's 4,903 URLs (derived), under 300 each to about 76,800 (derived). The GM's copies stay flat in
  `gm-copies/` (40 entries, T12). A one-time `relayout` moved the first 1,803 rows and their captures by `git mv`
  (observed 2026-10-02: 1,803 rows moved; the top level went from 1,775 entries to 257).
- **D12 - The inbox** (FR-013): every entry of `academic-sources/` but `TO-DOWNLOAD.md` and `for-the-gm-fetch-list.md` is
  copied to `gm-copies/<name>`, pushed, and deleted only where `git ls-tree origin/main -- <path>` lists it after the
  push; a failed push deletes nothing. A NEW file - not yet in `gm-copies.json` - is not processed until the session matches
  it: `make archive-inbox` lists it WAITING with the instruction, the session reads its first page (as T12 did for all 40),
  finds the source it copies (`TO-DOWNLOAD.md` names the key each download was asked for), and runs `make archive-inbox
  MATCH='<file>=<key>'`, or `NONE='<file>'` for one judged to copy no cited source (`keys: []`, archived all the same). A
  waiting file stays in the inbox, so the directory still shows it as unprocessed (plan review, Amendment 1). The table records `archived` for every processed file, which is how a copy
  is found once its file is gone (`place_gm`).
- **D13 - Archived at citation** (FR-014, Amendment 2): `_sources.archive_reads` runs `_archive_ops.py urls` from
  `make source-outcome` when the outcome is `cited:<key>`; `make reserve ... URL=` already archives. `make source-pages`
  records its reads and archives nothing. A URL with a row is not captured again (`unarchived`, by `_sources.norm`).
  `L7R_ARCHIVE_READS=0` is the test suite's seam (`tests/tooling/conftest.py`), as `L7R_SOURCES_HOME` is. The `consulted`
  operation (`make archive-sources CONSULTED=1`) stays, unrun: feature 312 archives the uncited pages its filter keeps, and
  the three it captured before the GM held it (2026-10-02) wait for that filter.
- **D14 - The lookup** (FR-015): `make archive-find` reads the rows (by `_sources.norm` of the URL, or a key) and greps the
  archived texts (`text.txt`, a GM PDF's `.txt`) for every term; exit 1 with nothing held, saying to go to the web.
- **D15 - Found while running the backfill, fixed in the work** (constitution XIV): a render that failed under load is tried
  once more, and a page that still will not render keeps its served HTML and text as `partial` (5 of the first ~1,150 had
  failed and rendered at once alone, observed 2026-10-02); each lane restarts its browser every 25 URLs (two lanes held
  1.8 GB at the host's low-memory warning, observed 2026-10-02) and the backfill ran at one lane while other sessions
  needed the memory; `gm_copies` raises on a malformed table instead of returning none (an edit had broken the table and the
  first ~1,450 rows were written without the GM's copies; `make archive-sources GM=1` copied them in after - 18 rows).
- **D16 - `_archive_ops.py`** holds the inbox, the reads, the lookup and the relayout, so `_archive.py` stays the capture.
