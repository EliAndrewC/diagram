# Feature Specification: What a reader takes for the river at the tap: the width and the hue (feature 230 pass 12, 2026-09-13)

**Status**: Done 2026-10-11 - the head race's first 30 ft taper from the brook's hue to the supply hue on every pool hamlet (`race_taper`); glyph-check before: reads as the river: YES, after: NO (PASS); width unchanged; claims IN-STEP; reopened at the GM's word (the goal named 355), its item taken out of 358

**Affects**: hamlet

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

**Request**: the GM, 2026-10-11 (`request.md`): *"Please implement features 355, 339, 340, 341, and 342. You can do them in
whatever order makes sense."* The entry below is the GM's own words for 355; its sketch is the method.

## User Scenarios & Testing

### User Story 1 - The dug race does not read as the river (Priority: P1)

The GM, looking at a hamlet's intake at close zoom, reads the brook as the watercourse and the head race as a ditch dug off it:
the race opens out of the bank in the brook's own color and turns to the supply blue over its first `~30 ft`, as the entry's
sketch asks, so the dark saturated band no longer starts at the brook as if it were the trunk.

**Independent Test**: on every pool hamlet's tap, the race's first stroke is drawn from the brook's hue at the tap to the supply
hue `~30 ft` along it (a gradient on the race's own line), and the rest of the race is unchanged; a close render shows it.

## Requirements

- **FR-000**: FIRST, the sketch's judgment: the new mouth judged at 9x by an independent review on Sawada - "judge the new mouth at
  9x in a settlement-review first". Since feature 294 the review checks are divided by what they judge, and whether one element's
  mark reads as what it depicts or can be confused with another is the `glyph-check`'s question (the whole-map `settlement-review`
  judges the map as a place); so the judge is a `glyph-check` of the head race at its mouth on Sawada, at 9x, on the map as main
  draws it. If it finds the race does NOT read as the river, 355 closes with that verdict recorded and no map change.
- **FR-001**: only if FR-000 finds the race reads as the river, the head race's first `~30 ft` MUST taper from the brook's bed hue
  (`#9CB4C8`) at the tap to the supply hue (`#6C9CBE`, `SUPPLY_HUE`) along the race's own line - the entry's sketch ("taper its
  first `~30 ft` from the brook's hue to its own").
- **FR-002**: the race's width MUST stay the water-width ladder's own figure (the entry's mechanism: width is drawn by RANK, and
  changing it here trades a junction misread for a map-scale one); only the hue tapers.
- **FR-003**: nothing else of the race or the brook changes: the brook still paints over the race's mouth (`open_race_mouth`), and
  a hamlet without a race mouth is untouched.
- **FR-004**: 358's carried copy of this entry MUST say it is done here, so the wave does not do it twice.

## Success Criteria

- **SC-000** (FR-000): a `glyph-check` verdict on Sawada's head-race mouth at 9x, on main's map, is recorded in this spec before
  any map change.
- **SC-001** (FR-001, FR-003): if SC-000's verdict is that the race reads as the river, every pool hamlet's race mouth carries the
  taper - its bed holds one gradient overlay of the race's first `~30 ft` (R1), starting at the tap in the brook's hue - and the pool
  gate stays green; otherwise no hamlet's map changes and the pool gate stays green.
- **SC-002** (FR-002, FR-004): the race's drawn width is unchanged on every pool hamlet; 358 names the item done by 355.

## Decisions Recorded

- **D1 (map drawing convention)**: the taper is a drawn gradient on the race's own first `~30 ft` (R1), the entry's sketch; no research
  is owed for a hue transition, which is a drawing convention for where a dug ditch leaves a brook.

## The entry, as filed

**Measured** (Sawada): the head race leaves the brook at `#6C9CBE` (128,167,191) - darker and more saturated than the
brook's own `#9CB4C8` (168,187,199) - and at 6.0 px against the brook's 7, so it is 86% of the trunk's width. At 9x the
dug ditch can read as the principal watercourse. The mouth half is done (269 B22: the race now opens out of the brook's
bank, research/contents.json#water 310, `hamletgen/water/brook.py` `open_race_mouth`); the width and the hue are what remain.
**Mechanism**: both widths are the water-width ladder's own figures, drawn by RANK rather than discharge, and the hues
are the supply/brook pair every map uses; changing either for this junction trades a junction-scale misread for a
map-scale one. **Sketch**: judge the new mouth at 9x in a settlement-review first; only if the race still reads as the
river, taper its first ~30 ft from the brook's hue to its own.

## The sketch's first step, measured (2026-10-11)

Judged on Sawada's mouth at (4575, 3455) as main draws it today (observed 2026-10-11; method: the pool SVG rendered at about
5 px per map unit around the tap, read by eye): the head race leaves the brook 6.0 px wide in the supply hue `#6C9CBE` against
the brook's 7 px in `#9CB4C8`, and at that zoom the dug race reads as the principal watercourse - the saturated band - while
the brook reads pale. That eye-read is context, not the judgment the sketch names (FR-000). 355 is built here at the GM's 2026-10-11 word,
and 358's carried copy is marked done by 355.

## SC-000: the judgment (glyph-check, 2026-10-11)

The `glyph-check` of the head race's mouth on Sawada at 9x, on the map main draws: **reads as the river: YES**. The race outweighs
the brook (the width step too small to show the rank, the saturated hue reversing it); the junction's geometry says "brook" and the
mouth itself is clean (the race leaves the bank). The tool recorded the unit NOT-REVIEWABLE only because this clone's gate was red
with the change the verdict gates; the verdict's text is the reviewer's. It also noted, pre-existing and not this entry's, that
research page 0068's drawing note says the brook arrives narrower than the race, where Sawada draws it wider. So FR-001's taper is built.
