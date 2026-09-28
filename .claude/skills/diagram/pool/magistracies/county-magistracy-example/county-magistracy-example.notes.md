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

- **R01 veranda**: the garden face alone (the first of the two forms), 4 ft wide (pass 6; 5 ft before) - an `engawa` strip inside the
  residence's south face (research buildings 240: 3-6 ft).
- **R02 residence massing**: one block under one roof, the ordinary form, massed in TWO ROWS of rooms front and back
  (as pass 2 re-massed Ochiba's, forms.md; the Kuchiba house's two rows, research buildings 260); the kitchen joined
  to it by a short covered corridor, not an echelon of halls (research buildings 250, 360/370).
- **R03 room order**: the palace order's lesser form - the reception room at the east END, the full depth, nearest the
  middle gate; the master's rooms beside it on the garden row; the family's beyond, on the garden row by the kitchen,
  with the inner rooms behind (research buildings 260). Room sizes are GUESSES.
- **Rear of the house**: the residence stands 10 ft off the north wall - the rear band narrowed to a cart/servant
  alley, one of research buildings 230's two forms (the other a service strip with the servants' row and a privy).
  Both privies of the house are attached to it at its rear (research buildings 220: "within the residence the privy
  came to be built in a corner of the corridor"; a guests' privy at the rear of the guest parlor): the family's at
  the rear corner by the family's rooms, the guests' behind the reception room, each leaving a 5 ft way along the
  alley. (Pass 6 had stood the family's flush to the wall for a hatch, ~140 ft outdoors round the house from the inner
  entrance; the hatch was a guess and is dropped for it.) THE CARTER'S ROUTE to both (pass 8): in by the kitchen
  postern in the west wall, north along the wall past the vegetable ground, up the 7 ft way between the servants' row
  and the kitchen, and east along the rear alley, which since pass 8 runs on behind the kitchen - the kitchen stands
  10 ft off the north wall as the house does, so the corridor between them no longer closes the alley's west end.
  Never through the ceremonial middle gate or the lord's garden. The alley opens east onto the inner court; at its
  west end the kitchen's corridor to the house closes it (the slot north of the corridor is closed on all sides - the
  pass-5 notes' "opens west into the slot" was wrong). The servants reach the kitchen by the kitchen yard instead:
  since pass 6 their row stands in the NW corner beside the kitchen, its door and privy on the yard with the postern.
- **House size**: research buildings 380 is the ground. Its two measured main houses are the Yokota house of a
  150-koku district magistrate (gun-bugyo) at about 49 tsubo (~1,740 sq ft) and the Matsue house of 500-1,000 koku
  retainers at about 67 tsubo (~2,380 sq ft, as restored to its Meiji plan). Pass 6 takes the 49-tsubo house: the
  district magistrate is this posting's own office, and nothing in the program raises it to the larger retainers'
  rank. The residence 56 x 24 ft with its veranda (1,344 sq ft), the kitchen 20 x 18 (360) and the bath 10 x 8 (80)
  come to 1,784 sq ft, ~50 tsubo; how much of a main house was kitchen is not given, so the kitchen's share is a GUESS.
  (Pass 5 wrote "~2,400 sq ft" for a house of 1,980 + 480 + 120 = 2,580 sq ft, ~72 tsubo; pass 4 drew ~4,700.) The
  residence kind entry's "about 180 to 200 ft" was corrected at its source (`interactive/compound_kinds/household.py`)
  and buildings.md's scale doctrine no longer calls those wings validated. The mass the house gave up went to the
  lodgings, stores and office (the office hall 113 x 38, the tax archive 34 x 34, the granary 60 x 30, the barracks
  45 x 34, the retainers' long-house 50 x 36, the servants' row 72 x 22, the stables 42 x 24, the grooms' row 44 x 18
  and the guest house 33 x 32), which holds coverage in the jin'ya band without shrinking the envelope; each of those
  sizes is a GUESS in its band.
- **R07 approach**: no genkan; the middle gate in the divider and a stepping-stone roji across the garden to a shoe
  stone at the reception's veranda (the Koseki form, research buildings 300). The household's own doors: the kitchen's
  one outside door on its WEST face, onto the 7 ft way between it and the servants' row that runs to the yard (pass
  7: on its yard face it opened into a ~5 ft pocket between the bath, the well and the house), and the residence's
  inner entrance on its west face, below the corridor
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
  keep a long-house of their own in the outer court, because buildings.md ("Only the lord's household lives here")
  gives senior retainers separate structures, never bays of the lord's wing. The KARO lodges in a bay of that staff
  long-house, its north 14 ft with a door of its own - R11's attested form (captioned `karo's quarters` - a bay, not a house; its kind stays `karo's house`, the registry's) (research buildings 340: at an intendancy
  the staff lived inside the compound in small houses or long-houses; a chief retainer's house inside the lord's own
  compound was not found). Pass 5's karo's house of its own in the inner court, its door on the lord's private court,
  is gone. The grooms lodge in a row of their own by the stables.
