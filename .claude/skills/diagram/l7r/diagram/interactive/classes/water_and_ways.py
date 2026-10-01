"""Water, ways and the things met along them - the brook, ditches, ponds, lanes, the well, the board.

Each class's DOCSTRING is its explanation - `What:`, `Why:`, `Note:`, optional `Caveat:` - parsed by
`_base.parse_explanation` (feature 189). Edit the prose here and the page changes; the gate does not re-open.
"""

from __future__ import annotations

from ._base import Kind


class Stream(Kind):
    """
    What: A natural brook off the high ground, feeding the head of the field at an intake on its bank.

    Why: A village creek runs about two meters wide, six or so times the width of a field ditch; every
    watercourse on the map declares which way it flows, because downstream is a real constraint on what may
    stand beside it.

    Note: we have drawn the stream's width by its RANK in the water hierarchy rather than by its real width, in
    order to keep brook, head race and ditch readable at every zoom - so junctions do not conserve width
    (the GM's ruling of 2026-08-16). The two rulings behind this modal do not quite agree, and the record
    has not reconciled them: the width ladder (the GM's ruling of 2026-07-21) draws a stream feeding a moat
    as wide as the moat, because the water that enters has to be carried, while the later ruling sizes
    every stroke by its own rank with no coordination across a junction. The stream's type and place are read. The 2 m is not: no page read gives a village
    creek a width, and the 0.3 m it is measured against is a modern design MINIMUM - the narrowest a canal of
    any grade may be built to - rather than a ditch anyone measured.

    Name: stream
    Covers: `streams` - the brook
    Label: convention
    Sources: jsslkx-002-2021, toro-site
    Entry: research/water.html - 'Water-width ladder - the real-world tiers', 'Drawn width is RANK, not discharge'
    """

    key = 'stream'


class IrrigationDitch(Kind):
    """
    What: The dug channels that bring water TO the paddies: the head race that leaves the brook at its intake,
    the two supply canals it forks into along the field's high margins, and the delivery ditches running
    down-slope between the plots. The intake is only an opening in the brook's bank: the head race opens out
    of the bank there, with no gate and no boards across its mouth.

    Why: The comb layout - supply along the high margins, delivery ditches perpendicular down-slope, one drain on
    the lowest line - is the Edo layout attributed to the Kishu school, and it is what Chinese canal doctrine
    codifies too. Mains taper as branches tap them. The old form passes water from paddy to paddy over the
    bund (tagoshi) rather than down a ditch to each, and a ditch beside every paddy is a Meiji anachronism, so
    the net is drawn SPARSE. What the net draws is drawn at true size, and it stops
    one tier above the finest: the distribution lateral at about a meter is the last thing on the sheet, and
    the field ditch that waters a single paddy is a hairline the map does not attempt. Where a brook's water
    stood high enough, the intake was nothing more than an entrance cut for it; the gates and slotted boards
    read at canal mouths and weirs all stand on great works, and none is recorded at a village intake.

    Note: Topology and taper are read (Tabayashi, the Minuma-dai record), and so is the paddy-to-paddy form
    (Bungotakada); how few ditches that form left is this record's own reading, since no page read counts
    ditches: the pages on it describe water passing from paddy to paddy, the one village page giving its merit
    as saving water, not saving digging, and keeping many weirs; prefectural and ministry papers a search
    showed saying such districts have hardly any channels could not be read. That a ditch beside every paddy is a Meiji anachronism is likewise the record's reading of that contrast: the Ishikawa method of 1887 put each squared parcel on a channel, and the 1899 law set out to build irrigation and drainage works, not in so many words a ditch to every paddy. The widths are drawn at true size on a ladder whose rungs are each dated before modern times: the head race's 6 ft matches the central canal of an excavated early paddy and a channel fixed by rule in 1537, and every drawn width but the drain's outfall has a width from before modern times beside it.
    The third of a meter is a modern design MINIMUM rather than a measured ditch, though the Rites of Zhou already name a finest field channel of about a foot, and the right-angle rule is carried by the classical commentary on the Rites of Zhou, the Song polders of the Lake Tai plain and the jori grid, so the rule is premodern and not a modern standard's invention. The national standard the record once leaned on for both is readable nowhere and is
    not cited. And the Kishu attribution is the layout's, not the name's: the school is attested for river
    channelization rather than for a field plan. Nor is the shape of this one drawn from a survey: the head
    race's length from the intake to the fork follows the fan's geometry, the record giving no distance. The
    bare mouth is read; that no gate or boards are drawn there rests on none being recorded at a village
    intake, and at a two-foot opening either would be smaller than the map can show.

    Caveat: the head race's length from the intake to the fork follows the fan's geometry, the record giving no distance

    Name: irrigation ditch
    Covers: `field_ditches` whose role is not `drain` (except on a dike-pond field, whose canals are the pond canal), and `channels` not leaving a drain - the head race, the supply canals, the delivery ditches, a source-to-field feed
    Label: accurate
    Sources: tabayashi-1987, jsidre-minumadai, jsslkx-002-2021, nougyoudoboku-matsutan, bungotakada-tagoshi, suido-ishizue-iseki, people-zhishui-2025, pwsannong-gudai-shuili, thepaper-guangai
    Entry: research/water.html - 'The comb net is drawn at TRUE SIZE', 'Where the drawn net STOPS', 'The head-race forks', 'Where does the brook stop being a brook and become the ditch', 'Where on the brook's bank is the intake', 'What does the intake mouth look like'; research/fields.html - 'Where does a field's water come from, and how is it shared out?'
    """

    key = "irrigation ditch"


