# Implementation Plan: homesteads at scale

**Branch**: none (`main` in the clone; `SPECIFY_FEATURE=304-homesteads-at-scale`) | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

**Input**: `specs/304-homesteads-at-scale/spec.md` (FAITHFUL, round 2), the GM's words in `request.md`, the measurements in
`research.md`.

## Summary

The homesteads stage grows 17-24x for 4x the households, and 139x on seed 47 (research R1). Three levers, in the spec's order,
each landing only on a measurement: the perf bookend gains a scaling leg at 10/20/40 households (P1, tooling only); the two
whole-map scans the profile names are indexed with identical answers (P2: the access tree's nearest targets, and the shared
sheds' pocket test against every paddy, R2-R3); then the exhaustive seating pass stops offering dead seats by one of the two
accepted forms, chosen by measurement (P3, R4).

## Technical Context

**Language/Version**: Python 3.14 (the engine under `.claude/skills/diagram/l7r/diagram/`)

**Primary Dependencies**: numpy, shapely, PIL (existing); `settlement/_geom/indexes.py` `PointGrid` for the new indexes

**Testing**: pytest through `make quick` / `make test-file` / `make done`; 100% coverage over the engine

**Project Type**: map generator (library + make-driven tools)

**Performance Goals**: the session's goals SC-002/SC-003 (homesteads s/household at 40 at most 2x that at 10; the stage at 40 at
least 2x faster than the base) - goals, not the GM's; a miss is recorded and raised (spec)

**Constraints**: SC-004 (the 15-household reference not slower, band 0 or better); SC-005 (P2 output-identical); SC-006 (every
cohort seed seats at least what it seated)

**Scale/Scope**: the reference spec at 10/15/20/40 households; the five pool hamlets; cohort seeds 1-24

**Single-artifact target**: `pool/hamlets/inashiro/inashiro.gen.py` (`make map` 5-7 s, memory note of 2026-10-01); the
scaling legs are measured by the snapshot tool, not by a pool map (no pool map has 40 households).

**Every step is two steps.** Each engine lever: Inashiro first (`make map GEN="--no-cache pool/hamlets/inashiro/inashiro.gen.py"`),
then the pool (`make maps SCOPE=all`) and the cohort (`make cohort N=24`), each its own task.

## Performance bookends (constitution VI)

| | label | total | median | worst | notes |
|---|---|---|---|---|---|
| before | `304-start` | 12.3 s | 3.0 s | 3.8 s | taken 2026-10-02T03:17Z on unmodified code (`dev/perf-log/20261002T031740Z-304-start-diagram-performance.json`) |
| scaling base | `304-scale-base` | | | | taken with the D1 tool on the UNMODIFIED engine, before D5 (the first engine edit) |
| after | `304-end` | | | | before the push; compared against both |

The trend before starting: 302-end 12.7 s on the same four seeds, 304-start 12.3 s - no drift.

## Decisions

### P1: the scaling leg (FR-001 - FR-003)

- **D1 The snapshot measures sizes.** `perf_snapshot.measure(seeds, households=None)` rolls `REFERENCE` with `households`
  overridden when given; a constant `SCALING_SIZES = (10, 20, 40)` beside `DEFAULT_SEEDS`, with the docstring saying why 80 is
  not in it (research R5). `record` writes the reference `rows` exactly as today plus a `scaling` list: one row per (size, seed)
  with `households`, `seed`, `seconds`, `stages`, `houses`, `placer_calls` (from `s._seat_search`, the counter that shows a
  pruning lever's effect without a profile) and, for a roll the generator refuses, `refused` (`"<ExceptionClass>: <message>"`)
  in place of `seconds`. Same four seeds at every size; a refusing seed is recorded, never swapped (spec Edge Cases).
- **D2 The band is lifted by the measuring tool alone (FR-003).** `hamletgen/plan.py` gains a context manager
  `beyond_the_band()` setting a module `ContextVar`; `HamletSpec`'s band check is skipped while it is set. Only
  `perf_snapshot.measure` enters it. A test asserts a spec of 40 households is refused outside it and admitted inside, and a
  second asserts no file under `pool/` names it.
- **D3 Each size is banded against its own history (FR-002).** `perf_bands.evaluate_scaling(base, cur)` returns one `Verdict`
  per size, evaluated by the SAME rules and lines as `evaluate` on that size's rows (a refused row on either side is left out
  of the sums and printed as refused). A base with no `scaling` (every snapshot before this feature) yields, per size, a
  "no baseline" line, not an error. `perf_snapshot.report` prints the scaling legs under the reference; `perf_review`'s push
  check and `perf-gate` take the band they owe as the maximum over the reference and the legs - one band per pair, as today.
