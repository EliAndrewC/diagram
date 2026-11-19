# Derivation - the Mode A compound generator (feature 449 T208)

Written 2026-11-19 in the form of `.specify/templates/derivation.md`, to be judged against `docs/work-budget-rubric.md`. The
work is counted per thing the generator seats: each building, each door, each part (bath, wells, fire-water tubs, privies, the
notice board, the shrine tree, the practice ground's rack and posts) and the roji path. Mode A has no households, so the sizes
are the two generated pool sheets, one Totals line each.

**Provenance (blind to the code).** Read: the template, the rubric, the finished Mode A derivation
`specs/449-rust-codebase/derivations/T198-placer.md` (for its form only), `docs/buildings.md` whole,
`docs/building-programs.md` (the county magistrate's manor: its composition rules, required items and knobs), the building
types declaration (`types.json`, its magistracy entry and its `checks` list), the drawing pages of research 0090, 0091, 0115 and
0116, and those of the parts (0100 tubs, 0101 privies, 0196 wells, 0190 the notice board), which add no radius or count that
`docs/buildings.md` does not already state. The sizes come from the two sheets' SVG, their design notes, and the program
`ochiba-roundtrip-test.gen.py` declares (its envelope, spine, and buildings with wall, order and size). Not read: the generator's
source in either language, its tests, any log, count or timing of it, the county example's program (it lives in the generator's
module, so it is unread), and the plan's sections on those modules. To meet the bundle's form I read the form checker under
`rust/gate` (the derivation's checks), not the generator. Disclosed: the two sheets' notes, and the comments of the round-trip's
pool generator file, carry remarks about how today's generator behaves (its tiers and second rank, where it seats an ell, a door-kind
building's tub seated only within reach of a door). The algorithm below is derived from the rules, not from those remarks.

**My own script.** Every figure below comes from the rules or from my own script over the SVG (kept outside the repository, at
`/tmp/t208/count.py`, `factors.py`, `tables.py`). It recovers each sheet's input as the sheet shows it, walks the pseudocode below
over it and counts each kind. Where a seat is needed it takes the seat the sheet draws, so each figure is the work to REACH that
seat by this derivation's search order. It is not the project's generator and never ran it.

## Contract

- Sizes: pool sheets: county-magistracy-example, ochiba-roundtrip-test
- Scale: 3 px = 1 ft
- Reads: a compound program in feet - the envelope (width, depth, the divider's line), the reserved court spine (named zones:
  garden, hearing court, forecourt, practice ground, and on the county example its yards), the gate openings (the main gate's
  form and passage, posterns, side gates), each building (its court, its wall, its order and rank, its width and depth, an inset
  off the wall, an ell it joins, its rooms and bays as offsets, its doors as faces and fractions), and the parts the program owes
  (the type's required items); the knobs' seeds.
- Writes: each building's seat; its rooms, bays, stalls and bars as the program gives them; each door; each part's seat; the
  walls broken at their openings and the gate posts; the hearing court's posts and mats; the knob rolls (each well's gear and
  roof, the water depth); every drawn shape with its kind; each caption's declaration (its words, face, size and what it names).
  The caption placer (feature 449 T202) seats the captions afterwards, budgeted in `T198-placer.md`: one run a sheet, outside
  this budget.
- Keeps: the composition rules of `docs/buildings.md` ("Composition: perimeter buildings + a named court-spine") and the
  program of `docs/building-programs.md`, each asked of a candidate before it is placed (S4); the type declaration lists 14 checks of a finished sheet, each restated below in words:
  - Office front, residence rear: two courts split by the divider, each building in its declared court (the two-court zoning check; 0090).
  - Buildings ring the edges, the court spine held open: the spine is filed before any building; each building hugs its wall,
    a foot or two clear of the wall's face (the perimeter-hugging and wall-clearance checks; 0116, 0092).
  - Perimeter-first in tiers: N/S rows (they own the corners), then E/W columns flowing below them, then the divider hall
    centered between the columns; within a tier highest order, then largest, first; slide along the wall to the first free span,
    fire gaps of 6-8 ft between wooden buildings and 6-10 ft at a kura (0116's drawing page; the tier order a GUESS of the docs).
  - The second rank: a store may stand behind its wall's rank-1 row; servants never (0115, 0091).
  - Coverage 30-42% of the walled ground (the coverage check; 0116); each size inside its band of the types declaration; the size
    hierarchy of the checklist's sweep (office hall, residence, rowhouse; residence the largest domestic building; stable and
    cell under the barracks; stores under the rowhouse).
  - No unnamed open void: every large open region is a named zone (0116); a cart route runs from the gates to the granary and the
    stables (the program's composition rules).
  - Nothing in a gateway (the passage check): each gate's passage and a held approach are filed before any building; a
    postern's approach stays clear (the postern-approach check); the middle gate stands behind the office hall (0090's GUESS).
  - Doors: each set wholly inside its building on the wall it opens through (the door check; 0117); every lodging has one.
  - Wells by use: the kitchen's past the bath within 20 ft of the kitchen, the garden's in the garden, the stables' just outside
    them (GUESSES, 0105, 0196); each well's gear and roof rolled from the sheet's seed.
  - Fire-water tubs (five checks: a tub against a building, by a door, at each wooden building, clear of every footprint, off
    every well; 0100): one at each wooden building, two at the kitchen, none at the plaster kura; each beside a door of its
    building, within 10.5 ft, against its wall about 0.7 ft off, clear of the footprint, of the door's approach and of any well;
    round the nearer corner where the door's face has no room.
  - Privies (the privies-by-zone check; 0101): the house's two attached (the guests' behind the reception, the family's at a back
    corner), the rest one to a zone against a service wall near a gate, each at least 15 ft from any well.
  - The notice board within about 15 ft of a gate (the board check; 0090, 0190).
  - One compound shrine (the one-shrine check), in a corner beside one tree, a crown about 20 ft across, its trunk within 15 ft
    of the hall (the shrine-tree check; 0218).
  - The stable's stalls one ken wide (the stall check; 0108), written from the program.
  - The kitchen garden only where it gets its six hours of sun (the garden-sun check; 0109, 0038).
- Bounds (measured 2026-11-19 by my script on the two sheets' SVG, lengths in ft; each compound inside 0090's range, from the
  Joge post's ~230 x 89 ft to Takayama's ~105,600 sq ft):

| sheet | envelope (ft) | zones Z | gates G | buildings (N, S, W, E, divider) + ell | doors D | parts P | drawn shapes | caption declarations | free rectangles |
|---|---|---|---|---|---|---|---|---|---|
| county-magistracy-example | 270 x 200, divider at 90 | 9 | 4 | 14 (3, 4, 2, 2, 3) + 1 | 26 | 27 | 184 | 50 | 52 |
| ochiba-roundtrip-test | 267 x 200, divider at 100 | 4 | 2 | 16 (3, 3, 3, 5, 2) + 1 | 20 | 28 | 159 | 46 | 69 |

  The parts are, on each sheet, the bath 1, wells 3, tubs 13 and 14, privies 5, the notice board 1, the shrine tree 1, the
  weapon rack 1 and striking posts 2. The county example adds a roji of 12 stepping stones and a kitchen garden. Neither sheet
  has a rank-2 building or an overflow. The round-trip's walls and orders are its program's. The county example's are read off
  its sheet (assumption 1).

## The algorithm

    once: the grid over the envelope (cells of 40 ft)
          each spine zone: asked of the grid (inside its court, clear of the zones filed before it); filed
          each gate opening in the compound wall (the main gate in the south wall, posterns, side gates): its passage and a
          held approach 12 ft deep filed
    the tiers: N/S rows, E/W columns, the divider; within a tier highest order, then largest; a rank-2 store after its wall's row
    for each building in tier order:
        its band: the strip along its wall from the wall's face (plus its inset, 1.5 ft clear of the face) to its own depth
        its wall's row: the intervals of the buildings already seated against that wall's face, sorted, each grown by its fire gap
          (side by side, or 6-8 ft for wood and 6-10 ft at a kura); each touches the face, so each blocks every later band on the
          wall whatever its depth (a building set in off the face is an obstacle in the grid, not in the row): the search resumes
          at the row's first gap long enough for the building (with its ell's length where it has one), never re-reading the
          filled stretch
        from there (the divider tier from its middle, both ways together), advance one cell column (40 ft) a chunk:
          the chunk's strip asked of the grid; each new obstacle found gives its interval along the wall, grown by its gap;
          the new intervals sorted and merged; the first free span at least the building's length read off directly;
          stop at the first chunk holding one
        seat it; check its size band (w, h), its court, its wall-hugging, add its area to the coverage; file it; where it
          touches the face, insert its interval into its wall's row
        the house's ell: its two ends, the near one first, one grid query each; checked and filed
        the office hall seated: the middle gate fixed behind it, its held approach filed
        no span on the wall: overflow (0 on these sheets; priced in assumption 9)
    each door: its seat from the program's face and fraction (a dwelling's door at its bay's middle), O(1); its mouth and a step
        before it asked of the grid (no other building, no other door's approach); checked on its wall; filed
    the open ground, per court: a sweep over the buildings' x-edges; each slab's free y-intervals; neighbouring slabs' intervals
        joined: every large free region lies in a named zone, and a walk over the free regions reaches the granary's and the
        stables' doors from a gate (the cart route); a failure refuses the program, nothing is moved
    which buildings take a tub (wooden; the kura none; the kitchen two) and which zones owe a privy: one decision a building
    each part, by its rule against its anchor, one face strip asked of the grid per face tried, its faces in rank order
        (the strip runs the part's reach along the face; each obstacle found gives its interval; the first free span is read off):
        the bath on the kitchen's service side; the wells (the kitchen's within 20 ft past the bath, the garden's, the stables');
        the tubs (the door's face first, else round the nearer corner; circles, so each obstacle met is tested exactly);
        the privies (the house's two behind the reception and at a back corner; the others against a service wall by a gate;
        the strip grown by 15 ft finds any well); the notice board within 15 ft of the main gate; the shrine tree (a circle);
        the rack flush to its wall; the posts in the practice ground;
        each: its distance rule checked; filed
    the kitchen garden (where drawn): the ground about 20 ft south of it asked once (its six hours of sun)
    the roji (the no-genkan form): its stones on one line from the middle gate to the shoe stone, the line's box asked once
    once: the hierarchy pairs of the size sweep (12); the knob rolls (6, and each well's gear and roof)
    write every drawn shape, and each caption's declaration; the caption placer seats the captions (one run a sheet, T198)

Nothing is placed and then moved (S4). Each building, door and part is seated once, every rule is asked before it is placed, and
a program whose composition cannot hold is refused, not repaired.

## Indexes

- Placement grid: cells of 40 ft (120 px), uniform over the envelope. Each spine zone, gate approach, building, door approach and
  part is filed by its box in every cell the box overlaps, as it is seated. A query reads the cells its box overlaps, reads every
  entry in them, deduplicates with a visit stamp, and compares each entry's box with the query's. The cell is about one band deep
  (a building's depth, 12-45 ft), so a wall band reads one or two rows of cells. My script's total over the two sheets at each
  cell size, at slack 1: 15 ft 4,882; 20 ft 4,225; 30 ft 3,983; 40 ft 3,679; 60 ft 3,593; 90 ft 3,802; 120 ft 4,443; 200 ft 5,738.
  The minimum is at 60 ft, 2% under 40 ft, but a 60 ft cell is a fifth of the compound's width, so a query there reads a
  quarter of a court and its entries grow with the compound; 40 ft keeps them to a band's neighborhood.
- Cells a query reads: (1 + w / c)(1 + h / c) for the query's box, measured per sheet in the tables below: a building's band
  chunks read 4.62 to 5.93 cells a building, a door's approach 1.23 to 1.35, a part's face strip 1.48 to 1.54.
- Entries a cell holds: measured per sheet on the cells the queries read (S8: the mean the sheet shows) - building bands 1.25
  and 0.97, door approaches 2.59 and 2.59, part strips 3.88 and 3.65. Parts stand among buildings and doors, so their cells are
  the densest.

## The count, factor by factor

The pooled figure is in brackets. Each sheet's own figure is in the tables after this one.

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | N = 69, 65 (134): buildings 15, 17 (the ell included) + doors 26, 20 + parts 27, 28 + the roji 1, 0 | every building, door and part the program owes is seated once (S4) | 65 (round-trip) to 69 (county) |
| buildings seated by a wall span | per item | B = 14, 16 (the ell apart) | perimeter-first: each building against its declared wall, in tier order | 14 to 16 |
| span chunks | per building | 3.43, 2.12 [2.73] chunk queries | the first free span along the wall, from the wall row's first long-enough gap, one cell column (40 ft) a chunk, stopping at the first chunk holding a free span (S9) | 1 to 7 a building (the county shrine and granary, the round-trip karo's house: the divider tier searches both ways from its middle) |
| building band cells | per building | 5.93, 4.62 [5.23] | the band's cells, one or two rows deep at 40 ft | 1 to 14 a building (the county office hall and granary) |
| entries a grid cell holds (S1) | per cell | 1.25, 0.97 on building bands; 2.59, 2.59 on door approaches; 3.88, 3.65 on part strips | the sheet's own density where each step reads (S8) | 0.18 (round-trip zones) to 3.88 (county parts) |
| span intervals | per building | 1.43, 0.50 [0.93] | one interval per distinct obstacle the chunks found (zones, gate approaches, buildings on other walls) | 0 to 4 (the county cell) |
| span compares | per building | 6.07, 3.88 [4.90] | the row's scan to its first long-enough gap, the new intervals sorted and merged, the scan to the first free span, the row's sorted insert | 1 to 19 (the county cell) |
| building checks | per building | 5 (5.07, 5.06 with the middle gate fixed behind the hall) | size band w and h, court, wall-hugging, coverage area (the composition rules, each O(1)) | always 5 |
| building cells filed | per building | 3.21, 3.44 | each building filed in the cells its box overlaps | 1 to 9 (the round-trip residence) |
| the ell | per item | 1, 1: one grid query (2 and 4 cells, 5 and 4 entries), 5 checks, 2 and 4 cells filed | the kitchen is an ell of the house, at one of its two ends; the near end held on both sheets | the far end: one more query |
| door approach queries | per item | D = 26, 20: one query each, 1.23 and 1.35 cells, 3.19 and 3.50 entries, one check, 1.23 and 1.35 cells filed | 0117: a door's seat is the program's (face, fraction), O(1); its mouth asked clear and filed, so no tub or part later stands in it | 1 to 4 cells |
| part face queries | per item | 28, 29 over P = 27, 28 parts (1.04 a part) | each part by its rule against its anchor's face, its faces in rank order; a tub round the corner is a second face: 0 of 13 and 1 of 14 tubs | 1 face (most) to 2 |
| part strip cells | per query | 1.54, 1.48 | a part's strip runs its reach along one face (10.5 ft for a tub, 15 ft for a privy or the board, 20 ft for the kitchen well) | 1 to 4 |
| part intervals and compares | per query | 1.04 and 2.71, 0.97 and 2.31 | the obstacles met along the face, sorted and scanned to the first free span | 0 to 4 obstacles |
| part exact tests | per item | 21, 19 | a tub, a post or the tree is a circle: each obstacle box it meets is tested exactly (the GM's rule: no part of the glyph in a footprint) | one a circle's obstacle |
| part checks and cells filed | per item | 55 and 31, 56 and 33 | each part's distance rule and its seat checked (2 a part); filed in its cells | 1 to 2 cells a part |
| the roji | once | 1 query (4 cells, 9 entries) + 12 stone seats, county only | 0104's no-genkan form: the stones on one line from the middle gate to the shoe stone | 0 on the round-trip (no roji) |
| kitchen garden sun | once | 1 query (inside the parts' figures), county only | the six hours of sun (0109): the ground about 20 ft south of it asked for shade | 0 on the round-trip |
| spine zones filed | once | Z = 9, 4: 9 and 4 queries (40 and 22 cells, 17 and 4 entries), 9 and 4 checks, 40 and 22 cells filed | the spine is reserved before any building (0116) | county's 9 include its yards (assumption 2) |
| gate approaches filed | once | G = 4, 2: 4 and 2 cells filed (the middle gate's after the office hall) | nothing stands in a gateway; the middle gate behind the hall | 1 cell each |
| open-ground sweep | once | 166, 178 sweep compares, over 52 and 69 free rectangles | no unnamed void (0116), and the cart route's ground, built once over the courts' buildings | grows with the buildings a court holds, n log n |
| cart route and void walk | once | 152, 203 adjacency edges | the cart route from the gates to the granary and the stables, and every free region named, walked once over the free rectangles | one visit a rectangle and edge |
| composition checks | once | 30, 32: 12 hierarchy pairs + one tub-and-privy decision a building (15, 17) + 3 zone privy counts | the checklist's size sweep; a tub at each wooden building; a privy to each zone; the coverage sum compared once | fixed |
| rolls | once | 12, 12: 6 knobs + gear and roof for each of 3 wells | 0196, 0093, 0098, 0102, 0218: each attested choice a knob rolled from the seed | 2 a well |
| writes | once | 184, 159 drawn shapes | every drawn shape with its kind, the walls broken at their openings, rooms, bays, stalls, posts, mats | one a shape |
| caption declarations | once | 50, 46 | each caption's words, face, size and what it names (its seat is the placer's) | one a declaration |
| caption placement | once | 0 here: one run of the placer a sheet, budgeted in `T198-placer.md` | Captions are placed last, on the finished sheet (0242) | not applicable |
| rank-2 and overflow | per item | 0 typical | no building on either sheet takes the second rank or overflows; priced in assumption 9 | not applicable |
| slack | per item, on the search kinds | 1.5 | the tier order and the start end, which no rule fixes past the docs' GUESS: my script's runs with the start end flipped and the in-tier order reversed spread the search kinds by 1.00x to 1.10x a sheet, like for like | not on the fixed kinds |

So, per sheet: the zones filed, plus the once terms, plus the fixed per-item work (checks and cells filed), plus 1.5 x the search
work (seats, chunk and grid queries, cells, entries, exact tests, intervals and compares) of the buildings, the ell, the doors,
the parts and the roji. The search kinds of the zone filing are not slackened: they do not vary with the order.

- pruning: a building's search starts at its wall row's first gap long enough for it and stops at the first chunk holding a free
  span (S9); no cell past that chunk is read. A part's search reads only its anchor's face strip at the part's reach, its faces
  in rank order, stopping at the first that holds a seat. The only passes over a whole set are the spine filing, the open-ground
  sweep and walk (once over each court's buildings, n log n), and the writes, each of which every drawn thing owes once.

## The factors on each sheet

Per building (the span search), per door and per part, from my script's walk of the pseudocode on each sheet's input:

| sheet | B | chunks | cells | entries | intervals | compares | search a building | checks | cells filed | fixed a building |
|---|---|---|---|---|---|---|---|---|---|---|
| county-magistracy-example | 14 | 3.43 | 5.93 | 7.43 | 1.43 | 6.07 | 25.29 | 5.07 | 3.21 | 8.29 |
| ochiba-roundtrip-test | 16 | 2.12 | 4.62 | 4.50 | 0.50 | 3.88 | 16.63 | 5.06 | 3.44 | 8.50 |

| sheet | D | cells a door | entries a door | search a door | fixed a door | P | face queries | cells a query | entries a query | exact | search a part | fixed a part |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| county-magistracy-example | 26 | 1.23 | 3.19 | 6.42 | 2.23 | 27 | 28 | 1.54 | 5.96 | 21 | 14.48 | 3.19 |
| ochiba-roundtrip-test | 20 | 1.35 | 3.50 | 6.85 | 2.35 | 28 | 29 | 1.48 | 5.41 | 19 | 13.29 | 3.18 |

The steps multiplied out (search kinds | fixed kinds):

| sheet | buildings | the ell | doors | parts | roji | search | fixed | zones filed | once |
|---|---|---|---|---|---|---|---|---|---|
| county-magistracy-example | 354 / 116 | 9 / 7 | 167 / 58 | 391 / 86 | 26 / 0 | 947 | 267 | 115 | 597 |
| ochiba-roundtrip-test | 266 / 136 | 10 / 9 | 137 / 47 | 372 / 89 | 0 / 0 | 785 | 281 | 56 | 631 |

The once column is the gate approaches filed (3, 1), the open-ground sweep (166, 178) and walk (152, 203), the composition
checks (30, 32), the rolls (12, 12), the writes (184, 159) and the caption declarations (50, 46).

The county sheet costs more a building because its order and walls are inferred (assumption 1) and it files ten zones to the
round-trip's four: its building bands meet more obstacles.

## Totals

Each line is zones filed + once + fixed + 1.5 x search, in the step table's figures. The half rounds to even.

- at county-magistracy-example: 115 + 597 + 267 + 1.5 x 947 = 2400
- at ochiba-roundtrip-test: 56 + 631 + 281 + 1.5 x 785 = 2146
- all sheets: 2400 + 2146 = 4546

That is about 34 operations a thing seated at the slack (4,546 over 134), about 27 at slack 1, far under the reference's 4,000
a thing placed: a compound's buildings stand on five walls, each seated by one span search, and every part by one face strip.

## The budget by counted kind

Each cell is the kind's count on the sheet, with the slack on the search kinds of the placement steps, rounded per cell.

| kind | county-magistracy-example | ochiba-roundtrip-test | both |
|---|---|---|---|
| seat | 120 | 99 | 219 |
| span_query | 72 | 51 | 123 |
| index_query | 93 | 79 | 172 |
| index_cell | 286 | 244 | 530 |
| index_entry | 569 | 458 | 1027 |
| exact_test | 32 | 28 | 60 |
| span_interval | 74 | 54 | 128 |
| span_compare | 242 | 194 | 436 |
| index_insert | 153 | 142 | 295 |
| rule_check | 196 | 198 | 394 |
| sweep_op | 166 | 178 | 344 |
| graph_edge | 152 | 203 | 355 |
| roll | 12 | 12 | 24 |
| write | 184 | 159 | 343 |
| decl_write | 50 | 46 | 96 |
| total | 2401 | 2145 | 4546 |

The column totals differ from the Totals lines by the per-cell rounding. The kinds, one counter each: `seat` a candidate seat built
(a building's, a door's, a part's face, a roji stone); `span_query` one chunk of a wall band; `index_query` one box asked of the
grid; `index_cell` one cell read; `index_entry` one entry read and its box compared; `exact_test` one circle tested against an
entry it met; `span_interval` one obstacle's interval along a wall or face; `span_compare` one comparison sorting, merging or
scanning intervals or a wall row; `index_insert` one cell written; `rule_check` one O(1) rule asked; `sweep_op` one comparison of
the open-ground sweep; `graph_edge` one adjacency or visit of the walk; `roll` one seeded draw; `write` one drawn shape emitted;
`decl_write` one caption declaration emitted.

## Growth

Per building the work is one band search: its cells are the band's (a fixed depth at 40 ft cells) out to the first free span,
and its entries are the band's neighbors at the sheet's density, neither growing with the compound. The wall row keeps the
filled stretch from being read again, so the k-th building on a wall does not pay for the k - 1 before it (S3). A door and a part
read one or two strips at their reach. The open-ground sweep is n log n in a court's buildings, once. So a compound twice the
buildings at the same density costs about twice as much (S6). The two sheets are close in size, so a log-log fit between them
says nothing about growth; the bound is per thing seated.

## How far over is "far over"

S10 applies: a rebuilt generator counting up to twice its sheet's line, the excess named and reasonable, is LEEWAY; past twice
a sheet's line or the sum, OVER. For scale, priced on my script over the same sheets:

- Starting each building's search at its wall's corner instead of the row's first long-enough gap: the building search 1.12x and
  1.20x here, growing with the square of the buildings on a wall.
- No grid: each query compares every entry filed so far (about 40 on average of 81 at the end on the county sheet) instead of its
  cells' 2 to 6, about 113 queries x 40 = 4,500 entry reads against 569, about 2.6x the sheet.
- A slide stepped a foot at a time with a 2-D overlap test at each step, in place of the span read off the intervals: tens of
  seats a building, each a grid query, about 4x the sheet and growing with the wall's length.

## Cheaper algorithms considered

- sweep: used. Along each wall the obstacles' intervals give the first free span exactly, with no stepped slide; the same along
  a part's face; and one slab sweep over each court's buildings gives the free ground for the void rule and the cart route.
- grid or spatial index: used. Uniform 40 ft cells, measured against 15 to 200 ft (Indexes). An R-tree is not used: about 80
  entries a sheet at 1 to 4 entries a cell read already bound each query.
- priority queue: not used. The tiers are a fixed order, a building's search stops at its first chunk with a free span, and a
  part ranks at most four faces, so a heap would be no cheaper than the scan.
- incremental update: used. Each wall's row of seated intervals is kept sorted and the next building on the wall resumes at its
  first long-enough gap; the grid is filed as things are seated, never rebuilt.
- memoizing what a scan does not change: used. The wall rows; each building's box, doors and faces read once for its parts; the
  free-ground decomposition built once and serving both the void rule and the cart route.

## Assumptions, and the ones least sure

Each assumption is labeled as in `research/` and names the rule it reads.

1. **The county example's walls and order (least sure).** Its program lives in the generator's module, unread blind. Each
   building's wall is read off the sheet as its nearest wall face, a corner building taking the wall its long side runs along,
   and the order within a tier is by size. Under that order only 4 of its 14 drawn seats are the first free span the search
   finds; 9 lie past an earlier one (7 to 248 ft) and one stands closer to its neighbor than the 6 ft gap. Each reach is priced
   to the drawn seat, an over-count of at most the extra chunks. On the round-trip, whose walls and orders are its program's,
   11 of 16 are the first free span; the servants' range and the granary lie 7 ft past it (about one fire gap); the barracks
   stands closer to a neighbor than 6 ft (0116 allows side by side); and the divider's two buildings are anchored elsewhere than
   the divider's middle (the office hall centered between the columns, 12 ft off it; the karo's house 67 ft), so their reach is
   counted from the middle out to the drawn seat. The check covers every tier, the span past the last obstacle, and whether the
   drawn seat is itself free.
2. **Which ground is reserved (least sure).** The county sheet draws 10 named grounds (garden, hearing court, practice ground,
   forecourt, an outer court strip, cart yard, rear yard, service yard, kitchen garden); all 9 are budgeted as the program's
   reserved zones. Filing only its spine (4) measures about 0.93x the sheet. The round-trip declares and draws 4.
3. **The work to the drawn seat.** No re-placement: each figure is the work this search order does to reach the seat the sheet
   draws. A program whose seats differ from the sheets' will read different bands, within the slack where its walls are as full.
4. **One face for most parts.** A tub's face is measured (beside its door's face, or round the corner: 0 of 13 and 1 of 14). Each
   other part is counted on its drawn face as the first ranked; a part whose first face is full costs one more face strip, about
   15 a part at these sheets' means.
5. **The open-ground term.** The void rule (0116) and the cart route (the program's composition rules) are taken as owed by the
   generator, about 13% and 18% of the sheets' totals. A generator that leaves both to the sheet audit saves them.
6. **Fire gaps and approaches.** The fire gap applies along the wall, between neighbors in a row: an interval grows by 6 ft
   (0116's "side by side, or about 6-8 ft apart" for wood, 6-10 ft at a kura, GUESSES there); in depth the band is the building's
   own, since the round-trip's storehouses stand 5.7 ft in front of the house in its rear strip. A gate's held approach is 12 ft
   deep (a GUESS of this derivation, about the passage's own scale). Neither moves the totals by more than a few percent.
7. **Writes.** One a drawn shape and one a caption declaration. The interactive page and the raster are later stages, not counted.
8. **Captions.** One run of the placer a sheet, budgeted in `T198-placer.md`, not counted here.
9. **Branches priced at 0 (S8).** No rank-2 building, overflow, second kami's own shrine, arch or second well round: each is absent
   from both sheets. A rank-2 store costs one more band search past the row (about 30 at these sheets' means); an overflow, a band
   along the whole wall (about 16 cells, 20 entries and their intervals, about 100); the audit should name either as the excess.
10. **Slack.** Its one source is the order and start end no rule fixes (the docs' tier order is itself a GUESS): reversing the
    in-tier order (against the base) and flipping the start ends (against the same search from the corner) spread the search
    kinds by 1.00x to 1.10x a sheet; 1.5 covers that and the county's inferred order (assumption 1) with room.
11. **No repair.** Nothing is placed and then moved or dropped, so the budget for moves and drops is 0 (S4).
