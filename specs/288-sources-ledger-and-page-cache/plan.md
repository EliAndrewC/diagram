# Plan - feature 288, a sources-consulted ledger and a saved-page cache keyed by URL

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Measurement: [`research.md`](research.md) R1.

## Decisions

- **D1 - one module, `scripts/_sources.py`** (FR-001 - FR-012): the ledger, the cache, the fill pass, the one-time
  seed and import, and the command line the new make targets call. `_source_pages.py`, `_quote_verbatim.py`,
  `_check_bundle.py` and `reserve-prefix.py` load it the way they load each other (by path). The saved form of a
  page - one sentence to a line, a page over 20,000 characters in parts - moves from `_source_pages.py` into it,
  because the cache stores that form too; `_source_pages` keeps the names `wrapped`, `parts`, `PART`.
- **D2 - the ledger** (FR-001, FR-002). `<mirror>/.specify/sources-consulted.jsonl` (the mirror found as `make
  reserve` finds it: a clone's grandparent under `.clones/`), appended under `flock` on
  `<mirror>/.specify/sources-consulted.lock`, polled with a 30-second limit as `make reserve`'s lock is. One JSON
  object per line: `url` (normalized by a copy of `extract_norm.py`'s `norm`), `raw` (as given), `utc`, `feature`
  (`SPECIFY_FEATURE`, else the clone's `.specify/feature.json`; its number), `clone` (the clone directory's name),
  `session` (`L7R_PAGE_SESSION`, else the harness's `CLAUDE_CODE_SESSION_ID`), `questions` (a list), `outcome`.
  Outcomes accepted by `make source-outcome`: `cited:<key>` (a registry key's shape), `rejected:<why>` (a reason
  required), `nothing-found`, `unreadable`, `pending`. `unknown-outcome` is written only by the seed. A line is never
  rewritten: an outcome is a later line, and a reader reads them in order. `L7R_SOURCES_HOME` moves the ledger and
  the cache - the tests' seam, set for every tooling test by an autouse fixture so no test touches the host's files.
- **D3 - what is printed, and when** (FR-003). Before each URL `make source-pages` is about to fetch (one already
  saved in the same OUT is not fetched and not printed), a line `sources-consulted: <url> - read N time(s) before:`
  or `- no earlier read on the ledger`, then EVERY earlier line for that normalized URL, one per line: date, feature,
  clone, session (its first eight characters), the read count on a seeded line, the outcome, the question(s). After
  each page saved (state FETCHED) a `pending` line is appended with the optional `QUESTION=<page/NNN>`. A page that
  could not be saved gets no line (the spec's edge case). `make check-bundle KEY=<k> WHOLE=1 [QUESTION=<q>]` passes
  its question to the save and so prints and appends identically; the excerpt bundle passes `--no-ledger` (spec D1).
- **D4 - the lookup and the outcome** (FR-004, FR-006). `make source-outcome URL=<u> OUTCOME=<o> [QUESTION=<q>]`
  appends one line and echoes it; a malformed outcome exits 2 naming the five forms. `make sources-consulted URL=<u>`
  prints the URL's lines; `KEY=<regex>` prints every `cited:` line whose key the regex matches, each under its URL.
  The lookup runs the fill pass (D5) first, so what it prints is current.
- **D5 - a registry entry marks its URL cited** (FR-005). `make reserve KIND=registry KEY=<k> URL=<u>`: the stub is
  the entry's opening - `<h3 id="k"><code>k</code></h3>` and a `<p>(<u>)</p>` pointer line, the shape every entry
  has and `_check_bundle.url_of` reads - and `cited:<k>` is appended for `<u>` under the reserve's lock-free append
  (the ledger has its own lock). Without `URL=`, reserve is byte-for-byte as today. The FILL PASS: every registry
  entry of the clone whose pointer (`url_of`) the ledger does not already mark `cited:<its key>` gets that line;
  `make record` runs it after assembling (not under `CHECK=1`, which writes nothing), and so does the lookup. A
  second run appends nothing.
- **D6 - the cache's layout** (FR-008). `<mirror>/.specify/page-cache/<h[:2]>/<h>/`, `h` the SHA-256 of the
  normalized URL: `text.txt` (the page's visible text as `Pages` returned it), `page.txt` or `page.p1.txt` ...
  (its saved form in parts, as `make source-pages` writes it), `meta.json` (`url`, `norm`, `fetched`, `chars`,
  `exact`, `origin`). Each file is written to a temporary name and renamed, under the ledger's lock, `meta.json` last,
  so a reader never sees half an entry. OUT is filled by COPYING (writing the same saved form under OUT's own
  `NN-host` names), never by linking: the `Grep` tool's ripgrep skips symbolic links while it walks a directory, so a
  linked page would never be found by the grep that is the point of the saved page, and `/tmp` (where bundles and
  scratch OUT directories go) is on a different filesystem from the mirror, so a hard link cannot be made. OUT's file
  names and manifest shape are unchanged; a page taken from the cache says so in its manifest row's note ("from the
  page cache (fetched <date>; REFRESH=1 fetches it again)"), its state still FETCHED.
- **D7 - the age rule** (FR-009). A cached copy older than SEVEN DAYS is fetched again. The saving is nearly all in
  the first day (R1, observed 2026-09-29: 5,236 repeats within an hour of the read before, 174 more than a day
  after), so a longer age buys little; what an age costs is a page edited after it was saved - a sentence rewritten
  under a quote. A week spans a feature's write-then-check cycle and bounds how stale a verbatim check can be.
  `REFRESH=1` fetches at once: make exports a command-line variable to its recipes, so every script that fetches
  through the cache reads `REFRESH` from its environment, with no per-target flag.
- **D8 - one seam for every fetch** (FR-008, FR-010). `CachedPages` wraps `_quote_verbatim.Pages` - the fetcher all
  three scripts already use - and answers from the cache first, storing each FETCHED page it had to fetch. A failure
  (UNFETCHABLE, a PDF, undecodable) is never cached, so it is tried again next time. `make source-pages` uses it;
  `make check-bundle` uses it in every mode, because its page saves ARE `_source_pages.py` runs and its quote report
  IS a `_quote_verbatim.py` run; `make quote-verbatim` uses it with `exact` set, so an imported copy (D9), whose text
  is the saved form rather than the page as fetched, is not used for a character-for-character comparison - that page
  is fetched and the cache entry replaced with the exact text. `--offline` (the tests' seam) is left as it is.
- **D9 - the one-time seed and import** (FR-007, FR-012): `make sources-import`, idempotent. SEED: from
  `per_url.json`, one line per URL, feature and session (not per read: the top page's 32 reads print as 17 lines),
  carrying the first read's time, the read count, up to three of the questions asked of the page (200 characters
  each), `seed: reread-2026-09-29`, and `cited:<key>` where a registry entry of the clone carries the URL (its own
  pointer first, then any URL in it - the measurement's test of "in a registry", R1), else `unknown-outcome`. A ledger
  already holding the seed is not seeded again. IMPORT: every `MANIFEST.txt` under `/tmp/l7r-check`; each FETCHED row
  whose file (or all its parts) is on disk and is not an EXCERPT (feature 250 D19: an excerpt is not the page); per
  normalized URL the newest such save; stored with `exact: false`, `origin: import:<dir>`, `fetched` = the file's
  modification time; a URL already in the cache is left alone. The counts of both go into research.md R2.
- **D10 - the agent files** (FR-011). One sentence each, in the step that already says to read saved pages before
  fetching: `source-reader` step 0 and `quote-check` procedure step 2 - the bundle's saved text comes from the
  host's page cache, so read it before any `WebFetch`, and fetch only a page the bundle does not carry (or one its
  manifest marks unreachable). Frontmatter untouched.
- **D11 - the process text** (FR-013). `research/CLAUDE.md` (its paragraph on `make source-pages`) and
  `page-session-rules.md` (its Research list): check the ledger (source-pages prints it; `make sources-consulted`
  looks); record every page's outcome with `make source-outcome`; a page already `rejected` for the same question is
  not re-read without a reason. The root CLAUDE.md's "Reading and checking" bullet gains a clause naming the ledger,
  and `test_page_session_rules.py`'s phrase list gains `make source-outcome`, so the slim file cannot lose it.
- **D12 - the Makefile** (FR-014, FR-015). New targets `source-outcome`, `sources-consulted`, `sources-import`, each
  with `# GUARD_EDIT_OK: feature 288 - a new operation ...; no guard changes`. Optional new variables on existing
  targets: `QUESTION=` on `source-pages` and `check-bundle`, `URL=` on `reserve`; `make record` gains the fill pass.
  Every existing variable and output stays. `.gitignore` gains `.specify/sources-consulted.jsonl` and
  `.specify/page-cache/` (the lock is covered by `*.lock`).
- **D13 - tests** (FR-015, SC-001 - SC-008). `tests/tooling/test_sources.py` (the ledger, the lock, normalization,
  the outcome forms, the lookup, the fill pass, the cache's put/get/age/exact, `CachedPages`, the seed and the import
  on fixtures, the command line); additions to `test_source_pages.py` (the print before the fetch, the `pending`
  line, the second save with no fetch, the cached note, `--no-ledger`), `test_check_bundle.py` (WHOLE=1 prints and
  appends with its question; the excerpt bundle appends nothing), `test_quote_verbatim.py` (a cached exact page is
  not fetched; an imported one is), `test_reserve_prefix.py` (URL= writes the stub and the line; without it, as
  before). No network anywhere: the fake opener the existing tests use. Every line of `_sources.py` and of the
  changed code is covered, checked with `make cov-file`.

## Constitution check

- XII: a tooling feature; it states nothing on a map. What it records (which pages were read, and with what result)
  serves the research doctrine's search pass; nothing in the record changes.
- XIII: the gate before the push; baseline in a detached worktree if anything fails.
- XVI: both fixes as asked, every piece the brief names; the one exclusion (spec D1) was ruled on at spec round 1.
- No guard (the GM's measurement, R1).
- Indexing: no overlap check.
