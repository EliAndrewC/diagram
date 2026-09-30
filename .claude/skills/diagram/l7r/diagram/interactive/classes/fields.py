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
    purpose until the mud cracks underfoot, for about a week, to stand the rice up to the wind and fill its ears -
    done in some places by the Edo period, and before the war only where water was plentiful - and it is
    drained again before the harvest.

    Why: Pre-modern paddies were fitted to land and water by piecemeal reclamation, so the plots are
    odd-sized and odd-shaped; the tidy rectangular grid is a Meiji/Showa land-consolidation artifact, though
    the alluvial plains of the west kept the far older jori grid working through the medieval period, and its
    regular plots stayed widespread there up to Meiji. A paddy's soil was fed from within: in China the water
    fern azolla was grown on the flooded paddy to take nitrogen from the air for the rice, and in Japan a
    winter vetch, renge, was sown in the paddy as a green manure. On the Chinese
    delta the rice fields were also where the ducks fed: Qu Dajun, writing of Guangdong in 1678, says the
    coastal fields bred small crabs that ate the rice sprouts and only ducks could eat them, so the villages
    kept many ducks, herded in the fields - on the crabs in spring and summer, on the gleaned rice in autumn.

    Note: Plot form and the irregular patchwork are read, and so is the scattering of a household's holding;
    that the bunds meet at T-junctions is a guess no page read states; drawing the patchwork on the western
    plains, where the jori grid ran, is a deviation; plot sizes are the map's own figures, a basin smaller
    than the register parcels of the 1600s (about 0.09-0.44 acre, read) on the guess that a parcel was split
    into several level basins, placed inside a pre-modern band no page read gives; the field is shown flooded, which is one moment of a cycle that runs
    from flooded to cracked and back - a cycle China's farming manuals give from the sixth century on, a paddy let out
    to sun its roots firm after weeding and drained again before the harvest; the depths behind that choice are modern
    extension figures, and no pre-modern depth was found; the midsummer drain appears in Edo-period farm books, in some places, and before
    the war it had spread only where water was plentiful - a field short of water kept its sheet; that the same
    limit held before modern times is this record's inference, and the week is a modern guide's, not an Edo figure.

    Caveat: the field is shown flooded, which is one moment of a cycle that runs from flooded to cracked and
    back - a cycle China's farming manuals give from the sixth century on, a paddy let out to sun its roots firm after
    weeding and drained again before the harvest; the depths behind that choice are modern extension figures, and no pre-modern depth was found; the
    midsummer drain appears in Edo-period farm books, in some places, and before the war it had spread only where
    water was plentiful - a field short of water kept its sheet; that the same limit held before modern times is
    this record's inference, and the week is a modern guide's, not an Edo figure.

    Name: paddy
    Covers: the wet plots of every `fields[kind=paddy]` - the flooded basins
    Label: accurate
    Sources: maff-suitou-mizu, zennoh-mizukanri, horikawa-2011-nakaboshi, doyoboshi-jawiki, qimin-yaoshu-juan2, chenfu-nongshu-juanshang, guangdong-xinyu-20, pwsannong-zhusanjiao-nongyeshi
    Entry: research/fields.html - 'Rice paddies and their plots (suiden)', 'Plot sizes', 'The paddy through the rice year: flooding, draining, transplanting and after the harvest'; research/rendering/fields.html - 'How our maps draw rice paddies and their plots (suiden)', 'How our maps show the paddy through the rice year'; research/archetypes.html - 'Which animals did a dike-pond village keep at its ponds? Pigs - the ducks were herded in the rice fields'
    """

    key = 'paddy'


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

    Name: wet paddy (shitsuden)
    Covers: the plots of a `fields[kind=paddy]` drawn with open water showing - the wettest ground the field has
    Label: accurate
    Sources: kotobank-shitsuden, kotobank-kanden, kotobank-yatsuda, kotobank-fukada, fao-rice-water
    Entry: research/fields.html - 'The wettest plots are their own kind of ground - shitsuden, and why they read blue'
    """

    key = 'wet paddy'


