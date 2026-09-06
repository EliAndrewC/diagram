"""The dike-pond hamlet (feature 150, Kuwabata) - ponds, planted dikes, sluices, the stock and the enclosing dike.

Each class's DOCSTRING is its explanation - `What:`, `Why:`, `Note:`, optional `Caveat:` - parsed by
`_base.parse_explanation` (feature 189). Edit the prose here and the page changes; the gate does not re-open.
"""

from __future__ import annotations

from ._base import Kind


# ---- the dike-pond hamlet (feature 150, Kuwabata - the first scripted mulberry_dike_fishpond) ----
class FishPond(Kind):
    """
    What: A stocked carp pond dug out of a former paddy parcel, two to three meters deep, its water held back by
    the planted dike piled from its own spoil - one cell of the mulberry-dike fish-pond system (桑基魚塘).

    Why: A dike-pond is dug where the ground was low and flood-prone: the digging drains the hollow and the spoil
    raises the dike, so the landscape was made cell by cell by the households that farmed it, over
    centuries. Each pond is fed and drained through a sluice in its dike, plumbed inlet-high and outlet-low,
    and is drained two or three times a year to dredge the mud onto the dikes. The ponds here are 0.4 to 0.6
    hectare oblongs, the size the surveys of the traditional landscape record.

    Note: The form and the loop are read; the pond SIZES are from 20th-century surveys of the traditional
    landscape, not Ming or Qing documents, and the whole-block conversion drawn here is the rare end state
    of a normally scattered system.

    Caveat: the pond SIZES are from 20th-century surveys of the traditional landscape, not Ming or Qing documents,
    and the whole-block conversion drawn here is the rare end state of a normally scattered system.
    """

    key = 'fish pond'
    name = 'fish pond'
    covers = 'the dug water of every `dikeponds[]` parcel - the pond inset inside its mulberry dike'
    label = 'accurate'
    sources = ('isis-dykepond', 'ruddle-zhong-1988', 'fao-ac241e', 'gmrb-2024-sangji')
    entry = "research/archetypes.md - 'The three overlay values', 'The 6:4 water-to-dike ratio, and coppiced mulberry', 'A dike-pond is fed and drained through sluice gates'"


class MulberryDike(Kind):
    """
    What: The raised earthen dike around a fish pond, six to ten meters wide, piled from the pond's own dredged
    mud and planted with coppiced mulberry - low bushes stripped for leaf several times a year to feed
    silkworms.

    Why: The dike is the silk side of the loop: mulberry leaf feeds the silkworms, the silkworm waste feeds the
    fish, the dredged pond mud re-fertilizes the dike. The prescription was six parts water to four parts
    dike (three-to-seven to four-to-six in the gazetteers) because too much water starves the worms and too
    much dike starves the fish. A bare dike of heaped mud gullies and slumps, so every dike was planted; in
    sericulture districts that planting was mulberry.

    Note: The ratio, the dike width and the planting are read; the coppice density the crowns are drawn at (one
    bush per ten to twenty square feet) was not re-found and stays on the re-sourcing queue.

    Caveat: the coppice density the crowns are drawn at (one bush per ten to twenty square feet) was not re-found
    and stays on the re-sourcing queue.
    """

    key = 'mulberry dike'
    name = 'mulberry dike'
    covers = 'the bank ring of every `dikeponds[]` parcel and the coppiced crowns planted along it'
    label = 'accurate'
    sources = ('gd-gazetteer-sangji', 'fao-ac241e', 'isis-dykepond', 'ruddle-zhong-1988')
    entry = "research/archetypes.md - 'The 6:4 water-to-dike ratio, and coppiced mulberry', 'Why dikes were planted at all'"


class PondSluice(Kind):
    """
    What: A protected opening in a pond's dike, closed with wooden boards to set the water level and pulled to
    drain the pond at harvest - the gate through which a dike-pond exchanges water with the canal network.

    Why: A dike-pond is not a sealed basin: the whole system runs in series from a high intake to a low outfall,
    each pond taking water in at its high side and letting it out at its low side. The stub drawn here is
    the cut in the dike; the boards themselves are a few inches wide and are not drawn at this scale.

    Note: The sluice's form is read from the FAO pond-construction manual; its position on each pond is the
    engine's inlet-high, outlet-low rule from the record, not a surveyed plan.

    Caveat: its position on each pond is the engine's inlet-high, outlet-low rule from the record, not a surveyed
    plan.
    """

    key = 'pond sluice'
    name = 'pond sluice'
    covers = "the short channel stubs of `dikepond_sluices` - where each pond's dike is cut to the canal"
    label = 'accurate'
    sources = ('fao-x6708e', 'cssn-sangyuanwei')
    entry = "research/archetypes.md - 'A dike-pond is fed and drained through sluice gates'"


