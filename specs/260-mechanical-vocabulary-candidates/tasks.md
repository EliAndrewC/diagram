# Tasks - feature 260, the prepass names the words

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D4). Research: [`research.md`](research.md)
(R1-R5). American spellings, hyphens only.

**No task here is `research: physical`.** The feature changes what a script prints and what a check is
asked to do; no research text is edited and no historical question is reopened.

## Phase 0 - the baseline

- [ ] T01 The regression baseline: `make done` on unmodified code, recorded as `m:baseline-done`; every
      later failure checked against it before it is called new
      research: rendering
      measure: the run's own output
      verify:
- [ ] T02 R4-before: the prepass's wall time as it stands, and the baseline's test phase
      research: rendering
      verify:

## Phase 1 - the candidate pass (FR-001 to FR-006; D1, D2)

- [ ] T03 RED: a test asserts that the candidate pass over the `ways` 010 entry raises `girder` and not
      `and`, and fails for want of the function
      research: rendering
      verify:
- [ ] T04 The pure function: the section's visible words, minus the variant index, minus the registry
      keys, kept where the corpus frequency is at most 2, each with its count. Tests on plain inputs -
      no filesystem
      research: rendering
      verify:
- [ ] T05 `make record-prepass` prints the list under its own heading, with the count beside each word
      and the cutoff stated; proven on `ways` 010, where it reports 34 where it reported 0, over the text
      the CHECK reads - the question fragment and its notes, not the assembled page's section
      research: rendering
      measure: the command's own output against `measure.py R2`
      verify:
- [ ] T06 **The sweep**: the pass runs over every entry of the record without raising on any registry
      key and without taking longer than FR-010's bar; the largest and smallest lists are recorded
      research: rendering
      measure: the run over all 1,479 fragments
      verify:

## Phase 2 - what the list is for (FR-007 to FR-009; D3, D4)

- [ ] T07 `record-format`'s contract: rule on every candidate, say which verdict each got, add what the
      list did not raise, and the three things it cannot reach (a phrase, a record-common word, and why
      an empty list is not an empty question)
      research: rendering
      verify:
- [ ] T08 `research/CLAUDE.md` carries the acceptance bar that replaces "the same findings", and says
      that features 258 and 259's specs keep the old one because a spec records what was decided when
      research: rendering
      verify:

## Phase 3 - landing

- [ ] T09 **The run that says whether this worked**: `record-format` over `ways` 010 with the candidate
      list, judged by the new bar - every candidate ruled on - and compared with feature 259's three
      runs on the same entry. Recorded as R5
      research: rendering
      measure: the dispatch's own report against the candidate list
      verify:
- [ ] T10 `make done` green; every failure checked against T01
      research: rendering
      verify:
- [ ] T11 R4-after: the prepass's wall time with the pass in it, against FR-010's bar
      research: rendering
      verify:
- [ ] T11a **FR-011, SC-007**: the GM is told what was substituted for the mechanism they approved and
      what the approved bar now certifies - that "every candidate ruled on" reaches only the words a
      word-level rarity filter can see, so a check missing every phrase and every record-common term
      clears it in both conditions - and the three statements of the old bar this feature does not
      change are named to them
      research: rendering
      verify:
- [ ] T12 Stop-work: commit, `scripts/sync-with-main.sh done`
      research: rendering
      verify:
