# Derivation - waterward, greenfield (feature 444 FR-015; revised under FR-022 rule 2, 2026-11-04)

## Contract

- Reads: the plan's settlement form and field archetype; on a polder, the dike's outline and its notches (the sluice cuts through its band), the band's widest, the fall and the side of the polder the seat chose; for drawing each strip, the polder's fields, the no-build ground standing, the dike's crest and every drawn watercourse (the streams, the channels and the drawn laterals), and the ways, the structures and the wells standing (none yet: the fringe is laid before the houses and the ways).
- Writes: a polder's waterward fringe - a reed strip outside its dike on each flank that faces the water it was reclaimed from (0019: "every flank of a polder but the landward one" holds water back; the reed fringe along the low foot where the outfall drains and along the cross flanks off the shore, the wild pond at the head, drawn as the pond), laid before the houses so they treat it as wet ground; each strip drawn as reed marsh - its corners rounded and edges waved (0074), cut to the open ground outside the dike and the fields, the ground its reeds keep off taken out (the paddy's edge, the no-build ground, the crest of the dike, the drawn water) - and recorded as the marsh, its ring the ground the reeds are drawn on, no-build ground for every later placer; the flanks declared. On any other form, nothing.
- Keeps: the strip at the dike's outer face, stepping in through a notch (0027: the band cut where a channel crosses); a strip held to the frame; the marsh's edge rounded and waved, never ruled (0074); no reed on the dike's crest or in the water, reeds to the water's edge and the paddy (0074, 0061); every marsh but a pond fringe no-build ground (0058).
- Bounds (measured 2026-11-04 on polder rolls, the reference spec with its field form a polder grid, seeds 4, 25, 39, 47, `make stage-sizes STAGE=waterward` and `STAGE=homesteads` with that form): the dike's outline 182, 240 and 342 points at 20, 40 and 80 households, its crest 178, 236 and 338, its notches 2; the dike's extent 1,184 by 1,354 ft, 1,580 by 1,740 and 2,373 by 2,320 (the mean, across and along the fall); the water-facing flanks 3 at every size (both cross flanks and the foot); the drawn watercourses 116, 196 and 396 points (the channels' 6 and the drawn laterals' 110, 190 and 390); the polder's fields one ring of 4 points; no way, structure or well standing; each strip's drawn ring 178, 220 and 296 points (534, 661 and 888 over the three strips, the marshes recorded after the stage).

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

- the keep-out grid: cells of 128 ft, each keep-out filed in the cells its box covers; a strip's box, 1,790 by 280 ft on a cross flank at 40 and 1,630 by 280 on the foot (the dike's extent and the runs past it), covers (1,790 / 128 + 1) x (280 / 128 + 1) = 48 and 44 cells, 47 on the mean; at 20, 38 and 34 (37); at 80, 62 and 64 (63); densest case from a smallest side of 128 ft, a cell where the crest, a lateral's mouth and a notch meet

No grid for the wave's samples: each is placed by a bisection of the ring's cumulative length, the rounded ring's 34 laid points and its four corners' arcs, about 7 steps.

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 3 | the water-facing flanks, measured: both cross flanks and the foot | 3, the village on the head's side; 2 where it stands on a cross flank |
| the face | per item | 246 at 20, 304 at 40, 406 at 80 | the dike's 182, 240 and 342 points binned (1 each), and each of the 32 bins asked of the 2 notches (64) | every notch on one flank |
| the strip written | per item | 34 | its two outer corners and a face point for each of the 32 bins | a face that changes at every bin |
| the rounding | per item | 544 | one try of two buffers, 8 arc points a corner over the strip's 34 points (2 x 8 x 34) | a narrow strip halved down to 5 ft, four tries |
| the clip to open ground | per item | 364 at 20, 464 at 40, 642 at 80 | the shaped ring (178, 220, 296) tested against the dike's outline (182, 240, 342) and the field's 4 | the strip beside the whole dike |
| the drawn ground's own ring | per item | 182 at 20, 224 at 40, 300 at 80 | the shaped ring read for its box (178, 220, 296) and the field's 4 | as above |
| the keep-out grid filed | per item | 414 at 20, 628 at 40, 1,134 at 80 | the field's 4, the crest's 178, 236 and 338 points boxed and filed as segments, and the drawn water's 116, 196 and 396 points read and filed (2 each) | a crest the length of the canvas |
| the keep-out grid's cells under the strip | per item | 37 at 20, 47 at 40, 63 at 80 | the 128 ft cells under the strip's box (the Indexes) | as the Indexes |
| the bare ground's items | per item | 100 at 20, 146 at 40, 247 at 80 | the items those cells hand back: a third of the crest's segments (59, 79, 113), a third of the water's (39, 65, 132), the field and about one earlier strip | the foot's strip, which touches both cross flanks' |
| the bare ground's shapes | per item | 1,512 at 20, 2,048 at 40, 3,160 at 80 | 4 passes over each vertex of those items: the crest's third (118, 158, 226), the water's third (78, 130, 264), the field's 4 and one earlier strip's ring (178, 220, 296) | as above |
| the record written | per item | 190 at 20, 232 at 40, 308 at 80 | the drawn ring rounded and written (178, 220, 296), its box (4) and its record's fields (8) | always its ring |
| the ways and the halo | per item | 2 | the ways and the structures and wells read, none standing | a re-laid fringe after the houses, which the contract does not lay |
| the wave's samples | over the run | 11,033 at 20, 13,702 at 40, 18,122 at 80 | each strip's ring over the 15 ft step - 3,368, 3,368 and 3,028 ft at 20 (224, 224, 201), 4,140, 4,140 and 3,820 at 40 (276, 276, 254), 5,300, 5,300 and 5,406 at 80 (353, 353, 360) - 649, 806 and 1,066 samples, each its bisection (7), its four components, its normal and its move (8) and its share of the cut and the simplify (2): 17 | a strip run to the frame on every side |
| the pond's cut | over the run | 534 at 20, 660 at 40, 888 at 80 | the earlier strips' rings read for their boxes: none, one and two of them, three rings over the run | as measured |
| the drawn ground's keep-out rings | over the run | 534 at 20, 660 at 40, 888 at 80 | the same three rings read for their boxes | as measured |
| the cuts buffered | over the run | 356 at 20, 440 at 40, 592 at 80 | the two earlier rings that reach a later strip (the foot's corners against the cross flanks') buffered and taken out | every earlier ring reaching |
| the earlier strips indexed | over the run | 534 at 20, 660 at 40, 888 at 80 | the same three rings' points indexed in the grid | as measured |
| the inputs read | once | 184 at 20, 242 at 40, 344 at 80 | the dike's outline and its 2 notches | the typical dike |
| the notches filed | once | 8 | each of the 2 notches against the 4 flanks | always 8 |
| the form's test and the flanks | once | 1 | the plan's form read; the flanks from the fall and the seat in the same pass | always 1 |
| slack | per item | 1 | every factor is a count of the stage's own inputs | not applicable |

