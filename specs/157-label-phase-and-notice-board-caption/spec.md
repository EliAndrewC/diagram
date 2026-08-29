# Feature Specification: the label phase, and a notice-board caption that stands beside its board

**Feature Branch**: `157-label-phase-and-notice-board-caption` (no branch - `export SPECIFY_FEATURE=157-label-phase-and-notice-board-caption`)

**Created**: 2026-08-29

**Status**: Draft

**Input**: The GM's request, verbatim, is in [`request.md`](request.md). In short: *"add a phase at
the very end of every settlement creation process, which is putting down the labels for things ...
First, by moving label placement so that the notice board itself is placed during a separate phase
than the labels for the map are placed ... and then second to correct the placement of the notice
board label so that it is actually directly next to the notice board itself."*

## Why this is not a one-line tweak

The GM's own reason: *"getting the notice board labeling correct is important because the code that
we write to apply labels will be generally reused for other map features on other types of
settlements once we get to them."* The notice board is the only labeled feature on a hamlet, so it
is the whole of the label subsystem's test surface today - and whatever it does is what a town's
twenty captions will do.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - the caption stands beside the board it names (Priority: P1)

The GM looks at Kuwabata. The notice board's caption is aligned with the board and stands off it by
about the right distance, but it sits well to the RIGHT of the board rather than beside it - the
board is not even over the caption's own run, so the reader's eye has to travel along a line of text
to find what it names. The GM wants the caption directly next to the board.

**Why this priority**: it is the defect the GM saw on a shipped map, and it is the behavior every
future captioned feature will inherit.

**Independent Test**: regenerate Kuwabata and measure, in the manifest, where the board's center
falls relative to the caption's own run. Today it falls off the end of it; after this feature it
falls within it.

**Acceptance Scenarios**:

1. **Given** Kuwabata's notice board at its recorded seat, **When** the map is regenerated,
   **Then** the caption stands directly beside the board - the board's center projects onto the
   caption's baseline INSIDE the caption's own extent, not past its end.
2. **Given** any pool map at hamlet or village scale, **When** it is regenerated, **Then** its
   notice-board caption satisfies the same rule, or the map records that no legal seat does.
3. **Given** a board whose every close seat genuinely laps a house or stands on a lane tread,
   **When** the seat is chosen, **Then** the caption still clears both - legibility rules are not
   traded away to get the caption closer.

---

### User Story 2 - labels are placed in their own final phase (Priority: P1)

Every settlement's generation ends with one phase whose only job is putting the labels down. Feature
placement finishes first - on a hamlet, the notice board is the last feature - and only then are
captions seated, so every caption is chosen against the finished map.

**Why this priority**: the GM asked for it *"right now, because this will matter later"*. It is the
structure the many-label tiers will be built on, and it costs nothing to establish while there is
one label to move.

**Independent Test**: the hamlet pipeline lists a label phase after the notice-board phase, and a
map generated with the notice board placed but the label phase not yet run has the board's glyph and
no caption.

**Acceptance Scenarios**:

1. **Given** the hamlet pipeline, **When** its stages are listed, **Then** the last stage places
   labels and the stage before it places the last map feature.
2. **Given** a settlement built by a generator that has no stage pipeline (a hand-authored town or
   city script), **When** it is finished, **Then** its labels are still placed, in the same label
   phase, with no change to the script.
3. **Given** the reference hamlet, **When** it is regenerated, **Then** moving the caption out of
   the notice-board phase and into the label phase does not by itself move any caption: on a hamlet
   nothing is placed between the two, so the label phase sees exactly the map the old inline seat
   search saw.

---

### Edge Cases

- **No legal seat anywhere.** A board hemmed in on every side keeps today's behavior: the least-bad
  seat is taken and the caption is still drawn. A map is never shipped with an unlabeled board.
