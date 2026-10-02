# Implementation Plan: Uncited-source catalog

**Feature**: `312-uncited-source-catalog` | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)

## Summary

Three pieces of tooling and two passes of judgment. The tooling: the blocked-domain and banned-citation lists with one
decision function used by every fetch route, every store and the record build (FR-001..FR-004); the attempts log and the
not-kept list, committed and union-merged, read before every fetch (FR-010, FR-015..FR-018); the "Uncited sources" part
of the built record and its refusals (FR-012..FR-014), and FR-020's push-and-gate check. The judgment: the `source-filter` agent, calibrated, over
the uncited set (FR-006..FR-011); and the write-ups of the kept pages, each checked by `source-applicability` (FR-012).
Then the work that waits on others: the footnotes of every source less than wholly readable confirmed in its readable part
or removed, once feature 313's access tags exist (FR-019), and
the high-risk sources confirmed once the GM has downloaded them (FR-021).

## Technical Context

- **Language**: Python 3.14 (scripts and the record builder), bash (the hook), the existing Playwright fetcher
  (`scripts/_archive.py:Browser`) for the pages with no saved text.
- **Engine half** (100% coverage owed): `l7r/diagram/interactive/record/blocked.py` (the two lists, `blocked(url)`,
  `banned(url)`), and the build's new refusals and the Uncited part in `store.py`, `site.py` and `source_tags.py`. The
  tooling imports `blocked.py`, so a fetch route and the build cannot disagree on what is blocked (the pattern feature 309
  used for the cited-URL census).
- **Tooling half** (tests in `tests/tooling/`, fake fetchers, no live fetch): `scripts/_uncited.py` (the set, the rule
  verdicts, the fetch, the filter bundles, applying verdicts, the coverage report), `scripts/_attempts.py` (seed, append,
  show), `scripts/blocked-fetch-hooks.sh` with `test-blocked-fetch-hooks.sh`, and small changes to `_sources.py`,
  `_source_pages.py`, `_archive.py`, `_archive_ops.py`, `reserve-prefix.py`, `_record_units.py`, `_check_bundle.py`.
- **Agents**: `.claude/agents/source-filter.md` (new; Opus, effort medium, `omitClaudeMd: true`, tools Read and Write - it
  writes its verdicts as JSON lines into the bundle, so its reply is one count line); `source-applicability` unchanged in
  tier, its contract told that an uncited entry has no `Used for:` line.
- **Data files** (all under `.claude/skills/diagram/research/`): `blocked-domains.json`, `banned-citations.json`,
  `not-kept.jsonl`, `source-attempts.jsonl`, `sources/040-uncited-works/`. The two `.jsonl` files are `merge=union` in
  `.gitattributes` (the feature-271 precedent for append-only files every clone writes).
- **Performance**: no generator change, no perf bookends owed. The build gains a set lookup per URL.

## Decisions

- **D1 - One decision function, imported everywhere.** `blocked.py` reads the two JSON files once per process. A domain
  matches itself and every subdomain (`grokipedia.com`, `www.grokipedia.com`), never a suffix inside another name
  (`notgrokipedia.com`). A banned pattern is a regular expression over the normalized URL (`_sources.norm`). An entry
  with no `approved` (date and words) is refused by the loader, so a list cannot grow without the GM.
