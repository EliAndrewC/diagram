# Tasks - feature 429: four rules that lived only in session memories, made into tooling

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md).

## Occasions

none: tooling only - hooks, a measurement script and docs; no drawing or placement code changes.

- [x] T01 No engine edit while a map review runs: `engine-freeze-hooks.sh` + `lib/hm_engine_freeze.py`, wired on Edit/Write/NotebookEdit (FR-001, SC-001)
      research: rendering
      verify: DONE. tests/hooks/test-engine-freeze-hooks.sh 21/21: refused with a review mid tool call, awaiting a reply, stalled, or days old; passes after end_turn, finished meta, or TaskStop+ack; docs, tests, ci/ and non-review agents pass
- [x] T02 A question to the GM goes through escalation-check: `escalation-hooks.sh` `ask_unfiltered` + `lib/hm_gm_question.py`, measured in research.md R1 (FR-002, SC-002)
      research: rendering
      verify: DONE. tests/hooks/test-escalation-hooks.sh 31/31, section 9: the 10-25 shape refused once, a report and a quoted question pass, a filter since the GM's last message lets it through, an older filter does not; research.md R1 holdout 9 of 11 before fitting, 0 false alarms in 89, reproduced by hash on 1,435 messages
- [x] T03 No write in gm-assistant's main tree: `gm-tree-hooks.sh` + `lib/hm_gm_tree.py`, wired on Bash/Edit/Write/NotebookEdit (FR-003, SC-003)
      research: rendering
      verify: DONE. tests/hooks/test-gm-tree-hooks.sh 24/24: Edit/Write/NotebookEdit and sed -i, >>, 2>, &>, >|, tee, cp, relative writes into the main tree refused; clones, the rest of /host-l7r-repo, reads, copies out and quoted mentions pass; GM_TREE_OK escapes Bash; main-tree suite 84/84 after the >| fix
- [x] T04 A reroll says whether it moved the map against HEAD: `make maps-moved`, the line at the end of `make map` (FR-004, SC-004)
      research: rendering
      verify: DONE. tests/tooling/test_maps_moved.py 4/4 (one changed manifest named alone, none, --only from a gen, untracked counts); make maps-moved prints no pool manifest moved against HEAD on this clone
- [x] T05 The records and the docs: guard-table rows, the escape census, the dev-loop lines (FR-005, SC-005)
      research: rendering
      verify: DONE. docs/guards.md rows for the three guards; GM_TREE_OK in the escape census (test_guard_firing_log.py green in make hooks-test); l7r/diagram/CLAUDE.md points at make maps-moved and engine-freeze-hooks.sh; make hooks-test rc=0
- [x] T06 Found while working: `make guard-edit` granted no hook in `scripts/hooks/` (plan T06, D171)
      research: rendering
      verify: DONE. tests/hooks/test-guard-file-hooks.sh 53/53 with the scripts/hooks/ case, 52/53 on the unfixed pattern
- [x] T07 Amendment 1: offers are not questions but owe the significance test - `hm_gm_question.classify`, the OFFER refusal, escalation-check's offer section, R3 (FR-006, SC-006)
      research: rendering
      verify: DONE. tests/hooks/test-escalation-hooks.sh 34/34, section 10: an offer-only message refused once with the significance instruction, an ask with an offer refused as a question; research.md R3: asks 18 of 19, offer 1 of 1, 0 false alarms in 161, reproduced by the reviewer on 1,449 messages
