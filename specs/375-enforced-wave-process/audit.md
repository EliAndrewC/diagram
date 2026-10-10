# SC-002 audit - each requirement, the test that fails on the old behavior, and how that was proved

SC-002: "Each FR has a test that fails with the old behavior and passes with the new, run by `make hooks-test` or the gate."
"Proved red" names how the old behavior was shown to fail: **removed** (the new code taken out and the test run red, then
restored), **by construction** (the test asserts what the old code could not do - it calls a function, a command or a refusal
that did not exist, or the old code's output is the one the test rejects), or **changed** (an existing test's expectation moved
with the behavior, the old expectation recorded in the diff).

| FR | test | proved red |
|---|---|---|
| FR-001 pop-up triage | `tests/tooling/test_modal_triage.py` (4); `test_modal_checks.py::test_the_depiction_tab_owes_its_own_check...` | changed: the depiction bundle on a moved drawing page returned 0 (bundled in full) and now 3 (triage first); by construction for the triage's bundle and reply |
| FR-002 line-scoped claims | `tests/tools/test_claims.py::test_a_section_claim_is_owed_by_its_own_line...`; `tests/tooling/test_claims_scoping.py::test_a_section_edit_off_a_claims_line_owes_a_triage...` | by construction: the old `Unit.code` folded the section's core into every claim, so a moved table row changed every claim's code - the equality the test asserts; the real index's migration owed nothing (281 re-keyed) |
| FR-003 decide, then freeze | `tests/hooks/test-checks-hooks.sh` (15), `tests/tooling/test_hm_checks.py`, `test_plan_gate.py::test_a_check_waits_for_its_task_s_decisions` | removed: with the freeze call taken out of `record-edit-hooks.sh` the suite failed 2 cases (T13); decide-first by construction (the refusal did not exist) |
| FR-004 preflight inside the gate | `tests/tooling/test_preflight.py` (3) | by construction: no phase ran before the gate's static checks, and no green was refused for a tree that moved |
| FR-005 (a) the triage | `tests/tooling/test_claims_scoping.py::test_a_withdrawn_block_that_never_reached_a_commit...` and `::test_the_triage_reads_only_lines_that_open_with_touches` | removed: with the kept snapshot text taken out (`snapshot=""`) the withdrawn-block test failed (T04). The parser itself was already anchored before 372 (d124372a1); its test pins that and has no old failure to show (plan D5) |
| FR-005 (b) a typo keeps the verdict | `tests/tooling/test_plan_gate.py::test_a_verdict_survives_a_typo_and_nothing_more` (8 cases) | by construction: the old gate compared the plan's whole hash, so the misspelling, re-wrap and punctuation cases fail on it |
| FR-006 file, don't fix | `tests/tooling/test_outside_the_change.py` (2) | by construction: no bundle named the change and no reply was filed |
| FR-007 escalation only for open findings | `tests/hooks/test-escalation-hooks.sh` section 7b; `tests/tooling/test_ledger_lint.py::test_a_row_from_375_on_says...` | by construction: the old stop hook blocked any armed review, so the disposed case (now silent and disarmed) fails on it |
| FR-008 the event log | `tests/hooks/test-event-log-hooks.sh` (18), `tests/tooling/test_event_log.py` | removed: with the log line's write taken out the suite failed 14 of 18 (T25) |
| FR-009 the report, every closing route | `tests/tooling/test_event_log.py::test_the_report_end_to_end`; `test_close_check.py::test_the_last_tick_refuses_without_the_report`; `tests/hooks/test-sync-with-main.sh` (the closed fixtures now carry a report) | by construction for the report; changed for the closing routes: the last tick and the push of a closed feature had succeeded with no report (`test_plan_gate.py`'s tick test and the sync suite's fixtures moved with it) |
| FR-010 tripwires | `test_hm_checks.py::test_the_third_round_goes_to_the_arbiter`, `::test_a_dropped_block_coming_back...`; `test_replays_375.py` (the bath bullet from its own history); `tests/tooling/ci/test_state.py::test_a_second_red_gate_in_a_row...`; `test_hm_arbiter.py::test_the_cascade_wire...`; `test_event_log.py::test_an_edit_putting_back...` | by construction: none of the wires existed; SC-006's replay over 372 fires each (`m:sc006-replay`) |
| FR-011 the round arbiter | `tests/tooling/test_hm_arbiter.py` (6), `test_hm_checks.py::test_a_ruled_trigger_is_never_put_to_the_arbiter_again`; `tests/hooks/test-pair-hooks.sh` section 12 (continue runs the round, accept closes it) | changed: the review cap's third round used to need `REVIEW_ROUNDS_OK`; now the refusal hands it to the arbiter and a `continue` ruling runs it |
| FR-012 the GM's review after landing | `tests/tooling/test_gm_review.py` (4); `test_lands_open.py` (the GM box honored only with a row) | by construction: no row, box or `Done - GM review pending` state existed |
| FR-013 the advisor told what to watch | `tests/tooling/test_375_doctrine.py` | by construction: CLAUDE.md named none of the patterns before |
| FR-014 a carried measurement held | `tests/tooling/test_close_check.py::test_a_feature_closes_with_its_report_and_its_carried_keys` | by construction: nothing read a `Carried:` line |

Every suite above runs in `make hooks-test` (the `tests/hooks/*.sh`) or the gate's test phase (`tests/tooling/`, `tests/tools/`).
