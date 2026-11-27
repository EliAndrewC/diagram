---
kind: adopted
title: the reversal index's STALE knob
for: the Edit hook's reversal tripwire reads a derived index of the log's PreToolUse Edit lines instead of the whole log (451 T443), the reversal index is rewritten only once the log has grown past STALE (1 MiB, a GUESS knob) since it, the tail read by T392's chunked scan meanwhile
measured: 2026-11-27
measurement: 451 T443's differential over copies of the 34 real event logs - 485,165 lines, 9,176 Edit lines, 1,937 paths, 0 lists differing cold, warm or grown; event-log-hooks 31.2 to 11.8 ms median in a pool tree and 31.3 to 9.7 in the clone (LOADED, load1 15 to 18)
command: make rust-test CRATE=rust/guard/shared ONLY="guards::event_log_hooks"; dev/measurements/2026-11-27/edit-hook/t443-differential.rs over fresh copies
falsifier: an Edit hook's tail scan past the index costing more than a rewrite would (the hook's median over 20 runs rising past T443's warm figure by more than the rewrite's own cost)
threshold: one missed reversal in a differential, or the warm hook's median past 20 ms at load under 10 (either reopens it)
cost: the Edit hook's PreToolUse (milliseconds, in make task-time's hook rows)
last-audited: 2026-11-27
cadence-days: 30
covers: STALE
---

451 T443 (`rust/guard/shared/src/guards/event_log_hooks/reversal/index.rs`): the index is the READER's, never a writer's, and is
rebuilt by a full scan on any mismatch, so a stale or lost index costs time, never a line. STALE is a GUESS knob chosen by T443's
builder within the GM's go-ahead of 2026-11-27 ("go ahead and do all of the load-bearing ones").
