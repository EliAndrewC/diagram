# Derivation - waterward, the polder form, greenfield (feature 444 FR-015; a form at its bounded n, as the field's polder: the round arbiter's ruling on ask:444-polder-sizes)

The waterward stage's polder form - the reed fringe outside a polder's dike - written from its contract alone. The valley form's one test of the plan is `waterward_greenfield.derivation.md`'s.

## Contract

- Reads: the plan's settlement form and field archetype; on a polder, the dike's outline and its notches (the sluice cuts through its band), the band's widest, the fall and the side of the polder the seat chose; for drawing each strip, the polder's fields, the no-build ground standing, the dike's crest and every drawn watercourse (the streams, the channels and the drawn laterals), and the ways, the structures and the wells standing (none yet: the fringe is laid before the houses and the ways).
- Writes: a polder's waterward fringe - a reed strip outside its dike on each flank that faces the water it was reclaimed from (0019: "every flank of a polder but the landward one" holds water back; the reed fringe along the low foot where the outfall drains and along the cross flanks off the shore, the wild pond at the head, drawn as the pond), laid before the houses so they treat it as wet ground; each strip drawn as reed marsh - its corners rounded and edges waved (0074), cut to the open ground outside the dike and the fields, the ground its reeds keep off taken out (the paddy's edge, the no-build ground, the crest of the dike, the drawn water) - and recorded as the marsh, its ring the ground the reeds are drawn on, no-build ground for every later placer; the flanks declared. On any other form, nothing.
- Keeps: the strip at the dike's outer face, stepping in through a notch (0027: the band cut where a channel crosses); a strip held to the frame; the marsh's edge rounded and waved, never ruled (0074); no reed on the dike's crest or in the water, reeds to the water's edge and the paddy (0074, 0061); every marsh but a pond fringe no-build ground (0058).
- Bounds: a bounded n: households 10-20 (0019's GUESS: the ten to twenty households a small polder holds; the plan refuses a polder past them). Measured 2026-11-04 on polder rolls, the reference spec with its field form a polder grid, seeds 4, 25, 39, 47 (`make stage-sizes STAGE=waterward SIZES=10,20` and `STAGE=homesteads` with that form): the dike's outline 124 and 182 points at 10 and 20 households, its crest 120 and 178, its notches 2; the dike's extent 885 by 871 ft and 1,184 by 1,354 (the mean, across and along the fall); the water-facing flanks 3 at both sizes (both cross flanks and the foot); the drawn watercourses 65 and 116 points (the channels' 6 and the drawn laterals' 59 and 110); the polder's fields one ring of 4 points; no way, structure or well standing; each strip's drawn ring 131 and 178 points (393 and 534 over the three strips, the marshes recorded after the stage).

## The algorithm

    the plan's form read (1); not a polder: done
    the dike's outline and notches read; each notch filed to the flank whose face it stands nearest (4 tests)
    the flanks facing the water from the fall and the seat's side (3)
    for each water-facing flank:
      the face: the dike's points binned along the flank (32 bins), the outermost of each bin its face, stepped in through each
        notch the bin's middle stands near; a run of bins at one face its ends only; the strip run from the face out to its depth
        or the frame
      the strip's outline rounded (a closing at the rounding radius, two buffers) and waved: samples along its ring at the wave's
        step, each placed by a bisection of the ring, moved inward by four wave components along its normal, the waved ring cut
        to the rounded one and simplified
      cut to the open ground outside the dike and the fields
      the no-build ground read for the pond's cut (the earlier strips' rings, no pond on a polder)
      the drawn ground: the ring less every keep-out ring near it, each read for its box, the ones that reach it buffered and taken out
      the keep-out grid filed: the fields, the no-build rings, the dike's crest as segments, every drawn watercourse's segments;
        the ways and the urban halo read (none standing)
      the bare ground: the grid's cells under the strip's box read, their items handed back, each item's shape built and buffered
      the record written: the drawn ring at the record's grain, its box and its fields, its ring no-build
    the flanks declared

## The knobs the count reads

