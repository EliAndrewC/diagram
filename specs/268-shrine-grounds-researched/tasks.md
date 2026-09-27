# Tasks - feature 268, a village shrine's grounds, researched

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Research: [`research.md`](research.md) (R1-R4 the
pass, D1-D7 its decisions; D8-D9 in the plan). Every prose or code task: American spellings, hyphens only.

## Phase 1 - the record (FR-001 to FR-003)

- [ ] T01 `research/religion-and-death/`: three new questions after entry 120 - "Was a village shrine
      walled or fenced?" (R1), "How large was a village shrine's precinct, and how much of it was built
      on?" (R2), "What else stood in a village shrine's precinct?" (R4) - and entry 090 rewritten to R3
      and the GM's ruling of 2026-09-27; entry 120's fence and precinct-size sentences and every other
      stale mention (`grep` the page directory for the fence, 30 ft, the precinct guess) brought to the
      finding; each new source registered with its write-ups; `make record`, `make citations`,
      `make glossary`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited  - [ ] quote-check confirmed  - [ ] source-applicability confirmed
      measure: `make quote-verbatim PAGE=religion-and-death` before quote-check; `make record-prepass PAGE=religion-and-death` before record-format
      verify:
- [ ] T02 The record's checks, in the background, from bundles (`make check-bundle`): `source-reader`,
      `quote-check`, `record-format`, `source-applicability` on the new and changed entries and keys;
      then `entry-drift` on every pair `scripts/_entry_owed.py` names (the torii and country-shrine
      kinds in `household.py`, the grove in `grounds.py`); every verdict folded in
      research: rendering
      verify:

## Phase 2 - the program (FR-004 to FR-006)

- [ ] T03 `buildings/programs.md` and `l7r/diagram/buildings/types.json`: no precinct enclosure; the
      precinct band from R2; the grove and sacred tree (site items) and the basin as items; the knobs
      (guardian figures, lanterns, strength stones and a sanctuary fence on wealth, none at average; a
      farmers' stage and a sumo ring, absent by default, prevalence stated); `buildings.md`'s arch (D5),
      grove and precinct vocabulary; `make building-programs CHECK=1`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited  - [ ] quote-check confirmed  - [ ] source-applicability confirmed
      verify:
- [ ] T04 `no_precinct_enclosure` (D7) replaces `fence_not_wall` in `tools/pack_audit/shared.py`,
      `registry.py` and the declaration; tests red first: the walled fixture and a precinct-fence
      fixture fire, a sanctuary-only fence passes
      research: rendering
      verify:

## Phase 3 - the engine (FR-009 to FR-011; D1-D4, D9)

- [ ] T05 The pitch (D1, D2): `TORII_PITCH_FT = 12.0` with its why; `TORII_PITCH_MAX_SPANS` retired;
      `_avenue_pitch` lays every avenue at the pitch; `roll.py`'s village avenue through the pitch and
      the threshold; `hoshigaoka.gen.py`'s `SHRINE_TORII` at the pitch for conversion; tests red first
      (a village roll and a wide town avenue both come out at 12 ft, the innermost one pitch off the hall)
      research: rendering
      verify:
- [ ] T06 The plan-view arch (D3, D4): `_torii` draws the kasagi bar and two post squares, true size with
      the stroke floor; `torii_halfbox` to the new extents; the wall-shortening floor at the drawn depth
      plus one px; tests red first (at 1, 2 and 3 ft/px, neighbors at the pitch do not overlap)
      research: rendering
      verify:
- [ ] T07 The crop check's reach (D9): the `on_map` excuse and `frame_is_the_maps` removed; the test
      that an on-map sheet with a wide margin fails; `buildings.md`'s on-map paragraph
      research: rendering
      verify:

## Phase 4 - the map and the sheet (FR-007, FR-008)

- [ ] T08 The Hoshigaoka village map by hand (D6, D8): the mirror's svg backed up and edited (grove,
      sacred tree, basin, the seven arches at 12 ft), the png re-rasterized, the manifest brought to it,
      the grove's area measured on its outline; the map's notes and `migration-plan.md`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited  - [ ] quote-check confirmed  - [ ] source-applicability confirmed
      verify:
- [ ] T09 The Hoshigaoka shrine sheet redrawn: no fence; the grove from the well to the outermost arch;
      the swept clearing; the sacred tree and the basin; the arches in plan at 12 ft, the innermost one
      pitch off the hall; the frame cropped to the ink; `make seat-label SHEET=... WRITE=1`; the pack
      audit green (program, map-match, crop, SC-002's whole-frame reading by eye and by the audit's
      margins); the notes rewritten with every knob
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited  - [ ] quote-check confirmed  - [ ] source-applicability confirmed
      verify:

## Phase 5 - reviews and close (FR-012; SC-001 to SC-005)

- [ ] T10 `size-audit` (after `make size-table`) and `building-review` on the sheet, `settlement-review`
      on the village map's edited region, in the background, one map per agent; ledger rows in
      `docs/review-ledger.md`; findings applied; anything for the GM through `escalation-check`
      research: rendering
      verify:
- [ ] T11 Close: `make perf LABEL=268-end`, `make perf-report AGAINST=268-start`; the XII closing bookend on
      the rendered PNGs against R1-R4; the spec's Decisions Recorded table; `make done` (background);
      `scripts/sync-with-main.sh done`
      research: rendering
      verify:
