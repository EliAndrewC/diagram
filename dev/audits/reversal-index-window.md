---
kind: adopted
title: the reversal index's WINDOW knob
for: the Edit hook's reversal tripwire reads a derived index of the log's PreToolUse Edit lines instead of the whole log (451 T443), the index is tied to its log by the open file's dev and inode, the length covered, and the raw first and last WINDOW (4096, a GUESS knob) bytes of the covered span, re-read and compared byte for byte
measured: 2026-11-27
measurement: 451 T443's differential over copies of the 34 real event logs - 485,165 lines, 9,176 Edit lines, 1,937 paths, 0 lists differing cold, warm or grown; event-log-hooks 31.2 to 11.8 ms median in a pool tree and 31.3 to 9.7 in the clone (LOADED, load1 15 to 18)
command: make rust-test CRATE=rust/guard/shared ONLY="guards::event_log_hooks"; dev/measurements/2026-11-27/edit-hook/t443-differential.rs over fresh copies
falsifier: a log changed in place between the windows going unseen in a differential over the real logs' copies (one such difference reopens it), or the compare's cost showing in the warm hook
threshold: one missed reversal in a differential, or the warm hook's median past 20 ms at load under 10 (either reopens it)
cost: the Edit hook's PreToolUse (milliseconds, in make task-time's hook rows)
last-audited: 2026-11-27
cadence-days: 30
covers: WINDOW
---

451 T443 (`rust/guard/shared/src/guards/event_log_hooks/reversal/index.rs`): the index is the READER's, never a writer's, and is
rebuilt by a full scan on any mismatch, so a stale or lost index costs time, never a line. WINDOW is a GUESS knob chosen by T443's
builder within the GM's go-ahead of 2026-11-27 ("go ahead and do all of the load-bearing ones").
