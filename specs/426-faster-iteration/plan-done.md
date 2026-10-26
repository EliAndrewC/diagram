# 426-faster-iteration - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-26 -->
### T01 Approach (checklist part A)

1. **The goal, in the world.** `make land` never waits for a claims round nothing can deliver.
2. **The constraints.** D1; FR-001, FR-002, FR-011.
3. **Where each comes from.** the GM 2026-10-26 (fix 1); measured: T50's two full waits (research R1).
4. **Do they describe the world here?** Measured by: the wait loop re-runs the gate each poll; the marker is the one new state.
5. **The order.** first: the cheapest, the largest measured waste.
6. **The exits.** green: landed by `make land` with T02-T04; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T03 Approach (checklist part A)

1. **The goal, in the world.** A docstring-, comment- or claims-only edit re-rolls and re-renders nothing; content docstrings still count.
2. **The constraints.** D3; FR-003, FR-005, FR-006, FR-012.
3. **Where each comes from.** the GM 2026-10-26; R2, R3; measured R5 (11 of 16 re-rolled before, 0 after).
4. **Do they describe the world here?** Measured by: `make cache-audit` (3 audited, 0 FAILED) and the before/after cohort count.
5. **The order.** after T02.
6. **The exits.** green: landed with T01, T02, T04; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T04 Approach (checklist part A)

1. **The goal, in the world.** The other code-hashing keys follow the same rule where they should.
2. **The constraints.** the audit table; FR-004.
3. **Where each comes from.** the GM 2026-10-26 ("look for any other places"); R3b.
4. **Do they describe the world here?** Measured by: each site's test: a function docstring keeps it, code moves it, usage text and the Makefile still count for `tooling_hash`.
5. **The order.** after T02.
6. **The exits.** green: landed with T01-T03; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T02 Approach (checklist part A)

1. **The goal, in the world.** A code edit that runs nothing changes no key.
2. **The constraints.** D2; FR-003, FR-004.
3. **Where each comes from.** the GM 2026-10-26 ("omitting docstrings when hashing code"); feature 133 T11's rule.
4. **Do they describe the world here?** Measured by: `gate-stamp.py`'s `semantic_bytes` already held the rule; moved, not rewritten.
5. **The order.** before T03 and T04, which use it.
6. **The exits.** green: landed with T01, T03, T04; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
### T02 part B (2026-10-26T12:15Z)

The trigger: red-gate@2026-10-26T12:13:24Z, the second red gate in a row on 426 T01-T04's landing.

1. **What exactly is refusing?** Gate 1 (11:53): seven hook and content-cache tests - their fixture repos copy `scripts/` but the
   code id sat under `l7r/`, so `gate-stamp.py` could not load it there. Gate 2 (12:13): the 100% floor, six lines of
   `gencache._split_sources`' raw (`interactive/`) branch no unit test ran.
2. **A3 again.** O: the gate's fixtures (they copy the scripts tree whole); the coverage floor over the whole engine.
3. **A4 again.** It describes the change: the module's home decided which fixtures carried it; `cover-changed` measured
   `tests/pipeline` only, the full floor the rest.
4. **Moving something placed earlier to suit something later?** The module moved to `scripts/gates/` beside `gate-stamp.py`,
   where the rule always lived, an engine shim at `l7r/diagram/pipeline/codeid.py`; no behavior changed.
5. **Tuning or changing?** Neither: two distinct defects, each fixed once (the move; one unit test).
6. **The one-sentence test.** "The code id lives where every fixture carries it, and its raw branch is tested" - no question.
7. **The next step is a measurement.** `make land` again: hook suites, the shim and `gencache` at 100% under the full floor.
8. **Routes measured?** One route each: the move (hook suites green), the test (coverage of the branch).
9. **After a ruling.** The round arbiter ruled continue (red-gate@2026-10-26T12:13:24Z); a third distinct red goes back to it.

### T05 Approach (checklist part A)

1. **The goal, in the world.** Iterating rolls the failing seeds first or only, and stops at the first failure.
2. **The constraints.** D4; FR-007, FR-008.
3. **Where each comes from.** the GM 2026-10-26 ("the pytest thing").
4. **Do they describe the world here?** Measured by: tests on stubbed rolls; one real run on a seeded failure.
5. **The order.** after T03 (the served/rolled count reads the new key).
6. **The exits.** green: `make land`; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T02 Approach (checklist part A)

