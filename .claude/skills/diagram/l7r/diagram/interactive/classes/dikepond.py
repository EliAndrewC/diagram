"""The dike-pond hamlet (feature 150, Kuwabata) - ponds, planted dikes, the polder's sluice gates, the stock and the enclosing dike.

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
    raises the dike, so the landscape was made cell by cell - by the households that farmed it, this record guesses, no page saying who dug - over
    centuries, into a mosaic of ponds of varied size round the creeks rather than a surveyed chessboard - the uniform
    grid of ponds is today's aerial view. The ponds lie in the creeks and canals the polder's own sluice gates feed and
    drain, and each is drained two or three times a year to dredge the mud onto the dikes. The ponds here are about 4 mu
    of water each, a hamlet's own, and about six parts in ten of a pond's parcel is water: the oldest figures, a
    township's of 1678, give the fish half its land and the ponds eight tenths of it, and every ratio written as a number
    is modern. What lives in it is carp. The young carp were not bred here: they were netted wild in the West River by
    the fry households of one township, Jiujiang, and sold to the pond districts, so an ordinary hamlet bought its fry
    and raised them to grown fish. A late-Ming farming compendium, written far to the north in Shanghai, names two carps
    fed in a fish pond there, the grass carp and the silver carp; of the delta's own ponds the record says only that
    they raised the four domestic carps.

    Note: The form, the mosaic and the loop are read. Reading the township's two shares together as six parts water in
    ten of a parcel is this record's arithmetic, a guess; the dike is drawn 23 ft, inside the modern 6 to 10 m, no width before modern
    times being found. The water-heavy order is a regional reading, the reverse, six parts dike to four of pond, being
    recorded too. The pond sizes drawn here are a hamlet's own, below the band 20th-century surveys report. And the
    whole-block conversion drawn here is the rare end state of a normally scattered system. A sluice through each pond's
    own dike is found only in a modern manual and is not drawn.

    Caveat: Reading the township's two shares together as six parts water in ten of a parcel is this record's
    arithmetic, a guess; the dike is drawn 23 ft, inside the modern 6 to 10 m, no width before modern times being found.

    Name: fish pond
    Covers: the dug water of every `dikeponds[]` parcel - the pond inset inside its mulberry dike
    Label: accurate
    Sources: isis-dykepond, ruddle-zhong-1988, gmrb-2024-sangji, guangdong-xinyu-22, pwsannong-zhusanjiao-nongyeshi, nongzheng-quanshu-41, minle-dou-people
    Entry: research/archetypes.html - 'Cash crops on rice land: dike-ponds, lotus fields and tea rows', 'Dike-ponds: fish ponds ringed by mulberry dikes (sangji yutang)', "Did a dike-pond village rear its own fish fry, or buy them? Most bought them - the nursery ponds were one township's trade", 'Which animals did a dike-pond village keep at its ponds? Pigs - the ducks were herded in the rice fields'; research/rendering/archetypes.html - "How our maps lay cash crops over a village's rice land", 'How our maps draw dike-ponds (sangji yutang)'
    """

    key = 'fish pond'


