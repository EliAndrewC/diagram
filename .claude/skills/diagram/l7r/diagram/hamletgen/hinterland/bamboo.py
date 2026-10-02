"""Split from hamletgen/hinterland.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist
from l7r.diagram.settlement._geom.indexes import BambooObstacles
from l7r.diagram.settlement.homestead_parts.bamboo_keepout import stand_spares_seats
from l7r.diagram.settlement.homestead_parts.tree_shade import BAMBOO_SHADE_FT
from l7r.diagram.settlement.land.wet import marsh_ground

from ..consts import Poly, Pt
from ..plan import SitePlan
from .frame import frame_bounds, title_pocket
from .parcels import _parcel_outline

# THE BAMBOO STANDS (feature 133 T47/T48, GM 2026-08-27; research/questions/0075-bamboo-groves-chikurin.html; research/questions/0075-bamboo-groves-chikurin.drawing.html). Two attested forms, the `bamboo` knob's values: the THICKET (take-yabu),
# ONE stand at the settlement's edge, seated here on dry ground just beyond the cluster's back (north) row - not at
# the field margin: feature 280 M49 (research/questions/0075-bamboo-groves-chikurin.html) finds a bamboo thicket round the settlement before modern
# times (an early-Edo screen, the Nagaokakyo bamboo villages, the Qimin yaoshu's high dry ground), while the field
# margin's shady end rested on a present-day page; which side of the cluster, and that the stand is held in common,
# are GUESSES; and HOUSEHOLD bamboo, a small strip on each farmstead that keeps one
# (`household_bamboo` in homesteads.py, seated with the sheds and gardens). The thicket's size is a working
# harvested stand in real feet; a stand under the legibility floor does not read at fit zoom.
BAMBOO_THICKET_FT = (84.0, 58.0)
BAMBOO_LEGIBLE_FT = 14.0  # the SHORT axis: a household strip is ~16 ft deep and reads; below this, nothing does


def bamboo_blocked(
    x: float,
    y: float,
    extent: Pt,
    pocket: tuple[float, float, float, float],
    rects: Sequence[tuple[float, float, float, float, float]],
    lanes: Sequence[tuple[Poly, float]],
    polys: Sequence[tuple[Poly, float]],
    pond: Any,
    pond_pad: float,
) -> bool:
    """Is this ground already spoken for, as far as a stand of take-yabu is concerned?

    LIFTED OUT OF `bamboo_seats` (feature 146, GM 2026-08-28 on inner functions and testability). Two of
    its arms - the canvas MARGIN and the TITLE POCKET - are geometry no rolled hamlet ever offers a culm
    for, because the sampler this serves never proposes a candidate that near the frame or under the title
    card. They are real refusals all the same, and want asking directly rather than through a planned site.
    """
    if x < 30 or y < 30 or x > extent[0] - 30 or y > extent[1] - 30:
        return True
    if pocket[0] <= x <= pocket[2] and pocket[1] <= y <= pocket[3]:
        return True
    for rx, ry, rw, rh, pad in rects:
        if abs(x - rx) <= rw / 2 + pad and abs(y - ry) <= rh / 2 + pad:
            return True
    for pts, half in lanes:
        if any(seg_dist(x, y, pts[k], pts[k + 1]) < half for k in range(len(pts) - 1)):
            return True
    for poly, pad in polys:
        if len(poly) >= 3 and (point_in_poly(x, y, poly) or min(seg_dist(x, y, poly[k], poly[(k + 1) % len(poly)]) for k in range(len(poly))) < pad):
            return True
    if not pond:
        return False
    return bool(((x - pond[0]) / (pond[2] + pond_pad)) ** 2 + ((y - pond[1]) / (pond[3] + pond_pad)) ** 2 <= 1.0)


def bamboo_blocked_indexed(x: float, y: float, extent: Pt, pocket: tuple[float, float, float, float], index: BambooObstacles, pond: Any, pond_pad: float) -> bool:
    """`bamboo_blocked` with its rect, lane and polygon arms asked of a `BambooObstacles` index (feature 223);
    the margin, the pocket and the pond are the same one comparison each."""
    if x < 30 or y < 30 or x > extent[0] - 30 or y > extent[1] - 30:
        return True
    if pocket[0] <= x <= pocket[2] and pocket[1] <= y <= pocket[3]:
        return True
    if index.blocked(x, y):
        return True
    if not pond:
        return False
    return bool(((x - pond[0]) / (pond[2] + pond_pad)) ** 2 + ((y - pond[1]) / (pond[3] + pond_pad)) ** 2 <= 1.0)


BAMBOO_SEAT_STEP_FT = 16.0
"""The lattice a bamboo stand's seat is searched on, in feet (feature 284, B6, a map drawing convention: the same keep-outs
and reach, sampled coarser). It was 8 ft; the walk outward (`nearest_fitting`) removed the tests the whole-square scan wasted
but on Mizuguchi, whose thicket seats far from its target, the bamboo still asked 226,223 calls (1.23x fewer, against the
spec's 2x floor), so the spec's fallback is taken: a stand seats at the nearest fitting point of the coarser lattice,
which can be a step or two from where the 8 ft lattice put it (18 and 24.5 ft on the pool's two thickets, specs/284 R6). The thicket is 84 by 58 ft (`BAMBOO_THICKET_FT`), so a stand on the coarser lattice is the same stand on the same ground."""


def nearest_fitting(target: Pt, reach: float, step: float, fits: Callable[[float, float], bool], box: tuple[float, float, float, float] | None = None) -> tuple[float, float, float] | None:
    """The fitting position nearest `target` on the `step` lattice of the square `reach` round it, as (distance, x, y) - or
    None - by walking OUTWARD and stopping at the first fit (feature 284, FR-008). The square was scanned whole, every
    position tested, the nearest fit kept (the first met in row order on a tie); the same positions, made by the same
    accumulation so every coordinate is the same float, are tested nearest first, ties in the old row order.

    `box` (x0, y0, x1, y1), when given, keeps the walk to the part of the square inside it, on a lattice laid CENTERED in
    that part (feature 293: a search over the whole sheet would otherwise list every point of a square round the target;
    and a band narrower than one step - the thicket's seats behind the back row and on the page are such a band at full
    size where the page's top is near the houses - still has its row, where a lattice stepped from the square's corner can
    miss it whole)."""
    spots: list[tuple[float, int, float, float]] = []
    x_lo, y_lo, x_hi, y_hi = target[0] - reach, target[1] - reach, target[0] + reach, target[1] + reach
    if box is not None:
        x_lo, y_lo, x_hi, y_hi = max(x_lo, box[0]), max(y_lo, box[1]), min(x_hi, box[2]), min(y_hi, box[3])
        x_lo += ((x_hi - x_lo) % step) / 2 if x_hi >= x_lo else 0.0
        y_lo += ((y_hi - y_lo) % step) / 2 if y_hi >= y_lo else 0.0
    y = y_lo
    while y <= y_hi:
        x = x_lo
        while x <= x_hi:
            spots.append((math.hypot(x - target[0], y - target[1]), len(spots), x, y))
            x += step
        y += step
    spots.sort()
    for d, _k, x, y in spots:
        if fits(x, y):
            return (d, x, y)
    return None


BAMBOO_SAMPLE_FT = 14.0
"""How far apart a bamboo stand's samples stand across its rect (feature 287, woods W24). A way is refused within its
half-width and 10 ft of a sample, so a tread anywhere in the rect lies within 14 / sqrt(2) = 9.9 ft of a sample and under
that reach: a map drawing convention - the density is the geometry's, not a fact about bamboo."""


def stand_samples(cx: float, cy: float, hw: float, hh: float, step: float) -> list[Pt]:
    """The points a stand's rect (center, half-extents) is asked at: its corners and edges, and a grid through it no more
    than `step` apart on either axis (feature 287, woods W24)."""
    nx, ny = max(2, math.ceil(2.0 * hw / step)), max(2, math.ceil(2.0 * hh / step))
    return [(cx - hw + 2.0 * hw * i / nx, cy - hh + 2.0 * hh * j / ny) for i in range(nx + 1) for j in range(ny + 1)]


THICKET_REACH_FT = 220.0
"""How far from its target the thicket's seat is looked for first, in feet (a GUESS, named by feature 293 - the literal
predates it): the thicket marks the edge of the houses it stands behind, so a seat near them wins over any seat farther
along the back row. Where none fits within it, the whole page behind the back row is searched (`bamboo_seats`)."""


def bamboo_seats(s: Settlement, plan: SitePlan) -> list[Poly]:
    """Where the hamlet's bamboo stands go, per the `bamboo` knob - SCANNED, like the coppice patches.

    A candidate is a rect on a `BAMBOO_SEAT_STEP_FT` lattice around its target, refused when any sample of a grid over
    the whole stand (`BAMBOO_SAMPLE_FT` apart) stands on a house, yard, garden, shed, byre, well, lane, paddy, marsh, pond, the belt,
    a coppice patch or the other stand (each with its own pad), and the surviving candidate nearest the
    target wins - behind the back row and on the page, within `THICKET_REACH_FT` of it at full size, then at 70%, and only
    then anywhere on the page behind the back row, full size then 70%; a stand that fits nowhere is dropped - a hamlet
    with no room for bamboo draws none rather than a sliver. Outlines are irregular rings inside the
    tested rect (`_parcel_outline`), because a thicket has a hard but not a ruled edge."""
    forms = ["thicket"] if plan.bamboo in ("thicket", "both") else []
    houses = s.M.get("houses", [])
    if not forms or not houses:
        return []
    px = s.px
    [float(o["x"]) for o in houses]
    hy = [float(o["y"]) for o in houses]
    north = min(hy)
    top = sorted(houses, key=lambda o: o["y"])[:3]
    home_target = (sum(float(o["x"]) for o in top) / len(top), north - px(40.0))
    thicket_target = home_target  # the settlement's edge, on the dry ground behind its back row (feature 280 M49)
    rects: list[tuple[float, float, float, float, float]] = []  # (x, y, w, h, pad)
    # ...AND EACH FARM'S OWN GROVE (feature 291): a take-yabu seated 40 ft north of the back row stood inside the north band
    # of Kashikawa's north-east far-row farm, and read as that farm's own bamboo in a grove that rolled none
    # (settlement-review, 2026-09-30)
    for key, pad in (
        ("houses", 10.0),
        ("threshing_yards", 8.0),
        ("gardens", 8.0),
        ("farm_sheds", 8.0),
        ("byres", 8.0),
        ("retirement_houses", 10.0),
        ("kosatsuba", 12.0),
        ("groves", 4.0),
    ):
        for o in s.M.get(key, []):
            if all(isinstance(o.get(f), (int, float)) for f in ("x", "y", "w", "h")):
                rects.append((float(o["x"]), float(o["y"]), float(o["w"]), float(o["h"]), px(pad)))
    # ...AND THE WELLS, BY THEIR RADIUS (feature 293, settlement-review of Kashikawa in the earlier 293 pass): the list above
    # named the wells, but a well record is x, y, r, so none of them ever entered it, and a re-packed Kashikawa drew its
    # thicket over a public well
    rects += [(float(o["x"]), float(o["y"]), 2.0 * float(o["r"]), 2.0 * float(o["r"]), px(14.0)) for o in s.M.get("wells", []) if all(isinstance(o.get(f), (int, float)) for f in ("x", "y", "r"))]
    # ...AND THE YARD PERSIMMONS, by their crowns: a take-yabu is a near single-species stand, and once feature 280 seated the
    # thicket behind the back row a dooryard persimmon stood inside it (settlement-review of Kashikawa, round 3)
    rects += [(float(o["x"]), float(o["y"]), 2.0 * float(o["r"]), 2.0 * float(o["r"]), px(2.0)) for o in s.M.get("persimmons", []) if all(isinstance(o.get(f), (int, float)) for f in ("x", "y", "r"))]
    # ...AND EVERY PLOT'S SUN GROUND (feature 315): a take-yabu throws a timber bamboo's shadow, so it keeps out of each yard's
    # and bed's sun at `BAMBOO_SHADE_FT`, a box like the rest
    rects += [(bx, by, 2.0 * bw, 2.0 * bh, 0.0) for bx, by, bw, bh in s._sun_keepouts((-1e9, -1e9, 1e9, 1e9), BAMBOO_SHADE_FT)]

    lanes = [([(float(a), float(b)) for a, b in ln["pts"]], float(ln.get("w", 3)) / 2 + px(10.0)) for ln in s.M.get("lanes", []) if len(ln.get("pts") or []) >= 2]
    # ...AND THE WATER (settlement-review of Mizuguchi, feature 261): nothing refused a watercourse, and when the houses moved
    # north of the brook the thicket's target on the field edge fell on it - 13 culms on the 7 ft ribbon, read as reeds in
    # the stream. A take-yabu stands on dry ground (research/contents.json#vegetation, bamboo); the water is kept by its half-width
    # and 3 ft, so a stand may still line the bank
    lanes += [
        ([(float(a), float(b)) for a, b in (st.get("poly") or st.get("pts") or [])], float(st.get("w") or 6) / 2 + px(3.0))
        for st in [*(s.M.get("streams") or []), *(s.M.get("drawn_channels") or [])]
        if len(st.get("poly") or st.get("pts") or []) >= 2
    ]
    polys: list[tuple[Poly, float]] = [(list(f), px(12.0)) for f in s.field_polys]
    # A TAKE-YABU MAY NOT STAND IN THE CROP - the DRY crop included (settlement-review, Mizuguchi, feature 145).
    # `field_polys` holds the paddy; the dry hem's plots are crop too, and nothing here refused them, so seed 23's
    # stand put 14 of its 66 culms up to 12.2 ft inside a soybean plot. A clonal bamboo rhizome in a bean field is
    # the one thing a farmer digs a trench to stop, so this is a placement error rather than a legibility one. The
    # gate could not catch it either: `bamboo_stands_clear_of_paddies` reads paddy outlines only (widened with this).
    polys += [([(float(a_), float(b_)) for a_, b_ in (o.get("poly") or [])], px(12.0)) for o in s.M.get("dry_plots", []) if len(o.get("poly") or []) >= 3]
    polys += [(ring, px(6.0)) for ring in marsh_ground(s.M)]
    polys += [(list(plan.belt), px(10.0))] if plan.belt else []
    polys += [(list(w), px(20.0)) for w in plan.woodland_polys]
    pond = s.M.get("pond")
    tp = title_pocket(s, plan)

    # THE THREE LISTS ARE INDEXED ONCE (feature 223, constitution X clause 15): they do not change during the scan,
    # and `bamboo_blocked` walked every lane segment and polygon edge for each of ~10,000 samples - 2.2 million
    # `seg_dist` on Sawada, 52% of the hinterland stage. Same verdicts; `bamboo_blocked` is the oracle its test uses.
    index = BambooObstacles(rects, lanes, polys)

    def _blocked(x: float, y: float) -> bool:
        return bamboo_blocked_indexed(x, y, (s.W, s.H), tp, index, pond, px(30.0))

    # ...ASKED OVER THE WHOLE STAND, NOT ITS PERIMETER (feature 287, woods W24): a 5 x 3 grid 29 ft apart let a lane cross
    # the stand between two rows. The samples stand `BAMBOO_SAMPLE_FT` apart, so every point of the rect lies within
    # `BAMBOO_SAMPLE_FT / sqrt(2)` of one, under the lane's refusal reach (its half-width and 10 ft): a tread that enters the
    # stand is always seen
    _sample = px(BAMBOO_SAMPLE_FT)
    # ...AND CLEAR OF EVERY HOUSEHOLD'S RESERVED COPSE SEATS by the copse's bamboo keep-out (`stand_spares_seats`; feature
    # 280 keeps the copse two crowns off the bamboo, feature 287 plants every reserved seat): the stand gives way, not the seat
    _seats = [(float(p[0]), float(p[1])) for h in s.M.get("houses") or [] for p in (h.get("wood_share") or {}).get("seats") or ()]

    def _fits(cx: float, cy: float, hw: float, hh: float) -> bool:
        if not stand_spares_seats(cx, cy, 2.0 * hw, 2.0 * hh, _seats, s.bscale):
            return False
        # a yard persimmon's crown fitted between the samples of a 72 x 55 ft thicket at five by three (settlement-review of
        # Kashikawa, feature 280, which went to nine by five); the `BAMBOO_SAMPLE_FT` grid is finer than a crown and its pad
        # (`PERSIMMON_CROWN_FT`, 23 ft across) on either axis, so a crown anywhere over the stand is always seen
        return not any(_blocked(x, y) for x, y in stand_samples(cx, cy, hw, hh, _sample))

    # THE PAGE AS IT STANDS (`frame_bounds`, the one question every placer asks of where the page will be): the belt is planted
    # after the bamboo and only grows the view, so ground inside this box is on the sheet
    vx0, vy0, vx1, vy1 = frame_bounds(s, plan)

    def on_sheet(cx: float, cy: float, hw: float, hh: float) -> bool:
        return vx0 <= cx - hw and cx + hw <= vx1 and vy0 <= cy - hh and cy + hh <= vy1

    out: list[Poly] = []
    for _form in forms:
        wft, hft = BAMBOO_THICKET_FT
        target = thicket_target
        step = px(BAMBOO_SEAT_STEP_FT)
        best: tuple[float, float, float] | None = None
        # ...AND OVER THE WHOLE PAGE BEHIND THE ROW, WHEN NOTHING FITS NEAR (feature 293; settlement-reviews of Kashikawa in the
        # earlier 293 pass): with the seat held behind the back row and on the page, the near search can find no seat within
        # its reach while open scrub lies farther along the row - "no room" was the search, not the ground. The second search
        # walks the page behind the back row, on a lattice centered in the band a seat's center may use there.
        far = max(math.dist(target, c) for c in ((vx0, vy0), (vx1, vy0), (vx0, vy1), (vx1, vy1)))
        for scale, reach, bounded in ((1.0, px(THICKET_REACH_FT), False), (0.7, px(THICKET_REACH_FT), False), (1.0, far, True), (0.7, far, True)):
            hw, hh = px(wft) * scale / 2, px(hft) * scale / 2
            # ...AND ONLY BEHIND THE BACK ROW, ON THE PAGE (feature 293): the search walked out from the target in every
            # direction, so where the ground behind the houses was taken the stand walked into the cluster and round a well;
            # and behind the row the nearest fitting seat could stand wholly off the page (main's Kashikawa drew 5 of its 12
            # outline points off the sheet, and 12 of 12 once its storehouses went to its largest houses). A seat's south edge
            # stands no further south than the northernmost house, and the stand inside the page; where none fits, none is drawn.
            best = nearest_fitting(
                target,
                reach,
                step,
                lambda x, y, hw=hw, hh=hh: y + hh <= north and on_sheet(x, y, hw, hh) and _fits(x, y, hw, hh),
                box=(vx0 + hw, vy0 + hh, vx1 - hw, north - hh) if bounded else None,
            )
            if best is not None:
                ring = _parcel_outline(s, best[1], best[2], hw, hh, 1.0, 0.0)
                out.append(ring)
                plan.bamboo_roles.append("thicket")
                break
    return out
