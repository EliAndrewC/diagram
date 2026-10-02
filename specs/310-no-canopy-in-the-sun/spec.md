# Feature Specification: No canopy tree in a yard's or bed's sun

**Feature Branch**: `310-no-canopy-in-the-sun` (no branch - committed on `main` in the clone)

**Created**: 2026-10-02

**Status**: Draft

**Input**: The GM, 2026-10-02 (verbatim in `request.md`): *"there's no reason for ANY trees to be exempt from the sunlight
calculations.  I mean, maybe bamboo since it doesbn't create much shade, but no canopy trees should be exempt"*

## Context (observed 2026-10-02)

The persimmon fix (pushed 2026-10-02) gave the map one predicate for a single tree's shade: a crown stands in a plot's
SUN GROUND when it comes within the reach east, west or south of a threshing yard or garden bed, from the plot's north
edge down (the reach is 50 ft, the shadow the record gives a working windbreak's tree late in autumn,
`research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html`). Every other kind of tree keeps a different, partial rule:

| trees | what they keep today |
|---|---|
| the windbreak belt | the south strip, the gardens' east lane, and the west lane (50 ft) |
| the village copse | the south strip and the gardens' east lane - EXEMPT from the west lane, on a comment citing "a persimmon in the yard center" that the record does not hold |
| a farm's own grove (yashikirin bands) | a 22 px strip south of a yard and a 22 px east reach beside a garden, only between neighbors; its own bands by construction |
| any other crown (woods, commons, shrine groves) | whatever its placer keeps; not measured against plots |

