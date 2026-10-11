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
- **D3 - the switch (FR-003)**, decided by D2's measurement (m:caption-disagreements, re-run 2026-10-11 after plan review round
  2: every variant now tries a caption's subjects in order, the first with a free seat winning, as `hand_sheet.seat` does): of
  45 captions, 11 seat apart; 10 are explained by the three sources - the obstacle VIEW alone 5 (garden, straw mats, practice
  ground, two wells), the SUBJECT alone 2 (the residence; the fire-water tubs, which the composer names by the roomiest tub
  where the declaration names all of them), the three TOGETHER 3 (gatehouse, cell, one clerk); WIDTH alone moves none. Fix 1
  (the composer indexing with `classify`) removes 5; fix 2 (the hand-sheet placer taking the composer's subjects) removes 2.
  The switch takes, per source: VIEW - fix 1: `emit_svg` builds each caption's index with `hand_sheet.classify` over the sheet
  it has drawn (its captions not yet written), the seated captions added as now, and no obstacle list or late obstacles of its
  own; SUBJECT - the composer takes the hand-sheet placer's reading of the declared subject, `hand_sheet.subjects` over the
  declared parts, the whole ordered list tried as the hand-sheet placer tries it (inside, then beside; the first with a free
  seat wins), since the composer's own single subject is what differs; WIDTH - the composer measures each caption with
  `hand_sheet.char_w_of` (FR-003: the source no longer differs, though on this example it moves no seat). Measured with all
  three swapped: 44 of 45 agree; the one left apart is a clerk (order, clearance or repair - not one of the three), reported
  and not unified; and every caption finds a strict seat (none soft). After the switch the harness re-ran on the built code (m:caption-disagreements-after): 3 apart - the straw mats 4.6 px and a clerk 84.2 px (order, clearance or repair) and a clerk 3.5 px (the hand-sheet seat covers ink) - none explained by the three sources.
- **D4 - strictness under the one view (FR-004)**: a shape the caption DECLARES never makes its seat unfree, flagged inner or
  not (plan review rounds 3-4): every obstacle `classify` gives for a declared shape is dropped from that caption's index,
  flagged inner or not (the striking posts are not judged against the posts they name, nor a caption tried beside one mat
  against the other mats it names); its outline bands are not the shape's own polygon and stay. Every other weighted obstacle blocks - the subject's partitions,
  a court's buildings, any shape the caption does not name - inner or not (round 2). Two rules of the hand-sheet placer's own
  classification are part of the one view and stay: a name in dark ink takes no dark fill it names (a well's shaft), and none
  lies across its subject's drawn outline; both are legibility, not naming, and the hand sheets keep them (round 4: LEGITIMATE,
  each from the entry's own "builds its obstacle index with hand_sheet.classify"). Measured: skipping the declared shapes
  outright drops both and left 7 captions apart - the outline rule alone accounts for that (it keeps the wells' names off
  them); the dark-fill rule moves no seat on this example; with both kept, 3 (m:caption-disagreements-after). Foot growth (`CAPTION_GROWTHS`) and the refusal message are
  unchanged and run only when no subject in the list has a free seat. The roofed court's late obstacles are retired with the
  composer's own index (the classification reads the court as built).
- **D5 - performance (FR-005)**: measured (m:composition-timing, best of five, varies with load): the composition takes 1.237 s
  under the one view against 0.237 s with the composer's own index. Profiled: index building was most of it - three indexes a
  seat tried - so `ObstacleIndex.copy` copies a classified sheet's buckets instead of re-adding them (1.543 s -> 1.237 s);
  the rest is `hand_sheet.classify` itself, once per caption and subject, which IS the one view the entry asks for. The
  priced alternative, classifying the sheet once and adjusting per subject, rewrites `classify` for every hand sheet and is
  not this feature's. The cost is accepted (the session, 2026-10-11; on the GM's review): about 1 s more on a pool gen whose
  render takes longer and runs far inside the 45 s default budget it falls under (it has no `GEN_TIME_BUDGETS` entry of its
  own); no hamlet perf bookend can move (`ObstacleIndex.copy` is new and only the composer calls it).
- **D6 - tests**: `tests/test_compound.py` keeps its refusal test unchanged; a declarations test (D1, seats unchanged); the D3
  switch's tests as D3 settles them, with 100% coverage of what changes.

## Constitution Check

- XVI literal: the entry's "measure first which disagreements each removes" is D2, run before D3 is chosen.
- XIII/XIV: the refusal test and the pool sheet's checks hold; any finding the re-seating causes is fixed here.
- VI: D5.
- Occasions: `layout-revised: county-magistracy-example` (its captions re-seated) - one `building-review` after D3 lands.
