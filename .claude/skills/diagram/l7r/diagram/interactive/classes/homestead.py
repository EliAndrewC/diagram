"""The farmstead and what stands on it - the dwelling, its outbuildings, its yards and fixtures.

Each class's DOCSTRING is its explanation - `What:`, `Why:`, `Note:`, optional `Caveat:` - parsed by
`_base.parse_explanation` (feature 189). Edit the prose here and the page changes; the gate does not re-open.
"""

from __future__ import annotations

from ._base import Kind


# The GM's ruling: a farmhouse's work yard and garden beds always line up with their house.
class Farmhouse(Kind):
    """
    What: The dwelling of one farming household: a thatched minka, its ridge on the long axis, standing on the
    slightly raised ground the homesteads share, its work yard and garden beside it and, where a farm stands
    alone, its own yashikirin sheltering it.

    Why: A house in a nucleated hamlet is reached by a lane and stands close to the paddy - up against it, but
    never on the bund. HOW that access is delivered is not settled: alleys cut off the spine, each household
    having made its own way to the road as this map reads it, and a laid-out back lane serving a regular row are
    both seen in villages read, so
    this map rolls between the two forms per settlement and guarantees only that every farmhouse is served.
    No two farmhouses face exactly the same way. A survey of the houses of 27 Okinawan villages found most of them
    facing within three points of the compass about their village's commonest bearing, the smaller turns where the
    streets curve - and curving streets, which its surveyors suppose follow the contours, are seen on the land-survey maps of a village moved to its site in 1736, though which of them were laid before 1868 the paper does not say. So
    each settlement rolls a common bearing near south, and each house turns a little with the lane and the field edge it
    stands on, never more than about 30 degrees; no house is turned a quarter away. Its work yard and garden beds turn
    with it: this project draws them always lined up with their house. About one farm in eight carries a storehouse
    against its back wall, a village headman's always.

    Note: Placement follows the read record; that every house in a nucleated cluster is reached by a lane holds in the villages read, though no page states it as a rule; the alleys-off-the-spine form is read only in one surveyed twentieth-century Manchu village on the dry northern plain, the back lane only for planned English villages, and that alleys mean a village grew while a back lane means it was planned is this record's reading, not a source's. The setback from the paddy is stated in feet by no source:
    it is built from a bund width that is sourced (one to two shaku), a levee path and an eave overhang that
    are both unsourced GUESSES, and one part that is
    read for a house facing a watercourse and extended to the paddy by this record, so the 6 ft floor beneath
    it is a soft threshold rather than a measured minimum - and the map draws 10 to 13 ft, well clear of it,
    close enough that the household works its own ground. No count of house bearings from before 1868 was found: the
    survey is one island region's houses in 1985, and the one tenth it found turned to the right is not drawn. How far a
    house turns with its lane, and rolling the common bearing within about 11 degrees of due south, are guesses, as is that the 1736 village's houses turned with its streets. The plain farmhouse is drawn 46 by 28 ft, the size of the well-off houses that survive and about twice the usual house of one village's count of 1885.

    Caveat: the 6 ft floor beneath it is a soft threshold rather than a measured minimum - and the map draws
    10 to 13 ft, well clear of it, close enough that the household works its own ground. No count of house bearings from
    before 1868 was found: the survey is one island region's houses in 1985, and the one tenth it found turned to the
    right is not drawn. How far a house turns with its lane, and rolling the common bearing within about 11 degrees of
    due south, are guesses, as is that the 1736 village's houses turned with its streets.

    Name: farmhouse
    Covers: `houses` - the dwelling of each household
    Label: accurate
    Sources: sakamoto-tsubaki-1985-omoya-muki, yamamoto-2014-koshijo-shuraku, oamishirasato-choshi-kaoku
    Entry: research/homesteads.html - 'Farmhouses (minka)', 'The farmstead and what stood on it (yashiki)'; research/ways.html - 'Village lanes'; research/rendering/homesteads.html - 'How our maps draw farmhouses (minka)', 'How our maps draw the farmstead and what stands on it (yashiki)'
    """

    key = 'farmhouse'