- **D2 - The fetch routes.** In Python: `_sources.CachedPages.get`, `_sources.put`, `_sources.append` (the ledger),
  `_archive.fetch`, `_archive.archive_url` and the GM-copy match raise `Blocked` with the list's reason; `make
  quote-verbatim` and `make reserve ... URL=` reach these. Outside Python: the hook, matched on `WebFetch` and `Bash`.
  WebFetch: its `url`. Bash: a URL on a blocked domain as an argument of `curl`, `wget`, `lynx`, `w3m`, `http`/`https`
  (httpie), `python3 -m urllib`, or a `make` target that fetches (`source-pages`, `archive*`, `reserve`, `source-outcome`,
  `quote-verbatim`) - an invocation, never a mention (a grep for the word passes; the guard doctrine).
- **D3 - The build's refusals** gathered with the rest (feature 305 FR-010): a registry entry or footnote linking a blocked
  or banned URL; an uncited entry linking the GM's notes (the canon section's URLs); a footnote citing a key whose entry
  is in `040-uncited-works/` (naming `make cite-uncited KEY=<k>`). FR-020 is a push and gate check, not the build's: a
  footnote citing a source FR-019 names (313's report JSON: `paywalled`, `gm-partial`, `never-read`, or a GM mark of
  paywalled or not found) with no confirmation line in `research/partial-confirmations.jsonl` is refused.
- **D4 - The uncited set and the rule verdicts.** `_uncited.py set` = `consulted_urls` minus URLs with a verdict line,
  minus URLs any registry entry carries (respellings resolved by `norm` and by the cleaned URL), plus manifest rows with no
  key, no note and no footnote (the pre-hold captures). Re-runnable: a page read and never cited after this feature is in
  the next run's set. The `no-substance` rule uses `prep.md`'s two regexes. A page with no saved text is fetched through
  `CachedPages` with the archive's browser, then an archived snapshot (`_archive.wayback`); a page none of them reads is
  `unreadable` with an access state from the failure: 401/402/a login wall -> `paywalled`, 403/406/429 -> `bot-refused`,
  timeout/5xx/TLS -> `down`, 404/410 -> `gone` (313's vocabulary).
- **D5 - The filter's input.** A bundle of up to 40 pages in `/tmp/l7r-check/312-filter-<n>/`: `MANIFEST.md` holding, per
  page, its id, URL, title and the first 3,000 characters of saved text (`_source_pages.excerpt` with no quotes, which keeps
  the front matter), and a note when the page is longer. 40 x 3,000 characters is about 40,000 tokens, under a quarter of
  the agent's window. The agent writes `verdicts.jsonl` beside it: `{"id", "verdict": "KEEP"|"NOT-KEPT", "reasons": [...],
  "note", "propose_block": "<domain>"?}`. `_uncited.py apply` refuses a bundle whose verdicts are missing an id, carry an
  unknown reason, or a NOT-KEPT with no reason.
- **D6 - Calibration** (FR-009, `research.md` R1). A control bundle mixes 40 POSITIVES (cited pages with saved text, a
  seeded random sample of the archive) and 40 NEGATIVES (uncited pages this session labels junk, each with its reason, in
  `measurement/negatives.json`), shuffled, ids opaque; three runs. Scored by `_uncited.py score`; the runs are R2.
- **D7 - Verdicts are written** by `_uncited.py apply`: a NOT-KEPT becomes a `not-kept.jsonl` line; a KEEP becomes a line of
  `specs/312-uncited-source-catalog/kept.jsonl` (the work list until its write-up exists, after which the registry entry is
  the record). A pre-hold capture judged NOT-KEPT has its manifest row deleted (`git rm`); its copy stays in the archive's
  history.
- **D8 - Archiving the kept** (FR-011): `consulted_urls` gains a `kept_only` filter, and `make archive-sources
  CONSULTED=1` archives the URLs of `kept.jsonl` and of `040-uncited-works/` only.
- **D9 - Write-ups.** `reserve-prefix.py` gains `KIND=uncited`, writing into `040-uncited-works/` with the registry's one
  number sequence (both directories are read for the highest prefix, so a moved entry keeps its number). Drafts are written
  by `sonnet` agents in batches of 15 kept pages, from the same excerpts plus the entry form, the tag vocabulary and three
  model entries, into the bundle; `_uncited.py install DIR=` reserves each key (refusing a key already in the registry and
  appending `-2`), writes the entry, and records `cited` nothing. Each entry is then owed `source-applicability`
  (`_record_units.py` learns the new directory), checked in bundles of up to 10 keys (`make check-bundle KEY="a b ..."`).
- **D10 - The Uncited part.** `store.py` reads `040-uncited-works/` as a fourth registry part; the Sources page lists it
  after the works cited, grouped by `source-sections.json` with the canon section skipped, under its own heading "Uncited
  sources"; the nav tree gains it. The single page (`all.html`) carries it too.
- **D11 - `make cite-uncited KEY=<k>`** moves an entry to `010-works-cited/` (`git mv`) and appends a `Used for:` line
  placeholder the build already refuses until it names a section.
- **D12 - Attempts.** `_attempts.py seed` maps each ledger row naming a question (old ids through `moved-303.json`; an id
  it cannot map is kept as written, prefixed `old:`) to a line `{url, key, question, sought, outcome, date, feature}`, with
  `sought` = `unknown - recorded before feature 312`. `make source-pages` requires `Q=` and `SOUGHT=`, prints the URL's
  attempts and verdict before fetching, and appends `pending` attempts; `make source-outcome` appends the outcome line.
  The WebFetch hook adds the same print as context and appends an attempt (its `prompt` as what was sought); the Bash
  side of the hook appends one for a `curl`/`wget`-style fetch (the command as what was sought). `make archive` and `make
  archive-find` append one. `make attempts URL=|KEY=|Q=` prints them.
- **D13 - FR-005 inventory** is a table in `docs/research-doctrine.md` - rule, where it is stated, what enforces it - with a
  test that every script, hook or agent file the table names exists; a mechanical rule found with no tool gets one here.
- **D14 - FR-019 removal** runs after feature 313 lands: the keys FR-019 names, from 313's report JSON; for each footnote
  citing one, `make quote-verbatim` and `quote-check` against the readable part (the open page, an open abstract, the
  GM's partial copy); a confirmed footnote gets a line in `research/partial-confirmations.jsonl` (key, note id, where the
  passage was read, the date); an unconfirmed one becomes an absence note, or is dropped where another note carries the
  claim. A key left with no footnote leaves the works cited, gets 313's hand-recorded state and a `not-kept.jsonl` line.
  Every changed question owes its record checks.
- **D15 - FR-021** runs when the GM reports downloads ingested (313's `make downloads-ingest`): per key, `make
  check-bundle KEY=` and `source-reader`; then `quote-check` on its notes; corrections applied with `make apply-edits`.

## Constitution Check

- XII (research): this feature changes no map; its rules are recorded beside the code and in `research.md`.
- XIII (no regressions): the baseline taken in a detached worktree before the engine edits.
- XVI (do the literal thing): FR-019's abstract clause and FR-008's widened threshold put to `spec-fidelity`.
- The 1,000-line bar: `site.py` is 525 lines and gains about 40; `_uncited.py` and `_attempts.py` are new and small.
