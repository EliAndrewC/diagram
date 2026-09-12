# Feature 233 - tasks

Spec ACCEPTED 2026-09-12 after four `spec-fidelity` rounds. Every task is classified
`research: rendering` or `research: physical`; a physical task carries its five research boxes.

## Phase 1 - the placer

- [x] T01 `poly_seg_dist` in `settlement/_geom/primitives.py`: least distance from a polygon or open
      polyline to a segment, ZERO on a crossing or containment. Composed from the existing
      `seg_dist` / `segments_cross` / `point_in_poly` - no rival geometry module. (SC-006)
      research: rendering
- [x] T02 Lift `duck_pen`'s wet-arc computation to a module-level `pen_wet_arc(cx, cy, w, water)`
      and have `duck_pen` delegate, so there is ONE body (feature 146 doctrine) and the seat test can
      build the arc a CANDIDATE seat would produce (`research.md` R6 implementation note).
      research: rendering
- [ ] T03 `SLUICE_CLEAR_FT = 6.0` in `farm_fixtures.py` with its GUESS label and reasoning at the
      point of change (FR-002, one of the three required places).
      research: physical
      - [ ] research pass - the record was searched by two `source-reader` agents; spacing along a
            dike is NOT-FOUND, FAO gives dike WIDTH only (`research.md` R2 C5, R3)
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
- [x] T04 `pond_fixture_fits` holds every drawn part of a sty or pen clear of every
      `dikepond_sluices[]` stub by `SLUICE_CLEAR_FT` - the sty footprint, the pen's dry run, and the
      pen's fence arc (the open polyline). (FR-001, FR-002)
      research: rendering
- [x] T05 `_bank_seat` returns the parcel's edges RANKED by distance to the house cluster; the placer
      takes the nearest that fits rather than skipping the pond. (FR-003, FR-004)
      research: rendering
      VERIFIED on the regenerated map: 7/7 sties, 2/2 pens (SC-002); worst clearance over every drawn
      part 8.47 ft against the 6 ft margin, no violations (SC-001). The R6 simulation predicted 8.5.
- [x] T06 Tests: the clearance fires when removed (SC-003); the distance returns 0 on a stub driven
      through a footprint, on one wholly inside, and does not close an open polyline (SC-006);
      counts hold (SC-002).
      research: rendering

## Phase 2 - the record

- [ ] T07 `research/archetypes.html`: extend 'What stands on a dike-pond hamlet that a paddy hamlet
      lacks?' with findings 1, 2, 5 and 7, and FIX its stale close - "neither is drawn" plus the
      resolved CANDIDATE comment, both contradicting the map since feature 150. (FR-005, FR-007, FR-011)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
- [ ] T08 New section 'Does a pig sty have to stand back from the water, or from the pond's sluice?'
      carrying findings 3, 4 and 6, with the 齊民要術 passage in English translation marked as one and
      the original as the anchor, and the inlet/outlet SILENCE as a labeled absence note - no key, no
      link, what was searched and when. (FR-005, FR-006)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
- [ ] T09 `research/citations/archetypes.html`: the footnotes for every new assertion, each quoting
      the passage it rests on and linking a public page where the quote can be read; every new
      registry key gets its What-it-is / Why-it-applies write-ups in `SOURCES.html`. (FR-005, FR-009)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
- [x] T10 Pond figure (4.0 mu / 0.27 ha) carries its honest limit wherever it reaches a reader - the
      same ponds sit below the ISIS 0.4-0.6 ha band. (FR-005)
      research: rendering

## Phase 3 - the modals

- [x] T11 Rewrite the `PigSty` and `DuckPen` docstrings in `interactive/classes/dikepond.py` against
      the record as it now stands, with `Sources:` and `Entry:` naming what the new text was written
      from. NEITHER may offer a water-quality reason for the fixture's position (FR-008, D2).
      research: rendering

## Phase 4 - verification

- [x] T12 Regenerate Kuwabata; assert SC-001 (no drawn part overlaps a stub, all clear by the margin)
      and SC-002 (7 sties, 2 pens) on the new manifest.
      research: rendering
- [ ] T13 `record-format` and `quote-check` over every changed research entry; `source-applicability`
      over every new registry key BEFORE its numbers reach a map or a rule. (FR-009)
      research: rendering
- [ ] T14 `make done` green, paired with `settlement-review` on the regenerated map (FR-010).
      research: rendering
