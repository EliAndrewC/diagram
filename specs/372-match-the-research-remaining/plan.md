# Implementation Plan: the rows feature 328 left open (feature 372)

**Spec**: `spec.md` | **Request**: `request.md` | **Model**: `specs/328-match-the-research/plan.md` (its D1-D4, its wave cycle,
its batch close and its bookends) - this plan records only what differs and each wave's amendment.

## Summary

The work list is 328's ranking's open in-scope rows at wave 97, in ranking order, with the findings carried at its landing
(spec, "What it carries"). Waves are numbered on from 328's (the first is wave 98), so 328's `audit/waves.json` stays the one
column; this feature's measurements are its own `measurements.json`, its decisions its own spec's table.

## Constitution Check

As 328's (XII research, XIII no known regressions, XIV fix where found, XVI the literal thing); nothing new is owed.

## The cycle (328's, unchanged)

Edit -> test-file -> `make map` for each map the wave changes (the pool's hamlets diffed against HEAD's manifests; a Mode A
sheet's `make pack-audit` before and after) -> `make cohort N=48` when engine code changes (52/54 at the start; a newly failing
seed is a regression, reverted with its measurement) -> `impl-drift` on the owed claims -> records -> `make quick` ->
`spec-fidelity` -> tick -> commit. A batch of 4-5 waves closes with `make done`, its occasions, one timing pair and its
`perf-audit`, and LANDS (spec FR-003).

## Wave 98 (amendment 1, 2026-10-10) - batch 1

- **Scope**: `docs/buildings.md::Latrines and the rear service strip#privy size` (328's ranking, E3: the procedure allowed
  14-20 px, ~5-7 ft, and the hand sheets drew up to 22 px; 0101's drawing page draws a privy 5 ft square, a one-seat privy,
  its size a GUESS). Sheets redrawn (328's FR-009 by FR-002): **Hayakawa** (5 privies), **Ochiba** (4), **Ubame** (5, two in the residence's one group) - 14 privies, every one 15 x 15 px,
  kept against the wall or house face its nearest edge stood on (each anchored on the side with the smaller measured gap; a
  privy between two faces centered). The generated sheets (the county example, the roundtrip test) and Hoshigaoka already
  draw 15 px.
- **The section's re-check** (impl-drift, 9 claims): `#privies away from water` (328's E4 row) MISLABELED - relabeled GUESS
  at 0101's 15 ft from a well, the food-prep half UNRESEARCHED, as its own claim; three unclaimed decisions claimed (the
  privy's glyph, a CONVENTION; the rear strip as the service side and its storehouses, 0091). `#residence privy attached` and
  `#servants in the rear strip` re-read DRIFTED, as ranked (E3), left for their place in the run.
- **Records**: the procedure's claim (GUESS, 0101 drawing) and its body text; each sheet's notes history; `make pack-audit`
  before and after unchanged on all three sheets (m:wave98-privy-size).
- **Occasions**: glyph-redrawn: latrine on ubame-magistracy (one map stands for the three; the same glyph, the same size).
- **Verification**: the three `make map` runs (REGENERATED, no untagged ink), the pack audits, `impl-drift`, `spec-fidelity`.

## Wave 99 (amendment 2, 2026-10-10) - batch 1

- **Scope**: `docs/buildings.md::Approaches and surroundings#boundary pillars` - 0083's drawing page gives about 1 to 1.5 ft
  of shaft, up to about 3 ft with a plinth (a GUESS); **Ubame**'s two pillars, 3 x 3.7 ft, drawn 3 ft square (the plinth form).
  IN-STEP under impl-drift.
- **Held, its place kept**: `Fire-water tubs#one tub per wooden building` (row 14) waits on `#senior retainers housed apart`
  (row 21, its `after`): row 21 may move the karo's house out of the walls, and row 14's tubs are added "if they survive".
  Wave 99's first draft added Ochiba's two tubs ahead of it and called Ubame's 19 the rule's own count without a measurement;
  plan review round 2 (BLOCKED) took both back - the tubs removed, the claim restored - and row 14 is taken after row 21, with
  Ubame's tubs counted per building then.
