"""STAGE 4a's Python half: what the seat and the house seating share - the way out's walls and its test, the seat's refusal -
and the skeleton's arm helpers. The seat itself is the Rust stage (`seat_stage`, `rust/phases/src/seat/`, feature 444 T27).

Split from hamletgen.py by feature 111. See hamletgen/CLAUDE.md.

Research: seat geometry - NONE: ray tests, polyline crossings and the refusal type
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from l7r.diagram import work_counts
from l7r.diagram.settlement import seg_intersect

from .consts import Poly, Pt
from .plan import SitePlan

# ---- STAGE 4: seating the settlement, and its ways ----------------------------------------------


def exit_walls(plan: SitePlan, toe: Poly | None = None, wet: Sequence[Poly] = ()) -> tuple[list[tuple[Poly, float]], list[tuple[Pt, Pt]]]:
    """The walls and the water lines a seat's dry way out keeps off (feature 287, ways W23), as `connector_dry_exit` walls them:
    the wet toe and the reed fringe grown by the lane's width, the field, the tameike at its 80 ft berth; the drain's run and
    every watercourse (the brook gapped at its fords) are lines it may not cross. Read by the seat (`seat_stage`) and by each
    ladder rung the house seating falls back to (`seat_has_dry_exit`).

    Research:
        the way out's walls - research/questions/0081-village-lanes.drawing.html: a track keeps off wet ground and runs off the map - the wet toe and the reed fringe grown by the lane's width, the field, the pond at its berth; the drain's run and every watercourse lines it may not cross
        no watercourse crossed off its fords - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: a way crosses the brook only at a crossing place, so the way out may not cross the brook or a watercourse it feeds
        tameike berth - GUESS: searched, the record silent (feature 417 T29 pass B, 2026-10-25); 80 ft
        its polygon - NONE: they decide nothing about the place - 16 (pond disc drawn as a 16-gon)
        its salts, guards and sentinels - NONE: they decide nothing about the place - 8 (pi/8 step of the same 16-gon)
    """
    from .ways.track import wet_grown_by_the_lane

    walls: list[tuple[Poly, float]] = [(wet_grown_by_the_lane(w), 0.0) for w in [*([toe] if toe else []), *wet] if len(w) >= 3]
    if __debug__:
        work_counts.OPS["moved@exit_walls"] += sum(len(w) for w, _ in walls)
    walls.append((list(plan.envelope), 0.0))
    if plan.sink_pond:
        px, py, rx, ry = plan.sink_pond
        r = max(rx, ry)
        walls.append(([(px + r * math.cos(k * math.pi / 8), py + r * math.sin(k * math.pi / 8)) for k in range(16)], 80.0))
    lines = [(plan.sink_brook[i], plan.sink_brook[i + 1]) for i in range(len(plan.sink_brook) - 1)] + list(plan.watercourses)
    return walls, lines


def seat_has_dry_exit(plan: SitePlan, start: Pt, toe: Poly | None = None, wet: Sequence[Poly] = ()) -> bool:
    """Has a seat at `start` a dry way out of the frame (feature 287, homes; ways W23)? The connector leaves the cluster by
    the flood fill `dry_exit` when no bearing is clean, and raises `NoDryExit` where the gateway is walled in - a property of
    the SEAT, so a ladder rung the house seating falls back to is refused here (the seat asks its head in Rust). Asked with
    what stands at seat time (`exit_walls`). The ONE flood fill, WAYS' own.

    Research:
        dry way out of the seat - research/questions/0081-village-lanes.drawing.html: lanes keep to dry ground
    """
    from .ways.dry_exit import EXIT_CELL_FT, dry_exit

    walls, lines = exit_walls(plan, toe, wet)
    if straight_exit(start, walls, lines, float(plan.W), float(plan.H), EXIT_CELL_FT):
        return True
    return dry_exit(start, walls, lines, float(plan.W), float(plan.H)) is not None


#: The straight exits the fast path tries: every 22.5 degrees.
EXIT_BEARINGS = 16


def straight_exit(start: Pt, walls: Sequence[tuple[Poly, float]], lines: Sequence[tuple[Pt, Pt]], W: float, H: float, cell: float) -> bool:
    """A SUFFICIENT test for `dry_exit`, asked first because the flood fill costs a canvas (feature 287): a straight run
    from `start` off the canvas that keeps every wall at its margin plus one and a half cells, and every water line at
    one and three quarter cells. Every cell such a run passes through then has its center clear of the fill's own
    blocking distances (a wall's margin plus half a cell's diagonal, a line's one cell), and the cells a straight run
    passes through are joined, so the fill would find its way out along it. False says nothing: the fill decides.

    Research:
        its margins - NONE: they decide nothing about the place - 1.75 (water-line margin in cells, so the quick test is sufficient for the flood fill); 1.5 (wall margin in cells, the same)
    """
    from shapely import LineString, Polygon

    polys = [(Polygon(p), m) for p, m in walls if len(p) >= 3]
    segs = [LineString([a, b]) for a, b in lines]
    for k in range(EXIT_BEARINGS):
        dx, dy = math.cos(math.tau * k / EXIT_BEARINGS), math.sin(math.tau * k / EXIT_BEARINGS)
        run = min(((W if dx > 0 else 0.0) - start[0]) / dx if abs(dx) > 1e-9 else math.inf, ((H if dy > 0 else 0.0) - start[1]) / dy if abs(dy) > 1e-9 else math.inf) + 2.0 * cell
        ray = LineString([start, (start[0] + dx * run, start[1] + dy * run)])
        if all(p.distance(ray) >= m + 1.5 * cell for p, m in polys) and all(s.distance(ray) >= 1.75 * cell for s in segs):
            return True
    return False


class SeatRefused(ValueError):
    """No field margin turns the settlement's back to the wind on legal ground (feature 287, homes H30, plan D3): the site
    is refused at `stage_seat`, naming it, before any house exists - never seated off the wind."""


def _arm_hit(a: Poly, b: Poly) -> Pt | None:
    """The first PROPER mid-run crossing point of two polylines - a touch at a segment
    endpoint is a JUNCTION, not a crossing, and returns nothing. Returning the POINT rather
    than a bool matters: raw skeletons may cross by design (a stem poked through its bar, the
    'cross' layout's crossbar over its spine), so "the raw pair crosses somewhere" cannot
    license a clipped crossing ANYWHERE - Kashikawa's two clipped arms X-ed 87 px out in open
    ground while their raw junction sat at the hub, and the existence test waved it through
    (2026-08-16). A clipped crossing is designed only where the raw one is."""
    for i in range(len(a) - 1):
        for j in range(len(b) - 1):
            _h = seg_intersect(a[i], a[i + 1], b[j], b[j + 1])
            if _h is not None and all(math.dist(_h, q) > 2.0 for q in (a[i], a[i + 1], b[j], b[j + 1])):
                return _h
    return None


def _arm_crossing_accidental(arm: Poly, raw: Poly, kept: list[tuple[Poly, Poly]]) -> bool:
    """AN ARM MAY NOT CROSS A SIBLING ANYWHERE THE LAYOUT DOES NOT (settlement-review, Sawada
    2026-08-16): the clip pipeline bends each arm independently, and two of a Y's arms came back
    CROSSING mid-run in open ground, near-superimposed for ~250 ft. A clipped crossing is designed
    only where the RAW pair crosses within ~40 px of it - existence alone is not enough, since a
    raw stem poked through its bar "crosses" at the hub while the clipped X sat 87 px away.

    Research: arms cross only where the layout does - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass B, 2026-10-25); within 40 ft of the raw crossing"""
    for k_arm, k_raw in kept:
        _h = _arm_hit(arm, k_arm)
        if _h is None:
            continue
        _hr = _arm_hit(raw, k_raw)
        if _hr is None or math.dist(_h, _hr) > 40.0:
            return True
    return False
