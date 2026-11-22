# Derivation - waterward, the polder form, greenfield (feature 444 FR-015; a form at its bounded n, as the field's polder: the round arbiter's ruling on ask:444-polder-sizes; re-derived by feature 449 T235; the bank bands added by feature 449 T250)

The waterward stage's polder form - the reed fringe outside a polder's dike - written from its contract alone. The valley form's one test of the plan is `waterward_greenfield.derivation.md`'s.

This round re-derives the stage as the Rust stage's contract states it (feature 444's `t42-brief.md`, stage 4c, `waterward`: its outputs the flanks and the strips; its drawing item 10, the marsh approximated as a polygon in a pale reed tint, "nothing in the six stages' logic depends on it"). The earlier rounds priced the drawing of each strip as reed marsh - its corners rounded and its edges waved, cut to the open ground outside the dike and the fields, the bare ground built from a keep-out grid, and the marsh recorded as no-build ground - which this stage no longer does. Each strip is laid as a plain polygon: a DELIBERATE DEVIATION from research question 0074's waved, never-ruled edge, a map drawing convention for the Rust driver (the brief's item 10), labeled here and flagged to the session as drawing work, not this stage's.

## Contract

- Reads: the plan's settlement form and field archetype; on a polder, the dike's outer face (one ring), the two channels that cross the dike at its sluices - the feeder into the inlet and the outfall's drain out of the tail, each its course and its drawn width - the strip's depth, the canvas, the fall and the side the seat faces out of.
- Writes: a polder's waterward fringe - a reed strip outside the dike on each flank that faces the water it was reclaimed from (0019: "every flank of a polder but the landward one" holds water back), each strip a plain filled polygon from the dike's outer face out to its depth or the frame, cut where a sluice's channel crosses it, in as many pieces as the channels leave; the denser band of reeds along each bank of the feeder and the outfall's drain where the bank runs through the reeds - the strips and the wild pond's fringe (0074: "a narrow band of denser reeds lines each bank" where a stream or ditch crosses the marsh) - each band a line of points `BANK_FT` (6 ft) wide; and the flanks declared. No rounding, waving, clip to open ground, keep-out grid or marsh record (the brief's item 10, above). On any other form, nothing.
- Keeps: the strip at the dike's outer face; held to the frame (20 ft past the canvas at most); run 30 ft before the dike's start and 20 ft past its end along the flank (a GUESS); the strip cut along each channel reach's bed at its drawn width, so the reeds stop at the water's edge and never cover the water (0074; 0019: water crosses the dike only at gated sluices; 0027: the band cut where a channel crosses); a piece left wholly past the dike's own extent - the run past the corner the channel cuts off - dropped (a GUESS); a bank band only where its bank stands in a ring of reeds - a strip or the fringe - and off the wild pond's water (its rim grown by the band's width), sampled along the bank every 2 ft (a drawing's grain), a band a run of two samples or more (0074).
- Bounds: a bounded n: households 10-20 (0019's GUESS: the ten to twenty households a small polder holds; the plan refuses a polder past them). Measured 2026-11-22 on the polder rolls the work budget counts - the reference spec with its field form a polder grid, seeds 4, 25, 39, 47, at 10 and 20 households - from each roll's drawn map (`make hamlet` on each spec, its dike band, its channels and its reed pieces read from the SVG, px = ft): the dike's outer face 120 and 178 points at 10 and 20 households at every seed; the feeder 3 points and the outfall's drain 3 (2 reaches each, 4 reaches, 6 points); the flanks asked 3, the flanks laid 2 at every seed (a cross flank and the foot; the seat stands on the third); the pieces drawn 4 at every seed - two strips and two slivers between the drain's bed and the dike - their points 82 at 10 (39 + 37 + 3 + 3) and 111 at 20 (60 + 45 + 3 + 3, or 46 + 59 + 3 + 3), so a strip's ring before its cuts about 38 points at 10 and 53 at 20 (the two strips' mean); the drain's two reaches reach both laid strips (the short diagonal at the dike's corner and the long run down the foot), the feeder's, at the head, neither. The bank bands, measured 2026-11-22 on the same eight rolls from each stage's outputs (a test reading the feeder's and the drain's courses and the rings of reeds - the four pieces and the fringe, 16 points - each bank's line offset by half the channel and the band and clipped to each ring's box; no count of the stage's operations read): each channel has 2 reaches and 2 banks, so 8 bank reaches, asked of 5 rings; the rings' points 98 at 10 and 127 at 20 (the pieces' 82 and 111, and the fringe's 16); 13 of the 40 reach-and-ring pairs meet, every seed and size, and the met rings' points summed over those pairs are 265 at 10 and 335 at 20 (331, 331, 331, 345); the bank lying in some ring's box about 604 ft at 10 and 606 at 20 (302 and 303 samples at 2 ft), and in the boxes summed over the rings it meets about 786 ft at 10 and 796 at 20 (393 and 398 samples); the bands drawn 4 at every seed (each bank of the drain in the foot's strip, each bank of the feeder in the fringe), their points 213 at 10 and 217 at 20 (the means of 216, 217, 211, 209 and 219, 211, 217, 219, read off the drawn reed-bank paths). The feeder runs 140 ft and the drain about 2,000 to 2,750 ft, on to the canvas edge, so most of each bank lies past every ring's box.

## The algorithm

    the plan's form read (1); not a polder: done
    the flanks facing the water from the fall and the seat's side (3 asked)
    the dike's outer face read in one pass: its box, and each point filed to the flank it faces and its place along it
    the channels' courses read (their points)
    for each flank laid:
      the face: the outermost filed point at each place along the flank; the strip from the face out to its depth or the frame,
        run past the dike's ends
      each channel reach's box asked of the strip's box; for each reach that reaches it, its bed (a quadrilateral at the reach's
        drawn width) taken out of the strip: each ring vertex's side of the bed's four sides, each ring edge against each side
        for its crossings, each bed corner asked whether the ring holds it, then the ring walked once to cut its pieces
      each piece's points asked of the dike's extent along the flank; a piece wholly past it dropped
      the pieces written
    the rings of reeds boxed: the pieces and the fringe (their boxes read with the pieces' writing)
    for each bank of the two channels, for each reach:
      the reach's offset line clipped to each ring's box (5 asked)
      for each ring whose box it meets: the ring's edges walked once - the reach's start's side of the ring (even-odd) and the
        reach's crossings of its edges, sorted
      for each sample of the reach in some met box, in order along the reach: the pond's rim asked; each met ring asked whether
        the sample is in it, by the start's side and the crossings passed so far (a cursor along the sorted crossings)
      the runs of samples in the reeds, of two or more, written as bands; a sample in no box is out of the reeds, never asked
    the flanks declared

## The knobs the count reads

- the strip's depth: 280 ft out from the dike's face (a GUESS: no page gives a reed fringe's breadth)
- the run past the dike's ends: 30 ft before its start and 20 ft past its end (a GUESS)
- the frame: the strip held to 20 ft past the canvas
- the channels' drawn widths: the feeder's 3 ft and the drain's 5.5 ft (the stage's inputs)
- the bank band's width: 6 ft (`BANK_FT`, 0074's drawing CONVENTION); its samples every 2 ft along the bank (a drawing's grain)

## Indexes

No grid: the strip is cut by at most the 4 reaches the two channels hold, each asked by its box first; the dike's points are filed once to the flank and the place along it they face, a bucketing, never searched again. The bank bands use no grid either: each bank reach is clipped to each of the 5 rings' boxes, and a ring whose box it meets is walked once for the reach's crossings, so a sample is asked of a ring by a cursor along its crossings, never by a walk of its edges.

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 2 | the flanks laid, measured: a cross flank and the foot | 2 at every measured seed; 3 where the seat stands on the head's side |
| the reaches boxed | per item | 4 | the two channels' 4 reaches, each box asked of the strip's box once | always 4 |
| the beds' differences | over the run | 2,008 at 10, 2,788 at 20 | 4 beds taken out - the drain's 2 reaches reach both laid strips, the feeder's, at the head, neither (measured) - each a difference of a strip's ring of m points (38, 53, the Bounds): each vertex against the bed's 4 sides (4m), each edge against its 4 sides for crossings (4m), each of its 4 corners asked of the ring (4m), the ring walked once with the bed's corners (m + 8): 4 x (12m + m + 8) | a channel crossing a third strip, 6 beds |
| the pieces asked of the extent | over the run | 82 at 10, 111 at 20 | each piece's points (the Bounds) against the dike's extent along its flank, 1 a point | as measured |
| the pieces written | over the run | 82 at 10, 111 at 20 | each piece's points written once (the Bounds) | as measured |
| the dike's face read | once | 120 at 10, 178 at 20 | the outer face's points, each boxed and filed to its flank and place in one pass | always the whole ring |
| the channels read | once | 6 | the feeder's and the drain's points | always 6 |
| the form's test and the flanks | once | 4 | the plan's form read (1); the 3 flanks asked of the fall and the seat | always 4 |
| the bank reaches boxed | once | 40 | the 8 bank reaches (2 channels x 2 reaches x 2 banks), each clipped to each of the 5 rings' boxes | always 40 |
| the reaches crossed | over the run | 265 at 10, 335 at 20 | each of the 13 reach-and-ring pairs that meet walks the ring's edges once, for the start's side and the crossings (the Bounds: the met rings' points summed) | every reach meeting every ring: 8 x the rings' points, 784 and 1,016 |
| the samples asked of the rings | over the run | 393 at 10, 398 at 20 | each sample of a reach in a met box asked of each ring its reach met, 1 a ring (the Bounds: the bank in the boxes summed, at 2 ft) | the bank's whole run in the boxes |
| the pond's rim | over the run | 302 at 10, 303 at 20 | each sample in some box asked of the rim once (the Bounds) | as measured |
| the crossings passed | over the run | 26 | the cursor's steps: a reach crosses a met ring's edge about twice, going in and out, 13 meets | a few a meet |
| the bands written | over the run | 213 at 10, 217 at 20 | each band point written once (the Bounds, the drawn points) | as measured |
| slack | per item | 1 | every factor is a count of the stage's own inputs and outputs | not applicable |

- reason above the reference: none owed - about 1,775 a strip at 10 and 2,260 at 20 with the bank bands, under the reference's 4,000 a thing

So: items x the reaches boxed x slack + the beds' differences + the pieces asked and written + each once term + the bank bands' terms (the reaches boxed and crossed, the samples asked, the rim, the crossings passed, the bands written).

## Totals

- at 10: 2 x 4 x 1 + 2008 + 82 + 82 + 120 + 6 + 4 + 40 + 265 + 393 + 302 + 26 + 213 = 3549
- at 20: 2 x 4 x 1 + 2788 + 111 + 111 + 178 + 6 + 4 + 40 + 335 + 398 + 303 + 26 + 217 = 4525

## Growth

From 10 to 20 households the stage grows at an exponent of about 0.35 (3,549 to 4,525): the strips are two at both sizes, and each grows with the dike's face along its flank; the bank bands barely grow (1,239 to 1,319), their samples bounded by the reach of bank in the rings' boxes, not by the drain's run to the canvas edge, which grows with the canvas. No loop over a growing set runs inside another: the dike's points are filed once, and each strip is cut by a constant 4 reaches at most, never by a set that grows.

## Work the first derivation missed

- the bank bands (feature 449 T240, added to the stage after T235's re-derivation): the denser reeds along each bank of the feeder and the outfall's drain through the reeds, a rule of the contract's Writes (0074: "a narrow band of denser reeds lines each bank" where a stream or ditch crosses the marsh) - the bank reaches boxed (40), the reaches crossed (265, 335), the samples asked of the rings (393, 398), the pond's rim (302, 303), the crossings passed (26) and the bands written (213, 217): 1,239 at 10 and 1,319 at 20

## Earlier findings

- verdict-1, finding 1: fixed - priced at 10 and 20, the polder's sizes, as since round 2
- verdict-2, finding 1: fixed - as verdict-1's
- verdict-5, finding 1: fixed - its SOUND stood on the six rows of missed work, five of them passes of the marsh drawing, no work of this stage with the marsh term dropped, and the sixth, the face's extra passes over the dike, folded into the face's one pass (the dike's face read); the section is gone
- verdicts 1-2, notes: the wave's samples, the keep-out grid, the rounding's arcs and the earlier rings' boxes are gone with the marsh drawing (above); the whole dike binned on each flank is now one pass for every flank
- waterward.audit-1, finding 1: fixed - the stage measured on polder rolls, where it runs, as since; the drawn ground, the pond's cut and the ground's readers are no work of this stage now (the brief's item 10)
- waterward.audit-1, notes: a strip with no ground left is dropped by the extent test, priced as a piece asked; the sty's seat is the dike-pond form's
- verdict-3, finding 1: fixed - the passes priced at 1 a point were the marsh drawing's, which this stage no longer makes
- verdict-4, finding 1: fixed - as verdict-3's
- verdicts 3-4, notes: answered by the marsh term's removal; the face read once, not a flank
- verdict-5, notes: the 64 ft ring index, the crest's box, the marsh's and the crest's boxes, the grid's cells and the outline's box were all the marsh drawing's and are gone; the face's coordinate and extremes are read once, in the face's one pass
- waterward.audit-2, finding 1: fixed - the marsh's ring passes are no work of this stage now; the passes the cut makes over a strip's ring are priced in one bed's difference
- waterward.audit-3, finding 1: fixed - as audit-2's
- verdict-6, finding 1: disputed - verdict-6 was SOUND and gave no finding, only a note under its Q2: the bed's 13m + 8 could be 6m + 8 (the edge crossings read off the vertex signs, three of the four corners off the crossings' parity), about 46% of the total, under the half that owes a round (rubric S10); left priced at 13m + 8, a bound the stage keeps
- the stage's waterward_polder audits (feature 449 T226, 2026-11-20, T235's filing): the budget priced the marsh drawing the Rust stage does not make, standing about 8 times over the stage's work; this re-derivation prices only the fringe the contract now writes - the strips laid from the face and cut at the channels' beds - so a regression of that size reads as one

## Cheaper algorithms considered

- sweep: used - the dike's face is read in one pass for every flank, each point filed to its flank and place; no sweep over the cuts, which number at most 4
- grid or spatial index: not used - the strip meets at most the 4 reaches of two channels, each asked by its box first; a grid over 4 items costs more than it saves
- priority queue: not used - nothing is ranked
- incremental update: not used - two strips, each laid once and cut by at most two beds
- memoizing what a scan does not change: used - the dike's box and its points' flanks found once and kept for every flank
- pruning: a reach whose box misses the strip's box is skipped, never differenced; a bank sample in no ring's box is out of the reeds, never asked - the drain's bank runs about 2,000 ft or more to the canvas edge, of which about 600 ft lies in a box
- the bank bands by sampling the whole bank: not used - every 2 ft sample of the drain's whole run, each asked of every ring's edges, is about 2,100 samples x 5 rings at 10, each a walk of its ring; the clip to the boxes and one crossing walk per met ring ask only the samples near the reeds
