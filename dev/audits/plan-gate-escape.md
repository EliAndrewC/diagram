---
kind: adopted
title: the plan gate's escape
for: PLAN_REVIEW_OK lets a tick or a push pass a plan the gate holds, with a reason; a clean gate honors no escape (one line, no record), and an honored escape's record carries what the gate held, so the escape is counted and classified by the gate's own answer instead of by the session's wording
measured: 2026-11-26
measurement: 158 plan-gate escape records dated 2026-11-25/26 in dev/bypass-log/2026-11 (102 at the push, 56 at the tick), counted by target, against 354 commits on main in the same window; 12 of them replayed at their commits with the push's scope by 451 T261's builder - the gate owed nothing in 7, and held blocks the reason did not name in the rest (449's withdrawn tasks' edited sections, three ticked tasks' stubs, 451 T227's renumbered Approach block); 155 of the 160 records that builder read carried a standing reason naming a cause the gate never had
command: grep -l '"target": "plan-gate ' dev/bypass-log/<YYYY-MM>/*.json | wc -l (the escapes honored); the same files' "held" lists (each feature, its rule, its blocks), which records before 451 T262 lack; make guard-log GUARD=plan-gate
falsifier: escapes still ride most landings once the blocks the gate truly held are reviewed (449 T439), or sessions keep carrying PLAN_REVIEW_OK on a clean gate after being told to drop it
threshold: honored escapes per landing staying above about 0.3 over a week once 449 T439's review lands, counted from the records that carry "held" (GUESS; today about 0.45 a commit on main, by the 12 replays most of them on a clean gate or on blocks 449 T439 reviews)
cost: the push's and the tick's plan-gate row (the gate is asked once, as before - the escape no longer skips the ask at the push, about one `l7r-gate plan push` a push); a record's `held` list in dev/bypass-log/
last-audited: 2026-11-26
cadence-days: 14
---

451 T262, on 451 T261's builder's measurement (2026-11-26). The rule is `tick_gate` and `bypass_record` in
`rust/gate/crates/plan/src/plan.rs` (the tick) and `scripts/gates/plan-gate.sh` (the push); its tests are
`an_escape_is_dropped_where_the_gate_owes_nothing_and_its_record_carries_what_was_held` and cases 5b and 6b of
`tests/hooks/test-plan-gate.sh`.

What the audit reads: the records since the rule carry `held`, so it counts honored escapes by rule (`plan-review-stale`,
`plan-review-blocked`, `plan-review-missing`, `plan-missing`) and by which task's blocks were held, and asks whether those blocks
were ever reviewed. `make audit`'s listing still prints the reason alone; a count by `held` is a reader's query until a measurement
is built on it. The commits-on-main figure is a stand-in for landings: the audit counts landings by `make land`'s tick commits.
