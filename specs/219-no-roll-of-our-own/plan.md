# Plan - 219 no roll of our own

Tooling, tests and doctrine. Constitution: VI (the gate rolls only what the floor needs; the count line is upkeep, no
bump); X (dead lines are deleted, every new line owes 100%); XIII/XIV (nothing regresses; the three polder lines become
unit tests before the roll goes); XVI (the spec reviewed against the GM's words).

1. FR-001: delete the immune test, `extra_draws`, `_perturbed_manifest`; the reference's row; the retirement recorded in
   the roster docstring, `tests/CLAUDE.md`, the `gencache` docstring, `dev/placement.md`'s randomness section and the
   skill `CLAUDE.md` line (practice kept, requirement retired).
2. FR-003: lift `stage_polder`'s two loops (`walk_pond_uphill`, `dike_gaps_at_channels`) with unit tests; a `fit_polder`
   stop test; `rollcache._roll_payload`/`_roll`/`hamlet`/`report` and `_pool`'s non-pool branches on stubs; the polder's
   behavior tests to `tests/soak/test_polder_fall_0.py`; `rolls.COVERAGE` = the two shipped maps; the floor's subjects and
   its test; the Polder row leaves.
3. FR-002 + FR-004 + FR-005: research R1 (all seven rolls), the roster with zero rows, the doctrine's count in six places.
4. `make done`, the census warm and cold, R2 (the floor's module set before and after), land.
