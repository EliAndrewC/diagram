# Plan - 217 rolls earn their lines

Tooling and doctrine. Constitution: VI (the clause this enforces; upkeep, no bump); X (every new line owes 100%);
XIII/XIV (nothing regresses; the seatings' one line becomes a unit test); XVI (the spec reviewed against the GM's words);
XVIII (a guard change carries its test).

1. THE RULE (FR-001, FR-001a, FR-002): `_census.record` writes the requester's coverage context; `ci/rollverdict.judge`
   takes the per-context unique lines (computed from the run's combined `.coverage` by `tools/roll_audit.read_contexts`
   + `unique_lines` with no floor) and fails a `Roll` or `Duplicate` whose set is empty, prints every rostered row's
   count, files and lines, and prints a rolled `PoolGen`'s count. Unit tests on synthetic censuses and databases.
2. THE GUARD (FR-004): `tests/rolls.py` in `guard-file-hooks.sh`'s regex and case list with a roster-specific Read-time
   context, and in `_hm_make.py`'s guard-write patterns; cases in both suites.
3. THE POINTER (FR-005): `Roll.audit` / `Duplicate.audit`; `tests/test_rolls.py` checks the section exists and holds
   an audit header; the two rows point at specs/215 R1 and specs/216 R2.
4. THE CONVERSION (FR-006): the seat placer's one unique line (from the printout) as a unit test; the three seating
   tests and `roll_seatings` to `tests/soak/test_seatings.py`; the SEATINGS row and `HERE_MOD` child leave.
5. FR-003 is a test of `incremental.plan` (a `tests/rolls.py` change already plans FULL as a non-module file under
   tests/); FR-007 the doctrine in four places; FR-008 the deferred agent in `future-work/cross-cutting.md`.
6. `make done`, the census read (2 of 2), R2, land.
