"""A lot's line follows what bounds it on the ground, and the open ground a parcel may take (split from `parcels.py` at the
1,000-line bar, feature 417 T38). `parcels/__init__.py` re-exports every name.

Research: lot bounds plumbing - NONE: segment indexes, margins and ring spans
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from l7r.diagram.settlement import point_in_poly, seg_dist, segments_cross
from l7r.diagram.settlement._geom import PointGrid, RingIndex, seg_reach_index

from ...consts import Poly, Pt

# ---- woods W26: a lot's line follows what bounds it on the ground ---------------------------------------------------
# GUESS (research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html, 0077): a wood's edge was a line the villages agreed or were
# given, and it bent; "whether it followed ridges, streams and paths is a GUESS: no page read says so." This builds that
# working answer: where a lot's outline comes within a small reach of a brook, a lane or a field's edge, its line keeps off
# that feature and runs parallel to it, rather than wandering near it or across it as a stamped disc would. The one form
# the record does attest as rectilinear (the Musashino strip holdings) is a settlement form and is not drawn here.

LANE_LOT_LINE = 70.0  # px from a lane's centerline: the scan's own lane keep-out (`open_ground_patches`), the lot's line along it
"""Research: lot line along a lane - GUESS: searched, the record silent (feature 417 T36 pass P5, 2026-10-25); 70 px from its centerline"""
STREAM_LOT_LINE = 60.0  # px from a brook's centerline: the scan's own stream keep-out, the lot's line along it
"""Research: lot line along a brook - GUESS: searched, the record silent (feature 417 T36 pass P5, 2026-10-25); 60 px from its centerline"""
LOT_BOUND_REACH = 45.0
"""How near (px, 1 ft at the hamlet scale) a lot's outline must come to a feature's line before the line bounds it.

GUESS, a calibrated degree (research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html is silent on any distance): half the scan's 90 px lattice step, so a
seat the lattice put within one half-step of a keep-out has its facing side drawn along that keep-out, while a lot a whole
step or more away keeps its free wandering edge. A larger reach would bound more lots and cut more of their ground.

Research: lot line reach - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: 45 ft"""

Bound = tuple[list[tuple[Pt, Pt]], float, "Poly | None"]  # (segments, the lot's line distance, the ring when closed)


def lot_bounds(lanes: Sequence[Sequence[Pt]], streams: Sequence[Sequence[Pt]], crops: Sequence[Poly], crop_setback: float) -> list[Bound]:
    """The features a coppice lot's line may follow (woods W26): each lane and brook as its segments at the scan's keep-out,
    each field ring as its closed edge at the set-back the scan seated the lot with (a point inside a field is on the wrong
    side of its line)."""

    def _segs(pts: Sequence[Pt], closed: bool) -> list[tuple[Pt, Pt]]:
        ps = [(float(p[0]), float(p[1])) for p in pts]
        return list(zip(ps, ps[1:] + ps[:1] if closed else ps[1:], strict=False))

    return [
        *((_segs(ln, False), LANE_LOT_LINE, None) for ln in lanes if len(ln) >= 2),
        *((_segs(st, False), STREAM_LOT_LINE, None) for st in streams if len(st) >= 2),
        *((_segs(c, True), crop_setback, [(float(p[0]), float(p[1])) for p in c]) for c in crops if len(c) >= 3),
    ]


def _bound_margin(p: Pt, bound: Bound) -> float:
    """How far `p` stands off `bound`'s feature, signed: negative inside a field's ring."""
    segs, _line, ring = bound
    d = min(seg_dist(p[0], p[1], a, b) for a, b in segs)
    return -d if ring is not None and point_in_poly(p[0], p[1], ring) else d


def _follows(p: Pt, bounds: Sequence[Bound], reach: float, tol: float = 1.0) -> bool:
    """One vertex of the lot's line: for every bound, either ON its line (within `tol`) or beyond `reach` of it."""
    return all(abs((d := _bound_margin(p, b)) - b[1]) <= tol or d >= b[1] + reach - tol for b in bounds)


