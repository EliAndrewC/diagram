"""The DISPERSED farmstead's layout: the house, its yard and garden, and its own grove on the sides its settlement rolled
(feature 291). Module-level and pure, so it is tested with plain numbers; `BundleMixin._bundle_layout` calls it.

THE CANONICAL FRAME. Every farmstead is laid out as if the cold wind came from the northwest - the grove's deep bands
on the north and west, the threshing yard on the south front, the garden against the east wall - and then carried to
the map's own wind by a symmetry of the square (`grove_sides.bundle_turn`). Before feature 291 the layout stopped at the
canonical frame, so a map that declared another wind still drew its groves on the north and west.
"""

from __future__ import annotations

from typing import Any

from ..homestead_parts.grove_sides import THIN_BAND_FT as THIN_BAND_FT
from ..homestead_parts.grove_sides import E, N, S, Turn, W, turn_face, turns_axes

# THE GARDEN'S MORNING SUN: no grove band stands within this reach east of a garden across its height - the reach
# `_east_trees` reads (px at the village grain, scaled by `bscale`; research/rendering/homesteads.html "How our maps keep yards and gardens in the sun").
EAST_SHADE_REACH = 22.0
# THE YARD'S DRYING SUN: the strip south of a threshing yard no grove may stand in - `_yard_sun_conflict`'s 22 px strip.
YARD_SUN_STRIP = 22.0
# THE WAY IN THROUGH A RING. A grove round all four sides must still let the farm be reached: its front band is broken
# once, at the yard's middle, for a way two lane treads wide (the lane fabric sizes every lane at 6 ft). A physical
# necessity; the width is a GUESS - no old page gives an opening's width, and the old entrances found stood on a grove's
# open side, which a ring does not have (research/vegetation.html, "How did a lane get through a belt?").
WAY_IN_FT = 12.0
# THE WINDWARD STAND'S DEPTH, in house depths: the grove ~6x the house (research/homesteads.html, the grove's real scale).
DEEP_BAND_HOUSE_DEPTHS = 1.57

Rect = tuple[float, float, float, float]


def _box(x0: float, y0: float, x1: float, y1: float) -> Rect:
    return ((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0)


def _edges(r: Rect) -> tuple[float, float, float, float]:
    return r[0] - r[2] / 2, r[1] - r[3] / 2, r[0] + r[2] / 2, r[1] + r[3] / 2


def canonical_farmstead(
    cw: float,
    ch: float,
    gap: float,
    garden: tuple[float, float],
    yard: tuple[float, float],
    *,
    sides: int,
    garden_by_yard: bool,
    thin: float,
    sun_east: float,
    way_in: float,
    yard_sun: float = YARD_SUN_STRIP,
) -> dict[str, Any]:
    """The farmstead in the canonical frame, about a house of `cw` x `ch` centered on the origin: `yard`, `garden`, and
    `groves` as (rect, face, "deep" | "thin") - the deep north and west bands; with three sides a thin east band; with four
    a thin south band too, broken at the yard's middle for the way in. The corners close: the north and south bands run
    the whole width, the west and east bands between them. Each thin band stands clear of what the ground it closes needs
    - the east band beyond the garden's morning-sun reach, the south band beyond the yard's drying strip."""
    gw, gh = garden
    yw, yh = yard
    yard_r = (0.0, ch / 2 + gap + yh / 2, yw, yh)
    # beside the yard, at its far end (the yard keeps the garden's sky open to the south), or against the house's east
    # wall, at its mid-height
    garden_r = (yw / 2 + gap + gw / 2, yard_r[1], gw, gh) if garden_by_yard else (cw / 2 + gap + gw / 2, 0.0, gw, gh)
    works = [(-cw / 2, -ch / 2, cw / 2, ch / 2), _edges(yard_r), _edges(garden_r)]
    west_in = min(e[0] for e in works) - gap
    north_in = min(e[1] for e in works) - gap
    east_w = max(e[2] for e in works)
    south_w = max(e[3] for e in works)
    b = DEEP_BAND_HOUSE_DEPTHS * ch
    east_out = east_w + max(gap, sun_east + 1.0) + thin if sides >= 3 else east_w  # +1 px: the reach is a strict bound
    south_in = south_w + max(gap, yard_sun + 1.0)  # +1 px, the same
    south_out = south_in + thin if sides == 4 else south_w
    groves: list[tuple[Rect, tuple[int, int], str]] = [
        (_box(west_in - b, north_in - b, east_out, north_in), N, "deep"),
        (_box(west_in - b, north_in, west_in, south_out), W, "deep"),
    ]
    if sides >= 3:
        groves.append((_box(east_out - thin, north_in, east_out, south_out if sides == 4 else south_w), E, "thin"))
    if sides == 4:
        mid = yard_r[0]
        groves.append((_box(west_in - b, south_in, mid - way_in / 2, south_out), S, "thin"))
        groves.append((_box(mid + way_in / 2, south_in, east_out, south_out), S, "thin"))
    return {"yard": yard_r, "garden": garden_r, "groves": groves}


def _carried(r: Rect, t: Turn, hx: float, hy: float) -> Rect:
    """A canonical rect carried by the turn `t` about the house at (hx, hy): its center turned, its sides swapped where
    the turn exchanges the axes."""
    x, y = t[0] * r[0] + t[1] * r[1], t[2] * r[0] + t[3] * r[1]
    w, h = (r[3], r[2]) if turns_axes(t) else (r[2], r[3])
    return (hx + x, hy + y, w, h)


def dispersed_layout(
    hx: float, hy: float, hw: float, hh: float, gap: float, garden: tuple[float, float], yard: tuple[float, float], *, sides: int, turn: Turn, thin: float, sun_east: float, way_in: float
) -> dict[str, Any]:
    """The dispersed farmstead about a house at (hx, hy) of `hw` x `hh` (as drawn), carried from the canonical frame by
    `turn`: `house`, `yard`, `garden`, `gardens` (one bed), `groves` (rects), `grove_faces` ((face, depth) beside each,
    the face as turned) and `_frame` (the box round the whole grove and ground, unraked). In every frame but the unchanged
    northwest one the garden goes beside the yard (plan D3): turned or mirrored, the east wall it stands against would be
    the house's north wall or its west, where the house takes its sun."""
    moved = turn != (1, 0, 0, 1)
    cw, ch = (hh, hw) if turns_axes(turn) else (hw, hh)
    can = canonical_farmstead(cw, ch, gap, garden, yard, sides=sides, garden_by_yard=moved, thin=thin, sun_east=sun_east, way_in=way_in)
    yard_r = _carried(can["yard"], turn, hx, hy)
    garden_r = _carried(can["garden"], turn, hx, hy)
    groves = [_carried(r, turn, hx, hy) for r, _f, _d in can["groves"]]
    faces = [(turn_face(turn, f), d) for _r, f, d in can["groves"]]
    edges = [_edges(r) for r in (*groves, yard_r, garden_r, (hx, hy, hw, hh))]
    frame = _box(min(e[0] for e in edges), min(e[1] for e in edges), max(e[2] for e in edges), max(e[3] for e in edges))
    return {"house": (hx, hy, hw, hh), "yard": yard_r, "garden": garden_r, "gardens": [garden_r], "groves": groves, "grove_faces": faces, "_frame": frame}
