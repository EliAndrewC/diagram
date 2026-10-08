# Placement: draw order, footprints, and the keep-clear contract

**Load this file when:** You are adding a new map feature, changing where something is placed or drawn, or wondering why the placer allowed an overlap the gate then caught. Read the DRAW ORDER section before moving any placement.

The short always-on version of each rule is in the engine index, [`l7r/diagram/CLAUDE.md`](../l7r/diagram/CLAUDE.md).

## DRAW ORDER: read this BEFORE changing where anything is placed or drawn

Most of what a Mode B feature gets wrong is not geometry, it is ORDER. A drawing method sees only
what is in `self.M` at the moment it runs, and a placement method avoids only what is in the
registries at the moment it runs - so "tree not drawn on a roof" and "building not placed under a
canopy" are the SAME rule enforced from two different points in the sequence. This map cost four
fail-read-fix cycles to reconstruct; it is written down so nobody pays for it twice.

**The three registries, and who honors them:**

| registry | holds | consulted by |
|---|---|---|
| `block_polys` | no-build polygons (field envelopes, the wood, dry plots, the manor court) | `_rect_blocked` tests a whole FOOTPRINT (homestead bundles); `_fits` -> `_in_blocked` tests only the candidate's CENTER (urban packs) |
| `placed` | `(x,y,w,h)` of everything already standing | `_fits` keeps each candidate a half-diagonal + 4px clear |
| `grove_rects` | tree footprints, deliberately kept OUT of `placed` so adjacent groves may abut | `_fits` (same clearance rule), `_east_trees` (garden morning-sun) |

**That `_fits` asymmetry is the trap.** A block poly stops a farmstead whose footprint merely touches
it, but stops an urban building only when its CENTER lands inside - so a wide building can put half
its roof over blocked ground. If a feature must keep whole footprints out, `placed`/`grove_rects`
(distance-based) is the registry that does it; `block_polys` alone is not enough.

**SEE IT BEFORE YOU READ IT.** `dev/placement-stages/hamlet-placement.html` is Inashiro rolled one
stage at a time, with a plate of the map after each of its stages (eighteen at feature 176) and a note on why that
stage sits where it does. Regenerate it with `make placement-stages` whenever
`STAGES` changes - it is generated, never hand-edited, and its per-stage prose is keyed by function
name so a renamed or new stage shows up as missing rather than silently inheriting its neighbor's.
The page is the picture; this document is the rulebook.

**THE ORDER IS `STAGES` IN `hamletgen/driver.py`, and it is the authority.** If you move a stage, move its row here
in the same change - a table that disagrees with the tuple it names is the failure this section exists to prevent.
A stage's NAME is not evidence of what it draws (stage 1 draws nothing, and a blank first plate was once reported as a
bug): `placement_stages.py` decides plate or no-ink card from a record-count delta around the call.

