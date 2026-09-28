"""The compound's grounds and its bounds - the courts, the gardens, the wall and its gates, the ways that reach it.

Each class's DOCSTRING is its explanation - `What:`, `Why:`, `Note:`, optional `Caveat:`, then the data tags -
parsed by `..classes._base.parse_explanation` (feature 189). Every kind is written FROM the existing record
(feature 262, FR-005): the sections its `Entry:` names, and the `buildings/types.json` program item folded into
it where there is one (the item's class and why are carried here, not re-decided). The measurement behind each
label is `specs/262-interactive-magistracy-pages/coverage.md`.
"""

from __future__ import annotations

from ..classes import Kind


class OuterCourt(Kind):
    """
    What: The public half of the compound, just inside the main gate: an open forecourt where arrivals
    gather, the office hall with its hearing court, and the working buildings of the office - stores,
    stables, the watch's lodging - set around its edges.

    Why: Chinese county offices put the office in front and the residence behind, and this setting follows
    them: Chinese regulation required it of a county office, and Japanese offices likewise kept the chief's
    household inside the working compound, though no source read sets it behind the office. So
    whoever comes on business - a petitioner, a taxpayer, a prisoner - is dealt with here, near the gate,
    and goes no deeper. Its open ground is not wasted space: a real jin'ya left most of its site open, and
    its forecourt and hearing court were features of the plan in their own right.

    Note: The two-court split follows the Chinese record, and the open forecourt follows the record; no
    codification of the split was found, and at Takayama the residence stood beside the office rather than
    behind it. No Japanese source read shows the residence behind the office; how much of a jin'ya's site stood
    open is this project's own estimate from plans, no source read giving the figure. On these plans the
    buildings stand somewhat further apart than in a real jin'ya, which joined its functions into a few long
    connected ranges, so that each reads as its own labeled footprint.

    Caveat: No Japanese source read shows the residence behind the office; how much of a jin'ya's site stood
    open is this project's own estimate from plans, no source read giving the figure. On these plans the
    buildings stand somewhat further apart than in a real jin'ya, which joined its functions into a few long
    connected ranges, so that each reads as its own labeled footprint.

    Name: outer court
    Covers: the outer court's ground and its labels, the forecourt among them
    Label: accurate
    Sources: neixiang-yamen-zhwiki, takayama-jinya-jawiki, takayama-jinya-city, machi-bugyo-jawiki, jinya-jawiki, yamen-enwiki, neixiang-xianya-zhwiki
    Entry: research/buildings.html - 'Office in front, residence behind - the two-court split is universal', 'Packing: a jin'ya is mostly open'
    """

    key = "outer court"


class InnerCourt(Kind):
    """
    What: The private half of the compound, behind the internal wall: the magistrate's residence and
    household, its garden and the compound's shrine, with the kitchen, the servants' quarters and the
    service ground that keep the household running.

    Why: The chief's household living inside the working compound is the point of the institution - the
    office is a household, and the wall between the two courts is the hinge between state and home. So the
    inner court lies behind the office hall, away from the gate, reached from the outer court only by the
    household's own door. The record's ideal puts its prized formal garden on the sunny south side, facing
    the reception rooms, and a plan seats it there where its buildings allow; the household's service
    economy fills the shady rear.

    Note: The household inside the compound follows the record; the residence-behind-the-office order is
    Chinese regulation (Neixiang), while the Japanese pages read show no front-and-rear order - at Takayama the
    residence stood beside the office, to the west. The two-court split and the formal garden south of the
    reception rooms follow the record. The service strip along the shady north rear is this record's own
    reasoning from where the formal garden sat, not something a source describes.

    Caveat: The service strip along the shady north rear is this record's own reasoning from where the formal
    garden sat, not something a source describes.

    Name: inner court
    Covers: the inner court's ground and its label
    Label: accurate
    Sources: neixiang-yamen-zhwiki, takayama-jinya-jawiki, machi-bugyo-jawiki, jinya-jawiki, yamen-enwiki, shoinzukuri-jawiki
    Entry: research/buildings.html - 'Office in front, residence behind - the two-court split is universal', 'The shady rear is the service strip'
    """

    key = "inner court"


