# Feature Specification: The wind is northwest unless a map declares otherwise

**Feature**: `261-northwest-wind-by-default` | **Created**: 2026-09-26 | **Status**: Draft
**Input**: the GM's question about Kashikawa's windbreak and their acceptance of the proposed fix,
verbatim in [`request.md`](request.md).

## Summary

The GM ruled on 2026-08-29 that shelter belts stand on the north and west of a settlement, because the
winter wind blows from the northwest across China, Japan and "Rokugan in most places when the local
geography does not override the regional geography" (`research/vegetation/030-...`). The scripted
hamlet generator never applies that ruling. It decides each map's windward side in two steps, and
neither step uses the northwest:

1. **From the slope.** The windward side is the map's uphill direction, turned 45 degrees either way at
   random (`windward_for`, `WIND_TURNS`). Kashikawa falls to the northeast, so this step could only give
   south, southwest or west.
2. **From wherever the village came to rest.** If the houses end up facing more than about 70 degrees
   away from that wind, the wind is renamed after whatever the cluster's back faces
   (`ways/track.py`, "the site wins"). Kashikawa's cluster settled with its back to the southeast, so
   its manifest says `windward: SE` and its belt stands on the south and east.

The five scripted hamlets are windward W/N (Inashiro), SE (Kashikawa), NW (Kuwabata), S (Mizuguchi)
and NE (Sawada): one in five on the northwest, and that one by accident. The record meanwhile claims
the maps are built "northwest by default", which is false, and the windbreak's pop-up says only
"the windward, high side", which on Kashikawa is neither true nor explained.

This feature does what the GM accepted: **the windward side is the northwest on every map, unless the
map declares a local wind.** Terrain no longer overrides it silently - not the slope, and not the seat.
The village is placed with its back to the wind rather than the wind being renamed to fit the village.
No map in the pool declares a local wind, so every scripted hamlet is re-rolled with its belt on the
north and west.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every map's windbreak is on the north and west (Priority: P1)

The GM opens any scripted hamlet - Kashikawa first - and the windbreak forest stands on the north and
west of the village, as the regional wind demands.

**Why this priority**: it is the defect the GM reported, and "fixed everywhere for now" is the request.

**Independent Test**: re-roll the five scripted hamlets; each manifest records `windward: NW`, and each
map's windbreak stands on the northwest side of its own house cluster.

**Acceptance Scenarios**:

1. **Given** a scripted hamlet whose spec declares no wind, **When** it is generated, **Then** its
   windward side is the northwest, whatever its slope and wherever its cluster is seated.
2. **Given** the five pool hamlets re-rolled, **When** their manifests are read, **Then** every one
   records `windward: NW` and none of their specs declares a wind.
3. **Given** any re-rolled pool hamlet, **When** its windbreak belt is measured against its house
   cluster, **Then** the belt lies on the cluster's northwest side (its center is to the north-west of
   the cluster's center, and the belt covers the cluster's north-west fringe).
4. **Given** a hamlet whose best seat by slope alone would face away from the northwest, **When** it is
   generated, **Then** the seat search places the cluster with its back to the northwest instead, and
   the recorded wind is never changed to match a seat.

---

### User Story 2 - A local wind is a declaration, never an accident (Priority: P1)

A future map in a valley whose local wind is not the regional one declares that wind on its spec, and
only then does its windbreak move.

**Why this priority**: it is the rule the GM chose ("only when declared"), and it is what keeps the
override from creeping back.

**Independent Test**: generate a test hamlet with a declared local wind; its windward is exactly the
declared quarter; generate it again without the declaration; its windward is the northwest.

**Acceptance Scenarios**:

1. **Given** a spec that declares a windward quarter, **When** the hamlet is generated, **Then** that
   quarter is the windward side and nothing in generation changes it.
2. **Given** no declaration, **When** the hamlet is generated, **Then** no stage - plan, seat, ways,
   hinterland - derives, rolls or rewrites the wind.
3. **Given** the manifest of any generated hamlet, **When** it is read, **Then** it records whether the
   wind was the regional default or a declared local wind.

