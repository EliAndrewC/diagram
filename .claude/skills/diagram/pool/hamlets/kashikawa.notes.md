# Design notes: Kashikawa (樫川, "oak river") - scripted hamlet, the top of the band

*One of four demo maps from the scripted-generation experiment (2026-08-11). See
[`../../hamletgen/`](../../hamletgen/) for the pipeline and
[`inashiro.notes.md`](inashiro.notes.md) for the head-to-head with the authored Ikegami.*

**Kanji triangle**: 樫 *kashi* "evergreen oak" + 川 *kawa* "river". Kashikawa, "oak river" - named
for the oaks on the high ground the settlement backs onto, which the map draws as its managed
coppice patches and its fengshui belt.

**Subject**: ~20 households - the ceiling of the hamlet band, above which a place needs a headman, a
shrine and tax-free plots and is a village instead - on land falling to the northeast, draining off
the frame.

**What it is here to show**: the size end of the range. As first rolled (2026-08-11) it was also
the one place the pipeline was allowed to miss - 18 farmhouses seated against 20 declared, inside
the gate's 0.85-1.05 band but at the bottom of it - and the notes presented that shortfall as the
honest report it was. The 2026-08-15 re-carve (supply-bank bund hem + the padded well sweep)
re-rolled the whole map and the cluster now seats **all 20**, so the allowed-miss demonstration is
history rather than the map's current state; the reporting machinery is unchanged and a future
re-roll that misses will say so again.