class BorderCourt(Kind):
    """
    What: A receiving court kept apart from the hearing court: a swept court that visitors of rank step into
    when they arrive by a door of their own, before they are shown into the room where they are received. On a
    border posting it is where a delegation from across the border is met.

    Why: A domain kept guard posts where its roads crossed into a neighbor's land, to watch the people and goods
    going in and out and sometimes to tax them. At Nuruyu, one of the few that survive, the front gate stood
    across the road and the inspection hall faced it, so the ground between gate and hall was where everyone
    crossing passed before the officers. Arrival of rank, too, was staged: through the gate, across open ground,
    then up the step of the formal entrance - a guest never stepped from the road straight into a room. So a
    guests' door opens into a court fit to receive them, and not onto the hearing court where the accused kneel.

    Note: a court between the gate on the road and the inspection hall is the ground those crossing really
    passed over, and a formal reception room in a border officer's house is attested even at a plain post.
    Keeping that court for delegations of rank from across a clan border, received there with ceremony, is this
    setting's own, a departure built on the examining ground: no page read describes a border post that kept a
    court for receiving officials of the neighboring domain.

    Name: border court
    Covers: the receiving court behind a border posting's parley door, and its label
    Label: deviation
    Sources: kotobank-bansho, bunka-nuruyu-bansho, bansho-jawiki, kotobank-shikidai, kominkai-genkan
    Entry: research/buildings.html - 'Why would a border posting keep a court for those crossing?', 'How did a guest of rank arrive, from the gate to the entrance?', 'Guest doors feed courts, not flanks'
    """

    key = "border court"


class HearingCourt(Kind):
    """
    What: The oshirasu: the roofed court directly before the office hall's dais where the parties to a case knelt
    to be heard and judged, the magistrate above them on the raised floor. Its floor is spread with white gravel,
    or with cobbles from the local riverbed.

    Why: A magistracy's court was roofed, either under a roof built over it or as an earth floor spread with
    gravel inside the building; the open-air court of white sand is the image of the period dramas, not the
    history. The one that survives at an intendant's office, Takayama's, is paved with river cobbles, because
    its province had not enough white sand, and was made inside the building because an open court would be
    buried in winter snow; Takayama keeps two such courts, one for suits and petitions and one for criminal
    cases. The courtroom was a room of the office hall, not a stage of its own, so the hearing court lies against
    the front of the hall where the magistrate sits. In Rokugan, where torture is unusual, a magistracy keeps no
    room built for interrogation, so questioning happens here or in the day office like any other business.

    Note: What covers the floor is one of two attested forms, white gravel or cobbles from the local riverbed
    where white sand is scarce, and each sheet takes one. That a jin'ya was laid out around the hearing court and
    the forecourt as open features is this project's reading of plans, which no readable source measures. No
    roofed court's size was found, so the size each sheet draws is a guess.

    Caveat: That a jin'ya was laid out around the hearing court and the forecourt as open features is this
    project's reading of plans, which no readable source measures. No roofed court's size was found, so the size
    each sheet draws is a guess.

    Name: hearing court (oshirasu)
    Covers: the roofed court before the dais and its label
    Label: accurate
    Sources: oshirasu-jawiki, takayama-jinya-city, takayama-gh-shirasu, shirasu-imidas, takayama-jinya-official, takayama-jinya-jawiki
    Entry: research/buildings.html - 'Was the hearing court open white sand, or roofed?', 'The courtroom is a room of the office hall, not a freestanding stage', 'No interrogation room', 'Packing: a jin'ya is mostly open'
    """

    key = "hearing court"


class PracticeGround(Kind):
    """
    What: A patch of swept earth in the outer court, marked by the gear that stands on it: the place where the
    compound's samurai keep up their daily practice.

    Why: A dojo with a resident teacher and enrolled students was an institution of cities, in Japan and
    China alike; rural samurai most likely trained at home in an earthen yard, in a hall cleared for the
    purpose, or on shrine grounds. A county seat holds about fifteen samurai - no student body and no living for a teacher -
    so its magistracy trains on open ground in its own compound, and what marks that ground is the gear
    practice leaves behind, not a building. It is sized to the samurai who drill there, about 90 to 135 sq ft
    each.

    Note: Courtyard keiko in place of a dojo follows the record only in part: the famous private fencing
    dojos read on stood in Edo, and practice before the mid-Edo period was held outdoors or on earthen floors.
    The one martial ground the pages read on an intendant's office name there is a riding ground, and the
    drill ground read on stood at a small domain's jin'ya, so they confirm the practice ground. That domain
    schools stood in castle towns and cities as a rule (the two read, Hagi's and Mito's, stood inside their
    castles), that rural samurai trained in yards, cleared halls or on shrine grounds, and that a Chinese
    county yamen had no training hall are guesses no page read confirms. That a
    rural intendant's office kept no martial hall is a guess from the silence of the pages read on one, which
    list its buildings without one but never say it had none.

    Caveat: That domain schools stood in castle towns and cities as a rule (the two read, Hagi's and Mito's,
    stood inside their castles), that rural samurai trained in yards, cleared halls or on shrine grounds, and
    that a Chinese county yamen had no training hall are guesses no page read confirms. That a rural intendant's office kept no martial hall is a guess from the silence of
    the pages read on one, which list its buildings without one but never say it had none.

    Name: practice ground
    Covers: the swept keiko patch and its label
    Label: accurate
    Sources: hanko-jawiki, hagi-meirinkan-guide, kodokan-mito-jawiki, edo-three-dojos-jawiki, jinya-jawiki, dojo-jawiki, genbukan-jawiki, kotobank-machidojo
    Entry: research/buildings.html - 'A dojo is a city institution; county training is courtyard keiko'; research/cities/government.html - 'Martial training is an URBAN institution'
    """

    key = "practice ground"


