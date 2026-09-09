# Research - 221 the gate's fixed costs

## R1 - the profile before (2026-09-09, this clone, warm caches, 22-CPU container)

**The gate, phase by phase** (each target timed on its own):

| phase | time | notes |
|---|---|---|
| static, format, typecheck | 1.4 + 0.1 + 0.6 s | autocorrecting |
| `_reference` | 9.4 s cold (the roll), ~2 s warm | |
| `hooks-test` | 26.7 s (guard scripts had changed); 0 s when stamped; 63 s for all 21 suites | |
| `test-full`, incremental with nothing reachable | 21.4 s | 2.9 s planning, ~10 s pytest, ~8 s bookkeeping |
| `test-full`, full, under the gate (the 220 landing run) | pytest 47 s, 3,496 tests, 6 workers | whole-engine coverage with per-test contexts |
| after pytest: combine, merge, three `coverage report` tables, the hamlet floor, the roll census, the baseline save | ~8 s | the tables ~2.5 s each |

A warm full gate lands at 60-70 s; cold rolls add 10-20 s; a guard change adds 27-63 s.

**The suite three ways:**

| run | tests | wall |
|---|---|---|
| everything but rolling tests, no coverage (`make durations FULL=1`) | 2,777 | 19.4 s |
| the same, scoped coverage, no contexts (`make test INCREMENTAL=0`) | 2,777 | 14.7 s |
| the rolling tests alone, no coverage (`MARK=rolls_map`) | 26 | 15.9 s |
| the full gate run: every tree, whole-engine coverage, contexts | 3,496 | 47 s |

Slowest tests (no coverage): `test_every_glossary_term_is_used_by_a_modal_or_a_record_page` 5.3 s,
`test_a_linear_hamlet_strings_its_houses_along_the_connector` 3.3 s, the browser test 2.9 + 1.2 s setup,
the driver's AST scan 1.7 s; nothing else over 1.5 s. The rolling tail: `test_roll_village_is_deterministic...`
6.7 s and `test_pinned_knob_is_byte_identical...` 5.2 s (both `tests/full/settlement/test_rolling.py`,
village-tier rolls), then 3.2 s and 3.1 s.

**`make roll-audit` on the landed baseline:** `test_pinned_knob...` 15 unique lines (`settlement/rolling/roll.py`);
`test_roll_village_is_deterministic...` **1** unique line (`settlement/_geom/water_index.py`) for two
6.7 s rolls; `test_roll_village_honors_a_pinned_knob` (gate tree) 0 unique; the cohort test 95; the pool
sweep's Mizuguchi 13, Sawada 13, Kashikawa 5.

**The worker cap's origin** (`Makefile`, `XDIST_WORKERS`): feature 213 measured the full test phase at
4 / 6 / 8 workers as 346 / 301 / 297-322 s and took "the smallest count within 10% of the fastest", with
~250 MiB back to other sessions as the tie-break - on the gate of 2026-09-07, which rolled 37 hamlets at
~24 s each. Today's gate rolls three at ~7 s.
