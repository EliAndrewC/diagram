"""THE PADDY'S OWN GRASS HILL (feature 374 wave 148): a small grass hill set aside for one paddy's sole use, the tazuke kusayama.

research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.html: "Sometimes a small grass hill was set aside for a
particular paddy's sole use, and called a tazuke kusayama"; its drawing page: "now and then, added at random, a small grass plot
beside one paddy ... one grass patch of about the paddy's own size on the slope above it. The plot's size and how often it is
rolled are a GUESS".

Research: paddy grass plumbing - NONE: a roll, a seat search and a square
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from l7r.diagram.settlement import Settlement

from ..consts import Poly, Pt
from ..plan import SitePlan, _roll

PADDY_GRASS_ODDS = (True, False, False)
"""How often a grass-hill hamlet keeps a paddy's own grass hill: one in three, rolled per settlement.

Research: how often - GUESS research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html: "now and then", the rate a GUESS the page names"""

UPSLOPE_PLOTS = 16
"""How many of the field's upslope-most plots are offered a grass hill above them, nearest the top first.

Research: plots offered - NONE: a bound on a seat search"""

GRASS_GAP_FT = 6.0
"""How far above its paddy's edge the grass hill's square stands: the bund and its cut strip (`SCRUB_FIELD_FT`'s 6 ft).

Research: off the paddy - research/questions/0073-scrub-and-rough-grass-at-the-edges-of-fields-and-channels.drawing.html: the bund and its cut strip kept bare"""


def paddy_grass_hill(plan: SitePlan) -> bool:
    """Does this hamlet keep a paddy's own grass hill? Rolled on a grass-hill map only (`grass_ground`): a floodplain map has no
    slope above its paddies.

    Research: on a grass-hill map - research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html: a small grass plot on the slope above its paddy"""
    from .stages import grass_ground  # local: stages imports this module

    return grass_ground(plan) == "grass_hill" and bool(_roll(plan.spec.seed, "paddy_grass_hill", PADDY_GRASS_ODDS))


def _centroid(poly: Sequence[Sequence[float]]) -> Pt:
    return (sum(float(p[0]) for p in poly) / len(poly), sum(float(p[1]) for p in poly) / len(poly))


def _area(poly: Sequence[Sequence[float]]) -> float:
    return abs(sum(float(a[0]) * float(b[1]) - float(b[0]) * float(a[1]) for a, b in zip(poly, [*poly[1:], poly[0]], strict=True))) / 2.0


def upslope_plots(plots: Sequence[Sequence[Sequence[float]]], fall: Pt, n: int = UPSLOPE_PLOTS) -> list[Sequence[Sequence[float]]]:
    """The field's `n` upslope-most plots (least far along `fall`), nearest the top first.

    Research: the paddies at the field's top - research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html: the grass hill on the slope above its paddy"""
    return sorted((p for p in plots if len(p) >= 3), key=lambda p: _centroid(p)[0] * fall[0] + _centroid(p)[1] * fall[1])[:n]


def seat_paddy_grass(s: Settlement, plan: SitePlan) -> Poly | None:
    """The square of a paddy's own grass hill - about one plot's own area, its near edge `GRASS_GAP_FT` upslope of the plot's top -
    seated by the engine's own seat search (`open_seat`: off the crop, the houses and their ground, the lanes and the water) above
    the first upslope plot that has such ground, or None where none has.

    Research:
        about the paddy's own size - GUESS research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html: one plot's own area, the size a GUESS the page names
        on the slope above it - research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html: upslope of the plot, against the fall"""
    fields = s.M.get("fields") or []
    plots = [p for f in fields for p in (f.get("plot_rings") or [])]  # each plot's ring (`plots` is its compact record)
    fx, fy = plan.fall
    gap = s.px(GRASS_GAP_FT)
    for plot in upslope_plots(plots, (fx, fy)):
        side = math.sqrt(_area(plot))
        if side < 1.0:
            continue
        top = min(float(p[0]) * fx + float(p[1]) * fy for p in plot)  # the plot's upslope edge, along the fall
        cx, cy = _centroid(plot)
        lift = (cx * fx + cy * fy) - top + gap + side / 2.0  # from the plot's center to the square's, against the fall
        ax, ay = cx - fx * lift, cy - fy * lift
        seat = s.open_seat((ax - side, ay - side, ax + side, ay + side), side, side)
        if seat is not None:
            x, y = seat
            h = side / 2.0
            return [(x - h, y - h), (x + h, y - h), (x + h, y + h), (x - h, y + h)]
    return None


def lay_paddy_grass(s: Settlement, plan: SitePlan) -> Poly | None:
    """Roll and seat the hamlet's paddy grass hill, recording the outcome (`meta.paddy_grass_hill`: none, drawn, or no seat);
    the square is held against what is placed after it (`block_polys`). Returns the square, or None.

    Research: recorded either way - NONE: the record of a roll"""
    if not paddy_grass_hill(plan):
        s.M["meta"]["paddy_grass_hill"] = "none"
        return None
    square = seat_paddy_grass(s, plan)
    s.M["meta"]["paddy_grass_hill"] = "drawn" if square else "no seat"
    if square:
        s.block_polys.append(square)
    return square


def draw_paddy_grass(s: Settlement, square: Any) -> None:
    """Draw the grass hill as open grass - the meadow's grass and odd brush dot, no pine (`commons`, role `paddy_grass`).

    Research: drawn as open grass - research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html: open grass on the hill ground, a cut patch on the scrub"""
    s.commons(square, role="paddy_grass")
