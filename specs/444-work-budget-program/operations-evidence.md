# Where the time and the operations go (feature 444, for the operations-budget talk)

Measured 2026-11-07 for the GM's two questions of the day: why the port takes so long in development time, and why its stages
count so many operations (amendment 8: "stop work on more porting until we get to the bottom of why this is taking so long, both
in terms of development time and per-phase operations"). Measurements only: no budget is raised and no stage is rewritten on
this paper (the round arbiter on ask:set-down-444-claims-wait).

## 1. Development time: the loop

| what | before | now | how measured |
|---|---|---|---|
| `make cover-changed` | 68 min (stopped) | 14 s | its wall time, `date +%s` either side, 2026-11-07 |
| the Rust crate's tests | 1,058 s | 7 s | `make rust-test`'s wall time, 2026-11-07 |
| `make done` at rust-only | red, about 25 min a round | 344 s green | `dev/run-log/2026-11/20261107T125247978136-3209868.json` |

Where the 68 minutes went (each found by measuring, not guessed):

- the crate's tests were built unoptimized; one test, the row village's seating, took 101.6 s of the suite, in Rust `seat_rows`:
  a map-wide distance grid asked point by point, the parallel streets' offset traced against a 2 ft street index (3.7 billion
  segment tests in one dry-edge case), an all-pairs nearest-point search, and every candidate stretch's six parallel streets set
  out though most were never read - fixed, 1.9 s, all 215 crate tests passing;
- the coverage run cleaned its build every time (`llvm-cov clean --profraw-only` drops cargo's fingerprints), built the crate
  twice (`--lib` missing) and a third time for the Python driver - now 0.0 s to build when nothing changed, 5-15 s after an edit;
- `cover-changed`'s Python half (46 minutes) ran the engine's tests, and a test helper regenerated four pool maps through the
  Python stages; at rust-only neither runs.

Where `make done`'s 344 s goes now (the run record's phases, which overlap): pytest 287 s, static 41 s, preflight 23 s,
counters-inert 8 s, floors 5 s. The slowest tests (`make durations N=60`, 2026-11-07, the engine trees left aside) are tooling
tests that build things:

| test | s |
|---|---|
| `test_rust_tooling` - the counters refuse an uncounted port | 57.3 |
| `test_rust_tooling` - coverage counts Python's lines | 50.2 |
| `test_claims_index` - the command line | 47.5 |
| `test_rust_tooling` - uncovered names each file's lines | 35.4 |
| `test_claims_index` - an unfiled carry refused | 30.6 |
| `test_claims_index` - a landing with no engine code | 28.2 |
| `test_claims_index` - owed, introduced, pre-existing | 25.7 |
| `test_work_budget_fixtures` - main builds and refuses | 21.6 |

The Rust tooling tests each compile a fresh copy of the fixture crate (its own package name, so cargo cannot share a build); the
claims-index tests build git repositories and run the gate in them. Both are the next speed work: share one fixture build, and
run the claims gate in process on a prepared tree.

Development time also went to process, the gate's red rounds today: four reds before the green, each in a phase no earlier
gate had reached (clippy, rustfmt, the coverage floor read two ways, a make `$(if)` split by a comma, five stale assertions), each
a round-arbiter ruling (about 2-4 minutes each) and a part B section. And the landing itself waits on 4,623 claims owed an
impl-drift check - six ported stages never landed, so their whole delta is new to main (about 103 dispatches, one a file).

## 2. Operations: the homesteads stage

Counted by `make work-budget` on 4 rolls a size (`dev/work-budget/20261106T121431Z-86406787cda6.json`, commit d5b46b322):

| households | operations (mean) | a household |
|---|---|---|
| 20 | 6,267,667 | 313,000 |
| 40 | 13,170,612 | 329,000 |
| 80 | 26,752,463 | 334,000 |

Growth is linear (exponent about 1.04): nothing is all-pairs. The cost is a constant of about 330,000 operations a household,
against a first-principles estimate of about 9,700 (the work-budget check's own, verdict-9 under S11), spread over 107 counters,
none more than a tenth. The largest at 40:

| counter | operations | share |
|---|---|---|
| `write@lane_blocked` (the lane ground's raster written) | 1,372,412 | 10.4% |
| `write@crossing_points` | 1,128,226 | 8.6% |
| `index_query@reach` | 1,029,309 | 7.8% |
| `dist@along_tail` | 899,055 | 6.8% |
| `candidate@grow` | 795,831 | 6.0% |
| `seg_test@oblique` | 784,512 | 6.0% |
| `seg_test@undeckable` | 784,512 | 6.0% |
| `pt_test@clears` | 665,182 | 5.1% |
| `candidate@flood` | 578,402 | 4.4% |
| `pt_test@standing_clear` | 485,048 | 3.7% |

and about 1.48 million calls a roll. The shape is the one the fixed SOUND check found in the budget's derivation: map-wide
rasters painted, labeled and flooded (the lane ground, the reach, the free ground), and searches whose candidates are tested
against every rule, where the stage's own work is a few thousand operations a house. The budget it was held to (1,477,085 at 40,
judged SOUND twice) is itself LOOSE under S11 (3.8 times the first-principles estimate); the count is 8.9 times that budget.

## 3. Operations: the appurtenances stage

| households | operations (mean) |
|---|---|
| 20 | 15,824 |
| 40 | 20,486 |
| 80 | 37,449 |

Against a first budget of 713 at 40: the first derivation priced a well seated at a corner four lots share, clear by
construction, and the rebuilt stage asks each drawn record of the registry (`index_examined@PointGrid.near` 30%,
`dist@seg_closest` 18%, the registry's rows and the houses' cells 24% at 40). Its re-derivation (`## Work the first derivation
missed`) prices the registry, the toe band, open water's reach and the lane-side seats at 20,303; it is small in absolute terms
next to the homesteads.

## 4. What this suggests (for the talk, not decided)

- the homesteads re-derived under S11 from what each household needs, each map-wide raster either justified by a rule or
  replaced by an index asked around the houses - the largest single lever on both the operations and the gate's own time;
- the tooling tests' builds shared - the largest lever left on `make done`'s wall time;
- the claims owed on the ported stages decided (the GM's question, put this session).
