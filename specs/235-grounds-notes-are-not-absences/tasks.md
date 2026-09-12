# Tasks - feature 235

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md).

## Phase 1 - teach the checkers before writing anything (FR-008)

- [x] T01 the constitution's Principle XII: the third form, the MINOR version bump, the GM's ruling recorded
      research: procedure
      verify: DONE. DONE. the constitution's Principle XII amended to THREE footnote forms, v2.25.0 -> v2.26.0 (a MINOR by its own policy: an existing principle is materially expanded), with the GM's words of 2026-09-12 quoted as the ruling. The prohibition travels with the form: a grounds note may never carry a claim about the world nor a sentence the record labels a guess
- [x] T02 `research/CLAUDE.md`: the grounds note, the closed list, which reasons are exemplified, the settled state, and the "exactly two forms" sentence corrected
      research: procedure
      verify: DONE. DONE. research/CLAUDE.md carries the third form where the next session writing an entry will read it - the closed list of six, that only two are exemplified today, that using an unexemplified one takes a written argument, that a converted note keeps its search in a comment, and the settled state with its two-pass bar and the base rate that argues against using it
- [x] T03 `tests/interactive/test_footnotes.py`: `footnote_form()` returns the new kind, AND its consumer accepts a grounds note owing no key, no link and no quotation
      research: procedure
      verify: DONE. DONE. tests/interactive/test_footnotes.py: footnote_form() returns 'grounds' and validates the reason against the closed list, AND its consumer accepts one - naming the classifier alone was the near miss, since the first grounds note would have failed the consumer whatever the classifier returned. The classifier's own string self-test is green
- [x] T04 `.claude/agents/quote-check.md`: its absence-note rule gains the grounds note, so it stops reporting one as a missing citation
      research: procedure
      verify: DONE. DONE. the quote-check agent knows the grounds note, reports it as such and checks nothing for it, and is told the one thing it SHOULD report - a grounds note on a claim about the world or on a sentence the record labels a guess, which is the failure the form exists to prevent

## Phase 2 - the census (FR-005)

- [x] T05 the footnote census: open absences, settled absences, grounds notes and citations, per page and in total, with a test that its numbers are the numbers in the files; 100% covered
      research: procedure
      verify: DONE. DONE. the footnote census counts cited/grounds/ABSENT/settled per page and in total, sharing the ENGINE's classifier (moved out of the test file into interactive/citations.py + sources.py, research R2); tests/tools/test_footnote_census.py holds the four kinds apart, that every citations page is walked exactly once, that the total equals a second count taken from the raw files, and both report branches
- [x] T06 the census run and recorded BEFORE any note changes, on this tree (SC-003)
      research: procedure
      verify: DONE. DONE. the BEFORE census run and recorded in research.md R1 with its per-page table: 969 cited, 0 grounds, 84 ABSENT, 0 settled, taken before any note was converted

## Phase 3 - the notes (FR-006, FR-007)

- [x] T07 `cities/sizing.html` fn-2 converted to a grounds note under `measured on our own maps`, its search kept in a comment (FR-001a)
      research: rendering
      verify: DONE. DONE. cities/sizing.html fn-2 is a grounds note under 'measured on our own maps' - the 5-15% band is read off Tango's 9% and Minami's 15.5%, and the dated search that established there is nothing to find is kept in the comment beside the reason (FR-001a)
- [x] T08 the three arguable notes argued at their own pages in writing - `fields.html` fn-85, `religion-and-death.html` fn-78 and fn-49 - each converting or staying on that argument
      research: rendering
      verify: DONE. DONE. all three argued at their own pages in an HTML comment at the note, and all three REFUSED: fields fn-85 (the identity of the lowest bund with the collector's top-of-bank is contingent, not definitional, and land-consolidation standards could settle it), religion-and-death fn-78 (a report of a reading is what an absence note already says; exhausting it would make it SETTLED, not grounds), fn-49 (the section credits the GM's ruling of 2026-07-21, so it rests on 'this project's decision', barred here; and the paragraph is the rule the map FOLLOWS, so the figures were chosen and then drawn)
- [x] T09 the fourteen confirmed as OPEN absence notes, thirteen under FR-003's first clause and fn-75 under its second
      research: rendering
      verify: DONE. DONE. all fourteen carry a comment at the note naming the clause that keeps them in the backlog - thirteen under FR-003's first clause, religion-and-death fn-75 under the second
- [x] T10 the two session-addressed sentences moved into comments, both footnotes left in place as open absences
      research: rendering
      verify: DONE. DONE. river-cities' 'Do not fix it' and defenses' 'which is why it is really a rule about what may NOT stand there' are HTML comments; the reader-facing half of the defenses sentence stays, and fn-17 and fn-18 are untouched open absence notes

## Phase 4 - verification and landing

- [x] T11 `record-format` on every changed page, including its new duty on the grounds notes; findings applied
      research: procedure
      verify: DONE. DONE. six record-format agents read every page and every citations page this feature and 232 changed. Their findings are applied: about 130 edits taking sheet-pixel figures, fetch verdicts, engine vocabulary and the document's own history out of the reader's text; 43 glossary terms added and two rows that were firing the WRONG definition fixed; three write-ups that ended mid-sentence repaired; a checker's NOTE removed from inside a quotation. Every one of them read cities/sizing fn-2, the record's only grounds note, and none reported it as carrying a claim about the world or a labeled guess
- [ ] T12 `quote-check` on every changed page, confirming it no longer reports a grounds note as a defect
      research: procedure
- [x] T13 the census run AFTER, and the delta stated with its three numbers (SC-003)
      research: procedure
      verify: DONE. DONE. the AFTER census on the same tree: 969 cited, 1 GROUNDS, 83 ABSENT, 0 settled, against 969 / 0 / 84 / 0 before. The delta is this feature's own: one note left the backlog because it owes no source, and no note left it any other way
- [ ] T14 `make citations`; `make page-check` green
      research: procedure
- [x] T15 the closing report: what changed, the census delta, and the `research/README.md` correction OFFERED not applied
      research: procedure
      verify: DONE. DONE. closing-report.md written: what shipped, the census delta (969/0/84/0 -> 969/1/83/0), the honest headline that the record contained one instance of the defect rather than eighteen, the two sentences moved into comments with both footnotes kept, and THREE research/README.md corrections OFFERED and not applied - the binary this feature replaced, the SUMMARY-ONLY label feature 195 retired, and a pointer to SOURCES.md, a file that no longer exists and that no test catches because the retired-Markdown sweep exempts the README by name
- [ ] T16 `make done` green (detached); commit; `sync-with-main.sh done`
      research: procedure