class CompoundGarden(Kind):
    """
    What: The compound's ornamental ground - planting, laid out to be looked at: the inner garden at the heart of
    the private court and, where a plan has them, a walled garden path to the reception room's veranda, a garden
    around the shrine or one kept for guests.

    Why: A samurai house's prized formal garden lay on the sunny south side, facing the reception rooms. At
    Takayama, the one intendant's office whose buildings survive, a single garden is seen both from the great
    hall of the office and from the room where the intendant lived, with stepping stones into it from each, so
    the private rooms look onto the one garden rather than a garden of their own. A garden was
    one of two kinds beside samurai rooms: a pond garden built around real water, or a dry garden of stones and
    white gravel standing for water. A guest reached the house in one of two ways: by a formal entrance on the
    office, as at Takayama, or, at a middle-rank house with no such entrance, through a middle gate in a wall
    and along a walled garden path (roji) straight to the veranda of the reception room. The household's god
    was kept in a corner of the lot, in a small shrine or at an old tree beside it.

    Note: The pond garden and the dry garden are both attested beside samurai rooms, and each sheet takes one;
    so are the two ways a guest reached the house. A separate small garden for the private rooms was found at no
    posting, and sharing the one garden is read from Takayama, grander than most postings. The pond's form and
    size are a guess: no page read gives the size of a residence garden's pond. A garden where a court
    would stand between gate and entrance, as where a guests' door opens into a guest garden, is a guess: the
    ground a guest crossed was an open court, and no page read says it was ever a garden. A fenced forecourt
    before the entrance rests on nothing found and is a guess. The shrine in a corner and a tree beside it are
    attested, but an ornamental garden planted around a compound's shrine is described on no page read and is a
    guess.

    Caveat: The pond's form and size are a guess: no page read gives the size of a residence garden's pond. A
    garden where a court would stand between gate and entrance, as where a guests' door opens into a
    guest garden, is a guess: the ground a guest crossed was an open court, and no page read says it was ever a
    garden. A fenced forecourt before the entrance rests on nothing found and is a guess. The shrine in a corner
    and a tree beside it are attested, but an ornamental garden planted around a compound's shrine is described
    on no page read and is a guess.

    Name: garden
    Covers: the inner garden, a garden path, a shrine garden and a guest garden, and their labels
    Label: accurate
    Sources: oniwa-takayama-jinya, kotobank-teien, okutono-jinya-garden, chiran-bukeyashiki-gardens, genkan-jawiki, shirobito-1717-takayama, shiroishi-koseki, kotobank-shikidai, kominkai-genkan, fuchu-joge-pamphlet, kotobank-yashikigami, jawiki-yashikigami, shoinzukuri-jawiki
    Entry: research/buildings.html - 'Did the private rooms of an ordinary posting have a garden of their own?', 'Did a residence garden have a pond, and did a county post keep one?', 'Where is the formal entrance, and how does a guest reach it?', 'How did a guest of rank arrive, from the gate to the entrance?', 'What grew around the compound's own shrine?', 'The shady rear is the service strip', 'Guest doors feed courts, not flanks'
    """

    key = "garden"


class VegetableGarden(Kind):
    """
    What: A vegetable garden for the household's own table, worked in the service ground behind the residence.

    Why: Samurai grew their own vegetables, on anything from a kitchen plot to half their grounds. The
    Boso-no-mura house of a middle-rank samurai family has a soup-greens plot of about 1,070 sq ft, planted
    mainly with leafy greens, on the west side of the house; at Matsushiro a 150-koku retainer's house kept
    about half its grounds in vegetable field. The formal garden took the south side of the house, so the
    vegetable garden lay off it.

    Note: Its size is one of two attested forms, a soup-greens plot or a field over about half the grounds, and
    each sheet takes its own. Seating it to the north of the house is a guess, reasoned from the formal garden
    taking the sunny south: no vegetable garden north of a house was found, and the one plot whose side is given
    lay to the west.

    Caveat: Seating it to the north of the house is a guess, reasoned from the formal garden taking the sunny
    south: no vegetable garden north of a house was found, and the one plot whose side is given lay to the west.

    Name: vegetable garden
    Covers: the kitchen garden's beds and label
    Label: accurate
    Sources: boso-no-mura-takei, matsushiro-bukeyashiki, shoinzukuri-jawiki
    Entry: research/buildings.html - 'Where did a residence keep its vegetable garden, and how big was it?', 'The shady rear is the service strip'
    """

    key = "vegetable garden"