class StorageShed(Kind):
    """
    What: A storehouse (kura): a farm's fireproof store, walled in thick earth under a tile roof, which a farm built
    once money had accumulated - drawn as an annex against the farmhouse wall on the largest farms.

    Why: Before modern times a farmstead carried far fewer outbuildings than the twentieth century's counts: a village
    count of 1885, which its historian reads back to the last years of the shogunate, gives about one and a half
    besides the privy and the retirement house, and a storehouse on only two farms in sixteen, both in households the
    historian places among the village's powerful ones, the second with a "probably". So on the hamlets our generator
    lays out a storehouse stands against about one farmhouse in eight, the largest of them, and a village headman's
    house always has one; the hand-drawn maps keep the higher share they were drawn with. It is drawn in the size band
    of the two farm sheds measured from the end of the Edo period or just after, 18 to 27 ft long and 1.5 to 1.8 times
    as long as deep, though the storehouses recorded were smaller, about 12 to 15 by 18 ft.

    Note: we have drawn the storehouse as a tiled annex against the farmhouse's west or north wall, 18 to 27 ft long,
    the size of a farm shed, in order to leave the sunny walls to the garden and every generated hamlet's houses where
    they stand. The storehouses recorded stood free of the house, in front of it or behind, and were smaller, about 12
    to 15 by 18 ft. Giving the storehouses strictly to the largest houses is this project's rule, stricter than the
    record (Kakimochi's largest house had none), and which of two farmhouses of one size gets it is a guess; the count
    is one village's, so the share is a calibration; that every
    storehouse is tiled is this project's reading of two examples. The Hannan shed's 18 ft is our arithmetic from its
    3 by 2 ken, and its registered area suggests it may have been somewhat larger. The larger barns built after 1868,
    and the 4.4 outbuildings a household of a 1972 survey, are not drawn.

    Name: storage shed
    Covers: `houses[].shed` (the storehouse against a farmhouse) and `farm_sheds` (its record)
    Label: convention
    Sources: oamishirasato-choshi-kaoku, koshigaya-shishi-noumin-jukyo, bunka-minami-naya, nerima-mitome-naya
    Entry: research/homesteads.html - 'The farmstead and what stood on it (yashiki)', 'Farm storehouses (kura)', 'Farm sheds and barns (naya)'; research/rendering/homesteads.html - 'How our maps draw the farmstead and what stands on it (yashiki)', 'How our maps draw farm storehouses (kura)'
    """

    key = 'storage shed'


