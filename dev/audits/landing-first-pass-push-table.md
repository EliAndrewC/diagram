---
kind: adopted
title: make land's first pass asks the push's own table, the record gate and the closing check before its gate
for: no landing runs its whole gate and is then refused by a check of the push that a first pass could have asked in seconds
measured: 2026-11-27
measurement: one run of the first pass's call on a pool tree (diagram-backlog-t270, T307 part 2's own delta), `push-checks --every` with the gate's stamp rows and the ledger's skipped: 14.27 s wall, one row refusing (this very entry owed by the audit register), every other row passing (measured 2026-11-27, `/usr/bin/time`). A landing refused after its gate costs the gate's minutes (dev/measurements/2026-11-27/tree-idle/results.md: 19 landings, 119 minutes of `make land` Phase lines in the window)
command: make rust-test CRATE=rust/gate/crates/land (cheap/tests.rs the_push_s_table_and_the_record_gate_are_asked_in_the_first_pass, every_refusing_row_of_the_push_s_table_is_said_whole); time scripts/gates/l7r-gate.sh push-checks "$PWD" --every --skip "gate-stamp selftest" --skip gate-stamp --skip ledger-owed
falsifier: the first pass's call costs more than the refusals it moves up front save - its wall time on every landing against the gate minutes of the landings it refused that the push would otherwise have refused after the gate
threshold: the call past 60 s on a landing's first pass, or no landing in 30 days refused by it (GUESS)
cost: make task-time books it to the landing's `cheap` phase
last-audited: 2026-11-27
cadence-days: 30
covers: landing refusal land/cheap.rs #7
---

451 T307 part 2. The push ran `l7r-gate push-checks` after the landing's gate and the first pass asked two of its rows (the ledger's
and the make-targets page's), so a row's refusal - a file past the line bar, a research pointer, a spec-lint finding, an unresolved
conflict - came after a whole gate run. The first pass now asks the same table in one call that does not stop at its first refusal
(`--every`), so a row added to the push is asked here by construction; what it cannot ask before the gate is the gate's own stamp
(two rows). `entry-gate.sh` joins the gates the first pass runs, and the closing check is asked in `tick::checks` where the landing's
tasks are a feature's last open boxes. The plan section `### T307 part 2` in specs/451-time-retro-and-efficiency/plan.md holds the
parity table, row by row, and what is still asked only at the push (filed as T413).
