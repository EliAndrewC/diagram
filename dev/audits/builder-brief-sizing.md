---
kind: adopted
title: builder brief sizing
for: a builder is given one task and at most three jobs, a task past about three files or opening on a measurement is split into builders that hand results along, and a one-turn edit is the coordinating session's own, so fewer builders reach the context cap and pay a fresh builder's re-read
measured: 2026-11-25
measurement: of the 97 general-purpose builders dispatched since 2026-11-24, 27 (28%) handed off (refused at the cap, a handoff written, or context at 290k or more); a brief of 4 or more jobs 52% (12 of 23) against 16% at 1-2 jobs (4 of 25) and 22% at 3 (11 of 49); 4-8 files edited 39% and 9 or more 45% against 22% at three or fewer; a brief beginning with a measurement 46% (6 of 13) against 25%; a one-turn edit by the coordinator about half a small builder's tokens (0.3-0.4M against 0.65M), past 5 minutes or several files about 1.5M
command: none yet - the M1 method, a read-only pass over the builder transcripts: dev/measurements/2026-11-25/talk-measures/ (m1.py and m1b.py the brief sizes, m2b.txt the coordinator's edits)
falsifier: builders briefed under the rule hand off about as often as before it
threshold: the handoff rate of builders briefed under the rule not falling below about one in five over a week, by the M1 method (today 28%); the three-job and three-file limits are GUESS knobs
cost: make task-time's builder rows (a split task's extra dispatches: each brief written and each report read, about 0.06-0.09M tokens a builder) and the coordinator's own one-turn edits
last-audited: 2026-11-25
cadence-days: 7
---

Decided by the GM, 2026-11-25 (pre-approved on its measurement; `docs/process-decisions.md`, "The builders' context cap stays at
300k, builders stay, and briefs are sized"). The rule is the SIZING paragraph of `scripts/container/builder-brief.md`, with one line
in the root `CLAUDE.md`; no guard enforces it, because a task's size is the coordinating session's judgment.

Caveats the audit carries: the six one-job briefs handed off half the time (3 of 6), so the job count alone does not
predict; the groups are small. Whether builders beat no builders per landed task is `delegating-to-builders.md`'s question, still
unmeasured. The cap itself is `builders-context-cap.md`.

The audit re-runs `m1.py` and `m1b.py` over the builders dispatched since the rule (2026-11-25) and compares the handoff rate with 28%.
