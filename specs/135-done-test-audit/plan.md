# Implementation Plan: The `make done` Tests Are Audited and Accepted by the GM

**Branch**: none (`SPECIFY_FEATURE=135-done-test-audit`) | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md) (spec-fidelity FAITHFUL, round 2) and the GM's words in [gm-request.md](gm-request.md).

## Summary

The four-to-five minute unlocked gate is the 31 `rolls_map` tests (~233 s) plus a 26 s uncached
reference roll; the locked gate already runs in ~35 s ([research.md](research.md) R1). So the
plan is, in order of payoff: (1) fix the mis-homed tests the audit found - a stale deselect that
runs the FULL-only cohort ratchet at every unlocked gate, seven stubbed CLI tests marked as
map-rollers, coverage carriers running where no floor is enforced, the pool sweep's file
smothering three cheap tests; (2) give the suite its third tree, `tests/full/`, so quick / done /
full are DIRECTORIES and the Makefile's deselect lists go away; (3) stop re-rolling a map nothing
changed - a rolled-subject cache keyed exactly the way the pool's `gencache` is (module hashes +
the source of every function the roll executed + every file it read), serving the finished
manifest and plan, with any doubt regenerating and `EXHAUSTIVE`/`GATE_NO_CACHE` bypassing it;
(4) the reference step goes through the same cache; (5) one representative seed at merge time
where a sweep ran before, the sweep under `EXHAUSTIVE=1`; (6) the ledger, the docs, the
constitution amendment, and the GM's acceptance as the last task.

## Technical Context

**Language/Version**: Python 3.14 (pinned) | **Primary Dependencies**: pytest, pytest-xdist,
pytest-cov, coverage; `sys.monitoring` for the dependency capture (already in `gencache`) |
**Storage**: `.gencache/rolls/<key>/` beside the pool cache (gitignored) | **Testing**: pytest
through `make quick` / `make done` / `make done FULL=1` | **Target Platform**: the dev container
and CodeBuild | **Project Type**: tooling + test suite of the diagram skill | **Performance
Goals**: SC-001 - the unlocked gate's phase sum at <= 25% of baseline; SC-004 - locked gate no
slower | **Constraints**: the scope lock and remote-off stay as set (tracked file, no override);
nothing rewrites history; the feature cannot land until T99 | **Scale/Scope**: 3,755 collected
tests, 31 map-rollers, 13 guard suites.

**Single-artifact target**: not a generator change - no map's drawing is touched. The reference
hamlet (Inashiro seed 4, ~26 s) is the artifact the cached reference step is proven on: a hit
must serve the byte-identical manifest a cold roll produces (asserted by a test, and re-proven
by `GATE_NO_CACHE=1 make reference` after the change).

**Every step is two steps**: N/A for drawing (nothing draws differently); for the cache it is
"the toy roll in a tmp engine" (unit) then "the real Inashiro roll" (the reference step).

## Performance bookends

N/A - `make perf` is refused under the scope lock the GM set, and no generator stage changes:
the diff is the pipeline package (`rollcache.py`), the Makefile, `tests/`, docs and the
constitution. The reference step's own wall clock before/after IS recorded (research R1 / R8),
which is the number this feature is about.

## Constitution Check

- **I / II**: N/A - no UI in this repository.
- **III, IV, V, VII, VIII, IX**: N/A - no pool content, no SOURCE blocks, no in-world prose.
- **VI**: every task names its verification: `make quick` while iterating, whole test files
  before the gate, ONE `make done` (locked, ~35 s) at the end of each batch, and the
  measurement tasks (T02, T41) that are the feature's own evidence. Delegated reviews:
  `spec-fidelity` (done, FAITHFUL). PASS.
- **X**: `ruff` + `ruff format` + `mypy --strict` + 100% coverage on `rollcache.py` (added to
  `[tool.coverage.run] source`); red-green for the cache (a hit must be shown to SERVE and a
  changed function shown to MISS before the tests use it); no file grows past ~1,000 lines (the
  largest touched, `Makefile`, stays under its current size - deselect lists are removed, not
  added). PASS.
