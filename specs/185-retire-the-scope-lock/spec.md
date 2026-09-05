# Feature 185 - retire the scope lock, and rename `lint` to `static`

**Status**: draft, pre-implementation. Review round 1 returned ELEVEN items; all applied. One of
them (FR-009) was not a wording fix - the requirement as drafted would have shipped a regression the
100% floor cannot see. See D2.
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

- **FR-001** `make lint` MUST become `make static`. **FOUR sites, named by line, because missing the
  third re-creates the exact trap FR-004 warns about:**

  | line | what |
  |---|---|
  | 8 | the `.PHONY` entry |
  | 107 | the gate's phase loop, `for phase in lint format typecheck; do` |
  | **973** | **`lint format typecheck test: | guard`** - a TARGET-POSITION declaration, none of the other three |
  | 981 | the target and its recipe |

  Rename 981 and leave 973 and **`make lint` still resolves** - declared with an order-only
  prerequisite and no recipe - and exits 0 silently. That is FR-004's own sentence: *"A phony name
  with no recipe still resolves and exits 0."* No test asserts `make lint` fails, and a coverage floor
  cannot see a Makefile target, so nothing would catch it. Also every doc that names it as a target.
- **FR-001a** **TWO ENGINE CALL SITES invoke it BY NAME and MUST move with it** - neither is reached
  by FR-001's enumeration or FR-003's guard suites:
  - `ci/dispatch.py:366` - `["make", "--no-print-directory", "lint", "format", "typecheck"]`, the
    local pre-dispatch ladder. Missing it breaks every `ci-check` and `ci-merge`.
  - `tools/timings.py:182-188` - the phase roster `("lint", "lint (ruff check + duplicate-def scan)")`
    followed by `sh(["make", phase])`. Missing it breaks `make durations`.
- **FR-001c** **THE ONE OPEN DECISION IN THIS SPEC, decided: ALL FIVE `lint` strings in
  `dispatch.py` are renamed, not just the command.** Only `:366` must change for correctness; the
  other four are an event tag, a verdict and two messages:

      367  ctx.events.append(f"lint:{rc}")
      370  ctx.out("ci: lint/format/types FAILED locally - nothing dispatched")
      371  return Outcome(rc=1, verdict="REFUSE(lint)")
      372  ctx.out("ci: lint, format, types clean - starting the build ...")

  **Decided by measurement**: none is consumed outside `dispatch.py` and its own suite - no stored
  record, no hook, no buildspec - so unlike `FULL` (FR-013, where `full` is a stored run-log value)
  there is no data argument for keeping them. Leaving them would have the event log and the verdict
  name a phase that does not exist, which is precisely the staleness feature 184 existed to remove
  and which FR-011a forbids in live text. Renaming all five obliges updating
  `tests/tooling/ci/test_dispatch.py:161`'s `events` assertion.
- **FR-001b** Historical `dev/run-log/` records keep the OLD phase name (`"result": "failed: lint
  test"` and similar). They are accounts of runs that happened. Stated because FR-013 declines the
  `FULL` rename on a data argument, and the same argument applies here - the difference is that the
  GM asked for this rename directly, so it proceeds and the records simply stay as written.
- **FR-002** `format` and `typecheck` MUST NOT be merged into it. They differ, and the gate reports
  each phase separately so a failure names itself; merging would lose that. Recorded in 184's FR-008
  and unchanged here.
- **FR-003** The suites that assert the phase NAMES move with them. This was the only requirement
  stating a rule and leaving the sites to be found; there are TWO, and both go red on the rename:
  - `tests/tools/test_timings.py:131` - `assert [c[1] for c in fake.calls] == ["lint", "format",
    "typecheck", "test"]`, which is what PINS FR-001a's `timings.py` change;
  - `tests/tooling/ci/test_dispatch.py:103, 106, 107, 161` - `ScriptedSh` keys the scripted shell on
    the literal `"lint format typecheck"` string and then asserts `REFUSE(lint)`, the failure message
    and `events == ["lint:0", ...]`. This is what PINS FR-001a's and FR-001c's `dispatch.py` changes.

### The scope lock

