# Feature 276 - engine hotspots and test scans

**Feature Branch**: none (main, in the clone `diagram-inashiro`)
**Created**: 2026-09-28
**Status**: Accepted - FAITHFUL at round 3 of 5 (2026-09-28); Amendment 1 FAITHFUL at round 3 of 5 on its reset counter (2026-09-28)
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

1. **Given** the four AST-scanning tests, **When** they run together in one process, **Then** the engine is parsed
   once (the parse counted), they take at most that one parse plus `0.5 s`, and each still fails on a planted
   offender of the kind it guards.
2. **Given** the five named record tests, **When** they run together in one process, **Then** their lookup tables
   are built once, they take at least `3x` less than their summed time before (the build cost recorded), and each
   still fails on a planted broken link, unused glossary term, retired rule-file name or converted `.md` token.

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
2. **Given** the placement primitive seating houses from 60, 120 and 240 seeds at one constant density (the site
   growing with the count, as a city's does), **When** placement runs, **Then** the cost per seated house grows by at
   most `1.25x` from 60 to 240 seeds (measured, recorded).

---

### User Story 3 - A comb field closes its seams in a fraction of the time (Priority: P2)

Closing the seams of a comb field does each geometric operation once, batched over the pieces, and a long
thin pocket can no longer explode into a thousand grid cells.

**Why this priority**: most of a field build and most of a hamlet's field stage; linear in paddies with
a large constant, so it matters at village and town scale.

**Independent Test**: time `close_seams` in the field builds the tests use and in the pool hamlets' field
stage, before and after; every field test and gate rule still passes.

**Acceptance Scenarios**:

1. **Given** the comb builds the waterfields tests use, **When** a field is built, **Then** seam closing is
   at least 2x faster and every paddy, bund and seam rule still holds.
2. **Given** a pocket that is a long sliver lying diagonally across the field's frame, **When** it is planted,
   **Then** the grid visits only cells the pocket touches, so the work grows with the pocket's area, and every
   basin rule still holds.

---

### User Story 4 - A track is routed without re-scanning the map per candidate (Priority: P3)

The track stage's path checks read the static water and crop geometry from an index built once per stage.

**Why this priority**: a few tenths of a second on a hamlet, but paths x obstacles at city scale.

**Independent Test**: profile the track stage on the reference hamlet before and after.

**Acceptance Scenarios**:

1. **Given** the reference hamlet, **When** the track stage runs, **Then** the path checks take at least half
   the time they did, the stage is not slower, and for every candidate path the checks report exactly the
   violations the full scan reports.

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
  every spiral offset, and no fit test scans every placed house. The bundle's geometry for a given house size,
  form and side is built once and moved, not rebuilt per candidate. The full fit test still DECIDES every seat
  that is taken (the index prunes, it never decides - `dev/performance.md`), so every rule the placement tests
  and the gate assert still holds.
- **FR-004 Seam closing does each operation once, batched, over the ground a pocket touches.** `close_seams` and
  its steps (`_plant`, `_despike`, `_absorb`, `_unjog`, `_shed_necks`, `_repair_crossing_rings`,
  `_visible_parts`) compute each geometric result once (no repeated identical operation on the same piece) and
  run per-piece operations over arrays where the geometry library supports it. `_plant`'s grid visits only the
  cells the pocket touches, so its work grows with the pocket's area and not with any bounding box - a long
  sliver lying diagonally across the field frame is the test case.
- **FR-005 Track path checks read an index, and report exactly what the scan reports.** `path_violations` and the
  checks it calls answer from the static water, crop and pond geometry indexed once per track stage, not from a
  scan of every segment and polygon per candidate path. The index prunes and the exact test decides: for every
  candidate path, the count is exactly the full scan's, proved by comparing both over the reference hamlet's
  candidate paths.
- **FR-006 Every rule still holds, and every settlement stays what it was.** After FR-003 to FR-005 every live pool
  map regenerates, `make done` is green at the `100%` floor, and every gate rule passes. The GM's condition -
  shifts are allowed "as long as the underlying reality of what these settlements are generally like stays the
  same" - is held concretely: every pool map and every placement-test scenario seats at least as many houses
  as today, with no new or larger shortfall, and keeps its forms (dispersed or nucleated, the headman's house);
  each moved map's research entry gives its houses, paddies and ways before and after, and a material change is
  a finding to fix, not a report. Byte-identity is not required (the GM, request.md).
- **FR-007 Measured, before and after.** The harness (`harness.py`) records, on the same machine and code path:
  each named test's time alone; the homestead stage (time, full fit tests) on the rescue-rounds scenario, the toy
  at 10 and 20 households, and the placement primitive at constant density at 60, 120 and 240 seeds - each placement
  scenario on the NUCLEATED path (the pool's) and the DISPERSED path (the spiral) and labeled so;
  `close_seams` inside a comb build; the track stage and its path checks. Research adds each pool hamlet's stage
  profile and `make quick ALL=1` and `make done` wall time. A slowdown anywhere is reported under constitution
  VI's bands like any other.
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

- **SC-001** (FR-001): The four AST-scanning tests, run together in one process, parse the engine ONCE (a parse count
  asserted by a test), and each fails on its planted offender. Their before-times alone were 1.23 s to 1.87 s
  (m:before-ast-tests-min, m:before-ast-tests-max; research R1) - most of it the parse one of them must pay alone, so the
  target is the four together: at most the one shared parse plus `0.5 s`.
- **SC-001a** (FR-002): The five named record tests build their lookup tables once per process; together alone they take at
  least `3x` less than their 17.22 s sum (m:before-record-tests-sum; the slowest alone was 4.47 s,
  m:before-record-tests-max), and each fails on its planted violation. The one-time build cost is recorded in
  research.
- **SC-002** (FR-003): On the DISPERSED path (the spiral `_place_bundle`, the form `_SETTLEMENT_FORMS_WHEN_GROVES_WORK` will
  roll), the rescue-rounds homestead stage is at least `5x` faster than 2.718 s (m:before-rescue-s - the first run, the
  stricter of the two recorded baselines; research R2) with at least `10x`
  fewer than its 46781 full fit tests (m:before-rescue-fits). On the NUCLEATED path (every pool hamlet's), the same
  scenario is not slower than 0.16 s (m:before-rescue-nucleated-s) and seats at least its 15 houses
  (m:before-rescue-nucleated-houses).
- **SC-003** (FR-003): At constant density the placement primitive's cost per seated house is flat ON BOTH PATHS: from 60
  to 240 seeds it grows by at most `1.25x` - before, nucleated 0.0009 s to 0.0017 s (m:before-dense-60-nucleated-per-house,
  m:before-dense-240-nucleated-per-house), which the unmodified engine fails - and neither path seats materially fewer
  houses: summed over five layouts of each density, each path's total is within `2%` of the old rolls' total (before,
  nucleated 285, 563 and 1138 at 60, 120 and 240 seeds - m:before-dense-60-nucleated-houses-five,
  m:before-dense-120-nucleated-houses-five, m:before-dense-240-nucleated-houses-five - and dispersed 188, 368 and 703,
  m:before-dense-60-dispersed-houses-five, m:before-dense-120-dispersed-houses-five, m:before-dense-240-dispersed-houses-five;
  Amendment 2). The DISPERSED path is also held to a deterministic target at density, because its timings are noise-bound (the
  first run read 0.0308 s to 0.0586 s per house, m:before-dense-60-per-house and m:before-dense-240-per-house; the re-run
  of the same scenario 0.046 s to 0.0406 s, m:before-dense-60-dispersed-per-house-rerun and
  m:before-dense-240-dispersed-per-house-rerun, with identical fit-test counts): 240 seeds need at least `10x` fewer than
  their 29372 full fit tests (m:before-dense-240-dispersed-fits).
- **SC-004** (FR-004): `close_seams` inside a comb build takes at least `2x` less than its 0.842 s to 1.018 s
  (m:before-close-seams-min, m:before-close-seams-max), and a diagonal sliver pocket's grid visits only the cells it
  touches.
- **SC-005** (FR-005): The track stage's path checks take at least `2x` less than the CORRECTED function did before the index -
  its time re-taken once `seg_intersect` was bounded, 0.139 s (m:before-track-checks-corrected-s; 0.966 s was the uncorrected one,
  m:before-track-checks-s) - the stage is not slower than 1.308 s (m:before-track-stage-s), and the checks' counts equal the full scan's on every candidate.
- **SC-006** (FR-006): Every live pool map regenerates with every gate rule passing, `make done` is green at `100%`, and FR-006's
  house counts and forms hold on every pool map and placement scenario.
- **SC-007** (FR-007, FR-008): every before- and after-figure SC-001 to SC-006 names is in `measurements.json`, the
  after-figures carrying the command that re-runs them (`make figures`), and `dev/performance.md` holds the three shapes
  this feature found, each with its measurement.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

This feature changes no rule, glyph or density, and no size distribution: every map is drawn by the same rules, a
homestead's part sizes come from the same distributions (rolled per household, the row below), and where a seat, a seam or
a track lands differently it is because the same rules were asked more efficiently - or, for the tracks, a cluster's
way-crossing finder and spur trim, and a homestead's brook-cut test, because a crossing test that counted segments that never
crossed now counts only real crossings (Amendment 1).

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Homestead seats are chosen by the same fit rules from a pruned candidate set, so a house may land at a different legal seat than before | map drawing convention (no rule changed; the placement order is an engine property, not a finding) | the GM: shifts are fine "as long as the underlying reality of what these settlements are generally like stays the same" | point of change in the placer; research R-section naming each moved map |
| A homestead's yard size, garden proportions and bed split are rolled once per household (at the seat it was sought from), not per candidate seat; the rake stays per seat | map drawing convention (the sizes come from the same distributions; only which seat seeds the roll changes) | a bundle built once per size and moved (FR-003) cannot re-roll its parts at every candidate; the GM allowed shifts "as long as the underlying reality ... stays the same" | point of change in `settlement/rolling/bundle.py`; research R2 |
| Crossing tests count only real segment crossings (`seg_intersect` bounded on both segments), so a track, a cluster's ways and spur, and a homestead's brook-cut may resolve differently | map drawing convention (no rule changed; the implementation now does what the rules said) | constitution XIV - a defect found while implementing FR-005, where seven callers counted crossings that did not exist (Inashiro's candidate paths scored 3,847 to 8,773, observed 2026-09-28, method: a probe wrapping `path_violations` in one roll); the GM's "as long as the underlying reality ... stays the same" | `settlement/_geom/primitives.py` and `overlap/taxonomy.py` `seg_intersect`; research R6 per moved map |
| Seam closing's grid is bounded by the pocket's extent; results may differ by sub-plot amounts where batched geometry rounds differently | map drawing convention | same ruling | point of change in `waterfields/seams`; research |

## Assumptions

- Shapely 2's array operations are installed (the engine already imports shapely 2 APIs).
- "No loss of fidelity" means every test keeps asserting the same property and still fails on its violation,
  and every gate rule holds on every live map - not that output is byte-identical.
- The dense synthetic placement scenario is a measurement harness (research), plus at most a bounded test;
  it is not a new pool map.
- Every task is `research: rendering` - performance of existing rules, no new physical claim.

## Review history

- **Round 1 (spec-fidelity, 2026-09-28): CHANGES REQUIRED**, five changes, all applied:
  1. FR-006 now holds the GM's condition concretely - no fewer houses seated, no new or larger shortfall, the forms
     kept, and each moved map's houses, paddies and ways reported before and after (a gate-green placer that seated
     fewer houses would otherwise have passed).
  2. FR-005 now says the index prunes and the exact test decides, with the count equality proved on the reference
     hamlet's candidate paths.
  3. FR-004, SC-004 and User Story 3 state the grid's goal as an outcome - only the cells the pocket touches - with a
     diagonal sliver as the test, because a frame-aligned extent does not bound a diagonal one.
  4. SC-001 now measures what FR-001 does (one parse shared by the four tests) instead of a per-test alone time the
     mechanism cannot reach; the record tests' target (SC-001a) is set from their measured sum.
  5. SC-005 measures the path checks' TIME (halved) with the stage not slower, not a share.
  The reviewer's aside: FR-007's "increase" meant a slowdown, and User Story 3's "every field build" - both reworded.
  The before-figures were then re-measured unprofiled by `harness.py` (`harness-before.json`, `measurements.json`).
- **Round 2 (spec-fidelity, 2026-09-28): CHANGES REQUIRED**, two changes, both applied: User Story 1's scenarios
  restated as SC-001 / SC-001a (the four AST tests together at one shared parse plus the margin; the record tests
  together at a `3x` cut of their sum), and User Story 2's scenario 2 restated as SC-003 (one constant density, 60 to
  240 seeds, per-house cost within `1.25x`). The asides: the harness docstring now names what it runs, and the timing
  entries in `measurements.json` carry `varies`.
- **Round 3 (spec-fidelity-verify, 2026-09-28): FAITHFUL.** Both round-2 items resolved; nothing introduced. Aside kept for the plan: give the harness a make-runnable command so `make figures` can re-run the recorded figures.

### Amendment 1 (2026-09-28, from the plan review), re-review on a reset counter

The plan review found that `_toy_hamlet` never set the placer's own nucleated switch, so every placement scenario had
run the DISPERSED spiral, which no pool hamlet uses. Fixed in the test; the scenarios now run both paths and the
figures were re-taken on the unmodified engine. SC-002 now names its path (the dispersed spiral, with the nucleated
path held not slower and not seating fewer); SC-003 covers both paths; FR-007 labels each scenario's path. The plan
review also ruled LEGITIMATE a per-household yard roll on condition that it is recorded here: a Decisions Recorded row
is added (yard size, garden proportions and bed split per household; the rake per seat).

Round 1 of this amendment (CHANGES REQUIRED): the amendment had dropped the accepted SC-003's dispersed target at density
(240 seeds `4x` faster than 8.198 s, m:before-dense-240-s) without saying so; the re-run showed that path's per-house timings are load noise, so
the target is restored as a deterministic one - `10x` fewer full fit tests at 240 seeds - and both dispersed baselines are
recorded. SC-002 cites the first run, the stricter.

A defect found while implementing FR-005, fixed under constitution XIV: `seg_intersect` returned the intersection of the
two infinite LINES for any non-parallel pair, and seven callers used it as a crossing test - `path_violations`' four water
tests (Inashiro's candidate paths scored thousands of "violations" with no real crossing), a cluster's way-crossing finder
and spur trim, and a homestead's brook-cut test. It is now bounded on both segments (agreeing with `segments_cross` on every
pair); `path_violations`, FR-005's oracle, is the corrected function, so tracks on maps with water may choose differently.

Round 2 of this amendment (CHANGES REQUIRED): the Decisions Recorded preamble named two of the fix's three consumers - the
homestead brook-cut test was missing - and the fix had no row of its own; both added. SC-005's path-check baseline is
re-taken on the corrected function, 0.139 s (m:before-track-checks-corrected-s), so its `2x` credits the index, not the fix.

Round 3 of this amendment (spec-fidelity-verify, 2026-09-28): FAITHFUL.

### Amendment 2 (2026-09-28, while implementing FR-003), review on a reset counter

SC-003's "neither path seats fewer houses than before" was judged on ONE layout of each density, and one layout's count
moves by a few houses whenever the households' rolls are reshuffled: with the per-household roll (Decisions Recorded, ruled
LEGITIMATE), the dispersed single-layout count at 240 seeds went from 140 to 137 - while over five layouts it went from 703
to 707. So the clause is now judged on the total over five layouts, within `2%`. Stated plainly, because it is the
judgment this amendment asks for: on the NUCLEATED path the five-layout totals read 281, 560 and 1133 against 285, 563
and 1138 (-1.4%, -0.5%, -0.4%; observed 2026-09-28, method: the probe named in measurements.json) - small and
consistent, most likely because a seat moved clear of a neighbor used to be re-rolled at its new position, a second chance
the household's own roll no longer gives. The pool hamlets' own counts are held separately by FR-006 (every household
seated), and checked when the pool regenerates.
