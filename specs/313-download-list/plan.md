# Implementation Plan: The canonical download list, the GM's marked copy, and the access tags

**Spec**: `specs/313-download-list/spec.md` | **Created**: 2026-10-02

## Summary

The GM's `TO-DOWNLOAD.md` and 312's high-risk list are imported into one canonical Markdown list in the record directory,
each entry given the GM's mark lines. Four commands own it: import (once), ingest, sync and add. A guard refuses a
session's write to the GM's copy, and a push check holds the list append-only. The access tag is computed per source from
the archive manifest, the registry's `READ` comments, the marks recorded in the list and the few states recorded by hand,
and one command reports it.

## Technical Context

- Tooling only: `scripts/` (Python 3, stdlib, git), one guard and its companion, the skill Makefile, docs, and two files in
  `research/`. No engine module (`l7r/**`) changes, so the delta takes the DIRECT route. No map changes, so there are no perf
  bookends and no map-review occasion.
- Reused, never copied: `reserve-prefix.py`'s `Lock` and `mirror_of` (the host-wide lock that sees every clone);
  `_archive_ops.process_inbox` and `_archive.gm_table` (the inbox); the manifest rows `research/archive/<id[:2]>/<id>.json`;
  `_guardlog.sh`'s `escape_or_refuse` and `guard_log`; `check-research-pointers.py`'s pointer forms.

## Decisions

**D1 - The files.**

| path | what | written by |
|---|---|---|
| `.claude/skills/diagram/research/to-download.md` | the canonical list | import, ingest, add; a session's hand edit to an entry's text (a pointer fix) is allowed |
| `.claude/skills/diagram/research/to-download.state.json` | the sync record: `imported`, `synced`, `ingested`, each `{sha256, date}`, `synced` also `commit` | import, sync, ingest |
| `.claude/skills/diagram/research/source-access.json` | the eight states in order with their names and meanings, and `recorded`: `{key: [{state, date, reason}]}` | by hand through the access command's `SET=` |
| `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md` | the GM's copy | sync only |

**D2 - The entry format.** An entry is a `### <id>. <title>` heading and everything up to the next `###` or `##` heading.
Its id is a number, or `H<n>` in the high-risk section. Directly under the heading come the mark lines:

```
- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
```

followed, once marks are recorded, by `- Marks recorded <date>`. A box reads ticked for `[x]` or `[X]`. Text after
`where:` and `Saved as ...:` is free. Ingest compares and records the three mark lines as a unit. The rest of the entry,
called its body, is everything else, and the recorded line belongs to the canonical list alone.

**D3 - The import (once).** `_downloads.py import` writes the canonical list as: a new header (how to mark, and the words
"ingest" and "sync"); `## High-risk sources (feature 312) - first`, holding 312's preamble and its tier headings with the H
entries; then the GM's file from its first line, unchanged. Every entry gets its mark lines. Entries 1-6, 8 and 12-16 are
ticked downloaded and entries 7, 9, 10 and 11 not found, each with `- Marks recorded 2026-09-13 (the GM's status table)`.
These come from the status table and entry 16's own text (spec FR-004). The state's `imported` holds the sha256 of the GM's
file as read. A test re-derives the GM's file and 312's from the canonical list by removing the mark and recorded lines and
the new header, and compares them byte for byte (SC-001).

**D4 - Ingest: a three-way comparison.** The base is the canonical list at `synced.commit` (`git show`). For each id in the
copy:

| | outcome |
|---|---|
| marks differ from the canonical marks | validated, then recorded with today's date; refused and named on found-elsewhere without downloaded or partial, or not-found with either |
| body = base body | nothing, whether or not a session changed it |
| body differs from base, canonical body = base | the GM's edit: shown as a diff, kept with `KEEP=<ids>`, discarded with `DROP=<ids>`, else pending |
| body differs from base and the canonical body differs from both | a conflict: shown three ways, settled only by `KEEP=` or `DROP=` |
| id not in the canonical list | named, pending |

