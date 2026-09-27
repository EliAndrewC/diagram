"""The household kinds of a compound plan: the lord's house and everything that keeps it (feature 262).

The magistrate's household lives inside the working compound, behind the office - the residence, the
dwellings of the karo, the retainers and the servants, the guest quarters, and the kitchen, bath, wells,
privies, stables, fire-water and shrine that serve them. Each class is written from the research section
its `Entry:` names, or says the record has no entry; where a `buildings/types.json` program item classified
the kind or its size band, that class and its reason are carried into the `Note:` (and, for a size the item
called a guess or a convention, into the `Caveat:`), not re-decided. What is true of one map only (Ochiba's
two-altar Inari hall, Hayakawa's enlarged bath, Ubame's shuttered wing) lives in that map's `.notes.md`
"Map notes" block, not here. The measurement behind every label is
`specs/262-interactive-magistracy-pages/coverage.md`.
"""

from __future__ import annotations

from ..classes import Kind


class Residence(Kind):
    """
    What: The magistrate's own house: the lord's family, their rooms and a formal reception room, drawn either as
    one block under one roof or as two or three halls stepped back one behind the next and joined by corridors. Its
    rooms, the veranda along its garden face, any corridor between its halls and the formal entrance porch (genkan)
    are each their own feature, and light with the house. The band label names the whole wing.

    Why: The household living inside the working compound is the point of the institution - the office is a
    household, and the gate between the two courts is the hinge between state and home. The ordinary house kept
    its rooms in one block under one roof; halls joined by corridors were the great house's form, and halls set in
    echelon, as at Katsura, are what a house becomes when it is added to hall by hall over half a century. Arrival
    was staged: through the gate, across open ground a palanquin could cross, to the entrance step, never straight
    from the street into a room. In the record's ideal the prized garden lies on the sunny south side facing the
    reception rooms, and a plan seats it there where its buildings allow; by that same sun rule the shady rear
    carries the service strip.

    Note: The household inside the working compound (its place behind the office is Chinese regulation; the
    Japanese pages read do not give that order, and at Takayama the residence stood beside the office, not behind
    it), the garden south of the reception rooms and the staged arrival are recorded findings, and the program
    classes the wing as accurate, its label naming a zone. Its size is the record's where a sheet follows it: a
    samurai's main house ran about 49 tsubo (about 1,740 sq ft) for a 150-koku district magistrate
    and about 67 tsubo (about 2,380 sq ft), as restored to its Meiji plan, for a retainer of 500 to 1,000 koku; the hand sheets' wings, about 180 to
    200 ft long, are larger than either, a guess. Both massings are attested and each sheet takes one: one block is the ordinary posting's form, and a
    residence drawn in echelon reads as one its holders have added to. That a corridor joins each hall to the last
    is this project's reading; no source read says how Katsura's echelon halls are joined. The service strip on
    the shady rear is reasoned from the sun rule, with no source read for it, and that the residence out-measures
    every other domestic building is this project's own reading of the compound; no page a reader can open ranks
    the footprints. A garden standing where the court would be, between the gate and the entrance, is a guess.
    Each labeled room is a suite of several rooms compressed to one label, a schematic convenience.

    Caveat: That a corridor joins each hall to the last is this project's reading; no source read says how
    Katsura's echelon halls are joined. The service strip on the shady rear is reasoned from the sun rule, with no
    source read for it, and that the residence out-measures every other domestic building is this project's own
    reading of the compound; no page a reader can open ranks the footprints. A garden standing where the court
    would be, between the gate and the entrance, is a guess. Each labeled room is a suite of several rooms
    compressed to one label, a schematic convenience.

    Name: residence
    Covers: the lord's residence blocks' fill and outlines, their room dividers, and the RESIDENCE band label
    Label: accurate
    Sources: watariroka-kotobank, irikawa-kotobank, katsura-rikyu-jawiki, touken-world-buke-madori, kotobank-shikidai, kominkai-genkan, fuchu-joge-pamphlet, neixiang-yamen-zhwiki, takayama-jinya-city, takayama-jinya-jawiki, machi-bugyo-jawiki, jinya-jawiki, yamen-enwiki, neixiang-xianya-zhwiki, kotobank-katteguchi, shoinzukuri-jawiki
    Entry: research/buildings.html - 'Were a residence's wings joined by corridors and set in echelon, like geese in flight?', 'How did a guest of rank arrive, from the gate to the entrance?', 'Office in front, residence behind', 'Guest doors feed courts, not flanks', 'The shady rear is the service strip', 'The compound has a size HIERARCHY', 'How big was a samurai's house, and what rank is a 67-tsubo house?'
    """

    key = "residence"


class AncestralAlcove(Kind):
    """
    What: The butsuma alcove at the residence's formal end, beside or behind the reception room, holding the
    memorial tablets (ihai) of the house's dead - at a lineage-held posting, the magistrates of that house who
    held the post before. A place within the house, not a hall of its own.

    Why: A house kept its Buddha images and the tablets of its dead in the butsuma, set either beside the alcove
    of the zashiki or in a small room behind the zashiki or the inner room - in both, at the formal end of the
    house; no source read puts it among the family's private rooms. One of the two kinds of Japanese tablet veneration keeps, in principle, the tablets of a house's successive heads
    along its line of inheritance, so - this project's guess from that - the alcove follows the house, not the post: where one lineage holds the
    magistracy across generations, the past magistrates are the present one's own forebears and the alcove is
    literally ancestral, and at a posting filled by appointment it holds only the family's own tablets.

    Note: The butsuma at the formal end, by or behind the zashiki, is a recorded finding; the two places for it
    are both attested, and each sheet takes one. A house keeping the tablets of its own successive heads is
    recorded, and that some magistrate's posts are held by a provincial lineage is the setting's ruling. Nothing
    read says tablets of predecessors in office were kept at an office or its residence, in Japan or at a Chinese
    county seat; the state hall for meritorious local officials that the record quotes stood at the Confucian
    temple, not inside the office. So past holders stand in the alcove only if they were heads of the incumbent's
    own house, and whether they were is a question of the setting.

    Caveat: Nothing read says tablets of predecessors in office were kept at an office or its residence, in Japan
    or at a Chinese county seat; the state hall for meritorious local officials that the record quotes stood at
    the Confucian temple, not inside the office. So past holders stand in the alcove only if they were heads of
    the incumbent's own house, and whether they were is a question of the setting.

    Name: ancestral alcove
    Covers: the alcove's tablets label at the residence's formal end (a lineage alcove where the tablets are a lineage's)
    Label: accurate
    Sources: butsuma-kotobank, sosen-saishi-kotobank, mingguanci-zhwiki
    Entry: research/buildings.html - 'Where does the butsuma sit - by the zashiki, or among the private rooms?', 'Whose tablets does the alcove hold when a post passes to a cousin, not a son?', 'An ancestral alcove holding office-predecessor tablets'
    """

    key = "ancestral alcove"