- **FR-004** `make scope-lock` and `make scope-unlock` MUST be removed, with their `.PHONY` entries.
  A phony name with no recipe still resolves and exits 0 - the trap feature 184 hit with `tripwire`.
- **FR-005** `SWEEP_OK` MUST be removed: **one definition (Makefile:288) and FIVE uses** - `cohort`
  (327), `cache-audit` (350), `perf-gate` (509), `perf` (949), `test-full` (1126) - plus its two prose
  mentions (1145, 1147). An earlier draft said seven sites and listed `soak`, which carries no scope
  guard at all, and `maps SCOPE=all`, which is **a separate inline call** (`Makefile:943`, with its
  own `GUARD_EDIT_OK` at 946) and MUST be removed in its own right or it will be missed.
- **FR-005b** **THERE ARE FOUR INLINE `check scope` CALLS, not one, and they are FIRST RECIPE LINES.**
  Round 1 broke out `maps SCOPE=all` as separate from `SWEEP_OK`; it is one of four of the same shape,
  and feature 132's own T05 enumerates exactly this set:

      Makefile:89   done      @$(if $(FULL),$(SWITCH) check scope "done FULL=1",true)
      Makefile:642  ci-check  @$(if $(FULL)$(TARGET),$(SWITCH) check scope "ci-check ...",true)
      Makefile:652  ci-merge  @$(if $(FULL),$(SWITCH) check scope "ci-merge FULL=1",true)
      Makefile:943  maps      @$(if $(filter all,$(SCOPE)),$(SWITCH) check scope "maps SCOPE=all",true)

  **This is a BREAK, not a documentation gap.** FR-006 removes the `check scope` subcommand, and
  `main()` declares `add_argument("axis", choices=("remote", "scope"))` at three places (280, 284,
  287). With `scope` gone from `choices`, argparse exits 2 - and because these are the FIRST line of
  each recipe, `make done FULL=1`, `make ci-check FULL=1`, `make ci-check TARGET=...` and
  `make ci-merge FULL=1` would each die before doing anything. That is the GM's own full gate and both
  paid dispatch routes. All four MUST go, with their `GUARD_EDIT_OK` comments (Makefile:90, the blocks
  above 642 and 652, and 946).
- **FR-005a** **The DERIVED ESCAPE CENSUS will go red and MUST be updated in the same change.**
  `tests/tooling/test_guard_firing_log.py:188` classifies `"SWEEP_OK": ("not-an-escape", ...)`, and
  `test_the_escape_census_is_derived_from_the_tree` asserts BOTH directions - a token classified but
  no longer in the tree fails. Deleting the macro without deleting that row fails the gate.
- **FR-006** The SCOPE AXIS MUST be removed from `switches.py` - `DEFAULT_SCOPE`, `scope_locked`,
  the axis in `Switches`, the `check scope` subcommand and the scope half of the rendered output.
  **`make switches` MUST still work and MUST still report the remote state.**
- **FR-006c** **FR-006's list of `switches.py` sites was PARTIAL and presented as complete** - the
  third instance of the shape that produced rounds 1 and 2. All SEVEN carry the axis:

  | site | what it is |
  |---|---|
  | `:61` `SCOPE_STATES` | the state tuple; the draft named `DEFAULT_SCOPE` but not this |
  | `:94` `_closed()` | builds `Axis("reference", why)`; fail-closed becomes remote-only |
  | `:212` `allowed = {"remote": ..., "scope": ...}` | `write()`'s axis dispatch table |
  | `:219` | `write()`'s two-branch `Switches(...)` construction, becomes single-axis |
  | **`:222`** | **the line that EMITS the `scope` block.** FR-007a requires that block gone from `dev/switches.json`, and nothing named the line that writes it - so an implementer could delete it by hand and have the next `make ci-off` write it straight back |
  | `:247-251` | `refusal()`'s `elif axis == "scope"` branch - a different function from `check` |
  | `:307-311` | `main()`'s `set` handler and its four-line "scope UNLOCKED. Nothing rolled a sweep..." reminder, keyed on `a.axis == "scope"` - reached by neither `check scope` nor `describe()` |

  Most self-correct under a type error or the 100% floor. **`:222` does not**, and it is the one
  FR-007a silently depends on.
