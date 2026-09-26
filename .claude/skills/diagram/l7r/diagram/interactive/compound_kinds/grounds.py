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

    Why: Both traditions this setting draws on put the office in front and the residence behind: Chinese
    regulation required it of a county office, and Japanese intendants' offices worked the same way. So
    whoever comes on business - a petitioner, a taxpayer, a prisoner - is dealt with here, near the gate,
    and goes no deeper. Its open ground is not wasted space: a real jin'ya left most of its site open, and
    its forecourt and hearing court were features of the plan in their own right.

    Note: The two-court split and the open forecourt follow the record; no Japanese codification of the
    split was found, and at Takayama the residence stood beside the office rather than behind it. On these
    plans the buildings stand somewhat further apart than in a real jin'ya, which joined its functions into
    a few long connected ranges, so that each reads as its own labeled footprint.

    Caveat: On these plans the buildings stand somewhat further apart than in a real jin'ya, which joined its
    functions into a few long connected ranges, so that each reads as its own labeled footprint.

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

    Note: The two-court split, the household inside the compound and the formal garden south of the
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
    What: A receiving court kept apart from the hearing court: a swept garden court that visitors of rank
    step into when they arrive by a door of their own, before they are shown into the room where they are
    received. On a border posting it is where a delegation from across the border is met.

    Why: Arrival of rank was staged: through a gate, then into a court or garden, then up the formal entrance
    (genkan) - a visitor of rank never stepped from the road straight into a room or against the side of a
    building. So a guests' door opens into a court fit to receive them, and not onto the hearing court where
    the accused kneel.

    Note: A guests' door that opens onto a court is the record's rule. The staged arrival behind it - gate,
    then a court or garden, then the formal entrance - is the record's own reading and the GM's rule for
    these plans; no page a reader can open sets it out. A magistracy that receives delegations from across a
    clan border, and keeps a court for them, is this setting's own, and the record has nothing on it.

    Caveat: The staged arrival behind it - gate, then a court or garden, then the formal entrance - is the
    record's own reading and the GM's rule for these plans; no page a reader can open sets it out. A
    magistracy that receives delegations from across a clan border, and keeps a court for them, is this
    setting's own, and the record has nothing on it.

    Name: border court
    Covers: the receiving court behind a border posting's parley door, and its label
    Label: accurate
    Sources: kotobank-katteguchi
    Entry: research/buildings.html - 'Guest doors feed courts, not flanks'
    """

    key = "border court"


class HearingCourt(Kind):
    """
    What: The oshirasu: the court directly before the office hall's dais where the parties to a case knelt to
    be heard and judged, the magistrate above them on the raised floor. The places where witnesses and the
    accused kneel are marked along its far side.

    Why: The courtroom was a room of the office hall, not a stage of its own: at Takayama, the surviving
    intendant's office, the examination room and the shirasu were one paired feature of the office block, so
    the hearing court lies against the front of the hall where the magistrate sits. With the forecourt it is
    one of the open spaces a jin'ya was built around, a feature of the plan rather than leftover ground. In
    Rokugan, where torture is unusual, a magistracy keeps no room built for interrogation, so questioning
    happens here or in the day office like any other business.

    Note: The oshirasu before the dais follows the record. At Takayama the examination room and the shirasu
    are paved with stone and roofed, where these plans draw an open court of sand.

    Caveat: At Takayama the examination room and the shirasu are paved with stone and roofed, where these
    plans draw an open court of sand.

    Name: hearing court (oshirasu)
    Covers: the sanded court before the dais, its kneeling marks and its label
    Label: accurate
    Sources: takayama-jinya-jawiki, takayama-jinya-city
    Entry: research/buildings.html - 'The courtroom is a room of the office hall, not a freestanding stage', 'No interrogation room', 'Packing: a jin'ya is mostly open'
    """

    key = "hearing court"


class PracticeGround(Kind):
    """
    What: A patch of swept earth in the outer court, with a weapon rack and striking posts: the place where
    the compound's samurai keep up their daily practice.

    Why: A dojo with a resident teacher and enrolled students was an institution of cities, in Japan and
    China alike; rural samurai trained at home in an earthen yard, in a hall cleared for the purpose, or on
    shrine grounds. A county seat holds about fifteen samurai - no student body and no living for a teacher -
    so its magistracy trains on open ground in its own compound, and what marks that ground is the gear
    practice leaves behind, not a building. It is sized to the samurai who drill there, about 90 to 135 sq ft
    each.

    Note: Courtyard keiko in place of a dojo follows the record: a dojo is a city institution. The one page
    read on it lists a drill ground at a small domain's jin'ya, which confirms the practice ground but not
    that a rural intendant's office kept no martial hall; that absence rests on no page read.

    Caveat: The one page read on it lists a drill ground at a small domain's jin'ya, which confirms the
    practice ground but not that a rural intendant's office kept no martial hall; that absence rests on no
    page read.

    Name: practice ground
    Covers: the swept keiko patch, its weapon rack and striking posts, and its label
    Label: accurate
    Sources: hanko-jawiki, edo-three-dojos-jawiki, jinya-jawiki, dojo-jawiki, genbukan-jawiki, kotobank-machidojo
    Entry: research/buildings.html - 'A dojo is a city institution; county training is courtyard keiko'; research/cities/government.html - 'Martial training is an URBAN institution'
    """

    key = "practice ground"


class CompoundGarden(Kind):
    """
    What: The compound's ornamental ground - planting, with stone lanterns and sometimes a pond: the inner
    garden at the heart of the private court and, where a plan has them, a garden around the shrine or one
    kept for guests.

    Why: A samurai house's prized formal garden lay on the sunny south side, facing the reception rooms, and
    a plan seats its inner garden there where its buildings allow. A guest of rank was received through a
    staged arrival - gate, then a court or garden, then the formal entrance - which is why a guests' door
    opens into a garden rather than against a building.

    Note: The inner court's garden, as a zone, and the formal garden south of the reception rooms follow the
    record. The garden a guest steps into rests on the staged arrival, which is the record's own reading and
    the GM's rule for these plans; no page a reader can open sets it out. The record says nothing of a garden
    around a compound's shrine; one drawn there rests on the inner garden's reasoning.

    Caveat: The garden a guest steps into rests on the staged arrival, which is the record's own reading and
    the GM's rule for these plans; no page a reader can open sets it out. The record says nothing of a garden
    around a compound's shrine; one drawn there rests on the inner garden's reasoning.

    Name: garden
    Covers: the inner garden, a shrine garden and a guest garden, with their lanterns, ponds and labels
    Label: accurate
    Sources: shoinzukuri-jawiki, kotobank-katteguchi
    Entry: research/buildings.html - 'The shady rear is the service strip', 'Guest doors feed courts, not flanks'
    """

    key = "garden"


class VegetableGarden(Kind):
    """
    What: A kitchen bed of greens for the household's own table - daikon, onions, beans, herbs - worked in the
    service ground behind the residence.

    Why: A household's saien was the small intensive bed that fed it its daily greens and nothing beyond them;
    bulk vegetables and dry crops grew out in the fields. The prized formal garden took the sunny south side
    of a samurai house, so its kitchen garden lay in the back, in the shady strip where the household's
    service economy went.

    Note: The kitchen bed as a thing follows the record. Its seat in the shady north rear is this record's own
    reasoning from where the formal garden sat, with no source that describes it, and no readable source
    gives a kitchen bed's size.

    Caveat: Its seat in the shady north rear is this record's own reasoning from where the formal garden sat,
    with no source that describes it, and no readable source gives a kitchen bed's size.

    Name: vegetable garden
    Covers: the kitchen garden's beds and label
    Label: accurate
    Sources: shoinzukuri-jawiki, hatake-jawiki, kateisaien-jawiki, shakkanho-jawiki
    Entry: research/buildings.html - 'The shady rear is the service strip'; research/homesteads.html - 'How big was a dooryard garden?'
    """

    key = "vegetable garden"


class ShrineGrove(Kind):
    """
    What: A stand of kept trees around the compound's shrine, its hall and arch set in a cleared opening among
    them: the shrine's own sacred wood.

    Why: A Japanese shrine's setting was a deliberately preserved grove, the chinju no mori - a wood kept and
    tended around the sanctuary, the approach and the place of worship, so that the swept precinct sits inside
    kept trees rather than in cleared ground. The tutelary shrine stands in its grove, and the grove
    surrounds the precinct.

    Note: The grove as the setting of a shrine follows the record. Everything the record holds is about a
    village shrine standing in its own wood; nothing covers a grove kept inside a compound wall.

    Caveat: Everything the record holds is about a village shrine standing in its own wood; nothing covers a
    grove kept inside a compound wall.

    Name: shrine grove (chinju no mori)
    Covers: the grove's ground and its tree canopies
    Label: accurate
    Sources: chinju-no-mori-jawiki, fengshui-woodland-enwiki, jinja-jawiki
    Entry: research/religion-and-death.html - 'Is the ground around a shrine or a grave swept clear of scrub?', 'Where does a village put its shrine, and how big is it?', 'How big is a country shrine, and what stands in its precinct?'
    """

    key = "shrine grove"


class CompoundWall(Kind):
    """
    What: The heavy wall around the whole compound: earth over a post core on a stone footing, under its own
    tiled coping, broken only at the gates. Buildings back onto it, but none stands in it.

    Why: A walled enclosure is the grammar every administrative compound shares, Japanese or Chinese. A wall
    of this class is a building in its own right - thick enough to stop a determined man and to carry the
    tiles that keep its earth core dry - so the ground under it is occupied, and the buildings ringing a
    court back onto it with their eaves nearly touching, a foot or two off so that the wall stays reachable
    for patching.

    Note: we have drawn the compound wall 3 ft thick, thicker than the typical wall, in order to make its
    stroke read on the plan; the real form it resembles is the rammed-earth tsuijibei, up to about 1 m (3.3
    ft) thick, while the ordinary plastered neribei was about 1 shaku, some 30 cm.

    Name: compound wall
    Covers: the outer wall's strokes
    Label: convention
    Sources: hei-jokaku-jawiki, kojodan-dobei, tsuijibei-jawiki
    Entry: research/buildings.html - 'A compound wall is a building, not a boundary line', 'Administrative culture is JAPAN-first for compound interiors'
    """

    key = "compound wall"


class MainGate(Kind):
    """
    What: The compound's formal entrance: a single opening in the front wall between heavy posts, with the
    gatehouse just inside beside it and the forecourt beyond. It is the widest of the compound's doors, and
    the one meant for visitors on business.

    Why: A magistrate's manor faces what it fronts - the town it governs or the road it stands beside - and
    its gate opens onto that way; where nothing else decides it, the gate faces south, the formal orientation
    a Chinese county office took by regulation. Behind it, arrival is staged: the gate, then the forecourt,
    and only then the buildings, so no visitor steps from the road into a room.

    Note: The gate and the way it faces follow the record. The staged arrival behind it - gate, then a court
    or garden, then the formal entrance - is the record's own reading and the GM's rule for these plans; no
    page a reader can open sets it out. The width of its opening is this project's own calibration rather
    than a measured gate: the record finds no width for a samurai residence's gate or a county office's.

    Caveat: The staged arrival behind it - gate, then a court or garden, then the formal entrance - is the
    record's own reading and the GM's rule for these plans; no page a reader can open sets it out. The width
    of its opening is this project's own calibration rather than a measured gate: the record finds no width
    for a samurai residence's gate or a county office's.

    Name: main gate
    Covers: the posts flanking the main opening
    Label: accurate
    Sources: neixiang-xianya-zhwiki, kotobank-katteguchi
    Entry: research/towns.html - 'Where does a magistrate's manor stand, and which way does its gate face?'; research/religion-and-death.html - 'How large are the gates, walls and funerary features drawn?'; research/buildings.html - 'Guest doors feed courts, not flanks'
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
    opens into a court or garden.

    Note: The service doors and the cart access they give follow the record. That a night-soil collector
    never has to cross the inner court is this record's own rule rather than a finding.

    Caveat: That a night-soil collector never has to cross the inner court is this record's own rule rather
    than a finding.

    Name: side gate
    Covers: the posts of the posterns, service gates, landing gate and guests' door
    Label: accurate
    Sources: kotobank-katteguchi, tajima-2007-night-soil, guernica-night-soil, kotobank-benjo
    Entry: research/buildings.html - 'Guest doors feed courts, not flanks', 'Privies attach to the house; night-soil drives their placement'
    """

    key = "side gate"


class CourtDivider(Kind):
    """
    What: The lighter wall that splits the compound into its outer and inner courts, with one narrow
    household door in it, the nakamon, which the plan places on the main axis directly behind the office
    hall.

    Why: The internal gate between the courts is the hinge between state and home. Formal visitors are
    received in the office hall and go no deeper; the household door serves the family and its servants, and
    the hall standing in front of it screens the private court from the public one.

    Note: The internal wall and its gate between the two courts follow the record. The door's seat on the
    main axis directly behind the office hall is the drawing program's own placement, not a recorded custom,
    and no source measures the household door or the divider: the door's 8 ft width and the wall's 2 ft
    thickness are this project's own figures.

    Caveat: The door's seat on the main axis directly behind the office hall is the drawing program's own
    placement, not a recorded custom, and no source measures the household door or the divider: the door's
    8 ft width and the wall's 2 ft thickness are this project's own figures.

    Name: court divider and nakamon
    Covers: the internal wall's strokes and its household gate posts
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
    the main gate. In a planned Chinese town a main avenue ran from the principal gate to the government
    office, though for an ordinary county seat that axis is a guess, and in neither Japan nor China was a
    country lane a wide road.

    Note: That the manor fronts its road and opens its gate onto it follows the record. The width each way is
    drawn at is this project's own choice - the road up to the main gate as wide as the gate's opening -
    since the record gives no width for a road up to a compound.

    Caveat: The width each way is drawn at is this project's own choice - the road up to the main gate as wide
    as the gate's opening - since the record gives no width for a road up to a compound.

    Name: road
    Covers: the approach road or town street, the lanes to the lesser doors, and a road across a border
    Label: accurate
    Sources: neixiang-xianya-zhwiki, song-architecture-enwiki, jokamachi-jawiki, lowtech-chinese-wheelbarrow, toyama-1988-road-undevelopment
    Entry: research/towns.html - 'Where does a magistrate's manor stand, and which way does its gate face?', 'Chinese towns were PLANNED - the gate-to-yamen axis'; research/ways.html - 'What vehicle used a village lane, and where could the lane run?'
    """

    key = "road"


class CartYard(Kind):
    """
    What: An open loading apron inside a cart gate, where goods carts stand to load and unload beside the
    stores; where those stores hold something that can burn, the same open ground is the fire gap they need.

    Why: A loading apron for carts and draft animals runs about 15 to 20 ft, and a compound keeps such open
    ground as a working feature, not as slack. Fresh charcoal absorbs oxygen fast enough to heat itself to
    ignition, so a charcoal store is set apart from the working yard across open ground; the record derives
    about 30 ft as the gap to keep, roughly one flame-height clear of a burning stack.

    Note: The apron and the separation it performs follow the record. The 30 ft gap is this record's own
    derivation, and no entry squares carts at a county compound with what the record finds on them: carts
    confined to city streets in Japan and forbidden on its highways, and a Chinese countryside built for the
    wheelbarrow.

    Caveat: The 30 ft gap is this record's own derivation, and no entry squares carts at a county compound with
    what the record finds on them: carts confined to city streets in Japan and forbidden on its highways, and a
    Chinese countryside built for the wheelbarrow.

    Name: cart yard
    Covers: the loading apron inside the cart gate
    Label: accurate
    Sources: fao-charcoal-safety, tonya-enwiki, daihachiguruma-jawiki, toyama-1988-road-undevelopment, lowtech-chinese-wheelbarrow
    Entry: research/urban-features.html - 'Charcoal yards: a tallied depot, a cooling ground, and a weighing floor'; research/buildings.html - 'Packing: a jin'ya is mostly open'; research/ways.html - 'What vehicle used a village lane, and where could the lane run?'
    """

    key = "cart yard"