class KarosHouse(Kind):
    """
    What: The house of the karo, the house elder - the magistrate's chief retainer - standing as a small house of
    its own inside the compound.

    Why: In the setting a county magistrate's samurai include the magistrate's karo. At a shogunal intendancy,
    the kind of office these postings follow, the staff lived inside the compound, in small houses and
    long-houses; a mansion of the karo's own near the lord's residence or in the castle was the form at a
    daimyo's scale, and belongs to a castle town. So the karo lives inside the walls, at the intendancy's scale.

    Note: The karo is the setting's own, and staff housed inside an intendancy's compound in small houses or
    long-houses is recorded. That the karo's quarters are a small house of their own, rather than a bay of the
    staff long-house, is a guess: no source sets the head of the staff apart from the rest, and a chief
    retainer's house inside the lord's own compound was not found. Its size and seat are a guess too.

    Name: karo's house
    Covers: the karo's house and its label with the "house elder" gloss
    Label: guess
    Sources: l7r-budgets, bukeyashiki-wiki, aizu-saigo-karo, jinya-kotobank, daikan-tetsuki-jawiki, mapple-takayama-jinya
    Entry: research/buildings.html - 'Where does the chief retainer live - inside the compound, or in a house of their own?'
    """

    key = "karo's house"


class RetainersQuarters(Kind):
    """
    What: Housing inside the walls for the magistrate's retainers - samurai of the working platoon, and on some
    postings their families - drawn as a long single-story range of rooms under one roof, a rowhouse.

    Why: A rural administrative compound housed its staff on the grounds; it was the great city magistrate's
    offices that sent their constables to live in a district of their own. Where lower-ranking samurai and foot
    soldiers lived as households, they lived in terraced ranges - one surviving ashigaru rowhouse holds eight
    households under one thatched roof, 143 by 24 ft - so a range, not a cluster of small houses, is the form.

    Note: Retainers' official residences laid out inside a small domain's jin'ya are recorded, and the city
    magistracy's separate constables' district and ranked households in terraced ranges rest on recorded
    findings. That a rural office's own staff lived on its grounds is the record's reconstruction, no source
    naming those staff or their housing, and that their housing took the form of a rowhouse is the record's
    own reading rather than a source's words; the record places ranks of small household dwellings at the
    town's edge, outside an elite quarter, rather than inside its walls.

    Caveat: That a rural office's own staff lived on its grounds is the record's reconstruction, no source
    naming those staff or their housing, and that their housing took the form of a rowhouse is the record's
    own reading rather than a source's words; the record places ranks of small household dwellings at the
    town's edge, outside an elite quarter, rather than inside its walls.

    Name: retainers' quarters
    Covers: the senior retainers' quarters, a family rowhouse for married retainers, and their labels
    Label: accurate
    Sources: hatchobori-jawiki, jinya-jawiki, takayama-jinya-jawiki, shibata-ashigaru-nagaya, hikone-ashigaru
    Entry: research/buildings.html - 'Staff housing spans a real spectrum'; research/cities/government.html - 'Servant housing in the samurai ward'
    """

    key = "retainers' quarters"


class ServantsQuarters(Kind):
    """
    What: A long, narrow single-story range - a nagaya - where the household's domestic servants live: the
    cooks, grooms and cleaners who keep the compound running, on annual contracts.

    Why: A samurai household's servants lived inside their master's walls, never in houses of their own - in a
    range along the boundary, in the rooms of the gate, or for a small household in rooms off the kitchen.
    The shady north rear, behind the residence, is the compound's service strip, so the servants' range
    backs the rear wall there, beside the vegetable plot and the family privy.

    Note: Servants housed inside the walls, in a range along the boundary, is a recorded finding. The program
    classes the building's size as a guess: a nagaya for about ten servants, with no measured example behind
    the band, and its seat in the north rear is reasoned from the sun rather than read.

    Caveat: The program classes the building's size as a guess: a nagaya for about ten servants, with no
    measured example behind the band, and its seat in the north rear is reasoned from the sun rather than
    read.

    Name: servants' quarters
    Covers: the servants' nagaya and its label
    Label: accurate
    Sources: jta-nagayamon, fukui-bushi-jutaku, aizu-bukeyashiki-jawiki, kotobank-degawari, nagayamon-jawiki, nando-jawiki, daozuofang, shoinzukuri-jawiki
    Entry: research/cities/government.html - 'Servant housing in the samurai ward'; research/buildings.html - 'The shady rear is the service strip'
    """

    key = "servants' quarters"


class GuestQuarters(Kind):
    """
    What: Where the household lodges a guest of rank: the guest room, the zashiki and the rooms beside it, inside
    the residence - or, where a plan draws one, a detached guest house.

    Why: The guest rooms of a samurai house were part of the house: the Takayama residence had a room for
    receiving guests among its rooms, and a middle-rank house kept its guest space - the formal entrance, the
    room where a visitor was announced, and the zashiki - within its one main house. A travelling lord or
    official lodged at a honjin, a post town's lodging house with its raised room of honor, not with the
    household. A guest of rank arrives across open ground to the entrance step, so a guest's door opens onto a
    court, never against a building's flank.

    Note: Guest rooms inside the residence and the staged arrival that leads to them are recorded findings. A
    guest house drawn as a building of its own is a guess: none was found at a samurai house, and the nearest
    attested form is the honjin's suite of honor, which belongs to a post town's lodging house, not to an office.
    A guest garden standing where the court would be is a guess too.

    Caveat: A guest house drawn as a building of its own is a guess: none was found at a samurai house, and the
    nearest attested form is the honjin's suite of honor, which belongs to a post town's lodging house, not to an
    office. A guest garden standing where the court would be is a guess too.

    Name: guest quarters
    Covers: the guest room of the residence with its floor and label, or a detached guest house and its label
    Label: accurate
    Sources: shirobito-1717-takayama, boso-no-mura-takei, honjin-jawiki, yakage-honjin, kotobank-shikidai, kominkai-genkan
    Entry: research/buildings.html - 'Did a guest stay in the house, or in a guest house of their own?', 'How did a guest of rank arrive, from the gate to the entrance?', 'Guest doors feed courts, not flanks'
    """

    key = "guest quarters"


class Kitchen(Kind):
    """
    What: The household's kitchen - a daidokoro, board-floored, with a small earth-floored doma at its edge - that
    feeds the family, the staff and the watch; its hearth, its door, and a well inside or beside it are each their
    own feature.

    Why: A samurai house's rooms were nearly all matted, but its kitchen was board-floored, and its doma was
    smaller than a farmhouse's. The kitchen had one door to the outside, the katteguchi, the service entrance;
    the family came and went by a separate inner entrance and guests by the formal one. So the kitchen stands at
    the edge of the inner court, its door opening into work space, the deliberate opposite of a guest's arrival.
    It is large, but a fraction of the living quarters, and with open fire burning all day it is the compound's
    worst fire risk, so it keeps two water tubs where every other hall keeps one.

    Note: The board-floored kitchen with its small doma, its one outside door, and the household's separate
    inner entrance are recorded findings. A second outside door on the kitchen, and the route by which food
    reached the rooms, are guesses wherever a plan draws them: nothing read draws either. The kitchen's own size
    is a guess, since no page read gives a kitchen's share of its house; it is measured against a whole house of
    about 49 tsubo (some 1,740 sq ft) at middle rank, or about 67 tsubo (some 2,380 sq ft) for a retainer of 500
    to 1,000 koku, and a kitchen that approaches either is too big. Its weighting as the compound's worst fire
    risk, with a second water tub, is this project's reading: no page read gives the kitchen extra water or sets
    one tub to a hall as a rule.

    Caveat: A second outside door on the kitchen, and the route by which food reached the rooms, are guesses
    wherever a plan draws them: nothing read draws either. The kitchen's own size is a guess, since no page read
    gives a kitchen's share of its house; it is measured against a whole house of about 49 tsubo (some 1,740 sq
    ft) at middle rank, or about 67 tsubo (some 2,380 sq ft) for a retainer of 500 to 1,000 koku, and a kitchen
    that approaches either is too big. Its weighting as the compound's worst fire risk, with a second water tub,
    is this project's reading: no page read gives the kitchen extra water or sets one tub to a hall as a rule.

    Name: kitchen
    Covers: the kitchen and pantries building and its label
    Label: accurate
    Sources: boso-no-mura-takei, liq-takayasu-daidokoro, kotobank-katteguchi, kotobank-uchigenkan, matsue-bukeyashiki, matsue-bukeyashiki-about, matsushiro-bukeyashiki, tfd-hongou-fire-history, thepaper-taipinggang, edo-no-kaji-jawiki, machibikeshi-jawiki
    Entry: research/buildings.html - 'What fire did a residence's kitchen cook on - a kamado range, or a sunken hearth?', 'How many doors does a residence's kitchen have, and who comes in by them?', 'How big was a samurai's house, and what rank is a 67-tsubo house?', 'The compound has a size HIERARCHY', 'Fire-water is distributed to the halls', 'Guest doors feed courts, not flanks'
    """

    key = "kitchen"


class Bath(Kind):
    """
    What: The residence's bath, the yudono: a small room added on to the house on its service side, by the kitchen
    and its well, drawn with a curl of steam rising above it.

    Why: A bath of one's own was a mark of rank. In the Edo period a bath room was built in the few shoin-style
    residences of upper-rank samurai, while middle and lower samurai washed from a tub or went to the public
    bath; around 1600 a warrior family's bath was a one-person tub in a corner of the doma, the earth-floored part
    of the house. At a posting the bath went with the residence: the Takayama residence had its earth floor and
    kitchen, a well and a bath, and a middle-rank house's bath was meant to be added on.

    Note: The bath as a room of the residence or a small addition to it is a recorded finding; a bath standing as
    a building of its own was not found, and a house of middle rank or below may have none. Placing it on the
    service side, with the doma, the kitchen and the well, is this project's reading of the Takayama list and of
    the bath in a corner of the doma, and its size is a guess: nothing read gives the size of a residence's bath.

    Caveat: Placing it on the service side, with the doma, the kitchen and the well, is this project's reading of
    the Takayama list and of the bath in a corner of the doma, and its size is a guess: nothing read gives the
    size of a residence's bath.

    Name: bath
    Covers: the bath, its steam mark and its label
    Label: accurate
    Sources: furo-kotobank, yokushitsu-kotobank, shirobito-1717-takayama, kanagawa-hatamoto-kaso, sayama-jinya-uematsu
    Entry: research/buildings.html - 'Did a residence have its own bath, and was it a building apart?'
    """

    key = "bath"


