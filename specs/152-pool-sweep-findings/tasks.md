# Tasks: the pool sweep's recorded findings

**Feature**: 152-pool-sweep-findings | **Spec**: [spec.md](spec.md) (FAITHFUL) | **Plan**: [plan.md](plan.md)

Every task is classified `research: rendering` or `research: physical` (constitution v2.12.0). A physical
task carries the three boxes. Most of this list is rendering: the placement rules it repairs were already
researched, and the task is to make the drawing obey them.

## Phase 1 - the windbreak, first because it moves canopy on every map

- [x] T01 Measure the before-state on EVERY pool map, not just the reviewed four: houses beyond the drawn
      belt's across-wind ends, drawn vs `clumps_offpage`, belt span vs cluster span. *(rendering)*
- [x] T02 Replace the one-axis off-page proxy in `settlement/homestead_parts.py` with a test against the
      actual crop box, so a clump on the page is drawn. Record the mechanism at the point of change.
      *(rendering)*
- [x] T03 Re-roll and re-measure T01's table. SC-002: no farmhouse beyond the belt's ends on any map.
      *(rendering)*
- [x] T04 The residue after T02 is 3 houses of 82, and it is NOT the belt's extent: on all five maps the
      belt POLYGON covers every house (measured along the across-wind axis - Kashikawa 204..1136 against
      houses 307..1066, Kuwabata 693..1440 against 782..1340, Sawada 2458..3299 against 2546..3209). Two
      of the three are the belt clipping at the page, which the doctrine explicitly permits - their
      remaining undrawn clumps sit at exactly that end, off the view. The third is Kuwabata's, 24 ft,
      under one clump diameter. So FR-003's first limb needs no change: the belt was never short, and
      SC-002 was revised to measure the belt rather than the crop. *(rendering)*
      **A measurement error of my own is recorded here** because it nearly sent me to fix a
      non-defect: I first tested page-containment by projecting the view's corners onto the across-wind
      axis and checking a 1-D range. That is invalid for a diagonal axis - the projection of an
      axis-aligned rectangle onto a diagonal covers points outside the rectangle - and it reported
      Kashikawa's off-page clumps as on-page, contradicting the 2-D partition in `set_view`, which is
      correct. Trust the 2-D test.

## Phase 2 - the two the GM named in their own words

- [x] T05 FR-001: the tameike finding into the marsh class record in `interactive/classes.py` - `why`,
      `sources` (the seven keys registered in feature 150), `entry`. Both halves of the one finding: the
      shore is reeded BECAUSE management sustains it, and the bank is mown to keep it strong. *(rendering
      - the research is done, cited and confirmed; this is putting it in front of the reader)*
- [x] T06 FR-001 verification: render a map with a pond fringe and confirm a reader clicking marsh sees
      the finding and its sources. *(rendering)*