def lot_follows_its_bounds(ring: Sequence[Pt], bounds: Sequence[Bound], reach: float = LOT_BOUND_REACH) -> bool:
    """THE ONE PREDICATE (feature 287, woods W26 - GUESS, research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html): does a coppice lot's line follow what
    bounds it? Where a vertex comes within `reach` of a brook's, a lane's or a field's line it lies on that line or keeps
    off it by the reach - a ragged wander near a feature, or a vertex over its line, is refused; and no edge of the lot
    crosses a feature. `open_ground_patches` draws only rings this admits, cut by `follow_the_bounds`.

    Research: line follows its bounds - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: on the feature's line or clear of it by the reach, never across it
    """
    edges = list(zip(ring, [*ring[1:], ring[0]], strict=False))
    for b in bounds:
        if any(segments_cross(a, c, s0, s1) for a, c in edges for s0, s1 in b[0]):
            return False
    return all(_follows(p, bounds, reach) for p in ring)


def ring_span(ring: Sequence[Pt]) -> float:
    """A ring's widest axis-aligned extent - the measure the commons floor is held on."""
    xs, ys = [float(p[0]) for p in ring], [float(p[1]) for p in ring]
    return max(max(xs) - min(xs), max(ys) - min(ys))


def bounds_near(bounds: Sequence[Bound], center: Pt, radius: float) -> list[Bound]:
    """Only the segments of each bound that could come within `radius` of `center` (a field ring keeps its whole ring for
    the inside test) - a prefilter: a segment farther than that can bound no vertex of a lot of that radius."""
    out: list[Bound] = []
    for segs, line, ring in bounds:
        near = [(a, b) for a, b in segs if seg_dist(center[0], center[1], a, b) < radius + line + LOT_BOUND_REACH]
        if near:
            out.append((near, line, ring))
    return out


def follow_the_bounds(ring: Sequence[Pt], center: Pt, bounds: Sequence[Bound], reach: float = LOT_BOUND_REACH) -> Poly:
    """The lot's line cut to follow its bounds (woods W26 - GUESS, research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html): each vertex that
    `lot_follows_its_bounds` would refuse is pulled in along its ray toward the lot's own `center` until it keeps off
    every bound by that bound's line plus the reach - so the lot's facing side runs parallel to the brook, lane or field
    edge. Only ever pulled IN: the ring stays inside the reach the scan tested, so no keep-out can be crossed by the cut.
    A vertex no point of its ray can clear (the center itself too near) is left, and the predicate refuses the ring.

    Research: line follows its bounds - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: vertices pulled in until they run alongside the feature
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N2, 2026-10-25) - 0.05 (bisection bracket); 20 (bisection iterations); 19 (coarse search start)
    """
    out: Poly = []
    cx, cy = center
    for p in ring:
        if _follows(p, bounds, reach):
            out.append(p)
            continue

        def _at(f: float, p: Pt = p) -> Pt:
            return (cx + (p[0] - cx) * f, cy + (p[1] - cy) * f)

        def _clear(f: float) -> bool:
            q = _at(f)
            return all(_bound_margin(q, b) >= b[1] + reach for b in bounds)

        lo = next((k / 20.0 for k in range(19, -1, -1) if _clear(k / 20.0)), None)
        if lo is None:
            out.append(p)
            continue
        hi = lo + 0.05
        for _ in range(20):
            mid = (lo + hi) / 2.0
            lo, hi = (mid, hi) if _clear(mid) else (lo, mid)
        out.append(_at(lo))
    return out


