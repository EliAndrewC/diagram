"""The planted and the wild green - bamboo, the windbreak, copses, the commons, scrub and marsh.

Each class's DOCSTRING is its explanation - `What:`, `Why:`, `Note:`, optional `Caveat:` - parsed by
`_base.parse_explanation` (feature 189). Edit the prose here and the page changes; the gate does not re-open.
"""

from __future__ import annotations

from ._base import Kind


class HomesteadBamboo(Kind):
    """
    What: A household's own bamboo stand on the damp north or west strip of its plot - a clonal thicket with a
    hard edge, drawn as paired culm strokes with a leafy fork.

    Why: Below the frost line bamboo was a matter of course in a lowland paddy hamlet - baskets, poles, fences,
    fans, food wrappings - and the shady, always-damp service side of the yashiki was where it stood. A cold
    upland hamlet may have none; whether a hamlet has bamboo is rolled per settlement.

    Note: we have rendered the bamboo stand as paired culm strokes with a leafy fork on a 7 ft grid, in order to
    show a stand that cannot be drawn at true scale: a culm is a few inches across, a fraction of a pixel at
    one foot per pixel. The stand's extent is to scale; the marks inside it are symbolic - the convention
    Japan's own topographic legend uses. Presence and place are read.

    Name: homestead bamboo
    Covers: `bamboo_stands[role=homestead]`
    Label: convention
    Sources: not recorded
    Entry: research/vegetation.html - 'Bamboo: how common, where it stood, and how to show it'
    """

    key = 'homestead bamboo'


class SharedBambooGrove(Kind):
    """
    What: A bamboo thicket held by the hamlet at the field margin, cut like a coppice.

    Why: The record gives bamboo two places: the household's own strip, and the take-yabu as a stand of its own
    at the village edge, harvested under the village's rules. The two forms are two knobs, not a choice.

    Note: we have rendered the shared grove with the same stand-level glyph as a homestead stand - paired culm
    strokes on a 7 ft grid - in order to show it at all: a culm is a few inches across and cannot be drawn
    at one foot per pixel. The grove's extent is to scale; the marks are symbolic. Presence is read.

    Name: shared bamboo grove
    Covers: `bamboo_stands` with any role other than homestead - the take-yabu at the field margin
    Label: convention
    Sources: not recorded
    Entry: research/vegetation.html - 'Bamboo: how common, where it stood, and how to show it'
    """

    key = 'shared bamboo grove'


class Windbreak(Kind):
    """
    What: The village shelter belt - the fengshui back grove: a dense, cedar-backed stand of real crowns on the
    windward, high side of the cluster, embracing it.

    Why: A nucleated village shelters behind one village-scale grove against the winter monsoon. Fujian villages
    keep about two fengshui forests each, at closed-canopy density in the well-kept Pearl River Delta patches;
    the one large measured sample of grove size, Hong Kong's survey of 115 village woods, puts the grove behind
    the village at a median of about one hectare - half under a hectare, four in ten between one and two - so the
    one-to-two-hectare belt drawn here sits in the upper half of the measured band, large relative to the
    cluster, and drawn so. It is kept off the west side of the gardens so the beds keep their afternoon sun.

    Note: The grove count follows the Fujian figure (forests-2020), the density the Pearl-delta patches
    (hu-2011-fengshui-patches), and the size the Hong Kong survey (afcd-ncsc-9-06); the water-mouth cluster's
    size and the tree counts are guesses bracketed by Korean village-grove analogues; the belt's shape follows
    the terrain and the cluster.

    Name: windbreak forest
    Covers: `village_groves[role=windbreak]`
    Label: accurate
    Sources: forests-2020
    Entry: research/vegetation.html - 'The fengshui forest - real scale, and why ours is honest'; research/homesteads.html - 'The garden's sun, and how far the windbreak shades'
    """

    key = 'windbreak'


class Copse(Kind):
    """
    What: A stand of fruit-tree and broadleaf greenery in the open ground among the houses - shade and fruit, not
    shelter.

    Why: The leafy greenery scattered through the gaps of a nucleated cluster is the third of the village's grove
    roles, after the back belt and the water-mouth grove; it threads between the dwellings and never stands
    on a roof, a yard or a crop.

    Note: The role is attested with the fengshui-grove system; how much ground one takes is nowhere given, so a
    copse is drawn to whatever gaps the houses, yards and crop leave it.

    Caveat: how much ground one takes is nowhere given, so a copse is drawn to whatever gaps the houses, yards and
    crop leave it.

    Name: copse
    Covers: `village_groves[role=copse]`
    Label: accurate
    Sources: forests-2020
    Entry: research/vegetation.html - 'The fengshui forest'; research/vegetation.html - 'What are the village's three groves'
    """

    key = 'copse'


