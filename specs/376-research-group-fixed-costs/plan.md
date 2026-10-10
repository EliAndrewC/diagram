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

**D1 - The claims tool** (`scripts/pages/research_claims.py`, FR-001).
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
  - An old page name followed by a run of section numbers (`homesteads  050 110 145`, `fields/090 080`,
    `PAGE=water SECTION=020`), each mapped to its number through `research/moved-303.json`.
- **When a claim is live.** It is the latest line of one owner naming that question, and:
  - and the line carries none of `done`, `released`, `landed`, `complete` or `withdrawn` anywhere after its owner. Old
    lines put the word in the item or in a sixth field, so the whole line is read.
- **Forgotten claims.** The spec keeps a claim live until a later line releases it, so a closed feature's forgotten
  claims are released by `research_claims.py sweep`. It writes one release line for each live claim whose feature
  `make speckit-todo` reads as closed, with that as the reason. It is run once at the landing and can be run again; it
  is never a rule applied silently on read (plan review, round 1).
- **Output.** At most one line per live claim touching the asked questions, and one summary line. Nothing else is
  printed.

**D2 - The sheet's guard** (`scripts/hooks/claims-file-hooks.sh`, FR-002).
- **What it refuses.**
  - A PreToolUse `Read`, `Edit` or `Write` whose path is the sheet.
  - A Bash command that acts on it (below). The FR-001 commands never name it on their command line.
- **The refusal** names `make research-claim` / `make research-claims`.
- **No escape.** FR-002 makes no carve-out, and no repair needs one: the tool only appends, reads every old line, its
  lock releases with its process, and a wrong claim is released through it.
- **What counts as acting on the sheet.** Its file name (with `.md`) as an operand of a command that reads or writes:
  `cat`, `sed`, a redirect, `make lines`, `make append`, and so on. A command that only mentions it, such as a grep
  over the docs or a commit message, passes. Guards match invocations, not mentions.
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

**D6 - The archive before an agent's own fetch** (FR-006; the plan review asked why R2's other held fetches were made).
- **The other held fetches.** Of the 26 outside the checking agents, 10 were main sessions' `make source-pages` served
  from the page cache, which never reached the web; R2 overcounted them. 2 were a PDF and a full text through
  `source-pages`, which D4 covers. 14 were ad-hoc agents' own `WebFetch`, and nothing told those agents the archive
  existed.
- **The fix.** `scripts/hooks/archive-first-hooks.sh` (decider `lib/hm_archive_first.py`, reading the archive through
  `sources._cited` and the manifest, as D4 does) refuses the FIRST `WebFetch` of a URL the archive holds, naming the
  archived text and its capture date. The same actor's second fetch of that URL passes.
- **Why the second fetch passes.** The archived copy is the cheap, exact first read. A second fetch is the actor saying
  it needs the live page, as quote-check's READABLE does.
- **The actor** is the session and agent id, kept in a small state file. It covers every agent, defined or ad hoc,
  with no contract change, because the refusal carries the route.

## Project Structure

```text
scripts/pages/research_claims.py                 new - the claims tool
Makefile                                research-claim, research-claims
scripts/hooks/claims-file-hooks.sh      new - the sheet's guard
.claude/settings.json                   its registration
scripts/record/quote_verbatim.py        a PDF asked about; archived passages count only when VERBATIM
scripts/record/sources.py               CachedPages reads the archive after the live page fails
scripts/container/page-session-rules.md, CLAUDE.md, docs/guards.md
tests/tooling/test_research_claims.py            new
tests/tooling/test_quote_verbatim.py, tests/tooling/test_sources.py
tests/hooks/test-claims-file-hooks.sh   new
scripts/hooks/archive-first-hooks.sh    new - D6
scripts/hooks/lib/hm_archive_first.py   new - D6's decider
tests/hooks/test-archive-first-hooks.sh new
```
