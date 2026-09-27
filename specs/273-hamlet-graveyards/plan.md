# Implementation Plan: 273 - hamlet graveyards

**Branch**: none (`export SPECIFY_FEATURE=273-hamlet-graveyards`) | **Date**: 2026-09-27 | **Spec**: [spec.md](spec.md)

## Summary

The record carries the GM's ruling (210, 530) and the new question 540 ("Where do a hamlet's dead lie?"): every form
the history shows puts a hamlet's dead by the hamlet, so it is a RULE, not a knob - every hamlet draws a burial
ground of its own at its edge. The scripted hamlet generator gains a stage that seats and draws it; the village roller
gains its cremation ground (530); the village's burial ground (269's 280 knob and 270 siting) lands once 269's 270
and 280 are on main.

## Technical context

- **Surface**: `l7r/diagram/hamletgen/` (a new `burial.py` stage, wired into `driver.STAGES`), `settlement/rolling/roll.py`
  (`_roll_civic`: the village's cremation ground), the interactive class the ground is tagged with, `dev/placement.md`
  (the draw order), the tests; the five pool hamlets re-roll.
- **Overlap check**: the seat is asked of the engine's `_fits`/`_footprint_clear` through the existing seat scan, with
  the houses, wells and water held as a `PointGrid`-style index built once before the candidates (constitution X
  clause 15); no per-candidate registry walk.

## Constitution check

- VI: PASS - placer unit tests, a seed test over the five pool hamlets, settlement-review of the moved maps, `make done`.
- IX: PASS - the GM's ruling is recorded as canon in 210 and 530; the rest is history.
- X: PASS - red-first tests; 100% coverage of the new stage.
- XII: PASS - 540 researched and checked (quote-check, record-format, source-applicability applied).
- XIII: PASS - baseline main's green gate; the five hamlets' moves are the feature's own.
- XVI: PASS - a rule because the evidence agrees, as the GM asked; no exception.

## Decisions

- **D1 - a rule, not a knob** (540): every hamlet draws its own burial ground. Class: accurate (the form); the drawn
  form is the organic common ground the village's is (`cemetery(parish=False)`, research 150).
- **D2 - its size**: the 750 to 2,450 sq ft 160 reckons for a hamlet's ground, set within the band by households
  (5 or fewer at the floor, 30 or more at the top, linear between) - accurate as a band, the value a guess; drawn
  about 1.4 to 1 long to wide, a guess.
- **D3 - its seat**: beyond the last house, down the fall line first (a burial place below the houses, as 270 has the
  village's - cited once 269 lands, the pointer a RELINK comment until then), turning to either side where the fall
  line is taken; at least 60 ft from every house and well footprint (the engine's `BOUNDARY_STONE_CLEAR_FT`, the
  measure of "outside the settlement" the wayside stones use - a guess for a burial ground); 180's water set-back as
  drawn bands (75 px from a stream, 50 px from a flooded field edge; at a hamlet's 1 ft per px, 75 and 50 ft); inside
  the map's frame; nearest the houses of the seats that pass. If none passes, the seat falls back to the nearest that
  clears the houses and the stream and the manifest says so (`meta.burial_ground_fallback`).
- **D4 - the village's cremation ground** (530, now the GM's ruling): `_roll_civic` seats one with
  `cremation_ground`, beside the burial ground or on its own at the edge downstream (530's knob, even odds), 120 ft
  from houses (the engine's pollution clearance); a hamlet draws none, nor a shrine or headman's house (FR-003: a roll
  test holds all three).
- **D5 - the village's burial ground** (269's 280 knob and 270 siting, handed over): designed with D3's machinery, but
  landed only after 269's R1 is on main (the Edge Case). A feature with an open task lands nothing, so if 269 is still
  hours off when D1-D4 are ready, D1-D4 land here and D5 is claimed as its own follow-up feature the day 269 lands
  (recorded in `/diagram/.clones/RESEARCH-CLAIMS.md` and told to "Diagram supplemental"), carrying this design.
- **D6 - reviews**: the five pool hamlets re-roll; one settlement-review per moved map (FR-005).

## Phases

1. T01: the record (done: 540, 210, 530, the checks). 2. T02: the hamlet stage, red-first tests. 3. T03: the village
cremation ground and the no-village-features roll test. 4. T04: the pool re-roll and reviews. 5. T05: `make done`,
push. The village burial ground (D5) is a follow-up feature once 269 lands.