---

### User Story 3 - The map explains its windbreak's side (Priority: P2)

The GM, or a player, clicks the windbreak on a map and is told which side it stands on and why.

**Why this priority**: the GM's complaint was partly "I don't see any explanation for that".

**Acceptance Scenarios**:

1. **Given** a map with the default wind, **When** the windbreak's pop-up opens, **Then** it says the
   belt stands on the north and west because the regional winter wind blows from the northwest.
2. **Given** a map with a declared local wind, **When** the windbreak's pop-up opens, **Then** it says
   which side the belt stands on and that the map declares a local wind departing from the regional
   northwest.

---

### User Story 4 - The record says what the generator does (Priority: P2)

The research entry on shelter belts, the map notes and the generator's docs describe the rule the
engine actually follows.

**Acceptance Scenarios**:

1. **Given** `research/vegetation/030-...`, **When** it is read, **Then** it says every map's windward
   side is the northwest unless the map declares a local wind, and its measured arcs are the re-rolled
   maps' own.
2. **Given** the scripted hamlets' notes files and `hamletgen.md`, **When** they are read, **Then** no
   passage still says the wind is derived from the slope or re-read from the seat, except as history
   of what this feature retired where the notes keep a dated log.

### Edge Cases

- **A map whose fall makes a northwest-backed seat hard.** Kashikawa falls to the northeast and
  Mizuguchi to the east (both put the northwest margin on a flank), and **Sawada falls to the northwest**
  (`down_deg=225` in the engine's screen convention, 0 = east, 90 = south; `sawada.gen.py`: "land falling
  northwest"), which is the direct opposition: its uphill side is the southeast, so its northwest margin
  is the field's low foot, where the seat's hard constraints (dwellings above the drain, off the wet toe)
  bite. Sawada is the hardest map. The seat's hard constraints still hold; the seat search must find a
  margin whose back faces the northwest among the margins they allow. The wind is not renamed to rescue
  a seat. If a map has no such margin at its current seed, the map is re-seeded (its seed is a roll, not
  a fact about the place); its declared fall, water and other declared knobs are kept.
- **When no seed works.** If no seed seats a northwest-backed cluster under a map's declared fall and
  water, NONE of these is done: the 45-degree bar loosened for that map, a wind declared on it (FR-005),
  the wind renamed from the seat (FR-003), a declared knob changed, or the belt planted in the crop
  (FR-010). The case goes to the `spec-fidelity` exception check with the GM's words, and then to the GM.
  Before relying on re-seeding, the plan measures each pool hamlet at its current seed under the new
  rule and records which needed a new seed and what the seed search found.
- **The belt and the cropland.** A northwest belt must still stand clear of the crop and the dry hem,
  and still pass every rule the belt obeys today (continuous within its sides, embracing the cluster).
- **The homestead groves.** Each farmstead's own grove (the yashikirin L-belt) takes its sides from
  the same windward key, so it moves to the north and west with the village belt.
- **The cohort.** The generator's regression cohort (seeds rolled with no declared wind) changes
  wholesale; its pinned baseline is re-measured, and any new failure is fixed, not pinned.
- **The legacy pool** (18 hand-authored maps) is frozen and never regenerated; it is out of scope. The
  one legacy map that declares a wind (Ubame) declares the northwest.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A scripted hamlet's windward side MUST be the northwest unless its spec declares one.
- **FR-002**: A declared windward side MUST be used as declared; it is the only way a map's wind departs
  from the northwest.
- **FR-003**: The wind MUST NOT be derived from the slope, rolled, or rewritten from the cluster's seat
  at any stage of generation. The slope-derived rule and the seat re-read are retired.
- **FR-004**: The cluster MUST be seated with its back to the windward side; where the slope and the
  wind pull different ways, the wind's pull is strong enough that the chosen seat's back faces within
  45 degrees of the windward bearing on every pool map.
- **FR-005**: No pool map's spec MAY declare a windward side; a test MUST fail if one does.
- **FR-006**: The five scripted hamlets MUST be re-rolled; each MUST record `windward: NW`, each MUST
  have its windbreak on its cluster's northwest side, and each MUST pass the full gate.
- **FR-007**: Each manifest MUST record whether its wind is the regional default or a declared local
  wind.
- **FR-008**: The windbreak's pop-up on each map MUST state the side the belt stands on and why - the
  regional northwest wind, or the map's declared local wind.
- **FR-009**: The research entry, the generator docs (`hamletgen.md`, code comments at the point of
  change) and the five notes files MUST describe the new rule; the record's false "northwest by default"
  claim and its measured arcs are corrected.
- **FR-010**: Every rule the belt and the seat obeyed before (clear of crop, continuous, embracing the
  cluster, dwellings above the drain, no household lost) MUST still hold on every re-rolled map.

### Key Entities

- **Windward side**: the compass quarter the cold wind blows from; the northwest by default, or a
  declared local quarter.
- **Wind source**: whether a map's windward side is the regional default or a declared local wind.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 5 of 5 scripted hamlets record `windward: NW` (today: 1 of 5).
- **SC-002**: 5 of 5 have their windbreak belt's center to the north-west of their cluster's center,
  with the cluster's back facing within 45 degrees of northwest.
- **SC-003**: 0 pool specs declare a wind; 0 code paths derive or rewrite the wind (a test covers both).
- **SC-004**: every re-rolled map passes the full gate and seats all its declared households.
- **SC-005**: every windbreak pop-up names its side and its reason.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class (accurate / deviation / guess) | Why | Recorded at |
|---|---|---|---|
| The windward side is the northwest on every map by default | accurate (the East Asian winter monsoon; the Sendai *igune* on the north and west because the winter winds are north-northwesterly) + the GM's ruling of 2026-08-29 | the regional wind is the fact the belt communicates; the GM ruled it holds "in most places" | `research/vegetation/030-...` (already cited), `plan.py` at the default |
| A local wind departs from the northwest only when a map declares it | the GM's ruling, 2026-09-26 ("only when declared") | a silent terrain override put Kashikawa's belt on the opposite side with no explanation | `research/vegetation/030-...`, `plan.py`, the windbreak pop-up |
| The slope-derived wind (katabatic drainage) is retired as a default | the GM's ruling, 2026-09-26 | the katabatic finding stays in the record as the reason a map MAY declare a local wind | `research/vegetation/030-...`, `consts.py` where `WIND_TURNS` stood |
| The seat bends to the wind, never the wind to the seat | map convention following the ruling | the belt's side is the information; a renamed wind makes it circular | comment at the seat search and at the retired re-read |

## Assumptions

- A map's seed is a roll, not a fact about the place; a pool hamlet may be re-seeded if its current seed
  cannot seat a northwest-backed cluster. Its declared fall, water sink and other declared knobs are
  kept, since those are what the map was made to show (Kashikawa's `brook_side` confluence included).
- Only the scripted hamlet generator derives a wind; the older settlement engine already defaults to the
  northwest and the legacy pool is frozen.

## Review history

- Round 1 (2026-09-26, `spec-fidelity`, Opus): CHANGES REQUIRED, two items, both applied. The round found
  nothing unrequested and nothing kept of the behavior the GM asked to change, and judged FR-004's 45-degree
  bar calibration rather than a loophole (one compass quarter; a seat backing due N or due W is still "north
  and west"). (1) **Sawada's fall was misstated** as southwest; it is northwest (`down_deg=225`, screen
  convention), which makes it the direct-opposition map and the hardest - the Edge Case now says so. (2) **The
  re-seed assumption did not say what happens when no seed works**: the Edge Cases now name the five exits
  that are NOT taken and route the case to the exception check and the GM, and the plan owes a per-map
  measurement at the current seeds before relying on re-seeding.
- Round 2 (2026-09-26, `spec-fidelity`, Opus): **FAITHFUL**. Both round-1 items RESOLVED; the fall bearings of
  all three maps named were re-checked against their generators, and the requirement ids the new Edge Case
  cites point where they should. Accepted.
