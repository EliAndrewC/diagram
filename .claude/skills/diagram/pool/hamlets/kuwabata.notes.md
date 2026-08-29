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

- 2026-08-29 feature 147's own `make overlap-audit`, on its first run against this map, found ink on
  water: one reed tuft 4.6 px from the inlet hairline with three of its blades drawn across it. MECHANISM:
  `draw_comb_field` drew the source pond's reed fringe BEFORE the field's channels were inked or recorded,
  so the reed keep-out - which does keep off every drawn watercourse - had nothing to keep off. On a comb
  map the source pond sits away from the channels and it never showed; on a polder the inlet hairline runs
  straight through the reservoir's fringe. FIXED in the same work (constitution XIV): the ring is handed
  back and scattered once the channels exist. The fringe's own rng is seeded from its bbox, so the scatter's
  draw order is unchanged - only the keep-out now sees what it must avoid.

- 2026-08-29 the GM's third review (T55): a vegetable ground lay across the irrigated channel beside
  it. Fixed in `build_polder`: a channel that crosses a parcel cuts it, and the rest of the outline is
  projected onto the band's edge (0 of 335 stroke samples remain inside a parcel). Two other approaches
  were measured and declined - see `_plots_clear_of_channels`.
- 2026-08-29 settlement-review DELTA of T55: PASS on the GM's own complaint, verified by a
  manifest-free pixel count (0 of 130 tilled-row elements on water; every channel at full nominal width
  along its whole run). CAUGHT: the `WATERWARD_DEPTH` comment citing 400 for a 280 constant; a garbled
  and stale `scatter_audit` paragraph here; a 1.2 px berm where the fabric keeps 7 (the cut edge met the
  waterline - fixed, `BERM` is now set from the fabric's own median); and the unguarded assumption that a
  280 px strip outlasts every crop (fixed: `waterward_strips_run_off_the_frame`). Also measured for the
  record: the cut costs 0.29% of the block's area against the 3.4% the declined half-plane clip cost, and
  four of the five cut edges wander at or above the fabric's median, so no cut reads as ruled.

- 2026-08-28 settlement-review FULL: needs-work -> fixed (crossings, title, caption). DELTA after
  the audit items: needs-work -> fixed (the north gate on the drawn stroke; banana as stools; cane
  in rows; pens before sties). Open: 3 pits of 16 against a 0.465 share (the manure placer seats
  by the privy and fails silently where the privy took the wall) - pre-existing for heaps too.

- 2026-08-28 the GM's second review (T54): the marsh haze lay over the mulberry dikes and past them.
  Both halves fixed - `marsh()` keeps every role's ink off any dike band or pond bank, and the
  waterward strip follows the dike's outer FACE instead of lapping 60 px inward. Priced and declined:
  clipping the strip to the dike's outer EXTREME (simplest, but it opened a dry apron up to 40 px wide
  wherever the ring wanders inward - the render showed it). Bug found and fixed on the way: binning
  the face over the whole ring let the EAST face win the bins the west face's crossing gaps left
  empty, and the west strip came out 2,422 px wide (the whole map wet, three checks red).
- T54's shore rule reaches EVERY map with a marsh beside water, by design: Inashiro, Mizuguchi,
  Kashikawa and Sawada each lost the marsh marks that had washed over their pond or a channel bed.
  Their geometry is untouched - the only manifest field that moved is `ink_classes` (the interactive
  census of marks per class). The commit that made the change said "pool manifests unchanged", which
  was wrong in that one field; recorded here rather than rewritten, since the history is the record.
- 2026-08-28 settlement-review DELTA of T50-T53: needs-work -> fixed (the NW ring corner's 1 ft
  seam - toes now overshoot 3 ft into their trunk; lane 9's hook - the final junction pass ends a
  lane where it first meets the way). See docs/review-ledger.md.
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

- `scatter_audit` has no dike-pond mode. Re-measured by the review of 2026-08-29 after T55: 2,988
  violations, of which 2,171 are `crown inside crop` (the archetype's OWN mulberry banks - the audit's
  crop keep-out predates the archetype), 564 `blade inside marsh` (commons grass grading into the reeds,
  which the doctrine admits over the same feather band), 133 `crown inside marsh` and 120 `crown inside
  water` - of which 0 crown centers stand inside pond water or a channel band; every one is inside the
  audit's pad only, and 67 are on the cut parcels because their banks are now correctly tighter. A clean
  bill cannot be earned on this archetype until the audit knows it.
