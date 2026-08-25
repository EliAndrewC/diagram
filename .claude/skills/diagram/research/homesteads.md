# Homesteads: the research behind the farmhouse, yard, garden and grove rules

*The research behind the rules in [`../settlements/homesteads.md`](../settlements/homesteads.md). Findings, anchors and disclosed departures live here so the rule file stays operational; this file is where citations and deeper historical context get added as they accumulate.*

**Load this file when:** you are changing a homestead rule, a size or a prevalence - or you want the historical basis before overriding one.

Every entry: what the research found, the decision it drove, and any deliberate departure from literal reality. Anchors are stable - rules link to them by `#slug`.

---

## Homestead groves (yashikirin) - the real scale and prevalence

**Grounds:** `groves_on_windward_side`, `grove_prevalence`, the size-adaptive L-belt

**Evidence:** attested

**Sources:** not recorded - the finding is in the prose below; add a key to `SOURCES.md` when it is re-consulted

## The threshing yard's sun, and how far a farmhouse shades

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
the N/W bamboo strip is "shady ... always damp" and given to the kitchen drain and service sheds.
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
**The two rulings conflict** - a belt that stands off the plots (2026-08-25) and a frame that
does not open for the belt (2026-07-20) - and only the GM can reconcile them; the state shipped
is the one that honors both to the letter. **What was priced and declined**: letting
the windbreak set the frame (reverses the 2026-07-20 ruling - the GM's to reopen, not a session's);
a lane scaled to 15 m without moving the frame (measured: the belt is dropped). **Who chose**: the
session, on the measurement; the GM can raise the belt to 15 m by reopening the frame ruling.

*Departures taken knowingly:* the lane is a square, not a solar wedge that swings through the
afternoon (the yard's south corridor takes the same shortcut); the 12 px in `belt_polygon`'s
stand-off is an average plot overhang, and the clump filter is the guarantee behind it.

*Sources:* Sendai City igune species list (city.sendai.jp); Minami/Yonezawa/Okaze 2022, Osaki
igune drone survey (J-STAGE, LES 38(2)); Tonami Scattered-Village Research Institute 1996 model
homestead; Izumo tsuijimatsu (Kanto Gakuin column); ISA Arboriculture & Urban Forestry 37(1) on
fukugi; solar elevations computed for 38N.

## May a byre stand beside a wellhead? (researched 2026-08-18)

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
settlement's arrangement: it presupposes a centre to be near. A dispersed farmstead has no centre to
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
