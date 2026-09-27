# county-magistracy-example - design notes (placer worked example)

This is NOT a hand-authored map. It is the worked-example OUTPUT of the perimeter-first
placer ([`../compound.py`](../../compound.py), feature 008): `county_magistracy_program()`
declares a generic county magistracy entirely in FEET (envelope, the reserved court-spine,
and buildings sized in feet with wall tags), and `place()` + `emit_svg()` compose it.

**Program type**: magistrate's manor (county magistracy) - the generic worked example.

Regenerate: `make map GEN=pool/magistracies/county-magistracy-example/county-magistracy-example.gen.py` (from the skill dir).

## Knob settings

The forms the draft takes where the research gives more than one (feature 267 outcomes; each is set in
`county_magistracy_program()` with its reason at the point of change):

- **R01 veranda**: the garden face alone (the first of the two forms), 5 ft wide - an `engawa` strip inside the
  residence's south face (research buildings 240: 3-6 ft).
- **R02 residence massing**: one block under one roof, the ordinary form; the kitchen joined to it by a short covered
  corridor, not an echelon of halls (research buildings 250, 360/370).
- **R03 room order**: the palace order's lesser form - the family's rooms at the kitchen (west) end, the master's
  next, the reception room at the east END, nearest the middle gate (research buildings 260). Room widths are GUESSES.
- **R07 approach**: no genkan; the middle gate in the divider and a stepping-stone roji across the garden to a shoe
  stone at the reception's veranda (the Koseki form, research buildings 300). The household's own doors: the kitchen's
  one outside door on its south (yard) face and the residence's inner entrance on its west face, below the corridor
  (research buildings 370). Note 300 says of the Koseki house that the everyday door is the kitchen entrance, while
  370 gives the family an inner entrance apart from it; the draft draws both doors.
