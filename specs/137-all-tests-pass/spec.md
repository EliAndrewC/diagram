# Feature Specification: One Hundred Percent of the Tests Pass

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=137-all-tests-pass`)

**Created**: 2026-08-28

**Status**: round 1 returned three changes (the opening message to the tests session unrecorded; completion narrower than 100%; GM acceptance as a completion condition unrequested) - applied; round 2 pending

**Input**: [`gm-request.md`](gm-request.md), verbatim and unedited. That file is the authority for
this specification.

## The feature, in one sentence

Every expected failure pinned in the diagram test suite during the reference-hamlet period is
FIXED - the pins removed, the seeds green - so that the whole suite passes with no waiver, while
this session and the "Diagram tests" session (test efficiency) pull each other's work only at the
points each declares safe.

## Why this exists (the GM's words)

- *"Your goal ... is to get one hundred percent of those tests passing."*
- *"faster tests will make quicker iteration, which means that you will have an easier time"* -
  hence the pull of the efficiency session's safe work before the correctness work starts.
- *"you should pull in the changes which they communicate to you are safe ... I do not want that
  session to pull in fixes which you have made, which are not fully tested."*

## The inventory (what "those tests" are, measured 2026-08-27/28)

| pin | where | seeds and checks | when it broke (feature 133 bisect) |
|---|---|---|---|
| `TRIPWIRE_EXPECTED` | `tools/mapcheck.py` | 27: `lanes_bend_like_paths`, `lanes_clear_of_bamboo`; 33: `village_windbreak_is_continuous`; 37: `lanes_bend_like_paths`, `lanes_form_one_network`; 47: `fields_clear_of_road`, `lanes_form_one_network`, `lanes_reach_something`, `long_ditches_have_a_footbridge` | 27: two checks added in the period (T32, T49); 33: T10 (the belt's face); 37: T41's re-roll under T32's smoothing; 47: red since before the lock |
| `GATE_COHORT_EXPECTED` | `tests/gate/hamletgen/test_driver.py` | 42: `farmhouses_reach_a_way`; 43: `lanes_bend_like_paths`, `lanes_form_one_network`, `title_clear_of_features`; 44: `houses_clear_of_paddies` | measured at the T92 unlock |
| `COHORT_BASELINE` | `hamletgen/driver.py` (the 24-seed canonical cohort, the `cohort` target) | 22: `field_ringed`; 24: `paddy_bunds_clear_the_supply_channels` | pre-133 |

Anything else the first full measurement turns up (a FULL-only failure, a polder seed, a seed of
the 48-cohort audit) joins the inventory by a task, never silently.

## User Scenarios & Testing

### User Story 1 - the pins come out (Priority: P1)

**Acceptance**: **Given** the inventory above, **When** the feature is complete, **Then** every
row's checks pass on its seed under the current engine, the pin rows are DELETED (a pinned seed
that passes is a stale pin and fails the gate by design), and the unlocked gate, the tripwire
(`maps`) and the 24-seed `cohort` are green with no expected failure anywhere.

### User Story 2 - the two sessions pull each other safely (Priority: P1)

**Acceptance**: **Given** the "Diagram tests" session's clone, **When** it names a commit as safe,
**Then** this clone merges exactly up to that commit (after main), and never anything past it;
**Given** this session has a tested set of fixes (a green gate on them), **Then** it names that
commit to the other session, and never an untested one. Every handoff in both directions is a
line in this feature's `handoffs.md` (who, sha, what it was tested with).

### User Story 3 - no fix is a rotation (Priority: P1)

**Acceptance**: a fix that closes one seed and opens another is not a fix (constitution XIII, the
belt-face lesson of 133 T91): each fix is measured on the full tripwire, the gate cohort and the
24-seed cohort before it is kept.

### Edge Cases

- A pinned check turns out to be a WRONG RULE (the check, not the map, is the defect): the fix is
  to the check, with its research recorded, and the seed goes green that way - the pin still comes
  out.
- The efficiency session changes what a test rolls (subsets, markers): the inventory is re-measured
  after each safe pull, and a seed that disappears from the gate's roll is still fixed (the
  inventory is about the maps, not the test selection).
- A seed that cannot be fixed without an architectural change: deferred as constitution XIV
  requires (measurement, mechanism, sketch) and put before the GM - never re-pinned quietly.

## Requirements

- **FR-000** (the request's first sentence): before any pull, message the "Diagram tests" session
  that this session is merging its changes into this clone and is taking on fixing the expected
  failures, and ask it to name a commit it considers safe (or expects to be safe); record the
  message in `handoffs.md`. SENT 2026-08-28 04:0xZ (msg 7b11f701), before this spec was reviewed.
- **FR-001**: Before any correctness work, pull main and then the efficiency session's clone up to
  the commit it names as safe; record it in `handoffs.md`.
- **FR-002**: Each inventory row is a task with its own measurement (the failing check's message on
  that seed, the mechanism, the fix), fixed in the engine or in the check with the research
  recorded where the rule lives, and verified on the whole tripwire + gate cohort + 24-seed cohort
  (no rotation).
- **FR-003**: A pin row is removed in the same commit as the fix that makes it stale.
- **FR-004**: Handoffs to the efficiency session are made only on a commit with a green gate and
  are recorded; pulls from it are made only on commits it names, and are recorded.
- **FR-005**: The feature is complete when ONE HUNDRED PERCENT of the diagram tests pass with no
  expected-failure pin and no waiver of a failing check remaining anywhere: the three tables above
  empty (today's measured instance), plus every row the first full measurement adds under the
  inventory note - including a FULL-sweep-only failure or a 48-cohort-audit seed, should either
  carry one - each proven by the run that owns it (the unlocked gate; the tripwire; the 24-seed
  cohort; the FULL sweep and the 48-cohort audit if they hold a row). The result is REPORTED to the
  GM on completion; acceptance is not a condition of it (the GM: "a specific background session").

## Success Criteria

- **SC-001**: no expected-failure pin or waiver of a failing check remains anywhere in the suite
  or its tooling - the three tables empty and any row the measurement added - and the runs prove
  it (a pinned-but-passing seed would fail; an unpinned failing seed would fail).
- **SC-002**: the tripwire reports every seed `ok`; the cohort reports 24 of 24.
- **SC-003**: `handoffs.md` has a line per pull and per handoff, each naming a sha and its test.

## Decisions Recorded

None yet - a fix that changes what a map draws records its class (accurate / deviation / guess)
in its task and in the research entry it cites, per constitution XII.

## Assumptions

- The "Diagram tests" session was messaged first (FR-000). If it does not reply, this session
  pulls nothing from it and works the inventory from main alone, re-asking at each handoff; a
  named safe commit is merged whenever it arrives.
- The GM's waivers of 2026-08-27 stay in force for the pins until each is fixed here; no other
  session touches them (the GM: "a specific background session").
