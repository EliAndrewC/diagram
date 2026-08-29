# Homesteads: the research behind the farmhouse, yard, garden and grove rules

*The research behind the rules in [`../settlements/homesteads.md`](../settlements/homesteads.md). Findings, anchors and disclosed departures live here so the rule file stays operational; this file is where citations and deeper historical context get added as they accumulate.*

**Load this file when:** you are changing a homestead rule, a size or a prevalence - or you want the historical basis before overriding one.

Every entry: what the research found, the decision it drove, and any deliberate departure from literal reality. Anchors are stable - rules link to them by `#slug`.

---

## Homestead groves (yashikirin) - the real scale and prevalence

**Grounds:** `groves_on_windward_side`, `grove_prevalence`, the size-adaptive L-belt

**Evidence:** attested

**Sources:** `kashima-kainyo-1987` (READ 2026-08-28 via Tonami City's archive page, which quotes the 1987 survey's figures verbatim - 1,542 trees over 46 households, 48% sugi; the pointer was summary-only from 2026-07 until the GM asked whether it was hallucinated); ja.wikipedia 屋敷林

## How big was the work yard, and how did the sizes spread? (researched 2026-08-28, feature 134 T49)

**Grounds:** `homestead_parts.YARD_MEDIAN_TSUBO` / `YARD_SIGMA_LN` / `YARD_HOUSE_BETA` / `YARD_MIN_TSUBO` / `YARD_MEDIAN_TSUBO_DRYFIELD`, `_yard_area_ft2`; the yard rect `rolling/bundle.py` reserves

**Evidence:** attested (the size band and the shape), interpolated (the wet-rice median, derived from the crop)

**Sources:** [`kitamoto-mushiro-niwa`](SOURCES.md#kitamoto-mushiro-niwa), [`kamikanai-1771-houses`](SOURCES.md#kamikanai-1771-houses), [`kikoba-kenchi`](SOURCES.md#kikoba-kenchi), [`santome-shinden-allotment`](SOURCES.md#santome-shinden-allotment), [`kodaira-niwa`](SOURCES.md#kodaira-niwa), [`yonekura-mushiro`](SOURCES.md#yonekura-mushiro), [`tobunken-mushiro`](SOURCES.md#tobunken-mushiro), [`irri-drying-floor`](SOURCES.md#irri-drying-floor), [`ndl-kokumori`](SOURCES.md#ndl-kokumori)

The GM, on the map's own modal: *"I see the threshing yard size is listed as a rendering convention.
How large WERE these yards?"* The doc had carried ~100-300 sq m as the yard - which turns out to be
the **homestead LOT** figure (Akishima city history: farms need a wide front yard, so lots run
100-300 tsubo = 330-992 sq m), a real number attached to the wrong thing.

**The size, as households themselves stated it.** Kitamoto (Saitama) city history, folk volume:
「収穫期には庭一面にムシロが敷かれ、しばしば庭の広さはこのムシロの枚数で表現された。麦の耕作面積と関係
していて、普通四〇〜六〇枚、中には百枚を越す家もあった。ちなみに、ムシロ二枚が一坪にあたる。」 - the yard
was measured in straw mats, 40-60 usually and past 100 for a few, two mats to the tsubo: **20-30
tsubo (66-99 sq m) ordinarily, past 50 tsubo (165 sq m) at the top**, and explicitly sized by the
household's cropped acreage. Two independent lines agree: an Okayama museum records ~50 mats per
farm, and the measured mat is 90 x 180 cm, so ~80 sq m; a directly measured yard at Kodaira is 70
tsubo (231 sq m) - a large Musashino holding, the upper end. No survey found tabulates yards as
areas; these are the readable figures.

**But Kitamoto is a BARLEY district, and this generator draws wet rice.** Its yard is sized by the
mugi crop, which the household spreads whole. Rice is field-dried on *hazakake* racks for 10-14
days before it reaches the yard and is threshed in batches over days, so a paddy household needs
less standing floor. Deriving it from the crop instead - 1.3 koku/tan (中田 石盛) -> 247 kg momi at a
79% hulling yield -> mats at IRRI's 2.5 cm spread, batched - gives **55-100 sq m for a full cho and
35-65 for five tan**. The generator therefore centers a rice hamlet's yards at **18 tsubo (59.5 sq
m)** and keeps Kitamoto's 25 tsubo as the dry-field figure (`yard_sizes="dryfield"`), for the barley
village no map draws yet. The GM ruled between the two readings on 2026-08-28: *"I agree with option
two"* - the sourced SHAPE everywhere, the sourced SCALE appropriate to what the household dries.

**The spread is lognormal, and it is right-skewed.** No survey gives a histogram of yards, so the
shape comes from what the cadastres do tabulate, and every one is right-skewed: Kamikanai (1771)
gives a complete main-house histogram whose 31 commoner houses fit a lognormal of median 22.5 tsubo
and **sigma_ln 0.46**, with the headman detached at 3.1x; Kikoba's Genroku 検地帳 puts homestead lots
at 15-100 bu about a mode of 30, great holders at 2x the ordinary class. Kitamoto's own
band-and-tail implies **sigma 0.35-0.45** - that convergence is what the drawn sigma of 0.40 rests
on. A floor exists but is not zero: early registers carry a no-homestead class (無屋敷登録人), but by
Genroku *"田畑を保有しない百姓も含め全百姓が屋敷を持つようになり"* - the landless simply occupy the small
end, so the roll is floored at 8 tsubo rather than allowed to vanish.

**The yard follows the household, but not proportionally.** Kamikanai measures the coupling as
ADDITIVE - 「持高が5石ほど増加すれば坪数が10坪ほど増加する」 - so a 20x holder does not get a 20x yard,
even though holdings inside one village span 5 sho to 355 koku. The generator gives the yard the
household's own deviation in log space, amplified by `YARD_HOUSE_BETA` and then perturbed by an
independent positional draw: a large household is overwhelmingly likely to have a large yard, a
mismatch is possible and rare - the GM's own reading of what the record implies.

**One attested form is NOT skewed, and is a knob.** A planned *shinden* colony issued every settler
an identical homestead - Santome 1696, *"屋敷の規模はまったくの均等配分"* - so `yard_sizes="allotted"`
draws uniform yards. Principle XII's ladder: two attested forms become a per-settlement knob.

