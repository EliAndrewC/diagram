"""The particulars: things a compound plan draws because of its place in the setting or its map's story (feature 262).

Ochiba's Fox wardings (the threshold stones and their buried Pact-Bowl, the Fox-Fire Lantern, the cinnabar
workshop, the fox relics), Hayakawa's river, landing and salt wards, and Ubame's Fox border, parley room,
boundary stones, charcoal store and wood-kami altar. A kind the SETTING makes - with no historical counterpart
the record covers - is `deviation`, written from the GM's canon (`/host-l7r-repo/setting/l7r.md`, which needs no
citation, so `Sources: not recorded`) and the map's design notes. A kind the record DOES cover (the river, the
landing, the drawn border line) keeps the record's classification, and what its one map
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
    What: Small cones of salt set in a pair outside a door of the compound, one on each side of the opening,
    set out for good fortune at the threshold.

    Why: A small heap of salt at a doorway, morijio, is recorded in the late Edo period at the doors of the
    trades that wanted customers - restaurants, assignation houses and variety halls - set out for good
    fortune. Today the salt is pressed into a cone or a three-sided pyramid, and at an entrance it commonly
    stands outside, one heap on each side, so the pair flanks each opening on its outer face, and every door
    so warded carries its own pair - the gates, the posterns and the river door alike.

    Note: The form follows the present-day custom, since no page read gives an Edo-period shape: a small cone,
    a pair outside each warded opening. No page read puts salt at the gates of a samurai residence or an
    official's compound, so its use here is a guess, and each heap is drawn as a marker far larger than a
    real cone of salt, which the record calls only small.

    Name: salt wards
    Covers: every salt-ward marker at the doors, the "salt wards" label and the salt-wards note box
    Label: guess
    Sources: kotobank-morijio, jawiki-morijio, ise-miyachu-morijio
    Entry: research/religion-and-death.html - "Were cones of salt set at the doors of an official's compound?"
    """

    key = "salt wards"


