"""The field fabric - paddy and its bunds, the dry crops on the hem, and fallow.

Each class's DOCSTRING is its explanation - `What:`, `Why:`, `Note:`, optional `Caveat:` - parsed by
`_base.parse_explanation` (feature 189). Edit the prose here and the page changes; the gate does not re-open.
"""

from __future__ import annotations

from ._base import Kind


class Paddy(Kind):
    """
    What: A rice basin under a shallow sheet of water behind its bunds - an inch or so for most of the season -
    one plot of the hamlet's comb field. The sheet is not constant: at midsummer the field is drained on
    purpose until the mud cracks underfoot, and it is drained again before the harvest.

    Why: Pre-modern paddies were fitted to land and water by piecemeal reclamation and inheritance, so the plots
    are odd-sized and odd-shaped, meeting at T-junctions; the tidy rectangular grid is a Meiji
    land-consolidation artifact. A flooded paddy makes its own nitrogen, which is why the same basins were
    cropped year after year.

    Note: Plot form and the irregular patchwork are read; plot sizes are calibrated from the record. the field is
    shown flooded, which is one moment of a cycle that runs from flooded to cracked and back; the depths
    behind that choice are modern extension figures, and no pre-modern record of either the depths or the
    drying stages was found.

    Caveat: the field is shown flooded, which is one moment of a cycle that runs from flooded to cracked and back;
    the depths behind that choice are modern extension figures, and no pre-modern record of either the
    depths or the drying stages was found.
    """

    key = 'paddy'
    name = 'paddy'
    covers = 'the wet plots of every `fields[kind=paddy]` - the flooded basins'
    label = 'accurate'
    sources = ('maff-suitou-mizu', 'zennoh-mizukanri')
    entry = "research/fields.html - 'Paddy plots - irregular patchwork', 'Nitrogen - a flooded paddy makes its own', 'Plot sizes', 'How deep the water actually stands'"


class WetPaddy(Kind):
    """
    What: Shitsuden, the wet paddy: a rice basin on ground too poorly drained to dry out, which stays waterlogged
    even in the season when no rice is growing. Its opposite is the kanden, the dry paddy, which empties to
    a dry field when the water is let out. The difference is the ground, not the crop - the same rice grows
    in both - which is why it lasts all year and is worth marking on a map.

    Why: It lies at the foot of the field, on the drain. Water falls basin to basin down a gravity system, and in
    a traditional paddy no line can be drawn between irrigating and draining, so the plots at the bottom
    take what the plots above shed and never come dry. That makes it the ground nobody wanted: the mud is
    deep, the soil runs colder and shorter of oxygen than a kanden, no winter crop of wheat or barley can
    follow the rice, and lodging and disease leave the yield unreliable. From Meiji the state drained wet
    paddy into dry as a national undertaking, and more than two thirds of the country's fields were
    converted - the measure of how much of it there was to convert, and the reason a map of these centuries
    should carry some.

    Note: The shitsuden and kanden categories, the wetness that defines them and the penalties they carry come
    from the dictionaries, quoted in the entry. Which plots wear the tint is a drawing convention rather
    than a survey: on a comb field a share of the wet rank carries it rather than all of it, and seating the
    wettest ground at the drain foot is inferred from how water falls through the system, not stated by the
    record.

    Caveat: Which plots wear the tint is a drawing convention rather than a survey: on a comb field a share of the
    wet rank carries it rather than all of it, and seating the wettest ground at the drain foot is inferred
    from how water falls through the system, not stated by the record.
    """

    key = 'wet paddy'
    name = 'wet paddy (shitsuden)'
    covers = 'the plots of a `fields[kind=paddy]` drawn with open water showing - the wettest ground the field has'
    label = 'accurate'
    sources = ('kotobank-shitsuden', 'kotobank-kanden', 'kotobank-yatsuda', 'kotobank-fukada', 'fao-rice-water')
    entry = "research/fields.html - 'The wettest plots are their own kind of ground - shitsuden, and why they read blue'"


class Bund(Kind):
    """
    What: The aze: a puddled-mud ridge one to two feet wide and about a foot high between two basins, re-plastered
    every spring so each paddy holds its water; the walking bunds ran two to five feet. Where bunds cross,
    the earth is piled into a lumpy node - the most-worked point in a field.

    Why: A bund is the wall BETWEEN two basins and is built once, so the fabric is one connected network meeting
    at T-junctions - never two parallel ridges with idle ground between. Farmers walked the bunds to reach
    the plots; the footplanks over the ditches serve that walking.

    Note: Construction, width and the shared-wall finding are read; the drawn stroke is at true size.
    """

    key = 'bund'
    name = 'bund'
    covers = 'the stroke of every paddy plot and the piled junctions between them'
    label = 'accurate'
    sources = ('aze-standard',)
    entry = "research/fields.html - 'Bunds are SHARED, and the fabric is continuous', 'A bund runs on, or it turns for a reason'; research/water.html - 'The bund runs along the channel bank'"


