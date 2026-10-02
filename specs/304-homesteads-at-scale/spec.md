# Feature Specification: Homesteads at scale

**Feature Branch**: none - committed on `main` in the clone (`SPECIFY_FEATURE=304-homesteads-at-scale`)

**Created**: 2026-10-01

**Status**: Draft

**Input**: the GM's request, verbatim in `request.md`: before moving on to scripted villages, make sure there is no more
low-hanging fruit in hamlet generation performance. The session's measurement (request.md) found the low-hanging fruit is not
at the reference hamlet's size but in how the homesteads stage grows with the household count; the GM accepted the proposed
next step ("Yes please"): the scaling benchmark first, then the levers.

## Context: what was measured (2026-10-01, after feature 302)

A scratch probe rolled the reference spec (Inashiro's: fall 90, pond sink, nucleated, one shrine) with the hamlet band lifted,
seeds 4 and 25, and timed every stage:

| households | stage total | homesteads | field | web |
|---|---|---|---|---|
| 10 | 1.8-2.1 s | 0.42-0.48 | 0.30-0.39 | 0.21-0.35 |
| 20 | 4.1-8.3 s | 1.48-5.04 | 0.65-1.08 | 0.48-0.81 |
| 40 | 13.2-14.7 s | 7.07-7.74 | 1.34-2.70 | 1.30-1.76 |
| 80 | refused (`FieldRefused`: no single fan lands 104 acres) | - | - | - |

The homesteads stage is the one that grows faster than the household count (4x the houses, ~16x the time); the rest grow
roughly in proportion. Profiled at 40 households (seed 25, cProfile, which roughly doubled the stage): the exhaustive seating
pass offered 3,774 seats to seat 40 houses (~70% of the stage), every refused seat paying the corridor search, the layouts and
the fixtures; the access tree's nearest-target lookup measures and sorts every point of the whole tree for each door (30,000
lookups over a tree that grows with the houses); the standing-ground clearance checks ran 1.8 million segment-distance
measurements.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A village-size slowdown cannot land unseen (Priority: P1)

The GM is about to start the village tier. Today every performance guard times only the 15-household reference, so a change
that is harmless at 15 households and ruinous at 40 lands green. The perf bookend gains a scaling leg: the same reference spec
rolled at 10, 20 and 40 households on the same fixed seeds, each size reported per stage beside the 15-household reference,
with the same trend record and the same bands the reference has.

**Why this priority**: the GM asked to start with the benchmark; without it neither lever below can show what it bought, and
the village tier would inherit no guard.

**Independent Test**: run the perf snapshot on the base commit; it reports every size's stage times and records them beside
the reference in the trend log; a deliberately slowed homesteads stage (a seeded fault that is linear at 15 and quadratic in the
household count) shows up in the 40-household leg's band and not only in its total.

**Acceptance Scenarios**:

1. **Given** the base engine, **When** the perf snapshot runs, **Then** it reports the 15-household reference as before plus
   per-stage seconds at 10, 20 and 40 households on the fixed seeds, and records them in the trend log.
2. **Given** a recorded snapshot, **When** a later snapshot is compared against it, **Then** each household size is compared
   against its own earlier figures and an increase is put in a band by the same rules as the reference.
3. **Given** a hamlet spec the GM writes, **When** it asks for more than 20 households, **Then** it is refused as today: the
   benchmark's larger sizes reach the generator by the measuring tool alone, never by widening the hamlet band.

---

### User Story 2 - The access lookups ask only what is near (Priority: P2)

The nearest-target lookup and the standing-ground clearance checks ask an index for what is near the door or the strip, in
place of scanning every corridor point and segment on the map. This is the safe lever: the answers are the same answers.

**Why this priority**: the scan over the whole tree is the quadratic shape this engine has been caught growing three times
(dev/performance.md); indexing it moves no map.

**Independent Test**: roll the pool and the cohort on the clone and the base; every map's houses, corridors and lanes are
identical; the homesteads stage at 40 households is faster by the wall clock.

**Acceptance Scenarios**:

1. **Given** any door and any access tree, **When** the indexed lookup answers, **Then** it returns the same targets in the
   same order as the scan it replaces (an equivalence test over the cohort's doors).
2. **Given** any strip, **When** the indexed clearance check answers, **Then** its verdict equals the scan's.

---

### User Story 3 - Seats that cannot work are not offered (Priority: P3)

The exhaustive seating pass stops offering seats a placement will refuse for a reason already knowable before the placer runs
- ground a house just seated now covers, or a seat with no clear straight strip to the access tree. Which of the two forms
(the seat region kept current as houses land, or the line-of-sight reach region priced in feature 297's research) is chosen by
measurement in the plan.

**Why this priority**: the largest single cost at 40 households, but it can move maps; it lands after the benchmark can show
what it buys and after the output-identical lever has taken its share.

**Independent Test**: count seats offered per house seated at each household size on the clone and the base; roll the pool
and the cohort and check every map passes its rules and seats every household it seated before.

**Acceptance Scenarios**:

1. **Given** the 40-household reference, **When** it is rolled, **Then** fewer seats are offered per house seated than the
   base offered, every household is seated, and every rule the map is held to passes.
2. **Given** a pruning that would refuse a seat the placer would have accepted, **When** the cohort rolls, **Then** the cohort
   seats at least the households it seated before on every seed (a pruning may change WHICH seat, never HOW MANY are seated).

---

### Edge Cases

- 80 households and up: the field refuses before the homesteads run (`FieldRefused`). That is a village-design question (one fan
  cannot land 104 acres), out of scope here; the benchmark stops at 40 and says why.
- A seed that refuses at a benchmark size on the base engine (a `WebRefused` or `FieldRefused`): the snapshot records the
  refusal for that row, not a time, and does not fail the run. The four reference seeds are kept at every size; a refusing
  seed is never swapped out (seeds 39 and 47 have not yet been rolled above 15 households).
- Seed variance: seed 25 at 20 households took 5.0 s in homesteads where seed 4 took 1.5 s. The benchmark keeps the reference's
  fixed seeds so a slow seed stays in the set, as perf_snapshot's own docstring requires.
- Machine load: every before/after comparison is the base and the clone run back to back (feature 297's method), never against
  a figure from another session.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The perf snapshot MUST time the reference spec at 10, 20 and 40 households, on the reference's fixed seeds,
  per stage, beside the unchanged 15-household reference, and record them in the trend log.
- **FR-002**: The perf comparison and bands MUST cover each household size against its own earlier figures; a snapshot recorded
  before this feature (no scaling rows) compares as "no baseline" for those rows, not as an error.
- **FR-003**: The benchmark MUST reach sizes outside the hamlet band without widening the band a GM-written spec is held to.
- **FR-004**: The nearest-target lookup of the access tree MUST answer from an index of what is near the asking point, with
  the same targets in the same order as the whole-tree scan.
- **FR-005**: The standing-ground and corridor clearance checks that the profile names MUST ask an index for nearby segments
  in place of scanning all of them, with the same verdicts.
- **FR-006**: The exhaustive seating pass MUST stop offering dead seats by one of the two named forms - the seat region kept
  current as houses land, or the line-of-sight reach region priced in feature 297's research - chosen in the plan by
  measurement; a form that seats fewer households on any cohort seed is withdrawn. Any other pruning goes to the GM first.
- **FR-007**: Every lever MUST be measured by the wall clock, base and clone back to back, and recorded in
  `dev/performance.md` with what it bought and what it did not, including any lever withdrawn.
- **FR-008**: No pool map or cohort seed may fail a rule it passed before; maps may move within the rules (GM 2026-09-30,
  feature 297: "They do NOT need to remain identical in output").

### Key Entities

- **Scaling rows**: per household size and seed, the stage seconds, houses seated, and seats offered.
- **Access index**: the corridor points and segments of the access tree, kept current as corridors are added.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The perf snapshot reports per-stage times at 10, 15, 20 and 40 households, and a seeded fault that is quadratic in
  the household count raises the 40-household leg's band.
- **SC-002**: The homesteads stage's seconds per household at 40 households is at most twice its seconds per household at 10
  (base, observed 2026-10-01, method: the scratch scaling probe in request.md: 0.045 s/household at 10, ~0.19 at 40, a ratio
  of ~4), measured on the fixed seeds, back to back.
- **SC-003**: The homesteads stage at 40 households is at least 2x faster than the base by the wall clock (base 7.1-7.7 s on
  seeds 4 and 25).
- SC-002 and SC-003 are the session's stated goals, not the GM's: nothing has yet measured that the three levers can reach them.
  A miss is recorded in `dev/performance.md` with what each lever bought, and raised with the GM; it is not pursued with levers
  beyond the three accepted.
- **SC-004**: The 15-household reference does not get slower (perf band 0 or better).
- **SC-005**: The indexed lookups (User Story 2) leave every pool map and cohort seed's houses, corridors and lanes identical.
- **SC-006**: Every cohort seed seats at least the households it seated on the base, and the cohort passes as many seeds as it
  did on the base.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

This feature adds no rendering decision: it changes no glyph, size, distance, density or placement rule. User Story 3 may
change which seat a household takes; every seat it takes is one the existing rules accept, so the record's existing placement
entries stay correct. Any lever that would change a rule (not only a seat) is out of scope and would be raised with the GM.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Benchmark sizes 10/20/40, not 80 | not a rendering decision (tooling) | 80 households refuses in the field stage on the base (one fan cannot land 104 acres) | this spec; the perf tool's docstring |

## Assumptions

- 40 households stands in for a small village's household count; the village tier's own generator may change the stages, but
  the homesteads placer is the code a village will reuse.
- The perf bookend's cost grows by the three new sizes; an estimate (observed 2026-10-01, method: the scratch scaling
  probe's stage totals for seeds 4 and 25 at 10, 20 and 40 households, 19.1-25.1 s a seed) of 76-100 s of stage time over the
  four seeds, the two unprobed seeds (39, 47) unmeasured, paid only where the bookend runs today (`make done FULL=1`, `make perf`), never in `make quick` or the plain gate.
- The line-of-sight reach region and the live seat region are both candidates for FR-006; feature 297's research (R9-R17)
  lists the levers already withdrawn and is read before either is built.
- The field's refusal at 80 households is left to the village tier.
