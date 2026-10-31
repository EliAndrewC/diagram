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
      resume (2026-10-31, items 1-4 done): the port is written, proven and accepted - the cache audit and the overlap census proven on it (no tooling row unproven), FR-004 (water_frame.fr004.md) and FR-012 (water_frame.fr012.md) measured, MODE AUDIT WITHIN (water_frame.audit-3.txt) and `make budget-accept` at 56. Left before the tick: `make cohort-landing`, the settlement-reviews of the pool hamlets the port moves (inashiro and sawada already moved in the tree; `make maps` regenerates the rest), then `make land F=444 T=T19` with the landing note naming the rolls outside water_frame's derivation (ask:444-T19-plan-site point 4) and the per-form counts (linear 64, dispersed 58, a nucleated polder 52, the reference 56). UPDATE 2026-10-31T03Z: the landing cohort refused (47 of 54 against main's 54; seeds 3, 20, 21, 36, 37, 903, 904 newly failing in later stages), Kashikawa and Sawada pinned to their shipped plans (they refused under the re-roll); four pool maps regenerated and uncommitted in the tree. Next: plan.md's `### T19 part B` item 7 - each seed's refusal dumped and diagnosed (3 and 903 through web.py's open found row E3) - then the route to the round arbiter.
      verify: DONE. landed: water_frame accepted: the plan's rolls counted where they happen and counted as the stage's own work (S5), 23 at 10-80 against 69, MODE AUDIT WITHIN; the work-budget run counts a stage over every roll it finished
- [ ] T16 phase: field - the comb field rebuilt in Rust to its greenfield derivation under the single-field cap, through the checklist (FR-003-FR-006, FR-017, FR-018)
      research: rendering
      phase: field
- [x] T17 FR-011's Rust tooling proven on a Rust fixture, every one-for-one, partial or rewritten row firing (FR-011, FR-017)
      research: rendering
      verify: DONE. landed: the Rust tooling proven on the fixture crate: 18 rows proven, cache audit and the overlap census owed by T19 (the round arbiter's Route A, narrowed by the plan review); a Rust phase's landing refused while any row is unproven
- [x] T18 the field re-derived under the single-field cap, its MODE BUDGET verdict (FR-018)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. landed: the single-field cap researched (research-pass ATTESTED: one tract from one intake about 1-45 ha, the largest Fei's polder of about 60 ha) and recorded in 0017 (#how-large-one-tract-of-paddy-grew) and its drawing page (the cap a knob of 45-60 ha, several fields past it) by two page sessions, the record's checks run and applied; the field's greenfield derivation re-derived under it - one field at 20/40/80 households (11/21/42 ha), no figure changed - MODE BUDGET verdict-3 SOUND, the standing pin (23,988 at 40, exponent 0.79) unchanged; the claims round on 0017's change: fit_field and fit_polder IN-STEP
- [x] T19 phase: water_frame - its Rust port, written from its derivation (FR-010, FR-017)
      research: rendering
      phase: water_frame
      owes (the round arbiter, ask:444-T17-rows-need-a-phase; the plan review of 2026-10-30): the two tooling rows T17 left to the first phase - `cache audit` and `the overlap census` (dev/rust-tooling.md) - each proven on the port and named in its "Proven" table before the tick
      verify: DONE. landed: water_frame ported to Rust (rust/phases/src/water_frame.rs, pyrand.rs): the plan's fall and 21 knobs rolled in Rust with knob_rng's own draws reproduced (SHA-256, MT19937, randrange), so every seed keeps its plan; cohort-landing 54 of 54, no regressed seed; the pool hamlets regenerate with main's layouts and renders (meta differs only for knobs off their form's branch, hidden by the title card); water_frame counted 56 against its budget of 56, MODE AUDIT WITHIN; impl-drift recorded on 38 claims, none owed; the gate stamp now hashes the Rust sources; the old Python rolls deleted in this landing (FR-005)
- [x] T20 Tooling from T19's landing: make land runs make work-budget at the engine it pushes before the push (refused twice, T17 and T19, each costing a gate); the tick reports every refusal together instead of the first of an or-chain (T19 took four landing rounds, one refusal each: part A's stamp, the plan review, part B's items 8-9, the plan gate); make decide refuses a section whose Approach is stamped before its Decisions, before dispatching the review it owes; the plan gate reads a restamped heading with an unchanged body as the same block, not a removal
      research: rendering
      verify: DONE. landed: the four tooling gaps T19's landing found, each pinned by a test red without its fix: land.py makes and commits a missing work-budget run before the push (tests/tooling/test_land_budget.py); the tick lists every refusal together (test_tick_task.py); make decide asks the approach checklist first (test_plan_gate.py); a re-dated heading with its text unchanged is the same block, neither its removal nor the new key owed (test_plan_gate.py)
- [x] T21 The Rust stage gate and the failing-seed list (amendment 5, FR-019, FR-020): make rust-gate, the checks asked by what they read, the landing held to it
      research: rendering
      verify: DONE. landed: amendment 5's Rust stage gate, each part pinned by a test: make rust-gate rolls a fresh block of 48 (the start a hash of the engine key, which covers rust/**), the six pinned row variants on fresh seeds and the failing list through the Rust stages alone, judging the checks where each Rust stage completes by what they read (Rust-owned across the run, or held by the fresh map); a failing seed joins the list with its stage's frozen input until both pass; every engine landing needs a clean record on its engine, and a Rust-stage landing reads its cohort as a rate; make land makes the record first, where owed. make rust-gate: 54 seeds through water_frame, 0 failing; impl-drift on 18 claims, all IN-STEP
- [ ] T22 water_frame's open claims closed (FR-021, amendment 6): the 15 open findings on its port - water_frame.rs's 8 MISLABELED, its DRIFTED fall-backs-the-wind and UNCLAIMED fall quantization, roll_plan's and stage_water_frame's CANNOT-TELL, _KNOBS's CANNOT-TELL and _rust_rolls's two UNCLAIMED decisions - each fixed in the code or its claim and re-checked IN-STEP
      research: rendering
- [ ] GM review (make gm-reviewed F=444) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