class ShrineGrove(Kind):
    """
    What: A stand of kept trees around the compound's shrine, its hall and arch set in a cleared opening among
    them: the shrine's own sacred wood.

    Why: A Japanese shrine's setting was a deliberately preserved grove, the chinju no mori - a wood kept and
    tended around the sanctuary, the approach and the place of worship, so that the precinct sits inside
    kept trees rather than in cleared ground. This map draws a village shrine's precinct as its grove, with the hall in a small
    swept clearing inside it and no fence around it.

    Note: The grove as the setting of a shrine follows the record, as does the village's own households answering for the shrine's cleaning; that its clearing was a swept surface is general reading with no page found; that the wood fills most of a precinct's unbuilt ground is a guess, since no source measures what covered the ground beyond buildings that took a fortieth to a seventh of it. Everything the record holds is about a
    village shrine standing in its own wood; nothing covers a grove kept inside a compound wall.

    Caveat: Everything the record holds is about a village shrine standing in its own wood; nothing covers a
    grove kept inside a compound wall.

    Name: shrine grove (chinju no mori)
    Covers: the grove's ground and its tree canopies
    Label: accurate
    Sources: chinju-no-mori-jawiki, fengshui-woodland-enwiki, jinja-jawiki
    Entry: research/religion-and-death.html - 'Is the ground around a shrine or a grave swept clear of scrub?', 'Where does a village put its shrine, and how big is it?', 'How big is a country shrine, and what stands in its precinct?', 'How large was a village shrine's precinct, and how much of it was built on?'
    """

    key = "shrine grove"


class CompoundWall(Kind):
    """
    What: The heavy wall around the whole compound: earth rammed or laid up thick, under its own
    tiled coping, broken only at the gates. Buildings back onto it, but none stands in it.

    Why: A walled enclosure is the grammar every administrative compound shares, Japanese or Chinese. A wall
    of this class is a building in its own right - thick enough to stop missiles and to carry the
    tiles that keep its earth core dry - so the ground under it is occupied, and the buildings ringing a
    court back onto it with their eaves nearly touching, a foot or two off so that the wall stays reachable
    for patching.

    Note: we have drawn the compound wall 3 ft thick, the heavier of the two real forms, in order to make its
    stroke read on the plan (the GM's ruling). Two forms of earth wall are attested: the lighter wall of earth or
    clay laid up without a frame, or plastered over posts, about 1 to 2 ft thick - a surviving late-Edo neribei
    measures 0.6 m, about 2 ft, across its base - and the rammed-earth tsuijibei, built up to about 1 m (3.3 ft)
    thick. Samurai of middle rank and above walled their land with earth; no page read measures the wall of a
    magistrate's post itself. How near the buildings stand to the wall, eaves nearly touching and a foot or two
    off, is our own reasoning; no source we found describes it.

    Name: compound wall
    Covers: the outer wall's strokes
    Label: convention
    Sources: kunishitei-toyonaga-neribei, kojodan-dobei, hei-jokaku-jawiki, mlit-kanazawa-dobei, tsuijibei-jawiki
    Entry: research/buildings.html - 'How thick was a compound's earth wall?', 'A compound wall is a building, not a boundary line', 'Administrative culture is JAPAN-first for compound interiors'
    """

    key = "compound wall"


class MainGate(Kind):
    """
    What: The compound's formal entrance in the front wall, with the forecourt beyond: either a gate of one bay
    between heavy posts, or an opening through a gate range (nagaya-mon) whose rooms flank it. It is the widest
    of the compound's doors, and the one meant for visitors on business.

    Why: A Japanese post's gate took one of two forms. The nagaya-mon, a gate opened through a range of rooms,
    arose as the gate of castles, jin'ya and samurai residences, its design fixed by the house's standing; a
    registered one opens in its central two ken, about 12 ft. The one-bay gate (yakuimon) measures about 6 to
    8.5 ft across its frontage in registered examples. A Chinese county office's gate was instead a roofed
    building, three bays wide by law. A magistrate's manor faces what it fronts - the town it governs or the road
    it stands beside - and its gate opens onto that way; where nothing else decides it, the gate faces south,
    the formal orientation a Chinese county office took by regulation. Behind it, arrival is staged: the gate,
    then open ground a palanquin can cross, then the step of the formal entrance, so no visitor steps from the
    road into a room.

    Note: The one-bay gate and the nagaya-mon are both attested, and each sheet takes one. A yamen's gate drawn
    as a roofed building of three bays follows the record, but its 18 to 24 ft width is a guess, since no page
    read gives one. Facing what it fronts, the town or the road, is this project's own siting, calibrated against
    the drawn maps; only the southern fallback rests on a source, and that one is Chinese.

    Caveat: A yamen's gate drawn as a roofed building of three bays follows the record, but its 18 to 24 ft
    width is a guess, since no page read gives one. Facing what it fronts, the town or the road, is this
    project's own siting, calibrated against the drawn maps; only the southern fallback rests on a source, and
    that one is Chinese.

    Name: main gate
    Covers: the posts flanking the main opening
    Label: accurate
    Sources: nagayamon-jawiki, tamba-kashiwara-jinya, bunka-saito-nagayamon, bunka-adachi-yakuimon, bunka-omi-yakuimon, bunka-fujioka-yakuimon, sohu-yamen-gate, bjd-qing-yamen, neixiang-xianya-zhwiki, kotobank-shikidai, kominkai-genkan
    Entry: research/buildings.html - 'How wide was the main gate of a magistrate's post?', 'How did a guest of rank arrive, from the gate to the entrance?', 'Guest doors feed courts, not flanks'; research/towns.html - 'Where does a magistrate's manor stand, and which way does its gate face?'; research/religion-and-death.html - 'How large are the gates, walls and funerary features drawn?'
    """

    key = "main gate"


