# The landing of T12, analyzed - and the landing it should have been

The GM, 2026-10-20, after T12's round (one claim, 35 minutes start to landed): *"I do not want each landing to owe a lands open
line ... It sounds like the landing being the biggest cost is something that we need to do something about ... 5 minutes is an
acceptable amount of time for actually implementing the task ... do an in-depth analysis of what you think would have been a
good process that would have done what we wanted in kind of a reasonable amount of time, and what else is needed to make that
happen, then create tasks for those changes that will be the very next tasks that we do here in this feature, and then go ahead
and work those tooling and process changes."*

## What happened (measured 2026-10-20 from the event log, the run logs and the session's own timestamps)

| UTC | what | cost |
|---|---|---|
| 12:01-12:07 | the fix: 0246 read, the plan section, a red test, two loops deleted, the ways package green | ~5 min |
| 12:03-12:12 | the spec reviewed (first time, two rounds), the plan reviewed (the first pass returned nothing: no request.md) - mostly in parallel with the fix | ~5 min of the session's own time |
| 12:11-12:15 | the claims round: triage, impl-drift, an UNCLAIMED rule claimed, impl-drift again | ~4 min |
| 12:14-12:16 | `make land-batch T=T12` refused: it takes two tasks or more. `sync-with-main.sh done` refused: no green gate on this content | 2 refusals, ~2 min |
| 12:16-12:21 | `make done`, started by hand after the refusal | 4.4 min (263 s) |
| 12:21-12:24 | the push refused: "neither route lands a feature in progress" - every other open task of 405 held it | 1 refusal |
| 12:24-12:28 | every open box marked `[lands-open]`, T12 put on the `**Lands open**:` line, the line's plan review (33 s); the hourly step-back blocked that dispatch until it was taken (165 s) | ~4 min |
| 12:28 | the push refused: the delta declared no occasions | 1 refusal |
| 12:29 | the push refused: no landing cohort on this engine | 1 refusal |
| 12:29-12:33 | `make cohort-landing`, started by hand after the refusal | 3.8 min |
| 12:33-12:35 | the push: its checks, then render-sync regenerating main's renders of OTHER sessions' maps (four magistracies), in the foreground | 2.5 min |
| 12:35-12:36 | `make tick` refused: the step-back owed T12 a part B | 1 refusal |

**The checks themselves are fast** (measured 2026-10-20, warm caches): `push_checks.py` 7.5 s, the claims gate 2.0 s, the
holding check 0.3 s, the review gate (occasions) 0.02 s. **So the landing's 15 minutes were not slow checks.** They were:

1. **Six refusals found one at a time**, each a session round trip (read the refusal, decide, act, re-run): about 1-1.5 min each,
   ~7 min in all. Every one of them was knowable at 12:14, before any gate ran.
2. **The two long runs started late and by hand**, each only after a refusal named it: `make done` (4.4 min) and `make
   cohort-landing` (3.8 min). Nothing about them needed the session.
3. **The Lands open line** - a bookkeeping review the GM does not want (*"that's going to slow things down"*), ~4 min with
   the step-back it ran into.
4. **render-sync in the foreground** - 2.5 min refreshing main's renders of maps this landing did not touch.

## The landing it should have been

One command, `make land F=405 T=T12`, at 12:14, the moment the claims round was recorded:

1. **Every cheap refusal first, all reported together** (~15 s): each named task's tick refusals but "not landed yet" (part B
   owed, decisions unreviewed, a retro row), uncommitted work, owed ledger rows, the claims gate, the holding rule, the review
   gate's occasions. One list; the session fixes all of it in one pass.
2. **The gate and the landing cohort, run by the command, only where their records do not already cover this content**: `make
   done` (4.4 min), then `make cohort-landing` (3.8 min). Files the gate regenerates (a pool manifest) committed by the command.
3. **The push**, which now refuses nothing - its checks already passed (~20 s).
4. **The ticks**, each with the note, the moment the push succeeds.
5. **render-sync in the background**: main's renders refresh after the landing returns.

**Expected: about 9-10 minutes of machine time and one session action**, against 15+ minutes and seven session round trips.
With the 5-minute fix and the ~4-minute claims round, a claim task on a started feature comes to **about 20 minutes**, most of it
the gate and the cohort, which run unattended.

## What is needed - the tasks, worked next

- **T32 - only the task being worked holds a landing** (the GM: no Lands open line). A feature in progress holds a landing only
  through its ACTIVE task (`make task-start`) while that task is open and the landing does not tick it; tasks not started hold
  nothing, and the `**Lands open**:` line and the `[lands-open]` marks are retired.
- **T33 - `make land F= T="..."`**: one command for one task or several (`land-batch` becomes the same command): the cheap
  refusals together, then the gate and the landing cohort as needed, the gate's regenerated files committed, the push, the ticks.
- **T34 - the push asks its cheap questions first**: the holding rule and the review gate's occasions run before
  `push_checks.py` and the claims gate, so a plain `sync-with-main.sh done` also refuses in seconds, not after its checks.
- **T35 - render-sync after the landing, in the background**: `done` returns once the work is on main.
- **T30 and T31** (filed while working T12): the plan bundle refuses a feature with no `request.md`, naming the file; `task-add`
  numbers a new task from the boxes' own ids.

## Weighed and not taken now

- **The gate and the landing cohort in parallel** (22 CPUs, 15 GB, 7 GB free, measured 2026-10-20) would save ~4 min, but both
  scale their workers to the machine and the memory cap has bitten before (feature 315); measure it as its own change once the
  sequence above is the norm.
- **Skipping the claims triage for a one-function change**: the triage was 11 s of agent time; not worth a rule.
- **The part B a step-back owes**: about a minute; it is the step-back's record, and `make land`'s first pass now names it with
  the rest instead of after the push.
