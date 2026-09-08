# `tests/soak/` - the tier ABOVE the gate

**This directory holds the tests that roll MORE than the gate's floor strictly needs** (constitution VI
v2.23.0, GM 2026-09-08, feature 216: *"the correct place for the kind of test in which we make more map
rolls than are strictly necessary is in the AWS tests. or the CI tests"*). It was declared empty on
2026-09-05 as the home of a tier this project wants and does not yet run; its first test arrived with feature
216 - the seed-43 kink's strict xfail, a roll that carried no coverage line and so could not stay in the gate.
The tier is still not RUN by anything ordinary; `make soak` runs it by hand.

**Nothing here is collected by any ordinary run** - not `make quick`, not `make done`, not
`make test-full`. The deselection is one line, `norecursedirs` in the skill's `pyproject.toml`,
chosen over an `--ignore` repeated across the Makefile's six pytest invocations because a path
literal copied six times is the stale-literal shape this repository has been bitten by. `make soak`
names the path explicitly, which `norecursedirs` still permits (measured, 2026-09-05).

## What belongs here

The four tiers, cheapest first:

| tier | what it buys | where |
|---|---|---|
| a targeted test or module | reproducing one specific thing | `make test-file FILE=...` |
| `make quick` | fast confidence during iteration | `tests/`, ~11 s |
| `make done` | 100% coverage, every code path exercised | the whole gate |
| **the soak** | **the same code under REALISTIC LOAD** | **here** |

The gate proves the code is *exercised*. It does not prove the code is *good*: it runs a small number
of seeds and packs small maps, because its job is to reach every branch quickly. The soak is the
answer to the next question - does this hold up over many random seeds, and on maps at the size we
actually ship?

Concretely, the shapes that belong here:

- **the same generator over many seeds** - dozens, not the gate's four
- **the same assertions on LARGER maps** - a full village or town rather than the reference hamlet
- **cost and termination under load** - a seed that takes pathologically long, a generator that does
  not terminate, a `GEN_TIME_BUDGETS` entry that only blows on an unusual roll
- **invariants that are cheap per map but only meaningful in bulk** - seating rates, acreage error,
  the distribution of a knob across a cohort

## The membership rule, and it is MECHANICAL

> **A test belongs here if removing it does not change coverage.**

This is not a matter of taste, and it is not enforced by anyone remembering it. The engine's measured
surface is `source = ["l7r"]` - the whole of it - and the 100% floor runs on a plain `make done`.
Feature 174 established the corollary in the Makefile's own comment: *a deselected test takes its
coverage with it*. So a test that lives here and is never collected locally contributes **no
coverage**, and if it were the only thing reaching some line, the floor would fail and say so by name.

The consequence is the rule above, enforced by the floor rather than by review:

- a soak test exercises **paths the gate already covers**, with different DATA - more seeds, bigger
  maps, longer runs;
- a test that reaches a line nothing else reaches is **misfiled** and belongs in `make done`.

Worked example of the rule biting: the seeds 41-44 cohort in
[`../gate/hamletgen/test_driver.py`](../gate/hamletgen/test_driver.py) looks like a soak test and is not
one. The hamlet-path floor counts what those in-process rolls execute, and the seed-dependent placer
branches (the fabric threader, the web smoother, the strip and trunk guards) are reached by rolls
rather than by fixtures. It is load-bearing for coverage, so it stays at the gate.

## Why it is empty, honestly

The tier this directory names is one the project has drifted away from rather than one it never had.
The intent is recorded in the cohort test's own comment, in the GM's words: *"against many random
seeds on the same map ... is something either more suited to a EXHAUSTIVE=1 Test run or better yet
best farmed out to the AWS tests"*.

What happened is that feature 174 made the coverage floors unconditional, and the switch that enables
them (`COV_FLOORS=1`) is also the switch that turns every deselection off and sets `L7R_TESTS_FULL`.
So the four-seed cohort that was meant to be the wide, farmed-out tier began rolling on every local
gate. Nothing was done wrong; a stricter gate absorbed the tier above it.

**And the failure category that tier was built for is largely gone.** Feature 166 deleted the
post-placement check battery, so there is no automated check on a generated map any more - a rule
about a map is a unit test of the placer that makes it. The wide sweep's own history says the same
thing: it was 7 of 12 seeds passing when the experiment started and 24 of 24 by 2026-08-12. The
residual per-seed differences are pinned as expected failures.

So this is not a directory anyone should rush to fill. The honest statement of when it earns its
keep, from the GM (2026-09-05): when there are **more settlement types and larger maps** to sweep -
at which point "does this hold up across seeds and at real size" becomes a question the gate genuinely
cannot answer.

**What a soak run can NEVER catch, stated so nobody expects it to** (GM 2026-09-05): *"many of the
failure cases on random seeds are things like a village lane meeting the criteria but then looking
wrong"*. A map that satisfies every predicate and still reads badly is invisible to any suite at any
scale. That is the GM's eye, or the `settlement-review` agent. Adding seeds adds no resolution there,
and a soak run that comes back green is not evidence that the maps are good.

## Why `soak`, and not `sweep`

**`sweep` was the first name and it was WRONG, caught by the naming audit the same day** (GM
2026-09-05). This repository used *sweep* for something else: the scope-lock check was
`SWEEP_OK`, and `switches.py` described a locked scope as one where *"every sweep refuses"* - a sweep
there meant **a run that rolls many MAPS**, which the lock existed to forbid. (The lock itself was
retired in feature 185, which is what finally left one meaning per word.) Keeping the name would have put
`$(SWEEP_OK)` - the guard asserting a target is NOT a sweep - three lines from a target called
`sweep`. **Soak** is the standard term for the thing this directory is actually for: the same code
held under realistic load for an extended run. It collides with nothing.

## Where it runs

`make soak` runs it locally. It is also what a remote run dispatches - `ci/dispatch.py`'s
`make_target()` returns `soak`, not `done` - so a remote build does the tier the laptop skipped
instead of repeating the tier it just finished.

**Remote is currently OFF** (`make switches`), and turning it on before there are soak tests would
buy a vacuously green build. `make soak` refuses on an empty suite for exactly that reason: this
project's rule is that non-vacuity is asserted, never assumed.

**`test_seatings.py` (feature 217, 2026-09-08)**: the three seating behavior tests - the `cluster_seeds` cloud alone,
the lane frontage alone, the frontage stopping at one household - on copies of one partial roll in a child. Their one
coverage line is `tests/hamletgen/homesteads/test_seats.py`; what they assert is behavior, which this tier is for.

**`test_polder_fall_0.py` (feature 219, 2026-09-08)**: the polder-grid archetype on Polder seed 12 - the reservoir walk on
the one seed that needs it, the grid solved to its acreage with every household seated and the dike gated, the keep-outs,
the lanes bending like paths, the ratchet's seating and acreage. Its three engine lines are unit tests in
`tests/hamletgen/test_water.py`; the pool ships no polder-grid map, so until this tier runs the archetype's behavior is
proved by nothing (stated to the GM at the feature's landing).
