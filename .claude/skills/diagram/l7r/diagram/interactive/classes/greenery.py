"""The planted and the wild green - bamboo, the windbreak, copses, the commons, scrub and marsh.

Each class's DOCSTRING is its explanation - `What:`, `Why:`, `Note:`, optional `Caveat:` - parsed by
`_base.parse_explanation` (feature 189). Edit the prose here and the page changes; the gate does not re-open.
"""

from __future__ import annotations

from ._base import Kind


class HomesteadBamboo(Kind):
    """
    What: A household's own bamboo stand on its plot - a clonal thicket, in most cases of nearly one species,
    drawn as paired culm strokes with a leafy fork.

    Why: Below the frost line a lowland paddy hamlet could keep bamboo, and this record infers it commonly did - baskets, fans, food
    wrappings, building timber and everyday tools; on the Tonami plain bamboo stands once grew in many a farmstead's
    grove, beside the cedar that led it. Which side of the plot it stood on was done more than one way: on the Tonami
    plain with the storehouses and fruit trees to the south; by rivers and in flood-prone ground at the wet edge, its
    roots holding the soil; and on the windward side - the groves of the Sendai plain filled their bare lower part with
    it against the wind, and the Tonami groves often mixed it in from the west round to the north of the house, likely
    their windward side too.
    So the side is rolled per farmstead - behind the house, beside the shed, on the windward side (the windward corner
    when the wind comes on a diagonal) or on the other flank. A cold upland hamlet may have none; whether a hamlet's
    bamboo stands in its farmsteads, in a thicket of its own, or both is rolled per settlement.

    Note: we have rendered the bamboo stand as paired culm strokes with a leafy fork on a 7 ft grid, in order to
    show a stand that cannot be drawn at true scale: a culm is only inches across, madake at most about four inches,
    a fraction of a pixel at one foot per pixel. The stand's extent is to scale; the marks inside it are symbolic - the convention
    Japan's modern topographic legend uses, a symbol of the national survey's maps of about 1910 that no page read traces to a map before 1868; older maps drew the growth itself. Presence below the frost line, the stand's two places (the
    household's plot, the village's own thicket, painted ringing settlements near Kyoto before modern times and wanted on
    high, dry ground by a sixth-century Chinese farm manual) and the three sides of the plot the sources give (with the
    storehouses, at a wet edge, on the wind side) are read, the seat behind the house being one no page names; the weights among the sides
    (behind the house the likeliest, then the windward side, then beside the shed, the other flank the least), the share of farmsteads keeping one (about three in five)
    and the 22 by 16 ft strip are guesses, no page giving a share or a size.

    Name: homestead bamboo
    Covers: `bamboo_stands[role=homestead]`
    Label: convention
    Sources: yashikirin-jawiki, tonami-yashikirin-haichi, sendai-igune-modelplan, tsuijimatsu, visit-toyama-sankyoson, chikurin-jawiki, phyllostachys-enwiki
    Entry: research/vegetation.html - 'Bamboo groves (chikurin)'; research/rendering/vegetation.html - 'How our maps draw bamboo, when one culm is too small to see'
    """

    key = 'homestead bamboo'


class SharedBambooGrove(Kind):
    """
    What: A bamboo thicket standing on its own at the settlement's edge, on dry ground behind its houses, cut in
    moderation and renewed from its shoots.

    Why: The record gives bamboo two places: the household's own grove of trees, and the take-yabu as a stand of its own
    round the settlement - an early-Edo screen paints settlements ringed by bamboo groves and the villages of one Kyoto
    district managed their own bamboo groves from the start of the Edo period, both in one bamboo-rich region beside a
    great city, and a sixth-century Chinese manual wants bamboo on high,
    dry ground. The record supports both, so whether a hamlet's
    bamboo stands in its farmsteads, in a thicket of its own, or both is rolled per settlement rather than the project
    picking one.

    Note: we have rendered the shared grove with the same stand-level glyph as a homestead stand - paired culm
    strokes on a 7 ft grid - in order to show it at all: a culm is only inches across, madake at most about four
    inches, and cannot be drawn at one foot per pixel. The grove's extent is to scale; the marks are symbolic.
    Bamboo below the frost line and its two places are read; which side of the settlement the thicket takes, and
    that it was held in common, and its size, 84 by 58 ft, are guesses; that it was cut like a coppice is this record's likeness, no page making
    it.

    Name: shared bamboo grove
    Covers: `bamboo_stands` with any role other than homestead - the take-yabu at the settlement's edge
    Label: convention
    Sources: chikurin-jawiki, take-jawiki, nagaokakyo-take-nishiyama, nagaokakyo-take-takenoko, qimin-yaoshu-zhongzhu, phyllostachys-enwiki
    Entry: research/vegetation.html - 'Bamboo groves (chikurin)'; research/rendering/vegetation.html - 'How our maps draw bamboo, when one culm is too small to see'
    """

    key = 'shared bamboo grove'


