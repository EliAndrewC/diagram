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


## No canopy tree stands under another's crown (researched 2026-08-28, feature 134)

**Grounds:** `woods._crown_seat_clear` / `_canopy_seats` / `_crowns_near`, the grove clump's seat test in `_draw_grove`; `tree_crowns_not_subsumed`

**Evidence:** observed (the GM's own trees), derived from the density entry above

**Sources:** not recorded - the finding is the GM's observation and the entry above; add a key when the stand structure is re-consulted

The GM, on the interactive map's highlight: *"practically every tree might have a smaller tree
underneath it ... I understand that real life trees can, in fact, overlap with each other ... but I
don't see a single tree which is entirely subsumed within the branch structure of a different
tree."* Measured on Inashiro before the rule: 298 of 1,728 drawn crowns wholly inside another crown
(17%), 950 with their center more than halfway in. Nobody decided it: the wood lays trees on the
13 ft grid the density entry gives, jitters each by up to 42% of a step in x and y, and sizes
crowns 0.75-1.4x the 8.5 ft mean radius - so two grid neighbors could land 2-3 ft apart and a 6 ft
crown vanished under a 12 ft one; the belt's clumps pack tighter still and overlapped each other,
and nothing tested a crown against the crowns already drawn.

**The rule.** A crown is seated only if its center is outside every crown already on the map AND
no seated center lies inside it (`d >= max(r, r_other)`); edge overlap between that and `r +
r_other` stays, because neighboring canopies do interlace. What is removed is the tree drawn
wholly under a neighbor - in a real stand a suppressed understory stem, not part of the canopy
layer the map draws. Dominants seat first (largest crown first within a stand); across stands and
clumps the map's recorded crowns are the seed, padded by two emergent radii. Measured after:
Inashiro 787 crowns, 0 subsumed, 737 (94%) still touching a neighbor - the stand reads as closed
canopy at ~one crown per 13 ft grid cell, which is the density entry's own figure; the belt thins
where its clumps overlapped, which is where the doubled trees were. Class: **accurate** for the
rule (a canopy has one tree per crown), the density unchanged from the entry above.

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
- **The edge is a gradient, and it is grass.** READ (German Wikipedia "Waldrand", found by the
  `source-reader` run of 2026-08-27 when the English pointer turned out not to carry the terms):
  "Ein idealer, ausgewachsener Waldrand gliedert sich von außen nach innen in Krautsaum,
  Strauchgürtel und Waldmantel" - an ideal mature forest edge runs, outside to inside, herb fringe,
  shrub belt, forest mantle. SUMMARY-ONLY: the EUNIS E5.2 factsheet's "mantle ... and fringe"
  (the page 404s). NOT-FOUND and dropped: the "canopy closure near-complete inside to partial at
  the boundary" sentence the first record carried. On a worked wood the shrub belt is what gets
  cut; the grass fringe is what remains, and it thins out under the first crowns.

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
Springer "Forest Edges, Scrub, Hedges and Their Herb Communities"; EUNIS "Thermophile woodland
fringes" (404); Forests 2025 on Okinawa homestead windbreaks (MDPI 403). **Read by the
source-reader run (T45):** German Wikipedia "Waldrand" (herb fringe / shrub belt / forest mantle);
"Distribution and utilization of homestead windbreak Fukugi trees", PMC 7898781 - "Homestead
windbreaks are managed as part of a residence and are strips of trees planted and maintained to
alter wind flow and microclimate ... designed based on Feng Shui concepts in the Ryukyu Kingdom,
around 300 years ago". English Wikipedia "Woodland edge" was read and does NOT carry the
three-layer terms. Corrected 2026-08-27 under T44 and T45.


## How is a coppice lot bounded? By ridge, stream and path - never by a page axis (researched 2026-08-18, revisited 2026-08-27, feature 133 T36)

The GM: *"those coppice Patches. basically it looked like little squares ... I want to make sure that
that is intentional and based on research rather than just happenstance because when we decided to
draw patches of trees, we just kind of unthinkingly drew a square."* It was happenstance, twice over.

**What the record says.** The village woods of the period were *iriai* commons - customary
common-property land held by the village and governed by its own rules on who might cut, when, and
how much (the usufruct the GM describes): firewood, forage and grass were the products, coppiced on
a 10-30 year cycle. READ (IJC, the Yamaguni district study): "each of the 11
villages in Yamaguni district has its own unique institutions for managing its customary common
property forests", held by residents' associations with membership limited to qualifying
residents - the management was a matter of RULES over a wood. UNSOURCED (found by the T46 read):
the sentence that iriai boundaries were "described by ridge, stream and path", carried since the
2026-08-18 review pass and repeated in `hinterland.py`, is NOT in that article and no source for it
has been found; it stands as a summary-only claim of unknown provenance. What the read record does
give: nothing in it describes a coppice lot laid out as a surveyed rectangle, and the coppice sits
on the slope break above the paddy (the satoyama entries). So a managed wood
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

**Sources (read):** International Journal of the Commons, "External impacts on traditional commons
and present-day changes: a case study of iriai forests in Yamaguni district" (management by
village institutions; NO boundary description); Wikipedia "Satoyama"; Wikipedia "Kichijōji" (the
1000 m strip grants and dry fields; the founding year and the 1664 survey are NOT in it and are
dropped). **Pointers, not read:** the Indiana DLC "Village Commons in Japan"; Totman, *The Green
Archipelago*; Takeuchi et al., *Satoyama* (Springer). **Unsourced:** "described by ridge, stream
and path" (2026-08-18). Corrected 2026-08-27 under T44/T46.


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
withstand temperatures around or below -18 to -20°C". READ (the `source-reader` run, T45):
madake "Minimum Temp: 5°F (-15°C), Hardiness Zone: 7" (completebamboo.com), with other readable
growers giving -18 to -23 C - a spread, not a number; and no read source says new SHOOTS take
frost, only that "colder weather will likely cause frost damage to leaves and canes" (bambubatu),
so that clause is softened to "frost-tender at the margin". SUMMARY-ONLY, still: that a typical Edo
farmstead kept "a grove where they could harvest bamboo" (Kids Web Japan - the page and its
archives all 403; no corroborating snippet found, so it carries no weight here); the broader list
of uses (Highlighting Japan). So: a lowland
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

