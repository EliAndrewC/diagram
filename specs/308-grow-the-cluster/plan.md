# Implementation Plan: grow the cluster

**Branch**: none (`main` in the clone; `SPECIFY_FEATURE=308-grow-the-cluster`) | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)

**Input**: the accepted spec (round 2 FAITHFUL), the GM's words in `request.md`, and the prototype rounds in `research.md`.

## Summary

The GM's growth works once a house's path can bend.
- **Rounds 1 to 3 (R1-R3).** Each grew houses at the footprint's minimum distance, sun corridor included. They stalled at 3 to
  21 houses a margin. A house grown behind another has no STRAIGHT run from its door to the access tree: the standing house and
  its woodlot stand across every run.
- **The current engine (R4).** It finds the rare seats a straight run reaches by offering every free grid point, which costs
  hundreds to thousands of offers and margins thrown away.
- **Round 5 (R5).** Where no straight corridor clears, the path is routed round what stands and pulled taut through the engine's
  own leg tests: FR-005, the path laid back to the tree as the house is placed. Growth then fills a margin. When its seats run
  dry it widens (more directions, farther rings), and the eight seeds tried all seat 40 households on the first margin in 1.6 to
  4.2 s.

The engine change is that grower (FR-003, FR-004, FR-007) and that router (FR-005).

## Technical Context

**Language/Version**: Python 3.14 (`.claude/skills/diagram/l7r/diagram/`)

**Testing**: pytest via `make`; 100% coverage over the engine

**Performance Goals**: the session's SC-002/SC-003

**Scale/Scope**: the reference at 10/15/20/40 households, the five pool hamlets, cohort seeds 1-24 and the six pinned

**Single-artifact target**: `pool/hamlets/inashiro/inashiro.gen.py`, then the pool and the cohort.

## Performance bookends (constitution VI)

| | label | notes |
|---|---|---|
| before | `308-start` | the scaling-leg snapshot on the unmodified engine, before any engine edit |
| after | `308-end` | before the push; `make perf-report AGAINST=308-start` |

## Decisions

- **D1 The growth seats a nucleated margin** (`hamletgen/homesteads/growth.py`, new; FR-003, FR-004, FR-007).
  - *The first house.* It is offered the margin's free ground nearest the seat, in order (`capacity.free_seats` through the
    seat region, at most `DRY_SPELL` offers), so the cluster starts where the front row started, against the field.
  - *Each next house.* Every standing house offers seats in a ring of directions round itself, jittered positionally from
    the map's seed (`_hjit`). The direction is jittered by ±12 degrees (`GROW_JITTER_DEG`) and the distance by up to +12%
    (`GROW_JITTER_FRAC`). Each seat stands at the distance in that direction where the two homesteads' FOOTPRINTS part, plus
    `GROW_GAP` (6 px).
  - *A homestead's footprint* is its envelope (`geom["bbox"]`) plus its reserved woodlot seats (a clump's half-width round
    each), and to the SOUTH its threshing yard's far edge plus `SUN_CORRIDOR_FT`. The new house's own reach is the first
    house's footprint.
  - *The order.* Seats are offered nearest the seat center first, within the form's bound (`FORM_BOUND` times the 162 ft
    seating band's diagonal). Each is judged by `try_place`, which relaxes and skips no rule (FR-006).
  - *When the seats run dry.* With households left, every standing house offers again at the next level of `GROW_LEVELS`:
    (8 directions, ring 1), then (12; rings 1 and 1.5), then (16; rings 1.25, 1.75 and 2). Past the last level the margin is
    reported short and the ladder offers the next. The levels are a search breadth, never a rule (R5).
  - *Class.* Every figure is a guess with its reason beside the constant: a jitter from the GM's *"a little randomized jitter"*,
    a gap and rings from R5's measurements. The ORDER of placement is a map drawing convention (spec Decisions).