class Bund(Kind):
    """
    What: The aze: a puddled-mud ridge between two basins, one to two shaku wide (about one to two feet) and a few
    inches high - outside modern works it had no fixed size, varying by region and soil; today's standard bund is about a
    foot high. Each late spring, before
    transplanting, its face was stripped of weeds and plastered with kneaded mud by the hoe (azenuri), so each
    paddy holds its water. A wider walking bund ran between the plots, two to five feet across. Where bunds cross,
    the earth is piled into a lumpy node - by this project's guess, the most-worked point in a field.

    Why: A bund is the wall BETWEEN two basins and is built once, so the fabric is one connected network meeting
    at T-junctions - never two parallel ridges with idle ground between. The bund was the path of farm work
    (azemichi) and the boundary of a holding; the footplanks over the ditches serve that walking.

    Note: Construction, the spring plastering and the dividing bund's width are read - the shogunate's survey reckoned a
    bund at one shaku (the word's earliest example is a shogunate order of 1726), and the small bunds of an early Yayoi paddy ran 20 to 60 cm wide and 5 to 20 cm high -
    and it is drawn about a foot and a half wide, at true size; no height from the Edo period was found; the
    shared-wall finding is this record's derivation from how the bund is built and kept. The walking bund's two to
    five feet is a GUESS: no page read gives its width, so it is held between the two-shaku bund and the one-ken
    (six-foot) farm road of that replanned field.

    Caveat: The walking bund's two to five feet is a GUESS: no page read gives its width, so it is held between the
    two-shaku bund and the one-ken (six-foot) farm road of that replanned field.

    Name: bund
    Covers: the stroke of every paddy plot and the piled junctions between them
    Label: accurate
    Sources: kotobank-azebiki, hattori-site-yayoiken, kato-1999-ittanbu-kukaku, kotobank-aze-sekai-daihyakka, kigosai-azenuri, kubota-azenuri-kuwa, aze-standard
    Entry: research/fields.html - 'Bunds between the paddies (aze)'; research/rendering/fields.html - 'How our maps draw bunds between the paddies (aze)'; research/water.html - 'The bund runs along the channel bank'
    """

    key = 'bund'


class BundBeans(Kind):
    """
    What: Soybeans planted along the tops of the paddy bunds - azemame - drawn as dark green beads.

    Why: The beans were a food crop of their own, sown along the bund tops after transplanting and harvested with
    the rice. Once grown across Japan, most disappeared with land consolidation, herbicide and damage by
    animals. A share of the bunds is planted, rolled per map.

    Note: we have rendered the bund beans as round beads about 3 ft across in a deep pine green, darker than the
    plant, in order to make them visible on the map at this scale against the pale rice, and any stretch of
    bund that carries them shows at least two, because a single bead does not read as a row. A soybean is an
    erect, bushy annual 50 to 125 cm tall (roughly 2 to 4 ft) with medium-green leaflets, sown in a row
    along the bund after transplanting and harvested with the rice; how wide one plant stands on the bund
    was not found, so the bead's width is not compared to it. The practice is attested.

    Name: bund beans
    Covers: the bead run along the bunds (`bund_beans`)
    Label: convention
    Sources: nabunken-azemame, wikipedia-soybean, cropfarming-soybeans
    Entry: research/fields.html - 'Rice paddies and their plots (suiden)', 'Bunds between the paddies (aze)'; research/rendering/fields.html - 'How our maps draw bunds between the paddies (aze)'; waterfields/palette.py BEAN_GREEN (the color decision)
    """

    key = 'bund beans'