**Known open**: Inashiro's two - the bare comb floor on the fan's shoulders (inherited from
`build_comb`), and a windward quarter derived from the slope. The woodland commons are
DERIVED, not authored - their count and sizes move with the roll (this file went stale on the
concrete number three rounds running, so it records the mechanism now): the shrink ladder
(250 -> 200 -> 160 -> 125 ft) and, when the generous crop set-backs would leave the oak map
woodless, a last-resort set-back profile (40/100 px against the gate's 14/69 floors) give the
dry, open, in-frame ground exactly the stands it can carry. The stands favor the unplowable
margins; whatever fraction of the name's high-ground oaks the window cannot hold stays implied
beyond the frame.

- 2026-08-15 (supply-bank hem re-roll): bunds hem onto the supply channels' banks
  (`build_comb(supply_banks=True)`, gate `paddy_bunds_clear_the_supply_channels`); the whole map
  re-rolled downstream. `settlement-review` (DELTA) passed the bund/channel read and the three
  re-seated wells, and caught this file's stale shortfall claim plus a gen docstring that was a
  copy of Inashiro's - both fixed the same day.

- 2026-08-16 (the fork draws both arms - engine change, this map re-rolled): the GM's Inashiro
  question settled in research/water.md "The head-race forks - supply commands both flanks";
  every `OFFTAKE_LADDER` row now draws canal B, gated by `comb_supply_commands_both_flanks`.
  This map re-rolled three times as review fallout was fixed at the engine (canal-B thread
  tails via interpolated piece boundaries, minimax worst-served well placement, the notice
  board's grove-clump keep-out, accidental-lane-crossing guards). Review log: round-2 DELTA
  flagged the blunt canal-B cap (fixed: the arm now tapers 7.2 -> 3.2 past its offtake); round-3 follow-up in the session of 2026-08-16.
- 2026-08-16 (round-3 review QUESTIONABLE, settled): the SW five-house pocket has no well of its
  own DELIBERATELY - its houses stand 77-182 ft from the drawn stream head and intake channel
  (measured from the manifest), and `settlement_dwellings_watered` counts surface water within
  ~760 ft as watering, so a well there would be redundant infrastructure beside a living stream.
  The minimax well objective still counts those houses (a known, harmless inefficiency - logged
  in future-work/); their real water is the stream, the period-correct arrangement.


- 2026-08-16 (known-opens round - floor trim, woodland re-seat, seeding trace; this map
  re-rolled): the ledger's four fork-re-roll defects were closed in one session. The comb floor is
  now TRIMMED to the collector's command area (`floor_overhang`, gate
  `comb_floor_ends_at_the_collector`); woodland commons seat inside the predicted kept window AND
  off the marsh (`open_ground_patches` frame + marsh keep-outs, shrink ladder 250 -> 200 -> 160 ->
  125 ft; gates `woodland_commons_within_the_frame` / `woodland_commons_on_dry_ground`); and
  `meta.cluster_seeding` records the seeding mode always ("frontage" on this roll).
  Map-specific: the envelope trim was provably surgical (NE extent 2726 -> 2484, all 750 plots and
  the wet plots byte-identical, one footbridge on the removed ground gone with it); the phantom
  bog parcel (250 ft recorded, 2 crowns drawn vs its sibling's 53) is gone and the roll then
  seated one dry 160 ft oak stand (the derivation has moved since - see the later entries). Review log: full DELTA caught the phantom parcel and this
  file's stale off-frame paragraph (both fixed same day); follow-up pass on the re-seat.

- 2026-08-16 (second known-opens round - flooded-sliver demotion, well/check alignment,
  recorded woodland canopy, trim dedup; this map re-rolled): pointed plots (interior angle
  < 25 deg) no longer take the FLOODED tint and the painted tint is recorded as
  `flooded_plots` (gate `flooded_plots_read_as_basins` at 15 deg); the well minimax and
  rescue read `settlement.surface_water_dist` - the watered check's own predicate - so wells
  stop chasing stream-watered houses; woodland stands record their crowns (`tree_crowns` +
  per-parcel count, gate `woodland_commons_visibly_stocked`) and register as placer
  keep-outs; the trim corner's duplicate vertices are merged (`dedup_ring`).
  Map-specific: the wells realigned (the SW stream-watered pocket now shapes the objective the
  settled ruling described: three wells in the NE cluster at 69-298 ft, none by the stream
  frontage) and the tighter window went WOODLESS at every shrink rung - the motivating case for
  the last-resort set-back profile. The stands re-derived twice more inside the round as the
  profile calibrated (a mid-round 35-crown 160 ft footslope stand was review-verified for
  recorded-vs-drawn crown agreement, 35=35 / 15=15); the shipped roll seats TWO 125 ft stands
  (15 and 17 crowns), dry and on-frame - the exact stands are roll-derived, the invariants
  (dry, on-frame, recorded canopy, check-legal set-backs) are what hold.

## 2026-08-17 - re-packed by feature 121 (the placer tests the rake it draws)

19 of 20 houses re-seated (median 362 ft, max 866 - a full re-seed, not a nudge); the SW outlier at
(1352.4, 3062.7) is byte-identical. Household, garden, yard, well and shed counts all unchanged.

WHY: the bundle placer used to clear an axis-aligned rect for a house the map draws raked by up to
+/-5 deg, and `houses_clear_of_lanes` measured an axis-aligned rect too. Both read the drawn raked
corners now, so `LANE_CLEARANCE` stopped being what holds a house off a lane and dropped 48 -> 40 px
(derived: longest drawn minka's half-diagonal 34.7 + the lane's half-tread 5).

MEASURED HERE (settlement-review, DELTA): house-corner-to-tread min 13.0 -> 5.2 ft, median 35.0 ->
29.1, and **0 on the tread** before and after. Cluster density 1.42 -> 1.45 houses/acre - it
compacted rather than re-composed. Bundle spacing IMPROVED: sub-5-ft bundle pairs 10 -> 7, min gap
2.0 -> 2.4 ft. The windbreak re-derived and stayed a belt (aspect 0.10) with no house corner under a
crown. Nothing else drifted onto a lane - the closest accessory is a threshing yard at 18.4 ft.

Review verdict: PASS, no errors.

OPEN, ruled nowhere (raised by that review, NOT caused by this change - the house is
byte-identical): the SW farmstead at (1352.4, 3062.7) stands 469 ft from its nearest neighbor and
385 ft from any lane, with no way reaching it, on a map declaring `nucleated: true`. The re-pack
moved the other 19 houses a median of 362 ft and left it, so the placer had every chance to fold it
in. Needs a one-line ruling: outlying holding by intent, or a seeding gap.

## 2026-08-17 (later) - the outlying farmstead: SUPERSEDED, see the note at the end

The settlement-review of the feature-121 re-pack asked for a ruling on the farmstead at
(1352, 3063): 469 ft from its nearest neighbor, 385 ft from any drawn way, with no track reaching
it, on a map declaring `nucleated: true`. Two separate complaints were tangled together, and they
have different answers.

**The isolation is GONE, and not by touching this house.** The front-row density fix (front_row now
samples by one-bundle-pitch spacing along the field edge instead of by household count) pulled the
rest of the cluster toward the paddy, and this farmstead's nearest neighbor is now **170 ft**
against 111 / 110 / 105 for the next three - an ordinary outer-edge spacing, not a hamlet of one.
The house itself did not move; the settlement grew toward it.

**The way-access is ACCEPTED, deliberately.** It still stands 385 ft from any lane against 41-70 ft
for its neighbors, and that is correct rather than an oversight: a lane must NOT run through the
flooded paddy (`settlements/ways.md`), and people cross into the fields on foot **along the bunds**.
An edge farmstead standing at the paddy margin is reached the same way every field worker reaches
the same ground. Drawing a lane out to it would put a no-build corridor across the crop to serve one
household - the opposite of the rule.

**What was declined**: (a) folding the house into the nucleus - it sits 50 ft from the drawn stream
with its own byre, which is a coherent holding, and the placer had every chance to move it and did
not; (b) drawing a spur lane to it - see above, it would cross the paddy; (c) a check requiring every
farmhouse within N ft of a way - it would fire on exactly this legitimate case and on nothing else.

~~Ruled 2026-08-17. Not to be reopened as a bug.~~

**SUPERSEDED THE SAME DAY - do not quote the ruling above.** The front-row cap re-packed this map
again and **there is no house at (1352, 3063) any more**. The westernmost farmhouse is now at
(1634, 3141), 68 ft from the spine. Measured across the shipped manifest: no farmhouse on this map
is more than **103 ft** from a way by center, or **71.7 ft** by corner-to-tread. The section above
says "The house itself did not move; the settlement grew toward it" and "It still stands 385 ft from
any lane" - both are false of the map that ships.

The paddy argument it rests on is still SOUND as reasoning (a lane may not cross the flooded paddy,
and field workers reach that ground along the bunds); it simply has nothing left to cover here. It
is kept for provenance rather than deleted, because the failure mode being guarded against is a
future session quoting "not to be reopened as a bug" at a genuinely stranded farmstead on some later
roll. If one appears, rule it fresh.

## 2026-08-18 - where the ox sleeps, and a well objective that measured the wrong houses

WHAT CHANGED, ACROSS ALL FOUR SCRIPTED HAMLETS (2026-08-18)

- **`byre_form` is a knob now.** The doctrine had been quietly self-contradictory: the *doma* rule
  says the draft ox is stalled under the farmhouse roof, while the byre placer drew a detached shed
  on the shared ground. Both are attested - a household that OWNS its team houses it in its own
  homestead (the *magariya* 曲家, whose short arm IS the stable; the animal range of the north-China
  *sanheyuan*), while a team that is SHARED or hired stands where the borrowing household can reach
  it - so per Principle XII it becomes a per-settlement roll rather than a ruling.
- **and the overlap registry had been describing code that no longer existed** - its `byres` entry
  claimed the byre "abuts its own farmhouse (draft_byres places it against the wall)", which the
  placer stopped doing long ago. Now corrected and GATED rather than asserted in prose.
- **the well tie-break's last key is the objective itself, not a proxy.** The primary key buckets
  coverage-plus-frame into 66 px steps, and inside a bucket the order was distance to the cluster
  CENTROID - the empty ground between the lobes of a two-lobed cluster. It is now `_worst_after` at
  full resolution, with the neighborhood measure breaking exact ties.

RIPPLE ON THIS MAP (re-measured 2026-08-18 after the round-2 review): 4 byres at the placer's
target of 4, form `detached_commons`, owned by the houses ranking [3, 4, 10, 11] by footprint of
20 - the owner ranking was reading a `wealth` field that is 1.0 on every scripted house, so it had
collapsed to smallest-x and was handing oxen to the west edge. The shelter belt carries 207 clumps
with a minimum canopy depth of 28.0 ft measured ACROSS the wind, which is the measure that means
anything on a diagonal belt; the per-latitude framing an earlier entry used flags healthy belts
and misses thin windows. Worst walk among the 3 houses that actually need a well: 152 ft.

## 2026-08-18 - the woodland commons: off the lattice, and two hamlets that had none

WHAT CHANGED, ACROSS ALL FOUR SCRIPTED HAMLETS (2026-08-18)

Two ledgered defects that turned out to be one, with a worse one underneath.

- **the commons are off the lattice, and no two are the same size.** `open_ground_patches` samples a
  uniform 90 ft lattice, scores every seat by ONE monotone function (near the cluster, leaning
  upslope) and takes the best seat outside a FIXED separation radius - three ingredients that do not
  merely tend toward an even chain, they produce one by construction. Mizuguchi shipped the proof:
  three IDENTICAL 250 ft squares stepping (+270,-270) twice, reading as three stamps of one wood on
  a ruled diagonal; Inashiro had the same chain the other way. The accepted seat is now nudged up to
  half a step off the lattice and its size rolled +/-15%, both from the map's own position hash
  (so a map is unchanged by regeneration and two maps differ from each other), and every nudge is
  re-asked through the same qualification test - it can only move a legal seat to another legal one.
- **a hamlet at the top of the band had no wood at all.** Kashikawa - the map NAMED 樫川, "oak
  river" - seated ZERO parcels out of 231-286 candidate seats, at every rung of the shrink ladder
  and both set-back profiles, with the best achievable clearance NEGATIVE (the square overlapped a
  paddy). The shrink ladder and the relaxed set-backs were each added FOR Kashikawa in earlier
  rounds and neither could ever have worked, because the binding constraint was not the set-back:
  the scan demanded the whole square inside the predicted crop window plus a further 16 ft, while
  its own gate check asks that **70% of the parcel's bbox** be inside the view and says outright
  that a parcel clipping at the edge "reads as 'more wood that way' and is fine". The scan mirrored
  the check's formula but not its WINDOW. It now judges a seat by area the way the check does.
  Being stricter than your own gate is not the safe direction - it cost two of four hamlets their
  woodland outright.

RIPPLE ON THIS MAP: The oak river has oaks: 0 -> 2 parcels, 117, 125 ft. They are small because 20
households genuinely commit this land, and both now clear the 120 ft legibility floor that stops
the variance machinery compounding its way into a copse.

## 2026-08-18 - the six-defect pass

WHAT CHANGED, ACROSS ALL FOUR SCRIPTED HAMLETS (2026-08-18)

Six known /diagram defects were cleared in one pass, plus one regression caused inside it. In the
order they matter to a reader of these maps:

- **the front row is ONE RANK.** `front_row` had begun sampling seats by density (to stop a starved
  row leaving a big field under-ringed) and, uncapped, seated every household by itself - every
  cluster came out a single file along the paddy. It now returns seats center-out and stops at one
  rank's worth of the band; the surplus falls to the flanking and cloud passes, which seat BEHIND.
- **a lane must reach something.** Internal lane ends ran the full cluster band into open grass,
  serving no house and meeting no way, because lanes are laid BEFORE the houses they serve.
  `trim_lane_stubs` now pulls such an end back AFTER the farmstead flush - rewriting the ink in the
  stream slots the lane already owns, so nothing re-layers - and stops at the last homestead served
  rather than at the rule's edge. A near-parallel contact does not count as arrival (a lane that
  MEETS another crosses it; one that FRAYS runs alongside). A fragment below one homestead's
  frontage (~71 ft) is dropped: it can front nobody. `lanes_reach_something` gates it.
- **byres are shared, so they spread.** Owners are chosen by a maximin spread, then - among the
  near-best - by how many households stand within borrowing distance. Spread alone picked the most
  ISOLATED homestead, which is the inverse of a shared shed.
- **the title placard may not sit on a woodland commons.** Dense canopy is an obstacle to the title
  the way a grove already was; only the sparse grazing scrub is not.
- **`scatter_audit` could not see tree crowns.** Its palette had drifted from the engine's; it now
  imports `CROWN_FILLS`, and a coverage guard fails when the two disagree.
- **the SVG emits the rake it placed** (`.1f` / `.2f`, not whole pixels and whole degrees), and the
  gate reads the same raked corners the placer does.

RIPPLE ON THIS MAP (re-measured 2026-08-18): woodland is [(125, 29)] - each pair is (ft across,
crowns) - stocked at 540-554 sq ft per crown, which is the stated density rather than an artifact
of how much of a parcel lies near a keep-out. Crown count used to be the number of THROWS at a
parcel, and `_sparse` rejected a share of them, so small parcels came out both smaller AND
thinner; it is a target now. Parcels under the 120 ft legibility floor are DROPPED rather than
drawn small.

OPEN, wanting a one-line ruling rather than a fix: the maximin spread put a byre 38 ft from a
communal wellhead (the other three are 168-317 ft from any well). Nothing governs it - `homesteads.md`
puts byres and wells in the same interstitial courtyard ground, so the adjacency is structural. The
reading I would take is "the beasts are watered at the well, that is where a byre goes". Recording
the decision matters more than which way it goes, because the next re-pack will produce it again.
## 2026-08-17 - the paddy size floor: a basin too small to be worth its own bund

The GM, reading a hamlet sheet: *"most of the rice paddy fields are rectangular, but then there are
a few very small triangles. Is that realistic? It looks like it is just a mistake, like, basically,
a rendering artifact rather than something that is from our historical research. Relatedly, should
there be a minimum rice paddy size?"*

Three answers came out of the research pass, and only one of them is yes. There is **no absolute
minimum** - Shiroyone Senmaida works 1,004 basins on ~4 ha, averaging ~18-20 m2, the smallest about
half a meter square - so a floor in acres was declined. **Four-sides-only** was declined too: it
would re-impose the *kochi seiri* consolidation grid the research already flags as the anachronism.
What is real is a **ratio**: on a terrace the wall is a riser the slope demands anyway, but on a
valley-floor fan the aze is the whole structure, built only to hold water and re-plastered every
spring, and the alternative to a scrap is never no-rice - it is making the basin next door bigger.
So a comb basin under **0.25 of the fan's own design cell** is dropped by the toe pass and absorbed
by `close_seams`; the gate `paddy_basins_are_worth_their_bund` fires under 0.20. The triangularity
was the symptom - a fragment clipped off the lattice at the fan boundary comes out triangular - and
the size was the cause. Full findings, both declined alternatives, the two derivations of 0.25 and
why the gate could not sit at 0.15: `research/fields.md`, "Minimum basin SIZE".

**On this map, measured on the SHIPPED manifest against main's tip.** 827 -> 814 basins; smallest
surviving basin 0.254 of the design cell; acreage, 20 of 20 households and the field outline all
hold.

**The cluster barely moved: 19 of 20 houses unmoved, min-max displacement 8 px** - worth recording
precisely because Inashiro's re-packed wholesale at 304 px on the same rule. Gardens, yards, sheds,
byres, wells and the kosatsuba are unchanged; the windbreak went 212 -> 190 clumps and `meta.view`
shifted. The ripple is real and its SIZE is map-specific; do not generalize from one map in either
direction.

This map needed no `settlement-review` pass this round: its cluster is effectively unchanged and the
fabric rule was reviewed on Inashiro, Mizuguchi and Sawada.
**The regression it caused, and how it was cleared.** The rule shifts the drawn plot count, which
rotates the shared placement stream, and on rolled cohort seed 41 the rotated roll seated a well
outside the house cloud and tripped `crop_not_held_open_by_one_feature` - seeds 1-48 went 45/48 ->
44/48. Measured in a detached worktree, seed 41's FIELD geometry was byte-identical either way, so
the failure was not a paddy defect at all: it was a well landing on a pre-existing weakness in
`hamletgen.place_wells`, whose minimax tie-break (distance to centroid) cannot express "this seat is
outside the settlement". The GM's call was to take that fix as its OWN piece of work first and land
the floor on top, which is why `e0fb2417` precedes this entry in history. With both in, seeds 1-48
are back to **45/48 with residue identical to baseline** - seed 41 passes and nothing else moved.
Cohort seed 62 still fails the same check and always did: its northern lobe has no interior seat in
its minimax bucket at all, so a tie-break cannot reach it (ledgered in `future-work/`).

### 2026-08-18 - the windbreak frame fix, corrected: CLIPPING IS THE DOCTRINE

Recorded once here and referenced from all four hamlet notes, because the mistake was general.

A review asked for a belt whose clumps were "touching the frame" to be contained. The fix inset the
allowed window by a canopy reach, which required the WHOLE crown to be inside - and that is
backwards. `settlements/presentation.md` (GM 2026-07-20) says the belt CLIPS at the view edge and
"a partially visible belt reads as 'the wood continues'"; `hard_features_within_frame` demands
partial visibility of a village grove rather than containment. Only a clump with **no visible ink**
is waste.

The cost of getting it backwards, measured by two independent reviews: Mizuguchi dropped **40
clumps to remove 3 invisible ones** - 37 at least partly visible, 12 not even touching the frame -
leaving a ~100 ft bare channel through the middle of the wind wall on the windward side; Sawada lost
**46% of its canopy** and its belt became shorter than the cluster it shelters.

Inverted to skip only a clump lying WHOLLY outside the frame. Result across the pool: **zero
invisible clumps on all four maps**, belt gaps 26-37 px against a 30 px baseline, and clump counts
164 -> 169 (Inashiro), 212 -> 190 (Kashikawa), 131 -> 127 (Mizuguchi), 231 -> 171 (Sawada) - the
Sawada figure being the re-pack's own effect on the house cloud the belt derives from, not the clip.

**The transferable part**: the first review's complaint was itself against a documented rule, and
following it literally made three maps worse. A reviewer's finding is evidence, not a verdict - check
it against the doctrine file before acting on it.

## Feature 123 - the lane web (back_lane)

**7 of this map's 20 farmhouses stood more than 100 ft from any way. Now none do** - the worst is
86 ft and the median 63 - **and every lane on the sheet belongs to one connected
network**, which is the part that took two review rounds to get right.

The research is decisive that a house in a nucleated cluster is reached: "every house in the
nucleated village is accessible via the interconnected system of narrow lanes and alleys". The FORM
is a seeded knob, because the record supports two and two supportable answers become variance rather
than a choice (Principle XII). This map rolled **`back_lane`**, which runs PARALLEL to the field margin behind the ranks of plots, tied to the rest by cross-links - the planned form the sources call a "rectangular framework", the one that says the place was LAID OUT. It carries **5 web
lanes** of 9.

**Four things here are load-bearing, and each was learned by getting it wrong first.**

*The web is laid last of the built things* - after the houses AND their byres, sheds and wells. Laid
before the houses it reserved ground from a cluster not yet packed and grew the four hamlets' long
axes 15-97%; laid between the two it exiled byres up to 210 ft and erased feature 121's
borrow-coverage fix. Reviewers verified the final order costs nothing: byres and wells are
byte-identical to the pre-web manifest, coordinate for coordinate.

*Connectivity is decided before any ink.* Candidate runs grow outward from the skeleton and only the
reachable ones are drawn, because a lane once drawn cannot be taken back.
`farmhouses_reach_a_way` enforces the same thing from the other side - it measures to the connected
COMPONENT containing the connector, since a check an island can satisfy rewards drawing an island,
which is exactly what the first version did. Orphaned SKELETON arms are linked too; the transitive
check found some, which no rule could see before.

*A lane is not drawn where a reader would see one lane twice.* A run that shadows an existing way -
by fraction OR by one unbroken bundle pitch - is refused, and so is one that would run the length of
the shelter belt rather than crossing it.

*A house is served with margin, not to the millimeter.* The footpath pass triggers at nine tenths of
the reach, so no house passes by inches and none gets a path drawn to cure a rounding error.

Where the regular web still cannot reach a steading, that house gets what an outlying farmstead
really has: a footpath of its own, routed round the neighboring plots rather than ruled at them,
stopping at its first contact with the network, and planked where it crosses a ditch.

## Feature 124 - a farmhouse fronts one lane end, not three

A `settlement-review` read this map's east node at 3x zoom as **a broom**: ways leaving one point
within about 23 degrees of each other, two of them ending blunt, and **all of them claiming the same
farmhouse** - at 66.9, 55.1 and 40.0 ft. Three ends, one house answering for all three.

Two rules should have caught it. `lanes_reach_something` lets an end discharge its obligation by
stopping at a farmhouse and never said a house could only do that once. The lane web's shadow rule
tests a new web run against what is already drawn - but both offending arms are SKELETON lanes, laid
before the houses exist, so they are never tested against each other.

The fix is one clause in `trim_lane_stubs`, which was already the right place: it runs after
placement, only ever SHORTENS (so it cannot invalidate a seated house), and rewrites ink in the
stream slots a lane already owns. Its house test is now **exclusive** - the end nearest a farmhouse
keeps it, and any end standing alongside it and pointing the same way must find its own reason to
exist or be trimmed until it does. Below one homestead's frontage the existing floor drops it, which
is what the reviewer proposed.

**A house reached from OPPOSITE quarters is a corner, and stays legal.** Without that clause the rule
flags most of a nucleated cluster's middle. And "blunt" means what `_FRAY_DEG` already means: the
ends in question stood 21.6 and 24.3 ft from another way and near-parallel to it, so they had not MET
it - proximity is not arrival, which this engine had already learned once.

This map now has no fan, and every farmhouse is still reached: worst 85 ft, median 60.

## 2026-08-24, feature 128: re-rolled under the new stage order, verdict unchanged

The lanes now go down after the houses (`stage_seat` -> `stage_homesteads` -> `stage_track`), and the
connector's bearing sweep ranks candidate bearings against the standing steadings. This map's
geometry moved with the reorder and it gates CLEAN, as it did before. Recorded so the manifest change
in this commit is not an unexplained diff - the substantive write-up is on
[`mizuguchi.notes.md`](mizuguchi.notes.md), which is the map that failed and forced the fix.

### 2026-08-28 - manifest re-recorded under the landed feature-137 engine

The committed manifest was rolled by an earlier engine state; this commit records what the landed engine (GitHub main f4456a72) draws, byte-identical to the mirror's render-sync, so main is clean. Not a review pass: this map is red on the gate and is feature 139 T08 (the review comes with its fix).
## 2026-08-28 - feature 140: seats measured against a few chords of the field edge (the map moved)

Placement now judges a farmhouse seat against the field outline's chords facing the cluster (open chain,
pushed out 3 px; `M["field_chains"]`) and never the full outline; `houses_clear_of_paddies` reads the same
chords. The GM ruled the maps may move (*"none of what we have done so far is in any way canonical"*), and
this one did - every seat re-rolled, wells, byres and the lane web with it. `settlement-review` DELTA
pass: **ACCEPTABLE WITH NOTES** - nothing attributable to 140; the lane-ink residue it names
(`lanes_bend_like_paths` on Kashikawa and Sawada) is feature 139's open class, now with coordinates in the
review record (`specs/140-placement-segments/research.md` R5). Set-backs read as a rank; the measured
corner-to-chord profile is in R5 too.