**What this changed on the map.** Yards were a fixed fraction of the house (~0.8 x 0.92 of its
footprint, jittered down), which produced a narrow 50-92 sq m band with no relation to the
household beyond the house's own size. They are now rolled per household from the distribution
above, which is an ENGINE change: the yard is part of the homestead bundle the placer reserves, so
every hamlet that dries rice re-solves its farmstead spacing (GM 2026-08-28: *"I completely
understand that"*).

## The threshing yard's sun, and how far a farmhouse shades

**Evidence:** reconstruction (derived from geometry)

**Sources:** derived - solar geometry at 38N for the 10th month, and the minka's 46 x 28 ft footprint; the thatched-roof pitch (45 degrees or steeper) and the 6-7 m ridge of surviving farmhouses were not cited when written - leftover (ja.wikipedia 茅葺 / 民家) `kayabuki-jawiki` (READ: the steep pitch as a material requirement; the 45-degree figure and the 6-7 m ridge not on the pages read)

**Grounds:** the sun-corridor keep-out in the nucleated bundle placer; `yards_unshaded_by_neighbors`

*What prompted it (GM 2026-08-13):* "Would threshing fields be directly to the north of another
house? Or would the shadow from the farmhouse directly to the south block too much light?"

*The house's height, DERIVED rather than assumed.* A thatched (*kayabuki*) roof has to be pitched
**45 degrees or steeper** - that is what the material demands, and it is why a minka carries such a
large dark loft. Our minka is 46 x 28 ft, so with the ridge along the long axis the roof rises about
**14 ft** from eaves to ridge; on a ~7 ft eaves wall that puts the ridge at roughly **20-22 ft**,
which agrees with surviving farmhouses (~6-7 m).

*The shadow, computed for the season that matters.* Threshing and drying are 9th-10th month work.
At 38N (mid-empire on the weather skill's east-coast analog) in the 10th month, a 20 ft ridge casts:

| solar time | sun elevation | shadow |
|---|---|---|
| noon | 43 deg | **21 ft** |
| 10:00 / 14:00 | 35 deg | 28 ft |
| 9:00 / 15:00 | 27 deg | **39 ft** |
| 8:00 / 16:00 | 17 deg | 65 ft |

*The decision:* a yard needs **39 ft of clear ground to its south** - the 9-to-3 window, which is
the drying day that matters. Inside ~21 ft the yard is shaded even at noon. The rule is a keep-out
corridor south of every threshing yard, and a neighboring FARMHOUSE may not stand in it.

*Why this was missed for so long, which is the useful part.* The engine already reasoned exactly
this way about GROVES - `yards_unshaded_by_groves` keeps a strip south of each yard clear, with the
comment "a neighbor's grove there would shade it" - and simply never applied it to houses, which
are taller than a grove clump and shade further. A rule stated for one obstacle and not for the
obvious other is the same shape as the way-list defects: the check could not see the case, so it
looked like a passing check.

*And the row pitch was already right.* `BUNDLE_PITCH_FT` is 92 ft, while house depth (28) + yard
depth (~26) + 39 ft of sun comes to ~93. The spacing reserved the room; the packer just never
aligned rows, so a neighbor dropped into the gap the pitch had set aside. Measured across the pool
before the fix: a neighbor's wall commonly stood **2-8 ft** south of a yard's edge, and on the
dense nucleated maps that was most yards (Ueda 45 of 85 shaded at noon, Hoshigaoka 31 of 70, Ubame
21 of 36). The provincial cities were clear (0-1 each) because their farm belt is loose.

*The departure we take knowingly:* the corridor is measured on the yard's own cross-slope span, as a
rectangle, not as a true solar wedge that swings through the day; and real *yashiki* lots also
resolved this by STAGGERING east-west rather than by spacing rows, which the placer is free to do
since the corridor only forbids the shadow, not the neighbor.

*Sources:* the 45-degree thatch pitch from the *kayabuki* literature (a steep pitch is required of
thatch, hence the large loft); solar elevations computed for 38N at the 10th-month declination;
minka ridge heights cross-checked against surviving farmhouses.

- *Historical scale - the real numbers (research grounding, for calibrating the glyph).* A homestead grove is a substantial STAND, not a few trees. The best hard data is a 1987 survey of Kashima in the Tonami plain (the classic *kainyo* dispersed-farmstead country, 46 households): **~33 trees of trunk diameter >= 10 cm per homestead**, of which cedar (*sugi*) was ~48% (**~16 cedars per house**), the rest spread over ~83 other species; **~6 species per homestead** (range 1-14); a large/notable homestead ran **200+ trees across 31 species**. That count is trunks >= 10 cm ONLY - it EXCLUDES the bamboo stand (hundreds of culms), saplings, and the trimmed hedge layer - so the honest figure for a typical grove is **~30-40 mature trees + a bamboo grove + understory**, and a big one **100-200+**. The grove canopy footprint is therefore the LARGEST homestead appurtenance - **bigger than the farmhouse**, and far bigger than the garden or threshing yard - wrapping the N/W as a belt several trees deep. The map need not draw every tree (houses/yards are already oversized symbols), but per Principle "relative sizes roughly honest" the grove glyph must read at the RIGHT relative scale: clearly the dominant homestead feature, a dense stand suggesting dozens of trees - not a garden-sized clump of 5-10. *(Cross-check on the windward rule: Okinawa's homestead groves sit on the E/N sides, because the islands' damaging wind is the typhoon/NE monsoon, not the mainland NW - same logic, different geography, which is exactly why `windward` is a per-map knob.)*

## The garden's sun, and how far the windbreak shades (researched 2026-08-25, feature 133 T10)

**Evidence:** reconstruction (derived), attested (the belt's side - SUMMARY-ONLY)

**Sources:** derived from the threshing-yard entry above; the bamboo-strip aspect is SUMMARY-ONLY (flagged under T48; ja.wikipedia 屋敷林 puts Tonami's bamboo on the south) - see the entry's own flag

**Grounds:** the garden half of the sun corridor (`_sun_corridor_ok` / `_gardens_sun_ok`,
`gardens_unshaded_by_neighbors`); the belt's afternoon lane (`west_sun_lane`, `WEST_SUN_FT`,
`village_trees_unshade_from_west`).

*What prompted it (GM 2026-08-25):* "there is not enough space for sunlight to hit the gardens and
thrashing yards ... The Windbreak Forest ... is so close to the gardens ... that I do not believe
that those gardens would get sufficient sunlight." Measured on the reference hamlet before the
fix: every threshing yard cleared the 39 ft corridor (nearest neighbor 42 ft), but **7 of 16
garden beds had a neighbor's wall 4-38 ft to their south**, and the belt's nearest clump stood
**8-43 ft west** of three beds and two yards. The yard rule had been stated for the yard and never
for the bed - the same one-obstacle shape that hid the yard rule itself for months.

*The garden takes the yard's corridor - one number, not two.* A dooryard garden's binding season
is the shoulder month too: autumn greens and daikon are in the ground under the same 28 deg 9am
sun that dries the rice, so a minka's ~20 ft ridge shades a bed 39 ft off exactly as it shades a
yard. The growing-season figure is shorter (a 60-70 deg noon sun in the 4th-7th months throws
7-12 ft), so the shoulder binds, as it does for the yard. Rule: **39 ft of clear ground south of
every bed**, both directions at placement, gated by `gardens_unshaded_by_neighbors` on scripted
maps. The bed is side-dependent (SE/SW/E/W), so its half of the test lives in `_bundle_side_fits`
and refuses one SIDE rather than the whole seat - a bed the SE would put in a shadow moves to the
other flank. Cost on Inashiro: none visible - all 15 households seat, beds now 41-242 ft clear.

*The belt's height, from the record.* Searched: igune (Sendai/Osaki), kainyo (Tonami),
tsuijimatsu (Izumo), Musashino yashikirin, Okinawa fukugi, Chinese fengshui woods. Found: the
Sendai igune planting list classes sugi/keyaki/kuromatsu/hinoki as "tall trees" at **>= 15 m**,
sub-canopy ~10 m, shrubs ~3 m; Tohoku sources put a mature skeleton at **20 m+**; the one MEASURED
igune (Osaki, drone survey, 2022) is **"about 10 m"**, tall sugi on the west with a lower layer to
8 m; Tonami's kainyo "over 10 m", sugi 2-3 rows thick on the S and W; Izumo's tsuijimatsu pines are
**clipped to 8-12 m** every 4-5 years, the one attested topping practice; Okinawa fukugi belts
average 7-10 m. Kainyo/igune are limb-pruned (*edauchi*), never height-capped. So the attested
band is **~10 m for a working belt, 15-25 m for an untended mature stand**.

*Where the plots stood, from the record.* The Tonami model homestead (Research Institute, 1996):
house faces E, away from the SW wind; the front (E) yard is the work yard, "securing adequate open
space" with only fruit trees and a persimmon in the yard center; S and W carry 2-3 rows of sugi;
the N/W bamboo strip is "shady ... always damp" and given to the kitchen drain and service sheds. (SUMMARY-ONLY, flagged under T48: no fetched source carries this sentence, and ja.wikipedia "屋敷林" puts Tonami's bamboo on the SOUTH side with the storehouses - see research/vegetation.md.)
Tohoku: the S-facing open ground in front is the drying yard. So the record's answer is that the
HOUSE BODY was the spacer - plots on the sunlit lee side, the belt behind - and it holds **no
measured plot-to-treeline distance**. For a nucleated village's communal belt the record is
silent altogether. Hence the number is DERIVED, as the 39 ft was.

*The shadow, computed for the season that matters.* At 38N in the shoulder month the 3pm sun
stands 28 deg high at azimuth ~232, so a belt throws 1.9 x its height to the NORTHEAST - a
10 m (33 ft) belt ~63 ft, of which **~50 ft reaches eastward**; a 15 m belt ~95 ft / ~75 ft.
In the 7th month the same hour gives ~35 ft / ~50 ft. The shoulder binds.

*The decision:* **50 ft of clear ground west and southwest of every yard and bed** (the 3pm
shadow starts from the southwest, so the keep-out runs from a plot's north edge to 50 ft below its
south edge), enforced when the belt is planted (`village_grove` refuses the clump and re-seats it
deeper; `belt_polygon` moves its near face out by the lane where the wind puts the belt west), and
gated by `village_trees_unshade_from_west`. Windbreak-role groves only: the copse is the dooryard's
own persimmon and bamboo, which the record puts IN the yard.

*75 ft was tried first and declined - a ruling, not a taste.* 75 is the same geometry at 15 m,
the class floor of an untended stand. At 75 the belt must stand so far off the west rank that it
falls outside the frame the hard features set, and the frame does not open for the belt (GM
2026-07-20, `settlements/presentation.md`: the communal windbreak clips at the view edge, gated by
`crop_hugs_content`). Measured on Inashiro: the belt fell from 131 clumps to 38 and
`village_windbreak_is_continuous` went red. At 50 it stands whole (81 clumps, continuous) inside
today's frame. **What is accepted**: a belt kept at working height, and a belt that is mostly OFF THE PAGE on
the west - measured by `settlement-review` on the shipped render: visible canopy 0-40 px per band,
median ~15 px, blank for ~90 ft (y 700-790, where the connector leaves) and 1-4 px for ~75 ft
(y 1075-1150); 85% of the 81 clumps stand outside the view. `village_windbreak_is_continuous` is
green because it reads geometry, not the page. The arithmetic says this is not tunable away: the
frame stops 48 px west of the westernmost hard feature and the lane keeps clump centers 66 px
west of the same plot, so on any row with a plot the belt's near canopy shows at most ~7 px.
**The two rulings conflicted** - a belt that stands off the plots (2026-08-25) and a frame that
does not open for the belt (2026-07-20) - and the GM reconciled them the next day: *"treat the
innermost edge of the windbreak forest as being something that is preserved"*. The belt's inner
FACE now sets the frame with the standard 48 px margin (`windbreak_face`, `crop_boxes`,
`settlements/presentation.md`); the belt's depth still clips. Measured after: the front row shows
whole (48 px at the face), no clump is drawn wholly off-page, per-band visible canopy 5-48 px
(the thin bands are where the connector crosses the belt's line, a form matter, not the crop). **What was priced and declined**: letting
the windbreak set the frame (reverses the 2026-07-20 ruling - the GM's to reopen, not a session's);
a lane scaled to 15 m without moving the frame (measured: the belt is dropped). **Who chose**: the
session, on the measurement, and the GM on 2026-08-26 chose to open the frame at the face rather
than shrink or raise the belt - 10 m stays as the record's measured working height.

*Departures taken knowingly:* the lane is a square, not a solar wedge that swings through the
afternoon (the yard's south corridor takes the same shortcut); the 12 px in `belt_polygon`'s
stand-off is an average plot overhang, and the clump filter is the guarantee behind it.

*Sources:* Sendai City igune species list (city.sendai.jp); Minami/Yonezawa/Okaze 2022, Osaki
igune drone survey (J-STAGE, LES 38(2)); Tonami Scattered-Village Research Institute 1996 model
homestead; Izumo tsuijimatsu (Kanto Gakuin column); ISA Arboriculture & Urban Forestry 37(1) on
fukugi; solar elevations computed for 38N.

## May a byre stand beside a wellhead? (researched 2026-08-18)

**Evidence:** attested (the stable wing), researched (the in-house well - not re-found)

**Sources:** `magariya-jawiki` (READ 2026-08-28: the stable projecting on the south face, joined to the house and warmed from its hearth); the well inside the doma or a rear projection was NOT found on the page - that half stays as the 2026-08-18 reading, unsourced

**Answer: yes, and the vernacular puts them far closer than our maps do. No GM ruling wanted.**

A `settlement-review` flagged a shared draft-animal byre standing 38 ft from a communal wellhead on
Kashikawa and asked for a ruling. Under the constitution's Principle XII rule that research precedes
a ruling, this was searched first, and the record is not ambiguous.

**Japan (the closest analogue, and the strongest signal).** In the *magariya* L-plan farmhouse the
draft animal lives **under the house's own roof**: the stable wing (*umaya*) meets the dwelling
(*omoya*) at right angles and extends off its SOUTH face, deliberately taking the best sunlight,
"indicating how valuable horses were". And the well (*ido*), where a house had one, sat "in the rear
corner of the earthen-floored *doma* or in a rear projection room" - i.e. **inside the same
building**. A household's horse and a household's well were therefore separated by the width of a
farmhouse, on the order of 20-40 ft, as a matter of course. This is also why our own doctrine draws
no European multi-stall barn (see the draft-animals-live-in-the-house rule in
[`../settlements/homesteads.md`](../settlements/homesteads.md)).

**China (the guiding star).** Vernacular villages **co-located the animal facilities with the
latrine** - cattle sheds, chicken houses and pigsties grouped with the privy - because both ends of
that group feed the same manure economy that kept the soil fertile for four thousand years
("treasure nightsoil as if it were gold"). That is a positive siting rule about the muck cluster,
and it is worth knowing; what it is NOT is a rule holding livestock away from drinking water. No
separation doctrine turned up in the geomantic or vernacular-layout material.

**Elsewhere, corroborating.** The public watering trough at a village or town water point - "a
trough, preferably with a well and a pump" - is a widespread and well-documented arrangement. Where
communities invested in water infrastructure at all, watering the beasts AT it was the norm rather
than a transgression.

**What is genuinely true and worth not over-reading:** livestock near a shallow, unsealed well IS a
real contamination vector, and modern rural-water studies in China measure exactly that. But that is
a public-health finding about the *consequences*, not evidence that the builders sited to avoid it.
A generator that separated byre from well would be drawing a modern sanitary intuition, not a
Rokugani village.

**The decision, therefore:** the beasts are watered at the well, and a byre near one is correct.
Nothing is changed in the placer; `_fits` already prevents an actual overlap with the wellhead's
footprint, which is the only part that was ever a defect. Recorded so the next re-pack does not
re-open it.

## Is every farmhouse reached by a lane, and in what FORM? (researched 2026-08-18)

**Answer: access is decisive (implement it); its FORM has two supportable shapes (make it a knob).**
This one is worth reading as the worked example of the constitution's research-then-knob ladder,
because the research came back decisive on one axis and genuinely two-formed on the other.

**Decisive: a house in a nucleated cluster IS reached by a way.** The Chinese material is explicit -
"the organization of the village plan as a gridiron of narrow lanes is functionally the most
efficient form of compact settlement", and "every house in the nucleated village is accessible via
the interconnected system of narrow lanes and alleys". This is not a planner's ideal imposed after
the fact; it is what compactness is FOR. The lanes are also socially live rather than purely
circulatory - the narrow lateral ones are "colonised as semi-private space by the adjoining house",
which is why they are narrow, irregular, and sometimes barely more than the gap between two walls.
Our own doctrine already said as much in one line ("a nucleated village is threaded with lanes") but
the generator was not honoring it: a back-rank house could sit with no way touching it at all.
That is now a defect with a research basis, not a matter of taste.

**Two supportable forms for delivering that access.** Both are attested, and neither dominates:

1. **Alleys off the spine.** Narrow lateral lanes branch from the through-lane between house plots
   and run back to serve the rank behind. This is the Chinese gridiron-of-lanes form, and the one
   whose laterals get colonised as semi-private space by the houses they pass.
2. **A back lane.** A way parallel to the main street, behind the plots, serving their rear. This is
   documented as a planned-village device - "back lanes on each side of the main street which,
   together with the main street itself, provides a rectangular framework" - and it typically
   "divided the village from the main agricultural area", i.e. it doubles as the field-ward edge.
   Rear-access ground behind the housing lots is separately documented in traditional Manchu
   villages in northeast China, so this is not a purely European shape.

Note what distinguishes them: a back lane implies PLANNING (someone laid the framework out at once,
and the plots are regular), while alleys off a spine imply ACCRETION (each household cut its own way
to the road, and the result is irregular). A Rokugani hamlet can plausibly be either, so this is
exactly the axis the project wants varied between maps rather than settled once.

**Therefore:** the generator must guarantee every farmhouse is served by a way, and must choose
between the two forms per settlement via a seeded knob. Per Principle XII this is NOT a question to
put to the GM - the research decided the part that was decidable and identified the part that is
genuinely two-formed, and the two-formed part becomes variance.

**Sources:** the lane-gridiron and semi-private-lateral findings are from the nucleated-village
morphology literature; the back-lane framework from planned-village morphology (see
[`SOURCES.md`](SOURCES.md)); rear-access in Manchu villages from Ushijima, "Spatial composition and
premise arrangement of traditional Manchu village in Northeast China", *Japan Architectural Review*
(2020).

**REVISITED 2026-08-27 (feature 133 T31) - the GM asked the question the other way round.** Looking at
Inashiro: *"a bunch of random scattered lanes strewn about without much rhyme or reason ... a short
section of lane, between three farmhouses. It does not really connect to anything on either end ...
I would have expected something like a lane leading to the reference hamlet and then probably just
not even anything between the farmhouses. Is that right? Is that wrong? What does our research
show?"* The record above already answers both halves, and no new pass was needed. (1) A lane to the
hamlet and NOTHING between the farmhouses is a real form - it is the DISPERSED hamlet of the next
section (散村, each steading reached from the field paths, no village street), and it is a knob
value, not a correction. (2) For a NUCLEATED cluster, which is what Inashiro rolled, the record is
decisive the other way: "every house in the nucleated village is accessible via the INTERCONNECTED
system of narrow lanes and alleys" - the lanes are the point of compactness, and they are one
network. So the research says the FORM on Inashiro is right and the DRAWING was wrong: the web was
connected only by tolerance (every pass treated an end within 30 ft of another way as joined) and
disconnected in ink - nine lanes in six components, ends stopping 29 ft short where the fabric margin
had clipped them beside a garden fence. That is the "scattered" look. The fix is in
`hamletgen/ways.py` (`_touch_junctions`, `_clear_touch`) and the gate holds it
(`lanes_form_one_network`): a junction is where two treads MEET. Label: the interconnected web is
ACCURATE for a nucleated cluster; a lane that runs along a garden fence to reach its junction is
ACCURATE too (the plot fronts the lane; the 7 ft fabric margin is a drawing convenience, not a
finding - see `_TOUCH_GAP`).

## How does a village lane bend? (researched 2026-08-27, feature 133 T32)

**Evidence:** attested (desire lines), reconstruction (the thresholds)

**Sources:** `desire-path-enwiki`, `ninety-nine-pi-desire` (READ); `ma-2024-desire-paths` (SUMMARY-ONLY, supports nothing here - see the entry)

**Answer: like a line feet wear - as few turns as the plots allow, none of them sharp, and never
back on itself. Decisive on the principle; the thresholds are drawing conventions.**

The GM, on Inashiro after T31: *"there are at least 2 places on the map where the zig-zagging looks
unnatural. There's a place where it looks like a loop-de-loop, which isn't how a lane would look. And
then there's another place where it zig-zags just below the loop de loop for no apparent reason."*
Two lines of evidence, one from how paths form and one from how villages are laid out:

- **Desire-line research.** READ (Wikipedia "Desire path"; 99% Invisible): "as few as 15 passages
  over a site can be enough to create a distinct trail, the existence of which then attracts
  further use"; the path "usually represents the shortest or the most easily navigated route"; and
  desire paths are not necessarily straight - they follow least resistance, sidestepping slopes and
  obstacles. UNVERIFIED (the paper is paywalled and its abstract could not be fetched; the phrase
  came from a search summary of Ma, Brandt, Seipel and Ma 2024): that walkers "consciously or
  unconsciously minimize the number and severity of turns". CONTRADICTED IN SCOPE (the abstract,
  read via ideas.repec.org, T45 - and caught only on the session's spot-check of the reader's
  quote): the paper's "angle (found to be limited to a narrow range of 90-120°)" is the simulated
  agent's ANGLE OF VISION, a visual parameter of the model set against "depth of vision" - not a
  walker's turning angle. The search summary had recast a field-of-view parameter as a
  turn-minimization finding, the first record repeated it, and a reader matching words found it
  "read". So that paper supports nothing here about turns; the sentence stays as a summary-only
  claim of unknown provenance, and the rule does not lean on it. What the read sources DO support
  is enough for the rule: a worn path is the shortest
  or easiest route between two points, so a switchback within a few paces - which is neither - is
  a path nobody walks, and a path nobody walks is never worn.
- **Village morphology.** The lanes of a nucleated Japanese or Chinese village are the gaps left
  between household plots - the "gridiron of narrow lanes" of the 2026-08-18 entry - so a lane bends
  at a PLOT CORNER and runs straight between corners. A bend has a reason on the ground (a fence, a
  bed, a yard); a bend with nothing at its elbow is a drawing artifact.

**What was wrong in the generator.** Not a placement rule - an absence of one. The web is assembled
from fragments: `clear_runs` cuts 4 ft-stepped runs between the steadings, joins append links, the
touch pass appends more, trims take ends off, and no pass ever read the assembled lane as a shape.
Three artifacts, all measured on Inashiro: a 180-degree RETRACE where the touch pass linked a lane's
free end to a way that lane already ran through; a KNOT where three lanes arrived at three points a
few feet apart (a closed triangle - the GM's loop-de-loop); and a lane of 140 ft for a 49 ft chord,
folded twice inside 50 ft, where a fabric-margin clip and a touch link met.

**The rule** (`hamletgen/ways.py` `_smooth_web`, the last pass of `stage_web`; the gate's
`lanes_bend_like_paths`): string-pull every lane (a chord at the web's own margins, or at footprint
margins when it only removes jogs within 6 ft of the old line); cut a hairpin's arm when it is under
40 ft; collapse ends within 25 ft of one another onto ONE node; cut a tail that runs on past a
crossing for under 40 ft; and make each junction once. Labels: the principle ACCURATE (a worn path
minimizes its turns; a bend sits at a plot corner); 140 degrees / 50 degrees within 40 ft / 25 ft /
6 ft are DRAWING thresholds chosen at the scale of a dozen paces, not findings.

**Sources (read):** Wikipedia "Desire path" (citing Hampton and Cole 1988 for the fifteen-passage
figure); 99% Invisible, "Least Resistance: How Desire Paths Can Lead to Better Design". **Pointers,
not read (paywalled/403):** Ma, Brandt, Seipel and Ma (2024), *Environment and Planning B*
(agent-based desire paths; its abstract READ via ideas.repec.org and found to be about the
agents' angle of VISION, not turning - the turn-minimization sentence is not from it); the 2025
*Landscape and Urban Planning* energy-based desire-path paper. The plot-corner geometry is the
2026-08-18 entry's. Corrected 2026-08-27 under T44 and the T45 spot-check.

## How close does a farmhouse stand to the paddy? Up against it - but never on the bund (researched 2026-08-27, feature 133 T41)

**Evidence:** attested (the levee's role), interpolated (the 6 ft floor)

**Sources:** `pmc7538448-levee`, `paddy-field-enwiki` (READ); `irri-bund-summary` (SUMMARY-ONLY); the eave-gap figure carried over from `FARMHOUSE_EAVE_GAP_FT`, unsourced

The GM: *"One of the farmhouses in the reference hamlet appears to actually be touching the edge of
the rice paddy fields. Is this realistic? ... I do imagine that they would be pretty much right up
against the edge, but actually touching looks wrong to me."* Measured first: one house's corner
0.9 ft from the paddy outline; every other house 10-13 ft; threshing yards as close as 7 ft.

**What the record gives, and what it does not.** No source states a setback in feet - the
question is not one anyone measured - so the floor is DERIVED from three attested parts:

- **The bund (aze) is a thing, not a line.** READ (PMC 7538448, verbatim): rice paddy levees "are
  constructed and maintained to retain water in the paddies and to allow the passage of people and
  transportation of tools", and "farmers generally maintain levee grasslands by periodic mowing".
  READ (Wikipedia "Paddy field"): plots "separated by bunds approximately 10 cm in height" (a Korean
  example). SUMMARY-ONLY (the `source-reader` run of 2026-08-27, T45): the IRRI Rice Knowledge
  Bank's "How to construct bunds" - unreachable to the tool, seen in a search snippet - says
  "bunds should be constructed no wider and taller than 50 cm x 30 cm ... high enough (at least
  20 cm) to avoid overflowing"; the "15-150 cm" range was seen nowhere. READ, and pulling the other
  way: FAO's basin-irrigation manual (fao.org/4/ac180e/AC180E07.htm) gives a permanent "dry bund"
  a 25 cm minimum height (60 recommended) and a 180 cm base tapering to 60 cm - a different, heavier
  structure than a field partition. So "about 1.5 ft" is one convention among several, and the
  6 ft floor below leans on it lightly.
- **The house's roof reaches past its wall.** A thatched farmhouse's eaves overhang the wall by
  about 3 ft - UNSOURCED here: it is the figure the `FARMHOUSE_EAVE_GAP_FT` rule already spends
  between neighboring houses, carried over rather than re-read; its drip line is where the wall's
  rain lands.
- **The plot fronts the paddy.** The nucleated cluster stands on the field margin with its face to
  the water (the *背山面水* seat, research above), so "right up against the edge" is the norm the
  GM expects, and the seat band's own standoff (12 px) draws it.

**Therefore** a wall nearer than bund + path + eave stands with its roof over the levee path and its
drip line in the rice. 1.5 + ~1.5 + 3 ft is 6 ft, the floor a wall may never cross - a MINIMUM
below the 10-13 ft the placer already draws, so nothing else on the map moves. The touching house
was not a rule but a measurement error: the 14 px field set-back was held from the seat's CENTER,
so a house 28 ft deep seated 14 px off the paddy stood with its wall on the bund (the CENTER-vs-
FOOTPRINT trap `dev/placement.md` names). Now `_wall_on_the_bund` tests the four corners in both
seat paths (`settlement/houses.py` `_fits`, `settlement/rolling/fit.py` `_bundle_common_fits`),
and the gate holds it (`houses_clear_of_paddies`, same constant). Inashiro after: 7.1 ft, one house
moved 6 px, nothing else changed.

Labels: the levee's footpath role ACCURATE (read); the bund's width UNVERIFIED (search summary only);
the 6 ft floor a DERIVED threshold - and a soft one, since two of its three parts are not read;
"up against the edge" ACCURATE.

**Sources (read):** "Earthworm species and density in semi-natural grasslands on rice paddy levees
in Japanese satoyama", PMC 7538448 (levees built and kept for water retention and passage of people
and tools; mown); Wikipedia "Paddy field" (bunds ~10 cm high, Korea). **Pointers, not read (403):**
ResearchGate "Scheme of bund, terrace, and field dimensions" (the 15-150 cm width); Britannica
"Paddy". Corrected 2026-08-27 under the read-what-you-cite rule (T44): the first record cited the
unread pages as if read.

## What stood on a farmstead - the inventory, with numbers (researched 2026-08-27, feature 133 T52)

**Evidence:** attested

**Sources:** `sugiura-1973-fuzoku` (READ, all eight pages) - the one quantified source; the 37-fetch reader pass is folded into the fixtures entry below

The GM: *"What things would exist on a noticeable percentage of farmhouses that we are not currently
representing on our maps ... What, if anything, are we missing?"* A `source-reader` pass (37 fetches)
plus one paper the session read itself, page by page.

**READ - the one quantified source.** Sugiura Tadashi, "農村集落における農家の付属建物について - 宮城県宮崎町の例"
(On the ancillary buildings of farmhouses in agricultural settlements: Miyazaki-machi, Miyagi),
*Tōhoku Chiri* 25(3), 1973, pp. 145-152 (JStage tga1948/25/3/25_3_145): a July 1972 survey of all
87 households in three hamlets (Asahi, Kita-Nagasaida, Minami-Nagasaida) on the terrace south of the
Naruse river, every roofed outbuilding counted and classified by function. Averages per household:
4.38 outbuildings (4.57 for farm households) - "surprisingly many" against the Tōhoku norm of a single
main building. Table 5 gives buildings PER HOUSEHOLD by function; the B1 column is houses built
before 1944 - the traditional stock, and the one that speaks for our period:
privy outbuilding (便所) **0.87**; firewood shed (マキ小屋) **0.76**; straw shed (ワラ小屋) **0.68**; barn
(納屋) 0.58; work shed (作業場) 0.55; livestock shed (畜舎) 0.55; storehouse (くら) 0.24; compost/
manure shed (堆肥舎) 0.24; bath shed (浴室) 0.29 (all-house average); chicken coop (鶏舎) 0.16
(0.28 all houses); general storage (物置) 0.48 (all); well house (井戸小屋) 0.19 (all); pickle shed
(つけもの小屋) 0.24; hasa shed 0.13; household shrine (社) 0.03; charcoal shed 0.01. Table 6 gives what
was INSIDE the old main house instead: livestock 60.5% of B1 households, bath 52.6%, privy 31.6%.
Scope, stated: 1972, Tōhoku (snow country, 5 km from the mountains, 145 cm max snow) - a region the
author himself says is unusually many-building; the Edo hamlet this map draws is temperate lowland,
so these are the SHAPE of a farmstead's inventory and an upper band on counts, not a transplant.

**The reader's pass, on the rest** (READ unless marked): shared wells outnumbered private ones,
"井戸の掘削費用が高額で ... 共同所有の井戸が多かった" (ja.wikipedia 井戸) - the map's communal wells are the
norm; the harvest drying rack (稲架, hasa) "主に収穫後の田畑に作られることが多い" - stands IN THE FIELDS after
harvest, seasonal, some regions leaving the frame up (ja.wikipedia 稲架); the household shrine
(屋敷神) is a small stone or wood hokora in a plot corner, N/W or N/E (ja.wikipedia 屋敷神) - attested,
and Sugiura counts it at 3 per 100 households, so RARE; dosojin and jizo stand on the road and at
passes, jizo also "in the villages" (nakasendoway.com) - a village-ENTRANCE stone is summary-only;
a gate (屋敷門) is a WARRIOR house's feature (JAANUS) - not a commoner farmstead's without a source;
the magariya attached stable is a Nanbu/Tōhoku cold form - our separate byres are the temperate
reading; a headman-class compound (Chiba museum's Boso-no-Mura reconstruction) had eight buildings:
主屋・土蔵・長屋門・馬小屋・納屋・木小屋・作業小屋・井戸 - the top of the ladder, not the typical plot.
SUMMARY-ONLY: persimmon "planted in the gardens of farming families without exception" from the late
Edo (MAFF, unfetched); firewood "stacked behind a shed or along the yashiki's front wall" (Chiba
museum, mojibake on fetch); straw ricks (waraguro) built around a pole to ~2 m and kept to spring;
the goemon-buro bath as a standalone shed common among farmers; water mills RARE - a 1788 record
counts 33 waterwheels on the whole Musashino plateau; kabata a spring-fed Shiga regional form; the
communal village graveyard the Edo norm, the farmstead grave (屋敷墓) a Heian-Muromachi elite
practice; chickens kept before Meiji mainly for time-telling and fighting, so a coop is uncertain.

**What the map draws today vs the inventory.** Drawn: the house (three sizes), ONE attached kura on
some, the threshing yard, the garden, the household bamboo, the grove; hamlet: wells, byres, belt,
coppice, board, planks, pond, marsh. NOT drawn, in order of the read prevalence: the privy (0.87 -
near-universal, a 1-ken shed on the plot's back or side, and in China the muck cluster with the
animal sheds, research above); the firewood stack/shed (0.76); the straw stack (0.68, seasonal in
the yard); a second and third work building (naya 0.58 + work shed 0.55 + storage 0.48 against our
one shed on some houses); the manure/compost heap (0.24); the bath shed (0.29); the chicken coop
(0.16-0.28, uncertain for Edo); the well house over a private well (0.19); the persimmon in the
yard (summary-only, "without exception"); the hasa frames in the fields (seasonal); the hamlet
graveyard; a wayside jizo. Not owed: a gate, a mill, kabata, an in-house stable.

Labels: every number above ACCURATE for 1972 Miyagi and a GUIDE elsewhere (stated scope); the
persimmon and the firewood placement SUMMARY-ONLY; nothing here is drawn yet - this entry is the
list the GM chooses from.

**Sources (read):** Sugiura 1973 (JStage PDF, read pp. 145-152); ja.wikipedia 井戸, 稲架, 屋敷神;
nakasendoway.com "Dosojin"; Chiba Prefectural Museum, Boso-no-Mura headman farmstead page; JAANUS
"yashikimon" (via the reader). **Pointers, not read:** MAFF (persimmon); the Chiba museum housing
page (mojibake); kubota.co.jp / JA Hiroshima (waraguro); japaaan / ohgaki (goemon-buro); mizu.gr.jp
(the 1788 waterwheel count); NDL reference desk (屋敷墓); ja.wikipedia 外便所 (the fetched text was
Australian in scope).

## Does a hamlet have to be NUCLEATED at all? (researched 2026-08-23)

**Answer: no. Three forms are supportable, so the form becomes a seeded knob (Principle XII), and
the access rule above is true of exactly one of them.**

The entry above settled that a house *in a nucleated cluster* is reached by a way. It did not ask
whether a hamlet must be nucleated - the generator simply assumed it, and hardcoded it. The GM
challenged the assumption from the other end on 2026-08-23, asking whether lanes should be laid
before houses at all when in life they are trodden by the households already living there. That
question turns out to be the same question: a settlement whose lanes are pre-laid can only be one
whose houses front lanes.

### DISPERSED (散村 *sankyoson*) - decisive, and our terrain is its terrain

The Tonami Plain in Toyama is the canonical Japanese case: **over 7,000 farmhouses scattered across
roughly 220 km²** on an alluvial fan built by the Shogawa and Oyabe rivers, a pattern more than 500
years old.

**The mechanism is irrigation, and it is the mechanism our own maps model.** Farmers built their
houses *in the middle of their own cultivated fields* in order to manage water for those fields
directly. An alluvial fan drains well - which is a PROBLEM for wet paddy, not a benefit - so water
control is per-holding and unremitting, and living on your holding is how it is done. The
farmhouses scattered **naturally** rather than by any plan. Edo-period land grants to those who had
reclaimed the land then entrenched the pattern.

**Each house sits in its own grove.** The regional term for the homestead woodland is *kainyo*; it
shelters the house from winter seasonal winds and snowstorms, and from summer sun. Note this
alongside the *yashikirin* entry above - both terms are real, *kainyo* is the Tonami one for exactly
this feature, and the two describe the same thing at different regional scales.

**Why this matters to the generator**: our comb field IS an alluvial fan, and the engine already
branches on per-house versus single shelter belts (`hinterland.py`: *"A nucleated settlement shelters
behind ONE grove rather than per-house belts"*). The dispersed form's most visible signature is
therefore already implemented as the road not taken.

**Consequence for the access rule**: a dispersed hamlet has no interconnected lane network to be
reached by. The rule in the entry above is a rule about nucleated settlements and must say so.

### LINEAR (路村 / row village) - supportable, but the weakest of the three

Settlements strung along a linear feature - a road, a riverbank, a valley floor - are a standard
morphological category. The German *Reihendorf* is the best-documented type: one or two rows of
farmsteads either side of a village street, **each holding's farmland adjacent to its dwelling**,
which saves travel and transport effort. That functional argument transfers directly to a rice
hamlet strung along a track between its paddies.

**Recorded limitation, so nobody re-runs this pass expecting more**: the English-language record for
the specific term 路村 was thin, and the strongest documentation of the row form is European. The
functional logic is not culturally specific, and elongated road- and river-following forms ARE
attested in the Chinese village-morphology literature (settlements in mountainous southwest Zhejiang
"tend to expand in the direction of rivers and roads"). But this is weaker ground than the dispersed
case, and the roll weights should reflect that rather than pretending to three equally-attested
forms.

**Consequence**: linear is the one form in which the road genuinely comes first, and therefore the
one form whose houses legitimately front a pre-existing way - the connector, which is exogenous.

### What this changed in the generator

Feature 126. Ways split by PROVENANCE rather than timing: the connector and field spur predate the
settlement and are laid first; the internal skeleton is derived from the placed houses. The form is
rolled per map. The access checks state the form they apply to.

**Sources:** Tonami dispersed settlement, *kainyo* homestead woodlands, and the irrigation mechanism
from [Visit Toyama, "What is dispersed settlement?"](https://visit-toyama-japan.com/en/travel-inspiration/sankyoson)
and [Plenus Rice Library, Toyama](https://www.plenus.co.jp/kome-academy/en/kome_library/culture/culture01_toyama.html);
the row-village form from [Reihendorf](https://en.wikipedia.org/wiki/Reihendorf); river- and
road-following expansion in Chinese traditional villages from ["Spatial Morphological Characteristics
and Evolution of Traditional Villages in the Mountainous Area of Southwest Zhejiang"](https://doi.org/10.3390/ijgi12080317).


## Does a DISPERSED hamlet's outlying farm have its own well? Yes - and the question was never the GM's

**Evidence:** attested

**Sources:** `visit-toyama-sankyoson`, `mdpi-sho-fan-groundwater` (READ 2026-08-24)

**Asked** in `pool/hamlets/akagahara.notes.md` as *"a GM ruling that would generalize to every
dispersed map"*, after three east-row farms measured 501 / 622 / 741 ft from a well while
`farm_wells_within_reach` (the 500 ft doctrine) is gated to town/city scale so nothing enforced it.
**Researched 2026-08-24 instead of asked** - Principle XII puts the search pass ahead of the GM, and
this is squarely a how-did-people-actually-live question.

**The finding.** On the Tonami Plain in Toyama - the canonical Japanese dispersed settlement, ~7,000
farmhouses over ~220 km2 - farmers *"used to build their houses in the middle of their cultivated
rice fields so that they could easily manage the water for their own rice fields"*. The dispersal is
not incidental to water; water is the REASON for it. Each house also carries its own *kainyo*
homestead grove, so the farmstead is a self-contained unit by construction. The plain is an alluvial
fan, where shallow groundwater is a mixture of river water and precipitation - a high, easily-reached
water table, which is what makes a per-farmstead well cheap.

**The answer, and why it needed no ruling.** A shared well with a reach radius is a NUCLEATED
settlement's arrangement: it presupposes a center to be near. A dispersed farmstead has no center to
share with - that is what dispersed MEANS - so it carries its own water. The 500 ft reach rule is not
"unenforced at hamlet scale"; it is the wrong rule for this form.

**The consequence for the generator**: the well rule is FORM-CONDITIONAL, not scale-conditional. A
nucleated hamlet shares wells within reach; a dispersed one gives each farmstead its own. That is the
same shape as feature 126's handling of `farmhouses_reach_a_way`, which was made conditional on
`meta.settlement_form` rather than waived - and for the same reason: a rule that is true of one form
and false of another is not a rule with an exception, it is two rules.

**Not implemented here.** `settlement_form` is currently pinned to `nucleated`, so no map draws the
dispersed case today. This is recorded so that whoever unpins it implements the right rule rather
than re-deriving it or re-asking.

Sources: [Visit Toyama on sanson dispersed settlement](https://visit-toyama-japan.com/en/travel-inspiration/sankyoson),
[Sho River alluvial fan groundwater study](https://www.mdpi.com/2076-3263/11/8/352).

## The farmstead's fixtures - privy, woodpile, manure heap, bath, coop, household shrine, persimmon (researched 2026-08-27, feature 133 T53-T59)

**Evidence:** attested (existence and use), reconstruction (placement and size - GUESS where marked)

**Sources:** `kotobank-benjo`, `sinyoken-madori`, `artic-pigsty-latrine`, `boso-no-mura-kigoya`, `jawiki-koedame`, `mizumaki-goemonburo`, `cambridge-animals-china`, `qimin-yaoshu-yangji`, `pitt-zhengzhou-coop`, `zhwiki-liuchu`, `tokushima-yashikigami`, `jawiki-yashikigami`, `kameyama-yashikigami`, `toyoko-kaki`, `uekipedia-kaki` (READ); `326woods-stack` and the japaaan / note.com sentences SUMMARY-ONLY; `sugiura-1973-fuzoku` for the rates

The GM chose from the T52 inventory: *"privies are something that we want ... firewood stacks are
actually large enough to render ... Same thing with manure heaps, same thing with baths, same thing
with persimmons ... a household shrine being something which is very rare, but which is notable when
it does appear ... as for chicken coops ... go with whatever was the case in imperial China."* Three
`source-reader` passes (Sonnet; 101 fetches) on the pointers a search pass turned up; the verdicts
are quoted per claim below. Every drawn size is TRUE feet at the map's scale; the sizes are GUESSES
unless a source is named, because the record describes these things and almost never measures them.

**The privy (便所, kawaya) - READ.** Nipponica (kotobank 便所): *"農家では、小便所一つと大便所一つを、母屋から
独立した一つの建物として設けるのが普通であった"* - on a farm the urinal and the privy were ONE building
independent of the main house, and that was the norm. Where it stood (sinyoken 間取り pages, READ):
*"便所が家の納屋のあたりに見られるようになったり、その前の中心部の裏口あたりに位置したり、背戸口の方に離れたり
するなど様々"* - by the naya, at the back door, off toward the back entrance; and *"背戸口や脇便所、戸口便所
として独立した便所"* - a privy at the door (戸口便所) is a named form. Three attested seats, so the seat
is ROLLED per house (back door .60 / gate .25 / naya .15), each falling back to the others. Size
NOT-FOUND (the one sizing page is dead) - 6 x 6 ft, the one-ken module, a GUESS. Share: "普通"
reads as near-universal; Sugiura's 0.87 outbuildings + 0.32 in-house (overlapping) agree; the
per-hamlet band is 0.85-0.95. In Han China (AIC catalog, READ via the museum API): *"latrines - or
toilets - were customarily built above a pigsty and connected by pipes to a cesspool"* - the privy
and the muck were one cluster, which is why the manure heap below is seated BEYOND THE PRIVY.

**The woodpile - READ (the shed), GUESS (the stack's wall).** The Boso-no-Mura reconstructed
farmstead lists a 木小屋: *"燃料として使う、炭やたきぎなどを収めておく建物です"* (a building holding the
charcoal and firewood used as fuel) - READ; where the pile stood relative to the house NOT-FOUND
(the earlier "behind a shed or along the front wall" summary is withdrawn - the page does not say
it). Sugiura counts a firewood SHED on 0.76 of pre-1944 households; the open stack under the eaves
is the cheaper and older form and the one drawn: 10 x 3.5 ft in plan, split logs stacked head-high
- the 1.5 m height is modern stacking practice (326-woods, SUMMARY-ONLY and MODERN; the object has
not changed). Wall: the back wall or the kura's outer wall, out of the rain - a GUESS; band 0.75-0.95.

**The manure heap - READ (the practice), SUMMARY-ONLY (the place).** ja.wikipedia 肥溜め / 下肥 (READ):
night soil was fermented in *"地中に埋めた壺や、漆喰をほどこした穴"* (buried jars, plastered pits) of
*"口径1-1.5メートル程度"*, *"夏の場合1-2週間、冬の場合3-4週間"*; where on the farm the pit stood the pages do
not say - a search summary put it *"厩（馬小屋）の近くや軒下"* (near the stable, under the eaves; SUMMARY-
ONLY). Stable litter and grass composted into 厩肥 (note.com, SUMMARY-ONLY). With the Han pigsty-
privy READ above, the heap is drawn as one 8 x 6 ft mound beyond the privy (size GUESS); share
band 0.40-0.70 (Sugiura: a compost SHED on 0.24 - the open heap is commoner than its shed; GUESS).

**The bath shed - READ (use), NOT-FOUND (placement).** Mizumaki museum (READ): the goemon-buro
*"自給自足を中心とした農村で多く使われた"* - used widely in self-sufficient farm villages; that it spread
into western-Japan homes in the late Edo is SUMMARY-ONLY (japaaan, the sentence not on the fetched
page). Sugiura: a bath SHED on 0.29 of pre-1944 households and a bath INSIDE the house on 0.53 -
two forms, so only the shed share is drawn (band 0.20-0.45) and the rest bathe indoors, undrawn.
Where the shed stood NOT-FOUND: seated at the back wall or a flank (GUESS), 6 x 6 ft (GUESS).

**The chicken coop - imperial China's, READ.** *Animals through Chinese History* (Cambridge, READ):
*"it seems that farmers in most regions of China managed to keep a pig and some chickens in their
yard, along with a draft animal or two"* (late imperial; the chapter leans on 1930s survey data,
its own caveat). The Qimin Yaoshu 養雞第五十九 (wikisource, READ): *"雞棲，宜據地為籠，籠內著棧 ... 若任之
樹林，一遇風寒，大者損瘦，小者或死"* - build the roost as a ground-level enclosure with a perch inside;
left to roost in trees the birds sicken - so a COOP, not a tree. A late-Ming coop at Zhengzhou
(Pitt HAA, READ): *"square-shaped structure had six niche-like openings in the west wall, with some
eggshell fragments"* - square; no size given. The chicken is one of the 六畜 (zh.wikipedia, READ).
No source gives a household PROPORTION; the band 0.50-0.80 is a GUESS bounded by "most regions",
above Sugiura's Japan (0.16-0.28, where pre-Meiji chickens were timekeepers). 5 x 5 ft, square
after Zhengzhou, size a GUESS; seated on the flank by the yard (GUESS - "in their yard").

**The household shrine (屋敷神) - READ, and the GM chose between two attested forms.** Tokushima
prefectural library (READ): *"各家にある場合と特定の旧家にだけある場合がある"* - in some places every house
has one, in others only certain old families; ja.wikipedia 屋敷神 (READ) states the same two
patterns. Under Principle XII two forms would be a knob; the GM ruled for this map (T58): *"very
rare, but which is notable when it does appear"* - the old-families pattern, Sugiura's 0.03; band
0.03-0.08, and the count is CAPPED at the share so positional luck cannot make it common. The
every-house pattern is the DECLINED alternative, recorded here for the knob a later tier may want.
Corner: NE (鬼門) - *"屋敷の一隅、特に鬼門（北東隅）に、石や木、わら屋根の祠"* (ja.wikipedia, minka-en, READ);
NW 17 of 37 and NE 11 of 37 in a Kameyama survey (SUMMARY-ONLY - the page would not render); SW
*"屋敷の西南隅に祀られているのが普通"* in Tokushima (READ) - three corners attested, rolled NW .45 / NE
.35 / SW .20. Size: *"石造か木造の小祠"* (READ); one measured example *"幅・奥行き・高さ各40cm位の石の祠"*
(Tokushima, READ) - about 1.3 ft. DRAWN at 6 x 6 ft, the small-shed module (T62; it was 3 x 3 for T58 and the GM *"could not tell
what it even is"*) - a DEVIATION for legibility above the one measured stone, the GM's ruling: *"as
a glyph rendering convention, we could make it the same size as one of those small sheds ... but
also red and visually distinctive in some other way"* - vermilion, a ridge line and a torii standing
before the door.

**The persimmon - READ.** *"だからどこの庭先にも柿の木が植えてある"* (toyoko-housing, READ) - hence a persimmon
in every dooryard; and *"江戸時代の農学者 宮崎安貞は、家屋敷の周りに柿の木を植える事を奨励した"* - the Edo
agronomist Miyazaki Yasusada urged planting them round the homestead; *"夏は家に木陰を作り"* - it shades
the house in summer, so it stands BESIDE the house (which side, a GUESS: the flank, then a front or
back corner). The earlier MAFF "without exception" pointer is WITHDRAWN - NOT-FOUND on any MAFF
page. Height 3-20 m (uekipedia, READ); crown width NOT-FOUND - drawn 18 ft across (GUESS); band
0.80-0.95. Its fruit dots are a RENDERING convention naming the tree, not a season.

**The straw rick - NOT DRAWN (T60).** Seasonal (waraguro built after the harvest, kept to spring):
the GM deferred it with every seasonal thing to future work (`future-work/farming-communities.md`,
"Seasonal maps").

**What this built** (`hamletgen/homesteads.py::farmstead_fixtures`, `settlement/farm_fixtures.py`,
checks `farm_fixtures_attached` / `farm_fixtures_as_declared`): a per-hamlet share per kind rolled
inside the band from the map seed and declared in meta; per-house presence positional; seats in the
house's own frame with the researched first choice rolled where the record gives forms; every seat
tested against every placed footprint, lane, paddy, marsh and pond, the persimmon's crown against
the engine's canopy keep-outs. Inashiro seed 4: privy 12, woodpile 7, coop 7, manure 5, bath 3,
shrine 1, persimmon 8 on 15 houses (the first roll seated 10; 8 on the shipped roll - the review at T99 caught the stale count).

**Sources (read):** kotobank 便所 (Nipponica); sinyoken.sakura.ne.jp camadori.htm and cayomo016.htm;
Art Institute of Chicago 37716 (catalog text via api.artic.edu); Chiba Prefectural Museum,
Boso-no-Mura 木小屋; ja.wikipedia 肥溜め, 下肥, 屋敷神, 六畜 (zh); Mizumaki town museum 五右衛門風呂;
toyoko-housing (ameblo) 農家の庭先の柿; uekipedia カキ; Tokushima prefectural library bulletin 50 pp.
131-133; minka-en.com 屋敷神; satologue.com 屋敷神様; Cambridge *Animals through Chinese History*,
"Where did the animals go"; 齊民要術 卷六 養雞第五十九 (wikisource); Pitt HAA, the Zhengzhou coop.
**SUMMARY-ONLY:** japaaan 五右衛門風呂 (late-Edo spread); 326-woods (stack height, modern); note.com
厩肥; Kameyama city history 屋敷神 survey (17/37, 11/37); the stable-and-eaves pit placement.
**Withdrawn:** MAFF persimmon "without exception"; Boso-no-Mura firewood placement; 百姓伝記 on
night soil (the readable manual saying it is 農業全書, 1696). Keys in `research/SOURCES.md`.

## The outhouse faces the SUN, not away from the wind - and 72.7% of them do

**The question, and the hypothesis it killed.** A settlement-review found every privy on Sawada standing
UPWIND of its own house (11 of 12 north-east, 1 east) and proposed seating them downwind. That is the
intuitive rule, and it is wrong. The research pass sent to settle it read the one primary source we could
reach and found the opposite consideration governing.

**What the record says.** Wang & Ochiai surveyed farmhouses in Arakawa village, Shiga - a windstorm-prone
settlement, so a place where wind-conscious siting would show if it existed anywhere: *"toilets, as
important sources of fertilizer for the paddy fields in the past ... tended to be located in southeast and
south directions, with a total percentage at 72.7%, as a relatively warm temperature helped quick
fermentation of excrements."* Night soil was a crop input, not a nuisance to be blown away; the sun on
that side sped the composting.

**And the wind finding in the same paper is about something else.** It covers *"storage buildings and
retirement houses in the southwest and west directions ... thus forming wind fences to protect the open
space in front of the house entrance"* - and even there the paper frames the placement as sunlight-driven
(the front yard wants sun) with the wind-fence effect as a consequence rather than the cause. The words
*leeward*, *downwind*, *windward*, *odor* and *hygiene* do not appear in the article at all. No source, in
English or Japanese, was found stating any general wind rule for *koedame* or *benjo* siting.

**The rule this produces.** `PRIVY_SUNNY_SHARE = 0.727` in `hamletgen/homesteads.py` - the GM's ruling
(2026-08-29) was to use the figure literally rather than round it. The three attested seats (back door,
戸口便所 at the gate, beside the *naya*) keep their own weights as the tiebreak WITHIN each group, so a
homestead that cannot put a privy to the southeast still seats it where the record says privies go.

**How the seat is found, and a wrong turn worth keeping.** The sun side is SEARCHED - bearings across
southeast to south, radii stepping out from the house wall, nearest first, taking the first spot clear of
the keep-outs. The first implementation instead offered the sector a handful of hand-picked offsets, they
landed on the work yard or a garden, the placer fell through to the old seat, and the realized share stuck
at 43.8%. I read that plateau as the sun side being FULL and wrote exactly that here.

The GM asked the question that broke it: the real farmsteads this 72.7% comes from had threshing yards
too, so why can ours not do what they did? Measured in answer, on Sawada: every one of the 19 houses has
free sun-side ground - 49 to 151 clear spots each, the nearest 24-32 ft out, the same radius the privy
already used on its north-east side. **The yard blocks a slice of a 90-degree arc, not the side.** The
plateau was evidence about the offsets, not about the ground, and the physical-sounding explanation was
wrong. Searching the sector took the realized share to **66.2%**.

**How far out, and why the realized share is NOT tuned to the target.** The source gives a DIRECTION and
no distance, and the three attested seats are all against the house - so the radius is ours to choose, and
choosing it to hit 72.7% would be fitting the map to the statistic rather than to the place. Measured, at
three radii, over the five scripted maps:

| sun-side radius | privies seated | SE-to-S | nearer a NEIGHBOUR's house | standing beyond 45 ft |
|---|---|---|---|---|
| 48 ft | 50 | **46.0%** | **3** | 11 |
| 58 ft | 65 | 73.8% | 8 | 43 |
| 66 ft | 65 | 76.9% | 8 | 46 |

**48 ft is chosen**, and it is the one that does not hit the number. Past it the privy walks out beyond
its own work yard and, in a cluster where the next farmhouse is 50 ft away, out of its own homestead: at
72 ft an acceptance review measured 15 of 86 privies and manure pits nearer ANOTHER house than the one
they serve, against 0 of 52 before this feature - a legibility defect no check can see, because nothing
tests which farmstead a fixture belongs to. A reader attributes a fixture to the nearest house whatever
the record says.

So the realized share is **46%** against a 72.7% rule, and the gap is the work yard: the near sun side is
the threshing floor, and a privy may not stand on it. Closing it honestly means reserving the sun seat
BEFORE the yard and gardens are placed - a stage reorder, recorded and not yet attempted - not widening
the radius until the number comes out right.

**Sources:** `wang-ochiai-2022`.