class MulberryDike(Kind):
    """
    What: The raised earthen dike around a fish pond, piled from the pond's own dredged mud and planted with
    coppiced mulberry - low bushes stripped for leaf several times a year to feed silkworms. Drawn here as a
    planted collar around each pond, twenty-three feet wide on the average but thinner along a long pond's sides and wider at
    its ends, with a canal running between neighbors.

    Why: The dike is the silk side of the loop: mulberry leaf feeds the silkworms, the silkworm waste feeds the
    fish, the dredged pond mud re-fertilizes the dike. The prescription was six parts water to four parts
    dike (the Guangdong gazetteer's water-to-dike split of three-seven to four-six, read in the order it names, leans the other way) because the dike's mulberry had to yield enough
    feed and fertilizer for the fish in the water beside it. Every dike on record was planted, a bare bank of heaped mud being
    apt, in this project's reasoning, to gully and slump; in sericulture districts that planting was mulberry.

    Note: The ratio and the planting are read, though every page that writes the ratio as a number is modern - the oldest figures found, Qu Dajun's shares of one township's land in 1678, are not a ratio, and the six parts water in ten drawn here is this project's guess from reading his two shares together. The modern width is a dike of six to ten meters, no width being found from before modern times (one modern study has dikes once twenty meters wide worn to under four as the ponds were enlarged), and the water drawn stands about seven meters in from each parcel's edge, though a canal runs between two parcels, so two ponds' banks are not one bank. The modern figure also reaches us only at second hand. The ratio's ORDER is
    contested - the classic prescription survives as six parts dike to four parts pond as well as the reverse,
    and seven to three is recorded where the fish had feed from beyond the dike - so the water-heavy reading drawn here is a regional one, disclosed
    rather than the only one; as drawn, water is about six parts in ten of each parcel and the planted bank the rest, and less across the whole block once the canal corridors between the parcels count. How
    thickly mulberry stood depended on how low it was cut, along one continuum: from about one bush to a
    square foot in the Pearl River delta's root-cut planting, a figure given as current practice with no date,
    to about 300 trees a mu - one to about 24 square feet - in the late-Qing Yangtze delta, the only figure
    dated before the modern period; only the delta's figure is given for pond dikes, said to be planted much as any flat-land mulberry field. The crowns are drawn at about one bush
    per twenty-four square feet, the late-Qing figure, by the GM's ruling that the map keeps the premodern
    spacing. No page read gives how wide a bush grew, so the four and a half to seven feet drawn is this
    project's own figure. And the dike is drawn as a RING, the band between the parcel's outer edge and the
    water's own outline, so hovering a dike lights its bank and not the pond inside it. So: the width of a bush's crown is this project's own, and so is the six-in-ten split drawn from Qu Dajun's two shares.

    Caveat: the width of a bush's crown is this project's own, and so is the six-in-ten split drawn from Qu Dajun's two shares.

    Name: mulberry dike
    Covers: the bank ring of every `dikeponds[]` parcel and the coppiced crowns planted along it
    Label: accurate
    Sources: gd-gazetteer-sangji, fao-ac241e, isis-dykepond, ruddle-zhong-1988, pwsannong-gudai-zaisang, pwsannong-sangji-yutang, kotobank-souen, kotobank-negari
    Entry: research/archetypes.html - 'Dike-ponds: fish ponds ringed by mulberry dikes (sangji yutang)', 'Polder dikes: what they were made of, how big, and what grew on them', 'How thickly was dike mulberry planted, and how wide did a bush grow?'; research/rendering/archetypes.html - 'How our maps draw dike-ponds (sangji yutang)'
    """

    key = 'mulberry dike'


