"""The overlap taxonomy's kinds: which manifest keys are footprints, targets, lines or exempt, their caption groups, and each
key's overlap class (split from `overlap/taxonomy.py` at 1,000 lines - feature 444).

Research: the kinds' plumbing - NONE: each table is claimed at its own docstring
"""

_OVERLAP_STRUCTS = (
    "theater_stage",  # a LIST since 2026-08-10 (dict manifests normalized at gate entry)
    "houses",
    "terraces",
    "precinct_halls",
    "buildings",
    "flophouses",
    "cemeteries",
    "mausoleums",
    "cremation_grounds",
    "ossuaries",
    "ministries",
    "fire_towers",
    "drum_towers",
    "byres",
    "retirement_houses",  # the retirement house (inkyoya), a second roof of its farmhouse's family in the same yard (269 B42)
    "kosatsuba",
    # the justice works (research/questions/0191-execution-and-punishment-grounds-keijo.html)
    "punishment_spots",
    "execution_grounds",
    "boundary_markers",
    # the trade works (GM 2026-07-24, research/questions/0183-shops-and-trades-in-towns-and-villages.drawing.html)
    "breweries",
    "dye_yards",
    "lumber_yards",
    "oil_presses",
    "pawnshops",
    "bathhouses",
    "kilns",
    "farriers",
    "tanning_yards",
    # the charcoal district's trade works (feature 016). For OVERLAP purposes these are ordinary
    # solid premises like any other; what is special about them is a SEPARATION rule each
    # (refining_forge_stands_off_dwellings; the charcoal yard's 30 ft gap was retired by feature 280 M104, a modern figure),
    # which is a different shape and lives in its own check rather than in this registry.
    "charcoal_yards",
    "refining_forges",
    # martial training (GM 2026-07-25): the state hall and the private dojos - solid compounds like
    # any other civic/private premises, so they overlap nothing
    "martial_halls",
    "dojos",
    # the domain capital's castle (feature 019). Recorded as a LIST precisely so this registry can
    # see it: the first cut recorded a bare dict, which this check enumerates past in silence, and
    # the Imperial road duly ran straight through the largest structure on the map with a green
    # gate. Its towers are outer-wall furniture and are solid in their own right.
    "castles",
    "castle_towers",
    # the capital's wharf granaries (feature 020): per-STORE records precisely so this registry
    # and the extractor see each kura - the legacy town M['granary'] is a bare dict special-cased
    # in solid_structs, which is the record shape feature 019 proved invisible.
    "granaries",
)
"""Research: solid footprints - CONVENTION: a solid feature's drawn footprint overlaps nothing it is not exempted for"""

# `shrines` duplicates the primary religious halls (shrine_hall records both), so it rides along with
# `religious`; both are halls that structs must AVOID, gated by no_structure_on_religious.
_OVERLAP_TARGETS = ("manors", "religious", "shrines", "gate_structs", "docks")
"""Research: halls kept clear - CONVENTION: no structure drawn on a manor, hall, gate complex or dock"""

_OVERLAP_LINEAR = (
    "fields",
    "fallow_patches",
    "flower_fields",
    "streams",
    "channels",
    "town_streets",
    "alleys",
    "lanes",
    "wards",
    "ponds",
    "pastures",
    "forests",
    "commons",
    "dry_plots",
    "marshes",
    "canals",
    "roads",
    "crescent_ponds",
    "towpaths",
    "quays",  # the revetted bank face at a wharf - a LINE feature, classified WAY like the towpath
    "aqueducts",
)  # linear / area features structs avoid (canals = the cargo canal; roads = the multi-road list, same ground the single M['road'] covers; crescent_ponds = the fengshui 半月塘 focal pond, reserved as a placement keep-out so the cluster packs around it; towpaths = the riverbank haulage path and aqueducts = the open supply cut, both feature 020 - ground a structure must keep off)
"""Research: ground kept clear - CONVENTION: no structure drawn on a field, water, way, pond, cover or wood"""