Marks are recorded even while a text edit is pending. `ingested` moves to the copy's sha256 only when nothing is pending,
and the command then exits 0, else 1, naming each pending id and the `KEEP=`/`DROP=` that settles it. Then it runs the inbox
(D7) and prints the access tags of every source whose entry changed. Ingest refuses before the first sync, saying sync first.

**D5 - Sync.** It refuses unless the copy's sha256 is one of `imported`, `synced` or `ingested`, or the copy is absent. The
refusal names the entries whose marks or body differ from the canonical list and says to ingest first. It also refuses when
the canonical list has uncommitted changes (the base must be a commit). Otherwise it copies the bytes, then writes `synced`
as `{sha256, date, commit: HEAD}`, which the session commits.

**D6 - Add.** `make download-add FILE=<draft.md>`: the draft holds one or more entries headed `### NEW. <title>`, each
carrying a link line (`- **[...](http...)**`), `- Fallback:` with a link, `- **Rests on it:**` naming at least one
`research/questions/<file>` or `research/contents.json#<section>` that exists, and `- Blocked by:`. Under `Lock`
(`<mirror>/.specify/download-ids.lock`), the next number is one past the highest held by the mirror's list, every clone's
list and the ledger `<mirror>/.specify/download-ids.jsonl`. Each number is written to the ledger, and the entry, with its
mark lines, is appended at the end. `HIGH_RISK=1` takes the next `H<n>` instead and appends at the end of the high-risk
section; feature 312 owns that list's growth.

**D7 - The inbox takes an entry's id.** `MATCH="<file>=#17"` or `"<file>=H3"` resolves to the keys that entry names (D8),
or to `[]`, and the table row records `"download": "<id>"`. Ingest passes a match for every entry whose saved-as line names
a file present in the inbox, so the GM's naming costs no question. A new download left unmatched waits, as it does today.

**D8 - An entry's keys.** These are the backticked tokens in its heading and body that are registry keys, plus the keys the
manifest gives for the URLs it links. A drafted entry may state `- Key: <k>[, <k>]`.

