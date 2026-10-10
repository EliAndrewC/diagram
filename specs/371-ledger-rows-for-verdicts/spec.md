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

### User Story 1 - A check's pass cannot land without its row (Priority: P1)

A session runs any check the ledger logs - a map review, a record check, `impl-drift`, a spec or plan round, `perf-audit`,
`escalation-check`. When the check returns, its pass is logged with its measured cost. Until a row of the ledger carries that
pass, every commit says which pass is missing its row and prints the row, and the push refuses.

**Why this priority**: it is the GM's question - can we see how often our subagent checks pay off - answered by construction,
so the table the answer is read from is whole: all of it, not the 40% the map reviews make up (spec review round 1, measured
on the table's 374 rows).

**Independent Test**: log a pass in a fixture clone; the report names it and the push refuses; add the row it printed; the
report is empty and the push passes.

**Acceptance Scenarios**:

1. **Given** a `glyph-check` pass logged today, **When** no row of the measured table carries its check and its cost cells,
   **Then** the report lists it with the row to add, and the push refuses.
2. **Given** that row added, **When** the check runs, **Then** it reports nothing and the push passes.
3. **Given** two rounds of one check on one subject on one day, **When** only the first has its row, **Then** the second is
   still reported - each pass has its own cost, so one row cannot answer both.

### User Story 2 - The row is printed, not reconstructed (Priority: P1)

The printed row carries the date, the check, what it checked and its wall and token cells as measured when the pass returned;
the session fills only the judgment cells (verdict, finding, class, author missed?, acted on).

**Independent Test**: a logged pass prints a row whose cost cells are the ones `make review-cost` gives for its agent.

### Edge Cases

- A pass from before this feature: not in the log, so not reported (the log starts empty).
- A pass whose rows land in an earlier push: still answered - the rows stay in the ledger, and a row answers by its cells, not
  by the push that carried it.
- A pass with several findings: one row per finding (the ledger's rule); any one row carrying its cells answers it.
- An agent that is not a check (a general-purpose helper, `round-arbiter`, `perf-audit`'s helpers): not logged - the log takes
  exactly the checks the ledger's `CHECKS` set names.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every return of a dispatched agent whose type is a check the ledger names (`ledger_lint.CHECKS`) MUST append a
  record - the date, the check, what it checked, its agent and its measured wall and token cells - to an append-only log in
  the clone's git directory; nothing rewrites or deletes an entry.
- **FR-002**: A pass is ANSWERED by a row of the measured table whose check, wall cell and tokens cell are the pass's; a check
  MUST list every logged pass no row answers.
- **FR-003**: For each, it MUST print the row to add with its date, check, subject and cost cells filled, and the judgment
  cells left for the session.
- **FR-004**: The check MUST report at every commit (it never refuses an unrelated commit) and MUST refuse the push while a
  pass logged in that clone has no row, with an escape that states a reason and is recorded.
- **FR-005**: A test MUST prove the check fires on a pass with no row, passes once the row exists, and tells two same-day
  rounds apart.

### Key Entities

- **The pass log**: one line per returned check, append-only, in the clone's git directory.
- **A row's answer**: a measured-table row carrying the pass's check and its cost cells.

## Success Criteria *(mandatory)*

- **SC-001** (FR-002, FR-003, FR-004): In a fixture, a logged pass with no row is named with the row to add, and the push
  refuses.
- **SC-002** (FR-002, FR-005): The same fixture with that row added passes.
- **SC-003** (FR-001, FR-005): Two returns of one check on one subject in one day leave two entries, each answered only by
  its own row.
- **SC-004** (FR-001, FR-003): A logged pass's printed cost cells are those `make review-cost` gives for its agent.

## Assumptions

- The ledger's measured table and its columns stay as feature 294 defined them (`scripts/reviews/ledger_lint.py`), and its
  cost cells are copied from `make review-cost AGENT=<id>`, never typed (its own heading says so) - which is what lets the
  cells identify a pass.
- Feature 375's hooks see every agent's launch (PostToolUse, with its type and agent id) and return (SubagentStop, with its
  transcript); the log is written there.

## Out of Scope

- Backfilling rows for passes from before this feature.

## Review history

- **spec-fidelity round 1 (2026-10-10): NOT FAITHFUL.** (1) Record and plan checks out of scope was a carve-out against "our
  subagent checks" - 60% of the table's rows on round 1's own run; now every check the ledger names is logged, at its return. (2) A same-date
  subject match could not tell two same-day rounds apart - a pass is now answered by its own cost cells. (3) FR-004 faithful.