- **D4 SC-001's seeded fault is a test.** A unit test builds a base and a current snapshot whose 40-household rows add a
  stage time quadratic in the household count while the 15-household rows are unchanged, and asserts the 40 leg's verdict
  reaches band 2 or 3 while the reference stays band 0. The live plumbing (the tool rolling 40 households end to end) is
  proven by `304-scale-base` itself.

### P2: the indexed scans (FR-004, FR-005; output-identical, SC-005)

- **D5 `AccessTree.targets` asks a ring, not the tree.** The answer today is `heapq.nsmallest(TARGETS_TRIED, pts, key=dist)` over
  a list of, per corridor in order, its nearest point and then its points along; `nsmallest` keeps list order among equal
  distances, so the answer is "the first `TARGETS_TRIED` by (distance, list position)". Indexed: the points along go into a
  `PointGrid` (cell 128 px, as `grid`) with their position `(corridor index, 1 + k)`; the corridors are already in `grid`
  (boxes widened by `half`, a superset). A query searches radius `r` from `4 * TARGET_STEP_PX`, doubling: the candidates are
  each corridor `grid.near(p, r)` returns (its nearest point, position `(i, 0)`) and each point along within the box; those
  within distance `r` are kept; once at least `TARGETS_TRIED` are within `r`, every point outside `r` is farther than all of
  them, so the first `TARGETS_TRIED` of the kept, sorted by (distance, position), ARE the scan's answer. When `r` exceeds the
  farthest corner of the tree's extent from `p`, the scan runs instead (fewer points than `TARGETS_TRIED` in all). The memo per
  door, cleared on `add`, stays. Distances by `math.dist` as today, so ties compare equal floats.
- **D6 The shared sheds' pockets ask the paddies near them.** `reserve_commons_byres` files `field_polys`' bounding boxes in a
  `PointGrid` once (the field does not change while the pockets are laid) and `_commons_pocket_clear` asks only the outlines
  whose box comes within `bh` of the candidate: a point inside an outline is inside its box, and an outline within `bh` has its
  box within `bh`, so no outline the scan would refuse on is skipped. Same predicate per outline, same verdict.
- **D7 What is left alone, and why** (research R3): `corridor_bars` and `_standing_clear` already read indexes;
  `surface_water_dist` scans the water, which does not grow with the households. `FreeGround._samples` (11.4% self on seed 47)
  is numpy work proportional to the corridor lines asked - D8's lever is what cuts the lines; it is not a scan to index.
- **D8 Proving identical output.** (a) An equivalence test per lever with the old body kept in the test file as the oracle:
  random trees and doors for D5 (including ties and a tree under `TARGETS_TRIED` points), random outlines and candidates for D6.
  (b) A one-roll spy (feature 297's form): the reference rolled with each indexed answer compared against the oracle on every
  97th call. (c) The pool regenerated: every pool hamlet's SVG and manifest byte-identical to the base (`git status` over
  `pool/hamlets/` empty after `make maps SCOPE=all`); the cohort's per-seed house and lane counts identical.

### P3: no dead seats (FR-006; may move seats, never the count)

- **D9 The forms measured, cheapest first, by scratch toggles on top of P2, base and clone back to back:**
  - **A, the region re-asked**: `seat_the_rest` re-asks `region.offer` of the seats it has not yet offered after each house it
    seats (`SeatRegion.sync` already paints the new corridors and wood seats; the reachable raster is rebuilt from the grown
    tree). Seated homesteads stay unpainted, as `sync`'s own rule says.
  - **A', the region re-asked with the homesteads painted**: A, plus each seated homestead's box painted as it lands -
    incrementally (one box per house), where 297's R15 rebuilt the raster per house and lost 9% at hamlet size.
  - **B, the line-of-sight reach region**: a cell is reachable when a straight strip from it to a tree point clears the
    standing ground - the lever 297 priced (R2: 348 of 477 corridor searches on Inashiro found no candidate at all).
  Each is timed on the four seeds at 15, 20 and 40 households (the stage, best of three) and counted (placer calls, houses
  seated), and on the pool and cohort seeds 1-24 (houses seated per seed, rules passed).
- **D10 The choice rule.** Kept: the form with the lowest summed homesteads time at 40 households that seats at least the base's
  households on every cohort seed and pool map, and is not slower at 15 households over the four seeds. Built in the engine
  only after the scratch measurement chooses it. If no form is faster at 40 than P2 alone, all three are withdrawn and recorded
  (FR-006, FR-007) and the feature lands P1 and P2.
