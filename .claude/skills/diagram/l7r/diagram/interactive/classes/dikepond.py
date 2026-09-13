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
    and is drained two or three times a year to dredge the mud onto the dikes. The ponds here are about 4 mu of water each - a
    little over a quarter of a hectare, SMALLER than the 0.4 to 0.6 hectares the surveys of the traditional
    landscape report, because this is a hamlet and a hamlet's ponds are small.

    Note: The form and the loop are read. The pond sizes drawn here are a hamlet's own, deliberately below the
    band those surveys report - and that band is 20th-century rather than Ming or Qing, and reaches this
    record only at second hand, through a summary of a monograph with no publicly readable copy. The ratio
    behind the split is contested in its ORDER too: the classic prescription survives as six parts dike to
    four parts pond as well as the reverse, so the water-heavy reading drawn here is a regional one,
    disclosed. And the whole-block conversion drawn here is the rare end state of a normally scattered
    system.

    Caveat: that band is 20th-century rather than Ming or Qing, and reaches this
    record only at second hand, through a summary of a monograph with no publicly readable copy.

    Name: fish pond
    Covers: the dug water of every `dikeponds[]` parcel - the pond inset inside its mulberry dike
    Label: accurate
    Sources: isis-dykepond, ruddle-zhong-1988, fao-ac241e, gmrb-2024-sangji
    Entry: research/archetypes.html - 'The three overlays a village may carry', 'The 6:4 water-to-dike ratio, and coppiced mulberry', 'A dike-pond is fed and drained through sluice gates'
    """

    key = 'fish pond'


class MulberryDike(Kind):
    """
    What: The raised earthen dike around a fish pond, piled from the pond's own dredged mud and planted with
    coppiced mulberry - low bushes stripped for leaf several times a year to feed silkworms. Drawn here as a
    planted collar about seven feet wide around each pond, with a canal running between neighbors.

    Why: The dike is the silk side of the loop: mulberry leaf feeds the silkworms, the silkworm waste feeds the
    fish, the dredged pond mud re-fertilizes the dike. The prescription was six parts water to four parts
    dike (three-to-seven to four-to-six in the gazetteers) because too much water starves the worms and too
    much dike starves the fish. A bare dike of heaped mud gullies and slumps, so every dike was planted; in
    sericulture districts that planting was mulberry.

    Note: The ratio and the planting are read. The WIDTH is where the drawing parts company with the record: the
    traditional figure is a dike of six to ten meters, and the collar drawn around each pond is about two - the
    ground from one pond's water to the next is thirteen meters, but a canal runs down the middle of it, so it
    is not one bank. The traditional figure also reaches us only at second hand. The ratio's ORDER is
    contested - the classic prescription survives as six parts dike to four parts pond as well as the reverse,
    and some districts kept seven to three - so the water-heavy reading drawn here is a regional one, disclosed
    rather than the only one; measured on the map that draws them, water is 80% of the parcel ground and the
    planted bank 20%, and about half the block once the canal corridors between the parcels count. The crowns
    are drawn THINNER than the record's own guess - one bush per twenty-three square feet against a guessed one
    per ten to twenty - because at the honest step the crowns fuse into a solid green band and stop reading as
    bushes at all; the crown SIZES are drawn true, and only the density is a map drawing convention. And the
    dike is drawn as a RING, the band between the parcel's outer edge and the water's own outline, so hovering
    a dike lights its bank and not the pond inside it. So: the collar drawn around each pond is about two
    meters where the traditional figure is a dike of six to ten, and the crowns stand at one bush per
    twenty-three square feet where the record's own guess is one per ten to twenty.

    Caveat: the collar drawn around each pond is about two
    meters where the traditional figure is a dike of six to ten, and the crowns stand at one bush per
    twenty-three square feet where the record's own guess is one per ten to twenty.

    Name: mulberry dike
    Covers: the bank ring of every `dikeponds[]` parcel and the coppiced crowns planted along it
    Label: accurate
    Sources: gd-gazetteer-sangji, fao-ac241e, isis-dykepond, ruddle-zhong-1988
    Entry: research/archetypes.html - 'The 6:4 water-to-dike ratio, and coppiced mulberry', 'Why dikes were planted'
    """

    key = 'mulberry dike'


class PondCanal(Kind):
    """
    What: The canals of a dike-pond settlement: the main canal that carries water in from the reservoir and the laterals
    between the rows of ponds, which every pond both takes water from and lets water out into.

    Why: A dike-pond is not a sealed basin and its canals are not a paddy's supply net. Each pond is joined to the
    canal network through gates in its dike, taking water in at its high side and letting it out at its low side, so
    the same canal carries water to one pond and away from the next - the network the whole system exchanges water
    with, running in series from the high intake to the low outfall. Which way a given canal carries water depends on the
    gates that open onto it - some take only feeds, some only drains, some both - and the ring drain around the block
    takes everything to the outfall.

    Note: That the canals are a conveyance-and-drainage network the ponds exchange water with is documented; which pond's
    gate opens onto which canal follows this map's own rule - water in on each pond's high side, out on its low side - not a
    surveyed plan.

    Caveat: which pond's gate opens onto which canal follows this map's own rule - water in on each pond's high side, out on its
    low side - not a surveyed plan.

    Name: pond canal
    Covers: `field_ditches` whose role is not `drain` on a dike-pond field - the main from the reservoir and the laterals between the ponds
    Label: accurate
    Sources: fao-x6708e, cssn-sangyuanwei, cssn-jiangnan-weitian
    Entry: research/archetypes.html - 'A dike-pond is fed and drained through sluice gates'
    """

    key = 'pond canal'


class PondSluice(Kind):
    """
    What: A protected opening in a pond's dike, closed with wooden boards to set the water level and pulled to
    drain the pond at harvest - the gate through which a dike-pond exchanges water with the canal network.

    Why: A dike-pond is not a sealed basin: the whole system runs in series from a high intake to a low outfall,
    each pond taking water in at its high side and letting it out at its low side. The stub drawn here is
    the cut in the dike; the boards themselves are a few inches wide and are not drawn at this scale.

    Note: The sluice's form is documented in the FAO pond-construction manual; its position on each pond follows the
    record's rule - water in on the pond's high side, out on its low side - not a surveyed plan.

    Caveat: its position on each pond follows the record's rule - water in on the pond's high side, out on its low side - not a
    surveyed plan.

    Name: pond sluice
    Covers: the short channel stubs of `dikepond_sluices` - where each pond's dike is cut to the canal
    Label: accurate
    Sources: fao-x6708e, cssn-sangyuanwei
    Entry: research/archetypes.html - 'A dike-pond is fed and drained through sluice gates'
    """

    key = 'pond sluice'


class SugarcaneDike(Kind):
    """
    What: The raised dike around a fish pond planted with sugar cane in close rows - the 蔗基魚塘 type of the
    dike-pond system, whose young leaves went to the fish and the pigs and whose refinery waste came back to the
    pond as feed.

    Why: The dike-pond types succeeded one another across the delta: mulberry, then fruit, cane and vegetables as
    markets changed, and by the late 1980s cane dikes covered more of the district than mulberry. One hamlet
    is one type, so a cane hamlet rolls cane on every dike.

    Note: The type is read, and so is the loop as written above - the young leaves fed to fish and pigs, the old
    ones shading the vegetable ground, the refinery waste returned to the pond. The often-repeated version of
    that loop, in which the pressed cane's bagasse goes to the pigs, is on no page read, and the row pitch is
    a drawing calibration from the plant's habit, not a Ming or Qing figure.

    Caveat: the row pitch is a drawing calibration from the plant's habit, not a Ming or Qing figure.

    Name: sugarcane dike
    Covers: the bank ring of every `dikeponds[]` parcel on a hamlet whose `meta.dike_crop` is sugarcane, and its cane rows
    Label: accurate
    Sources: gd-gazetteer-sangji, isis-dykepond, ruddle-zhong-1988, dili360-2005-sangji
    Entry: research/archetypes.html - 'What stands on a dike-pond hamlet that a paddy hamlet lacks?'
    """

    key = 'sugarcane dike'


class BananaDike(Kind):
    """
    What: The raised dike around a fish pond planted with banana stools - the 蕉基魚塘 type, the 'banana groves and
    sea of cane' the geographers remembered of the old delta.

    Why: A type of the same system, drawn as a hamlet's whole planting because the types succeeded one another
    rather than mixing on a dike. WHY banana took a dike is on no page read; what the accounts give is the type
    itself, and the remembered banana groves and sea of cane of the old delta.

    Note: The type is read; the clump pitch and crown size are a drawing calibration from the plant's habit, not a
    surveyed figure, and no page read gives the reason banana replaced another crop on a bank.

    Caveat: the clump pitch and crown size are a drawing calibration from the plant's habit, not a surveyed
    figure, and no page read gives the reason banana replaced another crop on a bank.

    Name: banana dike
    Covers: the bank ring of every `dikeponds[]` parcel on a hamlet whose `meta.dike_crop` is banana, and its clumps
    Label: accurate
    Sources: gd-gazetteer-sangji, dili360-2005-sangji
    Entry: research/archetypes.html - 'What stands on a dike-pond hamlet that a paddy hamlet lacks?'
    """

    key = 'banana dike'


class FruitDike(Kind):
    """
    What: The raised dike around a fish pond planted with fruit trees - the 果基魚塘 type of the dike-pond system.

    Why: The dike-pond types succeeded one another across the delta, and the gazetteer office puts mulberry
    first, with the fruit, cane and vegetable dikes following it as markets changed. One hamlet is one type, so
    a fruit hamlet rolls fruit on every dike, and the trees stand on the band's crest at an orchard's spacing.

    Note: The type is read; WHICH fruit is not - no page read names a species for a fruit dike - and the tree
    spacing is an orchard convention, not a measured dike.

    Caveat: no page read names a species for a fruit dike - and the tree spacing is an orchard convention, not
    a measured dike.

    Name: fruit dike
    Covers: the bank ring of every `dikeponds[]` parcel on a hamlet whose `meta.dike_crop` is fruit, and its trees
    Label: accurate
    Sources: gd-gazetteer-sangji, dili360-2005-sangji
    Entry: research/archetypes.html - 'What stands on a dike-pond hamlet that a paddy hamlet lacks?'
    """

    key = 'fruit dike'


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

    Name: vegetable ground
    Covers: an unconverted parcel of a wholly converted dike-pond block, on a hamlet whose `meta.leftover` is vegetables
    Label: accurate
    Sources: fei-1939, gd-gazetteer-sangji
    Entry: research/archetypes.html - 'What stands on a dike-pond hamlet that a paddy hamlet lacks?'
    """

    key = 'vegetable ground'