class Windbreak(Kind):
    """
    What: The village shelter belt - the fengshui back grove: a dense stand of real crowns on the windward one or
    two sides of the cluster, never ringing it - toward the northwest, where the region's winter wind comes from,
    unless the place has a local wind of its own. It is drawn in one of two forms, rolled per settlement:
    conifer-led, darker conifers set in rows along the belt with lesser broadleaf among them; or mixed broadleaf,
    an irregular wood of rounded crowns. In either, a little bamboo shows between the crowns.

    Why: A nucleated village is taken to shelter behind one village-scale grove against the winter monsoon - this
    project's guess at the southern pattern. Villages in Fujian, or in one county of it - the source does not say
    which - keep about two fengshui forests each, at closed-canopy density in the well-kept Pearl River Delta patches;
    the one large sample measured grove by grove, Hong Kong's survey of 115 village woods (Zhongshan's 66 groves
    average about four hectares, no grove's own size given), puts the grove behind the village at a median of about
    one hectare - half under a hectare, four in ten between one and two. A village's belt is drawn at one to two
    hectares, in the upper half of that band; a hamlet's follows the cluster it stands behind, the five hamlet maps
    drawing theirs at 0.6 to 1.8 hectares, from well under that band up into it.
    It is kept off the west side of the gardens so the beds keep their afternoon sun.
    What it was made of was done two ways. The Japanese farmstead grove was led by one tall tree - in three of the four
    regions of a 2004 survey cedar grew at every homestead and was the dominant tree, in two of them planted in rows -
    with about nine to eighteen kinds of tree beside it; the Chinese village grove of the Pearl River Delta is a mixed
    evergreen broadleaf wood of some 47 kinds a patch. Neither is a line of one kind of tree, so the map rolls between
    the two forms per settlement. Bamboo grew in the Japanese farmstead grove too, low under the tall trees on its
    windward side, filling the bare lower part against the wind.

    Note: The grove count follows the Fujian figure (forests-2020), the density the Pearl-delta patches
    (hu-2011-fengshui-patches), and the size the Hong Kong survey (afcd-ncsc-9-06), measured in modern times on groves centuries old, no older measurement being known; the water-mouth cluster's
    size and the tree counts are guesses bracketed by Korean village-grove analogues; the belt's shape follows
    the terrain and the cluster, its ragged outline, its 80 to 120 ft depth and its place in the upper half of the
    measured band being map conventions and its wrapping the cluster's flanks this project's choice; one shared grove
    as a clustered village's pattern is a guess; the 30 ft bare run at which the maps count a hole and fill it is a
    convention, no source giving an opening's width, and the planting resuming on both sides of a lane that crosses
    the belt is a guess, no old record saying how a lane passed through one. The side it stands on, never ringing the cluster, follows the Chinese village's separate grove patches (coggins-minor-2018) and the Sendai farmstead grove - the full ring being reported only of the Izumo plain's farmstead grove and of one island settlement's belt, Tarama's of 1742 in the Ryukyus, and given by the maps only to a farmstead's own grove - kept on the north
    and west against the northwesterly winter wind (irie-2020-igune, yashikirin-jawiki), and the GM's rulings
    that the maps show that regional wind unless a place declares its own. The two forms are read (the four-region
    survey, takehara-2004-yashikirin; the delta patches), and so is the bamboo, in the Japanese farmstead grove only
    (tonami-yashikirin-haichi, sendai-igune-modelplan); drawing the Japanese form at village scale is an interpolation,
    since every survey of it is of one farmstead's grove, and so is giving bamboo to a village belt and to the broadleaf
    form; the even odds between the forms, the rows' spacing, the conifer being the commonest crown and the bamboo's
    share - about one plant in twelve, showing only in the gaps between crowns and at the edge - are guesses, no page
    giving a share.

    Caveat: drawing the Japanese form at village scale is an interpolation, since every survey of it is of one
    farmstead's grove, and so is giving bamboo to a village belt and to the broadleaf form; the even odds between the
    forms, the rows' spacing, the conifer being the commonest crown and the bamboo's share - about one plant in twelve,
    showing only in the gaps between crowns and at the edge - are guesses, no page giving a share.

    Name: windbreak forest
    Covers: `village_groves[role=windbreak]`
    Label: accurate
    Sources: forests-2020, hu-2011-fengshui-patches, coggins-minor-2018, takehara-2004-yashikirin, tonami-yashikirin-haichi, sendai-igune-modelplan
    Entry: research/vegetation.html - "Groves around a southern Chinese village: the fengshui woods (fengshuilin) and the dooryard copse"; research/rendering/vegetation.html - "How our maps draw a village's groves: the back grove, the water-mouth grove and the dooryard copse"; research/vegetation.html - "Shelter belts on a village's windward side (bofurin)"; research/rendering/vegetation.html - "How our maps draw the shelter belt: its sides, its trees, and why it runs off the edge of the map"; research/homesteads.html - 'Sunlight and shade on the farm'; research/rendering/homesteads.html - 'How our maps keep yards and gardens in the sun'; research/vegetation.html - 'Bamboo groves (chikurin)'; research/rendering/vegetation.html - 'How our maps draw bamboo, when one culm is too small to see'
    """

    key = 'windbreak'