class FarmChannel(Kind):
    """
    What: The small channel a farm standing alone in its fields leads off the irrigation water into its own grounds,
    ending in the dooryard - its water for cooking, washing and drinking.

    Why: A farm of a dispersed hamlet has no neighbors to share a well with, so it carries its own water. On the
    Tonami plain, the canonical dispersed settlement, the fan's water table lay deep and a well was hard to dig, so in
    many areas a small channel was led off the irrigation water into the house's grounds. The other areas are read as
    having dug a well of their own, so a dispersed hamlet draws one form or the other, rolled per settlement.

    Note: The channel into the grounds is read (the Tonami museum). That the other areas dug a well is this record's
    reading, and the even odds between the two a guess. It is drawn from the nearest supply ditch, or the brook where
    that is nearer; where it ends in the dooryard no page read says, and where it left the lot again is not drawn.

    Caveat: where it ends in the dooryard no page read says, and where it left the lot again is not drawn

    Name: farm channel
    Covers: `farm_channels` - the channel led into a dispersed farm's grounds (feature 291), drawn with its record in `drawn_channels`
    Label: accurate
    Sources: tonami-sankyoson-museum
    Entry: research/homesteads.html - 'Does a DISPERSED hamlet's outlying farm have its own well?'
    """

    key = "farm channel"


class DrainageDitch(Kind):
    """
    What: The dug channel that carries water AWAY from the paddies: the collector along the field's low line,
    gathering what runs out of the basins, and its run onward - into the pond at the field's foot, into the
    passing brook, or off the edge of the map.

    Why: Supply and drainage are kept apart on the ground, the supply along the high margins and the one
    collector on the lowest line - the layout of the Edo reclamation of the Minuma reservoir in 1728, its supply canals a
    step higher along the edge and its drain on the paddies' lowest ground; before modern
    consolidation the water that left a village's paddies went on down to the river, or to the next field, to
    be used again below. On a comb field the collector widens as it goes - a thread where it starts
    between the last plots, its full width where it leaves the field - because every plot it passes adds that
    plot's drawdown to what it is already carrying; a polder's ring drain instead carries the whole basin at one
    rank from the start, and is drawn at one width. The collector runs ACROSS the fall, not down it: it has to
    gather what runs off every column of plots, and a drain that ran straight downhill would follow one column
    and collect nothing - so on a map whose land falls diagonally its outfall can sit up the page while lying
    lower on the ground than the end it starts from. It lets its water go at its lowest point - its low end, or partway along where its run meets a sink - off the map, into
    the passing brook, or into the pond at the field's foot, whichever lies below it.

    Note: The collector's form and its separation from the supply net are read, as an Edo layout (Minuma, 1728), and so is a drain letting its water go into a river or a natural watercourse, in a modern
    design standard and in a Saitama drain, which its article does not date, that carried the spent water of a district its canals watered in the
    Edo period; whether it widens along its run follows the field it drains; it is drawn for every hamlet,
    a deliberate trade over the older field-to-field and combined forms the record also holds, so a reader
    has a ditch between the plots to hover, and the sink its run reaches is the map's declared water sink. A
    drain that ends in a pond of its own is a guess, no page read describing one; and the angle at which the
    collector meets the brook is this record's own inference, the right angle a modern drainage manual gives
    being the one between the field drains and the collector.

    Caveat: it is drawn for every hamlet, a deliberate trade over the older field-to-field and combined forms the record also holds, so a reader has a ditch between the plots to hover, and the sink its run reaches is the map's declared water sink. A drain that ends in a pond of its own is a guess, no page read describing one; and the angle at which the collector meets the brook is this record's own inference, the right angle a modern drainage manual gives being the one between the field drains and the collector.

    Name: drainage ditch
    Covers: `field_ditches` whose role is `drain`, and `channels` leaving a drain - the collector and its run to the pond, the brook or the frame
    Label: accurate
    Sources: tabayashi-1987, maff-nogyoyosui-suiden, jawiki-yosuiro, maff-drain-shape, shonairyo-akusuiro-jawiki, fao-drainage-systems, akusuiro-kotobank
    Entry: research/water.html - 'Where does a field's drain let its water go?', 'Where does the water go once it has watered the paddies', 'The comb net is drawn at TRUE SIZE'; research/fields.html - 'Why does the drain run across the slope instead of down it?'
    """

    key = "drainage ditch"


