# Handoffs between "Reference testing" (correctness) and "Diagram tests" (efficiency)

One line per pull and per handoff: direction, sha, what it was tested with, when.

| when (UTC) | direction | sha | tested with | note |
|---|---|---|---|---|
| 2026-08-28 04:05 | message -> Diagram tests | - | - | FR-000: told it this session merges its changes and owns the correctness fixes; asked for a safe sha (msg 7b11f701) |
| 2026-08-28 04:25 | pull <- Diagram tests | ebbf29ef | its unlocked make done green (3,750 tests) | merged exactly up to the named sha (FR-001); their gate now has tests/ quick, tests/gate/ done, tests/full/ FULL; a roll cache (.gencache/rolls); GATE_COHORT_EXPECTED judged for the seeds the scope rolls (41 at the gate, all four under FULL) |
| 2026-08-28 04:5x | main <- Diagram tests | 1433d457 | feature 135 landed on main (the GM ticked T99); nothing further in its clone | arrived through the turn's sync-in; the ebbf29ef merge is a subset of it |
| 2026-08-28 13:xx | main <- Diagram tests | 837b6f2d | feature 138 (fabric + watercourse indexes; every manifest byte-identical, hamlets 3-4x faster) | arrived through the turn hook's sync-in as merge d9db3140; declared safe by its author with md5-equal manifests, so the correctness pins are unaffected; the reference re-rolled clean on the merged tree |
