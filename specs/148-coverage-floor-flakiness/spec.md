# Feature Specification: the coverage floor's flaky verdict

**Feature**: 148-coverage-floor-flakiness
**Created**: 2026-08-29
**Status**: DRAFT - awaiting `spec-fidelity` before implementation

## The defect

The hamlet-path coverage floor returns different verdicts for the same code. `hinterland.py` 503-504 - the
woodland shrink ladder - came out covered in some full runs and uncovered in others, with nothing changed
between them. Feature 147 parked those two lines so the speedup could land; this feature removes the park by
fixing the cause.

A floor that flips is worse than a slow one. Its whole purpose is to be believed: a session that sees it go
red on code it did not touch learns to re-run the gate until it passes, and at that point the floor has
stopped being a guarantee and become a toll.

## What feature 147 already eliminated (do not re-derive these)

Measured, each one ruling out a hypothesis:

| ruled out | how |
|---|---|
| the roll-sharing added by 147 | the floor is red with sharing disabled, and green in a tree that has the sharing and nothing else |
| the cohort seed count | each of the eight members covers the rung when rolled alone |
| PARALLELISM | a single-worker run (`XDIST_WORKERS=1`) is red too - so `--dist worksteal` is NOT the cause, contrary to 147's own first guess |
| pool-cache serving | forcing regeneration (`GATE_NO_CACHE=1`) is red too |
| a synthetic fixture | the woodland scan yields no seat without a fully planned site, so there is no cheap unit test for the rung |
| my own new tests | removing each implicated file in turn left it red, and the bisect's verdicts contradicted one another |

The contradictory bisect is itself evidence: the result is not a function of the test set alone.

## The leading hypothesis, to be tested first

`gencache.gate_obtain` on a HIT does not re-execute a map - it **replays the coverage data stored with the
cache entry**. That stored data is a set of LINE NUMBERS recorded when the entry was made. If the engine has
since changed in a way that moved the lines of a module the entry did not record as a dependency, the replay
marks the wrong lines: some show covered that were not, and some show uncovered that were. That would explain
every observation - cold runs green (everything re-executed), warm runs red (stale replay), isolation green,
and a bisect whose verdicts move with which entries happen to be fresh.

It is a hypothesis and the spec says so; FR-001 requires it to be tested before anything is built on it.

## Requirements *(mandatory)*

- **FR-001** The CAUSE must be established by measurement before a fix is written, and recorded - including
  the hypothesis above being disproved, if that is what happens. A fix that makes the symptom go away without
  a named cause is not acceptable here: the symptom is intermittent, so "it passed twice" proves nothing.
- **FR-002** The floor must return the SAME verdict for the same code. Demonstrated by repeated full runs on
  an unchanged tree, warm and cold, with the count of runs recorded.
- **FR-003** The park added by 147 must be REMOVED - both the `# pragma: no cover` in `hinterland.py` and the
  `PARKED` entry - and the floor must hold at 100% without it. The park is the debt this feature repays.
- **FR-004** The `PARKED` mechanism itself may stay (it is the general tool for a future case) but must be
  empty, and its test must keep proving that a parked line excuses only itself.
- **FR-005** If the cause is stored-coverage staleness, the fix must make a stale replay IMPOSSIBLE rather
  than unlikely - an entry whose stored coverage cannot be trusted must be re-executed, not replayed.
- **FR-006** No loss of the feature-147 speedup. The full sweep must not return to its 234 s baseline.
- **FR-007** Whatever the cause, a REGRESSION TEST must fail if it returns - a test of the mechanism, not a
  re-run of the suite, since re-running an intermittent failure proves nothing.

## Success Criteria *(mandatory)*

- **SC-001** The cause is named in writing, with the measurement that establishes it.
- **SC-002** The floor gives the same verdict across at least five consecutive full runs on unchanged code.
- **SC-003** `PARKED` is empty and `hinterland.py` carries no coverage pragma for these lines.
- **SC-004** The full sweep is no slower than the figure feature 147 landed.
- **SC-005** A regression test exists for the named cause and is proved to fail without the fix.

## Assumptions

- The GM takes no acceptance task; the feature lands when it is done (their instruction).
- "The same verdict" means the floor's pass/fail and its missing-line list, not the wall time.