**BUILT (feature 133 T47, GM 2026-08-27: "make that change in the manner that you had previously
proposed").** The four points above, as built: (1) `bamboo_stand` (settlement/homestead_parts.py)
records `M['bamboo_stands']` - a polygon whose position and extent are to scale - and draws a
stand-level glyph: paired culm strokes with a leafy fork on a 7 ft jittered grid, pale yellow-green,
no fill. (2) Bamboo left the grove species mix (`_draw_grove`: windbreak 20% -> 0, dooryard copse
45% -> 0). (3) The `bamboo` knob (settlement/_knobs.py; `BAMBOO_FORMS` in hamletgen/consts.py):
none / homestead / thicket / both, rolled per settlement; `hamletgen.bamboo_seats` scans a seat for
each form - the homestead stand on the cluster's shady side (drawn as its NORTH, the side the house
shades; the record's "N/W strip" read that way), the thicket at the field margin's shady end - and
`stage_bamboo` draws them after the belt; the scrub keeps out of them (T34's soft keep-out).
(4) The gate: `bamboo_declared_and_drawn`, `bamboo_stands_legible` (20 ft floor), and
`bamboo_stands_clear_of_paddies`; the overlap matrix and the caption groups know the record; the
scatter audit treats a stand as a wood. Inashiro rolled `homestead`: one stand of 46 x 29 ft and
25 marks north of the cluster; 315 invisible culm glyphs became 0.
Labels: bamboo's presence below the frost line and its two places ACCURATE (read); the stand
glyph a DEVIATION for legibility (the GSI convention; the marks are symbolic, the extent is not);
the sizes (48 x 34 and 84 x 58 ft) and the 7 ft mark pitch DRAWING conventions; "north = the shady
side" a READING of the record's N/W, recorded as such.

**REVISITED (feature 133 T48, GM 2026-08-27): household bamboo, per farmstead - which side, and how
common.** The GM asked whether a farmstead's own bamboo always stood to the north-west and whether
every farmstead had one. A `source-reader` pass (27 fetches) answered what could be read:

- WHERE (READ, ja.wikipedia "屋敷林"): on the Tonami plain "南側には蔵や納屋などがあり、無花果や葡萄、
  柿などの果実がなる植物や竹などが植えられていた" - storehouses and barns on the SOUTH side, and there
  the fruit trees and the bamboo; and separately, "河川の近い家や水害の多い地域では、防水用として
  ハンノキや、根を張る竹を植えて土壌の流出を防いでいる" - by rivers and in flood-prone ground, bamboo (and
  alder) planted for its roots. READ (tsuijimatsu.com): the kainyo "はスギが中心で、ほかにアテ（アスナロ）
  ・ケヤキ・カシ類・竹・柿・栗などで" - cedar central, bamboo among the secondary species. SUMMARY-ONLY:
  the grove as a whole faces the local harmful wind - north and west (Isawa, Iwate; Hikawa, Shimane),
  west (Iide, Yamagata), south and west (Tonami) - a regional table the reader saw in a search snippet
  and could not fetch. NOT CONFIRMED: the earlier record's "N/W strip ... kitchen drain" sentence (the
  1996 Tonami model homestead, research/homesteads.md) - no fetched source carries it. So the SIDE is
  two-formed at least (with the storehouses; at the wet edge; on the wind side) and is ROLLED per
  farmstead, weighted toward the back of the house and the shed's side (Principle XII: two supportable
  forms become a knob, here a per-house roll).
