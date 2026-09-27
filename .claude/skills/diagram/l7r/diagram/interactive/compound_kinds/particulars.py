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
    cinnabar fox-tracks.

    Why: The stones of the Fox road wardings are painted with cinnabar, and the painting is sacred work: the
    setting's record has the magistrate paint each newly dressed stone by their own hand, in daylight, at the
    colonnade off the shrine's eastern altar - which is why the workshop adjoins the shrine hall rather than
    standing in the service yard.

    Note: the painted threshold stones and the colonnade where they are painted belong to the setting's own
    canon and record, a departure made by the setting with no historical counterpart in the research record.

    Name: cinnabar workshop
    Covers: the hatched colonnade, its posts and its label
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
    stone, kept on its own stand at the shrine's eastern, fox altar - and the Chigiri-no-Chou is the setting's
    too. Neither has a historical counterpart, and the research record holds nothing like them, so both are a
    departure made by the setting.

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

    Note: Freight by water is a recorded finding, and the village granary is recorded as a temporary store for
    shipment, but that a well-watered county's office granary is a staging node its tax rice passes through is
    the research's own reading; the rule that only the Lion build canals is the setting's canon. That Japan's heavy freight also went by water rests on
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
    alongside it, a watch post over the water and a small altar for the boatmen - each its own feature, lit with
    the landing.

    Why: Tax grain went downstream on hired commoners' boats flying an official pennant and inspected at the
    ports of call - the magistracy owned no hulls, and its hold on the cargo was documentary - so a posting on
    a navigable river keeps a landing of its own where the grain is loaded.

    Note: That the tax grain went on hired boats under an official pennant, inspected at the ports of call,
    follows the record; that it passed through the compound, and so was loaded at the compound's own landing,
    is this project's reading.

    Name: river landing
    Covers: the landing label - its dock, revetment, barge, watch post and altar are each their own kind
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
    province's map made in the Genroku revision drew its district boundaries clearly. A border exists where
    two authorities have agreed it, so the plan draws the agreed line itself, which nothing on the ground need
    stand clear of.

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
    What: A room built into the compound's border wall, the border running across its floor; its doors and its
    kneeling mats are each their own feature.

    Why: Each party kneels on its own soil, so the two sides can meet and settle their business without either
    stepping onto the other's ground. Its inner door opens into a receiving court, never into the court where
    the accused kneel, because the room receives guests.

    Note: a room built across a clan border is part of its map's story, a departure made by the map's design
    with no historical evidence for one in the record. The drawn border line it stands on is the
    attested part; the record calls the room the architectural counterpart of that line, by analogy only.

    Name: parley room
    Covers: the room in the border wall and its label
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


# ---- the parts of the particulars (feature 264: a thing drawn inside a feature is its own kind) ----------------


class Revetment(Kind):
    """
    What: The stone facing of the riverbank at Hayakawa's landing, drawn as a gray band along the water's edge.

    Why: A river's level moves by many feet through the year, so a working bank is faced with stone or timber
    cribbing to hold it; at the great rice stores on the river at Edo, the stone revetment was part of the answer
    to flood.

    Note: A faced bank at a river landing follows the record.

    Name: revetment
    Covers: the stone facing along the landing's bank
    Label: accurate
    Sources: kashi-jawiki, gangi-kowan-jawiki, kuramae-jawiki
    Entry: research/cities/river-cities.html - "The wharf's working face"; research/cities/capitals.html - "The sluice's lifting frame"
    """

    key = "revetment"


class Dock(Kind):
    """
    What: The dock at Hayakawa's landing: a timber pier running out from the faced bank, where barges lie
    alongside to load.

    Why: A settlement on navigable water sends its freight by boat, and a pier gives a loaded hull the reach it
    needs where the bank shelves too gently to come alongside.

    Note: A pier at a river landing follows the record. The record makes steps cut into the faced bank the usual
    landing and the pier the exception for a shelving bank; Hayakawa draws a pier and no steps, and nothing
    records its bank as shelving.

    Caveat: The record makes steps cut into the faced bank the usual landing and the pier the exception for a
    shelving bank; Hayakawa draws a pier and no steps, and nothing records its bank as shelving.

    Name: dock
    Covers: the pier and its plank lines
    Label: accurate
    Sources: pier-enwiki, gangi-kowan-jawiki, gangi-hiroshima-jawiki, kuramae-jawiki, chinaknowledge-caoyun
    Entry: research/cities/river-cities.html - "The wharf's working face"; research/cities/capitals.html - "The sluice's lifting frame"; research/ways.html - "Where does a village's freight go?"
    """

    key = "dock"


