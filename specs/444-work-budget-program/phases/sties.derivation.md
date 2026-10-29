# Derivation - sties (feature 444)

## Contract

- Reads: the households and their farmsteads (the house and its outbuildings, their walls); the hamlet's form (a dike-pond hamlet keeps no sty here); the share of households keeping a sty (`quota_carriers`, about two in three, 0049); the registry of what stands - every part, way, crossing, tree and stand placed before this stage; each farm's grove band (`grove_rules.fixture_on_band`).
- Writes: each sty, a farm fixture of kind `sty` drawn 8 by 6 ft (`STY_FT`), against a wall of its house or an outbuilding; `meta.sty_target` and `meta.sty_short`.
- Keeps: the share's count of households, each sty on its own household's plot against a wall (0049, 0029: raked with its house); clear of the plot's other parts by the 3.5 ft wall gap (`WALL_GAP_FT`), the places 4 ft apart along each wall (`WALL_SLIDE_FT`), both GUESSES; never on a grove band; the first place the registry admits; a household with no place passes its sty to the next that keeps none (a GUESS); every rule asked before the sty is drawn (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): households 10 and 20, each tried at most once; sties 7 and 15 (x2.14: 15 at 20, 33 at 40, 69 at 80); a farmstead's wall length, its house and outbuildings, at most 273 and 350 ft (350 taken), on at most 2 and 3 buildings (3 taken: 12 walls), the longest wall 63 ft; at most 21 and 29 standing things (parts, way segments, crowns, stands) in one 64 ft cell about the houses (29 taken); 1 ft a pixel at the hamlet scale. The typical densities (rubric S8; `items.md`, measured 2026-10-28 on the same reference manifests at 10 and 20, each the mean over the cells occupied or crossed): things of every kind 3.4 and 3.3 an occupied 64 ft cell (4.5 and 5.5 within 3 cells of a house); homestead parts 2.8 and 2.6 an occupied 64 ft cell; water segments 4.1 and 3.7, ways' legs 1.3 and 1.9, the field's outline segments 2.1 and 1.8, and marsh segments 4.4 and 3.8 a crossed 64 ft cell; site-boundary segments 2.6 and 2.4 a crossed 32 ft cell; each held flat past 20, a mean over occupied cells not rising with the households as the densest cell does.

## The algorithm

    the count asked: the share of the households, rounded
    for each household in the seat order while sties are owed:
        if it keeps one (or one was passed to it): its places along each wall, 4 ft apart from each end, 99 at most
            for each wall: the things in the cells its 15 ft strip touches (the farm's grove band among them), each projected
                on the wall's axis as the interval of places where the sty's box would meet it - a thing is convex, so its
                blocked places are one interval - marked by its two ends in a difference array over the household's places
            one prefix sum over the places: the first unblocked place is the sty (the same place the rule's in-order test finds)
        drawn: recorded and filed in the registry's cells; none admitted: passed to the next household that keeps none
    record the count asked and the count short

## Indexes

- registry: cells of 64 ft; densest 29 standing things a cell (measured at 10 and 20 about the houses, 21 and 29, the ceiling taken: a Bound the audit at 40 and 80 confirms or refutes), from a smallest side of 64 ft against the sty's box of 15 by 13 ft (8 by 6 ft with its 3.5 ft gap each side), so a place lies in at most 2 by 2 cells

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 15 at 20, 33 at 40, 69 at 80 | the households that keep a sty, the share's count (7 of 10 and 15 of 20 measured; a passed sty goes to the next that keeps none, within the slack) | 80 households |
| the strips' cells (registry cells examined) | per item | 90 | the typical household's sty finds its place on its first wall or two (S8: the places the search order reaches): 2 walls' strips, each in at most 3 by 3 cells, read with the mean 4 things a cell near the houses and the cell (5) | the typical farmstead |
| the intervals (things projected) | per item | 216 | each of those 2 x 9 cells' mean 4 things projected (1) and its interval's two ends marked (2) | the typical farmstead |
| the places (places set and walked) | per item | 16 | the 2 walls' at most 8 places each, set and walked | the typical farmstead |
| the grove band and the rake (intervals marked) | per item | 20 | the farm's band projected on the 2 walls (4) and the rake's 2 walls turned (16) | always 20 |
| slack | per item | 2 | what varies around the typical case (S8): a third wall reached, a sty passed on | a crowded farmstead |
| the drawing (registry cells written) | over the run | 15 x 5 at 20, 33 x 5 at 40, 69 x 5 at 80 | each sty recorded (1) and filed in at most 4 cells (4) | the share's count drawn |
| the count | once | 1 | the share of the households, rounded | always 1 |

So: the sty households x (342) x 2, plus the drawing and the count.

## Totals

- at 20: 15 x (90 + 216 + 16 + 20) x 2 + 15 x 5 + 1 = 10336
- at 40: 33 x (90 + 216 + 16 + 20) x 2 + 33 x 5 + 1 = 22738
- at 80: 69 x (90 + 216 + 16 + 20) x 2 + 69 x 5 + 1 = 47542

## Earlier findings

- verdict-1, finding 1: fixed - a sweep per wall: the strip's things marked as intervals in a difference array and the places walked once; no sort, since the places are a fixed 4 ft lattice
- verdict-1, finding 2: fixed - the walls are bounded, 3 buildings measured, 12 walls
- verdict-1, finding 3: disputed - the cell density of 29 is a measured Bound, as the contract states it; it has no geometric ceiling (crowns and parts differ in size), so the audit at 40 and 80 is where it holds or fails
- verdict-2, finding 1: fixed - each strip carries the box's 15 ft overhang, and a raked wall's strip is bounded by its square, 3 by 3 cells a wall, 108
- verdict-2, finding 2: fixed - the grove band is projected on each wall apart from the registry, at most two intervals a wall
- verdict-2, finding 3: fixed - 99 places, both ends of each wall, and the difference array's setup is a row
- FR-014 re-score: each factor at the typical case (rubric S8): the households that keep a sty, each finding its place on its first wall or two, at the mean 4 things a cell near the houses (`items.md`); slack 2 (ask:444-budget-standard; the accept was ask:444-T03-sties-round-3)

## Cheaper algorithms considered

- sweep: used - along each wall, the strip's things marked once as intervals and the places walked once, in place of testing every thing at every place
- grid or spatial index: used - the registry's 64 ft cells bound each place's neighbors
- priority queue: not used - the places are taken in their order along the walls, not ranked
- incremental update: used - each sty is filed as it is drawn, for the next household's places
- memoizing what a scan does not change: used - nothing is filed while a household is scanned, so each strip's things are read once for all its places
