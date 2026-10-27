# Feature Specification: Call counts on the placement-stages page

**Feature Branch**: `434-placement-call-counts` (no branch; work on `main` in the clone)

**Created**: 2026-10-27

**Status**: Draft

**Affects**: tooling

**Approved**: the GM, 2026-10-27, "Yes, please do that, and please do include the per step counts."

**Input**: `request.md` (the GM's two messages, verbatim).

## Why

Feature 417's T57 measured a 40-household hamlet at 18,364,392 Python calls and broke them down by stage only in a chat
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

1. **Given** a recorded measurement of a 40-household hamlet, **When** the page is regenerated, **Then** each stage the
   measurement exercised shows its call count and its share of that roll's total.
2. **Given** a stage no recorded 40-household hamlet exercised, **When** the page is regenerated, **Then** it shows a dash,
   not a number.
3. **Given** the page, **Then** no time is shown with the counts.

### User Story 2 - The table at the end, each stage opening onto its steps (Priority: P1)

At the end of the page a table lists every stage with its calls and its share of the total. Clicking a stage's row expands
it to show the stage's steps, each with its calls, its share of the stage and its share of the whole map's generation.

**Independent Test**: on the regenerated page, click a stage's row: its steps appear with three numbers each; click again
and they collapse.

**Acceptance Scenarios**:

1. **Given** the table, **When** a stage row is clicked, **Then** its steps are shown, each with calls, percent of the stage
   and percent of the whole roll.
2. **Given** a stage's steps, **Then** the steps' calls and the stage's own work outside any listed step add up to the
   stage's calls (a step's calls are those made while it is the innermost listed step running, so no call is counted twice).
3. **Given** a stage no recorded hamlet exercised, **Then** its row shows a dash and has no steps to expand.

### User Story 3 - Measuring keeps the latest counts (Priority: P2)

One command measures a 40-household hamlet of a given map type (by default the reference hamlet's spec) and records its
per-stage and per-step counts, keeping the most recent measurement for each map type; the page shows, for each stage, the
most recent count among the map types that exercise it, and names the map type it came from.

**Acceptance Scenarios**:

1. **Given** the reference hamlet measured, **When** a polder hamlet is measured too, **Then** the polder's stages that the
   reference never runs show the polder's counts and name it, and the record keeps both.
2. **Given** a stage measured twice for one map type, **Then** the page shows the later measurement.

### Edge Cases

- A stage that runs but places nothing on this map type (it checks and returns) shows its small count, not a dash.
- A step listed on the page that never ran in the measured roll shows 0.
- The record is committed, so the page regenerates the same counts on any clone until a new measurement replaces them.

## Requirements *(mandatory)*

- **FR-001**: A make target measures one 40-household hamlet (seed and map type selectable, the reference spec by default)
  and records, per stage, the calls it made and, per step the page lists for that stage, the calls made while that step was
  the innermost listed step running; calls in a stage outside every listed step are recorded as the stage's own work.
- **FR-002**: The record keeps the most recent measurement per map type, with its date, seed and engine commit, in a
  committed file.
- **FR-003**: `make placement-stages` shows in each stage's heading its calls and its share of the measured roll's total,
  or a dash where no recorded hamlet exercised it.
- **FR-004**: The page ends with a table of every stage - calls and share of the total - each row expandable on click to its
  steps, each step with calls, share of its stage and share of the whole roll; a dash where unmeasured.
- **FR-005**: No time is shown beside the counts.
- **FR-006**: The counts are the same Python-call measure as `make perf-fanout` (cProfile's call count), each stage measured
  in a fresh process, so the page and the fanout agree on a stage's total for the same seed, type and engine.

## Success Criteria *(mandatory)*

- **SC-001**: For the reference 40-household hamlet, every stage's count on the page equals the record's, and the total
  equals the sum of the stages.
- **SC-002**: Within every stage, its steps plus its own work add up to the stage's count.
- **SC-003**: A stage's count on the page is within 1% of `make perf-fanout`'s for the same seed and engine.
- **SC-004**: Expanding and collapsing a stage row works in the page as generated, with no time anywhere in the counts.

## Assumptions

- "Steps" are the steps the page already lists under each stage (its per-step walk-through).
- The reference hamlet's spec at 40 households, seed 39, is the default measurement (feature 417's T57 roll).
- Counting calls under a step needs a call tally during the roll; it may cost more time than a plain roll and is run on
  demand, never by the gate.
