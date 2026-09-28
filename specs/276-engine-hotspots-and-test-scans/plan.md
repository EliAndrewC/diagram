# Implementation Plan: engine hotspots and test scans

**Branch**: none (main, clone `diagram-inashiro`) | **Date**: 2026-09-28 | **Spec**: [spec.md](spec.md) (FAITHFUL, round 3)
**Input**: [spec.md](spec.md), [research.md](research.md), [request.md](request.md)

## Summary

Five independent pieces, each proved on its own before the next: (A) the four AST-scanning tests share one parse;
(B) the record tests share one scan; (C) homestead placement pre-screens candidates by its cheapest exact rules
and answers every placed-house and static-ground scan from an index; (D) seam closing computes each result once,
batches per-piece work, and visits only the cells a pocket touches; (E) the track stage's path checks read an
index built once per stage. Every index PRUNES and the existing exact test DECIDES (`dev/performance.md`), so the
rules are unchanged; where a batched geometry call or a household-keyed yard roll (D4) moves a map, FR-006's house
counts and forms must hold.

## Technical Context

**Language/Version**: Python 3.14 (the engine), shapely 2 (already a dependency; its array functions are used).
**Primary Dependencies**: none new.
**Testing**: pytest through `make` (`make quick`, `make test-file`, `make done`); the harness `harness.py`.
**Project Type**: the `/diagram` engine and its tests.
**Performance Goals**: SC-001 to SC-006 (spec).
**Constraints**: every gate rule on every live map; the 100% coverage floor; files under 1,000 lines (all touched
files are 132-623 lines today).
**Scale/Scope**: the placement primitive at 240 seeds is the city proxy (SC-003).

**Single-artifact target**: `pool/hamlets/inashiro/inashiro.gen.py` (reference hamlet; regen ~8 s uncached), then
the pool sweep through `make done`.

**Every step is two steps**: each engine piece (C, D, E) is proved first on its unit tests and on Inashiro alone
(`make map`), then across the pool (`make done`, which rolls every live map) - separate tasks.

## Performance bookends (constitution VI)

| | label | total | median | worst | notes |
|---|---|---|---|---|---|
| before | `276-start` | 31.3 s | 7.7 s | 9.2 s | taken 2026-09-28 on unmodified code (m:perf-start-total, m:perf-start-median) |
| after | `276-end` | | | | taken before the push |

A decrease is the point; an increase on any seed is diagnosed under the bands like any other.

## Constitution Check

- **I, II, IV, V, VII, VIII, IX**: not applicable (no viewport, no GM writing, no pool data convention, no in-world
  text, no setting content).
- **III Pool data conventions**: pool maps regenerate through their generators; no convention changes.
- **VI Verify before done**: the harness before/after; `make done` green (every pool map, 100% coverage); the
  bookends; the cohort (XIII); FR-006's counts.
- **X Python discipline**: ruff, ruff format, pyrefly; red-green for each new index (a test that fails on the
  unindexed or wrong behavior first); 100% coverage of every new line; clause 15 - every new proximity test names
  its index (below); no file passes 1,000 lines.
- **XII Historical grounding**: nothing asserted about the world changes (research R8); Decisions Recorded in the
  spec lists the two map-drawing conventions.
- **XIII No known regressions**: baseline `make cohort N=24` in a detached worktree on unmodified code (research
  R7); zero new failing seeds at merge.
- **XIV Fix defects found**: any found in passing is fixed in this feature.
- **XVI Build what was asked**: all five pieces; no exception is planned.

## Design

### A. One parse of the engine (FR-001)

- **D1** `tests/_engine_ast.py`: `parsed(path) -> (source, tree)`, cached on `(path, mtime_ns, size)`, with a module
  counter `PARSES` and `walked(tree)` - one `ast.walk` per tree, cached, returning the node list and a node-type
  index. `engine_modules(root, needle=None)` lists `(path, source, tree)` for every `.py` under a root, skipping
  (without parsing) a file whose text lacks `needle` when one is given.
- **D2** The four tests take their modules from it. Each test's needle is a literal the property cannot exist
  without: `test_memory` - any of `shapely`/`numpy`/`PIL`; `test_driver` - `STAGES`; `test_water_ways` - `del `;
  `test_package_surfaces` - `l7r.diagram` (it reads `from l7r.diagram... import`). Each test's scan body is lifted to
  a module-level function over `(path, source, tree)` triples so a planted offender can be fed to it.
- **D3** `tests/test_engine_ast.py`: runs the four scans in one process and asserts `PARSES` equals the number of
  distinct files read (one parse each), and that each scan flags a planted offender (a synthetic module text).

### B. One scan of the record (FR-002)

