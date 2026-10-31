"""The comb's drain outfall run and the channel rule it keeps: a watercourse runs downhill (`runs_downhill`), and the drain's
continuation off the field curves out of the collector onto the fall (`outfall_run`). Lifted out of `comb.py` at the
1,000-line bar (feature 328); `comb` re-exports every name, so `from .comb import runs_downhill` still works.

Research: plumbing - NONE: geometry on a bare polyline
"""

import math
from collections.abc import Sequence

DOWNHILL_FRACTION = 0.0
#: How much of a watercourse's net travel must run down the fall (water:W10, `channels_flow_downhill`): a delivery may take
#: an oblique line, but not one whose net travel is level or uphill - so any net descent, strictly (feature 328: the
#: retired gate test's fifth, a bound of about 78 degrees, forbade the near-90 courses 0054 allows; a tighter bound
#: "was considered and declined, since it would condemn real contour works").
"""Research: downhill share - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a strict "under 90" degrees off the fall - any net descent"""


def runs_downhill(course: Sequence[Sequence[float]], fall: Sequence[float], frac: float = DOWNHILL_FRACTION) -> bool:
    """Does `course`'s net displacement, first point to last, run down `fall` by more than `frac` of its length - the
    channel rule (water:W10), ONE predicate for every writer of `M['channels']`: the sink's routes (`hamletgen/sink.py`)
    and the hairline feed (`_comb_source_channel`). A course that ends where it starts has no direction to judge.

    Research: water runs downhill - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: net travel down the fall, strictly under 90 degrees off it"""
    vx, vy = float(course[-1][0]) - float(course[0][0]), float(course[-1][1]) - float(course[0][1])
    L = math.hypot(vx, vy)
    return L == 0 or vx * float(fall[0]) + vy * float(fall[1]) > frac * L