## 2026-08-28 - feature 145 (the solver moved the fan; the whole map re-rolled)

settlement-review, NEEDS-WORK: two errors, both in ground the re-roll moved, both invisible to a green gate.

**The field grave (2092, 1645) - FIXED.** The mound was painted at 0.9 opacity over an intact lattice, so
three plot rings and nine bund junctions ghosted through and it read as a translucent decal. It is opaque
now. The registry's claim that the paddy tiles AROUND it is still geometrically false - carving the plots
is a field-engine change, deferred with its measurement in `future-work/farming-communities.md`.

**The board's caption over a byre (2003, 2838) - ACCEPTED, with what it costs and the alternatives.** The
"notice board" caption clips the byre's roof by 15.4 x 4.8 ft. Three things are true and worth separating:

1. The placer is doing what it was built to do. `label_blockers` is DERIVED and already includes byres, and
   `_best_label_spot` takes the least-covered seat when nothing inside the ladder's reach is clear. In this
   cluster nothing is clear: the board sits at the traffic optimum (14 of a possible 15 dwellings within
   250 ft) and its caption has no clean ground within reach.
2. The rule as written ALLOWED it. `_LABEL_EXEMPT` excused every caption over a byre, on the premise that
   "a caption cleared for the house is cleared for it" - which holds where a farmhouse carries a caption and
   fails at hamlet tier, which captions no farmhouse at all. Feature 145 moved `byres` into `_LABEL_GROUP`
   under the "farmhouse" group, so the rule now says what it should: a farmhouse caption may cover a byre and
   nothing else may.