- **FR-006a** **`switches.locked_out()` MUST go, and it has FIVE ENGINE CALL SITES** - the largest
  thing the first draft did not know about: `pipeline/regen.py:86`, `tools/cohort_audit.py:122`,
  `tools/perf_snapshot.py:314`, `tools/cache_audit.py:228`, and `tools/mapcheck.py:204-206`, which
  also reads `.scope_locked` directly and rewrites `a.scope` to `"reference"` at :209. Each call site
  MUST be removed, and mapcheck's locked branch MUST go with it - **lines 197-210, NOT 197-211.**
  Line 211 is `recovering = a.scope == "reference" or (a.scope == "auto" and not prev_ok)`, the
  SURVIVING state machine, read again at 215, 222, 223, 230 and 245. An earlier draft said 204-211;
  following it literally produces a `NameError`. The comment (197-201), the local import (202), the
  `locked` read (204) and both `if locked` branches (205-210) go; `recovering` stays.
  **BUT `mapcheck`'s OWN `--scope` SURVIVES UNTOUCHED, and this needs saying because the words
  collide.** `mapcheck.py:190`'s `--scope choices=("auto","reference","all")`, its `SCOPE` environment
  default, and the `SCOPE=` make variable are mapcheck's BREADTH argument - *"what you mean when you
  know better"* (Makefile:171) - not the switch axis, and the GM did not ask to retire them. An
  implementer reading "retire the scope" beside "remove `maps SCOPE=all`'s guard" could easily take
  the variable with it. Only the LOCK CHECK in front of them goes: `make maps SCOPE=all` keeps
  working and simply stops being refusable.
- **FR-006b** **`l7r/diagram/ci/state.py` is a live consumer and one part BREAKS OUTRIGHT.**
  `_scope()` (169-174) returns `switches.read(...).scope.state`; `VerificationState.scope` (:59) is
  written at :132/:185 and parsed at :97; and :216-217 carries the refusal *"`make done` was green
  ... while scope was LOCKED ... they are owed"*. All three go. **No migration is owed for
  `.git/verification-state.json`**: it is gitignored and `data.get("scope", "")` tolerates absence -
  stated here rather than left for an implementer to wonder about.
- **FR-007** **THE REMOTE SWITCH STAYS.** `ci-off` / `ci-on`, `remote-enabled` as a dispatch
  condition, and the `remote` axis are untouched. The GM retired the scope lock, not the switches.
  Separability was VERIFIED, not assumed: the remote axis shares no code with the scope axis, and
  `ci/decision.py`'s `scope` field is the unrelated CI run scope (`reference|full`).
- **FR-007a** The committed `dev/switches.json` currently carries a `scope` block. It MUST be deleted
  in this feature's commit, and `read()` MUST go on IGNORING an unknown key rather than failing
  closed - **failing closed on a stray `scope` key would turn `remote` OFF in every clone.** Today
  `_axis(data.get(...))` reads only named keys - `read()` (136-141) names exactly two, both through
  `data.get`, with no key iteration and no schema validation. **`_closed()` has exactly three
  entrances**: a JSON parse failure, a non-dict top level, or `_axis` rejecting a NAMED key. Never an
  unrecognized one. Naming the three is what makes the test writable, so it is stated here rather
  than left for the implementer to rediscover.
- **FR-008** The scope-dependent test machinery MUST go with it: `ROLL_DESELECT` (Makefile:1058),
  `TIER_SELECT` (1104) and the "map-rolling tests DEFERRED" branch (Makefile:1200) exist only to serve a locked scope
  - both are defined through `SCOPE_STATE` (1057), which is `$(SWITCH) state scope`, so with the axis
  gone they expand empty unconditionally. **`TIER_SELECT` is also used by `make quick` (Makefile:847)**
  - behavior-neutral to remove, but named so `quick`'s recipe is not disturbed by accident.