class Weir(Kind):
    """
    What: A low bar thrown across the brook at the intake, set at a slant so that it runs diagonally upstream
    from the point where the head race leaves the bank. Each weir hamlet builds it in one of four ways: a fence
    of driven stakes with brushwood woven between them, a frame of stakes and logs packed with clay, a crib of
    timber packed with stone, or a course of stone-filled baskets.

    Why: A weir does not take the brook - it raises its surface a little, so that water enters the canal
    at the height the field needs, and the rest goes on over the crest and down the valley. The slant is
    the old builders' way of leading water to the intake: it dams the shallow riffle, and it also keeps the bar out of the fastest
    water, where a flood is least able to break it. A weir on water this small was built of what lay to hand,
    and the first weirs, of nearby wood and stone, were fragile enough that small streams were the only place
    they could stand. Not every hamlet has one: where the brook kept its level through the season the intake
    was only an opening in the bank, and where the level fell something had to be set in the stream to raise
    it. The map gives a brook no level or season, so each hamlet's roll decides.

    Note: we have drawn the weir closing the brook bank to bank, in order to make it visible on the map at
    this scale; half-river closures were the common old form, and across a brook 7 ft wide a half-bar would
    be a line a pixel or two long. Its slant is read in the modern engineering histories, no period drawing
    of a village weir having been read. The four forms are read for small water except the baskets, which the
    record reads only on large rivers, so a course of them across a brook is a guess; which form a hamlet
    builds is rolled per settlement with an even chance, and that evenness is a guess, as is the even chance
    of a weir at all. Each form is drawn at its own thickness: the baskets at their read diameter, about 2 ft;
    the fence at about 1.5 ft, wider than a row of stakes so that it can be seen; the frame and the crib at
    5 ft, a guess, no source read giving the thickness of a village weir. The woven stake fence is ancient - the
    shigarami, stakes woven with brushwood or bamboo across a river, is in the Man'yoshu of the 8th century - but a
    weave of reed is found only in a present-day weir, so the fence is woven with brushwood.

    Name: weir
    Covers: `weirs` - the bar across the brook at a weir hamlet's intake
    Label: convention
    Sources: maff-toshuko-history, jsidre-miwa-2023, jawiki-seki, japanriver-koborebanashi-21, wangzhen-nongshu-18, suido-ishizue-iseki, kotobank-shigarami, hrr-agagawa-dento, kotobank-jakago, people-zhishui-2025, pwsannong-quxi
    Entry: research/water.html - 'Is there a weir at the intake', 'What was a village weir built of', 'What does the intake mouth look like', 'Where does the brook stop being a brook and become the ditch'
    """

    key = "weir"


