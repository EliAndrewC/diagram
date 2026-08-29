# Feature Specification: the coverage floor's flaky verdict

**Feature**: 149-coverage-floor-flakiness
**Created**: 2026-08-29
**Status**: APPROVED. `spec-fidelity` round 1 returned CHANGES REQUIRED (3): SC-002's fixed five re-runs contradicted FR-007's own reasoning and would have burned the measurement budget; FR-004 made an unrequested policy call about the PARKED machinery; and the plural in the GM's wording was never accounted for. All three applied.

## The defect

The hamlet-path coverage floor returns different verdicts for the same code. `hinterland.py` 503-504 - the
woodland shrink ladder - came out covered in some full runs and uncovered in others, with nothing changed
between them. Feature 147 parked those two lines so the speedup could land; this feature removes the park by
fixing the cause.

**WHAT "THE FLAKINESS" COVERS, since the GM's wording is plural.** They wrote "the flaky tests" and "even
with the four being somewhat flaky". Read in context, "the four" is a dictation of "the floor" - the
preceding sentence is "even with the flaky floor" - and the plural "tests" is loose: checked against the
tree, feature 147 created exactly ONE park (the `hamlet_floor.PARKED` entry for `hinterland.py` 503-504) and
no test anywhere is marked flaky or skipped for flakiness. So the scope is that one symptom and the cause
behind it, and this paragraph exists so that reading is on the record rather than assumed.

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

## Review history

- **`spec-fidelity`, round 1 - CHANGES REQUIRED (3).** (1) SC-002 demanded five consecutive full runs, which
  contradicted FR-007's own reasoning ("re-running an intermittent failure proves nothing") and would have
  cost 12-20 minutes against `scripts/measure-hooks.sh`, a guard the GM installed the day before for exactly
  that waste. (2) FR-004 kept the `PARKED` machinery "as the general tool for a future case" - an unrequested
  policy call creating a standing way to excuse lines from a NON-NEGOTIABLE floor. (3) The GM's plural ("the
  flaky tests", "the four") was never accounted for, so the spec narrowed "the flakiness" to one symptom on
  the reader's trust. The review also noted FR-006 was a weaker bar than SC-004.
- **All three applied**, plus the FR-006 wording: repetition demoted from proof to evidence, `PARKED`'s
  survival moved to Decisions Recorded for the GM to confirm or reverse, and the scope reading written down
  with the evidence for it.

## Requirements *(mandatory)*

- **FR-001** The CAUSE must be established by measurement before a fix is written, and recorded - including
  the hypothesis above being disproved, if that is what happens. A fix that makes the symptom go away without
  a named cause is not acceptable here: the symptom is intermittent, so "it passed twice" proves nothing.
- **FR-002** The floor must return the SAME verdict for the same code, warm and cold, with the number of runs
  actually taken recorded. Repetition is EVIDENCE, not the proof: the proof is the named cause (SC-001) and
  the mechanism-level regression test (FR-007). This feature does not buy confidence by re-running an
  intermittent failure, which is the thing FR-007 exists to say.
- **FR-003** The park added by 147 must be REMOVED - both the `# pragma: no cover` in `hinterland.py` and the
  `PARKED` entry - and the floor must hold at 100% without it. The park is the debt this feature repays.
- **FR-005** If the cause is stored-coverage staleness, the fix must make a stale replay IMPOSSIBLE rather
  than unlikely - an entry whose stored coverage cannot be trusted must be re-executed, not replayed.
- **FR-006** No loss of the feature-147 speedup: the full sweep must be no slower than the figure feature 147
  landed (the same bar as SC-004 - "not back to 234 s" would have been a far weaker promise than the GM's
  "I would like to keep the speed up").
- **FR-007** Whatever the cause, a REGRESSION TEST must fail if it returns - a test of the mechanism, not a
  re-run of the suite, since re-running an intermittent failure proves nothing.

## Decisions Recorded

**The `PARKED` machinery survives this feature, empty.** It is NOT a requirement, because the GM did not ask
for one either way: they authorized a skip for ONE case, for one stated reason - so another session would not
duplicate the work - while the fix was pending. Keeping a standing, general way to excuse lines from a
NON-NEGOTIABLE 100% floor is a policy call, so it is recorded here for the GM to confirm or reverse rather
than asserted as a requirement. The argument for keeping it: the next case of this kind will otherwise be
parked by an ad-hoc pragma with no announcement and no owner, which is what feature 147 would have had to do.
The argument against: an unused excuse mechanism is an invitation. Its test stands either way, because no
requirement here asks to change it.

## Success Criteria *(mandatory)*

- **SC-001** The cause is named in writing, with the measurement that establishes it.
- **SC-002** The floor gives the same verdict on consecutive full runs of unchanged code, within the standing
  measurement budget - `scripts/measure-hooks.sh` prices a full run at 2.5-4 minutes and blocks a third in a
  row, so the sanctioned before/after pair is the bar, NOT a fixed count of re-runs. A number here would have
  cost 12-20 minutes of re-running and a bypass of a guard the GM installed on 2026-08-28, to demonstrate
  something SC-005 demonstrates properly.
- **SC-003** `PARKED` is empty and `hinterland.py` carries no coverage pragma for these lines.
- **SC-004** The full sweep is no slower than the figure feature 147 landed.
- **SC-005** A regression test exists for the named cause and is proved to fail without the fix.

## Assumptions

- The GM takes no acceptance task; the feature lands when it is done (their instruction).
- "The same verdict" means the floor's pass/fail and its missing-line list, not the wall time.