class PigSty(Kind):
    """
    What: A simple pig shed built on the dike of a fish pond, a railed yard beside it along the bank, so the
    pigs' manure runs straight into the water. It stands a few feet clear of the short culvert that feeds or drains
    its pond, on the bank nearest the houses.

    Why: The shed is at the water on purpose - that is the whole arrangement, not an accident of crowding. A pig
    shed is built on a pond dike so the excrement is flushed directly into the pond, where it feeds the water
    rather than fouling it: the manure raises the plankton the fish eat. So the pigs are part of what feeds the
    fish the household cultivates. What the shed keeps clear of is the sluice itself - nobody builds over the
    opening they have to reach in order to lift its boards, and that is a matter of getting at the gate rather
    than of keeping the water clean. A pig penned on a pond DIKE is a Chinese form. Japan kept pigs - their
    bones are excavated at the Satsuma domain's Edo residence, at Osaka castle, at Hakata and at Nagasaki
    harbor, and the familiar account that the country did not is called an assumption under review by its most
    recent scholarly treatment - but nothing read links a Japanese pig to a pond at all. So it is the FORM
    rather than the animal that belongs to this kind of hamlet and to no other on these maps.

    Note: GUESS: the practice is read, and so is the reason the shed sits at the water, but nothing read gives
    how many households kept a sty in Ming or Qing - the per-hamlet share band is the generator's. The few feet
    of clearance at the sluice is a guess too: the record gives dike widths and no spacing along a dike at all.
    And the one width it does give, a shed-carrying dike of five to ten meters, the drawn bank does not meet -
    the planted collar under these sheds is two to five meters. That figure is a modern design requirement
    rather than a measurement of any old dike, and no older one was found to judge the bank by, but a reader
    measuring the collar should know it is snug.

    Name: pig sty
    Covers: every `pig_sties[]` record - a shed with its railed pen on a pond dike
    Label: guess
    Sources: fao-ac264e, fao-ac264e-ch9, fao-y1187e, qimin-yaoshu-yangzhu, isis-dykepond, ruddle-zhong-1988
    Entry: research/archetypes.html - "Does a pig sty have to stand back from the water, or from the pond's sluice?", 'What stands on a dike-pond hamlet that a paddy hamlet lacks?'
    """

    key = 'pig sty'


