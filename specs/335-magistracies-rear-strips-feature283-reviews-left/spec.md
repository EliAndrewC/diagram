# Feature Specification: The magistracy sheets' open findings - the rear strips (283's reviews), the landing steps, the doors and the arches

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=335-magistracies-rear-strips-feature283-reviews-left`)

**Created**: 2026-10-08 (filed by feature 330); specified 2026-10-11

**Status**: Draft (specified 2026-10-11 from its filed form) - carries 339, 341 and 342 word for word (the GM, 2026-10-11: *"If some of them should be undled together that's fine"*)

**Affects**: magistracy, country shrine

**Input**: `request.md` - the GM, 2026-10-11: *"Please implement features 355, 339, 340, 341, and 342. You can do them in
whatever order makes sense. If some of them should be undled together that's fine, or you can do them sequentially, whatever
makes the most sense."* ("355" read as 335 under the user-level transcription rules; `request.md` says why.)

**Why one feature**: 335, 339, 341 and 342 each redraw the same hand-drawn sheets (Hayakawa, Ochiba, Ubame, and Hoshigaoka
for the arch rule), and each revised sheet owes a `building-review`. Done together, each sheet is redrawn once and reviewed
once instead of up to four times. Feature 340 (the program example's caption placer, `compound.py`) is engine work on the
generated draft, not the hand sheets, and stays its own feature so the sheets are not held behind it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Hayakawa's landing steps are cut into the revetment (339) (Priority: P1)

The GM opens Hayakawa's sheet and the landing's flight of steps reads as notched into the stone revetment along the river, as
the research now holds (research/questions/0176-wharves-and-landings-piers-quays-and-stepped-landings-kashi-gangi.html:
"The steps are cut into the revetment"), not as a slab standing out into the river past the revetment's face.

**Independent Test**: measured on the sheet (`harness.py`, the steps against the `revetment` rect): before this feature the
steps run x 1058-1084 against a revetment at x 1064-1072 - 12 px (4 ft) past its river face. After: 0 px past it, and a
`tools/pack_audit/` check that fails on the unfixed sheet passes on the fixed one.

### User Story 2 - Every door is drawn flush inside the wall it opens through (341) (Priority: P1)

The GM sees one door convention on every sheet: the door's small block set flush inside the wall it opens through, as the
generated plans and research/questions/0117-doorways-and-doors-to.drawing.html set it - never a slab standing outside the
wall, and never straddling the wall line.

**Independent Test**: measured (`harness.py`, every `data-kind="door"` rect against the building it opens through), 2026-10-11:
Hayakawa 6 inside / 14 outside, Ochiba 7 inside / 7 outside, Ubame 9 inside / 9 straddling / 5 outside, Hoshigaoka 2 inside.
After: every door on every sheet inside and flush, and a `pack_audit` check that fails on each unfixed sheet passes on each
fixed one.

### User Story 3 - Every torii on a Mode A sheet is drawn in plan (342) (Priority: P1)

The rule is already settled in `docs/buildings.md` (feature 268: "a Mode A arch is drawn IN PLAN"); the GM sees it held on
every sheet. Measured 2026-10-11: Hoshigaoka's seven arches and Hayakawa's one are already in plan; Ubame's approach torii is
still an elevation silhouette (two beams over two legs, no `id="arch"`). It is redrawn in plan, the "Modest shrine" bullet's
"the existing sheets still draw an elevation silhouette" clause goes, and a check holds every torii to the plan form.

**Independent Test**: `harness.py` reports every `data-kind="torii"` group IN PLAN on every sheet; the `pack_audit` check fails
on the unfixed Ubame sheet and passes on the fixed one; `docs/buildings.md` no longer says any sheet draws a silhouette.

### User Story 4 - What feature 283's reviews left open in the rear strips is worked (335) (Priority: P1)

Each finding the filed entry lists is re-measured on today's sheet (they date from 2026-09-28; later features moved the
sheets), then worked: the research ones first, each a fix, a labeled guess, or - where today's sheet already answers it - a
recorded "no longer applies" with the measurement.

**Independent Test**: each finding below has a row in the plan with its re-measurement and its outcome; the fixed sheets pass
`pack_audit` and their `building-review`.

### Edge Cases

- A door that opens through a wall two buildings share (an ell abutting its house): it is drawn inside the building it is the
  door OF - the one whose `data-kind` group holds it.
- Moving a door inward by its own depth can bring a fire-water tub's distance to its door, or a door's approach, across a
  `pack_audit` limit (`tubs_off_their_doors`, `floating_doors`): every sheet is re-audited after the doors move, and any such
  finding is fixed in the same work.
- The Ochiba hall's "torii silhouette" is an ALTAR MARKER inside the shrine hall (docs/buildings.md "Hall shrine": identifiers
  like a torii silhouette for distinct altar aspects), not an arch on an approach: it is not a `data-kind="torii"` group and is
  left as drawn; the decision is recorded.
- A finding of 335's whose research question the record cannot answer is drawn as a labeled guess or not drawn, with an absence
  note saying what was searched - never left unlabeled.

## Requirements *(mandatory)*

### Functional Requirements

**The landing steps (339)**

- **FR-001**: Hayakawa's landing steps MUST lie within the revetment's river face: no part of the flight past the revetment rect's
  water-side edge. The flight is notched into the revetment and the bank behind it, its treads still running down toward the
  water; the moored barge's lines reach the new face.
- **FR-002**: A `tools/pack_audit/` check MUST fail a sheet whose declared landing steps (`data-id="landing-steps"`) run past its
  revetment's water-side face, proven red on the unfixed sheet (a frozen fixture) before the sheet is fixed.

**The doors (341)**

- **FR-003**: The door convention MUST be one rule, stated in `docs/buildings.md` (the operative doc), in research 0117's drawing
  page (the finding), at the point of change, and under Decisions Recorded: a door's block is set wholly inside the building it is
  the door of, flush to the wall it opens through (a MAP DRAWING CONVENTION; the generated plans already draw it so).
- **FR-004**: Every `data-kind="door"` rect on the Hayakawa, Ochiba and Ubame sheets that stands outside or straddles its wall MUST
  be redrawn flush inside it - 14, 7 and 14 doors as measured 2026-10-11 - and Hoshigaoka's two re-verified.
- **FR-005**: A `pack_audit` check MUST fail any sheet carrying a door rect not wholly inside a built footprint, proven red on a
  frozen fixture of an unfixed sheet before the sheets are fixed.

**The arches (342)**

- **FR-006**: Ubame's approach torii MUST be redrawn in plan as `docs/buildings.md` "Arch (torii) and approach" specifies - the
  `15 x 1.5 ft` vermilion top beam across the approach, the two `1.2 ft` darker post squares under its ends `10.3 ft` clear (the bullet's own figures), and the
  invisible `id="arch"` bounding rect - and its notes record the form (one arch).
- **FR-007**: The "Modest shrine" bullet's clause saying the existing sheets still draw an elevation silhouette MUST be removed once
  no sheet does.
- **FR-008**: A `pack_audit` check MUST fail a sheet with a `data-kind="torii"` group that declares no `id="arch"` rect, proven red
  on the unfixed Ubame sheet first.

**The rear strips and 283's open findings (335)**

- **FR-009**: Ubame's rear yard - each item re-measured, then worked: a way (stepping stones or a path) to the two storehouse doors;
  a service way to the reception's privy whose approach avoids the garden; the strip east of the reception (the filed entry's `19 x 31 ft`, from feature 283's 2026-09-28 review) settled;
  the garden ended at the storehouses' south faces.
- **FR-010**: Hayakawa's family way out of the inner garden - drawn as a labeled guess or not drawn (research 0104 holds an absence
  note on whether a wicket stood there), the choice recorded.
- **FR-011**: Hayakawa's working well at the middle gate's mouth beside the guests' first stone - a research pass on whether a
  draw-well ever stood on a roji's line, then the well kept, moved or labeled as the research decides.
- **FR-012**: Hayakawa's rear pocket (the filed entry's `33 x 12 ft`) - judged as dead space and either put to use or closed up, the judgment recorded.
- **FR-013**: Ubame's servants' quarters - the four bays' divisions MUST read as sliding partitions (research buildings 910, the
  common-room form), redrawn if they read as walls.
- **FR-014**: `pack_audit`'s aligned-gap finder (`tools/pack_audit/checks.py` `aligned_gaps`) MUST NOT pair two buildings across a
  third; a test pins Ochiba's nagaya-to-storehouse 28.7 ft pair (m:ochiba-aligned-gap) as not a gap.

**Across the whole**

- **FR-015**: Every sheet this feature revises MUST pass `make pack-audit` and its interactive page build (its gen's census) after
  the redraws, and owes ONE `building-review` after all of its redraws land.
- **FR-016**: 339, 341 and 342 MUST close as `Superseded by 335` with their entries carried word for word here.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-002): Hayakawa's steps past the revetment's river face: 12 px -> 0 px (m:steps-past-revetment, research.md R1).
- **SC-002** (FR-003, FR-004, FR-005): Doors not wholly inside their building, over the four sheets: 35 -> 0 (m:doors-off-walls, research.md R1).
- **SC-003** (FR-006, FR-007, FR-008): Torii groups not in plan, over the four sheets: 1 -> 0 (m:torii-not-in-plan, research.md R1).
- **SC-004** (FR-002, FR-005, FR-008, FR-014): Each new check red on its frozen unfixed fixture and green on every pool sheet; the
  aligned-gap test red before its fix and green after (`make test-file`).
- **SC-005** (FR-009, FR-010, FR-011, FR-012, FR-013, FR-015, FR-016): Every FR-009..FR-013 finding has a recorded outcome with its
  measurement (FR-011's from the search pass, research.md R2); every revised sheet passes `make pack-audit` and its
  `building-review` within two rounds (or the round arbiter rules); 339, 341 and 342 read `Superseded by 335`.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

- **D1 (map drawing convention) - doors flush inside**: one convention for every sheet, the generated plans' and 0117's. Of the
  sheets' 59 doors, 24 were inside, 26 outside, 9 straddling (2026-10-11). A door standing outside its wall reads as a step or a
  porch; one straddling reads as a stray mark on the stroke.
- **D2 (map drawing convention) - an arch in plan, an altar marker as an icon**: the plan arch is for a gateway on an approach; the
  Ochiba hall's torii silhouette is an altar marker inside the hall, an identifier, and stays.
- **D3 (historically accurate) - the steps cut into the revetment**: research 0176.
- Further decisions (the rear strip items, the well, the pocket) are recorded here as the plan settles them.

## Assumptions

- The sheets are hand-drawn SVG source (Mode A); redrawing them is the work, as each carried entry asks ("redraw them if they
  do", "Settle the rule, then redraw"). No generator changes except the `pack_audit` checks.
- Hoshigaoka needs no redraw (its doors are inside, its arches in plan); it is re-audited, not reviewed.

## What it carries

### 335 - the entry, as filed

Feature 283 moved the three magistracies' kitchen gardens out of their shady rear strips for their sun (the GM, "Move
them all"). Filling the strips they left took four `building-review` rounds a sheet; the session carried what the
fourth round still found here rather than into a fifth (spec 283, Decisions Recorded, with its cost). Each is a finding
to work, the research ones first:

- **Ubame's rear yard** (open ground since the GM's 2026-09-28 ruling to draw what the sources most safely support):
  stepping stones or a way to the two storehouse doors, a service way to the reception's privy (its cesspit has no approach that avoids a garden),
  and settle the 19 x 31 ft strip east of the reception; end the garden at the storehouses' south faces.
- **Hayakawa**: the family's way out of the inner garden (whether a wicket stood there is an absence note on
  research/questions/0104, so the sheet draws a labeled guess or none); the working well at the middle gate's mouth beside
  the guests' first stone (research: was a draw-well ever on the roji's line?); the 33 x 12 ft rear pocket, kept for
  caption seats the one placer no longer needs - judge it as dead space.
- **Ubame**: the servants' quarters' four bays under one door are the common-room form, accurate as drawn PROVIDED the
  bay divisions read as sliding partitions (research buildings 910, feature 293). Owed: look at the sheet's divisions and
  redraw them as sliding partitions if they read as walls.
- **Tools**: pack-audit's aligned-gap finder pairs two buildings across a third
  (Ochiba's "28.7 ft" nagaya-to-storehouse gap; `tools/pack_audit/checks.py` `aligned_gaps`, unchanged since 2026-08-31).

### 339 - the entry, as filed

- **Hayakawa's stepped landing (sheet check)**: the record now says the steps are cut into the revetment (0176); check
  whether the sheet's steps still project past the revetment face, and redraw them if they do.

### 341 - the entry, as filed

- Door glyphs drawn as slabs outside their walls where the rendering rule says flush (every sheet's informal doors -
  a convention question).

### 342 - the entry, as filed

- The torii drawn as an elevation silhouette on Mode A sheets while `docs/buildings.md` (feature 268) says a Mode A arch
  is drawn in plan; the "Modest shrine" bullet still says silhouette. Settle the rule, then redraw.

## Review history

- 2026-10-11, first dispatch: NOT-REVIEWABLE (no round used) - three figures with no key; keyed to `measurements.json`.
- 2026-10-11, round 1: FAITHFUL (ACCEPT). Notes acted on: the harness's command names a real path; the door check also reports a
  door floating just inside its wall (plan D2); the landing message says plainly that "355" was read as 335.