class Well(Kind):
    """
    What: A private well inside the compound's walls - a shaft with a stone curb - drawn as a square curb with a
    dark mouth: one at or in the kitchen, one in the garden, one beside the stables, sometimes a fourth.

    Why: Samurai and government households drew their water from wells inside their own walled compounds,
    not from the communal wells where commoners gathered. The kitchen well is the busiest; the stables well
    waters the horses; the garden well serves the family. The kitchen well sits in the service ground rather
    than in a court meant for ceremony.

    Note: we have drawn each well as a stone-curb marker about 7 ft square, larger than the curb itself, in
    order to mark where the well stands without claiming that its pixels are the well's size. A hand-dug
    well's shaft is about 1 m across; a measured width for the curb frame was not found, and the 3 to 4 ft
    curb is an estimate. That official households drew from wells inside their own walls is the record's
    reading.

    Name: well
    Covers: every well curb glyph and its label
    Label: convention
    Sources: kanda-josui-jawiki, nagaya-jawiki, saijo-mizu-rekishikan, kotobank-idoyakata, ido-jawiki, shoinzukuri-jawiki
    Entry: research/urban-features.html - 'Communal wells and the samurai exception', 'Wells - the research, and the deliberate liberty'; research/buildings.html - 'The shady rear is the service strip'
    """

    key = "well"


class Latrine(Kind):
    """
    What: A privy - a kawaya - over a pit: in the residence, the guests' privy at the rear of the reception room
    along a board veranda and the family's apart from it toward the living rooms; others serve the garrison, the
    stable yard and the gate, about one to each part of the compound.

    Why: In a samurai house the privy was built into the house, not set out in the yard, and a well-appointed
    house kept more than one. Where a townhouse or farmhouse had a guest parlor, a privy stood at its rear, and an official hall
    with a formal entrance and a zashiki had upper privies with board verandas. Night soil was a valuable,
    contracted commodity carted away by outside collectors, so the pits sit toward a service wall or gate where a
    collector's cart reaches them.

    Note: The privy built into the samurai house, the more than one privy of a well-appointed house, the privy at
    the rear of the guest parlor, the upper privies with board verandas at an official hall, and the carted
    night-soil trade are recorded findings, and the program classes the privies as accurate - one per functional
    zone, about three or four. The guests' privy at the rear of the zashiki, reached along a board veranda, is
    this project's reading of two sources together, neither of which shows the whole arrangement in one house.
    That the family's privy sits at the shady rear is reasoning from the sun rule, not a read source. That no
    collector should have to cross the inner court is this record's own rule rather than a finding.

    Caveat: The guests' privy at the rear of the zashiki, reached along a board veranda, is this project's
    reading of two sources together, neither of which shows the whole arrangement in one house. That the family's
    privy sits at the shady rear is reasoning from the sun rule, not a read source. That no collector should have
    to cross the inner court is this record's own rule rather than a finding.

    Name: latrine
    Covers: every privy building and its label
    Label: accurate
    Sources: sayama-jinya-uematsu, kotobank-benjo, tajima-2007-night-soil, guernica-night-soil, sinyoken-madori, shoinzukuri-jawiki
    Entry: research/buildings.html - 'Where does a residence put its guests' privy?', 'Privies attach to the house', 'The shady rear is the service strip'
    """

    key = "latrine"


class Stables(Kind):
    """
    What: A small stable - an umaya - a building of its own a few bays long, its stalls about 6 ft wide, for a
    few horses: the magistrate's mount and a couple of messengers' horses, with a well beside it for watering.

    Why: A warrior's stable was a freestanding building three, five or seven bays long, the most formal of them
    three bays and entered at the gable end, with separate stalls one bay wide on board floors, a matted room for
    the attendants and an earth-floored room for fodder; a lord's could be far larger. A county office is taken to keep only
    a handful of horses, so its stable is small - a fraction of the watch's barracks, never larger. It stands in
    the outer court by a service gate, so the horses and their muck go in and out without crossing the
    ceremonial ground, and the animals are led to water at a well rather than watered where they stand.

    Note: The freestanding stable a few bays long, its stalls one bay wide on board floors, and the watering at a
    well are recorded findings, and the program classes the stable as accurate: drawn smaller than the barracks,
    checked against the size audit. A stall's depth, and so its area, is a guess, and so is the number of horses:
    no page read gives either for a county post. The stable's rank below the barracks is the record's own
    reading - no readable source ranks a compound's footprints - and its watering finding was written for city
    stable yards.

    Caveat: A stall's depth, and so its area, is a guess, and so is the number of horses: no page read gives
    either for a county post. The stable's rank below the barracks is the record's own reading - no readable
    source ranks a compound's footprints - and its watering finding was written for city stable yards.

    Name: stables
    Covers: the stable building, its stall divisions and its label
    Label: accurate
    Sources: kotobank-umaya, jaanus-umaya, qingming-shanghe-tu, caravanserai-enwiki, equine-nutrition-enwiki
    Entry: research/buildings.html - 'What was a samurai's stable like, and how big was a stall?', 'The compound has a size HIERARCHY'; research/urban-features.html - 'Stable yards'
    """

    key = "stables"