- **FR-008a** Removing `locked_out` from `regen.py` retires the **ONE-MAP-PER-INVOCATION** refusal,
  which feature 161's FR-014 states as a standing requirement and which `switches.py`'s docstring
  calls "the whole carve-out under the lock". It fires never today (scope unlocked), so removal is
  behavior-neutral - but a reader could reasonably think it is independent doctrine. It is not: it
  goes with the lock, and **feature 161's FR-014 is thereby superseded.** Said explicitly because
  this is the kind of rule a later session would otherwise reinstate.
- **FR-009** **ONLY THE RELAXATION BRANCH of feature 136's idle context goes. `idle_context` ITSELF
  STAYS.** An earlier draft required removing the whole seam on the reasoning that it exists only to
  relax the lock. **That is false and would have broken the idle runner's safety property**, which no
  test and no coverage floor would have caught, because the code still executes - it just records
  under the wrong name:
  - `Makefile:934-935` - `IDLE_CTX = $(SWITCH) idle` and then
    `DONE_NAME = $(if $(filter 1,$(IDLE_CTX)),idle-done,done)`;
  - `DONE_NAME` is what the `done` target writes to the run log and the verification record
    (Makefile 101, 111, 127, 129, 139-141);
  - `ci/state.py:48` has `GREEN_TARGETS = ("quick", "reference", "test-file", "done")` - **`idle-done`
    is deliberately absent**, and that absence is the entire mechanism by which an unattended idle
    gate "neither grants nor revokes a push" (feature 136 D1/FR-006b).
  Remove `idle_context` and `DONE_NAME` collapses to `done`, so a detached timer would write a
  `green-local done` record that `already_verified` and the push both honor. **An unattended run would
  start granting pushes.**
  **What dies**: `switches.py:142`'s `if sw.scope_locked and idle_context(skill)` branch and the
  `[RELAXED: the idle run, feature 136]` Axis it builds. **What stays**: `idle_context`, `_ancestors`,
  `_proc_status`, `_cmdline`, `IDLE_TIMER_MARK`, the `switches idle` CLI subcommand
  (`switches.py:297-299`) and their tests.
- **FR-010** The test surface is LARGER than the first draft knew, and part of it needs EDITS rather
  than deletion:
  - **DELETE ENTIRELY**: `tests/tools/test_scope_lock.py` - verified, all five tests exercise only the
    retired axis.
  - **DELETE ENTIRELY**: `tests/tooling/ci/test_state.py:84-98`,
    `test_a_locked_scope_record_does_not_survive_the_unlock` - an EIGHTH file the draft missed, and
    the only test of the refusal FR-006b removes. It calls `switches.write(skill, "scope", ...)`,
    which raises `ValueError` the moment `write()` is single-axis.
  - **TWO ASSERTIONS IN `tests/test_switches.py` INVERT rather than merely reference**, and they are
    the ones an implementer would otherwise "fix" the wrong way:
    - `:64` parametrizes malformed-file cases including `'{"scope": "reference"}'` and
      `'{"remote": {"state": "on"}, "scope": {"state": "all"}}'`. Both are malformed ONLY because of
      the scope axis. After FR-007a they are **VALID**, so `:69`'s
      `assert s.error and s.remote_off and s.scope_locked` FAILS. Both parameters go. **Today this
      test asserts the opposite of the property FR-007a asks to pin** - and the tempting fix, making
      `read()` strict about unknown keys, is exactly what FR-007a warns would turn `remote` OFF in
      every clone.
    - `:43` `assert set(data) == {"remote", "scope"}` - the written-file shape. Becomes `{"remote"}`.
      This is the assertion that PROVES FR-007a's outcome, so it is named rather than left to taste.
    Also needing edits and unlisted before: 32, 37-38, 47-49, 73, 83-84, 92-93, 102, 123 (the
    rendered `"scope   unlocked   (default)"` row), 132-133, 135, and 195/200 (`state scope`, the CLI).
  - **EDIT**: `tests/tooling/test_switches.py` - a SECOND, distinct switches suite the draft missed.
    `test_make_sweeps_refuse_under_the_lock` (35-39) and the scope half of
    `test_make_switch_targets_require_a_reason_and_commit` (56-61, 68-69) go; the `_ancestors`,
    `_cmdline` and `idle_context` cases (142, 151, 159) STAY under FR-009.
  - **EDIT**: `tests/test_switches.py` - scope-refusal and relaxation cases (105-109, 134, 228-236)
    go; `test_idle_context_needs_the_marker` (211-225) STAYS.
  - **EDIT**: `tests/tooling/pipeline/test_regen.py:123-143`, `tests/tools/test_mapcheck.py:53, 98-99`,
    `tests/tools/test_perf_snapshot.py:195-215`, `tests/tools/test_cohort_audit.py:42-80`,
    `tests/tools/test_cache_audit.py:79, 125-130`. **Several of these patch `locked_out` to `False`
    merely to get PAST it** - with the function gone the patch is what must go, not the test.
  - The 100% floor is a check on the DELETIONS, not on these edits: a test deleted with its subject
    leaves coverage unchanged, one deleted while its subject lives fails the floor by name.
