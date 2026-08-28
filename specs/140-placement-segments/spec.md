# Feature Specification: Placement Measures Against a Few Segments, Not Thousands of Vertices

**Feature Branch**: none (`SPECIFY_FEATURE=140-placement-segments`)

**Created**: 2026-08-28

**Status**: APPROVED by `spec-fidelity` - round 3 verdict **FAITHFUL** (2026-08-28), after round 1 (a ring of hundreds; a hull across bays; the gate's measure; SC-001) and round 2 (the chain OPEN on the house side; the GM's under-ten figure; an FR opening 140). Implementation may proceed.

**Input**: [`gm-request.md`](gm-request.md), verbatim. That file is the authority.

## The feature, in one sentence

Homestead placement stops measuring seats against the field's full outline (49-73 vertices) and the
polder's drawn dike band (2,880 vertices) and measures instead against a FEW segments that follow the
same edge - the outline simplified to a handful of chords (a few per side, following its bays, never the
forty or seventy) and the dike's crest simplified the same way, each pushed out by the simplification's
own tolerance so it still contains the ground it stands for - and the gate checks that measure those two
shapes measure the same few segments; the maps are allowed to move (the GM: *"I do not require any of
these maps to maintain bite identity now or at any time"*), and every pool map that moves is reviewed.

## Why this exists (the GM's words)

- *"49-73 verticies still sounds like a lot ... you could do this in fewer than ten vertices for the
  reference hamlet ... a few line segments on one side of the field that you are checking that you are on
  the correct side of when placing a farmstead and that you are not overlapping with or that you are sub
  minimum distance from"*
- *"thousands of vertices is obviously bad ... draw a single line segement along the edge of the actual
  polder boundaries and then put the houses on one side of it"*
- *"I am happy with the maps being allowed to move ... none of what we have done so far is in any way
  canonical"*
- *"our automated checks need to fundamentally be testing the same kind of thing as our placement
  algorithm"*
- *"do the vertices improvement as a task and then open a new feature for this"* - the checks-and-corpus
  audit is feature 141, not this one.

## User Scenarios & Testing

### User Story 1 - the polder's seats are tested against a few chords along the dike (Priority: P1)

**Acceptance**: **Given** the seed-19 polder, **When** homesteads are placed, **Then** no seat test walks
the 2,880-vertex band; the keep-out is the dike's CREST simplified to at most twenty chords around the
whole ring (Douglas-Peucker at a stated tolerance), pushed out by the band's measured reach plus that
tolerance, so it contains every vertex of the drawn band (a test proves it) and a seat is judged by side
and distance against those chords; the drawn dike is unchanged; `stage_homesteads` drops from ~9 s to
under 1 s.

### User Story 2 - the field edge is an OPEN chain of a few chords on the house side (Priority: P1)

**Acceptance**: **Given** a scripted hamlet (whose cluster seat is planned before any house is placed),
**When** a seat is tested against a field, **Then** the test uses an OPEN chain - the outline's chords that
FACE the cluster seat, the GM's *"three ... maybe five or six"*, not forming a closed shape - each pushed
out by the tolerance so no part of the drawn outline lies on the house side of its chord; the seat is
judged by which side of the chain it falls on plus the minimum distance the rule already carries
(`HOUSE_PADDY_GAP_FT`); a field with houses on two sides gets two chains. Measured on the real maps at a
6 px tolerance: the reference hamlet 5 chords / 6 vertices (the GM: *"fewer than ten vertices"*), the
seed-19 polder 7 chords in two chains, cohort seeds 4-6 chords. A settlement whose engine plans no seat
(the legacy village roll) keeps a closed simplified ring, because it has no house side to face.

### User Story 2b - the gate measures the same segments (Priority: P1)

**Acceptance**: **Given** the checks that measure a house against the field edge or the dike
(`houses_clear_of_paddies`, `structures_clear_of_dike`, and any sibling measuring those two shapes),
**When** the map is gated, **Then** they read the same simplified segments the placer used, recorded on
the manifest beside the drawn shapes, so placement and check are one measure and the checks' cost falls
with the placer's.

### User Story 3 - the maps that move are reviewed (Priority: P1)

**Acceptance**: **Given** the four live pool hamlets and the reference regenerated on the finished engine,
**Then** each manifest is compared with the baseline's; every map whose manifest changed gets a
`settlement-review` pass before the push, and the change is recorded (constitution XII: a deviation, with
its reason).

### Edge Cases

- A field whose houses stand inside a bay of the outline: the simplified chords follow the bay (the
  tolerance is a few px), so the seat stays buildable; only a seat within the tolerance of the edge can
  flip - the map may move by feet, reviewed.
- A dike with gaps (sluice openings): the control ring still surrounds the ground; a house never sat in a
  sluice gap under the band either.
- The consumers of `block_polys` other than the fit (the commons scatter, the marsh, near-ring paddies)
  read the control ring too and keep off the same ground.

## Requirements

- **FR-001**: The dike's placement keep-out MUST be the crest simplified to a few chords (at most twenty
  around the ring; the tolerance and the count recorded), pushed out by the band's measured reach plus
  the tolerance; the drawn band MUST be unchanged, and the keep-out MUST be recorded on the manifest's
  dike entry.