_OVERLAP_EXEMPT = {
    "drawn_channels": "z-order record of the drawn field-channel strokes (post-clip geometry + stroke widths w0/w1 + bedz), not a placement feature: the strokes duplicate the field_ditches/channels ground the structs already avoid, and their mouths deliberately touch the pond/moat/stream they join (pond_fill_covers_channel_mouths and water_channels_join_not_cross read this record - it is the only source that says what was actually stroked, and how wide)",
    "storehouses": "merchant kura drawn as an annex deliberately abutting its shop",
    "row_street_plans": "a row village's PLANNED street lines (feature 291, `hamletgen/homesteads/rows.py`): bookkeeping the row rules read - the street drawn from each is a `lanes` record the matrix already reasons about",
    "row_holdings": "a row village's far-row holdings as reserved (feature 291): bookkeeping the row rules read - the ground drawn is the `dry_plots` records the matrix already reasons about",
    "borders": "a drawn CLAN/jurisdictional border is a LINE OF LAW, not a physical object - it has no footprint (no w/h), reserves no ground and blocks nothing. Being overlapped is the POINT: a frontier magistracy stands its wall ON the line so the border runs across the parley-room floor (the Mode A ubame-magistracy sheet), and the period PHYSICAL marker - an earthen mound, as at the Nanbu-Date boundary - is deliberately NOT what this draws, precisely because a mound would be a structure everything then had to stay clear of",
    "farm_sheds": "a farmstead's grain-storehouse kura drawn as an annex abutting its own farmhouse - on the west wall of a scattered farmstead, the shaded north wall in a clustered village (0040; farm_sheds_attached verifies the attachment)",
    "pig_sties": "a pig shed ON a pond dike, on the bank itself - set in from the plot's edge by half the bank's width - by construction (feature 150 A3; 0025)",
    "farm_fixtures": "a farmstead's small fixtures - privy, wood shed, manure heap, bath room, chicken coop, pig sty, household shrine - each seated on its own farmstead near its farmhouse, against a wall or a set step off it, by the placer, which tests the seat against every placed footprint, lane, paddy and water (feature 133 T53-T59; farm_fixtures_attached verifies the attachment)",
    "scrub_pines": "the scrub's hill pines as (x, y, r) records for the sun rule (feature 310): bookkeeping - their ink is the scrub's own marks, whose extents the commons already keep off every footprint",
    "bamboo_marks": "every inked bamboo culm mark as (x, y, r) records for the sun rule (feature 315): bookkeeping - the ink is the clump's own group, ruled on there",
    "planted_trees": "the willows and fruit trees a dike's planting drew before the plots, as (x, y, r) records per planted run (feature 310): bookkeeping - their ink is the dike's planted string, on the dike's own keep-out",
    "pond_bank_trees": "the trees on a tail pond's planted bank as (x, y, r, kind) records (feature 385 T08, 0061): bookkeeping - their ink is the crowns recorded in tree_crowns, seated off every roof, wellhead, tread, crop and water",
    "persimmons": "the yard persimmon: a crown record (x, y, r) whose ink is also in tree_crowns, which structures_clear_of_trees tests; the placer keeps the trunk off every footprint (feature 133 T57)",
    "threshing_yards": "a farmstead's threshing/drying yard drawn as an annex abutting its own farmhouse",
    "gardens": "a farmstead's dooryard kitchen garden drawn as a plot abutting its own farmhouse",
    "groves": "a farmstead's windbreak grove (yashikirin) drawn along its plot's edge on the sides its settlement rolls - two, three or all four (0028) - its windward stand about 24 ft off the house, only the thinner bands beside it (0036)",
    "merchant_estates": "a walled court AROUND an inner building that is itself an overlap-checked struct",
    "wells": "a small well-head dropped into the open gaps between dwellings (its nominal footprint may kiss a dense-city building)",
    "wall_towers": "guard towers stand ON the city wall - an intentional overlap - and clear of the interior",
    "bridges": "a bridge spans a stream/moat to carry a road over it (intentional water + road overlap)",
    "kido": "a ward gate sits ON the ward fence at the point a lane passes through it",
    "inspection_stations": "an inspection post sited AT the city gate, part of the gate complex (overlaps the gate furniture)",
    "water_gates": "the shuimen arch stands ON the city wall over its canal - intentional, like the kido on its fence",
    "weirs": "the bar across the brook at the intake sits ON the water by definition - a weir IS a structure in a stream, and the head race leaves the bank at the same point (feature 230)",
    "washing_places": "a footing of steps down a bank to the water stands at the waterline by definition (feature 374 wave 150, 0065), seated where the matrix admits it",
    "sluice_gates": "the field-channel intake/outfall board sits ON its channel at a water-to-water handoff (moat/river tap -> comb canal, drain -> culvert) - the control structure IS the junction",
    "jetties": "planked mooring fingers running out over the river water, like bridge decks",
    "log_booms": "a cabled chain of floating logs holding rafted timber against the bank - it FLOATS on the river, so overlapping the water is the whole point, exactly as a jetty deck does",
    "field_ditches": "in-field irrigation ditches (main/laterals/drain) - water lines drawn ON the paddy, validated by water_channels_obtuse_turns + field_ditches_terminate, not solid structures",
    "village_groves": "the COMMUNAL fengshui windbreak (back-village belt / water-mouth cluster / the dooryard copse, which draws no bamboo - 0071) - vegetation drawn LAST in open ground at the cluster margins; a copse may abut a house, validated by the village_windbreak_* checks",
    "bamboo_stands": "a BAMBOO STAND (take-yabu) drawn as a stand-level glyph of its own beyond the cluster's back row (0071: a farm's bamboo is a stand of its own) - vegetation drawn LAST in open ground; the stand's extent is to scale, its marks symbolic",
    "districts": "declarative fabric districts (feature 021), the quarter overlay's sibling - named pack regions validated by capital_districts_declared / capital_rank_gradient, never drawn",
    "precincts": "a sovereign-temple precinct RESERVATION (feature 021) - a region record like a district; its drawn content is precinct_halls, which carry their own classes",
    "quarters": "declarative zoning overlays (feature 006), not solid structures - they intentionally contain buildings and are validated by the city_quarters_* / per-quarter density checks",
    "mills": "a water mill (水磨) focal feature drawn BESIDE its watercourse with the wheel dipping into the drain/stream - an intentional water-adjacency like a bridge/jetty; reserved in open ground (self.placed) so it does not overlap dwellings",
    "field_ponds": "feature 012: a low-pocket pond sunk INTO one paddy plot, the field tiling around it - drawn ON the paddy like field_ditches, validated by paddy_features_match_archetype + field_ponds_sunk_into_one_plot",
    "field_rocks": "feature 012: a bedrock outcrop the terrace risers wrap around, drawn ON the paddy - validated by paddy_features_match_archetype (bedrock archetypes only)",
    "field_graves": "feature 012: a rare grave in the fields (calibrated liberty), an island the paddy tiles around or in a plot's corner against its bunds, the bund carried round it, on valley, terrace or strip paddy alike (0008) - drawn ON the paddy, validated by paddy_features_match_archetype",
    "clearings": "swept-ground records (the shrine keidai / torii sando collar / grave collar), not drawn features at all - they carry the cover-ordinal bookkeeping for scatter_respects_swept_clearings and deliberately CONTAIN their sacred/funerary feature",
    "stable_yards": "the gate stables' beaten-earth working yard (s._stable_yard) - a feathered ground scatter (hitching rails, trough, dung heaps, litter; no animal glyphs - the maps render no humans or animals) that deliberately SURROUNDS its stables and fills the open pocket; a ground record, not a keep-clear structure (validated by stables_have_yards). `troughs` counts the watering point's troughs and `troughs_at` records the cluster center, which must hug a wellhead (validated by stable_troughs_beside_well); `troughs_box` and `rails` record the furniture's DRAWN extents, which must not intersect each other or any wellhead (wells_troughs_rails_clear_of_each_other)",
    "dikes": "the reclaimed-polder PERIMETER dike earthwork band (s.perimeter_dike) - a walked, lived-on planted bank the village lines and the feeder/drain channels + footbridges cross by design; a broad ground feature, not a keep-clear structure (validated by polder_dike_is_earthwork)",
}
"""Overlap exemptions.

Research:
    annexes abut their house - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html, research/questions/0040-farm-storehouses-kura.drawing.html, research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the kura against its own farmhouse (west wall scattered, north wall clustered); the grove along the plot edge on its rolled 2-4 sides, its windward stand about 24 ft off the house and only the thinner bands beside it
    yard, garden and fixtures beside the house - research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html, research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html, research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html, research/questions/0044-baths-on-the-farm-furo.drawing.html, research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html, research/questions/0049-pigs-and-ducks-in-south-china-rice-villages.drawing.html: the yard drawn beside its house, the bed beside the house on the sides 0038 gives, fixtures seated on the plot near the house, the bath joined to the main house, the wood shed a ken beyond the wall's clear strip, about 9.5 ft off a wall, the pig sty against a wall of the house or an outbuilding
    yard persimmon near its house - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: in front of the house or behind it, its crown's edge within about 30 ft of the house; exempt here because its crown is tested as a tree crown and the placer keeps its trunk off every footprint
    pig sty on the dike - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html: exempt because it stands on the pond dike, on the bank itself, half the bank's width in from the plot's edge, not over the water
    wellhead among the houses - research/questions/0196-communal-wells-ido.drawing.html: in the gaps between dwellings
    border as a line - DEVIATION research/questions/0083-clan-borders-and-their-markers.drawing.html: a line of law with no footprint, which a frontier magistracy's wall stands on (the parley room with the line across its floor); no mound drawn, nothing keeps clear
    built on what it serves - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html, research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html, research/questions/0179-water-gates-and-sluices-shuimen.drawing.html, research/questions/0160-city-wards-and-the-gates-that-shut-them-at-night-machi-kido.drawing.html, research/questions/0176-wharves-and-landings-piers-quays-and-stepped-landings-kashi-gangi.drawing.html, research/questions/0148-towers-along-the-city-wall-mamian.drawing.html, research/questions/0210-timber-yards-and-log-booms-kiba.drawing.html, research/questions/0065-washing-places-at-the-waters-edge.drawing.html: bridges, weirs, gates, jetties, towers, booms, washing places on their banks
    mill beside its stream - research/questions/0064-water-mills-suisha.drawing.html: on the bank beside its watercourse, its wheel dipping into the water
    in-field ponds, rocks and graves - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: each sunk into one paddy plot, the field tiling round it, drawn on the paddy
    copse and bamboo against a house - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html, research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a clump stands against a house, never on it, so the village groves and bamboo stands, drawn last in open ground, may abut a house; the copse spread through the gaps between the houses, the belt on the windward north and west; the copse draws no bamboo, the thicket a stand of its own
    stable yard round its stables - research/questions/0195-stable-yards-and-watering-troughs.drawing.html: a ground scatter of beaten earth that surrounds its stables and fills the open pocket
    polder dike crossed - research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: a walked bank the lanes cross, and the channels through a cut in it, with their footbridges
    in-field ditches - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.drawing.html: drawn on the paddy
    inspection post on the gate - research/questions/0147-city-and-town-gates-the-opening-the-gate-tower-and-the-crossing-of-the-moat-chengmen.drawing.html: may overlap the gate furniture
    merchant storehouses - research/questions/0155-rich-merchants-walled-houses-and-their-fireproof-storehouses-kura.html: exempt as an annex abutting its shop
    merchant estate court - research/questions/0155-rich-merchants-walled-houses-and-their-fireproof-storehouses-kura.drawing.html: a walled court round its inner building, which is itself an overlap-checked footprint
    bookkeeping records - NONE: districts, quarters, precincts, clearings, row plans and tree records
"""

