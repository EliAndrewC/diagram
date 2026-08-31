"""Split from hamletgen/hinterland.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from collections.abc import Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist

from ..consts import Poly, Pt
from ..plan import SitePlan
from .frame import title_pocket
from .parcels import _parcel_outline

# THE BAMBOO STANDS (feature 133 T47/T48, GM 2026-08-27; research/vegetation.md "Bamboo: how common, where
# it stood, and how to show it"). Two attested forms, the `bamboo` knob's values: the THICKET (take-yabu),
# ONE communal stand at the village edge held and cut under the village's rules like its coppice, seated
# here on the cluster's shady side; and HOUSEHOLD bamboo, a small strip on each farmstead that keeps one
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


def bamboo_seats(s: Settlement, plan: SitePlan) -> list[Poly]:
    """Where the hamlet's bamboo stands go, per the `bamboo` knob - SCANNED, like the coppice patches.

    A candidate is a rect on an 8 ft lattice around its target, refused when any of its perimeter
    samples stands on a house, yard, garden, shed, byre, well, board, lane, paddy, marsh, pond, the belt,
    a coppice patch or the other stand (each with its own pad), and the surviving candidate nearest the
    target wins; a stand that fits nowhere at full size is tried once at 70%, then dropped - a hamlet
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
    env = [(float(a), float(b)) for a, b in plan.envelope]
    if env:
        ecx, ecy = sum(q[0] for q in env) / len(env), sum(q[1] for q in env) / len(env)
        near = min(env, key=lambda q: math.hypot(q[0] - home_target[0], q[1] - north))
        d = math.hypot(near[0] - ecx, near[1] - ecy) or 1.0
        thicket_target = (near[0] + (near[0] - ecx) / d * px(50.0), near[1] + (near[1] - ecy) / d * px(50.0))
    else:  # pragma: no cover - a hamlet always has its field
        thicket_target = home_target
    rects: list[tuple[float, float, float, float, float]] = []  # (x, y, w, h, pad)
    for key, pad in (("houses", 10.0), ("threshing_yards", 8.0), ("gardens", 8.0), ("farm_sheds", 8.0), ("byres", 8.0), ("wells", 14.0), ("kosatsuba", 12.0)):
        for o in s.M.get(key, []):
            if all(isinstance(o.get(f), (int, float)) for f in ("x", "y", "w", "h")):
                rects.append((float(o["x"]), float(o["y"]), float(o["w"]), float(o["h"]), px(pad)))
    lanes = [([(float(a), float(b)) for a, b in ln["pts"]], float(ln.get("w", 3)) / 2 + px(10.0)) for ln in s.M.get("lanes", []) if len(ln.get("pts") or []) >= 2]
    polys: list[tuple[Poly, float]] = [(list(f), px(12.0)) for f in s.field_polys]
    # A TAKE-YABU MAY NOT STAND IN THE CROP - the DRY crop included (settlement-review, Mizuguchi, feature 145).
    # `field_polys` holds the paddy; the dry hem's plots are crop too, and nothing here refused them, so seed 23's
    # stand put 14 of its 66 culms up to 12.2 ft inside a soybean plot. A clonal bamboo rhizome in a bean field is
    # the one thing a farmer digs a trench to stop, so this is a placement error rather than a legibility one. The
    # gate could not catch it either: `bamboo_stands_clear_of_paddies` reads paddy outlines only (widened with this).
    polys += [([(float(a_), float(b_)) for a_, b_ in (o.get("poly") or [])], px(12.0)) for o in s.M.get("dry_plots", []) if len(o.get("poly") or []) >= 3]
    polys += [([(float(a), float(b)) for a, b in m["poly"]], px(6.0)) for m in s.M.get("marshes", []) if m.get("poly")]
    polys += [(list(plan.belt), px(10.0))] if plan.belt else []
    polys += [(list(w), px(20.0)) for w in plan.woodland_polys]
    pond = s.M.get("pond")
    tp = title_pocket(s, plan)

    def _blocked(x: float, y: float) -> bool:
        return bamboo_blocked(x, y, (s.W, s.H), tp, rects, lanes, polys, pond, px(30.0))

    def _fits(cx: float, cy: float, hw: float, hh: float) -> bool:
        samples = [(cx + dx * hw, cy + dy * hh) for dx in (-1.0, -0.5, 0.0, 0.5, 1.0) for dy in (-1.0, 0.0, 1.0)]
        return not any(_blocked(x, y) for x, y in samples)

    out: list[Poly] = []
    for _form in forms:
        wft, hft = BAMBOO_THICKET_FT
        target = thicket_target
        step = px(8.0)
        best: tuple[float, float, float] | None = None
        for scale in (1.0, 0.7):
            hw, hh = px(wft) * scale / 2, px(hft) * scale / 2
            reach = px(220.0)
            y = target[1] - reach
            while y <= target[1] + reach:
                x = target[0] - reach
                while x <= target[0] + reach:
                    if _fits(x, y, hw, hh):
                        d = math.hypot(x - target[0], y - target[1])
                        if best is None or d < best[0]:
                            best = (d, x, y)
                    x += step
                y += step
            if best is not None:
                ring = _parcel_outline(s, best[1], best[2], hw, hh, 1.0, 0.0)
                out.append(ring)
                plan.bamboo_roles.append("thicket")
                break
    return out
