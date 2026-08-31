# Feature 174 - what was measured before changing any floor

Taken 2026-08-31 in the clone `diagram-tooling`, before a line of the feature was written. The GM
stated three premises; two are checkable and one of them does not survive. Recorded rather than
quietly inherited, per the feature-172 precedent.

## R1 - the floor was not LOWERED; its SCOPE was narrowed

The Makefile's coverage phase is three checks, not one:

```
coverage report --omit='*/settlement/*,*/waterfields/*,*/interactive/*,*/overlap/*' --fail-under=100
coverage report --include='*/settlement/*'                --fail-under=$(SETTLEMENT_COV_FLOOR)   # 94
python3 -m l7r.diagram.tools.hamlet_floor                                                        # derived, 100%
```

So a hard `--fail-under=100` already exists and already passes - over **88 files / ~9,710
statements**. What sits outside it is **115 files / ~14,447 statements**: `settlement/`,
`waterfields/`, `interactive/`, `overlap/`.

**But those are not unmeasured** - they are measured by a different rule. `make hamlet-floor` derives,
from the roll cache's own records, every module the scripted rolls EXECUTE, and holds each at 100%.
That set already includes this repository's newest files (`settlement/structures/fixtures/*`,
`settlement/water_ways/*`, `waterfields/seams/*`). So the picture is not "60% of the engine is
unchecked"; it is "the hamlet path is at 100% by one rule, and everything else is averaged into a
94% ratchet".

## R2 - the ratchet's recorded reason is NOT the refactor

The GM's premise: *"We turned this off because we were doing a large refactor, and we didn't even
know which of our code would remain."*

The Makefile says otherwise, in a comment dated the day the ratchet was set:

> COVERAGE IS ENFORCED PER-MODULE since the 2026-08-16 legacy freeze ... the hand-authored pool maps
> are frozen and their gens never run, so the above-hamlet wings of settlement.py (towns, cities, the
> capital) **are exercised by nothing until those tiers convert to scripted generation**. ... RAISE
> the floor as each tier converts; NEVER lower it. 94 = measured 94.4% (447 of 8043 statements
> unreached) on 2026-08-16.

**The gap is unconverted TIERS, not refactor debris.** The GM's memory fits feature 166 (the check
battery's retirement, a genuinely large refactor) but the settlement ratchet predates it by twelve
days and was set for a different reason. This matters because it decides what 100% can mean: the
uncovered statements are town/city/capital drawing code that no generator produces, so "cover it"
means either converting those tiers (the migration plan's standing work) or writing tests against
code whose shape changes when they do.

## R3 - THE STRUCTURAL BLOCKER: a deselected test takes its coverage with it

This is the finding that decides the design, and the Makefile already states it:

> WHAT THIS COSTS, said plainly: a coverage hole in code the reference scope does not execute
> survives until the FULL run. ... That is the price of having a cheap gate at all, and it was paid
> deliberately rather than by leaving **a floor in place that could never be met**.

`make done` at reference scope deselects three ways, and every one takes real coverage away:

| deselection | mechanism | what its coverage was |
|---|---|---|
| map-rolling tests | `ROLL_DESELECT = -m "not rolls_map"` under the scope lock | most of the engine's execution |
| tier-irrelevant tests | `TIER_SELECT = --tier hamlet` | the town/city/capital wings |
| the whole of `tests/tooling/` | `conftest.py` `skip_tooling`, when the tooling stamp is fresh | `_invocation.py`, `switches.py`, `ci/*` |

So **`fail_under = 100` cannot sit on `make done` as it is scoped today** - not because the code is
uncovered, but because the run deliberately does not execute it. That is why `COV_FLOORS` is empty
and the floors are deferred to `FULL`. The peer session's report of `_invocation.py` and
`hamletgen/clearance.py` at 14.80% is this exact effect, not a coverage hole.

**The corollary, which is the whole feature**: a hard 100% floor requires a run that deselects
NOTHING. There are only two ways to have one, and they trade against the GM's other stated goal
(iteration speed):

- **release the scope lock**, so `make done` runs the whole suite - it has been on since 2026-08-25
  for feature 133's reference-hamlet period, which ended long ago (we are at 174); or
- **put the hard floor on the run the PUSH requires**, leaving `make done` cheap.

The GM's own words point at the second - *"we literally cannot complete our make done in order to
merge back into main"* - i.e. the thing that gates MERGING must enforce it.

## R4 - FULL has never been green, so there is no baseline to restore to

5 FULL-scope runs are recorded in `dev/run-log/`, all of them failures:

| when | result |
|---|---|
| 2026-08-25 | ci-check full FAILED (1070 s) |
| 2026-08-30 x4 | `failed: test-full` (539 / 499 / 947 / 503 s) |

A peer session got the first green FULL **pytest phase** on 2026-08-31 (2434 passed), and the run
still failed on both coverage floors. So "back up to 100%" is not a restoration - **this floor has
never been met in this repository's recorded history**, and the feature has to establish it for the
first time rather than re-enable it.

**Sources**: a tooling finding, not a physical one - constitution XII's source obligation does not
attach. Every claim is a measurement of this repository, reproducible by the command beside it.
