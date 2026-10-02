# Feature Specification: Grow the cluster

**Feature Branch**: none - committed on `main` in the clone (`SPECIFY_FEATURE=308-grow-the-cluster`)

**Created**: 2026-10-02

**Status**: Draft

**Input**: the GM's request, verbatim in `request.md`: seat the households by growing the cluster outward from the first house
- *"compute the minimum distance needed to seat a second house, then place it in a direction, then repeat, with a little
randomized jitter to the distance and direction"* - with the minimum distance set by what a homestead holds AND by the sun and
shade rules (*"casting shade on a threshing yard also contributes"*).

## Context: where the seating stands after feature 306 (observed 2026-10-02, method: feature 306 research R15 and R17, the reference spec at 40 households, sixteen seeds, back to back)

The homesteads stage takes 82.8 s summed over the sixteen seeds; eleven seat on the first margin in 2.2-3.7 s, and seeds 2, 6, 7,
12 and 39 take 5-13 s because 3-6 margins are seated and thrown away before one holds every household. The seating offers
383-5,927 seats for 40 houses: three passes (a front row along the field, lattice ranks, then every free grid point near the
center), each seat asked the full placer rules, most refused because no straight path from the door to the access tree clears
what already stands. Feature 306's grow-from-the-houses round (its research R3) offered a neighbor's box-width away - where the
neighbor's door path and woodlot lie - as a last pass after the others, on the old band; it was not a fair test of this idea.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The grower measured before the engine changes (Priority: P1)

A prototype outside the engine seats a margin by growth: the first house at the cluster's seed point; each next house placed
from a house already standing, in a direction and at a spacing - both jittered from the map's seed - no closer than the
homestead's footprint and the sun rules allow; its path to the access tree laid back to the standing house's path as it is
placed. Every house it places is still asked the engine's full placer rules, which decide. It is timed against the engine's
seating on the same states, back to back.

**Why this priority**: the GM's approach, tested before it is built, as feature 306's were.

**Independent Test**: the harness reports, per reference seed at 10, 15, 20 and 40 households: both methods' seconds, margins
seated, seats offered, households seated; and a verdict.

**Acceptance Scenarios**:

1. **Given** the captured states, **When** the harness runs, **Then** it reports both methods per seed and size and a verdict:
   GO where the grower is faster beyond the measured run-to-run spread and seats every household on every seed the engine
   seats, NO-GO otherwise.
2. **Given** a NO-GO or a missed goal (SC-002, SC-003), **When** the session iterates, **Then** at least one further round is
   prototyped and measured the same way before the feature stops; a final miss is recorded with every round's numbers and
   raised with the GM.

---

### User Story 2 - The engine grows the cluster (Priority: P2, only on GO)

