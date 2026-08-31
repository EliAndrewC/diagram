# Feature 171 - runtime ratchets: a test target that gets slower FAILS

**Status**: **APPROVED** (`spec-fidelity` FAITHFUL at round 5, recorded below by its author) and
**IMPLEMENTED** 2026-08-30 by the `Diagram tooling` session. Specified by `diagram-testing`; the
implementation notes, and the two decisions the GM ratified on 2026-08-30, are in
[`tasks.md`](tasks.md).
**The GM's words**: [`request.md`](request.md). **The evidence**: [`research.md`](research.md).
**Review**: `spec-fidelity`, rounds 1-4. See "Review history" for each round's items and their fixes.

## Why

`make done`'s median went 35 s -> 135 s over three days and nothing failed, because nothing has ever
asserted on it. The duration is recorded on every run; `make audit` prints it; no code compares one run
to another. The GM's memory of a guard for this was correct - it exists as `QUICK_BUDGET` and covers
`make quick` alone (research R1). And `QUICK_BUDGET` is a 60 s absolute ceiling against a target that
runs 11 s, so `quick` could get 5x slower and still pass.

## Scope

**In:** detection. A target slower than its pinned baseline by more than a stated margin FAILS.

**Out, explicitly** (the GM drew both lines):
- Investigating WHY `make done` went 35 s -> 135 s. Separate, and it comes after this.
- Arming anything for the FULL / AWS scope. The pattern must EXTEND there cleanly; it must not be
  switched on there now. Remote is off while the hamlet baseline is made rock solid.
- Any change to what the tests do, select, or cover.

## The two numbers the GM stated, and how they bind

These are the GM's own figures and are HARD CEILINGS. The mechanism may tighten below them; **it may
never compute a ceiling above them.**