- **XII**: N/A for grounding - the feature asserts nothing about the world. "Decisions Recorded"
  was deleted from the spec for that reason. The record-the-why rule still binds: every verdict
  in the ledger carries its reason (research R7), and the constitution amendment quotes the GM.
- **XIII**: the baseline is research R1-R5, taken on unmodified code at `6486be5c` before the
  first edit (the lock is a tracked file, so a worktree is no different from the clone; the
  measurement ran in the clone before any change). Zero new failures: every test that passed at
  the baseline passes after, in whichever tree it now lives; a cached hit is a verdict on the
  same bytes a cold roll produces, and the cache is bypassed under `EXHAUSTIVE`. The three
  tripwire regressions waived as expected failures under 133 T91 stay waived. PASS.
- **XIV**: every defect the audit surfaced (research R6) is a task here. PASS.

## Project Structure

```text
specs/135-done-test-audit/
├── spec.md, gm-request.md, plan.md (this), research.md (the baseline + the ledger), tasks.md
.claude/skills/diagram/
├── l7r/diagram/pipeline/rollcache.py      # NEW - the rolled-subject cache (record / key / store / load)
├── tests/                                 # the QUICK tree (unchanged rule: tests/ IS the quick suite)
├── tests/gate/                            # the DONE tree (map-rollers that earn merge time, the corpus)
├── tests/full/                            # NEW - the FULL tree (pool sweep, cohort ratchet, coverage carriers, seed sweeps)
├── tests/tooling/, tests/tier_town/, tests/tier_city/   # done trees with a documented conditional-quick rule (unchanged)
├── Makefile                               # QUICK_TREE / GATE_TREE / test-full: trees, not deselect lists
└── tests/CLAUDE.md, dev/loop.md, docs/iteration-loop.md, .specify/memory/constitution.md
```

## Design decisions (the alternatives, so they are not reopened)

1. **Three trees are `tests/` (quick), `tests/gate/` (done) and `tests/full/`** - not a rename of
   `gate` to `done`. "Gate" is the project's word for `make done` in every doc and the Makefile;
   renaming costs a hundred references for no new information. `tooling/` and `tier_*` stay
   separate done-trees because their quick-inclusion is CONDITIONAL (tooling changed; the lock's
   tier), which a plain tree cannot express; the index states all five.
2. **The cache is keyed like `gencache`, not on a coarse engine hash.** A coarse key would miss on
   every engine edit - and `make done` only runs at all after an engine edit (the short-circuit
   answers otherwise), so a coarse cache would buy nothing. The fine key misses only when a
   function the roll EXECUTED changed, which is exactly when the roll must happen.
3. **Monkeypatched rolls are never cached.** A patched `front_row` or a faked gate changes what
   the roll does without changing any hashed source; the key cannot see it, so those tests roll
   for real every time (research R4 says which). Their cost is bounded by the smallest legal
   hamlet (10 households).
4. **Determinism tests must roll twice for real** - a served second roll would make "same seed,
   same bytes" vacuous - so they belong to the full tree, and the gate keeps one cached
   representative roll of each engine path instead.
5. **`EXHAUSTIVE=1` and `GATE_NO_CACHE=1` bypass the cache.** The full run is where the coverage
   floors are enforced, and a hit executes none of the rolled code; bypassing there keeps the
   floors honest without storing coverage per entry (the pool cache stores it because the pool
   sweep IS the floor's main carrier; these rolls are not).
6. **Tooling tests skip at the gate when the tooling is unchanged** - the same rule `hooks-test`
   already applies at the gate with its stamp - but never under the coverage floors (`FULL`),
   where the ci package owes its 100%.
7. **Declined: warm workers / a persistent runner** - the GM declined it on 2026-08-26; the
   collection floor is 1.3 s (R2) and not this feature's problem.