3. **No check enforces that rule any longer.** `labels_clear_of_other_buildings` - the check the whole
   caption registry exists to feed - was retired by feature 141's cut and is not in `gate_check_names.json`;
   only comments still name it. So the registry is live doctrine with no consumer, and this map was green by
   construction. Restoring it is feature 146 (class 2 is exactly "a check nobody has proved fires").

Alternatives priced and declined for the caption itself: move the board off the traffic (trades the thing
the board is FOR against 15 x 5 ft of overlap on an annex roof); shrink or re-tilt the caption (the tilt
already follows the glyph's own rake, which is the rule); drop the caption (a hamlet's one civic fixture
needs its name). Accepted as drawn, recorded here so the next reader knows it was a decision.

## 2026-08-29 - settlement-review, DELTA after the merge onto main (feature 150)

Re-rolled by the ENGINE under an unchanged `.gen.py`; the real delta is narrower than it looks -
`lanes` gained a `z` and two lost their end nubs, 4 manure heaps became pits, the title and scalebar
translated, and the water z bookkeeping moved. Houses, byres, wells, gardens, yards, fields, marsh,
commons and the kosatsuba are byte-identical to main. Verdict **needs-work**.

**CAUGHT, and fixed here.** The title placard was drawn at `fill-opacity="0.94"` and the ground cover
ghosted through it - **6,900 of 79,772 interior pixels, 8.65%**, with grass, brush dots and two whole
pine glyphs legible at native resolution. That is the same defect, and the same fix, as this map's own
field grave eight days earlier ("painted at 0.9 opacity over an intact lattice ... it is opaque now");
one was fixed for that reason and the other was left translucent with nothing recorded either way. The
placard is opaque now. Also fixed: the scalebar's recorded box was the placard's foot rather than its
ink, over-claiming 26 px - 41% of its own height - and reaching 12 px BELOW the placard containing it.

