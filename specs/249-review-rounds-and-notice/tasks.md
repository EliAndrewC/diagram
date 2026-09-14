# Tasks - 249 review rounds read the diff, and the notice speaks on any single call

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - tooling, nothing
physical behind it.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code; the plan
      reviewed (MODE 4) before any tick
      research: rendering
      verify: DONE. DONE. spec-fidelity: round 1 CHANGES REQUIRED (4 items), round 2 CHANGES REQUIRED (1, the discriminator precedence), round 3 FAITHFUL on the diff alone; plan review MODE 4 CLEAR at round 1, 14 decisions all within, plan-review.json recorded by the subagent
- [x] T02 the batching notice on any single call, and its suite case (FR-001)
      research: rendering
      verify: DONE. DONE. batching-hooks.sh notice condition is CALLS==1 and N==REARM-1 only; block unchanged; test-batching-hooks.sh 2c (folded single call) and 2d (backgrounded single call) receive the notice; 46 checks green
- [x] T03 `scripts/review-round-hooks.sh`: the rewrite, the first-round snapshot, the history-without-
      snapshot line, the no-feature pass, the escape (FR-002 to FR-004); wired in settings
      research: rendering
      verify: DONE. DONE. review-round-hooks.sh (log and print) + _hm_review_round.py judge (the decision): MODE 2/3 first then MODE 4/PLAN REVIEW then MODE 1/EXCEPTION CHECK, other-mode and no-feature pass untouched, first dispatch snapshots silently, history-without-snapshot told once, rewrite prepends the preamble with the round within the pass (1 after a recovered FAITHFUL), the verdict from the newest matching subagent transcript else the Review history marked as a summary, the diff since the snapshot; REVIEW_ROUND_OK escape with the reason floor; wired on the Agent matcher in .claude/settings.json
- [x] T04 `scripts/test-review-round-hooks.sh` and the census rows (FR-006); `make hooks-test` green
      research: rendering
      verify: DONE. DONE. test-review-round-hooks.sh 41 passed on a fixture clone with fixture transcripts (pass-throughs, silent first snapshot, the rewrite's preamble/diff/verbatim verdict/unchanged tail, the advancing snapshot, the pass restart, the summary fallback, the escape and its refusal); census rows for no-feature, other-mode, review-round-ok and REVIEW_ROUND_OK-no-reason, the token classified; make hooks-test green (7 suites ran, 18 unchanged)
- [x] T05 the agent contract (FR-005) and the record (FR-007); `make quick` green; land DIRECT (FR-008)
      research: rendering
      verify: DONE. DONE. spec-fidelity.md MODE 3 carries the GM's 2026-09-14 ruling, says the tooling supplies the preamble, and step 3 is the bounded grep; CLAUDE.md batching row amended and a review-round row added; docs/efficiency-tooling.md both rows; hook header states the defect and the ruling; make quick green (232 passed); landing DIRECT
