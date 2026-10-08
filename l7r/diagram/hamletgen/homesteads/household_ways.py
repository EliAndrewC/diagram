"""THE TRACK OUT, CHOSEN ONCE THE LAST HOUSE STANDS, AND THE HOUSEHOLDS' WAYS LAID TO IT (feature 320, plan D2, FR-008).

The GM, 2026-10-04, of the exit strip and the field's corridor the seating used to reserve before any house: *"we should
eliminate both ... because the space we've already allocated can serve the same function"*. So nothing of a way is laid or
reserved while the farmhouses are seated - the lane's room between neighbors (feature 318) is what keeps a way possible.

Once the last house stands, the track out's whole course is chosen ONCE (`track.choose_track_out`), the GM: *"collapsing the
multiple decisions into a single decision regarding the lane"* - a first leg decided on the seating's bearing apart from the
track's own route met a household's way in a nub. No farmstead is drawn yet (the overlap registry would refuse a way on a
drawn yard), so the homesteads as seated stand in for them (`seated_parts`, read by `fabric._homestead_polys`), with every
household's wood seats. Each household's way is then laid in the gaps to the track's stretch about the cluster
(`near_the_cluster`, `gap_ways.lay_the_ways`), and `stage_track` draws the track as chosen.

Research: houses before lanes - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: every farmhouse seated before any way is laid; the track out leaves from the cluster's edge and each household's way joins it
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING

from l7r.diagram.settlement.homestead_parts.groves import crown_lift
from l7r.diagram.settlement.homestead_parts.stands import crown_reach
from l7r.diagram.settlement.homestead_parts.wood_share import COPSE_CLUMP_BS

from ..consts import Poly, Pt
from .region import _clip

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from ..plan import SitePlan


def box_poly(b: Sequence[float]) -> Poly:
    """A box `(cx, cy, w, h)` as its four corners.

    Research: plumbing - NONE: a box's corners"""
    x0, y0, x1, y1 = b[0] - b[2] / 2, b[1] - b[3] / 2, b[0] + b[2] / 2, b[1] + b[3] / 2
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def seat_walls(s: Settlement) -> tuple[list[Pt], float]:
    """Every household's reserved wood seats and the reach a lane keeps off each: the buffer the registry reserves them with
    (`stages.reserve_the_seating`) and half the track's tread.

    Research: the track off the wood seats - UNRESEARCHED: a lane kept off a household's copse seat by the crown's reach (or 0.45 of the clump and 4 ft) and 4 ft more; the record keeps the copse off the main road, not the reverse"""
    clump = COPSE_CLUMP_BS * s.bscale
    reach = max(clump * 0.45 + 4, crown_reach(clump, 0.0, lift=crown_lift(s.bscale))) + 4.0
    seats = [(float(p[0]), float(p[1])) for h in s.M.get("houses") or [] for p in (h.get("wood_share") or {}).get("seats") or ()]
    return seats, reach


TRUNK_FT = 4.0
"""A persimmon's trunk box, the part of it a way keeps off (`access.fixtures_clear` holds it the same).

Research: a persimmon by its trunk alone - GUESS: held off by a 4 ft trunk box, the crown free to overhang the path"""


def seated_parts(s: Settlement) -> list[tuple[Poly, Pt | None, str]]:
    """The homesteads as seated, before any is drawn, as `fabric._homestead_polys` reads the drawn ones - (polygon, owner,
    kind): each household's house, threshing yard, beds, well, shed, byre and fixtures from its seated geometry (a persimmon
    by its trunk), and its wood seats as octagons of the reach a lane keeps off them (`seat_walls`).

    Research:
        nothing built on a lane - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the track out keeps off every homestead's house, yard, beds, well, sheds and fixtures as they will be drawn
        the track off the wood seats - UNRESEARCHED: each seat an octagon of the reach a lane keeps off it (`seat_walls`)
        a persimmon by its trunk alone - GUESS: held off by `TRUNK_FT`, the crown free to overhang the track"""
    out: list[tuple[Poly, Pt | None, str]] = []
    for h in s.M.get("houses") or []:
        boxes = (h.get("geom") or {}).get("boxes") or {}
        own = (float(h["x"]), float(h["y"]))
        for key, kind in (("house", "houses"), ("yard", "threshing_yards"), ("well", "wells"), ("shed", "sheds"), ("byre", "sheds")):
            if boxes.get(key) is not None:
                out.append((box_poly(boxes[key]), own, kind))
        out += [(box_poly(b), own, "gardens") for b in boxes.get("gardens") or ()]
        for name, b in (boxes.get("fixtures") or {}).items():
            out.append((box_poly(b if name != "persimmon" else (b[0], b[1], s.px(TRUNK_FT), s.px(TRUNK_FT))), own, "fixtures"))
    seats, reach = seat_walls(s)
    ring = [(math.cos(k * math.pi / 4.0), math.sin(k * math.pi / 4.0)) for k in range(8)]
    out += [([(p[0] + c * reach, p[1] + d * reach) for c, d in ring], None, "wood seats") for p in seats]
    return out


def near_the_cluster(s: Settlement, track: Poly, margin: float) -> list[tuple[Pt, Pt]]:
    """The legs of `track` within `margin` of the seated homesteads' extent and the track's start, each clipped to it (`region._clip`): the stretch the
    households' ways are laid to. The stages ask it at the gap pass's farther join reach (`gap_ways.JOIN_FAR_FT`): at the
    raster's 160 ft margin a household's way joined the track 26 ft past the cropped frame, two paths leaving the map side by
    side (Inashiro's glyph check, feature 320) - the frame is cropped later, about the homesteads' own extent.

    Research: plumbing - NONE: the search's window on the track"""
    boxes = list(getattr(s, "placed", None) or [])
    if not boxes:
        return list(zip(track, track[1:], strict=False))
    # ...AND THE TRACK'S START, its gateway off the cluster's edge: Kuwabata's stood 51 ft off its homesteads and ran on along
    # them, so a window of the homesteads alone held none of the track and no way could be laid
    g = track[0] if track else (boxes[0][0], boxes[0][1])
    box = (
        min(g[0], *(b[0] - b[2] / 2 for b in boxes)) - margin,
        min(g[1], *(b[1] - b[3] / 2 for b in boxes)) - margin,
        max(g[0], *(b[0] + b[2] / 2 for b in boxes)) + margin,
        max(g[1], *(b[1] + b[3] / 2 for b in boxes)) + margin,
    )
    out = []
    for a, b in zip(track, track[1:], strict=False):
        span = _clip(a, b, box)
        if span is not None and span[1] > span[0]:
            out.append(((a[0] + (b[0] - a[0]) * span[0], a[1] + (b[1] - a[1]) * span[0]), (a[0] + (b[0] - a[0]) * span[1], a[1] + (b[1] - a[1]) * span[1])))
    return out


def chose_the_track(s: Settlement, plan: SitePlan) -> Poly:
    """The track out chosen once the last house stands (`track.choose_track_out`), with the homesteads as seated standing in
    for the farmsteads not yet drawn (`seated_parts`).

    Research: the track out decided once - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each household's way joins the track out"""
    from ..ways.track import choose_track_out  # the ways' layer sits above the homesteads; asked here once the houses stand

    s._seated_parts = seated_parts(s)  # type: ignore[attr-defined]
    try:
        return choose_track_out(s, plan)
    finally:
        s._seated_parts = None  # type: ignore[attr-defined]