# ---- label classification registry (GM 2026-07-26) --------------------------------------------
# The sibling of _OVERLAP_STRUCTS, for the OTHER thing a new feature has to be protected from: a
# CAPTION landing on it. labels_clear_of_other_buildings used to build its victim list from ~22
# hand-written manifest keys, which is the same bug the keep-clear contract retired - and it had
# already fallen behind twice over. When the martial hall went in, `martial_halls` and `dojos` had
# to be remembered into it; a day later the execution-ground feature landed and `punishment_spots`,
# `execution_grounds` and `boundary_markers` were not in it either, so a foreign caption could sit
# squarely on an execution ground with the gate green.
#
# Now every solid feature is classified here exactly once. The GROUP name is what a caption must
# NAME to be allowed to cover the feature - and because the group name is the caption word, that
# permission is derived rather than hand-listed too (see _label_allows).
_LABEL_GROUP = {
    # A BYRE IS EXEMPT FROM ITS OWN HOMESTEAD'S CAPTION, NOT FROM EVERY CAPTION (settlement-review, Kashikawa,
    # feature 145). It sat in _LABEL_EXEMPT on the premise that "a caption cleared for the house is cleared for
    # it" - true where a farmhouse carries a caption, and false at hamlet tier, which captions no farmhouse at
    # all: Kashikawa's ONE caption belongs to a notice board 20 ft away and was drawn through a byre's roof,
    # with the gate green by construction. Under the "farmhouse" group a farmhouse caption may still cover it
    # and nothing else may.
    "byres": "farmhouse",
    "retirement_houses": "farmhouse",  # 269 B42: a small dwelling a ken or two off its own farmhouse, in the same homestead as a byre
    "pig_sties": "sty",
    "quays": "quay",
    "theater_stage": "theater",
    "granaries": "granary",
    "terraces": "terrace",
    "flophouses": "flophouse",
    "log_booms": "log boom",
    "religious": "temple",
    "precinct_halls": "temple",
    "ministries": "ministry",
    "governor_mansion": "governor",
    "gate_structs": "gate",
    "merchant_estates": "merchant",
    "manors": "estate",
    "cemeteries": "funerary",
    "mausoleums": "funerary",
    "cremation_grounds": "funerary",
    "ossuaries": "funerary",
    "breweries": "brewery",
    "dye_yards": "dye works",
    "lumber_yards": "lumber yard",
    "oil_presses": "oil press",
    "pawnshops": "pawnshop",
    "bathhouses": "bathhouse",
    "kilns": "kiln",
    "farriers": "farrier",
    "tanning_yards": "tanning yard",
    "charcoal_yards": "charcoal yard",
    "refining_forges": "refining forge",
    "drum_towers": "drum tower",
    "martial_halls": "martial hall",
    "castles": "castle",
    "castle_towers": "castle",
    "dojos": "dojo",
    "fire_towers": "fire tower",
    "kosatsuba": "notice board",
    "punishment_spots": "punishment ground",
    "execution_grounds": "execution ground",
    "boundary_markers": "boundary marker",
    "houses": "farmhouse",
    # a WELLHEAD is a drawn glyph a caption can bury, but it is _OVERLAP_EXEMPT (a well may kiss a
    # dense-city building), so it fell outside the classification ratchet - which iterates the
    # overlap registry - and a caption on a wellhead was invisible. Found by settlement-review 2026-07-26.
    "wells": "well",
    # THE SAME HOLE, ONE CLASS OVER (settlement-review 2026-07-27). The ratchet at
    # `labels_cover_every_feature` iterates the overlap registry, and `matrix_extents` SKIPS the
    # permissive classes outright - so every key registered "FIXTURE" is invisible to it and can go
    # unclassified for labels for ever. On Minami that let two captions ("punishment ground" and a
    # "dojo") be drawn straight through a ward kido's guard post, each biting a notch out of its
    # outline so a clean square rendered as two disconnected corners, with the gate fully green.
    # A kido and a dock are both solid drawn glyphs a caption can bury, so both are victims here.
    # (A concurrent session has since moved `kido` off the POINT FIXTURE row - it always had a
    # footprint - which fixes its overlap handling but not this: label classification is a separate
    # registry, and an unclassified key stays invisible to captions whatever its overlap class.)
    "kido": "ward gate",
    "docks": "dock",
    # a TORII ARCH, likewise (GM 2026-07-27: an arch must "never be covered by the 'temple of X'
    # label"). Its group word appears in no caption any map draws, so NOTHING may cover an arch -
    # correct, because a sando's whole legibility is the ROW it makes, and a caption laid across it
    # breaks the row into unrelated marks. The commonest offender was the hall's OWN caption, which
    # wants the same ground the approach does. See the torii branch in the victim builder: an arch is
    # recorded as a bare [x, y, z] triple, so the registry loop cannot pick it up on its own.
    "torii": "torii",
}
"""Caption groups.

Research:
    a caption covers its own group - research/questions/0243-what-labels-may-cover-and-how-districts-are-named-on-town-and-city-maps.drawing.html: the group word a caption names, and nothing else; the graveyard, cremation ground, mausoleum and ossuary one funerary group, and a samurai caption naming the estates (`manors`), each named by any of their words (`labels.obstacles.GROUP_WORDS`)
    an arch is never covered - CANON: the GM's ruling of 2026-07-27, an arch is never covered by the 'temple of X' label; the torii group word is in no caption
"""

