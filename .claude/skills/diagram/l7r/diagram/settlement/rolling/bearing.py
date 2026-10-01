"""Which way a farmhouse faces (269 B18): the village's common bearing and the spread about it, following its lane.

research/homesteads.html "Farmhouses (minka)" (its map rules at research/rendering/homesteads.html "How our maps draw farmhouses (minka)"): a survey of 27 villages found each
village's main houses spread over its commonest compass point and the point either side of it - three of sixteen, some
67 degrees - the neighboring bearings arising where the roads curve; 87% faced within that spread and 11% were turned to
the right. The rule the map follows: each farmhouse is turned from its village's common bearing, south or near it, by up
to about 30 degrees either way, most by much less and following the lane it stands on where the lane curves, and its yard
and garden beds turn with it (the GM's ruling of 2026-09-26). THE QUARTER-TURNED TENTH IS NOT DRAWN (feature 280 M26,
research/homesteads.html "Farmhouses (minka)"): the survey's right-turned 11% is a count of 1974-1984 with no count before 1868 beside it, while
the cause the survey gives for the smaller turns - streets curving along the slope - is attested in an Okinawan village laid
out in 1736, so the turn follows the lane and no house is turned a quarter away.

POSITION-PURE, as the rake always was (`Settlement._house_rot`): the placer must know the exact quad it will draw before
it commits a seat, so every term here is a function of the seat's coordinates and of what the map held before the first
house was seated - never of how many houses came before.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Any

from .._geom import PointGrid, Pt, turn_about

# ATTESTED (homesteads/400): three points of the compass span some 67 degrees, so a house may stand about 30 degrees from
# its neighbors' common bearing and still face with them.
BEARING_SPREAD_DEG = 30.0

# GUESS (homesteads/400: "how the turns spread inside that range is a GUESS", "most by much less"): a triangular spread of
# +-12 degrees about the lane's own bearing - its mode at the lane, one house in four more than 6 degrees off it - so a
# village reads as turned by eye rather than surveyed, and the 30 degree edge is reached where the lane itself curves.
BEARING_JITTER_DEG = 12.0
# GUESS on how near "south or near it" is (homesteads/400): the common bearing is rolled within half a compass point of
# south, so it still reads as the south point of the sixteen - and past that the survey's own example turned a whole
# village a quarter away from the fall of its ground, which is a slope this map does not draw.
COMMON_BEARING_DEG = 11.25
# How much of the margin a house reads as "the lane it stands on", in px either side of its nearest margin point: about
# half a bundle pitch each way, so one ragged outline vertex does not turn a house, and a bend the width of two homesteads
# does. A map drawing convention.
FOLLOW_HALF_SPAN_PX = 48.0
_SAMPLE_PX = 8.0
# A house within FOLLOW_FULL_PX of the margin stands on the lane that runs along it and follows its whole turn; past
# that the pull fades to nothing at FOLLOW_REACH_PX, so a house two rows back follows the lanes of its own row rather
# than a field edge it cannot see. About one homestead bundle deep, then a second; a map drawing convention. The first
# version followed the margin out to 400 px at full strength, and the settlement-review of Sawada at the 269 landing
# (2026-09-28) found houses 340-400 ft off the margin turned by it, 9 of 16 of them at the spread's edge.
FOLLOW_FULL_PX = 96.0
FOLLOW_REACH_PX = 240.0
# The per-house draws key on the seat rounded to this many px (a map drawing convention): a front-row seat moved a pixel or
# two by the rake's own reach keeps the rake it was moved for.
KEY_CELL_PX = 4.0


def wrap_line_deg(d: float) -> float:
    """An undirected line's angle folded into [-90, 90): a lane has no front or back, so 170 degrees is -10."""
    return (d + 90.0) % 180.0 - 90.0


def wrap_square_deg(d: float) -> float:
    """A lane's turn as a rectangular house follows it, folded into [-45, 45): a house stands square to its lane with
    its front or with its gable, so a lane at 80 degrees to the axis turns the house -10, not 80 - which the spread
    would only have clamped to its edge (the pile-up at +-30 the Sawada review found)."""
    return (d + 45.0) % 90.0 - 45.0


def soft_limit(d: float, limit: float) -> float:
    """`d` held inside +-`limit` by a smooth curve: near zero it is `d` itself, and it approaches the limit without
    reaching it, so turns that run past the edge spread under it instead of piling on it."""
    return limit * math.tanh(d / limit)


