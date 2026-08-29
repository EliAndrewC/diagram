# Field archetypes: the research behind the overlay, polder and dike-pond rules

*The research behind the rules in [`../settlements/archetypes.md`](../settlements/archetypes.md). Findings, anchors and disclosed departures live here so the rule file stays operational; this file is where citations and deeper historical context get added as they accumulate.*

**Load this file when:** you are changing an archetype rule, a parcel size, an overlay fraction or a check threshold - or you want the historical basis before overriding one. Not needed to simply DRAW an archetype.

Every entry: what the research found, the decision it drove, and any deliberate departure from literal reality. Anchors are stable - rules link to them by `#slug`.

---

## Why rape (油菜) was tried and removed

**Grounds:** `land_use_overlay` values are PERMANENT uses, never rotations

**Evidence:** reconstruction

**Sources:** `aburana-jawiki` (READ: autumn sowing, March-April cutting; rape into the harvested paddy) - the rice months and the Jiangnan rotation calendar were not found on a read page; the rice-rape rotation as one plot's two halves is the OCL *Rapeseed in China* review (403 to the fetcher) - SUMMARY-ONLY `rice-rape-calendar-summary` (SUMMARY-ONLY: sown late Sept-mid Oct, harvested Apr-May; rice transplanted Apr-May)

**RAPE (油菜) was tried and removed**: rice and rape are the two halves of one rotation in the SAME plot (rice May-Oct; rape sown into the drained stubble Oct-Nov, flowering Mar-Apr), so they are never both standing - mixing them at any fraction depicts two seasons at once, and the real spring picture is yellow rape against BARE stubble, not against green rice. Rape belongs on a future SEASONAL axis (a whole-field state), not this per-plot one.

## Overlay extent - a calibrated liberty, disclosed

**Grounds:** the `low` band = the bottom TWO levels; `overlays_on_wet_ground_only`

**Evidence:** interpolated, liberty

**Sources:** the lotus area share (a few percent to 10-15%) was found nowhere on 2026-08-28 (zh.wikipedia 莲藕 silent; a provincial share of aquatic-vegetable OUTPUT is the nearest figure) - the interpolation stands as a guess and is labeled one; the liberty is the GM's (2026-07-19)

**A CALIBRATED LIBERTY is recorded here** (constitution XII, GM 2026-07-19): the low band is the bottom TWO levels rather than the single hem on the drain. How wide a valley bottom's wet backswamp ran is unrecorded, and the researched extent for a lotus-growing village (a few percent to ~10-15% of field area) is itself interpolated from a national average that includes regions growing none. The single-hem reading put lotus at ~2% - inside the range, but so sparse the knob stopped making villages look distinct, which is the reason it exists. We chose the upper part of a plausible range for a stated non-historical reason (legibility) and disclosed it.

## The three overlay values - mulberry_fishpond, lotus, tea_fringe

**Grounds:** `s.apply_land_use`, `land_use_overlay_drawn`

**Evidence:** attested, interpolated, reconstruction