class Kennel(Kind):
    """
    What: A small building for the household's hunting dogs, drawn abutting the stables in the outer court's
    service ground.

    Why: Warrior households hunted with dogs: hawking spread widely among the daimyo, and in hawking dogs
    flushed the game from the thickets, kept and trained by dog-handlers under the chief falconer; boar was hunted
    with dogs too. The kennel stands with the stables because both keep the household's animals and share the
    service yard, its well and the service gate, away from the ceremonial ground of the forecourt.

    Note: Hunting dogs kept by a samurai household are recorded, and dogs were once housed inside an official's
    compound, at Kitami in 1693, though as dogs in care rather than a hunting pack. The kennel's form, its size of
    about 11 ft square and its seat beside the stables are a guess: no page read describes a household's hunting
    kennel, gives one a size or puts one with the stables.

    Name: kennel
    Covers: the kennel building and its label
    Label: guess
    Sources: takagari-jawiki, kishuken-jawiki, inukai-kotobank, inugoya-jawiki
    Entry: research/buildings.html - 'Did a samurai household keep hunting dogs, and where were they kept?'
    """

    key = "kennel"


class FireWaterTubs(Kind):
    """
    What: Standing tubs of rainwater - tensuioke, "heaven-water tubs" - kept against fire, one at the eaves
    corner of each major wooden building and two at the kitchen, fed by the roof's runoff.

    Why: The halls of an administrative compound were ordinary wooden buildings and burned again and again,
    so standing water was kept at the point of risk: at the wooden buildings, weighted to the kitchen and its
    open fire. The plastered storehouses carry none - a thick earthen kura is the one building made not to
    burn. Each tub stands against its building's wall, under the eaves, because the gutter fills it.

    Note: Townspeople's habit of keeping water ready at the front entrance and on the roof, and per-hall water
    vats in the Forbidden City, are recorded findings, and the program classes the tubs as accurate:
    gutter-fed tensuioke at the wooden buildings. A tub at every wooden building, as a rule rather than a
    townspeople's custom, is the record's reading. The tub's 2.5 ft size is the record's estimate on no page
    read, and the weighting toward the kitchen is the record's reasoning rather than a page's words.

    Caveat: A tub at every wooden building, as a rule rather than a townspeople's custom, is the record's
    reading. The tub's 2.5 ft size is the record's estimate on no page read, and the weighting toward the
    kitchen is the record's reasoning rather than a page's words.

    Name: fire-water tubs
    Covers: every fire-water tub glyph and the "fire-water tubs" label
    Label: accurate
    Sources: tfd-hongou-fire-history, thepaper-taipinggang, edo-no-kaji-jawiki, machibikeshi-jawiki, sado-bugyosho-fires, tensuioke-jawiki, dozo-jawiki
    Entry: research/buildings.html - 'Fire-water is distributed to the halls', 'Fire discipline: halls burn, kura endure'; research/cities/fabric.html - 'How did a dense wooden city watch for fire?'
    """

    key = "fire-water tubs"


class CompoundShrine(Kind):
    """
    What: The shrine every administrative compound keeps inside its walls - a modest hall, Inari's by default,
    with ground around it kept as garden or grove. Where a plan draws its altars, or a torii before a hall set in
    its own grove, each is its own feature; where a compound serves a second kami, it may give that kami a small
    shrine of its own on the same ground.

    Why: Even the shogunate's post at Jōge, an outpost of three officials, had shrines inside its walls - an
    Inari shrine and a Tenjin shrine among them - and a full Chinese county yamen kept three, so a shrine is part
    of the equipment of any office, not a sign of a pious magistrate; what varies is its size and its
    dedication. A shrine keeping more than one kami was the ordinary case, and a kami brought in from elsewhere
    could be kept in the main hall or given its own small shrine inside the precinct. The shrine stands in the
    inner court with the household and stays smaller than the residence - a worship hall is small even at a
    great shrine.

    Note: A modest shrine inside the walls of a post of any size is a recorded finding, read on the 1869 drawing
    of the Jōge post and on a Chinese yamen's three shrines, and a second kami in a small shrine of its own is one
    of three attested forms; the program classes the shrine as accurate, with a hall-shrine ceiling of about 36
    by 30 ft subordinate to the residence. Making it Inari's by default is a guess resting on that one post, whose
    shrines are known from the drawing alone: the excavation found the post's walls, steps and foundation stones,
    not its shrines. The ranking below the residence, and the small worship hall it rests on, are the record's
    own reading, no page read giving a worship hall's size or ranking a compound's buildings.

    Caveat: Making it Inari's by default is a guess resting on that one post, whose shrines are known from the
    drawing alone: the excavation found the post's walls, steps and foundation stones, not its shrines. The
    ranking below the residence, and the small worship hall it rests on, are the record's own reading, no page
    read giving a worship hall's size or ranking a compound's buildings.

    Name: compound shrine
    Covers: the shrine hall or halls, their edging and dividing rail, and the shrine labels
    Label: accurate
    Sources: fuchu-joge-pamphlet, neixiang-yamen-zhwiki, henan-neixiang, jawiki-saijin, jawiki-goshi, kotobank-aidono, hokora-jawiki, nara-nagao-jinja
    Entry: research/buildings.html - 'What did the smallest branch office hold inside its walls?', 'Every administrative compound keeps a shrine', 'The compound has a size HIERARCHY'; research/religion-and-death.html - 'When one shrine hall serves several kami, does each have its own altar?'
    """

    key = "compound shrine"


class WritingPavilion(Kind):
    """
    What: A small detached study standing apart in the inner garden, a room where the magistrate
    does their own writing, away from both the office and the house.

    Why: A study could be a room or a building of its own. Rai San'yō, a scholar and poet of the late Edo period,
    built a detached study-cum-tea room on his Kyoto estate in 1828, its garden on its west side, and in China
    the study drew apart from the living rooms into the quiet part of the compound, beside the rear garden. The
    office hall is where the county's business is done and the residence is the family's; a pavilion set apart
    in the garden gives its owner a room that belongs to neither.

    Note: A study standing apart in the garden as a building of its own is a recorded form, at a scholar's
    estate in Kyoto and in the Chinese compound. Giving one to a magistrate, in the inner garden of the posting,
    is a guess by extension from those, and so is its size of about 18 by 14 ft: no page read describes a
    detached study at an official's compound or gives a detached study's size.

    Name: writing pavilion
    Covers: the pavilion and its label
    Label: guess
    Sources: shosai-kotobank, kyoto-ga-sanshisuimeisho, chinesepen-shuzhai
    Entry: research/buildings.html - 'Did a study ever stand apart in the garden, as a building of its own?'
    """

    key = "writing pavilion"


