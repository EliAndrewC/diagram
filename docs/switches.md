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

## Do not reinstate the scope axis, and keep `idle_context`

The second axis, **scope**, was retired by feature 185 (GM 2026-09-05: *"please go ahead and retire the concept of the
scope lock and the scope unlock, i.e. retiring both the concept and the specific make targets"*), with its make targets,
the `SWEEP_OK` macro, `switches.locked_out` and `regen.py`'s one-map-per-invocation refusal. Do not bring back a piece of
it in isolation: the condition it served (map-rolling tests deferred out of a slow gate) ended with feature 174.

**`switches.idle_context` STAYS**, though it looks like part of the lock. The Makefile's `DONE_NAME` picks `idle-done`
over `done` from it, and `ci/state.py`'s `GREEN_TARGETS` deliberately omits `idle-done`: that omission is the whole
mechanism by which an unattended idle gate **neither grants nor revokes a push**. Removing the seam would make a
detached timer write a record the push honors, and nothing would catch it - the code still runs, only the recorded NAME
changes, so coverage stays full and every test passes.

`mapcheck`'s own `--scope auto|reference|all` and the `SCOPE=` make variable also stay: they are its breadth argument,
not the retired axis.