**D9 - The access tag** (`scripts/_access_tags.py`). For each registry key (from the entries' `<h3 id=...>`):

1. A GM mark recorded on an entry naming the key: downloaded gives gm-full whatever else is ticked; partial without
   downloaded gives gm-partial; paywalled alone gives paywalled; not found alone gives no state, and the basis says the GM
   did not find it. Several entries naming the key: the newest mark that gives a state, and on the same date the most open;
   a not-found mark never overrides another entry's state. Dated by the recorded line.
2. Else the manifest rows naming the key, each mapped: `archived` and `archived-earlier-snapshot` to open, `archived-gm-copy`
   to gm-full, `partial` and `unreachable` to gone on HTTP 404 or 410, down on a timeout, a network error or HTTP 5xx, and
   bot-refused otherwise (403, 405, 406, 429, a page that would not render). The most open row wins, in the order open,
   gm-full, gm-partial, paywalled, bot-refused, down, gone, never-read, dated by its capture.
3. If that gives bot-refused, down or gone, or there is no row, and the registry entry has no `READ` comment, the state is
   never-read. This keeps apart the three states 312's request names: read, never read but referenced, and once read but
   unreachable now.
4. No row, with a `READ` comment: open, dated by the latest `READ`.
5. A state recorded by hand in `source-access.json` wins over 2-4 when its date is the same or later, and never over a mark
   that gives a state (rule 1). A not-found tick alone leaves a hand state in force (round 4's aside).

**D9a - The seeds** (spec FR-011). The paywall knowledge already in prose is recorded with `SET`, one by one, each read in
its line first. It covers registry entries whose comment or write-up says the full text is paywalled, behind a
subscription or a login wall, and list entries whose `Blocked by` says paywalled, a subscription database or an
institutional login. Each seed is dated 2026-10-02, the day it was read and confirmed, and its reason quotes the line.
Mentions that say a page is open ("no paywall", "the full text to a reader with no subscription"), that concern another
work, or where the GM already holds a full copy are not seeded. The list of what was seeded and what was passed over goes
in `research.md`.

Each keyless list entry is `download:<id>`: rule 1 gives its state, else never-read.
`make access-tags [KEY=<key or download:<id>>] [JSON=1] [SET=<state> KEY= DATE=<d> REASON="..."]` prints counts per state, one tag, or
everything as JSON; `SET` appends a hand record. Not stored otherwise (spec Decisions).

**D10 - The guard** `scripts/download-copy-hooks.sh` (PreToolUse, Bash|Edit|Write|NotebookEdit): an Edit or Write whose path
is the GM's copy, or a shell command writing it (a redirect, `tee`, `sed -i`, `cp` or `mv` onto it, a Python
`write_text`), is refused with `make download-add FILE=<draft.md>` and, for a sync, `make downloads-sync`. The make targets
pass because they run the script, which the guard does not see. The escape is `DOWNLOAD_COPY_OK` with a reason, logged. Its
companion is `scripts/test-download-copy-hooks.sh`, proven red by deleting the match.

**D11 - The push check.** `_downloads.py check` runs in `sync-with-main.sh` beside the pointer check, comparing with
`origin/main`'s list. It refuses: an id that main has but this list lacks; main's ids out of their order; a new numeric id
not at the end, or not above main's highest; a new H id not at the end of the high-risk section; an id used twice; an entry
without well-formed mark lines. Each refusal names the id and the command that fixes it. `--selftest` runs first, as the
pointer check's does. While the list is absent on main, the check passes.

**D12 - The doctrine.** The rule at `CLAUDE.md` (Research), `research/CLAUDE.md` (two places),
`docs/research-doctrine.md`, `docs/research-record-rules.md` and `container-scripts/page-session-rules.md` is rewritten to
name the add command. The research `CLAUDE.md` gains a short section on the GM's two words and their commands, and the
root guard table gains its row. `_archive_ops.GM_LISTS` already leaves the GM's copy out of the inbox.

## Constitution Check

- I, II: N/A - no UI in this repository.
- III, VII, VIII, IX: N/A - no pool content, no in-world writing.
- IV, V: PASS - no SOURCE blocks. The GM's file is imported unchanged and their copy is written only on their word.
- VI: PASS - each task names its verification; `make done` and `make hooks-test` at the end; `make record CHECK=1` and
  the pointer check over the new file.
- X: PASS - ruff, ruff format and pyrefly over the new scripts. Tests are written red first in
  `tests/tooling/test_downloads.py` and `test_access_tags.py`. No file nears the 1,000-line bar (`check-file-scale.py` holds it at the gate).
  The coverage floor is over `l7r` and does not change.
- XII: N/A for rendering - nothing a map draws or states changes. The access tags restate what the archive and the registry
  record; no new finding is made.
- XIII: PASS - the baseline is `make done` in a detached worktree before the push. Shared code touched:
  `_archive_ops.py` (the inbox's match), `sync-with-main.sh` (one more check). Their existing tests stay green.

## Project Structure

```
scripts/_downloads.py                 import, ingest, sync, add, check (and --selftest)
scripts/_access_tags.py               the derivation and the report
scripts/download-copy-hooks.sh        the guard; scripts/test-download-copy-hooks.sh its companion
scripts/_archive_ops.py               MATCH= takes an entry id
scripts/sync-with-main.sh             the push check
.claude/skills/diagram/Makefile       downloads-ingest, downloads-sync, download-add, access-tags
.claude/skills/diagram/research/      to-download.md, to-download.state.json, source-access.json
.claude/skills/diagram/tests/tooling/ test_downloads.py, test_access_tags.py, test_archive_ops.py (one case)
.claude/settings.json                 the guard registered
```

## Complexity Tracking

None.
