# Feature Specification: Bamboo held out of a yard's or bed's sun

**Feature Branch**: `315-bamboo-in-the-sun` (no branch - committed on `main` in the clone)

**Created**: 2026-10-02

**Status**: Draft

**Input**: The GM, 2026-10-02 (verbatim in `request.md`): *"figure out whether it would need to be far away and then make
it be the distance away that it would have to be if that is appropriate. On the other hand, if you look it up and you find
that it deserves to be on the exempt list, then we can keep it on the exempt list."*

## Context (observed 2026-10-02)

Feature 310 holds every canopy tree out of a threshing yard's or garden bed's SUN GROUND: the plot widened east and west
and deepened south by a reach, from its north edge down. Each thing that casts a shadow keeps its own distance, worked out
from its height and where the late-autumn sun stands (`research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html`):
a neighbor's farmhouse, reckoned at a 20 ft ridge, keeps the south strip; a canopy tree, reckoned at the least height the
record gives a working windbreak's tree, keeps the canopy reach east, west and south. Bamboo was left out on the GM's
earlier "maybe bamboo", which the GM now says was not a ruling.

**What the research says.** Bamboo is not low. Madake, the timber bamboo a farm kept for its baskets and its building, has
culms of 10-20 m, and hachiku 10-15 m (to be cited from the pages read in the plan's research pass); the record's bamboo page
already has madake reaching "roughly 20 m" and growing in close thickets that shade out almost everything else
(`research/questions/0075-bamboo-groves-chikurin.html`). A bamboo stand at its least height is as tall as the tree the
canopy reach is worked out from, so the same derivation gives it the same reach. Bamboo therefore does not deserve the
exempt list, and its distance is the one its height gives.

**Where bamboo stands on our maps** (one-shot count, observed 2026-10-02; method: the recorded stands' outlines and the
culm marks parsed from each SVG, each tested against every plot's sun ground at the canopy reach):

| bamboo | recorded today | on the five pool hamlets | in a plot's sun ground |
|---|---|---|---|
| a household's own stand, and a shared thicket | yes, as stands | 3 stands | none |
| culm marks in a farm grove's windward bands | no | part of 329 marks | none |
| culm marks among a windbreak's or belt's clumps | no | part of 329 marks | none |

So no pool map draws bamboo in a plot's sun today, but nothing holds it there: the marks are placed without the sun test
(feature 310 skipped it for them by name), and two of the three kinds are not recorded, so no check can see them.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - No bamboo shades a threshing yard or a garden bed (Priority: P1)

The GM opens any generated hamlet and every threshing yard and garden bed has open sky to its east, west and south, bamboo
included, at the distance bamboo's height gives.

**Why this priority**: it is the request: if bamboo shades, it keeps the distance its shade needs.

**Independent Test**: on every shipped hamlet and on a cohort of rolled seeds, count the bamboo - stands and culm marks -
in any plot's sun ground at bamboo's reach; the count is zero, and the count is read from a record of every bamboo mark.

**Acceptance Scenarios**:

1. **Given** a generated hamlet, **When** every bamboo stand and every bamboo culm mark is tested against every threshing
   yard and garden bed, **Then** none stands in the plot's sun ground at bamboo's reach.
2. **Given** a bamboo mark a placer would set in a plot's sun ground, **When** the placer seats it, **Then** it is refused
   there, as a canopy crown is.
3. **Given** the finished map's check, **When** it counts bamboo, **Then** it reads every drawn bamboo mark and stand
   from the manifest, and the count matches the marks drawn.

---

### User Story 2 - The record says why bamboo is held and how far (Priority: P1)

The record's sun page states that bamboo is held, cites the heights its distance comes from, and no longer calls bamboo an
exemption; the map's explanations of bamboo, the yard, the garden and the groves agree with it.

**Why this priority**: the GM asked to look it up; the answer and its sources belong in the record, beside the rule.

**Independent Test**: the sun page names bamboo among the things held, with its reach and the cited heights; no page or
modal still calls bamboo exempt from the sun rule.

**Acceptance Scenarios**:

1. **Given** the record's page on keeping yards and gardens in the sun, **When** a reader looks up bamboo, **Then** it is
   held, at a reach worked out from its least cited height, with each height footnoted to a page the reader can open.
2. **Given** every modal and record page that mentions bamboo and the sun, **When** each is read, **Then** none says
   bamboo is exempt.

---

### Edge Cases

- **Bamboo under a grove's crowns.** A culm mark drawn between the crowns of a farm's grove or a belt is held like the
  crowns beside it; where a band's crowns already keep out of the sun ground, its bamboo keeps out with them.
- **A stand that cannot be seated.** A household's stand whose every seat lies in a plot's sun is not drawn there; the
  farm keeps none, as a farm with no room keeps none today.
- **The coppiced mulberry and the tea hedge** stay outside the rule, as feature 310 ruled: they are not tall, and this
  feature changes nothing about them.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: No bamboo - a household's stand, a shared thicket, or a culm mark in a farm grove, a windbreak or a belt -
  MUST stand in a threshing yard's or garden bed's sun ground at bamboo's reach, on any scripted map.
- **FR-002**: Bamboo's reach MUST be worked out from its least cited height by the same derivation the canopy reach uses
  (the late-autumn sun at the map's latitude), and stated beside the rule with the heights it comes from.
- **FR-003**: Every bamboo placer MUST test a mark's or a stand's seat against the sun ground before drawing it, as every
  crown placer does.
- **FR-004**: Every drawn bamboo mark and stand MUST be recorded on the manifest, so the finished map's check reads them.
- **FR-005**: The finished map's check (the gate's and the cohort audit's) MUST count bamboo in a plot's sun ground beside
  the canopy crowns, from that record, and MUST find what it counts (non-vacuity).
- **FR-006**: The record's sun page, the bamboo page where it speaks of the sun, and every modal that calls bamboo exempt
  MUST be brought in step: bamboo held, its reach and its sources stated.

### Key Entities

- **Sun ground**: a plot widened east and west and deepened south by a reach, from its north edge down (feature 310).
- **Bamboo reach**: the distance a bamboo stand's late-autumn shadow carries east, west and south, from its least cited
  height.
- **Bamboo record**: every drawn bamboo mark and stand on the manifest, by place.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On the five pool hamlets and on the cohort the gate rolls, zero bamboo marks or stands stand in any plot's
  sun ground at bamboo's reach, counted from the record (FR-001, FR-004, FR-005).
- **SC-002**: The count of bamboo marks the record holds equals the count drawn on each pool hamlet (FR-004).
- **SC-003**: A bamboo mark placed by hand in a plot's sun ground makes the check fail (FR-005), and a placer handed a seat
  in the sun refuses it (FR-003).
- **SC-004**: The sun page states bamboo's reach with each height it rests on footnoted and confirmed by the record's
  checks, and no page or modal calls bamboo exempt (FR-002, FR-006).

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Bamboo is held to the sun rule, not exempt | historically accurate for the heights; the rule itself a guess, as feature 310's is | the GM asked to look it up and keep the exemption only if bamboo deserves it; the timber bamboos a farm kept stand 10 m and more, as tall as the tree the canopy reach is reckoned from, in thickets that shade out almost everything else | the sun page; `tree_shade.py` |
| Bamboo's reach is worked out from its least cited height, by the canopy reach's own derivation | guess (the least height, as for trees; taller stands would reach further) | the GM expected a different distance for different things; the derivation gives each thing its own, and bamboo's least height is the tree's | the sun page; the plan |
| The coppiced mulberry and the tea hedge stay outside the rule | as feature 310 recorded | not tall; unchanged here | feature 310's spec |

## Assumptions

- The legacy hand-drawn pool is untouched (frozen exhibits).
- A bamboo mark under a crown is drawn beneath it; holding it out of the sun ground changes no crown.
- Houses, plots and seats stay where the seating puts them; only bamboo gives way.

## Review history

| round | reviewer | verdict | what it found |
|---|---|---|---|