The engine seats a nucleated cluster margin by growth (US1's method); the front row, the lattice ranks and the exhaustive pass
(with its rescue) are removed for that form. Every house still passes the same placer rules; a margin the growth cannot fill is
reported short and the margin ladder offers the next.

**Why this priority**: the redesign the GM asked for; built only on the prototype's verdict.

**Independent Test**: the reference at 10/15/20/40 households, the pool and the cohort: every household seated, every rule
passing, the homesteads stage timed against the base back to back.

**Acceptance Scenarios**:

1. **Given** the reference at 40 households, **When** it is rolled, **Then** the placer is offered at most a few seats per house
   kept, and a margin is thrown away only where the growth runs out of ground.
2. **Given** the pool and cohort seeds 1-24 with the six pinned, **When** they are rolled, **Then** every household each seated
   on the base is seated, every rule passes, and no seed is refused that the base seated.

### Edge Cases

- A direction blocked by the field, water, the canvas or the band's edge: growth continues from another standing house.
- Growth that runs out of room before every household stands: the margin is reported short and the ladder offers the next (as
  today) - the growth must say how many it could place, so a short margin is known without a second search.
- The linear form is outside the request: it seats every farm along planned streets (`seat_rows`, feature 291) and never ran
  the three passes the growth replaces. The dispersed form is a ruled exception: its farmsteads stand each amid its own holding,
  and growing each from a neighbor at the minimum distance would make it a cluster. Both rulings: `spec-fidelity`, round 1,
  2026-10-02 (LEGITIMATE).
- The cluster must still draw its rolled shape's band (`drawn_in_band`): growth is held inside the band.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A prototype MUST measure the growth against the engine's seating, back to back, before any engine change, with
  the GO rule of US1.
- **FR-002**: Wherever SC-002 or SC-003 is missed, at least one further round MUST be prototyped and measured before stopping;
  every round's numbers are recorded.
- **FR-003**: The minimum distance between homesteads MUST be computed from what a homestead holds - house, threshing yard,
  garden beds, its woodlot share and its path out - AND from the sun and shade rules the placer enforces: the open ground SOUTH
  of every threshing yard (`SUN_CORRIDOR_FT`), no farmhouse shading a garden bed, no grove in the strip south of a yard;
  so the distance depends on the direction.
- **FR-004**: Each next house MUST be placed from a house already standing, in a direction and at a spacing jittered from the
  map's seed (positional, so a map is reproducible), never closer than FR-003's distance in that direction.
- **FR-005**: Each house's path to the access tree MUST be laid as it is placed, back to a standing house's path or the tree,
  so reachability holds by construction; the placer's own corridor rules still judge it.
- **FR-006**: Every house the growth places MUST still pass the placer's full rules (no rule is relaxed or skipped).
- **FR-007**: On GO the engine MUST seat a nucleated cluster margin by growth; the front row, the lattice ranks and the
  exhaustive pass (with its rescue) are removed for that form. A margin the growth cannot fill is reported short and the margin
  ladder offers the next. Keeping any old pass is an exception put to `spec-fidelity` (MODE 1) with its measurement first.
- **FR-008**: No pool map or cohort seed may fail a rule it passed before or seat fewer households; maps may move within the
  rules (GM 2026-09-30, feature 297: "They do NOT need to remain identical in output").
- **FR-009**: Every lever MUST be timed by the wall clock, base and clone back to back, and recorded in `dev/performance.md`,
  including any withdrawn.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-002): The harness verdict is recorded with both methods' times, margins, offers and seated counts per
  seed and size.
- **SC-002** (FR-003, FR-004, FR-005, FR-007): The homesteads stage at 40 households under 4 s on every one of the sixteen seeds
  of feature 306's R15 (a target; the base observed 2026-10-02, method: feature 306 research R15 and R17 - 2.2-13 s, 82.8 s summed).
- **SC-003** (FR-004, FR-005, FR-007): At most five seats offered per house kept, and at most two margins seated, on every one
  of the sixteen seeds at 40 households.
- **SC-004** (FR-006, FR-008): The cohort passes as many seeds as the base (30/30), every pool map passes its rules.
- **SC-005** (FR-007, FR-009): The 15-household reference is not slower (perf band 0 or better).
- SC-002 and SC-003 are the session's goals, not the GM's: a miss is met with FR-002's further round; one that survives it is
  recorded with every round's numbers and raised with the GM.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Households seated by growth from the first house, each from a standing neighbor | map drawing convention (the placement ORDER; every seat passes the same rules) | the GM's *"once you've placed the first house, you should notionally be able to compute the minimum distance needed to seat a second house, then place it in a direction, then repeat"* | this spec; the grower's docstring |
| The jitter of direction and spacing | guess - its magnitude is set in the plan from measurement and labeled | the GM's *"a little randomized jitter to the distance and direction so that it's not jhusgt [just] an unrealistic grid"*; the record gives no spacing variance for a nucleated hamlet | the plan; the constant's comment |
| The minimum distance by direction from the sun rules | historically accurate (the sun rules' own research: `research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html`, `0038-sunlight-and-shade-on-the-farm.drawing.html`) | the GM: shade on a threshing yard sets the distance too | the research pages named; the grower's comment |

## Assumptions

- The reference spec at 10/15/20/40 households (feature 304's scaling leg) is the measure; feature 306 R15's three-leg runner
  is reused for back-to-back legs.
- The 162 ft seating band (feature 306) bounds the growth; the margin's choice, canvas and belt are unchanged.
