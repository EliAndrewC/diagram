# Feature 287 - every finished-map rule guaranteed by its placer

**Feature Branch**: none (main, in the clone `diagram-performance`)
**Created**: 2026-09-29
**Status**: Accepted - FAITHFUL at round 4 (2026-09-29)
**Request**: [`request.md`](request.md) - the GM's words verbatim: the five rules feature 284 found, "guaranteed by the
placement algorithm rather than just happening to work on particular seeds", and "if there are literally any other things
of this nature where our placement algorithm is not guaranteeing correct behavior, then we should include those along with
this feature as well."
**Predecessors**: 166 (the check battery retired: a rule about a map became a test of the placer that makes it, and a
property no single placer owned became a seed test on a cached roll - the tests this feature converts), 284 (the five).

## Summary

Feature 166 left one kind of rule outside the placers: a property of a FINISHED map, asserted by a test that rolls or reads a
map and checks the result. Such a rule holds on the seeds the tests roll; nothing stops the next seed, or any change that
moves a map, from breaking it - feature 284's field-search lever moved the pool's maps within every tolerance and five of
these rules broke. And the generator still checks one rule on the finished map itself and re-rolls on it (a stranded
farmhouse), which is a check, not a guarantee. The GM: *"make it so that it is impossible for those things to happen ...
guaranteed by the placement algorithm rather than just happening to work on particular seeds"*, with *"literally any other
things of this nature"* included, and the tests no longer needed afterwards retired.

