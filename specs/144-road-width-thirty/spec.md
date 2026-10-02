# Feature Specification: The Mode B Highway Default Is ~30 ft

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=144-road-width-thirty`)

**Created**: 2026-08-28

**Status**: **FAITHFUL** - `spec-fidelity` round 1 (2026-08-28), no changes; three asides carried into the plan (the ~30 fallback `26`s, the gate throat sized against the road, the stale 26 ft statements). CORRECTION after the review: the scope lock the spec assumed was released on 2026-08-27 (`dev/switches.json`), so the pool sweep is owed NOW, in this feature, not at unlock - US2 / FR-004 / SC-003 read accordingly.

**Input**: [`gm-request.md`](gm-request.md), verbatim. That file is the authority for this specification.

## The feature, in one sentence

The default real width of the trunk road that every Mode B settlement map draws (`s.road`, today 26 ft) becomes about thirty feet, on every Mode B map, because the source read for feature 143 gives the Tōkaidō's 1604 standard as 5 ken (~29.5 ft) and the GM chose to fix the default rather than keep 26 ft as a rounding.

## Why this exists (the GM's words)

*"For option four, yes, let us raise the default to about thirty feet For every mode B map."*

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The default trunk road is ~30 ft on the reference settlement (Priority: P1)

The reference hamlet (Inashiro) regenerates with its road drawn at the new default; every check that reads the road's width reads the new value from the manifest; the record says why.

**Why this priority**: the GM's instruction, and the reference settlement is the one map that can be rolled under the current scope lock.

**Independent Test**: `make maps` rolls Inashiro clean; the manifest's `road_width` equals the new default in that map's pixels; the gate is green.

**Acceptance Scenarios**:

1. **Given** a Mode B gen that calls `s.road(...)` without a width, **When** it runs, **Then** the road is drawn at the new default real width (converted at the map's scale) and `M["road_width"]` records it.
2. **Given** a gen that passes an explicit width, **When** it runs, **Then** that width is honored as before.
3. **Given** the research record, **When** a reader looks up the road width, **Then** `research/cities/capitals.md` "Street widths" and the road's own docstring cite `tokaido-jawiki` (5 ken) for the default, and the interactive map's road modal says the same.

---

### User Story 2 - Every other Mode B map takes the new default (Priority: P2)

The scope is UNLOCKED (released 2026-08-27, T92), so the pool sweep that widens every other map's road runs in this feature: the map target after the reference is clean rolls the whole tier and reports every failure together.

**Why this priority**: "every mode B map" is the instruction.

**Independent Test**: the map target rolls the whole tier clean with the wider roads; the unlocked gate is green; `settlement-review` passes on the reference map.

**Acceptance Scenarios**:

1. **Given** the new default, **When** the pool regenerates, **Then** every Mode B map's trunk road is at the new default and every gate check passes or is fixed forward.

---

### Edge Cases

- Manifests that lack `road_width` (older regression fixtures): the checks' fallback value is a separate decision, recorded in the plan - the fixtures freeze the maps as they were checked.
- The ōte-suji's 45 ft (capitals) was chosen as "half again the highway"; with the highway at ~30 ft the proportion is 1.5x still (45 / 30) - unchanged.
- The ring road, streets, lanes and roji have their own defaults and are not part of this feature.

## Requirements *(mandatory)*

- **FR-001**: The `s.road` default real width MUST become ~30 ft (5 ken = 29.5 ft; the drawn value is the plan's to fix at 30 ft as a round figure or 29.5 as the exact one - recorded).
- **FR-002**: An explicit width passed by a gen MUST still be honored.
- **FR-003**: The road's docstring, the research entry ("Street widths") and the interactive map's road text MUST cite the read source (`tokaido-jawiki`) and MUST NOT call 26 ft "the Tōkaidō's own width".
- **FR-004**: The reference settlement MUST be regenerated and gate-green first, then the whole pool (the map target widens to the tier once the reference is clean); both are tasks.
- **FR-005**: No other width (ring road, street, lane, roji, ōte-suji) changes in this feature.
- **FR-006**: The feature follows the engine route: a spec-kit feature, `make done` green, `settlement-review` on the reference map at acceptance/unlock per the period's doctrine.

## Success Criteria *(mandatory)*

- **SC-001**: Inashiro's manifest carries the new default; `make maps` and the locked `make done` are green.
- **SC-002**: No document in the skill glosses 26 ft as the Tōkaidō's width; the record cites 5 ken.
- **SC-003**: Every pool manifest with a road carries the new `road_width`.

## Decisions Recorded

| Decision | Class (accurate / deviation / guess) | Why | Recorded at |
|---|---|---|---|
| trunk road default ~30 ft (5 ken) | accurate | ja.wikipedia 東海道: the 1604 standard of 5 ken | `research/cities/capitals.md#street-widths`, the `s.road` docstring, `interactive/classes.py` road text |
| 30 ft rather than 29.5 ft (if the plan rounds) | deviation (a round figure) | the GM said "about thirty feet" | the same entry |

## Assumptions

- "Mode B map" = every settlement map drawn by the generator (hamlet, village, town, city, capital); Mode A sheets are hand-drawn and out of scope.
- The scope is unlocked: this feature rolls Inashiro, then the pool.
