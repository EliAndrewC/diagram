"""Where a sheet's roads go (feature 294, plan B21 and B23): a road leaves the frame or arrives somewhere, and a road
into a gate is no wider than the gate it feeds.

- `roads_leave_the_frame` (B21): each END of every road meets the viewBox edge, a gate, a door, an arch or another
  road - never a stub stopping short in the open (docs/building-programs.md and the building-review checklist: the approach
  runs "OFF the viewBox edge ... not a stub stopping short"; a MAP DRAWING CONVENTION).
- `gate_feeds_its_road` (B23): a road ending at a side gate (a wall opening the main gate's posts do not stand in) is no
  wider than that opening plus ROAD_GATE_TOL_FT; a road at the main gate is the road the compound stands on, at its own
  width (0088's drawing page, feature 449 T177) (research 0093 'The main gate and its gatekeepers (nagaya-mon)'; the feature 267
  pass 2 rulings recorded on the Hayakawa and Ubame sheets: "12 ft, matching the passage through the gate range it
  meets", "9 ft, matching the narrowed cart gate"). One-sided: a 2 ft footpath to an 8 ft river door is fine.

A road is a stroked path or line the sheet tags `road` or `footpath` (its ink width is its stroke), read with
`tagged.marks`; a road drawn twice (a wash and a dashed rut over it, as every hand sheet draws one) is one road.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from .checks import WallOpening, main_gate_passage_ft, wall_openings
from .grids import FTPX
from .parse import ParsedPlan
from .program_rules import ENTRANCE_KINDS, entrances
from .tagged import Mark, marks

#: The kinds a road is drawn under: the hand manors' `road`, the shrine's `footpath`.
ROAD_KINDS: frozenset[str] = frozenset({"road", "footpath"})
#: The kinds and ids an arch is drawn under (a shrine's way ends at its torii).
ARCH_KINDS: frozenset[str] = frozenset({"torii"})
#: The places a way inside a precinct is walked TO (drawing convention, feature 294 escalation-check 2026-10-01): B21's
#: grounds are an approach stopping short of the frame; a household path from the clearing to the well arrives at both.
DESTINATION_KINDS: frozenset[str] = frozenset({"well", "precinct clearing"})
"""Research: a way walked to a well or clearing - UNRESEARCHED: a way inside a precinct may end at a well or a precinct clearing, the places it is walked to, as a road may end at a gate or a door; which places a path leads to is how the place was lived in, and no page asks it."""
#: A road may be this much wider than the gate it feeds: a GUESS - the 3 px authoring grain (1 ft at 3 px = 1 ft), so a
#: road drawn on the grid next to an opening measured off the ink is not refused for a pixel.
ROAD_GATE_TOL_FT: float = 1.0
"""Research: road wider than gate - NONE: a road may be 1 ft wider than the gate it feeds, the 3 px authoring grain."""
_VIEWBOX = re.compile(r'viewBox="\s*([\-\d.]+)\s+([\-\d.]+)\s+([\d.]+)\s+([\d.]+)\s*"')


@dataclass(frozen=True)
class Road:
    """One road: its points in order and its ink width (px)."""

    pts: tuple[tuple[float, float], ...]
    width: float

    @property
    def half(self) -> float:
        return self.width / 2

    def distance(self, px: float, py: float) -> float:
        """From (px, py) to the road's centerline."""
        if len(self.pts) == 1:
            return math.hypot(px - self.pts[0][0], py - self.pts[0][1])
        return min(_seg(px, py, a, b) for a, b in zip(self.pts, self.pts[1:], strict=False))


def _seg(px: float, py: float, a: tuple[float, float], b: tuple[float, float]) -> float:
    (ax, ay), (bx, by) = a, b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def _box_distance(px: float, py: float, x0: float, y0: float, x1: float, y1: float) -> float:
    return math.hypot(max(x0 - px, 0.0, px - x1), max(y0 - py, 0.0, py - y1))


def roads(svg: str) -> list[Road]:
    """Every road on the sheet, each drawn path once (the widest where one line is inked twice)."""
    out: dict[tuple[tuple[float, float], ...], float] = {}
    for m in marks(svg):
        if m.tag in ("path", "line") and m.kind in ROAD_KINDS and len(m.pts) >= 2:
            out[m.pts] = max(out.get(m.pts, 0.0), m.stroke_width)
    return [Road(pts, w) for pts, w in out.items()]


def opening_box(o: WallOpening) -> tuple[float, float, float, float]:
    """A wall opening's gateway rect (x0, y0, x1, y1): the gap along the wall by the ink's thickness."""
    return (o.span1, o.across1, o.span2, o.across2) if o.horiz else (o.across1, o.span1, o.across2, o.span2)


def gate_passage_box(plan: ParsedPlan) -> tuple[float, float, float, float] | None:
    """The box the `main gate`'s posts bound - its passage and the posts themselves; None without posts."""
    posts = plan.gate_posts
    if not posts:
        return None
    return min(r.x for r in posts), min(r.y for r in posts), max(r.x2 for r in posts), max(r.y2 for r in posts)


def gates_met(end: tuple[float, float], reach: float, plan: ParsedPlan) -> list[float]:
    """The widths (ft) of every gate an end at `end` meets within `reach` px: a wall opening's gateway, the main gate's
    passage."""
    px, py = end
    out = [o.ft for o in wall_openings(plan) if _box_distance(px, py, *opening_box(o)) <= reach]
    box = gate_passage_box(plan)
    ft = main_gate_passage_ft(plan)
    if box is not None and ft is not None and _box_distance(px, py, *box) <= reach:
        out.append(ft)
    return out


