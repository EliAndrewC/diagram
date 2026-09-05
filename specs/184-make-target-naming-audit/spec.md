# Feature 184 - the make-target naming audit

**Status**: FAITHFUL pending - written AFTER the implementation, deliberately. The work reached two
executable lines in `l7r/`, which triggers this repository's rule that engine code always carries a
spec-kit feature; the spec was then written to cover what had landed. A later reader should not infer
the usual order from it. Renumbered twice (181, 182 both claimed by peer sessions mid-flight).
**Request**: [`request.md`](request.md) - the GM's words verbatim

## Summary

An audit of every make target and argument for whether the NAME still describes the BEHAVIOR, after
a run of refactorings (166 deleted the check battery, 174 made the coverage floors unconditional, and
this session repointed the remote at a new suite). Five findings; four are corrections to statements
that had become FALSE, and the fifth removes a redundant target.

**Most of this feature is documentation and one target's removal. It reaches `l7r/` in TWO executable
lines**, and the second is a behavior change rather than a name:
- `_invocation.py:203` - the operation registry entry, which must name a real make target;
- `ci/dispatch.py:262` - `make_target()`, which now returns `soak` instead of `done` (FR-010).

An earlier draft of this spec said "exactly one line". That was false, and the review caught it.

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

- **FR-001** The soak suite MUST NOT be called `sweep`, and the rename MUST BE COMPLETE. An earlier
  draft asserted it already covered everything; the review found THREE live strings still saying
  `sweep`, each false as written, and each is now required by name:
  - `Makefile:1130-1131` - claimed `make_target()` returns `sweep` and pointed at `tests/sweep/`;
  - `tests/soak/CLAUDE.md` - the same false sentence, inside the doc that explains the rename;
  - `Makefile:1140` - "a sweep test covers nothing the gate does not already cover", the suite sense
    three lines above the comment explaining why the suite is NOT called `sweep`;
  - `dev/switches.json` `remote.why` - **not a frozen record**: `switches.py` PRINTS it, so
    `make switches` was telling every session to run a target that does not resolve. Corrected by
    re-throwing the switch, which is the only way to change it. This repository uses SWEEP for a run that
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
    a make target verbatim (`run.sh` runs `make $MAKE_TARGET`). This is ONE of the two executable lines in `l7r/` this feature touches; the other is `ci/dispatch.py:262`, per FR-010.
  - **FR-005d** `.claude/skills/diagram/CLAUDE.md`'s scope-lock row MUST drop `tripwire` (and
    `regressions`, retired by feature 166). It is a LIVE instruction naming targets that no longer
    resolve - distinct from FR-006's records, which describe builds that really ran.
  - **FR-005c** `TRIPWIRE_SEEDS` KEEPS its name. The seeds (27, 33, 37, 41, 47) are a real rung
    inside `mapcheck`'s auto state machine and the engine's comments reference them by that name;
    what was wrong was a TARGET claiming to select a scope that does not exist.
- **FR-010** The remote target repoint MUST be recorded as a REQUIREMENT, not as background prose.
  `ci/dispatch.py:262` returns `soak` where it returned `done`, so a paid remote build now runs the
  tier the laptop skips rather than repeating the tier it just finished. `make soak` REFUSES on an
  empty suite, so this cannot become a vacuously green build. What is given up - the remote as a
  merge queue - is recorded in `ci/CLAUDE.md` at the point of change.
- **FR-011** **A DEFECT FOUND DURING THE AUDIT, fixed in it under constitution Principle XIV.**
  `scripts/check-stale-dirs.py` (with `--selftest`), `tests/tooling/test_stale_dirs.py`, and both
  wiring points (`Makefile` `lint`, `sync-with-main.sh` at push). A directory left holding only
  `__pycache__` is an importable PEP 420 namespace package, so a long-lived clone passes what a fresh
  clone fails - silently, in the direction that hides the bug. FOUR were live, all from feature 166's
  deletion; `l7r/diagram/check_village` was importable, verified with `importlib`. It REFUSES and
  never deletes. **The GM's naming request did not ask for this**; it is disclosed as such.
- **FR-012** `tests/test_switches.py`'s `LOCKED_TARGETS` MUST be correct. Retiring `tripwire` from it
  left `"maps SCOPE=all"` in the list TWICE, because the vacated slot was filled with a value already
  at the end. A duplicated entry in a roster of refusals silently tests one target twice and another
  never.
- **FR-006** Records MUST NOT be rewritten. `TARGET=tripwire` appears in `dispatch.py` and
  `test_cache.py` as an account of builds that really ran on 2026-08-31, and in `specs/`. Those stay.

## What this feature does NOT do