class BundBeans(Kind):
    """
    What: Soybeans planted along the tops of the paddy bunds - azemame - drawn as dark green beads.

    Why: A bund's top is soil that would otherwise grow weeds; planting it with beans took a second crop from the
    same ground without touching the paddy. A share of the bunds is planted, rolled per map.

    Note: we have rendered the bund beans as round beads about 3 ft across in a deep pine green, darker than the
    plant, in order to make them visible on the map at this scale against the pale rice. A soybean is an
    erect, bushy annual 50 to 125 cm tall (roughly 2 to 4 ft) with medium-green leaflets, sown in a row
    along the bund after transplanting and harvested with the rice; how wide one plant stands on the bund
    was not found, so the bead's width is not compared to it. The practice is attested.
    """

    key = 'bund beans'
    name = 'bund beans'
    covers = 'the bead run along the bunds (`bund_beans`)'
    label = 'convention'
    sources = ('nabunken-azemame', 'wikipedia-soybean', 'cropfarming-soybeans')
    entry = "research/fields.html - 'Paddy plots - irregular patchwork'; 'Bunds are SHARED, and the fabric is continuous'; 'What a bund bean actually looks like'; waterfields/palette.py BEAN_GREEN (the color decision)"


class Millet(Kind):
    """
    What: A dry-field (hatake) plot under millet, worked in ridged rows.

    Why: Wet-rice villages sort by a topographic catena: the paddy holds the flat valley bottom, dry crops take
    the higher, well-drained ground the water cannot command - the hem above the paddy and the raised ground
    the homesteads sit on - and coppice crowns the hills above.

    Note: Placement on the catena is read; the crop MIX on any one map (how much millet against buckwheat and
    barley) is rolled from the seed and is a GUESS at the proportions.

    Caveat: the crop MIX on any one map (how much millet against buckwheat and barley) is rolled from the seed and
    is a GUESS at the proportions.
    """

    key = 'millet'
    name = 'millet'
    covers = '`dry_plots[crop=millet]` and their furrows'
    label = 'accurate'
    sources = ('not recorded',)
    entry = "research/fields.html - 'Where dry (hatake) crops go - the topographic catena', 'Why ruled rows waited for Meiji'"


class Buckwheat(Kind):
    """
    What: A dry-field plot under buckwheat - the short-season crop for thin soil, sown late and taken in autumn -
    worked in ridged rows.

    Why: Dry crops take the higher, well-drained hem above the paddy, where the water cannot command the ground.

    Note: Placement on the catena is read; the crop mix per map is rolled from the seed and is a GUESS at the
    proportions.

    Caveat: the crop mix per map is rolled from the seed and is a GUESS at the proportions.
    """

    key = 'buckwheat'
    name = 'buckwheat'
    covers = '`dry_plots[crop=buckwheat]` and their furrows'
    label = 'accurate'
    sources = ('not recorded',)
    entry = "research/fields.html - 'Where dry (hatake) crops go - the topographic catena'"


class Barley(Kind):
    """
    What: A dry-field plot under barley - the winter grain, sown in autumn and taken in early summer - worked in
    ridged rows.

    Why: Dry crops take the higher, well-drained hem above the paddy, where the water cannot command the ground.

    Note: Placement on the catena is read; the crop mix per map is rolled from the seed and is a GUESS at the
    proportions.

    Caveat: the crop mix per map is rolled from the seed and is a GUESS at the proportions.
    """

    key = 'barley'
    name = 'barley'
    covers = '`dry_plots[crop=barley]` and their furrows'
    label = 'accurate'
    sources = ('not recorded',)
    entry = "research/fields.html - 'Where dry (hatake) crops go - the topographic catena'"


class Soy(Kind):
    """
    What: A dry-field plot under soybean (daizu) grown as a field crop of its own, worked in ridged rows - drawn a
    soybean green against the tan and ochre grains.

    Why: Dry crops take the higher, well-drained hem above the paddy, where the water cannot command the ground;
    the bean fixes its own nitrogen, which is why it also went along the bunds.

    Note: Placement on the catena is read; the crop mix per map is rolled from the seed and is a GUESS at the
    proportions.

    Caveat: the crop mix per map is rolled from the seed and is a GUESS at the proportions.
    """

    key = 'soy'
    name = 'soy'
    covers = '`dry_plots[crop=soy]` and their furrows'
    label = 'accurate'
    sources = ('not recorded',)
    entry = "research/fields.html - 'Where dry (hatake) crops go - the topographic catena'"


class Fallow(Kind):
    """
    What: Ground resting out of crop for the season.

    Why: Some dry ground rested between crops; how much, and where in the rotation, the record consulted here
    does not say.

    Note: The record is thin on fallow in this tier's fields; the patch is drawn where the field builder leaves
    ground unplanted, and that is a guess.
    """

    key = 'fallow'
    name = 'fallow'
    covers = '`fallow_patches`'
    label = 'guess'
    sources = ('not recorded',)
    entry = 'research/fields.html (no dedicated entry - recorded as silent)'
