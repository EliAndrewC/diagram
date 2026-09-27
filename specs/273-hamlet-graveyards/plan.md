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

- **D1 - a KNOB, not a rule** (540, plan review round 1): the history gives two answers - most forms put a hamlet's
  dead by the hamlet, but the grave at the parish temple was half an obligation and most households were registered
  with temples outside their village (500) - so, as the GM asked, each hamlet rolls `hamlet_burial`: "own_ground" (a
  burial ground at its edge, drawn as the village's organic common ground, `cemetery(parish=False)`, research 150) or
  "village_ground" (none; its dead lie in the village's ground by the shrine, the setting's parish temple). Even odds,
  a GUESS; a pinned value is honored and a nonsense one refused. Class: both forms accurate, the odds a guess.
- **D2 - its size**: within the 750 to 2,450 sq ft 160 reckons for a hamlet's FULL-BODY ground, set by households (5
  or fewer at the floor, 30 or more at the top, linear between) - a GUESS, since the band overstates an urn ground
  (540 says so); drawn about 1.4 to 1, a guess.
- **D3 - its seat**: the nearest seat out from the middle of the houses that clears everything below, and among
  equally near seats the one nearest the fall line (below the houses where it can - a scan that followed the fall
  line out to its reach put the ground across a hamlet's paddies from its houses, found by its own test): 60 ft from
  every house and well footprint (540's figure: the engine's `BOUNDARY_STONE_CLEAR_FT`, the distance the wayside
  stones take for the edge of a settlement - a guess for a burial ground); 180's water set-backs as drawn bands
  (75 px from a stream, 50 px from a flooded field edge; 1 ft per px on a hamlet); the engine's own `_fits` and
  footprint test; inside the canvas. No seat within the reach: no ground, and the manifest says `no seat`.
- **D4 - the village's cremation ground** (530, now the GM's ruling): `_roll_civic` rolls 530's seat knob
  (`cremation_seat`: beside the burial ground, or on its own at the edge, even odds, a guess) and seats the ground at
  the village's edge, down the fall line first, 120 ft clear of houses and wells (the engine's pollution clearance),
  30 px from water (180's fixed cremation margin), its fire bed off the shrine's approach, within ~650 ft of the middle
  of the houses (530), with six stone jizo at it (530; `cremation_ground(jizo=True)`, default off so no other map's
  glyph moves). Until the village draws a burial ground (D5), "beside" has nothing to stand beside, so it seats as on
  its own and the manifest says so (`meta.cremation_seat_note`).
- **D4b - which generators**: the scripted hamlet generator (`hamletgen`) is the only live hamlet generator; the
  roller's hamlet and village tiers (`settlement/rolling/roll.py`) are called only by the frozen legacy exhibits, which
  never re-roll (the pool doctrine: conversion, not retrofit), and by tests. So D1-D3 live in `hamletgen`, and D4 in
  the roller's village tier, where the village's civic features are drawn; a roll test holds that no hamlet from
  either generator draws a cremation ground, a shrine or a headman's house (FR-003).
- **D4c - the field graves** (Kashikawa, Mizuguchi): the in-field grave island is a separate calibrated liberty
  (research fields, the GM's ruling of 2026-07-20) - a family's grave among its fields, not the hamlet's burial ground
  - and this feature leaves it unchanged; a hamlet may carry both.
- **D5 - the village's burial ground** (269's 280 knob and 270 siting, handed over; 160's band as a rule in the
  population served, from 269): T06 builds it if 269's 270 and 280 are on main when T01-T05 are done; otherwise T06 is
  ticked by claiming the follow-up feature that carries this design (a feature with an open task cannot land).
- **D6 - reviews**: the pool hamlets whose roll draws a ground re-roll; one settlement-review per moved map (FR-005).
- **D7 - 160**: its hamlet clause and the village band are 269's to rewrite (in its R1 queue, agreed 2026-09-27: "a
  hamlet's dead lie either in a burial ground of its own at its edge or in the village's ground, rolled per hamlet";
  the village band a rule in the population served); this feature does not edit 160.

## Phases

1. T01: the record (done: 540, 210, 530, the checks). 2. T02: the hamlet stage, red-first tests. 3. T03: the village
cremation ground and the no-village-features roll test. 4. T04: the pool re-roll and reviews. 5. T05: `make done`,
push. The village burial ground (D5) is a follow-up feature once 269 lands.
