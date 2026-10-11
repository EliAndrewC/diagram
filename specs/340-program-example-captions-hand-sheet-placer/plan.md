# Implementation Plan: one view of the sheet for the program example's captions (340)

**Spec**: `spec.md` (FAITHFUL, round 2) | **Measurements**: `harness.py` (`make spec-harness SPEC=specs/340-program-example-captions-hand-sheet-placer OUT=<json>`)

## Summary

Three steps, as the spec orders them: the composed draft declares its captions the hand sheets' way (additive - no seat
moves); a harness measures, on that one declared draft, every caption the composer and the hand-sheet placer seat
differently, attributing each to the entry's three sources and reporting what each of the entry's two fixes removes; then the
seating switches to the fix the measurement supports, per source, keeping feature 287's strict rule. D3 is decided by the
measurement and the plan is amended and re-reviewed before it is built.

## Decisions

- **D1 - the declarations (FR-001)**: `emit_svg`'s `rect` gains a `data-id` argument and `caption` a `names` argument; the
  written caption carries `data-names` listing the drawn shapes it names. Each call site names the shape(s) the caption is
  about: a zone's, a building's or a room's own rect; the dais and each clerk's seat; the bath, a well, a latrine, every tub, the
  notice board; EVERY straw mat (the hand sheets' form: the caption names all the mats of its group - plan review round 1:
  naming only the last mat would hide the entry's 'one mat' difference before D2 measures it); the striking posts' two circles. Where the composer seats a caption on ground that
  is not a drawn shape (a block's name in its rear alley, `_rear_band`), the declaration names the block itself - that IS the
  subject difference the entry names, and the harness counts it. No invisible stand-in is added (the entry counts those as a
  difference). Nothing else changes: the composer still seats by its own subjects, so every seat is unchanged and a test
  asserts the declared draft's caption positions equal the undeclared draft's.
- **D2 - the harness (FR-002)**: on the declared draft, `C` = the composer's seats as emitted, `H` = `labels.hand_sheet.seat` on
  the same text. Variants of the composer's seating, each one source swapped for the hand-sheet placer's: the obstacle view
  (`hand_sheet.classify` over the drawn sheet less its captions, in place of `emit_svg`'s own obstacle list and the roofed
  court's late obstacles), the subject (`hand_sheet.subjects` over the declared parts), the width (`char_w_of` per caption in
  place of `CHAR_W_EM`); and the two fixes as the entry words them - fix 1 the composer indexing with `classify` (its own
  subjects), fix 2 the hand-sheet placer taking the composer's subjects. For each caption whose `C` and `H` differ by more than
  1 px it records the sources that remove the difference; one no source removes is reported with its cause (strictness, order,
  clearance, repair) and kept out of N. Recorded in `measurements.json`.
- **D3 - the switch (FR-003)**, decided by D2's measurement (m:caption-disagreements, 2026-10-11): of 45 captions, 11 seat
  apart; 6 are explained by the three sources - the obstacle VIEW 5 (garden, straw mats, practice ground, two wells), the
  SUBJECT 1 (the fire-water tubs: the composer names the roomiest tub, the declaration all of them), the WIDTH 0. Fix 1 (the
  composer indexing with `classify`) removes the 5; fix 2 (the hand-sheet placer taking the composer's subjects) removes 2, the
  residence and the gatehouse, which no single source explains (an order interaction), and none of the 6. So, per source:
  VIEW - fix 1: `emit_svg` builds each caption's index with `hand_sheet.classify` over the sheet it has drawn (its captions not
  yet written), the seated captions added as now, and no obstacle list or late obstacles of its own; SUBJECT - the composer
  takes the hand-sheet placer's reading of the declared subject (`hand_sheet.subjects` over the declared parts, first
  subject), which removes the tubs' difference where fix 2 removes none of the subject-source ones; WIDTH - unchanged (no
  difference). The 5 the three do not explain (residence, gatehouse, cell and two clerks: order, clearance or repair, and one
  clerk where the hand-sheet seat covers ink) are reported, not unified (FR-003). After the switch the harness re-runs: the 6
  go to 0, each remaining disagreement listed with its cause.
- **D4 - strictness under the one view (FR-004)**: a seat is free when it touches no ink the caption does not name: the
  `inner` obstacles `classify` marks for the caption's own subject (its partitions, its mats) do not make a seat unfree; every
  other weighted obstacle does, as today. Foot growth (`CAPTION_GROWTHS`) and the refusal message are unchanged.
- **D5 - performance (FR-005)**: the example's gen timed before and after (`make map ... PROFILE=1`); `make perf-report` read;
  any band crossed explained and audited.
- **D6 - tests**: `tests/test_compound.py` keeps its refusal test unchanged; a declarations test (D1, seats unchanged); the D3
  switch's tests as D3 settles them, with 100% coverage of what changes.

## Constitution Check

- XVI literal: the entry's "measure first which disagreements each removes" is D2, run before D3 is chosen.
- XIII/XIV: the refusal test and the pool sheet's checks hold; any finding the re-seating causes is fixed here.
- VI: D5.
- Occasions: `layout-revised: county-magistracy-example` (its captions re-seated) - one `building-review` after D3 lands.
