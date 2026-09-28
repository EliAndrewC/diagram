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
    centuries. Each pond is fed and drained through a sluice in its dike, plumbed inlet-high and outlet-low where the ground slopes,
    and is drained two or three times a year to dredge the mud onto the dikes. The ponds here are about 4 mu of water each - a
    little over a quarter of a hectare, SMALLER than the 0.4 to 0.6 hectares the surveys of the traditional
    landscape report, because this is a hamlet and a hamlet's ponds are small. What lives in it is carp. The
    young carp were not bred here: they were netted wild in the West River by the fry households of one
    township, Jiujiang, and sold to the pond districts, so an ordinary hamlet bought its fry and
    raised them to grown fish. A late-Ming farming compendium, written far to the north in Shanghai, names
    two carps fed in a fish pond there, the grass carp and the silver carp; of the delta's own ponds the record says only that they raised the four domestic carps.

    Note: The form and the loop are read, save the inlet-high, outlet-low plumbing, which rests on a monograph with no publicly readable copy. The pond sizes drawn here are a hamlet's own, deliberately below the
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
    Sources: isis-dykepond, ruddle-zhong-1988, fao-ac241e, gmrb-2024-sangji, guangdong-xinyu-22, pwsannong-zhusanjiao-nongyeshi, nongzheng-quanshu-41
    Entry: research/archetypes.html - 'The three overlays a village may carry', 'The 6:4 water-to-dike ratio, and coppiced mulberry', 'A dike-pond is fed and drained through sluice gates', "Did a dike-pond village rear its own fish fry, or buy them? Most bought them - the nursery ponds were one township's trade", 'Which animals did a dike-pond village keep at its ponds? Pigs - the ducks were herded in the rice fields'
    """

    key = 'fish pond'


class MulberryDike(Kind):
    """
    What: The raised earthen dike around a fish pond, piled from the pond's own dredged mud and planted with
    coppiced mulberry - low bushes stripped for leaf several times a year to feed silkworms. Drawn here as a
    planted collar about seven feet wide around each pond, with a canal running between neighbors.

    Why: The dike is the silk side of the loop: mulberry leaf feeds the silkworms, the silkworm waste feeds the
    fish, the dredged pond mud re-fertilizes the dike. The prescription was six parts water to four parts
    dike (the Guangdong gazetteer's water-to-dike split of three-seven to four-six, read in the order it names, leans the other way) because the dike's mulberry had to yield enough
    feed and fertilizer for the fish in the water beside it. A bare dike of heaped mud gullies and slumps, so every dike was planted; in
    sericulture districts that planting was mulberry.

    Note: The ratio and the planting are read. The WIDTH is where the drawing parts company with the record: the
    traditional figure is a dike of six to ten meters, and the collar drawn around each pond is about two - the
    ground from one pond's water to the next is thirteen meters, but a canal runs down the middle of it, so it
    is not one bank. The traditional figure also reaches us only at second hand. The ratio's ORDER is
    contested - the classic prescription survives as six parts dike to four parts pond as well as the reverse,
    and seven to three is recorded where the fish had feed from beyond the dike - so the water-heavy reading drawn here is a regional one, disclosed
    rather than the only one; measured on the map that draws them, water is 80% of the parcel ground and the
    planted bank 20%, and about half the block once the canal corridors between the parcels count. How
    thickly mulberry stood depended on how low it was cut, along one continuum: from about one bush to a
    square foot in the Pearl River delta's root-cut planting, a figure given as current practice with no date,
    to about 300 trees a mu - one to about 24 square feet - in the late-Qing Yangtze delta, the only figure
    dated before the modern period; none was measured on a pond dike. The crowns are drawn at about one bush
    per twenty-three square feet, the late-Qing figure, by the GM's ruling that the map keeps the premodern
    spacing. No page read gives how wide a bush grew, so the four and a half to seven feet drawn is this
    project's own figure. And the dike is drawn as a RING, the band between the parcel's outer edge and the
    water's own outline, so hovering a dike lights its bank and not the pond inside it. So: the collar drawn
    around each pond is about two meters where the traditional figure is a dike of six to ten, and the width
    of a bush's crown is this project's own.

    Caveat: the collar drawn
    around each pond is about two meters where the traditional figure is a dike of six to ten, and the width
    of a bush's crown is this project's own.

    Name: mulberry dike
    Covers: the bank ring of every `dikeponds[]` parcel and the coppiced crowns planted along it
    Label: accurate
    Sources: gd-gazetteer-sangji, fao-ac241e, isis-dykepond, ruddle-zhong-1988, pwsannong-gudai-zaisang, pwsannong-sangji-yutang, kotobank-souen, kotobank-negari
    Entry: research/archetypes.html - 'The 6:4 water-to-dike ratio, and coppiced mulberry', 'Why dikes were planted', 'How thickly was dike mulberry planted, and how wide did a bush grow?'
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

    Note: That a pond's dike carries a board sluice, opened and shut to set its water level, is documented; that each pond's sluice opens onto the canal network, so the canals are the conveyance-and-drainage network the ponds exchange water with, and that a pond on sloping ground takes water in high and lets it out low, the whole net running in series from a high intake to a low outfall, are Ruddle & Zhong's (1988) findings, which this project has not read, as no copy is publicly readable; which pond's
    gate opens onto which canal follows this map's own rule - water in on each pond's high side, out on its low side - not a
    surveyed plan. The ring drain around the block is this map's own layout, borrowed from the rice polder's inner ring
    canal: no source the record cites describes a ring drain on a dike-pond.

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
    drain the pond two or three times a year - the gate through which a dike-pond exchanges water with the canal network.

    Why: A dike-pond is not a sealed basin: the whole system runs in series from a high intake to a low outfall,
    a pond on sloping ground taking water in at its high side and letting it out at its low side. The stub drawn here is
    the cut in the dike; the gate itself is at most 0.80 m wide inside and is not drawn at this scale.

    Note: The sluice's form is documented in the FAO pond-construction manual; that it opens onto the canal network also comes only from Ruddle & Zhong, with no public page read saying so, and reading the Minle proverb's 窦 (dou) as a sluice is this project's guess; its position on each pond follows the
    record's rule - water in on the pond's high side, out on its low side - which the record takes from Ruddle & Zhong (1988), a book with no readable copy that this project has not read; it is not a surveyed plan.

    Caveat: its position on each pond follows the record's rule - water in on the pond's high side, out on its low side - which the record takes from Ruddle & Zhong (1988), a book with no readable copy that this project has not read; it is not a surveyed plan.

    Name: pond sluice
    Covers: the short channel stubs of `dikepond_sluices` - where each pond's dike is cut to the canal
    Label: accurate
    Sources: fao-x6708e, cssn-sangyuanwei
    Entry: research/archetypes.html - 'A dike-pond is fed and drained through sluice gates'
    """

    key = 'pond sluice'


class FruitDike(Kind):
    """
    What: The raised dike around a fish pond planted with fruit trees - the 果基魚塘 type of the dike-pond system:
    lychee above all, with longan, mandarin and orange, standing in a single line along the bank's crest.

    Why: The fruit dike is the oldest dike-pond planting read. Qu Dajun, writing of Guangdong in the late
    seventeenth century, says the villages of Guangzhou's large counties often gave up good fields to make
    dikes and planted them with fruit trees - lychee most, tea and mulberry next, then mandarin and orange -
    with a pond for fish below the dike. A modern history of the delta's farming dates the order: fruit-dike
    fish ponds arose first, in Nanhai and Shunde in the mid-Ming, and the mulberry dike replaced them in the
    late Ming and early Qing and became the dominant type in the Qing. So in Qu Dajun's day the fruit dike
    still stood beside the mulberry, and a hamlet may roll it as its dike crop, as it may mulberry or tea. One
    hamlet is one planting, so a fruit hamlet plants fruit on every dike.

    Note: The fruit dike, its age and its fruit are read. How thickly the trees stood is known only for a
    field turned to orchard - twenty-odd lychee to a mu, about one tree to 300 square feet - and nothing read
    gives the spacing along a dike, so the trees drawn about eighteen feet apart on the crest are this
    project's own, and so is how often a hamlet rolls fruit, about two in six. So is one planting to a
    hamlet: Qu Dajun names the fruit, tea and mulberry of the villages' dikes together, and only the modern
    gazetteer's succession of dike types puts one type to a place.

    Caveat: nothing read
    gives the spacing along a dike, so the trees drawn about eighteen feet apart on the crest are this
    project's own, and so is how often a hamlet rolls fruit, about two in six. So is one planting to a
    hamlet: Qu Dajun names the fruit, tea and mulberry of the villages' dikes together, and only the modern
    gazetteer's succession of dike types puts one type to a place.

    Name: fruit dike
    Covers: the bank ring of every `dikeponds[]` parcel on a hamlet whose `meta.dike_crop` is fruit, and its trees
    Label: accurate
    Sources: guangdong-xinyu-22, guangdong-xinyu-25, pwsannong-zhusanjiao-nongyeshi, gd-gazetteer-sangji
    Entry: research/archetypes.html - 'Were fruit, cane or banana dikes older than the mulberry dike? Fruit was - lychee above all', 'What else was planted on a pond dike besides mulberry?', 'What stands on a dike-pond hamlet that a paddy hamlet lacks?'
    """

    key = 'fruit dike'


class TeaDike(Kind):
    """
    What: The raised dike around a fish pond planted with tea: low bushes, clipped to a hedge, standing in two
    rows along the bank - a dike-pond planting beside the mulberry and the fruit.

    Why: Qu Dajun, writing in the late seventeenth century, says the villages of Guangzhou's large counties often
    gave up good fields to make dikes and planted them with fruit trees - lychee most, tea and mulberry next.
    So tea stood on the delta's pond dikes in his day, and a hamlet may roll it as its dike crop, as it may
    mulberry or fruit. One hamlet is one planting.

    Note: The tea dike is read, but only named in a list: nothing read says how the bushes stood on a dike, so the
    two clipped rows drawn here and their spacing are this project's own, and so is how often a hamlet rolls tea,
    about one in six, and so is one planting to a hamlet, since Qu Dajun names the dike crops together.

    Caveat: nothing read says how the bushes stood on a dike, so the two clipped rows drawn here and their spacing
    are this project's own, and so is how often a hamlet rolls tea, about one in six, and so is one planting to a
    hamlet, since Qu Dajun names the dike crops together.

    Name: tea dike
    Covers: the bank ring of every `dikeponds[]` parcel on a hamlet whose `meta.dike_crop` is tea, and its bushes
    Label: accurate
    Sources: guangdong-xinyu-22
    Entry: research/archetypes.html - 'Were fruit, cane or banana dikes older than the mulberry dike? Fruit was - lychee above all'
    """

    key = 'tea dike'


class PigSty(Kind):
    """
    What: A simple pig shed built on the dike of a fish pond, a railed yard beside it along the bank, so the
    pigs' manure runs straight into the water. It stands a few feet clear of the short culvert that feeds or drains
    its pond, on the bank nearest the houses.

    Why: The shed is at the water on purpose - that is the whole arrangement, not an accident of crowding. A pig
    shed is built on a pond dike so the excrement is flushed directly into the pond, where it feeds the water
    rather than fouling it: the manure raises the plankton the fish eat. It does so only in measure: too many pigs at one spot and the fish come up gasping, and the water right under the shed goes airless unless the manure is spread across the pond - a thing handled with buckets and channels rather than by moving the shed, and not drawn. So the pigs are part of what feeds the
    fish the household cultivates. What the shed keeps clear of is the sluice itself - nobody builds over the
    opening they have to reach in order to lift its boards, and that is a matter of getting at the gate rather
    than of keeping the water clean. A pig penned on a pond DIKE is a Chinese form. Japan kept pigs - their
    bones are excavated at the Satsuma domain's Edo residence, at Osaka castle, at Hakata and at Nagasaki
    harbor, and the familiar account that the country did not is called an assumption under review by its most
    recent scholarly treatment - but nothing read links a Japanese pig to a pond at all. So it is the FORM
    rather than the animal that belongs to this kind of hamlet and to no other on these maps. And the pig is
    the dike-pond village's own animal: a modern history of the Pearl River delta's farming names pig-raising
    as the dike-pond district's stock, as duck-raising was the sand fields', and puts the pig inside the Qing
    loop - fed from the pond, its dung and the pond mud manuring the mulberry. A pen on a fish-pond bank is an
    old instruction too: a farming compendium printed in 1639, written far to the north in Shanghai, advises
    penning a flock of sheep - the form, not the pig - on the bank of a fish pond and sweeping its dung into the water each morning to feed the
    fish.

    Note: The sty is read - the pig as the dike-pond village's animal and the pen on the pond bank - and so is
    the reason the shed sits at the water. But nothing read gives how many households kept a sty: the
    quarter to half of the households drawn with one, rolled per hamlet, is a guess. The few feet
    of clearance at the sluice is a guess too: the record gives dike widths and no spacing along a dike at all.
    And the widths it does give, the drawn bank does not meet - the planted collar under these sheds is two to
    five meters, short of the five-meter floor a modern manual sets for a shed-carrying dike (its ten-meter ceiling answers to pigsties, piping and traffic together, and the traffic at least, if it ran on the dikes as this page infers, is later than this map), while a Shunde village's dikes
    ran twenty meters before commercial fish farming eroded them, a width later than this map and so no measure of it;
    a reader measuring the collar should know it is snug by a modern standard and that no older standard was found to judge it by.

    Caveat: nothing read gives how many households kept a sty: the
    quarter to half of the households drawn with one, rolled per hamlet, is a guess.

    Name: pig sty
    Covers: every `pig_sties[]` record - a shed with its railed pen on a pond dike
    Label: accurate
    Sources: fao-ac264e, fao-ac264e-ch9, fao-y1187e, qimin-yaoshu-yangzhu, fao-ac257e, fao-x6708e, isis-dykepond, ruddle-zhong-1988, pwsannong-zhusanjiao-nongyeshi, nongzheng-quanshu-41
    Entry: research/archetypes.html - "Does a pig sty have to stand back from the water, or from the pond's sluice?", 'Which animals did a dike-pond village keep at its ponds? Pigs - the ducks were herded in the rice fields', 'Does a dike-pond hamlet keep pigs and ducks on its pond dikes?', 'What stands on a dike-pond hamlet that a paddy hamlet lacks?'
    """

    key = 'pig sty'


class FryPond(Kind):
    """
    What: A small nursery pond where carp fry are reared, then grown on as fingerlings, before they are stocked
    into the grow-out ponds - the hamlet's own nursery corner of the dike-pond block.

    Why: Fry were a trade of their own in the delta, and one township's. The young carp that stocked the ponds
    were netted wild in the West River by the fry households of Jiujiang in Nanhai, who held the fry-catching
    landings on the river - granted to them in the Hongzhi reign (1488-1505) - and supplied the other pond
    districts. Qu Dajun, writing in the late seventeenth century, says fry ponds were found only in Jiujiang,
    where seven parts in ten of the pond water raised fry; elsewhere the ponds mostly raised grown fish, and
    where they tried to raise fry the fry did not thrive. So the record holds two kinds of dike-pond village:
    one that raises grown fish and buys its fry, with no nursery ponds at all, and a fry village of the
    Jiujiang kind, where most of the water is nursery water.

    Note: GUESS: the fry trade, the township that held it and the two kinds of village are read, but the map
    draws neither: it marks the smallest parcels of a block, about one in ten, as fry ponds, a share that
    matches no village read and rests on the assumption that nursery ponds were the smallest, and the order of fry pond, fingerling pond and grow-out pond is a modern manual's, with no premodern block read; which of the two
    kinds a hamlet should be is awaiting the GM's ruling.

    Name: fry pond
    Covers: the dug water of a `dikeponds[]` parcel recorded `kind: fry` - the block's smallest parcels
    Label: guess
    Sources: cssn-sangyuanwei, isis-dykepond, guangdong-xinyu-22, pwsannong-zhusanjiao-nongyeshi
    Entry: research/archetypes.html - "Did a dike-pond village rear its own fish fry, or buy them? Most bought them - the nursery ponds were one township's trade", 'Were fish fry a trade, and which ponds were the nursery ponds?', 'What stands on a dike-pond hamlet that a paddy hamlet lacks?'
    """

    key = 'fry pond'


class ManurePit(Kind):
    """
    What: An earthenware jar half buried in the ground, in which the household's night soil is kept until it
    goes to the fields - the manure store in its Lake Tai form. Each hamlet has its own mix: some stand behind the house beside its privy,
    others out at the edge of the household's nearest field, or beside a road.

    Why: The most important fertilizer on a rice-and-silk farm was human manure, and Fei's village kept it in
    pits of earthenware half buried behind the buildings, so many that the public road along the stream was
    lined with them. Where Tohoku farms heaped theirs by the stable, the silk villages potted theirs: two
    attested forms, so each hamlet rolls one. Where the pit stood is a second choice. A 1959 survey of three
    Japanese villages found night soil kept in a tank beside the privy or in a pit out by the fields, the
    tank thought to have moved from the privy to the fields or the roadside to make manuring easier, and the
    share of households with a field pit ran from 2 of 83 in one village to 15 of 18 in another. So each
    hamlet rolls its share of field pits somewhere between almost none and most households.

    Note: The form and its place behind the house are read (Fei 1939), and so are the field pit and how widely
    its share varied (the highest, 15 of 18, in a village whose field pits also took night soil carted in from Sendai); carrying the field pit, found in Japan, to the silk village's jar is this project's own
    step, and the drawn 3.5 ft mouth is a size the record does not give.

    Caveat: carrying the field pit, found in Japan, to the silk village's jar is this project's own
    step, and the drawn 3.5 ft mouth is a size the record does not give.

    Name: manure pit
    Covers: a `farm_fixtures[]` record of kind `manure` with `form: pit` - the alternative to the heap
    Label: accurate
    Sources: fei-1939, sugiura-1973-fuzoku, suzuki-1959-noson-benjo
    Entry: research/archetypes.html - 'What stands on a dike-pond hamlet that a paddy hamlet lacks?'; research/homesteads.html - 'Where did the privy stand, and where was its night soil kept?'
    """

    key = 'manure pit'


class SluiceGate(Kind):
    """
    What: The wooden boards set in the cut of a polder dike where the water comes in or goes out: dropped, they
    hold the block's water; lifted, they let it flow.

    Why: A polder is enclosed against the flood outside, so its dike is cut only where a gate controls the water
    - at the inlet high on the block and the outfall low on it. The gate is a protected opening closed with
    wooden boards to set the level - opened in drought to draw the river in, shut in flood to keep it out - and it is why the dike can be complete and the block still fed and
    drained.

    Note: The form is read from the FAO pond-construction manual, and its opening in drought and shutting in flood from a Chinese account of the Jiangnan polders; the dou a Minle proverb names is taken for this sluice only by this project's guess, since no source read defines the word; the inlet-high, outfall-low placement comes from Ruddle & Zhong (1988), which has no readable copy and is not read; the 6 x 3 ft bar is drawn at the size of a whole board set, which the record does not measure; the FAO manual caps the opening itself at 0.80 m, less than half the bar.

    Caveat: the 6 x 3 ft bar is drawn at the size of a whole board set, which the record does not measure; the FAO manual caps the opening itself at 0.80 m, less than half the bar.

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

    Note: Full enclosure, the organic outline and the planting are read, though that any gap re-floods the block is this project's reasoning from the general polder; the drawn width band (14-40 ft) is a
    drawing calibration inside the attested 6-10 m dike widths.

    Caveat: the drawn width band (14-40 ft) is a drawing calibration inside the attested 6-10 m dike widths.

    Name: perimeter dike
    Covers: the earthwork band of `dikes[]` - the polder's enclosing dike, gapped at its sluices
    Label: accurate
    Sources: shen-kuo, isis-dykepond, ruddle-zhong-1988
    Entry: research/archetypes.html - 'Polder siting - full enclosure, fluctuating water, and where the village sits', 'Why dikes were planted'
    """

    key = 'perimeter dike'
