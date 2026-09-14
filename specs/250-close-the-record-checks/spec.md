# Feature 250 - close the record checks

**Status:** DRAFT, written 2026-09-14 by the session that closed feature 242, from that feature's handoff
record and closing report. Not yet reviewed; `spec-fidelity` before implementation (constitution XVI).

## Summary

Feature 242 footnoted every bare assertion on sixteen of its seventeen pages and every never-searched
absence note, and ran `quote-check`, `record-format` and `source-applicability` over the whole record.
The GM split it on 2026-09-14 (`request.md`): the footnoting and every finding that bears on honesty
landed with 242; what the checks surfaced beyond 242's derived work list, and what was cosmetic, is this
feature. The inputs are the thirteen verbatim reports under
`specs/242-cite-the-unfootnoted-assertions/handoff/reports/` and 242's `research.md` R12, which names
each deferred class and where its items are listed.

This feature writes no engine code beyond the glossary's data file, so its delta takes the DIRECT route
(D2).

## Functional requirements

**FR-001 - `cities/sizing.html` is footnoted.** The one page 242 did not reach: each of its bare items
(the work list is `specs/242-cite-the-unfootnoted-assertions/measure/worklist.py cities/sizing.html`)
goes through 242's pipeline - a `source-reader` pass, a note in one of the three forms (citation,
absence, grounds - 242's FR-004 defines them and its FR-003 forbids a note written from memory), the
registry write-ups for any new key, then `quote-check` and `record-format` over the page.

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
`.claude/skills/diagram/research/CLAUDE.md`, "A page the container cannot fetch is not thereby
unreadable").

**FR-009 - the closing report** states, per class above, what closed and what did not, and per unclosed
item whether it was searched and failed or never searched.

## Success criteria

- **SC-001** (FR-001) - `worklist.py cities/sizing.html` reports no LOCATED or NOT-LOCATED item.
- **SC-002** (FR-002) - every assertion listed at the end of the six quote-check reports carries one of
  the three forms, or the closing report names it as searched and failed.
- **SC-003** (FR-003) - no term the record-format reports named is without a glossary entry or a
  rewritten sentence; `make glossary` is green.
- **SC-004** (FR-004) - a `record-format` pass over the changed pages reports no HISTORY item.
- **SC-005** (FR-005) - no registry citation line's title is given only in Japanese or Chinese.
- **SC-006** (FR-006) - every item 242's `worklist.py` reported NOT-LOCATED, TOO-SHORT or AMBIGUOUS at
  242's close (its `research.md` R12) is confirmed or worked.
- **SC-007** (FR-007) - the verdicts are recorded in the task; `scripts/_entry_owed.py` names no
  unanswered pair at push.
- **SC-008** (FR-008) - Part 4 of the download list has grown only at its end, every entry with both links.
- **SC-009** (FR-009) - the closing report distinguishes searched-and-failed from never-searched.
- **SC-010** (spec-wide) - `make page-check` green and the push clean.

## Decisions recorded

**D1 - this feature is the deferred half of a split the GM made, not a second deferral.** Feature 242's
FR-011 said a split is proposed to the GM with a count rather than taken unilaterally; the GM made it
themselves on 2026-09-14 (`request.md`). What landed with 242 is everything that bore on honesty - a
footnote quoting text not on its page, a mark on the wrong sentence, a defect a reader sees, an
untranslated quotation. What is here is what the checks found beyond 242's derived list (FR-002),
what was cosmetic (FR-003 to FR-005), the one page 242 did not reach (FR-001), and the items of 242's
own list whose sentences its harness could no longer find - which 242's session disclosed as its own
addition to the cut, not the GM's (FR-006; 242 spec D7).

**D2 - research-only, DIRECT route.** The glossary data file is under `l7r/` but is data, not engine
Python; nothing here touches `l7r/**/*.py` or a pool generator.

## Review history

- none yet.
