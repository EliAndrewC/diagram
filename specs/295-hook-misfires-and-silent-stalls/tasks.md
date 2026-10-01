# Tasks - feature 295, hook misfires and silent stalls

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D10). Research: [`research.md`](research.md) (R1-R7).

**No task here is `research: physical`.** The feature is tooling; nothing is asserted about the world.

- [x] T01 Item 1: `finished-run-hooks.sh` judges a variable-named waiter and a chain's last file as watching (D1)
      research: rendering
      verify: DONE. test-finished-run-hooks 6g: the variable-named waiter and the chain's last-file waiter are watched with live processes; both red against the old hook (4 failing)
- [x] T02 Item 2: `_hm_review_round.classify_mode` reads the dispatch's MODE line (D2)
      research: rendering
      verify: DONE. test-review-round-hooks 9: the 2026-09-30 exception shape passes untouched with a snapshot; red with the MODE-line rule removed (2 failing)
- [x] T03 Item 3: `_page_session_runner.StallWatch` and the resume-at-once loop, with tests (D3)
      research: rendering
      verify: DONE. test_page_session.py: StallWatch ends a silent fake claude, leaves a writing one, measures from the watch start; the loop resumes at once and caps at 8; the file 23 passed
- [x] T04 Item 4: `stall-watchdog-hooks.sh` + `_stall_watchdog.py` and `test-stall-watchdog-hooks.sh`, every SC-004 fixture (D4-D6)
      research: rendering
      verify: DONE. test-stall-watchdog-hooks 28 cases: every SC-004 fixture and every exemption FR-005 names with live stand-ins; each of 7 rules red with it removed; a dry pass on the real host judged correctly
- [x] T05 Item 5: the periodic-report refusal in `no-poll-hooks.sh` / `_hm_shape.py periodic`, with cases (D7)
      research: rendering
      verify: DONE. test-no-poll-hooks feature-295 section: the 292 watcher refused with an hourly CronCreate, event waits (291, 293, while-true with break) pass; red against the old hook
- [x] T06 Items 6 and 7: escaped clauses and the sleep-in-loop rule, with cases (D8, D9)
      research: rendering
      verify: DONE. test-no-poll-hooks: the quoted ceiling and proof parse (bash -n), red with _fit disabled; the R7 command passes, sleeps in loops still blocked
- [x] T07 Each new rule shown red with it removed; wiring and tables (D10)
      research: rendering
      verify: DONE. each rule shown red (see T01-T06); settings.json registers stall-watchdog-hooks.sh prompt; CLAUDE.md and docs/guards.md rows; make hooks-test 32 suites green
- [ ] T08 `make hooks-test` and `make done` green, then land
      research: rendering
