# Feature 287 - every finished-map rule guaranteed by its placer

**Feature Branch**: none (main, in the clone `diagram-performance`)
**Created**: 2026-09-29
**Status**: Draft
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
these rules broke. A census of every test that reads a generated map (research R1: 195 tests, five readers) found 118
placement rules asserted that way: the placer already makes a violation impossible for 31; for 53 it guards some cases and
not others; for 34 nothing prevents a violation. This feature makes each of those 87 a guarantee of the placer that decides
it - the five of 284 among them - so that no roll of any spec can produce the violation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - No roll can break a placement rule (Priority: P1)

**Why this priority**: the whole request.

**Independent Test**: each rule's owning placer, driven on constructed inputs built to provoke the violation, refuses,
repairs or never emits it.

**Acceptance Scenarios**:

1. **Given** any of the 87 rules, **When** its owning placer is given inputs that would have produced a violation, **Then**
   the placer's output does not violate the rule, and a unit test of the placer shows it.
2. **Given** the pool and a cohort rolled under perturbations that move every map (feature 284's withdrawn A* router and
   field-search lever, applied as probes), **When** every finished-map rule is checked, **Then** none fails.

### User Story 2 - What a later stage does cannot undo an earlier guarantee (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a stage that rewrites what an earlier placer drew (the census names `stage_crossings` / `square_crossings`,
   which rewrite the lanes after the web and the woods), **When** it runs, **Then** every guarantee the earlier placers
   made about what it rewrites still holds.

### Edge Cases

- A placer that has no legal candidate left: it does not emit a violating one. What it does instead - drop the feature, draw
  it smaller, or place it by a stated fallback - is decided per rule and recorded (FR-005).
- A rule that is several placers' joint result: one owner (the last placer whose decision can break it) holds the guarantee,
  and the earlier ones do not break it after the owner has run.
- A hand-drawn map (the legacy pool, a hand Mode A sheet): no placer made it, so no placer can guarantee it; only the
  generated sheets are in scope (research R1's Mode A row).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 Every rule in research R1's table becomes a guarantee of its owner.** For each of the 87 rows, the owning placer
  (or, where the census names several, the last whose decision can break the rule) is changed so that its output cannot
  violate the rule: it refuses the violating candidate and takes the next, repairs the result, or constrains the candidate
  set so no violating candidate is offered. A rule found `partial` is completed for the cases the census found unguarded.
- **FR-002 A later stage cannot undo a guarantee.** A stage that rewrites what an earlier placer drew either re-applies the
  earlier guarantees to what it rewrites, or is moved before the placer whose guarantee it could break.
- **FR-003 The placer and its test read one predicate.** Where the census found a placer and its test measuring different
  things (the wells' spacing, the eave gap on a turned house, the field pond's inset, the flooded tint's ring, and any other
  found in the work), the rule is written once and both read it; where they disagree, the research or the GM's ruling behind
  the rule decides which reading is right.
- **FR-004 Each guarantee has a unit test on constructed inputs**, including the input that would have produced the
  violation, proving the placer refuses, repairs or cannot emit it (the engine's rule since 166: a rule about a map is a test
  of the placer that makes it).
- **FR-005 No fallback emits a violation.** Where a placer runs out of legal candidates, what it does is decided per rule and
  recorded at the point of change and in the Decisions table - never "emit the least-bad violating one", which the census
  found in several placers (the sink's least-bad off-map route among them).
- **FR-006 The finished-map tests stay, as end-to-end witnesses.** Each of the 118 keeps its test; after this feature a
  failure of one means a placer's guarantee is broken, not that a seed was unlucky.
- **FR-007 The census is taken again at the end** over the same tests plus any added, by the same method, and every map-rule
  reads `yes` - its placer's mechanism cited.
- **FR-008 Maps may move.** A guarantee that changes what a placer emits moves maps; that is within the GM's standing ruling
  (map changes within the rules are wanted). Every moved pool map is regenerated, keeps its households, forms and kinds,
  and passes every rule; its before and after is recorded in the research.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-007): the closing census reads `yes` on every map-rule test (118, and any added), each with its
  placer's mechanism named; 0 `partial`, 0 `no`.
- **SC-002** (FR-004): every one of the 87 rules has a unit test of its owning placer on constructed inputs that include a
  violating case.
- **SC-003** (US1 scenario 2): the pool and cohort seeds 1-48 rolled with feature 284's A* router and field-search lever
  applied as probes (neither ships) pass every finished-map rule - the perturbation that broke five rules in 284 breaks none.
- **SC-004** (FR-008): `make done` green; every live pool map regenerates and passes every rule; `make cohort N=24` shows no
  newly failing seed against main; every moved map's before and after is in the research.
- **SC-005** (constitution VI): `make perf-report` against the feature's start bookend; an increase owes its record, as
  every feature's does.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| The finished-map tests stay as end-to-end witnesses beside the placer tests | map drawing convention (a test policy: both kinds of proof) | FR-006 | this spec |
| Per-rule fallbacks when a placer runs out of legal candidates | decided per rule in the plan | FR-005 | each point of change |

## Assumptions

- The census's owner for each rule is a starting point; where the work finds the rule decided elsewhere, the guarantee goes
  where the decision is, and the research records the correction.

## Review history

(none yet)
