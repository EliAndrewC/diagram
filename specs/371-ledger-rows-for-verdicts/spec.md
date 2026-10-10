# Feature 371: a ledger row for every recorded review verdict

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-09 (filed by feature 328's session); specified 2026-10-10

**Status**: Draft

**Affects**: review process, tooling

**Input**: `request.md` - the GM, 2026-10-10: *"ledger rows for recorded verdicts is about having a log of when our subagent
checks find something that needs to be changed and when they don't, so that we can see how often they are paying off ... I
could have sworn we already had that"*, and *"implement all three ... starting with 370, then 371, then 361"*.

## Summary

The log the GM describes exists: `dev/review-ledger.md`'s measured table, one row per review pass with what it found, whether
the author had missed it, what was done and its cost (feature 294). What does not exist is anything that makes the row get
written. Feature 328 ran 26 glyph checks in its batches 2-4 (2026-10-08/09) and wrote none of their rows; they were found
missing at batch 5's close and rebuilt by hand from the agents' transcripts. The record a check leaves - `make
review-verdict`, one file per unit - keeps only the unit's LATEST round, so a round overwritten before its row is written is
gone. This feature keeps every verdict in an append-only log, names each one that has no ledger row, prints the row to add
with its cost already measured, and refuses a push that would land a review pass without its row.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A review pass cannot land without its row (Priority: P1)

A session runs a review check; the check writes its verdict. Until the session adds the ledger row for it, every commit says
which verdict is missing a row and prints that row, and the push refuses.

**Why this priority**: it is the GM's question - can we see how often the checks pay off - answered by construction, so the
table the answer is read from is whole.

**Independent Test**: record a verdict in a fixture clone; the report names it and the push refuses; add the row it printed;
the report is empty and the push passes.

**Acceptance Scenarios**:

1. **Given** a verdict recorded today for `glyph-check--copse`, **When** no ledger row of today's date names `glyph-check`
   and `copse`, **Then** the report lists it with the row to add, and the push refuses.
2. **Given** that row added, **When** the check runs, **Then** it reports nothing and the push passes.
3. **Given** two rounds of the same unit, **When** only the first has a row, **Then** the second is still reported.

### User Story 2 - The row is printed, not reconstructed (Priority: P1)

The printed row carries the date, the check, the subject, the verdict and the number of findings, and the cost cells from the
agent's own measurement (`make review-cost AGENT=<id>`), where the dispatch recorded which agent ran; where it did not, the
row carries the command to run instead.

**Independent Test**: a verdict whose dispatch recorded its agent prints a row whose cost cells are that agent's measured
wall time and tokens.

### Edge Cases

- A verdict recorded before this feature: not in the log, so not reported (the log starts empty).
- A verdict re-recorded for the same round (a corrected findings file): one entry per call; each needs its row, and one row
  of that date may answer several entries of the same unit only if it says so (the row's subject names the unit and the
  check, and its date matches - one row per pass is the ledger's own rule).
- A record or plan check (`impl-drift`, `spec-fidelity`, ...) writes no verdict through `make review-verdict`; its rows stay
  the session's to write, as today (out of scope).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every call of `make review-verdict` MUST append its record - the unit, its check, the verdict, the number of
  findings, the engine key, the gate's state and the time - to an append-only log beside the per-unit records; nothing
  rewrites or deletes an entry.
- **FR-002**: A check MUST list every logged verdict that no row of the ledger's measured table answers - a row of the same
  date naming the unit's check and its subject.
- **FR-003**: For each, it MUST print the row to add: the date, the check, the subject, the verdict and the findings, with
  the wall and token cells from `make review-cost` for the agent the dispatch recorded, or the `make review-cost AGENT=<id>`
  command where none was recorded.
- **FR-004**: The check MUST report at every commit (it never refuses an unrelated commit) and MUST refuse the push while a
  verdict logged in that clone has no row, with an escape that states a reason and is recorded.
- **FR-005**: A test MUST prove the check fires on a verdict with no row and passes once the row exists.

### Key Entities

- **The verdict log**: one line per `make review-verdict` call, append-only, in the clone's git directory.
- **A row's answer**: a measured-table row whose date, check and subject match a logged verdict.

## Success Criteria *(mandatory)*

- **SC-001**: In a fixture, a recorded verdict with no ledger row is named by the check with the row to add, and the push
  refuses (FR-002, FR-003, FR-004).
- **SC-002**: The same fixture with that row added passes (FR-002, FR-005).
- **SC-003**: Two `make review-verdict` calls on one unit leave two log entries (FR-001).
- **SC-004**: A verdict whose dispatch recorded its agent prints that agent's measured cost cells (FR-003).

## Assumptions

- The ledger's measured table and its columns stay as feature 294 defined them (`scripts/reviews/ledger_lint.py`).
- A unit's name carries its check (`<check>--<subject>`, e.g. `glyph-check--copse`); a legacy bare name (`kashikawa`) is a
  settlement-review.
- The dispatch's agent id is read from feature 375's checks state where it recorded one.

## Out of Scope

- Rows for record and plan checks (`impl-drift`, `quote-check`, `spec-fidelity`, ...), which do not write review verdicts.
- Backfilling rows for verdicts recorded before this feature.
