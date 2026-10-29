# Derivation - sties (feature 444)

## Contract

- Reads: the households and their farmsteads (the house and its outbuildings, their walls); the hamlet's form (a dike-pond hamlet keeps no sty here); the share of households keeping a sty (`quota_carriers`, about two in three, 0049); the registry of what stands - every part, way, crossing, tree and stand placed before this stage; each farm's grove band (`grove_rules.fixture_on_band`).
- Writes: each sty, a farm fixture of kind `sty` drawn 8 by 6 ft (`STY_FT`), against a wall of its house or an outbuilding; `meta.sty_target` and `meta.sty_short`.
- Keeps: the share's count of households, each sty on its own household's plot against a wall (0049, 0029: raked with its house); clear of the plot's other parts by the 3.5 ft wall gap (`WALL_GAP_FT`), the places 4 ft apart along each wall (`WALL_SLIDE_FT`), both GUESSES; never on a grove band; the first place the registry admits; a household with no place passes its sty to the next that keeps none (a GUESS); every rule asked before the sty is drawn (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): households 10 and 20, each tried at most once; sties 7 and 15 (x2.14: 15 at 20, 33 at 40, 69 at 80); a farmstead's wall length, its house and outbuildings, at most 273 and 350 ft (350 taken), on at most 2 and 3 buildings (3 taken: 12 walls), the longest wall 63 ft; at most 21 and 29 standing things (parts, way segments, crowns, stands) in one 64 ft cell about the houses (29 taken); 1 ft a pixel at the hamlet scale. The typical densities (rubric S8; `items.md`, measured 2026-10-28 on the same reference manifests at 10 and 20, each the mean over the cells occupied or crossed): things of every kind 3.4 and 3.3 an occupied 64 ft cell (4.5 and 5.5 within 3 cells of a house); homestead parts 2.8 and 2.6 an occupied 64 ft cell; water segments 4.1 and 3.7, ways' legs 1.3 and 1.9, the field's outline segments 2.1 and 1.8, and marsh segments 4.4 and 3.8 a crossed 64 ft cell; site-boundary segments 2.6 and 2.4 a crossed 32 ft cell; each held flat past 20, a mean over occupied cells not rising with the households as the densest cell does. The admission share (FR-014, measured 2026-10-28 on the reference manifests): of each house's 4 walls, 0.90 and 0.88 at 10 and 20 offer a place, 4 ft apart along the wall, where a sty's 8 by 6 ft box 3.5 ft off the wall is clear (0.88 taken), so a sty is placed at the 1 / 0.88 = 1.14th wall reached; the mean wall about 29 ft (350 ft over 12 walls), so 8 places a wall.

## The algorithm

    the count asked: the share of the households, rounded
    for each household in the seat order while sties are owed, if it keeps one (or one was passed to it): its walls in turn,
        each with its own difference array: the things in the cells its 15 ft strip touches (the farm's grove band among them),
        each projected on the wall's axis as the interval of places where the sty's box would meet it, marked by its two ends;
        a prefix sum over the wall's places; the first unblocked place is the sty, and the walk stops at that wall
    drawn: recorded and filed in the registry's cells; none admitted: passed to the next household that keeps none
    record the count asked and the count short

## Indexes

- registry: cells of 64 ft; densest 29 standing things a cell (measured at 10 and 20 about the houses, 21 and 29, the ceiling taken: a Bound the audit at 40 and 80 confirms or refutes), from a smallest side of 64 ft against the sty's box of 15 by 13 ft (8 by 6 ft with its 3.5 ft gap each side), so a place lies in at most 2 by 2 cells

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 15 at 20, 33 at 40, 69 at 80 | the households that keep a sty, the share's count (7 of 10 and 15 of 20 measured) | 80 households |
| the walls reached | per item | 1.14 | 1 / p, p = 0.88 the measured share of walls with a free place (S8); the walk stops at the first | the typical farmstead |
| the wall (registry cells examined) | per item | 70 | its strip, a 29 ft wall's 44 by 15 ft band, raked, in about 3 cells, read with the mean 4 things near the houses and the cell (15); each thing projected and its two ends marked (3 x 4 x 3, 36); its 8 places set and walked (16); the rake's turn (1); the grove band's projection (2) | the typical farmstead |
| slack | per item | 2 | what varies around the typical case (S8): a second wall reached, a sty passed on | a crowded farmstead |
| the drawing (registry cells written) | over the run | 15 x 3 at 20, 33 x 3 at 40, 69 x 3 at 80 | each sty recorded (1) and filed in its about 1.2 cells (2) | the share's count drawn |
| the count | once | 1 | the share of the households, rounded | always 1 |

So: the sty households x 1.14 walls x 70 x 2, plus the drawing and the count.

## Totals

- at 20: 15 x 1.14 x 70 x 2 + 15 x 3 + 1 = 2440
- at 40: 33 x 1.14 x 70 x 2 + 33 x 3 + 1 = 5367
- at 80: 69 x 1.14 x 70 x 2 + 69 x 3 + 1 = 11220

## Earlier findings

- verdict-3, finding 1: fixed - the walls reached are 1/p, p = 0.88 measured, with a difference array a wall and a stop at the first wall with a free place; a wall's strip in its mean 3 cells; the rake 1 a wall; the places set and walked counted twice (16)
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
