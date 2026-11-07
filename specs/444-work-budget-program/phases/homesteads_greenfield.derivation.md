# Derivation - homesteads, greenfield (feature 444 FR-015; re-derived for the whole stage under FR-022 rule 2, 2026-11-04)

## Contract

- Reads: the plan's seat - the cluster's center and anchor on the field's dry margin, its axis, its band's two half-extents and the ladder of margins after it - and the households, the settlement's form and the cluster's shape, the family, byre and fixture forms; the field's outline; the no-build ground standing (the dry plots, the wet ground, the wet toe below the fields, the ponds, the marshes); every watercourse with its width (the brook gapped at its fords, the ditches, the drawn channels); the registered corridors; the canvas.
- Writes: each household's homestead on its own ground - the house, its threshing yard, its kitchen beds, its fixtures (the privy, the manure heap, the coop, the bath, the woodpile, the household shrine, the persimmon), its storehouse or shed and its byre where it keeps one, a retirement house where the household has one, and its stand of wood - every part filed in the registry and drawn; the track out of the cluster, chosen once the last house stands, and each household's way laid in the gaps between the homesteads to the track or to a way already laid, recorded as the access corridors; the cluster's declared shape; the seating's measures.
- Keeps: every declared household seated, or the site refused (0001); houses before lanes - no way stands or is reserved while a house is seated (0246: "every household seated while no lane stands on the map"); a household of a clustered settlement spread once seated over about 162 ft a side with its stand of wood (0285); the cluster grown irregularly from its first house nearest the seat (0031), the next house nearest a standing one, the field the tie-break (0029); no house refused for its distance from the fields (0032); the threshing yard and the kitchen beds keep 39 ft clear to their south of any house and 50 ft west of any tree (0038); a farmhouse on the size ladder of 0029, the storehouse to one farm in eight (0040), the byre by the byre form (0048), the fixtures by their quota (0028, 0044, 0046, 0047), the homestead's wood at least 6,000 sq ft within 90 ft of the house (0036); no house on the wet toe (0058); a farmstead on one bank of the brook (0035); each household's way laid in the gaps between plots, joining a way within 25 ft, its treads 3 ft off a wall, held to the lane law's rules a way asks (0081, 0246); every rule asked of a seat before the house is drawn (S4); no house taken back.
- Bounds (measured 2026-11-04 on the reference rolls, seeds 4, 25, 39, 47, the mean; the seating's own record `meta.seat_search` and the stage's outputs, `make stage-sizes STAGE=track DUMP=`, and its inputs, `make stage-sizes STAGE=homesteads`): the houses 20, 40 and 80; the seats offered by the growth 152, 242 and 522; the positions tried 538, 694 and 1,673 (the offered seats and the moves off a neighbor); the rectangles tested 877, 1,261 and 3,165; the part layouts asked of the parts' rules 237, 406 and 868; the wood shares asked 70, 123 and 253 (a layout that reaches the wood), the lattice seats they tested 3,769, 5,947 and 12,230 (about 48 a share; `meta.seat_search.wood_tested`, recorded 2026-11-04); the fixtures 91, 180 and 359 (about 4.5 a household); the wood seats kept 434, 874 and 1,742 (about 22 a household); the access corridors 50, 96 and 207 legs of 2 points, their length 5,329, 9,926 and 20,896 ft (about 260 ft a household); the track out 2 to 4 points; the cluster's extent 1,361 by 707, 1,797 by 1,253 and 2,317 by 1,662 ft; the dry plots 94, 150 and 249 of 4 points, about 91 by 72 ft; the field's outline 68, 96 and 135 points across 1,263, 1,786 and 2,526 ft; the watercourses 454, 592 and 781 segments, about 60 ft long, their keep-out about 16 ft across (the drawn half-width and 5 ft each side); the canvas 6,400, 8,900 and 12,550 ft square.

