# Implementation Plan: Retire the exhibit-only engine

**Branch**: none (main, in the clone) | **Date**: 2026-10-18 | **Spec**: `spec.md`

## Summary

Delete the 166 engine names that only frozen exhibits reach (the 71 and their closure, `closure-rounds.txt`), the twelve
modules that empty, and their tests; repoint the prose; add the tier placeholders' pointer line. No live map changes.

## Technical Context

Python, the engine under `l7r/diagram/`; pytest under `make`. **Single-artifact target**: none - the deletion changes no live
map; FR-006 is proven across the whole live pool (`make maps`, nothing regenerated) and the landing cohort.

## Performance bookends

`392-start` on unmodified code, `392-end` before the push. Removing code no live map runs should move nothing; a flag over
the band is mentioned with its load.

## Constitution Check

- I, II: N/A - no UI. III, IV, V, VII, VIII, IX: N/A - no pool content, SOURCE block or in-world prose.
- VI: PASS - each task names its verification; `make maps` and the landing cohort stand in for reference-then-pool, since
  nothing is meant to move.
- X: PASS - ruff, pyrefly, the full-coverage floor; no new behavior; no function grows; nothing indexed is added.
- XII: PASS - no rendering decision changes (spec D3); the deleted code's claims leave the index.
- XIII: PASS - the landing cohort refuses a regressed seed. XVI: PASS - the literal reading is the spec's "What it is".

## T01 - the deletion (FR-001)

Apply the closure measured in the scratch worktree (`closure.py`: each round cuts every engine name with no live reference
that had one, or an exhibit's, before; to a fixpoint) to the clone, then:

| case | handling |
|---|---|
| a mixin class left with no member (the twelve modules in spec "What it is" (2)) | delete the module; drop its import and base from its package's composition (`settlement/__init__`-level `core.py`, `civic_grounds/__init__.py`, `structures/__init__.py`, `city/__init__.py`, `land/__init__.py`) |
| a module-level helper or constant a cut left unreferenced | cut by the next round (the fixpoint) |
| an import left unused by a cut | removed (ruff's F401) |
| a name reached through a string (a `getattr`, a dispatch or caption table, a surface roster) | found by the gate or a grep of the string; KEPT if live code reaches it, the row recorded here |
| a name also defined elsewhere | checked by hand; the census counts them as one |
| a re-export of a deleted name in a package `__init__` | removed |

Then `make dead-closure BASE=<the commit before>`: nothing NEWLY DEAD, no PINNED, STILL CALLED only frozen exhibits (or a
recorded false alarm such as a local of the same spelling).

Verify: `python -m compileall` clean through `make quick`; `make dead-closure`; `make done` green.

## T02 - the tests (FR-002)

Every test whose subject is a deleted name goes (the rule of 388): the town and city tests (`tests/tier_town/`,
`tests/tier_city/`) whose subjects are gone, the surface rosters' entries for deleted members (`test_civic_grounds.py`,
`test_city.py`, `test_shrines_wells.py`, `test_geom.py` and the like), the hill builders' tests (`tests/waterfields/test_hill.py`),
the caption-path entries (`tests/labels/test_caption_paths.py`). A test that mixes a deleted subject with a live one keeps the
live part; a test of live code that reached it through a deleted helper calls the live code. A directory left with no test
goes, with the Makefile's references to it (`QUICK_TREE`, the gate's trees). The coverage floor then names any line only the
deleted tests reached: deleted if nothing live reaches it, else a test is owed.

Verify: `make quick`; `make test-file` on each touched test file; `make done` green.

## T03 - the prose and the placeholders (FR-003, FR-004)

Repoint every docstring, comment and index naming deleted code as live: the package `CLAUDE.md` indexes (their rows for the
deleted modules and members), `l7r/diagram/CLAUDE.md`'s table (`citybudget.py` if it empties), `docs/` and `dev/` pointers
(`docs/migration-plan.md`'s "engine builder exists" rows for the hill archetypes and the town/city tiers). The claims index is
updated by its targets (`make claims-owed`; impl-drift on what moved). 380, 381 and 382 each gain one line: the commit
before this deletion, where that tier's deleted drawing code can be read (a pointer, not an owed item).

Verify: a grep of every deleted module name over `l7r/ docs/ dev/*.md` finds no live pointer; claims none owed.

## T04 - measure and land (FR-006, SC-001 - SC-004)

`make maps` (the pool unchanged), `make done`, `make cohort-landing`, the end bookend, the feature report with a section for
the GM, the gated push.

Verify: each command's log tail read before the tick.

## Project Structure

Touched: `l7r/diagram/settlement/**`, `l7r/diagram/waterfields/hill.py`, `l7r/diagram/citybudget.py`, `tests/**` (deletions),
`docs/`, `dev/`, `specs/380-*/spec.md`, `specs/381-*/spec.md`, `specs/382-*/spec.md`, the claims index.

## Complexity Tracking

None.