1. **The goal, in the world.** A code edit that runs nothing changes no key.
2. **The constraints.** D2; FR-003, FR-004.
3. **Where each comes from.** the GM 2026-10-26 ("omitting docstrings when hashing code"); feature 133 T11's rule.
4. **Do they describe the world here?** Measured by: `gate-stamp.py`'s `semantic_bytes` already held the rule; moved, not rewritten.
5. **The order.** before T03 and T04, which use it.
6. **The exits.** green: landed with T01, T03, T04; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
### T02 part B (2026-10-26T12:15Z)

The trigger: red-gate@2026-10-26T12:13:24Z, the second red gate in a row on 426 T01-T04's landing.

1. **What exactly is refusing?** Gate 1 (11:53): seven hook and content-cache tests - their fixture repos copy `scripts/` but the
   code id sat under `l7r/`, so `gate-stamp.py` could not load it there. Gate 2 (12:13): the 100% floor, six lines of
   `gencache._split_sources`' raw (`interactive/`) branch no unit test ran.
2. **A3 again.** O: the gate's fixtures (they copy the scripts tree whole); the coverage floor over the whole engine.
3. **A4 again.** It describes the change: the module's home decided which fixtures carried it; `cover-changed` measured
   `tests/pipeline` only, the full floor the rest.
4. **Moving something placed earlier to suit something later?** The module moved to `scripts/gates/` beside `gate-stamp.py`,
   where the rule always lived, an engine shim at `l7r/diagram/pipeline/codeid.py`; no behavior changed.
5. **Tuning or changing?** Neither: two distinct defects, each fixed once (the move; one unit test).
6. **The one-sentence test.** "The code id lives where every fixture carries it, and its raw branch is tested" - no question.
7. **The next step is a measurement.** `make land` again: hook suites, the shim and `gencache` at 100% under the full floor.
8. **Routes measured?** One route each: the move (hook suites green), the test (coverage of the branch).
9. **After a ruling.** The round arbiter ruled continue (red-gate@2026-10-26T12:13:24Z); a third distinct red goes back to it.

### T06 Approach (checklist part A)

1. **The goal, in the world.** A landing after a full run rolls no seed.
2. **The constraints.** FR-012, User Story 3b.
3. **Where each comes from.** the GM 2026-10-26 ("run the seeds locally and then do a make landing").
4. **Do they describe the world here?** Measured by: the landing-path test, and one real cohort then cohort-landing.
5. **The order.** after T03 and T05.
6. **The exits.** green: `make land`; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T02 Approach (checklist part A)

1. **The goal, in the world.** A code edit that runs nothing changes no key.
2. **The constraints.** D2; FR-003, FR-004.
3. **Where each comes from.** the GM 2026-10-26 ("omitting docstrings when hashing code"); feature 133 T11's rule.
4. **Do they describe the world here?** Measured by: `gate-stamp.py`'s `semantic_bytes` already held the rule; moved, not rewritten.
5. **The order.** before T03 and T04, which use it.
6. **The exits.** green: landed with T01, T03, T04; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
### T02 part B (2026-10-26T12:15Z)

The trigger: red-gate@2026-10-26T12:13:24Z, the second red gate in a row on 426 T01-T04's landing.

1. **What exactly is refusing?** Gate 1 (11:53): seven hook and content-cache tests - their fixture repos copy `scripts/` but the
   code id sat under `l7r/`, so `gate-stamp.py` could not load it there. Gate 2 (12:13): the 100% floor, six lines of
   `gencache._split_sources`' raw (`interactive/`) branch no unit test ran.
2. **A3 again.** O: the gate's fixtures (they copy the scripts tree whole); the coverage floor over the whole engine.
3. **A4 again.** It describes the change: the module's home decided which fixtures carried it; `cover-changed` measured
   `tests/pipeline` only, the full floor the rest.
4. **Moving something placed earlier to suit something later?** The module moved to `scripts/gates/` beside `gate-stamp.py`,
   where the rule always lived, an engine shim at `l7r/diagram/pipeline/codeid.py`; no behavior changed.
5. **Tuning or changing?** Neither: two distinct defects, each fixed once (the move; one unit test).
6. **The one-sentence test.** "The code id lives where every fixture carries it, and its raw branch is tested" - no question.
7. **The next step is a measurement.** `make land` again: hook suites, the shim and `gencache` at 100% under the full floor.
8. **Routes measured?** One route each: the move (hook suites green), the test (coverage of the branch).
9. **After a ruling.** The round arbiter ruled continue (red-gate@2026-10-26T12:13:24Z); a third distinct red goes back to it.

### T07 Approach (checklist part A)

