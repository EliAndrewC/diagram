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

**The pages left** (250's T19, and the FR-006 work 250's T19 did not name; re-derived 2026-09-27 by `brief.fr002` /
`fr006` / `over_cap_items` over every page): `towns` (10 FR-002 items), `cities/river-cities` (8), `buildings` (7),
`urban-features` (12, and 6 FR-006 items; five of its item questions over the cap - 010, 020, 030 and 060 with FR-002
items, 050 with an FR-006 item - split first), `ways` (1), and `cities/capitals` (0 FR-002 items, 7 FR-006 items -
242's R12 items 43 to 46 and 84 to 86, which 250's T19 missed because its list was built from the pages with FR-002
items).

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

## Success criteria (feature 250's SC-002 to SC-010, carried verbatim; SC-002 and SC-006 limited to the pages above)

- **SC-002** (FR-002) - every assertion listed at the end of the six quote-check reports carries one of
  the three forms (an assertion for which no readable source is found carries an ABSENCE note; one that
  is not a real-world assertion carries a GROUNDS note); FR-009's residue is never a way past this.
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

## Review history

- **Round 1 (2026-09-27), `spec-fidelity`: CHANGES REQUIRED**, three items. (1) `cities/capitals` is missing from
  the pages left: `brief.fr006('cities/capitals')` gives 7 items (6 NOT-LOCATED, 1 TOO-SHORT), the same 7 as
  242's R12 table, which 250's SC-006 names, and no task in 250 or 265 works them. Add it as an FR-006-only page
  with its own task. (2) `urban-features` has five questions over the cap, not four: `over_cap_items` gives 010,
  020, 030 and 060 (FR-002 items) and 050 (an FR-006 item). (3) T10 cuts FR-007 down to the owed pairs, and the
  success criteria drop 250's SC-003, SC-004, SC-005, SC-008 and SC-009. FR-007 needs `quote-check` and
  `record-format` over the sections the sweeps T06 to T08 change, plus `source-applicability` over new keys, and
  250's criteria should be carried verbatim for the requirements carried here.
  Applied (2026-09-27): all three - `cities/capitals` added as an FR-006-only page (T06); `urban-features`' five
  over-cap questions named; T11 carries FR-007 whole, and the success criteria are 250's SC-002 to SC-010 verbatim.
