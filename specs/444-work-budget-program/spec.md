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
   exponent at most the budget's; `make cohort-landing` shows no regressed seed and the fresh block's pass rate is no worse
   (not every seed passing: that is feature 417's goal); its claims round is IN-STEP; the reviews its occasions owe have run;
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
  placed above the reference's 4,000 with no named reason, are findings. `make budget-set` refuses a pin above the stage's
  counted operations at 40 in the newest `make work-budget` run unless a reason is named, and prints the program per household
  against the design's few thousand. The budgets pinned before FR-014 are re-scored to it - their algorithms and indexes stand,
  their factors change - each re-scored stage re-judged once in MODE BUDGET, the stages pinned on an accept put to the round
  arbiter as one batch, and lowered with `LOWER=1` (no GM words: a lowering asks nothing of him); the new target then goes to the
  GM under FR-002.
- **FR-012**: Any Rust spike or phase keeps the counters of 443 FR-001 as a macro behind the Cargo feature `counters`:
  development and the gate build with it on, the deployed build without it, so the compiler removes them. Before a Rust phase
  lands, a seed rolled with the feature on and off writes identical manifests, as 443 FR-004 holds for Python.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002, FR-013): every stage has a SOUND verdict, or the round arbiter's accept of its derivation (FR-013), given
  on a budget bundle the refusal passed, and a budget; the target carries the GM's words and names each stage pinned on an accept.
- **SC-008** (FR-013): a test refuses `make budget-set ARBITER=ask:<id>` when the arbiter's log holds no accept naming the stage and
  passes one that does; a test flags an accept-pinned budget whose derivation changed after its pin as owing the arbiter's ruling;
  each goes red with its condition deleted.
- **SC-009** (FR-014): a test refuses `make budget-set` above the stage's count today at 40 without a reason and prints the program
  per household at every pin, each going red with its condition deleted; and the target the GM approves is below today's counted
  operations at 40 at every stage, or names the stage's reason.
- **SC-002** (FR-003 to FR-006): each phase's checklist is ticked whole and its accepted figure at most its budget; the
  landing's size delta shows the old implementation removed, with no branch or flag left that selects it (`make
  dead-closure` checks for leftovers).
- **SC-003** (FR-007): `make work-budget-bundle MODE=table` writes the whole-table bundle, and each phase landing has its
  whole-table audit in the ledger.
- **SC-004** (FR-008): `research/language.md` records the decision with its measurement.
- **SC-005** (FR-009): the closing `make work-budget` shows the whole roll at most the program's budget.
- **SC-006** (FR-011, FR-012): `dev/rust-tooling.md` marks every ported row proven before the first Rust phase's landing,
  and a test refuses that landing with one unproven; the counters-on and counters-off manifests match.
- **SC-007** (FR-010): the rebuilt phases build as one extension module; a test finds every `STAGES` entry a Python function
  with its docstring, and no `.rs` file outside the test files holding a `#[cfg(test)] mod tests`.

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
