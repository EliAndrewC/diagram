# Feature Specification: No canopy tree in a yard's or bed's sun

**Feature Branch**: `310-no-canopy-in-the-sun` (no branch - committed on `main` in the clone)

**Created**: 2026-10-02

**Status**: Draft

**Input**: The GM, 2026-10-02 (verbatim in `request.md`): *"there's no reason for ANY trees to be exempt from the sunlight
calculations.  I mean, maybe bamboo since it doesbn't create much shade, but no canopy trees should be exempt"*

## Context (observed 2026-10-02)

The persimmon fix (pushed 2026-10-02) gave the map one predicate for a single tree's shade: a crown stands in a plot's
SUN GROUND when it comes within the reach east, west or south of a threshing yard or garden bed, from the plot's north
edge down (the reach is 50 ft, the shadow the record gives a 10 m tree late in autumn,
`research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html`). Every other kind of tree keeps a different, partial rule:

| trees | what they keep today |
|---|---|
| the windbreak belt | the south strip, the gardens' east lane, and the west lane (50 ft) |
| the village copse | the south strip and the gardens' east lane - EXEMPT from the west lane, on a comment citing "a persimmon in the yard center" that the record does not hold |
| a farm's own grove (yashikirin bands) | a 22 px strip south of a yard and a 22 px east reach beside a garden, only between neighbors; its own bands by construction |
| any other crown (woods, commons, shrine groves) | whatever its placer keeps; not measured against plots |

Measured on the five pool hamlets with the persimmon's predicate (every recorded crown, attributed to the stand it lies in):
Inashiro 95 copse crowns in a plot's sun (20 of 32 plots), Kashikawa 78 farm-grove crowns (24 of 40), Kuwabata 98 copse (18
of 35), Mizuguchi 10 farm-grove (4 of 24), Sawada 142 copse and 1 windbreak (26 of 43). Bamboo was not counted.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - No canopy tree shades a threshing yard or a garden bed (Priority: P1)

The GM opens any generated hamlet and sees every threshing yard and garden bed with open sky to its east, west and south,
whatever the tree - windbreak, copse, a farm's own grove, a wood, a persimmon. Bamboo may stand closer.

**Why this priority**: it is the request: no canopy tree is exempt from the sun rule.

**Independent Test**: on every shipped hamlet and on a cohort of rolled seeds, count the canopy crowns that stand in any
plot's sun ground; the count is zero.

**Acceptance Scenarios**:

1. **Given** a generated hamlet, **When** every drawn canopy crown is tested against every threshing yard and garden bed,
   **Then** none stands in the plot's sun ground.
2. **Given** the five pool hamlets that drew 95, 78, 98, 10 and 143 such crowns, **When** they are regenerated, **Then**
   each draws none.
3. **Given** a bamboo stand or a bamboo culm mark beside a plot, **When** the map is checked, **Then** it is not counted
   (bamboo is exempt).

---

### User Story 2 - The rule is one rule, in the record (Priority: P1)

Every tree placer asks the same question with the same reach, and the record states one rule for every canopy tree, so the
map's explanations of the windbreak, the copse, the farm grove, the yard and the garden agree.

**Why this priority**: the defect the GM found was a tree with its own, weaker rule; separate rules per stand are how it
happened.

**Independent Test**: the record's sun page states a single rule for canopy trees and names bamboo as the one exemption;
no placer keeps a different reach for a canopy crown.

**Acceptance Scenarios**:

1. **Given** the record's page on keeping yards and gardens in the sun, **When** a reader looks for an exemption, **Then**
   the only one is bamboo, with its reason.
2. **Given** the modals of the windbreak, copse, farm grove, yard and garden, **When** each is read against the record,
   **Then** none says a tree may stand in a plot's sun.

---

### Edge Cases

- **A farm's own grove.** Its bands stand hard against the house it shelters; a band that runs down beside the yard or a
  bed within the reach takes the plot's sun and is not drawn there - the band keeps its crowns north of the plot's north
  edge or beyond the reach. The rest of the band stands.
