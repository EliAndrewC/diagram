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
    What: A receiving court kept apart from the hearing court: a swept garden court that visitors of rank
    step into when they arrive by a door of their own, before they are shown into the room where they are
    received. On a border posting it is where a delegation from across the border is met.

    Why: Arrival of rank was staged: through a gate, then into a court or garden, then up the formal entrance
    (genkan) - a visitor of rank never stepped from the road straight into a room or against the side of a
    building. So a guests' door opens into a court fit to receive them, and not onto the hearing court where
    the accused kneel.

    Note: A guests' door that opens onto a court is the GM's rule for these plans; the one source cited defines
    the kitchen door, and says nothing of what a guests' door opens onto. The staged arrival behind it - gate,
    then a court or garden, then the formal entrance - is the record's own reading and the GM's rule for
    these plans; no page a reader can open sets it out. A magistracy that receives delegations from across a
    clan border, and keeps a court for them, is this setting's own, and the record has nothing on it.

    Caveat: A guests' door that opens onto a court is the GM's rule for these plans; the one source cited
    defines the kitchen door, and says nothing of what a guests' door opens onto. The staged arrival behind
    it - gate, then a court or garden, then the formal entrance - is the record's own reading and the GM's rule
    for these plans; no page a reader can open sets it out. A magistracy that receives delegations from across
    a clan border, and keeps a court for them, is this setting's own, and the record has nothing on it.

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
    be heard and judged, the magistrate above them on the raised floor.

    Why: The courtroom was a room of the office hall, not a stage of its own: at Takayama, the surviving
    intendant's office, the examination room and the shirasu were one paired feature of the office block, so
    the hearing court lies against the front of the hall where the magistrate sits. With the forecourt it is
    one of the open spaces a jin'ya was built around, a feature of the plan rather than leftover ground. In
    Rokugan, where torture is unusual, a magistracy keeps no room built for interrogation, so questioning
    happens here or in the day office like any other business.

    Note: The oshirasu before the dais follows the record; that a jin'ya was laid out around it and the
    forecourt as open features is this project's reading of plans, which no readable source measures. At
    Takayama the examination room and the shirasu are paved with stone and roofed, where these plans draw
    an open court of sand.

    Caveat: At Takayama the examination room and the shirasu are paved with stone and roofed, where these
    plans draw an open court of sand.

    Name: hearing court (oshirasu)
    Covers: the sanded court before the dais and its label
    Label: accurate
    Sources: takayama-jinya-jawiki, takayama-jinya-city
    Entry: research/buildings.html - 'The courtroom is a room of the office hall, not a freestanding stage', 'No interrogation room', 'Packing: a jin'ya is mostly open'
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
    schools stood in castle towns and cities, that rural samurai trained in yards, cleared halls or on shrine
    grounds, and that a Chinese county yamen had no training hall are guesses no page read confirms. That a
    rural intendant's office kept no martial hall is a guess from the silence of the pages read on one, which
    list its buildings without one but never say it had none.

    Caveat: That domain schools stood in castle towns and cities, that rural samurai trained in yards,
    cleared halls or on shrine grounds, and that a Chinese county yamen had no training hall are guesses no
    page read confirms. That a rural intendant's office kept no martial hall is a guess from the silence of
    the pages read on one, which list its buildings without one but never say it had none.

    Name: practice ground
    Covers: the swept keiko patch and its label
    Label: accurate
    Sources: hanko-jawiki, edo-three-dojos-jawiki, jinya-jawiki, dojo-jawiki, genbukan-jawiki, kotobank-machidojo
    Entry: research/buildings.html - 'A dojo is a city institution; county training is courtyard keiko'; research/cities/government.html - 'Martial training is an URBAN institution'
    """

    key = "practice ground"


class CompoundGarden(Kind):
    """
    What: The compound's ornamental ground - planting, laid out to be looked at: the inner garden at the heart of
    the private court and, where a plan has them, a garden around the shrine or one kept for guests.

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
    Covers: the inner garden, a shrine garden and a guest garden, and their labels
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
    What: The heavy wall around the whole compound: earth over a post core on a stone footing, under its own
    tiled coping, broken only at the gates. Buildings back onto it, but none stands in it.

    Why: A walled enclosure is the grammar every administrative compound shares, Japanese or Chinese. A wall
    of this class is a building in its own right - thick enough to stop missiles and to carry the
    tiles that keep its earth core dry - so the ground under it is occupied, and the buildings ringing a
    court back onto it with their eaves nearly touching, a foot or two off so that the wall stays reachable
    for patching.

    Note: we have drawn the compound wall 3 ft thick, thicker than the typical wall, in order to make its
    stroke read on the plan; the real form it resembles is the rammed-earth tsuijibei, up to about 1 m (3.3
    ft) thick, while the ordinary plastered neribei was about 1 shaku, some 30 cm - figures read for castle
    walls, since a county compound's own wall thickness is unsourced. How near the buildings stand to the
    wall, eaves nearly touching and a foot or two off, is our own reasoning; no source we found describes it.

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

    Note: The gate's southern fallback follows the record - a Chinese county office's regulation, not
    Japanese practice. Facing what it fronts, the town or the road, is this project's own siting, calibrated
    against the drawn maps; only the southern fallback rests on a source, and that one is Chinese. The staged
    arrival behind it - gate, then a court or garden, then the formal entrance - is the record's own reading
    and the GM's rule for these plans; no page a reader can open sets it out. The width of its opening is this
    project's own calibration rather than a measured gate: the record finds no width for a samurai
    residence's gate or a county office's.

    Caveat: Facing what it fronts, the town or the road, is this project's own siting, calibrated against
    the drawn maps; only the southern fallback rests on a source, and that one is Chinese. The staged arrival
    behind it - gate, then a court or garden, then the formal entrance - is the record's own reading and the
    GM's rule for these plans; no page a reader can open sets it out. The width of its opening is this
    project's own calibration rather than a measured gate: the record finds no width for a samurai
    residence's gate or a county office's.

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

    Note: The service doors and the cart access they give follow the record, though the dictionary names
    only the kitchen door and that it opens into work space is this record's reading. That a guests' door
    opens into a court or garden is the GM's rule: no readable source sets out the staged arrival behind
    it. That a night-soil collector never has to cross the inner court is this record's own rule rather
    than a finding.

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
    guess, found on no page read, and in neither Japan nor China was a country lane a wide road.

    Note: The record read gives only a south-facing gate for a Chinese county office. That the manor stands at
    the edge of its town and opens its gate onto the road it fronts is this project's own siting, set against
    the drawn maps rather than read from a source. The width each way is drawn at is this project's own
    choice - the road up to the main gate as wide as the gate's opening - since the record gives no width for
    a road up to a compound.

    Caveat: That the manor stands at the edge of its town and opens its gate onto the road it fronts is this
    project's own siting, set against the drawn maps rather than read from a source. The width each way is
    drawn at is this project's own choice - the road up to the main gate as wide as the gate's opening - since
    the record gives no width for a road up to a compound.

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

    Note: That a compound keeps the apron, and the separation it performs, follows the record. The apron's 15
    to 20 ft width is this record's own calibration, which no source read states. The 30 ft gap is this
    record's own derivation from its own one-flame-height rule of thumb, which no page read supports (the
    published rule, four flame heights, is for people, not timber), and no entry squares carts at a county
    compound with what the record finds on them: carts confined to city streets in Japan and forbidden on its
    highways, and a Chinese countryside built for the wheelbarrow.

    Caveat: The apron's 15 to 20 ft width is this record's own calibration, which no source read states. The
    30 ft gap is this record's own derivation from its own one-flame-height rule of thumb, which no page read
    supports (the published rule, four flame heights, is for people, not timber), and no entry squares carts
    at a county compound with what the record finds on them: carts confined to city streets in Japan and
    forbidden on its highways, and a Chinese countryside built for the wheelbarrow.

    Name: cart yard
    Covers: the loading apron inside the cart gate
    Label: accurate
    Sources: fao-charcoal-safety, tonya-enwiki, daihachiguruma-jawiki, toyama-1988-road-undevelopment, lowtech-chinese-wheelbarrow
    Entry: research/urban-features.html - 'Charcoal yards: a tallied depot, a cooling ground, and a weighing floor'; research/buildings.html - 'Packing: a jin'ya is mostly open'; research/ways.html - 'What vehicle used a village lane, and where could the lane run?'
    """

    key = "cart yard"


# ---- the parts of the grounds (feature 264: a thing drawn inside a feature is its own kind) --------------------


class GardenPond(Kind):
    """
    What: A small ornamental pond in the inner garden, drawn as an open oval of water set among the planting,
    within sight of the rooms that face the garden.

    Why: The formal garden of a samurai house lay south of the reception rooms, to be looked at from them, and
    water is one of the things such a garden was made to hold for the eye.

    Note: the research record has no entry on a pond in a residence garden, so whether a county post's garden kept
    one, and the pond's form and size, are a guess; the garden it lies in follows the record.

    Name: garden pond
    Covers: the pond in the inner garden
    Label: guess
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "garden pond"


