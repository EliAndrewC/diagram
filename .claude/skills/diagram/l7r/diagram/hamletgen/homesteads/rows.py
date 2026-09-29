"""THE ROW VILLAGE (feature 291 amendment 3; research/homesteads/155 and 156) - a linear hamlet's farms in rows along
their streets, never in ranks behind a row.

The record gives a row two lines, and both are drawn (`ROW_LINES`): a STREET LAID FIRST, straight as a surveyed road -
the planned row's form, which a paddy row may borrow - or the DRY EDGE THE GROUND GIVES, a levee, a dike, a fan's foot,
for which the field's margin stands here (this project's reading), the row curving with it. The farms stand on ONE side
of the street, the field across it, or on BOTH (`ROW_SIDES`), one FRAME apart - the grove farm's own ground and grove
and the lane's room between two groves (homesteads/715), a physical necessity, since a grove farm cannot stand on a
narrower lot. A row the line cannot hold grows another street parallel to the first, one row set further out, as a
planned colony grew more roads (homesteads/156) - how many farms a line holds before the next street is the ground's.

This module is pure geometry and one seating loop: `row_streets` gives the lines, `row_seats` the frame centers along
them, `seat_rows` asks the placer for each. The streets it planned are kept on the settlement for the web
(`ways/web.py` `_lay_street`), which lays each as one continuous way.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from l7r.diagram.settlement import Settlement

from l7r.diagram.settlement.homestead_parts.grove_sides import grove_faces
from l7r.diagram.settlement.rolling.dispersed import LANE_ROOM_FT

from ..consts import Poly, Pt
from ..plan import SitePlan

FIELD_KEEP_FT = 24.0
"""How far a row's street runs off its field's margin: the lane's room (homesteads/715) less the tread's half - a map
drawing convention, near enough that the field reads as the row's own, clear enough that the street is not on a bund."""

STREET_HALF_FT = 3.0
"""Half the street's drawn width (the connector's 6 ft tread; the web's lanes are 3-5), the room a row stands back from it."""

MAX_STREETS = 4
"""The most parallel streets a row village grows before the seat passes behind it take the remainder (a GUESS: a
twenty-farm row fills one or two)."""


def hard_ground(field: Poly, rings: Sequence[Sequence[Pt]] = (), water: Sequence[tuple[Pt, Pt, float]] = ()) -> Any:
    """The ground a row may not stand on, as ONE shapely geometry: the field, the site's other no-build outline (the hem,
    the marsh, the pond - `SiteCorridors.ring_pts`) and each water course at its clearance. A row's line runs off THIS, not
    the field alone: offset from the field only, Mizuguchi's first street ran between its brook and its paddy and the
    farms stood across the water."""
    from shapely.geometry import LineString, Polygon
    from shapely.ops import unary_union

    parts: list[Any] = [Polygon(field).buffer(0)] if len(field) >= 3 else []
    parts += [Polygon(r).buffer(0) for r in rings if len(r) >= 3]
    parts += [LineString([a, b]).buffer(max(float(c), 0.5)) for a, b, c in water if a != b]
    return unary_union(parts) if parts else None


def _ring_near(hard: Any, anchor: Pt, d: float) -> Any:
    """The exterior of the part of `hard` grown by `d` that lies nearest `anchor` (a far pond is its own part)."""
    from shapely.geometry import Point

    grown = hard.buffer(d, join_style="round")
    parts = list(grown.geoms) if hasattr(grown, "geoms") else [grown]
    return min(parts, key=lambda g: g.exterior.distance(Point(anchor))).exterior


def _normal_away(hard: Any, p: Pt, t: Pt) -> Pt:
    """The unit normal to tangent `t` at `p` that points away from the hard ground."""
    from shapely.geometry import Point

    n1 = (-t[1], t[0])
    a = Point(p[0] + n1[0] * 5.0, p[1] + n1[1] * 5.0).distance(hard)
    b = Point(p[0] - n1[0] * 5.0, p[1] - n1[1] * 5.0).distance(hard)
    return n1 if a >= b else (-n1[0], -n1[1])


