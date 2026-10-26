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
- [x] T04 E(b) pop-ups that share a paragraph: the bamboo and shelter batch replayed and measured, then the cascade cut (D6; FR-005, SC-004)
      research: rendering
      verify: DONE. landed in batch T04+T07: T04: the pop-up cascade measured (R2: no shared paragraph in the bamboo/shelter batch, 15 of 18 later rounds found real errors, 17 shared paragraphs in 51 places of 293 pop-ups); FR-005 (b) waived by the round arbiter (ask:432-t04-shared-paragraphs), nothing built; T07: FR-007's search re-run finds no text left saying every ruling reaches the GM (only docs/container.md's unrelated grant script); constitution 2.32.2; report.md written; spec FAITHFUL after the waiver
- [x] T05 E(a) claims after a page edit: the 0081 edit's triage measured, then the triage narrowed where the measure shows (D7; FR-005, SC-004)
      research: rendering
      verify: DONE. landed: make claims-triage clears every claim owed a triage only by a page move whose rested-on blocks stand (row field cleared), the rest triaged as before (no-rests rows, code and section triages); test_claims_scoping 23/23 (red on the old claims.py), test_claims_index 36, test_known_drift 12; R3: 7 findings in 5,304 re-checks priced, ruled not material (ask:432-t05-triage-price); the 0081 edit's triage 271 -> 35
- [x] T06 The backlog cleared with the GM's words; 374#60, 385#40 and 397#10 carried on as kept questions (D8; FR-006, SC-005)
      research: rendering
      verify: DONE. landed: all 465 open rows marked reviewed with the GM's words (36 features; 385, 407, 412 and 413 row by row, their boxes held by their own implementation check); 374#60, 385#40 and 397#10 carried as kept questions 374#90, 385#107, 397#11; make gm-review lists exactly 3 decisions and 0 rows to review; test_gm_review 12/12 (a new row reopens a ticked box)
- [x] T07 The texts that say what reaches the GM (FR-007's search), the report and the close (D9; FR-007)
      research: rendering
      verify: DONE. landed in batch T04+T07: T04: the pop-up cascade measured (R2: no shared paragraph in the bamboo/shelter batch, 15 of 18 later rounds found real errors, 17 shared paragraphs in 51 places of 293 pop-ups); FR-005 (b) waived by the round arbiter (ask:432-t04-shared-paragraphs), nothing built; T07: FR-007's search re-run finds no text left saying every ruling reaches the GM (only docs/container.md's unrelated grant script); constitution 2.32.2; report.md written; spec FAITHFUL after the waiver