class StoneLantern(Kind):
    """
    What: A stone lantern - a squat lamp-house on a short post - standing in a garden or a receiving court, drawn
    as a small gray glyph.

    Why: A lantern marks a garden or a court as a made place, meant to be walked and looked at rather than
    merely crossed.

    Note: the research record has no entry on stone lanterns in a residence garden or a receiving court, so their
    form, their count and their places are a guess.

    Name: stone lantern
    Covers: each stone-lantern glyph in a garden or the border court
    Label: guess
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "stone lantern"


class GardenPines(Kind):
    """
    What: A cluster of old pines in the inner garden, drawn as three canopies and labeled.

    Why: The garden of a long-held posting is old: generations of magistrates laid it down, and its trees are the
    part of it that shows the years.

    Note: the research record has no entry on pines in a residence garden; the trees are this map's story of a
    garden kept by many magistrates in turn, and their kind and size are a guess.

    Name: garden pines
    Covers: the old pines' canopies and their label
    Label: guess
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "garden pines"


class StrikingPosts(Kind):
    """
    What: Short standing posts on the practice ground (tategi), struck with a wooden sword in drill, drawn as small
    location markers with their label.

    Why: A county seat draws no dojo here (the offices read list no martial hall, though none says there was
    none), and this map guesses that what marks its swept ground as a place of daily keiko is the gear that
    stands on it.

    Note: we have drawn the striking posts as small markers of where each stands rather than at its own size, in
    order to mark the swept ground as a practice ground by its gear, the GM's convention for these plans
    (2026-07-24); the posts' real form, height and count were not found. No source read speaks of rural practice or
    its gear, that county samurai kept training on open ground is a guess, and only a small domain's jin'ya is
    read to have kept a drill ground.

    Name: striking posts
    Covers: the standing posts on the practice ground and their label
    Label: convention
    Sources: hanko-jawiki, edo-three-dojos-jawiki, jinya-jawiki, dojo-jawiki
    Entry: research/buildings.html - 'A dojo is a city institution; county training is courtyard keiko'
    """

    key = "striking posts"


