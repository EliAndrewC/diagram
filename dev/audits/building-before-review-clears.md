---
kind: adopted
title: building before the plan review clears
for: a new feature's first task is built, once its spec is FAITHFUL, while its plan review runs, so the session does not sit through the review's minutes before any code exists; the spec review still comes before implementation and the plan review still gates every tick and landing
measured: 2026-11-25
measurement: of 301 tasks with a task-level plan review (MODE 4 spec-fidelity rows of dev/review-ledger.md since 2026-11-19, features 449 and 451), 224 (74%) CLEAR on the first round; of the 69 blocked tasks whose first BLOCKED round could be read, 6 asked for a measurement, 13 for wording or form, 45 for code that built on what was there and 5 (about 7%: 451 T79, T186, T46, T102, T197) reversed built work; 18 more unreadable, their verdict files overwritten
command: none yet - a read-only pass over the ledger, the verdict files and the plan.md diffs; its scripts and table are dev/measurements/2026-11-25/reversals/ (summary.txt the counts, table.tsv each blocked task's class)
falsifier: on a later sample, BLOCKED rounds reverse built work often enough that the rework costs more than the wait the rule saves
threshold: the share of BLOCKED rounds that reverse built work passing about one in five (today 5 of 69, about 7%)
cost: make task-time's builder rows for a feature's first task - the minutes rebuilt after a BLOCKED spec or plan round; the rule itself runs nothing
last-audited: 2026-11-25
cadence-days: 30
---

Decided by the GM, 2026-11-25 (pre-approved on its measurement; `docs/process-decisions.md`, "Building begins before a new feature's
plan review returns"): "if our plan review takes, let's say, 4 minutes, then we could probably just do the first 4 minutes
of implementation ... and then we can adjust". The rule is a line in the root `CLAUDE.md` ("Development workflow") and its full text
in `docs/spec-kit-and-reviews.md`; no guard enforces or refuses it. The review gate at the push, the plan gate at the tick, the
decide-first hold on a task's checks and the hold on a plan block under review are unchanged.

The measured population is task-level plan reviews, where the code already came before the review; a feature's first plan review
is assumed to behave alike. The audit re-runs the reversals scripts over the rounds since the last audit and reads each BLOCKED
round of a feature's FIRST task apart, since that is the round the rule newly exposes. Extending the early build to the spec review
would amend constitution XVI and is an open question for the GM.
