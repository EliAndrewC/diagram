# Tasks - feature 429: four rules that lived only in session memories, made into tooling

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md).

## Occasions

none: tooling only - hooks, a measurement script and docs; no drawing or placement code changes.

- [ ] T01 No engine edit while a map review runs: `engine-freeze-hooks.sh` + `lib/hm_engine_freeze.py`, wired on Edit/Write/NotebookEdit (FR-001, SC-001)
      research: rendering
- [ ] T02 A question to the GM goes through escalation-check: `escalation-hooks.sh` `ask_unfiltered` + `lib/hm_gm_question.py`, measured in research.md R1 (FR-002, SC-002)
      research: rendering
- [ ] T03 No write in gm-assistant's main tree: `gm-tree-hooks.sh` + `lib/hm_gm_tree.py`, wired on Bash/Edit/Write/NotebookEdit (FR-003, SC-003)
      research: rendering
- [ ] T04 A reroll says whether it moved the map against HEAD: `make maps-moved`, the line at the end of `make map` (FR-004, SC-004)
      research: rendering
- [ ] T05 The records and the docs: guard-table rows, the escape census, the dev-loop lines (FR-005, SC-005)
      research: rendering
- [ ] T06 Found while working: `make guard-edit` granted no hook in `scripts/hooks/` (plan T06, D171)
      research: rendering
