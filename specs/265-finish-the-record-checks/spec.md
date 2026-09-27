# Feature 265 - finish the record checks

**The GM's request** is `request.md` (2026-09-27): move feature 250's remaining research tasks into a feature of their
own, so that 250 - the research PROCESS it built and measured over eleven rounds (its `research.md` R1 to R11) - can
land on main, and other sessions can research other things with it.

## What this feature is

The WORK feature 250 left: the requirements below are 250's own, carried verbatim (250's `spec.md`), for the pages
and sweeps 250 did not reach. The METHOD is 250's, landed: each page worked by `specs/250-close-the-record-checks/
measure/brief.py` - a split session for any item question over the cap, a write session, then check groups packed by
load - with the tooling 250 built (`make check-bundle`, `make apply-edits`, `make canon`, the size cap, the guards).
Nothing here changes that process; a change to it is a feature of its own.

**The pages left** (250's T19, re-derived 2026-09-27 by `brief.fr002` / `fr006` / `over_cap_items`): `towns` (10
FR-002 items), `cities/river-cities` (8), `buildings` (7), `urban-features` (12, and 6 FR-006; four of its item
questions over the cap - split first), `ways` (1).

## Requirements (feature 250's, carried verbatim)

**FR-002 - the additional bare assertions the quote-checks named are footnoted.** Each quote-check report
ends with the real-world assertions it found carrying no footnote, per section; these were never on
242's derived inventory (242 FR-001), so 242 did not own them. Each ends in one of the three forms, by
the same pipeline as FR-001, and the count is DERIVED from the reports, never restated.

**FR-003 - the record-format VOCABULARY findings are answered.** Each term a report named as one a casual
reader would not know either gets a glossary entry (`l7r/diagram/interactive/assets/glossary.json`, then
`make glossary`; a term no page uses fails a test) or the sentence is rewritten in the reader's terms;
the two variants the reports named (`ochiba` firing on the manor named Ochiba; the hyphenated
`fire-gap`) are resolved.

**FR-004 - the record's history passages are moved into comments.** Every HISTORY finding the reports
name that 242 did not already move - what a sentence used to say, a correction and its date, where a
pointer came from - becomes an HTML comment or is deleted, so nothing visible says what the record used
to say (feature 209).

**FR-005 - the registry's citation lines carry English titles.** The record-format reports found
registry citation lines whose titles are given only in Japanese or Chinese; each carries an English
rendering marked as this project's translation, in one mechanical sweep, so `record-format` can skip the
registry band thereafter.

**FR-006 - the items the work list cannot locate are confirmed or worked.** 242's `measure/worklist.py`
reports an FR-001 item as NOT-LOCATED, TOO-SHORT or AMBIGUOUS when it cannot find the item's sentence
on the page - the passes rewrote or corrected those sentences. 242's handoff record says every
inventory item was in a reader batch, and 242's closing session did not verify that item by item
(242 spec D7). Each is found by hand from its section and either confirmed as carrying its note or
worked as a bare item under FR-002. (The LOCATED class 242's handoff counted at line level was
retired by the sentence-level test; the few that remained were checked by hand under 242.)

**FR-007 - the checks the changed material owes.** `quote-check` and `record-format` over every changed
page, scoped to the changed notes and sections where the page was checked whole by 242;
`source-applicability` over every new registry key before its numbers reach a map or a rule; every
`entry-drift` pair `scripts/_entry_owed.py` names answered - dispatched, or discharged by one recorded
`ENTRY_DRIFT_OK="<reason>"` covering a sweep in which no finding moved, with the measurement 242 used
(`specs/242-cite-the-unfootnoted-assertions/measure/prose_moved.py`) as the ground.

**FR-008 - the documents that cannot be read go to the download list** in the GM's format, appended at
the end of `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md` (the rule is in
`.claude/skills/diagram/research/CLAUDE.md`, "A source the GM is to fetch by hand goes on the download
list, in the GM's format, appended at the END").

**FR-009 - the closing report** states, per class above, what closed and what did not, and per unclosed
item whether it was searched and failed or never searched.

## Success criteria

- Every page above worked to 250's standard: FR-002 items in one of the three forms, FR-006 items confirmed or worked,
  its checks run and applied, its owed modals answered.
- The sweeps (FR-003 to FR-005) done; the download list grown (FR-008); the closing report (FR-009).
