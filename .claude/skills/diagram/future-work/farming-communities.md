# Future work: farming communities (hamlets and villages)

**Everything to do with a settlement whose reason for existing is its fields.** Hamlets and villages
share one file deliberately (GM 2026-08-24): a village is a hamlet with a headman, a shrine and
tax-free plots, not a different kind of place, and its defects are the same defects.

This is where hamlet work goes - the paddy fabric, the lane web, homesteads and their groves, wells
and byres, woodland and windbreaks, the notice board. A known drift between the engine and the research record
is NOT tracked here: `make claims-report` lists every one, and `make open-questions` lists the research the record
labels a guess or finds silent. An entry here is work neither of those carries.

## Rename the `grave island` class to `field grave` (settlement-review, Kashikawa 2026-09-28)

Feature 267 made the field grave a knob - an island inside a plot (the Chinese form) or a grave in a plot's corner (the
Japanese form) - but the page class is still keyed and named `grave island`, so a corner-form hamlet's hover says
"grave island" while its own feature note says the grave is "not an island". Kashikawa's review raised it twice; it was
accepted for 267 with that note standing in. The rename touches 17 files: the ink tags in `settlement/fields/features.py`,
`GraveIsland` in `interactive/classes/water_and_ways.py`, the glossary term, `place.json`, `siblings.json`,
`overlap/taxonomy.py`, `tools/placement_stages.py`, the Mizuguchi and Kashikawa manifests' `ink_classes`, and the pinned
snapshot `tests/fixtures/classes_before_189.json` (through `SINCE_189`, the renaming table the snapshot test keeps).

## OPEN 2026-09-28, OWED AT CONVERSION: a village's funerary grounds (was feature 275, withdrawn), and the headman's gate

The GM, 2026-09-28: *"we just want to make sure that [when] we make village maps scripted that we do the correct
things in the scripted generation."* So the village's own burial ground is not a feature of its own now; it is owed by
the village tier's scripted generator when that is built (migration-plan step 5), with the rest of a village's
funerary grounds. The design, already researched:
- **The GM's ruling of 2026-09-27** (0226, 530): a village has a cremation ground and a hamlet none;
  the country monk lives in the main village and serves its district; within its district the village alone keeps the
  shrine, the headsman's house and the cremation ground.
- **The cremation ground**: already drawn by the roller's village tier (`_roll_civic` -> `_roll_cremation`, feature 273):
  530's `cremation_seat` knob, the shared `edge_seat`, six jizo, the ragged off-center glyph (feature 272). The village
  generator reuses it.
- **The burial ground**: 0236's knob (in the shrine or temple yard, or a ground of its own apart;
  even odds; a hilltop shrine always apart) and 270's siting (a ground apart downstream, beyond the last house,
  within ~650 ft of the middle of the houses); sized by 160's rule in the population served (the village's own
  households plus those of its hamlets, whose dead lie in the village's ground - `hamletgen/burial.py`, feature 280 M68);
  seated through `settlement/civic_grounds/edge_seat.py`. The cremation ground's "beside_burial" form then has something
  to stand beside. **A way reaches it**: no generator connects a graveyard at any tier today, and the record says a path
  was there (religion-and-death 140: at the seventh-day festival of the dead "the graves and the paths to the graves are
  cleaned", ndl-crd-nanukabon; 190 gives the pyre "a minor funeral path"). Register the ground's edge nearest the houses as
  a way target (`plan.way_targets`, feature 287 H36 - built, with no producer left since the hamlet's own ground was
  retired) so the web lays a footpath spur to it.
- **The wayside stones** (520: one to three at each place a road or lane enters a hamlet or village; a wayside-hall knob
  at even odds; Hoshigaoka's hand edit of feature 272 has them at the south lane's entry): put `boundary_marker` stones
  (unlabeled) beside each lane where it passes `BOUNDARY_STONE_CLEAR_FT` beyond the last house. The hamlet's own stones are
  the entry under feature 280 below; one placer can serve both tiers.
Hand-rolled village maps are not edited for any of this (the GM, 2026-09-28).

**The headman's gate (269 B19, the GM's ruling of 2026-09-28).** The scripted village MUST gate the headman's house.
The GM: *"As for the headsman's gate, Yes, absolutely, we should have that. ... I don't want you to update the
hand-drawn maps with this, but I do want it recorded in the research, and I do want it to be the case that when we
begin scripting our village generation ... we should absolutely make sure that the village headsman's house is gated
if that was a headsman's right."* It was: the one headman's plot read has a nagayamon (research/questions/0030-the-headmans-house-and-the-rich-farmers-homestead-shoya-gono.html, 520;
`specs/269-research-backfill/rulings-2026-09-28.md`). Measurement: `settlement/rolling/place.py` `headman()` draws a
92 x 56 ft house and no gate on every hand-rolled village. Mechanism: nothing in the roller knows a gate. Sketch: the
village generator seats the headman's house with a nagayamon on its road face as part of the plot, reserved with the
house, so a lane arrives at the gate rather than at the wall.