| target | GM's stated baseline | GM's stated ceiling | binds | what is compared |
|---|---|---|---|---|
| `make quick` | 11 s (today) | **15 s** | NOW | **the run itself** |
| `make done` (interim, baseline > 35 s) | - | - | now | **the median of the last 25 green same-scope runs** (author's departure - see D2) |
| `make done` (once baseline <= 35 s) | 35 s | **45 s** | then | **the run itself**, as the GM stated |

## Functional requirements

**FR-001** `make quick` FAILS when **that run** takes **15 s or more** (the GM: *"if it takes even as
much as fifteen seconds than I would like for that to result in a failure"* - at 15, not past it, and
per run, which is how the GM phrased it). This replaces the 60 s `QUICK_BUDGET`.

> **15 s is FIXED, not derived.** If `quick` gets faster, the bar does NOT tighten below the GM's
> number automatically. FR-004's derivation applies only to a target with no GM-stated ceiling, and to
> `done` until its baseline reaches 35 s. Auto-tightening below a figure the GM set would fail runs their
> own words treat as fine - they said 15 GIVEN 11 s today.

**FR-002** `make done` FAILS at or above its ceiling, and there is **one rule per regime**:

- **While the pinned baseline is above 35 s** the ceiling derives per FR-004. Today that is a **155 s**
  baseline giving a **201 s** ceiling (decision D1 - both numbers are the spec author's, not the GM's).
- **Once the pinned baseline is 35 s or less** the ceiling **is** the GM's **45 s**, fixed. It does NOT
  derive from the baseline and does NOT tighten as the baseline falls further.

> The second bullet is the same treatment FR-001 gives `quick`'s 15 s, for the same reason. An earlier
> draft said "computed per FR-004 ... capped at 45 s", which at a 25 s baseline yields a 32 s bar - i.e.
> auto-tightening below a figure the GM stated, the exact move this spec disowns one requirement earlier.
> The GM said 15 GIVEN 11 s and 45 GIVEN 35 s, in the same sentence shape; both are treated the same way.

WHAT is compared to the ceiling also changes with the regime - median while interim, the run itself once
the GM's 45 s is in force; see D2 and the table above.

**Nothing in this feature causes the re-pin.** `done`'s ceiling reaches the GM's 45 s when somebody
commits a pinned baseline of 35 s or less, which is the separate efficiency work's job, not this one's.

**FR-003** Each target has a **PINNED baseline**: a committed number, not a rolling statistic, moved in
EITHER direction only by an explicit committed edit carrying a written reason (FR-010).

> Round 2 removed the automatic downward pinning that an earlier draft had. The GM asked for a baseline
> to compare against (*"relative to some previous baseline"*); they did not ask for one that updates
> itself, and a self-updating baseline needed a whole run-history mechanism to support it. Re-pinning
> `done` as the efficiency work lands is a deliberate act with a written reason, which is what FR-010
> already requires and is one line of diff.

> Why pinned and not rolling: research R4 records that this regression arrived "in twenty small pieces",
> every one of which sits inside a rolling median of recent runs. A rolling baseline follows the
> degradation upward and would NOT have caught the motivating 35 -> 135 drift. This requirement and the
> old FR-008 contradicted each other in round 1; this is the resolution.

**FR-004** **While no GM-stated ceiling is in force for a target**, its ceiling derives from its pinned
baseline by one rule, so a new target needs no fresh judgment call:
**`ceiling = min(HARD_CEILING, max(baseline + 4 s, int(baseline * 1.3)))`** - `HARD_CEILING` being the
GM's number where one applies, and unbounded otherwise.

> **The two worked examples below are DEMONSTRATIONS, not live derivations.** They exist to show that the
> formula REPRODUCES the GM's numbers at the baselines the GM was reasoning from, which is why it is
> trustworthy for a target the GM has not named. Neither is actually computed at run time: `quick`'s bar
> is fixed at 15 s (FR-001) and `done`'s becomes fixed at 45 s once its baseline reaches 35 s (FR-002).
>
>   at `quick`'s 11 s:  `min(15, max(15, 14)) = 15`   - the GM's figure
>   at `done`'s  35 s:  `min(45, max(39, 45)) = 45`   - the GM's figure
>
> The live use of FR-004 today is exactly one target in one regime: `done` while its baseline is above
> 35 s, where no GM ceiling applies and 155 s yields 201 s.

> **An uncapped target cannot drift upward either**, and the `min()` is not what stops it - FR-003 is: a
> baseline never moves without a committed edit, so an uncapped ceiling can only grow behind a human
> decision with a written reason. The two requirements together close it, which is worth knowing because
> the `min()` alone does not.

> The `min(HARD_CEILING, ...)` is what stops the derivation LOOSENING past the GM's number. Round 1's
> draft omitted it, and the reviewer showed the consequence: a quick baseline drifting to 12 s would have
> bought a 16 s ceiling - the mechanism relaxing exactly when the thing it guards begins to happen.

**FR-005** The mechanism is **general across targets**: adding one is a table row, not a new
implementation.

**FR-006** The FULL / AWS scope is **wired but not armed** - one row away from working, and that row off.

**FR-007** *(spec author's addition, OPTIONAL - not requested by the GM.)* `make quick` records no
`dev/run-log/` entry at all (measured: n=0), so `make audit` cannot show its history and a future
re-pinning has nothing to compute from. **The GM's 15 s bar does NOT depend on this** - `quick` already
times itself inline (`Makefile:691` compares elapsed seconds against `QUICK_BUDGET` with no history
whatever), so FR-001 works with or without it. An earlier draft called this a prerequisite; the code
contradicts that, and it was a prerequisite only of the auto-tightening FR-003 has since dropped.

**FR-008** A failure **says what to do**, in the house style. `QUICK_BUDGET`'s message is the model: it
names the tool (`make durations`) and the shape to look for. Note
`tests/tooling/test_guard_message_durations.py` fails the gate if a guard message states how long a
command takes, so the text must quote the measured baseline rather than hard-code a duration.

**FR-009** The comparison judges only runs that **did the work** and compares like with like:
`dev/run-log/` records `result: already-verified` for short-circuits and `scope` for the scope in force.
Exclude the former; segregate the latter.

**FR-010** Moving a baseline **in either direction** leaves a **written reason** where it moves - the
single statement of that rule, which FR-003 refers to rather than restating. Down needs one as much as up
does: a baseline lowered without saying what made the target faster is how a bar ends up pinned to a
lucky run. Nothing more than that: an ordinary reviewed edit to a committed number. *This is deliberately NOT a perf-review-style ladder* - no audit
tiers, no `AS=` role, no sign-off. The perf ladder guards a different thing at a different cost.

## Decisions this spec makes (and whose they are)

**D1 - `make done`'s interim pinned baseline is 155 s. Proposed by the spec author; RATIFIED BY THE GM
on 2026-08-30, with one condition: RE-PIN once real post-172 runs exist.** The condition matters
because the 155 s came from a window spanning 2026-08-29/30, which predates feature 172's parallel
`hooks-test` - and no post-172 full-gate measurement exists yet, because every `done` run since has
short-circuited as `already-verified`. The GM was given the alternative (leave `done` unarmed until
the efficiency work stabilizes it) and declined it, on the author's own reasoning: an unarmed target
is how the slowdown went unnoticed. The original argument, unchanged:

The GM's 45 s cannot be armed today: `done` runs ~135 s and every run would fail, blocking all work. The
GM's phrasing was conditional (*"if they were down to thirty five seconds, then..."*). So an interim
number is needed and choosing it is not optional.

155 s is the median of the last 25 green reference-scope runs, and **the bar it produces via FR-004 is
201 s** - state that number when weighing this, not the baseline, because 201 s is what actually fails a
run. It is roughly 5.7x the 35 s the GM was reasoning from.

**It is deliberately loose**, because the same window runs 25 s to 334 s - a 13x spread driven by cold
roll caches after a main merge and by other sessions sharing the box. A tight bar on that distribution
would fire on noise and be escaped within a day, which is worse than no bar.

What it buys is the one thing that matters right now: `done` **cannot get twice as slow again** without
somebody stopping. The real number arrives with the efficiency work, which re-pins it; at 35 s the GM's
45 s takes over automatically (FR-002 bullet 2 - not FR-004's cap; the two agree at exactly 35 s, but
the rule that governs from there down is FR-002's).

**For the GM, if they want a different call:** the alternative is to arm `quick` now and leave `done`
unarmed until the efficiency work stabilizes it, on the grounds that a 201 s bar over a target whose
median is ~135 s today (155 s across the last 25 green reference runs) leaves a lot of room before
anything fires - and is 5.7x the 35 s the GM was reasoning from. The author chose to arm it anyway because "nearly vacuous" still stops a doubling, and an
unarmed target is how this happened in the first place.

**D2 - `done` is judged on a MEDIAN of recent runs, not on the single run. Proposed by the spec
author; RATIFIED BY THE GM on 2026-08-30.** It departs from how the GM phrased it, and they accepted
that departure knowing so, because it is BOUNDED to the interim: their literal per-run reading governs
`quick` today and governs `done` the moment its baseline reaches 35 s. The original argument,
unchanged:

The GM's words are per-run twice (*"if it takes even as much as fifteen seconds"*, *"if they take forty
five seconds to run"*), and `quick` is held to exactly that (FR-001). `done` is not, and the reason is
measured: with D1's 201 s ceiling, **7 of the last 25 green reference-scope runs are at or above it**
(201, 204, 212, 313, 315, 322, 334). A per-run bar would fire on 28% of today's normal runs - noise from
a shared box and cold roll caches, not regressions - and a guard that cries wolf weekly is escaped and
then ignored, which is this project's own stated reason for not shipping guards that fire on correct work.

So `done` compares the **median of the last 25 green runs at the same scope** - 25 because that is the
window D1's baseline was computed from, so the bar and the baseline describe the same population; a
shorter window reacts faster but is dragged further by one 334 s outlier, and a longer one reaches back
past the 08-26 change in what the gate does.

**D2 IS BOUNDED TO THE INTERIM, and this is the correction that matters most.** An earlier draft applied
the median in every state, including after `done` reaches 35 s and the GM's 45 s takes force - which
silently overturned the GM's own worked example, because a single 45 s run against a 35 s median passes.
The GM said *"if they take forty five seconds to run, then that should cause a failure"*, and that is a
sentence about a RUN. So: while the pinned baseline is above 35 s the comparison is the median; once it
is 35 s or less the comparison is the run itself, exactly as stated.

The evidence for D2 is evidence about the 155 s / 201 s regime ONLY - a 13x spread on today's gate. There
is no measurement of whether a 35 s `done` is noisy enough to need a median, and this spec does not
pretend there is. If it turns out to be, that is a question for the GM at the time, with the measurement
in hand.

`quick`, whose distribution is tight, keeps the GM's literal per-run reading throughout.

## Success criteria

**SC-001** A deliberately slowed `make quick` FAILS at 15 s, and the failure names `make durations`.

**SC-002** A deliberately slowed `make done` FAILS, on the same mechanism, from the same table.

**SC-003a** (`done`) With nothing slowed, the median of the REAL recent run-log sits under the ceiling -
not a fixture, so the bar is known not to fire on today's normal runs. **Note the shape this is testing**:
`done`'s median (155 s) is under its 201 s ceiling while 7 individual runs are not, so the criterion is
satisfiable only under D2's median comparison, and it is written to make that visible rather than
quietly true.

**SC-003b** (`quick`) A real `make quick` run passes at the 15 s bar. It is stated separately BECAUSE
`quick` has no run-log to judge from (measured: n=0 entries) and FR-007, which would give it one, is
optional. An earlier draft asked both targets to be judged against the run-log, which `quick` cannot
satisfy without building an optional requirement - the criterion leaned on a thing the previous round had
just demoted.

**SC-004** A baseline that drifts UP does not raise the ceiling. (The round-1 defect, pinned as a test.)

**SC-005** No computed ceiling exceeds a target's HARD_CEILING at any baseline.

**SC-006** The FULL row exists, is off, and switching it on is a one-line change.

**SC-007** Deleting the ratchet makes a test go red - the project's rule for any new guard.

**SC-008** *(spec author's addition, OPTIONAL - not requested by the GM.)* `make audit` shows each
target's pinned baseline and current ceiling, so "what is the bar right now" is answerable without
reading code. Drop it freely if it costs anything.

## Review history

**Round 1** (`spec-fidelity`): CHANGES REQUIRED, 7 items, all accepted:
1. FR-002 stated no bar and handed the choice to the implementing session - now D1 decides it and labels
   it as the author's, with the alternative routed to the GM rather than to the implementer.
2. FR-003 excluded the GM's constants ("not a hand-typed constant") - the GM's numbers are now HARD
   CEILINGS the mechanism sits underneath.
3. The formula was a two-point fit that loosened as the baseline drifted - now capped by `min(HARD_CEILING, ...)`.
4. FR-003 (best-known value) contradicted FR-008 (rolling median) - resolved to PINNED, with the reason.
5. FR-001 said "exceeds 15 s"; the GM said "even as much as fifteen" - now fails AT 15.
6. FR-009's re-baselining pointed at the perf ladder and could be read as a mandate to build audit tiers -
   now FR-010, explicitly minimal and explicitly not that.
7. SC-006 was unrequested - now SC-008, marked the author's and optional.

**Round 2** (`spec-fidelity`): all seven round-1 fixes confirmed real; 4 further items, all accepted:
1. The spec never said WHAT is compared to the ceiling - one run or a median. Measured consequence: at
   D1's 201 s ceiling, 7 of the last 25 green runs are at or above it, so a per-run bar fires on 28% of
   normal runs and SC-003 was unsatisfiable as written. Now decided per target in the table, with D2
   labeling the `done` departure as the author's.
2. D1 gave the baseline (155 s) but not the bar it produces (201 s), so the choice routed to the GM was
   against the wrong number. Now states both.
3. FR-001 vs FR-004 for `quick` below an 11 s baseline - now FIXED at the GM's 15 s, with automatic
   tightening below a GM-stated number explicitly rejected as the author's invention.
4. FR-007 claimed to be a prerequisite; the code contradicts it (`Makefile:691` times `quick` inline with
   no history). Now the author's OPTIONAL addition, saying plainly that the GM's bar does not need it.

**Round 3** (`spec-fidelity`): round-2 items 2 and 3 confirmed fully fixed; item 1 accepted but resolved
OVER-BROADLY, item 4's consequence missed. 5 further items, all accepted:
1. **The serious one.** D2's median was unbounded in time, so it governed `done` even after the GM's 45 s
   cap took force - where a single 45 s run against a 35 s median PASSES. That silently overturned the
   GM's own worked example (*"if they take forty five seconds to run, then that should cause a failure"*
   is a sentence about a RUN). D2 is now bounded to the interim regime, with the run itself compared once
   the cap is in force, and the spec says plainly that its evidence covers only the 155/201 regime.
2. D2's window was unspecified ("recent") - now the last 25 green same-scope runs, with the reason.
3. SC-003 required both targets to be judged against the run-log, which `quick` cannot satisfy (n=0
   entries) unless the OPTIONAL FR-007 is built. Split into SC-003a and SC-003b.
4. FR-003 required a written reason in either direction while FR-010 stated it for UP only - reconciled
   in FR-010, which is now the single statement of the rule.
5. D1's GM-facing paragraph said "a 201 s bar against a 35 s target", misstating today's state to the
   decision-maker - `done` runs ~135 s median now. Restated against the real number.

*(Round 3 was originally taken to be the last permitted round. `CLAUDE.md` raises the cap to five, and
its own text is self-contradicting on the point - "up to **three** times (raised from three by the GM on
2026-08-30); if the FIFTH round still returns changes, STOP and escalate". The escalation trigger is
unambiguous, so round 4 was taken rather than escalating. The stale word is flagged separately.)*

**Round 5** (`spec-fidelity`): **FAITHFUL.** All three round-4 fixes confirmed real; the request carried
clause by clause; every author decision labeled with whose it is; nothing missing, and nothing that
overturns a case the GM stated. Two asides applied without re-review at the reviewer's direction: D1's
stale attribution of the 45 s to FR-004's cap (it has come from FR-002 bullet 2 since round 4 - the
outcome was right, the named mechanism was not), and a clarifying note on research.md R3.

**Round 4** (`spec-fidelity`): all five round-3 fixes confirmed real; 1 live item + 1 mechanical, both
accepted:
1. **FR-002 specified `done` below a 35 s baseline TWO incompatible ways.** "Computed per FR-004 ...
   capped at 45 s" yields a 32 s bar at a 25 s baseline, while FR-001's box, the table and D1's "takes
   over" all imply a fixed 45 s. The readings coincide at exactly 35 s and diverge everywhere below it -
   which is exactly where the announced efficiency work is taking this target. Resolved to the fixed 45 s,
   because the tightening reading is auto-tightening below a GM-stated number, the very move this spec
   disowns one requirement earlier for `quick`: the GM said 15 GIVEN 11 s and 45 GIVEN 35 s, in the same
   sentence shape, and both are now treated the same way.
2. FR-004's precondition ("where a target has no GM-stated ceiling in force") excluded by its own first
   clause the only two cases it demonstrated. The worked examples are now marked as DEMONSTRATIONS that
   the formula reproduces the GM's figures - the live use of FR-004 is one target in one regime.
3. The header still advertised rounds 1-2. Corrected.

The reviewer's aside for the GM, carried forward verbatim: *"research R3 shows the gate is still 2.3x
faster than it was on 08-24, so the ratchet's baseline choice is really a question about which day counts
as 'best'. That is the GM's call to make once the efficiency work in the follow-on conversation has a
target."*

## Handoff notes

- Identified by `diagram-testing`, which did the measurement in `research.md` and is NOT implementing.
  Questions about the evidence can come back to it.
- `scripts/_gatecost.py` (feature 162) is the closest existing code - but note FR-003: its
  `median_seconds()` is a ROLLING median and is the wrong shape for the baseline. It is the right shape
  for computing a value to PIN, once.
- `dev/run-log/*.json` carries `{target, scope, seconds, result, commit}` back to 2026-08-24 for `done`.
  For `quick` it carries nothing - see FR-007.
