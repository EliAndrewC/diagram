# Tasks - feature 306, seat by packing

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Research: [`research.md`](research.md).

## Occasions

- none: D1 sizes the seat band each hamlet's homesteads are offered on (every map's cluster moves, looser), but no element is
  new to a map, no glyph is redrawn and no placement rule changes - every seat passes the same rules; D5 and D6 leave every
  answer identical.

## Phase 0 - the prototype rounds (US1; FR-001, FR-002, FR-011)

- [ ] T01 [US1] Rounds 1-7 prototyped and measured (`prototype.py`; research R1-R7): the capacity prediction, the seats beside the
      tree, grown from the houses, along lanes (NO-GO); the dry-spell cap, the rescue, the band's figure (GO for the figure)
      research: rendering
      verify: research R1-R7 with every round's numbers
- [ ] T02 [US1] The rescue and the dry cap on top of the figure, sixteen seeds at 40 households (plan D2): built or withdrawn
      research: rendering
      verify: research R9

## Phase 1 - the band (US2; FR-010, FR-008)

- [ ] T10 [US2] `306-start` bookend on the unmodified engine; the cohort baseline
      research: rendering
      verify: the snapshot file; the cohort's pass count
- [ ] T11 [US2] D1: `SEATING_GROUND_FT = 162` added for the seating's band, with its derivation; `HOMESTEAD_GROUND_FT` stays
      104 for the margin, canvas and belt; the tests pinning the band updated in the same edit
      research: rendering
      verify: `make quick` green
- [ ] T12 [US2] Inashiro regenerated, then the pool (`make maps SCOPE=all`) and the cohort (`make cohort N=24`): every rule passes,
      every household seated, the cohort at least the base's
      research: rendering
      verify: `maps clean`; the cohort count in research.md
- [ ] T13 [US2] The scaling leg against the base, back to back: SC-002, SC-003, SC-006 judged; a miss recorded and raised
      research: rendering
      verify: research R9 or R12 with the figures

## Phase 2 - the census (US3; FR-006, FR-007)

- [ ] T20 [US3] Red: the census tool's tests - a deliberate per-candidate scan in a stand-in check flagged over the threshold, an
      indexed one not; the pool-spec capture; the report's rows
      research: rendering
      verify: `make test-file` fails for the missing tool
- [ ] T21 [US3] Green: `tools/overlap_census.py`, `make census`, `make perf` running it (D4)
      research: rendering
      verify: `make quick`; 100% coverage of the tool; `make census` lists R10's nine
- [ ] T22 [US3] Every flagged check (D5), starting with R10's nine: indexed, boxed or lined - identical answers preferred (an
      equivalence test), a moved answer held to FR-008 - or, where the fix is slower, recorded why not
      research: rendering
      verify: research R13 per check; the pool manifests identical where the answers are
- [ ] T23 [US3] The census re-run after T22: what still flags, each resolved or recorded
      research: rendering
      verify: research R13's closing list

## Closing

- [ ] T30 D6 (the planted region's sliver line) in with its test
      research: rendering
      verify: `make test-file FILE=tests/waterfields/test_partition.py`
- [ ] T31 `306-end` bookend, `make perf-report AGAINST=306-start`; any band explained
      research: rendering
      verify: the bands printed
- [ ] T32 `dev/performance.md` "Seat by packing (feature 306)"; the memory note
      research: rendering
      verify: the section names each lever's gain and every withdrawn round
- [ ] T33 `make done` green; push
      research: rendering
      verify: the gate; `sync-with-main.sh done` lands
