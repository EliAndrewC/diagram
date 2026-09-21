# Implementation Plan: close the record checks

Spec: [`spec.md`](spec.md) (accepted, FAITHFUL at round 3). Request: [`request.md`](request.md).
Inputs: `specs/242-cite-the-unfootnoted-assertions/HANDOFF.md` sections 4 to 8, its thirteen reports,
its `research.md` R12.

## Summary

The spec was accepted on 2026-09-14. Since then the record was split into per-entry fragments (feature
258), the glossary into per-term files (259), the checks were tiered and given script pre-passes (251,
255, 260) and the defined agents stopped loading the project's instruction files (256). None of that
changes WHAT this feature owes; all of it changes WHERE an edit lands and HOW a check is dispatched.
This plan maps the spec's requirements onto the record as it now stands, and takes the work in two
steps: a measured slice first, then the rest.

## Technical Context

- No engine Python. Edits land in `research/<page>/NNN-*.html`, the `.notes.html` beside each,
  `research/sources/010-works-cited/NNNN-<key>.html`, and the glossary's per-term files; `make record`,
  `make citations` and `make glossary` assemble. Route: DIRECT (spec D2).
- Measurement scripts live in `specs/250-close-the-record-checks/measure/`.
- The four record tests (`tests/interactive/test_footnotes.py`, `test_citations.py`, `test_sources.py`,
  `test_record_format.py`) after each page; `make page-check` at the close (SC-010).

## Performance bookends

None owed: no engine code, no map moves.

## Constitution Check

- XII (research): every FR-001 and FR-002 task is `research: physical` and carries the five boxes.
- XIII (no regressions): T01 records the baseline of the four record tests before any edit.
- XVI (the literal thing): D1 and D3 below are the two places this plan could be read as departing
  from the request; both go to `spec-fidelity` with the GM's words before a task is ticked.

## The design

### D1 - The spec's paths are read through the split; the spec's text stays as it is

The spec names `cities/sizing.html`, `SOURCES.html` and `glossary.json` as edit targets. Each is now an
ASSEMBLED file that is never hand-edited (features 258, 259). The requirement on each is unchanged and
is met on the assembled file; the EDIT lands in the fragment that assembles into it. The spec is not
amended for this: a spec records what was decided when (feature 260 D4 took the same position), and an
amendment would reset an accepted review over a change of address.

242's `measure/apply_notes.py` places notes by LINE into a whole page and writes footnote numbers; both
are gone. Notes are hand-placed per the per-entry rule: `<sup class="fn" data-note="<key>"></sup>` in
the fragment, `<li data-note="<key>">` in its `.notes.html`. 242's `measure/worklist.py` reads the
assembled page and still runs (measured 2026-09-21: `cities/sizing.html`, 6 items, FOOTNOTED 1,
LOCATED 5), so SC-001 and SC-006 are judged with it unchanged.

### D2 - A check is dispatched per ENTRY, with its pre-pass, never per page

FR-007 asks for `quote-check` and `record-format` "scoped to the changed notes and sections". After the
split that scope is a file: one agent per changed entry, handed `make quote-verbatim PAGE= SECTION=` or
`make record-prepass PAGE= SECTION=` output and the fragment paths. `source-applicability` is handed
the one registry file of each new key. `source-reader` is handed pages saved by `make source-pages`.
242 measured 340,000 to 720,000 tokens per check when each read two to four whole pages and the
registry (HANDOFF section 7); this is the change that measurement asked for.

### D3 - A measured slice first, then the GM reads the figures (GM 2026-09-21)

The GM, starting this feature: *"begin feature 250, but then only perform a few of its tasks, and then
measure the token usage for the different aspects of each task. For example, how many tokens are eaten
up by the main session, how many by each named subagent, how many by the ad hoc subagents, etc. by
measuring this, we can then check whether we need to make any more structural changes before we proceed
with the rest of the feature."*

So Phase 1 is a slice chosen to run EVERY agent the full feature will run, once, on the smallest real
work that does so, and Phase 2 onward waits for the GM. `measure/tokens.py` cuts the session into one
window per task (`mark`) and reports the main session, each named agent and each ad-hoc agent per
window, with what each agent read, largest first. The slice:

- **FR-001 whole** - `cities/sizing`: two entries, five bare items. Runs `source-reader`, the note
  writing, `source-applicability` on any new key, `quote-check` and `record-format` per entry.
- **FR-003 for one entry** - the vocabulary findings of one entry, with a `record-format` re-check. No
  reader; the contrast case (edits and one check).

The slice is real work and stays. It is not pushed: a feature with an open task lands nothing but its
`specs/` claim, so the record edits wait in the clone for the feature's close.

### D4 - FR-002's count is derived by a script over the reports

`measure/assertions.py` cuts each quote-check report at its "assertions with no footnote" heading and
lists the bullets per page and section. The heading wording differs in every report (measured: six
wordings over six reports), so the script matches a heading containing both "footnote" and
"assertion", case-blind, and FAILS on a report where it finds none, so a seventh wording cannot
silently drop a page. The task list names no count; the closing report prints the script's.

### D5 - FR-006's items that landed in a rewritten sentence are found per fragment

`worklist.py` names the section of each NOT-LOCATED, TOO-SHORT or AMBIGUOUS item. The hand search opens
that section's one fragment, not the page.

## Phases

0. Baseline and the meter (T01, T02).
1. **The measured slice** (T03 to T09), ending in the measurement report (T10). STOP for the GM.
2. FR-002 page by page; FR-006 beside it, since both open the same fragments.
3. FR-003, FR-004, FR-005 (the cosmetic sweeps).
4. FR-007's owed checks over what phases 2 and 3 changed; FR-008; FR-009; the close.

## Complexity Tracking

Nothing added beyond two measurement scripts under `measure/`.
