# Feature 185 - retire the scope lock, and rename `lint` to `static`

**Status**: draft, pre-implementation
**Request**: [`request.md`](request.md) - the GM's words verbatim
**Predecessor**: feature 184, whose spec records both of these as authorized and owed

## Summary

Two removals the GM asked for after the naming audit. They are one feature because they are the same
kind of change - a name or a mechanism that stopped matching what the project does - and because the
second subsumes a terminology question the first raised.

1. **`make lint` becomes `make static`.** It runs `ruff check --fix` plus three custom guards; it has
   not been "linting" for some time.
2. **The scope lock is retired entirely** - both make targets, the `SWEEP_OK` guard, the scope axis
   in `switches.py`, its tests and its doctrine. **The remote switch STAYS.**

## Why the scope lock goes

It was built for the reference-hamlet iteration period (feature 132), when the gate was slow and
multi-map rolls had to be deferred out of it. **Feature 174 removed the condition it existed for**:
`COV_FLOORS=1` is unconditional now, which also turns every deselection off, so the gate runs the
whole suite every time and there is nothing left to defer. The scope has been UNLOCKED since
2026-08-27.

**What it costs to keep** is not CPU - it is a live concept that every future reader has to learn and
that no longer maps to anything. It is also the source of the word *sweep*, which collided with the
soak suite's first name hours after that name landed (feature 184, D1).

## Functional requirements

### The rename

- **FR-001** `make lint` MUST become `make static`. The target, its `.PHONY` entry, the gate's phase
  list, and every doc that names it as a target.
- **FR-002** `format` and `typecheck` MUST NOT be merged into it. They differ, and the gate reports
  each phase separately so a failure names itself; merging would lose that. Recorded in 184's FR-008
  and unchanged here.
- **FR-003** Any guard suite that asserts the gate's phase NAMES must move with it. A phase list is
  a contract that something checks.

### The scope lock

- **FR-004** `make scope-lock` and `make scope-unlock` MUST be removed, with their `.PHONY` entries.
  A phony name with no recipe still resolves and exits 0 - the trap feature 184 hit with `tripwire`.
- **FR-005** `SWEEP_OK` MUST be removed at all 7 sites. The targets it guarded (`cohort`, `test-full`,
  `perf`, `perf-gate`, `soak`, `maps SCOPE=all`, `cache-audit`) keep working with no gate on scope.
- **FR-006** The SCOPE AXIS MUST be removed from `switches.py` - `DEFAULT_SCOPE`, `scope_locked`,
  the axis in `Switches`, the `check scope` subcommand and the scope half of the rendered output.
  **`make switches` MUST still work and MUST still report the remote state.**
- **FR-007** **THE REMOTE SWITCH STAYS.** `ci-off` / `ci-on`, `remote-enabled` as a dispatch
  condition, and the `remote` axis are untouched. The GM retired the scope lock, not the switches.
- **FR-008** The scope-dependent test machinery MUST go with it: `ROLL_DESELECT`, `TIER_SELECT` and
  the "map-rolling tests DEFERRED" branch exist only to serve a locked scope.
- **FR-009** **Feature 136's IDLE-CONTEXT RELAXATION MUST GO TOO, and this is the subtle one.**
  `switches.idle_context` exists so an idle run may relax the scope lock - *"unforgeable by a
  session"*. With no lock there is nothing to relax, so the seam becomes dead code that still reads
  as a security boundary. It MUST be removed, and `idle-tests` MUST keep working without it.
- **FR-010** `tests/test_switches.py` and `tests/tools/test_scope_lock.py` MUST be reduced to what
  still exists. `test_scope_lock.py` tests only the retired axis and is expected to go entirely;
  `test_switches.py` keeps its remote-axis cases. **The 100% floor is the check on this**: a test
  deleted with its subject is correct, a test deleted while its subject lives fails the floor.
- **FR-011** `dev/switches.md`, the skill `CLAUDE.md` rows and the root `CLAUDE.md` rows MUST stop
  describing a mechanism that does not exist. The RECORD of why it existed and why it went is kept
  here and in `dev/switches.md`, which becomes the remote switch's doctrine.

### What this feature does not do

- **FR-012** It does not touch `idle-tests`, `make reference`, `make audit`, or any diagnostic. Those
  were questioned in the same conversation; 184's D2, D3 and D4 record the findings, and D3/D4 remain
  OPEN for the GM.
- **FR-013** It does not rename `FULL=1`, for the reason 184's D0 measured: `full` is a stored scope
  value in 7 `dev/run-log` records, so a rename reaches data.
- **FR-014** It removes no OTHER guard. `SWEEP_OK` goes because the axis it consults goes.

## Decisions Recorded

- **D1 - the remote switch survives and the scope switch does not**, though they share a file and a
  format. The remote switch gates MONEY and is consulted before every paid dispatch; the scope switch
  gated TIME, on a gate that no longer takes enough of it to be worth gating. One is load-bearing and
  the other is a holdover, and sharing a file is not a reason to keep both.
- **D2 - the idle-context seam goes with the lock (FR-009), and this is the item most likely to be
  missed.** It reads as a privilege mechanism - a run descending from the idle timer may do something
  a session may not - so a future reader could easily preserve it out of caution. With the lock gone
  it grants a privilege over nothing. A dead security boundary is worse than none: it invites code to
  be written that assumes it still means something.
- **D3 - the tests are DELETED, not skipped or marked.** The 100% floor is what makes this safe:
  delete a test whose subject is gone and coverage is unchanged; delete one whose subject lives and
  the floor names the uncovered lines. The floor is the check, not the author's judgment.
