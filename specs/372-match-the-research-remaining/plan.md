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

## Performance bookends (constitution VI)

| batch | waves | pair | gate | close |
|---|---|---|---|---|
| 1 | 98-100 | none owed: the batch changed no engine code (hand sheets, their notes and the procedure only), so the engine key is the landed one and a pair would time the same code | green 2026-10-10 (already verified on the landed engine key) | closed: glyph checks latrine, boundary stones, road PASS; escalation-check |
| 2 | 101-102 | none owed: no engine code changed (hand sheets, their notes, a modal, the procedure) | green 2026-10-10 on the landed engine key | closed: glyph checks gatehouse (Ubame) and latrine (Ochiba) PASS; Ochiba's building review NEEDS-WORK (E1: the gatehouse's pop-up and building-programs.md gave the old size - fixed, the pop-up's record checks clean on round 3) then PASS round 2 |
| 3 | 103-104 | none owed: the batch's engine code is a review tool (`pack_audit`'s crop check) and `compound_model.NOTICE_BOARD_MAX_FT`, read only by the generated compound draft's board check and the pack audit - neither in what the timing pair rolls (the hamlet's stages) | green 2026-10-10 at the board limit's engine key | closed: glyph checks road (Ochiba) PASS and notice board (Ubame) NEEDS-WORK then PASS round 2; the border note box moved below the road (round 2's F7); escalation-check |
| 4 | 105- | owed at the batch close | at the batch close | open |
