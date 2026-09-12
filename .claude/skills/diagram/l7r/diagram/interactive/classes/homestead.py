"""The farmstead and what stands on it - the dwelling, its outbuildings, its yards and fixtures.

Each class's DOCSTRING is its explanation - `What:`, `Why:`, `Note:`, optional `Caveat:` - parsed by
`_base.parse_explanation` (feature 189). Edit the prose here and the page changes; the gate does not re-open.
"""

from __future__ import annotations

from ._base import Kind


class Farmhouse(Kind):
    """
    What: The dwelling of one farming household: a thatched minka, its ridge on the long axis, standing on the
    slightly raised ground the homesteads share, its work yard and garden beside it and, where a farm stands
    alone, its own yashikirin sheltering it.

    Why: A house in a nucleated hamlet is reached by a lane and stands close to the paddy - up against it, but
    never on the bund. HOW that access is delivered is not settled: alleys cut off the spine, each household
    having made its own way to the road, and a laid-out back lane serving a regular row are both attested, so
    this map rolls between the two forms per settlement and guarantees only that every farmhouse is served.

    Note: Placement and form follow the read record. The setback from the paddy is stated in feet by no source:
    it is built from a bund width that is a GUESS, an eave overhang that is unsourced and one part that is
    read, so the 6 ft floor beneath it is a soft threshold rather than a measured minimum - and the map draws
    10 to 13 ft, well clear of it, close enough that the household works its own ground.

    Caveat: the setback from the paddy is built from three parts, and two of them - the bund's width and the
    eave overhang - rest on no page, so the 6 ft floor beneath it is a soft threshold rather than a measured
    minimum.

    Name: farmhouse
    Covers: `houses` - the dwelling of each household
    Label: accurate
    Sources: sugiura-1973-fuzoku
    Entry: research/homesteads.html - 'What stood on a farmstead', 'How close does a farmhouse stand to the paddy', 'Is every farmhouse reached by a lane'
    """

    key = 'farmhouse'


class StorageShed(Kind):
    """
    What: A roofed outbuilding for storage - grain, straw, tools, fuel. Some stand as a lean-to against the
    farmhouse, some free in the yard; storage either way.

    Why: A July 1972 survey of 87 households in three Miyagi hamlets counted 4.4 outbuildings per household -
    firewood shed, straw shed, barn, work shed, storehouse - so a farmstead with only its house would be the
    anomaly. The count drawn here is a band below that snow-country figure, because the temperate lowland
    hamlet this map draws kept fewer.

    Note: Presence and the mean count per household read (Sugiura 1973 - an upper bound on the share of households keeping one); the drawn count per household is deliberately set below the
    source's Tohoku figure, which is a colder and better-stocked district than this one.

    Caveat: the drawn count per household is deliberately set below the source's Tohoku figure, which is a colder
    and better-stocked district than this one.

    Name: storage shed
    Covers: `houses[].shed` (the lean-to against a farmhouse) and `farm_sheds` (the detached sheds of the same household)
    Label: accurate
    Sources: sugiura-1973-fuzoku
    Entry: research/homesteads.html - 'What stood on a farmstead - the inventory, with numbers'
    """

    key = 'storage shed'


class Byre(Kind):
    """
    What: An open-fronted shed for a household's ox or water buffalo - a roof carried on posts over a shaded
    stall, standing either inside its owner's yard or out on the ground the homesteads share.

    Why: Most farmsteads kept a draft animal or two, and the vernacular put the animal far closer to the house
    than a European barn would. Where the team is OWNED, the household houses it in its own homestead; where a
    team is shared or hired it stands out among the homesteads, on the common ground, so that the borrowing
    household can walk to it. Both are attested and neither dominates, so this map rolls between them per
    settlement - which is also what lets two hamlets differ honestly.

    Note: The separate byre is the temperate reading of the record; the attached stable wing (magariya) is a
    cold-country form and is deliberately not drawn. The animal's nearness to the HOUSE is read; its nearness
    to the wellhead is not on any page read, and neither is the commons siting itself.

    Caveat: the attached stable wing (magariya) is a cold-country form and is deliberately not drawn, and the
    byre's nearness to the wellhead is on no page read.

    Name: byre
    Covers: `byres` - the draft-animal sheds
    Label: accurate
    Sources: cambridge-animals-china
    Entry: research/homesteads.html - 'May a byre stand beside a wellhead?', 'What stood on a farmstead'
    """

    key = 'byre'


