# Tasks: the pool sweep's recorded findings

**Feature**: 152-pool-sweep-findings | **Spec**: [spec.md](spec.md) (FAITHFUL) | **Plan**: [plan.md](plan.md)

Every task is classified `research: rendering` or `research: physical` (constitution v2.12.0). A physical
task carries the three boxes. Most of this list is rendering: the placement rules it repairs were already
researched, and the task is to make the drawing obey them.

## Phase 1 - the windbreak, first because it moves canopy on every map

- [ ] T01 Measure the before-state on EVERY pool map, not just the reviewed four: houses beyond the drawn
      belt's across-wind ends, drawn vs `clumps_offpage`, belt span vs cluster span. *(rendering)*
- [ ] T02 Replace the one-axis off-page proxy in `settlement/homestead_parts.py` with a test against the
      actual crop box, so a clump on the page is drawn. Record the mechanism at the point of change.
      *(rendering)*
- [ ] T03 Re-roll and re-measure T01's table. SC-002: no farmhouse beyond the belt's ends on any map.
      *(rendering)*
- [ ] T04 If a residue remains after T02, judge whether the belt's EXTENT (not the trim) is short, and fix
      that too - FR-003's first limb. *(rendering)*

## Phase 2 - the two the GM named in their own words

- [ ] T05 FR-001: the tameike finding into the marsh class record in `interactive/classes.py` - `why`,
      `sources` (the seven keys registered in feature 150), `entry`. Both halves of the one finding: the
      shore is reeded BECAUSE management sustains it, and the bank is mown to keep it strong. *(rendering
      - the research is done, cited and confirmed; this is putting it in front of the reader)*
- [ ] T06 FR-001 verification: render a map with a pond fringe and confirm a reader clicking marsh sees
      the finding and its sources. *(rendering)*
- [ ] T07 FR-002: the privy/manure seat roll consults `plan.windward`. The three attested seats and their
      weights stay; the preference among them reorders so a seat within 90 degrees of windward loses to
      one that is not. *(physical - which side of a house a privy stood on is a fact about how these were
      built; the three seats are already researched and cited in the code's own research block, and this
      task only chooses AMONG them)*
      - [x] research pass - the record already answers it: the three seats (back door, 戸口便所 gate, by
        the naya) are attested and recorded at `_PRIVY_SEATS`; what is NOT recorded is a rule putting the
        privy downwind, and the sweep's own source for wind-relative siting of subsidiary farm structures
        is SUMMARY-ONLY (Journal of Asian Architecture and Building Engineering, Nov 2022)
      - [ ] source-reader confirmed - the SUMMARY-ONLY citation above must be read or replaced before the
        rule is written down as a finding rather than as a preference among attested seats
      - [ ] recorded and cited
- [ ] T08 FR-002 verification: privies and manure pits within 90 degrees of windward, per map, before and
      after. SC-001: Sawada 12/12 to a minority. *(rendering)*

## Phase 3 - features that draw wrong

- [ ] T09 FR-004: a copse draws as a distinguishable stand - not 2 clumps in a 205-313 ft record, not
      seated inside the windbreak's canopy. *(rendering)*
- [ ] T10 FR-007: the flooded-plot tint tests the FINAL ring's AREA as well as its sharpness. *(rendering)*
- [ ] T11 FR-008: persimmon fruit dots vary per tree off the map's position hash. *(rendering)*
- [ ] T12 FR-006: the caption seat filter gains a fabric term and a way-side term. *(rendering)*

## Phase 4 - the lane web

- [ ] T13 FR-009: a lane link within the join reach is not defeated by one movable farm fixture.
      *(rendering)*
- [ ] T14 FR-010: a lane reaches something - threshold derived from the existing rule, not invented.
      *(rendering)*
- [ ] T15 FR-011: a through-route keeps its width across a junction. *(rendering)*

## Phase 5 - records that disagree with the map

- [ ] T16 FR-012: seated fixture counts against their declared shares - MEASURE first; the fix may be the
      placer or may be what the share means. *(rendering)*
- [ ] T17 FR-013: the homestead fixture ring varies its offset and pitch off the map's hash. *(rendering)*
- [ ] T18 FR-014: `make jogs` green on every pool map. No ledger arm. *(rendering)*
- [ ] T19 FR-015: every notes file describes the map that ships - Kashikawa's absent byre, Inashiro's
      stale counts, Mizuguchi's board. *(rendering)*

## Phase 6 - the knobs, last

- [ ] T20 FR-005: copse siting becomes a per-settlement knob, rolled from the map's seed. *(rendering)*
- [ ] T21 FR-016: kosatsuba siting becomes a per-settlement knob. *(physical - both forms are attested;
      the takafuda stood at crossroads and bridgeheads AND at the village well)*
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
- [ ] T22 One map per knob VALUE - four rolls (constitution VI), read and recorded.

## Phase 7 - acceptance

- [ ] T23 Pool re-rolled; `make maps` to the standard of before.
- [ ] T24 A `settlement-review` pass over the changed maps, paired with the gate; no NEW error.
- [ ] T25 `make done` green; push by the LOCAL-GATED route.