def street_line(hard: Any, anchor: Pt, offset: float, length: float, form: str, slack: float = 0.0) -> list[tuple[Pt, Pt]]:
    """The street as (point, outward normal) samples every 8 ft, `length` long, centered on the point of the hard ground's
    edge - grown by `offset` - nearest `anchor`. The dry EDGE follows that ring and curves with it. A STREET laid first is
    straight: the line fitted to the same stretch of the ring (its principal axis), then set out until the whole stretch
    lies behind it, so it runs along the ground rather than off a corner of it. `slack` lengthens the line at both ends
    without changing the stretch it is fitted to. [] where there is no hard ground."""
    if hard is None or length <= 0:
        return []
    from shapely.geometry import Point

    ring = _ring_near(hard, anchor, offset)
    total = ring.length
    s0 = ring.project(Point(anchor))
    n = max(2, int(length / 8.0) + 1)
    arc = [ring.interpolate((s0 - length / 2 + k * length / (n - 1)) % total) for k in range(n)]
    pts = [(p.x, p.y) for p in arc]
    if form == "edge":
        if slack > 0:
            length += slack
            n = max(2, int(length / 8.0) + 1)
            pts = [(p.x, p.y) for p in (ring.interpolate((s0 - length / 2 + k * length / (n - 1)) % total) for k in range(n))]
        out: list[tuple[Pt, Pt]] = []
        for k, p in enumerate(pts):
            q, r = pts[min(k + 1, n - 1)], pts[max(k - 1, 0)]
            tx, ty = q[0] - r[0], q[1] - r[1]
            m = math.hypot(tx, ty) or 1.0
            out.append((p, _normal_away(hard, p, (tx / m, ty / m))))
        return out
    mx, my = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    syy = sum((p[1] - my) ** 2 for p in pts)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts)
    th = 0.5 * math.atan2(2 * sxy, sxx - syy)
    t = (math.cos(th), math.sin(th))
    nrm = _normal_away(hard, (mx, my), t)
    push = max((p[0] - mx) * nrm[0] + (p[1] - my) * nrm[1] for p in pts)  # through the stretch's outermost point: all of it behind
    cx, cy = mx + nrm[0] * push, my + nrm[1] * push
    full = length + slack
    m_ = max(2, int(full / 8.0) + 1)
    return [((cx + t[0] * u, cy + t[1] * u), nrm) for u in (-full / 2 + k * full / (m_ - 1) for k in range(m_))]


def frame_extent(bbox: Sequence[float], direction: Pt) -> float:
    """How far an axis-aligned frame (`cx, cy, w, h`) reaches along `direction` (a unit vector), end to end."""
    return abs(direction[0]) * float(bbox[2]) + abs(direction[1]) * float(bbox[3])


def row_seats(line: Sequence[tuple[Pt, Pt]], frame: Sequence[float], sides: str, gap: float) -> list[tuple[Pt, int, Pt, Pt]]:
    """The frame centers along one street, one frame apart (the frame's longer side, so a turn of the line never packs
    two frames closer), from the middle outward alternating the two ends; each on the far side of the street (away from
    the field) and, for BOTH, the near side too - as (center, side, tangent, normal), side +1 far and -1 near. `gap` is
    the room a frame stands off the street's centerline; the street's own samples give the normal at each seat."""
    if len(line) < 2:
        return []
    pts = [p for p, _n in line]
    arc = [0.0]
    for a, b in zip(pts, pts[1:], strict=False):
        arc.append(arc[-1] + math.dist(a, b))
    total = arc[-1]
    step = max(float(frame[2]), float(frame[3]))

    def at(u: float) -> tuple[Pt, Pt, Pt]:
        k = min(len(pts) - 2, next(i for i in range(len(arc) - 1) if arc[i + 1] >= u))
        seg = (arc[k + 1] - arc[k]) or 1.0
        f = (u - arc[k]) / seg
        t = ((pts[k + 1][0] - pts[k][0]) / seg, (pts[k + 1][1] - pts[k][1]) / seg)
        return (pts[k][0] + (pts[k + 1][0] - pts[k][0]) * f, pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f), line[k][1], t

    mid = total / 2
    order = [mid] + [mid + sign * k * step for k in range(1, int(total / step) + 2) for sign in (1, -1)]
    out: list[tuple[Pt, int, Pt, Pt]] = []
    for u in order:
        if not 0.0 <= u <= total:
            continue
        p, n, t = at(u)
        depth = frame_extent(frame, n)
        for side in (1, -1) if sides == "both" else (1,):
            off = side * (gap + depth / 2)
            out.append(((p[0] + n[0] * off, p[1] + n[1] * off), side, t, n))
    return out


