# Feature Specification: the kosatsuba's placement is a knob, not one objective

**Feature Branch**: none (this project uses `SPECIFY_FEATURE`; CLAUDE.md, GM 2026-07-27)

**Created**: 2026-08-29

**Status**: Draft

**Input**: The GM, 2026-08-29 - *"you should go ahead and implement the notice board task yourself"*,
after pushing back on my claim that it needed research first: *"I thought that our notice board
already was well researched? I would be really surprised if you actually need another research pass
for it."* Their words in full, with the research they were pointing at, are in `gm-request.md`.

## Why this exists

`place_kosatsuba` sites the board by ONE objective - the busiest node among the ways that are not
flagged `web`. The research it is meant to implement names FIVE attested placements, and the busiest
node is only one of them. Two consequences, both measured on shipped maps:

1. **Variance is thrown away.** Principle XII: where the record supports more than one form, the rule
   is a knob rolled from the map's own seed, never a session picking the reading it prefers. Five
   attested placements is five ways two hamlets can honestly differ, and today every hamlet gets the
   same answer to a question the record answers five ways.
2. **A single objective picks seats the record does not attest.** Sawada's board stands 9.0 ft off an
   **81.7 ft dead-end spur** whose far end is 70 ft from any other way: **7 of 19** dwellings within
   250 ft where the busiest point on the web has **13**. A cul-de-sac head is not a center, an
   entrance, a bridgehead, a shrine precinct or an official's frontage. It is outside what the record
   attests - not at one end of a supported range.

The research is already done, READ and cited (feature 133 T13, four sources). **This feature adds no
research.** It implements what is on file.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Two hamlets put their board in different places, for reasons the record attests (Priority: P1)

A reader opening two hamlet maps finds the board in materially different positions - one on the
frontage where the village gathers, another at the approach where the track enters - and the
interactive map can tell them which attested placement each is and why.

**Why this priority**: it is the whole point. Maps exist for players who must tell one settlement
from another at a glance, and this is a place the record permits difference.

**Independent Test**: roll one map per knob VALUE (the feature owes one map per value, not a cohort -
CLAUDE.md) and confirm the board's seat differs between them by more than its own glyph.

**Acceptance Scenarios**:

1. **Given** two hamlets whose seeds select different placements, **When** each is rolled, **Then**
   their boards sit at positions answering to different anchors, and each map records which.
2. **Given** one hamlet rolled twice from the same seed, **When** the manifests are compared,
   **Then** the placement and the seat are identical - the knob is seeded, not random.

---

### User Story 2 - The board never stands somewhere the record does not attest (Priority: P1)

**Why this priority**: this is the defect on the sheet today. It is independently valuable even if
only one placement is ever selected.

**Independent Test**: on Sawada, confirm the board no longer sits at the head of a dead-end spur.

**Acceptance Scenarios**:

1. **Given** a settlement with a short dead-end spur off its network, **When** the board is sited,
   **Then** the spur head is not chosen while any seat answering the selected placement exists.
2. **Given** any settlement, **When** the board is sited, **Then** it still stands ON a way at the
   recorded verge distance - every attested site is a verge, a gate front or a bridge foot.

---

### User Story 3 - A map is only offered placements it actually affords (Priority: P2)

**Why this priority**: a placement the map cannot site is worse than one not offered - the board would
either fail to be placed or land somewhere arbitrary.

**Independent Test**: build a settlement with no recorded connector, and one with no house carrying
`role == "headman"`, and confirm the selection never returns the placement each lacks.

**Acceptance Scenarios**:

1. **Given** a settlement with no connector recorded, **When** the placement is rolled, **Then** the
   entrance/approach is not selected.
2. **Given** a settlement with no house carrying `role == "headman"`, **When** the placement is
   rolled, **Then** the official's frontage is not selected.
3. **Given** a settlement affording no placement but the center, **When** the placement is rolled,
   **Then** the center is selected and the board is still sited. This is not hypothetical: 5 of the
   13 pool hamlets record no connector, so they afford one placement and get no variance - which is
   what Principle XII asks, since the knob applies where the record supports two forms FOR THAT
   SETTLEMENT.

## Requirements *(mandatory)*

- **FR-001**: The settlement MUST select its kosatsuba placement from the placements ATTESTED in
  `research/urban-features.md` that the map AFFORDS. Five are attested; three are afforded at these
  tiers and are what this feature offers - the center / assembly place, the entrance / approach, and
  the frontage of the official's house. The bridgehead and the shrine precinct are attested but are
  NOT offered at the hamlet and village tiers, for the measured reasons in "Decisions Recorded"; they
  MUST NOT be synthesized out of ditch planks or dooryard hokora.
- **FR-002**: The placement MUST be rolled from the map's own seed, deterministically, so the same
  seed yields the same placement, and MUST NOT perturb any other rolled value on the map.