class River(Kind):
    """
    What: A navigable river running beside the compound - the county's road to the rest of the world for its
    heavy goods.

    Why: Where navigable natural water exists, it is the main freight route, and a county on it is a staging
    node: its tax grain moves on by boat - hired hulls flying an official pennant, inspected at each port of call, for the office owns none - toward the central stores rather than sitting in rows of granaries
    at the office. In this setting only the Lion dig transport canals, so for any other county the river is
    the way.

    Note: Freight by water is a recorded finding, and the village granary is recorded as a temporary store for
    shipment, but that a well-watered county's office granary is a staging node its tax rice passes through is
    the research's own reading, and so is the contrast with an isolated county's rows of granaries, whose one example (Takayama holding rice for all of Hida) has no readable source; the rule that only the Lion build canals is the setting's canon. That Japan's heavy freight also went by water rests on
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
    What: The compound's landing on the river: steps cut into a stone-faced bank, the tax barge moored
    alongside it, a watch post over the water and a small altar for the boatmen - each its own feature, lit with
    the landing.

    Why: Tax grain went downstream on boats the shogunate hired directly, flying an official pennant and inspected at the
    ports of call - the magistracy owned no hulls, and its hold on the cargo was documentary - so a posting on
    a navigable river keeps a landing of its own where the grain is loaded.

    Note: That the tax grain went on hired boats under an official pennant, inspected at the ports of call,
    follows the record of the shogunate's rice shipped to Edo, and carrying it to a county is this project's own; that the magistracy's hold on it was documentary, a matter of counts and records, and that it passed through the compound and so was loaded at the compound's own landing,
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

    Note: a room built across a clan border is part of its map's story, made by the GM's ruling that the door
    which receives the Kitsune is the border - a departure with no historical room behind it, since no page
    read describes a room built across a border or two parties meeting on the line itself. Where two powers
    dealt regularly across a border, each kept its own ground: a post on each side of the line, facing each
    other across it, as Russia and Qing China built at Kyakhta, or a compound one side set aside for the
    other's officers with a reception hall beside it, as at the Japan House at Choryang, where Tsushima traded
    with Korea. The drawn border line the room stands on is the attested part.

    Name: parley room
    Covers: the room in the border wall and its label
    Label: deviation
    Sources: kyakhta-trade-enwiki, wakan-kotobank
    Entry: research/buildings.html - 'Did two sides ever meet in a room built across their border?'; research/urban-features.html - 'Drawing a clan border'
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
    What: A sealed storehouse for charcoal - a kura with thick plastered earthen walls - where the charcoal a
    county takes in is held under the office's seal, standing at the ordinary spacing of the buildings around it.

    Why: Charcoal was an industrial fuel moved at state scale, and this map keeps a store of it as a supervised, tallied depot
    rather than a back room. A plastered storehouse was built to protect what it held against fire, damp and
    theft - its walls often a foot thick, its outer doors sometimes faced with earth and plaster, and gunpowder among what
    such stores kept - so its own wall does for the charcoal what 30 ft of open ground does for an open stack in
    a charcoal yard. Fresh charcoal heats itself to ignition when packed, so it goes in only once it has cooled.

    Note: No page read says charcoal was kept in a plastered storehouse, or gives a spacing between a storehouse
    and its neighbors, so keeping it in one, at ordinary spacing with no fire gap, is a guess resting on the
    storehouse's recorded purpose.

    Name: charcoal store
    Covers: the sealed charcoal kura and its labels
    Label: guess
    Sources: dozo-jawiki, kotobank-dozozukuri, wagner-ming-iron, fao-charcoal-safety
    Entry: research/urban-features.html - "Does the charcoal yard's 30 ft fire gap apply to charcoal kept in a plastered storehouse?", 'Charcoal yards: a tallied depot, a cooling ground, and a weighing floor'
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
    What: The stone facing of the riverbank at Hayakawa's landing, drawn as a gray band along the water's edge,
    with the landing's steps cut into it across the bank street from the compound's wall.

    Why: A river's level moves by many feet through the year, so a working bank is faced with stone or timber
    cribbing to hold it; at the great rice stores on the river at Edo, the stone revetment was part of the answer
    to flood. Where samurai residences stood on a river, as on Hiroshima's, they were built back from the
    revetment and walled, which is why the compound's wall stands back behind the bank street.

    Note: A faced bank at a river landing, and a residence's wall standing back from it, follow the record.

    Name: revetment
    Covers: the stone facing along the landing's bank
    Label: accurate
    Sources: gangi-hiroshima-jawiki, kashi-jawiki, gangi-kowan-jawiki, kuramae-jawiki
    Entry: research/cities/river-cities.html - "Does an official's compound have its own stepped landing, or a pier?", "The wharf's working face"; research/cities/capitals.html - "The sluice's lifting frame"
    """

    key = "revetment"


class Dock(Kind):
    """
    What: The dock at Hayakawa's landing: a flight of steps cut into the faced bank across the bank street from
    the compound's wall, reached from a gate in that wall, where barges come alongside to load.

    Why: A river's level rises and falls through the year, so the usual landing is steps cut into a faced bank,
    which meet a moored hull at whatever height the water stands; a pier is the exception, for a bank that
    shelves too gently. Where samurai residences stood on a river, as on Hiroshima's, they were built back from
    the revetment and walled, and it is thought no gated landing opened from them onto the steps - a back gate straight onto
    the steps is the merchants' form on the landings that survive, built from the Meiji period on - so the compound reaches its steps from a gate in its wall, across the
    street.

    Note: The steps across the bank street, reached from a gate in the compound's wall rather than a back gate
    onto the steps, follow the record of samurai residences built back from the bank and walled, thought to have
    had no gated landing. That the back gate was already the merchants' form in the Edo period is this map's
    reading of landings built from the Meiji period on. No page read describes an official's compound with a
    landing of its own, so that these steps are the compound's own rather than a public landing is a guess.

    Caveat: That the back gate was already the merchants' form in the Edo period is this map's reading of landings
    built from the Meiji period on. No page read describes an official's compound with a landing of its own, so that these steps are the
    compound's own rather than a public landing is a guess.

    Name: dock
    Covers: the landing steps in the faced bank
    Label: accurate
    Sources: gangi-hiroshima-jawiki, gangi-kowan-jawiki, pier-enwiki, matou-zhwiki
    Entry: research/cities/river-cities.html - "Does an official's compound have its own stepped landing, or a pier?", "The wharf's working face"
    """

    key = "dock"