- **Tenure**: a freshly appointed, standardized office - no ancestral alcove, no accreted particulars (knob 6).
- **Vegetable garden**: WEST of the house, filling the kitchen yard (research buildings 400: the one plot whose side
  is given lay west; its size runs from the Takei house's ~1,070 sq ft plot to a field over about half the Yokota
  house's grounds). Pass 7 takes the field form, as large as the yard holds - 64 x 48 ft, 3,072 sq ft, its size a
  GUESS - leaving a ~12 ft way from the postern along the west wall (7 ft past the servants' privy, which stands flush to it) (pass 6's 36 x 30 plot left ~100 x 60 ft of the
  yard bare). It is drawn in the garden stipple, as the hand sheets draw theirs.
- **Garden**: 122 x 46 ft, from the kitchen's corridor to the guest house (pass 7): the one garden faces the
  reception and the guest house both, guests being received in the garden-facing rooms (research buildings 330).
  Pass 5's 188 ft garden ran on beside the servants' row with a bare strip; pass 6 cut it to the house's 68 ft and
  left ~62 x 66 ft of bare inner court east of it. Its size is a GUESS. A ~69 x 36 ft band of inner court north of
  it, east of the house (the alley's east end and the shrine's corner), stays open ground.
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
in the main house; a guest house apart was not found). (The karo's house of its own, a GUESS through pass 5, is now
a bay of the staff long-house - R11's attested form.) The kitchen postern's, the service gate's and the middle gate's 6 ft (narrower than the main
gate), the door width (a map drawing convention, research buildings 620), the roji's stone spacing, the hearing
court's 80 x 32 ft, the garden's 122 x 46 ft, the collection hatches, the dais's 30 x 10 ft, the cart yard's 62 x 25 ft, the 5 ft privies and
their 15 ft from any well are guesses too. The forecourt, the `outer court` ground beside the hearing court and the
cart yard are drawn as bare ground with no edge: an outlined forecourt read as a fenced one, a GUESS the record does
not support (research buildings 300).

Purpose: demonstrate that the toolchain can get the COMPOSITION right - buildings ring the
walls (72% perimeter-hugging, pack_audit 2026-09-27, pass 6), the garden -> oshirasu -> forecourt court-spine is held open
in the center (plus the practice ground beside the barracks, per the buildings.md program
item: a keiko-earth zone the placer reserves like any spine court, emitted with its weapon
rack and two tategi striking-post markers; the hand-refined map moves the rack flush to the
adjacent lodging's wall), coverage lands in the jin'ya band (33%, pack_audit 2026-09-27, pass 6), and nothing overflows. It is a
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

2026-09-27 pass 6 (building-review round 5):

- **Fire-water tubs** at the kitchen (two, on its west end by the yard - its yard face holds the bath, the well and
  the door) and one at the bath; a tub now finds an end face where its court face has no room.
- **The servants' row moved to the NW corner** beside the kitchen, the kitchen yard (bath, well, doors, postern,
  vegetable garden) before both; the house follows them east. The servants' privy stands flush to the west wall with
  a hatch, near the postern the carter uses.
- **Privies**: the family's flush to the rear wall with its hatch; a guests' privy behind the reception room; the
  stables' dropped - the grooms' row's, flush to the west wall with a hatch, serves both (the stables' hatch had opened
  12 ft from the gatehouse). Five in all: family, guests, servants, grooms, garrison.