- **FR-003**: A placement the map does not afford MUST NOT be selected. Affordance is read from the
  manifest the validator reads (the same-source doctrine), never assumed.
- **FR-004**: Every placement MUST keep the board ON a way at the recorded verge distance
  (`KOSATSUBA_VERGE_FT`), preserving `kosatsuba_by_the_road` and the caption machinery unchanged.
  The placement chooses WHICH way and WHERE along it; it never moves the board off the verge.
- **FR-005**: The selected placement MUST be recorded in the manifest so the interactive map, the
  checks and a later reader can all name it, and MUST be classed accurate / deviation / guess with
  its sources, per constitution XII.
- **FR-006**: A dead-end spur MUST NOT be preferred over a seat answering the selected placement.
- **FR-007**: This feature proceeds on `research/urban-features.md` AS IT STANDS. A research pass is
  NOT a precondition, and the placement question MUST NOT be treated or recorded as unresearched -
  that was the GM's correction. It is not a ban: they said in the same breath *"I don't object to doing
  more research"*, so if a decision arises that the existing record does not answer, the standing rule
  applies unchanged - search first, and escalate only where the record is silent or contradictory.
- **FR-008**: `sawada.notes.md`'s OPEN entry MUST be closed with the measured outcome, and the
  research doc's placement bullet MUST gain the pointer to the knob that implements it.
- **FR-009**: The knob MUST apply at `scale in ("hamlet", "village")` ONLY. Town and city boards keep
  their present seats. This is a REQUIREMENT and not an assumption because the code contradicts the
  obvious assumption: `pool/towns/hirameki.gen.py:475` calls `place_kosatsuba()`, so a town does go
  through this siter, and Hirameki's recorded board position MUST NOT move.

### Key Entities

- **Placement**: one attested kind of site, with an ANCHOR derived from the manifest (a point or set
  of points) and an affordance test.
- **Anchor**: what the placement is measured to - the dwelling centroid, the connector's mouth, a
  crossing, a shrine, the official's house.

## Success Criteria *(mandatory)*

- **SC-001**: On Sawada, the board's dwellings-within-250-ft count rises from 7 of 19, OR the board
  stands at a seat answering a named attested placement other than the center; the spur head is not
  the seat either way.
