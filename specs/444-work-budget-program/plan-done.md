# 444-work-budget-program - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-28 -->
### T01 - a budget counts the derivation's own items (D2)

`items_at_20`, `items_at_40` and `items_at_80` beside `per_thing`; `make budget-set` requires them; `make work-budget` and the ratchet read them and refuse a budgeted row without them. And the bundle's form check requires the contract's four parts: its `Reads:`, `Writes:` and `Keeps:` lines (the cohort properties and the claims), each filled (the design's checklist box 1).

### T01 Approach (checklist part A)

1. **The goal, in the world.** A stage's budget means the derivation's arithmetic, at each size, whatever the manifest counts.
2. **The constraints.** FR-001; the spec's Edge Cases (a stage that places nothing has a whole-stage figure); D2.
3. **Where each comes from.** G: the design the GM approved, 2026-10-28 (`request.md`, section 2, S7).
4. **Do they describe the world here?** `seat` and `sink` place nothing, measured 2026-10-28 (`make work-budget`, run 20261028T152105Z-45aa176ec9b8, its placed column).
5. **The order.** First: every `budget-set` of T02-T05 needs it.
6. **The exits.** Green: tests set a budget with its items and read its budget at 20, 40 and 80 households in the record and the ratchet; `budget-set` without them refused, and a budgeted row without them refused by the record and the ratchet; red with each condition deleted. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** The tests green.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - tooling.

<!-- plan-archive: archived 2026-10-28 -->
### T07 - a derivation's arithmetic and its index cells checked before any dispatch (the GM 2026-10-28)

The GM's rule on a repeated error (`request.md`, 2026-10-28): *"anytime I hear you say that something went wrong and that you will address this by being careful in the future, then I tend to think that that will not work, unless being careful specifically means that our checklist-based process has been updated to include whatever "careful" means in that context"*.

- **Approach**: the derivation template gains a `## Totals` section - one line per size, `- at <20|40|80>: <expression> = <value>` - and `make work-budget-bundle MODE=budget` refuses, naming the line: a missing size; a value that differs from its expression's evaluation, rounded to the integer (exact - a sum written wrong); an expression that leaves out any count row's figure at that size (a total leaving out a term), every row writing its figure as `N at 20, N at 40, N at 80` or one number for every size, a row with none refused; and a derivation whose `Cheaper algorithms considered` says a grid or spatial index is used without a count row whose factor names the cells examined. A figure read at the wrong size or unit (a radius as a diameter, a record's keys as its points) no script can tell, so the `work-budget` agent's MODE BUDGET gains a fourth question asking exactly that. Why: of T02's first twelve rounds on the water family (2026-10-28, `phases/*.verdict-*.txt`), the session's own slips - a sum written wrong (19 + 8 as 26, sink round 2), a total leaving out a term (field round 1), index cells left uncounted (field round 3, sink round 3) - a script refuses; a figure read at the wrong size - the pond's radii read as halves, and a record's keys counted as its points, both found by the session, not the agent - is now the agent's own question.

### T07 Approach (checklist part A)

1. **The goal, in the world.** A derivation reaches the judge with its totals arithmetically true and its index cells counted.
2. **The constraints.** The GM's rule above; the rubric (an index cell examined is a basic operation).
3. **Where each comes from.** G: the GM, 2026-10-28 (`request.md`); O: T02's rounds (`phases/field.verdict-3.txt`, `phases/sink.verdict-2.txt`, `phases/sink.verdict-3.txt`).
4. **Do they describe the world here?** The water family's rounds, measured 2026-10-28 (the twelve verdicts recorded beside the derivations).
5. **The order.** Before T02's next dispatch; it applies to every derivation after it.
6. **The exits.** Green: the bundle refuses a missing size, a total off its expression, a total leaving out a row's figure, a row with no figure and an indexed derivation with no cells row; the agent file asks the fourth question; the fixtures pass in their concrete form, and so do the water family's derivations once their totals are written (T02's next dispatch runs on them); each refusal red with its condition deleted. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** The refusals' tests green.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - tooling.

<!-- plan-archive: archived 2026-10-28 -->
### T08 - an arbiter accept pins a first budget (FR-013, SC-008)

`make budget-set ARBITER=ask:<id>`: the budget pinned on the round arbiter's ACCEPT of the derivation, refused when the arbiter's log
holds no accept at that trigger naming the stage; the pin records `pinned_on: accept`, the derivation's sha256, its rounds (the
stage's recorded verdicts) and its totals' spread (`SPREAD="<low>-<high> at <households>"`, required), for the program target (D5). `make work-budget`
and the push's ratchet (`work_budget.held`) flag an accept-pinned budget whose derivation changed since its pin, as owing the arbiter's
ruling.

### T08 Approach (checklist part A)

1. **The goal, in the world.** A stage whose total converged but whose verdict never reached SOUND is pinned on the arbiter's accept, and stays bound to the derivation it accepted.
2. **The constraints.** FR-013, SC-008 (amendment 1).
3. **Where each comes from.** G: the GM, 2026-10-28, answering 444#0 (`request.md`).
4. **Do they describe the world here?** field's accept, ask:444-T02-field-round-15 in `arbiter.jsonl`, recorded 2026-10-28.
5. **The order.** Before field's pin and before T03's first review.
6. **The exits.** Green: tests refuse a pin on an accept the log does not hold naming the stage and pass one it does; a changed derivation flagged in the record and the ratchet; each red with its condition deleted. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** SC-008's tests green; field pinned on its accept.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - tooling.

<!-- plan-archive: archived 2026-10-28 -->
### T02 - the water family's budgets (D1, D3, D4)

water_frame, field, sink, waterward, pond_stock, pond_bank: each derived, judged SOUND, or accepted by the round arbiter (FR-013), and pinned.

### T02 Approach (checklist part A)

1. **The goal, in the world.** Each water stage has a budget an independent judge, blind to today's code and counts, found derived.
2. **The constraints.** FR-001; the rubric S1-S7; the template (443 T13); D1, D3.
3. **Where each comes from.** G: the design the GM approved, 2026-10-28 (`request.md`, step 3).
4. **Do they describe the world here?** Each stage's contract, read when its derivation is written from D1's five sources: its docstring, the `plan` fields it reads, the manifest keys and registries it writes (`dev/placement.md`'s `STAGES` table and draw order), its claims (`make claims-report`) and the cohort's checks of what it places (`cohort_audit`'s rules).
5. **The order.** After T01.
6. **The exits.** Green: six verdicts recorded, each SOUND or an arbiter accept (FR-013), and six budgets pinned. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; six dispatches, more where a verdict asks a correction.
9. **Done, measured.** Six `budgeted` rows in `dev/work-budget.json`, each with its derivation and verdict.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - paper budgets; no code a roll runs changes.

<!-- plan-archive: archived 2026-10-28 -->
### T03 - the homesteads family's budgets (D1, D3, D4)

seat, homesteads, appurtenances, burial, lane_wells, sties, washing (seven, of D4's census of `STAGES`): each derived, judged SOUND, or accepted by the round arbiter (FR-013), and pinned.

### T03 Approach (checklist part A)

1. **The goal, in the world.** Each homesteads-family stage has a budget an independent judge found derived.
2. **The constraints.** FR-001; the rubric; the template; D1, D3.
3. **Where each comes from.** G: the design the GM approved, 2026-10-28 (`request.md`, step 3).
4. **Do they describe the world here?** Each stage's contract, read when its derivation is written from D1's five sources: its docstring, the `plan` fields it reads, the manifest keys and registries it writes (`dev/placement.md`'s `STAGES` table and draw order), its claims (`make claims-report`) and the cohort's checks of what it places (`cohort_audit`'s rules).
5. **The order.** After T01.
6. **The exits.** Green: seven verdicts, each SOUND or an arbiter accept (FR-013), and seven budgets pinned. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; seven dispatches, more where a verdict asks a correction.
9. **Done, measured.** Seven `budgeted` rows.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - paper budgets.

<!-- plan-archive: archived 2026-10-28 -->
### T04 - the ways family's budgets (D1, D3, D4)

track, web, crossings (three, of D4's census of `STAGES`): each derived, judged SOUND, or accepted by the round arbiter (FR-013), and pinned.

### T04 Approach (checklist part A)

1. **The goal, in the world.** Each ways stage has a budget an independent judge found derived.
2. **The constraints.** FR-001; the rubric; the template; D1, D3.
3. **Where each comes from.** G: the design the GM approved, 2026-10-28 (`request.md`, step 3).
4. **Do they describe the world here?** Each stage's contract, read when its derivation is written from D1's five sources: its docstring, the `plan` fields it reads, the manifest keys and registries it writes (`dev/placement.md`'s `STAGES` table and draw order), its claims (`make claims-report`) and the cohort's checks of what it places (`cohort_audit`'s rules).
5. **The order.** After T01.
6. **The exits.** Green: three verdicts, each SOUND or an arbiter accept (FR-013), and three budgets pinned. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; three dispatches, more where a verdict asks a correction.
9. **Done, measured.** Three `budgeted` rows.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - paper budgets.

<!-- plan-archive: archived 2026-10-28 -->
### T05 - the hinterland and frame family's budgets (D1, D3, D4)

hinterland, woodland, windbreak, bamboo, frame, notice, labels (seven, of D4's census of `STAGES`): each derived, judged SOUND, or accepted by the round arbiter (FR-013), and pinned.

### T05 Approach (checklist part A)

1. **The goal, in the world.** Each hinterland and frame stage has a budget an independent judge found derived.
2. **The constraints.** FR-001; the rubric; the template; D1, D3.
3. **Where each comes from.** G: the design the GM approved, 2026-10-28 (`request.md`, step 3).
4. **Do they describe the world here?** Each stage's contract, read when its derivation is written from D1's five sources: its docstring, the `plan` fields it reads, the manifest keys and registries it writes (`dev/placement.md`'s `STAGES` table and draw order), its claims (`make claims-report`) and the cohort's checks of what it places (`cohort_audit`'s rules).
5. **The order.** After T01.
6. **The exits.** Green: seven verdicts, each SOUND or an arbiter accept (FR-013), and seven budgets pinned. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; seven dispatches, more where a verdict asks a correction.
9. **Done, measured.** Seven `budgeted` rows.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - paper budgets.

<!-- plan-archive: archived 2026-10-28 -->
### T09 - the budgets re-scored to the typical case (FR-014)

The 13 stages pinned on an accept re-scored to rubric S8 - each factor at the mean the reference rolls' output shows, times slack at
most 2, their algorithms and indexes kept - judged once each in MODE BUDGET, and put to the round arbiter as one batch (`make
arbiter-bundle BATCH=1`); a SOUND-pinned stage re-scored and re-judged only where `make budget-set`'s gate fires on its pin - a stage
today's run counts nothing for included, re-scored like any other, its named reason covering only why its re-scored pin stands
above today's zero (for uncounted work, naming that work); each lowered with `LOWER=1`. The 13 are the stages `dev/work-budget.json`
records `pinned_on: accept` (read 2026-10-28).

### T09 Approach (checklist part A)

1. **The goal, in the world.** Every stage's budget is what the stage should do on the rolls it is held to, so the target is lower than today.
2. **The constraints.** FR-014; rubric S8; the round arbiter's ruling ask:444-budget-standard; FR-013 for the accept-pinned.
3. **Where each comes from.** G: the GM, 2026-10-28 ("I thought the idea was to REDUCE the number of operations"), `request.md`'s last section.
4. **Do they describe the world here?** Each stage's mean densities read from the reference rolls' manifests (`phases/items.md`), never the counters or the code.
5. **The order.** After amendment 2; before T06 is put to the GM again.
6. **The exits.** Green: every stage pinned at or under today's count at 40, or with its named reason. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; one MODE BUDGET pass a re-scored stage; one arbiter batch.
9. **Done, measured.** `make budget-set` prints the program per household at or under the design's few thousand, or names why.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - paper budgets.

<!-- plan-archive: archived 2026-10-29 -->
### T10 - today's code's names refused by the budget bundle (FR-015, SC-010)

### T10 Approach (checklist part A)

1. **The goal, in the world.** A derivation cannot carry today's implementation's choices in by name.
2. **The constraints.** FR-015; SC-010.
3. **Where each comes from.** G: the GM, 2026-10-29 ("the ENTIRE point of what we're doing is to do a greenfield implementation"; "sounds good, please proceed with that"), `request.md`'s last section.
4. **Do they describe the world here?** The names defined under `l7r/` (modules, functions, methods, classes, module- and class-level names) read by `ast`; the knobs' names and forms, the stages' names and the pool's manifests' keys passed; the `- pruning:` screen above the reference (FR-016) beside it.
5. **The order.** First of amendment 3; before any greenfield derivation is bundled.
6. **The exits.** Green: the test red with its condition deleted, the tooling landed with `make land-tooling`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One tooling landing.
9. **Done, measured.** `make work-budget-bundle MODE=budget` refuses a derivation naming one, naming each; a test pins it.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - paper budgets.

<!-- plan-archive: archived 2026-10-29 -->
### T11 - the water family greenfield - water_frame, field, sink, waterward, pond_stock, pond_bank (FR-015, FR-016)

### T11 Approach (checklist part A)

1. **The goal, in the world.** Each stage's budget is what a fresh design of it should cost, unencumbered by today's implementation.
2. **The constraints.** FR-015, FR-016, FR-014, FR-013; rubric S1-S9.
3. **Where each comes from.** G: the GM, 2026-10-29 ("the ENTIRE point of what we're doing is to do a greenfield implementation"; "sounds good, please proceed with that"), `request.md`'s last section.
4. **Do they describe the world here?** Each contract from the stage's research pages under `research/questions/` and the knobs' forms, its densities from the reference manifests (`phases/items.md`); no file under `l7r/` read while a derivation is written.
5. **The order.** After T10; the families in `STAGES` order; T06 after all four.
6. **The exits.** Green: each stage's `phases/<stage>.greenfield.md` judged SOUND, or the round arbiter's accept (FR-013), and pinned, a higher one left standing for the GM's words. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; one MODE BUDGET pass a stage a round, the round cap's arbiter rulings.
9. **Done, measured.** `dev/work-budget.json` holds each stage's budget pinned from its greenfield derivation, a higher one left standing and named for the GM's words (`make budget-change`).
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - paper budgets.

<!-- plan-archive: archived 2026-10-29 -->
### T12 - the homesteads family greenfield - seat, homesteads, appurtenances, burial, lane_wells, sties, washing (FR-015, FR-016)

### T12 Approach (checklist part A)

1. **The goal, in the world.** Each stage's budget is what a fresh design of it should cost, unencumbered by today's implementation.
2. **The constraints.** FR-015, FR-016, FR-014, FR-013; rubric S1-S9.
3. **Where each comes from.** G: the GM, 2026-10-29 ("the ENTIRE point of what we're doing is to do a greenfield implementation"; "sounds good, please proceed with that"), `request.md`'s last section.
4. **Do they describe the world here?** Each contract from the stage's research pages under `research/questions/` and the knobs' forms, its densities from the reference manifests (`phases/items.md`); no file under `l7r/` read while a derivation is written.
5. **The order.** After T10; the families in `STAGES` order; T06 after all four.
6. **The exits.** Green: each stage's `phases/<stage>.greenfield.md` judged SOUND, or the round arbiter's accept (FR-013), and pinned, a higher one left standing for the GM's words. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; one MODE BUDGET pass a stage a round, the round cap's arbiter rulings.
9. **Done, measured.** `dev/work-budget.json` holds each stage's budget pinned from its greenfield derivation, a higher one left standing and named for the GM's words (`make budget-change`).
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - paper budgets.

<!-- plan-archive: archived 2026-10-29 -->
### T13 - the ways family greenfield - track, web, crossings (FR-015, FR-016)

### T13 Approach (checklist part A)

1. **The goal, in the world.** Each stage's budget is what a fresh design of it should cost, unencumbered by today's implementation.
2. **The constraints.** FR-015, FR-016, FR-014, FR-013; rubric S1-S9.
3. **Where each comes from.** G: the GM, 2026-10-29 ("the ENTIRE point of what we're doing is to do a greenfield implementation"; "sounds good, please proceed with that"), `request.md`'s last section.
4. **Do they describe the world here?** Each contract from the stage's research pages under `research/questions/` and the knobs' forms, its densities from the reference manifests (`phases/items.md`); no file under `l7r/` read while a derivation is written.
5. **The order.** After T10; the families in `STAGES` order; T06 after all four.
6. **The exits.** Green: each stage's `phases/<stage>.greenfield.md` judged SOUND, or the round arbiter's accept (FR-013), and pinned, a higher one left standing for the GM's words. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; one MODE BUDGET pass a stage a round, the round cap's arbiter rulings.
9. **Done, measured.** `dev/work-budget.json` holds each stage's budget pinned from its greenfield derivation, a higher one left standing and named for the GM's words (`make budget-change`).
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - paper budgets.

<!-- plan-archive: archived 2026-10-29 -->
### T14 - the hinterland and frame family greenfield - hinterland, woodland, windbreak, bamboo, frame, notice, labels (FR-015, FR-016)

### T14 Approach (checklist part A)

1. **The goal, in the world.** Each stage's budget is what a fresh design of it should cost, unencumbered by today's implementation.
2. **The constraints.** FR-015, FR-016, FR-014, FR-013; rubric S1-S9.
3. **Where each comes from.** G: the GM, 2026-10-29 ("the ENTIRE point of what we're doing is to do a greenfield implementation"; "sounds good, please proceed with that"), `request.md`'s last section.
4. **Do they describe the world here?** Each contract from the stage's research pages under `research/questions/` and the knobs' forms, its densities from the reference manifests (`phases/items.md`); no file under `l7r/` read while a derivation is written.
5. **The order.** After T10; the families in `STAGES` order; T06 after all four.
6. **The exits.** Green: each stage's `phases/<stage>.greenfield.md` judged SOUND, or the round arbiter's accept (FR-013), and pinned, a higher one left standing for the GM's words. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; one MODE BUDGET pass a stage a round, the round cap's arbiter rulings.
9. **Done, measured.** `dev/work-budget.json` holds each stage's budget pinned from its greenfield derivation, a higher one left standing and named for the GM's words (`make budget-change`).
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - paper budgets.

<!-- plan-archive: archived 2026-10-29 -->
### T06 - the program's target to the GM (D5)

The sum at 40 households and the whole roll's exponent, beside today's figures, through `escalation-check` to the GM; his words
set it with `make budget-program`.

### T06 Approach (checklist part A)

1. **The goal, in the world.** The GM approves, in his own words, what the whole roll should cost before any phase is rebuilt.
2. **The constraints.** FR-002; D5.
3. **Where each comes from.** G: the design the GM approved, 2026-10-28 (`request.md`, step 3: "The GM approves the target").
4. **Do they describe the world here?** The budgets T02-T05 pin, one per stage of `STAGES`, and today's record, read after them.
5. **The order.** After T02-T05; before any phase task is filed.
6. **The exits.** Green: the GM's words recorded by `make budget-program`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; one escalation-check.
9. **Done, measured.** `dev/work-budget.json`'s program row set, its words in `dev/work-budget-changes.jsonl`.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - the target, on paper.

<!-- plan-archive: archived 2026-10-29 -->
### T15 - phase: water_frame, through the checklist (FR-003, FR-004, FR-005; step 4)

Occasions: none - the plan's rolls and the meta it writes are unchanged, so no map moves; no glyph, form or placement rule.

### T15 Approach (checklist part A)

1. **The goal, in the world.** The water frame rebuilt to its greenfield derivation - the plan's rolls counted where they happen, in the first stage, so the roll's count holds the work the plan does, and whatever of the old stage the derivation does not carry deleted.
2. **The constraints.** FR-003, FR-004, FR-005; rubric S5; the greenfield derivation `phases/water_frame_greenfield.derivation.md` and its budget, 69, set with the GM's words.
3. **Where each comes from.** G: the GM, 2026-10-29 ("yes please do step 4 and then we can stop and assess how things are going"); the design's step 4 (`request.md`, section 6).
4. **Do they describe the world here?** The plan's rolls (`plan_site`), today outside any stage's counted window; the stage's meta writes.
5. **The order.** First of step 4; before `field`.
6. **The exits.** Green: the stage counts its rolls at most its budget at 40 and 80, the cohort unmoved, `phases/water_frame.md`'s eight boxes ticked. Red, over its budget: rebuilt again, or the budget raised with the GM's words (`make budget-change`, FR-006) - never set down, never an arbiter's accept; a stop to assess goes to the GM, as he asked ("then we can stop and assess how things are going").
7. **The search smell.** none
8. **The budget.** One landing; one MODE AUDIT pass.
9. **Done, measured.** `make work-budget`: water_frame's counted operations at 40 and 80 against 69, its exponent 0.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a


<!-- plan-archive: archived 2026-10-30 -->
### T17 - FR-011's Rust tooling proven on a Rust fixture (amendment 4; before the first Rust phase lands)

Occasions: none (tooling: no map moves).

### T17 Approach (checklist part A)

(The round arbiter, 2026-10-30, ask:444-T17-rows-need-a-phase, Route A, narrowed by the plan review of 2026-10-30: T17 ticks with every row the fixture can fire; `cache audit` and `the overlap census`, which need a phase's maps or counters, are T19's, and the refusal of a Rust phase while any row is unproven lands with T17.)

1. **The goal, in the world.** A Rust fixture crate - one PyO3 extension module built by maturin, a thin Python function calling it,
   a `///` doc comment carrying a `Research:` claim and a `Steps:` list - against which every row of `dev/rust-tooling.md` marked one
   for one, partial, rewritten or replaced is shown to FIRE: each check refuses a fixture written to break it, and passes the fixture
   written to keep it.
2. **The constraints.** FR-010 (the module's shape), FR-011 and FR-017 (proven before the first Rust phase); `dev/rust-tooling.md`'s
   rows and keys; the toolchain pinned in `scripts/container/setup-dev-env.sh` (its pinned versions: clippy, rustfmt, llvm-tools,
   cargo-llvm-cov, maturin).
3. **Where each comes from.** G: the GM, 2026-10-29 ("I want to modify the plan so that we don't end up doing any Python rewrites")
   and 2026-10-30 ("please complete those tooling fixes that are the prerequisites"); the design's section 7.
4. **Do they describe the world here?** The fixture is a stand-in, not a phase: it lives under `tests/fixtures/rust/` and is never
   imported by the engine.
5. **The order.** First of the Rust work: before the `water_frame` port and the field rebuild.
6. **The exits.** Green: every proven row's check named with the fixture case that fires it (a table beside `dev/rust-tooling.md`'s),
   `make hooks-test` and `make done` green. A row that cannot be proven goes to the round arbiter with what blocked it. Red: a row whose check cannot be made to fire on the fixture goes to the round arbiter (`make arbiter-ask`) with what blocked it.
7. **The search smell.** none
8. **The budget.** Rows land in groups as they are proven (the lint and format group; the caps; coverage; the code id and the
   claims reader; the guards); one landing a group.
9. **Done, measured.** Every row of `dev/rust-tooling.md` marked one for one, partial, rewritten or replaced (step 1's four kinds) marked
   proven in its "Proven on the fixture" table with its firing case, but `cache audit` and `the overlap census`, which the arbiter's
   ruling gives T19 (they fire only on a phase's maps or counters).
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no


<!-- plan-archive: archived 2026-10-31 -->
### T19 - phase: water_frame, its Rust port (FR-017; after the tooling proof)

Occasions: settlement-review on each pool hamlet the port moves - none, measured 2026-10-31 (`make map` on each: D7 reproduces today's draws, so every layout and render is main's).

### T19 Approach (2026-10-31T04:00:49Z)

(The round arbiter, 2026-10-30, ask:444-T17-rows-need-a-phase, Route A, narrowed by the plan review of 2026-10-30: T19 also proves the two tooling rows the fixture cannot fire - `cache audit` (it audits maps, and the fixture draws none) and `the overlap census` (its replacement, the counters inside Rust, designed with this port) - before its tick; `check-rust-tooling.py` refuses the port's landing until they are.)

1. **The goal, in the world.** `water_frame` in the extension module, written from `phases/water_frame_greenfield.derivation.md`
   (its derivation came out the same as today's code: rolls and writes, no search), the stage a thin Python function calling it.
2. **The constraints.** FR-010, FR-017; the derivation's Contract and its pinned budget (`dev/work-budget.json`); the phase-source guard holds its
   old code while this task runs.
3. **Where each comes from.** G: the GM, 2026-10-29 (FR-017: water_frame's Rust port a task of its own, landed before the feature
   closes).
4. **Do they describe the world here?** One stage, one derivation; the manifest keys it writes are today's.
5. **The order.** After the tooling proof; before the field rebuild, so the first Rust landing is the smallest.
6. **The exits.** Green: counted operations within the pinned budget (`dev/work-budget.json`) at every size `make work-budget` rolls, MODE AUDIT
   WITHIN on the `.rs` modules, `cache audit` and `the overlap census` proven on the port (each check refusing a copy of the port
   written to break it, named in `dev/rust-tooling.md`'s "Proven" table - not merely run green), `make cohort-landing` with no regressed seed (as the GM wrote it: D7 reproduces today's draws, so a pinned seed names the same map), the Rust coverage floor whole. Red: a count over its budget, or MODE AUDIT not WITHIN, goes to the round arbiter (`make arbiter-ask`) with the measurement -
   a route, never an acceptance: a phase over its budget is rebuilt or its budget changed with the GM's words (FR-006).
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** `make work-budget`: water_frame's count at every size against its pinned budget; `cache audit` and `the overlap census` in the "Proven" table with their firing cases; `make perf-ab` beside it, recorded.
10. **Before moving a constant.** The research page each rolled knob cites (0054), read before it moves.
11. **Before fitting things into room.** n/a

**Performance work?** yes - docs/performance-checklist.md's questions follow.

### T19 part B (2026-10-31T02:51Z)

The trigger: `make cohort-landing` under the port (`phases/water_frame.cohort-landing-1.txt`, dev/cohort-log/20261031T025046Z): 47 of
54 pass the whole gate, against main's 54 of 54 on the same seeds; seeds 3, 20, 21, 36, 37, 903 and 904 newly failing.

1. **What exactly is refusing?** Not water_frame: its own checks hold (56 counted, MODE AUDIT WITHIN, FR-004, FR-012). Later stages
   refuse, each with a kind main's cohort knows - seed 3 and 36 `SiteRefused` (the seating), 20 and 21 `lane_knots 1`, 904
   `lane_knots 2`, 37 `OverlapRefused`, 903 `WebRefused`. Seeds 3 and 903 are named by an open found row,
   `l7r/diagram/hamletgen/ways/web.py::stage_web` (E3, a footpath to every farmhouse 7 ft off a plot - 0246's fence gap, CONVENTION): that row is read before any
   probe. The geometry of each refusal is NOT yet dumped - item 7.
2. **A3 again.** The rules refusing are the later stages' own (R: research-backed), unchanged by the port.
3. **A4 again.** Not yet looked at on the map, seed by seed - item 7.
4. **Moving something placed earlier to suit something later?** Not proposed: no fix is drafted.
5. **Tuning or changing?** Neither yet.
6. **The one-sentence test.** "The port re-rolls every plan; seven seeds now refuse in later stages" - the GM would ask whether the
   later stages fail on new rolls generally. Measured: main's own fresh-seed cohort (dev/cohort-log/20261030T233704Z, seeds from
   355289, commit 81a8dbc39) passes 46 of 54, on the same refusal kinds. Recorded as a number beside the diagnosis owed, not as an
   explanation (constitution XIII: a rotated residue is no defense).
7. **The next step is a measurement:** each of the seven seeds rolled on the port and dumped where it refuses (the lanes and what
   stands near them, the seat band for the two SiteRefused), the open found row read for 3 and 903; then each named as a defect of a
   later stage, with its fix, before any route is put to the round arbiter.

   **Item 7, begun (2026-10-31T03Z).** The open found row for seeds 3 and 903 (`specs/328-match-the-research/claims-followup.md`,
   E3, DRIFTED) is a known defect of the web: footpaths held 7 ft off a garden fence (0246's fence gap, CONVENTION) leave farmhouses off the network -
   "WebRefused at (3024, 3004) and (3265, 2589)" on Kashikawa, "re-route or re-seat so the gap holds". Seed 903's `WebRefused` is that
   row's kind; seed 3 refuses earlier, in the seating (`SiteRefused`), so the row does not explain it alone. The five others are
   not yet dumped.

   **Item 7, each seed rolled alone on the port (`make cohort N=1 SEED=<s> FRESH=0`, 2026-10-31T03Z):** seed 3 and 36 `SiteRefused`
   - "seated 19 of 20 households on margin 1", one house short of the band; 20, 21 and 904 `lane_knots` - 1, 1 and 2 knots, two
   lanes within the 25 ft join reach (`LANE_JOIN_FT`, a knob) left unjoined (15.2, 18.9 and 20.6 ft, measured 2026-10-31 (`make cohort N=1 SEED=<s> FRESH=0`, the knot verdicts)); 37 `OverlapRefused` - "lanes would be recorded on a
   gardens at (1545, 2814)"; 903 `WebRefused` - "lanes 1, 2 (skeleton: dangling_ends) still break a rule of the lane law", the E3
   row's kind. All seven refuse in the seating, the lane knots or the web - none in water_frame - each a class main's own fresh-seed
   cohort fails on (46 of 54). The lanes and the seat band at each place are not yet dumped.

### T19 part B (2026-10-31T03:05Z)

The trigger: the round arbiter's fair comparison (ruling on ask:444-T19-cohort-regression), the port rolled on main's own fresh block
(`make cohort N=48 SEED=355289 FRESH=0`, dev/cohort-log/20261031T030442Z): 44 of 54 pass against main's 46 of 54 at 81a8dbc39
(dev/cohort-log/20261030T233704Z); 7 of main's failures pass, 9 seeds newly fail (355298, 355302, 355305, 355306, 355327, 355329,
355334, 903, 904), and seed 355306 refuses `SiteRefused`, a class main's block never shows - the ruling's branch 3, a fault in the
port's rolls.

1. **What exactly is refusing?** Later stages, as before - `lane_knots` 4, `WebRefused` 4, `row_rules` 1, `SiteRefused` 1 (355306, a
   linear map of 19 households). The forms rolled match main's (nucleated 28 / linear 15 / dispersed 11 against 27 / 13 / 14), so the
   settlement form's odds are not the fault; every dispersed map passes on both.
2. **A3 again.** The refusing rules are the later stages' own, unchanged by the port.
3. **A4 again.** Read in the port's caller and the later stages' readers: the port rolls a knob only on its derivation branch, else
   writes its table's first form. A branch is right only where no stage reads the knob off it. (The old `plan_site` was also read at
   81a8dbc39 under the phase-source escape during this diagnosis, against the guard's purpose - the GM's 2026-10-30 rule that the
   rewrite not copy the old algorithms; spec-fidelity's MODE 4 review of T19 found it NOT LEGITIMATE. Both fixes rest on the readers'
   trace below alone, which finds them without it.)
4. **Moving something placed earlier to suit something later?** No: the fix is in water_frame's own rolls.
5. **Tuning or changing?** Changing: a wrong branch, not a value.
6. **The one-sentence test.** "Every row and farm hamlet was seated in the stubbiest band, because the port held the cluster's shape
   at round outside a cluster" - a defect the GM would recognize as one.
7. **Found:** `cluster_shape` was on the nucleated branch, but `seat_cluster` (`ways/track.py`, every form) and `seat_room` size
   every map's margin band and canvas through `band_extent(households, cluster_shape)`; on the port every linear and dispersed map
   took "round" (aspect 2.2, against elongated's 5.0). The grove knobs are read only by the row seating (`homesteads/rows.py`), the
   row and farm-water knobs only behind their form, `well_siting` only by the nucleated wells: those branches stand. Fixed
   (`_KNOBS`: `cluster_shape` on `all`), with `test_the_cluster_shape_rolls_on_every_form_since_every_band_is_sized_by_it`
   red on the unfixed branch (`('linear', {'round'})`); the derivation's per-form note corrected (linear 57; the reference's 56
   unchanged). Next: the same block re-rolled on the fix, and the ruling's branch read again.

### T19 Decisions

**D6 - The boundary: Python gathers, Rust rolls, Python writes** (FR-010, FR-004): `stage_water_frame` stays a thin Python function
in `STAGES`. It gathers the derivation's Reads into one record - the map's seed, the spec's name, households and scale, and for
each of the 20 knobs the forms its own table allows for the settlement form and the spec's pin if any - and calls
`l7r_phases.water_frame(record)`. Rust rolls the three bearings (the drainage bearing drawn within 90 degrees of the fall, so the
bound holds by construction) and each knob's form, and returns them with its counted operations. Python writes them where the
manifest keys are today (FR-004: the keys unchanged). The knob tables stay Python data: they are the research's tables, and one
copy of each is the rule.

**D7 - The rolls: `knob_rng`'s own draws, reproduced in Rust** (FR-017; amended 2026-10-31 on spec-fidelity's second MODE 4 review,
which found the first D7's premise - that today's draws could not be reproduced without reading the guarded plan code - unmeasured):
`settlement/_knobs.py`'s `knob_rng(seed, knob)` is the shared generator every stage calls, not the ported code, and public algorithm
end to end - SHA-256 of `"{seed}\0{knob}"`, its first 8 bytes seeding Python's `random.Random` (MT19937, `init_by_array`), drawn by
`randrange` (CPython's `_randbelow_with_getrandbits`). `rust/phases/src/pyrand.rs` reproduces it with no crate dependency, so the
port rolls the plan Python rolled and every seed keeps its map: the GM's landing rule, "`make cohort-landing` shows no regressed
seed", holds as written. Proven by `test_the_rust_draws_are_knob_rng_s` (the knobs and the fall on 32 seeds, one past 2^32) and
measured 2026-10-31 (`make map` on each pool hamlet): every layout and render is main's. What still differs is the meta of a knob
off its derivation branch - written as its table's first form, where Python rolled a value no stage reads - which the title card
hides behind each choice's own form (`interactive/choices.py` `applies`). The first D7 (a seeded SplitMix64, every plan rolled
anew) was replaced because it broke the literal rule; do not restore it.

**D8 - The build: maturin into a repository-local folder, keyed to the Rust sources** (FR-010): `rust/phases/` is the crate
(`l7r_phases`); `make rust-build` builds it with maturin into `.rust-ext/` (gitignored) when its sources' code id moved, and every
target that rolls a map or runs the tests depends on it; `l7r/diagram/hamletgen` puts `.rust-ext/` on the import path. The
generation key already holds the Rust sources (T17, `gencache.rust_sources`), so a Rust change re-keys every map.

**D9 - The counts: Rust counts as Python does, and hands them back** (FR-003, FR-012; `dev/rust-tooling.md` "the overlap
census"): behind the crate's Cargo feature `counters` (FR-012: compiled out of the deployed build), the crate keeps an operation counter keyed `<kind>@<function>` as the Python counters are, returns it with the stage's result, and the
thin function adds it to the roll's counts, so `make work-budget` and MODE AUDIT read a Rust stage as they read a Python one -
the replacement for the overlap census, proven on this port by a copy that does work it does not count.

### T19 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** <the stage and the loop: `make perf-profile` time beside `make phase-calls` / `make perf-fanout` calls>
2. **Removes work, or only moves it?** <fewer candidates, a screen, a kept result, an index, an early stop, a better algorithm,
   a loop into C - or an inlining, a merge, a builtin written out: never the goal, only where the time evidence shows a gain>
3. **What do you expect it to save, and why?** <a share of the stage's profiled time>
4. **How does the work grow with the settlement?** <the growth exponent between sizes, and whether this bends it>
5. **What did the before and after show, and under what conditions?** <calls; `make perf-ab` best of N with each arm's spread,
   the host's load - evidence, not a pass>
6. **Did any map move, and does it still keep the research?** <`make maps-moved`, the cohort>


### T19 part B (2026-10-31T03:10Z)

The trigger: the same block re-rolled on the `cluster_shape` fix (dev/cohort-log/20261031T031013Z): 45 of 54 against main's 46; the
SiteRefused gone, every refusal a class main's block shows (`lane_knots` 4, `WebRefused` 4, `row_rules` 1); 8 seeds still newly
failing (355298, 355302, 355305, 355327, 355329, 355334, 903, 904), 7 of main's failures passing.

1. **What exactly is refusing?** The later stages' rules only, each a kind main's block shows; still one seat under the ruling's 46.
2. **A3 again.** Unchanged rules.
3. **A4 again.** The audit of 03:05Z item 7 carried to every off-branch knob: `well_siting` is the second of the same fault -
   `place_wells` (`homesteads/stages.py`, every form) seats the communal wells of every house without a grove, and both its first
   seating and the reach loop (`wells.py`) read `plan.well_siting` on every form, and the port held it at
   "lane" outside a cluster. The rest hold: the row knobs are read in `rows.py` and behind the linear form in `wells.py`, `farm_water`
   behind the dispersed form, the grove knobs by the row seating alone.
4. **Moving something placed earlier to suit something later?** No: water_frame's own branch.
5. **Tuning or changing?** Changing a wrong branch.
6. **The one-sentence test.** "The row and farm hamlets' shared wells were always sited by the lane, because the port held the
   siting at its first form outside a cluster."
7. **Fixed** (`_KNOBS`: `well_siting` on `all`), the test widened to
   `test_the_knobs_every_form_reads_roll_on_every_form`, red on the unfixed branch (`AssertionError: linear`); the derivation's
   per-form note now linear 59 (the reference's 56 unchanged). Next: the block re-rolled on both fixes and the ruling's branch read
   from that run.

### T19 part B (2026-10-31T03:14Z)

The trigger: the block re-rolled on both branch fixes (dev/cohort-log/20261031T031422Z): 45 of 54 again, against main's 46; the
same eight seeds newly failing, the same seven of main's passing; every refusal a class main's block shows (`lane_knots` 4,
`WebRefused` 4, `row_rules` 1); the cohort's own census: "knob values never rolled: none", "knob values rolled but never drawn: none".

1. **What exactly is refusing?** The later stages, on kinds main's block shows: four knot passes, four webs (903 named by the open
   found row E3), one row rule.
2. **A3 again.** Unchanged rules.
3. **A4 again.** Every knob the port writes alone off its branch has now been traced to its readers (03:05Z and 03:10Z items 7);
   none remains read off its branch, and the census finds every value rolled and drawn. The settlement forms' odds match main's
   block (nucleated 28 / linear 15 / dispersed 11 against 27 / 13 / 14); the falls are tested equal to `fall_backs_the_wind` on
   every quarter.
4. **Moving something placed earlier to suit something later?** No fix is proposed.
5. **Tuning or changing?** Neither.
6. **The one-sentence test.** "On main's own block the re-rolled port passes 45 where main passed 46, on the same kinds of failure,
   eight seeds failing and seven healed" - the GM would ask whether one seat of 54 is the port or the dice.
7. **The next step:** a PROCESS question, to the round arbiter (`ask:444-T19-cohort-45`): whether a one-seat shortfall with no new
   class, after the port's rolls are audited knob by knob, is branch 3's fault still to find or within the block's own spread.

### T19 part B (2026-10-31T03:22Z)

The trigger: `make cohort-landing` on both branch fixes (dev/cohort-log/20261031T032224Z): 47 of 54, seeds 20, 21, 36, 37, 48, 903
and 904 newly failing against main's 54 of 54 on these pinned seeds - the comparison the round arbiter ruled unfair for a port that
re-rolls (ask:444-T19-cohort-regression), and accepted on the fair one (ask:444-T19-cohort-45: fresh 41/48 against main's 40/48).

1. **What exactly is refusing?** `lane_knots` (20, 21, 904), `OverlapRefused` (37 on a garden, 48 on a threshing yard), `SiteRefused`
   (36, 19 of 20 on margin 1), `WebRefused` (903, dangling ends); seed 3, failing before the `cluster_shape` fix, passes.
2. **A3 again.** The later stages' own rules, unchanged.
3. **A4 again.** Read: each refusal a stage's known kind; 903 the E3 web row's.
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Neither: the ruling's branch 2 - land, the seeds filed.
6. **The one-sentence test.** "The re-rolled port's landing seeds fail in later stages the fresh block also shows; each is filed as
   an open row against its stage."
7. **Done:** the seven seeds and the Kashikawa and Sawada pins filed as open rows
   (`specs/328-match-the-research/audit/found-444-t19.jsonl`, the SiteRefused row naming widening `SEATING_GROUND_FT` first). (Struck 2026-10-31: the Mizuguchi review this sentence owed is not owed - D7 reproduces today's draws and no pool map moves; the Occasions line.)

   **On spec-fidelity's MODE 4 review of T19 (2026-10-31, BLOCKED, 7 decisions):** (5) the landing reads FR-005 by User Story 2's
   own words, Approach item 6 and D7 amended above. The Kashikawa and Sawada pins: both are pool hamlets whose re-rolled plans
   refused on the port (SiteRefused on Kashikawa, SinkRefused on Sawada); their `.gen.py` now pin their shipped plans, so as shipped
   they do not newly fail - each regenerates unchanged against HEAD (observed 2026-10-31, method: `make map`, "this map's manifest
   is unchanged against HEAD") - and their open rows are to unpin them, not a failing map. (6) the old-code read is recorded at
   03:05Z item 3; both fixes rest on the readers' trace. (7) water_frame's pin is SOUND-pinned (`dev/work-budget.json`: its verdict
   `phases/water_frame_greenfield.verdict-2.txt`), and FR-013's re-owed ruling binds "an accept-pinned budget" alone; the edit
   changed no budgeted figure - the totals at 20, 40 and 80 stay 56 - only the per-form note beside the knobs row (linear 55, then
   59), so no ruling is re-owed and the pin stands.

   **On spec-fidelity's second MODE 4 review (2026-10-31, BLOCKED, 9 decisions):** (1) the cohort exit - the first D7's premise
   that today's draws could not be reproduced was unmeasured; measured, it was false: D7 amended to reproduce `knob_rng`, Approach
   item 6 back to the GM's words, and `make cohort-landing` on it passes 54 of 54, no regressed seed
   (dev/cohort-log/20261031T034931Z). (2) the Kashikawa and Sawada pins - removed; both regenerate as main's maps. The open rows
   filed at 03:22Z for the re-rolled port's seeds and pins (`found-444-t19.jsonl`) are withdrawn: no seed fails and no map is pinned.

### T19 part B (2026-10-31T04:09Z)

The trigger: every cohort this task rolled that refused a seed (dev/cohort-log/20261031T025046Z, 030442Z, 031013Z, 031422Z and
032224Z), each answered at its own part B above in items 1-7; this block answers items 8 and 9 for all of them, and the outcome.

1. **What exactly is refusing?** Nothing now: `make cohort-landing` on the reproduced draws passes 54 of 54
   (dev/cohort-log/20261031T034931Z).
2. **A3 again.** The rules are unchanged.
3. **A4 again.** Read at each block above; the last read found no knob read off its branch.
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Changing: two branches (`cluster_shape`, `well_siting`) and D7's draws.
6. **The one-sentence test.** "The port now draws Python's own rolls, so every seed keeps its map."
7. **Done:** D7 amended; the open rows withdrawn; the pins removed.
8. **Every route measured before the arbiter was asked?** At ask:444-T19-cohort-regression and ask:444-T19-cohort-45 the routes
   put were measured on the cohort and against the found rows (`cohort_known` named seed 903's E3 row), but not every route: the
   route that settled it - reproducing `knob_rng` so no seed re-rolls - was not measured or offered until spec-fidelity's second
   MODE 4 review called D7's premise unmeasured. The research did not decide it; a measurement did (the draws compared with
   `knob_rng` in `test_the_rust_draws_are_knob_rng_s`). Recorded so a later port measures the reproduction route first.
9. **After a ruling, the step it named?** Yes for each: the cohort-regression ruling's step (the fair comparison) was taken
   first and its branch 3 (a fault in the rolls) followed, which found the two branch faults; the cohort-45 ruling's accept was
   acted on until spec-fidelity's review blocked the landing it named, and the route taken then (D7 reproduced) went back
   through that review (CLEAR) rather than past it.
<!-- plan-archive: archived 2026-10-31 -->
### T20 - the tooling gaps T19's landing found (the GM 2026-10-31: "Please fix the tooling gaps by implementing T20.")

- **Approach**: four fixes to the landing's tooling, each measured on T19's own landing (2026-10-31, `dev/review-ledger.md` and
  the landing logs): the push refused twice for a work-budget run `make land` could have made (T17, T19); four landing rounds each
  showed one tick refusal of several; a plan review was spent on a section the tick then refused for its Approach's stamp; and a
  re-dated heading with an unchanged body owed a review of its "removal".

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| D1 land's budget run | its test, red without it | n/a (tooling) | none | n/a |
| D2 every tick refusal | its test, red without it | n/a | none | n/a |
| D3 decide's Approach check | its test, red without it | n/a | none | n/a |
| D4 a re-dated heading | its test, red without it | n/a | none | n/a |

<!-- plan-archive: archived 2026-10-31 -->
### T20 Approach (2026-10-31T11:08:39Z)

1. **The goal, in the world.** A landing that refuses says everything it will refuse at once, and does for itself what it can:
   no gate or review spent on a refusal the tooling could have answered first.
2. **The constraints.** FR-005 and FR-006 untouched (the budget review still refuses an accepted stage over its figure; only a
   MISSING run is made); the plan gate's FR-043 (a changed decision is reviewed) and feature 385's checklist rules unchanged in
   what they require - only when and how together they say it.
3. **Where each comes from.** G: the GM's words above. O: T19's landing, 2026-10-31 (the refusals in its land logs).
4. **Do they describe the world here?** Each fix is pinned by a test of the situation T19 met.
5. **The order.** D1-D4 independent; landed together.
6. **The exits.** Green: each test red without its fix and green with it, `make done` and `make hooks-test` green, landed by
   `make land F=444 T=T20`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through
   `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The four tests, and the landing itself.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

**Performance work?** no.

### T20 Decisions

- **D1 - `make land` makes a missing work-budget run itself** (`scripts/land.py`, after the landing cohort): where the delta
  carries engine code and `make work-budget-review ROUTE=GATED` refuses for "no work-budget run at the pushed engine" alone, land
  runs `make work-budget` and commits `dev/work-budget.md` and `dev/work-budget/` before the push. Any other refusal of the review
  (an accepted stage over its figure) still stops the landing, unchanged: only the GM's words raise a figure.
- **D2 - the tick reports every refusal together** (`scripts/tick-task.py`): the checks that were an `or`-chain - the plan gate,
  the boxes, the waits, the arbiter's hold, the checkpoint, the approach checklist, the wording - are each asked and every
  refusal is listed, numbered, in one message; a tick still refuses if any one refuses.
- **D3 - `make decide` asks the approach checklist first** (`scripts/gates/plan_gate.py` `decide_prompt`): where
  `approach_gate.refusal` names the task, decide refuses with that refusal before printing the review it owes, so a section is
  never reviewed only to be refused at the tick for its checklist and edited (and reviewed) again.
- **D4 - a re-dated heading is the same block** (`scripts/gates/plan_sections.py` `block_status`): a recorded block plan.md no
  longer has is not owed as `(removed)` where a live block has the same heading once a closing parenthetical (a stamp, "checklist
  part A") is dropped and the same text below its heading line. A changed body is owed as before.

<!-- plan-archive: archived 2026-10-31 -->
### T18 - the field re-derived under the single-field cap (FR-018), its MODE BUDGET verdict

Occasions: none (a derivation and its verdict; no map moves until the field rebuild).

### T18 Approach (2026-10-31T16:27Z)

1. **The goal, in the world.** The largest single paddy field the research finds for a settlement of this kind, as the field
   phase's contract (its cap and source), and `phases/field_greenfield.derivation.md` re-derived under it: a settlement whose
   farmland passes the cap draws more than one field.
2. **The constraints.** FR-018, FR-015, FR-016 (rubric S9); the research pass searches the record and the archive first
   (`make research-search`, feature 447); the findings of feature 447's field-size runs (`specs/447-semantic-index/research/t02-*`,
   `t04-validation.md`, `t06-validation-3.md`) as leads, each source written up and checked as the record's rules require.
3. **Where each comes from.** G: the GM, 2026-10-29 ("we can cap out at something approximating whatever that size is, and then
   larger settlements just have multiple fields").
4. **Do they describe the world here?** The cap is for the settlement kind the field draws: a hamlet's or village's comb field.
5. **The order.** Before the field rebuild; after or beside the tooling proof (no engine code).
6. **The exits.** Green: the cap and its source in the record, the derivation's MODE BUDGET SOUND; a figure above the standing pin
   (`dev/work-budget.json`) keeps that pin and is pinned only with the GM's words (`make budget-change`). Red: a derivation judged LOOSE or UNDERIVED twice, or a cap the research cannot settle, goes to the round arbiter (`make arbiter-ask`) with the verdicts.
7. **The search smell.** none
8. **The budget.** The research page through `make page-session`; one MODE BUDGET round a draft.
9. **Done, measured.** The verdict's figure at 40 and its exponent, beside the standing pin.
10. **Before moving a constant.** The research page the cap cites, read before it moves.
11. **Before fitting things into room.** n/a

**Performance work?** no

### T18 Decisions

- **D1 - the cap is the record's knob** (`research/questions/0017-...drawing.html#how-our-maps-size-a-settlements-farmland`, written
  by T18's page sessions): one field at most a cap rolled per settlement between about 45 and 60 ha (accurate at its top: Fei's
  largest polder; a knob within the attested band, the record's label); a settlement past it draws several fields. The two
  questions session C's handoff left "for the GM" - whether Yang's undivided 1,000-mu pond (about 61 ha) is one tract, and the
  1991 gazetteer's unstated mu - are whether a finding applies to a case, the record's to rule and never the GM's (the root
  CLAUDE.md, Research): the knob's band holds either reading, so neither moves the cap.
- **D2 - the derivation's figures stand** (`phases/field_greenfield.derivation.md`, its Bounds): at 20, 40 and 80 households the
  farmland - 1.3 acres a household, 0017's `GROSS_ACRES_PER_HOUSEHOLD` - is about 11, 21 and 42 ha, under the cap's 45 ha floor (0017's knob), so each draws one field and no total changes; the cap binds only
  past about 85 households, where each field's work is the derivation's at its own size. Owed: the MODE BUDGET verdict on the
  re-derived text (FR-018), and the pin kept as it stands unless that verdict moves a figure.


<!-- plan-archive: T19 to T19 moved to plan-done.md, 2026-10-31 (feature 375 FR-044) -->

<!-- plan-archive: T20 to T20 moved to plan-done.md, 2026-10-31 (feature 375 FR-044) -->
<!-- plan-archive: T20 to T20 moved to plan-done.md, 2026-10-31 (feature 375 FR-044) -->

