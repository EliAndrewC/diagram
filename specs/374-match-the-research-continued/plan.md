# Implementation Plan: Match the research - continued (feature 374)

**Spec**: `spec.md` | **Request**: `request.md` | **Model**: `specs/372-match-the-research-remaining/plan.md` (its cycle, its batch
close and its bookends, themselves 328's) - this plan records only what differs and each wave's decisions.

## Summary

The work list is 328's ranking's open in-scope rows at 372's close (198: 153 E3, 43 E4, 2 E2 held - counted from `ranking.json` 2026-10-10, rows with no wave in scope), in ranking order, with the
items the spec's "What it carries" lists. Waves are numbered on from 372's (the first is wave 112), so 328's `audit/waves.json`
stays the one column; this feature's measurements are its own `measurements.json`, its decisions its own spec's table. Also
carried, from feature 370's landing (its spec, 2026-10-10): the claims findings on the code 370 split, left in `make
claims-report` for this feature under the claims gate's escape - rows of the work list like any other.

Two of the spec's carried tooling gaps (FR-007) are placed here, not in a wave: the claims-triage reply parser counting
"TOUCHES" anywhere is already fixed by 375's D5 (`scripts/record/claims_triage.py` reads only lines opening with `TOUCHES`,
its test pinning a mid-line mention ignored) - recorded so under SC-006 at batch 1's close; and `make modal-bundle
FOR=modal-depiction`'s crop on a Mode A sheet is fixed, with its test, before the first modal-depiction check on a Mode A
sheet that a wave owes (batch 1 edits no drawing page and owes none, as planned).

## Constitution Check

As 372's (XII research, XIII no known regressions, XIV fix where found, XVI the literal thing). New here: 375's process (decide
first, the freeze, the tripwires, the preflight) is in its first real use, and a guard that refuses correct work is fixed with
its test (spec FR-005).

## The cycle (372's, under 375)

`make task-start F=374 T=<id>` -> the task's section below carries its verdict (this plan's review, or `make decide`) -> the check
first where a rule is drawn (red on the unfixed sheet) -> edit -> `make test-file` -> each Mode A sheet's `make pack-audit` before
and after -> `make cohort N=48` only when the hamlet's stage code changes -> `impl-drift` on the owed claims (`make claims-owed`,
the triage for the rest) -> the record checks a page edit owes (`make record-owed`) -> records -> `make quick` -> tick -> commit. A
batch closes with `make done`, its occasions, the timing pair or its recorded "none owed", `escalation-check`, and LANDS.

## Batch 1 (T01-T05)

Three waves, the first three rows the ranking leaves open after its two held E2 rows (the door band and `fixture_quota`, held for
the GM), with the kitchen's two rows taken as one wave because both redraw the same building; then the two measuring tasks 375
carried here (spec FR-006), which are not among the three measured.

**Pair (FR-002)**: none owed if the batch's engine code stays out of what the timing pair rolls (the hamlet's stages) - this
batch's engine code is `pack_audit` (a review tool) and `buildings/types.json`'s kitchen band, read by the Mode A draft and the
pack audit only, as 372's batches 3-5 recorded. If a wave touches the hamlet's stages, the pair is owed and taken.

### Wave 112 (T01) - the veranda's width and faces

- **Scope**: `docs/buildings.md::Inner court (private / sacred)#engawa` (E3). 0102's drawing page: a veranda 3-6 ft wide (half a
  ken to one ken, Katsura's widths), free to change from face to face, the garden face at the wider end a GUESS; which faces
  carry it a KNOB between two attested forms - the garden face alone, or a continuous veranda along two or three faces - never
  all four. The procedure says "~8 px" (2.7 ft) along the south face of each block, and every sheet draws 8 px on the garden face (each
  sheet's `data-kind="engawa"` rects read 2026-10-10, grep of the three SVGs).
- **Check first**: a `pack_audit` check, `veranda_depths`: every `data-kind="engawa"` strip's short side is 3-6 ft (9-18 px),
  reading the strip's rect (a `data-kind="engawa"` group's rect too). Red on all three magistracy sheets now; a red fixture
  beside the others. Its limits cite 0102's drawing page, ACCURATE (Katsura's measured widths).
- **The knob on the hand sheets**: each sheet rolls its faces as its other knobs are rolled, `random.Random(zlib.crc32(b"<map>:
  residence veranda faces")).choice(["garden face alone", "two or three faces"])` - **Hayakawa** two or three faces, **Ochiba**
  and **Ubame** the garden face alone (computed 2026-10-10). Each sheet's notes record the roll and the form drawn, as the
  shrine-arch knob is recorded.