class Byre(Kind):
    """
    What: The stall of a household's ox, water buffalo or horse - a roof over a shaded stall, drawn against its
    keeper's farmhouse or standing as a small shed of its own in the keeper's yard.

    Why: The beast lived with the household that kept it. Across much of the country the farmhouse stabled it
    inside, in a corner of the earth-floored work space - the inner stable - and elsewhere in a stable standing on
    its own, the outer stable. Not every household had a beast: in Bizen from the early eighteenth
    century only about half the farm households kept an ox or a horse, and fewer as time went on, and a household
    without one borrowed or hired a beast, which then lived with whoever had it. So each settlement rolls one of the
    two forms (or, rarely, a shed shared on common ground), and a byre stands in the homesteads of somewhat under
    half its households. The vernacular put the
    animal close to the house, and the record finds no old rule that kept a beast away from the well it drank at.

    Note: The two forms, the beast living with its keeper and the share of households keeping one are read. The
    inner stable is drawn against the farmhouse because a stall under the house's own roof cannot be seen from
    above - a map drawing convention; how much commoner the inner roll is, and the share drawn (35 to 50 of every
    100 households), are a calibration, not a count: the share follows one province's 'about half, and fewer later',
    though one village of Saitama district had a stable at 50 of its 76 houses in 1824; a third, rare roll - a shed out
    on the ground the homesteads share, reached by several households - is a guess, found on no page read and kept
    only until the record finds it or rules it out; the attached stable wing (magariya) belongs to Tohoku's
    horse-breeding districts, its stable warmed from the kitchen hearth, and is deliberately not drawn - that the
    warmth shows what the horses were worth is this record's own reading, and the form was common among the
    upper farm households, such as a headman's. The animal's nearness to the
    house is read; its nearness to
    the wellhead is not on any page read, and that it drank at the household's well is a guess, as is the outer
    stable's distance off the farmhouse wall, 6 to 12 ft.

    Caveat: The inner stable is drawn against the farmhouse because a stall under the house's own roof cannot be
    seen from above - a map drawing convention; how much commoner the inner roll is, and the share drawn (35 to 50
    of every 100 households), are a calibration, not a count: the share follows one province's 'about half, and
    fewer later', though one village of Saitama district had a stable at 50 of its 76 houses in 1824; a third, rare roll - a
    shed out on the ground the homesteads share, reached by several households - is a guess, found on no page read
    and kept only until the record finds it or rules it out; the attached stable wing (magariya) belongs to
    Tohoku's horse-breeding districts, its stable warmed from the kitchen hearth, and is deliberately not drawn

    Name: byre
    Covers: `byres` - the draft-animal sheds
    Label: accurate
    Sources: cambridge-animals-china, okayama-chikusanshi-shiyo, agrinews-2023-tajima-maya, ndl-crd-shakkogyu, kotobank-umaya, magariya-jawiki, koshigaya-shishi-noumin-jukyo
    Entry: research/homesteads.html - 'Draft oxen and horses and their byres (umaya)', 'The farmstead and what stood on it (yashiki)'; research/rendering/homesteads.html - 'How our maps draw and place byres (umaya)', 'How our maps draw the farmstead and what stands on it (yashiki)'
    """

    key = 'byre'


class RetirementHouse(Kind):
    """
    What: A small thatched dwelling standing a few paces off its farmhouse, in the same homestead, with a door of its
    own: the retirement house, where the old couple lived once they had handed the farm to their heir.

    Why: In much of the country the old couple did not stay under the heir's roof. On inkyo, retirement, they moved
    out to a small house of their own, and most such houses stood inside the family's own house plot, with a separate
    entrance - often with separate meals and purse too, one family living as two households. The custom was strongest
    from the Pacific coast through the Inland Sea, above all in Kyushu and Shikoku; in the northeast and along the Sea
    of Japan coast the generations stayed together under one roof. Both forms are attested, so each settlement rolls one from its seed, and a
    settlement that keeps the custom draws a retirement house in some of its homesteads. It belongs to its farmhouse's
    household: it is not counted as a household of its own, so the map's household count is the farmhouses.

    Note: The two family forms, and that the retirement house stood inside the family's own house plot with its own
    entrance, are read, and so is that where the custom was kept thoroughly every house had one; the share of
    homesteads that keep one across a region, how the two forms are weighted in the roll, the house's size (about 18 by
    15 feet), its distance from the farmhouse (one or two ken) and its seat off the back wall or a flank rather than the
    front, and which of those three sides, are guesses: no page read gives them.

    Caveat: the share of homesteads that keep one across a region, how the two forms are weighted in the roll, the
    house's size (about 18 by 15 feet), its distance from the farmhouse (one or two ken) and its seat off the back wall
    or a flank rather than the front, and which of those three sides, are guesses: no page read gives them.

    Name: retirement house
    Covers: `retirement_houses` - the retired couple's own roof in the homestead
    Label: accurate
    Sources: kotobank-inkyo, kotobank-inkyoya
    Entry: research/settlements.html - 'Households: how many live in a house, and under how many roofs (ie)'; research/rendering/settlements.html - 'How our maps count and draw households (ie)'
    """

    key = 'retirement house'