class Millet(Kind):
    """
    What: A dry-field (hatake) plot under millet, worked in ridged rows.

    Why: The foothill border zone holds paddy, dry fields and woods together in one mosaic, and the map reads it
    as a catena: the paddy holds the flat valley bottom, and dry crops take the higher, well-drained ground the
    water cannot command - terraces, levee crests, lower slopes, and on a fan its drier middle, though that was
    mostly left wild until the end of the Edo period; on these maps the strip along the field's high edge, just
    above the supply canal - with the woods on the slopes, by the early modern period mostly red pine, grass or
    bare hill rather than coppice. Neighboring plots on the same lie of land form a tract and share one row
    direction, each turned a few degrees; the direction changes between tracts, along the contour or down to the
    outfall, never straight down a steep slope, and all along the contour where the ground is steep - the land sets
    it, and the seams read the family strips apart.

    Note: The catena's elements - paddy, dry field, woodland - are read, and one page read puts the dry fields on
    the slopes around the settlement, for the Yoshino mountains only; that the old settlements stand on the raised
    ground that is also their dry field, with the paddy in the wet ground behind it, is read too; the rest of the
    order is this record's own reading, and one source read puts paddy round houses built on slightly higher ground
    instead; the plot a household works by its own house is named for its own consumption, read, and no page read puts
    grain there; ridged rows are read for China - a modern history says the sixth-century Qimin Yaoshu set ridge
    rules for soybeans and millet - but for Japan they are a GUESS: no page read says whether a pre-modern Japanese
    dry field was sown in rows or broadcast, and the only ridged rows found in Japan are modern. That the land sets
    the row direction tract by tract is this record's reading of a classical passage. The crop MIX on any one map
    (how much millet against buckwheat and barley) is rolled from the seed and is a GUESS at the proportions;
    whether a fan's middle stays wild is rolled per map too, since old heartlands such as Kinki and Kofu cleared
    theirs early, and the odds of that roll are a GUESS; where it stays wild the dry strip keeps to the fan's toe,
    and where on the fall the toe begins is a GUESS; how many plots a tract holds, how far a plot turns within one,
    and that every tract on steep ground runs along the contour are GUESSES - no page read says how rows ran there.

    Caveat: The crop MIX on any one map (how much millet against buckwheat and barley) is rolled from the seed and
    is a GUESS at the proportions; whether a fan's middle stays wild is rolled per map too, since old heartlands
    such as Kinki and Kofu cleared theirs early, and the odds of that roll are a GUESS; where it stays wild the dry
    strip keeps to the fan's toe, and where on the fall the toe begins is a GUESS; how many plots a tract holds, how
    far a plot turns within one, and that every tract on steep ground runs along the contour are GUESSES - no page
    read says how rows ran there.

    Name: millet
    Covers: `dry_plots[crop=millet]` and their furrows
    Label: accurate
    Sources: senjochi-kotobank, zuozhuan-chenggong, fao-aina-ridging, zgkpw-longzuo
    Entry: research/fields.html - 'Where dry (hatake) crops go - the topographic catena', 'Why ruled rows waited for Meiji', 'Why do neighboring dry plots run their furrows different ways?'
    """

    key = 'millet'