class SugarcaneDike(Kind):
    """
    What: The raised dike around a fish pond planted with sugar cane in close rows - the 蔗基魚塘 type of the
    dike-pond system, where the cane's bagasse feeds the pigs whose manure feeds the fish.

    Why: The dike-pond types succeeded one another across the delta: mulberry, then fruit, cane and vegetables as
    markets changed, and by the late 1980s cane dikes covered more of the district than mulberry. One hamlet
    is one type, so a cane hamlet rolls cane on every dike.

    Note: The type and the loop are read; the row pitch is a drawing calibration from the plant's habit, not a
    Ming or Qing figure.

    Caveat: the row pitch is a drawing calibration from the plant's habit, not a Ming or Qing figure.
    """

    key = 'sugarcane dike'
    name = 'sugarcane dike'
    covers = 'the bank ring of every `dikeponds[]` parcel on a hamlet whose `meta.dike_crop` is sugarcane, and its cane rows'
    label = 'accurate'
    sources = ('gd-gazetteer-sangji', 'isis-dykepond', 'ruddle-zhong-1988', 'dili360-2005-sangji')
    entry = "research/archetypes.md - 'What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit'"


class BananaDike(Kind):
    """
    What: The raised dike around a fish pond planted with banana stools - the 蕉基魚塘 type, the 'banana groves and
    sea of cane' the geographers remembered of the old delta.

    Why: Banana took the dikes where the silk market fell away; a type of the same system, drawn as a hamlet's
    whole planting because the types succeeded one another rather than mixing on a dike.

    Note: The type is read; the clump pitch and crown size are a drawing calibration from the plant's habit, not a
    surveyed figure.

    Caveat: the clump pitch and crown size are a drawing calibration from the plant's habit, not a surveyed figure.
    """

    key = 'banana dike'
    name = 'banana dike'
    covers = 'the bank ring of every `dikeponds[]` parcel on a hamlet whose `meta.dike_crop` is banana, and its clumps'
    label = 'accurate'
    sources = ('gd-gazetteer-sangji', 'dili360-2005-sangji')
    entry = "research/archetypes.md - 'What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit'"


class FruitDike(Kind):
    """
    What: The raised dike around a fish pond planted with fruit trees - lychee, longan, citrus - the 果基魚塘 type,
    the delta's older form before mulberry took the dikes.

    Why: The fruit dike is the type the delta's own accounts put first, before mulberry displaced it; the
    standard trees stand on the band's crest at an orchard's spacing.

    Note: The type is read; the tree spacing is an orchard convention, not a measured dike.

    Caveat: the tree spacing is an orchard convention, not a measured dike.
    """

    key = 'fruit dike'
    name = 'fruit dike'
    covers = 'the bank ring of every `dikeponds[]` parcel on a hamlet whose `meta.dike_crop` is fruit, and its trees'
    label = 'accurate'
    sources = ('gd-gazetteer-sangji', 'dili360-2005-sangji')
    entry = "research/archetypes.md - 'What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit'"


class VegetableGround(Kind):
    """
    What: A parcel of tilled vegetable ground in rows among the fish ponds - the one piece of the block that was
    neither dug into a pond nor left in rice.

    Why: A converted district grew no rice, and Fei's silk village grew its vegetables on whatever ground the
    mulberry left; so the residual parcel of a converted block reads as vegetable ground as honestly as
    paddy. Three attested states, so each hamlet rolls one.

    Note: The absence of rice and the vegetable ground are read; nothing says WHICH parcels carried them, so they
    take whatever the crop dikes and the ponds leave over.

    Caveat: nothing says WHICH parcels carried them, so they take whatever the crop dikes and the ponds leave over.
    """

    key = 'vegetable ground'
    name = 'vegetable ground'
    covers = 'an unconverted parcel of a wholly converted dike-pond block, on a hamlet whose `meta.leftover` is vegetables'
    label = 'accurate'
    sources = ('fei-1939', 'gd-gazetteer-sangji')
    entry = "research/archetypes.md - 'What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit'"


class PigSty(Kind):
    """
    What: A simple pig shed built on the dike of a fish pond, its pen railed at the water's edge so the pigs'
    manure runs straight into the pond.

    Why: The dike-pond loop fed its fish with more than silkworm waste: pigs, chickens and ducks were reared on
    the dikes to manure the ponds, and a cane hamlet fed its pigs on bagasse. The shed stands on the pond
    nearest the houses.

    Note: GUESS: the practice is read (the 1980s survey and the FAO/NACA manual), but nothing read gives how many
    households kept a sty in Ming or Qing; the per-hamlet share band is the generator's.
    """

    key = 'pig sty'
    name = 'pig sty'
    covers = 'every `pig_sties[]` record - a shed with its railed pen on a pond dike'
    label = 'guess'
    sources = ('fao-ac264e', 'isis-dykepond', 'ruddle-zhong-1988')
    entry = "research/archetypes.md - 'What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit'"


