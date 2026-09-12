"""Water, ways and the things met along them - the brook, ditches, ponds, lanes, the well, the board.

Each class's DOCSTRING is its explanation - `What:`, `Why:`, `Note:`, optional `Caveat:` - parsed by
`_base.parse_explanation` (feature 189). Edit the prose here and the page changes; the gate does not re-open.
"""

from __future__ import annotations

from ._base import Kind


class Stream(Kind):
    """
    What: A natural brook off the high ground, feeding the head of the field at an intake on its bank.

    Why: A village creek runs about two meters wide in reality, six times an irrigation ditch; every watercourse on the
    map declares which way it flows, because downstream is a real constraint on what may stand beside it.

    Note: we have drawn the stream's width by its RANK in the water hierarchy rather than by its real width, in
    order to keep brook, head race and ditch readable at every zoom - so junctions do not conserve width
    (the GM's ruling). A village creek runs about 2 m wide in reality, some six times an irrigation ditch. The
    stream's type and place are read.

    Name: stream
    Covers: `streams` - the brook
    Label: convention
    Sources: gb50288, toro-site
    Entry: research/water.html - 'Water-width ladder - the real-world tiers', 'Drawn width is RANK, not discharge'
    """

    key = 'stream'


class IrrigationDitch(Kind):
    """
    What: The dug channels that bring water TO the paddies: the head race that leaves the brook at its intake,
    the two supply canals it forks into along the field's high margins, and the delivery ditches running
    down-slope between the plots.

    Why: A canal commands only the ground below it, so the supply runs along the high margins and delivers
    perpendicular down the slope - the layout of Edo-period Minuma-dai and of Chinese canal doctrine alike.
    Mains taper as branches tap them; the net is SPARSE because a village digs the minimum, and a ditch
    beside every paddy is a Meiji anachronism. The net is drawn at true size: a field ditch is about a third
    of a meter, a hairline.

    Note: Topology, taper and true-size width are read (Tabayashi, the Minuma-dai record, GB 50288); the head
    race's length from the intake to the fork follows the fan's geometry, the record giving no distance.

    Caveat: the head race's length from the intake to the fork follows the fan's geometry, the record giving no distance

    Name: irrigation ditch
    Covers: `field_ditches` whose role is not `drain`, and `channels` not leaving a drain - the head race, the supply canals, the delivery ditches, a source-to-field feed
    Label: accurate
    Sources: tabayashi-1987, jsidre-minumadai, gb50288, nougyoudoboku-matsutan
    Entry: research/water.html - 'The comb net is drawn at TRUE SIZE', 'Where the drawn net STOPS', 'The head-race forks', 'Where does the brook stop being a brook and become the ditch'; research/fields.html - 'Water-first v2'
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
    be used again below. The collector is drawn wider at its outfall than the head race that fed the same
    ground, because it carries storm water and the season's drawdown as well as the irrigation duty.

    Note: The collector's form, its separation from the supply net and its tail wider than the head race are
    read; the sink its run reaches is the map's declared water sink.

    Caveat: the sink its run reaches is the map's declared water sink

    Name: drainage ditch
    Covers: `field_ditches` whose role is `drain`, and `channels` leaving a drain - the collector and its run to the pond, the brook or the frame
    Label: accurate
    Sources: tabayashi-1987, maff-nogyoyosui-suiden, jawiki-yosuiro
    Entry: research/water.html - 'Where does the water go once it has watered the paddies', 'The comb net is drawn at TRUE SIZE'; research/fields.html - 'Water-first v2'
    """

    key = "drainage ditch"


class Pond(Kind):
    """
    What: An irrigation reservoir - a valley-head tameike behind an earthen dike, sitting above the fields it
    waters.

    Why: A tameike is built by dividing off a valley mouth with a dike, at an elevation above the paddies it
    serves, with ONE outlet: an inclined intake feeding a bottom conduit through the dam. The spillway is
    for floods, never for distribution. On this map the pond is the field's drainage sink, at its low foot.

    Note: Form, siting and the single outlet are read (Tabayashi 1986, the Kagawa tameike documents).

    Name: pond
    Covers: `pond` - the tameike
    Label: accurate
    Sources: tabayashi-1987, kagawa-tameike
    Entry: research/fields.html - 'Water-first v2 - pond, distribution and the three layout modes'
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

    Note: Access and form are read; the drawn WIDTHS (3, 5 and 6 ft) are a GUESS - no source gives a figure for an
    ordinary hamlet lane - laddered from a footpath to a wheelbarrow's width, with the connector kept under
    the 9 ft of the one cart road the record does measure.

    Caveat: the drawn WIDTHS (3, 5 and 6 ft) are a GUESS - no source gives a figure for an ordinary hamlet lane -
    laddered from a footpath to a wheelbarrow's width, with the connector kept under the 9 ft of the one
    cart road the record does measure.

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