class MarginBearing:
    """How far the lane a house stands on has turned from the settlement's own axis, at any point - built once.

    THE LANES DO NOT EXIST YET when a house is seated (feature 126: every lane is worn after the houses), so the lane a
    house stands on is read from the line the lanes are laid along: the field margin, which the front row follows and
    the back lanes of the web are laid on (`stage_web`, "a straight one parallels a curved field edge"). That the web
    follows the margin is the engine's; that a house turns with the margin's bend before any lane is drawn is a map
    drawing convention standing in for the record's "following the lane it stands on where the lane curves".

    The ring is sampled every 8 px into a `PointGrid`; a query asks the grid for the nearest sample and reads the chord
    across `FOLLOW_HALF_SPAN_PX` either side of it - no scan of the ring per candidate (dev/performance.md)."""

    def __init__(self, ring: Sequence[Pt], along_deg: float) -> None:
        pts = [(float(a), float(b)) for a, b in ring]
        self.along = along_deg
        self.samples: list[Pt] = []
        n = len(pts)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            seg = math.dist(a, b)
            k = max(1, int(seg // _SAMPLE_PX))
            self.samples.extend((a[0] + (b[0] - a[0]) * t / k, a[1] + (b[1] - a[1]) * t / k) for t in range(k))
        self.grid = PointGrid(64.0)
        self.grid.extend((i, x, y, x, y) for i, (x, y) in enumerate(self.samples))
        self.span = max(1, int(FOLLOW_HALF_SPAN_PX // _SAMPLE_PX))

    def nearest(self, x: float, y: float) -> int | None:
        """The index of the ring sample nearest (x, y) within `FOLLOW_REACH_PX`, or None."""
        pad = 64.0
        while pad <= FOLLOW_REACH_PX * 2:
            near = [it for it in self.grid.near(x, y, pad) if math.hypot(it[1] - x, it[2] - y) <= pad]
            if near:
                best = min(near, key=lambda it: (math.hypot(it[1] - x, it[2] - y), it[0]))
                return None if math.hypot(best[1] - x, best[2] - y) > FOLLOW_REACH_PX else int(best[0])
            pad *= 2.0
        return None

    def __call__(self, x: float, y: float) -> float:
        """How far the margin nearest (x, y) turns a house standing there, in degrees: its turn from the settlement's
        axis folded square (`wrap_square_deg`), in full within `FOLLOW_FULL_PX` of it and fading to 0.0 at
        `FOLLOW_REACH_PX`; 0.0 out of its reach."""
        k = self.nearest(x, y)
        if k is None or len(self.samples) < 3:
            return 0.0
        n = len(self.samples)
        a, b = self.samples[(k - self.span) % n], self.samples[(k + self.span) % n]
        turn = wrap_square_deg(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) - self.along)
        d = math.dist((x, y), self.samples[k])
        return turn * max(0.0, min(1.0, (FOLLOW_REACH_PX - d) / (FOLLOW_REACH_PX - FOLLOW_FULL_PX)))


def house_rot(jit: Callable[[float, float, float], float], x: float, y: float, common: float, follow: Callable[[float, float], float] | None) -> float:
    """The full turn a farmhouse seated at (x, y) is drawn at, in degrees: the village's common bearing, the lane's turn
    and the house's own by-eye spread (together held inside `BEARING_SPREAD_DEG` by `soft_limit`, so turns that would run
    past the edge spread under it rather than all standing on it). `jit` is the settlement's position-seeded draw
    (`Settlement._hjit`)."""
    kx, ky = round(x / KEY_CELL_PX) * KEY_CELL_PX, round(y / KEY_CELL_PX) * KEY_CELL_PX
    spread = (jit(kx, ky, 11.0) + jit(kx, ky, 14.0) - 1.0) * BEARING_JITTER_DEG  # triangular: most houses near the lane
    lane = follow(x, y) if follow is not None else 0.0
    return common + soft_limit(lane + spread, BEARING_SPREAD_DEG)


def turned_box(rect: Any, rot: float) -> tuple[float, float, float, float]:
    """The axis-aligned box of `rect` (cx, cy, w, h) as DRAWN, turned by `rot` about its own center (its center already
    carried round the house by `_rake_parts`): the ground a fit rule clears for a turned part."""
    x, y, w, h = float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3])
    th = math.radians(rot)
    c, s = abs(math.cos(th)), abs(math.sin(th))
    return (x, y, w * c + h * s, w * s + h * c)


def turned_reach(box: tuple[float, float, float, float], rot: float, toward: Pt) -> float:
    """How far a homestead's core box (left, top, right, bottom about the house center) reaches along the unit vector
    `toward` once turned by `rot` about the house center - the front row's standoff for a turned homestead."""
    left, top, right, bottom = box
    corners = turn_about([(left, top), (right, top), (right, bottom), (left, bottom)], 0.0, 0.0, rot)
    return max(px * toward[0] + py * toward[1] for px, py in corners)