- **A hand seat is TWO unlike things, and only one of them is a decision.**
  - A hand seat that records a GM RULING is honored exactly, as today - Hoshizora's
    `label_xy=(1760, 195)` on the Imperial Road (*"GM 2026-08-08"*), Nagahara's boundary stone
    (*"the stone keeps its verge, GM 2026-08-10"*). The GM asked to correct the placement
    ALGORITHM, and a GM ruling is not the algorithm.
  - A hand seat that exists only as a WORKAROUND for the placer misplacing the caption is not a
    decision, and this feature REMOVES it so the fixed placer seats the caption. Two are known:
    Minami's `place_punishment_spot(label_xy=(1270, 1454))`, whose own comment says *"the
    auto-caption sat 106 px east of its own spot"*, and Nagahara's
    `kosatsuba(1492, 1341, rot=0, label_xy=(1530, 1329))`, which is the GM's reported defect
    preserved by hand on a city map. Leaving them would let the acceptance surface go green while
    the defect the GM reported still stands on the tier whose future reuse is the reason for the
    work.
- **A board at a square rotation.** Its caption is level; the "beside, not past the end" rule is
  measured on the same axes and means the same thing.
- **A generator that never runs the label phase.** Impossible by construction: the phase is also
  the last thing the finish step does, so a queued label cannot be dropped.
- **Two captions wanting the same ground.** Out of scope for this feature (see Assumptions) - with
  one label on the map there is nothing to arbitrate.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every settlement's generation MUST end with a LABEL PHASE that runs after every map
  feature has been placed. On a hamlet that means after the notice board, which is the last feature.
- **FR-002**: EVERY feature that carries a caption MUST place its glyph in its own phase and leave
  its caption to the label phase - the notice board, the punishment ground, the execution ground,
  the boundary stone, the theater stage, the ossuary mound, the road caption and every other
  captioned feature the engine draws. The GM's words are *"labels for whatever map features get
  labels"*, and an earlier draft of this requirement said "the notice board is the case that exists
  today", which is simply false: `place_punishment_spot` runs its own seat search, `finish()`
  already defers several captions with a documented drain order, and Nagahara's manifest carries
  five auto-seated captions besides the board. The remit is every caption, with no per-feature
  exception.
- **FR-002a**: The deferral MUST be GENERAL rather than per-feature - the engine's caption
  primitive queues while the phase is pending, so a captioned feature is covered the day it is
  drawn and cannot be forgotten. This is the same reasoning `label_blocker_quads` records for
  deriving its blocker list rather than hand-listing it: *"a probe that cannot see a feature looks
  exactly like a probe that passes"*.
- **FR-003**: The label phase MUST seat each caption against the FINISHED map - every feature drawn,
  the frame decided, and every caption already seated in this phase counted as an obstacle.
- **FR-004**: A generator with no stage pipeline (the hand-authored town, city and village scripts)
  MUST get the same label phase with no change to the script: the finish step runs it as the last
  thing it does, and a phase already run is a no-op.
- **FR-005**: The label phase MUST drain in a documented, deterministic order, and that order MUST
  keep today's rule that the most-constrained caption is seated first and the road caption last.
- **FR-006**: A caption MUST be seated DIRECTLY BESIDE the feature it names: among the seats that
  are legal, the one whose displacement ALONG the caption's own baseline is smallest wins, and the
  standoff perpendicular to it breaks the tie. Displacement along the baseline and standoff across
  it are not interchangeable, and ranking seats by straight-line distance alone treats them as if
  they were - which is what put Kuwabata's caption 39 px off to one side.
- **FR-007**: The seat search around a TILTED subject MUST sample the ground around it finely enough
  in both axes to find a legal seat beside the subject where one exists. Measured on Kuwabata: the
  present search samples 5 standoffs x 3 lateral offsets, and the nearest legal seat directly below
  the board lies between two of its rungs.
- **FR-008**: The structural-legality term of the seat search MUST measure the caption's TRUE
  ROTATED QUAD against each obstacle, not the axis-aligned bounding box of that quad. (Defect found
  in the course of this work, fixed under Principle XIV - see Success Criteria SC-004.)
- **FR-009**: A new gate check MUST hold FR-006: a caption may not stand further along its own
  baseline from the thing it names than that thing extends, plus the standoff air. The check reads
  the caption's recorded REFERENT box, so a second requirement comes with it - **every notice-board
  caption MUST record one**, and the check MUST fail a map whose board caption records none rather
  than skipping it. (Nagahara's manifest carries a six-element notice-board record with no referent,
  frozen before the engine started passing one; its caption stands 38.0 px right of its board with
  the board 11.6 px outside the caption's own run - the identical defect on a city map, invisible to
  any rule keyed on a referent. The sweep regenerates it; the "must record one" clause is what stops
  a future map going quiet the same way.) The check MUST be proven to fire by a frozen negative
  fixture built from the current Kuwabata manifest.
