# Tasks: the magistracy sheets' open findings (feature 335, carrying 339, 341, 342)

**Input**: plan.md (decisions D1-D9). Each sheet is redrawn once, after the checks are red on their fixtures; each revised
magistracy sheet is reviewed once, after all its redraws.

## Occasions

- layout-revised: hayakawa-magistracy - the landing steps notched into the revetment, 14 doors set inside their walls, the garden well removed, the storehouses slid west over the rear pocket
- layout-revised: ochiba-magistracy - 7 doors set inside their walls
- layout-revised: ubame-magistracy - 14 doors set inside their walls, the torii in plan, the rear yard reaching the reception privy, the servants' partitions as sliding partitions
- glyph-redrawn: torii on ubame-magistracy - the approach arch from an elevation silhouette to the plan form
- glyph-redrawn: river landing on hayakawa-magistracy - the flight of steps notched into the revetment
- placement-changed: door on hayakawa-magistracy - every door set wholly inside its building, flush to its wall

## Phase 1 - the tools (red before green)

- [x] T01 aligned gaps across a third building (FR-014, D9)
      research: rendering
      verify: DONE. DONE. _blocked tested the third building's y-extent against the gap's x-interval in the horizontal case; one test now; tests/tools/test_pack_audit.py: three-in-a-row low on the sheet red then green, Ochiba's 28.7 ft pair gone (m:ochiba-aligned-gap)
- [x] T02 the three checks, each red on its frozen fixture: `steps_past_revetment`, `doors_off_their_walls`, `arch_in_plan` (FR-002, FR-005, FR-008; D1-D3)
      research: rendering
      verify: DONE. DONE. marks_drawn.py: steps_past_revetment, doors_off_their_walls (by tag; outside or floating), arch_in_plan; registered with red fixtures hayakawa-steps-and-doors-red.svg and ubame-torii-silhouette-red.svg (test_registry fires on each); door check red on HEAD Ochiba 7 and Ubame 14; unit tests test_pack_audit_marks.py; green on every pool sheet after the redraws

## Phase 2 - the record

- [ ] T03 a guest's roji carries no well (0104's drawing page) and the one door convention (0117's drawing page), from the page sessions (FR-011, FR-003; D6, D2)
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed

## Phase 3 - the sheets, each redrawn once

- [ ] T04 Hayakawa: the steps (FR-001), the doors (FR-004), the family's way (FR-010), the garden well (FR-011), the rear pocket (FR-012); its notes
      research: rendering
- [ ] T05 Ochiba: the doors (FR-004); its notes
      research: rendering
- [ ] T06 Ubame: the doors (FR-004), the torii (FR-006), the rear yard (FR-009), the servants' partitions (FR-013); its notes
      research: rendering
- [ ] T07 `docs/buildings.md`: the door rule (FR-003) and the "Modest shrine" clause (FR-007)
      research: rendering

## Phase 4 - verified

- [ ] T08 every sheet through `make pack-audit` and its gen; the harness at SC-001..SC-003; `make done`; the reviews the Occasions owe, each within two rounds (FR-015, SC-004, SC-005)
      research: rendering
- [ ] GM review (make gm-reviewed F=335) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
