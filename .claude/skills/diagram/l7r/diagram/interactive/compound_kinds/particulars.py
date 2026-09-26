"""The particulars: things a compound plan draws because of its place in the setting or its map's story (feature 262).

Ochiba's Fox wardings (the threshold stones and their buried Pact-Bowl, the Fox-Fire Lantern, the cinnabar
workshop, the fox relics), Hayakawa's river, landing and salt wards, and Ubame's Fox border, parley room,
boundary stones, charcoal store and wood-kami altar. A kind the SETTING makes - with no historical counterpart
the record covers - is `deviation`, written from the GM's canon (`/host-l7r-repo/setting/l7r.md`, which needs no
citation, so `Sources: not recorded`) and the map's design notes. A kind the record DOES cover (the river, the
landing, the drawn border line, the charcoal store) keeps the record's classification, and what its one map
adds is in that map's `.notes.md` "Map notes" block. A kind neither the record nor the canon covers (the salt
wards) is a `guess`. The measurement behind every label is `specs/262-interactive-magistracy-pages/coverage.md`.
"""

from __future__ import annotations

from ..classes import Kind


class ThresholdStones(Kind):
    """
    What: A pair of river-stones painted with cinnabar fox-tracks, set one on each side of the road just outside
    the main gate, with a Pact-Bowl buried beneath: a small lacquer bowl holding rice, three copper coins and a
    tuft of fox fur, renewed every seventh year in a ceremony attended by the magistrate and an emissary of
    the Fox.

    Why: They are part of the Fox Clan's warding of the Emperor's road. Threshold stones stand along every
    stretch of Imperial road in or beside Fox lands, and a Pact-Bowl lies beneath the stone at each County
    Magistrate's checkpoint adjoining those lands: a traveler who passes the threshold has, by Fox reckoning,
    accepted the wood's hospitality, and one who then preys on another traveler owes the wood a debt. The
    stones flank the road rather than stand in it, because a threshold stone stands above ground - something
    to walk between, not to roll a cart over.

    Note: the threshold stones and the Pact-Bowl are the Fox Clan's road wardings, from the campaign's own
    canon, a departure made by the setting with no historical counterpart. Canon sets one stone at each
    checkpoint; the flanking pair is the GM's ruling for this drawing, a stone on each side of the road so
    that neither stands in it. And the pair is drawn larger than canon's stones on purpose - canon makes each
    stone a river-stone the size of two fists, and Ochiba's pair stands about 3.3 by 4.7 ft, because Ochiba is
    where the threshold stones are made and painted (the GM's ruling).

    Name: threshold stones
    Covers: the vermilion pair outside the main gate and their label with the "buried Pact-Bowl" sublabel
    Label: deviation
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "threshold stones"


class FoxFireLantern(Kind):
    """
    What: The Fox-Fire Lantern, a small stone lantern kept at the compound's Inari shrine by day and carried
    to the magistrate's bench when a grain-tax hearing is held in the evening - drawn at both of its places.

    Why: It is a votive offering to Inari: a small lantern of gray granite, carved by a stonemason once
    falsely accused of shorting his village's tax grain, and given to the County Magistrate so that it would
    burn at grain-tax hearings. Its flame is said to flicker blue when a witness conceals the truth about a
    harvest. It belongs to the compound's shrine and to its bench at once, which is why the plan marks it
    twice: at rest at the shrine, and in the hearing court, where an evening hearing brings it.

    Note: the lantern is one of the relics of the setting's own record, which describes it; it has no
    historical counterpart, and the research record holds nothing like it, so it is a departure made by the
    setting.

    Name: fox-fire lantern
    Covers: the lantern's sublabel at the rice altar and the note in the hearing court
    Label: deviation
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "fox-fire lantern"


class CinnabarWorkshop(Kind):
    """
    What: An open-sided covered colonnade against the shrine where the threshold stones are painted with their
    cinnabar fox-tracks, with river-stones laid out in it.

    Why: The stones of the Fox road wardings are painted with cinnabar, and the painting is sacred work: the
    setting's record has the magistrate paint each newly dressed stone by their own hand, in daylight, at the
    colonnade off the shrine's eastern altar - which is why the workshop adjoins the shrine hall rather than
    standing in the service yard.

    Note: the painted threshold stones and the colonnade where they are painted belong to the setting's own
    canon and record, a departure made by the setting with no historical counterpart in the research record.

    Name: cinnabar workshop
    Covers: the hatched colonnade, its posts, the drying river-stones and its label
    Label: deviation
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "cinnabar workshop"


class FoxRelics(Kind):
    """
    What: Two relics of the Fox, the Akami-fude and the Chigiri-no-Chou, kept with the warding materials at the
    fox altar of the compound's Inari hall.

    Why: They pass with the office rather than the family - the magistrate who holds the post keeps them, with
    the duty of the road wardings - so they rest in the compound's own shrine, at the altar of the fox, beside
    the work of the wardings.

    Note: the Akami-fude is the setting's own relic - the brush that paints the fox-tracks on each threshold
    stone, kept on its own stand at the shrine's eastern, fox altar - and the Chigiri-no-Chou is this map's
    own name, found in no setting file. Neither has a historical counterpart, and the research record holds
    nothing like them, so both are a departure made by the setting and this map.

    Name: fox relics
    Covers: the fox-altar sublabel and the relics annotation below the workshop
    Label: deviation
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "fox relics"


