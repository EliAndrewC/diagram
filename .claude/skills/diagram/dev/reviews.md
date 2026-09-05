# Invoking a review agent

**Load this file when:** You are about to launch `settlement-review`, `building-review` or `backstory-review`.

Split out of [`../CLAUDE.md`](../CLAUDE.md) so it is not in every diagram session's
context. The text is verbatim; the short always-on version of each rule stays in the index.

## Invoking a review agent: SCOPE it, SPLIT it, and launch it EARLY

`settlement-review` is mandatory before a Mode B map ships, and it is also the single most expensive
thing a session waits on. Measured 2026-08-08, on a change that resized some captions: one agent,
two maps, a full audit - **12.3 minutes, 22% of the whole task's wall clock**, with this session idle
for 11.4 of them. The findings were right; two of the five had nothing to do with the change and had
been sitting in the pool for weeks.

Three rules, all of them free:

- **Say the SCOPE.** The agent now takes `DELTA: <what changed>` and reviews the change, whatever the
  re-pack moved, and whatever the change made incoherent - skipping the spelling/twin/nuisance/traffic
  sweeps and saying which it skipped. Reserve `FULL` for a new or heavily-rewritten map. A caption
  resize is a DELTA.
- **One map per agent, launched in parallel.** The sweeps share no work across maps, so handing two
  maps to one agent just serializes two audits behind one notification.
- **Launch it the moment the motivating map's regen + gate is green - BEFORE your own visual
  pass**, the docs and the commit. Everything you do while it runs is free; everything after it is
  added on. Measured 2026-08-16 (the cut-bank fix): the review agent was the whole task's
  critical-path TAIL - its last 84s ran past an already-green `make done` - and it was launched
  only after a 52s reasoning turn plus the session's own crop reads. The reviewer independently
  re-verifies that ground anyway, so every second of your own pass spent before the launch is a
  second added to the task's total.

Same three rules apply to `building-review` and `backstory-review`.

## WHEN a review runs (GM 2026-08-26) - and it never blocks the GM's look

The GM, after a task in which three serial `settlement-review` passes added ~10 minutes and the
second of them passed a map the GM rejected on sight: *"iterating in a way that allows me to look at
something more quickly will probably be more productive than having a built in independent
reviewer, which runs multiple times on every pass."* So:

- **While `scope` is LOCKED (the reference-hamlet iteration period), no per-task review.** The GM
  is looking at every result and is the faster, more authoritative reviewer of the one map on the
  sheet. Gate green -> hand the map back. The independent review runs at **acceptance** (one FULL
  pass of the reference settlement before T99 is ticked) and at **unlock** (the pool re-roll, where
  48 seeds are more than the GM can look at - the place an automated reviewer earns its time).
  (the scope lock that used to defer this was retired in feature 185.)
- **When a review does run, it runs in the BACKGROUND, after the map is handed back** - or in
  parallel with a LONG gate (`make done FULL=1`, a CodeBuild run), never alongside `make quick`
  (~30 s: launching a 3-minute review "in parallel" with it just serializes). A finding becomes a
  follow-up task; it never holds the result.
- **Never busy-wait on one.** Same rule as the gate: act on the completion notification.
- **The push-time gate is unchanged** (`review-gate.sh`: a re-rolled pool map carries a logged
  review) - under FR-006 the push is the feature's end, which is exactly the acceptance pass above.
- **Every FINDING is a row in [`docs/review-ledger.md`](../../../../docs/review-ledger.md), written
  by the SESSION, never by the reviewer** (the GM: you may disagree with the reviewer, and the log
  must say both what was found and whether it was acted on - fixed / recorded-only / declined with
  why / MISSED-BY-REVIEWER). In the same commit that acts on the review. The first miss on record (T12 round 2: the mechanism measured, the picture not judged)
  became the agent's fit-zoom-first rule.

## A finding OUTSIDE the delta is still yours to fix

Constitution **Principle XIV** (GM 2026-08-17). An independent reviewer pointed at a DELTA reliably
turns up defects that have nothing to do with it - that is the reviewer working, not the reviewer
overreaching - and the answer is to FIX them in the work at hand, not to ledger them for a pass that
never comes. The only exception is a fix that would be an architectural change (a stage reordering, a
new subsystem, a placement engine rewritten); defer that WITH its measurement, its mechanism and an
implementation sketch, which is a deliverable rather than a shrug.

Do not reach for Principle XIII's "pre-existing failures stay ledgered" here. That clause is about
what BLOCKS a push, not about what you owe a defect you have seen.

Worked example, the paddy size floor (2026-08-17). Three `settlement-review` findings arrived that
had nothing to do with basin size: lane frontage regressed past the 94 ft threshold `homesteads.py`
records as its own diagnosed defect, the three shared byres collapsed onto three farmsteads
(median nearest-byre 373 ft), and a windbreak was clipped with 23 clumps drawn wholly off-canvas.
All three were fixed in that feature - 106/59/65/77 ft lane medians, byre median 107 ft, zero
off-canvas clumps - and the *first* attempt at the lane fix (a relaxation ladder) is recorded at the
point of change as having measurably done nothing, because a fix that fails is worth as much to the
next reader as the one that works.

## The pairing's stop hook fired once with a review actually in flight (observed 2026-08-29)

`scripts/pair-hooks.sh stop` reported PAIRING HALF-OPEN while a `settlement-review` agent was running
over exactly that delta. Investigated and NOT reproduced: replaying the same payload by hand exits 0,
and `agent-stall-hooks.sh pending` - which `review_pending()` delegates the "is it finished" question
to - lists the agent correctly. The most likely cause is a race, since the check runs against a
transcript the agent is still writing and the gate's reference sub-phase records a green key of its own
partway through the run.

Recorded rather than fixed at first, deliberately: the hook is self-limiting (`stop_told` fires once
per engine key, never in a loop), the cost of a false fire is one line of noise, and a speculative edit
to a guard that cannot be reproduced is the kind of change that breaks the guard for real.

**It fired a second time the same day, and the second one was reproducible and worse.** The gate had
been run with `PAIR_OK` and a written reason - which is precisely what the hook's own message asks for,
*"record why it is not owed: PAIR_OK=... on your next gate run"* - and the override logged its reason
and then changed nothing the stop branch reads. So the guard told the session to do the thing the
session had just done. That is the failure mode this project's own guard rules single out ("check the
ESCAPE FIRST or the guard cannot be repaired through the channel it guards"), and it is worse than a
false fire because it teaches a session that the documented remedy does not work.

Fixed: a `PAIR_OK` gate run now records `waived_key` against that exact engine key, and `stop` honors
it. Per content, so an engine edit after a waived gate is guarded again rather than riding the old
waiver. `scripts/test-pair-hooks.sh` gained four cases (21 total), and deleting the one line that
records the waiver turns two of them red.
