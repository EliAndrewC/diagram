# Feature Specification: the work-budget tooling

**Feature Branch**: `443-work-budget-tooling` (no branch; work on `main` in the clone)

**Created**: 2026-10-28

**Status**: Draft

**Affects**: tooling, performance, review process

**Approved**: the GM, 2026-10-28, "Thank you. I approve the design. Please proceed."

**Input**: `request.md` (the GM's words, verbatim, and the design he approved: its steps 1 and 2 are this feature; feature 444
is the program the tooling serves).

## Why

Eleven speed features and trials (226, 227, 297, 304, 306, 314, 417 T55, 427, 437, 439, 441) each asked whether one slice
saved time, found a few percent of the roll and set it down. No record said what the whole roll should cost. The roll makes 26.4M Python calls
for 40 households (measured 2026-10-27 (`make phase-calls`, seed 39, 40 households; `specs/435-speed-aims-at-time/research/t08-evidence.md`)),
about 660k a house; the homesteads stage alone builds 803 seat envelopes for 40 houses, 95% of them discarded (measured
2026-10-27 (`make perf-share` and a counting spike, seed 25, 40 households; `specs/439-fewer-envelope-probes/research/funnel.md`)). This feature builds
the instrument and the check that make a whole-roll budget visible and enforced; feature 444 sets the budgets and rebuilds the
phases to them.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Counted work, per stage, that survives a port (Priority: P1)

1. **Given** `make work-budget`, **Then** it rolls the reference hamlet at 10, 20, 40 and 80 households and prints, per stage,
   its basic operations (in total and per thing placed), their growth exponent from 20 to 80 households, the stage's budget
   and the ratio, with the whole roll's line last.
2. **Given** a run under `python -O`, **Then** no counter runs: the counters sit in `if __debug__:` blocks, which `-O` drops; a
   deployed build runs under `-O`.

### User Story 2 - The counters never change a map (Priority: P1)

1. **Given** `make counters-inert`, **Then** a roll with the counters on and one under `python -O` write identical manifests,
   or it refuses, naming the first key that differs.

### User Story 3 - The budget on record, and held (Priority: P1)

1. **Given** a stage accepted under its budget, **When** a landing raises its counted operations past its accepted figure or
   its budget, **Then** the push refuses, naming the stage, both figures and `make budget-change`.
2. **Given** `make budget-change PHASE=<stage> TO=<n> WORDS="<the GM's words>"`, **Then** the budget moves and the change is
   logged with his words; without WORDS it refuses.

### User Story 4 - The distance from the goal in view (Priority: P2)

1. **Given** an engine landing or `make speckit-todo`, **Then** the standing record (`dev/work-budget.md`) is printed: every
   stage's budget, measured value and status, the whole roll against the program's budget, and the stages that moved.

### User Story 5 - An adversarial check of the arithmetic (Priority: P1)

1. **Given** a phase's derivation, **When** `make work-budget-bundle MODE=budget PHASE=<stage>` bundles it for the
   `work-budget` agent, **Then** the bundle holds the contract, the pseudocode, the operation count and the rubric, and never
   the current code or its measurements.
2. **Given** a landed phase, **When** `MODE=audit` bundles it, **Then** the agent reads the code, the counters by function at
   each size and the budget.

### User Story 6 - The phase checklist, held at landing (Priority: P2)

1. **Given** a phase task of feature 444 (its `phase: <stage>` line) whose checklist is absent, short of the eight boxes or
   has an unticked box, **When** `make land` runs, **Then** it refuses, naming what is missing.

### User Story 7 - No Python-only check forgotten (Priority: P1)

1. **Given** a hook, gate script or make target that reads `.py` files or Python's syntax tree, **Then** `dev/rust-tooling.md`
   has its row (one for one, dropped, partial, rewritten, replaced or unchanged, with what replaces it), or `make hooks-test` fails,
   naming it.

## Requirements *(mandatory)*

