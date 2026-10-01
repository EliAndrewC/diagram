"""A DISPERSED farm's own water as a CHANNEL led into its grounds (feature 291 amendment 5, plan D18; FR-018).

homesteads/200, the Tonami dispersed-village museum (translated): "because in former times on the fan plain the water
table was deep and wells were hard to dig, in many areas a small channel was led into the house's grounds and used for
cooking, washing and drinking water" - ACCURATE. The `farm_water` knob (`FARM_WATERS`) rolls it against a well of the
farm's own (drawn at its well pocket, `wells.grove_water`), the other areas as the record reads them, a GUESS.

Each channel runs from the nearest point of the irrigation water - a drawn supply ditch (a main or a branch, never the
drain), or the brook where that is nearer (the nearest a map drawing convention; the brook standing for the water the
ditches are fed from, a GUESS) - to the farm's dooryard, a step off the edge of its threshing yard nearest the water
(where in the dooryard no page read says: a GUESS). It ends there: where it left the lot again no page read says, so the
return is not drawn (a deliberate deviation). It is routed round every building, yard and garden, every OTHER farm's
grove, the crop, the lanes and all other water, and may cross the farm's own grove band - it is led INTO the
grounds, through the wood that surrounds them. A later farm's channel may be led off one already drawn (amendment 6, a GUESS).
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, rot_rect, seg_closest, segments_cross
from l7r.diagram.settlement.water_ways.water import SUPPLY_HUE
from l7r.diagram.sitegen.geom import crop_polys

from ..consts import Poly, Pt

FARM_CHANNEL = "farm channel"
"""The class the channel is drawn under (`interactive/classes/water_and_ways.FarmChannel`)."""

FARM_CHANNEL_W_FT = 2.5
"""The channel's drawn bed: the field channel's legibility floor (`Settlement.channel`'s 2.5 ft) - a map drawing
convention; no page read gives the width of a channel into a farm's grounds."""

DOORYARD_STEP_FT = 6.0
"""How far off its threshing yard's edge the channel ends: a step, so the water stands in the dooryard beside the yard
rather than on its floor (a map drawing convention)."""

DOORYARD_STEPS = (1.0, 2.0, 3.5)
"""The multiples of `DOORYARD_STEP_FT` a channel's end is offered at off each side of the yard, nearest first (feature 291 on
287; where in the dooryard the channel ended no page read says - a GUESS, as the one step was)."""
SOURCE_TRIES = 6
"""The nearest candidate points on the irrigation water tried per farm, nearest first (the router's own budget)."""

SOURCE_STEP_FT = 20.0
"""The spacing of candidate points along each supply course."""

ROUTE_CELL_FT = 8.0
"""The router's lattice for a channel, finer than a lane's 12 ft, and the crop routed round as a WALL (at the channel's
own 2 ft gap), not as hard ground (at a lane's wider one): a supply ditch runs between the plots with a few feet either
side, and at a lane's margins no cell beside it was free - Audit-19's farm by the field's corner tried thirty routes off
the main and every one was refused at its first step."""

SOURCE_SPREAD_FT = 60.0
"""How far apart two tried sources stand at least - a different stretch of water, or a different course."""


def supply_courses(M: Mapping[str, Any]) -> list[list[Pt]]:
    """The irrigation water a channel may be led off: every supply ditch (`field_ditches` whose role is not the drain) and
    every brook (`streams`)."""
    out = [[(float(x), float(y)) for x, y in d["poly"]] for d in M.get("field_ditches") or [] if d.get("role") != "drain" and len(d.get("poly") or ()) >= 2]
    out += [[(float(x), float(y)) for x, y in r["poly"]] for r in M.get("streams") or [] if len(r.get("poly") or ()) >= 2]
    return out


def source_points(courses: Sequence[Sequence[Pt]], near: Pt, step: float, n: int, spread: float = 0.0) -> list[Pt]:
    """The `n` points along `courses`, every `step` and at each course's point nearest `near`, nearest `near` first - each
    at least `spread` from those before it, so the tries are not one stretch of water taken six times."""
    pts: list[Pt] = []
    for c in courses:
        for a, b in zip(c, c[1:], strict=False):
            k = max(1, int(math.dist(a, b) // step))
            pts += [(a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k) for i in range(k)]
            pts.append(seg_closest(near[0], near[1], a, b))
    out: list[Pt] = []
    for q in sorted(pts, key=lambda q: math.dist(q, near)):
        if all(math.dist(q, o) >= spread for o in out):
            out.append(q)
            if len(out) == n:
                break
    return out


def dooryard_end(yard: Sequence[Sequence[float]], toward: Pt, step: float) -> Pt:
    """Where the channel ends: `step` off the threshing yard's ring, at the ring's point nearest `toward` (the water),
    out along the line from the yard's middle."""
    ring = [(float(p[0]), float(p[1])) for p in yard]
    cx, cy = sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring)
    edge = min((seg_closest(toward[0], toward[1], a, b) for a, b in zip(ring, [*ring[1:], ring[0]], strict=False)), key=lambda q: math.dist(q, toward))
    dx, dy = edge[0] - cx, edge[1] - cy
    d = math.hypot(dx, dy) or 1.0
    return (edge[0] + dx / d * step, edge[1] + dy / d * step)


def crosses_other_water(path: Poly, water: Sequence[tuple[Pt, Pt]], start_free: float) -> bool:
    """Does `path` cross any of `water` more than `start_free` along it from its start - past its own mouth?"""
    run = 0.0
    for a, b in zip(path, path[1:], strict=False):
        seg_len = math.dist(a, b)
        for c, d in water:
            if segments_cross(a, b, c, d) and run + cross_t(a, b, c, d) * seg_len > start_free:
                return True
        run += seg_len
    return False


def cross_t(a: Pt, b: Pt, c: Pt, d: Pt) -> float:
    """How far along a-b (0..1) it meets the line c-d; 0 for parallel lines."""
    den = (b[0] - a[0]) * (d[1] - c[1]) - (b[1] - a[1]) * (d[0] - c[0])
    if abs(den) < 1e-12:
        return 0.0
    return ((c[0] - a[0]) * (d[1] - c[1]) - (c[1] - a[1]) * (d[0] - c[0])) / den


def _obstacles(s: Settlement, h: Mapping[str, Any]) -> tuple[list[Poly], list[Poly]]:
    """(hard, walls) for farm `h`'s channel: the crop is hard; every building, yard and garden, every OTHER farm's grove,
    and every lane are walls. The farm's own grove is not - the channel runs into its grounds through it."""
    from ..ways.geom import steading_footprints, stroke_quad  # local: the ways are a later stage

    me = (round(float(h["x"]), 1), round(float(h["y"]), 1))
    walls: list[Poly] = list(steading_footprints(s.M))
    for g in s.M.get("groves") or []:
        of = g.get("of")
        if of and (round(float(of[0]), 1), round(float(of[1]), 1)) != me and all(k in g for k in ("x", "y", "w", "h")):
            walls.append(rot_rect(float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"]), float(g.get("rot", 0.0))))
    # ...and every OTHER farm's WELL POCKET (feature 287's seating laid one in each grove farm's dooryard): a farm the channels
    # leave dry draws its well there, so no channel may run across one. Not the farm's own: its channel arriving is what
    # releases it (`wells.grove_water`), and walled, it turned away the one approach a farm on cohort seed 19 had
    vr = 2.0 * float(s._well_vr()) + s.px(6.0)
    walls += [
        rot_rect(float(q["well_pocket"][0]), float(q["well_pocket"][1]), vr, vr, 0.0)
        for q in s.M.get("houses") or []
        if q.get("well_pocket") and (round(float(q["x"]), 1), round(float(q["y"]), 1)) != me
    ]
    # NOT the other farms' FRAMES: a frame holds the lane's room between two groves, which is exactly where a channel to a
    # farm behind them runs (Audit-905: with the frames walled, six of sixteen farms were cut off their water)
    for ln in s.M.get("lanes") or []:
        p = [(float(x), float(y)) for x, y in ln.get("pts") or []]
        half = float(ln.get("w") or 3) / 2.0
        walls += [stroke_quad(a, b, half) for a, b in zip(p, p[1:], strict=False)]
    paddies = [[(float(a), float(b)) for a, b in r] for f in s.M.get("fields") or [] for r in f.get("plot_rings") or [] if len(r) >= 3]
    return [*crop_polys(s), *paddies], walls


def farm_channel(s: Settlement, h: Mapping[str, Any], courses: Sequence[Sequence[Pt]], water: Sequence[tuple[Pt, Pt]]) -> Poly:
    """The channel into farm `h`'s grounds - drawn, and returned - or [] where no course reaches its dooryard."""
    from ..ways.route import _route  # local: the ways are a later stage

    hx, hy = float(h["x"]), float(h["y"])
    yard = next((y for y in s.M.get("threshing_yards") or [] if y.get("of") and math.dist((float(y["of"][0]), float(y["of"][1])), (hx, hy)) < 0.5), None)
    ring = (yard or {}).get("poly") or (yard or {}).get("outline")
    if not ring:
        return []
    hard, walls = _obstacles(s, h)
    step = s.px(DOORYARD_STEP_FT)
    cx, cy = sum(float(p[0]) for p in ring) / len(ring), sum(float(p[1]) for p in ring) / len(ring)
    # EACH SIDE OF THE YARD, THE SIDE FACING THE WATER FIRST: the end a step off the side nearest the water can stand boxed
    # in between the yard, the house and the garden (Audit-905: two farms, every route to that one end refused)
    sides = [((float(a[0]) + float(b[0])) / 2, (float(a[1]) + float(b[1])) / 2) for a, b in zip(ring, [*ring[1:], ring[0]], strict=False)]
    # ...THE SHORTEST OF THEM ALL, over every source and every end, not the first found: the nearest side can be reached only
    # the long way round the grove (Audit-905: a channel carried 360 ft round its own farm to the side facing its water)
    # THE WAY THAT HAS ALWAYS SERVED FIRST, THE WIDER SEARCH ONLY WHERE IT FINDS NOTHING (cohort run 6): the nearest sources, a
    # step off each side of the yard, routed. Offered as equals, the wider search's shorter chords took the early farms' water
    # the straight way and walled the later farms off theirs (channels are laid nearest the water first, and each one drawn
    # is water the next may not cross): three dispersed seeds that had passed each left two or three farms dry.
    offered = source_points(courses, (cx, cy), s.px(SOURCE_STEP_FT), SOURCE_TRIES * 4, spread=s.px(SOURCE_SPREAD_FT) * 4)
    near = source_points(courses, (cx, cy), s.px(SOURCE_STEP_FT), SOURCE_TRIES, spread=s.px(SOURCE_SPREAD_FT))
    routes: list[Poly] = []
    for srcs, steps, straight in (
        (near, (1.0,), False),
        # ...THEN THE WIDER SEARCH: the nearest sources off the crop beside them (a ditch inside the field can be walled by its
        # paddies - cohort seed 19: all six of one farm's sources stood among them); ends farther off the yard (since feature
        # 287 a farm's fixtures are laid round it, and a single step off each side stood boxed in by them); and the straight
        # chord where it crosses nothing (a farm seated close by its field leaves a strip narrower than the router's clearance
        # on both sides - seed 19: 90 routes refused for a channel 30 ft long)
        ([*near, *[q for q in offered if q not in near and not inside_the_crop(q, hard)][:SOURCE_TRIES]], DOORYARD_STEPS, True),
    ):
        for src in srcs:
            mine = [(c, d) for c, d in water if _seg_d(src, c, d) > s.px(3.0)]  # the course it is led off, and its drawn twin
            ends = [dooryard_end(ring, t, step * k) for k in steps for t in (src, *sorted(sides, key=lambda m: math.dist(m, src)))]
            found = (
                straight_or_routed(src, e, hard, walls, mine, s.px(ROUTE_CELL_FT), s.px(2.0)) if straight else _route(src, e, [], [*hard, *walls], mine, cell=s.px(ROUTE_CELL_FT), gap=s.px(2.0))
                for e in ends
            )
            routes += [p for p in found if len(p) >= 2 and not crosses_other_water(p, water, s.px(6.0))]
        if routes:
            break
    path = min(routes, key=lambda p: sum(math.dist(a, b) for a, b in zip(p, p[1:], strict=False)), default=[])
    if path:
        s.field_channel(path, SUPPLY_HUE, s.px(FARM_CHANNEL_W_FT), s.px(FARM_CHANNEL_W_FT), cls=FARM_CHANNEL)
        s.M["drawn_channels"][-1]["farm"] = [hx, hy]
        s.M.setdefault("farm_channels", []).append({"of": [hx, hy], "pts": [[round(x, 1), round(y, 1)] for x, y in path], "w": s.px(FARM_CHANNEL_W_FT)})
        s.corridors.append((path, s.px(4.0)))
    return path


def straight_or_routed(src: Pt, end: Pt, hard: Sequence[Poly], walls: Sequence[Poly], water: Sequence[tuple[Pt, Pt]], cell: float, gap: float) -> Poly:
    """The straight chord from `src` to `end` where it crosses no hard ground, no wall and no water, else the routed way."""
    from ..ways.fabric import _crosses_fabric
    from ..ways.route import _route

    if not _crosses_fabric([src, end], [*hard, *walls], 0.0) and not any(segments_cross(src, end, c, d) for c, d in water):
        return [src, end]
    return _route(src, end, [], [*hard, *walls], list(water), cell=cell, gap=gap)


def inside_the_crop(q: Pt, hard: Sequence[Poly], edge: float = 1.0) -> bool:
    """Is `q` strictly inside the crop (`hard`) - inside a ring and more than `edge` from its boundary - so no source for a
    channel?"""
    from l7r.diagram.settlement import edge_dist

    return any(len(r) >= 3 and point_in_poly(q[0], q[1], r) and edge_dist(q[0], q[1], r) > edge for r in hard)


def _seg_d(p: Pt, a: Pt, b: Pt) -> float:
    q = seg_closest(p[0], p[1], a, b)
    return math.dist(p, q)


def farm_channels(s: Settlement, houses: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """A channel into each grove farm's grounds (`farm_channel`); returns the farms no course reached, which the caller
    gives a well of their own - never left dry, and reported by `row_rules.water_rules`.

    NEAREST THE WATER FIRST: taken in the order given, the long channels to the far farms walled the near farms off their
    water, and three of Audit-905's sixteen fell back to a well. And A LATER CHANNEL MAY BE LED OFF AN EARLIER ONE (FR-018
    amendment 6, a GUESS - whether neighbors shared a channel no page read says): measured 2026-09-30, Audit-19's farms,
    whose only irrigation water is the field's head, drew 1 channel in 11 without it and 11 in 11 with it."""
    from ..ways.checks import drawn_water_segs  # local: the ways are a later stage

    courses = supply_courses(s.M)
    dry: list[Mapping[str, Any]] = []
    if not courses:
        return list(houses)

    def reach(h: Mapping[str, Any]) -> float:
        c = (float(h["x"]), float(h["y"]))
        return min(math.dist(c, q) for q in source_points(courses, c, s.px(SOURCE_STEP_FT), 1))

    for h in sorted(houses, key=reach):
        water = drawn_water_segs(s)  # re-read per farm: the last farm's channel is water the next must not cross
        path = farm_channel(s, h, courses, water)
        if path:
            courses.append(list(path))
        else:
            dry.append(h)
    return dry