class HomesteadGrove(Kind):
    """
    What: A farm's own grove, where each farm keeps its own shelter rather than sharing a village's - a farm standing
    apart in its fields, or one of a row along a street: a dense stand of real crowns hard against the house on the side the winter wind comes from, and on some farms a thinner
    band of lesser trees round more of the house. Every farm in a settlement takes the same shape - two sides, three,
    or all four - and the shape is rolled for each settlement.

    Why: The grove is older than the modern surveys - the Kaga domain's documents of the 1600s and 1700s treat the
    homestead grove as a stand of timber and bamboo kept thick against wind and fire, and a 1987 survey counted dozens
    of good-sized trees around each farmhouse. Which sides it took differed from region to region: on the Sendai plain it stood on
    the north and west, planted there at the urging of the domain's first lord, and often lacked the south or the east; on the Tonami plain it was
    open only at the front, where the yard and the way in were; on the Izumo plain it went the whole way round the
    house before the Meiji era, on a bank against floods. So a settlement rolls its farms' grove shape, the windward
    sides always the deep stand, and a ring is broken once at its front for the way in.

    Note: The grove, its 1987 tree count and its three shapes are read; no page before 1868 counts a grove's trees, so
    the count drawn is a GUESS set from the 1987 survey, and so is the windward stand's depth (1.57 house depths, about
    44 ft); how often each shape was taken is on no page, so the roll -
    two sides half the time, three sides three times in ten, four sides twice in ten, and four sides four times in ten
    where the farms stand on flood-prone ground - is a GUESS, this project's choice, and so are the thin band's
    depth (one tree, 17 ft), the kind of trees in it, and the width of the way in through a ring.

    Caveat: how often each shape was taken is on no page, so the roll - two sides half the time, three sides three times
    in ten, four sides twice in ten, and four sides four times in ten where the farms stand on flood-prone ground - is a
    GUESS, this project's choice, and so are the thin band's depth (one tree, 17 ft), the kind of trees in it,
    and the width of the way in through a ring.

    Name: homestead grove
    Covers: `groves`
    Label: accurate
    Sources: miura-2014-kainyo, irie-2020-igune, kashima-kainyo-1987, tonami-yashikirin-haichi, yashikirin-jawiki
    Entry: research/homesteads.html - 'Groves of trees around farmhouses (yashikirin)'; research/rendering/homesteads.html - 'How our maps draw the groves around farmhouses'
    """

    key = 'homestead grove'