class SideGate(Kind):
    """
    What: A lesser door in the compound wall: the kitchen postern for deliveries and night soil, a service
    gate by the stables or the stores, a landing gate to the water, or a guests' door of its own. Each is
    narrower than the main gate.

    Why: Service traffic is the deliberate inverse of a guest's arrival: the kitchen postern opens straight
    into work space, so deliveries, muck and the night-soil carters never cross the courts where the office
    does its business or the household lives. Night soil was a paid-for commodity emptied by outside carters,
    so the pits sit toward a service wall or gate a cart can reach. A door meant for guests, by contrast,
    opens onto open ground before an entrance, the way a guest of rank arrived. In this setting wagons and carts
    use the roads between towns, so a compound that ships or receives bulk goods keeps a gate a cart can use.

    Note: The service doors follow the record, though the dictionary names only the kitchen door and that it
    opens into work space is this record's reading. That a night-soil collector never has to cross the inner
    court is this record's own rule rather than a finding. A cart gate or landing gate that carts pass is the
    setting's own: carts were kept to the towns and off the highways in Edo Japan, and the GM's notes put
    wagons and carts on the roads.

    Caveat: That a night-soil collector never has to cross the inner court is this record's own rule rather
    than a finding. A cart gate or landing gate that carts pass is the setting's own: carts were kept to the
    towns and off the highways in Edo Japan, and the GM's notes put wagons and carts on the roads.

    Name: side gate
    Covers: the posts of the posterns, service gates, landing gate, cart gate and guests' door
    Label: accurate
    Sources: kotobank-katteguchi, tajima-2007-night-soil, guernica-night-soil, kotobank-benjo, kotobank-shikidai, kominkai-genkan, kotobank-daihachiguruma, l7r-wagons
    Entry: research/ways.html - 'Could a cart use the roads here, and where would it go?'; research/buildings.html - 'How did a guest of rank arrive, from the gate to the entrance?', 'Guest doors feed courts, not flanks', 'Privies attach to the house; night-soil drives their placement'
    """

    key = "side gate"


class CourtDivider(Kind):
    """
    What: The lighter wall that splits the compound into its outer and inner courts, broken by one narrow
    household door, the nakamon.

    Why: The split between the courts is the split between state and home: the office and its public business
    in front, the household behind, with only the one door between them.

    Note: The internal wall between the two courts follows the Chinese record, where regulation put the office in front and the residence behind an inner residence gate; for Japanese compounds that front-and-rear order is on no page read, and at Takayama the residence stood beside the office rather than behind it. No source measures the divider: the wall's
    2 ft thickness is this project's own figure.

    Caveat: No source measures the divider: the wall's 2 ft thickness is this project's own figure.

    Name: court divider
    Covers: the internal wall's strokes
    Label: accurate
    Sources: neixiang-yamen-zhwiki, machi-bugyo-jawiki, yamen-enwiki
    Entry: research/buildings.html - 'Office in front, residence behind - the two-court split is universal'
    """

    key = "court divider"


class ApproachRoad(Kind):
    """
    What: The ways that bring traffic to the compound: the road or town street up to the main gate, and the
    lanes that serve its lesser doors.

    Why: A magistrate's manor stands at the edge of the settlement it administers, and its gate faces what it
    fronts - the town, or the road it sits beside - opening onto the roadbed; where a manor fronts a road at
    an angle, the whole compound turns so its front wall runs parallel to the way. So a road always arrives at
    the main gate. A planned Chinese capital was a grid of avenues keyed to its gates, and a county seat's
    streets linked its gates, but a main avenue running from the principal gate to the government office is a
    guess, found on no page read, and in neither Japan nor China was a country lane a wide road. The road at a compound's front gate is the road
    the compound stands on, at that road's width: the great highways ran about 18 to 24 ft wide, and one through a
    castle town about 15 ft.

    Note: the roads here carry carts and wagons, the setting's own departure from Edo Japan, where carts were
    kept to the towns and barred from the highways; the GM's notes put wagons and carts on the roads between
    towns. The road at the gate is drawn at the width of the road the compound stands on, 15 to 24 ft where it is
    a highway, as read; no page read gives the width of the road before an official's gate, so any wider ground
    before the gate is a guess, and so is a lane to a side or cart gate, drawn at about 6 ft where carts use it.
    The record read gives only a south-facing gate for a Chinese county office; that the manor stands at the edge
    of its town and opens its gate onto the road it fronts is this project's own siting, set against the drawn
    maps rather than read from a source.

    Name: road
    Covers: the approach road or town street, the lanes to the lesser doors, and a road across a border
    Label: deviation
    Sources: ctie-michi-nazenaze, hiroshima-saigoku-kaido, mlit-kinsei-michi, kotobank-daihachiguruma, l7r-wagons, neixiang-xianya-zhwiki, song-architecture-enwiki, jokamachi-jawiki, lowtech-chinese-wheelbarrow, toyama-1988-road-undevelopment
    Entry: research/ways.html - 'How wide is the road at a compound's gate?', 'Could a cart use the roads here, and where would it go?', 'What vehicle used a village lane, and where could the lane run?'; research/towns.html - 'Where does a magistrate's manor stand, and which way does its gate face?', 'Chinese towns were PLANNED - the gate-to-yamen axis'
    """

    key = "road"