class DuckPen(Kind):
    """
    What: A duck pen on a fish pond: a fenced run on the dike with the duck house in it, and a fenced corner of
    the water where the birds swim - their droppings feed the fish. Both the dry run and the fence reaching into
    the water stand clear of the pond's own culvert.

    Why: Fish-cum-duck ponds fence part of the dike as a dry run and part of the water as a wet run; ducks were
    among the stock the dike-pond loop kept to manure its ponds, and the droppings feed the water the same way a
    pig shed's do. The dry run stands on the same planted collar a pig shed does - two to five meters, where the
    one width the record gives for a dike carrying an animal shed is five to ten, and that is a modern design
    requirement whose ceiling is set by cart traffic and pipework a hand-piled dike never carried. The fence
    keeps off the culvert for the plain reason that a fence across the opening a pond is filled and drained
    through would be in the way of working it.

    Note: GUESS: the form is read from the modern manual; its premodern prevalence is not, and the share band is
    the generator's - the weakest-evidenced item of the audit, drawn because the GM chose it. The clearance at
    the culvert is a guess as well; nothing read gives a spacing along a dike.

    Name: duck pen
    Covers: every `duck_pens[]` record - a fenced dry run on the dike and a fenced wet run in the pond's corner
    Label: guess
    Sources: fao-ac264e, fao-ac264e-ch9, isis-dykepond
    Entry: research/archetypes.html - "Does a pig sty have to stand back from the water, or from the pond's sluice?", 'What stands on a dike-pond hamlet that a paddy hamlet lacks?'
    """

    key = 'duck pen'