## The algorithm

    the seating's window: a square about the seat's center, 2 x 162 ft x sqrt(households / pi) each side of it - the ground the
      households' 162 ft squares fill, twice over
    the free ground painted once over the window, 8 ft cells: the raster cleared; each ring of the no-build ground and the field's
      outline stepped through the rows its edges span and the spans between filled; each watercourse's keep-out strip painted
    the reach labeled once: the free cells joined to the way out's anchor, 4-connected, by a two-pass labeling (no way stands and
      no house is painted while the houses are seated, so the reach does not change while they are)
    the households seated by the settlement's form - the nucleated cluster grown from its first house (the dispersed hamlet's front
      row along the paddy's chords and its ranks behind, and the row village along its streets, offer their seats from their own
      lines into the same tests):
      the first house offered the free ground nearest the seat's center; each next house offered from a standing one, in a ring of
        directions round it at the distance the two homesteads' footprints part, jittered by the standing house's position, wider
        rings while households are left; the offers in a queue keyed on their distance to the seat, the field the tie-break
      each offered seat: up to 4 positions - the seat and its moves off one overlapping neighbor - each laying the homestead's four
        garden-side layouts from its size's template (9 parts turned), their union and each layout's own box tested against the
        raster at 9 points and the standing homesteads' boxes in a 64 ft grid
      a layout that clears: its parts' rules - the yard's and the beds' south sun against the standing houses, the yard opening onto
        the reach, every part off the field and the water, the beds off every ditch, each part admitted by the registry, the house
        then its fixtures stepped out from the house's walls, and its wood share: the lattice within its reach sorted behind the house
        first, each seat tested against the bars and the homestead's parts and kept where its own lattice square is fresh, until the
        squares kept cover 6,000 sq ft
      the layout with the least shaded garden kept; its parts written and filed; no house taken back
    the track out: from the cluster's gateway, straight runs off the canvas in 128 ft steps, each step's 3 x 3 cells of the
      homesteads and the water read, until one is clear
    the households' ways: the lane ground over the cluster's box and 160 ft round it, the free-ground raster's own 8 ft cells, the
      homesteads' boxes painted; one flood from the track, a bucket queue on each step's weight (1, and 3 more for the share of
      blocked cells within three cells); each household's way traced down the flood from its door, pulled taut and each leg held to
      the lane law's rules the way asks (the fixtures and parts clear, a lawful leg, the tree admitting it), the first admitted of
      its exits kept and filed as corridors
    written: each homestead's records and its ink, the corridors, the track, the shape declared

## The knobs the count reads

- the seating's window: 2 x 162 ft x sqrt(households / pi) each side of the seat (0285's ground, twice: NONE, a window's breadth)
- the free ground's cell: 8 ft (NONE: a raster's grain, under half the 18 ft narrowest gap a homestead leaves)
- the lane grid: the free ground's own 8 ft cells (a GUESS: two cells to the 18 ft narrowest gap a way takes, 0081), over the cluster's box and 160 ft round it (NONE: the breadth a way may swing out)
- the flood's weights: 1 a step and 3 more for the blocked share within three cells (a GUESS), quantized to a tenth for the bucket queue (NONE)
- the growth: 8, 12 and 16 directions on rings of 1 to 2 footprints, jittered 12 degrees and 12% (GUESS); the queue's ring 20 ft (GUESS)
- the positions: the offered seat and one computed move off a single overlapping neighbor, 4 at most (NONE)
- the layouts: the four garden sides (0038), 9 parts each (the house, the yard, 2 beds, 4 fixtures and a shed or byre, 0028-0048)
- the wood share: the lattice at 11 x sqrt(2), about 15.6 ft, within 90 ft (0036: the reach), about 105 points; each crown 22 ft across (0036), which covers its own 15.6 ft lattice square (its half-diagonal 11 ft), so a seat's ground is counted as its square, 242 sq ft (a GUESS: the crowns drawn reach past their squares, so the floor counted by squares is at least the floor drawn); 6,000 sq ft (0036), about 25 squares; the seats a share tests about 55, the measured 48 a share scaled by the 25 squares against the 22 crowns kept
- the fixtures: about 3 steps of 8 ft out from a wall before a seat clears (a GUESS, `WALL_GAP` 3.5 ft and 8 ft steps)
- the registry's and the homesteads' grid: 64 ft cells (NONE)
- the track's runs: 16, every 22.5 degrees, in 128 ft steps (NONE: a search's breadth)
- the way's exits: the first of up to 6 admitted, priced at its first, each its 3 joins (25 ft near, 45 ft far, and on to the way out: GUESS, 0081), each run pulled taut to at most 12 legs (0081), 2.4 on the mean (the corridors measured)