- **FR-011** Every LIVE surface describing the mechanism MUST stop doing so. The first draft named
  three; there are at least nine: `dev/switches.md`, the skill `CLAUDE.md` rows, the root
  `CLAUDE.md` rows, `dev/loop.md:189-190`, `dev/reviews.md:46`, `tests/CLAUDE.md:35`
  (`ROLL_DESELECT`/`TIER_SELECT`), `tests/soak/CLAUDE.md:93-96`, `docs/efficiency-tooling.md:91`, and
  **`scripts/guard-file-hooks.sh:103`**, which names `scope-lock`/`scope-unlock` as the supported
  write path for `switches.json` in LIVE GUARD TEXT. Also the Makefile's own `GUARD_EDIT_OK` prose
  (946, 988, 1152) and the `switches.py` module docstring, which says "the FOUR MAKE TARGETS" and
  carries the one-map-per-invocation paragraph.
- **FR-011a** The rule feature 184's FR-005d established applies: **a LIVE instruction must not name
  a mechanism that no longer exists; a HISTORICAL RECORD is left exactly as written.** Records, not
  to be touched: `specs/`, `docs/review-ledger.md`, `docs/iteration-loop.md`, `pool/*/*.notes.md`,
  `timings.md`, `dev/run-log/`, `dev/idle-log/`.

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
- **D2 - THE ITEM THAT WOULD HAVE SHIPPED A REGRESSION, recorded because the reasoning was
  plausible and wrong.** The first draft required removing `switches.idle_context` entirely, arguing
  that with no lock to relax it "grants a privilege over nothing" and that a dead security boundary
  invites code to assume it still means something. That argument is sound in general and false here:
  the seam has a SECOND consumer with nothing to do with the lock. `DONE_NAME` selects `idle-done`
  over `done`, and `ci/state.py`'s `GREEN_TARGETS` deliberately omits `idle-done` - which is the
  whole mechanism by which an unattended gate neither grants nor revokes a push. Removing the seam
  would have made a detached timer write a record the push honors.
  **And nothing would have caught it.** The code still runs; only the recorded NAME changes, so the
  100% floor sees full coverage and every test passes. It was found by an independent review reading
  the consumers, which is the only thing that could have found it. The general lesson, worth more
  than the specific fix: *"this exists only to serve X"* is a claim about CONSUMERS, and it is
  checkable - so check it, rather than reasoning from what the thing is called.
- **D3 - the tests are DELETED where their subject dies, and EDITED where it does not.** The first
  draft said only "deleted", which does not cover the several suites that patch `locked_out` to
  `False` merely to get past it - there the PATCH is what goes, not the test. The 100% floor is the
  check on the deletions: remove a test whose subject is gone and coverage is unchanged; remove one
  whose subject lives and the floor names the uncovered lines. The floor is the check, not the
  author's judgment - but it says nothing about the edits, which is why FR-010 enumerates them.
- **D4 - a note for the GM, from the review.** `ci/state.py` stores a field named `scope` holding the
  SWITCH state (`unlocked|reference`), while `ci/runlog.py` and `ci/decision.py` store a field named
  `scope` holding the CI RUN scope (`reference|full`). They are unrelated, and the shared word
  `reference` is what made this blast radius hard to measure. Retiring the switch axis makes the
  collision disappear on its own - no separate work is owed.
