# Feature Specification: Seat by packing

**Feature Branch**: none - committed on `main` in the clone (`SPECIFY_FEATURE=306-seat-by-packing`)

**Created**: 2026-10-02

**Status**: Draft

**Input**: the GM's request, verbatim in `request.md`: a redesign of how the farmhouses are set down - *"draw a bounding box
that will contain a homestead and the things in the homestead, and then place it on the map, and then place another one next
to it"* - prototyped before it enters the engine where that is practical, iterated *"at least another iteration pass or two"*,
and a general rule: an overlap check against more than a certain number of other things means a bounding box or a line to
stay on the right side of was not drawn.

## Context: where the time goes (observed 2026-10-02, method: a scratch probe timing `_seat_households` and the placer's questions through `stage_homesteads`, the reference spec at 40 households)

| seed | homesteads | margins seated | placer calls | per call | houses seated per margin |
|---|---|---|---|---|---|
| 47 | 50.0 s | **16** | 25,279 | 1.5 ms | 33, 30, 20, 29, 28, 21, 24, 22, 33, 31, 22, 38, 15, 18, 25, **40** |
| 25 | 8.3 s | 3 | 3,774 | 1.9 ms | 29, 27, **40** |

The cost is not a slow check: one placer call is ~1.5 ms. It is the SHAPE of the search.

1. **A margin's capacity is found by seating it.** `seat_every_household` seats every household it can on the chosen margin,
   and where that falls short it takes them all back and seats the next margin of the ladder from scratch. Seed 47 seated
   sixteen margins, ~3 s each, and kept the sixteenth.
2. **About 37 seats are offered per house kept.** Each margin's seating offers ~1,350-2,000 seats to the placer for 15-40
   houses; the exhaustive pass (`seat_the_rest`) alone is ~2 s of each margin's ~3 s, offering every free grid point.
3. Each offer still asks the house's box, the field's reach, four garden-side layouts with their fixtures, the envelope, the
   corridor search to the access tree (~0.9 ms) and the part rules (~0.6 ms) - the right questions, asked of seats a box packing
   would never have proposed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The packing measured before the engine changes (Priority: P1)

A prototype outside the engine takes each margin's starting state as the engine has it (the boundary, the exit strip, the
field's corridor, the seat region) and (a) PREDICTS the margin's capacity by packing each homestead's bounding box (house, yard,
garden, the kura where it has one) on the margin's free ground, adjacent to the boxes already placed, and (b) offers the
packed seats, in packing order, to the engine's own placer, which asks every rule it asks today. It is timed against the
engine's seating of the same states, back to back.

