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
- **R02 residence massing**: one block under one roof, the ordinary form, massed in TWO ROWS of rooms front and back
  (as pass 2 re-massed Ochiba's, forms.md; the Kuchiba house's two rows, research buildings 260); the kitchen joined
  to it by a short covered corridor, not an echelon of halls (research buildings 250, 360/370).
- **R03 room order**: the palace order's lesser form - the reception room at the east END, the full depth, nearest the
  middle gate; the master's rooms beside it on the garden row; the family's beyond, on the garden row by the kitchen,
  with the inner rooms behind (research buildings 260). Room sizes are GUESSES.
- **Rear of the house**: the residence stands 8 ft off the north wall - the rear band narrowed to a cart/servant
  alley, one of research buildings 230's two forms (the other a service strip with the servants' row and a privy);
  the example's service side is the kitchen yard at the house's west end. The alley is not a dead end: it opens east
  onto the inner court between the residence and the servants' row, and west into the slot north of the kitchen's
  corridor; the family privy stands in it, its cesspit toward the rear wall (research buildings 220). The kitchen keeps
  its one outside door on its yard (research buildings 370), so no kitchen door opens on the alley. Research 230 asks
  only that the rear band be a service strip or a narrow alley, not that it run through.
- **House size**: research buildings 380 is the ground - a samurai's MAIN HOUSE, kitchen included, of about 49 tsubo
  (~1,740 sq ft) for the Yokota house, a 150-koku district magistrate's, and about 67 tsubo (~2,380 sq ft) for a
  retainer of 500-1,000 koku. Pass 5 brought the whole house to ~2,400 sq ft: the residence 66 x 30 ft with its
  veranda (1,980), the kitchen 24 x 20 (480) and the bath 12 x 10 (120) - the 67-tsubo house. (Pass 4 drew ~4,700 sq ft
  and called it "a size above both"; the record contradicted that.) The residence kind entry's "about 180 to 200 ft,
  checked against the size audit" was corrected at its source (`interactive/compound_kinds/household.py`, rendered
  into buildings/programs.md): the hand sheets' wings of that length are larger than the record's houses, a guess.
  The ~2,000 sq ft the house gave up went to the lodgings and stores (the granary 60 x 30, the barracks 45 x 34, the
  retainers' quarters 50 x 24, the servants' row 72 x 18, the stables 36 x 24 and a grooms' row), which holds coverage
  in the jin'ya band without shrinking the envelope; each of those sizes is a GUESS in its band.
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
- **Staff housing**: option (a) of buildings/programs.md knob 5 - everyone lives inside the walls, the platoon in the
  barracks - WITH A DEVIATION from its letter ("everyone in the barracks and residence wing"): the senior retainers
  have quarters of their own and the karo a house of their own, because buildings.md ("Only the lord's household lives
  here") gives a chief retainer and senior retainers separate structures, never bays of the lord's wing. The karo's
  house of its own is itself a GUESS (R11, below).
- **Tenure**: a freshly appointed, standardized office - no ancestral alcove, no accreted particulars (knob 6).
- **Compound shrine**: a modest shrine, 18 x 14 ft (a GUESS in the 40-1,150 sq ft band) - the hall-shrine ceiling of
  ~36 x 30 ft is Ochiba's particular, not the generic post's (buildings/programs.md: "The shrine is universal
  equipment ... Scale and dedication are the per-manor particular").
- **Middle gate**: beside the office hall's east end, not behind it (buildings/programs.md puts it customarily on the
  main axis behind the hall, the hall as the privacy baffle). Here the hall backs the divider at 1.5 ft with no alley
  behind it, and it stands west of the main axis (the tax archive takes the west end), so the placer opens the gate at
  the first stretch of divider no building backs (`compound_parts._middle_gate`); the hall still screens the house
  from the hearing court. A deliberate DEVIATION from the customary seat, recorded.
- **Lesser gates**: the kitchen postern in the west wall (6 ft) and the outer court's service gate in the south wall
  by the cell (6 ft), at the head of the cart yard - muck, night-soil and prisoners skip the ceremonial gate.

Guesses the draft carries beyond those: a **detached guest house** (R10, research buildings 330: guests were received
in the main house; a guest house apart was not found) and a **karo's house of its own** inside the compound (R11,
research buildings 340: the intendancy's staff lived in small houses or long-house bays; a chief retainer's own house
there was not found). The kitchen postern's, the service gate's and the middle gate's 6 ft (narrower than the main
gate), the door width (a map drawing convention, research buildings 620), the roji's stone spacing, the hearing
court's 80 x 32 ft, the garden's 188 x 42 ft, the dais's 30 x 10 ft, the cart yard's 62 x 25 ft, the 5 ft privies and
their 15 ft from any well are guesses too. The forecourt, the `outer court` ground beside the hearing court and the
cart yard are drawn as bare ground with no edge: an outlined forecourt read as a fenced one, a GUESS the record does
not support (research buildings 300).