# STILL UNCLASSIFIED, and known to be (2026-07-27): the other six FIXTURE keys - `bridges`,
# `water_gates`, `sluice_gates`, `inspection_stations`, `jetties`, `wall_towers`. They are drawn
# glyphs a caption could bury exactly like the two above, and nothing will tell us when one does,
# because the ratchet cannot reach the permissive classes. Left open deliberately rather than
# half-closed: adding them is one line each, but each may fire on a finished map in the pool, and
# that is a fix to make with the regen budget to see it through - not a line to add blind.
# `buildings` is the one key whose group is not fixed: each record carries its own `kind`, and _grp
# folds those kinds into groups (samurai_large -> samurai, and so on).
_LABEL_BY_KIND = ("buildings",)

_LABEL_EXEMPT = {
    "districts": "a declared district is a REGION overlay like a quarter - it draws nothing, so there is nothing under it for a caption to bury",
    "weirs": "a bar five feet thick across a seven-foot brook, at the field's head where no caption is drawn - there is no room under it to bury and nothing captions it",
    "washing_places": "a footing four feet wide at the water's edge that nothing captions - there is no room under it to bury",
    "precincts": "a reservation region, never drawn - the halls inside it are the drawn features",
    "borders": "a jurisdictional line has no footprint to protect - there is nothing under it to be buried by a caption, and its own caption is drawn in the top layer so no ground feature can paint over it",
    # CORRECTED 2026-08-18: this said "an ANNEX abutting its own farmhouse (draft_byres places it
    # against the wall)", which the placer had not done for a long time - it spirals a DETACHED shed
    # out past the homestead and spreads the set by minimax across the whole cluster. A registry
    # comment that describes code which no longer exists is worse than none: it is the reason the
    # form was never questioned. Since the `byre_form` knob both forms are real, so the entry states
    # the property that holds in EITHER - the byre stands in the homestead ground among the houses,
    # near enough that a caption cleared for the house is cleared for it - and the form-specific
    # geometry is gated by `byres_stand_in_their_declared_form` instead of asserted here.
}
"""Research: nothing to bury - CONVENTION: undrawn regions, a weir no caption names, a line of law"""