class TaxBarge(Kind):
    """
    What: A river barge moored alongside Hayakawa's dock with bales of tax grain aboard, drawn at about 47 by 7 ft.

    Why: Tax grain moves down the river to the city on hired boats flying an official pennant; the
    magistracy owns no hulls, and the barge at its dock is one taken on for the run.

    Note: The barge's size, inside the record's range for such a boat, and the hiring of hulls for tax rice (read for the shogunate's sea shipments; a county's grain going downriver on them is this map's reading),
    follow the record. The bales aboard are drawn about 4 ft long so that they read, where a rice bale of today's 60 kg size is about
    2.5 ft long and 1.5 ft across, varying with what it held.

    Caveat: The bales aboard are drawn about 4 ft long so that they read, where a rice bale of today's 60 kg size is about 2.5 ft long
    and 1.5 ft across, varying with what it held.

    Name: tax barge
    Covers: the moored barge, its lines, its bales and its label
    Label: accurate
    Sources: takasebune-jawiki, kotobank-takasebune, gokura-jawiki, takayama-jinya-city, tawara-unit-jawiki, nisira-komedawara
    Entry: research/urban-features.html - 'How big is a bale of rice or charcoal?'; research/buildings.html - 'The granary is a staging node, not the terminal store'; research/cities/river-cities.html - "The wharf's working face"
    """

    key = "tax barge"


class BoatmensAltar(Kind):
    """
    What: A small shrine at the head of the landing, kept by the boatmen who work the river.

    Why: A boat's own guardian, the funadama, lives aboard, at the foot of the mast, and is only sometimes given
    a shrine on land; what river boatmen are recorded keeping ashore is a water god. In Katsushika, now a ward of
    Tokyo, the boatmen of the night-soil boats kept a water-god shrine, a Suitengu, that once stood on a river
    bank, and on its festival day they moored their boats near the bank and spent the day in its precinct.

    Note: Both forms are attested - a shrine on land to the boats' guardian, and a water-god shrine kept by the
    boatmen - and a landing keeps one of them, named in the map's notes. Neither is recorded standing at a
    landing itself, or with a size, so the shrine's place at the head of the landing and its size are a guess.

    Caveat: Neither is recorded standing at a landing itself, or with a size, so the shrine's place at the head
    of the landing and its size are a guess.

    Name: boatmen's altar
    Covers: the altar on the bank and its label
    Label: accurate
    Sources: funadama-jawiki, kotobank-funadama, katsushika-suijin
    Entry: research/cities/river-cities.html - 'Did the boatmen keep a shrine at the landing?'
    """

    key = "boatmen's altar"