## Indexes

- the free ground: cells of 8 ft over the window, 41,720, 83,520 and 167,080 cells at 20, 40 and 80 (the window 1,634, 2,312 and 3,270 ft a side); a rectangle read at its 9 points; densest case from a smallest side of 8 ft, a cell under three keep-outs
- the reach: cells of 8 ft, the free ground's own, each labeled once; densest case from a smallest side of 8 ft, a cell where two free pieces meet
- the homesteads' boxes and the registry: cells of 64 ft, each box filed in the cells it covers (about 2), a box asked of its about 4 cells and the about 2 boxes they hold; densest case from a smallest side of 64 ft, a cell where four homesteads meet
- the lane ground: cells of 8 ft over the cluster's box and 160 ft round it, 26,975, 52,033 and 81,664 cells (1,681 by 1,027, 2,117 by 1,573 and 2,637 by 1,982 ft); densest case from a smallest side of 8 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | the households, each seated | every declared household |
| the fixtures | per item | 216 | about 4.5 fixtures (measured), each about 3 steps out from its wall, each step its box against the house's parts (9) and the registry (7) | a fixture stepped its 24 steps |
| the growth's queue | per item | 192 | each standing house's ring of 8 directions on up to 3 rings pushed (24) and popped, each a heap of about 200 (8) | the widest ring, 16 directions on 3 rings |
| the household's way | per item | 451 | its 3 joins traced down the flood from its door - the near join's 25 ft (3 cells), the far join's 45 ft (6) and the run on to the way, about 260 ft (33, measured) - each cell its 8 neighbors read (336); each run pulled taut and held to the lane law's rules leg by leg, 2.4 legs (measured), each leg's about 2.7 cells of the 64 ft registry (about 108 ft long) read with their about 5 items (16): 3 x 2.4 x 16 = 115 | its 6 exits all refused but the last, 12 legs a run |
| the records and the reserve | per item | 86 | its 9 parts each written (4) and filed (4), and its about 2.4 corridor legs written (2) and filed (4) | always its parts |
| the ink | per item | 356 | its 9 parts drawn, each its corners and its fill (20), and its about 22 wood seats, each its crown's 8 points | always its parts |
| the positions tried | over the run | 88,232 at 20, 113,816 at 40, 274,372 at 80 | 538, 694 and 1,673 positions (measured), each 4 layouts of 9 parts turned from the template (4 x 9 x 4 corners = 144), their union's 9 raster points (9) and the homesteads' grid round it (11): 164 | a seat moved off a neighbor at every offer |
| the wood shares | over the run | 147,700 at 20, 258,475 at 40, 532,775 at 80 | 70, 123 and 253 shares asked (measured), each its lattice's about 105 points sorted behind the house first (735) and its about 55 seats tested (the knob), each against the bars in its 64 ft cells (11), the homestead's own 9 parts (9) and its lattice square's 4 neighbors' and its own freshness (5): 735 + 55 x 25 = 2,110 | a homestead walled by its neighbors, the whole lattice tested |
| the rectangles: the free ground's points and the homesteads' boxes and the registry's cells examined | over the run | 11,401 at 20, 16,393 at 40, 41,145 at 80 | 877, 1,261 and 3,165 rectangles (measured), each its 9 raster points and its 4 grid cells: 13 | as measured |
| the parts' rules | over the run | 46,926 at 20, 80,388 at 40, 171,864 at 80 | 237, 406 and 868 layouts asked (measured), each: the south sun of its yard and 2 beds against the standing houses (3 strips, 4 cells and their boxes: 20), their 50 ft west of any tree against the standing wood seats (3 strips, 4 cells and 2 seats: 18), the yard's touch of the reach (4, a summed-area table), its 9 parts off the field and the water (81, 9 raster points each), the beds off every ditch (12) and each part admitted by the registry (63, 4 cells and 3 records each): 198 | every layout reaching the registry |
| the free ground's cells painted | once | 92,710 at 20, 179,763 at 40, 352,120 at 80 | the window's cells cleared and filled (2 each: 83,440, 167,040, 334,160); the rings' edges through their rows - the dry plots' 4 points and about 18 rows each (2,068, 3,300, 5,478), the field's outline its points and the rows of its two sides across its breadth (384, 543, 767); the watercourses' strips, each segment's 60 by 16 ft over 64 sq ft cells (15: 6,818, 8,880, 11,715) | every ring inside the window |
| the reach's cells labeled | once | 125,160 at 20, 250,560 at 40, 501,240 at 80 | each window cell read with its west and north neighbors and labeled, then relabelled: 3 a cell | as always |
| the track's runs | once | 3,800 at 20, 5,320 at 40, 7,448 at 80 | 16 runs (the knob) of 25, 35 and 49 steps of 128 ft (half the canvas), each step its 3 x 3 cells (9) and about half an item (0.5) | sixteen runs walled |
| the lane ground's cells flooded | once | 269,750 at 20, 520,330 at 40, 816,640 at 80 | the lane ground's 26,975, 52,033 and 81,664 cells (the Indexes), each popped from the bucket queue (1), its 8 neighbors relaxed (8) and its blocked share read from a summed-area table (1): 10 | as always |
| slack | per item | 1 | every factor is a count of the stage's own inputs or the seating's own measured search | not applicable |