**Why this priority**: the GM asked for the approach to be tested before it is built into the engine where that is practical;
it is here (feature 302's harness pattern), and it decides whether the engine work is worth doing.

**Independent Test**: the harness reports, per reference seed at 15, 20 and 40 households: the engine's seating time and
houses, the prototype's time and houses, the margins each seats, and how often the predicted capacity agrees with the engine's
seated count.

**Acceptance Scenarios**:

1. **Given** the captured states, **When** the harness runs, **Then** it reports both methods' seconds, households seated and
   placer calls per seed and size, and a verdict: GO where the prototype is faster beyond the measured run-to-run spread and
   seats every household on every seed the engine seats, NO-GO otherwise.
2. **Given** a NO-GO, **When** the session iterates, **Then** at least one further design round is prototyped and measured
   the same way before the feature stops (the GM: *"at least another iteration pass or two"*); a final NO-GO is recorded with
   every round's numbers and raised with the GM.

---

### User Story 2 - The engine seats by packing (Priority: P2, only on GO)

The engine chooses the margin whose packed capacity holds every household (seating no margin it can predict will fall
short), proposes seats by packing bounding boxes on the margin's free ground next to the ones already standing, and asks the
full rules of those seats only. The exhaustive pass over every free grid point is retired where the packing replaces it.

**Why this priority**: it is the redesign the GM asked for; it is built only once the prototype shows it pays.

**Independent Test**: the reference at 10/20/40 households and the pool and cohort: every household seated, every rule passing,
the homesteads stage timed against the base back to back.

**Acceptance Scenarios**:

1. **Given** the reference at 40 households, **When** it is rolled, **Then** at most two margins are seated (one predicted to
   hold everyone, and the next only where the prediction failed) and the placer is offered at most a few seats per house kept.
2. **Given** the pool and cohort seeds 1-24 with the six pinned, **When** they are rolled, **Then** every household each seated
   on the base is seated, every rule passes, and no seed is refused that the base seated.

---

### User Story 3 - Overlap checks against many things are found (Priority: P3)

A census counts, for every overlap or proximity check a hamlet roll asks, how many other items each call compares against. A
check whose calls compare against more than a set number of items is flagged: by the GM's rule, a bounding box, an index or a
line to stay on the right side of was not drawn for it.

**Why this priority**: the GM's general rule; it is how the next inefficiency of this shape is found rather than stumbled on.

**Independent Test**: the census runs on the reference at 40 households and lists every check with its calls, its mean and
largest comparison count; a deliberately unindexed scan added to a test roll is flagged.

**Acceptance Scenarios**:

1. **Given** a roll, **When** the census runs, **Then** every flagged check is listed with its stage, calls and comparison
   counts.
2. **Given** a flagged check in the homesteads stage, **When** this feature lands, **Then** it is given its box, index or line,
   or recorded with the measurement of why not; a flagged check in another stage is recorded and raised with the GM.

### Edge Cases

- A margin the packing predicts too small that the engine's greedy seating would have filled: the prediction is a lower bound
  where it can be; a wrong prediction is measured by the harness (US1) and costs at most one extra seated margin (US2.1).
- The polder archetypes and the dispersed and linear forms do not seat by the nucleated placer; they are left as they are, and
  the harness says so per seed.
- 80 households and up refuse in the field stage (feature 304 research R5); out of scope.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A prototype MUST measure the packing against the engine's seating on captured states, back to back, before any
  engine change, and report a GO/NO-GO verdict by the rule in US1.
- **FR-002**: On NO-GO the session MUST iterate the design at least once more, measured the same way, before stopping; every
  round's numbers are recorded.
- **FR-003**: On GO the engine MUST choose the margin by the packing's predicted capacity rather than by seating each margin
  in turn.
- **FR-004**: On GO the engine MUST propose seats by packing homestead bounding boxes adjacent to the ones already standing, and
  ask the full rules only of the proposed seats.
- **FR-005**: The packing MUST read the free ground from rasters and boxes built once per margin and kept current as homesteads
  land (constitution X clause 15), never by a scan over the map's items per candidate.
- **FR-006**: A census MUST count the items each overlap or proximity check compares against, per call, over a roll, and flag
  the checks past a threshold set in the plan from the measured distribution.
- **FR-007**: Every flagged check in the homesteads stage MUST be indexed, boxed or lined, or recorded with why not; flagged
  checks in other stages MUST be recorded and raised with the GM.
- **FR-008**: No pool map or cohort seed may fail a rule it passed before or seat fewer households; maps may move within the
  rules (GM 2026-09-30, feature 297: "They do NOT need to remain identical in output").
- **FR-009**: Every lever MUST be timed by the wall clock, base and clone back to back, and recorded in `dev/performance.md`
  with what it bought, including any withdrawn.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-002): The harness verdict is recorded with both methods' times and seated counts per seed and size.
- **SC-002** (FR-003, FR-004, FR-005): The homesteads stage at 40 households takes under 0.1 s per household (4 s) on every
  reference seed (a target; the base observed 2026-10-02, method: the Context probe and feature 304 research R10 - 6.2-10.1 s
  on seeds 4, 25, 39 and 50.0 s on seed 47).
- **SC-003** (FR-003, FR-004): At most two margins are seated per roll, and the placer is offered at most five seats per house
  kept, on every reference seed at 10/20/40 households.
- **SC-004** (FR-008): The cohort passes as many seeds as the base (30/30) and every pool map passes its rules.
- **SC-005** (FR-006, FR-007): The census lists every check of a roll; every flagged homesteads check is resolved or recorded.
- **SC-006** (FR-003, FR-004, FR-009): The 15-household reference is not slower (perf band 0 or better).
- SC-002 and SC-003 are the session's goals, set from the GM's *"not a full second per box"*: a miss after the iterations FR-002
  asks for is recorded with every round's numbers and raised with the GM.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

The packing changes which seat a homestead takes and which margin the cluster stands on, never a rule a seat must pass, a
size, a glyph or a distance: every seat still passes the placer's full rules. No rendering decision is added by the levers; any
the implementation finds it needs is recorded here with its class before it lands.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Homesteads packed adjacent, nearest the seat's center first | map drawing convention (the placement ORDER, not a rule) | the GM's *"place another one next to it"*; the rules decide whether a seat may stand | this spec; the packing's docstring |

## Assumptions

- The reference spec at 10/15/20/40 households (feature 304's scaling leg) is the measure; `make perf` carries it.
- Feature 302's harness pattern (capture the inputs, run both methods back to back, compute the verdict) is reused.
- The nucleated form is the subject; the other forms keep their seating unless the census flags a check in them.
