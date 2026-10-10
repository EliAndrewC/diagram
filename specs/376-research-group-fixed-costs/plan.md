# Implementation Plan: the claims sign-up sheet through tooling, and the archive before the web (feature 376)

**Spec**: `spec.md` | **Request**: `request.md` | **Research**: `research.md` R1 (the premise), R2 (the measurement)

## Summary

Two pieces, as the GM asked: one tool for the claims sheet (FR-001 to FR-003) with the GM's large-file rule written
into the guidelines (FR-004), and the fix R2's measurement names (FR-005, FR-006). Main sessions already look locally
before the web. The checking agents re-fetch pages the archive holds, because the scripts in front of them cannot read
a PDF and never ask the archive. Everything is tooling: every task is `research: rendering`. No engine file changes, so
the landing is DIRECT.

## Technical Context

- **Code.** Python 3 stdlib scripts under `scripts/pages/` and `scripts/record/`, and a bash guard under
  `scripts/hooks/`.
- **Tests.** In `tests/tooling/` (the scripts) and `tests/hooks/` (the guard).
- **The claims sheet** sits outside every repository, at `/diagram/.clones/RESEARCH-CLAIMS.md`, shared by every clone.
- **The archive's working copy** is at `<mirror>/.specify/source-archive/`. Its manifest rows are
  `research/archive/<id[:2]>/<id>.json`.

## Performance bookends

N/A: no generator change.

## Constitution Check

- **I-V**: N/A.
- **VI**: N/A for maps. The guard is a `case` on the payload before any python.
- **X**: every new function has a test.
- **XII**: N/A - no physical decision.
- **XIII**: tooling tests and `make hooks-test` green before and after.
- **XIV**: the bugs R2 found are fixed here.
- **XVI**: every FR is built as written, with the mechanisms below.

## Decisions

**D1 - The claims tool** (`scripts/pages/claims.py`, FR-001).
- **The commands.**
  - `make research-claim Q="0060 0246" FEATURE=376 [STATUS="in progress"] [WHY=]` claims.
  - `make research-claims Q="..."` queries.
  - `STATUS=done` releases. `RELEASE=<owner> WHY="<reason>"` releases another owner's stale claim, and the reason is
    written on the line.
- **The owner** is the clone's directory name (`git rev-parse --show-toplevel`), so a session cannot claim as another.
- **New lines** keep the sheet's shape, so old and new read alike: `<owner> | <feature> | Q=0060,0246 | <status> |
  <YYYY-MM-DD>`.
- **The lock.** A claim is read, checked and appended under `fcntl.flock` on `<sheet>.lock`.
- **Which question a line names.**
  - Every 4-digit number in its item field.
  - An old `<page>/<NNN>` or `<page> <NNN>` form, mapped to its number through `research/moved-303.json`.
- **When a claim is live.** It is the latest line of one owner naming that question, and:
  - its status does not open with `done`, `released`, `landed`, `complete`, `withdrawn` or `DONE`;
  - and its feature is not settled. A feature is settled when `make speckit-todo`'s `feature()` reads its directory in
    the mirror's `specs/` as closed. That retires the old free-text lines whose features finished without a release
    line.
- **Output.** At most one line per live claim touching the asked questions, and one summary line. Nothing else is
  printed.

**D2 - The sheet's guard** (`scripts/hooks/claims-file-hooks.sh`, FR-002).
- **What it refuses.**
  - A PreToolUse `Read`, `Edit` or `Write` whose path is the sheet.
  - A Bash command that names it (`RESEARCH-CLAIMS`). The FR-001 commands never name it on their command line.
- **The refusal** names `make research-claim` / `make research-claims`.
- **The escape.** `CLAIMS_FILE_OK="<reason>"` covers a repair of the sheet itself, recorded by `guard_log` as every
  escape is.
- **Registration.** In `.claude/settings.json` on `Read|Edit|Write` and on `Bash`.

**D3 - The text** (FR-003, FR-004).
- `scripts/container/page-session-rules.md`: the claims sheet goes through `make research-claim` /
  `research-claims`; `make lines` / `make append` stay for handoffs and checks reports.
- CLAUDE.md gains the GM's rule: any time a process requires editing a potentially large file, it uses tooling (a make
  target) to edit it, never opening and editing it by hand, as `make tick` does for `tasks.md`.
- The guard table gains a row.

**D4 - The archive behind a page that cannot be read** (FR-006, R2).
- **A PDF is asked about.** `quote_verbatim.Pages._get` stops returning NOT-CHECKED from the URL's extension alone. It
  makes the request it already makes for any page and keeps only the headers for a PDF (as it does now for a PDF it
  learns of from the content type). So a PDF answers `NOT-CHECKED, live` or `UNFETCHABLE`.
- **`sources.CachedPages.get`.** On a cache miss it asks the inner fetcher (the live page) first, unchanged. When that
  is not FETCHED, it reads the archive's text for the URL: the manifest row's `path`, then
  `<mirror>/.specify/source-archive/<path>/text.txt`. If there is text, it returns
  `{"state": "FETCHED", "text", "archived": <capture date>, "live": <was the link answered>}`, and does not put it in
  the page cache, which holds what was fetched. Everything built on `CachedPages` gains this: `make quote-verbatim`,
  `make source-pages`, and a check bundle's `pages/`.
- **`quote_verbatim.judge_note`.** A passage judged on an archived page counts only when VERBATIM. Anything else there
  becomes `NOT-CHECKED` "not found verbatim in the archived text of <date> - check by hand", because PDF extraction can
  split words. A note VERBATIM only on archived pages is READABLE when every such link answered live, else `-`. So the
  archive can confirm a quotation but never sink one.

**D5 - Validation.** `make quote-verbatim` is run on real questions whose notes cite PDFs, before and after D4. The
NOT-CHECKED that became VERBATIM, and any verdict that changed otherwise, are recorded in R2. A verdict that LOSES
ground - a VERBATIM or READABLE lost, a new NOT-ON-PAGE or NOT-READABLE - is a bug. A PDF that is now asked and
refused moves from NOT-CHECKED to UNFETCHABLE, the truer of two residue verdicts.

## Project Structure

```text
scripts/pages/claims.py                 new - the claims tool
Makefile                                research-claim, research-claims
scripts/hooks/claims-file-hooks.sh      new - the sheet's guard
.claude/settings.json                   its registration
scripts/record/quote_verbatim.py        a PDF asked about; archived passages count only when VERBATIM
scripts/record/sources.py               CachedPages reads the archive after the live page fails
scripts/container/page-session-rules.md, CLAUDE.md, docs/guards.md
tests/tooling/test_claims.py            new
tests/tooling/test_quote_verbatim.py, tests/tooling/test_sources.py
tests/hooks/test-claims-file-hooks.sh   new
```
