# Design notes: Kuwabata (桑畑, "mulberry field"), the CASH-CROP hamlet - SCRIPTED

*Rewritten 2026-08-27 (feature 150) when the map was converted from a hand-authored script to a
`hamletgen` declaration. The earlier notes (reconstructed 2026-08-08 from the old generator's
comments) are in git history with that script; what they recorded that still holds is carried here.*

**Decision recorded (GM 2026-08-28, feature 143):** the dike-pond parcels are drawn at **6 parts water to 4 parts dike** as a *disclosed regional reading* - the classic prescription survives in both orders (基六塘四 on the page read; 六分为塘、四分为基 elsewhere; 7:3 in some districts). Kept as drawn; the interactive map's modal for this map's ponds and banks carries that sentence. Full record: `research/archetypes.html` "The 6:4 water-to-dike ratio, and coppiced mulberry".

**Subject**: 16 households on polder geometry carried to the dike-pond system's rare
**wholesale-conversion end state** - 桑基魚塘, the `mulberry_dike_fishpond` archetype: (almost)
every former paddy cell dug into a fish pond and the spoil piled into a mulberry-planted dike
around it. The END STATE is deliberately the exception; the scattered overlay is the norm
(research/archetypes.html "The three overlays a village may carry"). Reading this map as typical would be the
mistake it is here to make visible.

## Map notes

