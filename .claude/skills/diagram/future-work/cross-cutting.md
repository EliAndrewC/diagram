# Future work: cross-cutting

**Things that are not about one kind of map**: the gate, the caches and the render pipeline, engine
module organization, and generation doctrine that applies at every tier.

The test for this file is simple - if fixing it would change maps of more than one type, or would
change no map at all (tooling, structure, checks), it belongs here.

## 2. Fabric-first generation (the GM's ordering question, 2026-08-10) - RESEARCH DIRECTION
Today's order is shell-first: wall/roads/water, then fabric fitted inside, with the wall
PRE-SIZED from a budget density constant. The constant was wrong once (Tango's 690 vs the
capital's as-built 1,367) and the failure mode was structural: fabric could not fit, overflow
silently went extramural. A fabric-first order - grow streets/quarters/temples roughly
radially, THEN wrap wall/moat/ring around the built hull - makes wall-sizing correct BY
CONSTRUCTION. Known hard parts (the GM named them): gate-anchored programs (guard houses,
inspection stations, caravan clusters) need the gates, so it becomes two-pass - grow fabric,
choose gates on the hull, then place gate programs and re-arrange locally; ring/moat must
wrap an irregular hull rather than an ellipse. This is a full feature with its own spec, not
a mid-feature pivot. Candidate: the next city-tier map.

## 2g. The render cache serves a PNG made from a DIFFERENT SVG (recurs; five times on 2026-08-19/20)
`test_every_live_pool_png_matches_its_own_svg_viewbox` fails whenever a change moves a map's geometry:
the gen re-renders the SVG while the PNG comes back from the render cache, so the pair disagree on
aspect (kashikawa, 2600x3962 against the 3864 its own viewBox implies). Deleting the PNG and running
`regen --no-cache` fixes that pair - and the next `make done` re-breaks it, because the gate regenerates
too and the cache serves the same stale PNG again.

It bit five times in two days across three sessions, always after someone moved geometry, and each time
it was fixed by hand rather than diagnosed. **It is a cache-key defect, not a map defect**: the PNG's
entry is being treated as valid for an SVG it was not rendered from. Start at `pipeline/render_cache.py`
and ask what the PNG half of an entry is keyed on, and whether the SVG's own bytes are in that key -
`dev/cache.md` already records that an entry has "TWO independently-perishable halves" and that the
artifact half staying valid says nothing about the other half. This looks like the same shape one level
down: the SVG half is refreshed, the PNG half is not, and nothing notices until a test compares them.

## Three members that are in `settlement/structures/` only because of where feature 025 cut

Feature 114 split `settlement/structures.py` into a package and, in doing so, isolated the members
that do not belong to the structures subsystem at all - so each of these is now a one-file change
plus one row of `settlement/structures/CLAUDE.md`. None was moved by 114 itself, deliberately: a
cross-mixin relocation would have made that feature's byte-identity oracle answer two questions at
once, so a dirty diff could not have distinguished "the composition is wrong" from "moving `road`
changed something".

- **`road` -> `water_ways.py`.** It is a way, and `water_ways.py` is already the ways module (lanes,
  streets, alleys, kido). It sits in `structures/ground.py` today.
- **`pasture` -> `land/cover.py`.** It is a land surface, and `cover.py` already holds the commons
  and the hinterland layout (marsh and the toe band sit next door in `land/wet.py`). Same module
  today. Destination updated by feature 120, which split `land.py` into a package; the move itself
  was explicitly left out of that feature's scope, because a cross-package relocation does not
  belong in a split whose whole safety argument is that nothing moves but text.
- **`structures/captions.py` -> `castle_civic.py`, but this one is an OPEN QUESTION, not a pending
  move.** `castle_civic.py` holds `place_caption` (the draw-time seat ladder) while `captions.py`
  holds the probes underneath it - so folding them gives one caption subsystem, but three of the
  five probes are consumed by siters that live in `structures/fixtures.py`. The implementation
  sketch, the thing that holds it (the composed-surface guard, which fails naming the five names if
  they move out without the frozenset being updated in the same commit) and the one deliberate
  exclusion (`_under_a_caption`) are all in `settlement/structures/CLAUDE.md` under "Three
  placements you will want to fix".

The two straight moves are cheap and safe on their own: every consumer reaches these members through
`self.` on the composed `Settlement`, so no call site changes - the move is the member's text, its
row in the two indexes, and the name migrating between the two mixins' surface frozensets.

## Feature 115's leftovers (civic_grounds/)

Same shape as feature 114's above: pending PARENT-level relocations that were deliberately not
folded into the split, because moving a member between parent-level mixins would have made the
byte-identity oracle answer two questions at once.

- **`_ward_fence_cap` -> `water_ways.py`.** It is a ward-fence predicate and `water_ways.py` is
  already the wards/fences module. It sits in `civic_grounds/funerary.py` today because `mausoleum`
  is its caller inside the package being cut (the placement-follows-the-caller rule). Its other
  consumer, `structures/compounds.py`, reaches it through the composed `Settlement` and is unaffected
  either way.
- **`precinct_interior` -> `shrines_wells/`.** It draws a sovereign temple precinct's INTERIOR
  program (abbot's residence, order administration, library, two dormitories, kitchen/refectory), so
  it is religious ground; `civic_grounds/civic.py` holds it as the institutional-works member.
  Feature 116 has since made `shrines_wells` a package, so the destination is now a specific file -
  `shrines_wells/shrines.py` is the closest fit. Note it calls `self.cemetery`, which stays in
  `civic_grounds/funerary.py`; that cross-package `self.` call is already normal and needs no import.

Both are cheap: every consumer reaches these through `self.`, so the move is the member's text, its
row in the two indexes, and the name migrating between the two mixins' surface frozensets.

## The gate's 15 over-150-line segment functions (found by feature 122, deliberately NOT fixed there)

This file records "the largest function in the engine is now `_bundle_geom` at 81 lines, so nothing
is over the ~150-line bar features 112/115 converged on and there is no standing clause-12
candidate". That is true, and it is scoped to the ENGINE. **The GATE was never measured**, and it
has fifteen segment functions over the bar:

| lines | segment | file |
|---|---|---|
| 293 | `_seg_0555_007__execution_ground_outside_the_settlement` | `segments_09a_justice_grounds_and_land_fall.py` |
| 273 | `_seg_0324__field_ditches_terminate` | `segments_05c_streams_and_field_ditches.py` |
| 255 | `_seg_0581__polder_dike_is_earthwork` | `segments_11b_polder_dikes_and_waivers.py` |
| 248 | `_seg_0571__torii_count_canonical` | `segments_11a_taxfree_terraces_and_dikeponds.py` |
| 228 | `_seg_0580__dikepond_is_ponds_in_a_block` | `segments_11a_taxfree_terraces_and_dikeponds.py` |
| 227 | `_seg_0563_072__city_neighborhoods_have_wells` | `segments_10b_city_civic_and_commerce.py` |
| 221 | `_seg_0556__walled_town_has_wall` | `segments_09a_justice_grounds_and_land_fall.py` |
| 208 | `_seg_0033__hard_features_within_frame` | `segments_01a_city_ring_and_frame.py` |
| 199 | `_seg_0104__city_wall_tower_coverage` | `segments_02a_capital_budget_and_ministries.py` |
| 196 | `_seg_0563_325__city_moat_feeder_matches_width` | `segments_10g_city_streets_and_docks.py` |
| 195 | `_seg_0275__labels_clear_of_other_buildings` | `segments_04a_margins_lanes_and_wells.py` |
| 185 | `_seg_0603__paddy_plot_seams_shared` | `segments_08d_kosatsuba_and_paddy_basins.py` |
| 183 | `_seg_0127__city_fan_heads_quilted` | `segments_02c_walls_gates_and_housing.py` |
| 153 | `_seg_0563_335__city_streets_connected` | `segments_10h_city_torii_and_estate_grounds.py` |
| 151 | `_seg_0108__merchant_estate_wall_clear_of_water` | `segments_02b_capital_ways_and_burial.py` |

**Why 122 left them, which is the part worth keeping.** 122's whole safety argument is that it moved
whole functions and changed no character inside one - which let it prove itself with a byte-identity
oracle over 24,354 content lines plus an identical 1,377-row `GATE_SEGMENTS`. Decomposing a check
BODY is the opposite kind of edit: it changes text inside a function, so neither oracle can hold it,
and folding the two together would have meant a 24,000-line diff whose correctness rested on reading
rather than on a check. Doing them in one feature would have bought nothing and cost the proof.

**The bar these should be measured against is NOT the engine's.** A segment is a check, and a check
that is long because it walks a lot of geometry to reach one verdict is not the same defect as a
draw method doing eight things. Before decomposing any of these, ask which it is:
`_seg_0571__torii_count_canonical` at 248 lines is likely one long enumeration (the numerology has
cases), while `_seg_0555_007__execution_ground_outside_the_settlement` at 293 is the check with six
interacting rules that `dev/diagnostics.md` describes needing `site_justice.py` to adjudicate, and
that one probably does decompose into named predicates.

**Pre-flight, both cheap, both mandated by the 115/118 lesson** (recorded in `dev/pool.md`, where
each of them changed the plan once): measure the RNG surface - free here, since a check draws
nothing - and count the closures. Then decompose behind the same registry contract, with one trap
worth stating out loud: the numeric key in the NAME is the execution position, so a helper extracted
out of a segment must NOT be named `_seg_*`, or the registry will try to run it as a segment.

## 8. `TWIN_AXES` believes a declared knob over the drawn shape

The cap pushed the surplus households into the cloud pass, so Sawada's `cluster_seeding` flipped
`frontage` -> `cloud` and `meta.cluster_shape: "round"` is now emitted for the first time. The drawn
cluster is **808 x 235 ft, 3.48:1**. That would be harmless bookkeeping except `check_village/driver.py`'s
`TWIN_AXES` reads *"the declared knob if present, else the cluster-bbox aspect"* - so the
twin-distinctness axis now reports **round** on the strength of a rolled knob, where before the cap
it fell through to the MEASUREMENT and would have said elongated.

This is the derive-don't-pin rule inverted: a declaration is being trusted over the geometry it is
supposed to describe, and the flip was a side effect of a placer change that never touched the twin
detector. **Sketch**: prefer the measurement when both exist (a knob says what was ASKED for, the
bbox says what was DRAWN, and the twin detector's question is about what a reader sees) - or make
the cloud record what it actually produced.

**RULED BY THE GM 2026-08-24: the twin detector measures WHAT WAS DRAWN, not what was asked for.**
The GM's reasoning, which generalizes past this one axis: *"the thing that we are detecting when we
are doing automated checks is we should be running the automated checks against what is actually
being rendered, not just checking to see whether what was asked for was valid and then doing
something else and then not checking whether what we did matches our specifications."*

A knob records an INTENTION. A check that reads the knob is asking whether we meant well, and it
passes cleanly on a map that drew something else entirely - which is the failure mode this project
has hit repeatedly under a different name (`cluster_shape` was rolled, printed in every cohort header,
and read by nothing for months). So: prefer the measurement wherever both exist. **Not implemented
yet** - recorded here as DECIDED-AND-PENDING per the same 2026-08-24 direction that a code change
should not be started mid-feature.

## NOTE 2026-08-27 (feature 133 T90): the would-have-dispatched trail was empty for the whole period

Zero entries between the lock (2026-08-25) and the unlock (2026-08-27). Not because nothing was
built - 30 tasks landed in the clone - but because FR-006 refused every push before the route was
decided, so the recorder (which fires when the GATED route would dispatch) never ran. `make ci-status`
prints "(none)", which reads as "nothing wanted a build"; the honest reading is "no push got far
enough to want one". A one-line change when it matters: `ci-status` could count the FR-006 refusals
in the period beside the trail, so an empty trail says which of the two it is. Not a task - the
audit's answer (should any have run? no) does not change either way.

## The hamlet coverage floor's last 128 lines (feature 146 closed at 99.13%, 2026-08-28)

Feature 146 took the derived hamlet-path floor from 373 uncovered lines to **128** (99.13%) - about 5,300
lines of dead check code removed, ~50 refusal-reason unit tests, 27 scripted negative fixtures, and the
town/city battery gated for the first time since the 2026-08-16 freeze. It did NOT reach green, and the
spec records that rather than rounding. What is left, from `specs/146-the-hamlet-floor-residue/floor-at-close.txt`:

- **`hamletgen/ways.py`, 28** - nested closures in the web stages (`_rejoinable`, `_commit`, `_join_piece`,
  `_touch_junctions`, `_thread_the_fabric`'s detour). Reachable, but each needs a lane geometry contrived so
  precisely that the router, the string-pull AND the un-jog pass all fail first. Three were closed that way
  under 146, so the method is proven; the rest is the same work at a higher price per line.
- **`settlement/city/bridges.py`, 17** - the city bridge's rotation search and the footbridge's per-segment
  caps. Reachable only by a city map's PLACER, and the city pool is frozen, so nothing runs them. Not
  removable (the city tier needs them) and not reachable until a city is scripted - so this half closes for
  free the day the city tier converts, and not before.
- **~83 across 29 modules** - ones and twos, each a refusal reason whose setup is a whole carve or a whole
  web (`close_seams`, `_carve_sector`, `_dry_fields`), or a check branch needing a manifest shape the
  reference does not carry.

**UPDATE 2026-08-30 (feature 166): the floor now reads 99.28%, ~90 lines** - it improved from 128 as a
side effect of retiring the check battery, and 166 verified the residue is NOT a consequence of that
deletion (it probed the two largest blocks against the battery's own tests and found them Missing there
too). The composition is unchanged in shape: `hamletgen/ways.py` 25, `settlement/_knobs.py` 24,
`_geom/primitives.py` 16, `structures/fixtures.py` 9, the rest in ones and twos.

**AND THE FLOOR IS NOT ACTUALLY BEING ENFORCED** - see 2h below, which is the reason this entry has been
open across three features without anyone noticing it was never checked. Read 2h first; this entry is the
worklist, 2h is why nothing was failing over it.

`research: rendering`. Whoever picks this up: the worklist is generated straight off the FULL run's
hamlet-floor table, and `make hamlet-floor` lists the modules under it.

## The caption-over-a-building rule was cut, and its whole apparatus is still standing

**Found by `settlement-review` on Kuwabata, 2026-08-29 (feature 157), outside the delta.**

`labels_clear_of_other_buildings` - the check that stopped a caption being drawn across a roof - was
deleted in **b709c4ae** ("141: the GM's cut - 442 legacy-tier checks and 39 untested keeps"). What
survives it:

- **Live comments in NINE engine files** - `settlement/trades.py`, `settlement/castle_civic.py`,
  `settlement/shrines_wells/shrines.py`, `settlement/structures/captions.py`,
  `settlement/structures/fixtures.py`, `check_village/segments_06b_bridge_labels_and_reach.py`,
  `check_village/segments_10b_city_civic_and_commerce.py`, `settlement/city/walls.py` - and three
  pool gens, all describing it as an operative rule and justifying real geometry by it. (Feature 157
  corrected the one in `fixtures.py::_blocked` because that comment was justifying code the feature
  was changing; the rest stand.)
- **FOUR OPERATIVE DOCS, which is the half that matters most and which the first draft of this entry
  missed** (settlement-review round 2): `settlements/presentation.md`, `settlements/cities.md`,
  `dev/placement.md`, `dev/diagnostics.md`. `presentation.md` is the worst - it states the rule as a
  LIVE GATE in three separate passages, including the normative paragraph beginning *"A label must
  also not sit on a feature it does NOT name (`labels_clear_of_other_buildings`, town + city
  scale)"* and the "Checks stay narrow" bullet that names it as the backstop justifying why no wider
  label gate exists. A session that swept only the code from this entry would leave the doctrine
  asserting a gate that is gone - which is exactly how this got here.
- **The whole `_LABEL_GROUP` / `_LABEL_EXEMPT` registry** (`check_village/common_01_geometry.py`,
  ~lines 256-356) - the map from each solid feature key to *"the word a caption must contain to be
  allowed to cover it"*.
- **Its completeness guard, `every_solid_feature_classified_for_labels`**
  (`segments_03a_overlaps_and_ward_fences.py`, segments 0141/0142), which still fails the gate when a
  new solid feature is added without a caption GROUP - enforcing classification for a consumer that
  no longer exists. Census: the registry's only consumers are that guard and its own tests.

**Why it matters rather than being tidy-up**: nothing in the gate measures a caption against a
building any more, so a placer's own fabric probe is the sole defense - and feature 157 is exactly
the kind of change that leans on it, because it pulls captions IN off the empty margins and into the
crowded ground beside their subject. Measured on the five scripted hamlets, the notice-board
caption's clearance to the nearest built glyph is 20-70 px on four of them and **2.24 px on
Kuwabata**, nine times tighter than the next.

**The decision is the GM's, and it is one of two**, because both are defensible and they point
opposite ways:

- **RESTORE** it. The registry is sitting there unconsumed and the victim list derives from it, so
  the check is mostly re-assembly rather than design. If the 2026-08-26 cut was about LEGACY-TIER
  checks specifically, this one may have gone out with the tide rather than by intent.
- **RETIRE** the apparatus. Sweep the comments, delete the registry, delete segments 0141/0142 and
  their tests. A guard that enforces classification for nobody is the "verification that never runs"
  shape this repository keeps re-finding, and it taxes every new feature that draws a solid thing.

**Not decided here** because it reverses or ratifies a GM cut, which is not a session's call, and
because either branch is a sweep across six files rather than a fix at a point of change. What
feature 157 DID fix, at the point of change, is the narrow half that was its own: the comment that
asserted the dead check, and `_blocked`'s hand-listed victim families, which had fallen behind the
map exactly the way the registry's own docstring warns.

## 2h. `make done FULL=1` HAS NEVER BEEN GREEN - and nothing says so out loud (found 2026-08-30, feature 166)

**The measurement.** `dev/run-log/` records four FULL-scope runs in the project's history: one on
2026-08-25 and the three feature 166 ran on 2026-08-30. **None is green.** The reference-scope
`make done` is green routinely and is what the push actually requires, so nothing has ever forced the
FULL scope to pass, and its failures have quietly accumulated.

**Why it matters.** FULL is the ONLY scope that enforces the coverage floors and collects
`tests/full/`. So the floors this project believes it holds - the 100% rule outside the four exempt
packages, and the derived hamlet-path floor - are not actually being enforced by anything a session
runs. A floor nobody checks is not a floor.

**Three classes of failure, all found in one sitting, all pre-existing:**

1. **Stale path literals from feature 161's map move.** `tests/full/test_coverage_carriers.py` (all
   eight carriers), `test_gencache.py` and `test_villages.py` read `pool/<tier>/<name>.json` and
   `pool/hamlets/<name>.gen.py`, and 161 moved every map into a per-map folder. They stopped matching
   SILENTLY. Feature 166 fixed the two `.gen.py` literals and deleted the carriers (which the battery
   retirement made redundant), so this class may now be empty - but the LESSON is the standing one in
   [`../../../docs/session-clones.md`](../../../docs/session-clones.md): a layout change leaves path
   patterns outside the walk, and they fail silently.
2. **A FULL-only environment leak** (fixed by 166, recorded because the SHAPE will recur). A variable
   set on make's COMMAND LINE is exported to recipes as a plain environment variable, so
   `make done FULL=1` puts `FULL=1` into `os.environ` and a fixture's nested `make` inherits it. Feature
   145 fixed exactly this for `COV_FLOORS` by clearing `MAKEFLAGS` - which does not touch it, because it
   is not a flag. The next variable added to the FULL path is the third instance unless it is added to
   the strip list in `tests/test_switches.py`'s `make()`.
3. **The `tooling` deselection against the coverage floor.** `ci/` and `switches.py` tests are
   deselected when the tooling stamp is fresh, so their lines are uncovered in the coverage report
   without anything having been deleted. The floor and the selection disagree about what a run covers.

**What is left after 166.** (The worklist itself is the older entry above, "The hamlet coverage
floor's last 128 lines" - these two are one thread: that entry is WHAT to cover, this one is why nothing
has been failing over it.) The hamlet-path floor stands at **99.28%**, ~90 lines across 11 modules
(`hamletgen/ways.py` 25, `settlement/_knobs.py` 24, `_geom/primitives.py` 16, `structures/fixtures.py`
9, and the rest in ones and twos). Feature 166 probed the two largest blocks against the retired
battery's own tests and found them listed as Missing THERE too, so this predates the deletion and is
not a consequence of it. Bringing it up is a TESTS job (spec FR-002's rule: bring the floor up by
tests, never by widening the omit list).

**Why this is its own feature and not a tail on someone else's.** It is three unrelated causes plus
~90 lines of genuinely untested engine code, and the work is tooling rather than cartography - no map
changes. Doing it inside a map feature is how it stayed invisible for as long as it has.

**Where to start:** run `make done FULL=1` and read the whole failure list before fixing anything; it
reports every phase. The evidence and the two probes are in
`specs/166-retire-the-check-battery/research.md` R11.