def _meets_a_mark(end: tuple[float, float], reach: float, ms: list[Mark]) -> bool:
    return any(_box_distance(end[0], end[1], m.x, m.y, m.x2, m.y2) <= reach for m in ms)


def _frame(svg: str) -> tuple[float, float, float, float] | None:
    """Research:
    its salts, guards and sentinels - NONE: they decide nothing about the place - 5 (regex group range)
    """
    m = _VIEWBOX.search(svg)
    if not m:
        return None
    x, y, w, h = (float(m.group(i)) for i in range(1, 5))
    return x, y, x + w, y + h


def end_meets(end: tuple[float, float], road: Road, others: list[Road], svg: str, plan: ParsedPlan) -> str | None:
    """What the road's end at `end` meets - 'the frame', 'a gate', 'a door', 'an arch', 'a road', 'a well or clearing' - or None.

    Research:
        a road running off the sheet - CONVENTION: a road's end may meet the frame, the approach running off the viewBox edge rather than stopping short, a drawing rule of the building plans; no page gives it.
        where a road arrives - UNRESEARCHED: a road's other end meets a gate, a door, an arch, another road, a well or a clearing, never a dead end in the open; that a way leads somewhere is how the place was laid out, and no page asks it.
    """
    px, py = end
    frame = _frame(svg)
    if frame is not None:
        x0, y0, x1, y1 = frame
        if min(px - x0, x1 - px, py - y0, y1 - py) <= road.half:
            return "the frame"
    if gates_met(end, road.half, plan):
        return "a gate"
    if _meets_a_mark(end, road.half, entrances(svg, plan)):
        return "a door"
    arches = [m for m in marks(svg) if m.kind in ARCH_KINDS or m.ident == "arch"]
    if _meets_a_mark(end, road.half, arches):
        return "an arch"
    if any(o.distance(px, py) <= o.half for o in others):
        return "a road"
    if _meets_a_mark(end, road.half, [m for m in marks(svg) if m.kind in DESTINATION_KINDS]):
        return "a well or clearing"
    return None


def roads_leave_the_frame(svg: str, plan: ParsedPlan) -> list[str]:
    """Each end of every road meets the frame (within half its ink of the edge, or past it), a gate, a door, an arch, or
    another road's ink; an end that meets none is a stub stopping short."""
    rs = roads(svg)
    out: list[str] = []
    for road in rs:
        others = [o for o in rs if o is not road]
        for end in (road.pts[0], road.pts[-1]):
            if end_meets(end, road, others, svg, plan) is None:
                out.append(f"a {road.width / FTPX:.1f} ft road ends at svg({end[0]:.0f},{end[1]:.0f}) in the open - it runs off the frame or arrives at a gate, a door, an arch or another road")
    return out


def _boxes_touch(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    return a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]


def side_gates_met(end: tuple[float, float], reach: float, plan: ParsedPlan) -> list[float] | None:
    """The widths (ft) of every side gate an end at `end` meets within `reach` px - a wall opening that is not the main gate's - or
    None when the end meets the main gate: its passage, or the wall opening its posts stand in (feature 449 T177).

    Research:
        the road at the front gate at its own width - research/questions/0088-highways-and-what-lines-them-kaido.drawing.html: the road at a compound's front gate is the road the compound stands on, at that road's width, so an end meeting the main gate's passage, or the wall opening its posts stand in, is not held to a side gate's width
    """
    px, py = end
    box = gate_passage_box(plan)
    if box is not None and main_gate_passage_ft(plan) is not None and _box_distance(px, py, *box) <= reach:
        return None
    out: list[float] = []
    for o in wall_openings(plan):
        if _box_distance(px, py, *opening_box(o)) > reach:
            continue
        if box is not None and _boxes_touch(opening_box(o), box):
            return None
        out.append(o.ft)
    return out


def gate_feeds_its_road(svg: str, plan: ParsedPlan, tol_ft: float = ROAD_GATE_TOL_FT) -> list[str]:
    """A road ending at a side gate is no wider than the widest side gate that end meets, plus `tol_ft`; a road at the main gate
    is the road the compound stands on, at its own width, and is not judged here (feature 449 T177: it was refused when wider
    than the main gate, against 0088's drawing page).

    Research:
        a lane no wider than its side gate - GUESS research/questions/0088-highways-and-what-lines-them-kaido.drawing.html: a lane ending at a side gate or a cart gate is no wider than the widest such opening it meets, plus the claimed tolerance; the page draws a lane to a side gate or cart gate about 6 ft where carts use it, a GUESS, and records that no page gives the width of a lane to a side gate.
        the road at the front gate at its own width - research/questions/0088-highways-and-what-lines-them-kaido.drawing.html: the road at a compound's front gate is the road the compound stands on, at that road's width, so a road meeting the main gate's passage, or the wall opening its posts stand in, is not held to the gate's width.
    """
    out: list[str] = []
    for road in roads(svg):
        for end in (road.pts[0], road.pts[-1]):
            met = side_gates_met(end, road.half, plan)
            w_ft = road.width / FTPX
            if met and w_ft > max(met) + tol_ft:
                out.append(f"a {w_ft:.1f} ft road meets a {max(met):.1f} ft side gate at svg({end[0]:.0f},{end[1]:.0f}) - a lane is no wider than the side gate it feeds")
    return out


__all__ = ["ENTRANCE_KINDS", "Road", "gate_feeds_its_road", "roads", "roads_leave_the_frame"]
