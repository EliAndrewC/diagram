# Implementation Plan: the magistracy residences brought to the research (feature 433)

**Spec**: `spec.md` | **Request**: `request.md` | **Research**: `research.md`

## Summary

Hayakawa's house is redrawn within research 0091's range (D1), from about 145 tsubo (R1); the inner court is laid out again
around it, and its north wall moves south, the envelope a knob (D3), so the compound stays inside 0116's coverage band (R2). Ochiba's and
Ubame's large houses are recorded as deviations with the GM's reason. The procedure for a new sheet sizes the house by the
research and no longer copies Ochiba's.

## Measured before planning (2026-10-26)

- **Coverage with the house alone resized** (observed 2026-10-26, method: the sheet copied to the scratchpad, the two blocks
  cut to 108 and 82 px wide by 76 px deep and their verandas with them, `pack_audit.coverage` on both): 32.8% today, 26.3%
  with the house resized and nothing else changed - about 13,840 sq ft built on 52,592 sq ft walled.
- **What 30.5% needs** (observed 2026-10-26, method: arithmetic on the measure above): about 45,400 sq ft walled, a cut of
  about 7,200 sq ft, about 29 ft off the depth of the 247 ft wide inner court.
- **The karo's house** (observed 2026-10-26, method: its rect, 115 x 74 px): about 38 x 25 ft, 946 sq ft, inside 0118's
  junior houses of 700-1,000 sq ft, and not resized.

## Constitution Check

A hand-drawn Mode A sheet (`pool/magistracies/hayakawa-magistracy/`), its notes, `docs/` and one drawing page of the record
(0116). No engine code; the sheet's png and page are re-rendered by its gen. Every changed number cites its page; every
guess is labeled. Occasion: building-review (a sheet revised).

## T01 - Hayakawa's house and inner court redrawn to the research (FR-001)

### T01 Approach (checklist part A)

1. **The goal, in the world.** Hayakawa's magistrate lives in a house the size the record gives a samurai of that rank, on a
   compound whose buildings cover what 0116 says such a compound's do.
2. **The constraints.** The outer court is not touched. The house keeps its recorded forms (the echelon of two blocks, the
   reception at the east end, the roji, the kitchen ell, the veranda faces rolled). Every pack-audit check stays green.
3. **Where each comes from.** O: spec FR-001, SC-001; research 0091 (the house and its kitchen), 0118 (houses by rank), 0116
   (coverage), `research.md` R1-R2, the measures above.
