"""THE ROW VILLAGE (feature 291 amendment 3; research/questions/0033-row-villages-resson.html) - a linear hamlet's farms in rows along
their streets, never in ranks behind a row.

The record gives a row two lines, and both are drawn (`ROW_LINES`): a STREET LAID FIRST, straight as a surveyed road -
the planned row's form, which a paddy row may borrow - or the DRY EDGE THE GROUND GIVES, a levee, a dike, a fan's foot,
for which the field's margin stands here (this project's reading), the row curving with it. The farms stand on ONE side
of the street, the field across it, or on BOTH (`ROW_SIDES`), one FRAME apart - the grove farm's own ground and grove
and the lane's room between two groves (homesteads/715), a physical necessity, since a grove farm cannot stand on a
narrower lot. A row the line cannot hold grows another street parallel to the first, one row set further out, as a
planned colony grew more roads (0033) - how many farms a line holds before the next street is the ground's.

This module is pure geometry and one seating loop: `row_streets` gives the lines, `row_seats` the frame centers along
them, `seat_rows` asks the placer for each. The streets it planned are kept on the settlement for the web
(`ways/web.py` `_lay_street`), which lays each as one continuous way.

Research: row geometry - NONE: lines, offsets, clipping and seat arithmetic; the units that decide carry their own claims
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
drawing convention, near enough that the field reads as the row's own, clear enough that the street is not on a bund.

Research: street off the field - research/questions/0033-row-villages-resson.drawing.html: 24 ft off the field's margin
"""

STREET_HALF_FT = 3.0
"""Half the street's drawn width (the connector's 6 ft tread; the web's lanes are 3-5), the room a row stands back from it.

Research: street width - research/questions/0033-row-villages-resson.drawing.html: drawn 6 ft, where Santome's roads were 36 ft
"""

ROW_FRONTAGE_MAX_FT = 240.0
"""The widest a farm's lot fronts its street (the GM, 2026-10-01: "we do want the spacing capped at 240 feet"): Santome's
40 ken, the widest frontage on the planned rows measured (research/questions/0033-row-villages-resson.html, "How wide was a
farm's frontage on a planned row?" - 54 to 240 ft). Neighbors stood one frontage apart, lot against lot (the same entry), so
the row steps at its farm's frame or at this, whichever is narrower: a frame wider than the lot (a three- or four-sided
grove, 261 ft with the lane's room) keeps its grove and gives up part of the lane's room between two neighbors' groves.

Research: widest frontage - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: 240 ft cap on the step
"""

STREET_TREAD_PAD_FT = 0.5
"""How far past a street's tread a farm's laid part keeps off it while the row is seated: the lane law's own pad round a
fixture (`ways/law.FIXTURE_PAD_FT`), so a part kept off here is one the drawn street clears."""

MAX_STREETS = 6
"""The most parallel streets a row village grows (a GUESS): a twenty-farm row on open ground fills one or two, but where
the line soon runs off the sheet each street holds a few (cohort seed 12, four-sided groves: four streets seated 13 of 17).
A farm six streets cannot hold is reported unseated.

Research: most streets - research/questions/0033-row-villages-resson.drawing.html: six parallel streets at most
"""