- **A wood whose goal cannot be met.** The households' wood (copse plus groves) is rolled to an area; ground taken from it
  by the sun rule may leave less than the roll. The drawn wood stays honest to what it holds, as the existing goal
  machinery reports today, and the shortfall is measured in the plan.
- **A plot with no tree-free side.** A plot hemmed in by woods is not moved; the trees give way.
- **The persimmon** already keeps the rule; it is not changed.
- **Legacy hand-drawn maps** are exempt from every sun rule (the record's standing exemption) and are not touched.
- **A crown that overhangs from outside the reach** - the test is the crown's disc, not its center.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: No canopy tree crown drawn on a scripted map may stand in a threshing yard's or garden bed's sun ground,
  whatever stand it belongs to (windbreak, copse, a farm's own grove, a neighbor's grove, a wood, a shrine grove, a fruit
  tree, any later kind).
- **FR-002**: The sun ground is the persimmon's: the plot widened by the reach east and west and deepened by it to the
  south, from the plot's north edge; the reach is the one the record gives a 10 m tree (50 ft). One predicate serves every
  placer and the check.
- **FR-003**: Bamboo - a bamboo stand and the culm marks drawn among a grove's crowns - is exempt.
- **FR-004**: Each placer refuses or drops a crown in a plot's sun as it seats it; no stage after may draw one there.
- **FR-005**: A check on the finished map counts every canopy crown in a plot's sun, on every shipped hamlet and in the
  cohort audit, and fails on any; it is red on today's pool before the fix.
- **FR-006**: The copse's west-lane exemption and its unsupported justification are removed; the farm grove's 22 px strips
  are replaced by the one rule.
- **FR-007**: The record's sun page and the modals written from it state the one rule and the bamboo exemption.

### Key Entities

- **Plot**: a threshing yard or a garden bed, as drawn.
- **Sun ground**: the area east, west and south of a plot, within the reach, from its north edge.
- **Canopy crown**: any drawn tree crown; bamboo is not one.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On the five pool hamlets, zero canopy crowns stand in a plot's sun ground (from 95, 78, 98, 10 and 143).
- **SC-002**: On a cohort of at least 24 rolled seeds, zero canopy crowns stand in a plot's sun ground, and every seed that
  produced a map before the change produces one after (no regression).
- **SC-003**: The record names exactly one exemption, bamboo.
- **SC-004**: Each pool hamlet's drawn household wood and windbreak are measured before and after, and any drop is
  reported with the ground the sun rule took.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Every canopy tree, the farm's own grove included, keeps out of every yard's and bed's sun ground | deviation - the GM's ruling | *"no canopy trees should be exempt"*; the record has farm groves on the south and west of a house on the Tonami plain, so a grove close by a sunlit plot is attested there; our maps follow the GM's rule instead | `research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html`; the shared predicate's docstring |
| Bamboo is exempt | the GM's ruling, with the reason the GM gave | *"maybe bamboo since it doesbn't create much shade"* | the same page |
| One reach for every canopy tree: the 10 m tree's 50 ft | guess, carried | the record already reckons every shadow at the least height it gives a tree (a working windbreak's 10 m); taller trees would reach further | the same page, the predicate's constant |
| The sun ground is a rectangle east, west and south of the plot, from its north edge | reconstruction, carried | the 9-to-3 sun crosses from the southeast to the southwest; the record's knowing simplification of the wedge | the same page |
| A copse whose roll the freed ground cannot hold is drawn short, never moved into the sun | this project's decision | the plot's sun is the rule; the wood is the remainder | the plan; the wood-goal module |

## Assumptions

- Every drawn canopy crown is recorded (`tree_crowns`, the record every tree-over-building test already reads), so the
  check can read them all; the plan confirms no crown escapes the record.
- The legacy hand-drawn pool is untouched (frozen exhibits).
- The settlement form, house seats and plots stay where the seating puts them; only trees give way. Re-seating is not
  required, though a placer whose bands move may move a bundle's extent.
- Bamboo's exemption covers the household bamboo strip, the shared bamboo grove and the culm marks in groves.