# ---- the parts of the household's buildings (feature 264: a thing drawn inside a feature is its own kind) -------


class Hearth(Kind):
    """
    What: The kitchen's cooking fire - a kamado, a clay range with fire-mouths, drawn as a dark block with a spot
    of flame - standing on a small earth-floored doma at the kitchen's edge or on the kitchen's board floor.

    Why: A samurai's kitchen cooked on a kamado. The rule for houses of the period was the kamado on the doma,
    but a samurai house's doma was smaller than a farmhouse's, so its kamado was sometimes set on the kitchen's
    board floor instead. The sunken fire-pit, the irori, is the common house's hearth, and none was found in a
    samurai kitchen. With fire burning from morning to night, the kitchen's fire is the compound's top ignition
    source, which is why the kitchen keeps two fire-water tubs where every other hall keeps one.

    Note: The kamado range, and both of its seats - on a small doma or on the kitchen's board floor - are
    recorded findings; each sheet takes one seat. Ranking the kitchen's fire the compound's top fire risk, and
    so giving the kitchen a second tub, is this project's reasoning, on no page read.

    Caveat: Ranking the kitchen's fire the compound's top fire risk, and so giving the kitchen a second tub, is
    this project's reasoning, on no page read.

    Name: hearth
    Covers: the fire glyph in each kitchen
    Label: accurate
    Sources: boso-no-mura-takei, liq-takayasu-daidokoro, matsue-bukeyashiki, irori-jawiki, tfd-hongou-fire-history, edo-no-kaji-jawiki, machibikeshi-jawiki, thepaper-taipinggang
    Entry: research/buildings.html - 'What fire did a residence's kitchen cook on - a kamado range, or a sunken hearth?', 'Fire-water is distributed to the halls, not the kura'
    """

    key = "hearth"


class Genkan(Kind):
    """
    What: The genkan, the formal entrance with its shikidai, the low board step where guests were bowed in and
    out: a stepped-up porch where a guest of rank's palanquin is set down against the step. Where office and
    residence share the compound it stands on the office hall, and the way to the residence runs on through the
    office.

    Why: Arrival of rank was staged - through the gate, across open ground, to the step - and the palanquin was
    brought right alongside the step so that its rider went into the building without setting foot on the
    ground; the main genkan was kept for the head of the house and honored guests. At Takayama, the one jin'ya
    whose principal parts survive, a visitor enters by the genkan and goes round the rooms of the office on to the
    residence.

    Note: The genkan with its shikidai, the staged arrival that leads to it, and the genkan on the office where
    office and residence share a compound are recorded findings. Two approaches are attested and each sheet takes
    one: the genkan, the senior house's form, or no genkan at all, where a middle gate and a walled garden path
    lead a guest to the zashiki's veranda, attested at a middle-rank house; a sheet that takes the second draws no
    genkan. The Takayama page describes a visitor's route, not how the office and the residence were laid out
    against each other.

    Caveat: The Takayama page describes a visitor's route, not how the office and the residence were laid out
    against each other.

    Name: genkan
    Covers: the entry porch at the formal entrance
    Label: accurate
    Sources: genkan-jawiki, bukeyashiki-wiki, shirobito-1717-takayama, shiroishi-koseki, kotobank-shikidai, kominkai-genkan, jaanus-uchigenkan, fuchu-joge-pamphlet, takayama-jinya-jawiki, takayama-jinya-city
    Entry: research/buildings.html - 'Where is the formal entrance, and how does a guest reach it?', 'How did a guest of rank arrive, from the gate to the entrance?', 'Guest doors feed courts, not flanks'
    """

    key = "genkan"


class Engawa(Kind):
    """
    What: The engawa, the narrow roofed veranda along the residence's garden face, drawn as a pale strip at the
    block's edge.

    Why: In a shoin-style house a wide veranda stood between the main room and the garden, serving as part of
    that room - a secondary space of the main room. It came in two layers, the irikawa inside
    the building line and the nure-en on the outer edge a step below. How many faces it wrapped went with the
    size of the house - the garden face, or two or three faces late in the period, and all four only in the
    great mansions - and its width ran from half a ken to one ken, about 3 to 6 ft, changing from face to face.

    Note: The veranda along the garden face, its width of half a ken to one ken, and the two or three faces some
    houses wrapped are recorded findings; the garden face alone and a veranda round two or three faces are both
    attested at a provincial residence's scale, and each sheet takes one. Where a plan draws the garden face at
    the wider end, that is this project's reading of the widths at Katsura, not a stated rule, and no readable
    source gives a general width for the outer nure-en.

    Caveat: Where a plan draws the garden face at the wider end, that is this project's reading of the widths at
    Katsura, not a stated rule, and no readable source gives a general width for the outer nure-en.

    Name: engawa
    Covers: the veranda strip along the residence's garden face
    Label: accurate
    Sources: engawa-kotobank, shoinzukuri-kotobank, irikawa-kotobank, katsura-rikyu-jawiki
    Entry: research/buildings.html - 'Which faces of a residence carry the veranda, and how wide is it?'
    """

    key = "engawa"