class CartYard(Kind):
    """
    What: An open loading apron inside a cart gate, where goods carts stand to load and unload beside the
    stores; where those stores hold something that can burn, the same open ground is the fire gap they need.

    Why: In this setting wagons and carts use the roads between towns, so a compound that ships or receives bulk
    goods - rice bales, charcoal - has a cart gate, a cart yard and a lane a cart can use. A compound keeps such
    open ground as a working feature, not as slack. Fresh charcoal absorbs oxygen fast enough to heat itself to
    ignition, so a charcoal store is set apart from the working yard across open ground; the record derives
    about 30 ft as the gap to keep, roughly one flame-height clear of a burning stack.

    Note: carts at a county compound are the setting's own departure from Edo Japan, where carts were kept to the
    towns and barred from the highways to the end of the shogunate, though the hand cart, its bed about 8 by 2.5
    ft, spread through the castle towns and beyond them by late Edo; the GM's notes put wagons and carts on the
    roads between towns. The apron's 15 to 20 ft width is this record's own calibration, which no source read
    states, and the 30 ft gap is this record's own derivation from its own one-flame-height rule of thumb, which no
    page read supports (the published rule, four flame heights, is for people, not timber).

    Name: cart yard
    Covers: the loading apron inside the cart gate
    Label: deviation
    Sources: kotobank-daihachiguruma, mlit-kinsei-michi, l7r-wagons, fao-charcoal-safety, tonya-enwiki
    Entry: research/ways.html - 'Could a cart use the roads here, and where would it go?', 'What vehicle used a village lane, and where could the lane run?'; research/urban-features.html - 'Charcoal yards: a tallied depot, a cooling ground, and a weighing floor'; research/buildings.html - 'Packing: a jin'ya is mostly open'
    """

    key = "cart yard"


# ---- the parts of the grounds (feature 264: a thing drawn inside a feature is its own kind) --------------------


class GardenPond(Kind):
    """
    What: The garden's centerpiece, within sight of the rooms that face it: a small ornamental pond, an open oval
    of water set among the planting - or, where a sheet takes the other form, a dry garden of raked white gravel
    and set stones standing for water. Each map's note says which it draws.

    Why: The formal garden of a samurai house lay beside its reception rooms, to be looked at from them, and
    water - real, or stones and gravel standing for it - is one of the things such a garden was made to hold for
    the eye.

    Note: A residence garden was either a pond garden or a dry garden of stones and white gravel standing for
    water, both attested beside samurai rooms, and each sheet takes one. The two offices whose gardens can be read
    today, Takayama and Okutono, kept pond gardens, but both governed far more than a county, so a pond is the
    grander of the two forms for a small posting. The weight between the forms is a guess. No page read gives
    a residence pond's size: its form and size are a guess, drawn small enough to sit within sight of the rooms
    that face the garden. A pond set on the line from the middle gate to the entrance rests on nothing found and
    is a guess.

    Caveat: The weight between the forms is a guess. No page read gives a residence pond's size: its form and
    size are a guess, drawn small enough to sit within sight of the rooms that face the garden. A pond set on the
    line from the middle gate to the entrance rests on nothing found and is a guess.

    Name: garden pond
    Covers: the pond, or the dry garden, in the inner garden
    Label: accurate
    Sources: kotobank-teien, oniwa-takayama-jinya, okutono-jinya-garden, chiran-bukeyashiki-gardens, shiroishi-koseki
    Entry: research/buildings.html - 'Did a residence garden have a pond, and did a county post keep one?', 'Where is the formal entrance, and how does a guest reach it?'
    """

    key = "garden pond"


