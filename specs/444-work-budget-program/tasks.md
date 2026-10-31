# Tasks - feature 444, the work-budget program

## Occasions

- none: step 3 (T01-T06) is tooling and paper budgets - no map feature, glyph or placement rule; each phase task, filed after the
  GM's checkpoint, declares its own

## Tasks

- [x] T01 A budget counts the derivation's own items: `items_at_20`, `items_at_40`, `items_at_80` beside `per_thing`, required by `make budget-set`, read by `make work-budget` and the push's ratchet, a row without them refused; the bundle's form check requires the contract's Reads, Writes and Keeps lines (D2, D1; FR-001)
      research: rendering
      verify: DONE. landed: landed: the derivation's own items (items_at_20/40/80) beside per_thing - budget-set requires them, the record and the ratchet read them and refuse a budgeted row without them (the placed-things product retired); the bundle's form check requires the contract's Reads, Writes and Keeps lines; each red with its condition deleted
- [x] T02 The water family's budgets - water_frame, field, sink, waterward, pond_stock, pond_bank - each derived in the template, judged SOUND by the work-budget agent or accepted by the round arbiter (FR-013), and pinned (D1, D3, D4; FR-001)
      research: rendering
      verify: DONE. landed: landed: the water family's six budgets pinned - water_frame (40), waterward (1), pond_stock (1), pond_bank (155 a seat) and sink (37.5 a segment gathered) on SOUND verdicts, field (35,440 at 20, 56,558 at 40, 94,717 at 80) on the round arbiter's accept (FR-013: 14 rounds, spread 32,280-38,506 at 20); each derivation passing the pre-dispatch checks
- [x] T03 The homesteads family's budgets - seat, homesteads, appurtenances, burial, lane_wells, sties, washing (D1, D3, D4; FR-001)
      research: rendering
      verify: DONE. landed: the homesteads family's seven budgets pinned: seat and burial on SOUND; homesteads, appurtenances, sties, washing and lane_wells on the round arbiter's accepts (FR-013)
- [x] T04 The ways family's budgets - track, web, crossings (D1, D3, D4; FR-001)
      research: rendering
      verify: DONE. landed: the ways family's three budgets pinned: track, web and crossings, each on the round arbiter's accept (FR-013)
- [x] T05 The hinterland and frame family's budgets - hinterland, woodland, windbreak, bamboo, frame, notice, labels (D1, D3, D4; FR-001)
      research: rendering
      verify: DONE. landed: the hinterland and frame family's seven budgets pinned: labels, bamboo and frame on SOUND; notice, windbreak, woodland and hinterland on the round arbiter's accepts (FR-013)
- [x] T06 The program's target - the sum at 40 households and the whole roll's exponent - to the GM through escalation-check, his words set by `make budget-program`: the CHECKPOINT before any phase (D5; FR-002)
      research: rendering
      verify: DONE. landed: the program's target set with the GM's words (make budget-program): 57,235 operations at 40 households, exponent 0.87, about 1,431 a household; water_frame, burial and bamboo raised to their greenfield SOUND figures on the same words
