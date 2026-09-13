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
    (the GM's ruling). The stream's type and place are read. The 2 m is not: no page read gives a village
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
    down-slope between the plots.

    Why: The comb layout - supply along the high margins, delivery ditches perpendicular down-slope, one drain on
    the lowest line - is the Edo layout attributed to the Kishu school, and it is what Chinese canal doctrine
    codifies too. Mains taper as branches tap them; the net is SPARSE because a village digs the minimum, and
    a ditch beside every paddy is a Meiji anachronism. What the net draws is drawn at true size, and it stops
    one tier above the finest: the distribution lateral at about a meter is the last thing on the sheet, and
    the field ditch that waters a single paddy is a hairline the map does not attempt.

    Note: Topology and taper are read (Tabayashi, the Minuma-dai record). The widths are weaker than they look.
    The third of a meter is a modern design MINIMUM rather than a measured ditch, and the Chinese doctrine is
    carried by a 2021 provincial standard for consolidated farmland, so what it gives is the doctrine and not
    a premodern layout. The national standard the record once leaned on for both is readable nowhere and is
    not cited. And the Kishu attribution is the layout's, not the name's: the school is attested for river
    channelization rather than for a field plan. Nor is the shape of this one drawn from a survey: the head
    race's length from the intake to the fork follows the fan's geometry, the record giving no distance.

    Caveat: the head race's length from the intake to the fork follows the fan's geometry, the record giving no distance

    Name: irrigation ditch
    Covers: `field_ditches` whose role is not `drain` (except on a dike-pond field, whose canals are the pond canal), and `channels` not leaving a drain - the head race, the supply canals, the delivery ditches, a source-to-field feed
    Label: accurate
    Sources: tabayashi-1987, jsidre-minumadai, jsslkx-002-2021, nougyoudoboku-matsutan
    Entry: research/water.html - 'The comb net is drawn at TRUE SIZE', 'Where the drawn net STOPS', 'The head-race forks', 'Where does the brook stop being a brook and become the ditch'; research/fields.html - 'Where does a field's water come from, and how is it shared out?'
    """

    key = "irrigation ditch"


class DrainageDitch(Kind):
    """
    What: The dug channel that carries water AWAY from the paddies: the collector along the field's low line,
    gathering what runs out of the basins, and its run onward - into the pond at the field's foot, into the
    passing brook, or off the edge of the map.

    Why: Supply and drainage are kept apart on the ground, the supply along the high margins and the one
    collector on the lowest line, so that every plot can be filled and emptied on its own; before modern
    consolidation the water that left a village's paddies went on down to the river, or to the next field, to
    be used again below. On a comb field the collector widens as it goes - a thread where it starts
    between the last plots, its full width where it leaves the field - because every plot it passes adds that
    plot's drawdown to what it is already carrying; a polder's ring drain instead carries the whole basin at one
    rank from the start, and is drawn at one width.

    Note: The collector's form and its separation from the supply net are read; whether it widens along its run
    follows the field it drains, and the sink its run reaches is the map's declared water sink.

    Caveat: the sink its run reaches is the map's declared water sink

    Name: drainage ditch
    Covers: `field_ditches` whose role is `drain`, and `channels` leaving a drain - the collector and its run to the pond, the brook or the frame
    Label: accurate
    Sources: tabayashi-1987, maff-nogyoyosui-suiden, jawiki-yosuiro
    Entry: research/water.html - 'Where does the water go once it has watered the paddies', 'The comb net is drawn at TRUE SIZE'; research/fields.html - 'Water-first v2'
    """

    key = "drainage ditch"


class Weir(Kind):
    """
    What: A low bar of stone-packed timber crib thrown across the brook at the intake, set at a slant so
    that it runs diagonally upstream from the point where the head race leaves the bank.

    Why: A weir does not take the brook - it raises its surface a little, so that water enters the canal
    at the height the field needs, and the rest goes on over the crest and down the valley. The slant is
    the old builders' answer to floods: it dams the shallow riffle, keeps the bar out of the fastest
    water, and spreads the overflow along a longer crest so less of it breaks. Not every hamlet has one -
    where the brook ran high enough the water was simply led off the bank, and this map's roll decided.

    Note: we have drawn the weir closing the brook bank to bank, in order to make it visible on the map at
    this scale; half-river closures were the common old form, and across a brook 7 ft wide a half-bar would
    be a line a pixel or two long. Its materials and its slant are read; the 5 ft thickness it is drawn at
    is a guess, the engineering histories giving cross-sections only for weirs on real rivers.

    Name: weir
    Covers: `weirs` - the bar across the brook at a weir hamlet's intake
    Label: convention
    Sources: maff-toshuko-history, jsidre-miwa-2023, jawiki-seki, japanriver-koborebanashi-21, wangzhen-nongshu-18
    Entry: research/water.html - 'Where does the brook stop being a brook and become the ditch'
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

    Note: Form and siting are read (Tabayashi 1987, the Kagawa tameike documents). The SINGLE outlet is this
    record's reading of them: the Kagawa page describes the inclined intake, the bottom conduit and the
    spillway, and does not itself say there is only one way out. And where a pond is drawn at a field's foot to
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

    Why: Flat, flooded valley-bottom paddy is the archetype that hosts non-rice obstacles LEAST - graves and
    knolls go to the slope, rock outcrops belong to terraces - and a small open-water pond is the one thing
    that genuinely belongs in the wet middle. It is drawn sunk into a single low plot, never across a bund.

    Note: The kind of obstacle a flooded paddy hosts is read (corroborated in both traditions); no source counts
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
    What: A cluster of gray boulders inside a field plot - a bedrock outcrop the terrace risers wrap around, too
    big to clear.

    Why: Rock outcrops are a TERRACE feature, bedrock the risers wrap around, and are absent on alluvial valley,
    polder and delta ground; where the archetype allows one it stands off-center in its plot so it reads as
    a natural obstacle.

    Note: Which archetypes host an outcrop is read (corroborated); no source counts how many, so a terraced field
    gets one to three - enough that the reader meets the obstacle the terrace was cut around, few enough
    that the field still reads as worked ground.

    Caveat: no source counts how many, so a terraced field gets one to three - enough that the reader meets the
    obstacle the terrace was cut around, few enough that the field still reads as worked ground.

    Name: field rock
    Covers: `field_rocks` - a bedrock outcrop inside a plot
    Label: accurate
    Sources: not recorded
    Entry: research/fields.html - 'In-field features - flat flooded paddy hosts obstacles least'
    """

    key = 'field rock'


class GraveIsland(Kind):
    """
    What: A small raised earthen mound with two or three stone markers standing inside a paddy plot, the flat
    paddy tiling around it.

    Why: Graves among the paddy are a north-China dry-plain signature, corroborated in Japan - NOT the rice-south
    default, where feng-shui puts the dead on the slope with a backing hill and a downslope water view. The
    GM approved both looks, so the island is drawn rarely (about three valley, terrace or ribbon maps in
    ten) as a deliberate departure.

    Note: A calibrated liberty, disclosed: the in-field grave is drawn where the rice-south record would put the
    dead on the slope, at a rate the GM approved.

    Name: grave island
    Covers: `field_graves` - the rare in-field grave mound
    Label: deviation
    Sources: not recorded
    Entry: research/fields.html - 'In-field features - flat flooded paddy hosts obstacles least' (the CALIBRATED LIBERTY paragraph, GM 2026-07-20)
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
    compactness is for - and the narrow lateral lanes are colonized as semi-private space by the houses
    beside them, which is why they are narrow and irregular. A lane bends like a line feet wear: as few
    turns as the plots allow, none sharp, never back on itself. The connector to the off-map road predates
    the settlement; the lanes between the farmsteads were trodden by the households already living there.
    And the lane leads somewhere: unless this map's notes say otherwise, a village lane runs to the main
    village of the district the settlement belongs to.

    Note: Access and form are read; the drawn WIDTHS (3, 5 and 6 ft) are a GUESS, laddered from a footpath to a
    wheelbarrow's width, with the connector kept under the 9 ft of the one cart road the record does measure.
    The record now carries ONE measured figure for a way of this kind - blind alleys of 2 to 4 m, about 6.5 to
    13 ft, reaching the house lots of a surveyed village - and the map deliberately draws below that band,
    because the village measured is a twentieth-century dry-plain one in the north rather than a wet-rice
    hamlet.

    Caveat: the drawn WIDTHS (3, 5 and 6 ft) are a GUESS, laddered from a footpath to a wheelbarrow's width,
    with the connector kept under the 9 ft of the one cart road the record does measure. The record now
    carries ONE measured figure for a way of this kind - blind alleys of 2 to 4 m, about 6.5 to 13 ft,
    reaching the house lots of a surveyed village - and the map deliberately draws below that band, because
    the village measured is a twentieth-century dry-plain one in the north rather than a wet-rice hamlet.

    Name: village lane
    Covers: `lanes` - every lane on the map: the web, the internal skeleton, the connector to the off-map road and the field spur
    Label: accurate
    Sources: not recorded
    Entry: research/homesteads.html - 'Is every farmhouse reached by a lane, and in what FORM?', 'How does a village lane bend?'; research/SOURCES.html re-sourcing queue (lane width)
    """

    key = 'village lane'


class Footbridge(Kind):
    """
    What: A plank laid over a ditch, or a small timber deck where a lane crosses the stream.

    Why: Farmers reach the plots by walking the bunds, and the long laterals cut across that walking; a plank
    every so often keeps the field passable. Where a way crosses water, one deck - never two at the same
    point.

    Note: That ditches were planked is reasoned, not read: the record consulted says nothing about a plank over a
    two-foot ditch, so the plank and its spacing are a guess.

    Name: footbridge
    Covers: `bridges[foot]` - every plank and deck over water
    Label: guess
    Sources: not recorded
    Entry: research/water.html - 'What drawing at TRUE SIZE left open' (channel_footbridges)
    """

    key = 'footbridge'


class Well(Kind):
    """
    What: A communal wellhead: a stone curb and the dark water of the shaft, under a small roof.

    Why: A pre-modern rice village of about seventy households ran one to three communal wells, two typical -
    drinking water came mostly from surface water, settled and boiled, and a well was expensive durable
    capital dug by subscription only as surface quality forced. Shared wells outnumbered private ones.

    Note: we have drawn the wellhead about 19 ft across - a stone curb of 9.4 ft radius under a well-house roof -
    many times its true size, in order to make the well visible at map scale: the glyph marks where the well
    stands, not how much ground it takes. A hand-dug well's shaft is about 1 m across, big enough for a
    person to work in, under a well house that is posts and a roof and nothing more; the width of the curb
    frame itself was not found. Count and sharing are read (the Sphere/UNICEF figures, jawiki).

    Name: well
    Covers: `wells` - the wellheads
    Label: convention
    Sources: sphere-2004-water, saijo-mizu-rekishikan, kotobank-idoyakata
    Entry: research/urban-features.html - 'Wells - the research, and the deliberate liberty', 'Communal wells and the samurai exception'; research/homesteads.html - 'Does a DISPERSED hamlet's outlying farm have its own well?'
    """

    key = 'well'


class NoticeBoard(Kind):
    """
    What: The kosatsuba - the official edict board: a small roofed frame posting the standing law, rate tables and
    ban lists, its face turned square to the way it fronts.

    Why: Every Edo town AND village kept one, and its siting was a traffic decision: it is the state talking at
    all who pass, so the board stands where the settlement's one lane carries everyone. The circulars
    reached the farmers through exactly this board, read aloud where needed - one reader per settlement
    makes it work. The record names SEVERAL such places rather than one, so which of them a settlement uses
    is rolled from its own seed: the center where villagers assembled, the entrance where the track arrives,
    or the frontage of the village official's gate. Two more the record attests - a bridgehead, and the
    shrine precinct - are real at town and city scale and are deliberately not offered at a hamlet, whose
    crossings are 10 ft ditch planks and whose only shrine is a household hokora in someone's dooryard.

    Note: Presence and siting are both read. The placement is chosen from the attested set the map can actually
    site, never from one preferred reading; at hamlet grain the glyph is drawn at its true 12 x 5 ft.

    Name: notice board
    Covers: `kosatsuba`, with its label
    Label: accurate
    Sources: fuchu-kosatsuba, ogose-kosatsuba, kosatsu-jawiki, adachi-kosatsu
    Entry: research/urban-features.html - 'The notice board (kosatsuba) - siting is a TRAFFIC decision'
    """

    key = 'notice board'
