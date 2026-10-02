# Implementation Plan: seat by packing

**Branch**: none (`main` in the clone; `SPECIFY_FEATURE=306-seat-by-packing`) | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)

**Input**: the accepted spec (round 3 FAITHFUL; Amendment 1 FAITHFUL), the GM's words in `request.md`, the seven prototype
rounds in `research.md`.

## Summary

The homesteads stage at a village's size was slow because the seater seats a whole margin to learn it falls short, then
another, then another - sixteen on seed 47 (spec Context). Seven prototype rounds measured why (research R1-R7): the free
ground holds two hundred-odd homestead boxes, but a seat needs a straight corridor to the access tree, and a cluster seated
on a band sized for 104 ft a household - its house, yard and row, not its wood floor - sits at the edge of its capacity, so
whether a margin fills is near chance. Proposing seats differently (beside the tree, grown from the houses, along planned
lanes) did not move that edge; giving the band the ground a homestead actually takes did. The engine change is that figure
(FR-010), the crash the scaling leg found (R8), the overlap census (FR-006) and the fixes to the checks it flags (FR-007).

## Technical Context

**Language/Version**: Python 3.14 (`.claude/skills/diagram/l7r/diagram/`); `sys.monitoring` for the census

**Testing**: pytest via `make`; 100% coverage over the engine and the tools

**Performance Goals**: the session's SC-002/SC-003 (judged on the levers built, FR-011)

**Scale/Scope**: the reference at 10/15/20/40 households, the five pool hamlets, cohort seeds 1-24 and the six pinned

**Single-artifact target**: `pool/hamlets/inashiro/inashiro.gen.py`, then the pool and the cohort.

## Performance bookends (constitution VI)

| | label | notes |
|---|---|---|
| before | `306-start` | the scaling-leg snapshot on the unmodified engine (feature 304's tool), before D1 |
| after | `306-end` | before the push; `make perf-report AGAINST=306-start` |

## Decisions

- **D1 The seating's band holds the homestead's whole ground: `SEATING_GROUND_FT = 162`** (`hamletgen/consts.py`, FR-010; spec
  Decisions: a guess with its reasoning). The side of a square holding the MEAN homestead (the band's area is the households'
  sum): the pool's 82 envelopes' mean (20,366 sq ft, R6) plus the least wood floor (`HOMESTEAD_WOOD_FT2[0]`, 6,000). It sizes
  only `_seat_households`' lattice and seat bound; the margin's choice, the canvas's room and the belt keep `HOMESTEAD_GROUND_FT`'s
  104 - growing those too re-fitted every field and refused sites the base seated (R11), and the canvas grown alone made 40
  households worse (R12). Its own verdict (FR-011), the back-to-back run of R15: GO - the band ALONE (the dry cap and rescue off) 427.7 -> 95.0 s over
  the fifteen seeds the base rolled at 40 households (100.0 over all sixteen), the first margin on 9 of 16 against 1 of 15, every household seated; the
  cohort 30/30. The pool's two regressions under it (Inashiro's access lane, Sawada's doubled way) went to their root causes (R14).
- **D2 The rescue and the dry-spell cap are built only if they pay on top of D1** (FR-011): R15's third leg, on the final D1 -
  100.0 -> 83.3 s, margins saved on seeds 25, 8 and 6, seed 39 slower (7.45 -> 13.96 s), no seed seating fewer: GO, built.
  (R9 measured them on D1's withdrawn form; R15 is their verdict.)
- **D3 FR-003 (capacity predicted before seating) and FR-004 (packed proposals) are not built.** FR-004's packed proposals
  were prototyped and measured NO-GO (R3: beside the tree, grown from the houses; R4: along planned lanes). FR-003's
  free-ground prediction was measured and disproved (R1); its rules-based form was argued from R2-R3 (the cap is reachability,
  not ground) and NOT prototyped - with D1 a margin's capacity is no longer the edge it was. Seed 47 still seats on the seventh
  margin at 162 alone (R7), on the third with the rescue (R9); under the final D1 on the first, 2.99 s alone and 3.11 s with D2
  (R15) - every reference seed's miss against SC-002/SC-003 is recorded with every round's numbers and raised with the GM.
- **D4 The overlap census** (FR-006): `tools/overlap_census.py`. `sys.monitoring` armed on every pairwise measure - the
  geometry package's (`_geom/primitives.py`, `_geom/overlap.py`'s public predicates) AND shapely's binary predicates and
  `distance` on its geometries; each comparison charged to the nearest named function outside both (comprehensions and lambdas
  to their function), whose calls are counted from its first comparison. The reach it does not have, stated: comparisons made in
  C over arrays (a numpy raster, shapely's vectorized functions) - the boxes and rasters the rule asks for. Rolled over every pool
  hamlet's spec and the reference at 40 households. FLAGS a check over `CENSUS_FLAG = 5,000` comparisons a call - R10's
  distribution: nine checks 5,048-111,700; below them 3,859 (`serve._lay_web_lane`), then 2,631, 2,624, 1,857, 1,799, 1,725 ... and
  the bulk under 1,500: the step from the bulk to the tail is at ~4,000-5,000, and 5,000 flags the tail. `make census`; `make perf`
  runs it after the snapshot (the standing check).
- **D5 Every check the D4 census flags gets its index, box or line** (FR-007), starting with R10's nine. Identical answers are
  the preferred fix (an exact index, byte-identical pool manifests, an equivalence test with the old scan as its oracle); where
  only a box or a line that MOVES an answer cuts the comparisons, it is built and held to FR-008 instead (every pool map and
  cohort seed passes every rule and seats as many households). A check is left unchanged only where the fix is SLOWER by the
  wall clock, recorded with the measurement, mechanism and sketch. (R13: the nine indexed, all exact; the census after them
  flags none.)
- **D6 The planted region's sliver line** (R8): fixed, tested (constitution XIV).

## Constitution Check

- **I, II, III, IV, V, VII, VIII, IX**: N/A - no UI, pool content kind, SOURCE block, prose or setting detail.
- **VI**: per task below - `make quick`, `make test-file`, Inashiro then `make maps SCOPE=all` and `make cohort N=24`,
  `make done`, the bookends. Occasions: D1 moves every hamlet's cluster (a looser band) - no element new, no glyph redrawn, no
  placement RULE changed (the figure sizes the band offered; every seat passes the same rules); declared `none` in tasks.md
  with that reason.
- **X**: red-green (D4's census test on a deliberate scan, D5's equivalence tests, D6's done); 100% coverage of the census tool;
  clause 15 is D5 itself.
- **XII**: D1 is a rendering decision (how much ground the cluster's band holds) - classed a guess with its reasoning in the
  spec's Decisions table, the research (R6, R7) and the comment at the constant.
- **XIII**: the cohort baseline from feature 304 (30/30); re-measured on the base in a detached worktree before D1.
- **XIV**: D6.

## Project Structure

```text
specs/306-seat-by-packing/   request, spec, research, plan, tasks, prototype.py (the rounds)
.claude/skills/diagram/l7r/diagram/
├── hamletgen/consts.py              D1
├── tools/overlap_census.py          D4 (new)
├── waterfields/partition.py         D6
└── (the nine flagged checks' modules) D5
.claude/skills/diagram/Makefile      `census`, and `perf` running it
```

## Complexity Tracking

None.