4. **Do they describe the world here?** Yes: the GM placed Hayakawa's magistrate within the record's houses.
5. **The order.** First; T02-T04 cite its figures.
6. **The exits.** Red: a check that cannot be made green on this layout goes to `make arbiter-ask` with the measure.
7. **The search smell.** None.
8. **The budget.** 2 h (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** pack-audit: every check OK, coverage inside 0116's band (R2), the house's rects summed within 0091's
   range with kitchen, bath and corridor (D1), the render read, building-review passed.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** The room is cut, not added; D3 prices the alternatives.

### T01 Decisions

- **D1** The house is about 65 tsubo, about 2,320 sq ft, the top of research/questions/0091's range a GUESS for the RICH
  knob: the west block 36 x 25.3 ft and the east block 27.3 x 25.3 ft (GUESS, their split), the corridor, the 24 x 18 ft
  kitchen and the 18 x 12 ft bath (unchanged, GUESS on research/questions/0091's drawing page, which counts the kitchen in the
  house, as R1 counts the bath). The range is 0091's: 49 tsubo for a 150-koku district magistrate, 41-74 tsubo by the two measures of the
  Kuchiba house of a 1,000-koku retainer; the Matsue 67 tsubo is not used as a measure (0091's drawing page). The top of the
  range for Hayakawa's RICH posting is a GUESS: no page ties a house's size to its holder's wealth. Rooms, a GUESS as zones of
  about six rooms (research/questions/0091): the inner rooms 16 x 25 ft (GUESS), the family's quarters 20 x 25 ft with the
  maids' room in them (GUESS), Hajime's quarters 12 x 25 ft (GUESS) and the reception 15 x 25 ft (GUESS). Rendering: the house's rects and room lines.
- **D2** The inner court laid out again (north wall at the new line, D3): the house backs the north wall across a service
  alley of about 6-7 ft (GUESS: the rear strip's "narrow service alley" form, research/questions/0091's drawing page), the family privy and the
  guests' privy attached to its north face as before; the reception keeps the garden's west end before it, the roji running
  from the middle gate to its veranda; the kitchen ell, the bath on the kitchen's west face and the maids' room move with the
  house; the inner entrance moves to the west block's west face, onto the kitchen yard (the veranda and the bath take its
  south face). The two storehouses stand north of the garden, east of the reception, behind the garden as before; the woodshed
  and the rear-yard privy take the north-west corner by the postern; the karo's house moves west, onto the kitchen yard, its
  side door kept on its west face. The vegetable garden keeps its seat knob ("south beside the formal garden", 0109) and its
  size, set east of the pond where nothing shades it; the shrine, its tree, its arch and its tub move with the north wall.
  Rendering: the inner court's rects, the garden polygon, the pond, pines, lanterns and stones.
- **D3** The north wall moves 30 ft (90 px) south, the envelope a knob, and the guests' annex with it, so its top stays on
  the north wall: the walled ground falls to about 45,200 sq ft and the coverage to about 30.6% (this project's arithmetic on
  the measure above, inside R2's band). The envelope is a number no page measures - the
  notes call it the "audited Joge<->Takayama size", a range - so it is a knob (GM 2026-10-25, `make tunables`). Priced:
  (a) the sheet under the band as a recorded deviation - SC-001 forbids it; (b) buildings drawn past their research sizes to
  fill the court - the "Realistic unless the GM says otherwise" rule forbids it; (c) the west wall in 36 ft (this project's arithmetic) - the servants'
  range abuts the gate range and the outer court's west column would run into the office hall; (d) the east wall in - the
  outer court's east side has no 36 ft to give (this project's arithmetic). The checklist's "envelope NOT shrunk" and the coverage check's "never shrink
  the envelope" are kept for their reason - a smaller wall does not hide slack - and amended: when the research resizes a
  sheet's program, the envelope follows it (docs/buildings.md checklist; `pack_audit/shared.py` and `registry.py` messages,
  with the test that pins the text). Rendering: the walls, the precinct rects, the viewBox and the title block.

## T02 - the two kept houses recorded as deviations (FR-002)

### T02 Approach (checklist part A)

1. **The goal, in the world.** A reader of Ochiba's and Ubame's sheets learns the large house is the GM's choice and why.
2. **The constraints.** No ink changes on either sheet.
3. **Where each comes from.** O: spec FR-002; the GM's words in `request.md`.
4. **Do they describe the world here?** Yes.
5. **The order.** After T01, whose figure docs/buildings.md:23 cites.
6. **The exits.** Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** FR-002's grep, re-run.
8. **The budget.** 30 min (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** The grep's hits that label or size the magistrate's house on the two sheets or in docs/buildings.md
   say DEVIATION with the GM's reason; no `Research:` comment calls it a GUESS.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D4** docs/buildings.md:17's `Research:` comment and :23's prose become a DEVIATION: Ochiba's and Ubame's houses (about
  141 and 152 tsubo, R1) larger than the record's, the GM's ruling of 2026-10-26 that their magistrates are significantly
  wealthier than normal; Hayakawa's figure becomes its redrawn ~65 tsubo. Ochiba notes :65 and Ubame notes :109 ("keeps to
  the 49-tsubo residence") say the house is about 141 / 152 tsubo, a deviation for the magistrate's wealth. Rendering: none.

## T03 - the procedure for a new magistracy (FR-003)

### T03 Approach (checklist part A)

1. **The goal, in the world.** The next magistracy sheet draws its house at the record's size without anyone remembering.
2. **The constraints.** The worked example and validation instance stay named as examples of the program's composition.
3. **Where each comes from.** O: spec FR-003; FR-003's grep.
4. **Do they describe the world here?** Yes.
5. **The order.** After T01 (Hayakawa becomes the research-sized instance named).
6. **The exits.** Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** FR-003's grep, re-run.
8. **The budget.** 30 min (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** docs/usage.md :5, :41, :119 and docs/building-programs.md no longer make Ochiba the model for a
   house's size; the program's residence bullet and the checklist name 49-67 tsubo with kitchen and bath, a larger house only
   as a recorded deviation with its reason, and the coverage band.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T03 Decisions

- **D5** The residence bullet of docs/building-programs.md and a checklist line of docs/buildings.md state the house's size
  (49-67 tsubo, kitchen, bath and corridor counted, 0091), that a larger house is a recorded DEVIATION with its reason
  (Ochiba's and Ubame's), and that the envelope then follows the coverage band (D3). docs/usage.md keeps Ochiba as the
  template for the sheet's conventions and drawing, and says its house is a deviation not to be copied - the house sized by
  the program. Rendering: none.

## T04 - the record's figure and the close (FR-001)

### T04 Approach (checklist part A)

1. **The goal, in the world.** The record's figure for Hayakawa's coverage is the sheet's measured one (R2's page).
2. **The constraints.** The 0116 drawing page fragment is edited through its make route, and the checks `make record-owed`
   names run.
3. **Where each comes from.** O: research/questions/0116-...drawing.html ("Ochiba's and Hayakawa's compounds cover 38% and
   35%").
4. **Do they describe the world here?** Yes.
5. **The order.** Last, with T01's final measure.
6. **The exits.** Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** `grep -rn "35%" research/questions/0116*`.
8. **The budget.** 30 min (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** The sentence carries the measured figures; the owed checks recorded; `make feature-report F=433
   WRITE=1`.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T04 Decisions

- **D6** The sentence gives each compound's measured coverage on its date (Ochiba's re-measured too). Rendering: none.
