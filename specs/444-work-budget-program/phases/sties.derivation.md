# Derivation - sties (feature 444)

## Contract

- Reads: the households and their farmsteads (the house and its outbuildings, their walls); the hamlet's form (a dike-pond hamlet keeps no sty here); the share of households keeping a sty (`quota_carriers`, about two in three, 0049); the registry of what stands - every part, way, crossing, tree and stand placed before this stage; each farm's grove band (`grove_rules.fixture_on_band`).
- Writes: each sty, a farm fixture of kind `sty` drawn 8 by 6 ft (`STY_FT`), against a wall of its house or an outbuilding; `meta.sty_target` and `meta.sty_short`.
- Keeps: the share's count of households, each sty on its own household's plot against a wall (0049, 0029: raked with its house); clear of the plot's other parts by the 3.5 ft wall gap (`WALL_GAP_FT`), the places 4 ft apart along each wall (`WALL_SLIDE_FT`), both GUESSES; never on a grove band; the first place the registry admits; a household with no place passes its sty to the next that keeps none (a GUESS); every rule asked before the sty is drawn (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): households 10 and 20, each tried at most once; sties 7 and 15 (x2.14: 15 at 20, 33 at 40, 69 at 80); a farmstead's wall length, its house and outbuildings, at most 273 and 350 ft (350 taken), on at most 2 and 3 buildings (3 taken: 12 walls), the longest wall 63 ft; at most 21 and 29 standing things (parts, way segments, crowns, stands) in one 64 ft cell about the houses (29 taken); 1 ft a pixel at the hamlet scale.

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
| items | per item | 20 at 20, 40 at 40, 80 at 80 | the households tried, each at most once: a passed sty goes to the next household, never back | every household tried |
| the strips' cells (registry cells examined) | per item | 3240 | 108 cells: each wall's strip, its length and the box's 15 ft overhang at each end by the box's 15 ft depth, at most 93 by 15 ft for the longest wall, 63 ft; raked with its house at any angle its bounding square is at most 93 / root 2 + 15 / root 2, 77 ft, a side, in at most 3 by 3 cells; 12 walls x 9; each cell read with its at most 29 things, 30 | the longest walls raked at 45 degrees, the densest cells |
| the intervals (things projected) | per item | 9396 | each of the at most 108 x 29 things in the strips projected (1) and its interval's two ends marked (2) | the densest cells |
| the grove band (intervals marked) | per item | 24 | the farm's band projected on each of the 12 walls, at most two intervals each, from `grove_rules.fixture_on_band`, not the registry; the band need not be convex | every wall meets the band |
| the difference array (places set) | per item | 99 | the household's places cleared before marking | always 99 |
| the prefix sum (places walked) | per item | 99 | one pass over the household's at most 99 places: each wall's length over 4 ft rounded down, plus 1, summed over 12 walls and 350 ft, 87 + 12 | every place blocked |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the drawing (registry cells written) | over the run | 75 at 20, 165 at 40, 345 at 80 | each sty recorded (1) and filed in at most 4 cells (4) | the share's count drawn |
| the count | once | 1 | the share of the households, rounded | always 1 |

So: households x (3240 + 9396 + 24 + 99 + 99) x 1, plus the drawing and the count.

## Totals

- at 20: 20 x (3240 + 9396 + 24 + 99 + 99) x 1 + 75 + 1 = 257236
- at 40: 40 x (3240 + 9396 + 24 + 99 + 99) x 1 + 165 + 1 = 514486
- at 80: 80 x (3240 + 9396 + 24 + 99 + 99) x 1 + 345 + 1 = 1028986

## Earlier findings

- verdict-1, finding 1: fixed - a sweep per wall: the strip's things marked as intervals in a difference array and the places walked once; no sort, since the places are a fixed 4 ft lattice
- verdict-1, finding 2: fixed - the walls are bounded, 3 buildings measured, 12 walls
- verdict-1, finding 3: disputed - the cell density of 29 is a measured Bound, as the contract states it; it has no geometric ceiling (crowns and parts differ in size), so the audit at 40 and 80 is where it holds or fails
- verdict-2, finding 1: fixed - each strip carries the box's 15 ft overhang, and a raked wall's strip is bounded by its square, 3 by 3 cells a wall, 108
- verdict-2, finding 2: fixed - the grove band is projected on each wall apart from the registry, at most two intervals a wall
- verdict-2, finding 3: fixed - 99 places, both ends of each wall, and the difference array's setup is a row

## Cheaper algorithms considered

- sweep: used - along each wall, the strip's things marked once as intervals and the places walked once, in place of testing every thing at every place
- grid or spatial index: used - the registry's 64 ft cells bound each place's neighbors
- priority queue: not used - the places are taken in their order along the walls, not ranked
- incremental update: used - each sty is filed as it is drawn, for the next household's places
- memoizing what a scan does not change: used - nothing is filed while a household is scanned, so each strip's things are read once for all its places