- **FR-001**: Counters of basic operations - a point or segment test, a distance, a spatial-index query with the entries it
  examined, a candidate evaluated, a thing placed, a thing dropped or moved after placing - in
  `l7r/diagram/settlement/_geom/primitives.py`, `l7r/diagram/settlement/_geom/indexes.py` and at each stage's candidate loop.
  Each is an inline increment inside `if __debug__:` (no function call, so the push's call-count guard, feature 427 T03, sees
  no new calls); a vectorized operation counts its elements.
- **FR-002**: The driver attributes the counts to the stage that made them, outside the manifest (the manifest is unchanged).
- **FR-003**: `make work-budget [SEED=<n>] [SIZES=10,20,40,80]` (by default seed 25 and the cohort's pinned seeds) prints FR-001's counts per stage as User Story 1 states, the
  80-household roll past the band through `beyond_the_band()`, and writes the run to `dev/work-budget/` with its engine
  commit. Python calls and wall times are recorded beside the counts; neither is the budget. It regenerates the standing
  record, `dev/work-budget.md`: every stage's budget, measured value and status, and the whole roll against the program's
  budget. The feature lands with that record holding today's figures for every stage at 10, 20, 40 and 80 households.
- **FR-004**: `make counters-inert` rolls one seed in two subprocesses, counters on and under `python -O`, and refuses unless
  the manifests are identical; `make done` runs it.
- **FR-005**: `dev/work-budget.json` holds each stage's budget - basic operations per thing placed, the growth exponent, the
  pointer to its derivation and its `work-budget` verdict - its status (unbudgeted, budgeted, accepted with the accepted
  figure) and the program's whole-roll budget. It is a guard file. A first budget needs a SOUND MODE BUDGET verdict (LOOSE or
  UNDERIVED refuses); a raise needs `make budget-change` with the GM's words, checked as the approval guard checks an
  `**Approved**:` line (`scripts/hooks/lib/hm_approval.py`: the words appear in a message the GM wrote in the session) and
  refused otherwise, then logged (`dev/work-budget-changes.jsonl`).
- **FR-006**: The push refuses a landing that raises an accepted stage's counted operations past its accepted figure or past
  its budget, at 40 or 80 households, naming the stage, the figures and `make budget-change`. The round arbiter cannot accept
  it; the GM's words through `make budget-change` are the one way past.
- **FR-007**: `make land` on engine code and `make speckit-todo` print the standing record (`dev/work-budget.md`): the
  whole-roll line, every stage's status and the stages that moved.
- **FR-008**: `.claude/agents/work-budget.md` (Opus). MODE BUDGET asks of a derivation: is each factor derived (S1-S3, S7);
  is there a standard, cheaper algorithm (a sweep, a grid, a priority queue, an incremental update); is any factor padded -
  SOUND, LOOSE (naming the factor and a tighter bound) or UNDERIVED (naming the factor with no reason). MODE AUDIT asks of
  landed code: are the counters within budget; does a counter cover every inner loop, nothing uncounted in C (S5); is
  anything placed and then repaired (S4); is the growth linear (S6) - WITHIN, OVER (naming the chain) or UNCOUNTED (naming
  the loop). `docs/work-budget-rubric.md` states standards S1-S7 of the design, and its reference figure for a
  homestead shows its arithmetic (S7). `make work-budget-bundle MODE=budget|audit PHASE=<stage>` writes the bundle; the
  budget bundle refuses to include engine code or counts. The agent is added to the pre-authorized list
  (`scripts/container/append-system-prompt.md`) and the model tier table.
- **FR-009**: Before its first real use the agent is dispatched on two fixtures (`tests/fixtures/work-budget/`): today's
  homestead seat funnel, to be ruled LOOSE or OVER, and a grid-indexed placer, to be ruled SOUND or WITHIN. The rulings are
  recorded beside the fixtures and in the ledger; a test holds the recorded rulings to those expectations.
- **FR-010**: `.specify/templates/phase-checklist.md` holds the design's eight boxes. `make land` recognizes a feature-444
  phase task by its `phase: <stage>` line (444 FR-003) and refuses it when its checklist (`specs/444-*/phases/<stage>.md`) is
  absent, lacks the template's eight boxes or has one unticked.