class ThreshingYard(Kind):
    """
    What: A tamped-earth work floor in front of each farmhouse, drawn as the harvest leaves it: covered in straw
    mats. The rice was threshed here on mats, and the grain was then dried on mats spread over the whole
    yard - a household measured its yard in them, two to the tsubo: about 50 on an ordinary farm. Where the
    harvest weather is changeable, each household also gathers its drying rack by the house, along one side of
    the yard.

    Why: Threshing and drying were done per household, in the yard (though some south-China villages shared one drying floor), and the yard needs sun: a thatched roof
    pitched at 45 degrees would put a minka's ridge at about 20-22 feet (a reconstruction: no page gives the pitch or
    the height), so no yard is placed in the 39 ft band of shadow south of a neighbor's wall over a drying day taken,
    as a guess, to run from nine to three, and no windbreak tree stands within 50 ft to its west and southwest, and a rack never stands in the yard's southern half. Unless a map allots every household the same yard, as the planned colony at Santome did in 1696, every yard on it is different:
    each is rolled from a right-skewed spread about 25 tsubo, correlated with the household - the barley country's
    count and, in a rice district, a museum's count of about fifty mats a farm for drying the grain. Whether racks stand
    by the houses follows the weather of the region, not a village's taste: racks gathered by the house are recorded for
    a coast of changeable autumn weather, so that the threshing could be done at home, and the drying method followed the
    climate over whole regions - so every settlement in one climate draws the same; a settlement whose harvest weather
    is not stated is drawn as settled, with no rack at the house, which is this project's decision.

    Note: we have rendered between a third and two thirds of the straw mats that covered a yard (a yard whose
    outline or rack leaves no room for the last ones, a mat or two fewer), each with a little bare
    ground around it, most laid a little askew, as by hand, in order to keep them legible: at this scale dozens of mats laid edge to edge would read as a textured
    floor rather than as mats, so the drawing shows a smaller number to give the impression of many. The real yard at
    harvest was covered, 40 to 60 mats of about 3 by 6 feet each on an ordinary barley-country farm and 100 to 150 on a
    large one. The
    mats' size is read, and the yard's lopsided spread is read from registers of houses and homestead lots, since no survey counts yards; the yard's size rests on two undated records of remembered practice, a calibration and this project's choice; the rows the mats are laid in are a guess - no source read
    says; and where a map draws racks by the houses, which side of the yard a rack takes and how far along it the rack runs are guesses too, and the rack is
    drawn wider than its poles so that it reads.

    Name: threshing yard
    Covers: `threshing_yards` - the floor, its mats, and the rack by the house where the harvest weather is changeable
    Label: convention
    Sources: kitamoto-inakoki-niwa, kitamoto-mushiro-niwa, tobunken-mushiro, nishimura-makino-1959
    Entry: research/homesteads.html - 'Threshing and drying yards at farmhouses (niwa)'; 'Rice-drying racks (hasa, hasagi)'; research/rendering/homesteads.html - 'How our maps draw threshing and drying yards (niwa)', 'How our maps keep yards and gardens in the sun', 'How our maps draw rice-drying racks (hasa, hasagi)'
    """

    key = 'threshing yard'


class Garden(Kind):
    """
    What: The household's kitchen garden: a tilled bed in planted rows of daikon and greens, beside the house.

    Why: A dooryard garden fed the household and, like the yard, wants light - beds are kept out of a neighbor's
    shadow to the south, clear of the windbreak's afternoon shade to the west, and, where open ground allows, nudged south out of a neighbor's grove that would take their morning sun from the east.

    Note: The bed's size and its crops are guesses: no page read gives a kitchen bed's area or lists what it grew, so
    its area is held to a guessed range of 10 to 140 sq m (about 108 to 1,507 sq ft) and its crops - daikon, onions,
    beans and herbs - are this project's reading. That a farm household kept a bed of its own for its table is read.
    The sun rule is worked out from the autumn sun's geometry: its season rests on daikon standing in the bed through
    autumn, its west lane is sized to a windbreak drawn at a working height of 10 m (about 33 ft), a guess at the
    height of a stand kept in use, and moving a bed out of a neighbor's grove's morning shade is this project's choice.
    The record gives the bed no proportion or row count, so those are drawn to read as a worked kitchen bed at this
    scale.

    Name: garden
    Covers: `gardens`
    Label: guess
    Sources: not recorded
    Entry: research/homesteads.html - 'Sunlight and shade on the farm', 'Kitchen gardens beside farmhouses (yashikibatake)'; research/rendering/homesteads.html - 'How our maps keep yards and gardens in the sun', 'How our maps size kitchen gardens (yashikibatake)'
    """

    key = 'garden'


