# Tasks - 217 rolls earn their lines

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering`.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: rendering
      verify: DONE. FAITHFUL at round 2 of 5: round 1 required four changes (every row kind under the rule with PoolGen the stated exclusion; the proves-less section names the three seating assertions; D2's reason; FR-007's LINES mode and twenty-line threshold deleted)
- [x] T02 the rule at the gate: the record's context, the verdict's unique-line judgment and printout, PoolGen printed, unit tests (FR-001, FR-001a, FR-002)
      research: rendering
      verify: DONE. _census.record carries context (+ the gen mark, found on gate 2); rollverdict.judge takes unique-by-context, fails a Roll/Duplicate with none, prints count+lines per roll, PoolGen printed never judged (keyed on the gen child's mark); 5 verdict tests + census + main-with-db test; gate cold census in R2
- [x] T03 the roster is a guard file on both routes, with its own Read-time context; suite cases (FR-004)
      research: rendering
      verify: DONE. tests/rolls.py in guard-file-hooks.sh (regex + case list, roster-specific Read context) and _hm_make's guard-write pattern; test-guard-file-hooks 36/36 (section 6), test-make-only-hooks 74/74 (four roster cases); an apostrophe in the hook's python -c broke it once, fixed
- [x] T04 the audit pointer on Roll and Duplicate rows; the static test; the two rows pointed (FR-005)
      research: rendering
      verify: DONE. Roll.audit / Duplicate.audit; both rows point at specs/216 research R2; tests/test_rolls.py checks the file, the heading and the audit header
- [x] T05 the seatings converted: the one line as a unit test, the three tests to tests/soak/, the row gone (FR-006)
      research: rendering
      verify: DONE. seats.py:110 is tests/hamletgen/homesteads/test_seats.py; the three seating tests + roll_seatings moved to tests/soak/test_seatings.py (3 passed by hand, 17 s); SEATINGS row and spec gone; warm census 2 rolls of 2
- [x] T06 FR-003 as a test of the plan; the doctrine in four places; the deferred agent recorded (FR-003, FR-007, FR-008)
      research: rendering
      verify: DONE. test_a_roster_change_plans_a_full_run in test_incremental.py; doctrine in constitution VI clause (upkeep, no bump), root CLAUDE.md bullet, tests/CLAUDE.md, tests/soak/CLAUDE.md, the roster docstring; roll-review agent recorded in future-work/cross-cutting.md
- [x] T07 `make done` green, the census read (2 of 2, counts printed), R2, land (FR-009, SC-001..003)
      research: rendering
      verify: DONE. make done green 192 s cold (pytest 146 s, 3,459 passed, both floors 100%); census 7 rolls of 6 (2 rostered judged, 5 shipped gens printed); R2 written; landing follows