1. **The goal, in the world.** A probe answers "what did this change do to every seed and map" against HEAD in one command.
2. **The constraints.** D5; FR-009.
3. **Where each comes from.** the GM 2026-10-26 (fix 2).
4. **Do they describe the world here?** Measured by: tests on stubbed rolls and fixture manifests; one real probe.
5. **The order.** after T05 (its EXITFIRST).
6. **The exits.** green: `make land-tooling`; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T02 Approach (checklist part A)

1. **The goal, in the world.** A code edit that runs nothing changes no key.
2. **The constraints.** D2; FR-003, FR-004.
3. **Where each comes from.** the GM 2026-10-26 ("omitting docstrings when hashing code"); feature 133 T11's rule.
4. **Do they describe the world here?** Measured by: `gate-stamp.py`'s `semantic_bytes` already held the rule; moved, not rewritten.
5. **The order.** before T03 and T04, which use it.
6. **The exits.** green: landed with T01, T03, T04; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
### T02 part B (2026-10-26T12:15Z)

The trigger: red-gate@2026-10-26T12:13:24Z, the second red gate in a row on 426 T01-T04's landing.

1. **What exactly is refusing?** Gate 1 (11:53): seven hook and content-cache tests - their fixture repos copy `scripts/` but the
   code id sat under `l7r/`, so `gate-stamp.py` could not load it there. Gate 2 (12:13): the 100% floor, six lines of
   `gencache._split_sources`' raw (`interactive/`) branch no unit test ran.
2. **A3 again.** O: the gate's fixtures (they copy the scripts tree whole); the coverage floor over the whole engine.
3. **A4 again.** It describes the change: the module's home decided which fixtures carried it; `cover-changed` measured
   `tests/pipeline` only, the full floor the rest.
4. **Moving something placed earlier to suit something later?** The module moved to `scripts/gates/` beside `gate-stamp.py`,
   where the rule always lived, an engine shim at `l7r/diagram/pipeline/codeid.py`; no behavior changed.
5. **Tuning or changing?** Neither: two distinct defects, each fixed once (the move; one unit test).
6. **The one-sentence test.** "The code id lives where every fixture carries it, and its raw branch is tested" - no question.
7. **The next step is a measurement.** `make land` again: hook suites, the shim and `gencache` at 100% under the full floor.
8. **Routes measured?** One route each: the move (hook suites green), the test (coverage of the branch).
9. **After a ruling.** The round arbiter ruled continue (red-gate@2026-10-26T12:13:24Z); a third distinct red goes back to it.

### T08 Approach (checklist part A)

1. **The goal, in the world.** A new plan section already holds what its review asks.
2. **The constraints.** D6; FR-010.
3. **Where each comes from.** the GM 2026-10-26 (fix 3); T48's and T50's review rounds.
4. **Do they describe the world here?** Measured by: tests of the written section and the warning.
5. **The order.** any time.
6. **The exits.** green: `make land-tooling`; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T02 Approach (checklist part A)

1. **The goal, in the world.** A code edit that runs nothing changes no key.
2. **The constraints.** D2; FR-003, FR-004.
3. **Where each comes from.** the GM 2026-10-26 ("omitting docstrings when hashing code"); feature 133 T11's rule.
4. **Do they describe the world here?** Measured by: `gate-stamp.py`'s `semantic_bytes` already held the rule; moved, not rewritten.
5. **The order.** before T03 and T04, which use it.
6. **The exits.** green: landed with T01, T03, T04; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
### T02 part B (2026-10-26T12:15Z)

The trigger: red-gate@2026-10-26T12:13:24Z, the second red gate in a row on 426 T01-T04's landing.

1. **What exactly is refusing?** Gate 1 (11:53): seven hook and content-cache tests - their fixture repos copy `scripts/` but the
   code id sat under `l7r/`, so `gate-stamp.py` could not load it there. Gate 2 (12:13): the 100% floor, six lines of
   `gencache._split_sources`' raw (`interactive/`) branch no unit test ran.
2. **A3 again.** O: the gate's fixtures (they copy the scripts tree whole); the coverage floor over the whole engine.
3. **A4 again.** It describes the change: the module's home decided which fixtures carried it; `cover-changed` measured
   `tests/pipeline` only, the full floor the rest.
4. **Moving something placed earlier to suit something later?** The module moved to `scripts/gates/` beside `gate-stamp.py`,
   where the rule always lived, an engine shim at `l7r/diagram/pipeline/codeid.py`; no behavior changed.