- reason above the reference: a household is one thing placed, and seating it is a search - its offers, their layouts and their rules, its stand of wood - with the map-wide rasters (the free ground, its reach and the lane ground) and the one flood its way is traced down shared over every household; about 36,900 a household at 40, of it about 23,800 the rasters and the flood and about 6,500 the wood (0036)

So: items x (216 + 192 + 451 + 86 + 356) x slack + the positions, the rectangles, the parts' rules and the wood shares over the run + each once term.

## Totals

- at 20: 20 x (216 + 192 + 451 + 86 + 356) x 1 + 88232 + 11401 + 46926 + 147700 + 92710 + 125160 + 3800 + 269750 = 811699
- at 40: 40 x (216 + 192 + 451 + 86 + 356) x 1 + 113816 + 16393 + 80388 + 258475 + 179763 + 250560 + 5320 + 520330 = 1477085
- at 80: 80 x (216 + 192 + 451 + 86 + 356) x 1 + 274372 + 41145 + 171864 + 532775 + 352120 + 501240 + 7448 + 816640 = 2801684

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.89 (811,699 to 2,801,684): the households and their search with the
households, the rasters with the window and the cluster's extent, which grow with the households' ground. No loop over a growing set runs
inside another: an offer reads the raster's cells and the grid's boxes near it, never every homestead; the reach is labeled once,
because nothing changes it while the houses are seated; the lane ground is flooded once from the track and each way traced down it,
never a search a household. The reach labeled on the ground alone holds while the houses are seated because no house is painted into it (0246) and the growth seats each house at the distance its homestead's footprint parts from its neighbor's - the envelope, the woodlot and the path out - so a gap a way can take runs past every door; a door the gap ways cannot reach is reached across its neighbor's yard, as the contract's pinch has it.

## Work the first derivation missed

Feature 444 FR-022 rule 2 (amendment 7, the GM 2026-11-03): the first count priced a lattice of 162 ft lots taken in ring order, each
house's parts written and its way in; the contract the stage keeps holds all of the following, none of which it priced:

- the free ground painted and the reach labeled - the seat refused on any ground the water, the crop, the wet or the no-build takes, and its yard opening onto ground a way can reach (0246, 0058)
- the growth - the cluster grown irregularly from its first house, each next one nearest a standing one (0031, 0029), where the lots' lattice drew a grid
- the parts' rules - the yard's and the beds' south sun (0038), the registry's admission of each part, the beds off the ditches, the house off a neighbor's tread (S4)
- the homestead's wood - at least 6,000 sq ft within 90 ft (0036)
- the fixtures stepped out from the walls (0028, 0044, 0046, 0047)
- the track out, chosen once the last house stands (0246)
- the households' ways laid in the gaps and held to the lane law (0081, 0246) - the first count's "way in" was 4 points written
- the ink and the records of every part

