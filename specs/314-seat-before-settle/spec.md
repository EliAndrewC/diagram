# Feature Specification: Seat before settle

**Feature Branch**: none - committed on `main` in the clone (`SPECIFY_FEATURE=314-seat-before-settle`)

**Created**: 2026-10-02

**Status**: Draft

**Input**: the GM's request, verbatim in `request.md`: proceed with checking the refused-ground grid, and the placed houses where
it is cheap, before a grown seat's household is laid out - *"whatever it is that we are missing that an efficient process would
have, we need to keep iterating until we get there."*

## Context: where the seating's time goes at 40 households (observed 2026-10-02, method: `request.md`'s measurement - the homesteads stage at 40 households, seeds 1, 2, 4, 6, 8, 9, 10, 12, 13 and 39, every grown seat followed to its outcome, one process, sequential)

The homesteads stage took 53.8 s over the ten seeds, every seed seating 40 on its first margin. Each seat the growth pops is first
SETTLED - the next household's whole homestead laid out at the seat to find how far it must move to keep its distance - and then
offered to the placer:

| what the seat came to | seats | settle | placer | share of the stage |
|---|---|---|---|---|
| refused on ground the grid refuses outright (house box, field reach, water) | 3,219 | 6.0 s | 0.2 s | 11% |
| refused: no garden side's box fit among the standing homesteads | 3,556 | 6.7 s | 1.4 s | 15% |
| fit, refused by the parts - no lawful corridor, or the lane law | 2,021 | 3.8 s | 12.8 s | 31% |
| seated | 400 | 0.8 s | 12.9 s | 25% |

The same breakdown at the GM's case, 15 households on seeds 1-16, is measured with the base leg of US1 and recorded in
`research.md` R1 (SC-003).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A seat the ground refuses is never laid out (Priority: P1)

Before a grown seat's household is laid out, the questions that depend only on where the house stands - the refused-ground grid
under the house's own box, the field's reach, the water - and the placed homesteads where that test is cheap, are asked of it; a
seat they refuse is dropped without the layout. Every seat still offered is asked the placer's full rules.

**Why this priority**: the GM's chosen first step; 11-26% of the stage measured on seats whose refusal costs almost nothing.

**Independent Test**: the measurement of `Context` rerun on the same seeds, back to back against the base: the settle time of
refused seats, the stage's time, and the households seated.

**Acceptance Scenarios**:

1. **Given** the reference at 40 households on the ten seeds, **When** it is rolled, **Then** the settle time spent on seats the
   placer refuses on the ground falls by most of its 6.0 s and every seed seats every household.
2. **Given** the pool and the cohort, **When** they are rolled, **Then** every rule passes and every household seated on the base
   is seated.

---

### User Story 2 - Keep iterating on the rest (Priority: P2)

After US1, the stage's remaining costs - the corridor search and the lane law on seats that fit (31%), the settle itself, the
seated commit - are each measured and attacked in further rounds, each prototyped and timed back to back before it is kept. The
iteration stops only when the record names each remaining cost of the stage, states what an efficient process would do about it,
and shows either that the stage now does that or a measured reason it cannot; every round's numbers, kept or withdrawn, are
recorded.

**Why this priority**: the GM's *"keep iterating until we get there"*.

**Independent Test**: each round's back-to-back timing at 15 and 40 households, recorded in `research.md` and
`dev/performance.md`.

**Acceptance Scenarios**:

1. **Given** a round kept, **When** the pool and cohort are rolled, **Then** every rule passes and no household is lost.
2. **Given** the iteration stops, **When** the GM reads the record, **Then** it names each remaining cost of the stage, what an
   efficient process would do about it, and either that the stage now does it or the measured reason it cannot - the only
   stopping rule.

### Edge Cases

- A seat refused on its own ground at any position the settle would lay its household out at might have cleared the ground had the
  settle moved it on: dropping it is a change of search breadth, not of a rule. Whether it costs a household is measured (US1
  scenario 2); a margin short for it is offered the next margin as today.
- The linear and dispersed forms do not grow (feature 308's rulings); US1 changes only the grown seating. A later round may touch
  them where the cost it attacks is theirs too.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Before a grown seat's household is laid out, the seat MUST be asked the placer's questions that need no layout -
  the refused-ground grid and the canvas under its house's own box, the field's reach, the water - and dropped where they refuse.
- **FR-002**: Where the placed homesteads can be asked of a seat without the layout at a cost below the layout's, they MUST be
  asked first too; the measurement decides which.
- **FR-003**: Every seat offered MUST still pass the placer's full rules; no rule is relaxed or skipped (constitution XIII).
- **FR-004**: Further rounds (US2) MUST each be prototyped and timed by the wall clock, base and clone back to back, before being
  kept; each round's numbers, kept or withdrawn, are recorded in `research.md` and `dev/performance.md`.
- **FR-005**: No pool map or cohort seed may fail a rule it passed before or seat fewer households; maps may move within the
  rules (GM 2026-09-30, feature 297: "They do NOT need to remain identical in output").

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-002): The homesteads stage at 40 households on `Context`'s ten seeds is at least 10% faster than the
  base, back to back (the base observed 2026-10-02, method: `Context`'s measurement - 53.8 s summed).
- **SC-002** (FR-003, FR-005): The cohort passes as many seeds as the base, every pool map passes its rules, every household is
  seated.
- **SC-003** (FR-001, FR-002): The GM's case - the 15-household reference, seeds 1-16 - has its refusal breakdown recorded for the
  base, and US1's gain there is recorded, base against clone, back to back.
- **SC-004** (FR-004): The 15-household reference's homesteads stage, summed over seeds 1-16, is recorded after every kept round;
  the iteration stops only by US2's acceptance scenario 2.
- **SC-005**: The perf bookend's 15-household reference is not slower (perf band 0 or better).

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| A grown seat refused on its own ground at any position the settle would lay its household out at is dropped, not moved on | map drawing convention (the placement ORDER and search breadth, as feature 308 classed its growth; every seat offered passes the same rules) | the GM: check the grid "before the household layout"; whether dropping rather than moving out costs a household is measured (FR-005), not assumed | this spec; the growth's docstring |

## Assumptions

- `request.md`'s measurement harness (`specs/314-seat-before-settle/refusals.py`, copied from the scratchpad) is the measure;
  feature 308's sixteen reference seeds are the 15-household measure.

## Review history

- Round 1 (spec-fidelity, 2026-10-02): CHANGES REQUIRED, 2 items - US2's 5%-a-round stopping rule narrowed the GM's "keep
  iterating until we get there"; the GM's case is 15 homesteads and US1's success was defined only at 40. Addressed: the only
  stopping rule is the record naming each remaining cost, what an efficient process would do and that the stage does it or a
  measured reason it cannot; SC-003 records the breakdown and US1's gain at 15 households, seeds 1-16. The aside (the Decisions
  row's unmeasured claim) answered: the cost is measured (FR-005), not assumed.
- Round 2 (spec-fidelity, verify, 2026-10-02): FAITHFUL - both items and the aside confirmed against the diff.
- Amendment (the plan review's round 1, item 2, 2026-10-02): the Decisions row said the seat was dropped "at its first settled
  position"; the settle drops it at any position it would lay the household out at (each move is a layout, the GM's "before
  the household layout"). The row and the Edge Cases entry now say so; the review count restarts.