- **FR-002**: Every field test in placement (the bundle fit, the field keep-out index, the wall-on-the-bund
  test, the near-field test) MUST measure an OPEN chain of the outline's chords facing the cluster seat -
  three to six per side houses stand on, under ten vertices in total on the reference hamlet, more chains
  where houses stand on more sides - judging the side of the chain and the minimum distance; never the
  full outline and never a closed ring where a seat is known. The chains MUST be recorded on the
  manifest's field entry. Where no seat is planned (the legacy village roll), a closed simplified ring
  stands in, and the record says which.
- **FR-002b**: The gate checks that measure a house against the field edge or the dike MUST measure the
  recorded chords, not the drawn outline or band - one measure for placement and check.
- **FR-003**: The dike's ring MUST contain the drawn band; a field's chain MUST be no looser than the
  outline on the house side: no part of the drawn outline lies on the house side of its chord, so a seat
  the outline would refuse in the chain's reach is never accepted (a test proves both on random outlines
  and on a drawn dike).
- **FR-006**: This feature MUST open feature 141 - the checks-and-corpus audit - with the GM's words on it
  captured verbatim in its own `gm-request.md`, and MUST do none of that audit here.
- **FR-004**: The maps MAY move; every changed pool map and the reference MUST be reviewed by
  `settlement-review` before the push, and the seed-19 polder's stage timing recorded before/after.
- **FR-005**: Defects found on the way are fixed here (constitution XIV).

## Success Criteria

- **SC-001**: seed-19 polder `stage_homesteads` under 1 s (from ~9 s) and its roll under 18 s; the
  reference's field tests measured in milliseconds; the two gate checks' cost recorded before/after.
- **SC-002**: the containment tests pass; `make done` green; no gate check newly fails on any regenerated
  live map.
- **SC-003**: every changed map has a review verdict recorded.

## Assumptions

- The house side is the side facing the planned cluster seat; the chain is the run of the outline's
  chords whose outward normal points toward that seat (two runs where the seat faces two sides).
- The dike's keep-out stays a closed ring of the crest's chords: a ring dike's houses stand inside it, so
  the side they stand on is the whole inner edge - the GM's rule applied to a closed feature (the round-2
  reviewer's own note), not an exception to it.
- The seat test on the far sides of a field is carried by the crop-plot test (`_hard_clear`, bbox-gated
  and cheap), which a house cannot pass on a plot; the chain is the setback rule on the side houses
  stand.
- The scatter's cost (sample volume against small outlines) is not this feature's; the comb solver is not
  this feature's; the checks-and-corpus audit is feature 141.
