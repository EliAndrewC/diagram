# Derivation - sties (feature 444)

## Contract

- Reads: the households and their farmsteads (the house and its outbuildings, their walls); the hamlet's form (a dike-pond hamlet keeps no sty here); the share of households keeping a sty (`quota_carriers`, about two in three, 0049); the registry of what stands - every part, way, crossing, tree and stand placed before this stage; each farm's grove band (`grove_rules.fixture_on_band`).
- Writes: each sty, a farm fixture of kind `sty` drawn 8 by 6 ft (`STY_FT`), against a wall of its house or an outbuilding; `meta.sty_target` and `meta.sty_short`.
- Keeps: the share's count of households, each sty on its own household's plot against a wall (0049, 0029: raked with its house); clear of the plot's other parts by the 3.5 ft wall gap (`WALL_GAP_FT`), the places 4 ft apart along each wall (`WALL_SLIDE_FT`), both GUESSES; never on a grove band; the first place the registry admits; a household with no place passes its sty to the next that keeps none (a GUESS); every rule asked before the sty is drawn (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): households 10 and 20, each tried at most once; sties 7 and 15 (x2.14: 15 at 20, 33 at 40, 69 at 80); a farmstead's wall length, its house and outbuildings, at most 273 and 350 ft (350 taken); at most 21 and 29 standing things (parts, way segments, crowns, stands) in one 64 ft cell about the houses (29 taken); 1 ft a pixel at the hamlet scale.

## The algorithm

    the count asked: the share of the households, rounded
    for each household in the seat order while sties are owed:
        if it keeps one (or one was passed to it): the places along each wall of its house and outbuildings, 4 ft apart
            for each place, in order: the sty's box with its 3.5 ft gap, raked with the house, against the registry's things in
                its cells; the farm's grove band (1); the first admitted is the sty
        drawn: recorded and filed in the registry's cells; none admitted: passed to the next household that keeps none
    record the count asked and the count short

## Indexes

- registry: cells of 64 ft; densest 29 standing things a cell (measured at 10 and 20 about the houses, 21 and 29, the ceiling taken), from a smallest side of 64 ft against the sty's box of 15 by 13 ft (8 by 6 ft with its 3.5 ft gap each side), so a place lies in at most 2 by 2 cells

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | the households tried, each at most once: a passed sty goes to the next household, never back | every household tried |
| the places | per item | 88 | a farmstead's walls, at most 350 ft, over the 4 ft slide, rounded up | the longest walls, every place refused |
| the place test (registry cells examined) | per item | 121 | the box's at most 2 by 2 cells, each read with its at most 29 things (4 x 30), and the grove band (1) | the densest cells |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the drawing (registry cells written) | over the run | 75 at 20, 165 at 40, 345 at 80 | each sty recorded (1) and filed in at most 4 cells (4) | the share's count drawn |
| the count | once | 1 | the share of the households, rounded | always 1 |

So: households x 88 x 121 x 1, plus the drawing and the count.

## Totals

- at 20: 20 x 88 x 121 x 1 + 75 + 1 = 213036
- at 40: 40 x 88 x 121 x 1 + 165 + 1 = 426086
- at 80: 80 x 88 x 121 x 1 + 345 + 1 = 852186

## Cheaper algorithms considered

- sweep: not used - the first admitted place along the walls is the rule; an interval sweep per wall sorts the same things the cells already bound, and saves no factor
- grid or spatial index: used - the registry's 64 ft cells bound each place's neighbors
- priority queue: not used - the places are taken in their order along the walls, not ranked
- incremental update: used - each sty is filed as it is drawn, for the next household's places
- memoizing what a scan does not change: not used - each household's places are its own walls, tested once
