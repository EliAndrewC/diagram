---
kind: adopted
title: the builders' context cap and handoff
for: a builder stops at 300k tokens of context and writes a handoff a fresh builder resumes from, so no builder runs in the slow, costly band past the cap
measured: 2026-11-25
measurement: 634 general-purpose builder transcripts since 2026-11-18 (61,271 turns since 11-19): turn speed 7.3 s per 1,000 output tokens under 300k, 7.8 over; per-turn cost about 2.5x from 100k to 300k and 1.6x more to 600k; 135 handoffs with a successor (107 at the cap), the fresh builder re-reading a median 3.7 min (p90 12.5) and 326k tokens before its first edit, 421 min in all against about 215 min the old builder would have spent running slower; tokens favor the handoff at every context (33% less at 300k, 62% less at 800k), time a wash within 2.5 min from 300k to 800k; re-audited the same day on the brief's size (dev/measurements/2026-11-25/ctxcap/ and talk-measures/): of the 97 builders dispatched since 2026-11-24, 27 (28%) handed off, a brief of 4 or more jobs 52% of the time against 16-22% at 1-3, 4 or more files edited 39-45% against 22% at three or fewer
command: none yet - a read-only pass over the builder transcripts, context read as rust/guard/shared/src/context.rs reads it, its method in specs/449-rust-codebase/port-talk-agenda.md item 12; the 2026-11-19 slow-band figure (14.8 against 11.9 s per 1,000 output tokens past 400k) is spec 451 FR-006's
falsifier: the re-read minutes stay past the slow-band minutes saved AND the handoff's tokens per landed task are no better than a builder let grow past the cap
threshold: handoff tokens per landed task at or above a grown builder's (today 33% below at 300k) while the re-read minutes exceed the slow-band minutes saved (today 421 against 215 over six days)
cost: make task-time's builder rows (a handoff's successor booked from its dispatch to its first edit)
last-audited: 2026-11-25
cadence-days: 14
covers: CAP_TOKENS
covers: CONTEXT_CAP_TOKENS
covers: rust/guard/src/guards/context_cap_hooks.rs
---

451 T12's guard stops a builder at `CAP_TOKENS` (300,000, a GUESS knob in spec FR-006) and has it write a handoff under
`.git/l7r-handoffs/`; 451 T237 split the claims round out of builders (`context_cap_hooks/split.rs`, the brief's `STOP POINT` line)
because the claims round was what ran builders out.

The audit of 2026-11-25 (agenda item 12) withdrew the session's proposal to move the cap to 600k: raising it buys little time and
costs tokens. The lever named is the re-read: handoffs that name what to read, and tasks sized to finish. Caveats: the band past
300k is small and survivor-biased (the guard refuses there), and long-context builders run the heaviest tasks.

The second audit of 2026-11-25 closed the talk's item 12 (`docs/process-decisions.md`, "The builders' context cap stays at 300k,
builders stay, and briefs are sized"): the cap stays at 300k on the figures above, and the handoffs are met at the brief instead -
what predicts one is the brief's jobs and files, not the cap (`builder-brief-sizing.md`, the SIZING rule of
`scripts/container/builder-brief.md`).

The next audit re-measures from `make task-time` once its per-turn data covers a week of builders, and adds the three-way
comparison's arm (b) (builders let grow), whose first figures are those above.