**Confirmed**: `drop_end_nubs` was surgical on this map - index 1 in both cases, first stretches 2.69
and 4.00 ft, turns 66.7 and 90.0 degrees, both END points preserved exactly, and lane 11's approach to
house 4's doorway now runs straight instead of doglegging. The marsh keep-out holds under a
manifest-free pixel count: 0 of 691 brush dots, 0 of 72 pines and 0 of 78 crowns on marsh-colored
ground. The 2026-08-28 field-grave fix held (0 paddy-green px inside the mound).

**CAUGHT, recorded, not fixed**: lane 0's north end stands 206.1 ft from any other lane and 246.5 ft
from the nearest farmhouse, blunt-capped in open grazing, with `lanes_reach_something` green on it; the
homestead fixture ring is stamped rather than composed (13 of 20 houses carry the row at dy -18 to -21
ft, privies at bearing 31-41 degrees at 10 of 13); and the accepted-limitation entry in these notes
names a byre clipped by the board caption that stands nowhere within 167 ft, in this manifest or main's.

## 2026-08-29 - feature 155: the lane sweeps rewritten, and the 25 ft hole ACCEPTED as honest

Two `settlement-review` passes on this map graded the previous round's fixes `needs-work` and were
right on both counts: of the two lane defects, one fix was a no-op and the other could not reach its
target. Both are fixed at the cause now, and the third finding is recorded here rather than fixed.