class Alder(Kind):
    """
    What: Alder at the reed edge - where the village's shelter belt runs down into the marsh, its trees are the wet
    ground's own: alder, drawn a blue-gray green apart from the belt's cedar and broadleaf.

    Why: A marsh grades from reed through sedge and grass to dry ground, and where trees stand at a reed edge in
    Japan they are alder - the willow the sources list grows on lower-reach sand and mud, not in that sequence - and never pine; alder takes the ground as a mire dries, and standing water, not a
    table that swings below the ground, holds it off.

    Note: The zonation is read (packer-2017-phragmites from reed to alluvial forest; lou-2016-floodplain-zones
    for the sedge and grass between, read on Northeast-China floodplains - the Japanese study naming that step has no public copy), pine's absence from it is the record's reading of
    sources that never stand pine on wet ground, and alder's place in it is read (mlit-vegetation-classes,
    haneishi-2011-kushiro-alder, hotes-wetland-diversity); that a village's belt runs on into the marsh as alder where its ground does is
    this map's reading of them, and the crowns' blue-gray green is a map drawing convention - the real foliage is a
    plain dark green, tinted here so the wet stand reads apart from the belt.

    Caveat: the crowns' blue-gray green is a map drawing convention - the real foliage is a plain dark green, tinted
    here so the wet stand reads apart from the belt.

    Name: alder
    Covers: `village_groves[role=windbreak]` crowns standing in the marsh
    Label: accurate
    Sources: haneishi-2011-kushiro-alder
    Entry: research/vegetation.html - 'The marsh margin: reed -> sedge/grass -> dry ground; woody at a reed edge is alder or willow, never pine - ACCURATE'
    """

    key = 'alder'


class Copse(Kind):
    """
    What: The homesteads' own trees in the open ground among the houses - bamboo and fruit trees, useful trees, not
    shelter.

    Why: The leafy greenery scattered through the gaps of a nucleated cluster is the third of the village's grove
    roles, after the back belt and the water-mouth grove; it threads between the dwellings and never stands
    on a roof, a yard or a crop. In the Japanese record the grove that stands with a house is that homestead's own
    wood, formed on its lot, and the one period measurement of one - a 1684 register of village woods in the Mito
    domain - lists three households' woods of about 6,100, 10,700 and 27,800 sq ft; an encyclopedia account says their
    size varied. A 1910 account of the Musashino upland puts cedar, bamboo, evergreen-oak and zelkova woods round the
    farmhouses, and a survey of the Tonami groves finds persimmon among the three commonest trees, so the bamboo and
    fruit trees are the homestead wood's own. So the copse is sized by its homesteads: each rolls a wood of between
    about 6,000 and 28,000 sq ft, its windward grove and its share of the copse counted together, and the copse is
    filled to what the belt leaves of their sum.

    Note: That fruit trees and bamboo were the useful species planted in a fengshui wood, and that a homestead's wood
    was its own and ran from about 6,000 to 28,000 sq ft, are read; that they fill the gaps throughout the cluster is
    the GM's correction, on no page read. The range is a calibration against one register of three households, not a
    survey, and its low end rests on an entry whose sides (9 by 9 ken) do not match its stated area; counting the grove
    and the copse as one wood is this project's decision, because the record knows them as one. How the rolls spread across that range is a guess, and a clump stands only within a
    dooryard's reach of a house (90 ft), so where the ground near the houses is used up a copse is drawn short of its
    homesteads' woods - on some maps by nearly half - rather than pushed further out.

    Caveat: How the rolls spread across that range is a guess, and a clump stands only within a dooryard's reach of a
    house (90 ft), so where the ground near the houses is used up a copse is drawn short of its homesteads' woods - on
    some maps by nearly half - rather than pushed further out.

    Name: copse
    Covers: `village_groves[role=copse]`
    Label: accurate
    Sources: forests-2020, yashikirin-jawiki, miura-2019-yashikiyama, kotobank-yashikirin-heibonsha, takehara-2004-yashikirin
    Entry: research/vegetation.html - "Groves around a southern Chinese village: the fengshui woods (fengshuilin) and the dooryard copse"; research/rendering/vegetation.html - "How our maps draw a village's groves: the back grove, the water-mouth grove and the dooryard copse"; research/vegetation.html - "How big was the village's dooryard copse"
    """

    key = 'copse'