class Privy(Kind):
    """
    What: The household privy - on a farm, the urinal and the privy were one small building standing apart from
    the main house.

    Why: The common case, before modern times as after: most houses of one village in 1824 had a privy outside the
    main house, and every one of another village's sixteen households did; a 1959 survey of farm households in three
    villages found more than nine in ten with an outdoor privy. So the map draws one on 85 to 95 of every 100
    homesteads. The record finds it in four places: under the eaves by the stable beside the entrance, a separate
    outhouse in the yard, the front yard of the main house, and - at several farms of one Miyagi village - inside the
    barn, a tub sunk in its floor with boards laid across it. Each house rolls its seat among the four, and on most
    houses a seat on the sunny side is tried first. Its size is one of the sixteen the village count gives, from 5 by 5
    ft to 27 by 15 ft, most 18 by 12 ft or smaller.

    Note: Presence, the detached form, the four seats and the sizes are read (Hasuda 1824, the Kakimochi count, Suzuki
    1959, Sugiura), and so is the sunny side (Wang and Ochiai found 72.7% of one Shiga village's privies south or
    southeast of the house). How often each seat is drawn is a guess, each hamlet re-weighting them from its seed, and so
    is where in the yard the separate outhouse stands; a privy inside the barn is a tub under its floor, which cannot be
    seen from above, so it is drawn as the privy against the barn's outer wall - a map drawing convention; the size is
    one village's table, a calibration; the sunny side is searched only to 48 ft, this project's choice, so only about
    46 privies in 100 end up there against the 72.7% each house rolls.

    Caveat: How often each seat is drawn is a guess, each hamlet re-weighting them from its seed, and so
    is where in the yard the separate outhouse stands; a privy inside the barn is a tub under its floor, which cannot be
    seen from above, so it is drawn as the privy against the barn's outer wall - a map drawing convention; the size is
    one village's table, a calibration; the sunny side is searched only to 48 ft, this project's choice, so only about
    46 privies in 100 end up there against the 72.7% each house rolls.

    Name: privy
    Covers: `farm_fixtures[kind=privy]`
    Label: accurate
    Sources: koshigaya-shishi-noumin-jukyo, oamishirasato-choshi-kaoku, suzuki-1959-noson-benjo, sugiura-1977-tohoku, sinyoken-madori, wang-ochiai-2022
    Entry: research/homesteads.html - 'Farm privies and their night soil (benjo)'; 'The farmstead and what stood on it (yashiki)'; research/rendering/homesteads.html - 'How our maps place privies (benjo)'; 'How our maps draw the farmstead and what stands on it (yashiki)'
    """

    key = 'privy'


class WoodShed(Kind):
    """
    What: The household's firewood, kept in a wood shed of its own: a roofed shed a step off the house, its open front
    showing the log ends.

    Why: Firewood was the fuel, and before modern times it was kept in a shed: in one village's house-by-house record
    of 1824 many houses had a firewood shed or a storage shed standing apart from the main house, and in another
    village's count, which its historian reads back to the last years of the shogunate, six households of sixteen had
    one, seven sheds in all, three of them 4 by 2 ken. So a wood shed stands on about four farmsteads in ten, the larger houses first, 24 by 12 ft. An open stack
    under the eaves is found only on a present-day page, and the stack along the windbreak only in descriptions
    of today and of farms of the past with no date, so neither is drawn.

    Note: The shed, its share and its size are read (Hasuda 1824, the Kakimochi count), and giving it to the larger
    houses first is this project's reading of the same history's finding that the houses with the most outbuildings
    had the largest main houses; the share is one village's, a calibration, and where on the plot the shed stands - a
    step off the back wall or a flank - is a guess.

    Caveat: the share is one village's, a calibration, and where on the plot the shed stands - a step off the back wall
    or a flank - is a guess.


    Name: wood shed
    Covers: `farm_fixtures[kind=woodpile]` - the wood shed
    Label: accurate
    Sources: boso-no-mura-kigoya, koshigaya-shishi-noumin-jukyo, oamishirasato-choshi-kaoku
    Entry: research/homesteads.html - 'Firewood stacks and sheds (kigoya)'; 'The farmstead and what stood on it (yashiki)'; research/rendering/homesteads.html - 'How our maps draw firewood sheds (kigoya)'; 'How our maps draw the farmstead and what stands on it (yashiki)'
    """

    key = 'wood shed'