_LABEL_CLASSIFIED = set(_LABEL_GROUP) | set(_LABEL_BY_KIND) | set(_LABEL_EXEMPT)

_LABEL_GROUPS = frozenset(_LABEL_GROUP.values())

# ============================ THE OVERLAP MATRIX (feature 017) ============================
# WHY THIS EXISTS (GM 2026-07-26). `_OVERLAP_STRUCTS` models **structure x hazard** - a building
# against a road, wall, stream, torii. It has no notion of **ground x ground**, which is where
# `dry_plots x water` lives, so a dry crop field could sit in a stream with the gate fully green
# while a manor on a road got its own bespoke check. The GM's words: "it's like playing whack-a-mole
# where every time we make a new map, I see a few more things which have never happened to overlap
# before but now they do... I'd like to make sure our automated checks aren't just individually
# listing 'X cannot overlap with Y, N cannot overlap with M'."
#
# So: every geometric key gets ONE CLASS and a class-by-class policy decides every pair at once.
# FORBIDDEN BY DEFAULT; every permission carries its reason. Adding a feature is one line here.
OVERLAP_CLASS: dict[str, str] = {
    # --- TESTED CLASSES -------------------------------------------------------------------------
    # SOLID - an exclusive built footprint
    **{
        k: "SOLID"
        for k in (
            "houses",
            "terraces",
            "precinct_halls",
            "buildings",
            "flophouses",
            "manors",
            "religious",
            "shrines",
            "ministries",
            "merchant_estates",
            "cemeteries",
            "cremation_grounds",
            "ossuaries",
            "mausoleums",
            "fire_towers",
            "drum_towers",
            "martial_halls",
            "dojos",
            # the castle and its outer-wall towers (feature 019). SOLID like any other walled
            # compound: nothing may be built on the works, and no way may run through them.
            "castles",
            "castle_towers",
            "kosatsuba",
            "punishment_spots",
            "execution_grounds",
            "boundary_markers",
            "theater_stage",
            "wells",
            "breweries",
            "dye_yards",
            "lumber_yards",
            "oil_presses",
            "pawnshops",
            "bathhouses",
            "kilns",
            "farriers",
            "tanning_yards",
            "charcoal_yards",
            "refining_forges",
            # the capital's wharf granaries (feature 020) - kura rows, one record per store
            "granaries",
        )
    },
    # A ward gate's GUARD BOX is a small building on the verge beside the gateway, not part of the
    # opening: it is SOLID and rides none of the gate's fence/roadbed mounts (see matrix_extents,
    # which splits it out of `kido`). Not a manifest key - it is extracted from the gate's own
    # `parts` - so nothing reads M['kido_guard_box'] and the classification ratchet never sees it.
    "kido_guard_box": "SOLID",
    # The rampart and the torii arches are SOLID: things must keep off them. All of these were
    # UNCLASSIFIED until 2026-07-26 because the ratchet inspected only keys whose records are lists
    # of DICTS - a wall is a bare list of points, a torii a bare [x, y, z] triple - and a ratchet
    # that enumerates one record shape has exactly the blindness this feature exists to abolish.
    # `lane` (singular) is the same plural/singular trap that had already hidden `marshes` and `roads`.
    **{k: "SOLID" for k in ("wall", "torii")},
    # GROUND - cultivated / engineered ground worked AS A SURFACE: anything standing in it ruins it
    **{k: "GROUND" for k in ("dry_plots", "flower_fields", "fallow_patches")},
    # PADDY is GROUND in principle but RECONSTRUCTED in practice: a plot's polygon is not stored, so
    # its extent is rebuilt from recorded spans as an oriented bounding box (see matrix_extents).
    # That is good enough to reason with and NOT good enough to accuse another feature with, so
    # paddy is permissive HERE and the precise paddy rules stay authoritative -
    # harvest_yards_clear_of_paddies, structures_clear_of_dry_plots, streams_avoid_fields,
    # tanning_yard_clear_of_fields and fields_clear_of_road all test real geometry.
    "fields": "PADDY_RECONSTRUCTED",
    # `aqueducts` is WATER (feature 020): the open supply cut is a seam on the ground exactly like
    # a channel, and the shared crossing source (bridge_crossed_waters) already demands a deck of
    # any way over it. `towpaths` is a WAY: a beaten path things keep off, however unlike a road
    # it is drawn.
    **{k: "WATER" for k in ("streams", "channels", "field_ditches", "canals", "pond", "moat", "aqueducts")},
    **{k: "WAY" for k in ("road", "roads", "town_streets", "alleys", "lanes", "towpaths", "quays")},
    # ANNEX - belongs to a named parent and abuts IT (and nothing else)
    **{
        k: "ANNEX" for k in ("gardens", "threshing_yards", "farm_sheds", "storehouses", "byres", "retirement_houses", "farm_fixtures", "persimmons", "pig_sties")
    },  # pig_sties stand ON the pond dike by construction (feature 150)
    # --- PERMISSIVE CLASSES (never tested; each row below records WHY) ---------------------------
    **{k: "COVER" for k in ("commons", "pastures", "marsh", "marshes")},
    "quarters": "OVERLAY",
    "districts": "OVERLAY",
    "precincts": "OVERLAY",
    # A WARD IS NOT A QUARTER. A quarter is a zoning word; a ward is an enclosure with no wall round it,
    # sealed by a FENCE with a gate at every crossing (research/questions/0160-city-wards-and-the-gates-that-shut-them-at-night-machi-kido.drawing.html), and that fence
    # is a physical barrier everything except its own kido must stand clear of. Classed OVERLAY it was
    # never extracted, which is why a guard station, a notice board and an oil press all came to rest
    # on Minami's ward fence with a green gate. Extracted as the STROKE of its boundary (the fence
    # line), not as its interior - the interior does contain features, by definition.
    "wards": "BARRIER",
    # a caravan yard is beaten WORKING GROUND, like grazing: its rails, troughs and litter stand on
    # it by design, and that is what the yard IS
    **{k: "COVER" for k in ("stable_yards",)},
    # FIXTURE - a control structure deliberately built ON another feature, where the overlap is the
    # whole point. Reasons, carried over from the older _OVERLAP_EXEMPT entries:
    #   bridges             span water to carry a way over it
    #   kido                a ward gate sits ON the ward fence where a lane passes through
    #   water_gates         the shuimen arch stands ON the city wall over its canal
    #   sluice_gates        the intake/outfall board sits ON its channel - the control structure IS the junction
    #   inspection_stations an inspection post is part of the gate complex it stands in
    #   jetties             planked mooring fingers run out OVER the river
    #   wall_towers         guard towers stand ON the wall
    #   docks               a landing stands at the waterline by definition
    #   gate_structs        the guard station and tower ARE the gate complex, standing on wall and road
    #   log_booms           a cabled log pen floats ON the river it holds timber in
    **{k: "FIXTURE" for k in ("bridges", "kido", "water_gates", "sluice_gates", "weirs", "washing_places", "inspection_stations", "jetties", "wall_towers", "docks", "gate_structs", "log_booms")},
    # RECORD - bookkeeping geometry that duplicates ground already classified elsewhere, or an
    # in-field flourish drawn ON the paddy by design (feature 012). Never tested.
    #   drawn_channels  a z-order record of the drawn field-channel strokes; the ground it covers is
    #                   the field_ditches/channels the matrix already reasons about
    #   field_ponds / field_rocks / field_graves / crescent_ponds
    #                   a pocket pond, bedrock outcrop, grave island or crescent pond sunk INTO one
    #                   paddy plot, the field tiling around it - the overlap is the feature
    #   borders         a drawn jurisdictional line is a LINE OF LAW, not a physical object
    #   row_street_plans / row_holdings
    #                   a row village's planned streets and reserved holdings (feature 291); drawn as lanes and dry plots
    **{k: "RECORD" for k in ("drawn_channels", "field_ponds", "field_rocks", "field_graves", "crescent_ponds", "borders", "forest_edge", "lane", "row_street_plans", "row_holdings", "farm_channels")},
    # the intramural patrol strip has its OWN precise rule (ring_road_kept_clear), which knows the
    # real bed width and which frontages may legitimately stand against it; the matrix defers
    **{k: "RING_ROAD" for k in ("ring_road",)},
    **{k: "VEGETATION" for k in ("village_groves", "bamboo_stands", "groves", "forest", "tree_stands", "tree_crowns")},
}
"""The overlap classes.

Research:
    one class a key - CONVENTION: every drawn key in one class, every pair forbidden unless permitted
    annexes - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html, research/questions/0040-farm-storehouses-kura.drawing.html: abut their own farmhouse and nothing else
    worked ground - research/questions/0081-village-lanes.drawing.html, research/questions/0196-communal-wells-ido.drawing.html: no lane or well on a dry plot
    flower beds and resting patches - research/questions/0015-flower-growing-and-the-chrysanthemum-kiku.drawing.html, research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: the flower field (no street cut through it) and a paddy plot left to rest (a whole plot inside its own bunds) classed GROUND with the dry plots, worked ground nothing may stand in
    ward fence a barrier - research/questions/0160-city-wards-and-the-gates-that-shut-them-at-night-machi-kido.drawing.html: the fence seals its quarter unbroken with a gate at every crossing, so it is extracted as its fence line, which everything but its own kido stands clear of
    ward gate's guard box - research/questions/0160-city-wards-and-the-gates-that-shut-them-at-night-machi-kido.drawing.html: the one solid building at the gate, on the verge beside the opening, never in a roadbed; SOLID, and riding none of the gate's fence or roadbed mounts
"""

# A permissive class may be overlapped by anything, and is never extracted. The reason matters as
# much as the fact - these are the rows that stop the matrix crying wolf.

_OVERLAP_SINGLETONS = ("governor_mansion",)  # solid footprints the manifest stores as ONE dict, not a list

_OVERLAP_CLASSIFIED = set(_OVERLAP_STRUCTS) | set(_OVERLAP_TARGETS) | set(_OVERLAP_LINEAR) | set(_OVERLAP_EXEMPT)
