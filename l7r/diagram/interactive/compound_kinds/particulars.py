"""The particulars: things a compound plan draws because of its place in the setting or its map's story (feature 262).

Ochiba's Fox wardings (the threshold stones and their buried Pact-Bowl, the cinnabar workshop), Hayakawa's river
and landing, and Ubame's Fox border, parley room,
boundary stones, charcoal store and wood-kami altar. A kind the SETTING makes - with no historical counterpart
the record covers - says so in its About text, written from the GM's canon (`/host-l7r-repo/setting/l7r.md`, which needs
no citation, so `Sources: not recorded`) and the map's design notes. A kind the record DOES cover (the river, the
landing, the drawn border line) is written from the record, and what its one map adds is in that map's `.notes.md`
"Map notes" block.

A page shows nothing drawn from the GM-only notes of an Obsidian Portal record - not now and not ever (the GM,
2026-09-28): the Fox-Fire Lantern, the fox relics and Hayakawa's salt wards came from those notes and were taken off
the pages; a note the GM wants shown, they move to a visible place first.
"""

from __future__ import annotations

from ..classes import Kind


# The GM's rulings: a flanking pair of stones, one each side of the road, where canon sets one; and Ochiba's pair
# drawn larger than canon's two-fist stones (about 3.3 by 4.7 ft), because Ochiba makes and paints them.
class ThresholdStones(Kind):
    key = "threshold stones"


class CinnabarWorkshop(Kind):
    key = "cinnabar workshop"


class River(Kind):
    key = "river"


class RiverLanding(Kind):
    key = "river landing"


class FoxBorder(Kind):
    key = "fox border"


# The GM's ruling: the door which receives the Kitsune is the border, so the parley room is built across it.
class ParleyRoom(Kind):
    key = "parley room"


class BoundaryStones(Kind):
    key = "boundary stones"


class CharcoalStore(Kind):
    key = "charcoal store"


class WoodKamiAltar(Kind):
    key = "wood-kami altar"


# ---- the parts of the particulars (feature 264: a thing drawn inside a feature is its own kind) ----------------


class Revetment(Kind):
    key = "revetment"


class Dock(Kind):
    key = "dock"


class TaxBarge(Kind):
    key = "tax barge"


class BoatmensAltar(Kind):
    key = "boatmen's altar"


class RiverWatch(Kind):
    key = "river watch"


class Steelyard(Kind):
    key = "steelyard"


class CharcoalBales(Kind):
    key = "charcoal bales"


class ParleyMats(Kind):
    key = "parley mats"


class DryingStonesAndBowls(Kind):
    key = "drying stones and bowls"
