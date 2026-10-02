# Implementation Plan: Source archive

**Feature**: `309-source-archive` | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)

## Summary

Archive every URL the record cites (registry entries and direct footnote links) into the private repository
`EliAndrewC/diagram-research`: the served bytes, the whole page as one self-contained offline file, the text and a capture
record. One host-wide working copy of that repository, pushed straight to GitHub under a host-wide lock. A per-URL manifest
committed here records every outcome; the record build refuses a cited URL with none, and each source page shows its
archived-copy link. A one-time backfill archives what is already cited; `make reserve ... URL=` archives what is cited from
now on.

## Technical Context

- **Language**: Python 3.14 (the project's), Playwright with its pinned Chromium (already installed for the browser tests),
  `pdftotext` (poppler, installed) for a PDF's text.
- **Where the code goes**:
  - `scripts/_archive.py` - tooling beside `_sources.py` (feature 288): the cited-URL census, the capture, the archive
    working copy, the lock and push, the backfill and its report. Tested in `tests/tooling/test_archive.py` with saved
    fixtures (a served page, an MHTML, a PDF, a Wayback availability reply) - never a live fetch in a test.
  - `l7r/diagram/interactive/record/archive.py` - the ENGINE half (100% coverage owed): reads the manifest; gives a registry
    entry's archived-copy line; lists cited URLs with no outcome as build refusals.
  - `site.py:Build.entry_html` appends the archived-copy line; `Build.run` adds the refusals (`site.py` is 513 lines; the
    addition is ~10).
  - `scripts/reserve-prefix.py --url` calls the capture after the stub is written.
  - Makefile: `make archive URL=<u>` (one URL, now), `make archive-sources` (the backfill, resumable; `REPORT=1` prints the
    coverage table without fetching).
- **The manifest**: `.claude/skills/diagram/research/archive/<sha12>.json`, one file per cited URL (sha12 = the first 12 hex
  of SHA-256 of `_sources.norm(url)`): `{url, final_url, keys, notes, outcome, path, captured, sha256, revision, reason}`.
  One file per URL so two sessions archiving different URLs never touch the same file (no merge conflicts, D3).
- **The archive layout** (in diagram-research): `<key>/<sha12>/<UTC capture time>/` holding `served.<ext>`, `page.mhtml` (web
  pages), `text.txt`, `capture.json`; a URL cited only by a footnote goes under `notes/<sha12>/...`; a URL several entries
  cite is archived once, under the first key, and every key's manifest row points at it. A file past 95 MB is written as
  `served.<ext>.part1..N` with the whole file's SHA-256 in `capture.json`.
- **The working copy**: `<mirror>/.specify/source-archive/` (beside `page-cache/`; gitignored in the mirror - one line added
  to `.gitignore`), lock `<mirror>/.specify/source-archive.lock` (`fcntl`, the `_sources.locked` pattern). Every clone's
  session writes to the one copy (the GM: no per-clone copy). Push over HTTPS with the PAT from
  `l7r.diagram.ci.config.load_secrets(...).github_pat`, passed to git as `GIT_CONFIG_*` environment entries (an
  `http.extraHeader`), so the token is never on a command line, in a file or in a log (FR-011).
- **Performance**: no generator change; no perf bookends owed. The backfill: measured on a 40-URL random sample
  (`measurement/`, observed 2026-10-02, method: `measurement/samp.py`) - 37 of 40 captured, 4.7 s a URL mean, MHTML median
  761 KB, mean 772 KB, max 2.5 MB. Extrapolated to ~2,110 URLs: ~1.6 GB of MHTML (+ served bytes and text, ~2 GB), ~2.8 h
  sequential; run with up to 4 browser pages at once, never two on one host at a time, so ~1 h.

## Decisions

- **D1 - The whole page is an MHTML snapshot taken by Chromium** (`Page.captureSnapshot`). It is one file holding the page as
  rendered - script-built text included - with its images, stylesheets and fonts (RFC 2557); Chrome, Edge and every Chromium
  browser open it offline. Priced alternatives: SingleFile CLI (self-contained HTML, opens in any browser) fails on this
  host's Node (`CloseEvent is not defined`, observed 2026-10-02) and would add an npm dependency that moves; `monolith` is
  not packaged here and runs no scripts, so a script-built page (kotobank, several tourism sites) would archive empty.
  Cost: Firefox opens an MHTML only with an add-on. Chosen by the session.
- **D2 - Fallback order for a URL that will not archive** (FR-005, FR-012, the Edge Cases): (1) the GM's downloaded copy where
  the entry names one (`academic-sources/<file>` in the entry, 13 entries); (2) live fetch; (3) the newest Wayback snapshot
  (the availability API, then the raw `id_` capture plus its MHTML); (4) partial - whatever bytes the live site served, with
  the page-cache text beside them; (5) unreachable with the reason. For an entry with a GM copy the live page is ALSO captured
  where it answers, so the page the reader's link opens is archived too.
- **D3 - One manifest file per URL**, so concurrent sessions never conflict; ~2,110 small files.
- **D4 - Capture time is the version key**: a later capture is a new directory (FR-009); the manifest points at the latest
  and keeps the first in `first`.
- **D5 - At reserve time a failure never blocks** (FR-006): the outcome is written as it is; a push that fails writes
  `pending-upload`, which the next `make archive-sources` sends. The record build counts `pending-upload` as covered for
  7 days from the capture, then refuses (the same week as the page cache's age rule, `_sources.MAX_AGE_DAYS`).
- **D6 - A footnote's direct URL** is any `href="http..."` in `research/questions/*.notes.html` that is not a link into the
  record; the build refuses one with no manifest row, naming `make archive URL=<u>`.
- **D7 - Wikipedia revision**: read from the served page's `wgRevisionId` (MediaWiki's page config), stored in `revision`.
- **D8 - Politeness**: one request at a time per host, 1 s between them, a real browser user agent; a 429 or 503 waits 30 s
  and retries once.
- **D9 - The backfill pushes every 200 MB** of new captures, so no push nears GitHub's 2 GB push limit and a stopped run
  loses at most one batch's push (the captures stay in the working copy and the next run pushes them).

## Constitution Check

- I, II: N/A - the source pages gain one link line in the existing site; no new page.
- III, IV, V, VII, VIII, IX: N/A - no pool content, no SOURCE block, no in-world writing, no setting detail.
- VI: PASS - every task runs `make quick`; the feature ends on `make done`; SC-002's sample is opened and grepped by a
  script before the closing task is ticked.
- X: PASS - ruff, ruff format, pyrefly on both halves; red-green tests; `record/archive.py` at 100%; fixtures, not mocks of the
  transport; no file past 1,000 lines (`_archive.py` estimated ~450, kept under by splitting the backfill into
  `_archive_backfill.py` if it grows past 700).
- XII: N/A for map assertions - the feature draws and states nothing about the world. Decisions are recorded in the spec's
  table and here.
- XIII: PASS - the record build gains a refusal; baseline: `make record CHECK=1` builds cleanly on HEAD (taken before the
  change in a detached worktree); after the backfill it must still build cleanly.

## Project Structure

```text
specs/309-source-archive/   spec.md plan.md tasks.md request.md measurement/
scripts/_archive.py          census, capture, working copy, lock, push, backfill, report
scripts/reserve-prefix.py    --url: archive after the stub
.claude/skills/diagram/l7r/diagram/interactive/record/archive.py   manifest reader, entry line, refusals
.claude/skills/diagram/l7r/diagram/interactive/record/site.py      two call sites
.claude/skills/diagram/research/archive/<sha12>.json               the manifest
.claude/skills/diagram/tests/tooling/test_archive.py
.claude/skills/diagram/tests/interactive/test_record_archive.py
.claude/skills/diagram/Makefile                                     archive, archive-sources
.claude/skills/diagram/research/CLAUDE.md, docs/research-doctrine.md   one paragraph each: cited means archived
```
