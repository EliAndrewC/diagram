# Feature 302 - the comb field built by construction

**Feature Branch**: none (main, in the clone `diagram-performance`)
**Created**: 2026-10-01
**Status**: Draft
**Request**: [`request.md`](request.md) - the GM's words verbatim: the field "does seem like it should be simpler than it is",
the savings "will become more relevant as we make larger settlements that have more fields and larger fields"; then "I would
much rather do the larger redesign if we think that that would make this appreciably better. So go ahead and do that", the
smaller fixes kept "if the smaller fixes end up making sense in the context of the redesign", "if it is not faster, then I
suppose we probably don't want to move forward with it", and the method: "build in isolation a version of what we are trying
to do, and then comparing the time that it takes to do that to the time that we are doing the current version ... a good
early confirmation to sanity check whether or not it makes sense to move forward with this."
**Predecessors**: 220 (the field fitted once: the search carves, only the winner is finished), 287 (every ring rule asked at
its placer, `waterfields/ring_rules.py`), 297 (placement by construction: region first, then fill - the same doctrine, applied
to homesteads and ground cover).

## Summary

The comb field is 1.2-1.5 s of Inashiro's 6-7 s regeneration (0.7-2.0 s across the pool; observed 2026-10-01, method: `make
map PROFILE=1`, three runs). It is built in two halves: a CARVE lays the canals, marches the threads and cuts each sector into
rows of plots, dropping any plot a guard refuses; then a REPAIR (`close_seams`) finds every scrap of bare ground the carve left
inside the command area - dropped plots, fork wedges, the toe between the last rows and the drain - and plants it or absorbs it
into a neighbor, re-asking the ring rules at each absorb, so that every bund ends up shared. Because the repair grows the
planted area by 11-21%, the size search that fits the fan to its households' acreage must PREDICT the repair's outcome for each
trial size, by shape unions. About a third of the stage is the search, a third the repair (observed 2026-10-01, method: `make
perf-profile SEED=4 STAGE=field`, shares only).

This feature builds the field the other way round: the ground the fan may plant - the command area less its water - is
computed first as a region, and the region is then cut into plots by the row and column bunds in one partition, so the plots
tile it with every bund shared from the start and no bare ground left to find. The region's area IS the planted acreage, so
the size search asks the region rather than carving plots and predicting a repair.

**It is decided by measurement before it is built.** Phase 0 builds the new method IN ISOLATION - a prototype under this
feature's directory that reads the engine but changes nothing in it - and times it against the current field on the same
inputs. Only a GO from that measurement starts the engine work; a NO-GO ends the feature with its measurement recorded and the
engine untouched.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Know whether the redesign is worth it before paying for it (Priority: P1)

The GM wants the speed confirmed before the engine and its tests are changed (request: "I would hate to like make a bunch of
engine changes ... and then find out after all of that work that the feature was not worthwhile").

**Why this priority**: it gates everything else.

**Independent Test**: the prototype runs through `make` on the recorded inputs and prints, per input, the current field's time,
the prototype's time and the prototype's rule verdicts; the verdict GO / NO-GO is computed from those numbers by the criteria
in SC-001 to SC-004, not judged.

**Acceptance Scenarios**:

1. **Given** the inputs the current field is fitted from (each comb hamlet in the pool, and Inashiro's brief at 10 and 20
   households), **When** the prototype is run, **Then** it reports, for each, the current field's fit-and-finish time, the
   prototype's fit-and-build time, the ratio, and the prototype field's acreage, bare ground, unshared bunds and ring-rule
   violations.
2. **Given** that report, **When** the go criteria are applied, **Then** the outcome is GO or NO-GO with the numbers that
   decided it, recorded in this feature's research before any engine file is changed.
3. **Given** NO-GO, **Then** no engine or test file changes, the measurement and why are recorded, and the GM is told.

### User Story 2 - The field is built by construction (Priority: P1, only after GO)

**Why this priority**: the redesign itself.

**Independent Test**: regenerate the pool's comb hamlets; every gate rule passes and the field stage is faster by the margin
the prototype promised.

**Acceptance Scenarios**:

1. **Given** a comb hamlet, **When** its field is built, **Then** the planted ground is computed once as a region and cut into
   plots whose bunds are shared as laid; no pass looks for bare ground afterward.
2. **Given** a trial size in the fit, **When** it is scored, **Then** its acreage is read from its region, without cutting it
   into plots and without predicting a repair.
3. **Given** a cell of the partition that breaks a ring rule (too small, a needle, an arrowhead, a staircase, a self-crossing,
   a supply or collector intrusion), **When** the plots are laid, **Then** it is merged with a neighbor across a bund they
   share, or split, at construction - the way the repair resolves it today, without first leaving the ground bare.
4. **Given** any pool map, **When** it regenerates, **Then** it keeps its households, form, field kind and acreage band, and
   every gate rule passes.

### User Story 3 - Larger fields cost proportionally (Priority: P2)

The GM: the savings "will become more relevant as we make larger settlements that have more fields and larger fields".

**Independent Test**: the field's time at 10 and at 20 households (the hamlet generator's band), current against new.

**Acceptance Scenarios**:

1. **Given** Inashiro's brief at 10 and at 20 households, **When** both are built, **Then** the new field's advantage at 20 is
   at least its advantage at 10 (it does not shrink as the field grows).

### Edge Cases

- A sector too narrow for a column, or a fork wedge thinner than a plot: the partition yields a sliver, which is merged into
  its neighbor at construction (today: absorbed by the repair).
- The toe, where the rows meet the drain's bank at an angle: the partition's last cells are irregular and are kept as small
  irregular paddies where they hold the ring rules, merged where they do not (the research: a real fan's wedges "were terraced
  into small IRREGULAR paddies, and the odd unplantable scrap was simply taken into the basin beside it", `seams/close.py`).
- A trial size whose region is in the acreage band but whose partition cannot hold the ring rules: the fit takes the next
  admissible size, as `_finish_first_admissible` does today.
- A fan with no admissible size: the site is refused (`FieldRefused`), unchanged.
- The polder (Kuwabata) and the hill engines: not comb fields; out of scope and unchanged.

## Requirements *(mandatory)*

### Functional Requirements

**Phase 0 - the go/no-go measurement (before any engine change)**

- **FR-001**: A prototype of the field built by construction MUST be written under `specs/302-field-by-construction/` and run
  through `make`; it MAY import the engine and MUST NOT change any engine, pool or test file.
- **FR-002**: The prototype MUST start from the same inputs the current field starts from - the skeleton the carve builds
  (canals, threads, drain and its bank) for each trial size - so the two are compared on identical ground.
- **FR-003**: The prototype MUST build the whole field the engine would hand on - the fitted size, the plots tiling the planted
  region, the acreage - and its plots MUST be judged by the engine's own ring rules (`ring_violations`) and its own acreage
  band (`field_acres_in_band`), not by restated copies.
- **FR-004**: The comparison MUST time the current fit-and-finish and the prototype's fit-and-build on the same inputs, back to
  back, fastest of three each, and report per input and in total.
- **FR-005**: The GO / NO-GO verdict MUST be computed from the measurement by SC-001 to SC-004 and recorded in `research.md`
  with its numbers before any engine file changes. On NO-GO the feature stops: nothing else lands, and the GM is told what
  was measured and why it fell short.

**Phase 1 - the engine (only after GO)**

- **FR-006**: The comb field MUST be built as a region partitioned into plots: the planted ground computed once per fan, cut
  by the row and column bunds so every plot shares each bund with whatever lies across it, with no pass that finds bare ground
  afterward. The seam repair (`close_seams` and the pocket machinery it drives) is retired for comb fields wherever the new
  construction makes it unreachable, and deleted where nothing else calls it.
- **FR-007**: The fit's trial sizes MUST be scored on the region (its acreage and its water's legality) without cutting plots,
  and the carve-time acreage prediction (`CombCarve.planted_area`) retired with the repair it predicted.
- **FR-008**: Every ring rule `ring_violations` enforces today MUST hold on every finished plot, resolved at construction by
  merge or split; the two rules recorded and not enforced (width, dart) stay as they are.
- **FR-009**: What a comb field IS stays: water first (the canals and threads laid before the plots), rows along the contour
  with the wander between them, columns across each sector, the head row on the supply canal and the closing rank on the
  drain, the toe's small irregular paddies, the dry hem, the bund beans, the supply- and collector-bank clearances, and the
  acreage band. Maps may move within the rules (GM 2026-09-30, feature 297: "They do NOT need to remain identical in output").
- **FR-010**: The smaller levers on record (an area sum in place of the union; fewer trial carves) are adopted where they still
  apply to the new construction and dropped, with the reason recorded, where the redesign removes what they acted on.
- **FR-011**: Every engine change keeps the `100%` coverage floor, and every test of the retired machinery is either moved to
  what replaces it or retired with the rule it held carried by a test of the construction.

### Key Entities

- **Planted region**: the command area of one fan less its water (canals, drain, their banks) - what the plots must tile.
- **Partition**: the planted region cut by the row and column bunds into cells; adjacent cells share the bund between them.
- **Trial size**: one scale of the fan in the fit's search; scored by its region.
- **Recorded input**: one hamlet brief and seed whose skeleton both builders start from in the Phase 0 comparison.

## Success Criteria *(mandatory)*

### Measurable Outcomes

**The go criteria (Phase 0) - all four must hold for GO:**

- **SC-001**: The prototype's fit-and-build is at least **2x** faster than the current fit-and-finish, as the total over the
  recorded inputs (the comb hamlets of the pool and Inashiro's brief at 10 and 20 households).
- **SC-002**: The prototype's advantage at 20 households is at least its advantage at 10 (User Story 3).
- **SC-003**: Every prototype field lands its acreage band, leaves no bare ground in its planted region (under `0.5%` of its area,
  the rounding of recorded rings), shares every bund, and has no plot with a `ring_violations` finding.
- **SC-004**: The prototype builds every structure FR-009 names that the field stage's time covers, so the speed is not bought
  by leaving work out; any part the prototype stubs is named, and its current cost is added to the prototype's time.

**The landed feature (Phase 1):**

- **SC-005**: The field stage on the pool's comb hamlets is at least 2x faster than at this feature's base, base and clone back
  to back, fastest of three.
- **SC-006**: Every pool map regenerates green: every gate rule, households, form, field kind and acreage band kept.
- **SC-007**: No pass after the partition looks for bare ground in a comb field (a test holds it: a finished comb net has no
  bare ground and the seam repair is not called).
- **SC-008**: `make done` green with the `100%` floor.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

- **The go threshold is 2x** (a project choice, not a map decision: the GM's "appreciably better" made measurable). Why 2x:
  below it the redesign saves under about 0.65 s of Inashiro's 1.2-1.5 s field (observed 2026-10-01, method: `make map
  PROFILE=1`, three runs) for a large engine change; 297's levers delivered 1.14x against an expected "well under half", so
  the threshold is set where a disappointment still pays. Recorded here so the verdict is computed, not argued.
- **Every scrap of the command area planted, every bund shared**: unchanged - historically accurate, the research `seams/close.py`
  carries (a real fan "wasted nothing"); this feature changes how that state is reached, not the state.
- **Maps move within the rules**: map drawing convention, by the GM's standing ruling (2026-09-30).

## Assumptions

- The prototype may reuse the engine's skeleton builders as they stand (they are the inputs, not the thing being replaced);
  only the carve's plot cutting, the repair and the prediction are rebuilt.
- The recorded inputs are the four comb hamlets in the pool (Inashiro, Kashikawa, Mizuguchi, Sawada) and Inashiro's brief at
  10 and 20 households; Kuwabata is a polder and out of scope.
- The hamlet generator's band is 10-20 households, so nothing larger can be rolled; SC-002 reads the trend inside that band.
