# `tests/soak/` - the tier ABOVE the gate

**This directory is deliberately EMPTY.** It is not an oversight and it is not a stub waiting to be
filled in by whoever notices it next. It is the declared home of a tier of testing this project wants
and does not yet have, kept as structure so that when the work arrives there is no argument about
where it goes.

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
2026-09-05). This repository already uses *sweep* for something else: `SWEEP_OK` is the scope-lock
check, and `switches.py` describes a locked scope as one where *"every sweep refuses"* - a sweep here
means **a run that rolls many MAPS**, which the lock exists to forbid. Keeping the name would have put
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