HOLDING_DEPTH_FRAMES = {"street": 3.0, "edge": 1.0}
"""A far-row farm's holding behind its lot, in frame depths (feature 291 plan D16): on a street laid first a STRIP (the
planned row's order, house lot then field then woodland, homesteads/156 - its depth there 375 ken, a dry-field colony's;
three frames here is a GUESS, a paddy row borrowing the form, not the size); on the dry edge one frame, compact and near
the house (a dike row's holding, homesteads/156, accurate for a dike row, carried to a levee or fan foot as this
project's reading)."""

HOLDING_CELL_FT = 150.0
"""The holding's plots, cut across its depth at the near ring's cell (`near_ring_dry`'s 150 ft) - a map drawing convention."""


def row_offsets(frame_depth: float, sides: str, streets: int, keep: float, gap: float, holding: float = 0.0) -> list[float]:
    """Each street's offset from the field's margin: the first `keep` out for ONE side (the field across the street),
    or past a near row for BOTH; each next street past the last street's far row, its holdings (`holding` deep, BOTH
    only) and a lane's room."""
    first = keep if sides == "one" else keep + frame_depth + gap
    per = frame_depth * (2 if sides == "both" else 1) + 2 * gap + keep + (holding if sides == "both" else 0.0)
    return [first + i * per for i in range(streets)]


def holding_quad(center: Pt, t: Pt, n: Pt, along: float, depth: float) -> list[Pt]:
    """A holding's rectangle, `along` wide on the tangent `t` and `depth` deep on the normal `n`, about `center`."""
    ax, ay = t[0] * along / 2, t[1] * along / 2
    nx, ny = n[0] * depth / 2, n[1] * depth / 2
    cx, cy = center
    return [(cx - ax - nx, cy - ay - ny), (cx + ax - nx, cy + ay - ny), (cx + ax + nx, cy + ay + ny), (cx - ax + nx, cy - ay + ny)]


def largest_ring(geom: Any) -> list[Pt]:
    """The exterior of a polygon - or of a multi-polygon's largest part - as a point list without the closing repeat."""
    part = geom if geom.geom_type == "Polygon" else max(geom.geoms, key=lambda g: g.area)
    return [(float(x), float(y)) for x, y in list(part.exterior.coords)[:-1]]


def holding_clear(quad: Sequence[Pt], hard: Any, boxes: Sequence[tuple[float, float, float, float]], bounds: tuple[float, float, float, float]) -> list[Pt] | None:
    """The holding clipped to the sheet's `bounds` (a sheet shows only the near end of a strip), or None where it meets the
    hard ground or any reserved box, or where nothing of it is on the sheet."""
    from shapely.geometry import Polygon, box

    q = Polygon(quad)
    clipped = q.intersection(box(*bounds))
    if clipped.is_empty or clipped.area < q.area * 0.25:
        return None
    if hard is not None and clipped.intersects(hard):
        return None
    if any(clipped.intersects(box(x - w / 2, y - h / 2, x + w / 2, y + h / 2)) for x, y, w, h in boxes):
        return None
    return largest_ring(clipped)


FOOTPATH_DOOR_OUT_FT = 12.0
"""How far past the yard's far edge a farm's front door stands (`ways/serve.front_door`: a footpath's gap plus 4 ft, less
the fraction of a foot the frame's pad differs by) - the door `door_clear` tests."""

DOOR_ROOM_FT = 16.0
"""The room a farm's front door needs off the hard ground for a way to start from: a footpath's fabric gap and most of the
router's cell (`WAY_IN_FT`'s measurement) - a map drawing convention."""


def door_clear(frame: tuple[float, float, float, float], front: Sequence[float], pad: float, hard: Any, room: float) -> bool:
    """Is a frame's front door - the middle of its FRONT edge, less its lane pad, `FOOTPATH_DOOR_OUT_FT` out - at least `room`
    off the hard ground? The front is the page face the farm's grove leaves open, where its way in is."""
    if hard is None:
        return True
    from shapely.geometry import Point

    x, y, w, h = frame
    fx, fy = float(front[0]), float(front[1])
    reach = abs(fx) * w / 2 + abs(fy) * h / 2 - pad + FOOTPATH_DOOR_OUT_FT  # the door stands just past the yard, in the pad
    return bool(Point(x + fx * reach, y + fy * reach).distance(hard) >= room)


