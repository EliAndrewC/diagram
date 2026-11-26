---
kind: declined
title: raising the builders' context cap to 600k
for: the option - builders run to 600k tokens of context before the handoff, so fewer handoffs and fewer fresh builders re-reading
measured: 2026-11-25
measurement: across 61,271 builder turns since 2026-11-19 (634 general-purpose builder transcripts since 2026-11-18), time a wash at every context from 300k to 800k (within 2.5 min) and tokens favoring the handoff everywhere, 33% fewer at 300k and 62% fewer at 800k; turn speed 7.3 s per 1,000 output tokens under 300k against 7.8 over
command: none yet - a read-only pass over the builder transcripts, its method in specs/449-rust-codebase/port-talk-agenda.md item 12
falsifier: what would reopen it - the handoffs' re-read minutes exceed the slow-turn minutes they save by more than noise AND tokens stop favoring the handoff
threshold: handoff tokens per landed task at or above a grown builder's, with re-read minutes past the slow-band minutes saved (today 421 against 215 over six days)
cost: none: not built (the cap stays at 300k, `builders-context-cap.md`)
last-audited: 2026-11-25
cadence-days: 30
---

Declined on measurement on 2026-11-25 (`docs/process-decisions.md`, "Decisions NOT to do something"): the coordinating session had
recommended moving the stop to 600k and withdrew it on these numbers. The in-force cap's own entry is `builders-context-cap.md`;
the two are audited from the same data.
