# Tasks - feature 299, natural marsh edges

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (A-D).

- [x] T01 [US1] `land/outline.py` `natural_outline`, called from `marsh()` for every role but the pond fringe; its tests (A)
      research: rendering
      verify: DONE. land/outline.py natural_outline (rounded r 60, inward wave 0-40 ft, simplified 1 ft) for every role but the pond fringe; pond_cut (the pond as its ellipse); tests/settlement/test_outline_299.py
- [x] T02 [US2] The scrub keeps off the recorded marsh once one exists (B)
      research: rendering
      verify: DONE. hinterland hands the scrub no laid toe band once a marsh is recorded; test_the_scrub_meets_a_recorded_marsh_without_a_gap
- [x] T03 [US2] [US3] The fringe tile and band, the overlays, the reed tile's even haze; their tests (C)
      research: rendering
      verify: DONE. fringe tile + FRINGE_FT band in each side's slot; grass-clumps (97 ft) and reed-clumps (197 ft) overlays; reed tile 128 ft with an even haze; BoxObstacles by RingIndex (Sawada hinterland 0.43 s, base 0.42-0.44)
- [x] T04 The record (vegetation 125, 050; the marsh's drawing), record-format and entry-drift; Inashiro's manifest test (SC-001) (D)
      research: rendering
      verify: DONE. vegetation 125 (heading restored, the grading drawn), record-format applied; entry_owed none; gate test SC-001 fires on the base map (91-degree corner, 592 ft run) and passes now
- [x] T05 The pool regenerated and timed; the gate green; the GM's look at Inashiro; land (D)
      research: rendering
      verify: DONE. pool regenerated; make done green (89 s); Inashiro, Sawada, Kuwabata looked at; land