class ThreshingYard(Kind):
    """
    What: A small tamped-earth work floor beside each farmhouse - swept bare, with a straw drying mat and a little
    rack for hanging sheaves. Households measured it in straw mats: 40 to 60 of them, two mats to the tsubo,
    so an ordinary yard is 20 to 30 tsubo and a few run past 50.

    Why: Threshing and drying were done per household, in the yard, and the yard needs sun: a thatched roof
    pitched at 45 degrees puts a minka's ridge at 20-22 feet, so no yard is placed in the shadow band south
    of a neighbor's wall. Its SIZE follows the crop the household must dry, which is why every yard on this
    map is different: each is rolled from a right-skewed spread about 18 tsubo (59.5 sq m), correlated with
    the household - a large farm overwhelmingly has a large yard, and the occasional mismatch is a fact
    about that farmstead.

    Note: The size band and the spread's shape are read - Kitamoto's mat counts, and the lognormal that fits
    Kamikanai's 1771 house histogram; the wet-rice CENTER is interpolated from the crop (rice is field-dried
    on racks first, so a paddy household needs less floor than the barley district the mat counts come
    from), and the sun corridor is derived from the read roof pitch.

    Caveat: the wet-rice CENTER is interpolated from the crop (rice is field-dried on racks first, so a paddy
    household needs less floor than the barley district the mat counts come from), and the sun corridor is
    derived from the read roof pitch.

    Name: threshing yard
    Covers: `threshing_yards`
    Label: accurate
    Sources: not recorded
    Entry: research/homesteads.html - 'How big was the work yard, and how did the sizes spread'; 'The threshing yard's sun, and how far a farmhouse shades'
    """

    key = 'threshing yard'


class Garden(Kind):
    """
    What: The household's kitchen garden: a tilled bed in planted rows of greens, beside the house.

    Why: A dooryard garden fed the household and, like the yard, wants light - beds are kept out of a neighbor's
    shadow to the south and clear of the windbreak's afternoon shade to the west.

    Note: Presence and the sun rule are read; the record fixes the bed's AREA and that it is hand-worked and
    irregular, but gives no proportion or row count, so those are drawn to read as a worked kitchen bed at
    this scale.

    Caveat: the record fixes the bed's AREA and that it is hand-worked and irregular, but gives no proportion or row
    count, so those are drawn to read as a worked kitchen bed at this scale.

    Name: garden
    Covers: `gardens`
    Label: accurate
    Sources: not recorded
    Entry: research/homesteads.html - 'The garden's sun, and how far the windbreak shades'; 'The threshing yard's sun, and how far a farmhouse shades' (the garden rule is derived from it)
    """

    key = 'garden'


class Privy(Kind):
    """
    What: The household privy - on a farm, the urinal and the privy were one small building standing apart from
    the main house.

    Why: Near-universal: the Nipponica entry calls the detached privy the norm, and the 1972 survey counted one
    on 87 of 100 households. Its seat is rolled from three attested positions - by the back door, at the
    gate, or by the shed.

    Note: Presence and the three seats are read (kotobank, sinyoken); the 6 x 6 ft footprint is a GUESS - the one
    sizing page is dead.

    Caveat: the 6 x 6 ft footprint is a GUESS - the one sizing page is dead.

    Name: privy
    Covers: `farm_fixtures[kind=privy]`
    Label: accurate
    Sources: kotobank-benjo, sinyoken-madori, sugiura-1973-fuzoku
    Entry: research/homesteads.html - 'The farmstead's fixtures'
    """

    key = 'privy'


class Woodpile(Kind):
    """
    What: The household's fuel: split logs stacked head-high against a wall, out of the rain.

    Why: Firewood and charcoal were the fuel, and a shed for them stood on three farms in four; the open stack
    under the eaves is the cheaper and older form, and the one drawn.

    Note: The firewood SHED is read (Boso-no-Mura); where the open STACK stood relative to the house was found
    nowhere - the back wall or the shed's outer wall is a guess, and the stack's height is modern practice.

    Name: woodpile
    Covers: `farm_fixtures[kind=woodpile]`
    Label: guess
    Sources: boso-no-mura-kigoya, 326woods-stack, sugiura-1973-fuzoku
    Entry: research/homesteads.html - 'The farmstead's fixtures'
    """

    key = 'woodpile'