- the strip's depth: 280 ft out from the dike's face (a GUESS: no page gives a reed fringe's breadth; it outlasts any crop this tier makes), run 30 ft before the dike's start and 20 ft past its end (a GUESS)
- the face's bins: 32 along the flank (a GUESS, a search step)
- the rounding radius: 60 ft, the first tried, halved down to 5 ft until the rounded strip keeps 85% of its area (a strip 280 ft deep keeps all but its corners at the first, so one try); each buffer's arcs 8 points a corner
- the wave's step: 15 ft along the ring (a dozen samples to the shortest wave, 180 ft), four components (a lead, two slower and a short one), its ring simplified to 1 ft
- the keep-out grid's cell: 128 ft
- the bare ground's passes: each keep-out shape's vertices built, buffered and unioned a side, shrunk and grown (4)

## Indexes

- the keep-out grid: cells of 128 ft, each keep-out filed in the cells its box covers; a strip's box, 921 by 280 ft on a cross flank at 10 and 935 by 280 on the foot (the dike's extent and the 50 ft its runs pass it), covers (921 / 128 + 1) x (280 / 128 + 1) = 26 and 27 cells, 26 on the mean; at 20, 1,404 by 280 and 1,234 by 280, 38 and 34 cells (37); densest case from a smallest side of 128 ft, a cell where the crest, a lateral's mouth and a notch meet

