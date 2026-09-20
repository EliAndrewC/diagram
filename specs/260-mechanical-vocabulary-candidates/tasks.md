# Tasks - feature 260, the prepass names the words

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D4). Research: [`research.md`](research.md)
(R1-R5). American spellings, hyphens only.

**No task here is `research: physical`.** The feature changes what a script prints and what a check is
asked to do; no research text is edited and no historical question is reopened.

## Phase 0 - the baseline

- [x] T01 The regression baseline: `make done` on unmodified code, recorded as `m:baseline-done`; every
      later failure checked against it before it is called new
      research: rendering
      measure: the run's own output
      verify: DONE. Baseline is the green make done at 26f8bb4f, feature 259 landing, 124 s, dev/run-log/20260920T201939015530. No failure in this feature needed checking against it: every run since has been green.
- [x] T02 R4-before: the prepass's wall time as it stands, and the baseline's test phase
      research: rendering
      verify: DONE. R4-before: make record-prepass PAGE=ways SECTION=010 three times in a detached worktree at 26f8bb4f - 0.11, 0.11, 0.10 s.

## Phase 1 - the candidate pass (FR-001 to FR-006; D1, D2)

- [x] T03 RED: a test asserts that the candidate pass over the `ways` 010 entry raises `girder` and not
      `and`, and fails for want of the function
      research: rendering
      verify: DONE. RED first: the ways-010 test asserted girder raised and and not, and failed for want of rare_words.
- [x] T04 The pure function: the section's visible words with `<code>` spans dropped, minus the variant
      index, minus the registry keys, kept where the corpus frequency is at most 2, each with its
      count. Tests on plain inputs - no filesystem
      research: rendering
      verify: DONE. rare_words is pure over four inputs; 13 tests in tests/tooling/test_record_prepass_and_size_table.py run on plain dicts, no filesystem. Fails closed on an empty corpus.
- [x] T05 `make record-prepass` prints the list under its own heading, with the count beside each word
      and the cutoff stated; proven on `ways` 010, where it reports 34 where it reported 0, over the text
      the CHECK reads - the question fragment and its notes, not the assembled page's section
      research: rendering
      measure: the command's own output against `measure.py R2`
      verify: DONE. make record-prepass PAGE=ways SECTION=010 prints WORDS TO RULE ON with 34 candidates where it printed 0, over the fragment AND its notes - the text the check reads. 27 of the 34 come from the notes.
- [x] T06 **The sweep**: the pass runs over every entry of the record without raising on any registry
      key and without taking longer than FR-010's bar; the largest and smallest lists are recorded
      research: rendering
      measure: the run over all 1,479 fragments
      verify: DONE. measure.py R4, both readings: 19 question pages / 321 sections / 5,584 candidates / median 13 / largest 115 / 0 keys / 0.83 s, and every html but assets/ / 1,511 files / 3,766 sections / 32,836 candidates / 0 keys / 4.01 s. SC-003 claimed on the wider one.

## Phase 2 - what the list is for (FR-007 to FR-009; D3, D4)

- [x] T07 `record-format`'s contract: rule on every candidate, say which verdict each got, add what the
      list did not raise, and the three things it cannot reach (a phrase, a record-common word, and why
      an empty list is not an empty question)
      research: rendering
      verify: DONE. record-format.md carries Rule on the WORDS TO RULE ON list - three verdicts, the two blind spots, and that an empty list is not an empty question.
- [x] T08 `research/CLAUDE.md` carries the acceptance bar that replaces "the same findings", and says
      that features 258 and 259's specs keep the old one because a spec records what was decided when
      research: rendering
      verify: DONE. research/CLAUDE.md states the new bar and names the TIER rule as a different decision deliberately left.

## Phase 3 - landing

- [x] T09 **The run that says whether this worked**: `record-format` over `ways` 010 with the candidate
      list, judged by the new bar - every candidate ruled on - and compared with feature 259's three
      runs on the same entry. Recorded as R5
      research: rendering
      measure: the dispatch's own report against the candidate list
      verify: DONE. R5: one record-format run, 34 of 34 ruled on (11 propose, 3 defined inline, 20 ordinary) and 6 beyond the list, three of them exactly the ones R3 named unreachable.
- [x] T10 `make done` green; every failure checked against T01
      research: rendering
      verify: DONE. make done green - already-verified in 0 s, which is correct: scripts/, tests/tooling/, docs and specs/ are deliberately not gate keys. The change own verification is make quick clean plus the whole tooling file, 13 passed.
- [x] T11 R4-after: the prepass's wall time with the pass in it, against FR-010's bar
      research: rendering
      verify: DONE. R4-after: 0.48, 0.47, 0.48 s an invocation against FR-010 5 s bar; the pass costs about 0.37 s, nearly all of it the corpus walk.
- [x] T11a **FR-011, SC-007**: the GM is told what was substituted for the mechanism they approved and
      what the approved bar now certifies - that "every candidate ruled on" reaches only the words a
      word-level rarity filter can see, so a check missing every phrase and every record-common term
      clears it in both conditions - and the surviving statements of the old bar are named to them for
      what each one governs: the TWO about a model-tier downgrade, left as the GM's doctrine, and the
      ONE about scoping that this feature changed rather than leaving as a second bar on one decision
      research: rendering
      verify: DONE. Sent 2026-09-20, after escalation-check judged the draft and found section 3 stale (it still called all three survivors tier rules, having been drafted before the efficiency-tooling edit). Delivered with the two-and-one split, the runtime cost, the one-run qualifier on R5, and the decision named: leave the two tier statements or have a later feature restate them.
- [x] T12 Stop-work: commit, `scripts/sync-with-main.sh done`
      research: rendering
      verify: DONE. Committed in the clone; sync-with-main.sh done runs in this same turn, DIRECT route - no engine code in the delta.
