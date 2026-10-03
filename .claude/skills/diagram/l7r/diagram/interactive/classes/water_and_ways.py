"""Water, ways and the things met along them - the brook, ditches, ponds, lanes, the well, the board.

Each class's DOCSTRING is its explanation - `What:`, `Why:`, `Note:`, optional `Caveat:` - parsed by
`_base.parse_explanation` (feature 189). Edit the prose here and the page changes; the gate does not re-open.

Research: modal explanation - NONE: the explanation's research is its Entry:, checked by entry-drift
"""

from __future__ import annotations

from ._base import Kind


# The GM's rulings: stream width by rank in the water hierarchy, junctions not conserving width (2026-08-16);
# the earlier width ladder, a stream feeding a moat drawn as wide as the moat (2026-07-21).
class Stream(Kind):
    key = 'stream'


class IrrigationDitch(Kind):
    key = "irrigation ditch"


class FarmChannel(Kind):
    key = "farm channel"


class DrainageDitch(Kind):
    key = "drainage ditch"


class Weir(Kind):
    key = "weir"


class Pond(Kind):
    key = 'pond'


class FieldPond(Kind):
    key = 'field pond'


class FieldRock(Kind):
    key = 'field rock'


class GraveIsland(Kind):
    key = 'grave island'


# WHY THE CLASS IS A *VILLAGE* LANE AND NOT A HAMLET LANE - the GM, 2026-08-29: "I have been
# referring to hamlet lanes as village lanes specifically for this reason because they are presumed
# to lead into the main village when not otherwise stated." The rule is in the `why` where a reader
# needs it; the naming rationale is project process and stays here (settlement-review, 2026-08-29).
class VillageLane(Kind):
    key = 'village lane'


# The GM's ruling: a farm-ditch crossing is laid over water 2 ft wide or more.
class Footbridge(Kind):
    key = 'footbridge'


class Well(Kind):
    key = 'well'


class NoticeBoard(Kind):
    key = 'notice board'