class Pond(Kind):
    """
    What: A pond of held water behind an earthen bank. It plays one of two parts, and the map shows which by where
    it lies: above the fields and feeding them, it is the reservoir their water is drawn from; at the field's
    low foot, fed by the drainage ditch, it is where the water leaving the paddies is gathered.

    Why: The reservoir is the Japanese tameike - built by dividing off a valley mouth with a dike, at an
    elevation above the paddies it serves, with ONE outlet: an inclined intake feeding a bottom conduit through
    the dam. The spillway is for floods, never for distribution. A pond at the foot of the field keeps the water
    that has passed through the plots, because before modern consolidation that water was used again below
    rather than thrown away.

    Note: Form and siting are read (Tabayashi 1987, the Kagawa tameike documents). The SINGLE outlet, and the
    spillway's having no part in sharing the water out, are this record's reading of them: the Kagawa page
    describes the inclined intake, the bottom conduit and a works that passes heavy-rain inflow safely
    downstream, and does not itself say there is only one way out or that the spillway never serves the fields. And where a pond is drawn at a field's foot to
    gather the water leaving the fields, that siting is how the map ends its drainage, and the pond's bank and
    outlet are not drawn from a surveyed example.

    Caveat: where a pond is drawn at a field's foot to gather the water leaving the fields, that siting is how the map ends its drainage, and the pond's bank and outlet are not drawn from a surveyed example.

    Name: pond
    Covers: `pond` - the tameike
    Label: accurate
    Sources: tabayashi-1987, kagawa-tameike
    Entry: research/fields.html - 'Where does a field's water come from, and how is it shared out?'
    """

    key = 'pond'


class FieldPond(Kind):
    """
    What: A small pocket of open water inside one low paddy plot, reed-fringed - a low pocket where the ground
    pools, or a header pond within the field.

    Why: Flat, flooded valley-bottom paddy, the most valuable and most worked ground, is reckoned to host non-rice obstacles LEAST - graves and
    knolls go to the slope, rock outcrops are guessed to belong to terraces - and a small open-water pond, embanked and dug into low wet ground, is the one thing
    that genuinely belongs in the wet middle. It is drawn sunk into a single low plot, never across a bund.

    Note: That a plains pond is dug into low wet ground is read, as is feng shui setting graves on the hills; that flat paddy hosts obstacles least is this map's reasoning, and rocks as a terrace feature a guess; no source counts
    how often, so the rate is chosen - often enough that a reader meets the feature, rare enough that it
    does not litter the field.

    Caveat: no source counts how often, so the rate is chosen - often enough that a reader meets the feature, rare
    enough that it does not litter the field.

    Name: field pond
    Covers: `field_ponds` - the in-field pond sunk into one low paddy
    Label: accurate
    Sources: not recorded
    Entry: research/fields.html - 'In-field features - flat flooded paddy hosts obstacles least'
    """

    key = 'field pond'


class FieldRock(Kind):
    """
    What: A cluster of gray boulders inside a field plot - a bedrock outcrop the terrace risers wrap around.

    Why: The maps treat rock outcrops as a TERRACE feature, bedrock the risers wrap around, absent on alluvial
    valley, polder and delta ground; where the archetype allows one it stands off-center in its plot so it reads as
    a natural obstacle.

    Note: Which archetypes host an outcrop is this project's guess - no source found puts outcrops on terraces and
    off valley, polder and delta ground - and no source counts how many, so a terraced field
    gets one to three - enough that the reader meets the obstacle the terrace was cut around, few enough
    that the field still reads as worked ground.

    Name: field rock
    Covers: `field_rocks` - a bedrock outcrop inside a plot
    Label: guess
    Sources: not recorded
    Entry: research/fields.html - 'In-field features - flat flooded paddy hosts obstacles least'
    """

    key = 'field rock'


