# Feature 300 - reeds to the bank

**Feature Branch**: none (main, in the clone `diagram-performance`)
**Created**: 2026-10-01
**Status**: Accepted - FAITHFUL at round 2 (2026-10-01)
**Request**: [`request.md`](request.md) - the GM's words verbatim: the stream's banks through the marsh look "cleared of marsh",
a "rendering convention ... to make the stream legible, but I imagine there's a better way to do it than that. What do you
suggest?", and to the session's three-part proposal, "Yes, please."
**Predecessors**: 298 (the cover tiles), 299 (the marsh's fringe and overlays).

## Summary

The marsh's reed tile stops short of every watercourse that crosses it (observed 2026-10-01, method: reading the keep-out slots, research R1): a margin kept so a reed blade thrown one by one
never crossed the water, carried into the tiles though a tile needs none (research R1). The reeds now run to the water's drawn
edge, a narrow band of a denser, slightly darker reed tile lines each bank so the stream still stands out, and a thin dark outline is
added to the water only if the stream is still lost after that.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reeds stand at the water's edge (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a stream or an irrigation ditch crossing a marsh, **When** the map is drawn, **Then** the marsh's reeds reach the
   water's drawn edge on both banks - no bare strip between them.
2. **Given** that watercourse, **When** the map is drawn, **Then** a narrow band along each bank inside the marsh is drawn with a
   denser, slightly darker reed tile, and the water draws over the marsh.
3. **Given** scrub along a stream, **When** the map is drawn, **Then** nothing changes there.

### User Story 2 - The stream stays legible (Priority: P1)

**Acceptance Scenarios**:

1. **Given** Inashiro's stream through its toe marsh, **When** the GM looks at the map, **Then** the stream reads as clearly as it
   did with the bare strip; if the bank band alone does not do it, the watercourse gets a thin dark outline where it crosses the
   marsh.

### Edge Cases

- The pond's embankment stays bare (research/water 285: a reservoir's bank is kept dry and firm); only the watercourses' margin goes.
- A watercourse along a marsh's edge gets the bank band only on the marsh's side.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The marsh's reed tile MUST be kept off a watercourse only at its drawn width - no extra margin (research R1).
- **FR-002**: Within a marsh, a narrow band along each watercourse's bank (the proposal's target width and the as-built one in research R1) MUST be drawn
  with a bank reed tile of denser, slightly darker reeds than the marsh's own, in the marsh's class; the as-built width is
  calibrated by eye and recorded in R1.
- **FR-003**: If the stream is not clearly legible with FR-002 alone (judged by eye on Inashiro and recorded in research R1), the
  watercourse MUST be given a thin dark outline where it crosses a marsh.
- **FR-004**: The scrub, the pond's embankment and every other cover MUST be unchanged.
- **FR-005**: The record and the modals that say how the marsh is drawn MUST say what is drawn; the pool MUST pass the gate.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-002, FR-004): a unit test - a marsh with a stream across it - finds the reed tile's shape reaching the
  stream's drawn edge, the bank band in the marsh's slot, and nothing changed for a scrub zone the stream crosses.
- **SC-002** (FR-003, FR-005): the GM's look at Inashiro; `make done` green; the record checks run.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Reeds to the water's edge | historically accurate (research/questions/0061-reservoir-ponds-tameike.html: a reservoir's shore is reeded; reeds stand in the shallows) | the margin was a thrown blade's, not the ground's | `land/wet.py` |
| A denser bank band of reeds | map drawing convention | frames the stream where the bare strip did | `land/tiles.py`, `settlement/finish.py` |

## Review history

- Round 1 (spec-fidelity, 2026-10-01): CHANGES REQUIRED - FR-002 dropped the approved "narrow", the target width and "slightly
  darker". Addressed.
- Round 2 (spec-fidelity-verify): FAITHFUL. Aside applied: the Summary and scenario 2 say "slightly darker" too.