class ManureHeap(Kind):
    """
    What: The household's muck: night soil and byre litter composting before they go onto the fields - an open heap
    on some maps, a night-soil pit on others.

    Why: Night soil was fermented in buried jars or plastered pits and spread as fertilizer, and the stable's litter,
    straw and leaves trodden with the dung, rotted into stable manure. A 1959 survey found the night-soil pit in two
    places: in a tank beside the privy, or in a field pit out by the household's fields or the road - in 2 households
    of 83 in one village and 15 of 18 in another. So where a hamlet keeps pits, it rolls its own share at the fields,
    and the rest stand beside their privies. A heap is drawn beyond the privy, because in Han China the latrine stood
    over the pigsty and drained to the cesspool, and the two were one cluster.

    Note: The practice and the pit's two places are read (jawiki, Suzuki 1959); the share at the fields is rolled
    across the survey's span, calibrated liberty, and how far out a field pit may stand, within 160 ft of the house,
    is a guess. The heap's place beyond the privy, its 8 x 6 ft size and the 40 to
    70 of every 100 homesteads that keep one are guesses - no readable page says where the stable-manure heap stood
    in the yard.

    Name: manure heap
    Covers: `farm_fixtures[kind=manure]`
    Label: guess
    Sources: jawiki-koedame, artic-pigsty-latrine, kyuhi-jawiki, suzuki-1959-noson-benjo
    Entry: research/homesteads.html - 'Manure heaps and compost (kyuhi)'; 'Farm privies and their night soil (benjo)'; 'The farmstead and what stood on it (yashiki)'; research/rendering/homesteads.html - 'How our maps place manure heaps (kyuhi)'; 'How our maps place privies (benjo)'; 'How our maps draw the farmstead and what stands on it (yashiki)'
    """

    key = 'manure heap'


class BathRoom(Kind):
    """
    What: A small bath room joined to the farmhouse - the tub under the house's own roof line, at its main door or
    at the far end of its stable wing.

    Why: Before 1868 the bath was part of the house, not a shed: house-plan registers of villages on the shogun's road
    to Nikko show a bath of one or two tsubo in two or three houses in ten by 1824 and 1842, beside the main door or
    beyond the stable wing, and in a few - most of them headmen's - joined to the floored rooms. A bath standing as a
    building of its own is found only from the Meiji period on. So a bath room is drawn on two or three farms in ten,
    6 ft out from the wall and 6 to 12 ft along it; each hamlet rolls the main door or the stable wing's end, and a
    headman's bath is joined to his floored rooms.

    Note: The share, the size, the three places and the headmen's floored-room baths are read (Tsuda's reading of the
    Nikko registers); the odds between the places are a guess, and so is that every headman's bath stood at the
    floored rooms; the tub drawn in it is the map's mark for what the room is.

    Caveat: the odds between the places are a guess, and so is that every headman's bath stood at the floored rooms;
    the tub drawn in it is the map's mark for what the room is.

    Name: bath room
    Covers: `farm_fixtures[kind=bath]` - the bath room joined to the house
    Label: accurate
    Sources: tsuda-1991-nikko-shasan-minka, mizumaki-goemonburo
    Entry: research/homesteads.html - 'Baths on the farm (furo)'; 'The farmstead and what stood on it (yashiki)'; research/rendering/homesteads.html - 'How our maps draw farm baths (furo)'; 'How our maps draw the farmstead and what stands on it (yashiki)'
    """

    key = 'bath room'