- PERFORMANCE, measured against the pre-T54 tree in a detached worktree: Kuwabata's gen was 13-17 s and
  is now 27-32 s (the machine's own noise is +/-20% on both). The cost is T54's marsh keep-out, which
  asks a per-scatter-point question of every mound, plus the face-following waterward strips, whose
  outlines are 30-60 points where they used to be 4 - `point_in_poly` on the strip is the hottest test
  on the map (`stage_waterward` 0.68 s -> 7.4 s, `stage_hinterland` 3.5 s -> 9.8 s). Clawed back so far:
  the band is tested as its CREST + half-width rather than a 360-point ribbon, the strips are a 280 px
  band rather than a half-canvas the crop throws away, the face is thinned to square steps, and mounds
  and banks are pruned to each marsh's own bbox. T55's own parcel cleanup costs 0.02 s and runs on the
  winning block only, never on the 45 the acreage fit tries. No other map is affected: with no dike and
  no dike-ponds recorded the keep-out sets are empty and the per-point cost is a length check.
- The south outfall's surroundings, measured after the notch step-in landed (2026-08-29): the strip's
  inner edge now dips into the cut (edge y 2249.8 -> 2200.4 -> 2227.9 across x 2293-2354), the sluice
  gate is still drawn, and no mark stands on the band. The ground right at the mouth is still barer
  than the flank either side (13 marks in the 120 ft window against 43 on the control stretch, nearest
  mark 41.7 ft from the notch center) - and that residue is NOT the strip's shape: it is the outfall
  channel's own keep-out (a tint circle stands 30 px off a bed, a tuft 9 px, so the water's own
  corridor is bare by rule) plus the 46 px reed feather. Recorded rather than chased: the region is
  honest, and the remaining bareness is water, not dry ground.
- The reviewer's first cut of this rule was DEAD CODE and shipped as done: the step was an `elif` on an
  empty bin, and a notch bin holds 14 outline points (the ring's cut ends fill it), so it fired 0 times
  on all four flanks. The lesson is the standing one - a rule that cannot fire looks exactly like a
  rule that passes - and the guard is now a unit test that steps a notch whose bin is FULL.
- OPEN QUESTION for the GM, raised by the review of 2026-08-28 and NOT settled here: which way the
  reed density should run at a DIKED toe. Our strip feathers on every edge, so now that its inner
  edge is the dike face the ramp lands on the water side - 6% ink in the first 10 ft, full density
  at ~30 ft. The reviewer's search of the reed-zonation literature (Phragmites/Scirpus depth-gradient
  work, Lake Balaton, Dutch wave-exposure studies) says stem density RISES as the water shallows,
  which argues the densest reed should hug the toe; against that, a maintained polder dike's toe is
  walked, cut for withies and kept clear, which is the bare berm we now draw. If both stand for the
  same ground it is a KNOB (constitution XII); the reviewer's own read is that they split by
  SITUATION - berm on a diked margin, gradient on an undiked toe marsh - which needs no knob. Those
  citations came from the review pass and have NOT been re-read by a `source-reader`; they are
  SUMMARY-ONLY until they are, and nothing in the engine rests on them today.
- A 40-60 ft ring around the reservoir carries no cover at all - the seam between the pond fringe
  polygon's outer edge and where the toe/waterside cover picks up. Invisible at fit zoom against the
  tan ground (settlement-review 2026-08-29); worth a look if the fringe polygon is ever resized.
- Three windbreak crowns stand ~1 radius onto the pond fringe's east edge (2022,612), (2028,618),
  (2034,660) - invisible at fit; the belt is laid after the fringe and does not read `wet_polys`.
- The drain trunk is the engine's gray-blue drain palette (`#7C9EB0`) while the head canal and
  laterals are the bright canal blue: a standing convention (drains vs supply), not the water
  block's layering; the reviewer read it as a tonal change at the ring's corners.


- The acreage per household is the PADDY figure (`GROSS_ACRES_PER_HOUSEHOLD`); whether a silk-and-
  fish household held the same ground is a research question for the feature-139 audit.
- The pool sweep and the polder cohort are owed at unlock (scope locked at conversion time).
