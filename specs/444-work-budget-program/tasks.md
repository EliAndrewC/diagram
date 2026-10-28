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
- [ ] T03 The homesteads family's budgets - seat, homesteads, appurtenances, burial, lane_wells, sties, washing (D1, D3, D4; FR-001)
      research: rendering
- [ ] T04 The ways family's budgets - track, web, crossings (D1, D3, D4; FR-001)
      research: rendering
- [ ] T05 The hinterland and frame family's budgets - hinterland, woodland, windbreak, bamboo, frame, notice, labels (D1, D3, D4; FR-001)
      research: rendering
- [ ] T06 The program's target - the sum at 40 households and the whole roll's exponent - to the GM through escalation-check, his words set by `make budget-program`: the CHECKPOINT before any phase (D5; FR-002)
      research: rendering
- [x] T07 A derivation's arithmetic and its index cells checked before any dispatch: a ## Totals section evaluated by make work-budget-bundle MODE=budget (a missing size or a value off its expression refused), and an indexed derivation refused without a cells-examined row (the GM's rule on repeated errors, 2026-10-28)
      research: rendering
      verify: DONE. landed: landed: the Totals section evaluated exactly, every count row's figure a term of its size's total (each row its own, the arbiter's note), a row with no figure refused, an indexed derivation without a cells row refused; the agent's fourth question; the fixtures and the water family's six derivations passing; each refusal red with its condition deleted
- [x] T08 An arbiter accept pins a first budget: make budget-set ARBITER=ask:<id> (refused without an accept naming the stage), bound to its derivation (a changed derivation flagged as owing the arbiter's ruling) - FR-013, SC-008
      research: rendering
      verify: DONE. landed: landed: make budget-set ARBITER=ask:<id> SPREAD= pins a first budget on the round arbiter's accept naming the stage (FR-013), recording its derivation's sha256, rounds and spread; a changed accept-pinned derivation refused by make work-budget and the push's ratchet; each red with its condition deleted
- [ ] GM review (make gm-reviewed F=444) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