def frame_on_holdings(frame: tuple[float, float, float, float], holdings: Sequence[Sequence[Pt]]) -> bool:
    """Does an axis-aligned frame (`cx, cy, w, h`) meet any reserved holding?"""
    from shapely.geometry import Polygon, box

    x, y, w, h = frame
    fb = box(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
    return any(fb.intersects(Polygon(q)) for q in holdings)


def draw_holdings(s: Settlement) -> int:
    """Draw each reserved holding (`s._row_holdings`) as dry-field plots cut across its depth at `HOLDING_CELL_FT`, furrowed,
    recorded in `dry_plots` and registered in `dry_polys` (feature 291 plan D16). A cell on water or a lane is left undrawn;
    the rest of the holding stands. Returns the plots drawn."""
    from shapely.geometry import LineString, Polygon

    from l7r.diagram.waterfields import DRY_CROPS

    pal = list(DRY_CROPS.items())
    lanes = [LineString(ln["pts"]).buffer(float(ln.get("w", 3)) / 2 + 2.0) for ln in s.M.get("lanes", []) if len(ln.get("pts") or []) >= 2]
    water = [LineString(st["poly"]).buffer(6.0) for st in s.M.get("streams", []) if len(st.get("poly") or []) >= 2]
    n = 0
    for k, (quad, t, nrm, depth) in enumerate(getattr(s, "_row_holdings", None) or []):
        cells = max(1, round(depth / s.px(HOLDING_CELL_FT)))
        poly = Polygon(quad)
        crop, (fill, fur) = pal[k % len(pal)]
        mx = sum(p[0] for p in quad) / len(quad)
        my = sum(p[1] for p in quad) / len(quad)
        for c in range(cells):
            lo, hi = -depth / 2 + depth * c / cells, -depth / 2 + depth * (c + 1) / cells
            band = Polygon(holding_quad((mx + nrm[0] * (lo + hi) / 2, my + nrm[1] * (lo + hi) / 2), t, nrm, 1e5, hi - lo)).intersection(poly)
            if band.is_empty or band.area < 1.0 or any(band.intersects(g) for g in lanes + water):
                continue
            cell = largest_ring(band)
            pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in cell)
            s.add(f'<polygon points="{pts}" fill="{fill}" stroke="#A98C58" stroke-width="1.4" stroke-linejoin="round"/>')
            theta = math.atan2(nrm[1], nrm[0]) % math.pi  # the furrows run down the strip, across the street
            s._draw_furrows(cell, fur, theta)
            # `homestead`: a farm's own holding, not the field's hem - the reed toe is measured below the FIELD'S lowest crop
            # (`toe_band`), and read as field crop a holding moved the toe 220 ft onto three Kashikawa farms' doors
            s.M["dry_plots"].append({"poly": [[round(x, 1), round(y, 1)] for x, y in cell], "crop": crop, "theta": round(theta, 3), "holding": k, "homestead": True})
            s.dry_polys.append(cell)
            n += 1
    return n


