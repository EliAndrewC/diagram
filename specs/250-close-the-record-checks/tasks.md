# Tasks - feature 250, close the record checks

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D5). American spellings, hyphens only.

## Phase 0 - the baseline and the meter

- [ ] T01 The regression baseline: the four record tests and `make record CHECK=1`, `make citations
      CHECK=1`, `make glossary CHECK=1` on the unmodified clone; every later failure is checked against it
      research: rendering
      measure: the runs' own output
- [ ] T02 `measure/tokens.py`: one session cut into a window per task, reporting the main session, each
      named agent and each ad-hoc agent, with what each agent read, largest first (D3)
      research: rendering
      measure: its report over this session's own planning window

## Phase 1 - the measured slice (D3). STOP for the GM after T10

- [ ] T03 FR-001, reading: `make source-pages` for the candidate pointers, then one `source-reader`
      pass over the five bare items of `cities/sizing`
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
- [ ] T04 FR-001, writing: each of the five items carries a citation, an absence note or a grounds note
      in its entry's fragment and `.notes.html`; the registry write-ups for any new key; `make record`,
      `make citations`
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
- [ ] T05 FR-001, `source-applicability` over each new registry key, one file per key (D2); none
      dispatched if T04 added no key, and the task says so
      research: rendering
- [ ] T06 FR-001, `quote-check` per changed entry of `cities/sizing`, after `make quote-verbatim` (D2);
      findings applied
      research: rendering
- [ ] T07 FR-001, `record-format` per changed entry of `cities/sizing`, after `make record-prepass`
      (D2); findings applied; SC-001 judged with `worklist.py cities/sizing.html`
      research: rendering
- [ ] T08 FR-003 for ONE entry: the vocabulary terms the reports named in it each get a glossary term
      file or a rewritten sentence; `make glossary`
      research: rendering
- [ ] T09 FR-003, the `record-format` re-check of T08's entry: every candidate ruled on
      research: rendering
- [ ] T10 **The measurement the GM asked for**: `measure/tokens.py report` over T01 to T09, recorded in
      `research.md` R1 with the per-window table, what each agent read, and what it implies for phases
      2 to 4
      research: rendering
      measure: `python3 specs/250-close-the-record-checks/measure/tokens.py report`

## Phase 2 - FR-002 and FR-006 (not started until the GM has read T10)

- [ ] T11 `measure/assertions.py` derives FR-002's list from the six quote-check reports (D4)
      research: rendering
- [ ] T12 FR-002 and FR-006, page by page in the order T11 prints: read, write, check per entry. One
      task per page is cut here once T10's figures say how large a page's batch should be
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed

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
