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
    What: The magistrate's own house: the lord's family, their rooms and a formal reception room, drawn as two
    or three offset blocks joined by a corridor, with a veranda along each block's garden face and one
    formal entrance porch (genkan) on the reception block. The band label names the whole wing.

    Why: The household living inside the working compound, behind the office, is the point of the
    institution - the office is a household, and the gate between the two courts is the hinge between state
    and home. A visitor of rank crosses a court or garden and steps up at the genkan, never straight from the
    street into a room; the prized garden lies on the sunny side facing the reception rooms, and the shady
    rear carries the service strip. The residence is the largest domestic building on the plan - only the
    office hall may out-measure it.

    Note: The household inside the working compound, the staged arrival at the genkan and the garden before
    the reception rooms are recorded findings, and the program classes the wing as accurate - about 180 to
    200 ft long, checked against the size audit, its label naming a zone. Each labeled room is a suite of
    several rooms compressed to one label and named by who lives in it rather than by its historical room
    name, a schematic convenience; the veranda along each garden face has no entry of its own in the record.

    Caveat: Each labeled room is a suite of several rooms compressed to one label and named by who lives in it
    rather than by its historical room name, a schematic convenience; the veranda along each garden face has
    no entry of its own in the record.

    Name: residence
    Covers: the lord's residence blocks, their veranda strips, the genkan porch, the reception and room labels, and the RESIDENCE band label
    Label: accurate
    Sources: neixiang-yamen-zhwiki, takayama-jinya-city, takayama-jinya-jawiki, machi-bugyo-jawiki, jinya-jawiki, yamen-enwiki, neixiang-xianya-zhwiki, kotobank-katteguchi, shoinzukuri-jawiki
    Entry: research/buildings.html - 'Office in front, residence behind', 'Guest doors feed courts, not flanks', 'The shady rear is the service strip', 'The compound has a size HIERARCHY'
    """

    key = "residence"


class AncestralAlcove(Kind):
    """
    What: A bay of the residence holding the memorial tablets of the magistrates who held the post before - an
    alcove within the family's rooms, not a hall of its own.

    Why: Such an alcove is proper only where one lineage holds the magistracy across generations, so that the
    past magistrates are the present one's own forebears and the alcove is literally ancestral. At a posting
    filled by appointment, honoring one's predecessors in office belongs in the office hall if anywhere, and
    the residence alcove holds only the family's own tablets; so a plan draws this alcove only where the
    posting is held by a lineage.

    Note: The rule rests on the setting's ruling that some magistrate's posts are held by a provincial lineage, and
    the record follows it. The Chinese practice of venerating predecessors in office has no readable source;
    the state hall for meritorious local officials that the record does quote stood at the Confucian temple,
    not inside the office.

    Caveat: The Chinese practice of venerating predecessors in office has no readable source; the state hall
    for meritorious local officials that the record does quote stood at the Confucian temple, not inside the
    office.

    Name: ancestral alcove
    Covers: the alcove bay of the residence and its tablets label (a lineage alcove where the tablets are a lineage's)
    Label: accurate
    Sources: mingguanci-zhwiki
    Entry: research/buildings.html - 'An ancestral alcove holding office-predecessor tablets'
    """

    key = "ancestral alcove"


class KarosHouse(Kind):
    """
    What: The separate house of the karo, the house elder - the magistrate's chief retainer - standing in the
    residence court with a door of its own onto the court.

    Why: It stands in the inner court, on the household's side of the compound, but as a dwelling of its own
    rather than a bay of the lord's wing: the plan keeps the residence for the lord's family and gives a chief
    retainer of any standing a house of their own.

    Note: The research record has no entry on a chief retainer's house at a magistrate's compound. That a karo
    kept a separate dwelling rather than rooms in the lord's wing is a rule of the drawing program with no
    research section behind it, so the house's form, size and seat are a guess.

    Name: karo's house
    Covers: the karo's house, its informal door and its label with the "house elder" gloss
    Label: guess
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
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

    Note: Staff housed on the grounds of a rural office and ranked households in terraced ranges are recorded
    findings. That the retainers' housing at a rural office took the form of a rowhouse is the record's own
    reading rather than a source's words, and the record places ranks of small household dwellings at the
    town's edge, outside an elite quarter, rather than inside its walls.

    Caveat: That the retainers' housing at a rural office took the form of a rowhouse is the record's own
    reading rather than a source's words, and the record places ranks of small household dwellings at the
    town's edge, outside an elite quarter, rather than inside its walls.

    Name: retainers' quarters
    Covers: the senior retainers' quarters, a family rowhouse for married retainers, and their doors and labels
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
    Covers: the servants' nagaya, its door and its label
    Label: accurate
    Sources: jta-nagayamon, fukui-bushi-jutaku, aizu-bukeyashiki-jawiki, kotobank-degawari, nagayamon-jawiki, nando-jawiki, daozuofang, shoinzukuri-jawiki
    Entry: research/cities/government.html - 'Servant housing in the samurai ward'; research/buildings.html - 'The shady rear is the service strip'
    """

    key = "servants' quarters"


class GuestQuarters(Kind):
    """
    What: Where the household lodges a guest of rank: a guest room that is a bay of the residence, or on a
    richer posting a detached guest house with a garden of its own.

    Why: Lodging a guest is the household's business, not the office's, so the guest quarters stand with the
    residence in the inner court - a room of the house, or a house near it. A guest of rank arrives by way of
    a court or garden and steps up at a proper entrance, so a guest's door opens into a court or garden,
    never against a building's flank.

    Note: The program classes the guest quarters as accurate: a guest room in the residence or a detached guest
    house. The research record has no entry of its own on either form, so the kind rests on the program's
    classification alone; the rule that a guest's door opens into a court or garden is the record's, and
    no page read sets out that staged arrival.

    Caveat: The research record has no entry of its own on either form, so the kind rests on the program's
    classification alone; the rule that a guest's door opens into a court or garden is the record's, and
    no page read sets out that staged arrival.

    Name: guest quarters
    Covers: the guest room of the residence, or a detached guest house with its door and label
    Label: accurate
    Sources: kotobank-katteguchi
    Entry: research/buildings.html - 'Guest doors feed courts, not flanks'
    """

    key = "guest quarters"


class Kitchen(Kind):
    """
    What: The household's kitchen - a daidokoro, a large working building with its kamado range, pantries and a
    well inside or beside it - that feeds the family, the staff and the watch.

    Why: It stands at the edge of the inner court by a postern in the wall, because service traffic is the
    deliberate opposite of a guest's arrival: the kitchen door opens into work space, not into a court. It is
    large, but smaller than a living block of the residence, and with open fire burning all day it is the
    compound's worst fire risk, so it keeps two water tubs where every other hall keeps one.

    Note: The kitchen's rank below the living quarters, its fire risk and its postern into work space are
    recorded findings, and the program classes it as accurate: an institutional daidokoro of about 40 by 33 ft,
    smaller than a residence block, checked against the size audit. The whole mid-rank house it is measured
    against, about 67 tsubo, rests on no page a reader can open.

    Caveat: The whole mid-rank house it is measured against, about 67 tsubo, rests on no page a reader can
    open.

    Name: kitchen
    Covers: the kitchen and pantries building, its hearth and its label
    Label: accurate
    Sources: tfd-hongou-fire-history, thepaper-taipinggang, edo-no-kaji-jawiki, machibikeshi-jawiki, kotobank-katteguchi
    Entry: research/buildings.html - 'The compound has a size HIERARCHY', 'Fire-water is distributed to the halls', 'Guest doors feed courts, not flanks'
    """

    key = "kitchen"


class Bath(Kind):
    """
    What: A small detached bath house standing in the inner garden near the residence, drawn with a curl of
    steam rising above it.

    Why: It stands on the household's side of the compound, in the garden apart from the living blocks, and
    near enough to the kitchen well that its water is carried from there rather than drawn from a well of its
    own.

    Note: The program classes the bath as accurate: a detached pavilion of 12 to 18 ft, checked against the size
    audit. The research record has no entry on a manor's bath; its only bath entry is the farmstead's bath shed,
    which it attests on farms without finding where the shed stood.

    Caveat: The research record has no entry on a manor's bath; its only bath entry is the farmstead's bath shed,
    which it attests on farms without finding where the shed stood.

    Name: bath
    Covers: the bath house, its steam mark and its label
    Label: accurate
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "bath"


class Well(Kind):
    """
    What: A private well inside the compound's walls - a shaft with a stone curb - drawn as a square curb with a
    dark mouth: one at or in the kitchen, one in the garden, one beside the stables, sometimes a fourth.

    Why: Samurai and government households drew their water from wells inside their own walled compounds,
    not from the communal wells where commoners gathered. The kitchen well is the busiest; the stables well
    waters the horses; the garden well serves the family, and the well sits in the service ground rather than
    in a court meant for ceremony.

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
    What: A privy - a kawaya - over a pit: the family's attached to the back of the residence, others serving
    the garrison, the stable yard and the gate, about one to each part of the compound.

    Why: In a samurai house the privy was built into the house, not set out in the yard, and a well-appointed
    house kept more than one. Night soil was a valuable, contracted commodity carted away by outside
    collectors, so the pits sit toward a service wall or gate where a collector's cart reaches them.

    Note: The privy built into the samurai house, the count of about one to a functional zone and the carted
    night-soil trade are recorded findings, and the program classes the privies as accurate - one per
    functional zone, about three or four. That no collector should have to cross the inner court is this
    record's own rule rather than a finding.

    Caveat: That no collector should have to cross the inner court is this record's own rule rather than a
    finding.

    Name: latrine
    Covers: every privy building and its label
    Label: accurate
    Sources: tajima-2007-night-soil, guernica-night-soil, kotobank-benjo, sinyoken-madori, shoinzukuri-jawiki
    Entry: research/buildings.html - 'Privies attach to the house', 'The shady rear is the service strip'
    """

    key = "latrine"


class Stables(Kind):
    """
    What: A small stable - an umaya - with stalls for a few horses: the magistrate's mount and a couple of
    messengers' horses, with a well beside it for watering.

    Why: A county office kept only a handful of horses, so its stable is small - a fraction of the watch's
    barracks, never larger. It stands in the outer court by a service gate, so the horses and their muck go
    in and out without crossing the ceremonial ground, and the animals are led to water at a well rather than
    watered where they stand.

    Note: The stable's rank below the barracks and the watering at a well are recorded findings, and the program
    classes it as accurate: a few-horse umaya drawn smaller than the barracks, checked against the size audit.
    The stall figure of about 55 to 70 sq ft to a horse is the record's own estimate, and its watering finding
    was written for city stable yards.

    Caveat: The stall figure of about 55 to 70 sq ft to a horse is the record's own estimate, and its watering
    finding was written for city stable yards.

    Name: stables
    Covers: the stable building, its stall divisions and its label
    Label: accurate
    Sources: qingming-shanghe-tu, caravanserai-enwiki, equine-nutrition-enwiki
    Entry: research/buildings.html - 'The compound has a size HIERARCHY'; research/urban-features.html - 'Stable yards'
    """

    key = "stables"


class Kennel(Kind):
    """
    What: A small building for the household's hunting dogs, drawn abutting the stables in the outer court's
    service ground.

    Why: It stands with the stables because both keep the household's animals and share the service yard, its
    well and the service gate, away from the ceremonial ground of the forecourt.

    Note: The research record has no entry on a kennel at a magistrate's compound. Hunting hounds have a real
    historical counterpart, but nothing in the record describes, measures or places one, so the kennel's
    form, size and seat beside the stables are a guess.

    Name: kennel
    Covers: the kennel building and its label
    Label: guess
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
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

    Note: Water kept ready at every frontage and on the roofs, and per-hall water vats in the Forbidden City, are
    recorded findings, and the program classes the tubs as accurate: gutter-fed tensuioke at the wooden
    buildings. The tub's 2.5 ft size is the record's estimate on no page read, and the weighting toward the
    kitchen is the record's reasoning rather than a page's words.

    Caveat: The tub's 2.5 ft size is the record's estimate on no page read, and the weighting toward the kitchen
    is the record's reasoning rather than a page's words.

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
    with a torii before it and ground around it kept as garden or grove.

    Why: Even a small Japanese branch office kept shrines within its walls, and a full Chinese yamen kept three,
    so a shrine is part of the equipment of any office, not a sign of a pious magistrate; what varies is its
    size and its dedication. It stands in the inner court with the household, stays smaller than the
    residence - a worship hall is small even at a great shrine - and takes a single arch, the overwhelming
    form, set about 20 ft before its hall as at a village shrine.

    Note: The shrine as standard equipment, its Inari default, the small worship hall and the single torii are
    recorded findings, and the program classes it as accurate: a modest shrine, with a hall-shrine ceiling of
    about 36 by 30 ft subordinate to the residence. The Japanese branch office with two shrines inside its
    walls rests on an excavation plan no reader can open, and the worship-hall sizes the ceiling is set
    against are the record's reading rather than a page's figures.

    Caveat: The Japanese branch office with two shrines inside its walls rests on an excavation plan no reader
    can open, and the worship-hall sizes the ceiling is set against are the record's reading rather than a
    page's figures.

    Name: compound shrine
    Covers: the shrine hall or halls, their altars and inner glyphs, the approach torii, and the shrine labels
    Label: accurate
    Sources: neixiang-yamen-zhwiki, henan-neixiang, fushimi-inari-senbon, fushimi-inari-jawiki, torii-enwiki, hokora-jawiki, meiji-jingu-access, nara-nagao-jinja
    Entry: research/buildings.html - 'Every administrative compound keeps a shrine', 'The compound has a size HIERARCHY'; research/religion-and-death.html - 'Torii are VOTIVE DONATIONS', 'Torii spacing'
    """

    key = "compound shrine"


class WritingPavilion(Kind):
    """
    What: A small detached study standing apart in the inner garden, a room with a veranda where the magistrate
    does their own writing, away from both the office and the house.

    Why: The office hall is where the county's business is done and the residence is the family's; a pavilion
    set apart in the garden gives its owner a room that belongs to neither, which is why it stands alone
    rather than as a bay of either building.

    Note: The research record has no entry on a detached garden study at a magistrate's compound. The drawing's
    own notes call such a study a real form, but no research section records it, so the pavilion's form, size
    and place are a guess.

    Name: writing pavilion
    Covers: the pavilion and its label
    Label: guess
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "writing pavilion"