- reason above the reference: a strip is one thing laid, about 1,800 ft by 280 at 40, and drawing it is its whole outline waved at a 15 ft step and its bare ground built from every keep-out near it - not a cost per house or per mark placed

So: items x (the face + 34 + 544 + the clip + the drawn ground's own ring + the grid filed + the bare ground's cells, items and shapes + the record + 2) x slack + each over-the-run and once term.

## Totals

- at 20: 3 x (246 + 34 + 544 + 364 + 182 + 414 + 37 + 100 + 1512 + 190 + 2) x 1 + 11033 + 534 + 534 + 356 + 534 + 184 + 8 + 1 = 24059
- at 40: 3 x (304 + 34 + 544 + 464 + 224 + 628 + 47 + 146 + 2048 + 232 + 2) x 1 + 13702 + 660 + 660 + 440 + 660 + 242 + 8 + 1 = 30392
- at 80: 3 x (406 + 34 + 544 + 642 + 300 + 1134 + 63 + 247 + 3160 + 308 + 2) x 1 + 18122 + 888 + 888 + 592 + 888 + 344 + 8 + 1 = 42251

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.41 (24,059 to 42,251): the strips are three at every size, and each
grows with the dike - its outline, its crest and its extent - and the drawn water beside it. No loop over a growing set runs inside
another: the face bins the dike's points once a flank, the wave's samples each take a bisection, and the bare ground reads the grid's
cells under one strip's box, never every keep-out.

## Work the first derivation missed

The first derivation priced the valley hamlet's one test of the form and left the polder's figure to its own phase "when one is
rolled" (its Bounds); one is now rolled (`make work-budget SPEC=`), and the polder's fringe is work the contract owes on every polder
roll:

- the face and the strips (0019: a reed fringe off each water-facing flank, at the dike's outer face, stepping in through a notch - 0027)
- the strips drawn as marsh - rounded and waved (0074), cut to the open ground and the drawn ground (0074, 0061), recorded and no-build (0058) - found uncounted by the MODE AUDIT of 2026-11-04 (`phases/waterward.audit-1.txt`)
- the keep-out grid and the bare ground the reed tile leaves (0074: reeds to the water's edge, none on the crest)

## Earlier findings

- verdict-1, finding 1: fixed - its SOUND judged the valley form's one test, which the polder's rows above keep as the form's test; the polder's fringe priced for the first time
- waterward.audit-1, finding 1: fixed - the drawn ground, the pond's cut and the ground's readers counted and priced here; the stage measured on polder rolls, where it runs
- waterward.audit-1, notes: a strip with no open ground is never recorded and then removed - it is not drawn, a refusal after the Rust laid it, priced as a strip drawn; the sty's seat on a dike-pond is the dike-pond form's, which the polder grid's rolls do not run

## Cheaper algorithms considered

- sweep: used - the face bins the dike's points once a flank
- grid or spatial index: used - the keep-out grid for the bare ground; the ring's cumulative length bisected for each wave sample, no grid
- priority queue: not used - nothing is ranked
- incremental update: not used - three strips, each drawn once
- memoizing what a scan does not change: used - the grid filed once a strip from what stands; the keep-outs beyond a strip's box skipped by their boxes
- pruning: a keep-out ring whose box misses the strip is read for its box and skipped, never buffered
