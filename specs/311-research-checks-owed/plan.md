# Implementation Plan: The record's checks owed by what an edit touches, and the question that says why it is asked

**Spec**: `specs/311-research-checks-owed/spec.md` | **Created**: 2026-10-02

## Summary

One script names every record-check unit a delta owes, from what the delta touched, against the merge base with main; the
push refuses an owed unit not answered at the content being pushed; a bundle or a dispatch for a check that is not owed is
refused. A new defined check, `intro-check`, judges whether a question tells its reader why it is in the record; an intro
paragraph is a marked form that cites nothing and so owes no source-reading check. The new check is run once over every
question, the intros it calls for are written, and the parley-room question gets the GM's.

## Technical Context

- Tooling only: `scripts/` (Python 3, stdlib, git), one agent file, the record's CSS, docs, the record's question pages.
  No engine module (`l7r/**`) changes, so the delta takes the DIRECT route; no map changes, so no perf bookends and no map
  review occasion.
- Existing pieces reused, never copied: `_entry_owed.base_of` and its modal scan; `_translation_owed.owed`; the block reader
  of `_check_bundle.py` (`_BLOCK`, `_NOTE_LI`); `_hm_escape.py reason-ok`; the bypass-log writer in `entry-gate.sh`.

## Decisions

**D1 - What a unit is, and its fingerprint.** A unit is `<check>:<subject>`. Each has a fingerprint, a hash of exactly what
its check reads, normalized to its WORDS (HTML comments and markup removed, whitespace collapsed, each note mark kept as a
`[^key]` token), so a comment, a tag marker, a bold or a re-wrap changes nothing (spec FR-004):

| unit | subject | fingerprint over |
|---|---|---|
| `intro-check:NNNN` | a research page | its heading text and its intro paragraph |
| `record-format:NNNN` | a question (both pages, both notes files) | every visible block, heading and note |
| `quote-check:NNNN#<note>` | a note | the note and every block carrying its mark (VERBATIM + SUPPORTS) |
| `quote-check:NNNN#unfootnoted` | a question | its changed blocks with no mark, intros excluded (the unfootnoted-assertion half) |
| `source-reader:NNNN#<note>` | a note | the note |
| `source-applicability:<key>` | a write-up under `research/sources/` | its visible text |
| `translation-check:NNNN#<note>` | a pair | `_translation_owed`'s pairs of that note |
| `entry-drift:<modal key>` | a modal | its explanation prose and the sections its `Entry:` names, normalized as D8 |

**D2 - What is owed: the content is new, judged across the whole record.** A block, a note or a heading is CHANGED when its
normalized text is present nowhere in the record at the merge base - the comparison `_translation_owed` already makes for a
pair, so a move, a renumbering or a merge owes nothing (spec Edge Cases). The table of FR-004 is then mechanical:
a changed heading owes `intro-check`; a changed intro owes `intro-check` + `record-format`; a changed note owes
`source-reader` + `quote-check` on it + `record-format`; a changed marked block owes `quote-check` on each mark it carries +
`record-format`; a changed unmarked non-intro block owes `quote-check:NNNN#unfootnoted` + `record-format`; a write-up whose
visible text differs from the same key's at the base (or is new) owes `source-applicability`. A new question is just all of
its content changed. `intro-check` is owed on research pages only; the drawing page is read for context.
Read at the base with ONE `git ls-tree` + ONE `git cat-file --batch` over `research/questions/` and `research/sources/`
(about 1,700 files), never a `git show` per file.

**D3 - The intro paragraph is `<p class="intro">`**, the first block of a research page after its heading and comments; at
most one; no note mark; it says what Rokugan (or the map) has and that the research follows; it may name the class its cited body or drawing page reaches, and adds no historical claim that body does not carry.
The site inserts the "Not to be confused with" block straight after the heading, so the intro stands after it with no engine
change (verified on the built page, T05). It carries no styling (spec FR-002). Stated in `research/STYLE.md` section 2 and the research `CLAUDE.md`; `tests/interactive/test_record_format.py`
holds the mechanical shape (position, one, no mark).