**FIXED - the 44 ft doubled remnant (lane 11, running within 6.6 ft of lane 8 for its whole length).**
The sweep written for it measured `1.5 * w` - 4.5 ft for a 3 ft footpath - against a 6.58 ft defect, so
it dropped nothing on the map it was written for, and nothing on Sawada either, whose own 11.4 ft
remnant was quoted in the sweep's docstring three lines above the constant that rejected it. The
metric is gone. The test is now STRUCTURAL: a lane whose two ends both land on the same other way
connects that way to itself, and unless dropping it would put a farmhouse beyond
`farmhouses_reach_a_way`'s own 100 ft, it is ink for a journey nobody makes. A structural predicate
has no dial to leave set too low, which is the point - Sawada's reviewer named
*"calibrating a general rule to the single case that was easiest to measure"* as the recurring defect
across three separate fixes on these maps, and a threshold was going to keep re-committing it.

**ACCEPTED, NOT FIXED - the 24.95 ft hole between the caps at (2009.0, 2938.3) and (2000.9, 2914.7).**
The pass that exists to close it, `_bridge_collinear_breaks`, had been silently excluding it for six
days: `c0c724b2` (2026-08-23) wrote a tread-width candidate floor and a short-gap exemption from the
collinearity test, `569136fc` reverted the code the same day as collateral in a five-change revert
that does not name it, and **both comments survived**, so the function told every reader it handled
short holes while the code required 30 ft. That is repaired - the floor and the exemption are
restored narrowly, and three further defects the restoration exposed are fixed with it: the debris
floor silently refused every bridge shorter than 30 ft (a bridge is a join link and is now drawn as
one); a 10 ft routing lattice cannot represent a 25 ft gap; and the pass took the single smallest gap
and RETURNED when it could not route it, so one honestly-interrupted break silenced every other break
on the map.

