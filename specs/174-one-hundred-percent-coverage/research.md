# Feature 174 - what was measured before changing any floor

Taken 2026-08-31 in the clone `diagram-tooling`, before a line of the feature was written. The GM
stated three premises; two are checkable and one of them does not survive. Recorded rather than
quietly inherited, per the feature-172 precedent.

## R1 - SUPERSEDED (see the correction at its end)

## R1 - the floor was not LOWERED; its SCOPE was narrowed

The Makefile's coverage phase is three checks, not one:

```
coverage report --omit='*/settlement/*,*/waterfields/*,*/interactive/*,*/overlap/*' --fail-under=100
coverage report --include='*/settlement/*'                --fail-under=$(SETTLEMENT_COV_FLOOR)   # 94
python3 -m l7r.diagram.tools.hamlet_floor                                                        # derived, 100%
```

So a hard `--fail-under=100` already exists over a subset of the tree.

**CORRECTION (2026-08-31, spec review round 2).** Two things in the sentence that followed were
wrong and are struck: that check does NOT pass - the clean run reports `Coverage failure: total of
99 is less than fail-under=100`, 54 missing at the time, 33 now - and the file/statement counts
quoted here (88 files / ~9,710, and 115 / ~14,447 below) do not reconcile with the measured set
(**182 files / 20,618 statements**, R7's clean run). They were counted by walking the tree with an
AST rather than by reading the coverage report, and they are not the same population. **Use the
measured numbers; these are kept only so the error is visible.** What sits outside it is **115 files / ~14,447 statements**: `settlement/`,
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

## R5 - WHAT THE CHEAP VERSION WOULD COST, measured (the GM's question, 2026-08-31)

> I wonder whether we are able to reach one hundred percent code coverage on make done with a less
> expensive version of the tests even if what we would be testing is less valuable than the full
> tests ... one hundred percent code coverage is different from the kind of end to end testing, which
> is being done in the full tests, which is more valuable and will catch more actual bugs.

Four numbers, all taken on the same tree within an hour:

| run | wall | what it is |
|---|---|---|
| `make done` today | **89 s** (median of 283) | the iteration gate: no floors, `tests/full` ignored, tooling skipped, coverage traced only over the diff |
| the whole suite, NO coverage at all (`make durations`, `L7R_TESTS_FULL=1`) | **50 s** | 2,435 tests. **Every test in the repository, including the expensive tree, runs in 50 s when nothing is traced** |
| `tests/full` alone, under the gate's own tracing | **56 s** | 25 tests - the pool-map rolls |
| `make test COV_FLOORS=1` (the literal ask) | **237 s** | the whole suite + full coverage tracing + both floors |

**The finding that answers the question: the tests are not the expense - the COVERAGE TRACING is.**
The entire suite runs in 50 s untraced and 237 s traced, so ~185 s of the 237 is measurement
overhead, not testing. The `tests/full` tree the gate currently ignores is 56 s of the total, and
only ~6 s of that is its tests; the rest is tracing them.

**So the GM's premise is right and the cheap version exists, but the lever is not the one either of
us named.** Dropping the expensive END-TO-END tests would save ~6 s of run time and lose the
bug-finding they buy. What costs 2.7x is asking coverage to watch everything - and that price is
paid once per gate regardless of which tests run.

**What this rules in**: `make done` CAN carry a hard 100% floor for **+148 s** (89 -> 237), with the
end-to-end sweeps included rather than sacrificed. What it rules out is the idea that a cheaper,
less valuable test set would get there faster - the tests were never the cost.

**Sources**: measurements of this repository on 2026-08-31, each reproducible by the command in the
row beside it.

## R6 - TWO MEASUREMENT HAZARDS, both hit in one session

**A concurrent pytest CORRUPTS a running coverage measurement.** A `make test-full` was running while
this session ran `make test-file` and `make cov-file` beside it; both write the same `.coverage` data
file, and the run reported **44%** where the same tree had measured **95%** minutes earlier. It looks
exactly like a catastrophic regression. The skill's own dev-loop doc already says *"Never run a
pytest BESIDE a running gate"* and gives a different reason (two writers on the same pool maps); the
coverage data file is a second, quieter reason for the same rule. **Discard such a run; do not
diagnose it.**

**PER-TEST TIMINGS ON THIS BOX CARRY A HYBRID-CPU DISTORTION** (peer session, 2026-08-31). `lscpu`
reports an Intel Core Ultra 7 155H: 22 CPUs, P-cores plus E-cores. Under xdist a worker may land on
either, and a batch's wall time is set by its slowest worker - so a test that "got slower" may simply
have landed on an E-core, and two runs of identical code can differ materially. **This qualifies
R5's cost numbers** (89 s / 237 s): the RATIO is large enough to survive the noise, but neither
figure is a precise constant, and any future ratchet tuned on this box inherits the same lottery.
Coverage RESULTS - which lines executed - are unaffected; only the timings are.

The peer flagged a live consequence worth checking separately: `_ratchet.py` fails `make quick` at a
hard 15 s on the run itself, so a quick run whose heaviest tests land on E-cores while another
session is busy could fail as a false regression. Not measured here; recorded so it is not
rediscovered from scratch.

## R7 - the dead-code deletion, independently verified (and one claim of mine corrected)

An adversarial reviewer was asked to break the 8 deletions of commit `3650e055`, having been told
that I had called `waterfields/hill.py` dead an hour earlier and been wrong. **All 8 SAFE**, on
evidence stronger than the grep I used:

- **the executed-function record**, which is the check I should have run first: `.gencache/rolls/*/meta.json`
  records every engine function a roll actually ran, and **no roll record executes anything in
  `l7r/diagram/overlap/`** - the generation path never enters that package. That is a positive
  statement about what runs, where a grep is only a negative one about what is written.
- **pre-166 archaeology** (`git grep <name> 70bfa4f7^`): every consumer of every one lived inside
  `check_village/`, which feature 166 deleted.
- the frozen `.gen.py` channel - the one that made `hill.py` live - is **empty** for all 8.

**A correction to my own commit message.** It says the only consumers were
`check_village/test_common_geometry.py`. That is narrower than the truth: `unit_dir`'s real consumer
was the check SEGMENT `segments_07b::channels_flow_downhill`, `in_ellipse` had five segment
consumers, `sweep_hi` two, and `kiln_quarters` / `seg_to_rect_dist` / `clip_to_convex` one each. The
conclusion holds - all of those are deleted - but the stated reason was too narrow, and the record
should say what was actually true. (History is never rewritten here, so the correction lives here.)

**`_ditch_plankable` was the special case and 166 already answered it.** The footbridge rule still
has teeth in the PLACER - `settlement/city/bridges.py::_plank_reaches_useful_ground` implements the
both-banks useful-ground test, and `tests/gate/test_crossings_and_cover.py` says in as many words
that *"the retired check re-derived it through its own copy of the predicate"*. `_ditch_plankable`
was that copy. Deleting the copy while keeping the prose is right.

**Three things the deletion ORPHANED, fixed in the follow-up commit** (Principle XIV - a defect found
in the course of the work is fixed in that work):

- `FOOT_ABUTMENT`, `FOOT_BANK_REACH`, `FOOT_VILLAGE_REACH` (`overlap/matrix.py`): the two deleted
  functions were their only consumers, so the deletion made them dead.
- the comment above them still said *"the placement engine enforces it, these checks re-verify from
  the manifest"* - pointing at functions that no longer exist.
- `pt_to_rect` (`overlap/taxonomy.py`): `seg_to_rect_dist` was its only call site.