class ResidenceCorridor(Kind):
    """
    What: The short roofed corridor, a watari-roka, that joins the halls of a residence drawn in echelon, so the
    household passes from one to the other under cover.

    Why: A watari-roka is a corridor between two buildings that joins them. Such corridors belong to the great
    houses, where they joined the buildings of a shogun's or daimyo's mansion, while lesser houses had almost
    none. Halls stepped back one behind the next are, at Katsura, the form of a house built hall by hall over half
    a century, so a residence drawn this way reads as one its holders have added to; an ordinary posting's house
    is one block and has no corridor.

    Note: Corridors joining the buildings of a great house, and halls set in echelon as a house grew, are recorded
    findings; one block and echelon are both attested, and each sheet takes one. That a corridor joins each hall
    to the last is this project's reading, putting the great house's corridors together with Katsura's echelon: no
    source read says how Katsura's halls are joined.

    Caveat: That a corridor joins each hall to the last is this project's reading, putting the great house's
    corridors together with Katsura's echelon: no source read says how Katsura's halls are joined.

    Name: residence corridor
    Covers: the corridor between the residence blocks
    Label: accurate
    Sources: watariroka-kotobank, irikawa-kotobank, katsura-rikyu-jawiki
    Entry: research/buildings.html - 'Were a residence's wings joined by corridors and set in echelon, like geese in flight?'
    """

    key = "residence corridor"


class LordsQuarters(Kind):
    """
    What: The magistrate's own rooms in the residence - a room for working by day and a bedroom - several rooms
    under one label, named on the plan for the magistrate who holds the posting, standing behind the reception
    and before the family's rooms.

    Why: A lord's palace ran from front to back: the omote in front, with the entrance and the halls where the
    lord met retainers and envoys; behind it the lord's own rooms, a room for work by day and a bedroom; and
    beyond them the oku, the family's private rooms. So the master's rooms stand between the reception and the
    family, adjoining both, though Edo-period drawings count the lord's office and bedroom as part of the omote - and official
    business is done in the office hall and not here.

    Note: The lord's rooms as a working room and a bedroom, behind the reception and before the family, follow
    the record, as does the private study on the far side of the line between office and home. Two room orders
    are attested: this palace order, and a small house's (one house, as this project reads its plan), with the formal zashiki deepest in and the living rooms
    between it and the entrance; in both the reception sits at one end, and these plans follow the palace order.
    The suite's naming by its occupant is the GM's convention for these plans, and the name the lord's rooms go
    by today, the naka-oku, is a modern one.

    Caveat: The suite's naming by its occupant is the GM's convention for these plans, and the name the lord's
    rooms go by today, the naka-oku, is a modern one.

    Name: lord's quarters
    Covers: the lord's suite in the residence, its floor and its labels
    Label: accurate
    Sources: shirobito-612-omote-oku, edojo-kotobank, shoinzukuri-kotobank, matsue-bukeyashiki, touken-world-buke-madori, takayama-jinya-jawiki, takayama-jinya-city, aizu-bukeyashiki-jawiki
    Entry: research/buildings.html - 'In what order do a residence's rooms run - the reception, the master's rooms, the family's?', 'The courtroom is a room of the office hall, not a freestanding stage'; research/cities/government.html - 'Servant housing in the samurai ward'
    """

    key = "lord's quarters"


class FamilyQuarters(Kind):
    """
    What: The rooms of the magistrate's family, drawn as one labeled bay beyond the lord's own rooms, toward the
    private end of the residence.

    Why: The household lives inside the working compound, and within the house the family's rooms lie farthest
    from the formal approach. A lord's palace ran from the omote in front, through the lord's own rooms, to the
    oku, which held the lord's private rooms and the quarters of the lord's wife, where coming and going was
    strictly limited; a middle-rank house at Matsue kept a family room and the wife's living room besides its
    zashiki.

    Note: The household living inside the working compound (behind the office by Chinese regulation; at Takayama
    the residence stood beside it, and no Japanese rule was found), and the family's rooms beyond the lord's in
    the palace order, follow the record. Naming the bay by its occupants is the GM's convention for these plans.

    Caveat: Naming the bay by its occupants is the GM's convention for these plans.

    Name: family quarters
    Covers: the family's bay of the residence, its floor and its labels
    Label: accurate
    Sources: shirobito-612-omote-oku, edojo-kotobank, shoinzukuri-kotobank, matsue-bukeyashiki, neixiang-yamen-zhwiki, aizu-bukeyashiki-jawiki, jinya-jawiki, takayama-jinya-jawiki
    Entry: research/buildings.html - 'In what order do a residence's rooms run - the reception, the master's rooms, the family's?', 'Office in front, residence behind'; research/cities/government.html - 'Servant housing in the samurai ward'
    """

    key = "family quarters"


class InnerRooms(Kind):
    """
    What: A bay of the residence's private rooms at the far end from the reception, beyond the lord's and the
    family's rooms.

    Why: A samurai residence grouped its rooms by use under one roof, and in a lord's palace the private rooms,
    the oku, lay beyond the lord's own, at the far end from the front where guests were received. The house's
    memorial alcove is not among them: the butsuma was set at the formal end, by or behind the zashiki, and none
    was found among the family's private rooms.

    Note: A residence grouping its private rooms at the far end from its formal ones follows the record. The bay's
    contents are the drawing's own.

    Caveat: The bay's contents are the drawing's own.

    Name: inner rooms
    Covers: the innermost bay of the residence, its floor and its label
    Label: accurate
    Sources: shirobito-612-omote-oku, edojo-kotobank, butsuma-kotobank, aizu-bukeyashiki-jawiki
    Entry: research/buildings.html - 'In what order do a residence's rooms run - the reception, the master's rooms, the family's?', 'Where does the butsuma sit - by the zashiki, or among the private rooms?'; research/cities/government.html - 'Servant housing in the samurai ward'
    """

    key = "inner rooms"