class Buckwheat(Kind):
    """
    What: A dry-field plot under buckwheat - the short-season crop for thin soil, sown late and taken in autumn -
    worked in ridged rows.

    Why: Dry crops take the higher, well-drained ground the paddy water cannot command - terraces, levee crests,
    lower slopes, and on a fan its drier middle, though that was mostly left wild until the end of the Edo period.
    On these maps that is the strip along the field's high edge, just above the supply canal where the paddy water
    stops. The plot a household works beside its own house is its kitchen garden; no source read puts its grain
    there. Neighboring plots on the same lie of land form a tract and share one row direction, each turned a few
    degrees; the direction changes between tracts, along the contour or down to the outfall, never straight down a
    steep slope, and all along the contour where the ground is steep - the land sets it, and the seams read the
    family strips apart.

    Note: The catena's elements - paddy, dry field, woodland - are read, and one page read puts the dry fields on
    the slopes around the settlement, for the Yoshino mountains only; that the dry crops take the higher ground
    above the paddy, and share the houses' raised ground, is read for alluvial lowland, where one page puts the old
    settlements and their dry fields on the natural levee and another the paddy in the wet ground behind; on river
    terraces one page puts settlements and dry fields early, many turned to paddy once irrigation reached them, and
    on a fan two put the water-short middle late to clearing and the spring-fed toe early to paddy; elsewhere that
    order is this record's own reading, and one source read puts paddy
    round houses built on slightly higher ground instead; the plot a household works by its own house is named
    for its own consumption, read, and no page read puts grain there. Apart from the ridging, what is said here of
    the crop itself is not drawn from the sections this entry names; ridged rows are read for China - a modern
    history says the sixth-century Qimin Yaoshu set ridge rules for soybeans and millet - but no page read says
    whether a pre-modern Japanese dry field was sown in rows or broadcast, and the only ridged rows found in Japan
    are modern, so for Japan the rows are a GUESS. That the land sets the row direction tract by tract is this
    record's reading of a classical passage. The crop mix per map is rolled from the seed and is a GUESS at the
    proportions; whether a fan's middle stays wild is rolled per map too, since old heartlands such as Kinki and
    Kofu cleared theirs early, and the odds of that roll are a GUESS; where it stays wild the dry strip keeps to
    the fan's toe, and where on the fall the toe begins is a GUESS; how many plots a tract holds, how far a plot
    turns within one, and that every tract on steep ground runs along the contour are GUESSES - no page read says
    how rows ran there.

    Caveat: The crop mix per map is rolled from the seed and is a GUESS at the proportions; whether a fan's middle
    stays wild is rolled per map too, since old heartlands such as Kinki and Kofu cleared theirs early, and the
    odds of that roll are a GUESS; where it stays wild the dry strip keeps to the fan's toe, and where on the fall
    the toe begins is a GUESS; how many plots a tract holds, how far a plot turns within one, and that every tract
    on steep ground runs along the contour are GUESSES - no page read says how rows ran there.

    Name: buckwheat
    Covers: `dry_plots[crop=buckwheat]` and their furrows
    Label: accurate
    Sources: senjochi-kotobank, zuozhuan-chenggong, fao-aina-ridging, zgkpw-longzuo
    Entry: research/fields.html - 'Where dry (hatake) crops go - the topographic catena', 'Why ruled rows waited for Meiji', 'Why do neighboring dry plots run their furrows different ways?'
    """

    key = 'buckwheat'


class Barley(Kind):
    """
    What: A dry-field plot under barley - the winter grain, sown in autumn and taken in early summer - worked in
    ridged rows.

    Why: Dry crops take the higher, well-drained ground the paddy water cannot command - terraces, levee crests,
    lower slopes, and on a fan its drier middle, though that was mostly left wild until the end of the Edo period.
    On these maps that is the strip along the field's high edge, just above the supply canal where the paddy water
    stops. The plot a household works beside its own house is its kitchen garden; no source read puts its grain
    there. Neighboring plots on the same lie of land form a tract and share one row direction, each turned a few
    degrees; the direction changes between tracts, along the contour or down to the outfall, never straight down a
    steep slope, and all along the contour where the ground is steep - the land sets it, and the seams read the
    family strips apart.

    Note: The catena's elements - paddy, dry field, woodland - are read, and one page read puts the dry fields on
    the slopes around the settlement, for the Yoshino mountains only; that the dry crops take the higher ground
    above the paddy, and share the houses' raised ground, is read for alluvial lowland, where one page puts the old
    settlements and their dry fields on the natural levee and another the paddy in the wet ground behind; on river
    terraces one page puts settlements and dry fields early, many turned to paddy once irrigation reached them, and
    on a fan two put the water-short middle late to clearing and the spring-fed toe early to paddy; elsewhere that
    order is this record's own reading, and one source read puts paddy
    round houses built on slightly higher ground instead; the plot a household works by its own house is named
    for its own consumption, read, and no page read puts grain there. Apart from the ridging, what is said here of
    the crop itself is not drawn from the sections this entry names; ridged rows are read for China - a modern
    history says the sixth-century Qimin Yaoshu set ridge rules for soybeans and millet - but no page read says
    whether a pre-modern Japanese dry field was sown in rows or broadcast, and the only ridged rows found in Japan
    are modern, so for Japan the rows are a GUESS. That the land sets the row direction tract by tract is this
    record's reading of a classical passage. The crop mix per map is rolled from the seed and is a GUESS at the
    proportions; whether a fan's middle stays wild is rolled per map too, since old heartlands such as Kinki and
    Kofu cleared theirs early, and the odds of that roll are a GUESS; where it stays wild the dry strip keeps to
    the fan's toe, and where on the fall the toe begins is a GUESS; how many plots a tract holds, how far a plot
    turns within one, and that every tract on steep ground runs along the contour are GUESSES - no page read says
    how rows ran there.

    Caveat: The crop mix per map is rolled from the seed and is a GUESS at the proportions; whether a fan's middle
    stays wild is rolled per map too, since old heartlands such as Kinki and Kofu cleared theirs early, and the
    odds of that roll are a GUESS; where it stays wild the dry strip keeps to the fan's toe, and where on the fall
    the toe begins is a GUESS; how many plots a tract holds, how far a plot turns within one, and that every tract
    on steep ground runs along the contour are GUESSES - no page read says how rows ran there.

    Name: barley
    Covers: `dry_plots[crop=barley]` and their furrows
    Label: accurate
    Sources: senjochi-kotobank, zuozhuan-chenggong, fao-aina-ridging, zgkpw-longzuo
    Entry: research/fields.html - 'Where dry (hatake) crops go - the topographic catena', 'Why ruled rows waited for Meiji', 'Why do neighboring dry plots run their furrows different ways?'
    """

    key = 'barley'


