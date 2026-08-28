# Design notes: Kuwabata (桑畑, "mulberry field"), the CASH-CROP hamlet - SCRIPTED

*Rewritten 2026-08-27 (feature 139) when the map was converted from a hand-authored script to a
`hamletgen` declaration. The earlier notes (reconstructed 2026-08-08 from the old generator's
comments) are in git history with that script; what they recorded that still holds is carried here.*

**Subject**: 16 households on polder geometry carried to the dike-pond system's rare
**wholesale-conversion end state** - 桑基魚塘, the `mulberry_dike_fishpond` archetype: (almost)
every former paddy cell dug into a fish pond and the spoil piled into a mulberry-planted dike
around it. The END STATE is deliberately the exception; the scattered overlay is the norm
(research/archetypes.md "The three overlay values"). Reading this map as typical would be the
mistake it is here to make visible.

## The declaration

`HamletSpec(name="Kuwabata", seed=21, households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic")`

Seed 21 and 16 households are the hand-authored map's. `pond_layout="mosaic"` pins the form the GM
saw on it (the Pearl-delta accreted mosaic; the knob also rolls the surveyed grid - one map per
value is owed, the grid one at `wip/kuwabata-grid`). Everything else is derived: the grid fitted
to the acreage (`fit_polder`, 160 ft module, merge-heavy parcels - `POLDER_FABRIC`), the header
reservoir at the ring's head, the perimeter dike gapped at its sluices, the ponds and their banks
(`apply_land_use(eligible="all")`, `DIKEPOND_CONVERSION` 0.9), the village on the dry flank, the
reed fringe on the water-facing flanks (`stage_waterward`), the lanes, the fixtures, the bamboo,
the windbreak, the plank crossings clustered on the settlement side (`polder_crossing_caps`).

## What the conversion changed, and why

- **The village sits at the block's HEAD (north), not on the east flank** as the hand-authored map
  had it. `seat_cluster` seats a hamlet 背山面水 - back to the wind, tie-broken upslope - and for a
  south-falling polder under the NW winter wind that is the head. Research/archetypes.md 'Polder
  siting' attests the village on whichever dry ground the margin polder abuts; the head is dry
  ground here (the reservoir is beside it, not under it). The east-flank village was a hand
  decision, not a researched one; the derived seat is recorded as a GUESS between attested options
  until the audit says otherwise (spec 139, Decisions Recorded).
- **The waterward flanks are derived** (`waterward_flanks`): the cross flanks the village does not
  occupy plus the foot - `["W", "E", "S"]` here, where the hand-authored map declared `["W", "S"]`
  because its village took the east. The head is never a waterward flank (the reservoir stands
  there as the wild water).
- **The windward belt** wraps the cluster's NW as the belt stage derives it; the L-shaped belt in a
  reserved gap that the hand-authored script built by hand is not needed - the derived seat leaves
  the belt room.
- **Every reference-hamlet family is on the map** (`make family-census`): the fixtures (privy,
  woodpile, manure - here in its PIT form, rolled, bath shed, coop, hokora, persimmon), the new sheds, the bamboo, the lane
  web, the wells, the byres, the notice board. Absent by archetype: `dry_plots` (a comb's dry hem;
  a polder is a solid wet block), `field_ponds` (open water IS this fabric - no obstacle tiles,
  research D4), `field_ditches:branch` (a comb's deliveries; a polder has laterals).

## What the GM's audit added (feature 139 T40-T48, 2026-08-28)

See `settlements/archetypes.md` "The scripted dike-pond hamlet - the rules" and
`specs/139-kuwabata-dike-pond-hamlet/audit.md`. On THIS map, seed 21: no threshing floors
(forecourts recorded, no ink); manure form rolled PIT; three fry ponds (the smallest parcels,
same ink); a sluice gate at each of the two dike cuts; duck pens and pig sties on the ponds
nearest the houses (pens first); the dike crop pinned MULBERRY (the name), the leftover form
rolled VEGETABLES (the three unconverted parcels draw as tilled rows). The knob maps for the
other values are under `wip/kuwabata-*`.

## Review log

- 2026-08-28 settlement-review FULL: needs-work -> fixed (crossings, title, caption). DELTA after
  the audit items: needs-work -> fixed (the north gate on the drawn stroke; banana as stools; cane
  in rows; pens before sties). Open: 3 pits of 16 against a 0.465 share (the manure placer seats
  by the privy and fails silently where the privy took the wall) - pre-existing for heaps too.

- 2026-08-28 the GM's review of the map (T50-T53): two farmhouses and a garden in the reed
  fringe -> the fringe is hard ground (`wet_polys`) AND the cluster seat scores wet ground, so the
  cluster stands east of the reeds instead of losing two houses to far seats; the inlet stub reaches
  the reservoir rim (a 30 ft gap); the ring's toe collectors end ON their trunks (a 9 ft gap at the
  NW corner); lanes and water each composite in one block (junctions read as one tread / one flow,
  the pond's rim under the feeder's bed). Fallout the re-seated cluster exposed and fixed in the
  same work: the title pocket is reserved ONCE and, on a sheet with no blank box, OUTSIDE the
  content (the crop takes it in; the hug check counts the placard); the final junction pass repairs
  a hairpin at a door spur. Priced and declined: a 36 ft tread reach, a 2 ft forecourt allowance,
  rejecting zigzag links in the first pass, retiring short orphan pieces, re-rolling on a web in
  pieces - each re-solved Inashiro's web or regressed tripwire seeds 27/33. Inashiro's manifest
  differs from the HEAD roll in z-index fields only.

## The economy (GM-confirmed 2026-07-24)

A **cash-crop settlement, not a subsistence one** - the rice-farmer's analog of the tobacco or
indigo switch. Stocked carp ponds; the loop is mulberry leaf -> silkworm -> frass -> fish ->
dredged pond mud -> dike fertility. **Silk is the bigger earner**; fish go to market; grain is
bought in. Gazetteers found the total absence of rice remarkable enough to record. The market link is
the **connector lane** - to the market town, or to the river or canal that carries the goods there;
the map draws no creek or boats of its own. The GM (2026-08-28, feature 139 audit A1): a hamlet of
this kind need not sit on navigable water, and the lane is presumed to lead to whatever does.
Open flavor hook, NOT canon anywhere wider: L7R land tax is assessed in koku of rice, so
Kuwabata's tax is presumably commuted to cash or silk.

## No threshing floors (feature 139 T41, GM 2026-08-28)

A hamlet that grows no rice threshes none: the farmsteads draw no threshing/drying floor. The open
ground before each house is still RECORDED (`threshing_yards[].kind = "forecourt"`, no ink) because
the lane web threads around it and the trees, scrub and wells keep out of it - a silk-and-fish
household works its leaf, cocoons and nets on that ground. `meta.work_yards: false` declares it.

## What makes it a hamlet, not a village

No headman of its own, no shrine, no tax-free plots, no graveyard - its dead go to the village
district's ground. Drawn at 1 ft/px.

## Known open

- The acreage per household is the PADDY figure (`GROSS_ACRES_PER_HOUSEHOLD`); whether a silk-and-
  fish household held the same ground is a research question for the feature-139 audit.
- The pool sweep and the polder cohort are owed at unlock (scope locked at conversion time).
