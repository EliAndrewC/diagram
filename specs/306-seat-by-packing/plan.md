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

- **D1 The seat band's ground per household is 162 ft** (`hamletgen/consts.py` `HOMESTEAD_GROUND_FT`, FR-010; spec Decisions: a
  guess with its reasoning). The band's area is `households x HOMESTEAD_GROUND_FT^2` (`plan.band_extent`), so the figure is the
  side of a square holding the MEAN homestead: the pool's 82 envelopes' mean (20,366 sq ft, research R6) plus the least wood
  floor (`HOMESTEAD_WOOD_FT2[0]`, 6,000). The comment beside it carries the derivation, the twelve- and thirty-seed sweeps (R7)
  and the 104 it replaces (and why: the wood floor came after it). It also grows the canvas's room for the seat (`seat_room`),
  so every hamlet map moves; the pool and the cohort are re-rolled and held to every rule (FR-008).
- **D2 The rescue and the dry-spell cap are built only if they pay on top of D1** (FR-011): measured on the sixteen-seed set
  at 40 households, D1 alone against D1 with both (research R9); built where faster beyond the spread with every household
  seated, else recorded and withdrawn.
- **D3 FR-003 (capacity predicted before seating) and FR-004 (packed proposals) are not built** - their prototypes were NO-GO
  (R1-R4, FR-011); with D1 the first or second margin seats 28 of 30 seeds at 40 households (R7), so the ladder's cost is a
  margin or two, not sixteen.
- **D4 The overlap census** (FR-006): `tools/overlap_census.py`. `sys.monitoring` armed on the geometry primitives' code objects
  (`settlement/_geom/primitives.py`'s pairwise measures and `_geom/overlap.py`'s public predicates); each comparison charged to
  the nearest named function outside `settlement/_geom/` (comprehensions and lambdas charged to their function), whose calls
  are counted from its first comparison on (its code object armed then). Rolled over every pool hamlet's spec (read from its
  gen, `generate` intercepted) and the reference at 40 households, stages only (the perf tool's loop). Reports per check: the
  stage, calls, comparisons, comparisons per call; FLAGS a check over `CENSUS_FLAG = 5,000` comparisons per call - the knee
  of the measured distribution (R10: nine checks from 5,048 to 111,700; the next below at 3,859, the bulk under 1,500). `make
  census` runs it; `make perf` runs it after the snapshot (FR-006's standing check), printing the flagged list.
- **D5 Each flagged check gets its index, box or line, with identical answers** (FR-007): the nine of R10, given to three
  background agents in worktrees grouped by file, each held to byte-identical pool manifests and an equivalence test with the
  old scan as its oracle; a check that cannot be indexed exactly, or is slower indexed, is recorded with its measurement,
  mechanism and sketch (research R11).
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
