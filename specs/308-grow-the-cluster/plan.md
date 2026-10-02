# Implementation Plan: grow the cluster

**Branch**: none (`main` in the clone; `SPECIFY_FEATURE=308-grow-the-cluster`) | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)

**Input**: the accepted spec (round 2 FAITHFUL), the GM's words in `request.md`, and the prototype rounds in `research.md`.

## Summary

The GM's growth works once a house's path can bend.
- **Rounds 1 to 3 (R1-R3).** Each grew houses at the footprint's minimum distance, sun corridor included. None filled a margin
  reliably: R1 seated 3-15 a margin (8-28 on seed 25), R2 3-7, and R3's variants filled one margin in ten at best. A house grown behind another has no STRAIGHT run from its door to the access tree: the standing house and
  its woodlot stand across every run.
- **The current engine (R4).** It finds the rare seats a straight run reaches by offering every free grid point, which costs
  hundreds to thousands of offers and margins thrown away.
- **Round 5 (R5).** Where no straight corridor clears, the path is routed round what stands and pulled taut through the engine's
  own leg tests: FR-005, the path laid back to the tree as the house is placed. Growth then fills a margin. When its seats run
  dry it widens (more directions, farther rings), and the eight seeds tried all seat 40 households on the first margin in 1.6 to
  4.2 s.

The engine change is that grower (FR-003, FR-004, FR-007) and that router (FR-005). It is built ONLY ON GO (US2, FR-001), and
the verdict is recorded: R7, GO at 10, 15, 20 and 40 households.

**The goals it misses (FR-002).** R6 misses both of the session's goals:
- SC-002 (under 4 s on every seed at 40 households): seeds 3, 4, 7 and 8 take 5.32, 4.14, 4.10 and 10.01 s.
- SC-003 (at most 5 offers per house kept): R6's offers are 224-3,427 per seed at 40 households, 5.6-85.7 per house kept
  (research R6's table).

The plan review's footprint terms (D1) are a further round, measured before the engine build as R8. A further tuning round of
the levels and the router's breadth is measured on the engine (T06). A miss that survives both is recorded with every round's
numbers and raised with the GM.

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
    the path's room (`grow_gap`, below).
  - *A standing homestead's footprint* (FR-003) is made of:
    - its envelope (`geom["bbox"]`: the house, the yard and the beds);
    - its reserved woodlot seats (a clump's half-width round each);
    - to the SOUTH, the sun its yard AND its beds are owed. That is the farthest south edge of the yard or a bed, plus
      `SUN_CORRIDOR_FT` and the placer's 2 ft (`_sun_corridor_ok` and `_gardens_sun_ok`, computed, not assumed);
    - its PATH OUT. The gap (`grow_gap`) is a corridor's whole strip (2 x `ACCESS_HALF_FT`) plus 2 px, so a path fits between two
      footprints, and a standing house's own reserved path is refused to every envelope by the placer.
  - *The new household's reach* is its envelope ROLLED AT THE SEAT OFFERED, exactly as the placer will lay it there
    (`household_reach`, `settled_seat`).
    - The household is the next one: the k-th plain household takes lot k. Its parts are set as the seat search sets them
      (`household_parts`: its fixtures, its byre, its well pocket), and then taken down. Its house comes from the lot's size
      ladder and its kura from the lot (`_try_place_bundle`'s own reading). The rolls key on the seat, as the seat search
      keys them on `_household_seat`.
    - The seat is first placed with a first guess (the reach at the first house). Where the reach rolled at that seat
      exceeds the guess on any side, the seat is moved out to the union of the two and asked again. After `SETTLE_TRIES` (4)
      moves without settling, it is not offered. A unit test holds the move, the drop and the household's own lot.
    - MEASURED (research R9): no unmoved placement exceeds the reach its seat was spaced for. All 12 of 234 that do were
      moved by the placer's existing one computed move off an overlapping neighbor, by at most 5.5 px.
    - Two bounds were priced and refused.
      - The largest house with the household's parts left 33 of 272 placements over, by up to 21 px: the fixtures are
        sought round the household's own walls, so a larger house does not bound them.
      - The roll's own limits (the yard's lognormal reaching about 13 times the median area) would give a footprint every
        seat carries for a yard almost no household rolls.
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
    `parts_clear`, `standing_ground` and `lawful_leg`. A route has at most 5 legs, none doubling back (`doubles_back`).
    The whole route must then leave its own yard (`leaves_its_yard`, feature 287 M8). These are every test `_house_candidates`
    asks of a straight or round-the-gable corridor, so no corridor rule is skipped (FR-005, FR-006).
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
  - The paths' glyph is unchanged, and no element is new to a map. But two placement rules change substantially, so
    `tasks.md`'s `## Occasions` declares a glyph-check on Inashiro for each:
    - the village lane (D3), whose path may now be routed;
    - the farmhouse (D1, D2), whose cluster is now grown.
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