**Sources:** [`fortune-1843`](SOURCES.md#fortune-1843)

- **`mulberry_fishpond` (桑基魚塘)** - dug out of 低洼易有洪患之处, the low flood-prone hollows, as a flood adaptation that drained the hollow while raising the dike. **This value was nearly DELETED on a false premise** - that the dike-pond system was only ever a wholesale landscape conversion, so a scatter among rice never existed. The research refuted that outright: the scatter was the system's NORMAL state. Shunde county was ~4.6% dike-pond in 1581 (while containing townships already over 50% the same year); a 1980s survey of the heartland still found rice at 35%, the same share as the fishponds; and at Lake Tai mulberry sat on the *tang* banks with rice remaining the polder's main crop permanently. Gazetteers found *total* absence of rice remarkable enough to record. The wall-to-wall landscape is the rare end state of a ~300-year plot-by-plot process (挖塘培基 - dig one low plot into a pond, pile the spoil into a dike; a one-household, one-dry-season job), which is what the `mulberry_dike_fishpond` ARCHETYPE is for. **The archetype and the overlay are two SCALES of one system, not duplicates - do not delete either.** The archetype opts out of the topographic filter by name (`eligible="all"`), since at that scale the ponds really had engulfed the ordinary ground too. *Negative result worth keeping:* the outer-delta 沙田 *shatian* were equally low and equally wet and **stayed in rice** - low ground is necessary but not sufficient; the dike-pond zone also had smallholder tenure inside an established polder and water access to Canton.
  - **`lotus` (藕田)** - models **deep-water lotus** (深水藕, 30-50cm, tolerating ~1m) against paddy rice's ~5-9cm optimum, so it physically cannot sit on high ground. **Shallow-water lotus** (浅水藕, 10-20cm) in ordinary paddy is equally real but is deliberately NOT modeled: it is an economic choice rotating with rice (稻藕轮作), driven by a layer the generator does not have, and drawing it would be visually indistinguishable from the uniform-random bug this replaced. Read research.md D1 before "restoring" it. *Honest limitation:* the agronomy is solid but pre-modern village-scale practice is not directly sourced - the clearest conversions in the record (Kasumigaura 1970s, contemporary Vietnam) are modern and policy-driven. Extent where present is a few percent up to maybe 10-15% of field area; that range is interpolation, not a sourced figure.
  - **`tea_fringe` (茶)** - already correct, unchanged in code. But the prose describing it as the "upper slope" was WRONG: tea took the **lower-to-mid FERTILE hillside**, never the low lands and never the barren upper slope (Robert Fortune, eyewitness, 1843: "always situated on the lower and most fertile sides of the hills, and never on the low lands"; the upper slopes were forest, sweet potato and peanut). The boundary rule states itself - **the line is the highest irrigation ditch** - which is exactly what `net['dry_plots']` already is. Form is smallholder: recognizable rows in acre-scale patches, several per household, dotted across a hillside, not one contiguous block. **Two anachronism traps:** neat contour-TERRACED tea is post-1949 (a state program; terrace the paddy, not the tea), and bund-margin tea (畦畔茶) is a JAPANESE practice with no Chinese equivalent - do not project it westward.

## Polder parcels were a private-tenure patchwork

**Grounds:** `polder_parcels_vary`; the ~110 ft / ~160 ft modules

**Evidence:** attested

**Sources:** [`buck-survey`](SOURCES.md#buck-survey)

The research upheld the instinct: the surveyed rectilinear chessboard of the Taihu *tangpu* 塘浦 system was the CANAL grid at kilometer scale, while the parcels inside it were a private-tenure patchwork - mid-Qing Jiangnan farms averaged ~10 mu scattered over several parcels; Buck's pre-mechanization survey (1929-33) found a mean parcel of ~1 mu, rectangular only where it fronted a straight ditch; dike-ponds accreted household-by-household (挖塘培基, research.md D2), so 66 identical ponds contradict the map's own backstory. Uniform machine-sized rectangles are a 20th-century consolidation look (Japan's 1963 *hojo seibi* 30m x 100m standard; PRC consolidation campaigns).

## The perimeter dike followed the natural water edge

**Grounds:** `polder_dike_is_earthwork`, `s.perimeter_dike`

**Evidence:** attested, reconstruction

**Sources:** `sdlib-shunde-jitang` (READ: the dike as pond spoil, planted), `miragenews-polders` (READ: fish-scale polders named for their aerial outlines; organic forms replaced by standardized rectangles after 1949)

*What the research found:* a wei-tian 圩田 / dike-pond dike was dredged pond-mud heaped and packed (the 挖塘培基 dig-and-pile cycle that also formed the ponds), trapezoidal in section, PLANTED with mulberry/willow/crops that bind the soil, walked and lived on, and constantly breached-and-repaired - so it read as a mottled, vegetated green-brown band of VARYING width, not a uniform stroke. Crucially, the *plan form splits*: the surveyed interior ditch/paddy grid was genuinely rectilinear, but the OUTER perimeter dike **followed the natural water edge** (lake / creek / marsh) in gentle curves and non-square bends - the "fish-scale polder" (鱼鳞圩) form named for exactly those irregular overlapping outlines. The dead-straight right-angled rectangle is a **post-1949 industrial** shape (heritage scholars: "the organic forms of polders were replaced by standardized rectangular patterns"), so it is the one genuinely anachronistic thing on the old render.

## Why dikes were planted, and what the row spacing rests on

**Grounds:** `_mulberry_rows`, the willow/mulberry row split

**Evidence:** attested, analog, reconstruction

**Sources:** [`willow-palisade`](SOURCES.md#willow-palisade)

*Why dikes were planted at all:* a bare bank of heaped dredge-mud is a liability - rain gullies it, wave wash gnaws the waterside toe, and a slump becomes a breach - so planting the dike was the standard remedy wherever these earthworks existed: the roots bind the packed mud. The species split by role: WILLOW on the water face (thrives with wet feet; its root mat armors the bank against wave wash; pollarded for withies - willow-fascine bank protection is an ancient Chinese technique, in use by the last century BC), and in sericulture districts MULBERRY on the crest/inner face - the dike was elevated, well-drained, annually re-fertilized by the dredge cycle, i.e. prime planting ground in a landscape that is otherwise water (Lake Tai mulberry sat on the *tang* banks). A dike that looks bare and cleanly engineered is the modern-concrete-era tell. *What the numbers rest on:* dike planting was ROW planting along the alignment, not scatter. The closest attested in-row figure is the Qing Willow Palisade statute - willow whips planted every 5 chi (~1.67 m ~ 5.5 ft) in rows on an embankment - corroborated by modern willow-fascine practice descending from the same mechanics (rows 1-1.5 m apart on erosive soil, 1.5-2 m on cohesive). A polder-dike-specific statute was NOT found; the Willow Palisade figure is an ANALOG from a border embankment, recorded here as such, not as polder canon.

## Why dike willows do NOT replace the village windbreak

**Grounds:** keeping both features - do not simplify one away

**Evidence:** reconstruction

**Sources:** `usu-windbreak` (READ: shelter up to 30 H - the entry's 10-20 H is inside it), `yashikirin-jawiki` (READ: igune on the north and west; species スギ・マツ・ヒノキ・ケヤキ)

*Why the dike willows do NOT replace the village windbreak* (GM 2026-07-24, asked and answered - do not "simplify" one away): a windbreak's sheltered zone runs ~10-20x barrier HEIGHT, and the homestead belt is full-height dense planting for exactly that reason, while dike willows are POLLARDED low because the withies are the harvest - a single porous row at rooftop height shelters almost nothing at the houses' distance. Worse, willow and mulberry are DECIDUOUS: bare sticks during the NW winter monsoon, the one season shelter matters, which is why homestead windbreaks ran dense/multi-row/evergreen-heavy (the igune of the flat Sendai plain persisted amid abundant field-edge trees for the same reason). And an east-dike village sits downwind of the whole pond sheet - open water is the smoothest fetch there is, so the wind reaches the dike at full strength. Utility rows on the dike and a dense grove at the homestead are DIFFERENT plants doing DIFFERENT jobs; real polder landscapes carried both.

*Correction to the record (2026-08-28, feature 143):* "the igune ... ran dense/multi-row/evergreen-heavy" - the page read names three evergreen conifers and one deciduous broadleaf (keyaki) and never characterizes the mix; the north-and-west placement against the winter wind is read. Softened to "conifer-dominated, with keyaki"; the rule (a dense full-height belt, distinct from pollarded dike willows) is unaffected.

## The ring canal runs on the INNER toe - 一河围田

**Grounds:** `polder_channels_clear_of_dike`

**Evidence:** attested (gated crossings, inner channels), researched (the toe placement and the named forms - not re-found)

**Sources:** `cssn-jiangnan-weitian` (READ: "中有河渠，外有门闸" - channels inside the dike, gates through it, opened in drought and shut in flood). The 一河围田 shorthand, the inside-toe placement and the 月样 / 弓样 forms were not found on any page read (zh.wikipedia 圩田 silent) - leftover `weinei-he-summary` (SUMMARY-ONLY: the 月状 / 弓状 forms and gated ends)

*What the research found:* the polder's trunk distribution+collection canal rings the block on the INSIDE toe of the perimeter dike, on the FIELD side (Jiangnan shorthand **一河围田, "one river surrounds the field"**; cross-section outside->in: wild water -> dike -> inner ring canal 圩内河 -> field ditches 浜 -> paddies). Outside the dike is the wild lake/creek the dike holds back, so NO irrigation channel runs out there; water crosses the dike ONLY through gated **sluices** (斗门/水閘/涵洞) cut at discrete points (the inlet + outfall), never as an open cut over the dike body. And the trunk line is *organized-but-organic*: long runs that read straight-ish but GENTLY WAVY (a surveyed dug canal wavers with terrain and repair; crescent 月样 / bow 弓样 trunk forms are attested named options), with rounded corners rather than hard 90-degree turns - the finer laterals are visibly crookeder.

## Wet-rice hydrology has no crossings to draw

**Grounds:** `water_channels_join_not_cross`, `field_ditch_tips_land_on_the_trunk`

**Evidence:** attested

**Sources:** `fusekoshi-jawiki` (READ: the inverted siphon under a watercourse, with historical examples), `suirokyo-jawiki` (READ: the aqueduct bridge)

*Why any crossing is wrong here:* wet-rice hydrology has no crossings to draw - a ditch either feeds another or is fed by it, and where two courses genuinely had to pass at different levels the builders put in an aqueduct or an inverted siphon, a distinct structure this vocabulary does not contain.

## Grid vs mosaic - the arrangement differed by system

**Grounds:** `build_polder(mosaic=)`; `pond_layout` as a twin axis (a rolled hamletgen knob since feature 150)

**Evidence:** attested, corroborated

**Sources:** [`mdpi-3860`](SOURCES.md#mdpi-3860) (SUMMARY-ONLY - 403 in the 2026-08-28 re-sourcing pass), [`shen-kuo`](SOURCES.md#shen-kuo) for the surveyed wei-tian
**Sources:** `cssn-jiangnan-weitian` (READ: the tangpu lattice at five-to-seven and seven-to-ten li), `miragenews-polders` (READ). The Pearl-delta "mosaic-like ... boundary blurred" description and the dikes eroded from ~20 m to under 4 m: MDPI *Forests* 13(8):1241 and *Aquaculture* 2022 (both 403) - SUMMARY-ONLY, leftover `dikepond-erosion-summary` (SUMMARY-ONLY: ponds grew, dikes shrank 1967-2016)

*What the research found (web-sourced, cited in the session):* the answer is BOTH, and it splits by system. The individual ponds genuinely WERE rectangular oblongs - hand-dug from marsh (挖塘培基: dig the pond, pile the spoil into the dike), the recurring descriptor a "chessboard" of "rectangular-shaped dikes... with water in between" - because you dig a pond in whatever packs the space and straight dikes are easiest to pile, walk, and plant mulberry on. So all-rectangular ponds are correct; this is the rare farm landscape that does NOT grow organically around the terrain, because the farmers MADE the terrain. BUT the *arrangement* differed by system. The lower-Yangtze **圩田 (wei-tian)** was a SURVEYED rectilinear grid - the Song-era 塘浦 *tangpu* lattice, deliberately engineered - so a clean grid is historically right for it. The Pearl-delta **桑基魚塘 (dike-pond)** instead accreted household-by-household into a MOSAIC; the landscape-ecology literature describes the historical delta not as a uniform chessboard but as "mosaic-like constructed ponds with meandering natural river systems, [with] the boundary between constructed and natural blurred" - rectangles, yes, but of varied sizes at varied local orientations fitted around winding interior creeks (the perfectly-uniform grid is closer to the MODERN consolidated look, which the same sources note eroded the ~20 m dikes to under 4 m).

## The 6:4 water-to-dike ratio, and coppiced mulberry

**Grounds:** the drawn bank width; `_mulberry_rows` crown density; `POLDER_FABRIC` (feature 150)

**Evidence:** attested (the ratio, three reads); the coppice density is still unsourced

**Sources:** [`gd-gazetteer-sangji`](SOURCES.md#gd-gazetteer-sangji) (水基比 三七至四六开), [`fao-ac241e`](SOURCES.md#fao-ac241e) (6:4; 1:1 where the worms alone feed the fish), [`isis-dykepond`](SOURCES.md#isis-dykepond) carrying [`ruddle-zhong-1988`](SOURCES.md#ruddle-zhong-1988) SUMMARY-ONLY for the 0.4-0.6 ha ponds and 6-10 m dikes. The coppiced-bush density (one bush per 10-20 sq ft, crowns 4-6 ft) was NOT re-found on 2026-08-28 - it stays on the re-sourcing queue
**Evidence:** attested (the ratio exists in both orders), deviation (the drawn 6 water : 4 dike as a disclosed regional reading - GM 2026-08-28)

**Sources:** `cssn-sangji-yutang` (READ: "基六塘四"), `kuwa-jawiki` (READ: mulberry kept as a low shrub; the height and density SUMMARY-ONLY)

The classic dike-pond prescription was an explicit area ratio of 6 parts water to 4 parts dike (some districts 7:3); measured from the Kuwabata manifest, water is 76% of each parcel (bank 24%) and 50% of the whole block once the shared 22 ft dikes and canal corridors count - bracketing 6:4. The band is not marginal ground: each pond's ~6,300 sq ft (~0.14 ac) bank was the SILK side of the loop (leaf -> silkworm -> frass -> fish -> dredged pond mud -> dike fertility), and the ratio existed because too much water starves the silkworms and too much dike starves the fish.

Silkworm mulberry was not grown as trees: it was COPPICED into low bushes (crowns ~4-6 ft) so the leaf could be stripped several times a year, planted in dense rows on the dike at roughly one bush per 10-20 sq ft - i.e. 300-600 bushes per pond, tens of thousands across the map. At 1 px = 1 ft a crown is a 2-4 px dot and adjacent crowns nearly touch, so drawing the actual trees at honest density IS a packed dot band; individually distinguishable tree glyphs would mean 3-5x crown inflation, forbidden on to-scale maps. No berries either: leaf-stripped coppice barely fruits, and a mulberry fruit is sub-pixel at this scale - crown color carries the read.

*Correction to the record (2026-08-28, feature 143) - CONTRADICTED on the ORDER of the ratio, rule unchanged, awaiting the GM:* the one page read writes the classic prescription as **基六塘四 - six parts DIKE to four parts POND**; the entry (and a people.cn page seen only in a search summary, "六分为塘，四分为基") has it the other way, six water to four dike, and Kuwabata is drawn at 76% water per parcel. The literature carries both orders and a 7:3 variant, so this may be a regional split rather than an error - but as the record stands, the drawn ratio rests on the reading the read source inverts. Listed in the feature 143 ledger, section G, with the option of a follow-up read (Ruddle & Zhong 1988 is the authority) before any redraw.

**GM ruling (2026-08-28, feature 143 T20) - DEVIATION, disclosed regional reading:** Kuwabata keeps its 6 water : 4 dike parcels. The record carries the prescription in BOTH orders - 基六塘四 on the page read (`cssn-sangji-yutang`), 六分为塘、四分为基 in the people.cn summary - and a 7:3 variant; the map follows the water-heavy reading. The interactive map is to say so on every pond and bank of Kuwabata: "a regional reading; the classic prescription is also recorded as six parts dike to four parts pond". Class for the HTML modal: **deviation** (a priced trade-off, not an error).

## A dike-pond is fed and drained through sluice gates

**Grounds:** `dikeponds_fed_and_drained`, `M['dikepond_sluices']`

**Evidence:** attested (gated crossings), researched (the board-sluice detail - SUMMARY-ONLY)

**Sources:** [`fao-x6708e`](SOURCES.md#fao-x6708e) (the sluice-gate definition, verbatim, READ 2026-08-28), [`cssn-sangyuanwei`](SOURCES.md#cssn-sangyuanwei) (the polder's 窦)
**Sources:** `cssn-jiangnan-weitian` (READ: gates through the dike, worked by season - the polder case); the pond sluice "closed with wooden boards" and the inlet-high / outlet-low plumbing come from Ruddle & Zhong (Cambridge 1988; GeoJournal BF00645312 login-walled) and were not re-read: SUMMARY-ONLY - leftover

*What the research found:* a 桑基魚塘 pond is NOT a sealed basin - each connects to the creek/canal network through a SLUICE GATE, "a protected opening in the pond dike that can be easily closed with wooden boards to regulate water level" and, by pulling the boards, drain the pond at harvest. And a pond on a slope is plumbed INLET-HIGH, OUTLET-LOW so water flows downhill through it (the whole dike-pond net runs in series from a high intake to a low outfall). So the channels do not "irrigate" the ponds paddy-style; they are the conveyance-and-drainage network the ponds exchange water with.

## Polder siting - full enclosure, fluctuating water, and where the village sits

**Grounds:** the margin-polder form of both pool polders; `meta.waterward`; `s.dike_top_houses`

**Evidence:** attested, corroborated

**Sources:** [`shen-kuo`](SOURCES.md#shen-kuo), [`fei-xiaotong`](SOURCES.md#fei-xiaotong)

(1) *Does the dike really surround the paddies completely?* Yes - full enclosure IS the defining feature, not a drawing convenience. A weitian is wetland "enclosed with dykes to be hydrologically separated from the surrounding fluctuating water and then drained" (the character 圩 means the enclosing embankment); Shen Kuo (Northern Song, Illustrated Records of Wanchun Polder) describes "dikes and dams... built along the rivers to enclose the farmland, which is called a polder." The enclosed floor sits at or below the surrounding FLOOD stage, so on a flat lake plain there is no safe side to leave open - any gap re-floods the whole block at the next high water, which is why water crosses only at the two gated sluices. The scale is attested too: fragmented small polders were each "cultivated by a group of 10-20 households" behind dikes ~1.5 m high - Enokida's 16 households are exactly this unit. (2) *Should there be marsh/wetland on all sides then?* The outside is "fluctuating water," but that means neither open lake on every side nor water year-round. Attested surroundings: the lake/creek network the polder was dug from; reed marsh and mudflat where reclamation had not yet reached; NEIGHBOR polders across a shared creek (the mature Taihu landscape was "islet-like" fish-scale polders packed into the water net); and - at the district margin - the natural shore, because reclamation advanced FROM the shore ("mudflats along rivers and lakes were transformed"). The water also FLUCTUATES seasonally: at low stage much of the outside is exposed mudflat and reed, at flood it is sheet water - the dike is built against the flood stage, not the average day. Both pool polders are drawn as the landward-margin case: wild header pond NW (the source), reed marsh at the low south outfall side, village on naturally dry ground east. **RESOLVED (GM 2026-07-24, same day):** the WEST flank's outside used to draw as the same dry scrub as the landward east, so nothing communicated that the west dike held anything back; both polders now carry a `waterside` reed fringe along the west and declare `meta.waterward`, gated by `polder_waterward_flanks_wet` - see 'Polder waterward fringe + dike-top housing' below. (3) *Should the farmhouses be INSIDE the dike?* Both siting patterns are attested, split by what dry ground exists. Where the polder abuts the natural shore, the village sits on the landward dry ground at the dike's shoulder - the current renders' configuration, and the natural one for a margin polder (nobody lives on a flood-fighting earthwork when real dry ground is a few steps east). In the DEEP-water landscape with no natural dry ground, settlement used the polder's own raised earth instead: linear villages ON the dikes (canal-dike settlement "taking advantage of the elevated typology" is attested from the 8th century on) or houses inside the polder along its interior streams (Fei Xiaotong's Kaixiangong / the Xichang polder layout). So Enokida and Kuwabata are correct AS margin polders - but an "islet" polder map, water-ringed on all sides, would REQUIRE dike-top or interior housing, and `structures_clear_of_dike` (which keeps all structures off the dike band) would need a carve-out for that settlement form. **RESOLVED (GM 2026-07-24, same day):** dike-top housing is now a real engine capability (`s.dike_top_houses`, `settlement_form="dike_top"`, the carve-out + its honesty check) implemented as a KNOB for future variety - the GM explicitly chose NOT to convert any existing settlement; no pool map uses it yet. See 'Polder waterward fringe + dike-top housing' below. One more confirmation from the same research: the polder community IS its dike-maintenance community ("sustaining a polder necessitated a close-knit community," often one extended family, which named its polder) - so a polder village always sits hard against its own block, which is what `field_ringed` and the cluster-hug behavior already enforce.

## What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit (feature 150, 2026-08-28)

**Grounds:** the feature-139 audit list (`specs/150-kuwabata-dike-pond-hamlet/audit.md`); nothing drawn from it yet - the GM chooses (FR-008)

**Evidence:** attested for the boats, the in-house rearing and the manure pits (one primary ethnography, Lake Tai); attested-at-secondhand for the dike livestock and the fry trade (Pearl delta); silent on pond huts

**Sources:** [`fei-1939`](SOURCES.md#fei-1939), [`fao-ac264e`](SOURCES.md#fao-ac264e), [`fao-ac241e`](SOURCES.md#fao-ac241e), [`isis-dykepond`](SOURCES.md#isis-dykepond) (carrying [`ruddle-zhong-1988`](SOURCES.md#ruddle-zhong-1988), SUMMARY-ONLY), [`cssn-sangyuanwei`](SOURCES.md#cssn-sangyuanwei), [`miles-2003`](SOURCES.md#miles-2003) (SUMMARY-ONLY), [`gmrb-2024-sangji`](SOURCES.md#gmrb-2024-sangji), [`dili360-2005-sangji`](SOURCES.md#dili360-2005-sangji)

*What the question was.* The GM (2026-08-27): a research pass on the reference hamlet turned up outhouses and the rest; *"this is a different type of map ... I could imagine there being map features which would exist in Kuwabata but not in Inashiro."* The pass asked what PHYSICAL features stood on a silk-and-fish hamlet's ground - farmsteads, dikes, water's edge - that a rice hamlet's did not, and which rice features it should lack.

*What the research found.* The one primary ethnography of a silk village that could be READ in full is Fei Hsiao-tung's *Peasant Life in China* (1939), on Kaihsienkung south of Lake Tai - a rice-AND-silk village on a stream net, not a converted dike-pond block, so it answers the SILK half of the loop directly and the FISH half only by the Pearl-delta secondary literature.

- **Silkworms were reared INSIDE the dwelling, not in a separate building.** *"Silkworms are raised in rectangular and shallow containers about 1.5 by 1 metre in size. They are put on the shelves of a stand. Each stand has eight containers. Each house has enough room for five stands."* And during the two-week peak *"all the rooms except the kitchen may be used for sheltering silkworms. All the members of the household will crowd in one bed-room."* The front room *"is used for working, such as raising silkworms, manufacturing silk, threshing rice"*; the old reeling machine (*"a furnace to boil water, a wheel ... a rotating axle connected to a plate for treading"*) stood in the house too. So a sericulture hamlet owes the map NO silkworm house and NO reeling shed: the record puts both indoors. (Communal 蚕房 rearing halls are a 1950s collective form - the Shunde examples the search pass surfaced are dated 1958 - and are not premodern.) NOT OWED.
- **Boats, and a village laid out along its water.** *"Nearly every household possesses one or more boats except those who are not engaged in agricultural or fishing work."* *"The importance of the boat in communication means that the houses must be near the water and consequently determines the plan of the village. Villages grow up along the streams."* *"Every village has its own agent boat which serves as the buying and selling agent of the villagers in the town market."* The Pearl-delta proverb of the Sangyuanwei polder says the same of silk: 一船蚕丝出，一船白银归 - *a boat of silk out, a boat of silver back*. A cash-crop hamlet that sells silk and fish and buys grain in is a hamlet that LIVES by water transport. Kuwabata as generated has a header reservoir and a ring canal and no navigable water at all. It was put to the GM as a candidate (a creek along the landward flank with boats and a landing) and DECLINED (2026-08-28): *"would it necessarily be the case that any settlement of this sort would have one. I wouldn't think so"* - Kaihsienkung's water is that village's geography, not the archetype's; the hamlet's connector lane leads to the market, or to whatever water carries its goods there, and the map presumes rather than draws it. NOT DRAWN, by ruling.
- **Manure PITS, not heaps.** *"Human manure, being the most important fertilizer in the farm, is preserved in the pits made of earthenware, half buried in the ground at the back of the building. Along the southern bank of the Stream A, the public road is lined up with these manure pits."* Two attested forms for the same fixture (the reference hamlet draws a heap, research/homesteads.md) - by the knob rule this is a `heap | pit` roll, and a roadside pit is a distinct glyph. CANDIDATE, a new glyph - the GM's call.
- **Mulberry on the raised margin, houses beside it, vegetables beneath it.** *"Along the margin of each yu, ten to thirty metres of land is left for plantation of mulberry trees and a wider space for house building. This land on the margin is higher. It also serves as a dyke for the farm."* *"Limited space under the mulberry trees for growing vegetables."* Kuwabata already draws this: the planted perimeter dike, the village on the dry flank. ALREADY DRAWN.
- **Sheep huts** (Fei: *"little huts for the sheep and sometimes also for storage"*, *"the sheep hut has become a common appendage of a house"*) are a 1920s-30s Lake Tai innovation (*"in the past ten years"*) - NOT OWED on a premodern sheet.
- **Pigs and ducks ON the pond dikes** - the Pearl-delta loop. Ruddle & Zhong (1988) as carried by the i-sis summary: *"Pigs, chickens and ducks are reared on the dykes, to provide manure to fertilise the fishponds"*; the modern FAO/NACA manual: *"The simple pig shed constructed on the pond dyke or over the water surface"* lets the excreta flow to the pond; fish-cum-duck ponds fence a dry run on the dike and a wet run in a corner of the water. The premodern prevalence is not in anything read; the proverb 蔗榨糖后的蔗渣喂猪 (bagasse fed to pigs) puts pigs in the traditional loop. CANDIDATE: a pig sty ON a pond dike (we draw byres and coops; a sty on the dike is a new kind and a new position) and a duck pen at a pond corner - both new categories, prevalence unquantified - the GM's call.
- **Fish fry (鱼花) as a trade, and nursery ponds.** Jiujiang township (Nanhai) was the delta's fry center from the Ming (Miles 2003, SUMMARY-ONLY: the township's rise 1395-1657 on fry collected from the Xijiang); the Sangyuanwei proverb 男贩鱼花，妇女喂爱蚕 - *men trade fry, women feed the worms*. Fry are reared in small ponds before stocking the grow-out ponds. CANDIDATE, NOT a new glyph: designate a few of the block's smallest parcels as fry ponds in the manifest (a record for the interactive map's reader), or leave the mosaic as it is. The GM's call.
- **Other dike crops: sugar cane, fruit, banana** (蔗基/果基/蕉基). The 1980s survey carried by i-sis: sugar-cane dikes 18% of the district against mulberry 12%; 中国国家地理 2005 on the lost landscape: 蕉林蔗海 (*banana groves and a sea of cane*); the gazetteer office: dikes planted 桑、蔗、蕉. Attested alternative FORMS of the dike planting - by the knob rule a `dike_crop` roll - but each is a plant not on any map. CANDIDATE, new categories - the GM's call; Kuwabata itself is the mulberry case by name.
- **The dike-pond's own sluices** - already drawn and gated (`dikepond_sluices`, 'A dike-pond is fed and drained through sluice gates'). ALREADY DRAWN.
- **Pond-side huts (塘头屋 / a watchman's hut)**: searched twice in Chinese and English, nothing attested. NOT SUPPORTED - do not draw.
- **A silk-goddess shrine (蚕花娘娘, 蚕神庙)**: the Huzhou-Jiaxing festival temples are VILLAGE and town institutions (the Qingming 轧蚕花 gatherings); a hamlet has no shrine by the tier's own definition. NOT OWED at this tier; a note for the village tier.
- **What a no-rice hamlet should LACK.** Fei's village threshed rice *"in the open space in front of the house, or in the front room"* - the yard's threshing use is a RICE use. Kuwabata draws a threshing yard on every farmstead because the homestead bundle does; with no rice within its bounds the yard is at best a work yard (cocoons are sorted and leaves handled somewhere). SHOULD-BE-ABSENT CANDIDATE: the threshing yard as a rice feature, or its re-reading as a work yard - the GM's call. The straw rick is already not drawn. The in-field pocket pond, the dry hem and the comb deliveries are absent by archetype already (spec 139 Decisions Recorded).
- **Holdings.** Not settled: nothing read gives a silk-and-fish household's ground, so `GROSS_ACRES_PER_HOUSEHOLD` (the paddy 1.3 ac) stays a labeled GUESS on this archetype.

*Departures and honesty.* The gazetteer office frames 桑、蔗、蕉 as a SUCCESSION of dike-pond types (桑基 giving way to 果基、蔗基、菜基 over the region's history), not one dike carrying all three - so a `dike_crop` knob would roll a hamlet's TYPE, not mix crops on a dike. Fei is Lake Tai, 1936; the Pearl-delta reads are 1980s surveys and a 2006 summary of the 1988 monograph, which itself could not be fetched (403 on every host) - every Ruddle & Zhong number here is SUMMARY-ONLY. No single source describes a WHOLLY converted hamlet's farmsteads; the list is assembled across the two systems and says so per item.