- **SC-002**: Rolling one map per knob value produces at least two materially different board seats
  (further apart than the board's own drawn width).
- **SC-003**: Every live pool map still passes `kosatsuba_by_the_road` and `kosatsuba_on_a_main_way`,
  and the gate is green.
- **SC-004**: Re-rolling any map from its seed reproduces its placement and seat exactly.
- **SC-005**: Hirameki's recorded board position is byte-identical before and after.
- **SC-006**: The seat chosen for the busiest node is measured to hold the board AND its caption, or
  the fallback is taken and reported. `sawada.notes.md` makes this its own precondition - the Ubame
  lesson is that the caption is much larger than the glyph, so a siter denied a quiet spur can walk to
  the next empty verge rather than to the busy one. FR-004 keeps the caption machinery unchanged, so
  this is a measurement to take, not machinery to build.

## Decisions Recorded *(mandatory - this feature changes what a map draws and states)*

The five placements, each with its evidence class and its AFFORDANCE as MEASURED across the live pool
(13 hamlets, 4 villages, 1 town) on 2026-08-29. Measuring first is what removed this spec's only guess.

| placement | class | affordance, measured | offered? |
|---|---|---|---|
| the center / where villagers assembled | **accurate** - *"at the village center ... or the place where villagers assembled"* | every map has dwellings | always |
| the entrance / approach | **accurate** - *"the entrances and centers of towns and villages"* | a recorded connector: 8 of 13 hamlets | where a connector exists |
| the official's frontage | **accurate** - *"before the gate of the village officials' houses"*, and for a hamlet the record names *"the senior farmer answering to the village headman"* | `role == "headman"` is recorded on exactly one house in each of the 4 villages and on NO hamlet house | where the manifest records one |
| a bridgehead | **accurate but NOT AFFORDED at these tiers** - *"at bridgeheads"*, *"the foot of large bridges"* | every hamlet records 4-17 crossings, but they are **9.8-10.5 ft planks, 2 ft wide**, over field ditches | no - see below |
| the shrine precinct | **accurate but NOT AFFORDED at these tiers** - *"the shrine precinct"* | only 3 of 13 hamlets carry a shrine at all, and it is a `farm_fixtures` **household hokora** in a dooryard | no - see below |

**Two placements are attested and deliberately not offered, which is a decision and not an oversight.**
A 10 ft plank over a field ditch is not "the foot of a large bridge", and a household hokora in a
dooryard is not "the shrine precinct" where a village assembles. Pressing either into service would
reach five placements by relabeling things the record does not mean - an unlabeled guess wearing a
finding's clothes, which constitution XII names as the one failure. They stay in the table because
they become real at the town and city tiers, where a bridgehead and a shrine compound both exist.

**THE GUESS THAT WAS AVOIDED, recorded because the near-miss is instructive.** An earlier draft
proposed approximating the official's house by the settlement's LARGEST dwelling where no headman is
recorded, labeled a guess. Measurement retired it: across the 13 pool hamlets the largest and
second-largest dwellings differ by **1.00 to 1.14x**, and on several they are identical - so "largest"
would have been picking a house very nearly at random and calling it the headman's. The manifest
answers the question directly instead (`role == "headman"`), which is the same-source doctrine and
needs no guess.

**Withheld because it cannot be SITED, not because the official did not exist** - the distinction
matters, and an earlier draft of this section got it backwards. The record puts the person IN the
hamlet: *"the headman (or in a hamlet the senior farmer answering to the village headman) received,
copied, and relayed the circulars"* - local person, upward authority. What is missing is not the
official but a HOUSE for them: no hamlet manifest records `role == "headman"`, and the measured proxy
is arbitrary. Writing that up as "a hamlet has no such official" would have dressed a data limitation
in a finding's clothes, in the very section that feeds the interactive map's accurate / deviation /
guess labeling - constitution XII's one named failure. If hamlet manifests ever record the senior
farmer's house, this placement becomes affordable there with no change to the placement rule - but a
session doing that must also revisit `hamlet_has_no_headman`
(`check_village/segments_03c_clusters_and_labels.py:159`), which actively FORBIDS that field at hamlet
scale today. Recorded so the next reader does not have to discover it.

## Assumptions

- Where a selected placement affords no seat that fits, the siter falls back rather than returning
  None - a board that is placed and reported beats a map with no board, which is the ruling
  `place_kosatsuba` already follows.
- The `hamlet_has_no_headman` check keys on `role == "headman"`
  (`segments_03c_clusters_and_labels.py:149`). This feature READS that field and never writes it, so
  it cannot disturb that check.


## Review history

- **2026-08-29, `spec-fidelity` round 1 - CHANGES REQUIRED (5), all taken.** (1) FR-007 turned the GM's
  correction into a prohibition, contradicting their own *"I don't object to doing more research"* and
  inverting the standing research-before-a-ruling rule; rewritten as a released precondition. (2) SC-005
  made a legitimate citation into a test failure; replaced. (3) The Assumptions section claimed towns
  keep hand placement and the code says otherwise - `pool/towns/hirameki.gen.py:475` calls
  `place_kosatsuba()`; now FR-009, a requirement, with Hirameki's seat pinned by SC-005. (4) The
  mandatory "Decisions Recorded" section was missing; added, with each placement's evidence class.
  (5) British spelling at four places; fixed. The reviewer ADJUDICATED the knob framing FAITHFUL rather
  than a session's design choice - constitution lines 1135-1140 make a knob the compliant answer where
  the record supports distinct FORMS, so picking one placement would have been the violation - and
  accepted the largest-dwelling proxy as a labeled guess.
- **2026-08-29, `spec-fidelity` round 2 - CHANGES REQUIRED (2), both taken.** (1) User Story 3 still
  described a five-placement world and contradicted the narrowed FR-001 - its fixtures would have
  commissioned selection logic and tests for two placements FR-001 forbids; rewritten around the
  affordances that exist at these tiers. (2) **The Decisions Recorded section inverted the record**: it
  said a hamlet's board answers to a senior farmer of a village elsewhere, where
  `research/urban-features.md` puts the senior farmer IN the hamlet, answering upward. That is a data
  limitation written up as a historical finding, inside the section that feeds the interactive map's
  labeling - the failure constitution XII names. Corrected to the honest ground: the placement is
  withheld because no hamlet manifest records a house for the official, not because the official did
  not exist. The reviewer also adjudicated the narrowing to three placements FAITHFUL, on a stronger
  basis than I had argued it - `research/urban-features.md:23` carries the doc's own SETTLEMENT-scale
  sentence, "by the headman's frontage or the lane junction/entrance", so the five-item list at :26-29
  is the bakufu's general catalog across barriers, ports and bridges, not a roster every village had.
- **2026-08-29, measurement between rounds.** The proxy the reviewer was willing to accept was retired
  instead: the pool's largest and second-largest dwellings differ by 1.00-1.14x, so it would have been
  arbitrary, while `role == "headman"` is recorded outright on one house in each village. The affordance
  survey also cut the offered set from five placements to three, on the ground that a 10 ft ditch plank
  is not a bridgehead and a dooryard hokora is not a shrine precinct. Both are in "Decisions Recorded".