class TaxBarge(Kind):
    """
    What: A river barge moored alongside Hayakawa's dock with bales of tax grain aboard, drawn at about 47 by 7 ft.

    Why: Tax grain moves down the river to the city on hired boats flying an official pennant; the
    magistracy owns no hulls, and the barge at its dock is one taken on for the run.

    Note: The barge's size, inside the record's range for such a boat, and the hiring of hulls for tax rice (read for the shogunate's sea shipments; a county's grain going downriver on them is this map's reading),
    follow the record.

    Name: tax barge
    Covers: the moored barge, its lines, its bales and its label
    Label: accurate
    Sources: takasebune-jawiki, kotobank-takasebune, gokura-jawiki, takayama-jinya-city
    Entry: research/buildings.html - 'The granary is a staging node, not the terminal store'; research/cities/river-cities.html - "The wharf's working face"
    """

    key = "tax barge"


class BoatmensAltar(Kind):
    """
    What: A small altar on the bank beside the dock, kept by the boatmen who work the landing.

    Why: Those who work a river keep an altar where they set out, for safe passage.

    Note: the research record has no entry on an altar at a river landing; it is this map's own story, and its form
    and place are a guess.

    Name: boatmen's altar
    Covers: the altar on the bank and its label
    Label: guess
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "boatmen's altar"


class RiverWatch(Kind):
    """
    What: A small guard post at the landing, from which the watch keeps an eye on the river traffic.

    Why: A landing where the county's tax grain is loaded is worth watching, and the river's traffic is watched from
    the bank beside it.

    Note: the research record has no entry on a guard post at a river landing; the post is this map's own story,
    and its form and place are a guess.

    Name: river watch
    Covers: the guard post at the landing and its label
    Label: guess
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "river watch"


class BalanceBeam(Kind):
    """
    What: The balance on Ubame's weighing floor where bales of charcoal are weighed before the tally is written.

    Why: A bale of charcoal had no standard weight, so charcoal had to be weighed at the point of sale, and the
    weighing floor exists for that.

    Note: Weighing charcoal at the point of sale is reasoned from the charcoal bale having no standard weight, which the record states but for which no readable source was found. The instrument's form, a beam balance rather
    than a steelyard, is not in the record.

    Caveat: The instrument's form, a beam balance rather than a steelyard, is not in the record.

    Name: balance beam
    Covers: the balance on the weighing floor
    Label: accurate
    Sources: economy-song-enwiki, tonya-enwiki
    Entry: research/urban-features.html - 'Charcoal yards: a tallied depot, a cooling ground, and a weighing floor'
    """

    key = "balance beam"


class CharcoalBales(Kind):
    """
    What: Bales of charcoal stacked on Ubame's weighing floor, waiting to be weighed.

    Why: Charcoal traveled in straw bales of no standard weight, which is why every bale is weighed before it is
    tallied.

    Note: The charcoal bale of no standard weight is the record's finding, but no readable page for it has been traced: the page it had been attributed to says nothing about charcoal.

    Name: charcoal bales
    Covers: the stacked bales on the weighing floor
    Label: accurate
    Sources: economy-song-enwiki, tonya-enwiki
    Entry: research/urban-features.html - 'Charcoal yards: a tallied depot, a cooling ground, and a weighing floor'
    """

    key = "charcoal bales"


class ParleyMats(Kind):
    """
    What: The kneeling mats in a parley room, two on each side of the border that runs across its floor, facing
    each other across the line.

    Why: A delegation from across the border is received without either party stepping off its own soil: each side
    kneels on its own ground, the line between them.

    Note: the room and its mats are the map's own design, a departure with no historical room behind it - the
    building counterpart of the drawn border line - and the mats' 3 ft size is this project's own figure.

    Name: parley mats
    Covers: the four kneeling mats in the parley room
    Label: deviation
    Sources: not recorded
    Entry: research/urban-features.html - 'Drawing a clan border'
    """

    key = "parley mats"


class DryingStonesAndBowls(Kind):
    """
    What: River-stones and small lacquer-black bowls laid out to dry under a cinnabar workshop's colonnade.

    Why: The workshop is where the Fox Clan's threshold stones are made and painted - river-stones the size of two
    fists, painted with cinnabar fox-tracks - beside the shrine of the priest-magistrate who keeps the road
    wardings.

    Note: the threshold stones and their Pact-Bowls are the campaign's own canon, a departure made by the setting
    with no historical counterpart. Each stone and bowl is drawn as a marker, larger than a stone the size of two
    fists or a small bowl would be.

    Name: drying stones and bowls
    Covers: the drying river-stones and lacquer bowls in the workshop
    Label: deviation
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "drying stones and bowls"
