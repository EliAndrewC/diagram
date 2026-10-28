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
   of SOUND from the `work-budget` agent, and a budget in `dev/work-budget.json`; their sum is the program's target, which the
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
  contract alone, before the stage's current counts are read, and bundled by `make work-budget-bundle MODE=budget`.
- **FR-002**: The program's target - the sum of the stage budgets at 40 households, and the whole roll's growth exponent - goes
  to the GM for approval (through `escalation-check`) before any phase is rebuilt; his words are recorded in
  `dev/work-budget-changes.jsonl`.
- **FR-003**: Phases are rebuilt in `STAGES` order, so each rebuild's input is fixed; the first two are `water_frame` and `field`.
- **FR-004**: A phase's rebuild reads the same manifest keys and writes the same ones. Every rule is asked of a candidate
  before it is placed (rubric S4): no pass moves, drops or repairs a placed thing, and the counted drops and moves are zero.
  Where a rebuild does one of feature 417's tasks for its phase, that task is ticked with the landing as its evidence.
- **FR-005**: A phase is accepted only as User Story 2 states, and only with the old implementation deleted in the same landing
  (no fallback path, no flag); its accepted figure goes into `dev/work-budget.json`, which feature 443's ratchet then holds.
- **FR-006**: A phase is never set down because its time saved is small; a phase over its budget is either rebuilt again or
  its budget raised with the GM's words (`make budget-change`). The trial form's set-down rule does not apply to this
  program.
- **FR-007**: At each phase landing the `work-budget` agent re-reads the whole table (MODE AUDIT over `dev/work-budget.md`):
  no unbudgeted or unconverted stage grew, and the sum still converges on the target.
- **FR-008**: After phases 1 and 2, the language decision (User Story 3) is written in `research/language.md`, with its
  measurement dated and its method.
- **FR-009**: The feature closes only when the whole roll's counted operations meet the program's budget at 40 and 80
  households, or the GM changes the budget.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002): every stage has a SOUND verdict and a budget; the target carries the GM's words.
- **SC-002** (FR-003 to FR-005): each phase's checklist is ticked whole, its accepted figure at most its budget, its old code
  gone (`make dead-closure` shows nothing of it left).
- **SC-003** (FR-007): each phase landing has its whole-table audit in the ledger.
- **SC-004** (FR-008): `research/language.md` records the decision with its measurement.
- **SC-005** (FR-009): the closing `make work-budget` shows the whole roll at most the program's budget.

## Edge Cases

- A stage whose derivation shows the current output itself is wasteful (it places what a later stage drops): the derivation
  says so, and the fix goes to the stage that owes it, not into a looser budget.
- A rebuild that moves maps: allowed for speed work (the GM, 2026-10-18), held to the research claims and the cohort.

## Assumptions

- Feature 417 stays open as the all-seeds-pass feature and feature 405 keeps its hold on it; feature 405 also keeps the claims
  work, which ports with the code.