| # | stage | what it puts on the map |
|---|---|---|
| 1 | `stage_water_frame` | **nothing - it draws no ink at all.** Settles the drainage bearing and the land's fall and writes twelve values to `meta`; every later stage reads them |
| 2 | `stage_field` | the water skeleton AND the paddy - `build_comb` returns canals and plots from one call, so intake, head race and field ditches arrive here, not in stage 1. Since feature 230 the BROOK is drawn here too and runs on past the fan down one flank (`brook_skirt`), and the intake's weir - when the roll gave one - is drawn over it (`draw_intake`); everything placed later must keep off that course, which the corridor `s.stream` registers is what does it |
| 3 | `stage_sink` | tail drain, pond or off-map outfall |
| 4 | `stage_seat` | **nothing.** Decides WHERE the settlement sits (`plan.seat`), which `stage_homesteads` depends on. One half of what used to be `stage_ways`; the other half is stage 7 |
| 5 | `stage_waterward` | a polder's WATERWARD reed fringe (feature 150): the strips outside the dike on the flanks that face the water, derived from the seat - laid BEFORE the houses and the track because it reserves wet ground both must avoid (laid in the hinterland it was drawn over an already-routed connector). No ink on a valley hamlet |
| 6 | `stage_homesteads` | the farmhouses, seated with no lane anywhere on the map (feature 128, the GM's rule: water and fields, then FARMHOUSES, then every lane without exception) |
| 7 | `stage_track` | the CONNECTOR and the field spur, derived from the houses that landed. Before the appurtenances, so a well is sunk where the track already runs |
| 8 | `stage_appurtenances` | yards, gardens, byres, wells, sheds |
| 9 | `stage_pond_stock` | a dike-pond hamlet's pig sties, on the banks of the ponds nearest the houses (feature 150 A3; the duck pen retired, 269 B32) |
| 10 | `stage_burial` | the hamlet's own burial ground, on its knob (feature 273: a ground at its edge, or none, its dead in the village's): seated against the placed houses and wells, before the web because it reserves ground the web and the scrub work around |
| 11 | `stage_web` | the lane web - last of the BUILT things, because it fills leftover ground where everything above reserves it |
| 12 | `stage_hinterland` | marsh, the coppice scan, the farmstead FIXTURES (privy, heap, bath, coop, stack, hokora, persimmon - seated after the web so no lane is re-threaded, before the bamboo and the scrub, which keep off them; feature 133 T53-T59), the household bamboo, then the SHELTER BELT planted and the VIEW DECIDED once (feature 287 M6: the belt's inner face is the last thing that sets the frame; `plan.view` is what `stage_frame` crops to), then scrub and rough grazing, thrown within that view |
| 13 | `stage_woodland` | woodland commons |
| 14 | `stage_windbreak` | the copse among the homes (the belt itself is planted in `stage_hinterland` since feature 287) |
| 15 | `stage_bamboo` | the bamboo stands, on seats the hinterland stage scanned (feature 133 T47) |
| 16 | `stage_crossings` | planks and decks over every way that crosses water; on a polder the ring-canal planks cluster on the settlement-side toe collector and skip the feeder, the far toe and the drain (`polder_crossing_caps`, feature 150) |
| 17 | `stage_frame` | crop to content, title, scalebar |
| 18 | `stage_notice` | the kosatsuba - **the last map FEATURE**, after even the frame (GM 2026-08-29, feature 154): *"the real humans ... look around at the things which already exist and then decide where to put the notice board"*. It reserves no ground and grows into none, so nothing is placed after it for it to displace |
| 19 | `stage_labels` | **the LABEL PHASE** - every caption on the map, seated against the finished sheet (GM 2026-08-29, feature 157): *"after the final map feature is added ... a final phase in which we add labels for whatever map features get labels ... how we place labels will always depend on what else is on the map."* No feature draws its own caption any more; `label()` queues and `Settlement.place_labels` drains, seating every searched caption by the ONE placer (`l7r/diagram/labels/`, feature 266: the cartographic standard). Draws no ink but text, reserves nothing, and so can only ever be last |

**THE HOMESTEADS COME FIRST BECAUSE THAT IS HOW LANES WERE TRODDEN** (the GM, 2026-10-02, declining a
proposal to lay the lanes first and seat the houses along them for speed): *"Village lanes are footpaths
that are worn by people walking between houses. But in real life, when these farming communities were set
up, people built their homesteads, and then the village lanes came after. So it is inauthentic and
unrealistic for us to place the lanes first."* It was tried before and made the seating harder, not easier;
and even a measured speedup would not justify drawing a village the way villages were not made. A paved road
is the exception the GM named - *"planned government projects, which then people build things around"* -
so an Imperial road may come before the settlement that fronts it. The reader's version is at
`research/questions/0081-village-lanes.drawing.html`; do not propose lanes-first again.

The rule was settled by feature 128 (GM 2026-08-24: *"farmhouses are rendered after the fields and water, but before
any village lanes. That is what the feature is. Full stop."*); what that reorder taught is in [`lessons.md`](lessons.md).
A lane drawn before the houses registers a no-build corridor the placer then
refuses seats against, whatever the lane represents.

**The rules that fall out of the order:**

- **Must not be drawn ON something?** Run AFTER it, or defer to the flush at the crop (the trees' canopy and the yard
  furniture draw there, against the complete map). Drawing early and letting
  the later feature paint over it hides the overlap instead of preventing it - which is exactly what
  the yashikirin used to do, leaving crowns geometrically under roofs while looking fine.
- **Must FILL ground that is left over?** Run AFTER placement and read the drawn features as
  obstacles. This is easy to get backwards, because getting it backwards does not fail loudly: a lane
  web laid before the houses competed for ground with the very houses it existed to reach - the
  pool clusters' long axes grew 15-97% and nothing measures sprawl.
- **Must RESERVE ground?** Run BEFORE placement AND register in a registry that the placer in
  question actually honors (see the asymmetry above).

**Changing any of this deserves a design pass first.** Read the paths above and settle the ordering
on paper before editing - the failure mode is discovering the sequence one gate failure at a time,
which is what turned a small rule into four fix-fail-read cycles. If a change needs a feature to
move between stages, say so explicitly in the commit: stage moves are the changes most likely to
have effects far from the diff.

## CENTER vs FOOTPRINT: the three ways placement and the checks disagree

The GM, 2026-07-26, after the overlap matrix kept finding things the placer had allowed: *"if
placement is only testing the house's center while the matrix tests its footprint, then maybe the
placement test is wrong? Are there other placement checks which are only checking the center? That
could explain a lot of overlap issues as well as a lot of inefficiencies."* There turned out to be **three**
distinct disagreements. Know which you are looking at before you touch anything.

1. **Center-tested keep-outs (UNDER-restrictive -> overlaps).** Fixed by SPLITTING the registry: `hard_polys` (crop,
   pond, bog, a field's own ditches) is tested against the whole footprint; `block_polys` keeps the center test.
   **Do not merge them back**: `block_polys` also holds SOFT reservations (caption bands, aprons, fence standoffs)
   that a footprint routinely overhangs by a few px, and footprint-testing them all was tried and cost maps their
   wells. The honest reading of what is left: those polygons are drawn as keep-out plus slack, with the center test
   handing the slack back; the principled fix is to shrink them to the true keep-out and footprint-test, a pool-wide
   re-tune.
2. **Circumscribed-circle collision (OVER-restrictive -> wasted ground).** Against `placed` and `grove_rects`, the
   urban `_fits` uses half-diagonal circles, not real footprints - it never permits an overlap, but wastes up to ~2x
   the spacing. **Do not swap it for an axis-aligned box test on its own**: the circle is rotation-invariant, and that
   is what absorbs item 3 for rotated buildings; the naive swap turned a clean gate into five failures, two of them real
   overlaps. Item 3 first, then a real `sat_overlap` on real corner quads.
3. **Placement tests a DIFFERENT footprint than the one drawn.** The fix is for the placer to test the size, position
   and ROTATION it is going to DRAW. Done for the hamlet bundle in feature 121: the divergence was the rake alone
   (`_house_rot`'s +/-5 deg, up to 2.56 px of corner), fixed in the placer, in `_on_a_tread` (which had passed rotation
   0), in the check (which had built its own axis-aligned corners beside `rect_corners`), and in the renderer (which
   rounded `rotate()` to whole degrees). One measurement, not several: a check that re-derives the footprint has the
   defect it is meant to catch.

**The general lesson.** A point test is right for a SCATTER (each tuft is a point) and wrong for
anything with an extent. A tiler sampling a cell's center and four corners let a small keep-out against an edge
MIDPOINT slip between them - that is how a wellhead ended up 1 px inside a hatake plot. Region-vs-region helpers
(`quad_hits_poly`, `quad_hits_seg`, `point_quad_dist`) exist; use them rather than adding sample points.

## Centers, footprints, and aggregates: which one a rule is allowed to use

The GM, 2026-07-27, after the boundary-stone defect: *"I'm not sure it EVER makes sense to use a
center instead of a footprint... we've had a lot of bugs slip through because of using centers,
which makes me wonder whether we should just ban them."* An audit of all 42 center-distance sites
and 29 `point_in_poly`-on-a-center sites says: a blanket ban would break three things that are
right, and would still have missed the defect that prompted it. **Four families. Say which one your
rule is in, in a comment, at the point of the test.**

| family | measure | why | examples |
|---|---|---|---|
| **Gap VERDICT** - "N ft of clearance", "these must not overlap" | `edge_gap` / `within_edge_gap` / `sat_overlap` on real rotated corners. **Never** a center, **never** a circumscribed radius | the answer is a distance you could pace out between two walls | `execution_ground_outside_the_settlement`, `town_has_cremation_ground`, `burakumin_quarter_segregated`, `execution_ground_clear_of_the_dead`, `wells_among_dwellings`, `farm_sheds_attached` |
| **CLASSIFICATION / counting** - "which ward", "how many inside the wall", "what share of this quarter is civic" | center, deliberately | a building belongs to ONE ward; footprint-testing double-counts a building on a seam and the ward populations stop summing to the town | the 29 `point_in_poly(b["x"], b["y"], wall)` sites |
| **ASSOCIATION / reach** - "is there a well within reach", "do monk houses cluster at their temple", "is this yard on the water" | center, deliberately | the tolerance (75-480 px) dwarfs the footprints and the question is neighborhood membership, not clearance; converting them re-tunes ~21 calibrated constants to fix nothing | `settlement_dwellings_watered`, `city_monk_houses_by_their_temple`, `_ty_on_water` |
| **PREFILTER** in front of an exact test | circumscribed radius, deliberately | over-stating an extent can only ADMIT a pair the exact test then rejects - the index prunes, it never decides. Tightening these would start rejecting before the exact test runs | `fire_tower_standoff`, `no_structure_overlaps`, `city_house_doors_unblocked`, `within_edge_gap`'s own prefilter |
| **POINT FIXTURE** - a distance to a gate, torii, sluice gate or bridge | point, unavoidably | these are recorded as bare `[x, y]` in the manifest and have no footprint to test. If one ever gains `w`/`h`, the rules that measure to it become gap verdicts and move to row 1. **The kido left this row on 2026-07-27**: it never had `w`/`h` either, but it records `parts` - each drawn rect's rotated corner quad - and `guard`, so it always had a real footprint that nothing read. The trigger condition is therefore not "gains `w`/`h`" but "records ANY drawn extent"; check the record, not the two field names | `city_inspection_station_at_each_gate`, `city_kosatsuba_per_gate`, `city_temple_approach_has_torii`, `wall_towers_evenly_spaced` |

**The three conventions that were live before this, and what each cost.** Raw center-to-center
understates clearance by the sum of both half-extents, so a rule promising 120 ft delivered ~60;
`0.5 * math.hypot(w, h)` is the half-DIAGONAL, over by up to 41% on a square and more on a long
rect; `max(w, h) / 2` is the same error differently sized. The approximations' error **flips sign**
with the rule - subtracting too much makes a "must be far" rule strict and a "must be near" rule
lenient - so they are not even a uniform safety margin.

**The ratchet, not the doc.** `test_gap_verdicts_read_footprints_not_centers` plants two features at
exactly the offset where the conventions disagree and pins which verdict is right. Verified to have
teeth: of its nine entries, reverting the helper to raw centers breaks six and reverting it to
circumscribed radii breaks the other three - every entry is caught by one revert or the other. **Add
an entry when you add a gap rule** - a rule that lives only in this table has already been proven
not to hold.

**THE SWEEP IS DONE; DO NOT REDO IT, EXTEND IT.** Two passes, because the first one's METHOD had the
same shape of blind spot as the bug it was hunting. Pass 1 grepped `math.hypot(...["x"]...["x"]...)`
and found 42 sites across 34 checks. That regex cannot see a record compared against an unpacked
`(x, y)` tuple, which hid a second tranche of 45 sites across 36 checks - and one of them,
`tanning_yard_clear_of_dwellings`, was a live 120 ft gap verdict reading 150 ft where the yard's own
corner stood 76 ft from a farmhouse wall (Tango). Everything else in the second tranche classified
as point-fixture, association/reach, classification, or one SIDE test
(`dwellings_above_field_drain`, whose "is the house clearly on the wet side" question is a bearing,
and deliberately center-based). If you add a distance rule, put it in the right row of the table
above and give it a ratchet entry - that is cheaper than a third sweep.

**One measurement, not several.** `edge_gap` is now the only exact footprint-gap helper.
`_fr_gap`/`_fr_poly` - feature 016's own, written before it and doing the same job by the same
method - was folded in on 2026-07-27. Two CORRECT helpers for one question is how the three wrong
conventions got started; if you find yourself writing a third, use `edge_gap`.

**And a fourth axis, which no footprint discipline reaches: AGGREGATE PROXIES.** The boundary-stone
defect was not a footprint bug. `dist(stone, centroid) < dist(ground, centroid)` would stay green
with perfect geometry on both sides, because the centroid - an average of every dwelling - was
standing in for the built EDGE, and a settlement is not a disc. **Never let an aggregate stand in
for the distributed thing a verdict is about.** Measure to the nearest member (or, where the
settlement has a rampart, to the wall - the edge it actually has). `execution_ground_on_the_outcast_
side` still dots against the centroid and that is correct: a BEARING is an aggregate question. A
DISTANCE is not.

**Known debt, recorded as debt rather than design:** `_fits` center-testing `block_polys` (item 1 above).

## Adding a new map feature: the KEEP-CLEAR CONTRACT (read this before writing the glyph)

**And its FEATURE CLASS (feature 150).** Every `add*()` at the glyph's emit site carries the class
the interactive page highlights it under - `cls="<key>"` or `with self.feature("<key>"):` - and
the key is a row of `l7r/diagram/interactive/classes.py` with its explanation and label; ink the
GM has ruled NOT highlighted is tagged `"-"` with a row in `NOT_HIGHLIGHTED_RULINGS`. The gate
check `all_ink_is_ruled_on` fails a scripted hamlet on ink with no class and on a key the
registry does not know, so a new glyph without its class shows up at the next reference roll.
Index: [`../l7r/diagram/interactive/CLAUDE.md`](../l7r/diagram/interactive/CLAUDE.md).

The GM's observation, 2026-07-25, after a new building shipped sitting on a ring road:
*"every time we add a new type of thing, I end up looking at the map and saying 'oh, this new thing
should not overlap with X'."* That is now a solved problem, and this is the whole of what you have
to do.

**One registry, and everything follows from it.** A new footprint feature goes in
`_OVERLAP_STRUCTS` (`l7r/diagram/overlap/taxonomy.py`) - or, if it is MEANT to overlap something, in
`_OVERLAP_EXEMPT` with the reason. You cannot forget: `every_feature_classified_for_overlap` fires
when a generator emits a feature key nobody classified. Membership alone then governs the feature
against EVERYTHING on the map, because the registry gives it an overlap CLASS (`SOLID`, `GROUND`,
`WATER`, `WAY`, `ANNEX`, `COVER` - `OVERLAP_CLASS` in the same module) and the class matrix, forbidden
by default with every permission carrying its reason (`_MATRIX_PERMISSIVE` and its siblings), decides
every pair; `matrix_violations()` in `l7r/diagram/overlap/matrix.py` is the one place that judgment is
made. There is no per-hazard check list to keep in step any more: the fifteen-hazard battery and the
`solid_structs(M)` footprint builder it read went with the check battery in feature 166.

**Don't hand-list keys in a keep-clear rule.** A check or probe that reads its own list of manifest keys falls
behind the registry, and a check that never sees your feature looks exactly like a check that passes; the matrix
closes that class, because a pair the registry does not permit fails whichever feature is newer.

**The ratchet.** Since feature 287 M8 the matrix is refused at RECORD time, not audited after: every footprint the
settlement records goes through the registry of what stands (`overlap/registry.py`, a grid index filed as each record
lands), a hamlet raises `OverlapRefused` on a record the matrix forbids on what stands, and every placer asks
`Settlement.admits(key, record)` before it chooses (the finished-map test `test_no_feature_overlaps.py` is retired,
research R8). `tests/settlement/test_homestead_parts.py` censuses the roster. A new feature with no class fails the
classification guard before it ever reaches the matrix. **A permission or a prohibition in the class matrix extends
the contract to every existing feature at once** - that is the cheap way to answer the next "should not overlap with X".

**The same contract covers CAPTIONS** (GM 2026-07-26). A feature protected from every solid
neighbor is still not protected from a label dropped on top of it, and a hand-written list of caption-protected
keys fell behind twice in two days. `_LABEL_GROUP` now maps each manifest key to the caption GROUP a
label must name to be allowed over it, `_LABEL_EXEMPT` excuses the few that do not need protecting
(with the reason), and `every_solid_feature_classified_for_labels` fired when a key was in neither (both checks went
with `check_village/`, feature 166; the registry now lives in `overlap/taxonomy.py` and the one caption placer reads it).
The permission side is derived from the same registry - a group's name IS its caption word
("brewery", "martial hall", "execution ground") - so a classified feature can caption itself with
no second list to remember. The named branches in `_label_allows` survive only for SYNONYMS: a
caption reads "Temple of Benten" or "Governor's Mansion", not "temple" or "governor".

**RECORD A FOOTPRINT THE EXTRACTOR CAN READ - classification is only half.** GM, 2026-07-27: *"in
general we always want overlap checks to use full footprints."* `matrix_extents` reads `x`+`w`/`vw`,
a `poly`/`outline` ring, a stroked polyline, or a `parts` list of rotated quads. A record matching
NONE of those is extracted as nothing, and a feature the extractor never reaches is invisible to
every matrix check in both directions no matter how carefully it is classified and mounted - which
looks exactly like a feature with nothing wrong (three keys were in that state until an audit went looking). The
audit is cheap and worth re-running whenever a new key appears - per manifest, compare each classified key's
record count against `collections.Counter(k for k, *_ in matrix_extents(M))`; any key with records
and no extents is blind. And where one glyph draws SEVERAL rects, record them as `parts` (rotated
corner quads) rather than a bounding box, and split out any part that does not share the whole
feature's permissions - a gateway may stand on the fence it pierces, its watch box may not.

**The same disease turns up in PLACEMENT PROBES, where it is quieter**: a caption probe with its own hand-written key
list reported a clear box beside a feature it had never heard of. A probe iterates **any manifest list of dicts
carrying w/h**, so nothing has to be remembered into it. Two sibling lessons, both worth generalizing:

- **A probe must measure the box the CHECK will measure.** That probe sized its trial box with
  `_text_width` (the PIL glyph measurement) while `labels_clear_of_other_buildings` (since retired) read the box
  `_record_label` writes (`len(text) * size * 0.55`), which is ~2px wider per side at caption size. The
  probe cleared, the gate did not. Same rule as "placement and its check read the SAME manifest
  source", one level down: geometry, not just data.
- **A probe that gives up silently is worse than no probe.** When none of its nine candidate rings
  was clear it left `label_xy` as None and the caption fell back to the default seat - on top of three
  dwellings. It searches sixteen rings now, but the shape of the bug is the fallback, not the number.

**And a caption that is DEFERRED cannot be reserved by reading it back.** `place_caption` seats at
`finish()`, so `s.M["labels"][-1]` right after the call returns some *earlier* label, and a gen that
reserves that box reserves the wrong ground. Worse, the ladder
seats a deferred caption against a map that is already full, so it takes the LEAST-BAD spot rather
than a clear one. A deferred caption's ground has to be reserved by hand, BEFORE the packs run.

**So the checklist for a new feature is:** write the glyph with its feature class; record it under a new manifest key
with a footprint the extractor can read; add that key to `_OVERLAP_STRUCTS` (or `_OVERLAP_EXEMPT` with the reason) and
give it a caption group in `_LABEL_GROUP`; run the suite. A keep-clear rule no class pair covers is a matrix entry,
never a bespoke check with its own key list.

**The placement side.** `open_seat` verifies the whole FOOTPRINT against **the bound**, because a bound is a hard
edge (the ring-road loop, the wall) and a footprint crossing it is drawn on the patrol road at any overhang;
`block_polys` and corridors stay center-tested even there, deliberately (item 1 above). `footprint=False` gets the
center-only answer a pack would take (`test_open_seat_refuses_a_seat_whose_FOOTPRINT_crosses_the_bound` holds this).

## Two placer bugs of the same shape: INDEX vs POP

`pack` and `frontage` POP each item they seat; `rowpack` walks an INDEX and leaves the list intact.
So the `_shortfall` call added to `rowpack` on 2026-08-11 - copied from its siblings - handed over
the WHOLE list as "what did not fit", and every run reported an ask of exactly double what the gen
gave it. The symptom is nastier than a wrong number: a run seating half its ask reads as seating a
quarter, and trimming the ask to the reported figure halves it again, so the correction has a fixed
point at 50% and never converges. Four rounds of automated trimming chased that before anyone read
the loop. **When you add bookkeeping to a placer, check whether it consumes its work-list or indexes
it** - and if a correction loop is not converging, suspect the measurement before the geometry.

## RANDOMNESS IS POSITIONAL OR SCOPED - never "wherever the stream happens to be"

**THE REQUIREMENT IS RETIRED; THE PRACTICE STAYS (feature 219, GM 2026-09-08).** This section was written as a rule
the gate proved - an upstream change in the number of random draws must not move a map - with the measurement below
as its reason and the immune test as its proof. The GM retired the requirement: *"I am actually okay with an
upstream change in the number of random draws moving a map"*. The test, `rollcache.extra_draws` and
`_perturbed_manifest` went with it, and nothing proves the property any more. What follows is how the engine's
randomness IS structured, and why it was built that way - every current draw site uses the two mechanisms, and a new
draw is easier to reason about if it does too - not a rule a gate enforces.

The practice: **a feature's randomness depends on the feature, not on how much randomness the map has drawn
before it.** Two mechanisms, and one of them fits every case.

- **A per-feature attribute** - a house's rake, its wall color, whether it has a kura, which kind a
  ring seat gets - comes from **`self._hjit(x, y, salt)`**, which is a deterministic hash of the
  position. Its docstring has said why since it was written: "so it never ripples other placement or
  household counts". Pick an unused salt (1.0, 2.0, 3.0, 7.0, 11.0, 13.0, 21.0, 22.0 and 0.7/1.3/2.1
  are taken; `_quad` owns 71.0+).
- **A phase or a region** - a pack's seat jitter, a pasture's outline, a grove's crowns, a well grid,
  a ring's candidate seats - runs inside **`with self.rng_scope(name, *key)`**, whose stream is a hash
  of (map seed, name, key) and which restores the outer stream on the way out. Key it on the thing
  that identifies the instance: the bbox, the street run, the base polygon. Repeat calls on one key
  get their own numbers via a per-key counter, so two packs over the same ground do not twin.

**Why it was built that way (GM 2026-08-08):** when everything drew from one global stream, any change in the NUMBER
of draws before a phase re-rolled that phase however unrelated it was - a caption resize in a city's temple quarter
dropped a farm shed on a garden 700 px away, and debugging a map you did not change is the expensive kind of work.

**Converting a draw site re-rolls the whole pool once**, so batch them: convert everything you
intend to, THEN regenerate and fix the fallout in one pass. Fixing fallout between conversions is
work you will throw away, because the next conversion produces a different fallout set.

## ROUTING A WAY THROUGH GROUND THAT IS ALREADY FULL

Feature 123's lane web needed paths from outlying steadings to the network, and got there by three
successive answers, only the last of which works. Recorded because the first two look reasonable.

**A straight run, then a straight run plus fixed dog-legs.** Fails in both directions and for the
same reason - a fixed offset is not a length that means anything. 40/80/130 ft is a gentle correction
on a 300 ft path and a switchback on an 80 ft one, and a review caught the switchback: 271 ft of path
to join two points 77 ft apart, folded back through a windbreak. Scale the bend to the CHORD if you
try this, and bound directness (a path may not exceed ~2x its own straight line; every honest way on
these maps measures 1.00-1.34).

**A lattice router, string-pulled.** This is the one that works, and two details are load-bearing:

- **A diagonal may not cut a blocked corner.** Two cell centers can both be clear while the step
  between them clips the corner of a steading standing between them. Require both orthogonal
  neighbors on a diagonal move, or the planner "finds" routes that are not walkable and they fail
  their own acceptance test a moment later - which reads as a mysterious rejection, not as a
  planning bug.
- **String-pull at the clearance the lattice PLANNED with.** Validating shortcuts more strictly than
  the route was planned refuses every shortcut and leaves the raw lattice chain, whose diagonals then
  clip the corners the cell centers had cleared. One number, used by both.

**The lattice is an INDEX, not a decision** - the standing rule in this file's performance section
applies verbatim. Every shortcut is re-tested against the real geometry before it is taken, so the
drawn path is exactly as legal as one drawn by hand; the grid only proposes.

**And prefilter.** The clearance predicate gets called once per lattice cell per candidate per
target, and unprefiltered it scans every polygon in the settlement's fabric each time. That took a
hamlet from 15 s to 45 s and killed a cohort worker outright. A bounding-box test against the
polyline's own bounds prunes it; it never decides.

## A REPAIR PASS MUST RUN AFTER THE THINGS IT REPAIRS

Three ordering bugs in one feature, all the same shape, all silent. Writing the shape down because
fixing it three times separately is what a session does when it has not noticed the pattern.

1. **The lane web ran before the houses.** It reserved ground from a cluster that had not been packed
   yet, so it competed with the very houses it existed to serve - the four pool clusters' long axes
   grew 15-97%. No check measures sprawl, so nothing said a word.
2. **The web ran before the appurtenances.** Its corridor reserved courtyard ground ahead of the byre
   placer and exiled byres up to 210 ft, erasing a previous feature's borrow-coverage fix.
3. **The orphan-join ran before the bridges and the footpaths.** On cohort seed 39 it saw FOUR of the
   twelve lanes the map finishes with, found nothing to join, and the eight lanes added after it
   formed a second network of their own. Every house on that map is within 86 ft of a lane and twelve
   of them still counted as unreached, because the lane serving them was not on the connector's
   network.

**The rule.** Sort every stage into one of three kinds and place it accordingly:

- **RESERVES ground** (a no-build corridor the houses pack around) - runs BEFORE placement.
- **FILLS ground left over** (the lane web, ground cover) - runs AFTER placement, reading the drawn
  features as obstacles.
- **REPAIRS what the others produced** (joining orphans, closing breaks, trimming stubs) - runs LAST,
  after every pass that can create the thing it repairs. If a repair pass can be invalidated by a
  later stage, it either moves after that stage or runs twice.

**Why it stays silent.** Each of these produces a map that draws fine and gates green on everything
except the one rule that happens to measure the consequence - and two of the three had no rule at all
until this feature added one. The failure signature is a check firing on a map whose ink looks
correct: that is usually an ordering problem, not a geometry one.