- **FR-011**: `dev/rust-tooling.md` holds one row per check, from section 7 of the design. A check run by `make hooks-test`
  (`make rust-tooling` prints its list) finds every hook, gate script and tool that reads `.py` files (lists or globs `*.py`,
  or tests for a `.py` suffix) or imports `ast`, `tokenize`, `inspect` or `symtable` or calls `compile()`, and every make recipe that runs a Python-only tool (ruff, pyrefly, pytest, coverage,
  testmon, vulture), and fails on any without a row.
- **FR-012**: Every refusal added is a guard: a test companion run by `make hooks-test`, a message naming the compliant
  command, proven to fire by deleting it and watching a test go red; `docs/guards.md` and each target's help name it.
  Nothing added refuses on a time (feature 435 FR-006).

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002, FR-003): `make work-budget` prints a row for every stage and the whole roll at four
  sizes; the Python calls `make perf-fanout` counts on seed 25 at 40 households stay within one call in a thousand of the count before the
  counters.
- **SC-002** (FR-004): `make counters-inert` passes on the engine as landed, and a test fails it on a counter that writes to
  the manifest.
- **SC-003** (FR-005, FR-006): tests refuse a landing over an accepted figure and over a budget, pass one under both, refuse
  a first budget without a SOUND verdict, refuse `make budget-change` without WORDS or with words the GM did not write, and
  log it with his.
- **SC-004** (FR-003, FR-007): `dev/work-budget.md` lands holding every stage at four sizes; a test reads the standing
  record in `make speckit-todo`'s output.
- **SC-005** (FR-008, FR-009): the agent file asks the three MODE BUDGET and four MODE AUDIT questions; its two fixture
  rulings are recorded and match; a test refuses a budget bundle holding
  engine code.
- **SC-006** (FR-010): tests refuse a phase task's landing with an unticked box, with no checklist file and with a checklist
  short of the eight boxes.
- **SC-007** (FR-011): the inventory check fails on a scratch reader with no row that uses `ast.parse`, one that uses
  `tokenize`, one that uses `inspect` and one that only globs `*.py`, and passes on the tree.
- **SC-008** (FR-012): each guard's test goes red with the guard deleted; `docs/guards.md` names each.

## Edge Cases

- A stage that places nothing (the seat, the sink): its budget is a whole-stage figure, not per thing placed.
- A size the roll refuses (80 households on a seed): the row says so and the exponent is taken over the sizes that rolled.

## Assumptions

- The counters' kinds are the design's (section 1); a kind added later is one more counter, not a redesign.
- The first budgets are set by feature 444's first task; until then every stage is unbudgeted and FR-006 holds nothing.

## Review history

- 2026-10-28, spec-fidelity MODE 2: NOT-REVIEWABLE (SC-001's tolerance carried a unit); written without one.
- 2026-10-28, round 1 (spec-fidelity, MODE 2): CHANGES REQUIRED, 8 items - the standing record `dev/work-budget.md` made and
  printed (FR-003, FR-007); a first budget needs SOUND (FR-005); WORDS checked as an Approved line is (FR-005, SC-003); an
  absent or short checklist refused, the `phase:` line recognized (FR-010, the round arbiter's note on 444); the inventory's
  detection named, `tokenize` and `inspect` included, "replaced" added (FR-011, SC-007, US7); the pinned seeds by default
  (FR-003); the agent's questions listed (FR-008); `-O` stated as the deployed run (US1).
- 2026-10-28, round 2 (spec-fidelity-verify, MODE 3): CHANGES REQUIRED, 1 item - seven of round 1 resolved; FR-011's detection
  had dropped "reads `.py` files" (it missed `check-file-scale.py`), now restored beside the parser imports, SC-007 testing a
  reader that only globs `*.py`.
- 2026-10-28, the round cap: the round arbiter ACCEPT (ask:443-spec-round-3), standing as the spec's verdict; FR-011's check is
  to find `scripts/gates/check-file-scale.py` on the real tree.
