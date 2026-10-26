# Tasks - feature 432: the GM-review queue holds only what is his

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md).

## Occasions

none: tooling only - the review queue's scripts, hooks, agent contracts and docs; no drawing or placement code changes.

## Tasks

- [x] T01 The question record and one source for held decisions: `gm-review.jsonl` rows of kind `question` (owed, kept, cut), `make gm-escalated`, `held()` reads kept questions only (D1, D2; FR-002, FR-004, SC-003)
      research: rendering
      verify: DONE. landed in batch T01+T02+T03: T01: question rows owed/kept/cut, make gm-question and gm-escalated, the GM's decisions read from kept questions alone, an override's Held flag or held key no decision (test_gm_review 11/11); T02: only for_gm (any trigger) and declined fixes reach the GM, as owed questions, prose handing him a decision refused without for_gm (test_hm_arbiter 41, test_arbiter_fix 20, test_checkpoint 19); T03: a push with an owed question refused (push_checks gm-questions), a kept question not named in the final message refuses the turn's end once (test-escalation-hooks 38/38)
- [x] T02 What the arbiter queues: only `for_gm` (any trigger) and declined fixes, as owed questions; fixes made and every other ruling stay in `arbiter.jsonl`; a ruling handing the GM a decision without `for_gm` refused (D3, D4; FR-001, FR-003, SC-001, SC-002)
      research: rendering
      verify: DONE. landed in batch T01+T02+T03: T01: question rows owed/kept/cut, make gm-question and gm-escalated, the GM's decisions read from kept questions alone, an override's Held flag or held key no decision (test_gm_review 11/11); T02: only for_gm (any trigger) and declined fixes reach the GM, as owed questions, prose handing him a decision refused without for_gm (test_hm_arbiter 41, test_arbiter_fix 20, test_checkpoint 19); T03: a push with an owed question refused (push_checks gm-questions), a kept question not named in the final message refuses the turn's end once (test-escalation-hooks 38/38)
- [x] T03 The door enforced: a landing with an owed question refused; a question kept since the GM's last message and not named in the final message refuses the turn's end once (D5; FR-002, SC-002)
      research: rendering
      verify: DONE. landed in batch T01+T02+T03: T01: question rows owed/kept/cut, make gm-question and gm-escalated, the GM's decisions read from kept questions alone, an override's Held flag or held key no decision (test_gm_review 11/11); T02: only for_gm (any trigger) and declined fixes reach the GM, as owed questions, prose handing him a decision refused without for_gm (test_hm_arbiter 41, test_arbiter_fix 20, test_checkpoint 19); T03: a push with an owed question refused (push_checks gm-questions), a kept question not named in the final message refuses the turn's end once (test-escalation-hooks 38/38)
- [ ] T04 E(b) pop-ups that share a paragraph: the bamboo and shelter batch replayed and measured, then the cascade cut (D6; FR-005, SC-004)
      research: rendering
- [ ] T05 E(a) claims after a page edit: the 0081 edit's triage measured, then the triage narrowed where the measure shows (D7; FR-005, SC-004)
      research: rendering
- [ ] T06 The backlog cleared with the GM's words; 374#60, 385#40 and 397#10 carried on as kept questions (D8; FR-006, SC-005)
      research: rendering
- [ ] T07 The texts that say what reaches the GM (FR-007's search), the report and the close (D9; FR-007)
      research: rendering