**The rest of 269's village rows (outcomes.md section 3), owed at the same conversion:**
- **Tax rice (B19)**: today the tax rice is taken to be in the headman's kura; the record allows either the
  headman's kura or a village gogura among the houses. Mechanism: no storehouse placer exists at the village tier.
  Sketch: a knob `tax_store` headman_kura / gogura, the gogura seated among the houses (`gogura-kotobank` gives the
  siting).
- **The cluster's spacing (B19)**: no house more than ~650 ft from the next. Measurement: no village is scripted, so
  nothing holds it. Sketch: the village's cluster seating asks a nearest-house test per candidate from the placed
  index, and the gate checks the largest gap.
- **The headman's house size (B19)**: 92 x 56 ft is about four times a farmhouse; the record reads 2 to 2.5 times,
  about 65-75 x 40 ft, a labeled guess. Sketch: the village generator takes the record's figure as `headman()`'s default.
- **The dosojin (B20)**: the entrance stone is a guess today; the record puts a dosojin by the road at the
  village's entrance. Sketch: seat it through `edge_seat` at the road's crossing of the village edge.

## OPEN 2026-09-27, OWED AT CONVERSION: the village generator draws no shrine grove, sacred tree or basin

Feature 268 (the GM, 2026-09-27: "Add grove to map") put a grove, a roped sacred tree and a stone basin round
Hoshigaoka's shrine by hand, and the country-shrine program now says a village shrine's precinct holds its
grove, in the form its ground gives (research religion-and-death 124, 126, 129). No generator draws them: `rolling/roll.py`'s civic shrine lays the
hall, its arches at the 12 ft pitch and its well, nothing more. So converting Hoshigaoka (or any village) drops
them. Sketch: after `shrine_hall`, reserve a precinct outline from behind the shrine well to the outermost arch
(the register band of research 124 as its area), carve the clearing and the approach, then lay the WOOD in the
form of the program's knob 8, `grove form` (feature 279, research 129): read the hall's ground - at the foot of a
slope the candidates are `behind` / `behind and sides`, at the top with the approach climbing to it
`behind and sides` / `sides`, midway on an even slope all three slope forms, on a rise or flat paddy `all around` -
and roll between the candidates from the settlement's seed with equal weights; the wood's region is a smooth-noise outline about the form's base shape,
never a ruled box (the edge is its crowns' own where it meets scrub or slope; where a paddy-plain wood meets its
fields, its foot rolls the program's second grove knob - `field line` along the fields' straight edge, as a
photograph shows, or `ragged` - with equal weights). Fill the
region with the grove scatter the windbreak already uses (a `KeepoutGrid` of the clearing, the approach and the
well), carry the scrub into the precinct's open ground, then seat the sacred tree beside the approach and the
basin at the innermost arch, and the keeper's kitchen garden (a `gardens` entry) on the open ground nearest the
dwelling that gets its six hours (feature 283, `garden_sun`'s sun; Hoshigaoka's sheet draws it below the forecourt,
west of the approach). Measure: the region's area and canopy share, and feature 279's `STRAIGHT_RUN` on its
edge crowns (no four within 2 ft of one line), against the hand-drawn Hoshigaoka grove (form `behind and sides`, feature 279), and the `LONG_RUN` bar (no
stretch of edge 50 ft or longer within a crown's radius of one line).

## RESEARCH OWED (feature 287's woods review, 2026-09-29): did a village lane ever run between a house and its own grove?

A reviewer found copse crowns whose nearest farmhouse stood across a lane. Feature 287 keeps lanes off a household's
copse seats by reservation (woods W25), which settles the map, not the question; no research page carries it as a guess
or an absence, so `make open-questions` cannot list it. When it is searched, record the answer (or the absence) on
research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html and drop this entry.

## OPEN 2026-09-28 (269 B16): the shared byre on the commons is still rolled, one map in ten, on no evidence

`settlement/_knobs.py` `byre_form` rolls `courtyard` (the inner stable) / `yard_shed` (the outer stable) /
`detached_commons` at 0.6 / 0.3 / 0.1. The record found the beast living with its household (research/contents.json#homesteads
300), and research/questions/0048-draft-oxen-and-horses-and-their-byres-umaya.drawing.html draws the third form as "rarely, a
shed on the common ground among the houses ... a GUESS, found on no page we read". A knob is for forms the research
supports, so a form found on no page is not one to roll (`docs/research-doctrine.md`). **Measurement**: Inashiro and Sawada
roll `detached_commons` and draw it. **Sketch**: drop `detached_commons` from the knob (or weight it 0), re-roll the two
maps, retire its gate form, the `fraction` sizing the test pins and the guess on 0048's drawing page. If the GM keeps it
instead: lay the pockets during the seating rather than before it (`reserve_commons_byres` runs before the houses, so a
re-pack can leave a shed out of every household's `_BORROW_REACH`).

## DEFERRED 2026-08-27 (GM, feature 133 T60): seasonal maps - the straw rick, the hasa frames, the drained paddies

The straw rick (waraguro, built round a pole after the harvest and kept to spring - Sugiura counts
a straw SHED on 0.68 of households) and the hasa drying frames in the fields are HARVEST-SEASON
features, so the GM ruled them out of the current phase: *"the straw shed, I think we should omit if
it is something that would only appear during the harvest time. That is something that we can put
under future work where, in general, we want the ability to have seasonal maps ... Seasonal maps will
require a number of changes as well because things like rice paddies being drained and then used for
other crops in the off season are also the kind of thing that we would need to do on some maps, but
not others."* Sketch when it comes: a `season` knob on the spec (spring / summer / harvest / winter)
read by the field renderer (flooded vs drained vs winter crop), by a `farmstead_fixtures` row for the
rick (harvest and winter only, at the yard's edge) and by a hasa pass in the fields; the checks that
read `meta.farm_fixtures` already carry the declaration shape. The research is now recorded (269 B05): the
winter barley on a drained paddy and the rick on the reaped paddy or its bund (research/contents.json#fields); the GM's deferral
stands, so nothing is drawn.

## What a reader takes for the river at the tap: the width and the hue (feature 230 pass 12, 2026-09-13)

**Measured** (Sawada): the head race leaves the brook at `#6C9CBE` (128,167,191) - darker and more saturated than the
brook's own `#9CB4C8` (168,187,199) - and at 6.0 px against the brook's 7, so it is 86% of the trunk's width. At 9x the
dug ditch can read as the principal watercourse. The mouth half is done (269 B22: the race now opens out of the brook's
bank, research/contents.json#water 310, `hamletgen/water/brook.py` `open_race_mouth`); the width and the hue are what remain.
**Mechanism**: both widths are the water-width ladder's own figures, drawn by RANK rather than discharge, and the hues
are the supply/brook pair every map uses; changing either for this junction trades a junction-scale misread for a
map-scale one. **Sketch**: judge the new mouth at 9x in a settlement-review first; only if the race still reads as the
river, taper its first ~30 ft from the brook's hue to its own.

## Two ways that meet where the material changes (feature 230 pass 12, 2026-09-13)

**Measured** (Kuwabata, the polder ring): at the SE corner the e_toe pond canal ends at (2699.2, 2186.1) with a rounded
cap at its 3.0 ft tail width while the drain trunk starts at (2702.2, 2185.6) at 5.0 - centerlines 2.5 ft apart, widths
2 ft apart, and since feature 230 in two different inks. The SW corner is the same joint. The strokes overlap, so there
is no gap; what a reader sees at 7x is a blue cap stuck on the end of a wider gray pipe. Re-measured 2026-10-07: three
such joints on Kuwabata, a 5.0 ft stroke meeting a 3.0-3.4 ft one with ends 3.0 px apart.

**Sketch**: end the toe ON the drain's centerline rather than 3 ft short and 2.5 ft off, or taper the drain's head to
the toe's width where they meet, the way the feeder/lateral junctions already read. Both are changes to the polder ring
builder's corner, which every polder map draws.

## OWED AT CONVERSION and knob candidates (feature 280, the modern-only sweep, 2026-09-29)

The GM's rule of 2026-09-28: anything attested only in modern times is eliminated. The scripted hamlets were brought into
line in feature 280 (`specs/280-modern-only-sweep/outcomes.md`, one row per item); what is left is open here.

- **Wayside stones: no scripted hamlet draws them yet.** The record (0226, the row retitled "Wayside
  stones"; 520 dates a paired dosojin set at a settlement's entrance to 1695, Ueda) supports stones at a hamlet's
  entrance and at its crossings. Sketch: a placer that seats one to three stones where the connector leaves the web
  and at the busiest crossing, as `farm_fixtures[kind=wayside_stone]` with a class and a caption group.
- **The frozen hamlets' modern-only forms, by map** (never retrofitted - fixed by CONVERSION, `migration-plan.md`):
  Akagahara, Ikegami, Moritono, Tanada, Yatsuda - M34 (the reed edge grounded on a modern survey); Enokida - M54 (the
  110 ft polder cell; three mu is 190 ft), M57 (a sluice per dike pond), M58 (the 0.80 water share; 0.62 at the 23 ft
  inset), M34; Honda - M56 (a pond grid other than the mosaic), M58, M34; Shimizu - M34.
- **The frozen villages' owed forms**: Hoshigaoka - M12 (the pond sized by command area), M65 and M81 (the sanctuary fence),
  M66 (the swept collars), M68 (a hamlet's own burial ground),
  M70 (the roofed pyre ground, platform and hut), M71 (six jizo at a cremation ground alone), M80 (the basin's roof,
  drawn plain, its roof a guess); Kikuta - M56, M58. (M50, M52, M53 and M64 were kept by the GM on 2026-09-29.)
- **M13, the homestead grove**: no pool hamlet draws one; `_find_grove_arms` (the arms-only L) serves the legacy maps
  only. Owed: the grove's premodern size at conversion, or the arms retired with the last legacy map.
- **M38, a knob candidate**: the bare dike-pond bank is attested (turfed or trodden), and so is a bank planted sparse
  with mulberry. Sketch: roll `bank_form` per settlement in `consts.POLDER_FABRIC`, the mulberry rows thinned on the
  second form.
- **M93, a knob candidate**: the communal windbreak is premodern; a ring around the settlement and a belt on the
  windward side alone are both read. Sketch: roll `windbreak_form` (ring / windward) in `SitePlan` and let the belt
  placer take an arc.

## Found by feature 280's settlement-reviews (2026-09-29), measured and not yet fixed

- **The privy's sun-side share is under the ruled 0.727 on every scripted map** - re-measured 2026-10-07 (bearing 112.5-202.5
  from the nearest house): Inashiro 6 of 13, Kashikawa 4 of 17, Kuwabata 9 of 14, Mizuguchi 5 of 11, Sawada 7 of 17; the
  shortfall predates feature 280. Sketch: record the realized share in `meta` beside the target and walk the sector's
  bearings before its radii.
- **Sawada's entrance board stands inside the last junction** on the connector (re-measured 2026-10-07: the board 36 ft
  along it, a join at 50 ft; Inashiro, where the 280 review found it, is now clear): a household joins beyond it and passes
  within sight of the board, not by its face. Sketch: seat the entrance board at or beyond the outermost junction.
- **A dike pond's water is its parcel shrunk toward its center, not offset inward** (`landuse.py`, `s_w = 1 - DIKEPOND_WATER_INSET /
  apo`; `features.py` `_rounded_pond` the same): measured on Kuwabata's 29 ponds (settlement-review, 2026-09-29) the bank runs
  7-35 ft (p50 18.5) round a 23 ft average, thin on a long pond's sides and fat at its ends, and the four mulberry rows crowd the
  thin sides. Sketch: offset the parcel inward by the inset (a polygon buffer) for the water and each row loop, and re-measure
  the share.
- **A bath room beside the main door is never drawn**: the work yard covers the front wall on every scripted house, so a hamlet
  whose seat is `main_door` (Kuwabata, Sawada) draws its bath rooms at the next seat, and `meta.bath_seats_drawn` says so
  (re-measured 2026-10-07: Kuwabata `floored_rooms` 2 and `stable_end` 3, Sawada `stable_end` 5, none at the door).
  Sketch: let the bath lap the yard's corner under the eaves beside the door - the yard's keep-out is a guess, the seat is not.
- **Some houses walk several times the straight distance to the way out** (the 280 round-5 review measured Mizuguchi's two east
  houses at about four times; re-measured 2026-10-07 on an approximate lane graph - ends within 8 px joined, each house tied
  to its nearest lane vertex - Mizuguchi's worst is now 1.46, Kuwabata's 3.69 (981 ft for 266) and Inashiro's 2.81 (550 for
  196)). Sketch: re-measure on the engine's own way graph first; if it holds, a detour test in `ways/sweeps.py` re-routes a
  way whose walk exceeds a ratio of its chord.

## Found by feature 291's settlement-reviews (2026-09-30), measured and left

- **A far-row farm's grove and its holding strip do not meet** (Kashikawa, nitpick F1 of the passing round). The grove is
  square to the page (the house faces south) and the strip square to the street (-59 degrees), so a wedge of open scrub
  26-56 ft wide at its nearest lies between them on all 11 far farms; at fit zoom the holdings read as one field block
  behind the row rather than as the back of each lot. No norm sets a gap (homesteads/157: "house lot, then field").
  Sketch: start the strip at the lot's back edge as drawn (the grove band's outer edge along the normal), or turn the
  farm's frame to the street on a street laid first - the latter a question for the record first (does a planned row's
  house face its street or the south?).
- **A carried-on spur's end is written at full float precision** (Sawada, nitpick of the passing round; re-measured
  2026-10-07: 112 unrounded lane points on Kashikawa, 100 on Mizuguchi, so possibly wider than `carry_on` alone):
  `ways/bund.carry_on` draws `[q, *step]` unrounded where every other lane point is rounded to one decimal. Sketch: round
  the step's points in `carry_on` as `commit_lane` does. An engine change, so it waits for the next feature that re-rolls
  the pool rather than re-keying a reviewed one.

## OPEN 2026-09-30 (feature 287): a tree run crossing water more than ~18 deg off square is refused, not straightened

`hamletgen/ways/tree.py:rejoined` pads a run 4 ft (`REJOIN_PAD_FT`) either side of a water crossing before the
crossing is squared, which leaves two elbows of about 70 deg some 21 ft apart on any run crossing more than about 18 deg
off square; the lane law's `bends` then refuses it. On rolled maps the seating's `tree.admits` refuses such corridors
before any is drawn, so nothing ships kinked (0 `bends` over the pool and cohort 1-20) - but the seating may be turning
down seats a straighter rejoin would keep. Sketch: size the pad from the crossing angle (the squared leg's own length),
or square the crossing before rejoining; measure seats offered and refused on the cohort before and after. Moves maps.

## OPEN 2026-09-30 (feature 293, settlement-review of Kuwabata, round 2): the notes census does not count the storehouse annexes

`make notes-census` derives each map's fixture counts from its manifest but leaves out `farm_sheds`, so a map's storehouse
count lives only in hand-typed dated entries - the kind of line that went stale on Kuwabata (round 1, F1). Sketch: one
`storehouses: **n** of **m** farmhouses` line in the census block, read from `farm_sheds` and the plain houses, beside the
fixture line.

## OPEN 2026-09-30 (feature 293 on 291): the connector may leave through the belt's windward corner

**Measured**: the 293 review found Inashiro's connector leaving through the windbreak's north-west apex, about 13 degrees
off the north-west wind. Re-measured 2026-10-07: Inashiro's now leaves south-west, but Kuwabata's runs through the belt -
27 belt clumps within 40 px of its connector, centered 141 degrees from the cluster (about north-west).
**Mechanism**: the connector's dry-exit search (`ways/track.py`, `connector_through`, `dry_exit.py`) scores bearings by dry,
clear ground and has no preference for the belt's open side. research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html records the lane's crossing as a GUESS and the old entrances found as standing on the grove's open side (Tonami;
the Huizhou water mouths). **Sketch**: among the dry bearings the sweep admits, prefer the one that leaves through the
belt's lee or flank arc (`plan.windward`), and fall back to the windward arc only where no other is dry - asked of the
whole cohort, since it moves every map whose connector currently leaves windward.
