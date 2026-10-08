"""The comb's drain outfall run and the channel rule it keeps: a watercourse runs downhill (`runs_downhill`), and the drain's
continuation off the field curves out of the collector onto the fall (`outfall_run`). Lifted out of `comb.py` at the
1,000-line bar (feature 328); `comb` re-exports every name, so `from .comb import runs_downhill` still works.

Research: plumbing - NONE: geometry on a bare polyline
"""

import math
from collections.abc import Sequence

from .._geom import Pt

DOWNHILL_FRACTION = 0.2
#: How much of a watercourse's net travel must run down the fall (water:W10, `channels_flow_downhill`): a delivery may take
#: an oblique line, but not one whose net travel is level or uphill. The retired gate test's own figure.
"""Research: downhill share - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a fifth of a course's length net down the fall"""


def runs_downhill(course: Sequence[Sequence[float]], fall: Sequence[float], frac: float = DOWNHILL_FRACTION) -> bool:
    """Does `course`'s net displacement, first point to last, run down `fall` by at least `frac` of its length - the
    channel rule (water:W10), ONE predicate for every writer of `M['channels']`: the sink's routes (`hamletgen/sink.py`)
    and the hairline feed (`_comb_source_channel`). A course that ends where it starts has no direction to judge.

    Research: water runs downhill - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: net travel down the fall, at least DOWNHILL_FRACTION of the length"""
    vx, vy = float(course[-1][0]) - float(course[0][0]), float(course[-1][1]) - float(course[0][1])
    L = math.hypot(vx, vy)
    return L == 0 or vx * float(fall[0]) + vy * float(fall[1]) >= frac * L


CURVE_LEG_PX = 10.0
"""Research: the fallback's curve - NONE: the leg of the turn out of the drain where the lead would climb, short so the run's net
descent holds (three legs at most against the reach)"""


def outfall_run(b0: Sequence[float], b1: Sequence[float], fall: Sequence[float], lead: float = 70.0, reach: float = 520.0, turn_max: float = 55.0) -> list[Pt]:
    """The village and city comb's drain-outfall run (water:W10, W12): `lead` px on along the drain's own exit (`b0` toward
    `b1`) for a smooth junction, then CURVING onto the unit `fall` in turns of at most `turn_max` degrees, legs of half the
    lead, and `reach` px straight down the fall off the map - taken only where it `runs_downhill`. Where it would not, the
    run curves out from the drain's own end on legs of `CURVE_LEG_PX`, the turns held as before, then runs down the fall.

    Feature 328: the run turned down the fall at one corner of up to ~90 degrees where the exit ran cross-slope; 0060's
    drawing page has the run curve out of the collector, at most 55 degrees (`JUNCTION_TURN_MAX_DEG` on the hamlet).

    Research: drain outfall - research/questions/0060-field-drains-akusuiro.drawing.html: on along the drain's exit, curving onto the fall at most 55 degrees a turn, then straight down the fall off the map"""
    run = _curved_run(b0, b1, fall, lead, lead / 2, reach, turn_max)
    if runs_downhill(run, fall):
        return run
    return _curved_run(b0, b1, fall, 0.0, CURVE_LEG_PX, lead + reach, turn_max)


def _curved_run(b0: Sequence[float], b1: Sequence[float], fall: Sequence[float], lead: float, leg: float, reach: float, turn_max: float) -> list[Pt]:
    """`lead` on along the exit (`b0` toward `b1`), then legs of `leg` turning at most `turn_max` degrees each until the heading is
    within `turn_max` of the `fall`, then `reach` straight down it - every turn, the first one off the exit included, at most
    `turn_max`.

    Research: curving out of the collector - research/questions/0060-field-drains-akusuiro.drawing.html: the turn held to 55 degrees or less"""
    ex, ey = float(b1[0]) - float(b0[0]), float(b1[1]) - float(b0[1])
    el = math.hypot(ex, ey) or 1.0
    start = (float(b0[0]), float(b0[1]))
    run = [start] if lead <= 0 else [start, (start[0] + ex / el * lead, start[1] + ey / el * lead)]
    h, goal = math.atan2(ey, ex), math.atan2(float(fall[1]), float(fall[0]))
    step = math.radians(turn_max)
    while True:
        d = (goal - h + math.pi) % (2 * math.pi) - math.pi
        if abs(d) <= step:
            break
        h += math.copysign(step, d)
        run.append((run[-1][0] + math.cos(h) * leg, run[-1][1] + math.sin(h) * leg))
    run.append((run[-1][0] + float(fall[0]) * reach, run[-1][1] + float(fall[1]) * reach))
    return run