class FryPond(Kind):
    """
    What: A small nursery pond where carp fry are reared before they are stocked into the grow-out ponds - the
    hamlet's own hatchery corner of the dike-pond block.

    Why: Fry were a trade of their own in the delta: a seventeenth-century account of Guangdong has the men
    trading fish fry while the women feed and tend the silkworms. A hamlet stocking its ponds each year keeps
    a few small ponds for the fry; the smallest parcels of the block are read as those.

    Note: GUESS: the fry trade and the nursery stage are read, but the naming of one township and the century the
    trade rose in are not - the work that carried them is not readable anywhere - and nothing read gives how
    many fry ponds a hamlet kept or which parcels, so the one-in-ten share and the choice of the smallest
    parcels are the generator's.

    Name: fry pond
    Covers: the dug water of a `dikeponds[]` parcel recorded `kind: fry` - the block's smallest parcels
    Label: guess
    Sources: cssn-sangyuanwei, isis-dykepond
    Entry: research/archetypes.html - 'What stands on a dike-pond hamlet that a paddy hamlet lacks?'
    """

    key = 'fry pond'


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

    Name: manure pit
    Covers: a `farm_fixtures[]` record of kind `manure` with `form: pit` - the alternative to the heap
    Label: accurate
    Sources: fei-1939, sugiura-1973-fuzoku
    Entry: research/archetypes.html - 'What stands on a dike-pond hamlet that a paddy hamlet lacks?'
    """

    key = 'manure pit'


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

    Name: sluice gate
    Covers: the board bar of every `sluice_gates[]` record - the gate in each cut of the perimeter dike
    Label: accurate
    Sources: fao-x6708e, cssn-sangyuanwei, shen-kuo
    Entry: research/archetypes.html - 'A dike-pond is fed and drained through sluice gates', 'Polder siting - full enclosure, fluctuating water, and where the village sits'
    """

    key = 'sluice gate'


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

    Name: perimeter dike
    Covers: the earthwork band of `dikes[]` - the polder's enclosing dike, gapped at its sluices
    Label: accurate
    Sources: shen-kuo, isis-dykepond, ruddle-zhong-1988
    Entry: research/archetypes.html - 'Polder siting - full enclosure, fluctuating water, and where the village sits', 'Why dikes were planted'
    """

    key = 'perimeter dike'