5. **Tuning or changing?** Neither: two distinct defects, each fixed once (the move; one unit test).
6. **The one-sentence test.** "The code id lives where every fixture carries it, and its raw branch is tested" - no question.
7. **The next step is a measurement.** `make land` again: hook suites, the shim and `gencache` at 100% under the full floor.
8. **Routes measured?** One route each: the move (hook suites green), the test (coverage of the branch).
9. **After a ruling.** The round arbiter ruled continue (red-gate@2026-10-26T12:13:24Z); a third distinct red goes back to it.

### T10 (feature 426, found 2026-10-26: commit 335cfa840 swept in the cache audit's perturbation): no write or commit while `make cache-audit` runs

- **Approach**: `make cache-audit` perturbs a numeric literal inside an engine function IN THE WORKING TREE, sweeps the pool, and
  restores the file at the end (observed 2026-10-26, method: `git show 335cfa840` carried `rot_rect`'s `w / 3`, restored by
  a7e46883b). The gate-write guard (`scripts/hooks/gate-write-hooks.sh`) already refuses a write while this tree's `make done`
  runs (`own-make.sh done`); it learns the same of `make cache-audit` (`own-make.sh cache-audit`), refusing an Edit or Write
  under `l7r/` or `pool/` and any `git add` or `git commit`, with the cure (wait: `make verify-wait`-style, the audit's own
  exit) in its message. Escape: the guard's existing `GATE_WRITE_OK`. Rendering: none.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a (a guard, no map step) | - | - | - | - |

### T10 Approach (checklist part A)

1. **The goal, in the world.** No commit carries a file the cache audit has perturbed.
2. **The constraints.** FR-011 (the fix in its own output, a test proving it fires); the guard's existing escape.
3. **Where each comes from.** O: commit 335cfa840 (observed 2026-10-26, method: its diff); G: the GM's "tooling, not remembering".
4. **Do they describe the world here?** Measured by the suite: a refusal while a stand-in `make cache-audit` runs, a pass after.
5. **The order.** After T08; before the close.
6. **The exits.** Green: landed by `make land`. Red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask` (D11, D35).
7. **The search smell.** None: one guard clause, its test first.
8. **The budget.** One landing.
9. **Done, measured.** `tests/hooks/test-gate-write-hooks.sh` refuses the write and the commit during the audit, passes them after.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T02 Approach (checklist part A)

1. **The goal, in the world.** A code edit that runs nothing changes no key.
2. **The constraints.** D2; FR-003, FR-004.
3. **Where each comes from.** the GM 2026-10-26 ("omitting docstrings when hashing code"); feature 133 T11's rule.
4. **Do they describe the world here?** Measured by: `gate-stamp.py`'s `semantic_bytes` already held the rule; moved, not rewritten.
5. **The order.** before T03 and T04, which use it.
6. **The exits.** green: landed with T01, T03, T04; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
### T02 part B (2026-10-26T12:15Z)

The trigger: red-gate@2026-10-26T12:13:24Z, the second red gate in a row on 426 T01-T04's landing.

1. **What exactly is refusing?** Gate 1 (11:53): seven hook and content-cache tests - their fixture repos copy `scripts/` but the
   code id sat under `l7r/`, so `gate-stamp.py` could not load it there. Gate 2 (12:13): the 100% floor, six lines of
   `gencache._split_sources`' raw (`interactive/`) branch no unit test ran.
2. **A3 again.** O: the gate's fixtures (they copy the scripts tree whole); the coverage floor over the whole engine.
3. **A4 again.** It describes the change: the module's home decided which fixtures carried it; `cover-changed` measured
   `tests/pipeline` only, the full floor the rest.
4. **Moving something placed earlier to suit something later?** The module moved to `scripts/gates/` beside `gate-stamp.py`,
   where the rule always lived, an engine shim at `l7r/diagram/pipeline/codeid.py`; no behavior changed.
5. **Tuning or changing?** Neither: two distinct defects, each fixed once (the move; one unit test).
6. **The one-sentence test.** "The code id lives where every fixture carries it, and its raw branch is tested" - no question.
7. **The next step is a measurement.** `make land` again: hook suites, the shim and `gencache` at 100% under the full floor.
8. **Routes measured?** One route each: the move (hook suites green), the test (coverage of the branch).
9. **After a ruling.** The round arbiter ruled continue (red-gate@2026-10-26T12:13:24Z); a third distinct red goes back to it.

### T09 Approach (checklist part A)

1. **The goal, in the world.** The feature closed with its numbers shown to the GM.
2. **The constraints.** the close.
3. **Where each comes from.** the constitution's close.
4. **Do they describe the world here?** Measured by: the feature report.
5. **The order.** last.
6. **The exits.** green: the report written; red: the missing items named and the close set down.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