class Soy(Kind):
    """
    What: A dry-field plot under soybean (daizu) grown as a field crop of its own, worked in ridged rows - drawn a
    soybean green against the tan and ochre grains.

    Why: Dry crops take the higher, well-drained ground the paddy water cannot command - terraces, levee crests,
    lower slopes, and on a fan its drier middle, though that was mostly left wild until the end of the Edo period.
    On these maps that is the strip along the field's high edge, just above the supply canal where the paddy water
    stops. The plot a household works beside its own house is its kitchen garden; no source read puts its grain
    there. Neighboring plots on the same lie of land form a tract and share one row direction, each turned a few
    degrees; the direction changes between tracts, along the contour or down to the outfall, never straight down a
    steep slope, and all along the contour where the ground is steep - the land sets it, and the seams read the
    family strips apart. The bean fixes its own nitrogen, which is why it also
    went along the bunds.

    Note: The catena's elements - paddy, dry field, woodland - are read, and one page read puts the dry fields on
    the slopes around the settlement, for the Yoshino mountains only; that the dry crops take the higher ground
    above the paddy, and share the houses' raised ground, is read for alluvial lowland, where one page puts the old
    settlements and their dry fields on the natural levee and another the paddy in the wet ground behind; on river
    terraces one page puts settlements and dry fields early, many turned to paddy once irrigation reached them, and
    on a fan two put the water-short middle late to clearing and the spring-fed toe early to paddy; elsewhere that
    order is this record's own reading, and one source read puts paddy
    round houses built on slightly higher ground instead; the plot a household works by its own house is named
    for its own consumption, read, and no page read puts grain there. Apart from the ridging, what is said here of
    the crop itself is not drawn from the sections this entry names; ridged rows are read for China - a modern
    history says the sixth-century Qimin Yaoshu set ridge rules for soybeans and millet - but no page read says
    whether a pre-modern Japanese dry field was sown in rows or broadcast, and the only ridged rows found in Japan
    are modern, so for Japan the rows are a GUESS. That the land sets the row direction tract by tract is this
    record's reading of a classical passage. The crop mix per map is rolled from the seed and is a GUESS at the
    proportions; whether a fan's middle stays wild is rolled per map too, since old heartlands such as Kinki and
    Kofu cleared theirs early, and the odds of that roll are a GUESS; where it stays wild the dry strip keeps to
    the fan's toe, and where on the fall the toe begins is a GUESS; how many plots a tract holds, how far a plot
    turns within one, and that every tract on steep ground runs along the contour are GUESSES - no page read says
    how rows ran there.

    Caveat: The crop mix per map is rolled from the seed and is a GUESS at the proportions; whether a fan's middle
    stays wild is rolled per map too, since old heartlands such as Kinki and Kofu cleared theirs early, and the
    odds of that roll are a GUESS; where it stays wild the dry strip keeps to the fan's toe, and where on the fall
    the toe begins is a GUESS; how many plots a tract holds, how far a plot turns within one, and that every tract
    on steep ground runs along the contour are GUESSES - no page read says how rows ran there.

    Name: soy
    Covers: `dry_plots[crop=soy]` and their furrows
    Label: accurate
    Sources: senjochi-kotobank, zuozhuan-chenggong, fao-aina-ridging, zgkpw-longzuo
    Entry: research/fields.html - 'Where dry (hatake) crops go - the topographic catena', 'Why ruled rows waited for Meiji', 'Why do neighboring dry plots run their furrows different ways?'
    """

    key = 'soy'


