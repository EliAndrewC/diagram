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
    or three offset blocks. Its rooms, the veranda along each block's south face, the corridor between the blocks and
    the formal entrance porch (genkan) are each their own feature, and light with the house. The band label
    names the whole wing.

    Why: The household living inside the working compound, behind the office, is the point of the
    institution - the office is a household, and the gate between the two courts is the hinge between state
    and home. A visitor of rank crosses a court or garden and steps up at the genkan, never straight from the
    street into a room. In the record's ideal the prized garden lies on the sunny south side facing the
    reception rooms, and a plan seats it there where its buildings allow; by that same sun rule the shady rear
    carries the service strip. The residence is the largest domestic building on the plan - only the office hall
    may out-measure it.

    Note: The household inside the working compound (its place behind the office is Chinese regulation; the
    Japanese pages read do not give that order, and at Takayama the residence stood beside the office, not behind
    it) and the garden south of the reception rooms are recorded findings; the service strip on the shady rear is
    reasoned from the sun rule, with no source read for it; and the program classes the wing as accurate - about
    180 to 200 ft long, checked against the size audit, its label naming a zone. That the residence out-measures
    every other domestic building is this project's own reading of the compound; no page a reader can open ranks
    the footprints. The staged arrival - gate, then a court or garden, then the formal entrance - is the record's
    own reading and the GM's rule for these plans; no page a reader can open sets it out. Each labeled room is a suite of several rooms compressed to one label, a schematic convenience.

    Caveat: The staged arrival - gate, then a court or garden, then the formal entrance - is the record's own
    reading and the GM's rule for these plans; no page a reader can open sets it out. Each labeled room is a
    suite of several rooms compressed to one label, a schematic convenience.

    Name: residence
    Covers: the lord's residence blocks' fill and outlines, their room dividers, and the RESIDENCE band label
    Label: accurate
    Sources: neixiang-yamen-zhwiki, takayama-jinya-city, takayama-jinya-jawiki, machi-bugyo-jawiki, jinya-jawiki, yamen-enwiki, neixiang-xianya-zhwiki, kotobank-katteguchi, shoinzukuri-jawiki
    Entry: research/buildings.html - 'Office in front, residence behind', 'Guest doors feed courts, not flanks', 'The shady rear is the service strip', 'The compound has a size HIERARCHY'
    """

    key = "residence"


class AncestralAlcove(Kind):
    """
    What: An alcove among the residence's private rooms holding the memorial tablets of the magistrates who held
    the post before - a place within a room, not a room or hall of its own.

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
    Covers: the alcove's tablets label in the residence's inner rooms (a lineage alcove where the tablets are a lineage's)
    Label: accurate
    Sources: mingguanci-zhwiki
    Entry: research/buildings.html - 'An ancestral alcove holding office-predecessor tablets'
    """

    key = "ancestral alcove"


class KarosHouse(Kind):
    """
    What: The separate house of the karo, the house elder - the magistrate's chief retainer - standing in the
    residence court.

    Why: It stands in the inner court, on the household's side of the compound, but as a dwelling of its own
    rather than a bay of the lord's wing: the plan keeps the residence for the lord's family and gives a chief
    retainer of any standing a house of their own.

    Note: the karo's separate dwelling, rather than rooms in the lord's wing, is a rule of the drawing program
    with no research section behind it - the research record has no entry on a chief retainer's house at a
    magistrate's compound - so the house's form, size and seat are a guess.

    Name: karo's house
    Covers: the karo's house and its label with the "house elder" gloss
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

    Note: Retainers' official residences laid out inside a small domain's jin'ya are recorded, and the city
    magistracy's separate constables' district and ranked households in terraced ranges rest on recorded
    findings. A source names a storehouse keepers' rowhouse on a rural office's grounds; that the rest of its staff lived there is the record's reconstruction, no source
    naming those staff or their housing, and that their housing took the form of a rowhouse is the record's
    own reading rather than a source's words; the record places ranks of small household dwellings at the
    town's edge, outside an elite quarter, rather than inside its walls.

    Caveat: A source names a storehouse keepers' rowhouse on a rural office's grounds; that the rest of its staff lived there is the record's reconstruction, no source
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
    What: Where the household lodges a guest of rank: a guest room that is a bay of the residence, or on a
    richer posting a detached guest house with a garden of its own.

    Why: Lodging a guest is the household's business, not the office's, so the guest quarters stand with the
    residence in the inner court - a room of the house, or a house near it. A guest of rank arrives by way of
    a court or garden and steps up at a proper entrance, so a guest's door opens into a court or garden,
    never against a building's flank.

    Note: The program classes the guest quarters as accurate: a guest room in the residence or a detached guest
    house. The research record has no entry of its own on either form, so the kind rests on the program's
    classification alone. The rule that a guest's door opens into a court or garden rests on the staged
    arrival - gate, then a court or garden, then the formal entrance - which is the record's own reading and
    the GM's rule for these plans; no page a reader can open sets it out.

    Caveat: The research record has no entry of its own on either form, so the kind rests on the program's
    classification alone. The rule that a guest's door opens into a court or garden rests on the staged
    arrival - gate, then a court or garden, then the formal entrance - which is the record's own reading and
    the GM's rule for these plans; no page a reader can open sets it out.

    Name: guest quarters
    Covers: the guest room of the residence with its floor and label, or a detached guest house and its label
    Label: accurate
    Sources: kotobank-katteguchi
    Entry: research/buildings.html - 'Guest doors feed courts, not flanks'
    """

    key = "guest quarters"


class Kitchen(Kind):
    """
    What: The household's kitchen - a daidokoro, a large working building with pantries - that feeds the family,
    the staff and the watch; its hearth, and a well inside or beside it, are each their own feature.

    Why: It stands at the edge of the inner court by a postern in the wall, because service traffic is the
    deliberate opposite of a guest's arrival: the kitchen door opens into work space, not into a court. It is
    large, but smaller than a living block of the residence, and with open fire burning all day it is the
    compound's worst fire risk, so it keeps two water tubs where every other hall keeps one.

    Note: The program classes the kitchen as accurate: an institutional daidokoro of about 40 by 33 ft,
    smaller than a residence block, checked against the size audit. The kitchen's rank below the living
    quarters, its weighting as the compound's worst fire risk, with a second water tub, and its postern into
    work space are this project's reading: no readable page orders the compound's buildings by size, no page
    read gives the kitchen extra water or sets one tub to a hall as a rule, and the dictionary cited defines
    only the kitchen door, not what it opens onto. The kitchen is measured against a whole mid-rank samurai
    house of about 67 tsubo (some 2,400 sq ft), a figure that rests on no page a reader can open.

    Caveat: The kitchen's rank below the living quarters, its weighting as the compound's worst fire risk,
    with a second water tub, and its postern into work space are this project's reading: no readable page
    orders the compound's buildings by size, no page read gives the kitchen extra water or sets one tub to a
    hall as a rule, and the dictionary cited defines only the kitchen door, not what it opens onto. The
    kitchen is measured against a whole mid-rank samurai house of about 67 tsubo (some 2,400 sq ft), a figure
    that rests on no page a reader can open.

    Name: kitchen
    Covers: the kitchen and pantries building and its label
    Label: accurate
    Sources: tfd-hongou-fire-history, thepaper-taipinggang, edo-no-kaji-jawiki, machibikeshi-jawiki, kotobank-katteguchi
    Entry: research/buildings.html - 'The compound has a size HIERARCHY', 'Fire-water is distributed to the halls', 'Guest doors feed courts, not flanks'
    """

    key = "kitchen"


class Bath(Kind):
    """
    What: A small detached bath house standing in the inner garden near the residence, drawn with a curl of
    steam rising above it.

    Why: It stands on the household's side of the compound, in the garden apart from the living blocks. The
    plan gives it no well of its own.

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
    What: A privy - a kawaya - over a pit: the family's attached to the back of the residence, others serving
    the garrison, the stable yard and the gate, about one to each part of the compound.

    Why: In a samurai house the privy was built into the house, not set out in the yard, and a well-appointed
    house kept more than one. Night soil was a valuable, contracted commodity carted away by outside
    collectors, so the pits sit toward a service wall or gate where a collector's cart reaches them.

    Note: The privy built into the samurai house, the more than one privy of a well-appointed house and the
    carted night-soil trade are recorded findings, and the program classes the privies as accurate - one per
    functional zone, about three or four. That the family's privy sits at the shady north rear is reasoning from the sun rule, not a read source. That no collector should have to cross the inner court is this
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

    Note: The watering at a well is a recorded finding, and the program classes the stable as accurate: a
    few-horse umaya drawn smaller than the barracks, checked against the size audit. The stable's rank below
    the barracks is the record's own reading - no readable source ranks a compound's footprints - and so is
    the count of a few horses, since no page read gives a county office's horses; the stall figure of about 55
    to 70 sq ft to a horse is the record's own estimate, and its watering finding was written for city stable
    yards.

    Caveat: The stable's rank below the barracks is the record's own reading - no readable source ranks a
    compound's footprints - and so is the count of a few horses, since no page read gives a county office's
    horses; the stall figure of about 55 to 70 sq ft to a horse is the record's own estimate, and its watering
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

    Note: hunting hounds have a real historical counterpart, but the research record has no entry on a kennel
    at a magistrate's compound - nothing in it describes, measures or places one - so the kennel's form, size
    and seat beside the stables are a guess.

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
    its own grove, each is its own feature.

    Why: Even a small Japanese branch office kept shrines within its walls, and a full Chinese yamen kept three,
    so a shrine is part of the equipment of any office, not a sign of a pious magistrate; what varies is its
    size and its dedication. It stands in the inner court with the household and stays smaller than the
    residence - a worship hall is small even at a great shrine.

    Note: The Inari default comes from the Japanese office below; the shrine as standard equipment (read on a
    Chinese yamen's three shrines) is a recorded finding, and the program classes it as accurate: a modest shrine,
    with a hall-shrine ceiling of about 36 by 30 ft subordinate to the residence - though that ranking, and the
    small worship hall it rests on, are the record's own reading, no page read giving a worship hall's size or
    ranking a compound's buildings. The Japanese branch office with two shrines inside its
    walls rests on an excavation plan no reader can open, and the shrine's size ceiling of about 36 by 30 ft
    is set against worship-hall sizes that are the record's reading rather than a page's figures.

    Caveat: The Japanese branch office with two shrines inside its walls rests on an excavation plan no reader
    can open, and the shrine's size ceiling of about 36 by 30 ft is set against worship-hall sizes that are
    the record's reading rather than a page's figures.

    Name: compound shrine
    Covers: the shrine hall or halls, their edging and dividing rail, and the shrine labels
    Label: accurate
    Sources: neixiang-yamen-zhwiki, henan-neixiang, fushimi-inari-senbon, fushimi-inari-jawiki, torii-enwiki, hokora-jawiki, meiji-jingu-access, nara-nagao-jinja
    Entry: research/buildings.html - 'Every administrative compound keeps a shrine', 'The compound has a size HIERARCHY'; research/religion-and-death.html - 'Torii are VOTIVE DONATIONS', 'Torii spacing'
    """

    key = "compound shrine"


class WritingPavilion(Kind):
    """
    What: A small detached study standing apart in the inner garden, a room where the magistrate
    does their own writing, away from both the office and the house.

    Why: The office hall is where the county's business is done and the residence is the family's; a pavilion
    set apart in the garden gives its owner a room that belongs to neither, which is why it stands alone
    rather than as a bay of either building.

    Note: the drawing's own notes call a detached garden study a real form, but the research record has no
    entry on one at a magistrate's compound, so the pavilion's form, size and place are a guess.

    Name: writing pavilion
    Covers: the pavilion and its label
    Label: guess
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "writing pavilion"


# ---- the parts of the household's buildings (feature 264: a thing drawn inside a feature is its own kind) -------


class Hearth(Kind):
    """
    What: The kitchen's cooking fire - a fire-pit or cooking range, drawn as a dark block with a spot of flame -
    where the household's meals are cooked all day.

    Why: With open fire burning from morning to night, the kitchen's fire is the compound's top ignition source,
    which is why the kitchen keeps two fire-water tubs where every other hall keeps one.

    Note: The kitchen's open cooking fire follows the record, which names it as a kamado cooking range. Ranking
    the kitchen's fire the compound's top fire risk, and so giving the kitchen a second tub, is this project's
    reasoning, on no page read. A hearth drawn as a small square reads as a sunken fire-pit (irori), a form the
    record does not name for a kitchen.

    Caveat: Ranking the kitchen's fire the compound's top fire risk, and so giving the kitchen a second tub, is
    this project's reasoning, on no page read. A hearth drawn as a small square reads as a sunken fire-pit
    (irori), a form the record does not name for a kitchen.

    Name: hearth
    Covers: the fire glyph in each kitchen
    Label: accurate
    Sources: tfd-hongou-fire-history, edo-no-kaji-jawiki, machibikeshi-jawiki, thepaper-taipinggang
    Entry: research/buildings.html - 'Fire-water is distributed to the halls, not the kura'
    """

    key = "hearth"


class Genkan(Kind):
    """
    What: The genkan, the formal entry porch of the residence: a stepped-up entrance on the reception bay, where a
    guest of rank leaves the court or garden before it and enters the house.

    Why: Arrival of rank was staged - through the gate, across a court or garden, then up the formal entrance -
    so that a visitor never stepped from the street into a room. The genkan is the last of those stages, and it
    stands on the reception bay because the reception room is where such a guest is received.

    Note: The genkan as the formal entrance follows the record. The staged arrival that leads to it is the
    record's own reading and the GM's rule for these plans; no page a reader can open sets it out. And the one
    genkan the record attests, at the Takayama intendant's office, belonged to the office block, where these
    plans put theirs on the residence.

    Caveat: The staged arrival that leads to it is the record's own reading and the GM's rule for these plans; no
    page a reader can open sets it out. And the one genkan the record attests, at the Takayama intendant's
    office, belonged to the office block, where these plans put theirs on the residence.

    Name: genkan
    Covers: the entry porch on the residence's reception bay
    Label: accurate
    Sources: kotobank-katteguchi, takayama-jinya-jawiki, takayama-jinya-city
    Entry: research/buildings.html - 'Guest doors feed courts, not flanks', 'The courtroom is a room of the office hall, not a freestanding stage'
    """

    key = "genkan"


class Engawa(Kind):
    """
    What: The engawa, the narrow roofed veranda that runs along each residence block's south face, drawn as a pale
    strip at the block's edge.

    Why: It joins the rooms along that face and is where the house meets the ground in front of it: the rooms open
    onto it, and where the block fronts the garden, the garden is seen from it.

    Note: the research record has no entry of its own on the veranda of a residence, so its run along each block
    and its width are a guess.

    Name: engawa
    Covers: the veranda strip along each residence block's south face
    Label: guess
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "engawa"


class ResidenceCorridor(Kind):
    """
    What: The short roofed corridor that joins the residence's two offset blocks, so the household passes from
    one to the other under cover.

    Why: The residence is drawn as two blocks stepped against each other rather than one long bar, and a corridor
    between them keeps the house one dwelling.

    Note: the research record has no entry on the offset massing of a residence or on the corridor joining its
    blocks; both are the GM's ruling for these plans, and the corridor's form is a guess.

    Name: residence corridor
    Covers: the corridor between the residence blocks
    Label: guess
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "residence corridor"


class LordsQuarters(Kind):
    """
    What: The magistrate's own rooms in the residence: several rooms under one label, named on the plan for the
    magistrate who holds the posting, and usually holding a private study.

    Why: A samurai residence grouped its rooms by use under one roof, and the lord's own rooms stand on the home
    side of the line between state and household - which is why official business is done in the office hall and
    not here.

    Note: That the residence holds the lord's private study, on the far side of the line between office and home,
    follows the record, as does a samurai residence's grouping of rooms by use under one roof. The suite's
    naming by its occupant is the GM's convention for these plans; the record says little of the lord's own
    rooms beyond the study; and the order these plans follow, from the formal rooms to the lord's to the
    family's, is the drawing program's.

    Caveat: The suite's naming by its occupant is the GM's convention for these plans; the record says little of
    the lord's own rooms beyond the study; and the order these plans follow, from the formal rooms to the lord's
    to the family's, is the drawing program's.

    Name: lord's quarters
    Covers: the lord's suite in the residence, its floor and its labels
    Label: accurate
    Sources: takayama-jinya-jawiki, takayama-jinya-city, aizu-bukeyashiki-jawiki
    Entry: research/buildings.html - 'The courtroom is a room of the office hall, not a freestanding stage'; research/cities/government.html - 'Servant housing in the samurai ward'
    """

    key = "lord's quarters"


class FamilyQuarters(Kind):
    """
    What: The rooms of the magistrate's family, drawn as one labeled bay toward the private end of the residence.

    Why: The household lives inside the working compound, behind the office, and within the house the family's
    rooms lie away from the formal approach. A samurai residence grouped its rooms by use under one roof, the
    family's among them.

    Note: The household living inside the working compound (behind the office by Chinese regulation; at Takayama the residence stood beside it, and no Japanese rule was found), and a residence grouping its family's rooms under one roof,
    follow the record. That the family's rooms lie toward the private end rests on the Chinese case, where the
    innermost rows house the family; and naming the bay by its occupants is the GM's convention for these plans.

    Caveat: That the family's rooms lie toward the private end rests on the Chinese case, where the innermost rows
    house the family; and naming the bay by its occupants is the GM's convention for these plans.

    Name: family quarters
    Covers: the family's bay of the residence, its floor and its labels
    Label: accurate
    Sources: aizu-bukeyashiki-jawiki, siheyuan-zhwiki, jinya-jawiki, takayama-jinya-jawiki
    Entry: research/cities/government.html - 'Servant housing in the samurai ward'; research/buildings.html - 'Office in front, residence behind'
    """

    key = "family quarters"


class InnerRooms(Kind):
    """
    What: A bay of the residence's private rooms, apart from the formal ones, where a lineage-held posting keeps
    its ancestral alcove.

    Why: A samurai residence grouped its rooms by use under one roof, the private rooms apart from the formal
    ones, and the tablets a lineage keeps belong among its private rooms.

    Note: A residence grouping its private rooms apart from its formal ones under one roof follows the record. The
    bay's contents beyond the alcove are the drawing's own.

    Caveat: The bay's contents beyond the alcove are the drawing's own.

    Name: inner rooms
    Covers: the innermost bay of the residence, its floor and its label
    Label: accurate
    Sources: aizu-bukeyashiki-jawiki, siheyuan-zhwiki
    Entry: research/cities/government.html - 'Servant housing in the samurai ward'
    """

    key = "inner rooms"


class ReceptionRoom(Kind):
    """
    What: The zashiki, the residence's formal reception room, where the magistrate receives guests of rank, with
    the genkan at its door.

    Why: Reception was one of the room groups a residence kept apart from the family's and the servants', and in
    the record's ideal a samurai house's prized formal garden lay on the sunny south side, facing its reception
    rooms.

    Note: Reception as a group of rooms of its own, and the ideal of the formal garden before it, follow the
    record. Where a plan's buildings allow, the reception faces the garden; where they do not, it faces the court
    or the service ground before its block, short of the ideal.

    Caveat: Where a plan's buildings allow, the reception faces the garden; where they do not, it faces the court
    or the service ground before its block, short of the ideal.

    Name: reception room (zashiki)
    Covers: the reception bay of the residence, its floor and its labels
    Label: accurate
    Sources: shoinzukuri-jawiki, aizu-bukeyashiki-jawiki
    Entry: research/buildings.html - 'The shady rear is the service strip'; research/cities/government.html - 'Servant housing in the samurai ward'
    """

    key = "reception room"


class ShutteredWing(Kind):
    """
    What: A bay of the residence closed behind its storm shutters - rooms no longer lived in, drawn darker with the
    shutters across them.

    Why: A household one of whose members has gone may keep those rooms closed rather than give them to another
    use; whose they were is the map's own story.

    Note: the research record has no entry on shuttered rooms or storm shutters; the wing is the map's own story,
    closed shutters on an unused room have a plain historical counterpart, and their drawn form is a guess.

    Name: shuttered wing
    Covers: the shuttered bay, its shutters and its labels
    Label: guess
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "shuttered wing"


class ShrineAltar(Kind):
    """
    What: An altar inside a compound shrine's hall to one of the setting's own kami, drawn as a small glyph
    standing for the kami it serves - a rice-straw figure, a fox's torii, a flame, a wave - with its name where
    the plan gives one.

    Why: A compound keeps a shrine as standard equipment, and the kami it serves is where a magistracy's shrine
    differs: a priest-magistrate's hall may keep more than one altar, and a posting on a river or in an old
    household keeps altars to the powers that matter there.

    Note: a shrine in every compound follows the record (a Chinese yamen's three shrines, read); Inari's as
    the default rests on a Japanese branch office's plan that could not be found again; what each altar
    serves, and why a hall
    keeps more than one, is the setting's or the map's own, and each map's note says which. Each glyph is drawn
    as a marker, not the altar at its size.

    Name: shrine altar
    Covers: each altar glyph inside a shrine hall, with its name and sublabels
    Label: deviation
    Sources: not recorded
    Entry: research/buildings.html - 'Every administrative compound keeps a shrine'
    """

    key = "shrine altar"


class Torii(Kind):
    """
    What: A torii, the gateway arch over the approach to a compound shrine, standing a short way in front of the
    hall.

    Why: The arch marks the sacred ground: it stands where the approach enters the shrine's precinct. One arch is
    by far the usual number for a shrine, and where the map draws several it lays them one pitch apart, the innermost one pitch
    (12 ft) off its hall; long avenues of arches are the gifts of rich patrons at great shrines, not the rule.

    Note: One arch over the approach, standing where the approach enters the shrine's ground, follows the record; no page gives how far a village shrine's innermost arch stood from its hall, and the 12 ft pitch, with the innermost arch one pitch off the hall, is a guess inside the GM's ruling, bounded by one remote mountain shrine's estimated row.

    Name: torii
    Covers: the approach torii before a compound shrine
    Label: accurate
    Sources: torii-enwiki, fushimi-inari-jawiki, fushimi-inari-senbon, hokora-jawiki, nara-nagao-jinja, jinja-jawiki
    Entry: research/religion-and-death.html - 'Torii are VOTIVE DONATIONS', 'Torii spacing', 'How big is a country shrine, and what stands in its precinct?'
    """

    key = "torii"