class ReceptionRoom(Kind):
    """
    What: The zashiki, the residence's formal reception room, where the magistrate receives guests of rank, at
    one end of the house.

    Why: In a lord's palace the reception rooms stood at the front, the omote, with the lord's own rooms behind
    them and the family's beyond; a smaller house could set its formal zashiki deepest in instead, past the
    living rooms. In both orders the reception sits at one end of the house, and no source found sets it between the master's rooms
    and the family's. In the record's ideal a samurai house's prized formal garden lay on the sunny south side,
    facing its reception rooms.

    Note: Reception as a group of rooms of its own at one end of the house, and the ideal of the formal garden
    before it, follow the record; both room orders are attested, the small house's on one house as this project reads its plan, and these plans follow the palace order, the
    reception at the end nearest the approach. Where a plan's buildings allow, the reception faces the garden;
    where they do not, it faces the court or the service ground before its block, short of the ideal.

    Caveat: Where a plan's buildings allow, the reception faces the garden; where they do not, it faces the court
    or the service ground before its block, short of the ideal.

    Name: reception room (zashiki)
    Covers: the reception bay of the residence, its floor and its labels
    Label: accurate
    Sources: shirobito-612-omote-oku, edojo-kotobank, shoinzukuri-kotobank, touken-world-buke-madori, matsue-bukeyashiki, shoinzukuri-jawiki, aizu-bukeyashiki-jawiki
    Entry: research/buildings.html - 'In what order do a residence's rooms run - the reception, the master's rooms, the family's?', 'The shady rear is the service strip'; research/cities/government.html - 'Servant housing in the samurai ward'
    """

    key = "reception room"


class ShutteredWing(Kind):
    """
    What: A bay of the residence closed behind its storm shutters - rooms no longer lived in, drawn darker with the
    shutters across them.

    Why: A household one of whose members has gone may keep those rooms closed rather than give them to another
    use; whose they were is the map's own story. The storm shutters themselves, the amado, were board doors
    running on a one-groove sill along the veranda, stowed by day in a box at the end of their run and shut at
    night against wind and rain and for security.

    Note: The storm shutters are recorded. A wing drawn with its shutters closed in daylight because its rooms
    stand unused is a guess: nothing read says an unused wing was kept shut up.

    Name: shuttered wing
    Covers: the shuttered bay, its shutters and its labels
    Label: guess
    Sources: amado-kotobank
    Entry: research/buildings.html - 'Did a residence keep the storm shutters shut on rooms it was not using?'
    """

    key = "shuttered wing"


class ShrineAltar(Kind):
    """
    What: An altar inside a compound shrine's hall to one of the setting's own kami, drawn as a small glyph
    standing for the kami it serves - a rice-straw figure, a fox's torii, a flame, a wave - with its name where
    the plan gives one.

    Why: A compound keeps a shrine as standard equipment, and the kami it serves is where a magistracy's shrine
    differs. A shrine keeping several kami was the ordinary case, with a name of its own, aidono, and one form
    gave each kami a bay of the hall side by side, as a two-bay hall with two doors or small halls joined under
    one roof, the main kami in the middle as on a household's three-shrine shelf. Some kept the lesser kami (for a hall, a guess from the household shelf) behind
    the main one's altar, or gave a kami a small shrine of its own inside the precinct.

    Note: Several kami in one hall, and their altars side by side, a bay to each, are recorded findings; which of
    the three forms a compound takes is rolled per map, and each map's note says which. The single altar with the
    others behind it is attested for a household shelf only, so for a hall it is a guess. What the pages
    attest is a hall of two bays or small halls joined under one roof, not separate altars inside one undivided
    hall, so drawing them in one undivided hall is a guess. What each altar serves is the setting's or the map's
    own, and each glyph is drawn as a marker, not the altar at its size.

    Caveat: The single altar with the others behind it is attested for a household shelf only, so for a hall it is
    a guess. What the pages attest is a hall of two bays or small halls joined under one roof, not separate altars
    inside one undivided hall, so drawing them in one undivided hall is a guess. What each altar serves is the
    setting's or the map's own, and each glyph is drawn as a marker, not the altar at its size.

    Name: shrine altar
    Covers: each altar glyph inside a shrine hall, with its name and sublabels
    Label: accurate
    Sources: kotobank-aidono, jawiki-saijin, genbu-honden-styles, jawiki-goshi, tokyo-jinjacho-kamidana
    Entry: research/religion-and-death.html - 'When one shrine hall serves several kami, does each have its own altar?'; research/buildings.html - 'Every administrative compound keeps a shrine'
    """

    key = "shrine altar"


class Torii(Kind):
    """
    What: A torii, the gateway arch over the approach to a compound shrine, standing a short way in front of the
    hall.

    Why: A torii stands at the boundary between the shrine and the world outside, so how far it stands from the
    hall is how deep the shrine's ground is in front of it, and a compound shrine's ground is small. An arch is a
    mark of care, not a fixture: a household shrine that is carefully kept "may even have" one, and a compound
    shrine may have none. Two shrines on one ground may share the arch at its entrance, since it marks everything
    inside it, or each may have its own. Long avenues of arches are the gifts of rich patrons at great shrines,
    not the rule.

    Note: The arch at the boundary of the shrine's ground, and both a shared arch and one to each shrine, are
    recorded findings; each sheet takes one. How far the arch stands from its hall is a guess, kept short because
    a compound shrine's ground is small - about 5 ft where the plan is tight, up to the 20 ft a village shrine is
    drawn with where there is room: no page read gives a distance from any torii to its hall.

    Caveat: How far the arch stands from its hall is a guess, kept short because a compound shrine's ground is
    small - about 5 ft where the plan is tight, up to the 20 ft a village shrine is drawn with where there is
    room: no page read gives a distance from any torii to its hall.

    Name: torii
    Covers: the approach torii before a compound shrine
    Label: accurate
    Sources: jinjahoncho-keidai, jawiki-torii, jawiki-yashikigami, torii-enwiki, fushimi-inari-jawiki, fushimi-inari-senbon
    Entry: research/religion-and-death.html - 'How far before a small shrine does its torii stand, and can two shrines share one?', 'Torii are VOTIVE DONATIONS'
    """

    key = "torii"