class StoneLantern(Kind):
    """
    What: A stone lantern (ishidoro) - stacked stone parts, from the top a jewel, a cap, the fire-box that holds
    the light, a platform, a post and a base - standing in a garden or a receiving court, drawn as a small gray
    glyph.

    Why: The stone lantern came to Japan with Buddhism as a votive light, a single lantern standing at the center
    of the front of a shrine or temple. From the Momoyama period it was set in tea gardens, to light gatherings
    held in the evening, and in ordinary gardens, until it was one of a garden's usual furnishings beside the
    stepping stones and the fences.

    Note: A lantern in a residence garden follows the record. It came in many kinds - the Kasuga, the
    snow-viewing, the Enshu and the Oribe among them - and all are drawn as one small glyph, a drawing
    convention. How many a garden holds, and where, are a guess. A lantern in a court where guests are received
    is a guess, described on no page read and borrowed from the shrine and temple use, so one drawn there
    stands singly on the line of approach.

    Caveat: It came in many kinds - the Kasuga, the snow-viewing, the Enshu and the Oribe among them - and all
    are drawn as one small glyph, a drawing convention. How many a garden holds, and where, are a guess. A
    lantern in a court where guests are received is a guess, described on no page read and borrowed from the
    shrine and temple use, so one drawn there stands singly on the line of approach.

    Name: stone lantern
    Covers: each stone-lantern glyph in a garden or the border court
    Label: accurate
    Sources: kotobank-ishidoro, kotobank-teien
    Entry: research/buildings.html - 'Where did a stone lantern stand - in the garden, or in a court where guests were received?'
    """

    key = "stone lantern"


class GardenPines(Kind):
    """
    What: A cluster of old pines in the inner garden, drawn as three canopies and labeled.

    Why: The Japanese black pine is the lead tree of the Japanese garden, and a garden pine is a tended one, its
    new shoots pinched and thinned twice a year; a pine planted at the foot of the wall so that it shows over it
    is named already in a dictionary of 1603-04. The garden of a long-held posting is old: generations of magistrates laid it
    down, and its trees are the part of it that shows the years.

    Note: Pines in a residence garden follow the record, and so does a pine at the wall showing over it. Their
    crown size is a guess: no page read gives the crown of a pruned garden pine, though left to grow the tree
    reaches 15 to 40 m. The drawn crowns of 4 to 6 ft read as young or closely pruned trees, while a garden kept
    by generations would likely hold older trees with wider crowns; a crown of 15 to 30 ft would be no less a
    guess.

    Caveat: Their crown size is a guess: no page read gives the crown of a pruned garden pine, though left to
    grow the tree reaches 15 to 40 m. The drawn crowns of 4 to 6 ft read as young or closely pruned trees, while
    a garden kept by generations would likely hold older trees with wider crowns; a crown of 15 to 30 ft would be
    no less a guess.

    Name: garden pines
    Covers: the old pines' canopies and their label
    Label: accurate
    Sources: uekipedia-kuromatsu, kotobank-mikoshi-no-matsu
    Entry: research/vegetation.html - 'How big were the pines in a residence garden?'
    """

    key = "garden pines"


class StrikingPosts(Kind):
    """
    What: Standing timbers on the practice ground (tategi), struck hard with a wooden sword in drill - either
    upright posts or a bundle of branches laid across at knee height - drawn as small location markers with
    their label.

    Why: The swordsmanship of Satsuma trains by striking a standing timber from left and right with a shout, over
    and over, on a practice ground that can be open to the sky. In its main line the post is a log a little over
    2 m long set about 70 cm into the ground, so that about 4.5 ft stands above it, struck from shoulder height
    down to the stomach; a branch line strikes a bundle of a dozen or more long thin branches laid at knee
    height. A county seat draws no dojo here, and what marks its swept ground as a place of daily keiko is the
    gear that stands on it.

    Note: we have drawn the striking posts as small markers of where each stands rather than at their own size,
    in order to mark the swept ground as a practice ground by its gear, the GM's convention for these plans; a
    real upright post stood about 4.5 ft, and the bundle lay at knee height. The two forms are both attested and
    each sheet takes one: the upright post as Satsuma practice, the bundle only as a present-day practice whose
    school and region its one source does not name. Carrying either to a practice ground outside those lines is
    a guess, and so is the count.

    Name: striking posts
    Covers: the standing posts on the practice ground and their label
    Label: convention
    Sources: jigen-ryu-jawiki, kotobank-tategi-uchi, nodachi-jigen-ryu, bujutsukarate-tategi, jinya-jawiki, dojo-jawiki
    Entry: research/buildings.html - 'What did a practice ground's striking posts and weapon rack look like?', 'A dojo is a city institution; county training is courtyard keiko'
    """

    key = "striking posts"