Purpose: demonstrate that the toolchain can get the COMPOSITION right - buildings ring the
walls (75% perimeter-hugging, pack_audit 2026-09-27, pass 5), the garden -> oshirasu -> forecourt court-spine is held open
in the center (plus the practice ground beside the barracks, per the buildings.md program
item: a keiko-earth zone the placer reserves like any spine court, emitted with its weapon
rack and two tategi striking-post markers; the hand-refined map moves the rack flush to the
adjacent lodging's wall), coverage lands in the jin'ya band (33%, pack_audit 2026-09-27, pass 5), and nothing overflows. It is a
SCAFFOLD: a real magistracy starts from a draft like this and is hand-refined into a final
pool SVG (particulars, relics, annotations, the scale bar, and the crop are added by hand).

Reviewed by building-review from pass 3 on (the Review log below); the packing/composition metrics are checked via
pack_audit.

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
  by the bath. (Pass 4: the servants' latrine had in fact stopped seating - it was matched by the building's name,
  which the pass-3 rename changed - and the sheet carried two; it now carries four, see below.)
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

2026-09-27 pass 4 (building-review round 3):

- **Privies**, one per zone and found by KIND: the family's attached to the residence's west end by its inner door,
  its cesspit toward the kitchen postern (research buildings 220); the servants' by their quarters; the stables' on
  the stables' east end toward the south wall (it stood 5 ft from the stable well - no latrine now stands within 15 ft
  of a well); the garrison's at the barracks' south end by the cell (it stood inside the practice ground - no latrine
  stands on a spine court, nor in the divider's ink).
- **Service gate** in the south wall by the cell with a **cart yard** before it (the bare SE ground named).
- **Office hall**: the magistrate's dais, 30 x 10 ft centered on its south face over the hearing court; a door on its
  east face, by the middle gate.
- **Shrine** shrunk 36 x 30 -> 18 x 14 ft, a modest shrine (Knob settings).
- **Residence** massed in two rows (Knob settings), 8 ft off the north wall; its name seated in its rear alley, naming
  the block (it sat inside the middle room under `lord's quarters`).
- The gatehouse's name drops to 8 px where 10 would overrun its 54 px box, and its door opens on the gate passage.
- The cell's lattice is short bars across its court face (the two end lines bracketed its name); `senior retainers`
  -> `senior retainers' quarters`; the ~50 x 40 ft ground beside the hearing court captioned `outer court`.

Coverage 33%, perimeter-hugging 73%, nothing overflows; every registered check passes (pack_audit).

2026-09-27 pass 5 (building-review round 4):

- **The house at its researched size** (Knob settings, "House size"): residence 66 x 30 ft in two rows, kitchen 24 x 20,
  bath 12 x 10. The garden, now 188 x 42 ft, starts at the residence's west end; the karo's house moved to the divider's
  east end (the garden took the ground it stood on).
- **Privies against walls**: the servants' and outer privies take an end face at its wall end first, and one against a
  compound wall has a 2 ft collection hatch drawn through it (the kumitori-guchi form - research buildings 220 has the
  pits emptied by outside carters toward a service wall; the hatch is a GUESS): the servants' at the servants' row's
  east end on the north wall, the stables' on the south wall. The family privy moved to the house's rear (it stood 5.7
  ft from the kitchen well on the west face). Five privies: family, servants, grooms, stables, garrison.
- **Office hall**: the rear day rooms - clerks' room, day office, official study - across its back; two clerks'
  positions flank the dais; the hearing court carries its straw mats (the accused's at the center, the plaintiff's and
  the village officials' behind to either side, research buildings 440), the court 32 ft deep (was 36) so the stable
  well seats before the stables.
- **A grooms' row** (a servants' nagaya, 44 x 16 ft, a GUESS) in the SW corner beside the stables: the bare SW ground
  the review named now lodges the grooms by their horses. The practice ground went back to 33 ft wide (1,386 sq ft,
  still in its band) for the longer barracks; the cart yard's north edge moved to y 172 for the garrison privy.
- **Doors** on the stables, the granary, the tax archive and the shrine.

Coverage 33%, perimeter-hugging 75%, nothing overflows; every registered check passes (pack_audit).

## Review log

- **2026-09-27 building-review of the pass-2 draft** (the pass-3 fix list): 3 delta errors (a tub and its caption under
  the roofed court; the garden off the house; the court longer than the hall and off its axis), 5 program items the
  outcomes name (the gate pair R19/R26, doors and the approach R07, the divider gate and kitchen postern, the
  residence's rooms and veranda R01/R03, these notes), 4 nitpicks. All applied in pass 3 above.
- **2026-09-27 building-review round 3** (needs-work): 9 errors (two latrines only and none in the inner court; the
  stable latrine by its well; the garrison latrine in the practice ground; no service gate; no dais band or hall door;
  the hall-scale shrine; the one-room-deep residence and its caption; the staff-housing option and a stale review line;
  the gatehouse caption overrun), 5 questionable items (the middle gate's seat, the residence's size, its rear, the
  outlined forecourt, two unnamed grounds) and 3 nitpicks. All applied or recorded in pass 4 above.
- **2026-09-27 building-review round 4** (needs-work): the house ~2x research buildings 380's size; stale Purpose
  figures; the servants' latrine out in the court; the office hall's day rooms, clerk positions and the court's mats
  missing; three questionable items (the rear alley, the SW ground, the residence kind's 180-200 ft); doors on four
  buildings; four caption seats seat_label reads differently. All applied or recorded in pass 5 above.
