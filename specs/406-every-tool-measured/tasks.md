# Tasks - feature 406: every tool measured by what it does

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md).

- [x] T01 The usage-log helper and the tool registry: one helper every silent tool records through, and one registry of what records (FR-002) [lands-open]
      research: rendering
      verify: DONE. usage_log.py (record/exited/goals, errors swallowed, no bytecode written) and scripts/tool-registry.json (held in step by check-tool-signals); tests/tooling/test_usage_log.py green
- [x] T02 A make target's outcome recorded: the event log records a failed tool call beside a succeeded one, and the runs it cannot see record through the helper (FR-003) [lands-open]
      research: rendering
      verify: DONE. the event-log hook wired on PostToolUseFailure records a failed call; the Makefile's parse-time line records every make goal (make -n/-q skipped); idle-tests records its outcome; test_event_log.py and test_usage_log.py green
- [x] T03 The silent tools record: every refusing check, the two silent hooks and the automatic steps call the helper, each in the registry (FR-002) [lands-open]
      research: rendering
      verify: DONE. 18 gate checks, speckit-todo, ratchet, one-gate wrapped; automatic steps (planhold-restore, tick-archive, land-tooling-docs/-merge, clone-sync-merge, ledger-owed-write) record; the rest name their record with TOOL_RECORD; check-tool-signals clean on the repo
- [x] T04 `make tool-yield`: every wired hook, refusing check, make target, review check and logged step, with its uses, interventions, likely misfires, too new or no outcome record (FR-001) [lands-open]
      research: rendering
      verify: DONE. make tool-yield lists guards, checks (entry points followed through prerequisites and MAKE), targets, reviews and steps with uses, interventions, misfires, too new / no outcome record; tests/tooling/test_tool_yield.py (9) green
- [x] T05 The rule: `make hooks-test` refuses a hook or check that records nothing without naming its record, and a helper call or registry entry the other lacks (FR-004) [lands-open]
      research: rendering
      verify: DONE. scripts/gates/check-tool-signals.py run by make hooks-test (roster companion and a live run): refuses a silent hook or check, an unregistered call, an uncalled entry; tests/hooks/test-check-tool-signals.sh 10/10 green and red (6 fail) on a copy without its refusal
- [x] T06 `make fix-yield` on the new numbers: each arbiter fix by the tools its change touched, since it was made; the step-back reads it (FR-005) [lands-open]
      research: rendering
      verify: DONE. make fix-yield reads each fix by its tools since it was made: tools from the first code commit (note hash, exact trigger, test file in the window), the note's files/targets otherwise; D166 readings; fix_measure and the command rate retired; step-back reads the same; test_fix_yield.py green
- [x] T07 The 22 fixes judged: each a recorded judgment citing its numbers, for the GM's review (FR-005, SC-003) [lands-open]
      research: rendering
      verify: DONE. specs/406-every-tool-measured/fix-judgments.md: the 22 of the hour-37 table, each with its tools and numbers since it was made; all too new to say (made 10-17..19, readable 10-24..26)
- [x] T08 The close: the feature report and its retro rows [lands-open]
      research: rendering
      verify: DONE. make feature-report F=406 WRITE=1 written (report.md); retro.md holds a row for each of T01-T08; both committed (c-406 T08 commit) just before this task-start, which the wording-only tick needed

- [ ] GM review (make gm-reviewed F=406) [lands-open]
