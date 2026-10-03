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
    key = "outer court"


class InnerCourt(Kind):
    key = "inner court"


class BorderCourt(Kind):
    key = "border court"


class HearingCourt(Kind):
    key = "hearing court"


class PracticeGround(Kind):
    key = "practice ground"


class CompoundGarden(Kind):
    key = "garden"


class RearYard(Kind):
    key = "rear yard"


class VegetableGarden(Kind):
    key = "vegetable garden"


class ShrineGrove(Kind):
    key = "shrine grove"


# The GM's ruling: the compound wall is drawn 3 ft thick, the heavier of the two real forms.
class CompoundWall(Kind):
    key = "compound wall"


class MainGate(Kind):
    key = "main gate"


class SideGate(Kind):
    key = "side gate"


class CourtDivider(Kind):
    key = "court divider"


class ApproachRoad(Kind):
    key = "road"


class CartYard(Kind):
    key = "cart yard"


# ---- the parts of the grounds (feature 264: a thing drawn inside a feature is its own kind) --------------------


class GardenPond(Kind):
    key = "garden pond"


class StoneLantern(Kind):
    key = "stone lantern"


class GardenPines(Kind):
    key = "garden pines"


class StrikingPosts(Kind):
    key = "striking posts"


class WeaponRack(Kind):
    key = "weapon rack"


class Nakamon(Kind):
    key = "nakamon"


class Door(Kind):
    key = "door"