class ManureHeap(Kind):
    """
    What: The muck heap: night soil and byre litter composting before they go onto the fields.

    Why: Night soil was fermented in buried jars or plastered pits and spread as fertilizer; the heap is drawn
    beyond the privy because the two were one cluster - in Han China the latrine stood over the pigsty and
    drained to the cesspool.

    Note: The practice is read (jawiki, the Art Institute's Han model); the heap's PLACE on the farm and its size
    are guesses - the pages describe the pit, not where it stood.

    Name: manure heap
    Covers: `farm_fixtures[kind=manure]`
    Label: guess
    Sources: jawiki-koedame, artic-pigsty-latrine
    Entry: research/homesteads.html - 'The farmstead's fixtures'
    """

    key = 'manure heap'


class Bathhouse(Kind):
    """
    What: A small bath shed - the iron goemon-buro tub under its own roof.

    Why: The cauldron bath was widely used in self-sufficient farm villages; the 1972 survey found a bath shed on
    about three farms in ten and a bath inside the house on half, so only the shed share is drawn and the
    rest bathe indoors, unseen.

    Note: Use is read (Mizumaki museum); where the shed stood was found nowhere - the back wall or a flank is a
    guess, and so is the 6 x 6 ft size.

    Name: bathhouse
    Covers: `farm_fixtures[kind=bath]`
    Label: guess
    Sources: mizumaki-goemonburo, sugiura-1973-fuzoku
    Entry: research/homesteads.html - 'The farmstead's fixtures'
    """

    key = 'bathhouse'


class HenCoop(Kind):
    """
    What: A small square roost for a few chickens, on the flank of the yard.

    Why: Farmers kept a pig and some chickens in the yard along with a draft animal; the Qimin Yaoshu says to
    build the roost as a ground enclosure with a perch, because birds left to the trees sicken.

    Note: The coop's existence and ground form are read (Cambridge, the Qimin Yaoshu, the Zhengzhou coop); the
    household proportion, the 5 x 5 ft size and the seat are guesses bounded by 'most regions'.

    Name: hen coop
    Covers: `farm_fixtures[kind=coop]`
    Label: guess
    Sources: cambridge-animals-china, qimin-yaoshu-yangji, pitt-zhengzhou-coop
    Entry: research/homesteads.html - 'The farmstead's fixtures'
    """

    key = 'hen coop'


class HouseholdShrine(Kind):
    """
    What: A household's own small shrine - a stone or wooden hokora in a corner of the plot, drawn vermilion with
    a torii before its door.

    Why: In some regions every house had one, in others only certain old families; the GM ruled for the
    old-families pattern here - rare, and notable when it appears - so the count is capped at about three
    households in a hundred. It stands in the plot's northwest, northeast or southwest corner, all three
    attested.

    Note: we have drawn the household shrine at 6 x 6 ft - the small-shed module - in vermilion with a torii
    before it, in order to make it visible on the map at this scale. The one measured stone hokora is about
    40 cm (1.3 ft) on a side, a stone or wooden shrine that at true size would be a single pixel. Presence,
    rarity and corner are read.

    Name: household shrine
    Covers: `farm_fixtures[kind=shrine]` - the hokora
    Label: convention
    Sources: tokushima-yashikigami, jawiki-yashikigami, kameyama-yashikigami, sugiura-1973-fuzoku
    Entry: research/homesteads.html - 'The farmstead's fixtures'
    """

    key = 'household shrine'


class Persimmon(Kind):
    """
    What: The household's persimmon tree beside the house, drawn a yellower green than the groves with four fruit
    dots - the map's convention for naming the tree, not a season.

    Why: A persimmon stood in every dooryard: the Edo agronomist Miyazaki Yasusada urged planting them around the
    homestead, and the tree shades the house in summer, so it stands beside it.

    Note: Presence and the beside-the-house placement are read (toyoko, uekipedia); WHICH side and the 18 ft crown
    are guesses - the crown width was found nowhere.

    Name: persimmon
    Covers: `persimmons` - the dooryard persimmon tree
    Label: guess
    Sources: toyoko-kaki, uekipedia-kaki
    Entry: research/homesteads.html - 'The farmstead's fixtures'
    """

    key = 'persimmon'
