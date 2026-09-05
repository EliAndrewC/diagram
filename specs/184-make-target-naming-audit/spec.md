# Feature 182 - the make-target naming audit

**Status**: draft, pre-implementation
**Request**: [`request.md`](request.md) - the GM's words verbatim

## Summary

An audit of every make target and argument for whether the NAME still describes the BEHAVIOR, after
a run of refactorings (166 deleted the check battery, 174 made the coverage floors unconditional, and
this session repointed the remote at a new suite). Five findings; four are corrections to statements
that had become FALSE, and the fifth removes a redundant target.

**Most of this feature is documentation and one target's removal. It reaches `l7r/` in exactly one
line** - the operation registry entry that must name a real make target - which is why it is a
spec-kit feature at all.

## Why the names drifted, stated once

None of these were wrong when written. Each became wrong when something else changed:

- feature 174 made `COV_FLOORS=1` unconditional, and that switch also sets `L7R_TESTS_FULL` and turns
  every deselection off - so `FULL=1` silently stopped adding tests, while its banner went on saying
  it did;
- deselecting `tests/soak/` this session made `test-full`'s "nothing deselected" false;
- repointing the remote at `make soak` made both `ci-*` help lines describe a route that no longer
  runs what they say;
- and `mapcheck`'s scope vocabulary (`auto|reference|all`) never contained `tripwire`, so that
  target's help described a tier it could not select.

## Functional requirements

- **FR-001** The soak suite MUST NOT be called `sweep`. This repository uses SWEEP for a run that
  rolls many MAPS - `SWEEP_OK` is the scope-lock check and `switches.py` describes a locked scope as
  one where *"every sweep refuses"*. `soak` is the standard term for the thing the suite is: the same
  code held under realistic load for an extended run. Rename covers the directory, the target, the
  doc, `norecursedirs`, the dispatcher's `make_target`, and every test that pins either name.
- **FR-002** The gate banner MUST NOT claim `FULL=1` runs tests a plain `make done` skips. It adds
  the perf bookends, a bypass audit and a scope check; the test phase is `test-full` on both branches.
- **FR-003** `test-full`'s help MUST NOT say "nothing deselected" while `tests/soak/` is deselected.
- **FR-004** `ci-check` and `ci-merge` help MUST describe what they now run (the soak suite), and
  `ci-merge` MUST NOT still be called a merge queue - that property was retired this session.
- **FR-005** `tripwire` MUST be removed as a target. It ran the same `mapcheck` with the same auto
  scope, so with no `SCOPE` set it was `maps` minus the pool-index refresh, and its help - *"the
  middle tier: reference map, then the tripwire seeds"* - could not be true, because `mapcheck`'s
  scopes are `auto|reference|all` and there is no `tripwire` among them.
  - **FR-005a** It MUST come off `.PHONY` as well as losing its rule. A phony name with no recipe
    still RESOLVES and exits 0, so leaving it there would keep a dead command silently succeeding.
  - **FR-005b** The operation registry entry MUST name `maps`, because an operation name is used as
    a make target verbatim (`run.sh` runs `make $MAKE_TARGET`). This is the ONE line in `l7r/`.
  - **FR-005c** `TRIPWIRE_SEEDS` KEEPS its name. The seeds (27, 33, 37, 41, 47) are a real rung
    inside `mapcheck`'s auto state machine and the engine's comments reference them by that name;
    what was wrong was a TARGET claiming to select a scope that does not exist.
- **FR-006** Records MUST NOT be rewritten. `TARGET=tripwire` appears in `dispatch.py` and
  `test_cache.py` as an account of builds that really ran on 2026-08-31, and in `specs/`. Those stay.

## What this feature does NOT do

- **FR-007** It does not rename `SWEEP_OK` or reword `switches.py`. Retiring the word *sweep*
  entirely was proposed and is NOT taken here: it is a separate ~8-site change to a guard the GM has
  not yet ruled on, and bundling it would put a scope-lock change inside a naming audit.
- **FR-008** It does not merge `lint` and `format`. They differ - `lint` is ruff plus three custom
  guards, `format` is whitespace - and the gate reports them as separate phases. The finding recorded
  instead: the misleading part is the NAME (`lint` is really "the static checks"), and renaming it is
  not attempted here.
- **FR-009** It does not touch `make maps`'s own behavior, `idle-tests`, the scope lock, or any
  diagnostic. Those were questioned in the same conversation and are answered in Decisions Recorded.

## Decisions Recorded

- **D1 - `soak`, not `sweep`, and not left alone.** The collision was caught the same day the name
  landed, by the audit that this feature is. Declined: keeping `sweep` and renaming `SWEEP_OK`
  instead, which would have churned a guard used at 7 sites to protect a name chosen hours earlier.
- **D2 - the diagnostics are KEPT, against the initial reading.** The GM asked whether `why_placed`,
  `overlap_audit` and the rest are holdovers from hand-drawn maps. The record says the opposite:
  feature 166 already retired the five tools that drove the check battery (`make_regressions`,
  `check_census`, `firing_census`, `site_justice`, `new_check`), and `tools/CLAUDE.md` states that to
  ask where a feature may go you now use `open_seat` and `why_placed`, *"which read the placer's own
  refusals rather than a second opinion about them"*. `overlap_audit` was built in feature 151 for
  GENERATED maps - the same point-in-polygon question hand-written twelve times across feature 150.
  The cull already happened; what remains survived it.
- **D3 - `idle-tests` is KEPT.** 17 runs, all rc=0, none ever found a failure, and 15 of 17 finished
  in 0-5 s because they short-circuited. Its original purpose (the reference-hamlet lock, when
  expensive tests were deferred out of the gate) is gone. It stays because it costs ~2 s, runs
  detached, blocks nothing and needs no infrastructure - unlike the remote, which had real cost. The
  live case is a session that edits engine code, never gates it and goes idle.
- **D4 - `make reference` is KEPT and is not a convenience target.** It is a PHASE: step 3 of the
  remote dispatch sequence, a phase of `make done`, and `REF_FIRST` before every map target. Its
  original justification (a 15-minute suite) is gone; what it does now is fail in 0.55 s before
  anything expensive is paid for.