- **FR-010**: No existing gate check may regress. `label_hugs_its_referent`,
  `captions_clear_the_ways_they_stand_on`, `labels_clear_of_other_buildings` and
  `labels_within_image` stay green across the whole pool and the cohort.
- **FR-011**: The seat search's LANE clearance term already reads the quantity
  `captions_clear_the_ways_they_stand_on` reads, and MUST still read it after this feature - a
  non-regression property, not a new requirement. It is stated here because the structural fix in
  FR-008 sits three lines away from it and the two were confused once already: an earlier draft of
  this requirement demanded a lane-scoring change that had in fact landed four attempts ago
  (recorded in the code as *"READS THE LANE'S EDGE, THE SAME QUANTITY
  `captions_clear_the_ways_they_stand_on` READS - and it did not, for four attempts"*). Held by
  SC-007.

### Key Entities

- **Label phase**: the final phase of a settlement's generation. Takes the queued captions and seats
  them against the finished map. Idempotent - running it twice places nothing twice.
- **Queued caption**: a caption a feature has asked for but not yet placed - its text, its subject's
  footprint and rotation, its type size and color, and any hand seat its generator gave it.
- **Seat**: a candidate position for a caption, described by its displacement ALONG the caption's
  baseline (lateral) and its standoff ACROSS it (gap), measured in the subject's own frame.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On Kuwabata the notice-board caption stands beside its board: the board's center falls
  within the caption's own run. Measured today: the caption's center is 36.3 px right and 5.4 px up
  from the board, a lateral displacement of ~34.6 px against a caption half-run of 26.9 px - the
  board is past the end of its own label.
- **SC-002**: The caption's standoff from the board does not grow to buy that: it stays inside the
  cap `label_hugs_its_referent` allows (3 x the type size), as it does today.
- **SC-003**: Every hamlet, village, town and city map in the pool regenerates with the whole gate
  green, and the 48-seed cohort's pass rate does not fall.
- **SC-004**: The structural probe agrees with the geometry it claims to measure. Measured today on
  Kuwabata: the seat directly below the board at the 11 px rung is called blocked by a house, and
  its true rotated caption quad clears the nearest structure by 4.43 px - the probe inflates a
  54 x 10 px caption to a 52 x 34 px box.
- **SC-005**: A reader of the finished map can tell what the caption names without following a line
  of text to its end - the board is under (or over) the words that name it.
- **SC-006**: Removing the new check from the battery turns a test red (the negative fixture), so
  the rule is proven to have teeth rather than assumed to.
- **SC-007**: The seat search's lane-clearance term still measures the lane's EDGE, as
  `captions_clear_the_ways_they_stand_on` does - proven by the existing test that pins it, still
  green.
- **SC-008**: No caption anywhere in the engine is drawn outside the label phase. Measured
  structurally rather than by inspection: with the phase pending, the caption primitive draws
  nothing, so a caption emitted early would be missing from the finished map and every
  caption-reading check would say so.

## Decisions Recorded *(mandatory)*

This feature is entirely a MAP CONVENTION - it changes where a caption is drawn, not what the map
claims about how a place was built. Every row below is therefore a **deviation** in constitution
XII's sense: a deliberate rendering choice made for legibility, with nothing physical behind it. No
row is a finding, and no row is a guess. Nothing here is a research question, so no research pass is
owed (the ladder in CLAUDE.md: research first - but only for questions about how a place was built,
farmed, planted or lived in, and none of these are).

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Labels are placed in a phase of their own, after every map feature | **deviation** (rendering convention) | *"how we place labels will always depend on what else is on the map"* (GM 2026-08-29) - a caption seated before the map is finished is judged against half a map, which is the same reasoning that already defers `place_caption` to the finish step | `hamletgen/driver.py` STAGES comment; `settlement/structures/captions.py::place_labels` docstring; `dev/placement.md` DRAW ORDER map |
| A caption is seated beside its subject: least displacement ALONG its own baseline first, standoff across it as the tie-break | **deviation** (legibility) | a caption slid along its own baseline reads as naming something else - the board ends up past the end of its own label - while the same distance taken as standoff still reads as "beside". Straight-line distance cannot tell the two apart, and ranking by it is what shipped Kuwabata's caption 34.6 px off to one side | comment at the seat search in `settlement/structures/fixtures.py`; gate check `caption_stands_beside_its_referent` |
| The seat search around a tilted subject samples finely in both axes | **deviation** (legibility) | measured: the coarse 5 x 3 ladder steps straight over the pocket of legal ground directly below Kuwabata's board (legal at a 14 px standoff; the ladder samples 11 and 16) | comment at the ladder in `settlement/structures/fixtures.py` |
| The structural probe measures the caption's true rotated quad | **deviation** (a probe that measures what its check measures) | the AABB of a rotated quad inflates a 54 x 10 px caption to 52 x 34 px, so the probe refuses ground the caption clears by 4.4 px. This engine's oldest rule: the placer and its check read one source | comment at the probe in `settlement/structures/fixtures.py` |

## Assumptions

- **Caption PRIORITY is out of scope, deliberately.** The GM described it and then ruled it out for
  this map: *"When we begin putting labels on maps that have many labels, we can assign a priority
  to each type of thing ... However, that will not apply here."* This feature therefore builds the
  phase and NOT a priority scheme. The label phase drains in a documented deterministic order, so
  priority becomes one additional sort key on the day a map has competing labels - that is the
  extension point, recorded, not built.
- **"Every settlement creation process"** means both shapes the engine has: the hamlet's stage
  pipeline, and the hand-authored gen scripts of the village, town and city tiers. Both get the
  phase; only the first gets a named stage, because only the first has stages.
- The notice board stays the LAST map feature placed on a hamlet (GM 2026-08-29, feature 154). This
  feature moves its CAPTION out of that phase; it does not move the board.
- Town and city maps place their notice board mid-script, so deferring its caption to the label
  phase will move that caption on those maps. That is the intended consequence of the GM's rule, not
  a regression - it is the caption now seeing features that were drawn after the board.
- Scale is unlocked and remote is off (`dev/switches.json`), so the pool sweep this feature owes can
  actually be run locally.

## Review record

**Round 1** (`spec-fidelity`, 2026-08-29): CHANGES REQUIRED, four items. All four accepted and
applied - FR-002/FR-002a (the phase's remit is every caption, and the earlier "the notice board is
the case that exists today" was false), the hand-seat edge case split into a GM ruling and a
workaround with the two workarounds named for removal, FR-011 restated as the non-regression
property it actually is with SC-007 behind it, and FR-009 given the "every notice-board caption
records a referent" clause that stops the rule going quiet on a manifest like Nagahara's. The agent
also confirmed as faithful, and untouched: FR-006, FR-007, FR-008, FR-010, the exclusion of caption
priority, and the reading of *"every settlement creation process"* as covering both the hamlet
pipeline and the hand-authored gen scripts.

**Round 2** (`spec-fidelity`, 2026-08-29): **FAITHFUL**. Every clause of the request is carried and
nothing is missing; the general deferral was checked against the code rather than taken on trust
(54 `self.label(...)` emit sites against 5 `place_caption(...)` ones, so `label()` is the real
caption primitive and queuing there reaches them all); the hand-seat split and the removal of the
two workaround seats were adjudicated separately and both held in scope; the only
exception-shaped clause left (a board with no legal seat anywhere) was adjudicated as a
physical-impossibility case the GM himself conditioned the ask on (*"there is plenty of empty
space"*). Three asides, all folded into the task list rather than the spec:

1. **Eight** pool manifests carry six-element notice-board records with no referent, not one -
   `enokida`, `honda`, `yatsuda`, `tanada`, `hirameki`, `minami`, `nagahara`, `tango`. The sweep
   SC-003 requires must regenerate all of them.
2. The FR-009 check must NOT honor a placer-written "no legal seat" record. A check that reads the
   placer's own verdict is graded by the thing it grades - the hazard FR-002a itself quotes.
3. Two caption paths emit raw text without going through the caption primitive
   (`fields/paddy.py` `paddy_field(label=...)` and `water_field(label=...)`; dormant - no pool map
   passes either today). SC-008 as written already covers them; the implementation routes them
   through the phase so the coverage is structural rather than incidental.