class WoodlandCommons(Kind):
    """
    What: A worked coppice wood beyond the fields, on the hill ground above them: a thicket of small crowns over a
    floor raked clear of leaf litter.

    Why: The village woods were iriai commons - customary common land held by the village and governed by its own
    rules on who might cut, when, and how much - cut and let regrow from the stump every fifteen to forty years or
    so, for firewood, forage and the leaf litter that fertilized the paddies. The village of the record is its houses
    at the center, its fields around them and hill land beyond, and the nearest hill slope - the satoyama - carried the
    fuel wood; low ground by a river or marsh, below the houses, was the grass and riverbank commons', not the
    forest's. So the wood is seated beyond the fields, on ground higher than the field it adjoins - or, where
    the map has no such ground, on the level past the fields - and never downslope of the houses. A worked wood stood as clumps of thin stems: konara stands at the old end of their cutting cycle held
    about 1,700 stems a hectare, one to about 63 sq ft on centers near 8 ft - a thicket, denser than an old hill wood.
    A cut wood lets sun reach the floor, so herbs grow there, not brush.

    Note: The commons regime, the raked floor, the order of houses, fields and wood, and the stocking are read (the
    Yamaguni study, the satoyama, village-boundary and iriai-land entries, a 1910 forester's account of the Musashino
    upland, the Nagano and Tsukuba konara stands); reading "beyond the fields" as higher than the field a wood adjoins
    is this record's reading of "the slopes around the settlement". Every stem count read was taken in the twentieth century and no record before modern times counts a worked wood's stems, so the stocking is a modern calibration with no older figure beside it; the 1,700 a hectare is calibrated on a planted
    konara stand of 29 years and on Nagano woods of 26-31 that this record reads, the report not saying so, as fuel
    woods left uncut - both at or just past the old end of the cutting cycle - so the wood may read a little more open than it
    stood, and each crown's 8-9 ft width is a guess sized from the spacing, no
    page giving one. A boundary ruled at law was a drawn line, and it bent; no page read describes a hillside lot laid
    out as a surveyed square (the planned Musashino upland villages of the later 1600s did give each household a
    straight-sided strip of wood behind its fields, a form of the whole settlement not drawn here), so the patches are
    irregular, their smoothly wandering edge a drawing convention; that a lot's edge followed ridge, stream and path
    is a guess, no page read saying so.

    Caveat: each crown's 8-9 ft width is a guess sized from the spacing, no page giving one.

    Name: woodland commons
    Covers: `commons[role=woodland]` - the coppice patches
    Label: accurate
    Sources: ijc-yamaguni, satoyama-enwiki, satoyama-jawiki, kotobank-murazakai, iriaichi-jawiki, miura-2019-yashikiyama, rinya-satoyama-junkan, katakura-1989-konara-coppice, migita-chiba-konara-canopy
    Entry: research/vegetation.html - 'Village fuel woods and their coppice (satoyama)', 'How thickly trees stood in a wood, and how wide their crowns'; research/rendering/vegetation.html - 'How our maps bound and draw the coppice woods', 'How our maps stock woods and size crowns'
    """

    key = 'woodland commons'


class ScrubAndRoughGrazing(Kind):
    """
    What: The cut-over fuel and fodder land around the settlement: grass with a few scraggly pines, grazed and
    cut.

    Why: Everything the paddy and the homesteads do not take is the hamlet's rough ground, and it is worked. The
    grass of a paddy bund was cut several times a season, and cut ground does not go over to scrub, so scrub stands
    6 ft off every field edge - the bund and the cut strip beside it; off open water; and off the banks of the
    irrigation channels, taken here to be kept like the bunds, though not off a natural brook, whose bank is grown to
    the water's edge.

    Note: That bund grass is cut several times a season today, and that cut land does not go over to scrub, are read;
    that it was cut before modern times, for green manure, is read, and that it was cut as often then is a guess, no page giving the old rate;
    the 6 ft is this record's choice, wider than the one old figure found, and it is a flat-ground figure: on terraced ground the
    kept-cut slope face below a field is wider, at times wider than the field itself, and the map does not set that
    width. The channel bank takes the same 6 ft by the GM's ruling, and that a bank was kept like a bund at all is this
    record's analogy, no page read speaking of a channel bank; nothing describes how
    the clumps sit within them, so the scatter is drawn to read as rough grazing rather than as any surveyed pattern.

    Caveat: nothing describes how the clumps sit within them, so the scatter is drawn to read as rough grazing
    rather than as any surveyed pattern.

    Name: scrub and rough grazing
    Covers: `commons[role=grazing]`
    Label: accurate
    Sources: pmc7538448-levee, meadow-enwiki, nonoichi-keihanritsu, hiroshima-keihan-manual
    Entry: research/vegetation.html - 'Scrub and rough grass at the edges of fields and channels'; research/rendering/vegetation.html - 'How our maps keep scrub off fields, channels and open water'
    """

    key = 'scrub and rough grazing'