- **D2 The front row, the lattice ranks and the exhaustive pass with its rescue are removed for the nucleated form**
  (FR-007, round 1's ruling). `_seat_households` calls `grow_the_margin` in their place where `settlement_form == "nucleated"`.
  The dispersed form keeps them (round 1: LEGITIMATE), and the linear form's `seat_rows` is untouched. `capacity.seat_the_rest`
  and the rescue stay for the dispersed form. `seat_search` records `grow_offered`, `grow_took` and `grow_level`, and drops the
  front row and rounds keys on the nucleated path.
- **D3 A corridor is routed where no straight one clears** (`settlement/rolling/route.py`, new; FR-005).
  - *Where it runs.* `_house_candidates` (`access.py`) yields its straight and round-the-gable corridors as before, and THEN,
    where the tree says so (`AccessTree.routed`, set True by the nucleated seating only), the routed ones. The search is A*
    (weight 1.5, aimed at the tree's nearest points) on a 12 px grid within 320 px of each dooryard door. A grid point is
    open off the site's taken ground, off every placed box by the corridor's half-width, off the reserved wood seats and off
    the house's own box.
  - *Pulled taut.* Each leg reaches the farthest node the engine's own leg tests admit: `house_clear`, `fixtures_clear`,
    `parts_clear`, `standing_ground` and `lawful_leg`, the same tests a straight corridor passes. A route has at most 5 legs,
    none doubling back (`doubles_back`).
  - *Admitted.* It is admitted by `tree_admits` as any corridor is, and recorded leg by leg (`reserve`), which the web already
    draws as a chain.
  - *Class.* A map drawing convention: the routing is how a seat's path is found, and the web draws it under the unchanged
    lane law. The paths it draws bend between the homesteads, which the record's accretion form of village lanes already
    describes (each household cutting its own way, `research/contents.json#ways`). It is recorded at the module's docstring
    with the pointer.
  - *Indexed* (the root CLAUDE.md's overlap rule): each grid point asks the placed index (`_reach_index`), the site raster
    (`FreeGround`) and the wood grid, never a registry walk. The route is remembered per door while nothing stands anew
    (`_standing_memo`).
- **D4 Dispersed and linear are unchanged**, per round 1's rulings. Only the nucleated form grows.

## Verification

The prototype's legs are back to back over the sixteen seeds at 10/15/20/40 households (R6). Then:
1. Inashiro alone.
2. `make maps SCOPE=all` and `make cohort N=24` plus the six pinned seeds, each against the base's baseline, measured in a
   detached worktree.
3. `make done`, then the bookends.

## Constitution Check

- **I, II, III, IV, V, VII, VIII, IX**: N/A. There is no UI, pool content kind, SOURCE block, prose or setting detail.
- **VI**: per task below.
  - The occasions: the seating moves every nucleated hamlet's cluster, and the corridors may now bend.
  - The paths' glyph is unchanged, and no element is new to a map. But the placement rule that lays a house's path changes
    substantially (D3), so a glyph-check of the access lanes on Inashiro is declared in `tasks.md`'s `## Occasions`.
- **X**: red-green tests for the router and the grower (unit tests on plain inputs), and 100% coverage.
- **XII**: D1's figures are guesses with reasons at the constants; D3's class is recorded at the module.
- **XIII**: the cohort and pool baseline is taken on the base in a detached worktree before the engine edit.
- **XIV**: any defect found on the way is fixed in this work.
- **XVI**: FR-007 is built literally for the nucleated form. Dispersed and linear are scoped out by spec-fidelity's round-1
  ruling, not by this plan.

## Project Structure

```text
specs/308-grow-the-cluster/   request, spec, research, plan, tasks, prototype.py (the rounds)
.claude/skills/diagram/l7r/diagram/
├── hamletgen/homesteads/growth.py   D1 (new)
├── hamletgen/homesteads/stages.py   D2
├── settlement/rolling/route.py      D3 (new)
└── settlement/rolling/access.py     D3 (the `routed` slot, the hook in `_house_candidates`)
```

## Complexity Tracking

None.
