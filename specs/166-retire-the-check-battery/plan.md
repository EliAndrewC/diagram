# Implementation Plan: Retire the post-placement check battery

**Feature**: 166-retire-the-check-battery | **Spec**: [`spec.md`](spec.md) | **Created**: 2026-08-30

## Summary

Delete `check_village/` entirely and land each of its 147 rules where it belongs: a unit test of the placer
that owns it, a seed-sweep test, a static code test, or a recorded drop. Cut the generator's dependency on
the gate first, because that is the only part that can move a map. Sweep the docs for Mode B battery
doctrine while leaving Mode A's intact.

## Technical Context

**Language/Version**: Python 3.14. **Testing**: pytest; `make quick` while iterating, `make done` at each
phase boundary. **Project Type**: a deletion and migration across an existing package.

**Single-artifact target** (constitution VI): `pool/hamlets/inashiro/inashiro.gen.py`, the reference
hamlet - it is what US1's byte comparison turns on. Then the tier via `make maps`. Both are tasks.

**The size, stated honestly**: `check_village/` is 52 files and 14,575 lines; its tests are 7,464; the
frozen corpus is 105 fixtures. 147 checks need destinations. This does not land in one sitting, and the
ordering below is what keeps the tree green throughout.

## Performance bookends (constitution VI)

| | label | total | median | worst | notes |
|---|---|---|---|---|---|
| before | `166-start` | | | | UNMODIFIED code, before the first edit |
| after | `166-end` | | | | before the push |

This feature REMOVES the battery from every roll (`hamletgen.generate` runs it in-process), so a decrease
is expected and needs no `perf-audit` under feature 129. Any seed that gets SLOWER is diagnosed in writing
with the number.

## Constitution Check

| principle | status |
|---|---|
| **I, II** | N/A - no UI in this repository |
| **III, IV, VII, VIII, IX** | N/A - generates no pool content, writes no in-world prose |
| **V** | PASS - no SOURCE block is touched |
| **VI (verify before done)** | PASS - `make done` at each phase boundary; `make maps` at the reference then the tier; US1's byte comparison is the map-level proof. A `settlement-review` IS owed if US1 moves a map, and that is the one place this feature can |
| **X (Python discipline)** | PASS - ruff, pyrefly, pytest, and the floors RE-DERIVED per FR-007. The migration ADDS tests and removes ~22,000 lines |
| **XII (historical grounding)** | The closing obligation is the live one and it is FR-005: a check body may be the sole operative statement of a finding, and the urban rules bind hardest because they have no placer to migrate into. Per rule, recorded, never per class |
| **XIII (no known regressions)** | PASS - baseline in a detached worktree at T01. The migration is designed so the battery still runs while replacements are written, so a regression is visible before the safety net goes |
| **XIV (fix defects where found)** | ACKNOWLEDGED - reading 147 checks against their placers will surface placer defects. A check that fires today for a real reason is a placer BUG, and fixing it is the feature, not a distraction |
| **XVI (no unrequested exception)** | `spec.md` FAITHFUL at round 3; the Mode A carve-out reviewed as a delta |
| **XVIII (a guard needs a companion test)** | this feature RETIRES guards; each retirement's replacement is proven to fire, which is the same property in the other direction |

## Phase 0 - baseline

Detached worktree (`git worktree add --detach /tmp/base166 HEAD`), `make done`, record. `make perf
LABEL=166-start`. Both on unmodified code, before the first edit.

## Phase 1 - cut the generator's dependency (US1, FR-001/FR-002)

The only engine consumer of `gate()` is `hamletgen/driver.py`'s re-roll ladder, and it depends on the
battery twice: it PARSES the printed verdict for `farmhouses_reach_a_way` failures to learn which seats
stranded a farmhouse, and its accept criterion is `len(f2) <= len(failures)` - the whole failure list got
no longer.

- The seat extraction becomes a predicate `hamletgen` owns. `driver.py` records why it reads the gate
  today: a hand-rolled reach measure *"was wrong on five of six seeds... it over-counted and never read
  zero"*. So the predicate is not re-derived - it is the check's own body, lifted.
- The accept criterion is the harder half and it is a REAL behavior change: a global quality proxy is being
  exchanged for a local one. What replaces it is stated in the code with its reasoning.
- Then re-roll all five live hamlets and compare byte-for-byte. Any difference is diagnosed before Phase 2.

## Phase 2 - classify all 147 to destinations (US2, FR-003)

One row per check: owning placer (feature 163's ledger already measured the last-touching stage for all
147), destination, and - for a drop - the covering test or the reason. Nothing is deleted in this phase.

## Phase 3 - migrate, in batches BY OWNING PLACER (US2, FR-004)

The ledger's stages are the batches: `water_frame`, `field`, `sink`, `seat`, `homesteads`, `track`,
`appurtenances`, `web`, `notice`, `hinterland`, `woodland`, `windbreak`, `bamboo`, `crossings`, `frame`,
`finish`. Per batch: write the replacement test, PROVE IT FIRES against the unfixed placer, then delete the
check. **The battery keeps running throughout**, so a botched migration is visible immediately - that is
the whole reason for this ordering.

The 17 completeness ratchets (which read no manifest key) become static tests over the code. The whole-map
properties become one seed-sweep test.

## Phase 4 - delete the apparatus (US3, FR-006)

`check_village/`, `tests/check_village/`, `tests/gate/`, the 105 fixtures, the Makefile targets, the
`_invocation` row, the pool sweep. Then: nothing in the tree references it.

## Phase 5 - the record and the docs (FR-005, FR-010, FR-011)

Per-rule confirmation that each research finding has a documented home (the urban rules bind hardest -
they have no placer). `dev/gate.md` rewritten to carry the successor doctrine in the GM's words. The doc
sweep, per MENTION: Mode B battery doctrine goes, **Mode A's stays** - `pack_audit`, `scatter_audit` and
the 8 frozen red SVG fixtures are untouched and still documented.

## Phase 6 - verify

Coverage floors RE-DERIVED (not lowered - a drop is a sentence to the GM). `make done` green. `make maps`
reference then tier. Perf bookend. `settlement-review` if and only if a map moved.

## Complexity Tracking

No constitution gate is violated or deferred.
