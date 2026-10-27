# Feature Specification: Call counts on the placement-stages page

**Feature Branch**: `434-placement-call-counts` (no branch; work on `main` in the clone)

**Created**: 2026-10-27

**Status**: Draft

**Affects**: tooling

**Approved**: the GM, 2026-10-27, "Yes, please do that, and please do include the per step counts."

**Input**: `request.md` (the GM's three messages, verbatim).

## Why

Feature 417's T57 measured a 40-household hamlet at 18,364,392 Python calls (measured 2026-10-27, `make perf-fanout LABEL=417-T57`) and broke them down by stage only in a chat
reply. The GM wants the breakdown where the procedure itself is described - the generated placement-stages page
(`dev/placement-stages/hamlet-placement.html`, `make placement-stages`) - so that reading what each stage does shows what it
costs, by stage and by step, from the most recent measurement.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Each stage's calls where the stage is described (Priority: P1)

The GM opens the placement-stages page and sees, in each stage's heading, how many calls that stage made in the most
recently measured 40-household hamlet and its share of the whole roll.

**Independent Test**: measure a 40-household hamlet, regenerate the page, and read each stage heading's count against the
measurement.

**Acceptance Scenarios**:

1. **Given** the reference hamlet's recorded measurement at 40 households, **When** the page is regenerated, **Then** each
   stage shows the reference's call count and its share of the reference's total.
2. **Given** a stage the reference's record does not hold (none recorded yet, or a stage added since), **When** the page is
   regenerated, **Then** it shows a dash, not a number.
3. **Given** the page, **Then** no time is shown with the counts.

### User Story 2 - The table at the end, each stage opening onto its steps (Priority: P1)

At the end of the page a table lists every stage with its calls and its share of the total. Clicking a stage's row expands
it to show the stage's steps, each with its calls, its share of the stage and its share of the whole map's generation.

**Independent Test**: on the regenerated page, click a stage's row: its steps appear with three numbers each; click again
and they collapse.

**Acceptance Scenarios**:

1. **Given** the table, **When** a stage row is clicked, **Then** its steps are shown, each with calls, percent of the stage
   and percent of the whole roll.
2. **Given** a stage's steps, **Then** the expanded rows show each step and a row for the stage's own work outside every
   listed step, and they add up to the stage's calls; the page states that a step's calls are those made while it was the
   innermost listed step running, so a step that contains another shows only its own share.
3. **Given** a stage no recorded type holds, **Then** its row shows only dashes and has no steps to expand; where only another
   type holds it, the row shows the reference's dash with that type beside it (FR-003).

### User Story 3 - Measuring keeps the latest counts (Priority: P2)

One command measures a 40-household hamlet of a given map type (by default the reference hamlet's spec) and records its
per-stage and per-step counts, keeping the most recent measurement for each map type. Every roll runs every stage - a
stage that does not apply to a map type returns after a handful of calls. The page breaks down the reference hamlet's roll:
the reference's counts stand for every stage, and another recorded type's count is shown beside a stage's - named, never
in its place - where that type spent more calls in the stage than the reference did.

**Acceptance Scenarios**:

1. **Given** the reference hamlet measured, **When** a polder hamlet is measured too, **Then** `waterward` (the polder dike's
   reed fringe, which the reference runs in a handful of calls) shows the reference's count with the polder's beside it,
   named, and the record keeps both.
2. **Given** a stage measured twice for one map type, **Then** the page shows the later measurement.

### Edge Cases

- A stage that does not apply to the reference shows the small count of its check-and-return, not a dash (the GM: "some
  of those will be literally zero"); a stage that does real work but places nothing (the settlement's seat) shows its
  count like any other.
- A step listed on the page that never ran in the measured roll shows 0.
- The record is committed, so the page regenerates the same counts on any clone until a new measurement replaces them.

## Requirements *(mandatory)*

- **FR-001**: A make target measures one 40-household hamlet (seed and map type selectable, the reference spec by default)
  and records, per stage, the calls it made and, per step the page lists for that stage, the calls made while that step was
  the innermost listed step running; calls in a stage outside every listed step are recorded as the stage's own work.
- **FR-002**: The record keeps the most recent measurement per map type, with its date, seed and engine commit, in a
  committed file.
- **FR-003**: `make placement-stages` shows in each stage's heading the reference hamlet's calls in that stage and their share
  of the reference's total, or a dash where the reference's record does not hold the stage; beside them, each other recorded
  type that spent more calls in the stage than the reference or holds a stage the reference's record lacks, named, with its
  calls and their share of its own total (where the reference lacks the stage, a dash with that type beside it).
- **FR-004**: The page ends - after its "Features this map does not have" section - with a table of every stage - the reference's calls and share of the reference's total, and
  beside them any other recorded type as FR-003 shows it - each row expandable on click to the reference's steps and a
  row for the stage's own work, each with calls, share of its stage and share of the reference's total, the page stating
  that a step's calls are those made while it was the innermost listed step; a dash where the reference's record does not
  hold the stage. The table's total row is the reference's total.
- **FR-005**: No time is shown beside the counts.
- **FR-006**: The counts are the same Python-call measure as `make perf-fanout` (cProfile's call count), each stage run in
  the process state the fanout's job gives it, so for the reference spec the record and the fanout agree on a stage's total
  for the same seed and engine.

## Success Criteria *(mandatory)*

- **SC-001** (FR-002, FR-003, FR-004): Every stage's count and share on the page equal the reference's record, the stages' counts sum to the total
  row, which equals the reference's recorded total, and every other type shown beside a stage equals its own record.
- **SC-002** (FR-001, FR-004): Within every stage, its steps plus its own work add up to the stage's count.
- **SC-003** (FR-006): For the reference spec, a stage's recorded count equals `make perf-fanout`'s for the same seed and engine
  (the fanout measures the reference spec only): both are cProfile's call count over the same stage run in the same process state, the step tally switching profilers rather than counting its own way, and the calls its own switching adds subtracted.
  NOTE (the round arbiter's accept on ask:434-SC-003-exact, 2026-10-27): met for the reference spec at seed 39, 40
  households, on this engine, by waiver - 19 of 23 stages equal the fanout's; sink -52 and seat +465 each equal one fanout
  run exactly (the fanout's own run and environment variation); field -307 and homesteads +298 keep a residue of a few
  hundred calls in stages of millions, measured 2026-10-27 (make phase-calls against make perf-fanout).
  The waiver holds at this scale only: a stage thousands of calls apart is a new question.
- **SC-004** (FR-004, FR-005): Expanding and collapsing a stage row works in the page as generated, with no time anywhere in the counts.

## Assumptions

- "Steps" are the steps the page already lists under each stage (its per-step walk-through).
- The reference hamlet's spec at 40 households, seed 39, is the default measurement (feature 417's T57 roll).
- Counting calls under a step needs a call tally during the roll; it may cost more time than a plain roll and is run on
  demand, never by the gate.