class GraveIsland(Kind):
    """
    What: A family's grave in the fields: a small raised earthen mound with stone markers, standing either inside a
    paddy plot as an island the flat paddy tiles around, or in a plot's corner against its bunds.

    Why: Around Shanghai many villagers buried their dead one by one out in the open fields, wherever a geomancer
    placed the grave, and a column of soldiers in 1842 found graves in every field; far to the north, Henan leveled
    more than two million field graves in 2012. In Japan no grave we read stood out in mid-paddy: some stood beside
    the bunds, until an order of 1872 forbade burying the dead at the bund edge of one's own fields; others stood in a
    field's corner, as in Ibaraki they still do. So the island inside a plot is the Chinese form and the corner grave
    the Japanese one, and each hamlet takes one.

    Note: How often a map draws a field grave at all, about three valley, terrace or ribbon maps in ten, is a degree
    chosen for the maps: no source gives a rate, and the record argues they were common where the custom held. No
    source we read puts a grave in flooded paddy: the Chinese accounts show graves inside working fields without
    naming the crop, so the island in a paddy plot is drawn from graves in fields, not read of paddy.

    Caveat: How often a map draws a field grave at all, about three valley, terrace or ribbon maps in ten, is a
    degree chosen for the maps: no source gives a rate, and the record argues they were common where the custom
    held.

    Name: grave island
    Covers: `field_graves` - a grave mound inside a paddy plot or in its corner
    Label: accurate
    Sources: henriot-shanghai-graves, henan-grave-removal-enwiki, ryobosei-jawiki, yashikibaka-ibaraki-blog
    Entry: research/religion-and-death.html - 'Where a village buries its dead: its own ground, the temple yard, the fields or the home plot'; research/fields.html - 'In-field features - flat flooded paddy hosts obstacles least'; research/rendering/religion-and-death.html - 'How our maps choose where a village's and a hamlet's dead lie'
    """

    key = 'grave island'


# WHY THE CLASS IS A *VILLAGE* LANE AND NOT A HAMLET LANE - the GM, 2026-08-29: "I have been
# referring to hamlet lanes as village lanes specifically for this reason because they are presumed
# to lead into the main village when not otherwise stated." The rule is in the `why` where a reader
# needs it; the naming rationale is project process and stays here (settlement-review, 2026-08-29).
class VillageLane(Kind):
    """
    What: A trodden earth track - packed dirt with soft worn shoulders, a single narrow way, no paving and no
    center line.

    Why: Every house in a nucleated village is reached by the interconnected lanes and alleys - that is what
    compactness is for - and the narrow lateral lanes are taken over as semi-private space by the houses
    beside them, which in this record's reading is why they are narrow and irregular (the one readable case
    is Shanghai's lane housing, a city form standing in for a village's). A lane bends like a line feet wear: as few
    turns as the plots allow, none sharp, never back on itself. The connector to the off-map road predates
    the settlement; the lanes between the farmsteads were trodden by the households already living there.
    And the lane leads somewhere: unless this map's notes say otherwise, a village lane runs to the main
    village of the district the settlement belongs to. Past its last farmhouse a lane stops at that house's
    dooryard, or runs on until it reaches something a reader can see - the fields, another way; it never
    trails off into empty ground. The way out to the rice does not stop at the field's edge either: among the
    paddies the way is the bund itself, the path a farmer walks to weed and manure, so the path to the fields
    runs on to the paddy's outer bund and joins it, and where a hamlet stands so close to its paddy that no
    path is left between them, its nearest lane runs on to the bund. In a row village the farms stand along a street
    instead - a street laid out first, or one along the dry edge the ground gives.

    Note: That every house is reached by a way is read from a surveyed village's own lane hierarchy; of the two
    forms, the planned back lane is read and the alleys off the spine are on no publicly readable page, as is
    the access passage this record paraphrases; the drawn WIDTHS (3, 5 and 6 ft, a row village's street at the 6 ft, a rank wider than the lanes off it) are a GUESS, laddered from a footpath to a
    wheelbarrow's width, with the connector kept under the 9 ft of the one cart road the record does measure.
    The record now carries ONE measured figure for a way of this kind - blind alleys of 2 to 4 m, about 6.5 to
    13 ft, reaching the house lots of a surveyed village - and the map deliberately draws below that band,
    because the village measured is a twentieth-century dry-plain one in the north rather than a wet-rice
    hamlet. How far a lane runs past its last farmhouse is a guess: no page read measures it or says whether a
    lane stopped at the dooryard or ran on, so the map's rule - end at the dooryard or reach something seen,
    and a lane end that reaches nothing is pulled back to the last house it serves - is its own, and how close
    counts as serving a house (within 12 ft of its house, yard or beds, or beside it within 60 ft) is a guess
    too, as is the point where the field path joins its bund, the one nearest the hamlet. A row village's street running
    on as the road the row stands on, and a path from each farm's door to it, are map drawing conventions.

    Caveat: the drawn WIDTHS (3, 5 and 6 ft, a row village's street at the 6 ft, a rank wider than the lanes off it) are a GUESS, laddered from a footpath to a wheelbarrow's width,
    with the connector kept under the 9 ft of the one cart road the record does measure. The record now
    carries ONE measured figure for a way of this kind - blind alleys of 2 to 4 m, about 6.5 to 13 ft,
    reaching the house lots of a surveyed village - and the map deliberately draws below that band, because
    the village measured is a twentieth-century dry-plain one in the north rather than a wet-rice hamlet. How
    far a lane runs past its last farmhouse is a guess: no page read measures it or says whether a lane stopped
    at the dooryard or ran on, so the map's rule - end at the dooryard or reach something seen, and a lane end
    that reaches nothing is pulled back to the last house it serves - is its own, and how close counts as
    serving a house (within 12 ft of its house, yard or beds, or beside it within 60 ft) is a guess too, as is
    the point where the field path joins its bund, the one nearest the hamlet.

    Name: village lane
    Covers: `lanes` - every lane on the map: the web, the internal skeleton, a row village's streets, the connector to the off-map road and the field spur
    Label: accurate
    Sources: kotobank-nodo, kotobank-aze-sekai-daihyakka, aze-jawiki, kotobank-keihan, kotobank-nawate, sonraku-jawiki
    Entry: research/homesteads.html - 'Is every farmhouse reached by a lane, and in what FORM?', 'How does a village lane bend?', 'How far does a village lane run past its last farmhouse?', 'How was a row village laid out?'; research/fields.html - 'Where does the path to the fields end?'; research/SOURCES.html re-sourcing queue (lane width)
    """

    key = 'village lane'