class Fallow(Kind):
    """
    What: A paddy basin left to rest this year, drawn as grazed grass inside its own bunds - a whole plot, never a
    patch within one - on a settlement whose paddy rests at all. The two to four resting basins lie scattered
    among the cropped plots, never side by side.

    Why: On the early medieval estates short water and thin soil left much paddy unstable, and each year the plots
    to be worked were chosen anew from the cropped and the resting ground (kataarashi). The resting land was mixed
    in among the land under crop, not a block of its own, and while it rested it was not marked off but grazed in
    common by cattle and horses. The nucleated village on stable ground, and the early modern village after the
    land surveys, cropped the same paddy every year, so most maps draw no resting plot.

    Note: Whether a settlement rests any paddy is rolled from the map's seed: settled, cropped every year, or
    unsettled, with a few basins resting. The two forms, the scattering and the grazing are read; that the settled
    form is the commoner is this record's reading, and the weight between the two a GUESS; how many basins rest is
    a liberty kept within the record's "a few"; that they favor the far end of the water's run is this record's
    reading of short water, and a GUESS, since nothing read says which plots of a village's paddy were rested.

    Caveat: that the settled form is the commoner is this record's reading, and the weight between the two a
    GUESS; how many basins rest is a liberty kept within the record's "a few"; that they favor the far end of the
    water's run is this record's reading of short water, and a GUESS, since nothing read says which plots of a
    village's paddy were rested.

    Name: fallow
    Covers: `fallow_patches`
    Label: accurate
    Sources: nishitani-2023-chusei-nogyo, kotobank-kataarashi-yamakawa, kotobank-kataarashi-nipponica, mizkan-2005-sato-kyuko
    Entry: research/fields.html - 'Is any paddy left to rest - and where does a resting plot lie?'
    """

    key = 'fallow'


class Holding(Kind):
    """
    What: A row village farm's own holding - the dry field behind a farm on the far side of its street, drawn in plots
    back from the house.

    Why: Where a row of farms stands along a road laid out first, each farm's land runs behind it: house lot, then
    field, then woodland, in a strip as wide as the lot. That is the planned new-field colony's order, Santome's among
    them, and a row village on paddy ground may borrow the form though not its size. Where the row follows a dike, a
    levee or a fan's foot, a farm's holding lies near the house and fairly compact. So a row with farms on both sides
    of its street draws the far farms' holdings behind them - a long strip on a street laid first, a compact plot on
    the dry edge - while the near farms stand between the street and the ground the row keeps off - the rice field, or the marsh or water beside it - with that ground at their backs. The map draws the lot and the field; the woodland beyond is not drawn.

    Note: The order back from the road and the compact holding on a dike are read; the strip's depth here, three lots,
    is a GUESS (Santome's strip was a dry-field colony's and ran far deeper), and so are its crop, dry field, and the
    compact holding carried from a dike row to a levee or fan-foot row. The plots' size is a map drawing convention.

    Caveat: the strip's depth here, three lots, is a GUESS (Santome's strip was a dry-field colony's and ran far
    deeper), and so are its crop, dry field, and the compact holding carried from a dike row to a levee or fan-foot row.
    The plots' size is a map drawing convention.

    Name: farm holding
    Covers: `dry_plots[holding]` and their furrows
    Label: accurate
    Sources: kotobank-santome-shinden, kawashima-1986-santome, saitama-santome-history
    Entry: research/homesteads.html - 'How wide was a farm in a row, how long was the row, and where did its field and grove lie?', 'How was a row village laid out?'
    """

    key = 'farm holding'
