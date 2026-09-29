"""THE ROW VILLAGE'S STREETS (feature 291 amendment 3, plan D17; research/homesteads/155 and 156) - each street the row
seating planned (`homesteads/rows.py`, `s._row_streets`) laid as ONE continuous way along its row, a rank wider than
the lanes off it, joined to the connector or to the street before it; and each row farm's way ending on its OWN street.

A layer between `serve` (the door paths) and `web` (the stage that calls it).
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, seg_closest, seg_dist

from ..consts import FOOTPATH_FABRIC_GAP, Poly, Pt
from .fabric import _crosses_fabric, _draw_web
from .route import _route

STREET_WIDTH = 6
"""The street's tread: the connector's, a rank wider than the web's 3-5 lanes (FR-017)."""

_VERTEX_FT = 40.0
"""The street's vertex spacing once laid: the planned line is sampled every 8 ft; a worn way keeps a vertex every two
treads' lengths or so - a map drawing convention."""


def street_span(line: Sequence[Pt], houses: Sequence[Pt], reach: float, pad: float) -> list[Pt]:
    """The stretch of a planned street its farms stand along: from the first farm's projection less `pad` to the last's
    plus `pad`, over the farms within `reach` of the line; [] when no farm is. The line's own vertices are kept, thinned to
    `_VERTEX_FT`."""
    if len(line) < 2:
        return []
    arc = [0.0]
    for a, b in zip(line, line[1:], strict=False):
        arc.append(arc[-1] + math.dist(a, b))
    along: list[float] = []
    for h in houses:
        best = min(((seg_dist(h[0], h[1], a, b), i) for i, (a, b) in enumerate(zip(line, line[1:], strict=False))), key=lambda t: t[0])
        if best[0] > reach:
            continue
        i = best[1]
        q = seg_closest(h[0], h[1], line[i], line[i + 1])
        along.append(arc[i] + math.dist(line[i], q))
    if not along:
        return []
    lo, hi = max(0.0, min(along) - pad), min(arc[-1], max(along) + pad)
    idx = [i for i, u in enumerate(arc) if lo <= u <= hi]
    kept: list[int] = []
    for i in idx:
        if not kept or arc[i] - arc[kept[-1]] >= _VERTEX_FT:
            kept.append(i)
    if idx and kept[-1] != idx[-1]:
        kept.append(idx[-1])  # the stretch ends where its last farm does, not at the last whole vertex step
    return [line[i] for i in kept]


def thread(path: Sequence[Pt], walls: Sequence[Poly], hard: list[Poly], water: list[tuple[Pt, Pt]], half: float = STREET_WIDTH / 2 + 1.0) -> list[Pt]:
    """`path` with every leg whose TREAD - `half` either side of the line - meets a steading replaced by a route round it
    (`_route`, a footpath's gap) between the clear vertices either side; a vertex whose tread meets one is dropped. The
    street stays one way. (Tested at the centerline, a street grazed a grove band with its drawn tread - cohort seed 904.)"""
    clear = [p for p in path if not _crosses_fabric([p, p], walls, half)]
    if len(clear) < 2:
        return list(clear)
    out: list[Pt] = [clear[0]]
    for a, b in zip(clear, clear[1:], strict=False):
        if _crosses_fabric([a, b], walls, half):
            # routed at the STREET's gap, not a footpath's: a detour at 4 ft ran 3 ft off a grove band, inside the 6 ft tread
            # (cohort seed 23); a leg still grazing is routed once more a foot wider
            leg = _route(a, b, hard, walls, water, gap=half + 1.0)
            if len(leg) >= 2 and _crosses_fabric(leg, walls, half):
                leg = _route(a, b, hard, walls, water, gap=half + 3.0)
            out += leg[1:] if len(leg) >= 2 else [b]
        else:
            out.append(b)
    return out


def join_to(path: list[Pt], network: Sequence[tuple[Pt, Pt]], hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> list[Pt]:
    """`path` extended from whichever of its ends is nearer the `network` to the nearest point on it, routed round the
    steadings; unchanged when the network is empty, already touched, or no route is found."""
    if len(path) < 2 or not network:
        return path

    def near(p: Pt) -> tuple[float, Pt]:
        return min(((seg_dist(p[0], p[1], a, b), seg_closest(p[0], p[1], a, b)) for a, b in network), key=lambda t: t[0])

    (d0, q0), (d1, q1) = near(path[0]), near(path[-1])
    if min(d0, d1) < 1.0:
        return path
    if d0 <= d1:
        leg = _route(q0, path[0], hard, walls, water, gap=FOOTPATH_FABRIC_GAP)
        return (leg[:-1] + path) if len(leg) >= 2 else path
    leg = _route(path[-1], q1, hard, walls, water, gap=FOOTPATH_FABRIC_GAP)
    return (path + leg[1:]) if len(leg) >= 2 else path


def lay_row_streets(s: Settlement, houses: Sequence[Mapping[str, Any]], hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]], reach: float, pad: float) -> int:
    """Lay each planned street of `s._row_streets` as one way: its farms' stretch (`street_span`), threaded round any
    steading in its way (`thread`), joined to the connector or a street already laid (`join_to`), drawn at the street's
    tread and recorded `street` with its index. Returns the streets drawn."""
    centers = [(float(h["x"]), float(h["y"])) for h in houses]
    n = 0
    for k, line in enumerate(getattr(s, "_row_streets", None) or []):
        path = thread(street_span(line, centers, reach, pad), walls, hard, water)
        net = [(tuple(a), tuple(b)) for ln in s.M.get("lanes", []) if ln.get("connector") or ln.get("street") for a, b in zip(ln["pts"], ln["pts"][1:], strict=False)]
        path = join_to(path, net, hard, walls, water)  # type: ignore[arg-type]
        if len(path) >= 2 and _draw_web(s, path, STREET_WIDTH, houses=centers):
            s.M["lanes"][-1]["street"] = True
            s.M["lanes"][-1]["street_index"] = k
            n += 1
    return n