- **The stables' well** stands beside the stable door, not before it: a well tries the fracs off a face's middle first.
- **The house at 49 tsubo** (Knob settings), the notes' arithmetic corrected, and buildings.md's scale doctrine
  corrected to research 380.
- **The karo in a bay of the staff long-house** in the outer court (Knob settings).
- **The garden sized to the house**, the vegetable garden west of it, the east ground named `inner court`.
- **The office hall's doors** open on its front room at both ends (east by the middle gate, west to the archive and
  the retainers); the hall is 38 ft deep, the hearing court moved 4 ft south with it.
- A bold name's width is measured at 0.60 em (the retainers' 26-letter name, judged to fit at 10 px, ran over the
  wall's ink).
- LEFT, with its reason: the family's inner entrance opens straight into a room with no earthen entry drawn. The
  registry has no kind for an inner entrance's earthen floor, and adding one owes a research-backed entry (research
  buildings 370 names the uchigenkan but gives no plan of it); a hand refinement draws it once that entry exists.

Coverage 33%, perimeter-hugging 72%, nothing overflows; every registered check passes (pack_audit).

2026-09-27 pass 7 (building-review round 6):

- **The family privy back in the house**, attached at its rear corner by the family's rooms (research 220), its
  hatch dropped (Knob settings, "Rear of the house").
- **The kitchen's one outside door on its west face**, onto the way to the yard (Knob settings, R07).
- **The two bare patches used**: the garden runs on to the guest house (122 x 46 ft), and the kitchen yard holds
  research 400's field form of the vegetable ground (64 x 48 ft, the garden stipple the hand sheets use).
- **Notes fixed**: the veranda is 4 ft as drawn; the karo's bay is captioned `karo's quarters` (the kind
  `karo's house` still finds it for the program's check).

Coverage 33%, perimeter-hugging 72%, nothing overflows; every registered check passes (pack_audit).

2026-09-27 pass 8 (building-review round 7):

- **The rear alley opened at its west end**: the kitchen stands 10 ft off the north wall, so the alley runs on behind
  it to the way by the servants' row and the kitchen yard - the carter's service route to the house's two privies
  (Knob settings, "Rear of the house"). No hatch is restored.
- **Notes**: the vegetable ground leaves a ~12 ft way along the west wall, 7 ft past the servants' privy.

Coverage 33%, perimeter-hugging 71%, nothing overflows; every registered check passes (pack_audit).

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
- **2026-09-27 building-review round 5** (needs-work): 7 errors (no tubs at the kitchen and bath; the servants cut off
  from the kitchen; no guests' privy; no hatch on the family privy; the stables' privy by the gate and apart from the
  grooms'; the stables' well before its door; the notes' arithmetic and buildings.md's validated-wings line), 3
  questionable items (the 49- or 67-tsubo house, the karo in the inner court, the long garden) and 2 nitpicks. All
  applied or recorded in pass 6 above; the earthen entry is left, with its reason.
- **2026-09-27 building-review round 6** (needs-work): the family privy apart from the house; the kitchen door into a
  ~5 ft pocket; two bare patches (east of the garden, the kitchen yard); the veranda's width and the karo's bay's
  label in the notes. All applied in pass 7 above.
- **2026-09-27 building-review round 7**: pass 7's five items confirmed; the rear alley closed at its west end (the
  house's privies ~400 ft from a service edge) and the vegetable ground's way misstated. Applied in pass 8 above.