The scope, from three sources (research R1-R3): every placement rule asserted on a finished map (a census of the tests: 118
rules); every placer fallback that knowingly emits a compromise of a recorded rule (a census of the engine's code); and every
violation already on record but excused (a test's skip list, a strict xfail, a future-work entry). Research R1 counts
118 placement rules asserted on finished maps; R2 finds 31 placer fallbacks that break a stated rule when their branch runs
(of 150 read); R3 finds 58 violations on record and not fixed (of 116 items read). They overlap, and the plan joins them by
owning placer. Each becomes a guarantee
made where the placer decides - so no roll of any spec can produce the violation - with a unit test of that placer; and the
finished-map tests it makes unnecessary are retired.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - No roll can break a placement rule (Priority: P1)

**Why this priority**: the whole request.

**Independent Test**: each rule's owning placer, driven on constructed inputs built to provoke the violation, refuses,
repairs or never emits it.

**Acceptance Scenarios**:

1. **Given** any rule in scope, **When** its owning placer is given inputs that would have produced a violation, **Then**
   the placer's output does not violate the rule, and a unit test of the placer shows it.
2. **Given** the pool and cohort seeds 1-48 rolled under perturbations that move every map (feature 284's withdrawn A*
   router and field-search lever, applied as probes), **When** every placement rule is checked, **Then** none fails, and no
   roll needed a re-roll to get there.

### User Story 2 - What a later stage does cannot undo an earlier guarantee (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a stage that rewrites what an earlier placer drew (the census names `stage_crossings` / `square_crossings`,
   which rewrite the lanes after the web and the woods; `round_the_brooks`, which reshapes the brook after the woods),
   **When** it runs, **Then** every guarantee the earlier placers made about what it rewrites still holds.

### User Story 3 - The tests cost what the guarantees need (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a finished-map test whose rule a placer now guarantees with its own unit test, **When** the feature lands,
   **Then** the finished-map test is retired, and the gate no longer rolls or reads a map for it.

### Edge Cases

- A placer with no legal candidate left does not emit a violating one. What it does instead is decided per rule and
  recorded (FR-005).
- A rule several placers produce jointly: one owner (the last placer whose decision can break it) holds the guarantee, and
  no placer after it can break it (FR-002).
- Hand-drawn geometry (the legacy pool; a hand Mode A sheet's buildings) was made by no placer and is out of scope. What a
  placer puts ON a hand sheet - the captions the one caption placer seats (feature 266) - is in scope. The rows this puts
  out: the hand-drawing half of `tests/test_mode_a_sheets.py::test_every_mode_a_sheet_passes_its_checks` (the two generated
  sheets are in).
- A tier no live generator produces (the town and city tiers, whose maps are frozen legacy exhibits - the GM's 2026-08-16
  freeze, `migration-plan.md`): code only those tiers run places nothing that ships, so its fallbacks are recorded in the
  census but not converted (research R2 names the one: `wards.py:_ward_ends_on_wall`). The line is drawn by code path, not
  module: a city module a live generator calls (`settlement/city/bridges.py`, from every hamlet) is in scope.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 Every rule in scope becomes a guarantee of its owner.** The scope is research R1's placement rules (every
  map-rule row - the 118, not only those the census read as unguarded, since a reader's `yes` is a judgment and one was
  wrong: the copse's bank), R2's placer fallbacks and R3's excused violations, and it names these five explicitly, whatever
  any census verdict: `test_a_bund_does_not_build_a_flight_of_steps`, `test_no_three_woodland_parcels_stand_in_a_ruled_row`,
  `test_every_copse_clump_stands_on_the_bank_of_a_house_within_reach`,
  `test_no_brook_segment_lies_on_a_screen_axis_but_the_tap_run`, `test_every_pool_hamlet_has_its_belt_on_the_regional_northwest`.
  A row that bundles several rules is one guarantee and one test per rule. The owning placer is changed so its output cannot
  violate the rule: it refuses the violating candidate and takes the next, repairs the result, or constrains the candidates
  so no violating one is offered.
- **FR-002 The guarantee is made where the placer decides.** A check of a finished manifest or SVG that triggers a
  whole-map re-roll, a raise or a retry does not count: `generate`'s re-roll loop on `farmhouses_reach_a_way` is replaced by
  the seat and way placers guaranteeing that every seated farmhouse is reached, and no census sketch that says "feed it to the
  driver's re-roll" or "check the finished map and raise" is taken as written. A stage that rewrites what an earlier placer
  drew re-applies the earlier guarantees to what it rewrites, or moves before the placer whose guarantee it could break.
- **FR-003 The placer and its test read one predicate.** Where a placer and its test measure different things (the wells'
  spacing, the eave gap on a turned house, the field pond's inset, the flooded tint's ring, the woodland's dry-ground sample,
  the drip lines, and any other found in the work), the rule is written once and both read it; where they disagree, the
  research or the GM's ruling behind the rule decides which reading is right.
- **FR-004 Each rule has a unit test of its owning placer** on constructed inputs, including the input that would have
  produced the violation, proving the placer refuses, repairs or cannot emit it - every rule in scope, the 118 included.
- **FR-005 No fallback emits a violation.** Where a placer runs out of legal candidates, what it does is decided per rule
  and recorded at the point of change and in the Decisions table - never "keep the least-bad violating one". Every such
  fallback R2 finds is converted.
- **FR-006 Excused violations end.** Each test-side carve-out that excuses a known violation (the `ACREAGE_SHORT` seeds, the
  seed-43 strict xfail, and any R3 finds) is removed and the test asserts the rule on those seeds; a carve-out that is part
  of the rule itself (the polder's cell band) stays.
- **FR-007 Every test the refactor makes unnecessary is retired** (the GM, 2026-09-29: *"retire any unit tests which are no
  longer necessary after this refactor, especially ones which impact performance without any longer being needed to
  guarantee correctness"*). That is any test, not only the finished-map ones: a finished-map test whose rule its placer now
  guarantees with its own unit test; a test of the re-roll loop FR-002 removes; a test of a fallback branch FR-005 converts;
  the excuse lists FR-006 removes - and the rolls, roster rows and fixtures only they needed. A test is kept for exactly one
  reason: it guards correctness that no placer unit test covers, and the record names that correctness. Keeping a test as a
  witness, or out of caution, is not a reason. The end-to-end proof is SC-003's sweep, run at acceptance.
- **FR-008 The census is taken again at the end**, over the same selection by a re-runnable script (`census_select.py`) and
  the same judgment, and every placement rule reads guaranteed - its placer's mechanism cited.
- **FR-009 Maps may move.** A guarantee that changes what a placer emits moves maps, within the GM's standing ruling (map
  changes within the rules are wanted). Every moved pool map is regenerated, keeps its households, forms and kinds, and
  passes every rule; its before and after is recorded in the research.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-005, FR-008): the closing census reads guaranteed on every placement rule, each with its placer's
  mechanism named; none partial, none unguarded; every R2 fallback converted; every R3 excuse removed.
- **SC-002** (FR-003, FR-004): every rule's placer and its test read one predicate, and every rule in scope has a unit test of its owning placer on constructed inputs that include a
  violating case.
- **SC-003** (FR-001, FR-002, US1 scenario 2): the pool and cohort seeds 1-48, rolled plain and again with feature 284's A* router and
  field-search lever applied as probes (neither ships), pass every placement rule, and no roll re-rolls.
- **SC-004** (FR-006, FR-009): `make done` green; every live pool map regenerates and passes every rule; `make cohort
  N=24` shows zero failing seeds on any placement rule (not merely none newly failing); every moved map's before and after
  is in the research.
- **SC-005** (FR-007): every retired test is listed with the cost the gate no longer pays for it (its measured seconds, and
  the rolls it alone required); every kept test that reads or rolls a finished map is listed with the correctness it guards
  that no placer unit test covers; and the gate's test phase is measured before and after (`make audit`) and is not slower.
- **SC-006** (spec-wide): under constitution VI, `make perf-report` against the feature's start bookend; an increase owes its record.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Every test the refactor makes unnecessary is retired, kept only for correctness no placer test covers; SC-003's sweep is the end-to-end proof at acceptance | map drawing convention (a test policy) | the GM, 2026-09-29 | FR-007 |
| Per-rule fallbacks when a placer runs out of legal candidates | decided per rule in the plan | FR-005 | each point of change |
| The town and city tiers' fallbacks recorded, not converted: no live generator produces those tiers | map drawing convention (scope) | Edge Cases | research R2 |

## Assumptions

- The census's owner for each rule is a starting point; where the work finds the rule decided elsewhere, the guarantee goes
  where the decision is, and the research records the correction.

## Review history

- Round 1 (spec-fidelity, 2026-09-29): CHANGES REQUIRED - one of the five named outside the scope (the copse, read `yes`);
  the 31 `yes` verdicts unchecked; the census read only tests (not the placers' fallbacks nor the violations on record); a
  finished-map check plus re-roll allowed as a guarantee; SC-004 allowed existing failures; hand geometry contradictory.
  Addressed: the five named in FR-001, all 118 tested, research R2 and R3, FR-002 against the re-roll, zero failing seeds,
  the hand line drawn; and the GM's second message (retire what is no longer needed) taken into FR-007.
- Round 2 (spec-fidelity, 2026-09-29): CHANGES REQUIRED - the town/city carve-out applied by module (bridges.py, which every
  hamlet runs, missed; the city-only wards row in scope); FR-007 and SC-005 narrower than the GM's retirement wording.
  Addressed.
- Round 3 (spec-fidelity-verify, 2026-09-29): CHANGES REQUIRED - scope-by-owner.json stale; R2's method missing city/moat.py.
  Addressed (scope_join.py).
- Round 4 (spec-fidelity-verify, 2026-09-29): FAITHFUL.
