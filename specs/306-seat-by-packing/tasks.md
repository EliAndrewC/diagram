# Tasks - feature 306, seat by packing

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Research: [`research.md`](research.md).

## Occasions

- none: D1 sizes the seat band each hamlet's homesteads are offered on (every map's cluster moves, looser), but no element is
  new to a map, no glyph is redrawn and no placement rule changes - every seat passes the same rules; D5 and D6 leave every
  answer identical.

## Phase 0 - the prototype rounds (US1; FR-001, FR-002, FR-011)

- [x] T01 [US1] Rounds 1-7 prototyped and measured (`prototype.py`; research R1-R7): the capacity prediction, the seats beside the
      tree, grown from the houses, along lanes (NO-GO); the dry-spell cap, the rescue, the band's figure (GO for the figure)
      research: rendering
      verify: DONE. rounds 1-7 in research R1-R7: capacity by packing, seats beside the tree, grown from the houses, along lanes - NO-GO; the dry cap, the rescue, the band's figure - GO
- [x] T02 [US1] The rescue and the dry cap on top of the figure, sixteen seeds at 40 households (plan D2): built or withdrawn
      research: rendering
      verify: DONE. R15: the band 100.0 -> with both 83.3 s over sixteen seeds; built (plan D2)

## Phase 1 - the band (US2; FR-010, FR-008)

- [x] T10 [US2] `306-start` bookend on the unmodified engine; the cohort baseline
      research: rendering
      verify: DONE. 306-start dev/perf-log/20261002T071251Z-306-start-base306.json on 8d15b8a27; cohort base 30/30
- [x] T11 [US2] D1: `SEATING_GROUND_FT = 162` added for the seating's band, with its derivation; `HOMESTEAD_GROUND_FT` stays
      104 for the margin, canvas and belt; the tests pinning the band updated in the same edit
      research: rendering
      verify: DONE. SEATING_GROUND_FT 162 in consts.py (HOMESTEAD_GROUND_FT 104 kept); _seat_households' lattice and bound; tests updated; make done green
- [x] T12 [US2] Inashiro regenerated, then the pool (`make maps SCOPE=all`) and the cohort (`make cohort N=24`): every rule passes,
      every household seated, the cohort at least the base's
      research: rendering
      verify: DONE. make maps SCOPE=all clean; make cohort N=24 30/30 on the final engine (R14)
- [x] T13 [US2] The scaling leg against the base, back to back: SC-002, SC-003, SC-006 judged; a miss recorded and raised
      research: rendering
      verify: DONE. R15 + R16: SC-002/SC-003 missed (recorded, raised), SC-004/005 met, SC-006 total -13.8% with two seeds explained (band 2)

## Phase 2 - the census (US3; FR-006, FR-007)

- [x] T20 [US3] Red: the census tool's tests - a deliberate per-candidate scan in a stand-in check flagged over the threshold, an
      indexed one not; the pool-spec capture; the report's rows
      research: rendering
      verify: DONE. tests/tools/test_overlap_census.py red on the missing tool
- [x] T21 [US3] Green: `tools/overlap_census.py`, `make census`, `make perf` running it (D4)
      research: rendering
      verify: DONE. tools/overlap_census.py, make census, make perf runs it; 100% coverage; first run listed R10's nine
- [x] T22 [US3] Every flagged check (D5), starting with R10's nine: indexed, boxed or lined - identical answers preferred (an
      equivalence test), a moved answer held to FR-008 - or, where the fix is slower, recorded why not
      research: rendering
      verify: DONE. nine indexed, all exact: byte-identical pool, equivalence tests with the old scans as oracles (R13)
- [x] T23 [US3] The census re-run after T22: what still flags, each resolved or recorded
      research: rendering
      verify: DONE. make census after: 0 over 5,000, the largest 2,624 (R13; the 306-end bookend's census)

## Closing

- [x] T30 D6 (the planted region's sliver line) in with its test
      research: rendering
      verify: DONE. region_rings polygons only; test_a_sliver_line_in_the_region_is_not_a_ring passes
- [x] T31 `306-end` bookend, `make perf-report AGAINST=306-start`; any band explained
      research: rendering
      verify: DONE. 306-end vs 306-start: band 2 (40 hh seed 39 +10.3%), explained with controls; perf-audit dispatched
- [x] T32 `dev/performance.md` "Seat by packing (feature 306)"; the memory note
      research: rendering
      verify: DONE. dev/performance.md 'Seat by packing (feature 306)'; memory project_seat_by_packing_306
- [ ] T33 `make done` green; push
      research: rendering
      verify: the gate; `sync-with-main.sh done` lands
