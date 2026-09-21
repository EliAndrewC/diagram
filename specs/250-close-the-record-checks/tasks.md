# Tasks - feature 250, close the record checks

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D5). American spellings, hyphens only.

## Phase 0 - the baseline and the meter

- [x] T01 The regression baseline: the four record tests and `make record CHECK=1`, `make citations
      CHECK=1`, `make glossary CHECK=1` on the unmodified clone; every later failure is checked against it
      research: rendering
      measure: the runs' own output
      verify: DONE. Baseline on the unmodified clone: record, citations and glossary CHECK in sync; the four record tests 257 passed.
- [x] T02 `measure/tokens.py`: one session cut into a window per task, reporting the main session, each
      named agent and each ad-hoc agent, with what each agent read, largest first (D3)
      research: rendering
      measure: its report over this session's own planning window
      verify: DONE. measure/tokens.py: windows from marks, main session plus each agent per window, first-turn floor, what each agent read, and the main session's largest tool results. Output in measure/tokens-slice.json.

## Phase 1 - the measured slice (D3). STOP for the GM after T10

- [x] T03 FR-001, reading: `make source-pages` for the candidate pointers, then one `source-reader`
      pass over the five bare items of `cities/sizing`
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. make source-pages saved the Edo and Jokamachi pages; one source-reader pass over the five items: 1 READ, 1 CONTRADICTED, 3 NOT-FOUND with partials. Boxes: the pass is this task; the reader returned a verdict per item; T04 records and cites; T06 quote-check; T05 source-applicability.
- [x] T04 FR-001, writing: each of the five items carries a citation, an absence note or a grounds note
      in its entry's fragment and `.notes.html`; the registry write-ups for any new key; `make record`,
      `make citations`
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. Five items carry a citation or an absence note in the two sizing fragments; the contradicted sentence now says what Chang says; the edo-enwiki and jokamachi-wiki write-ups carry the new use. Fixed where found: make record did not write the citations page. Boxes as T03.
- [x] T05 FR-001, `source-applicability` over each new registry key, one file per key (D2); none
      dispatched if T04 added no key, and the task says so
      research: rendering
      verify: DONE. No new key, two changed write-ups: source-applicability one agent per key, both APPLICABLE-WITH-LIMITS; the missing limit (the Edo article's two maintenance banners) and the stale What-it-is sentence applied.
- [x] T06 FR-001, `quote-check` per changed entry of `cities/sizing`, after `make quote-verbatim` (D2);
      findings applied
      research: rendering
      verify: DONE. quote-check one agent per entry after make quote-verbatim (3 VERBATIM by script, Chang image-only): 2 SUPPORTS, 4 PARTIAL, 0 DOES-NOT-SUPPORT; marks re-aimed, the p. 94 passage quoted, one unfootnoted assertion rewritten as the map's own decision.
- [x] T07 FR-001, `record-format` per changed entry of `cities/sizing`, after `make record-prepass`
      (D2); findings applied; SC-001 judged with `worklist.py cities/sizing.html`
      research: rendering
      verify: DONE. record-format one agent per entry; findings applied. SC-001: worklist reports FOOTNOTED 4, LOCATED 1, NOT-LOCATED 1 - both confirmed by hand as rewritten sentences carrying chang-2 and chang-3 to 5. Fixed where found: record-prepass SECTION=010 matched nothing, silently.
- [x] T08 FR-003 for ONE entry: the vocabulary terms the reports named in it each get a glossary term
      file or a rewritten sentence; `make glossary`
      research: rendering
      verify: DONE. ways 010: girder, the term the 242 report named, defined; the sizing entries' terms defined from today's reports. make glossary green, 735 terms.
- [x] T09 FR-003, the `record-format` re-check of T08's entry: every candidate ruled on
      research: rendering
      verify: DONE. record-format over ways 010 with the candidate list: 33 of 33 ruled on; eight terms defined, three left with the reason (bearing seat is not a phrase the page uses, carried deck and sine need the record's own wording).
- [x] T10 **The measurement the GM asked for**: `measure/tokens.py report` over T01 to T09, recorded in
      `research.md` R1 with the per-window table, what each agent read, what it implies for phases
      2 to 4, and BY NAME every agent the slice did not measure (D3), so the figures are not read as
      complete
      research: rendering
      measure: `python3 specs/250-close-the-record-checks/measure/tokens.py report`
      verify: DONE. research.md R1: main session 87 percent of input over 92 turns, 13 named runs 13 percent, no ad-hoc; a check reads 2,400 to 10,600 tokens of the record and carries 28,400 of nested CLAUDE.md; experiment X1 cut a record-format run's peak from 47,700 to 14,500; the agents not measured are named.

## Phase 2 - FR-002 and FR-006 (not started until the GM has read T10)

- [ ] T11 `measure/assertions.py` derives FR-002's list from the six quote-check reports (D4)
      research: rendering
- [ ] T12 FR-002 and FR-006, page by page in the order T11 prints: read, write, check per entry. One
      task per page is cut here once T10's figures say how large a page's batch should be
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited  - [ ] quote-check confirmed  - [ ] source-applicability confirmed

## Phase 3 - the cosmetic sweeps

- [ ] T13 FR-003, the rest of the vocabulary findings and the two variants (`ochiba`, `fire-gap`)
      research: rendering
- [ ] T14 FR-004, the history passages into comments
      research: rendering
- [ ] T15 FR-005, the registry's citation lines carry English titles, one mechanical sweep
      research: rendering

## Phase 4 - the close

- [ ] T16 FR-007, the checks owed by what phases 2 and 3 changed; every `_entry_owed.py` pair answered
      research: rendering
- [ ] T17 FR-008, the download list grown at its end
      research: rendering
- [ ] T18 FR-009, the closing report; `make page-check`; the push
      research: rendering