class RiverWatch(Kind):
    """
    What: A small watch hut at the head of the landing, manned from the office, from which the watch keeps an eye
    on the boats that come to it.

    Why: In the Edo period, domains set boat watch posts at the landings of busy boat routes to inspect passing
    boats. The best recorded, the shogunate's Nakagawa post of 1661, was a fenced compound of about 155 by 100 ft
    guarding the approach to the shogun's city, with ten spears and a watch hut at the river's edge, manned by the
    retainers of the officer who held the duty; a landing like this one keeps only the hut. The domains' posts
    also collected taxes, but this setting taxes goods where they are sold, not where they pass through, so the
    watch here inspects and records who and what comes to the landing and takes no toll.

    Note: The watch hut at the river's edge follows the record, and taking no toll is the setting's own rule. No
    page read describes a watch at a local office's own landing, so the hut's size and its place at the office's
    landing are a guess.

    Caveat: No page read describes a watch at a local office's own landing, so the hut's size and its place at the
    office's landing are a guess.

    Name: river watch
    Covers: the guard post at the landing and its label
    Label: accurate
    Sources: funabansho-jawiki, koto-nakagawa-funabansho, l7r-tariffs
    Entry: research/cities/river-cities.html - 'Who kept watch on the river at an official's landing, and what did the watch post look like?'
    """

    key = "river watch"


class Steelyard(Kind):
    """
    What: The steelyard on Ubame's weighing floor where bales of charcoal are weighed before the tally is written: a
    wooden beam with a hook at one end for the bale and a weight on the other, slid along the beam until it balances.

    Why: Charcoal was packed by grade rather than to one weight, so a bale is weighed at the point of sale, and
    one account, naming no country or period, has the steelyard weighing food and everyday goods and the two-pan balance serving valuables. Japan used
    steelyards from the Edo period, in sizes that included one for a load of four of the best charcoal bales, and China's was its
    traditional market scale, built for heavy loads too.

    Note: The frame or post the steelyard hangs from at the weighing floor is a guess.

    Caveat: The frame or post the steelyard hangs from at the weighing floor is a guess.

    Name: steelyard
    Covers: the steelyard on the weighing floor
    Label: accurate
    Sources: zhwiki-ganchen, zjnews-cixi-steelyard, osaka-keiryo-history, kanazawa-saobakari
    Entry: research/urban-features.html - 'Was bulk charcoal weighed on a balance beam or a steelyard?', 'Charcoal yards: a tallied depot, a cooling ground, and a weighing floor'
    """

    key = "steelyard"


class CharcoalBales(Kind):
    """
    What: Bales of charcoal stacked on Ubame's weighing floor, waiting to be weighed.

    Why: Charcoal traveled in straw bales, woven into a cylinder like the rice bale, and a bale had no standard
    size before the modern period - not even for rice, whose bale held anything from 2 to 5 to by time and place.
    Charcoal was packed at a weight set by its grade: in one charcoal district, 4 kan for the best and 8 or 10 for
    the lower grades. A bale of no standard size cannot be traded by count, which is why every bale is weighed
    before it is tallied.

    Note: we have drawn each bale about 4 ft long, in order to make it read on the plan; a charcoal bale is about
    2 by 1.3 ft, as a mid-20th-century one in a museum measures, and no page read measures one of the Edo period.

    Name: charcoal bales
    Covers: the stacked bales on the weighing floor
    Label: convention
    Sources: tawara-jawiki, tawara-unit-jawiki, edo-tokyo-sumidawara
    Entry: research/urban-features.html - 'How big is a bale of rice or charcoal?', 'Charcoal yards: a tallied depot, a cooling ground, and a weighing floor'
    """

    key = "charcoal bales"


class ParleyMats(Kind):
    """
    What: The kneeling mats in a parley room, two on each side of the border that runs across its floor, facing
    each other across the line.

    Why: A delegation from across the border is received without either party stepping off its own soil: each side
    kneels on its own ground, the line between them.

    Note: the mats belong to the same departure as the parley room, the map's own design: no page read seats two
    parties across a border line in one room, and where two powers dealt regularly across a border each kept its
    own ground, in a post on each side of the line or in a compound one side set aside for the other's officers.
    The mats' 3 ft size is this project's own figure.

    Name: parley mats
    Covers: the four kneeling mats in the parley room
    Label: deviation
    Sources: kyakhta-trade-enwiki, wakan-kotobank
    Entry: research/buildings.html - 'Did two sides ever meet in a room built across their border?'; research/urban-features.html - 'Drawing a clan border'
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
