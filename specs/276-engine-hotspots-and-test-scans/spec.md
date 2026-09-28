# Feature 276 - engine hotspots and test scans

**Feature Branch**: none (main, in the clone `diagram-inashiro`)
**Created**: 2026-09-28
**Status**: Draft
**Request**: [`request.md`](request.md) - the GM's words verbatim, and the analysis they said yes to.
**Predecessors**: 218 (efficient overlap checks: the index-once doctrine, `dev/performance.md`), 220 (the field
fitted once), 222-226 (render and scatter levers), this session's quick-suite passes (gate-stamp per-file
lookups, `_hookdeps` memoization, the tooling tree out of quick).

## Summary

The GM asked which of the slow tests are slow because the TEST is wasteful and which because an engine
ALGORITHM is - "we're frankly just not dealing with data that's that big" - and asked that the root
inefficiencies be fixed before the city tier, where thousands of inhabitants would make them "a nightmare".
The profiles split them cleanly. This feature fixes both halves: the test-side rescans (one parse, one
scan, shared), and the three engine hotspots - homestead placement's generate-and-test search, comb-field
seam closing's per-polygon geometry churn, and the track stage's per-candidate rescans of static geometry.
Maps may shift (the GM, this session: "it is completely okay for things to shift a bit as long as the
underlying reality of what these settlements are generally like stays the same"); every rule the gate
enforces must still hold, and no test may check less than it does today.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The slow tests are fast because they stop redoing work (Priority: P1)

The GM runs `make quick ALL=1` or the gate. The tests that re-parse the whole engine or re-scan the whole
research record per case now parse and scan once and share the result, and each asserts exactly what it
asserted before.

**Why this priority**: the cheapest, safest half, and it removes most of the test-side seconds.

**Independent Test**: time each named test alone before and after; run each against a planted violation
(the same kind it exists to catch) and see it fail.

**Acceptance Scenarios**:

1. **Given** the four AST-scanning tests, **When** each runs alone, **Then** it finishes well under a second
   and still fails on a planted offender of the kind it guards.
2. **Given** the record tests, **When** each runs alone, **Then** it finishes well under a second and still
   fails on a planted broken link, unused glossary term, retired rule-file name and converted `.md` token.

---

### User Story 2 - A house is seated without testing a hundred wrong places first (Priority: P1)

A settlement's homesteads are placed by asking what ground is free, not by trying spiral offsets one after
another and rebuilding the whole bundle for each. A hamlet's homestead stage drops sharply; a much denser
synthetic settlement shows the cost growing roughly in proportion to the houses, not faster.

**Why this priority**: the GM's city concern - this is the loop whose rejections grow with density.

**Independent Test**: the rescue-rounds test and a dense synthetic placement benchmark, before and after:
time, candidates fully tested, and the placement rules all holding.

**Acceptance Scenarios**:

1. **Given** the rescue-rounds scenario, **When** the homestead stage runs, **Then** it is at least 5x faster
   and fully tests at least 10x fewer candidate seats, and every placement rule its tests assert still holds.
2. **Given** a synthetic site with several hundred houses to seat, **When** placement runs at two densities,
   **Then** the time per house stays within a small constant factor as the count grows (measured, recorded).

---

### User Story 3 - A comb field closes its seams in a fraction of the time (Priority: P2)

Closing the seams of a comb field does each geometric operation once, batched over the pieces, and a long
thin pocket can no longer explode into a thousand grid cells.

**Why this priority**: ~80% of every field build and most of a hamlet's field stage; linear in paddies with
a large constant, so it matters at village and town scale.

**Independent Test**: time `close_seams` in the field builds the tests use and in the pool hamlets' field
stage, before and after; every field test and gate rule still passes.

**Acceptance Scenarios**:

1. **Given** the comb builds the waterfields tests use, **When** a field is built, **Then** seam closing is
   at least 2x faster and every paddy, bund and seam rule still holds.
2. **Given** the seams test map whose pockets cut ~1,400 cells each, **When** it closes, **Then** the cell
   count is bounded by the pocket's own extent, not its bounding box, and the test's assertion still holds.

---

### User Story 4 - A track is routed without re-scanning the map per candidate (Priority: P3)

The track stage's path checks read the static water and crop geometry from an index built once per stage.

**Why this priority**: a few tenths of a second on a hamlet, but paths x obstacles at city scale.

**Independent Test**: profile the track stage on the reference hamlet before and after.

**Acceptance Scenarios**:

1. **Given** the reference hamlet, **When** the track stage runs, **Then** the path checks' share of the stage
   is at least halved and the ways drawn obey every crossing and clearance rule.

### Edge Cases

- A pocket that is one long diagonal sliver across a big field (the pathological grid).
- A site so full that no seat fits: placement must still report the failure the way it does today (the
  rescue rounds, then the recorded shortfall), not loop or place illegally.
- A module or record page that changes during a test session (a cache keyed on content, not name).
- Nucleated and dispersed homestead forms, and the headman's larger house, all through the new placement path.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 One parse of the engine per test process.** The tests that read every engine module's syntax tree
  (at least `tests/test_memory.py`, `tests/hamletgen/test_driver.py`, `tests/test_package_surfaces.py`,
  `tests/settlement/test_water_ways.py`) read it from one shared, content-keyed parse per worker, and skip a
  module whose text cannot contain what they look for only where that skip is provably a superset test. Each
  keeps its assertion and is proved to fail on a planted offender.
- **FR-002 One scan of the record per test process.** The record tests (`tests/interactive/test_record.py`,
  `test_record_format.py`) build what they look up - link targets, the corpus's words, the names to find in
  tracked files - once, and answer each case from it. Each keeps its assertion and is proved to fail on a
  planted violation.
- **FR-003 Homestead seats come from the free ground.** Homestead placement (dispersed and nucleated, the
  spiral search, the slides and the rescue rounds) asks an index of the ground already taken - built once
  per stage and updated as each bundle lands - for candidate seats, instead of running the full fit test at
  every spiral offset. The bundle's geometry for a given house size, form and side is built once and moved,
  not rebuilt per candidate. The full fit test still DECIDES every seat that is taken (the index prunes, it
  never decides - `dev/performance.md`), so every rule the placement tests and the gate assert still holds.
- **FR-004 Seam closing does each operation once, batched.** `close_seams` and its steps (`_plant`,
  `_despike`, `_absorb`, `_unjog`, `_shed_necks`, `_repair_crossing_rings`, `_visible_parts`) compute each
  geometric result once (no repeated identical operation on the same piece), run per-piece operations over
  arrays where the geometry library supports it, and bound `_plant`'s grid by the pocket's extent in the
  field frame, so a long thin pocket yields cells in proportion to its area.
- **FR-005 Track path checks read an index.** `path_violations` and the checks it calls answer from the
  static water, crop and pond geometry indexed once per track stage, not from a scan of every segment and
  polygon per candidate path.
- **FR-006 Every rule still holds; maps may move.** After FR-003 to FR-005 every live pool map regenerates,
  `make done` is green at the 100% floor, and every gate rule passes. A map that moved is named in research
  with what moved; byte-identity is not required (the GM, request.md).
- **FR-007 Measured, before and after.** Research records, from the same machine and commands: each named
  test's time; the homestead stage (time, candidates fully tested) on the rescue-rounds scenario and a dense
  synthetic scenario at two sizes; `close_seams` time per field build; the track stage's path-check share;
  each pool hamlet's stage profile; `make quick ALL=1` and `make done` wall time. A performance increase
  anywhere is reported under constitution VI's bands like any other.
- **FR-008 The practice is written down.** `dev/performance.md` gains the two shapes this feature found in the
  engine - a generate-and-test seat search (answer from the free ground) and a chain of per-piece geometry
  calls (batch it, never compute the same result twice) - and the test-side shape (parse or scan once per
  process), each with its measurement.

### Key Entities

- **Free-ground index**: what ground a new homestead may not take, kept current as bundles land; asked for
  seats near a target.
- **Bundle template**: a homestead bundle's geometry for one house size, form and garden side, relative to the
  house center, moved to each candidate.
- **Shared parse / scan caches** (tests): one syntax tree per engine module and one lookup table per record
  question, per test process, keyed on content.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Each of the four AST-scanning tests and each named record test runs in under 0.5 s alone (from
  2.3-6.6 s and 2.8-4.4 s), and each fails on its planted violation.
- **SC-002**: The rescue-rounds homestead stage is at least 5x faster (from 6.6 s under the profiler, measured
  unprofiled before and after) with at least 10x fewer candidates fully tested.
- **SC-003**: On a dense synthetic scenario, doubling the houses to seat at most roughly doubles placement
  time (per-house time within 1.5x across the two sizes).
- **SC-004**: Seam closing per comb build is at least 2x faster; the seams test's pathological map produces
  cells bounded by its pockets' extent.
- **SC-005**: The track stage's path-check share on the reference hamlet is at least halved.
- **SC-006**: Every live pool map regenerates with every gate rule passing, and `make done` is green at 100%.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

This feature changes no rule, size, glyph or density: every map is drawn by the same rules, and where a seat,
a seam or a track lands differently it is because the same rules were asked more efficiently.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Homestead seats are chosen by the same fit rules from a pruned candidate set, so a house may land at a different legal seat than before | map drawing convention (no rule changed; the placement order is an engine property, not a finding) | the GM: shifts are fine "as long as the underlying reality of what these settlements are generally like stays the same" | point of change in the placer; research R-section naming each moved map |
| Seam closing's grid is bounded by the pocket's extent; results may differ by sub-plot amounts where batched geometry rounds differently | map drawing convention | same ruling | point of change in `waterfields/seams`; research |

## Assumptions

- Shapely 2's array operations are installed (the engine already imports shapely 2 APIs).
- "No loss of fidelity" means every test keeps asserting the same property and still fails on its violation,
  and every gate rule holds on every live map - not that output is byte-identical.
- The dense synthetic placement scenario is a measurement harness (research), plus at most a bounded test;
  it is not a new pool map.
- Every task is `research: rendering` - performance of existing rules, no new physical claim.
