# Vegetation and terrain: the research behind the windbreak, commons and forest rules

*The research behind the rules in [`../settlements/vegetation.md`](../settlements/vegetation.md). Findings, anchors and disclosed departures live here so the rule file stays operational; this file is where citations and deeper historical context get added as they accumulate.*

**Load this file when:** you are changing a vegetation rule, a grove size, a tree density or a check threshold - or you want the historical basis before overriding one.

Every entry: what the research found, the decision it drove, and any deliberate departure from literal reality. Anchors are stable - rules link to them by `#slug`.

---

## The fengshui forest - real scale, and why ours is honest

**Grounds:** `village_windbreak_scales_with_cluster`

**Evidence:** attested

**Sources:** [`forests-2020`](SOURCES.md#forests-2020)

- *Scale - the real numbers (research grounding, for calibrating the glyph).* Field surveys of southern-China village fengshui forests: **~2 groves per village** on average; **stem density ~3,400 woody stems/ha**, basal area ~49 m²/ha (genuine closed-canopy forest, not scattered trees); patch AREA is highly variable (famous lineage-village groves exceed 20 ha, e.g. Lingtou, 800 years old), but a TYPICAL village grove is a small forest patch, **~1-2 ha for the back grove** (modest villages <1 ha, big clan villages much larger) and **~0.1-0.5 ha for the water-mouth cluster**. So a ~1-2 ha back belt is *thousands* of woody stems in total, of which roughly **100-300 are mature canopy trees** over a dense bamboo/shrub understory; the water-mouth is **a few dozen big old trees**. Per "relative sizes roughly honest": the back belt reads as a real small FOREST (clearly the largest vegetation feature, a wall of dozens-to-hundreds of crowns - `village_grove` fills its polygon with overlapping dense clumps so a big belt does not read as a handful of lone trees), the water-mouth as a distinct smaller cluster, plus the bamboo/fruit scatter through the village. Hoshigaoka draws a ~1-2 ha embracing windward belt + a ~0.3 ha water-mouth + the leafy scatter.

- *Why the sizing is honest at this scale.* At 1 px = 2 ft a ~1-2 ha grove is ~27,000-54,000 px² - genuinely large relative to the ~11 ha built cluster (~10-18%), so the belt reads as the dominant feature without being cartoonishly oversized. Sources: Fengshui woodland (Wikipedia); Chen & Coggins et al., "Fengshui forests and village landscapes in China" (57-village survey); Hu et al., "Values of village fengshui forest patches" (Pearl River Delta, 32 patches, the density/basal-area figures); "Village Fengshui Forests as Cultural and Ecological Heritage" (Forests 2020).

## Forest density and crown size

**Grounds:** `settlement._tree_stand`, `structures_clear_of_trees`

**Evidence:** reconstruction

**Sources:** not recorded - the finding is in the prose below; add a key to `SOURCES.md` when it is re-consulted

- *Density and crown size - the numbers and the why.* A closed premodern hill wood (the mixed broadleaf/conifer cover of a settled valley's back slope, cut over for fuel and timber on a rotation) carries roughly **500-800 canopy stems per hectare**. 1 ha = 107,639 sq ft, so ~600 stems/ha is one canopy tree per ~180 sq ft: a mean spacing near **13 ft** (`CANOPY_SPACING_FT`). Canopy crowns in such a stand run **~5-8 m across** (16-26 ft) with occasional wider emergents, so `CANOPY_R_FT = 8.5` is the mean radius, jittered 0.75-1.4x. Crowns of ~17 ft mean diameter on 13 ft centers OVERLAP, and that is the point - **closure is what makes a wood a wood**, so the packed look is honest rather than decorative. Same finding as the mulberry rows (`_mulberry_rows`): at a to-scale grain, drawing real planted density honestly IS a dense mass of crowns, not sparse symbols spaced for the eye. Nothing is inflated for legibility - at 1 ft/px a crown is r ~6-12 px and it shrinks with the map at coarser grains, exactly like the buildings.


## The crop margin - scrub stands 6 ft off every field edge

**Evidence:** reconstruction (web research 2026-08-15; searched paddy-levee structure/width and traditional field-margin management)

**Sources:** not recorded per-claim - the finding is in the prose below; add a key to `SOURCES.md` when it is re-consulted

- *What was found.* A paddy levee (*keihan*/*aze*; Chinese *tian'geng*) is a narrow earthen ridge - roughly 1-2 ft wide and under a foot tall, up to ~3 ft where it doubles as a footpath (*azemichi*). Levee structure studies (e.g. the Lake Biwa paddy-levee flora work) describe a flat trodden part plus a grassed face, and the levee grass was CUT several times a season - fodder, thatch, green manure - as was the strip immediately beside any crop. Constant cutting is why woody scrub could not establish within about a scythe's swath (~1-2 m) of a field edge; the same ~1 m clean strip separating crop from boundary vegetation shows up as standing practice in traditional field-margin management. The 6 m+ "conservation headlands" of modern European agri-environment schemes are a MODERN wildlife intervention, not the historical norm, and East Asian land hunger kept margins at the narrow end of the range.
- *The decision it drove.* `settlement/homestead_parts.py` `_CROP_MARGIN_FT = 6.0` - bund plus one cut swath (~1.8 m total). The `commons` scatter (all roles) skips every paddy and dry plot padded by this margin, converted at the map's `ftpx`; tall glyphs (scraggly pines ~14*bs px tip reach, woodland crowns ~11.5*bs px radius) additionally stand their own drawn reach back so no ink leans over a crop.
- *Disclosed departures.* (1) Grass-tuft blade TIPS may lean up to a few real feet past the margin line at coarse tiers (blades are 2.4-4.2*bs px and get no lean pad) - accepted deliberately: grass overhanging a bund is real, and the overhang is sub-pixel-to-invisible at render (settlement-review, 2026-08-16). (2) The reed `marsh` gets NO margin at all - wet ground genuinely starts at the polder dike, so reeds abutting a field's low bund is honest.

## Scrub stays off open water - including the comb laterals' drawn width

**Grounds:** `settlement._watercourse_segs`, `test_commons_keeps_scrub_off_drawn_channels`

**Evidence:** defect fix (GM 2026-08-16, Inashiro), not new research

- The scatter's water skip ("vegetation never draws OVER open water") read `M['streams']` + `M['channels']` only - and on a comb-built map `M['channels']` holds the hairline TOPOLOGY connectors (w 2.5) while the drawn supply laterals live in `M['drawn_channels']`, up to ~14 ft wide on their own filleted post-clip polylines. Result: 27 grass tufts standing on Inashiro's head-race, plus tufts crowding its banks inside the drawn stroke. `_watercourse_segs` now feeds the skip every drawn course at its drawn (piece-tapered) width; base points keep the same 2 px pad as before, and the scatters query it through a pre-boxed grid (the grid prunes, it never decides).
- *Deliberately NOT decided here* (as of this fix): a maintained-bank margin - tufts standing right up to the water's edge remained legal. DECIDED the same day, when the GM saw them: see "The cut bank" below. *(Worked example for the open-decision-sketch convention, diagram CLAUDE.md: this entry should also have carried the three lines the deciding session had to re-derive - land it at the commons scatter's `wat_b` grid in `settlement/land/cover.py` (it was `settlement/land.py` until feature 120 split the package); hold it by extending the drawn-channels margin test in `tests/settlement/test_homestead_parts.py`; exclude streams + marsh, whose natural banks keep vegetation to the water's edge.)*

## The cut bank - scrub stands 6 ft off every irrigation channel's drawn edge

**Grounds:** `settlement/homestead_parts.py` `_BANK_MARGIN_FT`, `test_commons_keeps_scrub_a_cut_bank_off_the_channels_but_not_the_streams`

**Evidence:** GM decision (2026-08-16, Inashiro second pass), extending the crop-margin reconstruction above; no new sources consulted

- *What prompted it.* After the drawn-width fix (previous section), tufts still seeded the 10-16 ft berm strips between the supply channels and the dry hem plots: the drawn-width skip (2 px pad) and the 6 ft crop margin each guarded their own edge and left a legal sliver mid-strip. The GM read the strips as scrub crowding the channels and resolved the open decision: the bank takes a margin too.
- *The decision.* The `commons` scatter (all roles) stands its base points `_BANK_MARGIN_FT = 6.0` real feet off the drawn water edge of every IRRIGATION course - `M['channels']` and `M['drawn_channels']` at their drawn (piece-tapered) widths, converted at the map's `ftpx`. The reasoning is the crop margin's, applied to the bank: a supply channel's bank is maintained ground - walked for sluice operation and bund upkeep, its grass scythed for fodder on the same rotation as the field margins - so woody scrub never establishes within a swath of the water. 6 ft = one scythe swath, the same figure as `_CROP_MARGIN_FT`. Between them the crop margin and the bank margin close any berm strip up to ~12 ft of bare ground, which covers every hem berm the comb builds (Inashiro's run 3-9 ft).
- *Deliberate exclusions.* (1) STREAMS take no margin - a natural brook bank is vegetated to the water's edge, and the 2026-08-16 settlement-review pass explicitly praised the ABSENCE of a sterile halo on the banks; only the engineered courses are maintained ground. (2) The reed `marsh` keeps its no-margin rule from the crop-margin entry - reeds ARE the water fringe. (3) Grass-tuft blade TIPS keep their few-feet lean allowance, exactly as at crop edges.


## The marsh margin: reed -> sedge/grass -> dry ground; woody at a reed edge is alder or willow, never pine - ACCURATE (researched 2026-08-26)

**Label: accurate** for the rule as drawn (grass alone grades into the reeds; no pine or brush in
the marsh); **the managed-margin reasoning below is unsourced and marked**. Researched 2026-08-26
on the GM's instruction after the T12 reviewer raised it (it had been recorded as a GUESS the same
day - the label was honest and the research was owed).

**What the record says.** The textbook hydrosere - the zonation from open water to dry land that
every lowland wetland shows in space - runs open water -> littoral -> **reed swamp** (*Phragmites*,
ヨシ) -> **sedge / wet meadow** (*Carex*, *Calamagrostis*, スゲ) -> **alluvial / swamp WOODLAND** ->
dry ground ([Packer et al. 2017, Biological Flora of *Phragmites australis*](https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/1365-2745.12797)).
In Japan the woody stage is **alder** (*Alnus japonica*, ハンノキ林) and **willow** (タチヤナギ群落):
the Kushiro Mire, mainly reed, is being invaded by alder where it dries, and the reed-sedge
community with a fluctuating water table is what resists that invasion
([Kushiro Mire, Ecohydrology & Hydrobiology 2014](https://www.sciencedirect.com/science/article/abs/pii/S1642359314000706));
a northern-Japan wetland classified into reed swamp, *Carex lyngbyei* marsh, and reed/*Calamagrostis*
grassland with *Spiraea* shrubs ([Otanoshike, Ecological Research 2004](https://link.springer.com/article/10.1111/j.1440-1703.2004.00644.x));
the national river-vegetation classification names ヨシ群落, マコモ群落 and タチヤナギ群落 as the
low-wetland communities and ハンノキ林 as the eutrophic-mire woodland
([MLIT river-environment vegetation classes](https://www.nilim.go.jp/lab/fbg/ksnkankyo/mizukokuweb/system/maegaki.files/shiryo2.pdf);
[Hotes, wetland ecosystem diversity](https://www.airies.or.jp/attach.php/6a6f75726e616c5f31322d316a706e/save/0/0/12_1-04.pdf)).
Northeast-China floodplains show the same ladder: emergent *Carex* marsh streamside, meadow marsh
at intermediate flooding, *Calamagrostis* wet meadow on the terrace
([PLOS One 2016](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0153972)).
**Red pine** (*Pinus densiflora*, アカマツ) - the scraggly pine our scrub draws - is a tree of
ridges, rocky slopes and well-drained poor soil, drought-tolerant, absent from wet lowland
([Gymnosperm Database](https://www.conifers.org/pi/Pinus_densiflora.php); [Mt. Takao museum](https://www.takao599museum.jp/treasures/selected/1419/?lang=en)).

**The decision it drives.** (1) Pines and dry brush inside the reeds: unsupported in every source -
the hard exclusion stands as ACCURATE. (2) Grass grading into the reeds over the margin: ACCURATE -
it is the sedge / wet-meadow zone of the hydrosere, drawn with the commons' blade glyph. (3) Woody
plants DO stand at a reed margin in the natural state - but they are alder and willow, a wet
woodland the engine has no glyph for. **Two supportable forms, so a KNOB, not a choice (Principle
XII):** a managed toe (reeds and sedge cut for thatch and fodder, the margin kept open - the current
form) versus an alder-willow carr along the toe (a distinct wet-woodland glyph, deliberately unlike
the dry scrub and the fengshui grove). Recorded as future work, not built here; when built, it is a
per-settlement roll like every other knob. *Unsourced, and labelled so:* that Edo-period reed beds
were mown (ヨシ刈り, 茅場) and that mowing is what kept the margin open - plausible, searched, not found.
**Grounds:** `settlements/vegetation.md` "Scrub NEVER scatters into a marsh"; `cover.py` `_in_soft`.


## Does scrub stand under a village wood? No - the floor was worked clear; grass fringes the edge (researched 2026-08-27, feature 133 T34)

The GM: *"Should scrubland overlap with forests? It seems like it shouldn't. Like, visually, it looks
weird. but maybe what is being represented is more accurate than what I am imagining."* It was not
more accurate. Two findings, one from land use and one from vegetation structure:

- **A satoyama wood's floor was kept clear, on purpose.** READ (Wikipedia "Satoyama"): "During the
  Edo era, young and fallen leaves were gathered from community forests to use as fertilizer in wet
  rice paddy fields"; "succession to dense and dark laurel forest is prevented by farmers that cut
  down these trees for firewood and charcoal every 15 to 20 years"; satoyama declined with "the
  drastic shift ... from charcoal and firewood to oil and the change from compost to chemical
  fertilizer". READ (the Geography Hub): leaf litter (*ochiba*) went to fertilizer, oak and chestnut
  were cyclically cut, and the cutting let sunlight reach the floor - so the floor's cover was
  herbs and flowers under a managed canopy, not brush. READ (Uehara et al. 2009, AGRIS): a managed
  coppice stand held 42 plant species against 23 in a stand left uncared for 50 years, the neglected
  one poorer in herbs - the abandoned wood is the different one. UNVERIFIED and softened: "the
  undergrowth was cut" (a search-summary phrase; the read sources say litter was gathered and the
  trees cut on a cycle). So brush and young pine under the crowns of an inhabited village's grove
  is the form the read record does not show; the floor is litter-raked ground under a canopy cut
  every 15-20 years.
- **The edge is a gradient, and it is grass.** Woodland-edge ecology describes the transition as a
  herb FRINGE outside, a shrub BELT, and the woody MANTLE - canopy closure falling from near-complete
  inside to partial at the boundary, and vegetation height stepping down from crown to shrub to
  herb. On a worked wood the shrub belt is what gets cut; the grass fringe is what remains, and it
  thins out under the first crowns.

**Rule** (`settlement/land/cover.py` `hinterland(soft_extra=)` -> `commons(soft=)`, the T12 marsh
machinery reused; `hamletgen/hinterland.py` computes the belt two stages early so the scrub can see
it; `tools/scatter_audit.py` holds a `grove` keep-out): brush dots and pines are hard-excluded from
every village-grove polygon; grass blades thin into it over the reed feather (46 units) and are gone
beyond it; crowns are the grove. Inashiro before: 2,688 blades, 158 dots, 11 pines inside the belt
polygon; after: 1,263 blades, all within the 46-unit fringe, no dots, no pines, audit 0 violations.
**REVISITED the same day (T35):** the first cut applied this to the windbreak only and left the coppice patches scattered through - the GM saw it at once. The record above never supported that split: the coppice IS the worked wood. Every woodland commons is now a soft keep-out too (the patches are scanned before the scrub is laid), and the audit adjudicates them.
Labels: the clear floor and the grass fringe ACCURATE; the 46-unit feather a DRAWING convention
shared with the marsh (one ramp for every soft edge, so two edges never read differently for no
reason). Not built, recorded: an abandoned-coppice shrub layer is a real second form for a
DESERTED settlement, never for an inhabited one.

**Sources (read):** Wikipedia "Satoyama"; the Geography Hub, "Japan's Satoyama Landscapes"; Uehara,
Shigematsu, Fujii, Iwamoto (2009), "Succession of shrub-layer vegetation and situation of wild
Rhododendron in the abandoned Satoyama coppice forest" (AGRIS record). **Pointers, not read:**
Wikipedia "Woodland edge"; EUNIS "Thermophile woodland fringes"; Springer "Forest Edges, Scrub,
Hedges and Their Herb Communities" (the mantle-and-fringe structure came from search summaries);
Forests 2025 on Okinawa homestead windbreaks. Corrected 2026-08-27 under T44.


## How is a coppice lot bounded? By ridge, stream and path - never by a page axis (researched 2026-08-18, revisited 2026-08-27, feature 133 T36)

The GM: *"those coppice Patches. basically it looked like little squares ... I want to make sure that
that is intentional and based on research rather than just happenstance because when we decided to
draw patches of trees, we just kind of unthinkingly drew a square."* It was happenstance, twice over.

**What the record says.** The village woods of the period were *iriai* commons - customary
common-property land held by the village and governed by its own rules on who might cut, when, and
how much (the usufruct the GM describes): firewood, forage and grass were the products, coppiced on
a 10-30 year cycle. Their boundaries were customary and were described by natural and worked
features - a ridge, a stream, a path - and the coppice itself sits on the slope break above the
paddy. Nothing in the record describes a coppice lot laid out as a surveyed rectangle; the
management was a matter of RULES over a wood, not of parcel lines on the ground. So a managed wood
is not evidence for a square - the GM's instinct was right.

**The one rectilinear form, and why it is not drawn here.** The *shinden* villages of the dry
Musashino upland (Kichijōji, settled by migrants after the 1657 Edo fire) were laid out as long strip holdings - a household's house,
dry fields and fuel wood (*zokibayashi*) in one strip, some over 1,000 m long - so THERE the wood is a
strip with straight sides. That is a settlement FORM (a planned dry-upland strip village with no
paddy at all), not a shape knob for a hillside coppice: it would change the houses, the fields and
the lanes together. Recorded as the second form for the day a dry-upland archetype exists; a
paddy-fan hamlet like Inashiro draws the hillside form.

**What the generator did.** The 2026-08-18 review pass reached the same finding and wrote it down
correctly ("there is no attested rectilinear woodlot"), then implemented it as a ROTATED RECTANGLE
with the plain square as the fallback for a tight seat - still rectilinear, and on Inashiro all
three parcels took the fallback (`rot 0`, `w == h`; twelve of twelve across the pool before that).
The ruling was only half drawn.

**Rule** (`hamletgen/hinterland.py` `_parcel_outline`): a parcel is a 12-vertex ring inside the
rolled ellipse, its radius wandering 0.80-1.00 of the ellipse's on two low harmonics seeded from the
parcel's own position - smooth, because a wood's edge wanders rather than serrates - and never
outside the reach the keep-outs were tested at. Area comes out ~85% of the ellipse's, so every size
rule still bounds it from above. Labels: the irregular, feature-bounded outline ACCURATE; the ring's
harmonic wobble and its 0.80 floor DRAWING conventions; the strip form a recorded knob-in-waiting.

**Sources:** iriai commons and their customary bounds (International Journal of the Commons,
Yamaguni district case study; the Indiana DLC "Village Commons in Japan"; Totman, *The Green
Archipelago*); coppice management and cycle (Takeuchi et al., *Satoyama: The Traditional Rural
Landscape of Japan*, Springer; Wikipedia "Satoyama"); the Musashino strip holdings (Kichijoji
history, Wikipedia "Kichijōji"; ; the founding year and the 1664 survey are NOT in that article
and are dropped as unverified).


## Bamboo: how common, where it stood, and how to show it (researched 2026-08-27, feature 133 T42 - a question, not yet a rule)

The GM: *"is there supposed to be bamboo on the reference hamlet? Why or why not? how common was it
for there to be bamboo in settlements such as this?"* - and the rendering problem behind it: a culm
is a few inches across, so at 1 px = 1 ft a bamboo stand has nothing to draw at true scale.

**How common: ubiquitous below the frost line.** READ (Wikipedia "Satoyama"): satoyama "contains a
mosaic of mixed forests, rice paddy fields, dry rice fields, grasslands, streams, ponds, and
reservoirs for irrigation", and by the 1960s were used as "rice fields, plowed fields, shifting
cultivation, grasslands, thatch fields, secondary forests for fuel, and giant bamboo forests". READ
(Wikipedia "Phyllostachys bambusoides"): madake's "long internodes and equally long fibres ... make
it ideal for traditional basket-weaving and the production of fans"; its sheaths wrapped food and
covered geta; it made shakuhachi. READ (PMC 5723622, the moso/madake range study): bamboo
"distribution remained south of 41°N, in areas that included plains and hilly regions of central
Honshu, as well as the coasts of northern Honshu"; stands "were not found at study sites where ...
mean annual minimum temperature was below -16.8°C", and "moso and madake bamboo distribution in
northern Japan depends primarily on temperature", agreeing with prior work "that moso bamboo cannot
withstand temperatures around or below -18 to -20°C". UNVERIFIED (403; from search summaries):
that a typical Edo farmstead kept "a grove where they could harvest bamboo" (Kids Web Japan); the
madake -15 C hardiness figure (PFAF); the broader list of uses (Highlighting Japan). So: a lowland
paddy hamlet in a temperate province has bamboo as a matter of course, and a cold upland one may
have none - that half is read. THAT is the axis of variance the
project wants: two attested forms, a knob per settlement (Principle XII).

**Where it stood.** Two places, both already in this record: (1) the homestead's own N/W strip -
the "shady, always damp" side of the yashiki given to the kitchen drain and service sheds - is
the bamboo strip (research/homesteads.md); and the dooryard's "persimmon and bamboo" stand IN the
sunlit yard; (2) the *take-yabu* (bamboo thicket) as its own stand at the village edge, harvested
like a coppice. Bamboo was NOT scattered one culm at a time through a mixed wood: a stand is a
clonal thicket, dense and monospecific, with a hard edge.

**What the generator does today (measured on Inashiro).** `_draw_grove` seeds every grove clump
with a species mix - 20% bamboo in the windbreak, 45% in a dooryard copse - and draws each bamboo
"tree" as one to-scale culm-and-top glyph about 6 ft across (a 2026-07 legibility decision that
already replaced a 6-culm clump with one). Inashiro carries 315 of them among 1,239 broadleaf and
conifer crowns: 311 inside the windbreak belt, 4 in the copse. At fit zoom they read as nothing -
pale dots in a dark belt - so the map does have bamboo and no reader can tell. Two things are wrong
with that at once: bamboo mixed at 20% through a cedar windbreak is not how bamboo grows (a stand,
not a seasoning), and a glyph the size of one culm cannot be seen at the sheet's scale.

**The convention the record suggests (not built; the GM's to name).** Japan's own topographic maps
solved exactly this: the GSI legend has a distinct bamboo-grove symbol (竹林), separate from the
broadleaf and conifer symbols, because a reader of a map must be able to tell the three apart at
map scale. So: (1) bamboo becomes a STAND with its own record (`bamboo_stands`, a polygon), drawn
with a stand-level glyph at legibility scale - the GSI culm-and-leaf mark or a hatch of paired culm
strokes with a leafy tick, in bamboo's pale yellow-green - a DEVIATION for legibility recorded like
the oversized well: the stand's POSITION and EXTENT to scale, the mark inside it symbolic;
(2) bamboo leaves the species mix of the windbreak and the copse (those become cedar/zelkova and
fruit stands, which is what they are); (3) a per-settlement knob rolls whether the hamlet has
bamboo at all (frost line) and where: the damp N/W strip of the cluster, a take-yabu at the field
margin's shady end, or both; (4) the gate learns `bamboo_stands` in the overlap matrix and a
legibility check (a stand under ~20 ft across does not read).

**Sources (read):** Wikipedia "Satoyama"; Wikipedia "Phyllostachys bambusoides"; "Detecting
latitudinal and altitudinal expansion of invasive bamboo Phyllostachys edulis and Phyllostachys
bambusoides in Japan", PMC 5723622. **Pointers, not read (403):** Kids Web Japan (the Shirakawa
farmstead); PFAF and Gardenia (hardiness); Highlighting Japan 2022 (uses); Wikimedia Commons
"Japanese Map symbol (Bamboo grove)" (not fetched; the symbol's existence is the claim). Corrected
2026-08-27 under the read-what-you-cite rule (T44).