No grid for the wave's samples: each is placed by a bisection of the ring's cumulative length, the rounded ring's 34 laid points and its four corners' arcs, about 7 steps.

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 3 | the water-facing flanks, measured: both cross flanks and the foot | 3, the village on the head's side; 2 where it stands on a cross flank |
| the face | per item | 188 at 10, 246 at 20 | the dike's 124 and 182 points binned (1 each), and each of the 32 bins asked of the 2 notches (64) | every notch on one flank |
| the strip written | per item | 34 | its two outer corners and a face point for each of the 32 bins | a face that changes at every bin |
| the rounding | per item | 544 | one try of two buffers, 8 arc points a corner over the strip's 34 points (2 x 8 x 34) | a narrow strip halved down to 5 ft, four tries |
| the clip to open ground | per item | 259 at 10, 364 at 20 | the shaped ring (131, 178) tested against the dike's outline (124, 182) and the field's 4 | the strip beside the whole dike |
| the drawn ground's own ring | per item | 135 at 10, 182 at 20 | the shaped ring read for its box (131, 178) and the field's 4 | as above |
| the keep-out grid filed | per item | 254 at 10, 414 at 20 | the field's 4, the crest's 120 and 178 points boxed and filed as segments, and the drawn water's 65 and 116 points read and filed (2 each) | a crest the length of the canvas |
| the keep-out grid's cells under the strip | per item | 26 at 10, 37 at 20 | the 128 ft cells under the strip's box (the Indexes) | as the Indexes |
| the bare ground's items | per item | 64 at 10, 100 at 20 | the items those cells hand back: a third of the crest's segments (40, 59) - one flank about a quarter of the dike's perimeter and the cells round its corners - a third of the water's (22, 39) - the laterals' mouths at the dike, an upper figure - the field and about one earlier strip | the foot's strip, which touches both cross flanks' |
| the bare ground's shapes | per item | 1,032 at 10, 1,512 at 20 | 4 passes over each vertex of those items: the crest's third (80, 118), the water's third (43, 78), the field's 4 and one earlier strip's ring (131, 178) | as above |
| the record written | per item | 143 at 10, 190 at 20 | the drawn ring rounded and written (131, 178), its box (4) and its record's fields (8) | always its ring |
| the ways and the halo | per item | 2 | the ways and the structures and wells read, none standing | a re-laid fringe after the houses, which the contract does not lay |
| the wave's samples | over the run | 8,194 at 10, 11,033 at 20 | each strip's ring over the 15 ft step - 2,402, 2,402 and 2,430 ft at 10 (160, 160, 162), 3,368, 3,368 and 3,028 at 20 (224, 224, 201) - 482 and 649 samples, each its bisection (7), its four components, its normal and its move (8) and its share of the cut and the simplify (2): 17 | a strip run to the frame on every side |
| the pond's cut | over the run | 393 at 10, 534 at 20 | the earlier strips' rings read for their boxes: none, one and two of them, three rings over the run | as measured |
| the drawn ground's keep-out rings | over the run | 393 at 10, 534 at 20 | the same three rings read for their boxes | as measured |
| the cuts buffered | over the run | 262 at 10, 356 at 20 | the two earlier rings that reach a later strip (the foot's corners against the cross flanks') buffered and taken out | every earlier ring reaching |
| the earlier strips indexed | over the run | 393 at 10, 534 at 20 | the same three rings' points indexed in the grid | as measured |
| the marsh's ring passes | over the run | 3,930 at 10, 5,340 at 20 | each strip's drawn ring (131, 178) rounded to the record's grain, copied to the wet ground, copied into its cover, scanned for the record's box (4), written to it and copied twice as no-build ground: 10 a point, three strips | always its ring |
| the outline's box | over the run | 393 at 10, 534 at 20 | each strip's shaped ring read once for its box | always its ring |
| the crest's scans | over the run | 1,800 at 10, 2,670 at 20 | the dike's crest (120, 178 points) read for its box against each strip's reach (4 scans) and copied (1): 5 a point, three strips | always the whole crest |
| the keep-out rings indexed, beyond their points | over the run | 1,533 at 10, 2,083 at 20 | each ring filed in the grid - the earlier strips', three over the run - copied and its edges built (2 a point), each edge in the rows its height spans and the cells its box covers in the ring's own 64 ft index (an edge of the shaped ring about 18 ft at 10 and 20 ft at 20, 1.3 rows and 1.6 cells): 4.9 a point less the 1 already priced - 3 x 131 x 3.9, 3 x 178 x 3.9 | a ring whose edges run along the rows |
| the grid's cells | over the run | 1,083 at 10, 1,875 at 20 | each item filed in every 128 ft cell its box covers, beyond the one priced: the crest's segments about 30 ft long (the dike's 3,512 and 5,076 ft perimeter over its points), 1.25 cells each (150, 223 a strip), the drawn water's segments as the grid takes them - the laterals split at their tapers, 98 and 197 points a strip - 1.25 each (123, 246), the field's ring over its box (62 and 119 cells) and an earlier strip's (26, 37); three strips | a crest segment across a cell corner |
| the face's extra passes | over the run | 744 at 10, 1,092 at 20 | each flank's face reads the dike's points twice more, for their coordinate along the flank and its extremes (2 a point, three flanks) | always the whole dike |
| the inputs read | once | 126 at 10, 184 at 20 | the dike's outline and its 2 notches | the typical dike |
| the notches filed | once | 8 | each of the 2 notches against the 4 flanks | always 8 |
| the form's test and the flanks | once | 1 | the plan's form read; the flanks from the fall and the seat in the same pass | always 1 |
| slack | per item | 1 | every factor is a count of the stage's own inputs | not applicable |

- reason above the reference: a strip is one thing laid, about 920 ft by 280 at 10 and 1,300 at 20, and drawing it is its whole outline waved at a 15 ft step and its bare ground built from every keep-out near it - not a cost per house or per mark placed

So: items x (the face + 34 + 544 + the clip + the drawn ground's own ring + the grid filed + the bare ground's cells, items and shapes + the record + 2) x slack + each over-the-run and once term.

## Totals

- at 10: 3 x (188 + 34 + 544 + 259 + 135 + 254 + 26 + 64 + 1032 + 143 + 2) x 1 + 8194 + 393 + 393 + 262 + 393 + 3930 + 393 + 1800 + 1533 + 1083 + 744 + 126 + 8 + 1 = 27296
- at 20: 3 x (246 + 34 + 544 + 364 + 182 + 414 + 37 + 100 + 1512 + 190 + 2) x 1 + 11033 + 534 + 534 + 356 + 534 + 5340 + 534 + 2670 + 2083 + 1875 + 1092 + 184 + 8 + 1 = 37653

## Growth

From 10 to 20 households the stage grows at an exponent of about 0.46 (27,296 to 37,653): the strips are three at both sizes, and each
grows with the dike - its outline, its crest and its extent - and the drawn water beside it. No loop over a growing set runs inside
another: the face bins the dike's points once a flank, the wave's samples each take a bisection, and the bare ground reads the grid's
cells under one strip's box, never every keep-out.

## Work the first derivation missed

Feature 444 FR-022 rule 2: the form's first budget (17,813 / 24,059 at 10 / 20, SOUND twice blind, verdicts 3 and 4) priced each of
the strip drawing's passes over a ring at 1 a point; the MODE AUDITs of 2026-11-04 (`phases/waterward.audit-2.txt`, `-3.txt`) found the
passes the drawing makes, each work the contract owes - the strip drawn as marsh, recorded, its ring no-build ground (0058), its reeds
kept off the crest (0074) and its bare ground built from the keep-outs near it:

- the marsh's ring passes - the drawn ring rounded, copied, boxed, written and filed as no-build ground
- the outline's box, read once
- the crest's scans against each strip's reach
- the keep-out rings indexed - their edges in their rows and cells, beyond the one a point priced
- the grid's cells - every item in each cell its box covers, beyond the one an item priced
- the face's extra passes over the dike's points

## Earlier findings

- verdict-1, finding 1: fixed - its SOUND judged this derivation priced at 20, 40 and 80, past the polder's bounded n; priced now at 10 and 20, its sizes, with its notes answered below
- verdict-2, finding 1: fixed - as verdict-1's
- verdicts 1-2, notes: the water's third is an upper figure, its reason stated (the laterals' mouths at the dike); the wave's samples by bisection - kept, see below; the grid filed again for each strip - each strip's grid holds the earlier strips' rings, which change between strips, and the crest and water are filed with them (about 4%); the earlier rings' boxes read from their points (about 4%); the whole dike binned on each flank (under 2%); the rounding's arcs at every vertex (about 3%); the grid row at 40 no longer owed
- waterward.audit-1, finding 1: fixed - the drawn ground, the pond's cut and the ground's readers counted and priced here; the stage measured on polder rolls, where it runs
- waterward.audit-1, notes: a strip with no open ground is never recorded and then removed - it is not drawn, a refusal after the Rust laid it, priced as a strip drawn; the sty's seat on a dike-pond is the dike-pond form's, which the polder grid's rolls do not run
- verdict-3, finding 1: fixed - its SOUND stood on each pass priced at 1 a point; the passes the audits found priced under `## Work the first derivation missed`
- verdict-4, finding 1: fixed - as verdict-3's
- verdicts 3-4, notes: answered under the rows - the wave's samples by bisection (kept: the shaping's own interpolation), the grid filed again a strip (it holds the earlier strips' rings), the earlier rings' boxes read from their points (one pass each now), the whole dike a flank (under 2%)
- waterward.audit-2, finding 1: fixed - the marsh's ring passes counted and priced; the outline's samples placed in one pass over the ring, its cumulative lengths taken once (the walk from the ring's start for each sample removed)
- waterward.audit-3, finding 1: fixed - the ring index's passes counted, its box found in its edge loop; the marsh's and the pond cut's boxes in one pass; the face's extra passes tallied; each priced above

## Cheaper algorithms considered

- sweep: used - the face bins the dike's points once a flank; not used for the wave's samples - a walk along the ring would place each in about one step where the bisection takes 7 (about 3,000 at 20, 12%, under S10's half), and the ring's samples are placed by the shaping's own interpolation, which this stage does not write
- grid or spatial index: used - the keep-out grid for the bare ground; the ring's cumulative length bisected for each wave sample, no grid
- priority queue: not used - nothing is ranked
- incremental update: not used - three strips, each drawn once
- memoizing what a scan does not change: used - the grid filed once a strip from what stands; the keep-outs beyond a strip's box skipped by their boxes
- pruning: a keep-out ring whose box misses the strip is read for its box and skipped, never buffered