- **Passed over, its place kept**: `Walls and gates#main gate posts` (E3) - 0092's 2 ft post is thinner than the 3 ft wall it
  ends (6 px against the wall's 9 px), so drawn as written it would vanish into the wall's ink; how a post shows at a wall's
  end is a drawing question for the row's own wave, not taken here.
- **Records**: m:wave99-pillars; Ubame's notes (the history line; its point-glyph line no longer calls the stones markers).
- **Occasions**: glyph-redrawn: boundary stones on ubame-magistracy.

## Wave 100 (amendment 3, 2026-10-10) - batch 1

- **Scope**: `docs/buildings.md::Approaches and surroundings#cart lane to a side gate` - 0082's drawing page takes a cart lane
  at about 6 ft (a GUESS: the hand cart's 2.5 ft bed and room for its wheels). **Hayakawa**'s lane from the east postern to the
  bank street (10.7 ft) and **Ubame**'s run of the Fox road to the cart gate (9 ft) drawn 6 ft (18 px); the gates themselves
  keep their widths. IN-STEP under impl-drift.
- **Records**: m:wave100-cart-lanes (every pack-audit check OK on both sheets); both sheets' notes and comments.
- **Occasions**: glyph-redrawn: road on hayakawa-magistracy (the lane narrowed; Ubame's the same glyph).

## Wave 101 (amendment 4, 2026-10-10) - batch 2

- **Scope**: `docs/buildings.md::Walls and gates#gatehouse` (E3, flagged deviation-tempting: 18 x 12 ft is the one guardroom
  measured, the page's 40 ft a guess). 0093's drawing page draws both forms 2 ken (~12 ft) deep, measured, and a gatehouse of
  its own about 40 ft long, a GUESS a fifth over Takayama's measured ~400 sq ft; the fix follows the page, as the ranked fix
  says, not the tempting deviation. **Hayakawa**'s and **Ubame**'s gate ranges 14 -> 12 ft deep, the north face moved in, the
  south face kept on the wall line (the doors and Hayakawa's passage follow); **Ochiba**'s gatehouse 18 x 12 -> 40 x 12 ft,
  grown east into open outer court (nothing stood within 80 px).
- **Knock-on**: Ubame's tub at the range's north face stood 4.0 ft off once the face moved in (the pack audit's
  fire_water_adrift); moved in with it.
- **Records**: m:wave101-gatehouse; the procedure's Gatehouse paragraph and claim; three sheets' notes.
- **Occasions**: layout-revised: ochiba-magistracy (the gatehouse more than doubled); glyph-redrawn: gatehouse on ubame-magistracy.

## Wave 102 (amendment 5, 2026-10-10) - batch 2

- **Scope**: `docs/buildings.md::Latrines and the rear service strip#residence privy attached` and the checklist row that waits
  on it (`Checklist for a new diagram#privies and rear strip`). 0101's drawing page gives a house two privies, the guests' at
  the rear of the reception room and the family's at a back corner by the living rooms (a GUESS); the procedure gave one.
  The bullet, the checklist line and both claims now say two. Sheets: **Ochiba** draws its second, the guests', attached to the
  reception room's east face at its rear corner, clear of the garden (its first captioned `family privy`); Hayakawa and Ubame
  already drew both (m:wave102-two-privies).
- **The section's re-check** (impl-drift, 25 claims, 23 IN-STEP): the checklist claim relabeled (two privies built into the
  house a finding, the family's place and the ~3-4 count guesses, the rear strip 0091's guess); two unclaimed decisions
  claimed (an entrance drawn on every lodging, UNRESEARCHED; the checklist's tub seat, 0100). `#servants in the rear strip`
  (328's E3 row) re-read MISLABELED; a relabel was drafted and taken back at plan review (W102-servants-relabel, NOT
  LEGITIMATE: the ranked fix is a move - the servants to the street-side ranges, the gate range or under the main roof, the
  ~10 dropped - and 0115 and 0091 disagree, a NEEDS-RESEARCH question or a knob, not a relabel); the row stays open as ranked,
  with `#second rank` behind it.
- **Records**: m:wave102-two-privies; Ochiba's notes.
- **Occasions**: placement-changed: latrine on ochiba-magistracy (a privy new to the house's formal side).

## Wave 103 (amendment 6, 2026-10-10) - batch 3

- **Scope**: `docs/buildings.md::Approaches and surroundings#road at the gate` - 0088's drawing page draws the road at a
  compound's gate as the road the compound stands on, at that road's width (the Imperial road 30 ft, a lesser highway 15-24
  ft), with no wider ground before the gate. **Ochiba**'s approach, labeled the Imperial road but drawn as an 8 ft lane into
  the gate, becomes the Imperial road at 30 ft running east-west past the gate (its direction a GUESS), the gate opening
  straight onto it with the threshold stones and the notice board on its near edge; the sheet extends 32 px south.
  **Hayakawa**'s street and **Ubame**'s road read as the lesser highways their compounds stand on (a GUESS that each is one),
  12 -> 18 ft, each redrawn the way Ochiba's is: running past the gate across the sheet (Hayakawa's to the bank street,
  Ubame's turning south off the sheet short of the border wall), the gate opening straight onto it. No road now ends at a
  gate, so the GM's B23 (2026-10-01, a road no wider than the gate it feeds, `pack_audit`'s `gate_feeds_its_road`) holds
  with nothing narrowed. A first draft gave Ochiba a 9 ft verge, cited the 15-24 ft as a town street's, and narrowed
  Hayakawa's and Ubame's streets to their gates for the last 13 ft; impl-drift and plan review round 1 (W103-narrow-to-gate,
  NOT LEGITIMATE: it put the gate's width back at the gate) took all three back.
- **A tool defect fixed where found** (XIV): `pack_audit`'s crop check (`shared.ink_bounds`) read a stroked path or line at
  its centerline, so the 90 px road counted 45 px of its own ink as an empty margin; a stroke is now ink half its width each
  side (a unit test, red on the old code). Every sheet's crop check stays OK.
- **Next**: `#notice board size` (row 13, after this row) - the gate board as 0190's roofed frame, 16 x 6 ft, on a stone footing
  inside a fence, re-laid on the verge and beside the streets.
- **Records**: m:wave103-road-at-the-gate; the procedure's Road to gate bullet and its two claims; three sheets' notes.
- **Occasions**: glyph-redrawn: road on ochiba-magistracy (the Imperial road at 30 ft past the gate; the streets on Hayakawa and Ubame the same glyph).

## Wave 104 (amendment 7, 2026-10-10) - batch 3

- **Scope**: `docs/buildings.md::Approaches and surroundings#notice board size` (row 13, after row 12). 0190's drawing page draws
  a board as a roofed frame 16 x 6 ft, its long side to the road, on a stone footing about 2 ft wider all round with a fence
  line at its edge (the Kanagawa board); the sheets drew ~7 x 3 ft gate boards and a ~9 x 4 ft bounty board. All four boards -
  **Ochiba**'s, **Hayakawa**'s and **Ubame**'s two - drawn so (a 48 x 18 px frame with a ridge line for its roof, on a 60 x 30 px
  stone footing with a dashed fence line), on the road's far verge straight across from the gate: the gate opens straight onto
  the road (0088), so beside the road means across it (0190: a board stands beside the road, never in it); Ubame's bounty board
  stands beside its notice board on the same verge, west, so the pair does not mirror about the gate. A first draft stood the
  boards on the road's near edge; the notice board's glyph check (round 1, NEEDS-WORK, F1) found them in the road.
- **The board's limit**: `compound_model.NOTICE_BOARD_MAX_FT`, the engine's one predicate behind `pack_audit`'s
  `notice_board_adrift` (feature 287 H29b), was 20 ft, set while boards stood against the wall and on no page; a board facing
  its gate across the Imperial road's 30 ft stands beyond 20 ft, so it is 40 ft, this project's figure (UNRESEARCHED). The two
  frozen red fixtures' misplaced boards moved farther out (Ochiba's 90 px, Hayakawa's 80) so the check still fires on them; the
  generated draft's own board, 8 ft from its gate, is unaffected. Ochiba's road edge set on the wall's outer face (the road
  check's F6), closing a half-foot strip under the wall.
- **Records**: m:wave104-notice-boards; the claim; three sheets' notes (their point-glyph lines no longer give 7 x 3 ft).
- **Occasions**: glyph-redrawn: notice board on ubame-magistracy (the same glyph on all three sheets).

## Wave 105 (amendment 8, 2026-10-10) - batch 4

- **Scope**: `docs/buildings.md::Outer court (administrative / public)#tax archive size`. 0100's drawing page sets an office's
  records storehouse at no more than ~450 sq ft (the one measured, Takayama's book storehouse, ~446 sq ft, served a whole
  province - accurate as a ceiling), its shape about 24 x 18 ft (a GUESS); the sheets drew 32 x 26-28 ft. The tax archive on
  **Hayakawa**, **Ochiba** and **Ubame** drawn 24 x 18 ft (72 x 54 px), each door face where it stood; the procedure's bullet
  (its strongroom role now within the same ceiling) and claim, and the drawing page's bullet that recorded our plans drawing it
  larger (removed: the plans no longer do).
- **Round 2 (plan review BLOCKED W105-band and W105-page-bullet)**: the ranked fix names "the band and prose" too, and the
  generated draft still drew 34 x 34 ft. Now: the `tax_archive` band in `types.json` is w 18-24 by h 12-18 ft (it was 20-48 by
  10-36, which admitted four times the ceiling); `compound.py`'s draft archive and its claim 24 x 18 ft; the roundtrip sheet's
  program (Ochiba's measured sizes) 24 x 18 ft. The draft then covers 32%, under `pack_audit`'s 33% floor - a floor read off
  0116 before its 2026-10-01 correction to 30-42% (Takayama's measured ~31% the bottom), so it follows the page at 0.30
  (fixed where found; the report line with it). The draft's hearing court, a fixed zone, re-centered on the office hall the
  smaller archive let slide east (test_compound's own rule). The drawing page's bullet stays removed: no plan now draws the
  archive larger. Left as found: the draft's gatehouse, 18 x 12 ft where 0093 now draws ~40 ft - at 40 its stables find no
  seat on that wall; it is the draft's own row (`docs/building-programs.md` walled enclosure), recorded at its line
  (m:wave105-draft-and-band).
- **Batch 4's first gate** failed one test: the 26 frozen red fixtures under `tests/fixtures/` copy Ochiba's or Ubame's old
  sheet, archive and all, and the tighter band made `ochiba-no-scale-red.svg` fire `size_bands` beside the one check it exists
  for. Each fixture's archive brought to 72 x 54 px (its east face kept), so each still fires only its own check (the tools
  suite 513 passed).
- **Left as found**: the pack audit reads the gaps round the smaller archive LOOSE (a heuristic note, not a check) on
  Hayakawa and Ubame; the open ground is outer court.
- **The record checks the drawing page's edit owed**: four pop-ups citing 0100's drawing page re-checked (modal-depiction): the
  fire-water tubs clean; the tax archive, granary and storehouse each given what their tabs left out (the legibility spacing
  of 0116, the granary's rank below the residence, the storehouse door's convention and its 0117 link; "the one kind of
  building made not to burn" said of every plastered storehouse), then clean on round 2. The section's claims (35): the tax
  archive IN-STEP; one unclaimed decision claimed (the kura granary's door on the apron, UNRESEARCHED); five DRIFTED rows read
  as ranked (barracks, forecourt, the stables' three), left for their places.
- **Records**: m:wave105-tax-archive; three sheets' notes.
- **Occasions**: glyph-redrawn: tax archive on hayakawa-magistracy (the same glyph on all three sheets).
- **Batch 4's close, building-review round 1 of the draft** (NEEDS-WORK): E1, a regression of this wave - the outer court's
  yard, a zone drawn after the hearing court, still began where the court had ended before it slid east and painted out
  its east end; the yard now starts at the court's east edge, and `tests/test_compound.py` holds that no two of the draft's
  zones share ground (m:batch4-county-yard-off-the-court). E2, the draft's notes stale (the archive's old size, no entry for
  the wave, the middle gate's old reason, the archive's proportions unlabeled): all four fixed (m:batch4-county-notes-current).
  E3, the staff long-house squat against 0097's rowhouse form, predates the wave and was tracked nowhere: a found row, E3,
  in the ranking (`audit/found-wave105.jsonl`). E4, the barracks, is ranked row #barracks, left for its wave.

## Wave 106 (amendment 8, 2026-10-10) - batch 5

- **Scope**: `docs/buildings.md::Fire-water tubs#tub against its wall`. 0100 keeps standing water at a wooden building's
  ENTRANCE; the sheets and the draft seated each tub at an eaves corner or along its court face. Now each tub stands beside a
  door of its building - ONE rule, not a knob: the roof seat 0100 also attests is inside the footprint, which the GM's
  2026-07-25 ruling keeps every tub out of, so the entrance is the one seat a plan can draw.
- **Check first** (`pack_audit` `tubs_off_their_doors`, the draft's own predicate `compound_parts.tub_by_its_door`): a tub held by
  a building's eaves stands within `TUB_DOOR_MAX_FT` of a door the sheet TAGS on that building's outline. Two readings were
  wrong on the way and are recorded at the check: a small dark rect took a hearth for a door, and a door deep inside a
  footprint is an inner room's. A building that tags no door is not judged. Measured at main: Hayakawa 7 of 13 tubs off,
  Ochiba 5 of 10, Ubame 9 of 19, Hoshigaoka's 4 unjudged (no door tagged) (m:wave106-tubs-at-doors). Its red fixture
  `ochiba-tub-off-door-red.svg`.
- **The limit, a CONVENTION**: the kitchen's two tubs at one door, the second beside the first where the door's other side is
  taken (the round-trip sheet's bath abuts the kitchen below its door), set it - the door's approach, the draft's clearance and
  two tub widths put the far tub ~10.2 ft off; 10.5 ft (compound_model, beside the constant; 0100's drawing page; docs/buildings.md).
- **The draft** (`compound_parts._point_features`): the doors are seated before the tubs, so each building's doors are kept and its
  tub tried beside one first (`beside_door_fracs`, nearest first, past the door's held approach), then round the corner
  nearest the door where the face is too short (`round_the_corner`: the gatehouse's 12 ft end), then the court face as before.
  The county draft and the round-trip sheet pass with every tub at a door.
- **The hand sheets**: 21 tubs moved, each beside a door of its own building, every move audited; Ochiba's residence tub,
  whose only tagged door (the family's, west) stands in a notch between the privy and the kitchen, stands at the notch's
  corner under both eaves, ~5 ft from the door. **Hoshigaoka**: its two doors tagged, two tubs beside each (it drew one at each
  corner). The count rows (`#one tub per wooden building`, held; the country shrine's `#fire-water` count) are not this row.
- **Record**: 0100's drawing page gained the rule's bullet; the fire-water-tubs pop-up says it; the checklist and the country
  shrine's fire-water line say it (their sections' claims re-checked). The checks: quote-check SUPPORTS, record-format clean
  (its wording suggestion, "the kitchen's two one either side", left: one more visible edit re-owes five checks), modal-depiction
  clean on the four pop-ups 0100's drawing page feeds (the storehouse's ken given its feet and the archive's "pale" dropped, each
  as the check proposed; the archive's crop shows the page's highlight, not the drawn fill - the modal-bundle gap this spec lists).
- **Plan review round 1 (BLOCKED, decision c)**: a building that tagged no door left its tub unjudged - 23 of 77 tubs, some
  still at eaves corners. Now the check FAILS a tub at a building with no entrance, reads a door drawn up to 4 ft off its wall
  (Hayakawa's guest house's was 8 px out), and takes the reception's shoe stone, declared `id="shoe-stone"`, as its entrance
  (R07, research 0104: no genkan - no door is drawn on the veranda); a tub at a bath, entered from the house, is not judged by
  a door (decision c3). The hand sheets are brought to the draft's rule that every building draws its door ("a building with
  no drawn door reads as sealed", pass 5): doors drawn, each on the face toward its approach or yard, in each sheet's small
  dark door style (nine doors: Hayakawa 2, Ochiba 2, Ubame 5 - Ubame's shrine's on its south face, toward its approach torii, after plan review round 2); the drafts' cell, cinnabar workshop and clerks' room join `DOOR_KINDS`. Ten more tubs moved; the bath exemption holds only where the bath is the tub's nearest building (round 2). The roof seat
  0100 also attests is not drawn (the GM's footprint ruling), now on 0100's drawing page and in the Decisions row; the page's
  bullet takes the record-format check's wording too, in the same edit. m:wave106-tubs-at-doors restated per sheet, strict.
  Hoshigaoka's `glyph-check--door` and `size-audit--door` units were run all the same (the tooling owed them: the tag is
  new to the sheet, though its door ink predates the wave): both PASS.
- **Records**: m:wave106-tubs-at-doors; the six sheets' notes.
- **Occasions**: placement-changed: fire-water tubs on ubame-magistracy (every hand sheet's tubs re-seated); layout-revised:
  county-magistracy-example (the draft's tub seat).

## Wave 107 (amendment 8, 2026-10-10) - batch 6

- **Scope**: three E0 rows wave 106's impl-drift found in `docs/building-programs.md`, the claim lines alone: `#two-court zoning`
  relabeled DEVIATION on 0090's drawing page (residence-behind-office is its deliberate simplification; at Takayama the residence
  stood beside the office); `#commuting clerks` relabeled DEVIATION on 0113 (an intendant's clerks lived inside the compound; the
  setting's commuting scribes are canon); and the table's rule that a hill shrine's village keeps its burial ground apart claimed as
  0236's drawing page records it, a GUESS (no source says so outright; plan review: not UNRESEARCHED, and not 0226 as the ranked
  fix had it - 0226 says nothing of a hill shrine). The clerks' claim points at 0113's drawing page, which records the deviation.
  No sheet, no engine code.
- **Records**: the claims' impl-drift; waves.json.

## Wave 108 (amendment 8, 2026-10-10) - batch 6

- **Scope**: `docs/buildings.md::Inner court (private / sacred)#bath`. 0105's drawing page draws the bath 10 x 8 ft, a GUESS (no page
  gives a bath's size; drawn small so the whole house keeps to the 49-tsubo residence); the procedure said 12-15 ft. **Ochiba**'s
  bath (13 x 11 ft) and **Ubame**'s (10 x 11 ft) drawn 10 x 8 ft against their kitchens, each bath's tub moved to stay on its yard
  side; the procedure's claim and text say 10 x 8 ft; the band in `types.json` tightened from 8-22 to w 8-18 by h 8-12 ft.
- **Hayakawa's bath kept at 18 x 12 ft**: its notes roll it as a resident particular ("superstitious Hajime keeps TWO well-tended
  modest shrines and an enlarged bath", knob 7), so the band admits it. The particular is kept and recorded, a GUESS, on 0105's drawing page (plan review: the
  choice between two of this project's readings is the session's to make, not the GM's - the GM's 2026-10-02 ruling - and the
  49-tsubo concern was unmeasured: Hayakawa's house is ~163 tsubo without its bath, which adds ~4); the procedure claims it there.
  The band's height floor raised to 8 ft (the 10 x 8 bath either way round). The ranked fix named only Ochiba and Ubame; the draft already drew 10 x 8.
- **Records**: m:wave108-bath-size; the two sheets' notes.
- **Review**: glyph-check bath (Ochiba) PASS round 1; its nitpicks left - the bath now nearer a door tab in size, its steam arcs
  drawn for the old room (the east one ~2 px inside the wall's stroke), its tub on the room's center line.
- **Occasions**: glyph-redrawn: bath on ochiba-magistracy (the same change on Ubame).

## Wave 109 (amendment 8, 2026-10-10) - batch 7

- **Scope**: three E0 rows this batch's impl-drift found in `docs/buildings.md`, the claim lines alone: `Wells#bath-area well`
  relabeled GUESS on 0105's drawing page (that the kitchen well serves the bath is 0105's own reading), with the optional fourth
  well "only for very large compounds" claimed apart, UNRESEARCHED; the residence along the inner court's north range claimed on
  0091's drawing page (the garden before it, the shady north band behind it); and the hand plans' karo's house inside the compound
  claimed as the GUESS 0106's drawing page records. No sheet, no engine code.
- **Records**: the claims' impl-drift; waves.json.

## Wave 110 (amendment 8, 2026-10-10) - batch 7

- **Scope**: the E0 found row `research/questions/0105-baths-furo.notes.html#bath-building-absence`: the absence note said "The
  Matsue samurai residence lists its yudono by name only", a claim about a named, unlinked page an absence note may not carry
  (quote-check, CLAIM-FROM-UNREAD); the sentence removed from both 0105 notes files, the note's stated silence unchanged.
- **Records**: the note's quote-check and record-format; its source-reader answered as an absence note citing no page.

## Wave 111 (amendment 8, 2026-10-10) - batch 7

- **Scope**: the found row `docs/buildings.md::Wells#kitchen well` (E1). The procedure set the kitchen well "inside or immediately
  adjacent to the kitchen"; 0105's drawing page set it "past the bath, as far as 20 ft out". The hand sheets draw it inside the
  kitchen on its earth floor (Ochiba's "on the doma since pass 3"), the generated plans past the bath. No page places a samurai
  kitchen's well, so neither form is research-backed and the ranked fix's "follow the drawing page" would move three wells on no
  evidence: the drawing page now records both seats, a GUESS, and the procedure and its claim say the same. The well pop-up says
  the kitchen's well stands inside the kitchen or past the bath. (Plan review round 1: only Ochiba's well stands on a doma -
  Ubame's is inside the kitchen off its doma, Hayakawa's kitchen has none - so the seat is "inside the kitchen", the doma named
  for Ochiba alone.) No sheet, no engine code.
- **Records**: the claims' impl-drift; the record checks the page edit owes.

## Performance bookends (constitution VI)

| batch | waves | pair | gate | close |
|---|---|---|---|---|
| 1 | 98-100 | none owed: the batch changed no engine code (hand sheets, their notes and the procedure only), so the engine key is the landed one and a pair would time the same code | green 2026-10-10 (already verified on the landed engine key) | closed: glyph checks latrine, boundary stones, road PASS; escalation-check |
| 2 | 101-102 | none owed: no engine code changed (hand sheets, their notes, a modal, the procedure) | green 2026-10-10 on the landed engine key | closed: glyph checks gatehouse (Ubame) and latrine (Ochiba) PASS; Ochiba's building review NEEDS-WORK (E1: the gatehouse's pop-up and building-programs.md gave the old size - fixed, the pop-up's record checks clean on round 3) then PASS round 2 |
| 3 | 103-104 | none owed: the batch's engine code is a review tool (`pack_audit`'s crop check) and `compound_model.NOTICE_BOARD_MAX_FT`, read only by the generated compound draft's board check and the pack audit - neither in what the timing pair rolls (the hamlet's stages) | green 2026-10-10 at the board limit's engine key | closed: glyph checks road (Ochiba) PASS and notice board (Ubame) NEEDS-WORK then PASS round 2; the border note box moved below the road (round 2's F7); escalation-check |
| 4 | 105 | none owed: the batch's engine code is the Mode A band (`buildings/types.json`), the generated compound draft (`compound.py`), its round-trip test generator and `pack_audit`'s coverage floor - none in what the timing pair rolls (the hamlet's stages) | green 2026-10-10 at engine key cb24cd5f61e7 | closed: glyph check tax archive (Hayakawa) PASS round 1 and 2; building-review county-magistracy-example NEEDS-WORK then PASS round 2 (the yard off the court, the notes; the long-house a found row); escalation-check |
| 5 | 106 | none owed: the batch's engine code is the Mode A draft's tub seat (`compound_parts`, `compound_model.DOOR_KINDS`, `TUB_DOOR_MAX_FT`) and `pack_audit`'s door check - none in what the timing pair rolls (the hamlet's stages) | green 2026-10-10 at engine key 4ade95493877 | closed: glyph checks tubs (Ubame) NEEDS-WORK then PASS and door (Hoshigaoka) PASS round 2; size audit door PASS round 2; building-review county NEEDS-WORK then PASS; plan review CLEAR round 3; escalation-check |