**D4 - `intro-check`, the defined agent.** `.claude/agents/intro-check.md`: Opus at medium effort (it judges; the project's
rule - a downgrade stands only after seeded runs, and the backfill is about ten dispatches, so the saving does not repay the
experiment), `omitClaudeMd: true`, tools Read and Grep, reads a bundle. Verdicts per question: NO-INTRO-NEEDED,
NEEDS-INTRO (what the intro must say and the drawing page's class for it - attested, deviation, convention), INTRO-OK,
INTRO-FIX (what is wrong: no "why", or a historical claim the cited body does not carry). Its bundle (`make check-bundle Q=NNNN FOR=intro-check`, or
`QS="NNNN NNNN ..."` for a batch) holds, per question: the research page's heading, intro and opening paragraph and its lead
lines; the drawing page's heading and opening; the `Name:` and `Label:` of each modal whose `Entry:` names the question.
Added to `test_agent_models.py`'s tier table and to `_ledger_lint.py`'s check list.

**D5 - The owed command.** `scripts/_record_owed.py` (CLI, git) over `scripts/_record_units.py` (pure: blocks, notes,
fingerprints, the FR-004 decision over plain dicts, so it is tested without a repository). `make record-owed [Q=NNNN]` prints
one line per unit: slug, check, subject, occasion, and the bundle command; `--unanswered` keeps those with no current answer
record; `--between A B` replays a historical commit pair (SC-002). `_entry_owed` and `_translation_owed` are called, not
re-implemented. Each script stays well under the 1,000-line bar.

**D6 - The answer record.** `make record-checked CHECK=<check> (BUNDLE=<dir> | Q=NNNN [NOTES=k,k] | KEY=<key> | KIND=<modal>) RESULT="<counts>"`
writes `$(git rev-parse --git-common-dir)/record-checks/<slug>.json` per unit: slug, fingerprint, counts, utc. With BUNDLE= the
fingerprints are those the bundle recorded in its MANIFEST when it was built (what the check actually read); without, the
tree's now - the form for `source-reader` (it reads before the note exists) and for fixes that apply the check's own
findings. A record is current while its fingerprint equals the unit's now. In the pushing clone, as the review records are
(spec decision); a headless page session works in the clone its brief names, which is the clone that pushes.

**D7 - The push.** `scripts/entry-gate.sh` becomes the record gate (its name kept: it is wired into both routes and four docs):
it runs `_record_owed.py --unanswered` and refuses naming each unit and its bundle command. `ENTRY_DRIFT_OK="<reason>"` keeps
discharging the `entry-drift` units; `RECORD_CHECKS_OK="<reason>"` discharges every unit; both write `dev/bypass-log/` as
today. An `entry-drift` unit is still also discharged by rewriting the prose (the unit then vanishes, as today).

**D8 - entry-drift sees findings, not upkeep.** `_entry_owed.moved_anchors` compares the normalized body - comments and the
intro paragraph removed - so an intro, a tag marker or a session note no longer owes a modal check (FR-004 last row).

**D9 - No check that is not owed.** `_check_bundle.py` asks `_record_owed` before building: a `FOR=<check>` bundle with no unit
of that check owed on the question is refused (exit 3) with the owed list, unless `NOT_OWED_OK="<reason>"` (two words or more;
recorded in the guard log and in the MANIFEST). A `FOR=quote-check` bundle with no `NOTES=` holds only the owed notes (the
whole question when `#unfootnoted` is owed). Every question bundle's MANIFEST carries `owed-checks:` and one
`unit: <slug> <fingerprint>` line per owed unit. `check-bundle-hooks.sh` refuses a dispatch of a record check whose
MANIFEST does not list it as owed, with `CHECK_NOT_OWED_OK="<reason>"` as the escape. Exempt: `source-reader` (a research read
precedes the note it supports, so nothing is owed yet) and `record-style` (owed by a declared sweep, feature 292). A KEY=
bundle is not refused (its readers are source-reader and the write-up check).

**D10 - The backfill.** Ten `intro-check` dispatches of about 24 questions each, bundles built with
`NOT_OWED_OK="feature 311 backfill"`; rulings tabulated in `specs/311-research-checks-owed/backfill.md`; every NEEDS-INTRO and
INTRO-FIX written or fixed by this session from the drawing page and `make canon`, never inventing a setting detail; each
written intro then owes `intro-check` + `record-format` by D2 and is answered in at most two rounds.

**D11 - The doctrine follows the command.** The research `CLAUDE.md`, `STYLE.md`, `docs/research-doctrine.md`,
`container-scripts/page-session-rules.md`, the root `CLAUDE.md` guard table, `docs/guards.md`, and the descriptions of
`quote-check`, `record-format`, `source-applicability`, `source-reader` and `translation-check`: "run on every new or changed
entry" becomes "run on the units `make record-owed` names", and each says to record the answer with `make record-checked`.

## Verification

- Red first: `tests/tooling/test_record_owed.py` over plain dicts and a temporary repository, one case per FR-004 row and each
  Edge Case (move, merge, new question, deleted note, unmarked block, intro, write-up, comments only), red before the scripts
  exist. `test_entry_owed.py` gains the intro and comment cases. `test-entry-gate.sh` gains the unanswered, stale, answered,
  `RECORD_CHECKS_OK` and silent cases (SC-004). `test-check-bundle-hooks.sh` gains the not-owed dispatch and its escape;
  `test_check_bundle.py` the refused bundle, the escape and the owed-notes default.
- SC-005: `intro-check` seeded with three known questions (the parley room without its intro -> NEEDS-INTRO; a plain farm
  subject -> NO-INTRO-NEEDED; an intro adding a historical claim its cited body does not carry -> INTRO-FIX), three runs a leg, before the backfill.
- SC-002: `make record-owed` `--between` over the last 30 record-only commits, tabulated in `research.md`.
- `make quick` while iterating, `make done` once at the end (no engine change, but the tests and static checks are owed);
  `make record CHECK=1`; `make hooks-test`.

## Constitution Check

- I, II: N/A - no UI; the intro carries no styling (FR-002).
- III, VII, VIII: N/A - no pool content; the intros are expository, not in-world voice.
- IV, V: PASS - no SOURCE block touched.
- VI: PASS - verification above; no map changes, so no map review occasion (`## Occasions: none`).
- IX: PASS - each intro read against `make canon`; the parley room is the GM's own (the GM's draft in `request.md`, and the
  ruling recorded on 0094's drawing page).
- X: PASS - stdlib Python, ruff, pyrefly where the gate holds scripts, red-green tests, no file near 1,000 lines.
- XII: PASS - each intro states the class the drawing page already records (accurate, deviation, convention); no new
  rendering decision; the record of the decisions is the spec's table.
- XIII: PASS - baseline `make quick ALL=1` in a detached worktree before the first script edit; zero new failures.
- XIV: a defect found on the way is fixed in this work.
- XVI: PASS - the spec is reviewed by `spec-fidelity`; no exception to the GM's ask is planned.

## Project Structure

```
scripts/_record_units.py, scripts/_record_owed.py           new
scripts/entry-gate.sh, scripts/test-entry-gate.sh            the record gate
scripts/_entry_owed.py, scripts/_check_bundle.py             D8, D9
scripts/check-bundle-hooks.sh, scripts/test-check-bundle-hooks.sh   D9
.claude/agents/intro-check.md                                new
.claude/skills/diagram/Makefile                              record-owed, record-checked, check-bundle QS=/NOT_OWED_OK=
.claude/skills/diagram/research/{STYLE.md,CLAUDE.md}
.claude/skills/diagram/research/questions/*.html             the intros
.claude/skills/diagram/tests/tooling/test_record_owed.py     new
docs/, CLAUDE.md, container-scripts/page-session-rules.md    D11
```

## Complexity Tracking

None.
