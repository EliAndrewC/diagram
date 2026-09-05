# Tasks - feature 185

Spec: [`spec.md`](spec.md) (FAITHFUL, round 5). Request: [`request.md`](request.md).

## The rename

- [x] T01 FR-001: `lint` -> `static`, all four Makefile lines (8, 107, 973, 981)
      research: procedure
      verify: `make static` works; **`make lint` must FAIL**, not silently resolve
- [x] T02 FR-001a/FR-001c: the engine call sites - `dispatch.py:366-372` (all five strings) and
      `tools/timings.py:182-188`
      research: procedure
      verify: `make durations` runs; the ci ladder still refuses on a red static phase
- [x] T03 FR-003: the two suites that pin the phase names
      research: procedure
      verify: `test_timings.py:131` and `test_dispatch.py:103/106/107/161` green

## The scope lock

- [x] T04 FR-005/FR-005b: `SWEEP_OK` (1 def + 5 uses) and the FOUR inline `check scope` calls
      research: procedure
      verify: `make done FULL=1`, `ci-check`, `ci-merge`, `maps SCOPE=all` all still parse and run
- [x] T05 FR-004/FR-004a: the two targets, both Makefiles, plus the two already-stale forwards
      research: procedure
      verify: `make scope-lock` fails from BOTH the root and the skill
- [x] T06 FR-006/FR-006c: the scope axis inside `switches.py`, all seven sites
      research: procedure
      verify: `make switches` still reports remote; `:222` no longer emits a `scope` block
- [x] T07 FR-006a: `locked_out` and its five engine call sites, incl. mapcheck 197-210 (NOT 211)
      research: procedure
      verify: `recovering` still defined and read; `make maps SCOPE=all` works and is unrefusable
- [x] T08 FR-006b: `ci/state.py` - `_scope()`, the `scope` field, the LOCKED refusal
      research: procedure
      verify: the verification state still round-trips; no migration owed
- [x] T09 FR-008/FR-008a: `SCOPE_STATE`, `ROLL_DESELECT`, `TIER_SELECT` (incl. Makefile:847), the
      DEFERRED branch (1200), and regen's one-map refusal (supersedes 161 FR-014)
      research: procedure
      verify: `make quick` unaffected
- [x] T10 FR-009: ONLY the relaxation branch; `idle_context` and its five helpers STAY
      research: procedure
      verify: `DONE_NAME` still picks `idle-done`; `GREEN_TARGETS` still omits it
- [x] T11 FR-007a: the `scope` block out of `dev/switches.json`, and a test pinning that `read()`
      ignores an unknown key
      research: procedure
      verify: a stray `scope` key does NOT turn remote off
- [x] T12 FR-005a/FR-010: the escape census row, two whole-file deletions, seven edits, and the two
      INVERTED assertions in `tests/test_switches.py` (:43, :64/:69)
      research: procedure
      verify: full suite green at the 100% floor
- [x] T13 FR-011/FR-011a: the nine live doc surfaces; records untouched
      research: procedure
      verify: no live instruction names a retired target; `specs/`, run-log, ledgers unchanged

## Closing

- [x] T14 gate green, pushed
      research: procedure
      verify: DONE. `make done` GREEN - 2,950 passed, **22,575 statements 0 uncovered 100%**, hamlet
      floor **12,449 / 0 / 100%**. It took THREE attempts to get a run that actually ran: the first
      two short-circuited on a green record written by `make -n done`, which executes the recipe's
      `$(MAKE)` sub-invocations under `-n` and then runs its closing LOGRUN/STATE lines for real. The
      record was self-perpetuating - each short-circuit re-stamped it - so only removing
      `.git/verification-state.json` forced real work. Recorded for its own feature; NOT fixed here.
      The forced run then earned its keep immediately, naming six uncovered lines in `switches.py`