- [x] T07 FR-002 (REWRITTEN by the GM's ruling of 2026-08-29 - see below): the privy/manure seat roll consults `plan.windward`. The three attested seats and their
      weights stay; the preference among them reorders so a seat within 90 degrees of windward loses to
      one that is not. *(physical - which side of a house a privy stood on is a fact about how these were
      built; the three seats are already researched and cited in the code's own research block, and this
      task only chooses AMONG them)*
      - [x] research pass - the record already answers it: the three seats (back door, 戸口便所 gate, by
        the naya) are attested and recorded at `_PRIVY_SEATS`; what is NOT recorded is a rule putting the
        privy downwind, and the sweep's own source for wind-relative siting of subsidiary farm structures
        is SUMMARY-ONLY (Journal of Asian Architecture and Building Engineering, Nov 2022)
      - [x] source-reader confirmed - the paper was fetched and READ, and it CONTRADICTED the wind
        hypothesis: toilets went southeast and south for solar warmth to speed fermentation, 72.7% of them
      - [x] recorded and cited - research/homesteads.md and SOURCES.md `wang-ochiai-2022`
- [x] T08 FR-002 verification: privies and manure pits within 90 degrees of windward, per map, before and
      after. SC-001: Sawada 12/12 to a minority. *(rendering)*

## Phase 3 - features that draw wrong

- [x] T09 FR-004: a copse draws as a distinguishable stand - not 2 clumps in a 205-313 ft record, not
      seated inside the windbreak's canopy. *(rendering)*
- [x] T10 FR-007: the flooded-plot tint tests the FINAL ring's AREA as well as its sharpness. *(rendering)*
- [x] T11 FR-008: persimmon fruit dots vary per tree off the map's position hash. *(rendering)*
- [x] T12 FR-006: the caption seat filter gains a fabric term and a way-side term. *(rendering)*

## Phase 4 - the lane web

- [x] T13 FR-009: a lane link within the join reach is not defeated by one movable farm fixture.
      *(rendering)*
- [x] T14 FR-010: a lane reaches something - threshold derived from the existing rule, not invented.
      *(rendering)*
- [x] T15 FR-011: a through-route keeps its width across a junction. *(rendering)*

## Phase 5 - records that disagree with the map

- [x] T16 FR-012 (largely closed as a side effect of T07 - the shortfall was seat REFUSAL, not the share): seated fixture counts against their declared shares - MEASURE first; the fix may be the
      placer or may be what the share means. *(rendering)*
- [x] T17 FR-013: the homestead fixture ring varies its offset and pitch off the map's hash. *(rendering)*
- [x] T18 FR-014: `make jogs` green on every pool map. No ledger arm. *(rendering)*
- [x] T19 FR-015: every notes file describes the map that ships - Kashikawa's absent byre, Inashiro's
      stale counts, Mizuguchi's board. *(rendering)*

## Phase 6 - the knobs, last

- [x] T20 FR-005: copse siting becomes a per-settlement knob, rolled from the map's seed. *(rendering)*
- [x] T21 FR-016: kosatsuba siting becomes a per-settlement knob. *(physical - both forms are attested;
      the takafuda stood at crossroads and bridgeheads AND at the village well)*
      - [x] research pass - both forms attested: the takafuda stood at crossroads and bridgeheads AND
        at the village well; recorded at `KOSATSUBA_SITINGS` in `hamletgen/consts.py`
      - [x] source-reader confirmed - the two-sided finding came from the settlement-review's own search
        and is recorded as a KNOB rather than a picked answer, which is what constitution XII asks
      - [x] recorded and cited
- [x] T22 One map per knob VALUE - four rolls (constitution VI), read and recorded.

## Phase 7 - acceptance

- [x] T23 Pool re-rolled; `make maps` CLEAN - better than the standard of before, which carried the seed-37 tripwire failure.
- [ ] T24 A `settlement-review` pass over the changed maps, paired with the gate; no NEW error.
- [ ] T25 `make done` green; push by the LOCAL-GATED route.

## T13 and T14 closed by MEASUREMENT rather than by a change (2026-08-29)

Both recorded findings were real when the sweep took them and are not on the map that ships. Recorded
here with the measurement, because "we looked and it is not there" is a result and the next session
should not re-derive it.

- **T13, the back lane severed by a woodpile.** Every SCRIPTED map's lane web is now ONE connected
  component (union-find over the lanes at a 4 ft touch). Kuwabata's 25 ft gap is gone, closed by this
  feature's other work rather than by anything aimed at it. A woodpile-yields fallback WAS built for it
  and measured as a no-op - the note is at the point of change in `ways.py` so nobody builds it twice.
- **T14, a lane reaching nothing.** Measured against the engine's OWN rule (`lanes_reach_something`: a
  way within 40 ft, a farmhouse within 90, or the field at the spur setback), **no lane end on any
  scripted map reaches nothing**. Kashikawa's lane 0 - the review's case - ends 17.0 ft from the paddy
  edge: it is a field spur arriving at the crop, which is the one purpose that rule explicitly counts as
  service. The review measured distance to lanes and farmhouses and not to the field, and the map has
  re-rolled since.

## Pre-existing failures met along the way, verified against main and NOT adopted

`houses_clear_of_lanes` fails on Kashikawa and Sawada. Both fail identically on main's own manifests
(baselined 2026-08-29), so neither is this feature's. Sawada's is the same house as main's,
(1826, 2438); Kashikawa's is a different house because the map re-rolled entirely, and disabling this
feature's route-width pass leaves it failing, so T15 did not cause it. They stay ledgered.

## A 15th defect, met while working and NOT adopted (2026-08-29)

`houses_clear_of_lanes` fails on Kashikawa and Sawada, and is **pre-existing on main** (baselined; Sawada's
is the same house main reports, (1826, 2438)). It is not one of the fourteen the GM pointed at, and it is
recorded here rather than fixed because the diagnosis lands in door-path geometry rather than anywhere this
feature touched:

Measured properly - the check tests the house's CORNERS against the lane CENTERLINE, not its centre, which
is what my first measurement got wrong and why it found nothing. Both offenders are 2-point 3 ft door
paths clearing a NEIGHBORING corner of the house they serve: **Sawada lane 13 at 2.78 ft where the check
wants 3.5 (short 0.72); Kashikawa lane 11 at 0.81 ft (short 2.69)**. A door path necessarily ends at its
house, so its last stretch is close by construction; what fails is the clearance to the OTHER corners.

Confirmed not to be this feature's: disabling `_keep_the_route_wide` leaves Kashikawa failing, and that
pass only acts on cart-width lanes (w >= 5) while both offenders are 3 ft paths.

