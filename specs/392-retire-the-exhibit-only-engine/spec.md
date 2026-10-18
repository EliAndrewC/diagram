# Feature Specification: Retire the exhibit-only engine - delete what only frozen maps call

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=392-retire-the-exhibit-only-engine`)

**Created**: 2026-10-18

**Status**: Draft

**Approved**: the GM, 2026-10-18, "Yes please file that feature and then execute it."

**Affects**: hamlet

**Input**: `request.md` - the GM's ruling on 388 (frozen maps need not stay runnable), the session's proposal, and the GM's
approval, verbatim.

## Why

Feature 388 amendment 1 established, by the GM's ruling, that the frozen legacy maps need not stay runnable ("especially if
it streamlines our code base and reduces our support surface"). After it, 71 engine functions, classes and constants are
called by nothing but frozen exhibits (measured 2026-10-18 by the name-level census of `scripts/measure/dead_closure.py`
over `l7r/` and `pool/` against the same plus `legacy-hand-authored-pool/`): most of the town and city drawing code and the
hill-rice field builders. The GM asked for them to be filed and deleted.

## What "it" is, read literally

1. **The 71**: every engine name that only frozen exhibits reference (no live pool map, no scripted generator, no Mode A
   sheet, no other engine module, no tool or script).
2. **What only they reached**: the closure of (1) - each round deletes what the last left with no live reference - to a
   fixpoint. Measured 2026-10-18 in a scratch worktree (`closure.py` and `closure-rounds.txt` beside this spec): five rounds
   after the 71 (52, 22, 16, 4, 1), **166 names**, about 7,500 lines over 38 files. Twelve mixin modules come out empty and
   go whole, with their place in their package's composition: `trades.py`, `structures/compounds.py`, `structures/packing.py`,
   `structures/urban_fixtures.py`, `civic_grounds/funerary.py`, `civic_grounds/justice.py`, `civic_grounds/lodging.py`,
   `civic_grounds/stable_yard.py`, `land/nearring.py`, `city/civic.py`, `city/crop.py`, `city/waterfront.py`.
   The census is name-level: a name also defined elsewhere, a name reached only through a string (`getattr`, a dispatch
   table), or a local of the same spelling is checked by hand in the plan; the gate (every module imported, 100% coverage,
   every test) is the check that nothing live was cut.
3. **Pre-existing dead code is not in scope**: a name that nothing referenced before - no exhibit either - is left for its
   own feature (the request names exhibit-only code).

## Requirements

- **FR-001**: Every name in "What it is" (1) and (2) is deleted from the engine, and a module left with no member goes whole,
  with its mixin from its composition. A name the plan or the gate finds still reached by live code is kept, and the plan
  says who reaches it.
- **FR-002**: A test goes with the code it tests: a test whose SUBJECT is deleted code is deleted; a test that mixes a
  deleted subject with a live one keeps the live part; a test file or test directory left empty is removed (the
  `tests/tier_town/` and `tests/tier_city/` trees and the Makefile's references to them included, if nothing is left in
  them). A test of live code that reached it through a deleted helper calls the live code instead.
- **FR-003**: Prose that names deleted code as live is updated where it stands - the package `CLAUDE.md` indexes, module and
  function docstrings, `docs/` and `dev/` - and the research claims of deleted code leave the claims index (its own
  targets). Specs are history and keep their words.
- **FR-004**: The tier placeholders (380 village, 381 town, 382 provincial city) each gain one line naming the commit
  before this deletion, where the deleted drawing code for that tier can be read from git - a pointer, not an owed item.
- **FR-005**: The frozen legacy maps are not edited: their manifests, renders and pages are untouched; their scripts
  simply no longer run (388 amendment 1, the GM).
- **FR-006**: No live map changes: the deletion removes only code no live map runs.

## Success Criteria

- **SC-001** (FR-001, FR-002): `make done` is green - every module imported, the full-coverage floor, ruff, pyrefly and
  every test - with the deleted code gone.
- **SC-002** (FR-001): `make dead-closure BASE=<the commit before>` names nothing NEWLY DEAD and no PINNED test, and its STILL
  CALLED lines name only frozen exhibits (or a recorded false alarm).
- **SC-003** (FR-006): `make maps` regenerates the live pool unchanged, and the landing cohort (`make cohort-landing`)
  regresses no seed against main.
- **SC-004** (FR-003, FR-004): no package index or docstring names a deleted module or member as live; 380, 381 and 382
  carry the pointer line.

## Decisions Recorded

- **D1 - the closure is the scope**: the 71 and what only they reached, iterated (FR-001). Who chose: the GM ("execute
  it"), on the session's proposal, which named the 71 and the cost.
- **D2 - the tiers' cost accepted**: the scripted town and city tiers (381, 382) rebuild what they need or recover it from
  git at the pointer commit (FR-004). Who chose: the GM, told the cost in the proposal.
- **D3 - no research changes**: no rendering decision changes and no live map draws anything new; the research pages the
  deleted docstrings cited keep their words.

## Assumptions

- "Called only by frozen maps" is the name-level census; a string-dispatched member it misses is found by the gate and kept.
- The Mode A sheets (`pool/magistracies/`, `pool/country-shrines/`) are live: anything they reach stays.
