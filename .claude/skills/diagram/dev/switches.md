# The iteration switch - remote off (feature 132; the scope axis retired in feature 185)

**Load this when:** a target refused with "remote is OFF", or you are about to throw or release the
switch.

## What it is

ONE committed, repository-wide switch in one tracked file, `dev/switches.json`:

| axis | states | what it governs | throw / release |
|---|---|---|---|
| **remote** | `on` (default) / `off` | whether anything is dispatched to AWS CodeBuild, and whether the gated push may spend money | `make ci-off REASON=...` / `make ci-on REASON=...` |

`make switches` prints it, with the reason, who threw it and when. The history of throws and releases
is the file's git log - each target commits its own change.

**A REASON IS REQUIRED and there is no override.** No flag, no environment variable, no `--force`.
The switch is a tracked file, so throwing it is a diff someone reads, and releasing it is another.
That is the whole design: *"a reason someone will READ is a decision you have to defend."*

**A MALFORMED FILE FAILS CLOSED** - remote off, with `error` set and `MALFORMED` in the description.
A corrupt switch must not silently permit spending.

**AN UNKNOWN KEY IS IGNORED, and that is load-bearing.** `read()` names only `remote`, through
`data.get`, with no key iteration and no schema validation. A clone checked out from before feature
185 still carries a `scope` block; it is simply not looked at. Making this strict would send such a
file down `_closed()`, and failing closed means **remote OFF in every clone that still has one**.
`tests/test_switches.py::test_an_unknown_key_is_IGNORED_not_failed_closed` pins it.
`_closed()` has exactly three entrances: a JSON parse failure, a non-dict top level, or `_axis`
rejecting a NAMED key. Never an unrecognized one.

## Why there is only one axis now

There were two. The second, **scope**, locked every invocation to the tier's reference settlement so
that no command could roll another map. It was retired in feature 185 (GM 2026-09-05: *"please go
ahead and retire the concept of the scope lock and the scope unlock, i.e. retiring both the concept
and the specific make targets"*), and the reasoning is worth keeping because it is a good example of
a mechanism outliving its condition rather than being wrong:

- It was built for the **reference-hamlet iteration period**, when `make done` was slow and the
  map-rolling tests had to be deferred out of it to keep the loop usable.
- **Feature 174 removed that condition.** Making the coverage floors unconditional also turned every
  deselection off, so the gate runs the whole suite every time - there is nothing left to defer.
- The scope had been UNLOCKED for nine days when the GM asked, and `ROLL_DESELECT` / `TIER_SELECT`,
  the variables it drove, expanded to nothing on every run.
- It also owned the word **sweep** (`SWEEP_OK` was the scope check), which collided with the soak
  suite's first name. Retiring the lock retired the word: `cohort` is a set of seeds, `soak` is the
  tier that would run them, and nothing is called a sweep any more.

**What went with it, recorded so nobody reinstates a piece in isolation:** `make scope-lock` /
`scope-unlock` (in BOTH Makefiles - the root forwards them too), the `SWEEP_OK` macro and its five
uses, four inline `check scope` calls that were the FIRST recipe line of `done`, `ci-check`,
`ci-merge` and `maps`, `switches.locked_out` and its five engine call sites, the scope field and the
LOCKED refusal in `ci/state.py`, `SCOPE_STATE`, and **`regen.py`'s one-map-per-invocation refusal**,
which feature 161's FR-014 stated as standing doctrine and which was `locked_out` and nothing else -
FR-014 is superseded.

**What did NOT go with it, and this is the subtle one.** `switches.idle_context` STAYS. It looks like
part of the lock - it existed so an idle run could relax it - but it has a second consumer: the
Makefile's `DONE_NAME` picks `idle-done` over `done` from it, and `ci/state.py`'s `GREEN_TARGETS`
deliberately omits `idle-done`. That omission is the whole mechanism by which an unattended idle gate
**neither grants nor revokes a push**. Removing the seam would have made a detached timer write a
record the push honors - and nothing would have caught it, because the code still runs and only the
recorded NAME changes, so coverage stays full and every test passes. Only the relaxation branch died.

`mapcheck`'s own `--scope auto|reference|all` and the `SCOPE=` make variable also stay. They are its
breadth argument - *"what you mean when you know better"* - not the retired axis. The words collide;
the mechanisms never did.

## The one axis, and why it is not two

`remote` gates MONEY: it is consulted before every paid dispatch, and `ci/decision.py` prints it
first among the five conditions. `scope` gated TIME, on a gate that no longer takes enough of it to
be worth gating. Sharing a file was never a reason to keep both.
