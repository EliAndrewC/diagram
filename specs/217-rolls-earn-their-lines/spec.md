# 217 - rolls earn their lines

**Status**: FAITHFUL at round 2 (implementation in progress) - `spec-fidelity` round 1 required four changes, applied: every row KIND is stated under the rule
(FR-001a; `PoolGen` is the one exclusion, with its reason, for the GM to see); the proves-less section names the three seating
assertions that leave the gate; D2 states the real reason the seatings convert here; FR-007 (a `LINES=1` mode and a
twenty-line threshold) deleted, the line listing folded into FR-001's printout with no threshold. Round 2: FAITHFUL (one cross-reference slip fixed in passing).
**Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md).
**Predecessors**: 216 (the floor as doctrine: 3 rolls of 3, constitution VI v2.23.0, `make roll-audit`), 215 (the floor
itself), 214, 213 (the roll census and the roster).

## Summary

The GM's concern: a later session, without the context of features 213-216, thoughtlessly adds rolls back - while the hamlet
work continues, and especially at the village tier, where *"ten different village maps being rolled in our make done tests
when, in fact, only two or three would do"* is the failure to prevent. The ask is automation, not an instruction: *"if a new
map roll is added, then that causes a test failure or something Unless we prove in some way that we have consulted the
project guidelines and made a justification, done an audit"*, with no subagent on every run.

The GM accepted the session's proposal as stated in `request.md`. This feature builds items 1-4 and records item 5 as
deferred. The mechanism is the one the GM's own criterion dictates: a roll is justified by the engine lines it alone
reaches, and the gate measures that. Zero such lines means the roll can be removed with 100% kept, so under the doctrine
it must be - no threshold to argue about, no judgment call for the automation to make. What the automation cannot decide
(whether a roll's few unique lines could be unit tests instead) stays a session's duty, and the two cheap layers put the
doctrine in front of the session at the moment it opens the roster.

## Functional requirements

- **FR-001 THE RULE, at the gate.** After the test phase, the census verdict (`ci/rollverdict.py`) computes, for every
  `Roll` row the run rolled, the set of engine lines its coverage context reaches that NO other context of the run
  reaches - the same arithmetic as `make roll-audit`, on the run's combined coverage database. A row whose set is EMPTY
  fails the gate. The failure names the roll and the requesting test, quotes constitution VI's clause, and gives the three
  exits in the doctrine's words: pack the assertion onto a roll already made, make it a unit test of the placer, or move
  the test to `tests/soak/`. On every floored run, green or red, the verdict PRINTS each rostered roll's unique count and
  its files with the line numbers, so the number is seen every time and not only when it is zero, and the unit test
  that replaces a roll is written from the printout rather than from a second measurement.
- **FR-001a Every row KIND is under the rule, or its exclusion is stated.** The GM's fear is *"ten different village maps
  being rolled in our make done tests"*, and a roll can enter the roster by four kinds of row. `Roll`: judged by FR-001
  and owes FR-005's audit pointer. `Duplicate` (a second roll of a rostered spec a test makes by its nature; none today):
  judged by FR-001 on its own context - the mechanism it exists to exercise must reach lines the first roll did not, or
  the second roll is not needed - and owes the audit pointer. `InProcess`: a stub row rolls no map (bounded by
  `STUB_MAX_S`, feature 213) and a non-stub row only names WHERE a rostered spec may roll, so its spec is judged through
  its `Roll` row; no pointer of its own. `PoolGen` is the ONE EXCLUSION from FR-001's failure, stated here for the GM:
  a shipped generator is rolled by the sweep only when its cache key moved (an engine change) and is served from the
  gen cache otherwise (feature 215), and the pool's membership is the GM's exhibit decision, not a coverage one - a
  shipped map that reaches nothing the others do not is still a map the GM ships. FR-001 PRINTS each `PoolGen` row's
  unique count when the sweep rolled it, so the GM sees when the pool carries such a map; adding a `PoolGen` row is an
  edit to the guard file (FR-004) and so carries a stated reason. The cold cost of a large pool is therefore visible
  and decided, never silent.
- **FR-002 A roll knows its context.** `_census.record` writes the requester's coverage context (`L7R_COV_CONTEXT`, which
  every coverage child already inherits) on each `roll` record, so the verdict maps a roll to the context its lines were
  recorded under - a fixture's context when the roll was requested from a fixture, the test's `|run` context otherwise.
  A record with no context (a run without contexts, `make quick`) is not judged by FR-001.
