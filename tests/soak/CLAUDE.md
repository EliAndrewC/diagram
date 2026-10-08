# `tests/soak/` - the tier ABOVE the gate

**This directory holds the tests that roll MORE than the gate's floor strictly needs** (constitution VI
v2.23.0, GM 2026-09-08, feature 216: *"the correct place for the kind of test in which we make more map
rolls than are strictly necessary is in the AWS tests. or the CI tests"*). Today it holds one:
`test_village_determinism.py`, the village roll's determinism test (two real rolls whose only unique line became a unit
test). `make soak` runs the tier by hand.

**Nothing here is collected by any ordinary run** - not `make quick`, not `make done`, not
`make test-full`. The deselection is one line, `norecursedirs` in `pyproject.toml`, chosen over an
`--ignore` repeated across the Makefile's pytest invocations because a path literal copied six times is the
stale-literal shape this repository has been bitten by. `make soak` names the path explicitly, which
`norecursedirs` still permits.

## What belongs here

The four tiers, cheapest first:

| tier | what it buys | where |
|---|---|---|
| a targeted test or module | reproducing one specific thing | `make test-file FILE=...` |
| `make quick` | fast confidence during iteration | `tests/` |
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

The engine's measured surface is `source = ["l7r"]` - the whole of it - and the 100% floor runs on a plain `make
done`. *A deselected test takes its coverage with it*, so a test that lives here contributes **no coverage**, and if it
were the only thing reaching some line, the floor would fail and say so by name. So:

- a soak test exercises **paths the gate already covers**, with different DATA - more seeds, bigger
  maps, longer runs;
- a test that reaches a line nothing else reaches is **misfiled** and belongs in `make done`.

Worked example of the rule biting: the seeds 41-44 cohort in
[`../gate/hamletgen/test_driver.py`](../gate/hamletgen/test_driver.py) looks like a soak test and is not
one. The hamlet-path floor counts what those in-process rolls execute, and the seed-dependent placer
branches (the fabric threader, the web smoother, the strip and trunk guards) are reached by rolls
rather than by fixtures. It is load-bearing for coverage, so it stays at the gate.

**When the tier earns more tests** (GM 2026-09-05): when there are **more settlement types and larger maps** to sweep -
at which point "does this hold up across seeds and at real size" becomes a question the gate genuinely cannot answer.

**What a soak run can NEVER catch** (GM 2026-09-05): *"many of the failure cases on random seeds are things like a
village lane meeting the criteria but then looking wrong"*. A map that satisfies every predicate and still reads badly
is invisible to any suite at any scale. That is the GM's eye, or the `settlement-review` agent; a soak run that comes
back green is not evidence that the maps are good.

**Don't rename it `sweep`**: *sweep* already means a run that rolls many MAPS in this repository; *soak* (the same code
held under realistic load) collides with nothing.

## Where it runs

`make soak` runs it locally. It is also what a remote run dispatches - `ci/dispatch.py`'s
`make_target()` returns `soak`, not `done` - so a remote build does the tier the laptop skipped
instead of repeating the tier it just finished. `make soak` refuses on an empty suite: non-vacuity is asserted, never
assumed.

Tests retired from here, and the placer tests that took their place: `specs/287-placer-guarantees/research.md` R8.