- **D4** `tests/interactive/test_record.py`: `_ids(path)` cached on content (the link test's per-link re-scan goes);
  the two `.md`-token scans skip a file with no `.md` substring (a match requires it) before running the regex.
- **D5** `tests/interactive/test_record_format.py`: the corpus is joined once per process (cached), and each glossary
  variant is answered by a word-set lookup when it is a single token under `_bounded_in`'s own boundary rule, the
  existing `_bounded_in` search otherwise - the same verdict, proved on every variant by a test comparing the two
  paths over the real corpus.
- **D6** Planted-violation tests where none exists: a broken link id, an unused glossary term, a converted `.md`
  token (the retired-rule-file test already has one).

### C. Homestead placement (FR-003)

- **D7 The placed-house index**: `M["houses"]` and `placed` are `Indexed` lists (the `houses` record list is created
  as one in `core.py`, and the two rebinding sites in `rolling/farmsteads.py` rebind to `Indexed`), and every
  per-candidate scan asks an `indexed_grid` of them (clause 15: a `PointGrid` keyed on the record list's version,
  extended on append) for the records whose extents - house, yard, gardens, groves - fall within the rule's reach
  box: `_sun_corridor_ok` (both scans), `_gardens_sun_ok`, `_yard_sun_conflict`, `_house_too_near_a_neighbor`,
  `_bundle_side_fits` and `_envelope_blocked` (placed boxes, returned in list order so its "the ONE box" answer is the
  first box as today). The exact comparisons are unchanged; a unit test compares each indexed answer with the linear
  one over a synthetic settlement of placed houses.
- **D8 The static ground index**: `SiteCorridors` gains a vertex grid per ring and a hole grid, so `hit_points` asks
  only the vertices inside the query box and only the holes whose box contains the point; the exact tests decide.
  A unit test compares with the linear form on synthetic rings with holes.
- **D9 The pre-screen**: `_place_bundle` (dispersed spiral) and the nucleated seat loop test, per candidate and before
  building the bundle, the house rect's ground (`_rect_blocked(house)`) and the eave gap; after building it, the
  yard's and grove's ground and the placed-box overlap; only survivors reach `_bundle_fits` / `_envelope_blocked`.
  Exact because the conjunction is order-independent (research R2); a test asserts the seat chosen with and without
  the pre-screen is the same over the rescue scenario and the toy.
- **D10 Bundle template**: `_bundle_geom` builds the relative rects once per `(hw, hh, side, shed, nucleated, yard
  dims)` and translates; the yard's rolled size is keyed to the household's seed position (the attempt), not to each
  candidate position - a map-drawing convention change (spec Decisions Recorded: the yard size is the household's,
  drawn from the same distribution), which moves yards by a roll and is covered by FR-006.

### D. Seam closing (FR-004)

- **D11 Compute once**: `_plant`'s `k.buffer(-half)` once per piece; the tint pass's `Polygon(p["poly"]).buffer(0)` once
  per plot; any other repeat found by the profile after D12.
- **D12 Batch**: `_plant`'s per-cell chain (intersection, despike, core, fat, kept, arms) runs as shapely array calls
  over all cells of a pocket; the tint pass's areas, convex hulls and minimum rotated rectangles run as array calls
  over all plots. Order of results is kept (the outputs are sorted the same way as today).
- **D13 Touched cells**: `_plant` intersects the pocket with each ROW band first and cuts only the cells within that
  band's intersection extent, so the cells visited are those the pocket touches; a test builds a diagonal sliver
  pocket and asserts the cell count tracks its area.
- **D14** Re-profile after D11-D13; the next heaviest step (`_visible_parts`, `_absorb`, `_unjog`) gets the same
  treatment until SC-004 holds.

### E. Track path checks (FR-005)

- **D15** `hamletgen/ways/checks.py`: `PathChecker(avoid, pond, brook, waters)` - brook and water segments boxed in
  `PointGrid`s, avoid polygons by box - with `violations(path)` running the same per-segment tests on the near items
  only, plus the double-bridge `pairs_within` count as today. `stage_track` builds one per argument set it uses and
  calls it where it called `path_violations`. `path_violations` stays as the oracle.
- **D16** The equality test: over Inashiro's candidate paths (recorded through the track stage on a real roll), the
  checker's count equals `path_violations`'s for every path.

### F. Measure, sweep, record (FR-006 to FR-008)

- **D17** `make h276` (a Makefile operation) runs the harness and writes a JSON; the measurements' `command` field
  names it, so `make figures` can re-run them (round 3's aside).
- **D18** After C-E: `make done` (every pool map regenerated, 100% coverage), FR-006's counts against
  `pool-before.json`, the after-cohort against R7, `make perf LABEL=276-end` and `perf-report`.
- **D19** `dev/performance.md` gains the three shapes with their measurements (FR-008).

## Verification per piece

| piece | proves it | then across the pool |
|---|---|---|
| A | D3 green; SC-001 by the harness | `make quick ALL=1` |
| B | D5's equality test and D6 green; SC-001a | `make quick ALL=1` |
| C | D7/D8 equality tests, D9 same-seat test, SC-002/SC-003 by the harness, Inashiro regenerated | `make done`, FR-006 counts, cohort |
| D | D13 test, the waterfields tests, SC-004, Inashiro regenerated | `make done` |
| E | D16, SC-005, Inashiro regenerated | `make done` |

## Project Structure

```text
specs/276-engine-hotspots-and-test-scans/  spec, plan, research, request, harness.py, measurements.json, tasks.md
.claude/skills/diagram/tests/_engine_ast.py, tests/test_engine_ast.py       (A)
.claude/skills/diagram/tests/interactive/test_record.py, test_record_format.py (B)
.claude/skills/diagram/l7r/diagram/settlement/rolling/{fit,place,bundle,farmsteads}.py, settlement/core.py,
    hamletgen/homesteads/boundary.py                                        (C)
.claude/skills/diagram/l7r/diagram/waterfields/seams/{plots,pockets,close}.py (D)
.claude/skills/diagram/l7r/diagram/hamletgen/ways/{checks,track}.py         (E)
```

## Complexity Tracking

None: no file passes 1,000 lines, no function grows past human scale, no exception to a rule.
