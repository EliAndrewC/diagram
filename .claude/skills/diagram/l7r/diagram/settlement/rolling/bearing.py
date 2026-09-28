"""Which way a farmhouse faces (269 B18): the village's common bearing, the spread about it, and the quarter-turned tenth.

research/homesteads/240 ("Why do a village's farmhouses face different ways ..."): a survey of 27 villages found each
village's main houses spread over its commonest compass point and the point either side of it - three of sixteen, some
67 degrees - the neighboring bearings arising where the roads curve; 87% faced within that spread and 11% were turned to
the right. The rule the map follows: each farmhouse is turned from its village's common bearing, south or near it, by up
to about 30 degrees either way, most by much less and following the lane it stands on where the lane curves; about one in
ten is turned a quarter turn to one side, and its yard and garden beds turn with it (the GM's ruling of 2026-09-26).

POSITION-PURE, as the rake always was (`Settlement._house_rot`): the placer must know the exact quad it will draw before
it commits a seat, so every term here is a function of the seat's coordinates and of what the map held before the first
house was seated - never of how many houses came before.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Any

from .._geom import PointGrid, Pt, turn_about

# ATTESTED (homesteads/240): three points of the compass span some 67 degrees, so a house may stand about 30 degrees from
# its neighbors' common bearing and still face with them.
BEARING_SPREAD_DEG = 30.0
# ATTESTED share (homesteads/240: 11% turned to the right); drawing that class as ONE quarter turn is the record's GUESS -
# the survey's right-turned class runs over several compass points.
QUARTER_TURN_SHARE = 0.10
# To the RIGHT: a house facing south that turns to its right faces west, and +90 in `rot_rect`'s sense (SVG's `rotate`,
# y down) carries the yard from the south front to the west.
QUARTER_TURN_DEG = 90.0
# GUESS (homesteads/240: "how the turns spread inside that range is a GUESS", "most by much less"): a triangular spread of
# +-12 degrees about the lane's own bearing - its mode at the lane, one house in four more than 6 degrees off it - so a
# village reads as turned by eye rather than surveyed, and the 30 degree edge is reached where the lane itself curves.
BEARING_JITTER_DEG = 12.0
# GUESS on how near "south or near it" is (homesteads/240): the common bearing is rolled within half a compass point of
# south, so it still reads as the south point of the sixteen - and past that the survey's own example turned a whole
# village a quarter away from the fall of its ground, which is a slope this map does not draw.
COMMON_BEARING_DEG = 11.25
# How much of the margin a house reads as "the lane it stands on", in px either side of its nearest margin point: about
# half a bundle pitch each way, so one ragged outline vertex does not turn a house, and a bend the width of two homesteads
# does. A map drawing convention.
FOLLOW_HALF_SPAN_PX = 48.0
_SAMPLE_PX = 8.0
# A house further than this from every margin sample follows nothing: it is not on a lane that runs along the field.
FOLLOW_REACH_PX = 400.0
# The per-house draws key on the seat rounded to this many px (a map drawing convention): a front-row seat moved a pixel or
# two by the rake's own reach keeps the rake it was moved for.
KEY_CELL_PX = 4.0


def wrap_line_deg(d: float) -> float:
    """An undirected line's angle folded into [-90, 90): a lane has no front or back, so 170 degrees is -10."""
    return (d + 90.0) % 180.0 - 90.0


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
        """The margin's turn from the settlement's axis at the point nearest (x, y), in degrees; 0.0 out of its reach."""
        k = self.nearest(x, y)
        if k is None or len(self.samples) < 3:
            return 0.0
        n = len(self.samples)
        a, b = self.samples[(k - self.span) % n], self.samples[(k + self.span) % n]
        return wrap_line_deg(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) - self.along)


def house_rot(jit: Callable[[float, float, float], float], x: float, y: float, common: float, follow: Callable[[float, float], float] | None, share: float) -> float:
    """The full turn a farmhouse seated at (x, y) is drawn at, in degrees: the village's common bearing, the lane's turn
    and the house's own by-eye spread (together held within `BEARING_SPREAD_DEG`), and a quarter turn on one house in
    `1 / share`. `jit` is the settlement's position-seeded draw (`Settlement._hjit`)."""
    kx, ky = round(x / KEY_CELL_PX) * KEY_CELL_PX, round(y / KEY_CELL_PX) * KEY_CELL_PX
    spread = (jit(kx, ky, 11.0) + jit(kx, ky, 14.0) - 1.0) * BEARING_JITTER_DEG  # triangular: most houses near the lane
    lane = follow(x, y) if follow is not None else 0.0
    rake = max(-BEARING_SPREAD_DEG, min(BEARING_SPREAD_DEG, lane + spread))
    quarter = QUARTER_TURN_DEG if jit(kx, ky, 13.0) < share else 0.0
    return common + rake + quarter


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