- HOW COMMON (READ, Visit Toyama): on the Tonami plain "each house has been surrounded by homestead
  woodland ... over 7,000 houses", with "cedar, Japanese zelkova, and bamboo ... used as materials for
  building new houses as well as materials for various everyday tools"; READ (tsuijimatsu.com):
  "竹は日常生活の資材として重要なものでした". NOT-FOUND: any share of farmsteads keeping bamboo, and any
  source distinguishing household bamboo from the communal take-yabu by number. So the presence rate
  is a GUESS - `HOUSEHOLD_BAMBOO_PREVALENCE` 0.6, "one of several secondary species" read as common but
  not universal, set like the shed's - labeled as such.
- BUILT: `hamletgen.household_bamboo` seats a 22 x 16 ft strip per farmstead that rolls one, side
  rolled (back 0.45 / shed side 0.30 / windward 0.15 / other flank 0.10), reserved with the sheds and
  gardens so the lanes and wells keep off it, drawn by `stage_bamboo` with the stand glyph; the knob's
  `homestead` value now means these strips, `thicket` the one communal stand, `both` both. Inashiro
  (rolled `homestead`): 8 of 15 farmsteads keep a strip. The legibility floor is the short axis (14 ft).
  On the way: the notice board's roadside re-seat left the first board's and caption's INK behind when
  it popped their records (two boards, one record), stood the board 16 ft off its lane against T13's
  6 ft verge, and could align a board to a lane that was not its nearest - three latent defects the
  reservations exposed, fixed in `hamletgen/frame.py`.

**Sources (read):** ja.wikipedia "屋敷林" (the Tonami south-side passage; bamboo at the wet edge);
築地松景観保全対策推進協議会, tsuijimatsu.com/62 (kainyo species; bamboo as daily material); Visit
Toyama, "Sankyoson" (7,000 farmsteads each in its grove); Wikipedia "Satoyama"; Wikipedia
"Phyllostachys bambusoides"; "Detecting latitudinal and altitudinal expansion of invasive bamboo
Phyllostachys edulis and Phyllostachys bambusoides in Japan", PMC 5723622; completebamboo.com, bambubatu.com and practicalplants.org on
madake hardiness (T45 run); ridgelineimages.com "Reading GSI Topographic Maps" - the bamboo forest
(竹林) symbol listed as its own category beside broad-leaved (広葉樹林) and coniferous (針葉樹林)
forest, and distinct from the bamboo-grass (笹地) symbol (T45 run). **Pointers, not read (403):**
Kids Web Japan (the Shirakawa farmstead); PFAF and Gardenia; Highlighting Japan 2022 (uses); the
regional wind-side table for the grove (search snippet of 屋敷林 / Satte city); the Osaki igune
dwarf-bamboo composition (Springer, paywalled - and DWARF bamboo is not a stand). Corrected 2026-08-27 under the read-what-you-cite rule (T44) and the source-reader run (T45).