class WeaponRack(Kind):
    """
    What: A rack for practice weapons standing at the edge of the practice ground, flush against the wall of the
    building beside it.

    Why: Like the striking posts, the rack is the durable gear that marks open ground as the place where the
    compound's samurai drill every day, in place of a hall built for it.

    Note: Practice on open ground rather than in a hall is read only for the time before the mid-Edo period and
    in a small domain's drill ground; that a county magistracy's samurai still drilled that way is our guess,
    resting on the setting's own numbers; marking it with gear such as this rack is the map's own convention,
    since no source read describes rural practice gear. The rack's form and its size of about 8 by 2 ft are
    not in the record.

    Name: weapon rack
    Covers: the rack at the practice ground's edge and its label
    Label: guess
    Sources: hanko-jawiki, edo-three-dojos-jawiki, jinya-jawiki, dojo-jawiki
    Entry: research/buildings.html - 'A dojo is a city institution; county training is courtyard keiko'
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
    What: A building's own door, drawn as a small block at its wall: the family's kitchen-side door
    (katteguchi), the doors of the lodgings and the servants' row, the karo's side door, the heavy doors of a
    plastered storehouse, and the entry of a guest house or a room where visitors are received.

    Why: Every building has a way in. The household's working doors open onto work space, the deliberate opposite
    of a guest's arrival, which comes across a court or garden to its door; a servants' row turns its doors
    inward, into the compound; and a plastered storehouse keeps outer doors faced in earth and plaster so that
    fire cannot get in.

    Note: The kitchen-side door, the inward-facing doors of a servants' row, the plastered storehouse doors and a
    guest's door follow the record; that the guest's door opens off a court rather than against a building's flank
    is the GM's rule, the staged arrival behind it (gate, then court or garden, then the entrance) is this
    project's reading that no source a reader can check sets out, and that the kitchen door opens onto work space
    is likewise the map's own. No source gives a drawn door's width, and a door of a
    room that the setting or a map's story made is as much the drawing's own as its room.

    Caveat: No source gives a drawn door's width, and a door of a room that the setting or a map's story made is
    as much the drawing's own as its room.

    Name: door
    Covers: every small door glyph on a building's wall
    Label: accurate
    Sources: kotobank-katteguchi, dozo-jawiki, gogura-jawiki, nagayamon-jawiki, jta-nagayamon
    Entry: research/buildings.html - 'Guest doors feed courts, not flanks', 'Rendering / layout is checked automatically'; research/cities/fabric.html - 'How did a dense wooden city watch for fire?'; research/cities/government.html - 'Servant housing in the samurai ward'
    """

    key = "door"