- **Widths** (calibrated liberty within 3-6 ft, the garden face at the wider end - 0102's GUESS): every garden-face strip 12 px
  (4 ft); Hayakawa's turned faces 9 px (3 ft), as Katsura's veranda narrows where it turns the corner. Hayakawa's board veranda to
  the guests' privy (already 9 px) stays. What a widened strip runs into (a door, a stone, a tub, the garden) moves with it, each
  move audited.
- **Hayakawa's two or three faces**: the east block's veranda runs on round its south-east corner up the reception's east end
  (the formal end, facing the garden's east side), a third face being its north board veranda already drawn; the west block keeps
  its garden face alone (a hall of its own; the knob is the house's, and the house shows it on its formal hall).
- **The procedure**: the bullet's veranda sentence says 3-6 ft (9-18 px), the faces a rolled knob between the two forms, never all
  four; the claim gets the knob and the widths, each labeled (the forms ACCURATE, the garden face wider a GUESS).
- **The generated draft** (`compound.py`, seedless) keeps its 4 ft garden-face veranda, the form 0102's drawing page records it
  taking; it cannot roll a knob, and that is recorded there.
- **Tooling gap fixed here** (spec FR-007, carried from 372): a glyph-check verdict is keyed by element alone, so this batch's
  second sheet would overwrite the first's; the verdict is keyed by element and map, with a test red on the old keying.
- **Occasions**: glyph-redrawn: engawa on hayakawa-magistracy (the new turned form); glyph-redrawn: engawa on ochiba-magistracy
  (the garden-face form; Ubame's the same glyph).

### Wave 113 (T02) - the kitchen at 0091's size, joined as an ell

- **Scope**: `docs/buildings.md::Inner court (private / sacred)#kitchen` (E3) and `#kitchen corridor tagged residence corridor`
  (E3, after the first; the same building). 0091: the one kitchen measured, the Kuchiba house's east wing, is about 12 tsubo
  (~440 sq ft, 5.9 x 6.9 m) by the prefecture's measure, about a sixth of the house; a middle-rank house was one block, its kitchen
  projecting from one side, with almost no corridors. The sheets draw 120 x 100 px (40 x 33 ft, ~1,320 sq ft) kitchens (each kitchen's rect read off the three SVGs, 2026-10-10), and
  Hayakawa joins its kitchen to the house by a covered way tagged a residence corridor.
- **The fix**: each sheet's kitchen drawn about 24 x 18 ft (72 x 54 px), the size of 0091's measured wing taken as the
  kitchen's - a GUESS, as 0091's drawing page holds a kitchen's size (impl-drift, wave 113: the plan first called it an ACCURATE ceiling), joined to the house as an ell (abutting it, no corridor); Hayakawa's covered way removed. The kitchen band in
  `buildings/types.json` narrowed so the old size fails it: w 18-24 by h 14-18 ft (either orientation; at most 432 sq ft, under the measured ~440 - the T02 preflight's aside). The procedure's kitchen
  bullet and both claims say ~24 x 18 ft, an ell, 0091 cited; "a large institutional daidokoro" goes (the ranked fix sizes it to
  the measured house; nothing in the record sizes a kitchen to its feeding). The draft's kitchen is 20 x 18 ft (`compound.py`'s program,
  read 2026-10-10), already inside the new band.
- **What stands in the kitchen moves with it**: the kamado range, a well drawn inside the kitchen (0105's drawing page: inside
  the kitchen on a hand plan), its door, the two tubs at its door (wave 106's rule, `tubs_off_their_doors`), the bath abutting it.
  The ground the smaller kitchen frees is left as the court or service ground it opens onto. Each move audited.
- **Amendment 1 (2026-10-10, found in the work)**: (a) Ubame joins its kitchen by a covered corridor too (an L across its service
  alley, tagged a residence corridor), so its kitchen becomes an ell as Hayakawa's does: it projects south from the west block under
  the shuttered wing, its door on its west face toward the kitchen postern, the bath on its south face; the west block's veranda
  starts at the kitchen's east face. Hayakawa's ell projects south from its west block's family end, the bath on its west face, the
  door on its south face; Ochiba's is the ell it was, shrunk into the house's corner. (b) The generated draft
  (`compound_parts._point_features`) also joins its kitchen by a covered corridor (`_corridor`, `CORRIDOR_W_FT`) across the 7 ft
  fire-gap the placer leaves: the procedure now drops that form, so the draft draws the ell - a `BuildingSpec.joins` names the
  building an ell projects from, the placer abuts the two with no fire-gap (`_place_one`), and the corridor code goes. Its
  occasion: layout-revised: county-magistracy-example. (c) Knock-ons in the tooling, each fixed where found: `pack_audit` read a
  kamado tagged `hearth` as a door glyph adrift (`floating_doors`) once a small kitchen put it within a door's reach of a wall -
  a rect inside a `hearth` element is no door (a test); the round-trip sheet's program kitchen 18 x 24 ft (its court face then
  seats the bath; at 24 x 18 the bath found no clear run); the frozen red fixtures' kitchens brought to 72 x 54 px against their
  houses, their contents and baths moved with them, so each fires only its own check (the two whose check counts tubs at the old
  kitchen keep it).
- **Amendment 3 (2026-10-10, impl-drift)**: the kitchen claim relabeled GUESS on 0091's drawing page (above), and the
  corridor claim renamed `#kitchen abuts the house, no corridor` - its old name described the corridor the wave removed.
- **Amendment 4 (2026-10-10, impl-drift round 2)**: the kitchen's size is taken from the measured wing as a size, whatever the
  house's size, not as its sixth share - recorded so on 0091's drawing page as a GUESS (the ranked fix's ~12 tsubo kept; sizing
  every kitchen to a sixth of its house was impl-drift's other way out, and would size the hand sheets' larger houses'
  kitchens past the measured wing); the claim names that page. The residence-rooms claim (T03) renamed `#residence of about
  six rooms`. The residence-corridor pop-up's guess bullet gives the drawn width (about 11 ft, Hayakawa's and Ubame's) and its
  `Covers:` drops "covered" (modal-form round 1).
- **Amendment 2 (2026-10-10, the draft as built)**: with the ell abutting the house's west end, the house's west face keeps 6 ft
  free below the kitchen, short of a door's 8 ft approach, so the draft's inner entrance opens on the house's rear (north)
  face at the kitchen end, onto the rear alley; 0107's drawing page said "on the residence's face toward the kitchen" and now
  says "on the residence's back, at the end the kitchen stands against" (its record checks owed: the pop-ups naming the
  page triaged, quote-check on the note in that block, record-format). The house stands 7 ft further west with the gap gone,
  so the draft's garden zone starts 7 ft west to stay before the whole south face; the family privy at the house's rear west
  corner stands a foot in from it, its half-foot margin off the kitchen. Hayakawa's kitchen door stands on its south face,
  its two tubs either side.
- **Occasions**: layout-revised: hayakawa-magistracy and ubame-magistracy (the kitchen joined as an ell, the corridor gone);
  layout-revised: county-magistracy-example (the draft's ell); glyph-redrawn: kitchen on ochiba-magistracy.

### Wave 114 (T03) - the residence's rooms

- **Scope**: `docs/buildings.md::Inner court (private / sacred)#residence of ~18-25 tatami rooms` (E3). The procedure says a real
  residence of this footprint held ~18-25 tatami rooms; 0091 sizes the residence to the 49-tsubo district magistrate's house, and
  the one house measured with its rooms, the thousand-koku Kuchiba house of 41-74 tsubo, held six. The fix follows the record:
  the procedure says the labeled zones TOGETHER compress a house of about six rooms (0091 - the count is the whole house's), and
  the claim cites it; the sheets label
  zones, not rooms, so no sheet is redrawn. Searched 2026-10-10: Hayakawa's notes alone state the count ("a real residence of
  this footprint holds ~18-25 tatami rooms"); that line says the house held about six (0091), as the procedure does.
- **Occasions**: none (no drawn element changes).

### T04 - 375's SC-003 over T01-T03 (key `sc003-375-first-three-tasks`)

From `make feature-report F=374` at batch 1's close: red gates and their causes against the preflight's checks, pages re-checked
while a check on them was outstanding, plan-review BLOCKs on a decision a decision preflight had ruled on. Recorded in
`measurements.json` with its command.

### T05 - 375's SC-004 over T01-T03 (key `sc004-375-dispatches-per-row`)

The dispatches per closed row of T01-T03 (four rows), from the same report, beside 372's ~10 (375's "Why", an estimate).

## Batch 2 (T06-T09): the claims labeled as the record has them

**The work list** stays 328's ranking (FR-001), brought current with the claims report (`make claims-report`, 2026-10-10:
DRIFTED 119, MISLABELED 28, UNCLAIMED 21, NEEDS-RESEARCH 16, CANNOT-TELL 11). The ranking had gone stale against it both ways:
26 of its open rows read IN-STEP now (closed by later relabels - the room order and the senior retainers' rows among them),
closed by that re-check and marked wave 115 in `audit/waves.json`; and 56 of the report's findings were not in it, added as
found rows (`audit/found-wave115.jsonl`, tiered E0 for a label, E1 for a re-check, E3 for a drift, E4 for a research question)
and the ranking rebuilt (`audit/merge.py`); then every report finding still without an open row was given one - a row closed
at an earlier wave whose claim drifts again reopened (Ochiba's clump inside the page window, closed at wave 10; the belt's
continuous planting, wave 47; eleven more), and the procedure rows `audit/scope.json` marked deferred that the report counts in
scope (the country shrine's three, the manor's universal shrine, the divider gate, the latrines by zone) set in scope: 243 open
rows, every in-scope finding of the report among them (measured 2026-10-10: 0 findings without an open row). The 34 open rows that are no claim at all - review and cohort
findings, Sawada's zigzag, the 20/40-household reach rows, the held door band - stay on the list under T99. This batch takes the
cheapest tier first, as 328's did: the MISLABELED, UNCLAIMED and CANNOT-TELL claims - labels, new claims, fuller re-checks, no
drawn change. A finding whose fix is a drawn change (the compound shrine's grove) or a code change (a label the code
contradicts) waits for the wave that makes it. Docstring and comment edits change no engine key (the gate's short-circuit), so no
map moves and no review occasion is owed.

### Wave 115 (T06) - the procedures' four relabels

- `docs/building-programs.md` `#divider gate on the axis`: a GUESS recorded on 0090's drawing page (new sentence: the gate
  behind the office hall, no page placing a jin'ya's middle gate); "customarily on the main axis" goes from the program's text.
- `#latrines by zone`: a GUESS on 0101's drawing page (about one per part of the compound, three or four, near service gates).
- `docs/buildings.md` `#named court spine`: cites 0116's drawing page (the open courts), not 0099.
- `#office front, residence rear`: a DEVIATION on 0090's drawing page (the yamen's order kept as a deliberate simplification;
  Takayama's residence stood beside the office); "universal in both traditions" goes from the text.
- Owed: impl-drift on the six (the four and the two below); the record checks the 0090 sentence owes (record-format, quote-check on its block, the pop-ups
  naming the page triaged).
- A re-check's own finding is answered in the same wave: the manor's two-court bullet drops "never through the divider
  gate" (impl-drift: it left formal visitors no way to the house, against 0104's drawing page), and the alley behind the
  hall, which the bullet names, is claimed UNRESEARCHED.

### Wave 116 (T07) - the hamlet's ways and hinterland labeled

The MISLABELED and UNCLAIMED claims under `l7r/diagram/hamletgen/` (ways, hinterland, plan, rows): each label set to what
its finding says (a GUESS on the drawing page that records it, CONVENTION, UNRESEARCHED where unsearched, NONE for plumbing),
each UNCLAIMED decision given its claim; where a finding says the page answers the question, the claim cites the page. A finding
that needs the code changed (a value the page contradicts) is not relabeled: it stays for its DRIFTED wave.

### Wave 117 (T08) - the settlement, waterfields, labels and interactive claims labeled

The same, for `l7r/diagram/settlement/`, `waterfields/`, `labels/` and `interactive/`.

### Wave 118 (T09) - the CANNOT-TELL re-checks

Each of the 11 CANNOT-TELL claims re-checked by impl-drift with the reader or page it said it lacked added to its bundle
(`make claims-bundle UNITS=`, the named function or page beside it); a claim that then reads DRIFTED joins the DRIFTED work.
A re-check that finds a departure the drawing page never recorded reads DRIFTED and joins the DRIFTED work; the session
never records a DEVIATION to close it (328's exception path, amendment 5). The polder kept out of the random roll
(`ROLLED_ARCHETYPES`) is one, with the dike-pond block beside it: 0019's drawing page names both a known gap, and the row
stays open until the polder and the dike-pond pass their cohort and are rolled.

## Batch 3: the hamlet's code brought to the research

**The work list** is 328's ranking brought current (2026-10-11): batch 2's re-checks closed 39 more rows (36 whose unit
now carries no UNCLAIMED or MISLABELED finding, or whose claim reads IN-STEP; three UNCLAIMED rows whose decisions now
carry claims), marked wave 118 in `audit/waves.json`; then `audit/scope.py` was re-run on today's cache (328 FR-010, the execution
record) and re-marked 14 more open rows `scope: deferred` (the paddy and ribbon builders, a town's kiln, a city's matrix
permissions among them; `scope.py` now counts `docs/building-programs.md` among the Mode A procedures, which it had sent to
deferred), leaving **183 open rows** in scope (126 E3 DRIFTED). `make claims-report` shows the deferred
units' claims as DEFERRED (158).

**Three rules for every wave of this batch:**
- A row's fix text that says "label it a DEVIATION and have the drawing page record it" predates the plan review's
  ruling (batch 2, W118-2): the code is changed to match the page (328 FR-004). Where a change still looks wrong, the
  exception goes to `spec-fidelity` with the GM's words and is recorded only if ruled LEGITIMATE; otherwise the code
  is changed to match the page.
- Engine discipline: `make quick` per fix; reroll only the maps the change reaches and compare their manifests with
  `git diff HEAD`; one `impl-drift` per wave over the claims the wave's code edits re-owe; the review occasions a
  wave declares in `tasks.md ## Occasions` dispatched on a green gate, with no engine edit while one runs; one `make done`
  at the batch's close with the timing pair, `perf-audit` on a band of 1 or more.
- A row whose unit `audit/scope.py` derives DEFERRED (328 FR-010, re-run on today's cache) leaves the work list: its
  ranking row is re-marked `scope: deferred` and no wave takes it.

**Not in this batch:** the two held rows (the door band, `fixture_quota`: the GM's); `oblique_at`'s square crossing,
which waits on the E4 research row beside it (`law_water.py::oblique_at#a channel crossing at its way's angle`, named in its
`after`); and `settle.py::_unkinked#a returning leg of 40 ft or more` with `settle_shapes#no hairpin or zigzag`, which cuts
through it: 0081's drawing page forbids the hairpin a returning leg of 40 ft or more leaves and gives the cut only under
40 ft, its folded spur and joining stub named exceptions to that threshold, so what a longer leg becomes is a research
question (both rows re-tiered E4; meanwhile the code keeps its cut and the claim its GUESS label). And
`comb.py::_comb_draw_source#feeder brook width`: its E1 fix (the brook in feet, `self.px(7.0)`) is in the code, and what
reads DRIFTED today is the E4 question beside it, `#feeder brook width against the ladder` (0068's ladder against its
question page's 7 ft GUESS and 0059's 7 ft, with the "narrower than the head race" bullet), named in its `after`; the code
and both pages stay as they are meanwhile. The three waves take
every E0-E2 row in scope that is neither held, measured DEFERRED nor waiting on research.

### Wave 119 (T10) - the hamlet's lanes

- `serve.py::lay_door_paths#door path off a grove band`: 0036 lays a lane through a grove band "with a footpath's
  clearance and some working room kept off the trees on each side" (about 22 ft of a 36 ft opening: about 9.5 ft each side
  of a 3 ft tread); the code's 0.5 ft margin becomes that working room (`GROVE_WORKING_ROOM_FT`, measured off the band's
  rect, which bounds the trunks), and the claim cites 0036. Measured on the hamlet cohort before it is kept: a farm the wider
  berth leaves unreached is a conflict put to `spec-fidelity` (rule 1).
- Measured and ruled (2026-10-11): at 9.5 ft cohort seed 22's two row farms were walled in between their dooryards and a
  neighbor's band. `spec-fidelity` ruled the 9.5 ft stands for every band (no per-farm fallback, no reading of the page as
  "openings only"), and that widening 0036's 32 ft between groves to the 46.1 ft the router's grid wants would reword the page
  to fit the code: the pinch is the door router's 10 ft lattice (2 x 11 ft + 2.41 cells must fit the gap). So the door router
  asks again on a finer lattice, `DOOR_FINE_CELL_FT` (4 ft, at most 4.1 ft for the 32 ft gap), only where the coarse one finds
  no way - the derivation `dry_exit.GROVE_EXIT_CELL_FT` records, paid where needed. The lane room stays 32 ft and 0036 is
  unchanged. Measured: the 48-seed cohort and its six pinned rows pass but seeds 10 and 20, both refused at HEAD before the
  change (the baseline 52/54).
- Kashikawa, rerolled, was refused for a "needle" the law found where two door paths end on the skeleton at the point it
  bends: a face 0.09 ft round, three lanes noded a hair apart, no ground at all. A pre-existing defect of the law's face test
  (constitution XIV): `law.needle_loops` skips a face whose perimeter is under `NODING_SPECK_FT` (1 ft); a real needle runs
  the length of its ways. Kashikawa then rolls, its door paths moved; the other four pool hamlets are unchanged, and the
  cohort with the rule matches the baseline (52/54).
- Maps: every pool hamlet is rerolled; a hamlet whose paths change owes no glyph-check (no glyph is redrawn) - the lane
  law's acceptance sweep and the cohort hold the change.

### Wave 120 (T11) - the hamlet's ground

- `hinterland/parcels.py::_beyond_the_fields#no wood below the houses`: 0077's drawing page refuses only "a wood seated below
  the houses, past the fields and beside a river or marsh". The wood follows the page's two tiers alone - the slope higher
  than the field beside it, then the level beyond the fields (`woodland_tier` no longer ranks by the houses) - and a seat is
  refused only where it is below the houses' median height and within `LOW_BY_WATER_FT` of a river's course or a marsh
  (`low_by_the_water`; the marsh keep-out holds a square only off the marsh itself, so a square flush against it had passed).
  "Beside" has no figure on the page: 46 ft, the width over which the maps draw reeds and grass interleaving at a marsh's
  edge, recorded on 0077's drawing page as a GUESS (its record checks owed), and the claims label it so.
- `_knobs.py::_kosatsuba_seat_ok#bridgehead and shrine withheld`: 0190 attests boards at bridge ends with no size
  qualifier; the bridgehead joins the seat's forms where the settlement has a bridge (every pool hamlet has four to ten).
  The shrine precinct stays withheld, its claim giving the reason: no kept map draws a precinct (the pool hamlets' only
  shrine is a dooryard hokora). The new form is anchored at the settlement's widest bridge, a brook's before a ditch's plank, and of two alike
  the one nearest the houses (`bridgehead_anchor`): which of a village's bridges held its board no page says, so 0190's
  drawing page records the choice as a GUESS. The form takes its title-card label ("at the foot of a bridge") and a pop-up
  of its own (`choice/kosatsuba_seat--bridgehead`, written from 0190 as its three siblings are), which owe the record
  checks a new pop-up and a drawing-page sentence owe.
- Maps: the pool hamlets rerolled. Occasions: the board's new bridgehead seat and the wood's newly allowed ground are
  elements re-placed (`placement-changed:`, a glyph-check each on one hamlet where the roll moves them).

### Wave 121 (T12) - claims the rows name

- `farm_fixtures.py::KURA_PARTS#west annex`: the row is the claim `#west annex` already carries; the unit re-checked
  clears it.
- `belt_law.py::BeltReading.holes#continuous planting`, `stands.py::village_grove#clump inside the page window`,
  `bundle.py::_bundle_layout#south band off an unkept yard`: each claim worded to what the code does and re-checked; a
  claim that then reads DRIFTED joins the DRIFTED work.

## Landing by batch (375's D18)

374 is the remainder of 328's ranking, too long for one clone, so it lands batch by batch and stays open between them:
`tasks.md` holds the current batch's tasks and one standing task, T99, for the batches still to come. A batch whose
decisions need no new ruling adds its tasks under its own plan section, decided per task (`make decide`).

**Lands open**: T99

## Performance bookends (constitution VI)

| batch | waves | pair | gate | close |
|---|---|---|---|---|
| 1 | 112-114 | none owed: the batch's engine code is the Mode A draft (`compound.py`, `compound_parts.py`, `compound_model.py`: the kitchen ell, the corridor gone), `pack_audit` (`veranda_depths`, the hearth not a door) and `buildings/types.json`'s kitchen band - none in what the timing pair rolls (the hamlet's stages), as 372's batches 3-5 recorded | green 2026-10-10 at engine key 026828713522 | the review occasions running (three building-reviews, two glyph-checks); escalation-check 3 keep |
| 2 | 115-118 | none owed: the batch's engine edits are `Research:` docstrings and claim wording only (no engine token moves, the maps unchanged: `git diff origin/main -- pool/` empty after the gate's roll) | green 2026-10-11 on the merged tree | the record and claims checks answered; no review occasion (no sheet or glyph moved) |