class Footbridge(Kind):
    """
    What: A small single-file crossing laid over a ditch too wide to step across, or a small timber deck where
    a lane crosses the stream. Each settlement lays its ditch crossings in one of three forms: a single log or
    board laid across, a short deck of logs under trodden earth, or a planked deck.

    Why: Farmers reach the plots by walking the bunds, and the long laterals cut across that walking; a
    crossing every so often is taken to keep the field passable, laid square across its ditch where both banks land on
    ground worth crossing to. All three forms are attested over small water: the one-log bridge laid across a
    brook, the earthen bridge that was the common bridge of old Japan, and the plank deck that was the rarer
    one; the record cannot say which crossed a paddy ditch, so each settlement rolls its own. Where a way
    crosses water, one deck - never two at the same point, and a lane's deck is always planked.

    Note: The three forms are read; no page read shows one laid where a bund path meets a paddy ditch, so what
    the crossing is for is a guess; which one a settlement lays is rolled with an even chance, and that
    evenness is a guess - the one proportion read, for river bridges and from an article that cites no
    sources, would make the planked deck far rarer than logs under earth. No page read says at what width a
    farm ditch was bridged: a crossing is laid over water 2 ft wide or more by the GM's ruling, about 4 ft wide
    by another, and where along a ditch it stands and how often is a guess.

    Caveat: no page read shows one laid where a bund path meets a paddy ditch, so what the crossing is for is a guess; which one a settlement lays is rolled with an even chance, and that evenness is a guess - the one proportion read, for river bridges and from an article that cites no sources, would make the planked deck far rarer than logs under earth. No page read says at what width a farm ditch was bridged: a crossing is laid over water 2 ft wide or more by the GM's ruling, about 4 ft wide by another, and where along a ditch it stands and how often is a guess.

    Name: footbridge
    Covers: `bridges[foot]` - every plank and deck over water
    Label: accurate
    Sources: kotobank-marukibashi, kotobank-ipponbashi, zhwiki-dumuqiao, dobashi-jawiki, xinhua-jiahou-muqiao, itabashi-kotobank, aze-jawiki
    Entry: research/water.html - 'What crosses a farm ditch - a plank, a log, or earth over logs', 'When is a farm ditch worth a plank' (channel_footbridges); research/ways.html - 'What is a plank bridge, and what is it for?'
    """

    key = 'footbridge'