class DuckPen(Kind):
    """
    What: A duck pen on a fish pond: a fenced run on the dike with the duck house in it, and a fenced corner of
    the water where the birds swim - their droppings feed the fish.

    Why: Fish-cum-duck ponds fence part of the dike as a dry run and part of the water as a wet run; ducks were
    among the stock the dike-pond loop kept to manure its ponds.

    Note: GUESS: the form is read from the modern manual; its premodern prevalence is not, and the share band is
    the generator's - the weakest-evidenced item of the audit, drawn because the GM chose it.
    """

    key = 'duck pen'
    name = 'duck pen'
    covers = "every `duck_pens[]` record - a fenced dry run on the dike and a fenced wet run in the pond's corner"
    label = 'guess'
    sources = ('fao-ac264e', 'isis-dykepond')
    entry = "research/archetypes.md - 'What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit'"


class FryPond(Kind):
    """
    What: A small nursery pond where carp fry are reared before they are stocked into the grow-out ponds - the
    hamlet's own hatchery corner of the dike-pond block.

    Why: Fry were a trade of their own in the delta: Jiujiang township on the Xijiang rose on it from the Ming,
    and the polder proverb has the men trading fry while the women feed the worms. A hamlet stocking its
    ponds each year keeps a few small ponds for the fry; the smallest parcels of the block are read as
    those.

    Note: GUESS: the fry trade and the nursery stage are read, but nothing read gives how many fry ponds a hamlet
    kept or which parcels - the one-in-ten share and the choice of the smallest parcels are the generator's.
    """

    key = 'fry pond'
    name = 'fry pond'
    covers = "the dug water of a `dikeponds[]` parcel recorded `kind: fry` - the block's smallest parcels"
    label = 'guess'
    sources = ('miles-2003', 'cssn-sangyuanwei', 'isis-dykepond')
    entry = "research/archetypes.md - 'What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit'"


class ManurePit(Kind):
    """
    What: An earthenware jar sunk to its mouth in the ground behind the house, in which the household's night soil
    is kept until it goes to the fields - the manure store in its Lake Tai form.

    Why: The most important fertilizer on a rice-and-silk farm was human manure, and Fei's village kept it in
    pits of earthenware half buried behind the buildings, so many that the public road along the stream was
    lined with them. Where Tohoku farms heaped theirs by the stable, the silk villages potted theirs: two
    attested forms, so each hamlet rolls one.

    Note: The form and its place behind the house are read (Fei 1939); the drawn 3.5 ft mouth is a size the record
    does not give.

    Caveat: the drawn 3.5 ft mouth is a size the record does not give.
    """

    key = 'manure pit'
    name = 'manure pit'
    covers = 'a `farm_fixtures[]` record of kind `manure` with `form: pit` - the alternative to the heap'
    label = 'accurate'
    sources = ('fei-1939', 'sugiura-1973-fuzoku')
    entry = "research/archetypes.md - 'What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit'"


class SluiceGate(Kind):
    """
    What: The wooden boards set in the cut of a polder dike where the water comes in or goes out: dropped, they
    hold the block's water; lifted, they let it flow.

    Why: A polder is enclosed against the flood outside, so its dike is cut only where a gate controls the water
    - at the inlet high on the block and the outfall low on it. The gate is a protected opening closed with
    wooden boards to set the level, and it is why the dike can be complete and the block still fed and
    drained.

    Note: The form is read from the FAO pond-construction manual; the 6 x 3 ft bar is drawn at the size of a board
    set, a glyph the record does not measure.

    Caveat: the 6 x 3 ft bar is drawn at the size of a board set, a glyph the record does not measure.
    """

    key = 'sluice gate'
    name = 'sluice gate'
    covers = 'the board bar of every `sluice_gates[]` record - the gate in each cut of the perimeter dike'
    label = 'accurate'
    sources = ('fao-x6708e', 'cssn-sangyuanwei', 'shen-kuo')
    entry = "research/archetypes.md - 'A dike-pond is fed and drained through sluice gates', 'Polder siting - full enclosure, fluctuating water, and where the village sits'"


class PerimeterDike(Kind):
    """
    What: The hand-piled earthen embankment that encloses a polder block, following the natural water edge in
    gentle curves and non-square bends, planted with willow and mulberry to bind it, and cut only where a
    gated sluice lets water in at the high corner and out at the low one.

    Why: A polder is wetland enclosed by dikes so it can be drained; its floor sits at or below the flood stage
    outside, so the enclosure is complete - any gap re-floods the block. The dike was dredged pond mud
    heaped and packed, breached and repaired for centuries, so it reads as a mottled vegetated band of
    varying width rather than a ruled line; the dead-straight rectangle is a post-1949 industrial shape.

    Note: Full enclosure, the organic outline and the planting are read; the drawn width band (14-40 ft) is a
    drawing calibration inside the attested 6-10 m dike widths.

    Caveat: the drawn width band (14-40 ft) is a drawing calibration inside the attested 6-10 m dike widths.
    """

    key = 'perimeter dike'
    name = 'perimeter dike'
    covers = "the earthwork band of `dikes[]` - the polder's enclosing dike, gapped at its sluices"
    label = 'accurate'
    sources = ('shen-kuo', 'isis-dykepond', 'ruddle-zhong-1988')
    entry = "research/archetypes.md - 'Polder siting - full enclosure, fluctuating water, and where the village sits', 'Why dikes were planted at all'"