- **D11 A built form's tests.** Red first: a test that the exhaustive pass offers no seat the region's current state refuses
  (A/A') or that a seat with no clear strip is not offered (B), on a hand-built settlement; then the counts test on the
  reference roll (placer calls per house seated below the base's).

### Records

- **D12** `dev/performance.md` gains a section "Homesteads at scale (feature 304)": R1's table, what each lever bought by the wall
  clock, the forms withdrawn with their numbers (FR-007). `research.md` holds each measurement as it is made.
- **D13** The memory note on the hamlet profile is updated with the outcome.

## Constitution Check

- **I, II**: N/A - no UI in this repository.
- **III, IV, V, VII, VIII, IX**: N/A - no pool content kind, SOURCE block, in-world prose or setting detail is added.
- **VI. Verify before done**: each task names its check - `make quick` per edit; `make test-file` for the new tests; Inashiro
  regenerated then `make maps SCOPE=all` and `make cohort N=24` for P2 and P3; `make done` at the end; the bookends above.
  No review check has an occasion here (no element new to a map, no glyph or placement rule changed); P3 may move seats within
  the existing rules, which is not a `_review_owed` occasion.
- **X. Python discipline**: red-green per decision (D4, D8a, D11 first); ruff, format, pyrefly; 100% coverage. Clause 15: D5 and
  D6 ARE the index for their checks (a `PointGrid` built once / kept on `add`); B, if built, reads a raster built once per
  change to what stands. File sizes: `access.py` 611 lines + D5 (~40) stays under 1,000; `byres.py` 506 + ~10; `perf_snapshot.py`
  322 + ~60; `perf_bands.py` 184 + ~40; none nears the bar.
- **XII. Historical grounding**: N/A for P1 and P2 (no output change). P3 changes which seat a household may take, never a rule,
  a size or a glyph: every seat taken passes the same rules (spec Decisions Recorded). No rendering decision.
- **XIII. No known regressions**: baseline in a detached worktree at the claim's base, `git worktree add --detach /tmp/base304
  52c3d8725`: `make cohort N=24` there and in the clone, back to back; the pool's rules from `make maps SCOPE=all`. Zero new
  failures; P2 must leave every artifact identical, P3 every count at least equal.
- **XIV**: a defect found on the way is fixed in this work.
- **XVI**: no exception to the spec; D7 leaves three scans alone because they are not superlinear (research R3), and that is
  in this plan for the review to judge.

## Project Structure

```text
specs/304-homesteads-at-scale/
├── request.md, spec.md, research.md, plan.md, tasks.md
.claude/skills/diagram/l7r/diagram/
├── tools/perf_snapshot.py      D1, D3 (report)
├── tools/perf_bands.py         D3
├── tools/perf_review.py        D3 (the band owed)
├── hamletgen/plan.py           D2
├── settlement/rolling/access.py        D5
├── settlement/shrines_wells/byres.py   D6
└── hamletgen/homesteads/capacity.py, region.py   D9 (the chosen form only)
.claude/skills/diagram/tests/   the tests of D2, D3, D4, D8, D11
```

No `data-model.md`, `contracts/` or `quickstart.md`: the one data shape (the snapshot's `scaling` rows) is D1, and the feature
exposes no interface beyond `make perf` / `make perf-report`, whose usage does not change.

## Complexity Tracking

None.

## Amendment 1 (2026-10-02): what the measurements withdrew (research R10)

- **D5 withdrawn.** The ring query answered exactly as the scan (74 equivalence cases, the spy's 1,314 ring comparisons, research R7) but was 1-4%
  SLOWER on the stage at 40 households on all four seeds, alternated runs; a fallback to the scan once the ring outgrew the
  tree's point count did not close the gap. The scan is restored and `access.py` records the attempt at `targets`. FR-004's
  index is therefore not shipped: FR-007 ("including any lever withdrawn") and D10's rule govern, and the miss is raised with
  the GM with SC-002/SC-003's.
- **D6 kept**: seed 47's stage 55.6 -> 48.8-49.9 s; nothing on the other seeds (no `detached_commons` byres).
- **P3 withdrawn under D10**: at 40 households A 113.7 s, A' 198.6 s, B 82.7 s against P2's 77.0 s summed; T32-T34 dropped.
- **Two pre-existing cohort failures fixed** (T02, T03; research R8, R9), the cohort 28/30 -> 30/30; Kashikawa gains one lane.
- **The scaling bookend (P1) shipped as planned**: `304-scale-base` -> `304-end` back to back, band 0 at every size.