- **FR-007** It does not rename `SWEEP_OK` or reword `switches.py`, and it does not retire the scope
  lock. **THE GM HAS SINCE AUTHORIZED BOTH** (2026-09-05: *"please go ahead and retire the concept of
  the scope lock and the scope unlock, i.e. retiring both the concept and the specific make targets"*),
  which subsumes the word *sweep* - `SWEEP_OK` is the scope-lock check, so retiring the lock retires
  the term. It is NOT done here because it is a different change to different code, and folding it in
  would invalidate the review this spec is under. **OWED AS THE NEXT FEATURE** - see the debt below.
- **FR-008** It does not merge `lint` and `format`. They differ - `lint` is ruff plus three custom
  guards, `format` is whitespace - and the gate reports them as separate phases, so merging would
  lose which one failed. The misleading part is the NAME: `lint` is really "the static checks".
  **THE GM HAS SINCE AUTHORIZED THE RENAME** (2026-09-05: *"I also agree that it should be renamed to
  make static, so please do that"*). Not done here for the same reason as FR-007. **OWED AS THE NEXT
  FEATURE** - see the debt below.

### THE DEBT THIS FEATURE LEAVES, so it cannot be lost to a context roll

Two changes the GM authorized while this spec was under review. Both touch engine code or a guard, so
both need their own feature; neither is optional and neither is a maybe:

1. **`lint` -> `static`.** The target, its `.PHONY` entry, the gate's phase list, every doc that
   names it, and the guard suites that assert the phase names.
2. **Retire the scope lock ENTIRELY** - `make scope-lock` / `make scope-unlock`, the `SWEEP_OK`
   check at its 7 sites, the scope half of `switches.py` (the remote half STAYS), `dev/switches.md`,
   `tests/test_switches.py` and `tests/tools/test_scope_lock.py`, and the CLAUDE.md rows. This is
   also what retires the word *sweep*, closing the terminology question for good.

A session picking this up should confirm with the GM before doing anything a reader of this list
would find surprising, but the two items themselves are settled.
- **FR-009** It does not touch `make maps`'s own behavior, `idle-tests`, the scope lock, or any
  diagnostic. Those were QUESTIONED by the GM in the same conversation and are recorded in Decisions
  as the session's findings with a recommendation - **not as rulings**. D3 and D4 stay OPEN until the
  GM decides; the GM asked about them and did not answer.

## Decisions Recorded

- **D0 - `FULL=1` and `test-full` KEEP their names, and this is the GM's OWN example.** Their
  request named it directly: *"having something like `FULL=1` or `make full` which are actually not
  running all of the tests is just confusing."* The review was right that the spec answered it by
  fixing the DESCRIPTIONS and never recorded the decision about the NAMES, leaving the request's
  centerpiece invisible. Recorded now:
  - **What `FULL` means today**: the perf bookends, a bypass audit and a scope check. NOT more tests
    - since feature 174 the test phase is `test-full` on both branches.
  - **`test-full` still does not run everything**: `tests/soak/` is deselected, by design.
  - **Why no rename** (`PERF=1`, `test-most`): `FULL` appears at 19 sites in the Makefile plus the
    switches, the door, the buildspecs and the run-log's recorded scope values, where `full` is a
    STORED string in past records - a rename reaches data, not just code. The corrected descriptions
    remove the falsehood at a fraction of the blast radius. **This is a judgment the session made,
    and it is the one most worth the GM overruling** if they would rather have the honest name.
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
- **D3 - `idle-tests`: the SESSION's finding, OPEN for the GM.** Recommendation: keep. 17 runs, all rc=0, none ever found a failure, and 15 of 17 finished
  in 0-5 s because they short-circuited. Its original purpose (the reference-hamlet lock, when
  expensive tests were deferred out of the gate) is gone. It stays because it costs ~2 s, runs
  detached, blocks nothing and needs no infrastructure - unlike the remote, which had real cost. The
  live case is a session that edits engine code, never gates it and goes idle.
- **D4 - `make reference`: the SESSION's finding, OPEN for the GM.** Recommendation: keep, and note it is not a convenience target. It is a PHASE: step 3 of the
  remote dispatch sequence, a phase of `make done`, and `REF_FIRST` before every map target. Its
  original justification (a 15-minute suite) is gone; what it does now is fail BEFORE anything
  expensive is paid for. **No timing is quoted, deliberately.** An earlier draft said "0.55 s" and
  no source could be found: `dev/run-log/` holds zero `target: reference` rows, and the tree's own
  two figures - `~26 s` (`ci/dispatch.py`) and `~60 s` (the Makefile's reference block) - describe
  different things. A number nobody measured is what this project forbids writing down.
