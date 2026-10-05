"""The household kinds of a compound plan: the lord's house and everything that keeps it (feature 262).

The magistrate's household lives inside the working compound, behind the office - the residence, the
dwellings of the karo, the retainers and the servants, the guest quarters, and the kitchen, bath, wells,
privies, stables, fire-water and shrine that serve them. Each class's modal text (`assets/modals/sheet/`, the About
form) is written from the research section its `Entry:` names, or says the record has no entry. What is true of one map
only (Ochiba's two-altar Inari hall, Hayakawa's enlarged bath, Ubame's shuttered wing) lives in that map's `.notes.md`
"Map notes" block, not here.
"""

from __future__ import annotations

from ..classes import Kind


class Residence(Kind):
    key = "residence"


class AncestralAlcove(Kind):
    key = "ancestral alcove"


class KarosHouse(Kind):
    key = "karo's house"


class RetainersQuarters(Kind):
    key = "retainers' quarters"


class ServantsQuarters(Kind):
    key = "servants' quarters"


class GuestQuarters(Kind):
    key = "guest quarters"


class Kitchen(Kind):
    key = "kitchen"


class Bath(Kind):
    key = "bath"


class Well(Kind):
    key = "well"


class Latrine(Kind):
    key = "latrine"


class Stables(Kind):
    key = "stables"


class Kennel(Kind):
    key = "kennel"


class Storehouse(Kind):
    key = "storehouse"


class FireWaterTubs(Kind):
    key = "fire-water tubs"


class CompoundShrine(Kind):
    key = "compound shrine"


class WritingPavilion(Kind):
    key = "writing pavilion"


# ---- the parts of the household's buildings (feature 264: a thing drawn inside a feature is its own kind) -------


class Hearth(Kind):
    key = "hearth"


class Genkan(Kind):
    key = "genkan"


class Engawa(Kind):
    key = "engawa"


class ResidenceCorridor(Kind):
    key = "residence corridor"


class LordsQuarters(Kind):
    key = "lord's quarters"


class FamilyQuarters(Kind):
    key = "family quarters"


class InnerRooms(Kind):
    key = "inner rooms"


class ReceptionRoom(Kind):
    key = "reception room"


class ShutteredWing(Kind):
    key = "shuttered wing"


class ShrineAltar(Kind):
    key = "shrine altar"


# The GM's ruling of 2026-09-27: a village shrine's innermost arch stands 12 ft from its hall where there is room.
class Torii(Kind):
    key = "torii"
