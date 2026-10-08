"""A seat's geometry and the cluster's drawn shape, split from `stages.py` (feature 316): how far a box moves off the water,
how far a turned house's seat moves out, which bank of the brook a point stands on, and the cluster shape the houses draw.
Bodies moved verbatim; `stages.py` re-exports every name, so callers and tests are unchanged.

Research: seat geometry - NONE: distances, sides and aspects measured; the rules that decide are each unit's own"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, seg_dist
from l7r.diagram.settlement.rolling.bearing import turned_reach

from ..consts import CLUSTER_DRAWN_ASPECT, CLUSTER_SHAPES, Pt
from ..plan import _roll
from .seats import cluster_aspect


def water_push(water: Sequence[tuple[Pt, Pt, float]], center: Pt, n: Pt, half_lat: float, near: float, far: float) -> float:
    """How far a box must move along `n` so that no water course (`(a, b, clearance)` segments) lies within its clearance
    of the box: the box spans `near`-`far` along `n` and `half_lat` either side of `center` across it. Zero when clear.
    Each segment is sampled every 8 ft, which is finer than any clearance the courses carry (half-width + 5)."""
    lx, ly = -n[1], n[0]
    push = 0.0
    for a, b, clr in water:
        if seg_dist(center[0], center[1], a, b) > half_lat + (far - near) + clr:
            continue
        k = max(1, int(math.dist(a, b) / 8.0))
        for j in range(k + 1):
            x, y = a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k
            if abs((x - center[0]) * lx + (y - center[1]) * ly) <= half_lat + clr:
                d = x * n[0] + y * n[1]
                if near - clr <= d <= far + clr:
                    push = max(push, d + clr - near)
    return push


def turn_the_seat(s: Settlement, seat: Pt, n: Pt, core: tuple[float, float, float, float]) -> Pt:
    """A front-row seat moved out along `n` by how much further the homestead's core reaches toward its chord once
    turned (269 B18). `front_row` offsets every seat by the unturned core (`core`: left, top, right, bottom about the house
    center); the turn is the seat's own, known before it is offered, so the extra is measured, not a slack. Asked twice -
    the seat it moves to may take a different turn - and the larger move kept; the placer's own tests stay the judge.

    Research: a turned seat's reach - NONE: the seat moved out by the turned core's measured reach; the turn itself is `face_the_houses`'
    """
    toward = (-n[0], -n[1])
    base = turned_reach(core, 0.0, toward)
    extra = 0.0
    q = seat
    for _ in range(2):
        extra = max(extra, turned_reach(core, s._house_rot(q[0], q[1]), toward) - base)
        q = (seat[0] + n[0] * extra, seat[1] + n[1] * extra)
    return q


def bank_of(x: float, y: float, brook: Sequence[Pt]) -> int:
    """Which side of the brook a point stands on: the sign of its offset from the NEAREST reach of the course.

    A CROSSING TEST IS NOT A SIDE TEST, and that mistake cost two rolls. Asking whether the line from one house
    to another crosses the brook reads a curving course wrongly - the brook comes down one flank and wraps the
    field's toe, so two houses on the same bank can have the water between them as the crow flies, and every
    candidate after the first was refused (1 house of 15 seated on three maps). The side of the nearest reach is
    local, so a bend cannot invert it."""
    j = min(range(len(brook) - 1), key=lambda i: seg_dist(x, y, brook[i], brook[i + 1]))
    (ax, ay), (bx, by) = brook[j], brook[j + 1]
    return 1 if (bx - ax) * (y - ay) - (by - ay) * (x - ax) >= 0 else -1


def shapes_drawn_at(drawn: float) -> list[str]:
    """The cluster shapes whose drawn band (`CLUSTER_DRAWN_ASPECT`) holds a drawn aspect - a shape other than round only
    past round's ceiling (the settlement-review of Inashiro, feature 261: crescent's band starts at 1.9 and round's ends
    at 2.0, and a quarter-disc of houses drawn at 1.97 is round). Past every band, the nearest band's shape.

    Research:
        shapes a drawing admits - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the shapes the page names (lump, string, crescent, split)
        aspect bands and round first - UNRESEARCHED: round 1.0-2.0, crescent and split 1.9-4.2, elongated 2.8-12; another shape only past round's ceiling; past every band, the nearest band's
    """
    ceiling = CLUSTER_DRAWN_ASPECT["round"][1]
    held = [k for k, (lo, hi) in CLUSTER_DRAWN_ASPECT.items() if (lo if k == "round" else max(lo, ceiling + 1e-9)) <= drawn <= hi]
    return held or [min(CLUSTER_DRAWN_ASPECT, key=lambda k: min(abs(drawn - CLUSTER_DRAWN_ASPECT[k][0]), abs(drawn - CLUSTER_DRAWN_ASPECT[k][1])))]


def in_a_shapes_band(houses: Sequence[dict[str, Any]]) -> bool:
    """THE ONE PREDICATE of `test_the_cluster_draws_inside_the_band_of_the_shape_it_declared` (feature 287, homes wave 5):
    do the houses draw an aspect (`cluster_aspect`) some shape's band holds (`CLUSTER_DRAWN_ASPECT`)? Every aspect is at
    least round's floor, so the one way out is past the longest band's ceiling - elongated's 12:1 - where `shapes_drawn_at`
    could only name the nearest band, which the drawing breaks. Nothing is refused for it (feature 318: the 12:1 refusal that
    took a seating back went with every other take-back); the declared shape records what was drawn (`declare_cluster_shape`).

    Research: a cluster's longest draw - UNRESEARCHED: past the longest band's ceiling (`CLUSTER_DRAWN_ASPECT`, 12:1), read and refusing nothing
    """
    drawn = cluster_aspect([h["x"] for h in houses] or [0.0], [h["y"] for h in houses] or [0.0])
    return any(lo <= drawn <= hi for lo, hi in CLUSTER_DRAWN_ASPECT.values())


def declare_cluster_shape(houses: Sequence[dict[str, Any]], shape: str | None, seed: int) -> dict[str, Any]:
    """The cluster shape the manifest declares, and the plan keeps: the rolled shape wherever the houses draw it, and
    otherwise the knob RESOLVED OVER THE SHAPES THE DRAWING ADMITS (feature 287, homes H05, plan D4) - `shapes_drawn_at`,
    rolled from the map's seed with the knob's own weights (`CLUSTER_SHAPES`). The drawn shape is the declared shape on
    every map; there is no `cluster_shape_unhonored` record. The stage and its unit test read this one function.

    D4'S OTHER HALF WAS TRIED FIRST AND MEASURED A NO-OP (2026-09-29): steering the rank rounds toward the rolled shape -
    the along-the-field ends offered before the ranks while the standing houses draw rounder than the shape's band - left
    31 of 64 maps (pool and cohort 1-60) drawing a crescent or a string rounder than its band, the same 31 as without it:
    the front row, the brook's far bank and the field's chords seat the cluster, and the ends are refused where the ranks
    were. The record of three earlier failed bindings (`CLUSTER_BAND_ASPECT`) says the same. So the knob is narrowed to
    what the band draws, which D4 allows: on that measurement round is declared on 57 of the 64 maps, crescent on
    6, elongated on 1.

    Research:
        cluster shape knob - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the rolled shape kept where the houses draw it, else rolled again, with the knob's weights, over the shapes the drawing admits
    """
    drawn = cluster_aspect([h["x"] for h in houses] or [0.0], [h["y"] for h in houses] or [0.0])
    space = shapes_drawn_at(drawn)
    rolled = shape or "crescent"
    resolved = rolled if rolled in space else str(_roll(seed, "cluster_shape", tuple(v for v in CLUSTER_SHAPES if v in space) or tuple(space)))
    return {"cluster_shape": resolved, "cluster_aspect_drawn": round(drawn, 2)}