With all four repaired, this hole still does not close, and the measurement says it should not.
`_route` returns **nothing at all** between these two caps - not "nothing short enough" - at BOTH the
fabric clearance (7 ft) and the join clearance (4 ft), on a 3 ft lattice.

**WHAT IS ACTUALLY IN THE WAY - and the first version of this entry got it wrong three times over
(settlement-review, 2026-08-29, third pass).** It named one obstacle at 2.81 ft and blamed overlap.
All three corrections matter, because they are what a future session would act on:

- **It is a TWO-SIDED PINCH between two different homesteads' appurtenances, not one garden.** Garden
  bed 0 stands west of the line and **threshing yard 1** - house 1's yard - stands east of it. The
  first entry missed the yard entirely.
- **The distances were measured on the axis-aligned `x/y/w/h` rects, not the DRAWN polygons.** Read
  the way `dev/placement.md` requires, garden bed 0 is **3.40 ft** off the line (not 2.81) and
  threshing yard 1 is **3.64 ft**. This is the same error these notes record fixing in feature 121 -
  *"the bundle placer used to clear an axis-aligned rect for a house the map draws raked"*.
- **Overlap is NOT what refuses the bridge.** The narrowest free corridor across the gap is
  **10.71 ft** (garden 6.76 ft one side, yard 3.94 ft the other, at 35% of the way across). A 3 ft
  tread centered there would leave ~3.9 ft to each footprint and overlap nothing;
  `features_do_not_overlap` would pass it. What refuses it is the **4 ft join clearance**, a planning
  margin. Saying "a tread through someone's vegetables" priced the alternative against a consequence
  it does not have, which is exactly the sentence that stops a future session looking further.

**What it costs, in observable terms**: at fit zoom the reader sees two rounded caps facing each other
across ~25 px of bare grass in the middle of the built-up frontage. It is a LEGIBILITY cost only - the
lane web remains a single connected component at a 6 ft ink tolerance, and every farmhouse is served
(worst house-to-way 89.1 ft, unchanged by the remnant drop).

**Alternatives priced and declined**:
- *Relax the directness budget* (`_PATH_DIRECTNESS` x 24.95 = 49.9 ft). Declined because it buys
  nothing: there is no route at any length, so the budget is not what refuses this one.
- *Route below the 4 ft join clearance.* Declined HERE, but not because the tread would overlap
  anything - see above. Declined because lowering a global planning margin to close one hole on one
  map is the wrong shape of fix; the right shape is the knob in the open question below.
- *Trim the two caps back so they stop reading as an interrupted way.* Declined: both arms front
  farmhouses at their far ends, so the trim would strand service to buy tidiness.

**Reopen with a route that clears BOTH garden bed 0 and threshing yard 1 at the join clearance** - or
with the ruling below. Not with a wider tolerance, and not by looking for the single obstacle the
first version of this entry invented.

**OPEN QUESTION this raises, for a research pass rather than a ruling: should a 4 ft planning margin
bind inside a 10.7 ft interstice between two homesteads?** The gap sits between one house's garden and
another's threshing yard - the interstitial courtyard ground `settlements/homesteads.md` already
describes as shared, where byres and wells stand. A 3 ft footpath passing ~3.9 ft from a garden bed
and ~3.9 ft from a work yard is not obviously a violation of anything physical; it is the ENGINE's
margin that refuses it. What the record would have to show is attested in-cluster path widths and the
clearance between a footway and a kitchen garden or work yard in a nucleated Japanese farming
settlement - the roji/komichi literature and the vernacular farmstead-layout record both bear on it.
The reviewer's read, which matches the project's own knob rule: the record will support NARROW
in-cluster footways hard against garden and yard edges, since that is what makes a nucleated cluster
nucleated - which would make this a **per-settlement in-cluster margin knob**, tight on a dense roll
and generous on a loose one, rather than one number to lower. Take that shape, not this one hole.