class Well(Kind):
    """
    What: A communal wellhead: a square curb round the dark water of the shaft, on a paved apron, with a sweep
    or a pulley frame over it and, on about one well in three, a roof. (In Edo a tenement's communal "well"
    could be an aqueduct intake rather than a dug shaft.)

    Why: Most wells were shared, because a well cost a great deal to dig: a whole village, or a group of
    households within one, drew from a common well - at Karihama, on the Ehime coast, about one well to every
    five to ten houses - and it stands among the houses it serves. The bucket came up on a sweep where the
    water stood shallow and on a rope over a pulley where it lay deep. A samurai household could have a well
    of its own inside its fence; a dispersed farmstead, with no center to share a well with, carries its own
    or draws from the channel or pond it sits beside.

    Note: we have drawn the wellhead about 19 ft across - a curb of 9.4 ft radius -
    many times its true size, in order to make the well visible at map scale: the glyph marks where the well
    stands, not how much ground it takes. A hand-dug well's shaft is about 1 m across, big enough for a
    person to work in; the one curb found measured, an undated bucket well photographed for a modern book of
    old implements, is 118 cm square, and a premodern curb's size was searched for and not found, so the curb of about 4 ft is fitted
    round the premodern shaft and its exact figure is a guess. The Edo aqueduct intake is read, and so are
    the capacity (a well served several hundred - late-Qing Beijing at least about 650 persons to a well, a
    capital's figure), that digging was costly so shared wells were the majority, Karihama's houses to a well,
    and the sweep and the pulley with the depth that chose between them. A south-China village's one to three
    wells, a tenement's ten to twenty households to a well, the three-in-four split between the gears and the
    roof over one well in three are this record's guesses: the dictionaries define the well house but do not
    say how common it was. A dispersed farm's own well is a
    guess: on the Tonami plain, where the water table lay deep and a well was hard to dig, the farms in many
    areas led a small channel into their grounds instead, and a dispersed settlement draws that channel or a well of its own, rolled at even odds (a guess). The map draws more wells than that count - a hamlet one or two, a village of 60 households six to nine, a town about sixteen - as a disclosed liberty, and the distances that keep a well among the houses and every household within reach of a well or a channel are calibrations against the drawn maps, not figures from a record.

    Name: well
    Covers: `wells` - the wellheads
    Label: convention
    Sources: qq-2024-beijing-wells, saijo-mizu-rekishikan, kotobank-idoyakata
    Entry: research/urban-features.html - 'Communal wells (ido)'; research/rendering/urban-features.html - 'How our maps place and draw wells (ido)'; research/homesteads.html - 'Does a DISPERSED hamlet's outlying farm have its own well?'
    """

    key = 'well'


class NoticeBoard(Kind):
    """
    What: The kosatsuba - the official edict board: a roofed frame posting the standing law, rate tables and
    ban lists, its face turned square to the road it fronts.

    Why: Every Edo village kept one, and every town by this record's reading, and it stood where traffic was
    heaviest: it is the state talking at all who pass, so the board stands on the settlement's main road or
    street. The circulars reached the farmers through the headman, who copied and relayed them, and the
    weightiest were posted on this board - one reader per settlement makes it work. The record names several
    such places - the center, the entrance, an official's gate, a bridge end - and the map chooses among the
    sites along its main road as those who set up a board did: by the passers-by it would meet, as Nakatsugawa
    set its board at a crossroads so more would see it. The board clears no ground and may stand under a tree,
    since its label is drawn above every crown; a city draws a board at its central market and another on the
    approach to every main gate, and labels one.

    Note: Presence is read (a board site in every village of the Edo period, a board at a key point in each of
    one district's 17 villages, and the shogunate's order to post them; that every town kept one too is this
    record's reading), and so is the siting where traffic was heaviest - the center, the entrance, the
    official's gate and a bridgehead; a shrine precinct or the assembly place is this record's guess, and no
    page read says the notices were read aloud. Every board, a hamlet's too, is drawn as the roofed frame 16 by
    6 ft measured at two post towns, on a stone footing inside a fence - below the post towns a guess, since no
    village board was measured; the siting measures it by a 7 by 3 ft face, this record's own figure.

    Name: notice board
    Covers: `kosatsuba`, with its label
    Label: accurate
    Sources: fuchu-kosatsuba, ogose-kosatsuba, kosatsu-jawiki, adachi-kosatsu
    Entry: research/urban-features.html - 'Notice boards (kosatsuba)'; research/rendering/urban-features.html - 'How our maps place and draw notice boards (kosatsuba)'
    """

    key = 'notice board'