def hard_ground(field: Poly, rings: Sequence[Sequence[Pt]] = (), water: Sequence[tuple[Pt, Pt, float]] = ()) -> Any:
    """The ground a row may not stand on, as ONE shapely geometry: the field, the site's other no-build outline (the hem,
    the marsh, the pond - `SiteCorridors.ring_pts`) and each water course at its clearance. A row's line runs off THIS, not
    the field alone: offset from the field only, Mizuguchi's first street ran between its brook and its paddy and the
    farms stood across the water.

    Research: street off all no-build ground - UNRESEARCHED: the field, the hem, marsh, pond and every water course at its clearance
    """
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
    without changing the stretch it is fitted to. [] where there is no hard ground.

    Research: line form - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: a street laid first straight, the dry edge curving with the field's margin
    """
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


def row_seats(line: Sequence[tuple[Pt, Pt]], frame: Sequence[float], sides: str, gap: float, pitch: float = math.inf) -> list[tuple[Pt, int, Pt, Pt]]:
    """The frame centers along one street, one frame apart (the frame's longer side, so a turn of the line never packs
    two frames closer) or `pitch` apart where that is narrower (the lot's frontage, `ROW_FRONTAGE_MAX_FT`), from the middle outward alternating the two ends; each on the far side of the street (away from
    the field) and, for BOTH, the near side too - as (center, side, tangent, normal), side +1 far and -1 near. `gap` is
    the room a frame stands off the street's centerline; the street's own samples give the normal at each seat.

    Research:
        farm spacing - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: one frame apart (its longer side), or the lot's frontage where narrower
        one side or both - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: the far side only, or both sides of the street
        seat order - UNRESEARCHED: from the line's middle outward, alternating ends
    """
    if len(line) < 2:
        return []
    pts = [p for p, _n in line]
    arc = [0.0]
    for a, b in zip(pts, pts[1:], strict=False):
        arc.append(arc[-1] + math.dist(a, b))
    total = arc[-1]
    step = min(max(float(frame[2]), float(frame[3])), pitch)

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
"""A far-row farm's holding behind its lot, in lots - frame WIDTHS along the street (feature 291 plan D16; feature 328: it
was the frame's shorter side, against 0033's "three times the frame's width"): on a street laid first a STRIP (the
planned row's order, house lot then field then woodland, 0033 - its depth there 375 ken, a dry-field colony's;
three lots here is a GUESS, a paddy row borrowing the form, not the size); on the dry edge one lot, compact and near
the house (a dike row's holding, 0033, accurate for a dike row, carried to a levee or fan foot as this
project's reading).

Research:
    far-row dry-field share - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: a fixed depth behind the lot, 3 lots (frame widths) on a street laid first and 1 on the dry edge, every foot of it drawn dry field; the share is never rolled or set, it falls out of the geometry
"""

HOLDING_CELL_FT = 150.0
"""The holding's plots, cut across its depth at the near ring's cell (`near_ring_dry`'s 150 ft) - a map drawing convention.

Research: holding plot depth - research/questions/0033-row-villages-resson.drawing.html: 150 ft
"""


def row_offsets(frame_depth: float, sides: str, streets: int, keep: float, gap: float, holding: float = 0.0) -> list[float]:
    """Each street's offset from the field's margin: the first `keep` out for ONE side (the field across the street),
    or past a near row for BOTH; each next street past the last street's far row, its holdings (`holding` deep, BOTH
    only) and a lane's room.

    Research: next street beside, never behind - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: each further street past the far row's holdings and a lane's room
    """
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
router's cell (`WAY_IN_FT`'s measurement) - a map drawing convention.

Research: door room - NONE: 16 ft, a routing tolerance a way needs to start (called a map drawing convention above)
"""


def door_clear(frame: tuple[float, float, float, float], front: Sequence[float], pad: float, hard: Any, room: float) -> bool:
    """Is a frame's front door - the middle of its FRONT edge, less its lane pad, `FOOTPATH_DOOR_OUT_FT` out - at least `room`
    off the hard ground? The front is the page face the farm's grove leaves open, where its way in is.

    Research: way in at the open front - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the door on the lee face the grove leaves open
    """
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


def seat_allowed(hx: float, hy: float, w: float, h: float, allowed: Any) -> bool:
    """May a row farm's house stand at (`hx`, `hy`): on the `w` x `h` sheet, and where the stage's `allowed` says it may
    (lifted from `seat_rows`, feature 291: no pool roll reaches the refusal once the streets keep inside the sheet)."""
    return 0 < hx < w and 0 < hy < h and (allowed is None or bool(allowed(hx, hy)))


def frame_refused(fr: tuple[float, float, float, float], front: Sequence[float], lane_pad: float, hard: Any, door_room: float, all_streets: Any, holdings: Sequence[Sequence[Pt]]) -> bool:
    """Is a row seat's frame refused (lifted from `seat_rows`, feature 291)? Its door has no room (`door_clear`); or the
    frame reaches across ANY of the row's streets where a line bends - square to its own line at its seat, it stood on a
    street at the bend, and no route round its yard and grove existed (cohort seed 23); or it stands on a holding already
    reserved (cohort seeds 3 and 4: houses, yards and gardens on dry plots)."""
    from shapely.geometry import box

    if not door_clear(fr, front, lane_pad, hard, door_room):
        return True
    fx, fy, fw, fh = fr
    if all_streets is not None and box(fx - fw / 2, fy - fh / 2, fx + fw / 2, fy + fh / 2).intersects(all_streets):
        return True
    return bool(holdings) and frame_on_holdings(fr, holdings)


def draw_holdings(s: Settlement) -> int:
    """Draw each reserved holding (`s._row_holdings`) as dry-field plots cut across its depth at `HOLDING_CELL_FT`, furrowed,
    recorded in `dry_plots` and registered in `dry_polys` (feature 291 plan D16). A cell on water or a lane is left undrawn;
    the rest of the holding stands. Returns the plots drawn.

    Research:
        holding drawn as dry field - research/questions/0033-row-villages-resson.drawing.html: every cell a dry crop, none paddy
        furrows down the strip - CONVENTION: across the street, the crops cycled from the dry palette
    """
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
            s.add(f'<polygon points="{pts}" fill="{fill}" stroke="#A98C58" stroke-width="1.4" stroke-linejoin="round"/>', cls="farm holding")
            theta = math.atan2(nrm[1], nrm[0]) % math.pi  # the furrows run down the strip, across the street
            s._draw_furrows(cell, fur, theta, cls="farm holding")
            # `holding`: a farm's own holding, not the field's hem - the reed toe is measured below the FIELD'S lowest crop
            # (`toe_band`), and read as field crop a holding moved the toe 220 ft onto three Kashikawa farms' doors
            s.M["dry_plots"].append({"poly": [[round(x, 1), round(y, 1)] for x, y in cell], "crop": crop, "theta": round(theta, 3), "holding": k})
            s.dry_polys.append(cell)
            n += 1
    return n


def inside_the_sheet(line: Sequence[tuple[Pt, Pt]], bounds: tuple[float, float, float, float]) -> list[tuple[Pt, Pt]]:
    """The longest run of consecutive `line` samples inside `bounds` (x0, y0, x1, y1); [] where none is."""
    best: list[tuple[Pt, Pt]] = []
    run: list[tuple[Pt, Pt]] = []
    for p, n in line:
        if bounds[0] <= p[0] <= bounds[2] and bounds[1] <= p[1] <= bounds[3]:
            run.append((p, n))
            if len(run) > len(best):
                best = list(run)
        else:
            run = []
    return best


def longest_part(geom: Any) -> list[Pt]:
    """The coordinates of a line geometry's longest part - itself for a LineString; [] for an empty or zero-length one."""
    if geom.geom_type == "MultiLineString":
        geom = max(geom.geoms, key=lambda g: g.length)
    if geom.is_empty or geom.length <= 0.0:
        return []
    return [(float(x), float(y)) for x, y in geom.coords]


def street_bend_radius_ft() -> float:
    """The radius a further street is rounded at on the inside of a corner (`parallel`): twice the radius at which one step of
    the lane law's bend run (`clearance._ZIGZAG_RUN_FT`, 40 ft - the drawn street keeps a vertex about that often) turns a
    kink's turn (`_ZIGZAG_DEG`, 50 degrees) - about 92 ft. At it a drawn vertex turns about 25 degrees, and one thinned to
    48 ft about 30, never two kinks' turns inside a run. A MAP DRAWING CONVENTION derived from the law's figures, not a finding.

    Research: street bend radius - CONVENTION: about 92 ft, from the lane law's bend figures
    """
    from ..ways.clearance import _ZIGZAG_DEG, _ZIGZAG_RUN_FT  # the ways import this package's seats; read where it is used

    return 2.0 * _ZIGZAG_RUN_FT / math.radians(_ZIGZAG_DEG)


def parallel(line: Sequence[tuple[Pt, Pt]], d: float, radius: float = 0.0) -> list[tuple[Pt, Pt]]:
    """`line` set out `d` on its outward side (the next street of a row village, plan D15), as a TRUE parallel curve
    (`offset_curve`, rounded at the joins) resampled at the line's own spacing, each sample carrying the outward normal
    of the first street's sample nearest it. Set out sample by sample along each one's own normal, the samples on the
    inside of a bend tighter than `d` crossed over each other and the street drawn through them doubled back: Mizuguchi's
    second street, set out 400 ft beyond a first that curves with the brook's bank, was a 7,208 ft line with 17 turns past
    140 degrees (settlement-review, 2026-09-30); dropping the samples that ran back still left two folds.

    ...AND ROUNDED ON THE INSIDE OF A CORNER at `radius` (set out `d + radius`, then back `radius`: a closing, which leaves a
    straight stretch and the outside of a bend where they were). An offset curve is sharp wherever the first street turns
    toward its outward side, and turns there by as much as the first street does round the corner: cohort seed 903's edge
    street ran a Z round the field, its second street came out with a 142 degree corner - a hairpin of the lane law - and a
    street is a tree lane no settle may cut, so the web was refused (feature 306).

    Research: further streets parallel - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: each next street a true parallel of the first
    """
    if len(line) < 2 or d == 0.0:
        return [((p[0] + n[0] * d, p[1] + n[1] * d), n) for p, n in line]
    from shapely.geometry import LineString

    pts = [p for p, _n in line]
    base = LineString(pts)
    # THE OUTWARD SIDE FROM THE NORMALS THEMSELVES, each sample's normal asked whether it stands left of the line's own
    # tangent (shapely's positive offset): asked of the one curve nearest a point set out from the middle sample, the side was
    # wrong wherever the inside offset is trimmed back past that sample - as it is round any corner sharper than the offset
    left = sum(n[0] * -(b[1] - a[1]) + n[1] * (b[0] - a[0]) for (a, n), (b, _m) in zip(line, line[1:], strict=False))
    side = (1.0 if left >= 0.0 else -1.0) * (1.0 if d > 0.0 else -1.0)
    coords = longest_part(base.offset_curve(side * (abs(d) + radius), join_style="round"))
    if radius > 0.0 and len(coords) >= 2:
        coords = longest_part(LineString(coords).offset_curve(-side * radius, join_style="round"))  # ...and back: the closing
    if len(coords) < 2:
        return []
    off = LineString(coords)  # in the first street's direction on either side: shapely 2 keeps an offset's direction
    step = max(math.dist(pts[0], pts[1]), 1.0)
    k = max(1, int(off.length // step))
    qs = [(float(q.x), float(q.y)) for q in (off.interpolate(off.length * i / k) for i in range(k + 1))]
    out: list[tuple[Pt, Pt]] = []
    for i, qp in enumerate(qs):
        # THE NORMAL OF THE NEW STREET ITSELF, square to its own tangent on the first street's outward side: borrowed from the
        # first street's nearest sample, every sample round a rounded corner took the corner's one normal, and the farms
        # seated along the arc all faced one way and stood behind each other (cohort seed 904)
        a, b = qs[max(0, i - 1)], qs[min(len(qs) - 1, i + 1)]
        tl = math.dist(a, b) or 1.0
        n0 = min(line, key=lambda s: math.dist(s[0], qp))[1]
        nx, ny = -(b[1] - a[1]) / tl, (b[0] - a[0]) / tl
        out.append((qp, (nx, ny) if nx * n0[0] + ny * n0[1] >= 0.0 else (-nx, -ny)))
    return out


def clear_frames(
    line: Sequence[tuple[Pt, Pt]],
    frame: Sequence[float],
    sides: str,
    gap: float,
    hard: Any,
    bounds: tuple[float, float, float, float],
    front: Sequence[float],
    pad: float,
    room: float,
    pitch: float = math.inf,
) -> int:
    """How many of a line's row seats hold a frame clear of the hard ground, inside `bounds`, with room at its door - the
    measure `best_row_line` ranks a stretch by (the placer still decides each seat)."""
    from shapely.geometry import box

    n = 0
    for (fx, fy), _side, _t, _n in row_seats(line, frame, sides, gap, pitch):
        w, h = float(frame[2]), float(frame[3])
        inside = bounds[0] <= fx - w / 2 and fx + w / 2 <= bounds[2] and bounds[1] <= fy - h / 2 and fy + h / 2 <= bounds[3]
        if inside and (hard is None or not box(fx - w / 2, fy - h / 2, fx + w / 2, fy + h / 2).intersects(hard)) and door_clear((fx, fy, w, h), front, pad, hard, room):
            n += 1
    return n


def best_row_line(
    hard: Any,
    anchor: Pt,
    offset: float,
    length: float,
    form: str,
    slack: float,
    frame: Sequence[float],
    sides: str,
    gap: float,
    bounds: tuple[float, float, float, float],
    front: Sequence[float],
    pad: float,
    room: float,
    samples: int = 16,
    pitch: float = math.inf,
) -> list[tuple[Pt, Pt]]:
    """The first street of a row village: of the lines centered on the planned seat's point of the hard ground's grown edge
    and on `samples` points of that edge within a row's length either way of it, the one holding the most clear frames
    (`clear_frames`), the nearest the seat among equals. [] where there is no hard ground.

    Research: where the street runs - research/questions/0033-row-villages-resson.drawing.html: the stretch within a row's length of the seat that holds the most farms
    """
    if hard is None:
        return []
    from shapely.geometry import Point

    ring = _ring_near(hard, anchor, offset)
    s0 = ring.project(Point(anchor))
    total = ring.length
    # ...within one row's length of the seat along the edge: the brook and the marsh carry the hard ground's edge off to the
    # sheet's far side, and a stretch there held clear frames the placer then refused as far from the field (cohort seed
    # 12 on its larger canvas: 3 of 17 seated at the bottom edge)
    near = min(total / 2, length)
    tries = [anchor] + [(p.x, p.y) for p in (ring.interpolate((s0 + near * (2 * k / (samples - 1) - 1)) % total) for k in range(samples))]
    best: tuple[int, float, list[tuple[Pt, Pt]]] | None = None
    for a in tries:
        line = street_line(hard, a, offset, length, form, slack=slack)
        score = (clear_frames(line, frame, sides, gap, hard, bounds, front, pad, room, pitch), -math.dist(a, anchor))
        if best is None or score > best[:2]:
            best = (score[0], score[1], line)
    assert best is not None
    return best[2]


def seat_rows(s: Settlement, plan: SitePlan, frame: Sequence[float], allowed: Any = None) -> int:
    """Seat a linear hamlet's farms in rows along its streets (`row_offsets`, `street_line`, `row_seats`), each seat
    offered once to the placer at the frame's own house offset; returns the farms seated, and keeps the streets that
    seated any on `s._row_streets` (a list of point lists) and the line and sides on the manifest.

    Research:
        row farm faces its street - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: never turned to its street - every frame keeps the settlement's one windward orientation (grove to windward, open front to lee, `grove_faces(plan.windward, ...)`) on either side of the street, so only the grove-to-windward form is drawn and the house turned to face its road never is
        far-row dry-field share - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: each far-row farm's holding one lot wide and `HOLDING_DEPTH_FRAMES` lots deep, all dry field; the near row and a one-sided row hold none
        far-row farm only with its holding - research/questions/0033-row-villages-resson.drawing.html: a far-row seat whose holding does not fit clear is passed over
        farms to a street - research/questions/0033-row-villages-resson.drawing.html: a full street gets a further street set out parallel beside it, never a second row behind
        a line's share and length - UNRESEARCHED: half the households to a line on both sides, the line one lot longer than its farms with two lots of search room (`best_row_line`); the page (0033 drawing) says only that a street holds what its ground allows
        farms one frame apart, never more than 240 ft - research/questions/0033-row-villages-resson.drawing.html: the row steps one frame, `lot = min(fw, ROW_FRONTAGE_MAX_FT)`, lot against lot and never past Santome's 240 ft lots
        the next street past the last one's holdings - research/questions/0033-row-villages-resson.drawing.html: each further street is set out past the last street's frames and their holdings (`row_offsets(..., hold_depth + gap)`), its own gap off the street as `frame off the street`
        holding set behind its frame - UNRESEARCHED: the strip starts half the 15 ft gap (7.5 ft) behind its farm's frame; the page (0033 drawing) says only that it is drawn behind each farm
        at most MAX_STREETS (6) parallel streets - GUESS: six streets at most (research/questions/0033-row-villages-resson.drawing.html)
        front door's ground: a frame refused without DOOR_ROOM_FT (16 ft) and half LANE_ROOM_FT clear before its front - UNRESEARCHED: the 16 ft door room `DOOR_ROOM_FT` declares; no cited page measures a door's ground
        frame off the street - UNRESEARCHED: half the street plus half `FIELD_KEEP_FT`, 15 ft off its centerline
        first street on the hard ground's edge - research/questions/0033-row-villages-resson.drawing.html: the first street runs along the stretch of the hard ground's edge that holds the most clear frames (`best_row_line`)
        streets rounded at a corner - UNRESEARCHED: a street is rounded on the inside of a corner at `street_bend_radius_ft`
    """
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
    lot = min(fw, s.px(ROW_FRONTAGE_MAX_FT))  # the row's step: one frame, never past the widest frontage measured
    hx_off, hy_off = float(frame[0]), float(frame[1])  # the frame's center relative to its house
    # THE FRONT DOOR'S GROUND (plan D17): a farm's way in is at its front - the lee face its grove leaves open - so a seat
    # whose front edge stands on the hard ground's footpath margin has no way in (Kashikawa: three near-row farms fronting
    # the marsh, no route from their doors to the street) and is passed over like a refused seat
    front = grove_faces(plan.windward, plan.grove_sides, plan.grove_flank)[2]
    door_room = s.px(DOOR_ROOM_FT)
    lane_pad = s.px(LANE_ROOM_FT) / 2
    streets: list[list[Pt]] = []
    street_farms: list[list[Pt]] = []
    placed = 0
    s._exact_seat = True  # type: ignore[attr-defined]  # the placer nudges a row's seat, never slides it (`_place_bundle_dispersed`)
    hold_depth = lot * HOLDING_DEPTH_FRAMES.get(plan.row_line, 1.0)  # the frame's WIDTH, a lot (0033: three times the frame's width)
    bounds = (30.0, 30.0, float(s.W) - 30.0, float(s.H) - 30.0)
    holdings: list[tuple[list[Pt], Pt, Pt, float]] = []
    # WHERE THE ROW GOES: the stretch of the hard ground's edge whose line holds the most clear frames, the planned seat
    # breaking a tie - seated at the plan's seat alone, a seat on a narrow strip between field and marsh held one farm and
    # the rest went to streets that circled to the far side of the map (cohort seed 12)
    first_off = row_offsets(fd, sides, 1, s.px(FIELD_KEEP_FT), gap)[0]
    first = best_row_line(hard, anchor, first_off, per_line * lot + lot, plan.row_line, 2 * lot, frame, sides, gap, bounds, front, lane_pad, door_room, pitch=lot)
    # ...and the streets beyond it set out by the frame's depth ALONG THE LINE'S NORMAL, not its shorter side: on a diagonal
    # street a frame reaches deeper, and the second street ran through the first row's groves (cohort seed 901)
    depth_n = max((frame_extent(frame, n) for _p, n in first), default=fd)
    offsets = row_offsets(depth_n, sides, MAX_STREETS, s.px(FIELD_KEEP_FT), gap, hold_depth + gap)
    offsets = [first_off + (o - offsets[0]) for o in offsets]
    from shapely.geometry import LineString, MultiLineString

    # ...EACH ROUNDED ON THE INSIDE OF A CORNER at the radius a drawn street bends through lawfully (`parallel`, feature 306)
    planned = [parallel(first, o - offsets[0], s.px(street_bend_radius_ft())) for o in offsets]
    all_streets = MultiLineString([LineString([p for p, _n in ln]) for ln in planned if len(ln) >= 2]) if first else None
    # THE STREETS' TREAD IS RESERVED WHILE THEIR FARMS ARE SEATED (`overlap/reserved.py`'s corridor rule): a part a farm lays
    # - a fixture, its well pocket - is admitted only off every planned street's tread, as the frame is (`frame_refused`).
    # Unreserved, the end farm of Mizuguchi's row laid a fixture on its street, the drawn street was refused on it, and
    # seven farms stood off the network (2026-10-01). Released when the row is seated: the web draws the street itself.
    res = s.standing.reserved
    street_mark = res.corridors_mark()
    tread = s.px(STREET_HALF_FT + STREET_TREAD_PAD_FT)
    for ln in planned:
        for (a, _na), (b, _nb) in zip(ln, ln[1:], strict=False):
            res.reserve_corridor(a, b, tread)
    for off in offsets:
        if placed >= want:
            break
        # two lots of slack beyond what the row needs: a refused seat is taken up at the row's end rather than sent to a
        # second street across the holdings (Kashikawa: one farm alone on a second street no way could reach). Each next
        # street is the FIRST one set out parallel, so the streets stay a grid beside each other (FR-016)
        # ...ITS STRETCH INSIDE THE SHEET BY HALF A FRAME: set out round a bend, Mizuguchi's second street ran 675 ft down
        # the canvas's west edge, outside the farms it served and past the view the map is cropped to - a second way off
        # the map past its notice board (settlement-review, 2026-09-30)
        line = inside_the_sheet(planned[offsets.index(off)], (fd / 2, fd / 2, float(s.W) - fd / 2, float(s.H) - fd / 2))
        took = 0
        mine: list[Pt] = []  # this street's farms, as seated - what its span is drawn over (`ways/street.lay_row_streets`)
        seats = [q for q in row_seats(line, frame, sides, gap, lot) if seat_allowed(q[0][0] - hx_off, q[0][1] - hy_off, float(s.W), float(s.H), allowed)]
        for (fx, fy), side, t, nrm in seats:
            if placed >= want:
                break
            hx, hy = fx - hx_off, fy - hy_off
            # A FAR-ROW FARM IS SEATED ONLY WITH ITS HOLDING (plan D16): behind its lot, away from the street, clear of the
            # hard ground and every reserved box - else not seated here, as a farm whose grove has no room is not.
            if frame_refused((fx, fy, float(frame[2]), float(frame[3])), front, lane_pad, hard, door_room, all_streets, [hq for hq, *_r in holdings]):
                continue
            hold = None
            if sides == "both" and side > 0:
                depth_here = frame_extent(frame, nrm)
                along_here = lot  # one lot wide, lot against lot (0033) - not the frame's extent, which shrinks as the street turns
                hc = (fx + nrm[0] * (depth_here / 2 + gap / 2 + hold_depth / 2), fy + nrm[1] * (depth_here / 2 + gap / 2 + hold_depth / 2))
                boxes = [(float(p[0]), float(p[1]), float(p[2]), float(p[3])) for p in s.placed]
                hold = holding_clear(holding_quad(hc, t, nrm, along_here, hold_depth), hard, boxes, bounds)
                if hold is None:
                    continue
            if s.try_place(hx, hy, "plain"):
                placed += 1
                took += 1
                mine.append((float(s._pending_farmsteads[-1]["x"]), float(s._pending_farmsteads[-1]["y"])))
                if hold is not None:
                    rec = s._pending_farmsteads[-1]  # the farm just seated (`try_place` queues its record)
                    holdings.append((hold, t, nrm, hold_depth))
                    s.M.setdefault("row_holdings", []).append({"id": len(holdings) - 1, "of": [float(rec["x"]), float(rec["y"])], "poly": [[round(x, 1), round(y, 1)] for x, y in hold]})
                    s.block_polys.append(hold)  # the next placers and the woods keep off it (plan D16)
                    s.hard_polys.append(hold)
        if took:
            on_sheet = [p for p, _n in line if 0.0 <= p[0] <= s.W and 0.0 <= p[1] <= s.H]  # the sheet's part: the road runs on from its edge
            streets.append(on_sheet if len(on_sheet) >= 2 else [p for p, _n in line])
            street_farms.append(mine)
    res.release_corridors_to(street_mark)
    s._exact_seat = False  # type: ignore[attr-defined]
    s._row_holdings = holdings  # type: ignore[attr-defined]
    s._row_streets = streets  # type: ignore[attr-defined]
    s._row_street_farms = street_farms  # type: ignore[attr-defined]
    s.M["meta"]["row_streets"] = len(streets)
    s.M["row_street_plans"] = [[[round(x, 1), round(y, 1)] for x, y in line[:: max(1, len(line) // 60)] + line[-1:]] for line in streets]  # the planned lines, for the street and row rules
    return placed