class SaltWards(Kind):
    """
    What: Small heaps of salt set in a pair outside a door of the compound, one on each side of the opening,
    to keep ill fortune from crossing the threshold.

    Why: A ward works from outside, so the pair flanks each opening on its outer face rather than standing
    inside the wall, and every door so warded carries its own pair - the gates, the posterns and the river
    door alike.

    Note: the small cone of salt set out at a doorway has a Japanese name, morijio, but the research record
    has no entry on salt wards, so the form, the pairing at each door and the placement outside are a guess,
    and each heap is drawn as a marker far larger than a real cone of salt a few inches across.

    Name: salt wards
    Covers: every salt-ward marker at the doors, the "salt wards" label and the salt-wards note box
    Label: guess
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "salt wards"


class River(Kind):
    """
    What: A navigable river running beside the compound - the county's road to the rest of the world for its
    heavy goods.

    Why: Where navigable natural water exists, it is the main freight route, and a county on it is a staging
    node: its tax grain moves on by boat toward the central stores rather than sitting in rows of granaries
    at the office. In this setting only the Lion dig transport canals, so for any other county the river is
    the way.

    Note: Freight by water and the staging granary of a well-watered county are recorded findings; the rule that
    only the Lion build canals is the setting's canon. That Japan's heavy freight also went by water rests on
    general reading rather than a page a reader can open.

    Caveat: That Japan's heavy freight also went by water rests on general reading rather than a page a reader
    can open.

    Name: river
    Covers: the river band and its labels
    Label: accurate
    Sources: gokura-jawiki, nishimawari-koro-jawiki, takayama-jinya-city, takayama-jinya-jawiki, chinaknowledge-caoyun, daba-jawiki, chuma-jawiki
    Entry: research/buildings.html - 'The granary is a staging node, not the terminal store'; research/ways.html - "Where does a village's freight go?"
    """

    key = "river"


class RiverLanding(Kind):
    """
    What: The compound's landing on the river: a dock springing from a stone-faced bank, the tax barge moored
    alongside it, a watch post over the water and a small altar for the boatmen.

    Why: Tax grain went downstream on hired commoners' boats under the office's seals - the magistracy owned no
    hulls, and its hold on the cargo was documentary. A river's level moves by many feet through the year, so
    a working bank was faced with stone and a landing stage ran out from it about a boat-length, to reach
    water deep enough for a loaded hull; a river barge of the period ran from about 30 to 73 ft.

    Note: The hired barge under seal, the stone-faced bank, the boat-length landing stage and the barge's size
    are recorded findings. The river watch and the boatmen's altar are this map's own story, with no entry in
    the record.

    Caveat: The river watch and the boatmen's altar are this map's own story, with no entry in the record.

    Name: river landing
    Covers: the dock, the revetment, the moored tax barge, the river-watch post, the boatmen's altar and the landing label
    Label: accurate
    Sources: nishimawari-koro-jawiki, kashi-jawiki, gangi-kowan-jawiki, takasebune-jawiki, kotobank-takasebune, matou-zhwiki, kuramae-jawiki, chinaknowledge-caoyun
    Entry: research/buildings.html - 'The granary is a staging node, not the terminal store'; research/cities/river-cities.html - "The wharf's working face"; research/cities/capitals.html - "The sluice's lifting frame"; research/ways.html - "Where does a village's freight go?"
    """

    key = "river landing"


class FoxBorder(Kind):
    """
    What: The border between the Fox Clan's lands and a neighboring clan's, drawn as a dashed line with no
    width, running off the sheet at both ends.

    Why: Agreed, marked borders between domains were real: two neighboring domains settled a boundary of about
    130 km in 1642 after half a century of dispute and marked it with a line of earth mounds, and every
    province's map drew its boundaries plainly. A border exists where two authorities have agreed it, so the
    plan draws the agreed line itself, which nothing on the ground need stand clear of.

    Note: The agreed, drawn border line is a recorded finding. The period's large border markers were earthen
    mounds, and the plan draws the line alone; a compound standing on the line is its map's story.

    Caveat: The period's large border markers were earthen mounds, and the plan draws the line alone; a compound
    standing on the line is its map's story.

    Name: fox border
    Covers: the border line, its labels and the border note box
    Label: accurate
    Sources: nanbu-date-mounds-enwiki, kuniezu-enwiki, kotobank-genroku-kuniezu, mukoyama-linear-borders
    Entry: research/urban-features.html - 'Drawing a clan border'
    """

    key = "fox border"


class ParleyRoom(Kind):
    """
    What: A room built into the compound's border wall with a door on each face, the border running across its
    floor, and two pairs of kneeling mats facing each other across the line.

    Why: Each party kneels on its own soil, so the two sides can meet and settle their business without either
    stepping onto the other's ground. Its inner door opens into a receiving court, never into the court where
    the accused kneel, because the room receives guests.

    Note: a room built across a clan border is part of its map's story, a departure made by the map's design
    with no historical evidence for one in the record. The drawn border line it stands on is the
    attested part; the record calls the room the architectural counterpart of that line, by analogy only.

    Name: parley room
    Covers: the room in the border wall, its doors, its kneeling mats and its label
    Label: deviation
    Sources: not recorded
    Entry: research/urban-features.html - 'Drawing a clan border'
    """

    key = "parley room"


class BoundaryStones(Kind):
    """
    What: Stone pillars set on a border line, one on each side of the crossing, drawn stone-gray - a pair that
    marks the line rather than wards it.

    Why: Boundary markers were common under the Tokugawa, and a border exists where it has been agreed and
    marked; the pillars stand ON the line, north and south of the crossing, so that the line itself can be
    read on the ground.

    Note: we have drawn the boundary stones at about 3 by 3.7 ft, in order to mark where each stands on the
    line. The record estimates a boundary pillar's shaft at about 1 to 1.5 ft, up to about 3 ft with a plinth -
    an estimate rather than a read figure - and the period's large border markers were earthen mounds, which
    are not what is drawn.

    Name: boundary stones
    Covers: the two border pillars and their label
    Label: convention
    Sources: nanbu-date-mounds-enwiki, kuniezu-enwiki, kotobank-genroku-kuniezu, mukoyama-linear-borders
    Entry: research/urban-features.html - 'Drawing a clan border'
    """

    key = "boundary stones"


class CharcoalStore(Kind):
    """
    What: A sealed storehouse for charcoal - a kura with thick plastered earthen walls - set apart from the
    working yard, where the charcoal a county takes in is held under the office's seal.

    Why: Charcoal was an industrial fuel moved at state scale, and a store of it was a supervised, tallied depot
    rather than a back room. Fire-resistant stores had thick plastered walls because timber cities burned, and
    fresh charcoal heats itself to ignition when packed, so the store stands apart from the yard and the other
    buildings with open ground between.

    Note: The supervised, tallied depot, the plastered fire-resistant store and the self-heating of fresh
    charcoal are recorded findings. How far the store should stand apart is this record's own derivation rather
    than a read figure.

    Caveat: How far the store should stand apart is this record's own derivation rather than a read figure.

    Name: charcoal store
    Covers: the sealed charcoal kura and its labels
    Label: accurate
    Sources: wagner-ming-iron, fao-charcoal-safety, tonya-enwiki, fires-in-edo-enwiki, economy-song-enwiki
    Entry: research/urban-features.html - 'Charcoal yards: a tallied depot'
    """

    key = "charcoal store"


class WoodKamiAltar(Kind):
    """
    What: A small altar to the kami of the wood, no bigger than a shed, with no torii before it, standing in the
    shrine grove beside the compound's proper shrine.

    Why: Small altars below the rank of a shrine far outnumbered real shrines, and they stood without an arch;
    this one stands in the shrine grove, among the trees it is kept for. It is kept up by a private hand,
    though anyone may pray at it.

    Note: the altar's dedication to the kami of the wood, and its keeping by a private hand with no monk
    behind it, are its map's story, a departure made by the map's design. Its form - a small altar with
    no torii, below the rank of a shrine - is the historical one, and it is drawn about 6 ft square.

    Name: wood-kami altar
    Covers: the altar and its label with the "personally maintained" sublabel
    Label: deviation
    Sources: hokora-jawiki, tokushima-yashikigami, jawiki-yashikigami
    Entry: research/religion-and-death.html - 'Torii are VOTIVE DONATIONS'; research/homesteads.html - "The farmstead's fixtures"
    """

    key = "wood-kami altar"