def open_ground_region(
    cache: dict[tuple[float, float, float], Any],
    half: float,
    normal: float,
    sunny: float,
    crops: Sequence[Poly],
    keep: Sequence[tuple[float, float, float]],
    keep_rects: Sequence[tuple[float, float, float, float]],
    lines: Sequence[tuple[Poly, float]],
    marshes: Sequence[Poly],
    window: tuple[float, float, float, float],
) -> Any:
    """The ground a woodland square of half-side `half` may not CENTER on (feature 297, plan B4), as one `Region` built once per
    (half, set-backs) into `cache`: each crop grown by its set-back plus `half` (`_crop_refuses`'s `normal`), and by the sunny
    set-back over the band south of it (its `south_of` - the square's top below the crop's last 40 px, its center within the crop's
    x-span grown by `half`); the keep circles grown by `half`; the keep rectangles grown by `half`; the lanes and streams at their
    reach plus `half`; the marsh grown by `half` (a square with any of its nine points in a marsh is refused, `_wet`).

    Research:
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N2, 2026-10-25) - 40 ("south of the crop" tolerance)
    """
    key = (half, normal, sunny)
    got = cache.get(key)
    if got is None:
        import shapely
        from shapely.geometry import Polygon

        from l7r.diagram.settlement._geom.region import Region

        x0, y0, x1, y1 = window
        pad = max([normal, sunny]) + half + 40.0
        got = Region((x0 - pad, y0 - pad, x1 + pad, y1 + pad), 3.0)  # 3 px: the margin is two cells, 6 px; at 8 px its 16 px moved a parcel off the brook line its lot follows (test_hinterland_287)
        polys = [g if g.is_valid else g.buffer(0) for g in (Polygon(c) for c in crops if len(c) >= 3)]
        geoms: list[Any] = list(polys)
        pads: list[float] = [normal + half] * len(polys)
        if polys:  # ...the sunny set-back over the band south of each crop (`_crop_refuses`' `south_of`)
            b = shapely.bounds(polys)
            bands = shapely.box(b[:, 0] - half, b[:, 3] - 40.0 + half, b[:, 2] + half, b[:, 3] + sunny + half + 1.0)
            south = shapely.intersection(shapely.buffer(polys, sunny + half, quad_segs=4), bands)
            geoms += [g for g in south if not g.is_empty]
            pads += [0.0] * sum(1 for g in south if not g.is_empty)
        geoms += [shapely.Point(float(kx), float(ky)) for kx, ky, _kr in keep]
        pads += [float(kr) + half for _kx, _ky, kr in keep]
        geoms += [shapely.box(rx0, ry0, rx1, ry1) for rx0, ry0, rx1, ry1 in keep_rects]
        pads += [half] * len(keep_rects)
        for pl, reach in lines:
            if len(pl) >= 2:
                geoms.append(shapely.LineString([(float(q[0]), float(q[1])) for q in pl]))
                pads.append(float(reach) + half)
        for mp in marshes:
            if len(mp) >= 3:
                g = Polygon(mp)
                geoms.append(g if g.is_valid else g.buffer(0))
                pads.append(half)
        got.fill_many(geoms, pads)
        cache[key] = got
    return got


def _crop_refuses(center: Pt, half: float, crop: RingIndex, normal: float = 80.0, sunny: float = 180.0) -> bool:
    """Does this crop refuse a candidate square here - standing in it, or nearer than its set-back?

    The set-back is 80 px normally and 180 px when the square sits on the crop's SUNNY side (south,
    in screen terms) - the shading case. `woodland_clear_of_crops` uses 1 : 2.5-ish set-backs for the
    same reason; this is deliberately a little more generous than the check, so a patch that passes
    here passes there with room to spare rather than sitting on the line.

    One crop at a time, from its ring index (feature 218): the scan used to measure every candidate
    against every edge of every crop to return the nearest distance, and its only caller asked
    whether that was None. The distance is asked of the index only under the widest set-back this
    crop could apply (+1 px of slack), and the refusal is the expression the scan ran - `d - half <
    set-back` on the true distance - so the verdict is the same to the bit.

    Research: crop set-back - research/questions/0038-sunlight-and-shade-on-the-farm.html: a tree shades one tree's height to its east, west and north (the Qimin Yaoshu), about 33 ft, which the set-backs clear; 80 px, 180 px on the crop's sunny side
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N2, 2026-10-25) - 40 (same tolerance)
    """
    cx, cy = center
    if crop.inside(cx, cy):
        return True
    south_of = cy - half > crop.y1 - 40 and crop.x0 - half < cx < crop.x1 + half
    limit = sunny if south_of else normal
    dist = crop.edge_within(cx, cy, limit + half + 1.0)
    return dist is not None and dist - half < limit


def _lines_at(cache: dict[float, PointGrid], lines: Any, half: float) -> PointGrid:
    """`seg_reach_index(lines, half)`, built once per `half` into `cache` (feature 278)."""
    grid = cache.get(half)
    if grid is None:
        grid = cache[half] = seg_reach_index(lines, half)
    return grid


def _near_line(center: Pt, half: float, pts: Sequence[Pt], pad: float) -> bool:
    cx, cy = center
    return any(seg_dist(cx, cy, pts[i], pts[i + 1]) < half + pad for i in range(len(pts) - 1))
