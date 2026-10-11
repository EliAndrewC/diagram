# Tasks: one view of the sheet for the program example's captions (feature 340)

**Input**: plan.md (D1-D6). D3 is amended into the plan from T02's measurement and re-reviewed before T03 starts.

## Occasions

- layout-revised: county-magistracy-example - its captions re-seated through the one view (after T03)

## Tasks

- [x] T01 the composed draft declares its captions (FR-001, D1); seats unchanged, held by a test
      research: rendering
      verify: DONE. the composed draft declares every caption (data-id on drawn shapes, data-names on captions; the straw mats over every mat, the tubs every tub); seats unchanged (all 49 text positions equal, the draft identical apart from the declarations); tests/test_compound_declarations.py
- [x] T02 the harness: every disagreement attributed, each fix's removals reported, recorded in measurements.json (FR-002, D2)
      research: rendering
      verify: DONE. harness.py: on the declared draft 11 of 45 captions seat apart, 10 explained by the three sources (view 5, subject 2, the three together 3), width 0; fix 1 removes 5, fix 2 removes 2 (m:caption-disagreements); each subject tried in order as hand_sheet.seat does
- [x] T03 the switch to the measured fix, strictness kept (FR-003, FR-004, D3, D4); tests at 100%
      research: rendering
      verify: DONE. the composer seats through the one view - classify per caption and subject (declared shapes never block; the dark-fill and outline rules kept), the declared subjects in order, char_w_of; late obstacles retired; 3 apart after, none from the three sources (m:caption-disagreements-after); compound.py 100%
- [x] T04 performance read and recorded (FR-005, D5); `make done`; the building-review the Occasions owe
      research: rendering
      verify: DONE. m:composition-timing recorded (1.24 s one view vs 0.24 s own index, ObstacleIndex.copy, accepted in D5); make done green; building-review PASS on county-magistracy-example (N1 fixed in its notes); compound.py split into compound_view.py under the 1,000-line bar
