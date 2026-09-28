# Feature 278 - the second hotspot pass

**Feature Branch**: none (main, in the clone `diagram-inashiro`)
**Created**: 2026-09-28
**Status**: Draft (round 2)
**Request**: [`request.md`](request.md) - the GM's words verbatim: run feature 276's exercise again - measure, find, make faster.
**Predecessors**: 276 (the first pass: placement indexes, batched seam closing, the track's `PathChecker`, the shared
test parses; `dev/performance.md` "Three more shapes"), 218 (the index-once doctrine; its research R2 priced the
vectorized scatter), 138 (the router's one index per box).

## Summary

The same exercise as feature 276, on the code as it stands after 276 and 261 landed (main `ac01ffe2d`). The
measurement (research R1-R3) rolled every pool hamlet with each stage timed and every mechanism counted, profiled each
heavy stage alone, profiled a full regeneration with rendering, and timed the whole test suite. The five pool hamlets
take 60.1 s to roll between them (m:before-pool-roll-s), and it found:

- **Per-candidate scans an index or a hoist removes exactly**, in the router (the whole search box evaluated before
  searching), a doorstep search (one index's memo key rebuilt per candidate), the footbridge widening (every water
  segment per deck), the well placer (the whole pool re-sorted every iteration), the field's hem pass (every plot per
  drain sample), the notice board (every way segment per verge candidate; every hard polygon's box per fit), the
  windbreak (five keep-out grids asked per candidate where one would do) and the page writer (every extent in a bucket
  per element).
- **Work done and thrown away**: Sawada seats a farmhouse no way can reach, so every Sawada roll is two builds, and
  the driver finishes the discarded attempt too.
- **A scatter in pure Python** that 218 priced as a vectorized one: the commons.
- **Tooling**: `make map` rolls the reference twice; a test goes red in every clone after a sync-in that adds a class;
  one of feature 276's equality tests costs 4.6 s of `make quick` (observed 2026-09-28, method: `make durations`).

Whatever the profile shows is left after these - the per-sample work each drawing genuinely needs - is written down
with its levers priced (FR-015).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The pool rolls in far less time, and every map is the same place (Priority: P1)

The GM waits on hamlet rolls in every iteration. After this feature the five pool hamlets roll much faster between
them; the maps an exact change touches are byte-identical, and the two that a moving change touches (Sawada, and the
commons' ground cover everywhere) are the same settlements by feature 276's measure.

**Why this priority**: it is the whole point of the exercise.

**Independent Test**: the harness, before (a detached worktree of the base) and after (the clone), back to back.

**Acceptance Scenarios**:

1. **Given** the five pool hamlets, **When** they roll, **Then** their summed roll time is well under the base's.
2. **Given** an exact change, **When** the pool regenerates, **Then** the manifests it touches are byte-identical.

### User Story 2 - The ways are routed without evaluating ground the search never reaches (Priority: P1)

The lane router marks every cell of its search box, up to 90,000, before Dijkstra starts, most of which the search
never reaches; the doorstep search asks for one index per candidate standing-place.

**Why this priority**: the largest shared engine cost, on every map with lanes.

**Independent Test**: count the router's cell tests before and after; route recorded requests through both routers
and compare the paths.

**Acceptance Scenarios**:

1. **Given** any start, goal and ground, **When** the router runs, **Then** it returns exactly the eager router's path.

### User Story 3 - The placers stop re-deriving what does not change (Priority: P1)

The footbridge widening, the well placer, the field's hem pass, the notice board's two probes, the windbreak's
keep-outs and the page writer's merge test each re-scan geometry that does not change during their loop.

**Why this priority**: each is the per-candidate-scan shape the doctrine names, and each removal is exact.

**Independent Test**: count each mechanism before and after; the manifests they touch are unchanged.

**Acceptance Scenarios**:

1. **Given** the pool hamlets, **When** they roll, **Then** each named mechanism runs a fraction as often, each stage
   it dominates is faster, and every manifest is what it was.

### User Story 4 - Sawada is rolled once, and a discarded roll is not finished (Priority: P1)

Sawada's first attempt seats a farmhouse in a bare pocket inside its paddy field that no way can reach (research R3),
so the driver re-rolls it; and it finishes the discarded attempt first.

**Why this priority**: it doubles the most expensive pool hamlet, and a seat no way can reach is a placer defect.

**Independent Test**: roll Sawada and count its builds and finishes; a stub roll that re-rolls shows the discarded
attempt unfinished.

**Acceptance Scenarios**:

1. **Given** Sawada's spec, **When** it rolls, **Then** it is built and finished once, seats all 19 households, and every
   farmhouse reaches a way.

### User Story 5 - The commons scatter runs as array operations (Priority: P2)

The commons scatter draws and tests its marks one at a time in Python; 218 priced a vectorized form that keeps its
density.

**Why this priority**: most of the hinterland stage on every map; the one lever here that moves every map's marks.

**Independent Test**: the hinterland stage before and after; the scatter's density and keep-outs tested as before.

**Acceptance Scenarios**:

1. **Given** any map, **When** the commons are scattered, **Then** the marks keep every keep-out and the same density,
   in a fraction of the time.

### User Story 6 - The tooling stops paying for work nobody asked for (Priority: P2)

`make map` on the reference hamlet rolls it once for the gate's check and again to draw the render; a synced clone goes
red on `test_every_clickable_class_is_named_somewhere_on_the_committed_page` until someone re-plates a gitignored page
by hand; and the `md_tokens` equality test costs 4.6 s of `make quick` (observed 2026-09-28, method: `make durations`).

**Why this priority**: seconds on every iteration, and a false red on every sync-in that adds a class.

**Acceptance Scenarios**:

1. **Given** the reference hamlet, **When** `make map` runs on it, **Then** it is rolled once.
2. **Given** a clone synced in after a class was added, **When** `make quick` runs, **Then** the placement-stages page
   test is not red for a page the landing re-plates - and a class genuinely missing from the page still turns it red.
3. **Given** the quick tree, **When** it runs, **Then** the `md_tokens` equality test checks every tracked text in a
   fraction of the time - and a planted `.md` token the whole-text scan finds is still found.

### Edge Cases

- A route with no path: the lazy router explores every reachable cell, as the eager one did, and returns [].
- A deck whose box meets no other watercourse: the widening returns the span unchanged.
- A well pool pass that places nothing: the order it leaves is the order the next pass reads.
- A hamlet whose ground can serve no seat the placer would take: FR-005 does not seat fewer households than today;
  a seat is refused only where another legal seat is taken instead (feature 276's FR-006 condition).
- The placement-stages page absent in a fresh clone: the test's existing skip.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 The router evaluates only the cells its search reaches.** A cell's free/fouled state and its brook-band
  membership are computed when Dijkstra first touches the cell; the returned path is exactly the eager router's.
- **FR-002 The doorstep search obtains its index once per house**, not once per candidate standing-place.
- **FR-003 The footbridge widening asks an index of the other watercourses' segments**, built once per footbridge pass,
  the exact test deciding as before.
- **FR-004 The hamlet's well placer re-sorts only when a well lands**, the parts of its key that do not depend on the
  wells placed computed once per candidate.
- **FR-005 A farmhouse is not seated where no way can reach it.** The placer refuses a seat the roll's own reach rule
  would fail - found at the placer, not after the build - so Sawada's first roll seats every farmhouse (research R3);
  the class of the change is recorded under Decisions when the plan settles the mechanism.
- **FR-006 The driver finishes only the attempt it keeps.**
- **FR-007 The field stops re-scanning static geometry**: the hem pass asks an index of the plots for a drain sample's
  containment, not every plot; and a thread's point at a fall (`_at_f`) is found from its vertices projected once, not
  by re-projecting and walking the whole polyline per query.
- **FR-008 The commons scatter is vectorized** - throws and keep-out tests as array operations (218's research R2),
  the same density and the same keep-outs; its marks move.
- **FR-009 The notice board's probes ask indexes**: `off_every_bed` a segment index of the way beds; `_hard_clear` an
  index of the hard polygons' boxes, and `quad_hits_poly` tests only the vertices and edges its box can meet.
- **FR-010 The windbreak asks one keep-out grid per candidate**, the grove's static families filed together (218's
  "one grid per scatter, not one per family", never applied to the grove).
- **FR-011 The page writer's merge test asks an index of a bucket's extents**, not every extent.
- **FR-012 `make map` rolls a map once.**
- **FR-013 The placement-stages page a test reads is current in a synced clone.** The tooling that brings a new class
  into a clone re-plates the page (or the test reads the page a reader opens, re-plated from the clone) - never a red
  that only a landing clears, and never a stand-in for the page the GM's 2026-09-12 rule is about.
- **FR-014 The `md_tokens` equality test keeps its corpus and loses its cost.** Every tracked text is still checked.
- **FR-015 What is left is measured and written down.** `dev/performance.md` records what the after-profile shows
  remaining - per stage, where the seconds go - with each remaining lever priced, and the finishing's external
  renderer wait and the rest of the durations list among them.

### Key Entities

- **The harness** (`harness.py`): per pool hamlet, stage seconds from unprofiled rolls and mechanism counts from a
  profiled one; before-figures from a detached worktree of `ac01ffe2d` (`harness-before.json`), after-figures from the
  clone, back to back.

## Success Criteria *(mandatory)*

### Measurable Outcomes

A "per build" figure divides a count by the hamlet's builds (Sawada 2 before, m:before-sawada-builds), so FR-005's
halving is not counted twice.

- **SC-001** (all): the five pool hamlets' summed roll time is at least `1.5x` less than 60.1 s (m:before-pool-roll-s), back to back.
- **SC-002** (FR-001): the router's cell tests are at least `2x` fewer on Kashikawa (358398 fouled and 174118 band,
  m:before-kashikawa-cell-fouled, m:before-kashikawa-brook-band) and Kuwabata (331302, m:before-kuwabata-cell-fouled),
  and an equality test over recorded route requests returns the eager router's paths.
- **SC-003** (FR-002): fabric-index requests per build on Sawada are at least `3x` fewer than 7071 over two builds
  (m:before-sawada-fabric-index-calls).
- **SC-004** (FR-003): `quad_hits_seg` calls on Inashiro are at least `10x` fewer than 63674 (m:before-inashiro-quad-hits-seg).
- **SC-005** (FR-004): the well sort key is evaluated at least `5x` less on Kuwabata (72324, m:before-kuwabata-wells-key)
  and Kashikawa (53865, m:before-kashikawa-wells-key); Kuwabata's appurtenance stage is at least `3x` faster than
  1.78 s (m:before-kuwabata-stage-appurtenances-s).
- **SC-006** (FR-005, FR-006): Sawada is built once and finished once (m:before-sawada-builds, m:before-sawada-finishes),
  seating all 19 households with every farmhouse reaching a way; a stubbed re-roll shows the discarded attempt unfinished.
- **SC-007** (FR-007): `_pip` calls per build are at least `10x` fewer on Sawada (1932276 over two builds,
  m:before-sawada-field-pip) and Kashikawa (252417, m:before-kashikawa-field-pip), and the field stage per build is at
  least `1.2x` faster on Sawada (7.494 s over two builds, m:before-sawada-stage-field-s).
- **SC-008** (FR-008): the hinterland stage per build is at least `2x` faster on Sawada (2.143 s over two builds,
  m:before-sawada-stage-hinterland-s) and Kashikawa (1.199 s, m:before-kashikawa-stage-hinterland-s).
- **SC-009** (FR-009): the notice stage per build is at least `2x` faster on Sawada (2.516 s over two builds,
  m:before-sawada-stage-notice-s) and Inashiro (0.833 s, m:before-inashiro-stage-notice-s).
- **SC-010** (FR-010): the windbreak stage is at least `1.5x` faster on Kashikawa (2.222 s,
  m:before-kashikawa-stage-windbreak-s) and Inashiro (1.047 s, m:before-inashiro-stage-windbreak-s).
- **SC-011** (FR-011): `_hits` calls per finish are at least `3x` fewer on Sawada (896436 over two finishes,
  m:before-sawada-page-hits) and Kashikawa (398186, m:before-kashikawa-page-hits), and the page is byte-identical.
- **SC-012** (FR-012, FR-013, FR-014): `make map` on the reference rolls it once; a synced clone's `make quick` is not red on
  the placement-stages page, while a class planted missing from the page still turns the test red; the `md_tokens`
  equality test takes under `1 s`, and a planted `.md` token is still found.
- **SC-013** (the pool): FR-001 to FR-004, FR-006, FR-007 and FR-009 to FR-012 leave every manifest they touch
  byte-identical. The maps FR-005 and FR-008 move hold feature 276's FR-006 condition in full: every live pool map
  regenerates, `make done` is green at the `100%` floor and every gate rule passes; every pool map, the rescue-rounds
  scenario and the 10- and 20-household toys seat at least as many houses as today, with no new or larger shortfall,
  and keep their forms (dispersed or nucleated, the headman's house) and house kinds; each moved map's research entry
  gives its houses, paddies and ways before and after, and a material change is a finding to fix, not a report; and
  `make cohort N=24` shows no newly failing seed.
- **SC-014** (FR-015): `dev/performance.md` holds the after-profile's remaining costs with their levers priced; every
  before- and after-figure named here is in `measurements.json`, the after-figures carrying the command that re-runs them.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| The commons' marks are thrown and tested as arrays, so every map's ground-cover marks land in different places at the same density and under the same keep-outs | map drawing convention (no rule, density or keep-out changes; only which random places the marks take) | 218's research R2 priced it; the GM: shifts are fine "as long as the underlying reality of what these settlements are generally like stays the same" | point of change in `settlement/land/cover.py`; research R2 |
| A seat no way can reach is refused at the placer (FR-005) | recorded here by the plan when the mechanism is settled, before the fix lands | research R3 | the plan; point of change |

## Assumptions

- The seconds are taken back to back against the base worktree at a low load; the counts are load-independent.
- FR-005's refusal finds another legal seat on Sawada; if the plan finds none, the spec is amended with the measurement.

## Review history

- Round 1 (spec-fidelity, 2026-09-28): CHANGES REQUIRED - the residue carve-out rested on an unmeasured premise and a
  bar the GM had lifted; FR-007/FR-008 (now FR-013/FR-014) owed planted-offender proofs. Addressed: research R2
  profiles each residue stage alone; every lever it found that keeps the settlements what they are is its own FR and
  SC (FR-006 to FR-011); the moving levers are held to 276's FR-006 condition (SC-013); FR-015 now records only what
  the after-profile shows is left, with levers priced, the finishing and the durations list included; the Decisions
  class of the old row is gone with the row; SC-012 names both planted offenders.
- Round 2 (spec-fidelity, 2026-09-28): CHANGES REQUIRED - SC-013 claimed 276's FR-006 condition but stated less of it. Addressed:
  SC-013 now carries it in full (research entries before and after, no new or larger shortfall, the rescue-rounds
  scenario and the toys). The aside on `_bnd` is answered in research R2: `_at_f` is a linear per-query scan of a static
  polyline, so it joins FR-007 as a lever, with a field-stage target in SC-007.