class HenCoop(Kind):
    """
    What: A small square roost for a few chickens, against the house's flank or behind it.

    Why: Chickens were the commonest livestock on a Chinese farm: a survey of 2,866 farms in seven provinces in
    1921-1925 found them on 82 per cent, and the Cambridge history reads farmers in most regions keeping a pig and
    some chickens in their yard. The Qimin Yaoshu says to build the roost as a ground enclosure with a perch,
    because birds left to the trees sicken - so a coop, not a tree - and an excavated late-Ming coop is square.
    Each hamlet rolls its share around the survey's 82%, between about seven and nine farmsteads in ten.

    Note: Presence, the ground form and the square plan are read (Buck, Cambridge, the Qimin Yaoshu, the Zhengzhou
    coop). The survey's count was made in the 1920s, and what was seen before 1912 agrees with it; the band's width
    about it is calibrated liberty; that every farm with chickens kept a coop is a guess - no account before 1912
    says where the yard's chickens slept; the 5 x 5 ft size and the seat at the house's flank or back wall are
    guesses - the record says only 'in their yard'.

    Caveat: The survey's count was made in the 1920s, and what was seen before 1912 agrees with it; the band's width
    about it is calibrated liberty; that every farm with chickens kept a coop is a guess - no account before 1912
    says where the yard's chickens slept; the 5 x 5 ft size and the seat at the house's flank or back wall are
    guesses - the record says only 'in their yard'.

    Name: hen coop
    Covers: `farm_fixtures[kind=coop]`
    Label: accurate
    Sources: cambridge-animals-china, qimin-yaoshu-yangji, pitt-zhengzhou-coop, buck-1930-farm-economy
    Entry: research/homesteads.html - 'Chickens and chicken coops'; 'The farmstead and what stood on it (yashiki)'; research/rendering/homesteads.html - 'How our maps draw chicken coops', 'How our maps draw the farmstead and what stands on it (yashiki)'
    """

    key = 'hen coop'


# The GM's ruling: the old-families pattern for household shrines (rare, notable when it appears; three to
# eight households in a hundred), over the every-house pattern of other regions.
class HouseholdShrine(Kind):
    """
    What: A household's own small shrine - a stone or wooden hokora in a corner of the plot, drawn vermilion with
    a torii before its door.

    Why: In some regions every house had one, in others only certain old families; this project draws the
    old-families pattern here - rare, and notable when it appears - so the count is capped at three to eight
    households in a hundred. It stands in the plot's northwest, northeast or southwest corner, all three
    attested.

    Note: we have drawn the household shrine at 6 x 6 ft - the small-shed module - in vermilion with a torii
    before it, in order to make it visible on the map at this scale. The one measured stone hokora is about
    40 cm (1.3 ft) on a side, a stone or wooden shrine that at true size would be a single pixel. Presence,
    rarity and the three corners are read; how often each corner is drawn is a guess, ordered after the Japanese Wikipedia article's commonest corners, since no count we could read gives it.

    Name: household shrine
    Covers: `farm_fixtures[kind=shrine]` - the hokora
    Label: convention
    Sources: tokushima-yashikigami, jawiki-yashikigami, kameyama-yashikigami, sugiura-1973-fuzoku
    Entry: research/homesteads.html - 'Household shrines (yashikigami)'; 'The farmstead and what stood on it (yashiki)'; research/rendering/homesteads.html - 'How our maps place household shrines (yashikigami)'; 'How our maps draw the farmstead and what stands on it (yashiki)'
    """

    key = 'household shrine'