class WeaponRack(Kind):
    """
    What: A rack for practice weapons standing at the edge of the practice ground, flush against the wall of the
    building beside it.

    Why: Like the striking posts, the rack is the durable gear that marks open ground as the place where the
    compound's samurai drill every day, in place of a hall built for it. Two real racks lie behind it: the sword
    rack, which holds swords lying level on forked supports, usually in two tiers, and was kept in a guardroom;
    and the long arrest weapons kept at checkpoints and guard posts, which a painting shows stood in a row in the
    open beside a theater's entrance, probably as symbols of order and authority.

    Note: A rack for practice weapons at the edge of a practice ground is described on no page read; it is a
    guess joined from the guardroom's sword rack and the guard post's long weapons, and its size of about 8 by 2
    ft is a guess too. Standing long weapons upright in the open at a post's front is itself a guess, drawn from
    a painting of them standing at a theater's entrance.

    Name: weapon rack
    Covers: the rack at the practice ground's edge and its label
    Label: guess
    Sources: kotobank-katanakake, kotobank-mitsu-dogu
    Entry: research/buildings.html - 'What did a practice ground's striking posts and weapon rack look like?', 'A dojo is a city institution; county training is courtyard keiko'
    """

    key = "weapon rack"


class Nakamon(Kind):
    """
    What: The nakamon - the one narrow household door in the wall between the outer and inner courts, on the main
    axis directly behind the office hall.

    Why: The internal gate between the courts is the hinge between state and home. Official business stops at the
    office hall; the family, its servants and the household's own guests of rank pass this door into the private
    court, and the hall standing in front of it screens that court from the public one.

    Note: The gate between the two courts follows the Chinese record, where the inner residence gate is one
    of Neixiang's five; no Japanese page read gives the front-and-rear order, and at Takayama the residence
    stood beside the office, not behind it. Who passes the gate, and the hall screening the private court,
    are this project's own reading; no page read says either. Its seat on the main axis directly behind the
    office hall is the drawing program's own placement, not a recorded custom, and no source measures the
    household door: its 8 ft width is this project's own figure.

    Caveat: Its seat on the main axis directly behind the office hall is the drawing program's own placement, not
    a recorded custom, and no source measures the household door: its 8 ft width is this project's own figure.

    Name: nakamon
    Covers: the posts of the household door in the court divider
    Label: accurate
    Sources: neixiang-yamen-zhwiki, machi-bugyo-jawiki, yamen-enwiki
    Entry: research/buildings.html - 'Office in front, residence behind - the two-court split is universal'
    """

    key = "nakamon"


class Door(Kind):
    """
    What: A building's own door, drawn as a small block at its wall: the kitchen door (katteguchi) on the
    kitchen's earth floor, the doors of the lodgings and the servants' row, the karo's side door, the heavy doors
    of a plastered storehouse, and the entry of a guest house or a room where visitors are received.

    Why: Every building has a way in. A samurai house had three: the formal entrance for guests, an inner
    entrance for the family and the household to come and go by, and the kitchen door, the one way in from
    outside to the kitchen, by its earth floor, where, on a plan drawn for a fictional house of the period, those of lower status came and went. A guest's arrival
    comes across open ground to its door; a servants' row turns its doors inward, into the compound; and a
    plastered storehouse keeps outer doors faced in earth and plaster so that fire cannot get in.

    Note: The kitchen door, the inward-facing doors of a servants' row, the plastered storehouse doors and a
    guest's door follow the record. A second outside door on a kitchen, and the route by which food reached the
    rooms, are a guess, and a door of a room that the setting or a map's story made is as much the drawing's own
    as its room. A drawn door's width is a drawing convention, not a measurement: the working doors are drawn two
    to three times the width of an ordinary door so that they read at the sheet's scale. A real ordinary door was
    about 3 ft wide (half a ken, this project's reading of how the big door was defined), a farmhouse's one-ken
    main sliding door about 6 ft with a low wicket in it, and each of a storehouse's paired leaves about 3.5 ft.

    Caveat: A second outside door on a kitchen, and the route by which food reached the rooms, are a guess, and a
    door of a room that the setting or a map's story made is as much the drawing's own as its room. A drawn
    door's width is a drawing convention, not a measurement: the working doors are drawn two to three times the
    width of an ordinary door so that they read at the sheet's scale. A real ordinary door was about 3 ft wide
    (half a ken, this project's reading of how the big door was defined), a farmhouse's one-ken main sliding door
    about 6 ft with a low wicket in it, and each of a storehouse's paired leaves about 3.5 ft.

    Name: door
    Covers: every small door glyph on a building's wall
    Label: accurate
    Sources: madoken-odoguchi, hongofuji-koiwai, s-kent-kuratomae, kotobank-katteguchi, kotobank-uchigenkan, matsue-bukeyashiki, homes-jin-bukeyashiki, dozo-jawiki, gogura-jawiki, nagayamon-jawiki, jta-nagayamon
    Entry: research/buildings.html - 'How wide was a real doorway, and how wide are the drawn doors?', 'How many doors does a residence's kitchen have, and who comes in by them?', 'Guest doors feed courts, not flanks', 'Rendering / layout is checked automatically'; research/cities/fabric.html - 'How did a dense wooden city watch for fire?'; research/cities/government.html - 'Servant housing in the samurai ward'
    """

    key = "door"
