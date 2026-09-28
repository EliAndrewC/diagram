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
    No two farmhouses face exactly the same way. A survey of the houses of 27 Okinawan villages found 87% of them
    facing within three points of the compass about their village's commonest bearing, and about one in ten turned
    to the right of it. So each settlement rolls a common bearing near south, each house stands up to about 30
    degrees off it - most by much less, turning with the lane and the field edge it stands on - and about one
    farmhouse in ten is turned a quarter turn to the right. Its work yard and garden beds turn with it: the GM
    ruled that they always line up with their house.

    Note: Placement follows the read record; that every house in a nucleated cluster is reached by a lane, and the alleys-off-the-spine form, are paraphrased from a morphology literature no public page carries, and the back lane is read only for planned English villages. The setback from the paddy is stated in feet by no source:
    it is built from a bund width that is sourced (one to two shaku), a levee path and an eave overhang that
    are both unsourced GUESSES, and one part that is
    read for a house facing a watercourse and extended to the paddy by this record, so the 6 ft floor beneath
    it is a soft threshold rather than a measured minimum - and the map draws 10 to 13 ft, well clear of it,
    close enough that the household works its own ground. How the turns spread inside the surveyed range, drawing
    the survey's right-turned tenth as one quarter turn when its class runs over several compass points, and rolling
    the common bearing within about 11 degrees of due south are guesses; the survey counts one island region's
    villages, in 1985.

    Caveat: the 6 ft floor beneath it is a soft threshold rather than a measured minimum - and the map draws
    10 to 13 ft, well clear of it, close enough that the household works its own ground. How the turns spread
    inside the surveyed range, drawing the survey's right-turned tenth as one quarter turn when its class runs over
    several compass points, and rolling the common bearing within about 11 degrees of due south are guesses; the
    survey counts one island region's villages, in 1985.

    Name: farmhouse
    Covers: `houses` - the dwelling of each household
    Label: accurate
    Sources: sugiura-1973-fuzoku, sakamoto-tsubaki-1985-omoya-muki
    Entry: research/homesteads.html - 'What stood on a farmstead', 'How close does a farmhouse stand to the paddy', 'Is every farmhouse reached by a lane', 'Why do a village's farmhouses face different ways'
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
    What: The stall of a household's ox or water buffalo - a roof over a shaded stall, drawn against its owner's
    farmhouse or standing as a small shed of its own in the owner's yard.

    Why: The beast lived with the household that kept it. Across much of the country the farmhouse stabled it
    inside, in a corner of the earth-floored work space - the inner stable - and elsewhere in a stable standing on
    its own beside the house, the outer stable. Not every household had a beast: in Bizen from the early eighteenth
    century only about half the farm households kept an ox or a horse, and fewer as time went on, and a household
    without one borrowed or hired a beast, which then lived with whoever had it. So each settlement rolls one of the
    two forms, and a byre stands in the homesteads of somewhat under half its households. The vernacular put the
    animal close to the house, and the record finds no old rule that kept a beast away from the well it drank at.

    Note: The two forms, the beast living with its keeper and the share of households keeping one are read. The
    inner stable is drawn against the farmhouse because a stall under the house's own roof cannot be seen from
    above - a map drawing convention; how much commoner the inner roll is, and the share drawn (35 to 50 of every
    100 households), are calibrated to the record's 'about half, and fewer later'; a third, rare roll - a shed out
    on the ground the homesteads share, reached by several households - is a guess, found on no page read and kept
    only until the record finds it or rules it out; the attached stable wing (magariya) belongs to Tohoku's
    horse-breeding districts, its stable warmed from the kitchen hearth, and is deliberately not drawn - that the
    cold made the form is this record's own reading. The animal's nearness to the house is read; its nearness to
    the wellhead is not on any page read.

    Caveat: The inner stable is drawn against the farmhouse because a stall under the house's own roof cannot be
    seen from above - a map drawing convention; how much commoner the inner roll is, and the share drawn (35 to 50
    of every 100 households), are calibrated to the record's 'about half, and fewer later'; a third, rare roll - a
    shed out on the ground the homesteads share, reached by several households - is a guess, found on no page read
    and kept only until the record finds it or rules it out; the attached stable wing (magariya) belongs to
    Tohoku's horse-breeding districts, its stable warmed from the kitchen hearth, and is deliberately not drawn

    Name: byre
    Covers: `byres` - the draft-animal sheds
    Label: accurate
    Sources: cambridge-animals-china, okayama-chikusanshi-shiyo, agrinews-2023-tajima-maya, ndl-crd-shakkogyu, kotobank-umaya, magariya-jawiki
    Entry: research/homesteads.html - 'Where did a village's draft ox stand', 'May a byre stand beside a wellhead?', 'What stood on a farmstead'
    """

    key = 'byre'


class RetirementHouse(Kind):
    """
    What: A small thatched dwelling standing a few paces off its farmhouse, in the same homestead, with a door of its
    own: the retirement house, where the old couple lived once they had handed the farm to their heir.

    Why: In much of the country the old couple did not stay under the heir's roof. On inkyo, retirement, they moved
    out to a small house of their own, and most such houses stood inside the family's own house plot, with a separate
    entrance - often with separate meals and purse too, one family living as two households. Elsewhere the generations
    stayed together under one roof. Both forms are attested, so each settlement rolls one from its seed, and a
    settlement that keeps the custom draws a retirement house in some of its homesteads. It belongs to its farmhouse's
    household: it is not counted as a household of its own, so the map's household count is the farmhouses.

    Note: The two family forms, and that the retirement house stood inside the family's own house plot with its own
    entrance, are read; how many of a settlement's homesteads keep one, how the two forms are weighted in the roll, the
    house's size (about 18 by 15 feet), its distance from the farmhouse (one or two ken) and its seat off the back wall
    or a flank rather than the front, and which of those three sides, are guesses: no page read gives them, save one survey of a single windswept village that found most on the windward side.

    Caveat: how many of a settlement's homesteads keep one, how the two forms are weighted in the roll, the house's size
    (about 18 by 15 feet), its distance from the farmhouse (one or two ken) and its seat off the back wall or a flank
    rather than the front, and which of those three sides, are guesses: no page read gives them, save one survey of a single windswept village that found most on the windward side.

    Name: retirement house
    Covers: `retirement_houses` - the retired couple's own roof in the homestead
    Label: accurate
    Sources: kotobank-inkyo, kotobank-inkyoya
    Entry: research/settlements.html - 'How many lived in one farmhouse, and under how many roofs?', 'Is every household in a hamlet actually drawn?'
    """

    key = 'retirement house'


class ThreshingYard(Kind):
    """
    What: A tamped-earth work floor in front of each farmhouse, drawn as the harvest leaves it: covered in straw
    mats. The rice was threshed here on mats, and the grain was then dried on mats spread over the whole
    yard - a household measured its yard in them, two to the tsubo: 40 to 60 on an ordinary farm of the barley country
    the count comes from, fewer on a rice farm, whose yard was smaller. Where the
    harvest weather is changeable, each household also gathers its drying rack by the house, along one side of
    the yard.

    Why: Threshing and drying were done per household, in the yard, and the yard needs sun: a thatched roof
    pitched at 45 degrees puts a minka's ridge at 20-22 feet, so no yard is placed in the shadow band south
    of a neighbor's wall, and a rack never stands in the yard's southern half. Its SIZE follows the crop the
    household must dry, which is why every yard on this map is different: each is rolled from a right-skewed
    spread about 18 tsubo (59.5 sq m), correlated with the household. Whether racks stand by the houses
    follows the weather of the country, not a village's taste: racks gathered by the house are recorded for a
    coast of changeable autumn weather, so that the threshing could be done at home, and the drying method
    followed the climate over whole regions - so every settlement in one climate draws the same.

    Note: we have rendered between a third and two thirds of the straw mats that covered a yard (a yard whose
    outline or rack leaves no room for the last ones, a mat or two fewer), each with a little bare
    ground around it, most laid a little askew, as by hand, in order to keep them legible: at this scale dozens of mats laid edge to edge would read as a textured
    floor rather than as mats, so the drawing shows a smaller number to give the impression of many. The real yard at
    harvest was covered, 40 to 60 mats of about 3 by 6 feet each on an ordinary barley-country farm and 100 to 150 on a
    large one. The
    mats' size, the yard's size band and its spread are read; the rows the mats are laid in are a guess - no source read
    says; and where a map draws racks by the houses, which side of the yard a rack takes is a guess too, and the rack is
    drawn wider than its poles so that it reads.

    Name: threshing yard
    Covers: `threshing_yards` - the floor, its mats, and the rack by the house where the harvest weather is changeable
    Label: convention
    Sources: kitamoto-inakoki-niwa, kitamoto-mushiro-niwa, tobunken-mushiro, nishimura-makino-1959
    Entry: research/homesteads.html - 'What lay in the work yard at harvest? Straw mats over the whole floor'; 'Did a village put its drying racks by the houses by custom, or because of its weather?'; 'How big was the work yard, and how did the sizes spread'; 'The threshing yard's sun, and how far a farmhouse shades'
    """

    key = 'threshing yard'


class Garden(Kind):
    """
    What: The household's kitchen garden: a tilled bed in planted rows of daikon and greens, beside the house.

    Why: A dooryard garden fed the household and, like the yard, wants light - beds are kept out of a neighbor's
    shadow to the south, clear of the windbreak's afternoon shade to the west, and, where open ground allows, nudged south out of a neighbor's grove that would take their morning sun from the east.

    Note: Presence is read; the sun rule is DERIVED from the geometry, and its east half is the GM's call, since the record finds no readable source for a bed's need of morning light - its season rests on daikon standing in
    the bed through autumn (the other autumn greens are this record's reading), and its west lane is sized to
    a working belt of about 10 m, the low end of a surveyed band whose measured trees reach 22 m; the record
    fixes the bed's AREA and that it is hand-worked and irregular, but gives no proportion or row count, so
    those are drawn to read as a worked kitchen bed at this scale.

    Caveat: the record fixes the bed's AREA and that it is hand-worked and irregular, but gives no proportion or row
    count, so those are drawn to read as a worked kitchen bed at this scale.

    Name: garden
    Covers: `gardens`
    Label: accurate
    Sources: not recorded
    Entry: research/homesteads.html - 'The garden's sun, and how far the windbreak shades'; 'How much open ground does a kitchen garden keep to its south and east?'; 'The threshing yard's sun, and how far a farmhouse shades' (the garden rule is derived from it)
    """

    key = 'garden'


class Privy(Kind):
    """
    What: The household privy - on a farm, the urinal and the privy were one small building standing apart from
    the main house.

    Why: The common case: the Nipponica entry calls the detached privy the norm, and a 1959 survey of farm
    households in three villages found more than nine in ten with an outdoor privy, so the map draws one on 85 to
    95 of every 100 homesteads - though three prewar Tohoku villages ran from 85% of farms down to none. The record finds it in four places: under the eaves by the stable beside the
    entrance, a separate outhouse in the yard, the front yard of the main house, and - at several farms of one
    Miyagi village - inside the barn, a tub sunk in its floor with boards laid across it. Each house rolls its
    seat among the four, and on most houses a seat on the sunny side is tried first.

    Note: Presence, the detached form and the four seats are read (kotobank, sinyoken, Suzuki 1959, Sugiura). How
    often each seat is drawn is a guess, each hamlet re-weighting them from its seed, and so is where in the yard
    the separate outhouse stands; a privy inside the barn is a tub under its floor, which cannot be seen from
    above, so it is drawn as the privy against the barn's outer wall - a map drawing convention; the 6 x 6 ft
    footprint is a guess - no readable page gives a privy's size.

    Caveat: How often each seat is drawn is a guess, each hamlet re-weighting them from its seed, and so is where
    in the yard the separate outhouse stands; a privy inside the barn is a tub under its floor, which cannot be
    seen from above, so it is drawn as the privy against the barn's outer wall - a map drawing convention; the
    6 x 6 ft footprint is a guess - no readable page gives a privy's size.

    Name: privy
    Covers: `farm_fixtures[kind=privy]`
    Label: accurate
    Sources: kotobank-benjo, sinyoken-madori, sugiura-1973-fuzoku, suzuki-1959-noson-benjo, sugiura-1977-tohoku
    Entry: research/homesteads.html - 'Where did the privy stand, and where was its night soil kept?', 'The farmstead's fixtures'
    """

    key = 'privy'


class Woodpile(Kind):
    """
    What: The household's fuel, split logs and charcoal, kept in one of three forms: a woodshed of its own, a long
    stack along the inside of the windbreak, or an open stack head-high against the house wall.

    Why: Firewood and charcoal were the fuel, and Sugiura counted about three firewood sheds for every four
    farmhouses built before 1944. The record holds three forms: the woodshed, which a reconstructed Boso farmstead keeps and which
    marked the farmsteads of the cold Shonai plain; the kizuma of the Isawa plain in Iwate, the firewood stacked
    along the windbreak on a homestead's windward side, filling the gaps under the grove's lower branches; and the
    open stack against the house. Each hamlet rolls one form. The kizuma is drawn only where a homestead has the
    windbreak at its back, and the open stack where it does not.

    Note: The woodshed and the kizuma are read; the open stack against the back wall or the kura, the one form
    attested nowhere, is a guess, and so are the even odds between the three, how near the windbreak must stand
    to count as the homestead's own (40 ft), the stack's head-high height (modern stacking practice) and the sizes -
    the woodshed 12 x 9 ft, the kizuma 24 ft long, the open stack 10 ft.

    Name: woodpile
    Covers: `farm_fixtures[kind=woodpile]`
    Label: guess
    Sources: boso-no-mura-kigoya, 326woods-stack, sugiura-1973-fuzoku, suido-ishizue-kizuma, sugiura-1977-tohoku, sato-1962-haichi
    Entry: research/homesteads.html - 'Where was the firewood stacked, and how big was the pile?'; 'The farmstead's fixtures'
    """

    key = 'woodpile'


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
    across the survey's span, calibrated liberty. The heap's place beyond the privy, its 8 x 6 ft size and the 40 to
    70 of every 100 homesteads that keep one are guesses - no readable page says where the stable-manure heap stood
    in the yard.

    Name: manure heap
    Covers: `farm_fixtures[kind=manure]`
    Label: guess
    Sources: jawiki-koedame, artic-pigsty-latrine, kyuhi-jawiki, suzuki-1959-noson-benjo
    Entry: research/homesteads.html - 'Where did the manure heap stand, and what went into it?'; 'Where did the privy stand, and where was its night soil kept?'; 'The farmstead's fixtures'
    """

    key = 'manure heap'


class Bathhouse(Kind):
    """
    What: A small bath shed - the iron goemon-buro tub under its own roof - out in the front yard, or against the
    house and joined to it by a short covered corridor.

    Why: The cauldron bath was widely used in self-sufficient farm villages. How many farms had a bath shed
    differed from village to village: reconstructions of three Tohoku villages before the war put it on four farms
    in five in Tono, one in three in Inawashiro and none in Shiokawa, and a survey of three hamlets in one Miyagi
    town found about three in ten. So each hamlet rolls its share between none and four in five, and the rest bathe indoors, unseen. A prewar
    housing report puts the bath in the front yard of the main house in northern Miyagi, and an architectural
    historian describes the Meiji farmhouse bath kept apart from the house, sometimes joined to it by a corridor;
    each hamlet rolls one of the two forms.

    Note: The use, the village-by-village shares and the front-yard seat are read. The village shares are a
    reconstruction its author thinks runs high, and which printed column gives the Miyagi town's three in ten is this
    project's unconfirmed reading; the corridor form rests on one interview, which leaves open whether its
    'farmhouses are like that' takes in the corridor; the odds between the two forms, the corridor's one-ken length,
    the back wall or a flank where neither seat has room, and the 6 x 6 ft size are guesses.

    Caveat: The village shares are a reconstruction its author thinks runs high, and which printed column gives the
    Miyagi town's three in ten is this project's unconfirmed reading; the corridor form rests on one interview, which
    leaves open whether its 'farmhouses are like that' takes in the corridor; the odds between the two forms, the
    corridor's one-ken length, the back wall or a flank where neither seat has room, and the 6 x 6 ft size are
    guesses.

    Name: bathhouse
    Covers: `farm_fixtures[kind=bath]`
    Label: accurate
    Sources: mizumaki-goemonburo, sugiura-1973-fuzoku, sugiura-1977-tohoku, mizu-no-bunka-11-furo
    Entry: research/homesteads.html - 'Did a farmhouse have a bath shed, and where did it stand?'; 'The farmstead's fixtures'
    """

    key = 'bathhouse'


class HenCoop(Kind):
    """
    What: A small square roost for a few chickens, against the house's flank or behind it.

    Why: Chickens were the commonest livestock on a Chinese farm: a survey of 2,866 farms in seven provinces in
    1921-1925 found them on 82 per cent, and the Cambridge history reads farmers in most regions keeping a pig and
    some chickens in their yard. The Qimin Yaoshu says to build the roost as a ground enclosure with a perch,
    because birds left to the trees sicken - so a coop, not a tree - and the one excavated late-Ming coop is square.
    Each hamlet rolls its share around the survey's 82%, between about seven and nine farmsteads in ten.

    Note: Presence, the ground form and the square plan are read (Buck, Cambridge, the Qimin Yaoshu, the Zhengzhou
    coop). The survey's 1920s count stands in for the late empire, as the Cambridge chapter's figures do, and the
    band's width about it is calibrated liberty; the 5 x 5 ft size and the seat at the house's flank or back wall are
    guesses - the record says only 'in their yard'.

    Caveat: The survey's 1920s count stands in for the late empire, as the Cambridge chapter's figures do, and the
    band's width about it is calibrated liberty; the 5 x 5 ft size and the seat at the house's flank or back wall are
    guesses - the record says only 'in their yard'.

    Name: hen coop
    Covers: `farm_fixtures[kind=coop]`
    Label: accurate
    Sources: cambridge-animals-china, qimin-yaoshu-yangji, pitt-zhengzhou-coop, buck-1930-farm-economy
    Entry: research/homesteads.html - 'Did a farmstead keep chickens, and in what kind of coop?'; 'The farmstead's fixtures'
    """

    key = 'hen coop'


class HouseholdShrine(Kind):
    """
    What: A household's own small shrine - a stone or wooden hokora in a corner of the plot, drawn vermilion with
    a torii before its door.

    Why: In some regions every house had one, in others only certain old families; the GM ruled for the
    old-families pattern here - rare, and notable when it appears - so the count is capped at three to eight
    households in a hundred. It stands in the plot's northwest, northeast or southwest corner, all three
    attested.

    Note: we have drawn the household shrine at 6 x 6 ft - the small-shed module - in vermilion with a torii
    before it, in order to make it visible on the map at this scale. The one measured stone hokora is about
    40 cm (1.3 ft) on a side, a stone or wooden shrine that at true size would be a single pixel. Presence,
    rarity and the three corners are read; how often each corner is drawn is a guess, from a survey count we could not read.

    Name: household shrine
    Covers: `farm_fixtures[kind=shrine]` - the hokora
    Label: convention
    Sources: tokushima-yashikigami, jawiki-yashikigami, kameyama-yashikigami, sugiura-1973-fuzoku
    Entry: research/homesteads.html - 'Which farmsteads had a household shrine, and in which corner?'; 'The farmstead's fixtures'
    """

    key = 'household shrine'


class Persimmon(Kind):
    """
    What: The household's persimmon tree, in the dooryard in front of the house or behind it, drawn a yellower green
    than the groves with four fruit dots - the map's convention for naming the tree, not a season.

    Why: A persimmon stood in every dooryard: the Edo agronomist Miyazaki Yasusada is said to have urged planting
    them around the homestead, and the tree shades the house in summer. The farm villages of the past had an old
    giant persimmon in the dooryard of every house, and one is remembered in the bamboo grove behind a house, so the
    tree stands in front of the house, most often, or behind it, each hamlet rolling how often each. Its crown is
    about 23 ft across, a full-grown tree's.

    Note: Presence and the two sides are read (toyoko, a newspaper history of the Fuyu persimmon, Sato on fruit trees
    in the front yard). The crown is a modern horticultural reference's full-grown size, which fits the old giants
    better than an ordinary tree; how much likelier the front is, the seat at the edge of the work yard, and the
    share drawn - 80 to 95 of every 100 homesteads, against the sources' every dooryard - are guesses.

    Caveat: The crown is a modern horticultural reference's full-grown size, which fits the old giants better than an
    ordinary tree; how much likelier the front is, the seat at the edge of the work yard, and the share drawn - 80 to
    95 of every 100 homesteads, against the sources' every dooryard - are guesses.

    Name: persimmon
    Covers: `persimmons` - the dooryard persimmon tree
    Label: accurate
    Sources: toyoko-kaki, uekipedia-kaki, jataff-fuyu-kaki, sato-1962-haichi, pfaf-kaki
    Entry: research/homesteads.html - 'Why does a persimmon stand beside so many farmhouses?'; 'The farmstead's fixtures'
    """

    key = 'persimmon'


class BurialGround(Kind):
    """
    What: A small common burial ground at the hamlet's edge - an irregular patch of earth set with low stone
    markers and a taller memorial stone or two.

    Why: The district's cremation ground is the main village's, and its country monk performs the rites. Where
    the bones then lie, the history gives two answers: by the hamlet's own houses - a hamlet's burial ground at
    its edge, the ground its inhabitants hold in common, the two-grave custom's burial grave on common land - or at
    the parish temple, which in this setting is the village's shrine. So some hamlets keep a ground of their own,
    holding the urns brought home from the village's cremation ground, and some bury in the village's. That ground
    lies in the village shrine's own yard or, in other villages, as a ground of its own downstream of the houses and
    beyond the last of them, never upstream, within about 650 ft of the middle of the houses; it is sized to
    everyone it serves, at 7.5 to 18 sq ft for each inhabitant.

    Note: Both answers are read, and so are the village ground's two forms and its downstream side. Which form a
    village's ground takes, the shrine's yard or a ground of its own, is rolled at even odds, and those odds are a
    guess; the village ground's 650 ft is the surveyed distance of the graves a two-grave village visited, carried
    over to an urn ground, and its size is this project's own reckoning from a death rate and a reuse period no page
    gives; which answer a hamlet takes is rolled at even odds, and those odds are a guess; the size is the band the
    record reckons for a hamlet's full-body ground, 750 to 2,450 sq ft, which overstates an urn ground, so it is a
    guess; so is its outline, and its keeping 60 ft from houses and wells.

    Caveat: Which form a village's ground takes, the shrine's yard or a ground of its own, is rolled at even odds, and
    those odds are a guess; the village ground's 650 ft is the surveyed distance of the graves a two-grave village
    visited, carried over to an urn ground, and its size is this project's own reckoning from a death rate and a reuse
    period no page gives; which answer a hamlet takes is rolled at even odds, and those odds are a guess; the size is the band the
    record reckons for a hamlet's full-body ground, 750 to 2,450 sq ft, which overstates an urn ground, so it is a
    guess; so is its outline, and its keeping 60 ft from houses and wells.

    Name: burial ground
    Covers: `cemeteries` - the hamlet's own burial ground
    Label: accurate
    Sources: kofukuroman-sanmai, bochi-jawiki, kotobank-ryobosei, haka-jawiki, danka-jawiki, oikawa-2008-kikaijima, nakajima-2006-huizhou, kawazoe-2010-ryobosei, takeuchi-2017-bochi-hosei, meiji-1884-bochi-saimoku
    Entry: research/religion-and-death.html - 'Where do a hamlet's dead lie?'; 'How much ground does a village burial ground need, and whose dead lie in it?'; 'How far from its houses does a village bury its dead, and on which side?'; 'Does a village bury in its temple's yard, in a ground of its own, or in its fields?'
    """

    key = 'burial ground'