## Earlier findings

- verdict-1, finding 1: fixed - the slack 1.05, from the clear lots' measured 0.83 to 0.87; the lot's search per house one clear lot and 0.18 refused, 18
- verdict-1, finding 2: fixed - the view dropped; the lot asks the water index and the belt's band, both in the Reads
- verdict-1, finding 3: fixed - a clear lot on the field's margin reads the outline's segments in the cells it crosses, the third of the lots facing the field (1.8)
- verdict-1, finding 4: fixed - the Bounds' 11.45 are the ground record's keys; the parts drawn are 9.05, the storehouse among them as the 0.15 storehouse or shed
- verdict-1, finding 5: fixed - the way in's legs and the corridors filed in the registry (22)
- verdict-2, finding 1: fixed - the lots grown breadth-first from the anchor, never through a lot the outline crosses, so a lot inside the field is never reached (0 on either reference roll); p re-measured from the anchor, 0.59 and 0.69
- verdict-2, finding 2: fixed - a part's registry overlap 1.67 cells (43)
- verdict-2, finding 3: fixed - a clear lot's border cells read the water near a ditch or the brook, the third of the lots at 2 crossed cells (2.5)
- verdict-2, finding 4: fixed - the slack from the measured spread of the lots tried, 1.7 at 10 and 1.45 at 20: 1.15
- verdict-3, finding 1: fixed - a lot a water crosses reads all its cells before it is grown through (28.5), a lot the outline crosses stops at its first outline cell (10), each at its measured share of the refusals, 0.15 and 0.30 a house
- verdict-5, finding 1: fixed - the wood's seats tested measured on the manifest (`meta.seat_search.wood_tested`, about 48 a share over 70, 123 and 253 shares) and priced over the run, a seat judged at its own lattice square; the fabric's 16 a leg derived from the leg's length over the registry's cells; the tread test dropped, no way standing while a house is seated
- verdict-5, notes: the way's legs at the measured 2.4; the joins traced at their own lengths; the reason line's figures from the rows; the track's 16 runs kept as an upper figure (under 1%); the flood over every lane cell kept, each way traced down one flood (a search a door would repeat it); the records and ink at 9 parts and the wood
- verdict-6, finding 1: fixed - its SOUND stood on the wood priced a house; the wood repriced over the shares measured, and its notes answered below
- verdict-6, notes: the west-tree check priced (18 a layout); the window's twice and the 160 ft margin kept as knobs, each under S10's half; the candidates a house rise from 40 to 80 as the measured search does, the cluster's ring widening; the reach's invariant stated in Growth
- the re-derivation (2026-11-04): the lots' lattice replaced by the growth the contract keeps (0031), each lot's rows replaced by the offers' and the layouts' measured search; the findings above stand on the rows they answered, which this re-derivation drops
- verdict-7, finding 1: disputed - its SOUND judged each factor against the algorithm chosen, never the total's reasonableness; re-judged under S11 (the GM 2026-11-07)
- verdict-8, finding 1: disputed - the same: the second SOUND of the raise, re-judged under S11

## Cheaper algorithms considered

- sweep: used - the rings painted row by row through the raster
- grid or spatial index: used - the free-ground raster for every point a seat asks, the 64 ft grid of the homesteads' boxes, the lane ground's raster; the reach read from a summed-area table
- priority queue: used - the growth's offers in distance order; the flood's bucket queue on its quantized weights, in place of a heap's log a cell
- incremental update: not used for the reach - nothing changes it while the houses are seated, so it is labeled once
- memoizing what a scan does not change: used - one template of parts a house size, turned per seat; the flood once for every household's way
- pruning: an offer refused at its first raster point taken; a layout's rules cheapest first, the wood share last; a way's first admitted exit kept