- **R18 granary**: an earth-walled kura on the ground, no posts (the dozo form).
- **R19 guardroom**: a freestanding gatehouse BESIDE the gate (Takayama's form, research buildings 420), 18 x 12 ft
  (Kita-in's 3 x 2 ken), flush west of the gate's post.
- **R26 main gate**: a one-bay yakuimon with an 8 ft passage between its posts (research buildings 480: 6-8.5 ft).
- **R30 garden**: no pond drawn - the draft's garden is ground only, which reads as the dry-garden form; its stones and
  sand are left to the hand refinement.
- **R34 striking posts**: two upright posts as location markers (the ~4.5 ft standing timber); the practice-weapon rack
  at the ground's edge is a GUESS.
- **Staff housing**: option (a) - the platoon in the barracks, the senior retainers in their own quarters and the karo
  in a house, all inside the walls (buildings/programs.md knob 5).
- **Tenure**: a freshly appointed, standardized office - no ancestral alcove, no accreted particulars (knob 6).

Guesses the draft carries beyond those: a **detached guest house** (R10, research buildings 330: guests were received
in the main house; a guest house apart was not found) and a **karo's house of its own** inside the compound (R11,
research buildings 340: the intendancy's staff lived in small houses or long-house bays; a chief retainer's own house
there was not found). The kitchen postern's 6 ft and the middle gate's 6 ft (narrower than the main gate), the door
width (a map drawing convention, research buildings 620), the roji's stone spacing, the hearing court's 80 x 36 ft
and the garden's 172 x 42 ft are guesses too.

Purpose: demonstrate that the toolchain can get the COMPOSITION right - buildings ring the
walls (78% perimeter-hugging, pack_audit 2026-09-27), the garden -> oshirasu -> forecourt court-spine is held open
in the center (plus the practice ground beside the barracks, per the buildings.md program
item: a keiko-earth zone the placer reserves like any spine court, emitted with its weapon
rack and two tategi striking-post markers; the hand-refined map moves the rack flush to the
adjacent lodging's wall), coverage lands in the jin'ya band (35%, pack_audit 2026-09-27), and nothing overflows. It is a
SCAFFOLD: a real magistracy starts from a draft like this and is hand-refined into a final
pool SVG (particulars, relics, annotations, the scale bar, and the crop are added by hand).

Not run through building-review / size-audit as a finished map (it is a placer example, not a
finished instance); the packing/composition metrics are checked via pack_audit.

2026-07-24 wall-ink clearance: regenerated after `compound.py` stopped seating wall-hugging
buildings on the wall CENTERLINE. The wall is drawn at true thickness centered on the
boundary, so half of it lies inside - every rank-1 building here had been standing 1.5 ft
inside the masonry, with its own outline swallowed by the wall stroke. The placer now leaves
the ink plus a hair (2 ft off a compound wall, 1.5 ft off the divider), and the inner-court
garden zone moved 36 -> 38 ft so the shifted N-wall row still clears it. Checked by
`tools/pack_audit.py` `structures_on_walls`; see buildings.md "Walls and gates".

2026-09-27 the example brought into line with feature 267's research (`compound.py`; each number carries its
reason and research section at the point of change):

- **Cell** 18 x 16 -> 12 x 10 ft: the small end of the single cells read (research buildings 460, R24); a GUESS in
  the span.
- **Clerks' room** is a ROOM of the office hall (research buildings 430, R20), not a building: a 30 x 20 ft floor
  at the hall's west end on its rear side, drawn the hand sheets' way (the hall's fill, a same-color floor tagged
  `clerks' room`, a dashed partition, the hall's outline on top, all in the hall's group - `BuildingSpec.rooms`).
  The program item `clerks` is still found by its tag. The placed-building count went 15 -> 14.
- **Hearing court** is ROOFED (research buildings 450, R22): the oshirasu zone keeps its white-gravel fill and now
  has a solid building outline (#5A3F1E, 2 px) with 1 ft posts on a ~12 ft bay along its open south side (the bay a
  GUESS). The placer drew no kneeling marks, so no mats were added.
- **Bath** is a 15 x 12 ft addition ABUTTING the kitchen's court face (research buildings 320, R09), no longer a
  pavilion in the garden. To give it that face, the garden's west edge moved 50 -> 72 ft; the kitchen well now
  stands just past the bath (up to 20 ft off the kitchen, serving both), and the garden well moved to the garden's
  east end so the two wells do not read as a pair. One of the servants' latrine seats in the unit fixture is taken
  by the bath; on this sheet all three latrines still seat.
- **Kitchen joined to the house** (research buildings 360/370): the kitchen and residence already face each other
  across a 7 ft fire-gap, so a 6 ft covered corridor (width a GUESS) tagged `residence corridor` spans it, drawn as a
  part of the residence. No placer change was needed.
- The fire-water tubs' caption now goes on the tub with the most open ground (`_roomiest`); the first tub, the
  residence's, is hemmed in by the corridor and the caption landed 13 ft from it (`orphan_group_labels`).

Coverage 37% after the change (pack_audit), perimeter-hugging 76%; nothing overflows.

2026-09-27 pass 3 (building-review of the pass-2 draft; `compound.py` split into `compound_model.py` and
`compound_parts.py` past the file-size bar):

- The office hall's fire-water tub stood inside the roofed hearing court: a roofed court is now a footprint to every
  seat (`compound_parts._point_features`) and to the audit's `tubs_in_buildings` (a court floor with a roof's outline);
  the hall's tub moved to the uncovered east end of its face. No caption but the court's own stands under its roof.
- The garden turned its back on the house: the kitchen (now 40 x 30 ft) takes the NW corner on the north wall,
  joined to the residence's west end by the corridor, with its bath, well, door and the postern on a yard of its own;
  the garden runs the residence's whole south face and was deepened to y 80.
- The hearing court is 80 x 36 ft, centered on the office hall and shorter than it (it was 132 x 39, 34 ft off the
  hall's center); the senior retainers' quarters shortened 60 -> 50 ft to keep a run before their door; the forecourt
  (55 x 31) and the practice ground (45 x 42, still in the 1,200-2,000 sqft band) took the ground the court gave up.
- The gate: the R19/R26 pair above, with the posts drawn as a `main gate` group; buildings.md's main-gate and
  gatehouse bullets rewritten to the two forms.
- Doors on every lodging block (and the kitchen and gatehouse), the approach form (R07), a 6 ft middle gate in the
  divider and a kitchen postern in the west wall; `two_court_zoning` now requires a gate in the divider.
- The residence divided into its rooms with the reception at the east end and a veranda on its garden face.
- Nitpicks: `servants` -> `servants' quarters`, the zone caption `oshirasu` -> `hearing court`, the cell's two lattice
  lines, the regenerate line in the make form.

Coverage 35%, perimeter-hugging 78%, nothing overflows; every registered check passes (pack_audit).

## Review log

- **2026-09-27 building-review of the pass-2 draft** (the pass-3 fix list): 3 delta errors (a tub and its caption under
  the roofed court; the garden off the house; the court longer than the hall and off its axis), 5 program items the
  outcomes name (the gate pair R19/R26, doors and the approach R07, the divider gate and kitchen postern, the
  residence's rooms and veranda R01/R03, these notes), 4 nitpicks. All applied in pass 3 above.