def seat_rows(s: Settlement, plan: SitePlan, frame: Sequence[float], allowed: Any = None) -> int:
    """Seat a linear hamlet's farms in rows along its streets (`row_offsets`, `street_line`, `row_seats`), each seat
    offered once to the placer at the frame's own house offset; returns the farms seated, and keeps the streets that
    seated any on `s._row_streets` (a list of point lists) and the line and sides on the manifest."""
    want = plan.spec.households
    field = [(float(x), float(y)) for x, y in (plan.envelope or [])]
    corr = getattr(s, "_site_corridors", None)
    # ...AND THE WET GROUND the ways refuse: the toe marsh (asked before it is drawn, as `stage_web` asks it) and every marsh
    # drawn so far - missing, three Kashikawa farms fronted the toe marsh and no way could reach their doors
    wet = [[(float(a), float(b)) for a, b in (s.toe_band() or [])]] + [[(float(a), float(b)) for a, b in m["poly"]] for m in s.M.get("marshes", []) if m.get("role") != "defense" and m.get("poly")]
    hard = hard_ground(field, [*(getattr(corr, "ring_pts", ()) or ()), *[w for w in wet if len(w) >= 3]], getattr(corr, "water", ()) or ())
    anchor = (float(plan.seat["cx"]), float(plan.seat["cy"]))
    sides = plan.row_sides
    per_line = math.ceil(want / (2 if sides == "both" else 1))
    gap = s.px(STREET_HALF_FT) + s.px(FIELD_KEEP_FT) / 2
    fw, fd = max(float(frame[2]), float(frame[3])), min(float(frame[2]), float(frame[3]))
    hx_off, hy_off = float(frame[0]), float(frame[1])  # the frame's center relative to its house
    # THE FRONT DOOR'S GROUND (plan D17): a farm's way in is at its front - the lee face its grove leaves open - so a seat
    # whose front edge stands on the hard ground's footpath margin has no way in (Kashikawa: three near-row farms fronting
    # the marsh, no route from their doors to the street) and is passed over like a refused seat
    front = grove_faces(plan.windward, plan.grove_sides, plan.grove_flank)[2]
    door_room = s.px(DOOR_ROOM_FT)
    lane_pad = s.px(LANE_ROOM_FT) / 2
    streets: list[list[Pt]] = []
    placed = 0
    s._exact_seat = True  # type: ignore[attr-defined]  # the placer nudges a row's seat, never slides it (`_place_bundle_dispersed`)
    hold_depth = fd * HOLDING_DEPTH_FRAMES.get(plan.row_line, 1.0)
    bounds = (30.0, 30.0, float(s.W) - 30.0, float(s.H) - 30.0)
    holdings: list[tuple[list[Pt], Pt, Pt, float]] = []
    for off in row_offsets(fd, sides, MAX_STREETS, s.px(FIELD_KEEP_FT), gap, hold_depth + gap):
        if placed >= want:
            break
        # two lots of slack beyond what the row needs: a refused seat is taken up at the row's end rather than sent to a
        # second street across the holdings (Kashikawa: one farm alone on a second street no way could reach)
        line = street_line(hard, anchor, off, per_line * fw + fw, plan.row_line, slack=2 * fw)
        took = 0
        for (fx, fy), side, t, nrm in row_seats(line, frame, sides, gap):
            if placed >= want:
                break
            hx, hy = fx - hx_off, fy - hy_off
            if not (0 < hx < s.W and 0 < hy < s.H) or (allowed is not None and not allowed(hx, hy)):
                continue
            # A FAR-ROW FARM IS SEATED ONLY WITH ITS HOLDING (plan D16): behind its lot, away from the street, clear of the
            # hard ground and every reserved box - else not seated here, as a farm whose grove has no room is not.
            if not door_clear((fx, fy, float(frame[2]), float(frame[3])), front, lane_pad, hard, door_room):
                continue
            # ...and no farm stands on a holding already reserved (cohort seeds 3 and 4: houses, yards and gardens on dry plots)
            if holdings and frame_on_holdings((fx, fy, float(frame[2]), float(frame[3])), [hq for hq, *_r in holdings]):
                continue
            hold = None
            if sides == "both" and side > 0:
                depth_here = frame_extent(frame, nrm)
                along_here = frame_extent(frame, t) - 2 * gap
                hc = (fx + nrm[0] * (depth_here / 2 + gap / 2 + hold_depth / 2), fy + nrm[1] * (depth_here / 2 + gap / 2 + hold_depth / 2))
                boxes = [(float(p[0]), float(p[1]), float(p[2]), float(p[3])) for p in s.placed]
                hold = holding_clear(holding_quad(hc, t, nrm, along_here, hold_depth), hard, boxes, bounds)
                if hold is None:
                    continue
            if s.try_place(hx, hy, "plain"):
                placed += 1
                took += 1
                if hold is not None:
                    rec = s._pending_farmsteads[-1]  # the farm just seated (`try_place` queues its record)
                    holdings.append((hold, t, nrm, hold_depth))
                    s.M.setdefault("row_holdings", []).append({"id": len(holdings) - 1, "of": [float(rec["x"]), float(rec["y"])], "poly": [[round(x, 1), round(y, 1)] for x, y in hold]})
                    s.block_polys.append(hold)  # the next placers and the woods keep off it (plan D16)
                    s.hard_polys.append(hold)
        if took:
            on_sheet = [p for p, _n in line if 0.0 <= p[0] <= s.W and 0.0 <= p[1] <= s.H]  # the sheet's part: the road runs on from its edge
            streets.append(on_sheet if len(on_sheet) >= 2 else [p for p, _n in line])
    s._exact_seat = False  # type: ignore[attr-defined]
    s._row_holdings = holdings  # type: ignore[attr-defined]
    s._row_streets = streets  # type: ignore[attr-defined]
    s.M["meta"]["row_streets"] = len(streets)
    s.M["row_street_plans"] = [[[round(x, 1), round(y, 1)] for x, y in line[:: max(1, len(line) // 60)] + line[-1:]] for line in streets]  # the planned lines, for the street and row rules
    return placed