class PondCanal(Kind):
    """
    What: The canals of a dike-pond settlement: the main canal that carries water in from the reservoir and the laterals
    between the rows of ponds, among which the ponds lie.

    Why: A dike-pond is not a sealed basin and its canals are not a paddy's supply net. The polder's own dike was pierced
    by sluices, the dou of the Pearl delta - one carved with its name in 1878 - and the villagers watered and drained
    through the dikes, the creeks and those gates; the ponds lie among the creeks and canals the gates feed. The ring
    drain around the block takes everything to the outfall.

    Note: The polder's gates and the creeks the ponds lie in are read. A sluice through each pond's own dike, and a pond
    taking water in at its high side and out at its low side, are not found before 1912: the first only in a modern manual,
    the second on no page this project read, so neither is drawn. The ring drain around the block is this map's own layout, borrowed from
    the rice polder's inner ring canal: no source the record cites describes a ring drain on a dike-pond.

    Caveat: The ring drain around the block is this map's own layout, borrowed from the rice polder's inner ring canal:
    no source the record cites describes a ring drain on a dike-pond.

    Name: pond canal
    Covers: `field_ditches` whose role is not `drain` on a dike-pond field - the main from the reservoir and the laterals between the ponds
    Label: accurate
    Sources: minle-dou-people, cssn-sangyuanwei, cssn-jiangnan-weitian
    Entry: research/archetypes.html - 'Dike-ponds: fish ponds ringed by mulberry dikes (sangji yutang)'; research/rendering/archetypes.html - 'How our maps draw dike-ponds (sangji yutang)'
    """

    key = 'pond canal'


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
    Entry: research/archetypes.html - 'Were fruit, cane or banana dikes older than the mulberry dike? Fruit was - lychee above all', 'What else was planted on a pond dike besides mulberry?', 'The dike-pond hamlet: what stands there that a rice hamlet lacks'; research/rendering/archetypes.html - 'How our maps furnish a dike-pond hamlet'
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
    What: A simple pig shed on the bank of a fish pond, a railed yard beside it along the bank, on the bank nearest
    the houses.

    Why: A pen on a fish-pond bank is an old form: a farming compendium printed in 1639, written far to the north in
    Shanghai, advises penning a flock of sheep - the form, not the pig - on the bank of a fish pond and sweeping its dung
    into the water each morning to feed the fish, and a modern history of the Pearl River delta's farming names
    pig-raising as the dike-pond district's stock, as duck-raising was the sand fields', and puts the pig inside the Qing
    loop - fed from the pond, its dung and the pond mud manuring the mulberry. So the sty stands on the bank, near its
    pond. A shed built so its waste runs straight into the pond, and the reasoning that the manure raises the plankton,
    are found only in modern manuals, so nothing is drawn to carry the waste into the water. A pig penned on a pond bank
    is a Chinese form. Japan kept pigs - their bones are excavated at the Satsuma domain's Edo residence, at Osaka castle,
    at Hakata and at Nagasaki harbor - but nothing read links a Japanese pig to a pond at all, so the FORM belongs to
    this kind of hamlet and to no other on these maps.

    Note: The sty is read - the pig as the dike-pond village's animal and the pen on the pond bank. Nothing read gives
    how many households kept a sty: the quarter to half of the households drawn with one, rolled per hamlet, is a guess.
    The width a modern manual sets for a shed-carrying dike, five to ten meters, is modern and is not a rule the map
    follows; no older width was found.

    Caveat: Nothing read gives how many households kept a sty: the quarter to half of the households drawn with one,
    rolled per hamlet, is a guess.

    Name: pig sty
    Covers: every `pig_sties[]` record - a shed with its railed pen on a pond bank
    Label: accurate
    Sources: qimin-yaoshu-yangzhu, isis-dykepond, pwsannong-zhusanjiao-nongyeshi, nongzheng-quanshu-41, fao-ac264e
    Entry: research/archetypes.html - "Does a pig sty have to stand back from the water, or from the pond's sluice?", 'Which animals did a dike-pond village keep at its ponds? Pigs - the ducks were herded in the rice fields', 'Does a dike-pond hamlet keep pigs and ducks on its pond dikes?', 'The dike-pond hamlet: what stands there that a rice hamlet lacks'; research/rendering/archetypes.html - 'How our maps furnish a dike-pond hamlet'
    """

    key = 'pig sty'


class FryPond(Kind):
    """
    What: A nursery pond where carp fry are reared, then grown on as fingerlings, before they are stocked
    into the grow-out ponds - drawn only in a fry village, its water a muddier green than a grow-out pond's.

    Why: Fry were a trade of their own in the delta, and one township's. The young carp that stocked the ponds
    were netted wild in the West River by the fry households of Jiujiang in Nanhai, who held the fry-catching
    landings on the river - taken up in the Hongzhi reign (1488-1505) - and supplied the other pond
    districts. Qu Dajun, writing in the late seventeenth century, says fry ponds were found only in Jiujiang,
    where seven parts in ten of the pond water raised fry; elsewhere the ponds mostly raised grown fish, and
    where they tried to raise fry the fry did not thrive. So the record holds two kinds of dike-pond village,
    and each hamlet rolls one: most raise grown fish and buy their fry, with no nursery ponds at all; a few are fry
    villages of the Jiujiang kind, where the smallest ponds, up to seven tenths of the pond water, are nursery ponds. Fry water was turbid and grown-fish water clear, so the color of a pond told what it held, and the map draws it so.

    Note: The fry trade, the township that held it and the two kinds of village are read; how many hamlets are fry
    villages is a guess, and so is taking the smallest ponds as the nursery ponds.

    Caveat: how many hamlets are fry villages is a guess, and so is taking the smallest ponds as the nursery ponds.


    Name: fry pond
    Covers: the dug water of a `dikeponds[]` parcel recorded `kind: fry` - a fry village's smallest ponds
    Label: accurate
    Sources: cssn-sangyuanwei, guangdong-xinyu-22, pwsannong-zhusanjiao-nongyeshi
    Entry: research/archetypes.html - "Did a dike-pond village rear its own fish fry, or buy them? Most bought them - the nursery ponds were one township's trade", 'Were fish fry a trade, and which ponds were the nursery ponds?', 'The dike-pond hamlet: what stands there that a rice hamlet lacks'; research/rendering/archetypes.html - 'How our maps furnish a dike-pond hamlet'
    """

    key = 'fry pond'


class ManurePit(Kind):
    """
    What: An earthenware jar half buried in the ground, in which the household's night soil is kept until it
    goes to the fields - the manure store in its Lake Tai form. Each hamlet has its own mix: some stand behind the house beside its privy,
    others out at the edge of the household's nearest field, or beside a road.

    Why: The most important fertilizer on a rice-and-silk farm was human manure, and Fei's village kept it in
    pits of earthenware half buried behind the buildings, so many that the public road along the stream was
    lined with them. Where the rice hamlet heaps its muck in the yard, the silk villages potted theirs: two
    attested forms, so each hamlet rolls one. Where the pit stood is a second choice. A 1959 survey of three
    Japanese villages found night soil kept in a tank beside the privy or in a pit out by the fields, the
    tank thought to have moved from the privy to the fields or the roadside to make manuring easier, and the
    share of households with a field pit ran from 2 of 83 in one village to 15 of 18 in another. So each
    hamlet rolls its share of field pits somewhere between almost none and most households.

    Note: The form and its place behind the house are read (Fei 1939, with earthen jars sunk by farm paths and roads already in an account of China printed in 1797), and so are the field pit and how widely
    its share varied (the highest, 15 of 18, in a village whose field pits also took night soil carted in from Sendai); carrying the field pit, found in Japan, to the silk village's jar is this project's own
    step, and the drawn 3.5 ft mouth is a size the record does not give.

    Caveat: carrying the field pit, found in Japan, to the silk village's jar is this project's own
    step, and the drawn 3.5 ft mouth is a size the record does not give.

    Name: manure pit
    Covers: a `farm_fixtures[]` record of kind `manure` with `form: pit` - the alternative to the heap
    Label: accurate
    Sources: fei-1939, sugiura-1973-fuzoku, suzuki-1959-noson-benjo
    Entry: research/archetypes.html - 'The dike-pond hamlet: what stands there that a rice hamlet lacks'; research/rendering/archetypes.html - 'How our maps furnish a dike-pond hamlet'; research/homesteads.html - 'Where did the privy stand, and where was its night soil kept?'
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

    Note: The board form is read only from a modern FAO pond-construction manual, which puts its sluice through a single pond's dike rather than the polder's, and its opening in drought and shutting in flood from a Chinese account of the Jiangnan polders; the dou is read as the polder's own sluice - the Minle dou of the Sangyuan polder is an old sluice gate, its name carved above its opening in 1878; the inlet-high, outfall-low placement is read from an account of the Japanese ring-diked polders, which sets the intake at the ring's upstream head and the outlet at its downstream tail; a large polder had many such openings, drains outnumbering intakes, and drawing a village polder with only two is a guess; the 6 x 3 ft bar is drawn at the size of a whole board set, which the record does not measure; the FAO manual caps the opening itself at 0.80 m, less than half the bar.

    Caveat: the 6 x 3 ft bar is drawn at the size of a whole board set, which the record does not measure; the FAO manual caps the opening itself at 0.80 m, less than half the bar.

    Name: sluice gate
    Covers: the board bar of every `sluice_gates[]` record - the gate in each cut of the perimeter dike
    Label: accurate
    Sources: fao-x6708e, cssn-sangyuanwei, shen-kuo, ishizue-waju, wajyu-nogyo
    Entry: research/archetypes.html - 'Dike-ponds: fish ponds ringed by mulberry dikes (sangji yutang)', 'Polders: fields diked against the fluctuating water (weitian, waju)'; research/rendering/archetypes.html - 'How our maps draw polders (weitian, waju)', 'How our maps draw dike-ponds (sangji yutang)'
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
    varying width rather than a ruled line; the dead-straight rectangle is a modern industrial shape, from after China's 1978 reform.

    Note: Full enclosure and the planting are read, though that any gap re-floods the block is this project's reasoning from the general polder; that the outer dike follows the water's edge in curves is a guess, since no page read describes a polder's outer dike; the inlet high and outfall low are read, but a large polder had many openings, drains outnumbering intakes, and drawing a village polder with just two is a calibrated liberty and a guess; the drawn width band (14-40 ft) is a calibrated liberty: no village polder's own dike width was read, and the band's broadest stretches are wider than the 18 ft base of the Echizen river dikes, which a village dike stood below.

    Caveat: the drawn width band (14-40 ft) is a calibrated liberty: no village polder's own dike width was read, and the band's broadest stretches are wider than the 18 ft base of the Echizen river dikes, which a village dike stood below.

    Name: perimeter dike
    Covers: the earthwork band of `dikes[]` - the polder's enclosing dike, gapped at its sluices
    Label: accurate
    Sources: shen-kuo, isis-dykepond, ruddle-zhong-1988, ishizue-waju, wajyu-nogyo
    Entry: research/archetypes.html - 'Polders: fields diked against the fluctuating water (weitian, waju)', 'Polder dikes: what they were made of, how big, and what grew on them'; research/rendering/archetypes.html - 'How our maps draw polders (weitian, waju)', "How our maps draw a polder's dike and its trees"
    """

    key = 'perimeter dike'