class Marsh(Kind):
    """
    What: Reed wetland on the undrained low ground - the wet toe below the fields and the fringe of the pond.

    Why: Wet rice is reclaimed FROM marsh: where reclamation stops it stays wetland, and an abandoned paddy
    reverts to it. The toe marsh is as wide as the fan it drains - this record's reading of where the fan's springs
    come out - and
    its margin grades reed, then sedge and grass, then dry ground - the form of a toe that is cut. Reed and thatch
    grass were a crop, cut every year from ground kept for it, wetlands among it; on Lake Biwa the reed was cut in
    winter and the stubble burned in spring, and the cutting and burning are what kept such ground from going over to
    willow and forest. Left alone, an alder and willow carr would stand at the reed edge; the record supports both
    forms and the map should roll between them, but so far it draws only the cut one. A RESERVOIR'S SHORE IS REEDED
    BECAUSE THE POND IS WORKED, not in spite of it: the obvious guess is that a maintained tameike - its bank repaired,
    its silt dredged, its water often let out after the rice harvest - would have a margin kept clear, and the record
    contradicts that. A Kagawa Prefecture study found a statistically significant POSITIVE correlation
    between the number of emergent and floating-leaf plant species (the reed and cattail belt among them) and the practice of dredging
    silt and cutting weed within the pond; water plants are in decline overall, abandoned management named as a cause,
    and it is the small ponds where water use has STOPPED and bank mowing has fallen off that have been given up
    furthest. The reeds
    are a sign of a pond in use. The EMBANKMENT is the other half of the same finding and is different
    ground: a bank kept for its strength and not cultivated - trodden firm by cattle in a Song-dynasty Chinese farming
    manual, a Chinese classic's commentary already keeping the water plants off it, and mown and burned today - and
    what grows on it is sun-loving meadow flowers. So reeds stand in the shallows and stop at the foot of the bank -
    which is why you will not see the wet haze on a dike or a pond's raised rim. Whether a pond's own reed was cut as a
    crop, no page read says - the reed harvest is attested for Lake Biwa, not for a tameike - so the pond's fringe
    is drawn standing, with no cut bed, drying racks or stacks.

    Note: The reclaimed-from-marsh finding, the order of the margin gradient, the reeded-shore finding, and the yearly
    winter cutting that keeps trees out of a reed bed are all read; a pond's fringe shows no harvest because none is
    read there; the toe's width following the fan is this record's reading of where its springs come out; the
    embankment's mowing and burning are present-day management, the reed-free bank itself older (the turfing of a
    bank is read only of one Edo domain's river embankments); the toe is drawn as a straight band along the contour
    where a real fan's toe is an arc, a deliberate deviation; that a village cut its own toe marsh the same way is carried across from thatch fields in general and Lake Biwa's reed beds, no page saying it of a village
    marsh; that every toe is drawn in the cut, open form is a shortfall, the record supporting an alder-willow carr as
    well and the map not yet rolling between them; that sedge was cut for fodder is unsourced; that every pond bank is
    drawn bare is a shortfall, the Song manual planting a pond's bank sparsely with mulberry and cudrania and the map
    not yet drawing it.

    Caveat: the toe is drawn as a straight band along the contour where a real fan's toe is an arc, a deliberate
    deviation; that a village cut its own toe marsh the same way is carried across from thatch fields in general and
    Lake Biwa's reed beds, no page saying it of a village marsh; that every toe is drawn in the cut, open form is a
    shortfall, the record supporting an alder-willow carr as well and the map not yet rolling between them; that sedge
    was cut for fodder is unsourced; that every pond bank is drawn bare is a shortfall, the Song manual planting a
    pond's bank sparsely with mulberry and cudrania and the map not yet drawing it.

    Name: marsh
    Covers: `marshes` - every marsh patch, whatever its role
    Label: accurate
    Sources: aas-rice-technology, mineta-2007-tameike, tameike-jawiki, kagawa-tameike-structure, maff-tameike-shizen, nies-tameike, inamino-tameike-museum, kayabun-kayabuki, ohmi-yoshi, biwako-visitors-yoshi-hiire, opal-biwa-yoshi-hara
    Entry: research/water.html - 'Marshes and wetlands (shitchi)', 'Reservoir ponds (tameike)'; research/rendering/water.html - "How our maps draw the marsh at the fields' foot", 'How our maps draw reservoir ponds (tameike), their reeds and their embankments'; research/vegetation.html - 'The marsh margin', 'Were the reed beds cut'
    """

    key = 'marsh'
