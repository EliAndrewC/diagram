# Feature Specification: the work-budget program - every phase rebuilt to an algorithmic budget

**Feature Branch**: `444-work-budget-program` (no branch; work on `main` in the clone)

**Created**: 2026-10-28

**Status**: Draft - starts once feature 443's tooling has landed

**Affects**: hamlet, performance, tooling

**Approved**: the GM, 2026-10-28, "Thank you. I approve the design. Please proceed."

**Input**: `request.md` (the GM's words, verbatim, and the design he approved: its steps 3 to 6 are this feature; feature 443
is the instrument and the check).

## Why

The past speed work judged each slice by the time it saved and set it down when that was small (`request.md`, "Why the past
attempts lost sight"). This program judges each phase of the hamlet roll against a budget derived from first principles, and
closes only when the whole roll meets the program's budget. The GM's goal: "not just faster, but that we are performing an
algorithmically sensible number of computations as validated by some kind of adversarial subagent check based on some real
standards" (`request.md`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The whole-program budget first (Priority: P1)

1. **Given** every stage of `STAGES` (`l7r/diagram/hamletgen/driver.py`), **Then** each has a written derivation (its contract,
   its minimal algorithm in pseudocode and its operation count, factor by factor, per the rubric's S7), a MODE BUDGET verdict
   of SOUND from the `work-budget` agent or the round arbiter's accept of its derivation (FR-013), and a budget in `dev/work-budget.json`; their sum is the program's target, which the
   GM approves before the first rebuild.

### User Story 2 - Each phase rebuilt to its budget, through the checklist (Priority: P1)

1. **Given** a phase, **When** it is rebuilt, **Then** its checklist (`.specify/templates/phase-checklist.md`, copied to
   `phases/<stage>.md`) is ticked in order: contract, minimal algorithm, budget reviewed, today's measurement, the rebuild
   behind the manifest seam with the old code deleted, acceptance, the MODE AUDIT review, the standing record.
2. **Given** acceptance, **Then** the phase's counted operations are at most its budget at 40 and 80 households and its
   exponent at most the budget's; every seed of the Rust stage gate passes where each Rust stage completes (FR-019, amendment 5:
   the Python stages after it report a rate and refuse nothing - not every seed passing them is feature 417's goal); its claims round is IN-STEP; the reviews its occasions owe have run;
   its time is recorded by `make perf-ab`.

### User Story 3 - The language decided on measurement (Priority: P2)

1. **Given** phases 1 and 2 rebuilt, **Then** a written decision compares the basic operations per second of the rebuilt Python
   against a Rust spike of the same phase on the same counters, and records the choice and its cost; a choice of Rust lands
   no Rust phase before every row of `dev/rust-tooling.md` marked one for one, partial or rewritten fires on a Rust fixture.

## Requirements *(mandatory)*

- **FR-001**: The program's first task derives every stage's budget (User Story 1), each derivation written from the stage's
  contract alone, and each MODE BUDGET verdict is given on a bundle from `make work-budget-bundle MODE=budget`, whose refusal
  of engine code and counts (443 FR-008) it passed - so today's counts cannot anchor the budget.
- **FR-002**: The program's target - the sum of the stage budgets at 40 households, and the whole roll's growth exponent - goes
  to the GM for approval (through `escalation-check`) before any phase is rebuilt; his words are recorded in
  `dev/work-budget-changes.jsonl`.
- **FR-003**: Each phase is one task of this feature, named for its stage (`phase: <stage>`), with its checklist at
  `phases/<stage>.md` - what 443 FR-010's landing check reads. Phases are rebuilt in `STAGES` order, so each rebuild's input is fixed; the first two are `water_frame` and `field`.
- **FR-004**: A phase's rebuild reads the same manifest keys and writes the same ones. Every rule is asked of a candidate
  before it is placed (rubric S4): no pass moves, drops or repairs a placed thing, and the counted drops and moves are zero.
  Where a rebuild does one of feature 417's tasks for its phase, that task is ticked with the landing as its evidence.
- **FR-005**: A phase is accepted only as User Story 2 states, and only with the old implementation deleted in the same landing
  (no fallback path, no flag); its accepted figure goes into `dev/work-budget.json`, which feature 443's ratchet then holds.
- **FR-006**: A phase is never set down because its time saved is small; a phase over its budget is either rebuilt again or
  its budget raised with the GM's words (`make budget-change`). The trial form's set-down rule does not apply to this
  program. The round arbiter may rule on process, but may not accept a phase over its budget, at acceptance (checklist box
  6) or anywhere else.
- **FR-007**: This feature adds `make work-budget-bundle MODE=table`: the whole standing record (`dev/work-budget.md`, the
  latest `make work-budget` run and the one before it), one bundle for one agent. At each phase landing the `work-budget`
  agent reads it in MODE AUDIT: no unbudgeted or unconverted stage grew, and the sum still converges on the target.
- **FR-008**: After phases 1 and 2, the language decision (User Story 3) is written in `research/language.md`, with its
  measurement dated and its method.
- **FR-009**: The feature closes only when the whole roll's counted operations meet the program's budget at 40 and 80
  households, or the GM changes the budget.
- **FR-010**: If the decision is Rust, the shape is the design's section 7: one extension module (PyO3, built by maturin)
  holding the rebuilt phases, each stage a thin Python function with its docstring calling into it; the driver, `STAGES`,
  the manifest, rendering, the pool's `.gen.py` scripts, the tools and the pytest suite stay Python. Its conventions: 1,000
  lines per file, split into submodules of about 650 lines re-exported by `mod.rs`; clippy's `too_many_lines` at 100;
  `#[expect(lint, reason = "...")]` for every suppression; unit tests in their own files, never at the bottom of the code's.
- **FR-011**: Before the first Rust phase lands, this feature builds every row of `dev/rust-tooling.md` marked one for one,
  partial or rewritten, and proves each fires on a Rust fixture; the landing of a Rust phase is refused until every such row
  is marked proven.
- **FR-013**: A stage's first budget is pinned on a SOUND verdict, or on the round arbiter's ACCEPT of its derivation (the GM 2026-10-28, answering 444#0: "Yes, I am okay with option one, letting the
  arbiters acceptance pin it"). An accept-pinned budget is bound to the derivation as it reads: any later change to a figure in it re-owes the arbiter's
  ruling (`make arbiter-ask`) before the budget stands; the program target (FR-002) names each
  stage pinned on an accept, with its rounds and its totals' spread; and the rebuilt phase is held to the budget as any other (FR-005,
  FR-006) and audited (MODE AUDIT). This amends 443 FR-005's SOUND-only rule for this program's budgets; `make budget-set` takes the
  accept by its trigger (`ARBITER=ask:<id>`), refusing one the arbiter's log does not hold as an accept naming the stage.
- **FR-014**: A budget counts the typical case, not the worst (the GM 2026-10-28, on a target of 15.3M at 40 households, above
  what the roll counts today: "I thought the idea was to REDUCE the number of operations. Why would we be targeting something
  HIGHER?"; the round arbiter's ruling ask:444-budget-standard). Each factor is the mean the stage's output shows (things per
  area, parts per index cell, the candidates the contract's search order reaches), read from the reference rolls' manifests and
  never from the counters or the code, times a slack of at most 2 (rubric S8); a factor at its worst case, and a cost per thing
  placed above the reference's 4,000 with no named reason, are findings - flagged by the bundle screen (`make work-budget-bundle`
  asks the reason of a derivation whose total at 40 over its items at 40 passes 4,000) and found by the work-budget agent. `make budget-set` refuses a pin above the stage's
  counted operations at 40 in the newest `make work-budget` run unless a reason is named, and prints the program per household
  against the design's few thousand. The stages pinned on an accept before FR-014 are re-scored to it - their algorithms and
  indexes stand, their factors change - and put to the round arbiter as one batch (`make arbiter-bundle BATCH=1`), which
  discharges the ruling FR-013 re-owes; a SOUND-pinned stage is re-scored and re-judged once in MODE BUDGET only where `make
  budget-set`'s gate fires on its pin; each is lowered with `LOWER=1` (no GM words: a lowering asks nothing of him). The new
  target then goes to the GM under FR-002 with the program's operations per household beside the design's few thousand.
- **FR-015**: Every stage is re-derived GREENFIELD (the GM 2026-10-29: "the ENTIRE point of what we're doing is to do a greenfield
  implementation unencumbered by the bad implementation chopices of our previous implementation ... if you're looking at the
  reference maps but not the original code, then that's one thing - that seems fine and even good"; his answer: "sounds good,
  please proceed with that"). A stage's contract - what it reads, writes and keeps - is written from the research record (its
  questions and drawing pages under `research/questions/`, the knobs' forms) and the reference rolls' manifests, never from today's
  code; its algorithm is designed from that contract. `make work-budget-bundle MODE=budget` refuses a derivation naming any module,
  function, method, class or module- or class-level name defined under `l7r/` (a local variable is not one), other than a knob's
  name or form, a stage's name and a manifest key, naming each; a figure the research
  fixes for a rendering choice is cited to its page, and a figure only today's code holds is a knob the derivation names as one,
  never a constant it inherits. The 23 budget units stay the record's stage names (the counters' keys); a derivation that finds two
  stages cheaper laid as one says so, and the merge goes to the round arbiter. The derivations are new files
  (`phases/<stage>.greenfield.md`), so the pins they replace stand until each new one is pinned - on SOUND or the arbiter's accept
  (FR-013), with `LOWER=1` where it is lower; a higher one leaves the standing pin in place, is named in the target, and is
  pinned only with the GM's words (`make budget-change`). The target of T09 is withdrawn: the new target
  goes to the GM under FR-002.
- **FR-016**: A stage touches only what can win (rubric S9; the GM 2026-10-29: "Why do we think it should take 8,730-11,277
  operations to place a single notice board?!"): a search that keeps one or a few of a set does work in proportion to the
  candidates that could win, by a bound read from an index (branch and bound), and a row that scores, sorts or paints every member
  of a set growing with the map names why no bound prunes it (`- pruning:`); work only a knob's branch needs is charged at that
  branch's share. The bundle screen asks the `- pruning:` line of a derivation above the reference's 4,000 a thing, and the
  work-budget agent judges it.
- **FR-017**: No phase is rebuilt in Python (the GM 2026-10-29, amendment 4: "I want to modify the plan so that we don't end up
  doing any Python rewrites. I think those are just going to slow us down"). The language decision is his, Rust, recorded in
  `research/language.md` in his words in place of FR-008's measured comparison, so FR-010's shape, FR-011's tooling proven before
  the first Rust phase and FR-012's counters apply to every phase from `field` on; the design's step 5 measurement is not run. A
  phase already accepted in Python whose rebuild was only its counters (`water_frame`, T15) stands, its algorithm unchanged, until
  its port to Rust - a phase task of its own, filed with FR-011's tooling and landed before the feature closes, held to the same
  budget - so SC-007's one extension module holds at the close.
- **FR-018**: A single paddy field is capped near the largest single field the research finds for a settlement of this kind, and a
  settlement whose farmland passes that cap draws more than one field (the GM 2026-10-29: "we can cap out at something approximating
  whatever that size is, and then larger settlements just have multiple fields"); the cap and its source are the field phase's
  contract, from a research pass that searches the record and the archive first (constitution XII). The field's greenfield
  derivation, already SOUND and pinned, is re-derived under the cap and owes a new MODE BUDGET verdict before the field phase
  lands; a figure above its standing pin keeps that pin and is pinned only with the GM's words (`make budget-change`, FR-006,
  FR-015).
- **FR-012**: Any Rust spike or phase keeps the counters of 443 FR-001 as a macro behind the Cargo feature `counters`:
  development and the gate build with it on, the deployed build without it, so the compiler removes them. Before a Rust phase
  lands, a seed rolled with the feature on and off writes identical manifests, as 443 FR-004 holds for Python.

- **FR-019**: The Rust stage gate (amendment 5, the GM 2026-10-31: "no Rust stage ever ends with any failing checks at the point
  where that stage has completed ... all seeds pass for all Rust stages, but we don't care at all about the Python stages which
  come after"). The stages are ported in `STAGES` order, so the Rust stages are always the front of the pipeline; a stage is Rust
  when `rust/phases/src/<stage>.rs` holds it, derived, and a test refuses a Rust stage that is not part of that front. Every seed
  is rolled through the Rust stages only and stops there; it fails when a Rust stage raises, or when a check of the finished-map
  checks fails whose every read of the map is of something the Rust stages wrote - a check that reads what only a later stage
  writes is that stage's, and is not asked (the check-to-stage assignment derived from what each check reads, never a hand
  table). Every engine landing requires the gate on its engine with no failing seed. A landing that changes a Rust stage
  (`rust/**`) is judged by it alone: its whole-pipeline cohort is rolled as a rate and refuses nothing, and a Python stage that
  fails on the Rust output is that stage's defect, never a reason to change the Rust stage. Matching Python's draws is not
  required; a port may roll with its own generator, its moved pool hamlets owing their settlement-reviews. A landing that
  changes no Rust stage keeps feature 386's landing cohort as it stands.
- **FR-020**: The Rust gate's seeds (amendment 5): no fixed reference block - a FRESH block of 48 seeds from a start that rotates
  with the engine, the six pinned row variants (901-906's pins) each on a fresh seed, and the FAILING LIST. A seed that fails the
  gate goes on the list with the Rust stage it failed in, and is rolled by every gate run until it first passes, then leaves the
  list. Beside it, the failing stage's INPUT - the map and the plan as the stages before it left them - is frozen as a fixture
  and replayed into that stage by every gate run until it passes, so a failure cannot leave the list only because a change
  upstream turned its seed into another map. The list and its fixtures are the Rust stages' alone; Python stages never add to it.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002, FR-013): every stage has a SOUND verdict, or the round arbiter's accept of its derivation (FR-013), given
  on a budget bundle the refusal passed, and a budget; the target carries the GM's words and names each stage pinned on an accept.
- **SC-008** (FR-013): a test refuses `make budget-set ARBITER=ask:<id>` when the arbiter's log holds no accept naming the stage and
  passes one that does; a test flags an accept-pinned budget whose derivation changed after its pin as owing the arbiter's ruling;
  each goes red with its condition deleted.
- **SC-009** (FR-014): a test refuses `make budget-set` above the stage's count today at 40 without a reason and prints the program
  per household at every pin, each going red with its condition deleted; and the target the GM approves is below today's counted
  operations at 40 at every stage, or names the stage's reason, and carries the program's operations per household beside the
  design's few thousand; a test refuses a derivation's bundle whose cost per thing at 40 passes 4,000 with no named reason.
- **SC-010** (FR-015, FR-016): a test refuses a derivation's bundle naming a function, a module, a method or a module-level name
  defined under `l7r/` and passes a knob's name and form, a stage's name and a manifest key, and refuses one above the reference with no `- pruning:` line, each going red with its
  condition deleted; every stage has a greenfield derivation with a SOUND verdict or the arbiter's accept, given with S9 in the
  rubric, and a budget pinned from it; the target the GM approves is the sum of those.
- **SC-011** (FR-018): the field phase's contract names the single-field cap and cites its research source; a test rolls a
  settlement whose farmland passes the cap and finds it draws more than one field, each at most the cap.
- **SC-002** (FR-003 to FR-006): each phase's checklist is ticked whole and its accepted figure at most its budget; the
  landing's size delta shows the old implementation removed, with no branch or flag left that selects it (`make
  dead-closure` checks for leftovers).
- **SC-003** (FR-007): `make work-budget-bundle MODE=table` writes the whole-table bundle, and each phase landing has its
  whole-table audit in the ledger.
- **SC-004** (FR-008, FR-017): `research/language.md` records the decision - the GM's choice of Rust in his words, amendment 4.
- **SC-005** (FR-009): the closing `make work-budget` shows the whole roll at most the program's budget.
- **SC-006** (FR-011, FR-012): `dev/rust-tooling.md` marks every ported row proven before the first Rust phase's landing,
  and a test refuses that landing with one unproven; the counters-on and counters-off manifests match.
- **SC-007** (FR-010): the rebuilt phases build as one extension module; a test finds every `STAGES` entry a Python function
  with its docstring, and no `.rs` file outside the test files holding a `#[cfg(test)] mod tests`.

- **SC-012** (FR-019): a test finds the Rust stages derived from `rust/phases/src/` and refused when not the front of `STAGES`; a
  test finds a check reading only Rust-written parts of the map asked at the gate and one reading a later stage's not asked; a
  test finds an engine landing refused when the gate has a failing seed, and a Rust-stage landing not refused by its whole-pipeline
  cohort.
- **SC-013** (FR-020): a test finds a failing seed added to the list with its stage and frozen input, rolled and replayed by the
  next run, and removed on its first pass; and the gate's seeds hold no fixed block.

## Edge Cases

- A stage whose derivation shows the current output itself is wasteful (it places what a later stage drops): the derivation
  says so, and the fix goes to the stage that owes it, not into a looser budget.
- A rebuild that moves maps: allowed for speed work (the GM, 2026-10-18), held to the research claims and the cohort.

## Assumptions

- Feature 417 stays open as the all-seeds-pass feature and feature 405 keeps its hold on it; feature 405 also keeps the claims
  work, which ports with the code.

## Review history

- 2026-10-28, round 1 (spec-fidelity, MODE 2): CHANGES REQUIRED, 7 items - the ports built and proven before a Rust phase,
  with section 7's shape and conventions (FR-010, FR-011); the Rust counters behind a Cargo feature (FR-012); the whole-table
  bundle named and built here (FR-007); SC-002 reads the size delta, not dead-closure alone; the arbiter's limit (FR-006);
  each phase one task (FR-003); the budget's freedom from today's counts is the bundle's refusal (FR-001).
- 2026-10-28, round 2 (spec-fidelity-verify, MODE 3): CHANGES REQUIRED, 1 item - all seven of round 1 resolved; FR-010 had
  no criterion, now SC-007 (the one extension, the stages still Python functions, no tests at the foot of a code file).
- 2026-10-28, the round cap: the round arbiter ACCEPT (ask:444-spec-round-3), standing as the spec's verdict; SC-007 applies
  only if the language decision is Rust, as FR-010 does.
- 2026-10-28, amendment 1 (the GM's answer to 444#0, `request.md`): FR-013 - an arbiter accept may pin a first budget, bound to its
  derivation, named in the program target, the rebuilt phase still held to it; SC-001 and User Story 1 read it; SC-008 tests it.
- 2026-10-28, amendment 1's review (spec-fidelity-verify, MODE 3): CHANGES REQUIRED, 4 items - FR-013's added convergence condition
  dropped; any change to a figure re-owes the ruling (not only a Total or a Bounds figure), the dispatch bar dropped; User Story 1;
  SC-008 for its two guards.
- 2026-10-28, amendment 1's review, round 2 (spec-fidelity-verify, MODE 3): FAITHFUL - all four items of round 1 resolved, no new
  contradiction; FR-013 matches the GM's "letting the arbiters acceptance pin it".
- 2026-10-28, amendment 2 (the GM's question on the step-3 target, the round arbiter's ruling ask:444-budget-standard): FR-014 - a
  budget counts the typical case times slack at most 2, the budgets pinned before it re-scored and lowered; SC-009 tests it.
- 2026-10-28, amendment 2's review (spec-fidelity-verify, MODE 3): CHANGES REQUIRED, 3 items - the re-scoring narrowed to the round
  arbiter's ruling (the accept-pinned stages in one batch, a SOUND one only where the gate fires); the per-household figure in the
  target the GM sees; the 4,000 screen named in the bundle screen and the agent.
- 2026-10-28, amendment 2's review, round 2 (spec-fidelity-verify, MODE 3): FAITHFUL - all three resolved, no new contradiction.
- 2026-10-29, amendment 3 (the GM on the budgets' source, `request.md`): FR-015 - every stage re-derived greenfield, its contract from
  the research and the reference manifests, today's code's names refused by the bundle; FR-016 - rubric S9, touch only what can win;
  SC-010 tests both; T09's target withdrawn.
- 2026-10-29, amendment 3's review (spec-fidelity, MODE 3): CHANGES REQUIRED, 2 items - a higher greenfield budget leaves the
  standing pin for the GM's words; the name check widened to modules, methods and module- or class-level names.
- 2026-10-29, amendment 3's review, round 2 (spec-fidelity-verify, MODE 3): FAITHFUL - both resolved, no new contradiction.
- 2026-10-29, amendment 4 (the GM on Rust first and the field's size, `request.md`): FR-017 - no phase rebuilt in Python, Rust his
  decision, step 5's measurement not run; FR-018 - a single field capped near the researched largest, a larger settlement drawing
  several; SC-004 reads it.
- 2026-10-29, amendment 4's review (spec-fidelity-verify, MODE 3): CHANGES REQUIRED, 3 items - SC-011 for FR-018; water_frame's
  Rust port scheduled before the close, so SC-007 holds; the field's derivation re-derived under the cap, a new verdict owed.
- 2026-10-29, amendment 4's review, round 2 (spec-fidelity-verify, MODE 3): FAITHFUL - all three resolved, no new contradiction.
- 2026-10-31, amendment 5 (the GM on the landing rule, `request.md`): User Story 2's acceptance reads the Rust stage gate in place
  of "no regressed seed"; FR-019 - every seed passes where each Rust stage completes, the checks asked by what they read, the
  Python stages after a rate; FR-020 - a fresh block, the pinned variants on fresh seeds, the failing list and its frozen inputs;
  SC-012 and SC-013 test them.