**ALSO CAUGHT by the same pass, outside the delta, and re-recorded here because the old numbers are
quoted:**
- **The notice board is no longer at the traffic optimum and these notes said it was.** Measured
  2026-08-29: **9 of 20** dwellings within 250 ft against a best-available 13 anywhere in the cluster
  (69% of the maximum). The feature-145 entry records "the board sits at the traffic optimum (14 of a
  possible 15 dwellings within 250 ft)", which described a roll that no longer exists. The board sat
  at (1999.8, 2852.0) with 13 of 13 at `b248ab25` and moved to (2255.5, 2989.2) at `8260a6e0` - the
  commit BEFORE feature 155's lane work, so not caused by it. It stands on a lane fork rather than in
  a quiet corner, so this is a drop rather than the Sawada failure mode; it was silent, and the stale
  number is the kind that gets quoted.
- **Lane 0's north end is a FIELD TRACK, not an unfixed blunt end.** The 2026-08-29 entry records
  "206.1 ft from any other lane and 246.5 ft from the nearest farmhouse, blunt-capped in open
  grazing". Current roll: **152.4 ft** and **166.4 ft** - and the number nobody had measured,
  **17.0 ft from the field outline**. A track that runs out of the cluster and stops at the paddy
  edge, where you step onto the bunds, is the arrangement these notes already ruled sound on
  2026-08-17. Re-recorded as sound so the next session does not trim it.

## 2026-08-29 - feature 154: an `entrance` board on the windward fringe eats the shelter belt (OPEN)

**THE REGRESSION, and it is this feature's own.** The `kosatsuba_seat` knob rolled `entrance` here,
which pushes the board out of the cluster - and on this map the way out runs along the windward
fringe, so the board landed inside the windbreak belt's own band. `stage_notice` runs BEFORE
`stage_windbreak`, so the board wins and the belt yields: five clumps that had covered those columns
are gone, all five inside the board's `village_grove` keep-out disk, and nothing re-seated into them.
`village_windbreak_is_continuous` fails with a 40 ft bare run.

**PROVEN BY A REVIEWER, AGAINST TWO OF MY OWN WRONG DIAGNOSES.** I called it a chord artifact - the
straight across-wind projection leaving a bowed belt's footprint, which a peer session had just fixed
on Kuwabata. It is not, and the proof is clean:

- the belt's recorded `poly` is **byte-identical** between the two commits - 24 vertices, unchanged
- replaying segment 0613 by hand: the previous roll gives a **20 ft** run and PASSES; this one gives
  **40 ft** and FAILS, on the same polygon
- the polygon has **93.7 to 95.2 ft of depth** at every bare column, so the peer's polygon-depth fix
  cannot clear it
- I had sampled `(2205, 3118)`, the coordinate in the failure message. **That is not the hole.** The
  segment reports `_near`, the nearest clump in projection - 15.5 ft outside the r=14 window. Reading
  a diagnostic's coordinate as the thing it diagnoses is how both wrong diagnoses happened.

**A FIX WAS TRIED, MEASURED AND REVERTED - recorded so nobody pulls the same lever.** The board's
keep-out is one disc, `30.0 + clump * 0.90`, sized to reach the far end of a ~53 x 8 ft caption: about
9,500 sq ft of woodland cleared to protect about 450. Replacing it with a small disc on the glyph plus
a row of discs stepped along the caption's recorded box **made the hole worse - 40 ft to 70 ft, five
more belt clumps lost.** The reason is that `M["labels"]` records the caption's box UNROTATED while
the caption is drawn rotated about its centre (here -42.7 degrees), so the discs march along a line
the caption does not occupy: they clear ground the belt needed and miss ground the caption uses. Any
shape-aware keep-out has to rotate the box first.

**TWO OPTIONS PRICED, NEITHER TAKEN, because both are bigger than the hour they were found in:**

1. **Refuse an anchored seat whose keep-out would lie in the belt**, when a legal seat outside it
   exists. This is the narrow fix and it is contained to the board siting. The obstacle is ordering:
   `plan.belt` is not populated until `stage_hinterland`, one stage AFTER `stage_notice`, so the
   siter cannot see the belt. `belt_polygon(s, plan)` is pure and could be called early from
   `stage_notice` to predict it, and the prediction passed to `place_kosatsuba` as an avoid region -
   new plumbing across a layer boundary, worth doing deliberately rather than late.
2. **Make the keep-out proportionate**, rotating the caption box first. Fixes every map at once and
   removes the disproportion (a 12 x 5 ft plank clearing a 55 ft radius, larger than a well's or a
   shrine's). Blast radius is every map that carries a board.

**And a research question the reviewer raised that would settle which:** was a village's planted
windbreak cleared around a notice board at all? The expectation is that it was not - the board stood
at the wood's EDGE, not in a glade - which would argue for option 2 with a much tighter figure, and
would resolve this as a side effect. Nothing in `research/urban-features.md` speaks to it.