class Persimmon(Kind):
    """
    What: The household's persimmon tree, in the dooryard in front of the house or behind it, drawn a yellower green
    than the groves with four fruit dots - the map's convention for naming the tree, not a season.

    Why: Accounts of the old farm villages give a persimmon to every dooryard: the Edo agronomist Miyazaki Yasusada is said to have urged planting
    them around the homestead, and the tree shades the house in summer. The farm villages of the past had an old
    giant persimmon in the dooryard of every house, and one is remembered in the bamboo grove behind a house, so the
    tree stands in front of the house, most often, or behind it, each hamlet rolling how often each. Its crown is
    drawn about 23 ft across.

    Note: Presence and the two sides are read, though the one account from before 1868 is at second hand and the rest are undated or later (toyoko, a newspaper history of the Fuyu persimmon, Sato on fruit trees
    in the front yard). The crown is a modern horticultural reference's full-grown size, a guess: no record from before
    1868 gives an ordinary dooryard persimmon's crown. How much likelier the front is, the seat at the edge of the work
    yard, and the share drawn - 80 to 95 of every 100 homesteads, against the sources' every dooryard - are guesses.

    Caveat: The crown is a modern horticultural reference's full-grown size, a guess: no record from before 1868 gives an
    ordinary dooryard persimmon's crown. How much likelier the front is, the seat at the edge of the work yard, and the
    share drawn - 80 to 95 of every 100 homesteads, against the sources' every dooryard - are guesses.

    Name: persimmon
    Covers: `persimmons` - the dooryard persimmon tree
    Label: accurate
    Sources: toyoko-kaki, uekipedia-kaki, jataff-fuyu-kaki, sato-1962-haichi, pfaf-kaki
    Entry: research/homesteads.html - 'Fruit trees in the farmyard: persimmon, chestnut and plum (kaki)'; 'The farmstead and what stood on it (yashiki)'; research/rendering/homesteads.html - 'How our maps draw farmyard fruit trees (kaki)'; 'How our maps draw the farmstead and what stands on it (yashiki)'
    """

    key = 'persimmon'


class BurialGround(Kind):
    """
    What: A village's burial ground - an irregular patch of earth set with low stone markers and a taller memorial stone
    or two, with six small stone jizo in a row at its entrance. A hamlet draws none: its dead lie in the village's
    ground.

    Why: The district's cremation ground is the main village's, and its country monk performs the rites. A graveyard
    held by a settlement itself is found at the end of the Edo period, but as one form among an individual's, a
    lineage's and a temple's, and the dead went more often to temple graves; that every hamlet kept a ground of its own
    rests only on twentieth-century records, so a hamlet draws none and its dead lie with the village's. That ground
    lies in the village shrine's own yard or, in other villages, as a ground of its own just beyond the last of the
    houses, downstream of them; no set distance from them is drawn, none being found from before modern times. It is
    sized to everyone it serves, at 7.5 to 18 sq ft for each inhabitant, with a death rate of about 25 to 30 in a
    thousand a year, inside what Edo village registers give.

    Note: The village's ground and its two forms are read, but the attested yard is a temple's: putting it in the
    shrine's yard is a deliberate deviation, since this setting's country monk keeps the shrine and performs the rites.
    Which form a village's ground takes, the shrine's yard or a ground of its own, is rolled at even odds, and those
    odds are a guess, as is the rule that a village whose shrine stands on a hill always takes a ground apart; its size
    is this project's reckoning from the Edo death rates, a reuse period no page gives and an urn plot's footing no page
    gives either; that its dead lie downstream of the houses, where the map draws a ground apart, is attested in today's
    villages only.

    Caveat: Which form a village's ground takes, the shrine's yard or a ground of its own, is rolled at even odds, and
    those odds are a guess, as is the rule that a village whose shrine stands on a hill always takes a ground apart; its
    size is this project's reckoning from the Edo death rates, a reuse period no page gives and an urn plot's footing no
    page gives either; that its dead lie downstream of the houses, where the map draws a ground apart, is attested in
    today's villages only.

    Name: burial ground
    Covers: `cemeteries` - a village's burial ground
    Label: accurate
    Sources: kofukuroman-sanmai, bochi-jawiki, kotobank-ryobosei, haka-jawiki, danka-jawiki, takeuchi-2017-bochi-hosei, kaf2-kinsei-bo, tsuya-kurosu-tokugawa-mortality
    Entry: research/religion-and-death.html - 'Where a village buries its dead: its own ground, the temple yard, the fields or the home plot'; 'Village burial grounds (bochi)'; research/rendering/religion-and-death.html - 'How our maps choose where a village's and a hamlet's dead lie'; 'How our maps draw village burial grounds'
    """

    key = 'burial ground'