Measured on the five pool hamlets with the persimmon's predicate (every recorded crown, attributed to the stand it lies in):
Inashiro 95 copse crowns in a plot's sun (20 of 32 plots), Kashikawa 78 farm-grove crowns (24 of 40), Kuwabata 98 copse (18
of 35), Mizuguchi 10 farm-grove (4 of 24), Sawada 142 copse and 1 windbreak (26 of 43). Bamboo, counted the same way (observed 2026-10-02, a one-shot count of the recorded stands against the same ground): 2 bamboo stands on the five maps, neither in a plot's sun; the culm marks inside grove clumps are not recorded apart and were not counted.

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
   the one exemption among canopy trees is bamboo, stated as the GM's choice, never as a fact that bamboo casts little shade; the coppiced mulberry and the tea hedge are stated as not canopy, with their class and reason.
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
  south, from the plot's north edge; the reach is the one the record gives a working windbreak's tree (the sun page's west-lane reach). One predicate serves every
  placer and the check.
- **FR-003**: Bamboo - a bamboo stand and the culm marks drawn among a grove's crowns - is exempt.
- **FR-004**: Each placer refuses or drops a crown in a plot's sun as it seats it; no stage after may draw one there.
- **FR-005**: A check on the finished map counts every canopy crown in a plot's sun, on every shipped hamlet and in the
  cohort audit, and fails on any; it is red on today's pool before the fix.
- **FR-006**: The copse's west-lane exemption and its unsupported justification are removed; the farm grove's narrower strips
  are replaced by the one rule.
- **FR-007**: The record's sun page and the modals written from it state the one rule and the bamboo exemption as the GM's choice; the bamboo page's tall madake is not contradicted.

### Key Entities

- **Plot**: a threshing yard or a garden bed, as drawn.
- **Sun ground**: the area east, west and south of a plot, within the reach, from its north edge.
- **Canopy crown**: any drawn tree crown; bamboo, the coppiced mulberry and the tea dike's clipped hedge are not ones (Decisions).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-002, FR-004, FR-005): On the five pool hamlets, zero canopy crowns stand in a plot's sun ground (from 95, 78, 98, 10 and 143).
- **SC-002** (FR-001, FR-004, FR-005): On a cohort of at least 24 rolled seeds, zero canopy crowns stand in a plot's sun ground, and every seed that
  produced a map before the change produces one after (no regression).
- **SC-003** (FR-003, FR-006, FR-007): The record names exactly one exemption among canopy trees, bamboo, as the GM's choice, and states the coppiced mulberry and the tea hedge as not canopy, each with its class and reason.
- **SC-004** (FR-001, FR-004): Each pool hamlet's drawn household wood and windbreak are measured before and after, and any drop is
  reported with the ground the sun rule took.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Every canopy tree, the farm's own grove included, keeps out of every yard's and bed's sun ground | guess - the GM's rule over a silent record | *"no canopy trees should be exempt"*. The record gives a grove's SIDES (Tonami: tall trees from the south round to the west of a house) but no distance from a farm's plots to its trees - the sun page says "No source measures how far a farm's plots stood from its trees" - so the rule is the GM's, not a departure from anything attested | `research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html`; the shared predicate's docstring |
| Bamboo is exempt | guess - the GM's tentative allowance (*"maybe bamboo"*) | *"maybe bamboo since it doesbn't create much shade"*. The record's bamboo page gives madake as a tall culm in thickets "shading out almost everything else" (`research/questions/0075-bamboo-groves-chikurin.html`), so the exemption is recorded as the GM's choice, not as little shade. Its cost on today's maps is nil for the 2 recorded stands on the five pool hamlets, neither in a plot's sun (one-shot count, 2026-10-02); the culm marks drawn in grove clumps are not recorded apart and were not counted, and that gap is raised with the GM beside the count. Raised with the GM, with the count and the bamboo page's madake height, once the implementation works | the sun page |
| Coppiced mulberry (the perimeter dike's and the mulberry dikes' rows) and the tea dike's clipped hedge are not canopy, so not held | accurate for the mulberry (the record's low bushes); guess for the tea hedge's form, low height and width (the record says nothing of how it stood) | the GM narrowed "ANY trees" to "canopy trees", naming bamboo as what "doesn't create much shade"; the mulberry was "for the most part trained as low bushes", pruned once a year (`research/questions/0026-mulberry-and-other-crops-on-pond-dikes-sangji-guoji.html`), and the tea hedge is clipped low (its width a guess in the drawing); at the record's shadow ratio such a bush throws a small fraction of the reach. The coppiced mulberry ruled legitimate by the plan review (D3-mulberry, 2026-10-02); the tea hedge by the plan review's round 3 and the spec amendment review (2026-10-02), as a clipped shrub rather than a tree. Both raised with the GM once the implementation works | the sun page; `research.md` R1 |
| One reach for every canopy tree: the working windbreak tree's west-lane reach | guess | the record already reckons every shadow at the least height it gives a tree (a working windbreak's, stated on the sun page); taller trees would reach further | the sun page, the predicate's constant |
| The sun ground is a rectangle east, west and south of the plot, from its north edge | deliberate deviation | the 9-to-3 sun sweeps a wedge from the southeast to the southwest; the sun page takes the rectangle "a simplification, taken knowingly" | the sun page |
| A copse whose roll the freed ground cannot hold is drawn short, never moved into the sun | guess | the plot's sun is the rule and the wood the remainder; what it costs - the drawn wood against its roll - is measured before and after (SC-004) | the plan; the wood-goal module |
| On a grove farm, the thin east band closes only the house's east side, the garden standing beside the yard | guess - chosen by the research, as the GM asked | the 3- and 4-sided grove (`research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html`) put a thin band beside the garden, in its sun; the rule stripped it to a stub (the homestead grove's glyph-check). Standing it the reach out instead widened Kashikawa's farm frames past the record's widest row frontage (one-shot measurement, 2026-10-02: every frame wider, the widest well past it, measured from the manifest; `research/questions/0033-row-villages-resson.html`), and seated 4 of 10 households on the linear test field. The garden beside the yard is a form the layout already draws under every other wind; the frontage stays as it was. The GM, asked: "whichever of these options appears to be in accordance with our research findings" | the grove page; `dispersed.canonical_farmstead` |

## Assumptions

- Every drawn canopy crown is recorded (`tree_crowns`, the record every tree-over-building test already reads), so the
  check can read them all; the plan confirms no crown escapes the record.
- The legacy hand-drawn pool is untouched (frozen exhibits).
- The settlement form, house seats and plots stay where the seating puts them; only trees give way. Re-seating is not
  required, though a placer whose bands move may move a bundle's extent.
- Bamboo's exemption covers the household bamboo strip, the shared bamboo grove and the culm marks in groves.

## Review history

| round | reviewer | verdict | what it found |
|---|---|---|---|
| spec 1 | spec-fidelity | CHANGES REQUIRED | bamboo as a firm ruling on a premise the record contradicts; row 1's attestation; labels outside the four classes |
| spec 2 | spec-fidelity-verify | CHANGES REQUIRED | the bamboo cost "nil" while the culm marks were uncounted |
| spec 3 | spec-fidelity-verify | FAITHFUL | - |
| spec 4 (spec-lint wording) | spec-fidelity-verify | FAITHFUL | no meaning changed |
| amendment 1 (the not-canopy row) | spec-fidelity | CHANGES REQUIRED | the tea hedge's ruling overstated; three passages contradicting the row |
| amendment 2 | spec-fidelity-verify | CHANGES REQUIRED | tasks T22 named the hill margin's tea rows, which no ruling covers (dropped: never a tree site) |
