# Implementation Plan: Every Research Finding Cites Its Sources

**Branch**: none (`SPECIFY_FEATURE=136-research-citations`) | **Date**: 2026-08-28 | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), authority [gm-request.md](gm-request.md)

## Summary

Re-source every uncited historical finding in the diagram skill: 117 research-tree candidate
rows (73 `not recorded` + 44 with no sources line; the `SOURCES.md` queue), the standalone
research documents under the skill root, inline grounding in the operative and pool documents
(the top-level `settlements.md` included), the historical halves of ~12 spec research files, and
grounding stated in engine comments (recorded in the tree; the code untouched).
The work is a research feature, not an engine feature: its diff is docs (`research/`,
`SOURCES.md`, pointers in operative docs, spec research files) and nothing else. No engine path,
pool artifact or operative rule changes; a contradicted finding is corrected in the record and
queued for the GM.

## Technical Context

**Language/Version**: Markdown records; no code
**Primary Dependencies**: the `source-reader` agent (Sonnet; WebFetch/WebSearch) for every reading;
`WebSearch` in the session for the search pass
**Storage**: `research/*.md`, `research/SOURCES.md`, `specs/136-research-citations/ledger.md`
**Testing**: the existing gate (the task-boxes test); the ledger's open-row count as the measure
**Target Platform**: n/a
**Project Type**: docs only
**Performance Goals**: none - no generator runs
**Constraints**: FR-006 - no engine, pool, or rule-text change beyond a pointer; every push is DIRECT (docs)
**Scale/Scope**: ~117 tree rows + the other homes; batches of one research file each (15), plus one batch each for standalone docs, spec research and engine comments

**Single-artifact target**: n/a - no generator change. **Every step is two steps**: n/a - no map
is rolled; the "reference then pool" split has no meaning for a records feature.

## Performance bookends

N/A - constitution VI's bookends bind a diagram-GENERATOR change; this feature changes no
generator and rolls no map; a docs-only delta takes the DIRECT route and owes no gate run.

## Constitution Check

- **I / II**: N/A - no UI in this repository.
- **III. Pool Data Conventions**: N/A - no pool content added.
- **IV. One Canonical Home for GM Source**: PASS - no SOURCE blocks touched.
- **V. Protecting the GM's Writing**: PASS - `gm-request.md` is quoted verbatim and never edited;
  no SOURCE markers under the skill are edited.
- **VI. Verify Before Reporting Done**: PASS - each batch: `source-reader` verdicts on record for
  every cited key; the ledger recounted by the entry parser; the quick suite (the task-boxes
  test) after the batch's edits. `spec-fidelity` on the spec before implementation. No map review is
  owed (no map changes).
- **VII / VIII**: N/A - no in-world content generated.
- **IX. Setting Integration**: PASS - `setting-canon` findings cite `l7r.md` / `budgets.md`
  by pointer; nothing contradicting the GM's notes is written.
- **X. Python Discipline**: N/A - no Python is written (the sources-registration check is
  proposed to the GM as future work, not built - spec FR-010).
- **XII. Historical Grounding Bookends**: PASS in the sense that binds here - the feature IS the
  opening bookend applied retroactively; each pass records finding, class and sources. The closing
  bookend (re-examine the rendered PNG) is N/A: nothing rendered changes. Decisions for the
  reader: every entry keeps or corrects its accurate / deviation / guess class in place; a
  contradiction is a row for the GM, not a rendering decision this feature makes.
- **XIII. No Known Regressions**: PASS - a docs-only feature; nothing the tests exercise changes.
- **XIV. Fix defects where found**: any DEFECT the passes surface in code (a stale `Grounds:` line
  naming a check that no longer exists, a comment describing dead code) is fixed if it is docs, and
  RECORDED with a measurement and reported if it is engine - because FR-006 forbids this feature
  touching the engine. That is the GM's own instruction in this feature and overrides the default.
- **XV / XVI**: PASS - the chain runs unattended; the spec is reviewed by `spec-fidelity` against
  the GM's words; an exception (any temptation to "just fix" a contradicted rule) goes to
  `spec-fidelity` before it is taken.
- **XVIII**: N/A - no guard is added (deliberately: spec FR-010).

## Method, per batch (one research file = one task)

1. **Diff inline vs tree**: read the operative doc the file grounds; list any grounding prose with
   no tree entry; add rows to the ledger section B.
2. **Search pass** for every open row: China-first and Japan corroborating as the project's
   doctrine says; primary and scholarly first (JStage, CiNii, JSTOR abstracts, university and
   museum pages, ministry sites, Wikipedia's references over Wikipedia). Never Grokipedia.
   Anchors (Takayama Jin'ya, Hikone, Pingyao ...) are read from their own documentation.
3. **`source-reader`** dispatched in the background with every claim verbatim + pointer; it
   returns READ (quote) / SUMMARY-ONLY / CONTRADICTED / NOT-FOUND per claim. Batch the whole
   file's claims into one dispatch (or two for capitals.md).
4. **Write**: `SOURCES.md` keys with "used for" and the READ/SUMMARY-ONLY label; the entry's
   `**Sources:**` line; a supplement only where the reading adds; evidence class corrected; a
   NOT-FOUND claim gets "searched: ... not found" and class `reconstruction`; a CONTRADICTED claim
   gets the corrected finding, the old finding kept as "what the rule currently implements", the
   status `contradicted - rule unchanged, awaiting GM`, and a row in ledger section E.
5. **Ledger** rows updated; the `SOURCES.md` queue rows owned by the file struck.
6. **Verify**: the entry parser recount into the ledger; the quick suite (the task-boxes test); commit;
   push at the end of each batch (see "Pushing while the feature is open").

## Project Structure

```text
specs/136-research-citations/
├── gm-request.md        # verbatim
├── spec.md
├── plan.md              # this file
├── ledger.md            # FR-001: the inventory and its status - the feature's progress meter
├── research.md          # Phase 0: how the passes are run; source pools per subject
├── tasks.md
└── checklists/requirements.md

.claude/skills/diagram/research/*.md, cities/*.md   # entries re-sourced in place
.claude/skills/diagram/research/SOURCES.md          # keys added; queue worked
.claude/skills/diagram/settlements.md, settlements/*.md, buildings.md, pool/**/*.notes.md  # pointers only
.claude/skills/diagram/*.md (flophouse-research.md etc.)  # standalone docs: sources or a pointer
specs/NNN-*/research.md                              # historical findings get sources or a pointer
(l7r/**/*.py - READ for findings stated in comments; never edited)
```

**Structure Decision**: no new directories; the record lives where the project already keeps it.

## Complexity Tracking

None.

## Pushing while the feature is open

Feature 133's rule refuses a push whose delta touches a spec with an open task, except that
feature's `specs/` directory alone. This feature's batches each change `research/` docs, which the
sync script's active-feature derivation may tie to the open 136 tasks. The batches are therefore
committed in the clone as milestones, and the push is attempted after each; if refused, the work
stays in the clone until the feature's tasks are all ticked (the GM's contradiction review is a
task the GM closes, as in 133/135). The ledger in the clone is the progress record either way.