class WoodlandCommons(Kind):
    """
    What: A managed coppice wood on the slope above the paddy: spaced crowns with an open canopy, the floor raked
    clear of leaf litter.

    Why: The village woods were iriai commons - customary common land held by the village and governed by its own
    rules on who might cut, when, and how much - coppiced on a 15-20 year cycle for firewood, forage and the
    leaf litter that fertilized the paddies. A cut wood lets sun reach the floor, so herbs grow there, not
    brush; the wood sits on the slope break above the fields, one part of the satoyama the community worked
    as a whole.

    Note: The commons regime and the raked floor are read (the Yamaguni study, the satoyama entries); a lot's
    boundary was NOT laid out as a surveyed square, so the patches are irregular.

    Caveat: a lot's boundary was NOT laid out as a surveyed square, so the patches are irregular.

    Name: woodland commons
    Covers: `commons[role=woodland]` - the coppice patches
    Label: accurate
    Sources: not recorded
    Entry: research/vegetation.html - 'How is a coppice lot bounded?', 'Does scrub stand under a village wood?', 'Forest density and crown size'
    """

    key = 'woodland commons'


class ScrubAndRoughGrazing(Kind):
    """
    What: The cut-over fuel and fodder land around the settlement: grass with a few scraggly pines, grazed and
    cut.

    Why: Everything the paddy and the homesteads do not take is the hamlet's rough ground, and it is worked:
    scrub stands six feet off every field edge (one scythe swath - land hunger keeps the margin to that),
    off open water and off the cut banks of the channels.

    Note: The margins are read; nothing describes how the clumps sit within them, so the scatter is drawn to read
    as rough grazing rather than as any surveyed pattern.

    Caveat: nothing describes how the clumps sit within them, so the scatter is drawn to read as rough grazing
    rather than as any surveyed pattern.

    Name: scrub and rough grazing
    Covers: `commons[role=grazing]`
    Label: accurate
    Sources: not recorded
    Entry: research/vegetation.html - 'The crop margin', 'Scrub stays off open water', 'The cut bank'
    """

    key = 'scrub and rough grazing'


class Marsh(Kind):
    """
    What: Reed wetland on the undrained low ground - the wet toe below the fields and the fringe of the pond.

    Why: Wet rice is reclaimed FROM marsh: where reclamation stops, or the ground is too wet to manage, it stays
    reed wetland, and an abandoned paddy reverts to it. The toe marsh is as wide as the fan it drains, and
    its margin grades reed, then sedge and grass, then dry ground. A RESERVOIR'S SHORE IS REEDED BECAUSE THE
    POND IS WORKED, not in spite of it: the obvious guess is that a maintained tameike - its bank repaired,
    its silt dredged, its water drawn down each season - would have a margin kept clear, and the record
    contradicts that. A Kagawa Prefecture study found a statistically significant POSITIVE correlation
    between the number of emergent-plant species (the reed and cattail belt) and the practice of dredging
    silt and cutting algae, and it is the ponds whose water use has STOPPED that lose the fringe. The reeds
    are a sign of a pond in use. The EMBANKMENT is the other half of the same finding and is different
    ground: it is mown and burned and may not be cultivated, to keep the bank strong, and what grows on it
    is dry-grassland herbs. So reeds stand in the shallows and stop at the foot of the bank - which is why
    you will not see the wet haze on a dike or a pond's raised rim.

    Note: The reclaimed-from-marsh finding, the margin gradient, and the reeded-shore finding are all read; the
    embankment is mown in the record as it is bare on the map.

    Name: marsh
    Covers: `marshes` - every marsh patch, whatever its role
    Label: accurate
    Sources: aas-rice-technology, mineta-2007-tameike, tameike-jawiki, kagawa-tameike-structure, maff-tameike-shizen, nies-tameike, inamino-tameike-museum
    Entry: research/water.html - 'Marsh - wet rice is reclaimed FROM wetland', 'The wet toe is as wide as the FAN', "A reservoir's shore is reeded, and its EMBANKMENT is mown"; research/vegetation.html - 'The marsh margin'
    """

    key = 'marsh'
