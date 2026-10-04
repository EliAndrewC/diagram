# Feature Specification: No ways placed before the homesteads

**Feature**: 320-no-ways-before-homesteads | **Created**: 2026-10-04 | **Status**: Draft
**Input**: the GM's words, verbatim in `request.md`.

## Summary

A clustered (nucleated) hamlet fixes two ways before any farmhouse is seated: the EXIT STRIP, a straight corridor from the
cluster's center outward that every house keeps off and the map later draws as the start of the track out; and, on a brook
map, the FIELD WAY, the hamlet's path to its field, routed and reserved before seating. Both go. The farmhouses are seated
with nothing laid or reserved for a way; the room feature 318 already keeps between neighbors (a lane's room, `growth.grow_gap`: `MIN_WEB_GAP` plus the parting) is
what keeps a way possible; the track out and the ways are laid after the houses stand. The GM: *"we should eliminate both
the exit strip and the field way as things placed in advance of the homesteads being placed, because the space we've
already allocated can serve the same function"*; kept only *"if it makes things significantly faster"*, as an optimization.

## User Scenarios & Testing

### US1 - Houses first, every way after (P1)
A GM rolls a clustered hamlet: no corridor, strip or field way exists on the map while its farmhouses are seated; the track
out, the field path and every household's way are laid afterwards, in the ground the houses left.

**Acceptance**: (1) on the reference spec and the cohort's nucleated seeds, nothing is reserved for a way (no corridor in the
registry, no `access_exit`) when the last house is seated; (2) every household is reached by a way of its own or across a
neighbor's yard, as now; (3) the track out runs off the map and the field is reached, as now.

### US2 - The record says what the map does (P2)
A reader of page 0081's drawing page finds that every farmhouse is seated before any way is laid, with no exception for the
track out or the field path; the claims of the code that seats and lays them cite it in step.

### Edge cases
- A margin whose ground has no lawful way out at all: still refused before seating, as now (the dry-exit test of the seat,
  and the outward bearing's test), but nothing is reserved by that test.
- A brook map whose field lies across the brook: the field path is laid after the houses, at a ford, as the web lays it.
- A household no way reaches after the houses stand: reached across its nearest reached neighbor's yard (feature 318's pinch).

## Requirements

- **FR-001**: The exit strip (`access.start_tree`'s corridor, `access_exit`) and the field's corridor
  (`stages.reserve_field_corridor`) MUST be removed, and nothing reserved, drawn or recorded in their place before the last
  farmhouse is seated. (A row village's planned streets, page 0033's planned colony, are not touched.)
- **FR-002**: While houses are seated, "a way of its own" (feature 318's `SeatRegion.opens`) MUST mean a dooryard opening onto
  lane ground connected to the open country on the side the way out will leave - ground, not a way; a household beyond water
  or walled in by its neighbors is not counted open.
- **FR-003**: Once the last house stands, the track out MUST be laid first, from the cluster's edge, then each household's way
  in the gaps (feature 318's gap pass), joined to the track out or an earlier way, then the field path as the web lays it.
- **FR-004**: Every rule a map is held to today MUST hold after: every household reached (by a way or across a neighbor's yard),
  the track out off the map, the field reached on a brook map, the cohort passing every seed main passes.
- **FR-005**: Performance MUST be measured against main (the bookends, which measure the two removals together); were the
  exit strip or the field's corridor shown to make the hamlet significantly faster, the GM's words allow keeping it as an
  optimization - the measurement decides, and is put to the GM.
- **FR-006**: Page 0081's drawing page and the claims of every changed unit MUST say what the map does; the record checks and
  claims checks the edits owe are run (feature 318's scoped re-check).

## Success Criteria

- **SC-001** (FR-001): a test fails if any way, corridor or strip is reserved or recorded before the last house is seated on a
  nucleated roll.
- **SC-002** (FR-002): a test on a constructed site: a dooryard opening only onto ground cut off from the way-out side (across
  water) is not counted open; one opening onto connected ground is.
- **SC-003** (FR-003, FR-004): the cohort passes every seed main passes; the reference spec and the 10/20/40-household bookend
  seeds reach every household; no map's field goes unreached.
- **SC-004** (FR-005): the bookends against main recorded, with the perf records their band owes.
- **SC-005** (FR-006): the record and claims checks owed answer clean, or their findings are filed.

## Decisions Recorded

- The room between neighbors is feature 318's lane's room (a map drawing convention, page 0081); nothing else is kept open.
- Whether a way out exists is still asked of a margin before seating (it chooses the site), but answered by ground, not by a
  reserved corridor.

## Assumptions

- The row and dispersed forms already seat with no exit strip; their branches of the track and gateway code are the model.

## Review history

- Round 1 (spec-fidelity, 2026-10-04): CHANGES REQUIRED - FR-001 narrowed to the two named reservations (a row village's
  streets untouched), FR-005 covers both, the Summary's room named by its constant; applied.
