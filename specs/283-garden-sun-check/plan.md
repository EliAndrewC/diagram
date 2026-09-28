# Plan - feature 283, a garden's sun, checked on hand-drawn sheets

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

## Decisions

- **D1 - the record** (FR-001, FR-002): research homesteads 044, "How many hours of direct sun does a kitchen bed
  need?" - six hours for a bed of sun crops, three for a half-shade bed, which takes dappled light under trees as lit
  (atariya-nisho's crop table, jasaga-hiatari's three lists); the check's counting - 38 degrees north, the shoulder
  month (declination -8.5 degrees), half-hour steps, a step lit when at least half the bed is out of shadow - and the
  heights it gives what stands up (a building 20 ft, a small roof under 100 sq ft 6 ft, a wall 1.6 m, a tree 10 m), each
  a least height and labeled. Two sources registered; every record check run and applied.
- **D2 - the check** (FR-003, FR-004): `garden_sun` in the pack audit's shared layer
  (`l7r/diagram/tools/pack_audit/sun.py`, a row in `registry.py`), so it runs on every hand-drawn building sheet the gate
  audits. It finds each fill of kind `vegetable garden`; a `data-bed="half-shade"` declares the half-shade knob (the sun
  bed the default). It casts every structure not in its named not-standing list (basin, door, engawa, hearth, notice
  board, weapon rack, stone lantern, tax barge, dais, clerks' seats, well, the two altars - each flat or knee-high), every
  wall and divider, and every tree - a crown, a grove's crowns, a sacred tree - as a footprint swept along the sun's
  bearing, and reports the hours, the threshold and the shade makers by kind. No index: a sheet has tens of casters and
  one or two beds, and the sweep runs in milliseconds. The red fixture is the shrine sheet as drawn before this feature
  (`tests/fixtures/hoshigaoka-garden-shaded-red.svg`), whose report names the trees; nine unit tests carry it to 100%,
  among them a bed shaded by trees alone.
- **D3 - where a garden goes is research** (FR-005; the GM's redirect): research buildings 405, "Where does a walled
  compound keep its vegetable garden, and does the sun decide it?" - four attested seats (west of the house, south
  beside the formal garden, the rear service ground, a parcel of its own) make a knob, and the sun rules out any seat
  under its hours (a guess that the sun chose). 400's "off the south side" is corrected to point at 405. Four sources
  registered; every record check run and applied.
- **D4 - the four beds** (FR-005), each measured by `garden_sun` after the move:
  - the Hoshigaoka shrine's to the open ground south-west of the hall (2.5 h before, 7.5 h after);
  - Hayakawa's from the rear strip (1.5 h) to the SE corner of the south court, along the divider beyond the pond (8 h),
    an 8 ft strip of garden kept before the reception; the pines and the roji's last stones moved clear and the well to
    the bed's NE corner. The sheet had drawn it under the size knob's attested low end (research buildings 400), so it
    grows to that low end (about 1,067 sq ft, 96 x 100 px) - a defect fixed where found (constitution XIV);
  - Ochiba's from the rear strip (0.5 h) to the NE corner of the south court under the karo's house, cut from the inner
    garden (9.5 h);
  - Ubame's from the rear strip (0 h) to the middle of the south court between the writing pavilion and the roji's west
    wall (7.5 h), at the size knob's low end (research buildings 400), the only open ground in its walls with a sun
    bed's hours; the pavilion shifted west with its tub, the well moved below it.
  None is declared half-shade. Each sheet's captions re-seated by `make seat-label`, its notes carry a dated bullet.
- **D5 - a defect fixed on the way** (constitution XIV): the caption placer weighed ground painted after a caption,
  inside the ground it names, as open ground, and seated Hayakawa's garden name under the new bed. Ground painted over a
  caption now weighs as a caption does (`tools/seat_label.py`, one test); every other sheet's seats are unchanged, and
  the two generated sheets' off-seat counts are the same as at HEAD (measured with HEAD's code in a detached worktree).
- **D6 - the docs** (FR-006): `buildings/programs.md` - the magistracy's `kitchen_garden` row names the seat knob and
  the sun rule, and the country shrine's hall bullet says the garden stands where neither the hall nor the wood takes its
  sun; `compound.py`'s county-example zone comment points at 405 and its measured hours.
- **D7 - verification** (FR-007): `make quick`; entry-drift on any modal written from 400; a `building-review` of each
  of the four sheets, ledgered in `docs/review-ledger.md`, findings through escalation-check; `make done` green.

## Constitution Check

- XII (research): every figure the check uses is on 044 with its source or its label; the seats on 405.
- XIII (no regressions): the seat placer's change measured against HEAD on every sheet.
- XIV (fix where found): D5.
- XVI (the literal thing): the check runs on the GM's class as answered ("Sheets only"); the four gardens move as
  chosen ("Move them all"), none declared half-shade.

## Round 2 (after the building reviews, 2026-09-28)

- **D8 - the reviews' findings** (FR-005): Hayakawa's bed to the divider beyond the pond (8 h, about 1,067 sq ft), the
  well at its corner; every bed painted in `vegetable-rows` over a formal garden restored to its own shape (a map drawing
  convention; `compound.py` draws the county example's bed the same way); two household storehouses in each magistracy's
  rear strip (a `storehouse` kind, written from research buildings 400, 160 and 230), a 7-11 ft alley kept behind each
  house; the shrine's bed 12 px south, clear of the clearing; `programs.md` and `buildings.md` put a kitchen garden in the
  rear only where it gets its sun; notes, knob lists and Map notes restated; research buildings 405's open questions as
  absence notes.
- **D9 - tooling defects fixed where found** (constitution XIV): `pack_audit/parse.py` reads a filled rectilinear
  `<path>` as its rects (even-odd slabs); `labels/placer.place` takes an optional `leader_index`, which only
  `tools/seat_label.py` supplies (the other captions and glyphs under 600 px2), so the engine's maps are unchanged; a
  `busy` fill (a bed's rows) is no seat for another name; `tests/_sheets.fresh` checks staleness under its lock. Each
  with its unit test; the seat reports of every sheet compared against HEAD (only Ochiba's RESIDENCE moved).

