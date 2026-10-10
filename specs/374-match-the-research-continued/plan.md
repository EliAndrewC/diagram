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
- **The fix**: each sheet's kitchen drawn about 24 x 18 ft (72 x 54 px), its shape a GUESS, the ceiling ACCURATE (0091's measured
  wing), joined to the house as an ell (abutting it, no corridor); Hayakawa's covered way removed. The kitchen band in
  `buildings/types.json` narrowed so the old size fails it: w 18-26 by h 14-20 ft (either orientation). The procedure's kitchen
  bullet and both claims say ~24 x 18 ft, an ell, 0091 cited; "a large institutional daidokoro" goes (the ranked fix sizes it to
  the measured house; nothing in the record sizes a kitchen to its feeding). The draft's kitchen is 20 x 18 ft (`compound.py`'s program,
  read 2026-10-10), already inside the new band.
- **What stands in the kitchen moves with it**: the kamado range, a well drawn inside the kitchen (0105's drawing page: inside
  the kitchen on a hand plan), its door, the two tubs at its door (wave 106's rule, `tubs_off_their_doors`), the bath abutting it.
  The ground the smaller kitchen frees is left as the court or service ground it opens onto. Each move audited.
- **Occasions**: layout-revised: hayakawa-magistracy (the kitchen joined as an ell, the corridor gone); glyph-redrawn: kitchen on
  ochiba-magistracy (Ubame's the same change).

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

## Performance bookends (constitution VI)

| batch | waves | pair | gate | close |
|---|---|---|---|---|