- **FR-003 A roster change is judged against the whole suite.** A change to `tests/rolls.py` is one of the reasons the
  incremental gate runs FULL (`ci/incremental.py`'s plan), so a new row is measured against every context of the suite
  and never against a partial merge. On an incremental run FR-001 still runs over the merged database, which carries the
  kept contexts.
- **FR-004 The roster is a GUARD file.** `scripts/guard-file-hooks.sh` treats `tests/rolls.py` as it treats the Makefile:
  an Edit or Write without `GUARD_EDIT_OK` and a reason is refused, and the Read-time context for THIS file names the
  doctrine (constitution VI, "the gate rolls only what the floor needs") and the command to run first (`make roll-audit`).
  The same applies on the Bash route wherever the guard-file list is enumerated. Its test suite gains the cases.
- **FR-005 A roster row points at its audit.** `Roll` gains an `audit` field: the path of a research section
  (`specs/NNN-<slug>/research.md#R<k>`) that records the `make roll-audit` run (or feature 215's `unique_lines.py` output)
  which justified the row. `tests/test_rolls.py` checks the file exists and the section carries an audit header line
  (`roll audit:` or `unique of`). A row without one fails the static test - documentation as a required artifact, the
  research-checkbox shape. The two rows that stay point at specs/215 research R1 and specs/216 research R2.
- **FR-006 The seatings roll is converted under the rule.** Its one unique line (`hamletgen/homesteads/seats.py`)
  becomes a direct unit test; the three seating behavior tests and `roll_seatings` move to `tests/soak/` unchanged in
  what they assert (they keep their child roll there); the `SEATINGS` row leaves the roster. The gate then rolls 2 of 2.
- **FR-007 The doctrine names the enforcement.** `tests/rolls.py`'s docstring, `tests/CLAUDE.md`, the root `CLAUDE.md`
  bullet and the constitution VI clause each state that the rule is MEASURED at the gate and what the three exits are;
  the constitution edit is upkeep of the existing obligation, no version bump.
- **FR-008 Deferred, recorded.** The push-time `roll-review` agent (an independent Opus check on the perf-audit pattern,
  demanded by the push only when the delta adds a roster row) is not built; its design is recorded in
  `future-work/cross-cutting.md` with the reason it is third in line: the rule and the two layers act at zero token
  cost, and a row that passes FR-001 has already proved it reaches lines nothing else does.
- **FR-009 Measured after.** research.md R2: the verdict's printout on the landed gate, the roll count, the gate time.

## What proves less

ONE NEW SITE, for the GM to accept or refuse at landing. FR-006 moves three seating behavior assertions out of the gate
into `tests/soak/`, which no ordinary run collects and which nothing runs today: that the `cluster_seeds` cloud seats a
hamlet when both row passes offer nothing (and records the rolled shape as honored or unhonored), that the lane
frontage seats the hamlet when the field row offers nothing, and that the linear frontage pass stops once the households
are housed. Their one coverage line holds as a unit test of the seat placer; their BEHAVIOR is proved by nothing until
the soak tier runs. This is the same class of loss the GM accepted site by site in feature 216 (*"those types of tests
are intended for our longer AWS tests rather than for our make done gate"*), but that was a per-site acceptance, not a
standing one, so this site is named here as its own.

## Success criteria

- **SC-001** A unit test of the verdict fails a synthetic run whose rostered roll reaches no unique line and passes one
  whose roll reaches one; the real gate prints two rostered rolls with their counts.
- **SC-002** The guard-file suite proves an edit to `tests/rolls.py` without the marker is refused and one with it passes.
- **SC-003** `make done` green at 100% on both floors; the census reads 2 rolls of 2 specs on a warm run.

## Decisions Recorded

- **D1 - the floor is ZERO, not a number.** A threshold ("a roll owes 50 lines") would be arbitrary and would need a
  per-tier value; zero is the GM's criterion stated exactly - a roll with no unique line can go with 100% kept. What a
  roll with a FEW unique lines should become is judgment, and the printout plus the guard's Read-time marker put that
  judgment in front of the session; the deferred agent (FR-008) would make it independent.
- **D2 - the seatings are converted here.** The conversion is item 4 of the proposal the GM accepted (*"the seatings roll
  (one unique line) is converted under the rule in the same feature"*). Under FR-001 a roll with ONE unique line passes;
  the reason it converts is the doctrine's, not the rule's - one line is a unit test, and once that test exists the row's
  unique set is empty and FR-001 requires its removal. Shipping the rule and leaving that roll would be doing half of
  what was accepted.
- **D3 - the push-time agent is deferred**, per the session's recommendation the GM accepted ("hold as a follow-up").
- **D4 - the audit pointer is a research section, not free text.** A reason string is what the roster already had, and
  it was written in ten seconds; a section that must contain an audit's output exists only if the audit was run.
- **D5 - a roster change forces a FULL run.** The incremental merge keeps contexts, but a rule about "no other context"
  must not depend on the merge's completeness; a FULL run on a roster edit costs one gate and removes the question.