- [x] T07 A derivation's arithmetic and its index cells checked before any dispatch: a ## Totals section evaluated by make work-budget-bundle MODE=budget (a missing size or a value off its expression refused), and an indexed derivation refused without a cells-examined row (the GM's rule on repeated errors, 2026-10-28)
      research: rendering
      verify: DONE. landed: landed: the Totals section evaluated exactly, every count row's figure a term of its size's total (each row its own, the arbiter's note), a row with no figure refused, an indexed derivation without a cells row refused; the agent's fourth question; the fixtures and the water family's six derivations passing; each refusal red with its condition deleted
- [x] T08 An arbiter accept pins a first budget: make budget-set ARBITER=ask:<id> (refused without an accept naming the stage), bound to its derivation (a changed derivation flagged as owing the arbiter's ruling) - FR-013, SC-008
      research: rendering
      verify: DONE. landed: landed: make budget-set ARBITER=ask:<id> SPREAD= pins a first budget on the round arbiter's accept naming the stage (FR-013), recording its derivation's sha256, rounds and spread; a changed accept-pinned derivation refused by make work-budget and the push's ratchet; each red with its condition deleted
- [x] T09 The budgets re-scored to the typical case - the 13 accept-pinned in one arbiter batch, a SOUND one where the gate fires, each lowered (FR-014; research: rendering)
      research: rendering
      verify: DONE. landed: every budget re-scored to the typical case (FR-014) and pinned, the program 1,409,176 operations at 40 from 15.3M
- [x] T10 Today's code's names refused by the budget bundle: a derivation naming a module, function, method, class or module- or class-level name defined under `l7r/` (other than a knob's name or form, a stage's name or a manifest key) refused, naming each; the `- pruning:` line asked above the reference (FR-015, FR-016, SC-010)
      research: rendering
      verify: DONE. landed: the budget bundle refuses a derivation naming any module, function, method, class or module- or class-level name of today's code (a knob's name or form, a stage's name and a manifest key pass), and asks a pruning line above the reference; each red with its condition deleted
- [x] T11 The water family re-derived greenfield - water_frame, field, sink, waterward, pond_stock, pond_bank - each contract from the research and the reference manifests, judged with rubric S9, pinned (FR-015, FR-016)
      research: rendering
      verify: DONE. landed: the water family re-derived greenfield: field 23,988 at 40 (from 29,232), sink 149 (from 3,638), pond_bank 142 (from 2,065), waterward and pond_stock 1, each pinned on its SOUND with LOWER=1; water_frame SOUND at 69 against its pin of 40, left standing for the GM's words (FR-015)
- [x] T12 The homesteads family re-derived greenfield - seat, homesteads, appurtenances, burial, lane_wells, sties, washing (FR-015, FR-016)
      research: rendering
      verify: DONE. landed: the homesteads family re-derived greenfield: homesteads 4,118 at 40 (from 243,411), appurtenances 713 (from 5,457), lane_wells 292 (from 115,719), washing 1,194 (from 4,937) on the round arbiter's accepts; seat 191 and sties 138 on SOUND, each LOWER=1; burial SOUND at 77 against its pin of 3, left standing for the GM's words (FR-015)
- [x] T13 The ways family re-derived greenfield - track, web, crossings (FR-015, FR-016)
      research: rendering
      verify: DONE. landed: the ways family re-derived greenfield: web 1,160 at 40 (from 91,798) on the round arbiter's accept, track 223 (from 2,090) and crossings 442 (from 7,879) on SOUND, each LOWER=1 (FR-015)
- [x] T14 The hinterland and frame family re-derived greenfield - hinterland, woodland, windbreak, bamboo, frame, notice, labels (FR-015, FR-016)
      research: rendering
      verify: DONE. landed: the hinterland and frame family re-derived greenfield: hinterland 19,058 at 40 (from 784,872), notice 1,160 (from 16,884), frame 637 (from 7,826) on the round arbiter's accepts; windbreak 3,183 (from 71,854), woodland 5 (from 12,516), labels 6 on SOUND, each LOWER=1; bamboo SOUND at 288 against its pin of 252, left standing for the GM's words (FR-015)
- [x] T15 phase: water_frame - the plan's rolls counted where they happen, through the checklist (FR-003-FR-005)
      research: rendering
      phase: water_frame
      resume (2026-10-30, after the GM's "you can begin the waterframe port to Rust"): the derivation is corrected to the 21 plan fields plan_site rolls (ask:444-T19-which-knobs) and pinned SOUND at 56 (water_frame_greenfield.verdict-2.txt, LOWER from 69); no port code yet. Its inputs: decisions D6-D9 (plan.md), the rulings on ask:444-T19-output-keys, ask:444-T19-plan-site and ask:444-T19-which-knobs (arbiter.jsonl), phases/water_frame.keys.json, phases/water_frame.plan_site.md (its last section: the 21 knobs), the derivation. Next: one logged `make phase-read` of plan.py to replace plan_site's rolls of the 21 knobs and 2 bearings with the Rust call (the branch order: the settlement form first, each knob rolled only on its branch - the derivation's knob row), the crate under rust/phases/ (D7's SplitMix64, D9's counters feature), D8's build, then cache audit and the overlap census proven on the port before the tick. After T19: T18's research pass, then T16.
      verify: DONE. landed: water_frame accepted: the plan's rolls counted where they happen and counted as the stage's own work (S5), 23 at 10-80 against 69, MODE AUDIT WITHIN; the work-budget run counts a stage over every roll it finished
- [ ] T16 phase: field - the comb field rebuilt in Rust to its greenfield derivation under the single-field cap, through the checklist (FR-003-FR-006, FR-017, FR-018)
      research: rendering
      phase: field
- [x] T17 FR-011's Rust tooling proven on a Rust fixture, every one-for-one, partial or rewritten row firing (FR-011, FR-017)
      research: rendering
      verify: DONE. landed: the Rust tooling proven on the fixture crate: 18 rows proven, cache audit and the overlap census owed by T19 (the round arbiter's Route A, narrowed by the plan review); a Rust phase's landing refused while any row is unproven
- [ ] T18 the field re-derived under the single-field cap, its MODE BUDGET verdict (FR-018)
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
- [ ] T19 phase: water_frame - its Rust port, written from its derivation (FR-010, FR-017)
      research: rendering
      phase: water_frame
      owes (the round arbiter, ask:444-T17-rows-need-a-phase; the plan review of 2026-10-30): the two tooling rows T17 left to the first phase - `cache audit` and `the overlap census` (dev/rust-tooling.md) - each proven on the port and named in its "Proven" table before the tick
- [ ] GM review (make gm-reviewed F=444) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
