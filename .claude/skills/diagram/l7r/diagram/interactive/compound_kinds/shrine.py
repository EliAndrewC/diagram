"""The country shrine's own kinds (feature 277): what a village district's shrine sheet draws that no magistracy does.

Written in the magistracy kinds' form (feature 262) and from the same record - research religion-and-death 090 to 128 -
so the country shrine's page is read from its sheet's `data-kind` tags exactly as a magistracy's is. A kind both draw
(the torii, the grove, the well, the kitchen, the latrine, the garden, the fire-water tubs, the genkan) is written
once, in its magistracy family, and serves both.
"""

from __future__ import annotations

from ..classes import Kind


# The GM's ruling: one roof over the hall and the dwelling is the setting's form for its country shrines.
class HallAndDwelling(Kind):
    key = "hall and dwelling"


class Sanctuary(Kind):
    key = "sanctuary"


class MonksRooms(Kind):
    key = "the monk's rooms"


class WritingRoom(Kind):
    key = "writing room"


# The GM's rulings: the number of arches along the approach and their pitch.
class ShrineApproach(Kind):
    key = "approach"


class ShrineBasin(Kind):
    key = "basin"


class SacredTree(Kind):
    key = "sacred tree"


class SweptClearing(Kind):
    key = "precinct clearing"


class Footpath(Kind):
    key = "footpath"


class GuardianFigures(Kind):
    key = "guardian figures"


class StoneLanterns(Kind):
    key = "lanterns"


class StrengthStones(Kind):
    key = "strength stones"


class FarmersStage(Kind):
    key = "stage"


class SumoRing(Kind):
    key = "sumo ring"


class BellTower(Kind):
    key = "bell tower"


class ShrineBurialGround(Kind):
    key = "burial ground"