<!-- READ BY THE INTERACTIVE MAP (`l7r/diagram/interactive/notes.py`, feature 156): these bullets
     appear on the page's title card and in feature modals. Everything is optional and the reader is
     forgiving by design (GM 2026-08-29: "we should not presume that such sections exist ... should
     default to simply not pulling anything in if the parsing fails") - a missing, misspelled or
     half-written block simply contributes nothing. The key list and the format are documented in
     `l7r/diagram/interactive/CLAUDE.md`. Every other word in this file is prose and is never parsed. -->

### Place

- **district**: Aozawa
- **district direction**: west

*Aozawa (青沢, "green marsh stream") is INVENTED for this map - drawn from gm-assistant's
`place-names/pool.jsonl`, which carries its kanji and meaning, and not ruled on by the GM. The
DIRECTION is not invented: it is the bearing of this map's own connector track where it leaves the cluster.*

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

## What the GM's audit added (feature 150 T40-T48, 2026-08-28)

See `research/archetypes.html` "The scripted dike-pond hamlet - the rules" and
`specs/150-kuwabata-dike-pond-hamlet/audit.md`. On THIS map, seed 21: no threshing floors
(forecourts recorded, no ink); manure form rolled PIT; three fry ponds (the smallest parcels,
same ink); a sluice gate at each of the two dike cuts; duck pens and pig sties on the ponds
nearest the houses (pens first); the dike crop pinned MULBERRY (the name), the leftover form
rolled VEGETABLES (the three unconverted parcels draw as tilled rows). The knob maps for the
other values are under `wip/kuwabata-*`.

## Review log

- **2026-08-29 settlement-review, DELTA after the merge onto main** (the map re-rolled under a
  291-commit main): **needs-work, six errors**, four of which no gate check can see. Fixed here: the
  marsh HIT polygon still covering the mulberry banks while the ink was clean (the record half of the
  GM's own T54 complaint - 5.2% of the toe outline, 5 of 26 bank rings); the reed fringe at 48% of
  this map's own bed density with one empty 30-degree sector; the connector's 3.1 ft splice nub.
  Deferred with their measurements in `specs/150-kuwabata-dike-pond-hamlet/tasks.md` D1-D3: the back
  lane severed by 25 ft at a woodpile, the windbreak sheltering 3 of 16 houses, the caption lapping a
  garden. **What the author had got wrong**: the fringe had been called fixed on a TUFT COUNT, which
  was never the thing that was wrong.

- **2026-08-29 settlement-review, DELTA re-check of those three fixes**: all three verified
  independently, and **three more caught**. The reservoir's shore now has reeds but no WET TINT - a
  pond fringe can never carry it, because the tint's pond keep-out inflates the water by its own 28 ft
  radius while the fringe is only 44 ft wide; see the open question below. `_clipped_to_open_ground`
  contradicted its own docstring (it subtracted the dike BAND, not the filled block, and got the right
  answer only because the largest-piece tie-break happened to pick the outside one, silently
  discarding 65,325 sq ft) - now fixed by filling the ring, so the geometry does what the docstring
  says. And the write-up's claim that the 22 ft overrun "went with" the nub was a shapely-intersection
  artifact: the overrun is byte-identical in both rolls and is closed on the honest ground instead -
  it runs to a real three-way node, so it is a route rather than a hook.

- **2026-08-29: ACCEPTED by the GM** (feature 150 T99), after T50-T55 and four settlement-review
  passes. The map ships as the scripted dike-pond exemplar.

- 2026-08-29 settlement-review of that fringe fix: **needs-work, and it was right**. Deferring the fringe
  moved it past `block_polys.append(pond bbox + 10)` as well, and the reed scatter reads `block_polys` -
  so the reeds inherited a keep-out meant for BUILDINGS, covering the shore band itself. Measured by the
  reviewer's replay: 32 of 54 tufts gone, 45% of the annulus, three sectors empty, the tameike reading as
  a bare blue plate - 92% of the ink that fix actually changed, against the 3 tufts the channel rule
  intends. My commit message said "only the keep-out now sees what it is supposed to avoid", which was
  wrong. FIXED: the no-build rect follows the reeds again, as it always did. Now 52 tufts in the annulus,
  0 marks on the water, and the ink delta is 13 marks rather than 149.
- OPEN (reviewer's nitpick): two call sites build the identical `+40` fringe ring by hand
  (`hamletgen/sink.py` and `settlement/fields/comb.py`) and only one is subject to that ordering hazard.
  One shared helper would stop the next ordering change diverging them.
- 2026-08-29 feature 151's own `make overlap-audit`, on its first run against this map, found ink on
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
the map draws no creek or boats of its own. The GM (2026-08-28, feature 150 audit A1): a hamlet of
this kind need not sit on navigable water, and the lane is presumed to lead to whatever does.
Open flavor hook, NOT canon anywhere wider: L7R land tax is assessed in koku of rice, so
Kuwabata's tax is presumably commuted to cash or silk.

## No threshing floors (feature 150 T41, GM 2026-08-28)

A hamlet that grows no rice threshes none: the farmsteads draw no threshing/drying floor. The open
ground before each house is still RECORDED (`threshing_yards[].kind = "forecourt"`, no ink) because
the lane web threads around it and the trees, scrub and wells keep out of it - a silk-and-fish
household works its leaf, cocoons and nets on that ground. `meta.work_yards: false` declares it.

## What makes it a hamlet, not a village

No headman of its own, no shrine, no tax-free plots, no graveyard - its dead go to the village
district's ground. Drawn at 1 ft/px.

## Known open

- `scatter_audit` has no dike-pond mode. **Re-measured 2026-08-29 on the roll that shipped** (this
  paragraph has now gone stale twice, both times caught by a review, so re-measure it whenever the map
  is re-rolled and quote the roll): **2,787 violations**, of which **2,155** are `crown inside crop`
  (the archetype's OWN mulberry banks - the audit's crop keep-out predates the archetype), **576**
  `blade inside marsh` (commons grass grading into the reeds, which the doctrine admits over the same
  feather band), **46** `crown inside water+cutbank` and **10** `crown inside marsh`. The marsh clip
  took the crown family from 133 to 10 and the water family from 120 to 46; the ten that remain are in
  the audit's feather pad, not on drawn water. Density beyond the water keep-out: 0-15 px = 366,
  15-30 px = 346, 30-45 px = 59. A clean bill cannot be earned on this archetype until the audit knows
  the dike-pond.
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
- **PARTLY ANSWERED 2026-08-29 by a `source-reader` pass on the tameike record** (research/water.html
  "A reservoir's shore is reeded, and its EMBANKMENT is mown"). The half that is settled: the
  reviewer's "berm on a diked margin" read is CORRECT for the embankment itself and for the reason
  the reviewer guessed - a tameike's 堤 is mown and burned and may not be cultivated, **to keep the
  bank strong**, and the plants recorded on it are dry-grassland herbs. That is an independent
  confirmation of the GM's own T54 rule, arrived at from the other direction. The half that is
  OVERTURNED: the intuition that a *maintained* pond has a bare *margin*. Mineta 2007 (JSIDRE),
  on a Kagawa study, found a statistically significant POSITIVE correlation between emergent-plant
  species counts and dredging and algae-cutting - active management SUSTAINS the reed fringe, and it
  is the abandoned ponds that lose it. So the shore is reeded and reads wet, which is why the fringe
  now carries the wet tint. Still NOT-FOUND, and the search was run and named it: whether the record
  distinguishes a DIKED polder's wet foot from an UNDIKED valley toe. The line below stands for that
  remainder only.

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
- The drain trunk is the engine's own drainage hue (`#4F7186`, a dark slate blue) while the head canal and
  laterals are the bright canal blue: a standing convention (drains vs supply), not the water
  block's layering; the reviewer read it as a tonal change at the ring's corners.


- The acreage per household is the PADDY figure (`GROSS_ACRES_PER_HOUSEHOLD`); whether a silk-and-
  fish household held the same ground is a research question for the feature-139 audit.
- The pool sweep and the polder cohort are owed at unlock (scope locked at conversion time).

## 2026-08-29 - feature 153, the highlighting changes (page-side)

The drawn map is unchanged in substance: the manifest moved only in `z` ordinals, and the PNG differs on
18,640 of 12,181,000 pixels, every one of them by 1 or 2 of 255 - clip-edge antialiasing from splitting
the perimeter dike's planted rows into their own string so they can carry their own highlight tone.

`settlement-review` read the delta (scoped to the lit appearance, the hit regions and the changed
strings, since the ink did not move) and returned **needs-work**, catching two defects the gate could
not see: the perimeter dike's willow and mulberry still flattening to gold when lit (36,843 px), and the
pond sluice's widened hit box winning only 42.4% of its own area because 49 of the 52 sluices are drawn
on a field ditch whose group came later. Both fixed and re-measured (sluice 88.6%, worst 75.8%); the
full row, including what was recorded rather than fixed, is in `docs/review-ledger.md`.

**Round 2 of that review** verified both fixes on its own measurements and caught the sluice fix
breaking the rule it was allowed under: the lifted box took 88.4% of a pig sty's own footprint and
42.8% of a duck pen's. The layer is clipped against every recorded structure now (75 holes for this
map's 75 records); each sty and pen is back to its main-branch share, and the sluice keeps 88.3% of its
box (96.0% of the widened stroke region, on the reviewer's stricter definition of "inside").

Two record corrections from that pass, both against my numbers: the raster delta from the dike split is
**45,564 px of 12,181,000, max 3 of 255** (not 18,640 / max 2), and in a browser the two pages render
pixel-identical unlit; and the perimeter dike is **4,591 ft along its crest** - the manifest's `outline`
is the band polygon, 1.99x that, so the sibling text's "half an hour" was a double count and now reads
"the better part of twenty".

**Round 3** verified the clip on all 75 structures (+0.00 everywhere, 85,767 sample points) and found
this map had been **missing from `make maps` since its conversion to `hamletgen` on 2026-08-27** - the
tier sweep filtered the frozen list by raw membership while `regen.py` asks `classify()`. The sweep asks
`classify()` now and Kuwabata is off the legacy list, so it is swept with the rest of the tier.

## 2026-08-29 - feature 152: D1-D3 are closed, and this file still called them deferred

The three deferrals recorded against this map are done, and an acceptance review found nothing here
saying so:

- **D1, the back lane severed by 25 ft at a woodpile** - closed. Every scripted map's lane web is now
  ONE connected component; this map's gap is gone, closed by other work rather than by anything aimed
  at it. A woodpile-yields fallback was built for it and measured as a no-op, and reverted with the
  reason at the point of change.
- **D2, the belt sheltering 3 of 16 houses** - closed. The trim that decides which clumps are drawn now
  tests the real page rather than a 48 ft proxy for it, and houses standing beyond the belt's ends went
  3 of 16 to 1. (The clump figures this bullet used to quote were an intermediate roll's and
  contradicted the same file four paragraphs down; the shipped counts are in the Census block.)
- **D3, the caption lapping a garden** - closed twice over: it resolved itself on the re-roll, and the
  seat filter now carries a fabric term and a way-side term regardless.

**Closed 2026-08-29:** `village_windbreak_is_continuous` passes here. The gaps it used to flag were
two separate things and each needed its own answer. The planted run's interior holes were filled by
seating at the belt polygon's real depth rather than on the chord between neighbors. The remaining
"gap" was not in the belt at all: the check bounded its scan by the belt POLYGON's across-wind extent,
and almost all of that extent is off the page - Kuwabata's belt polygon runs 693..1440 along its own
axis, the planting covers 734..1330, and fine-sampling the polygon at 4,000 points per column puts the
last on-page belt ground at u ~ 1350. So about **20 ft** of visible belt carries no canopy, under the
40 ft the check flags, and it reads at native resolution as the wood running off the page; the earlier
"entirely off-page" in this paragraph was 20 ft stronger than the measurement supports
(settlement-review, 2026-08-29). The check now clips its columns to the view, so it asks for canopy
exactly where a reader can look for it.

**Counts:** in the Census block below. Knobs rolled {'copse_siting': 'among_the_houses', 'kosatsuba_siting': 'frontage'}.


## Census - the counts this map ships with

## What pass 12 changed here (feature 230, 2026-09-13)

**The map's name stopped printing over its windbreak.** The placard covered 174 ft of a 440 ft belt - the windward end,
which shelters the westernmost homesteads - and hid 28 of its clumps, while the pocket reserved for the title stood
empty. Four things were wrong and each is now a rule: a grove was an obstacle by its POLYGON rather than by its canopy,
so the title refused bare ground inside the belt including its own reservation; the belt honored that reservation by
pushing polygon vertices out of it, which cannot hold when a crown is drawn 14 ft round a center that is itself outside
(35 of 87 clumps had canopy inside the pocket); the pocket was reserved on ground that was blank only because the belt
had not been planted yet, so holding it cost the belt a third of itself; and the title took the pocket's top-left corner
or nothing, so one byre seated there after the reservation sent it back out onto the belt. The placard now sits inside
its own pocket and the belt is whole.

**And the map no longer claims works it does not draw.** A polder takes its water from a reservoir at the high corner
and draws no stream, and this manifest recorded `intake: weir` and `brook_side: -1` beside `streams: []`. The knob still
rolls - it is part of the seed stream - but a map with no brook writes neither down.

**What the copse records now**: 3 clumps at a median 62.6 ft from the nearest farmhouse. A single row on a dike head has
no interior for a copse to fill, and `copse_siting: among_the_houses` cannot say that by itself.

Derived, never typed. `make notes-census` rewrites the block below from the manifest and
`tests/test_notes_census.py` fails when it disagrees with one. Three settlement-review passes running
caught a hand-typed count describing a roll that no longer shipped, twice in the paragraph written to
correct the last one - so the numbers a reader can check now come from the artifact itself.

<!-- census: generated by `make notes-census` - do not hand-edit -->
- windbreak: **110** clumps drawn, **43** off the page
- copse: **51** clumps drawn
- farmhouses: **16**
- farmstead fixtures: bath **9**, coop **9**, pit **6**, privy **9**, woodpile **12**
- notice board at **(1976.9, 337.4)**, **8** of 16 farmhouses within 250 ft
- windbreak: **82** clumps drawn, **0** off the page
- copse: **3** clumps drawn
- farmhouses: **16**
- farmstead fixtures: bath **9**, coop **10**, pit **2**, privy **14**, shrine **1**, woodpile **10**
- notice board at **(2280.0, 500.3)**, **12** of 16 farmhouses within 250 ft
<!-- /census -->


## 2026-08-29 - feature 154: the notice board becomes a knob and moves to the last stage

This map's `.gen.py` is unchanged; the engine moved under it. Two changes reach every hamlet:

- **`kosatsuba_seat` is a per-settlement knob** rolled from the map's own seed over the placements the
  record attests AND the map can site - the center where villagers assembled, the entrance where the
  approach arrives, and the frontage of the official's gate. Two further attested sites, a bridgehead
  and the shrine precinct, are deliberately withheld at this tier: the pool's "bridges" are 9.8-10.5 ft
  planks over field ditches and its only "shrines" are household hokora in dooryards, so pressing
  either into service would reach five placements by relabelling things the record does not mean.
- **`stage_notice` is now the LAST stage, 17 of 17** (GM 2026-08-29), after the woods, the ground
  cover, the crop and the title - *"the real humans that live in the society ... look around at the
  things which already exist and then decide where to put the notice board."* The board's
  `village_grove` keep-out went with it: it may stand at the wood's edge or under a canopy, and its
  label carries the read (verified - the caption is on the topmost layer at z 20,000,005, above every
  crown, on every map).

**NO PER-MAP settlement-review ran on THIS map**, and that is deliberate rather than an omission. Three
maps were read in four passes for this feature - Sawada and Kashikawa twice each, Mizuguchi once - and
every error they raised was fixed at the cause and re-verified. This manifest moved only because the
engine did, which is the case the GM ruled on: they read the map themselves. Their ruling on the
placements, given after seeing the knob's output across the pool: *"literally every place that you have
ever described the notice board as being put as specified by these different tunable knobs is all
fine."*

**This map's outcome**: rolled `center`; the board stands at (2394.2, 559.1) with 10 of
16 dwellings within 250 ft, broadside to the way it fronts, one caption on the board's own side
of the tread. `kosatsuba_by_the_road` and `kosatsuba_faces_the_road` - the only two live gate checks
that constrain where the board goes, the other five merely asserting it exists - both pass.

## 2026-08-29 - feature 157: the LABEL PHASE, and the caption that stands beside its board

**The GM read this map and reported the defect**: *"the label for the notice board on the Kuwabata
Map is surprisingly far away from the notice board itself. It is correctly aligned with the notice
board, and the distance of the line on which the label rests is the correct distance from the notice
board. But for some reason, rather than being directly below the notice board, it's off to the right
a bit, and I'm not really sure why or how that happened."*

**Measured, before**: the board at (2394.2, 559.1) rot 151.9, its caption tilted -28.1 with its box
at x 2404.1..2456.9. Decomposed in the caption's own frame that is **35.6 px along the baseline** and
10.4 px across it, against a caption half-run of 26.4 - so the board stood **past the end of its own
label**. The alignment and the standoff were right, exactly as the GM said; only the slide was wrong.

**Three causes, all in the tilted branch of the board's seat search, and they compound:**

1. **The lateral offsets were derived from the CAPTION, not from the SUBJECT** - `_chw + hw + 6`,
   which is 38.88 px of slide along a 12 px plank. Sliding a caption along its subject is a real
   convention, but where the engine does it deliberately the slides are fractions of the SUBJECT
   (`span * 0.25`, `span * 0.4`). 39 px along a 12 ft board is not "along", it is "away".
2. **The standoff ladder stepped over the good ground.** Five rungs (11, 16, 21, 28, 36). At lateral
   0 this board's south side is legal at a standoff of **14 and at no other sampled value** - 11
   misses the lane-clearance target by 1.1 ft, 16 and beyond genuinely clip a house. A dense re-scan
   under the identical rules finds 97 legal seats.
3. **The structural probe measured a box it does not draw.** It built the caption's true rotated quad
   and then collapsed it to that quad's bounding box: at -28.1 degrees a 53.8 x 10 px caption becomes
   52 x 34, more than tripling its thickness. That is what refused the seat directly below the board,
   whose true quad clears the nearest structure by **4.43 px**.

**Measured, after**: **lateral -1.02 px** - the caption is directly beside the board, and the standoff
stays well inside what `label_hugs_its_referent` allows. Every other scripted hamlet improved or held:
inashiro 2.22, kashikawa 1.53, mizuguchi 0.63, sawada 1.55 (inashiro and mizuguchi were already
central and their manifests are unchanged).

**And labels now have a phase of their own** (the GM's other ask): the notice board is placed in
`stage_notice` and every caption on the sheet is seated in `stage_labels` after it, because *"how we
place labels will always depend on what else is on the map."* On a hamlet nothing is placed between
the two, so the phase move alone is byte-neutral - which is what lets the caption movement above be
attributed to the seat rules and to nothing else.

### What the independent review then found on this map (settlement-review, 2026-08-29)

It confirmed the fix from PIXELS rather than from the manifest - the caption's 280 dark-ink pixels
have their nearest foreign ink at 4.30 px, the board's own at 7.55, and the halo (stroke `#EFE3C2`,
exactly the parchment) notches nothing at 6x. It verified independently that nothing else on the map
moved. And then it caught two engine defects this feature was leaning on:

- **The caption placer's own safety comment cited a check that does not exist.**
  `labels_clear_of_other_buildings` was deleted in b709c4ae (feature 141's cut), so nothing in the
  gate measures a caption against a building any more - while ~15 live comments and a whole registry
  with its completeness guard still describe it as operative. That matters HERE because this feature
  pulls captions in off the empty margins, leaning on a defense that had quietly become the only one.
  The comment is corrected; the restore-or-retire decision is written up in
  `future-work/cross-cutting.md` because it reverses or ratifies a GM cut.
- **The fabric probe was hand-listed and had fallen behind the map.** Nine families, missing
  `farm_fixtures` - the engine's own *"every ROOFED structure"* - and the sties, pens and boundary
  markers. Measured across the five scripted hamlets, the caption's clearance to the nearest built
  glyph is 20-70 px on four of them and **2.24 px here**, nine times tighter, at exactly the map
  whose caption had just been pulled inward.

**And fixing the second exposed a third that neither of us had seen.** Widening the families cost
this caption 9 px of centrality (lateral -1.02 -> -10.06), because `_hug` and `_blocked` probed a
hand-guessed box - 26.88 x 5.00 against the recorded 26.40 x 4.20, 19% too tall - so the inflated box
just touched the woodpile at the seat directly under the board and the search walked out for a
collision no drawn glyph makes. `_box_clearance` had been taught to measure the recorded box in
feature 137; these two were left on the guess. Both read `label_caption_hw` now, and the caption is
back at **lateral -1.02** with the placer able to see what it is clearing.

**Two things recorded rather than changed**: about 6 px of the GM's own "off to the right" survives by
construction (a perpendicular hang from a -28.1 degree caption is not vertical in the reader's frame -
an 82% reduction, and sliding it out would trade the axis the new check measures for one nothing
does); and the recorded referent is the board's UNROTATED footprint, 12 x 5 against a drawn rotated
AABB of 13.2 x 10.1, which is conservative in both directions and so tightens two live rules rather
than loosening them.

## 2026-09-11 (feature 222): the blade buckets as tiled paths, the page picture a JPEG - no placement change

NO feature moved: the manifest differs from the previous roll only in `ink_classes` (the scrub and marsh counts fell
8-13x because the census counts the writer's tile paths where it counted one `<line>` per blade). The title,
the labels, the crop and the PNG's size are unchanged. settlement-review (2026-09-11) diffed the render against
main's: the blade coordinate multiset is identical to the last digit; 0.4-1.7% of the sheet's pixels differ by up
to 61/255 at tuft roots, where a path anti-aliases a shared root once instead of once per blade (~8/255
lighter), invisible at every zoom (the mechanism is at `interactive/page.py` `merge_lines`). The page's picture is
a JPEG q90 4:4:4 now (the GM, 2026-09-11, to try it and reverse it if it looks bad); the review judged it clean at
1:1 and 4x - no ringing, no color smear, zero blocking on the parchment.

## 2026-09-11 (feature 223): the off-frame blades no longer written, the page picture tiled at 2 px per map px - no placement change

NO feature moved: `bamboo_stands`, `wells`, the title, the labels, the crop and the PNG's size are unchanged, and the
manifest differs from the previous roll only in `ink_classes` (the marsh and scrub rows, down 0.2-0.4%: the writer now
culls the blades wholly outside the frame plus 24 px before merging, so the SVG holds 18,478 blade subpaths where it
held 280,368; the page's own subpath count did not move, since the page had dropped them itself). settlement-review
(2026-09-11) diffed the render against the previous one: 2 px, max channel delta 1; the scrub and reed ink in the outer 36 px band is pixel
for pixel the same, so nothing reaches the frame edge that did not before. The page's picture is rendered as four
pixel-aligned tiles by parallel resvg processes and stitched, at 2 px per map px (the GM's item; the note at
`interactive/raster.py` `RASTER_R`): the review found the seams statistically invisible and the picture at its
display scale indistinguishable from the 3 px one; a retina reader's opening view is now the vector page (spec D3).

## 2026-09-11 (feature 224): the scatter thrown only inside a predicted frame - the texture re-rolls, nothing placed moves

NO feature moved: the manifest differs from the previous roll only in `ink_classes` and two new meta keys
(`scatter_frame`, the frame the commons and marsh scatters threw within - the crop's boxes plus the reserved polygons,
the margin and a 120 px pad, 140 more on the north for a title band - and `scatter_frame_overhang`, the view's
distance inside it per side, negative on every side). The in-frame scrub and marsh TEXTURE is a different throw of the
same density under the same keep-outs (the GM's 2026-09-08 ruling); the houses, fields, lanes, water, crowns and every
recorded feature are byte-identical. settlement-review (2026-09-11) adjudicated every scatter base against the recorded
keep-out geometry at zero pad: 0 on crop plots, structures, lane treads or water, 0 woody marks on bog pixels, 0 reeds on
water, 0 inside the cluster's hull - before and after; in-view density per 1,000 sq ft blades 3.55 -> 3.50, reeds 3.26 -> 3.26; the
outer 40 px of every side within 10% of before, no bare strip; the same place at fit zoom and 1:1.

## 2026-09-11 (feature 225): element opacity folded, the hem's rows cut to their plot, the scatter's marks culled, the pad 40 px - no placement change

NO feature moved: the manifest differs from the previous roll only in `ink_classes` and the scatter-frame meta keys
(on Kuwabata also in draw-position indexes, by exactly 3: three vegetable-ground clip strings left the stream). Every
single-paint element's `opacity` is now the paint's own opacity (pixel-identical; settlement-review 2026-09-11 audited
every folded element for a second paint through the group stack and found none, an isolated resvg A/B differs by 1 in
255); the dry plots' furrow rows end at the plot's edges instead of under a clip (no crossing row missing, rows within
0.11 px of where they lay, the ends clean at 4x); the brush dots, pines, tint and glints outside the frame are no
longer written and the scatter throws only 40 px past the crop's boxes (the widest mark is 28 px), so the in-frame
texture re-rolled again under the GM's 2026-09-08 ruling - density within 3.5%, no bare strip on any edge, 0 marks on
a plot, a house, a yard, a lane or bog. Every drawn string is byte-identical; the crop and the PNG's size unchanged.

## 2026-09-12 (feature 226): the homesteads seated from the site boundary - the layout moved

  The homesteads are seated from ONE site boundary now (feature 226, GM 2026-09-12: *"draw a section of cords
  which literally separate the area in which we are placing our homesteads from literally everything"*): the
  paddy's facing chains, one holed union outline of the hem, the marshes, the ponds, the no-build ground and the
  reed-marsh toe (asked of `toe_band()` before it is drawn, and registered as hard ground so the byres, sheds
  and wells refuse it too), and the water courses and registered corridors as a few segments (`site_boundary`
  in the manifest). Seats are proposed from the chains and a pitch lattice over the cluster band, pre-tested
  before the placer is asked; `meta.seat_search` counts every guess. Every pad and every point set the old
  tests applied is kept (spec D2), so what changed is how the ground is asked, not what it answers - and the
  layout re-packed under the same rules (D4, the GM's 2026-09-08 ruling that a map may move if the invariants
  hold). The belt's southern sun strip now reads the 39 ft corridor a farmhouse owes the same bed (it kept
  22 px; the review of this feature measured the contradiction), so the windbreak re-rolled as well.

  On this map the re-pack is plainly better: 16 of 16 seated on the first roll with 7.0 candidates per house
  (1.8 placer calls - the mosaic's ponds refuse the most ground, and the outline has the pool's one hole, the
  ground between two ponds), and the lone outlier farmhouse the old layout carried (271 px from its nearest
  neighbor, its own component) is gone - one cluster, the row along the dike head reading as one street, the
  worst byre walk 404 -> 170 px and the worst water carry 339 -> 212. The round shape stays unhonored (2.51
  drawn against a band of 1.0-2.0; it was 3.69). The boundary is 7 chords, one ring with one hole, and no
  corridor segment: the mosaic's water is all inside the outline.

  The review's second pass (pass on all five) measured two pool-wide movements this entry records with their
  numbers: the cluster packed LOOSER - the median nearest-neighbor house spacing here 78 -> 79 ft, because the back
  ranks come from a lattice at the bundle pitch (100 ft, a homestead's own ground) rather than a random cloud a
  spiral could squeeze tighter; and the two-bed garden share (position-seeded, ~1 in 4 declared) re-rolled to
  5 of 16 here, 13 of 82 pool-wide against 24 of 82 before - about two standard deviations low, chance on this
  evidence, and nothing in the gate counts it. Whether a nucleated hamlet's house spacing is the homestead pitch
  or tighter is a research question the record does not yet answer; no rule measures the spread today.

## 2026-09-12 (feature 227): the homesteads seated envelope first - the layout moved

  The homesteads are seated ENVELOPE FIRST (feature 227, GM 2026-09-12: *"drawing a rectangle around what would be
  within the homestead. And then once we definitely have enough space, we decide things like whether the garden is
  on the left or the right side"*): a placer call tests the box around the homestead's configurations against the
  site boundary and the placed boxes, then each configuration's own box where that is refused, and lays the parts
  inside a box the ground admitted. The spiral of offsets and the two 2 px slides are gone; the seat is computed
  (*"measuring the distance to the neighbor and then moving however much the correct amount is"*). The front row
  stands at the wall rule plus the homestead's core reach from its chord, pushed once past an outline that lies
  beyond it; the ranks behind stand at the row's own depth plus one step each, a lane's room apart, in a brick.
  The layout re-packed under the same rules; the GM accepted looser packing and set no target for the bed splits.

  On this map: 16 of 16 seated (roll attempt 1), 25 placer calls at 5.0 envelope tests each and
  16 rectangle tests per house against 387 under feature 226; the front row seated 2 and the ranks
  behind ran 5 rounds. The nearest house stands 135 px from the field outline with 3 within 165, and
  homestead to homestead the median gap is 4 px (worst 19) - the fabric is continuous, which a center-to-center
  reading of the same cluster does not show. Drawn aspect 1.86 (round, honored); 2 of 16 gardens split,
  sides {'W': 6, 'E': 10}. The belt and copse clump counts are NOT typed here - they are in the derived
  census block above. A settlement-review caught this pair stale on 2026-09-12 (112 and 56 typed against a
  shipped 110 and 51, one screen below the census preamble that warns about exactly this), which is the
  fourth instance of the same recurrence in this file. A derived number is read, never restated.

## 2026-09-12 (feature 228): the crop dike's bank drawn as a ring - no placement change

  The GM, on this map's interactive page: hovering the mulberry dike *"lights up not only the Mulberry Dyke
  itself, but the fish ponds Inside each Mulberry dike, which is confusing"* - they asked for *"basically the same
  behavior that we give to the perimeter dyke"*. Each pond's bank had been one filled path covering the whole
  parcel with the pond painted over it; on the vector page the pond hid the disk, but raster mode (the opening
  view) draws the lit class as a wash over the image, so the lit disk tinted all 26 dike groups' ponds gold.
  The bank is now the ring between its outer edge and the water's outline, under the even-odd rule - the
  perimeter dike's own band form (research/archetypes.html "The 6:4 water-to-dike ratio and coppiced mulberry" 'The bank is a ring'). Nothing placed moves: the
  manifest is byte-identical (the two outlines come from the same draws in the same order), the crowns and the
  earth mottle still clip to the bank outline, so the few that lean over the water's rim still light with the
  dike, and the ring's inner stroke lies under the pond's own wider stroke. Measured on the page in raster mode
  with the dike lit (settlement-review, by pixel area): the share of water pixels that change when the dike
  lights fell from 100% to 6.2%, all of it within the rim (the inner stroke, the crowns and the mottle leaning
  over the waterline), the bank 100% lit both ways; the picture differs from the shipped render in 0.14% of its
  pixels, every one within the pond's own stroke band, by at most 9 of 255 on a channel.

## 2026-09-12 (feature 227): the board's caption rests 0.02 px off a byre - measured, three holes closed, the cause named

  A settlement-review read this map's sheet and found the caption "notice board" resting on a BYRE, 34 ft from
  the board it names: a reader pairs the words with the chest-shaped outbuilding under them. Measured with the
  engine's own `label_quad` and `poly_gap`, not a hand-rolled rotation: **0.02 px** from the byre's quad, and
  26.3 px from its own board. The other four pool maps sit at 2.35, 33.45, 45.56 and 52.58 px.

  WHY NOTHING CAUGHT IT. Three separate tests were wrong in the same way - each asked for an OVERLAP where the
  thing that matters is a DISTANCE - and all three are now fixed, with `CAPTION_FEATURE_GAP` (4 px, the reading
  distance every other "these two inked things must read as separate" rule on the map uses):
  the seat probe (`boards.py` `_blocked`), the seat picker's fallback when every seat is blocked (which chose on
  lane clearance alone, so a seat touching a roof scored as well as one in the open), and `pull_caption_toward`,
  which moves a caption half way toward its subject AFTER the seat is judged and refused the move only on
  `rects_overlap`. The gate's own `test_every_caption_hugs_what_it_names` cannot see any of it: it measures the
  caption's AXIS-ALIGNED box, and this caption is swung 76 degrees out of that box.

  AND THE CAUSE IS NONE OF THE THREE, which is why the caption did not move when they were fixed. The board's
  caption may only sit ALONG the board's own axis - above it, below it, or laterally - which is 30 candidate
  seats at five standoffs, and on this map every one of them is blocked. 0.02 px is the BEST of the thirty. A
  ring of 252 seats at arbitrary angles within the same hug cap has 214 with 4+ px of clearance and a best of
  34.6 px, so clear ground is abundant; it simply is not on the board's axis. The board is standing in the one
  place on its verge where its own caption has nowhere to go.

  THE FIX IS THEREFORE THE BOARD'S SEAT, NOT THE CAPTION'S, and it is recorded rather than done: the siter
  already scores the caption as part of the seat (GM 2026-07-27) but scores its LANE clearance and its hug, not
  its clearance from the built fabric - so a board seat whose thirty caption seats are all blocked scores as
  well as one with open ground on both sides. Adding that term moves boards on maps whose captions are fine
  today, which re-rolls the pool and wants its own cohort measurement. Sketch: score each candidate BOARD seat
  by the best `CAPTION_FEATURE_GAP` its own thirty caption seats can reach, and prefer a seat whose caption can
  stand clear - the same "the caption is part of the seat" rule, extended to the term that was missing.

## 2026-09-12 (feature 233): the pond stock held clear of the sluices - the layout moved

  The GM, looking at this map, asked whether the pig sties would stand as close to the pond sluices as
  they did, and whether the runoff harms the fish in a pond cultivated for fishing. Two source-reader
  passes answered the second question and declined the premise behind it: a pig shed on a fish-pond dike
  is built there so the waste reaches the water, the manure raising the plankton the fish eat, and the
  oldest siting instruction anyone has for a pig pen - the *Qimin Yaoshu*, about 540 AD - says the place
  is *not* disliked for being filthy. What can go wrong is a rate and a concentration, never a distance.
  And on the sluice itself the record came back SILENT, from both readers independently.

  So nothing was moved back from the water. What was wrong was narrower: three of the seven sties had a
  feed culvert drawn straight THROUGH the shed, and the pond-1 duck pen's fence arc crossed one - all
  four at 0.0 ft, an overlap rather than a gap. The cause was a gap in the placer, not a roll:
  `pond_fixture_fits` held a fixture off eight registries and off nothing in the water system, while the
  engine's own dike-top house placer had skipped a sluice notch since feature 150. Every drawn part -
  the sty footprint, the pen's dry run, and the pen's fence arc - now stands 6 ft clear of every stub,
  measured to the stub SEGMENT and returning zero on an overlap. The reason is constructional and the
  record says so: nobody builds over the opening they must reach to lift its boards.

  Five of the nine fixtures moved. Counts held at 7 sties and 2 pens, on the same ponds, because
  `_bank_seats` now ranks the parcel's edges and the placer takes the nearest that FITS - the old code
  took the single nearest seat or skipped the pond, so any clearance would have moved fixtures between
  ponds or lost them. Minimum clearance over every drawn part: 0.0 -> 8.47 ft. The sheds did not retreat
  from the water doing it; the review measured five center-to-waterline distances that all got SHORTER
  (5.6 -> 3.9, 7.5 -> 6.2, 6.7 -> 4.6, 11.5 -> 10.2, 6.5 -> 3.8 ft), and the walk from the houses grew
  by +0 to +9 ft for the sties and +24 ft for the one pen.

  The accept is BOUNDED (settlement-review): ranking alone left the whole perimeter available, and this
  map's nine fixture-carrying ponds put the far bank 155.6 to 320.0 ft further from the houses than the
  first choice - a shed there would read as belonging to no household. A seat may not be further from
  the house cluster than the pond's own PARCEL center is (the figures: `specs/233-pigsty-clear-of-the-sluice/research.md` R7). It refuses nothing drawn here (the accepted seats
  cost +0 to +21.2 ft, and the tightest sits 57.3 ft inside the bound), and it is geometric rather than
  a tuned distance.

  Two things the review corrected in the record rather than the drawing. The claim that the banks are
  "about 6.5 m" measured nothing: that figure was one pond's two opposite collars added together. The
  collar a sty actually stands on is 2.0 m median (2.6-4.7 m under the sheds), the ground between one
  pond's water and the next is 13.3 m with a canal down the middle of it, and the modern standard for a
  shed-carrying dike is 5 m - so the drawn collar is SNUG by that standard, which the record now states
  instead of claiming a comfortable fit. And the duck pens had been a near-symmetric pair on facing
  north banks, reading as decoration; pond 1's is down the east bank now and they read as two
  households'.

  Left alone, both pre-existing and both noted by the review: `pig1` and `pig4` sit skewed at a dike
  elbow (36.2 and 16.1 degrees off the local bank run), because a seat is an edge MIDPOINT and a
  mosaic parcel's corner-cutting segment belongs to neither adjoining run; and three sheds have one
  corner 0.3-0.8 ft outside their parcel polygon, sub-foot and invisible at any zoom.

## Its canals are pond canals, and no brook to tap (feature 230, 2026-09-12)

This hamlet is the dike-pond: its water comes from a reservoir, not from a brook, so nothing at its head
changed. Two things did. The field ditch that used to be one class is split on every map into the
irrigation ditch and the drainage ditch - but on THIS map the canals between the ponds carry water both
ways, each pond's gates feeding from one canal and draining into another, so they are neither: they are
`pond canal`, the conveyance-and-drainage network the ponds exchange water with, and only the ring drain
that takes everything to the outfall is a `drainage ditch`. And the run that carries this map's runoff off the
frame is drawn and recorded as a drainage ditch at the collector's own width, like every other map's, where
before it was an eight-pixel stream: the same thing wearing two labels on two maps was what the GM caught.
