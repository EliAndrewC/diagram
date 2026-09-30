"""Split from hamletgen/homesteads.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist, segments_cross
from l7r.diagram.settlement._geom import PointGrid, boxed_grid, boxed_ring_hit, boxed_rings, boxed_segs
from l7r.diagram.settlement.homestead_parts.groves import HOUSEHOLD_BAMBOO_PREVALENCE as HOUSEHOLD_BAMBOO_PREVALENCE
from l7r.diagram.settlement.rolling.bearing import turned_box

from ..consts import Poly, Pt
from ..plan import SitePlan

# HOUSEHOLD BAMBOO (feature 133 T48, GM 2026-08-27; research/vegetation.html "Bamboo: how common, where it
# stood, and how to show it", the T48 pass). READ: on the Tonami plain every farmstead stood in its own
# grove (kainyo) and bamboo was one of its named species beside a dominant cedar, valued as "important
# daily-life material"; the bamboo stood WITH the storehouses on the plot's south side there, and at a
# plot's wet edge for its roots elsewhere; the grove as a whole faces the local wind (N+W, W, or S+W by
# region). THE WIND SIDE IS READ NOW, not summary-only (269 B29; research/vegetation/260 and 154): on the Tonami
# plain bamboo was often mixed into the grove from the west round to the north of the house, and the Sendai igune's
# bamboo filled its low part against the wind. So the SIDE is rolled per farmstead, weighted toward the back, the
# wind side and the shed's side, never fixed. The weights are a GUESS - no page gives a share per side; `wind` was
# raised from .15 to .30 when the wind side was read, taken from `back` and `shed`: `back` stays the likeliest, then
# `wind`, then `shed`, then the other flank.
# The PRESENCE rate is a GUESS - no source gives a share; "one of several secondary
# species" says common but not universal - set like the shed's, and labeled. Sizes are a working strip.
# HOUSEHOLD_BAMBOO_PREVALENCE lives with the grove drawer (settlement/homestead_parts/groves.py) since feature 291: a
# farm with its own grove draws its bamboo in that grove, so the drawing makes the same positional roll.
HOUSEHOLD_BAMBOO_FT = (22.0, 16.0)
_HOUSEHOLD_BAMBOO_SIDES = (("back", 0.35), ("shed", 0.25), ("wind", 0.30), ("side", 0.10))


_DIAGONAL = math.sin(math.radians(22.5))  # a wind component past this on both axes is a diagonal wind (NW, not N)


def wind_seat(wlx: float, wly: float, hw: float, hh: float, gap: float, sw: float, sh: float) -> tuple[float, float, float, float]:
    """The windward strip's (center x, center y, w, h) in the house's frame, for a wind (`wlx`, `wly`) pointing where it
    comes FROM (269 B29). A diagonal wind seats it on the windward CORNER, a near-cardinal one on the windward FACE -
    either way `gap` clear of the walls. It used to scale the half-sizes by the wind's components, which for a diagonal
    wind put the strip's center ~0.7 of the way out and its body over the house's own corner: the near seat was refused
    on every NW-wind hamlet in the pool, so the side rolled "wind" fell through to another side and raising its weight
    moved nothing."""
    if abs(wlx) > _DIAGONAL and abs(wly) > _DIAGONAL:
        return (math.copysign(hw / 2 + gap + sw / 2, wlx), math.copysign(hh / 2 + gap + sh / 2, wly), sw, sh)
    if abs(wly) >= abs(wlx):
        return (0.0, math.copysign(hh / 2 + gap + sh / 2, wly), sw, sh)
    return (math.copysign(hw / 2 + gap + sh / 2, wlx), 0.0, sh, sw)


def household_bamboo(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]]) -> list[Poly]:
    """Seat a small bamboo strip beside each farmstead that keeps one, per the `bamboo` knob.

    Seated in `stage_hinterland`, AFTER the web and the notice board (T49): seated with the sheds it
    was in the web's way, and the web threaded through it (two lanes on Inashiro) - and putting it in
    the web's fabric instead re-threaded the whole web and broke it. Seated after, the strip keeps 6 ft
    off every lane and clear of every placed footprint, the board and the wells, and the scrub keeps
    out of it (a soft keep-out, like every wood). Drawn by `stage_bamboo` with the stand glyph. Per house: presence by `HOUSEHOLD_BAMBOO_PREVALENCE`, side by the weighted roll
    above, both from the house's own position (positional randomness). A candidate that lands on a
    footprint, a lane, a paddy, the marsh or the pond is refused and the next side tried; a farmstead
    with no room keeps none. Returns the count seated."""
    out: list[Poly] = []
    if plan.bamboo not in ("homestead", "both") or not houses:
        return out
    px = s.px
    sw, sh = px(HOUSEHOLD_BAMBOO_FT[0]), px(HOUSEHOLD_BAMBOO_FT[1])
    wx, wy = plan.wind
    fields = [list(f) for f in s.field_polys]
    marsh = [[(float(a), float(b)) for a, b in m["poly"]] for m in s.M.get("marshes", []) if m.get("poly")]
    pond = s.M.get("pond")
    lanes = [([(float(a), float(b)) for a, b in ln["pts"]], float(ln.get("w", 3)) / 2 + px(6.0)) for ln in s.M.get("lanes", []) if len(ln.get("pts") or []) >= 2]
    footing = Footing(s, fields, marsh)  # the static ground, indexed once for every strip this pass tests (feature 218)
    for h in houses:
        hx, hy, hw, hh = float(h["x"]), float(h["y"]), float(h["w"]), float(h["h"])
        if s._hjit(hx, hy, 95.0) >= HOUSEHOLD_BAMBOO_PREVALENCE:
            continue
        # A FARM WITH ITS OWN GROVE KEEPS ITS BAMBOO IN THAT GROVE (feature 291; research/vegetation/260, "Did a farmstead's
        # grove carry bamboo? Yes - mixed in low under the tall trees, on its windward side"). Its deep windward bands draw
        # the windbreak mix, which carries the bamboo; a separate strip would stand exactly where the grove already does -
        # and did not: once the dispersed and linear forms rolled again, every seat (back, shed, side, wind) lay in the
        # grove and Kashikawa's 12 expected strips silently became 0. Counted, so the knob's household half is on record.
        if (h.get("geom") or {}).get("groves"):
            s.M["meta"]["household_bamboo_in_grove"] = int(s.M["meta"].get("household_bamboo_in_grove", 0)) + 1
            s.M["meta"].setdefault("household_bamboo_in_grove_farms", []).append([round(hx, 1), round(hy, 1)])  # which, for `row_rules.bamboo_mismatch`
            continue
        th = math.radians(float(h.get("rot", 0.0)))
        ca, sa = math.cos(th), math.sin(th)
        gap = px(6.0)
        # candidate centers in the house's local frame: back (-y, behind the house), the shed side
        # (local -x, with the kura), the windward side, the other flank
        shed_side = h.get("shed_side", "W")
        local = {
            "back": (0.0, -(hh / 2 + gap + sh / 2), sw, sh),
            "shed": ((-(hw / 2 + gap + sh / 2)) if shed_side != "N" else 0.0, 0.0 if shed_side != "N" else -(hh / 2 + gap + sh / 2), sh if shed_side != "N" else sw, sw if shed_side != "N" else sh),
            "side": (hw / 2 + gap + sh / 2, 0.0, sh, sw),
        }
        local["wind"] = wind_seat(wx * ca + wy * sa, -wx * sa + wy * ca, hw, hh, gap, sw, sh)  # the wind in the house's frame
        # the rolled side first, then the others in their listed order as fallbacks
        roll = s._hjit(hx, hy, 96.0)
        first = _HOUSEHOLD_BAMBOO_SIDES[-1][0]
        acc = 0.0
        for name, wgt in _HOUSEHOLD_BAMBOO_SIDES:
            acc += wgt
            if roll < acc:
                first = name
                break
        order = [first] + [nm for nm, _ in _HOUSEHOLD_BAMBOO_SIDES if nm != first]
        seated = False
        for name in order:
            if seated:
                break
            lx0, ly0, cw, ch = local[name]
            # two offsets per side (T49): against the house, then a strip's depth further out - the
            # lanes now stand where the near seat often is, and a strip 16 ft off the wall is still
            # the household's own
            for k in (0.0, 1.0):
                d = math.hypot(lx0, ly0) or 1.0
                lx, ly = lx0 + lx0 / d * k * sh, ly0 + ly0 / d * k * sh
                cx, cy = hx + lx * ca - ly * sa, hy + lx * sa + ly * ca
                if _strip_blocked(s, cx, cy, cw, ch, hx, hy, fields, marsh, pond, lanes, footing) or in_belt(plan.belt, cx, cy, cw, ch):
                    continue
                ring = [(cx - cw / 2, cy - ch / 2), (cx + cw / 2, cy - ch / 2), (cx + cw / 2, cy + ch / 2), (cx - cw / 2, cy + ch / 2)]
                out.append(ring)
                plan.bamboo_roles.append("homestead")
                s.placed.append((cx, cy, cw, ch))
                s.block_polys.append(ring)
                seated = True
                break
    return out


def in_belt(belt: Sequence[Pt] | None, cx: float, cy: float, cw: float, ch: float) -> bool:
    """Does a household strip centered (cx, cy), cw x ch, reach into the windbreak belt (its center or a corner inside)? The
    stands are drawn after the belt's crowns, so a strip in the belt painted its culms over the conifers - the reverse of the
    belt's own order, conifers over the bamboo between them (269 B30; settlement-review of Inashiro, feature 280)."""
    if not belt or len(belt) < 3:
        return False
    pts = [(cx, cy)] + [(cx + sx * cw / 2, cy + sy * ch / 2) for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]
    return any(point_in_poly(x, y, list(belt)) for x, y in pts)


class Footing:
    """The static ground a household strip or a tree trunk is tested against, indexed ONCE per pass
    (feature 218). `_strip_blocked` and `_trunk_blocked` used to walk every edge of every paddy and
    marsh polygon per corner of every candidate, and asked `_on_watercourse` with no `near`, which
    REBUILT the watercourse segment list (the laterals re-split into taper pieces) on every corner -
    210 rebuilds and 0.55 s of profiled time on the reference roll's 1,064 strip tests. A caller
    builds one of these after it gathers `fields` and `marsh` and passes it in; a call without one
    builds its own (slower, never wrong), which is what keeps the old positional signature and its
    unit tests valid. The rings carry the wider of the two pads the callers apply (6 ft for a paddy
    or the marsh, 3 ft for a dry plot); the exact tests are the ones each caller ran."""

    __slots__ = ("dry", "rings", "water")

    def __init__(self, s: Settlement, fields: Sequence[Poly], marsh: Sequence[Poly]) -> None:
        self.rings: PointGrid = boxed_grid(boxed_rings([p for p in list(fields) + list(marsh) if len(p) >= 3], 6.0))
        dry = [[(float(a), float(b)) for a, b in o.get("poly") or []] for o in s.M.get("dry_plots", [])]
        self.dry: PointGrid = boxed_grid(boxed_rings([p for p in dry if len(p) >= 3], 3.0))
        self.water: PointGrid = boxed_grid(boxed_segs(s._watercourse_segs(4.0)))

    def on_water(self, s: Settlement, x: float, y: float) -> bool:
        """`_on_watercourse(x, y, pad=4.0)`, answered from the grid - the crescent pond still by `s`."""
        return s._on_watercourse(x, y, pad=4.0, near=self.water.near)


def _strip_blocked(
    s: Settlement,
    cx: float,
    cy: float,
    cw: float,
    ch: float,
    hx: float,
    hy: float,
    fields: Sequence[Poly],
    marsh: Sequence[Poly],
    pond: Any,
    lanes: Sequence[tuple[Poly, float]],
    footing: Footing | None = None,
    skip: frozenset[tuple[float, float, float, float]] = frozenset(),
) -> bool:
    """Would a household bamboo strip centered here stand on something? Its own farmhouse is not something, and neither
    is a reserved box in `skip` (a caller whose parts are each registered passes the homestead BUNDLE boxes: feature 261,
    the fixtures pass, where a steading's own bundle and a neighbor's refused the open ground of its flanks)."""
    if cx - cw / 2 < 30 or cy - ch / 2 < 30 or cx + cw / 2 > s.W - 30 or cy + ch / 2 > s.H - 30:
        return True
    ft = footing or Footing(s, fields, marsh)  # a caller that tests many seats builds one and passes it (feature 218)
    corners = [(cx - cw / 2, cy - ch / 2), (cx + cw / 2, cy - ch / 2), (cx + cw / 2, cy + ch / 2), (cx - cw / 2, cy + ch / 2), (cx, cy)]
    for px_, py_, pw, ph, *_ in s.placed:
        if (px_ == hx and py_ == hy) or (px_, py_, pw, ph) in skip:
            continue
        if abs(cx - px_) < (cw + pw) / 2 + 2 and abs(cy - py_) < (ch + ph) / 2 + 2:
            return True
    # EVERY OTHER FARMHOUSE, as drawn: a caller that passes the bundle boxes in `skip` excuses a neighbor's bundle, and on a
    # map whose houses carry no separate placed box that excused the neighbor's house as well - Kuwabata's woodpile landed
    # on the next house's gable once the 269 landing's bearing fix moved the row (tests/gate/test_no_feature_overlaps.py).
    for o in s.M.get("houses", []):
        ox, oy = float(o["x"]), float(o["y"])
        if abs(ox - hx) < 0.5 and abs(oy - hy) < 0.5:
            continue
        _, _, ow, oh = turned_box((ox, oy, float(o["w"]), float(o["h"])), float(o.get("rot", 0.0)))
        if abs(cx - ox) < (cw + ow) / 2 + 2 and abs(cy - oy) < (ch + oh) / 2 + 2:
            return True
    for key in ("wells", "kosatsuba", "byres", "farm_sheds", "retirement_houses"):  # everything seated between the sheds and this pass (T49)
        for o in s.M.get(key, []):
            ow, oh = float(o.get("w", 2 * float(o.get("r", 8)))), float(o.get("h", 2 * float(o.get("r", 8))))
            if abs(cx - float(o["x"])) < (cw + ow) / 2 + 6 and abs(cy - float(o["y"])) < (ch + oh) / 2 + 6:
                return True
    if any(boxed_ring_hit(q[0], q[1], ft.rings.near(q[0], q[1]), 6.0) for q in corners):  # a paddy or the marsh, inside or within 6 ft of an edge
        return True
    # A LANE THROUGH THE STRIP, not only past its corners (feature 137, cohort seed 03): five sample
    # points on a 22 by 16 ft strip let a lane cross it diagonally between them, and
    # `lanes_clear_of_bamboo` walks the tread's quarter-points. So the tread is also tested as a
    # segment against the strip's edges - a crossing, or an end inside, is a stand on a lane.
    _edges = [(corners[k], corners[(k + 1) % 4]) for k in range(4)]
    for pts, half in lanes:
        for k in range(len(pts) - 1):
            a, b = pts[k], pts[k + 1]
            if any(seg_dist(q[0], q[1], a, b) < half for q in corners):
                return True
            if any(segments_cross(a, b, e0, e1) for e0, e1 in _edges) or any(abs(p[0] - cx) < cw / 2 and abs(p[1] - cy) < ch / 2 for p in (a, b)):
                return True
    # the dry hem's plots and the watercourses (unlock tripwire seed 47: a fixture on a dry plot and one
    # on the stream - neither is a paddy, a lane or the pond, so nothing above saw them), and any crown
    # already drawn (seed 37: a fixture seated under a grove crown drawn two stages earlier)
    if any(boxed_ring_hit(q[0], q[1], ft.dry.near(q[0], q[1]), 3.0) for q in corners):  # a dry plot, inside or within 3 ft
        return True
    if any(ft.on_water(s, q[0], q[1]) for q in corners):
        return True
    tc = s.M.get("tree_crowns") or []
    for k in range(0, len(tc) - 2, 3):
        tx, ty, tr = float(tc[k]), float(tc[k + 1]), float(tc[k + 2])
        hd = math.hypot(cw, ch) / 2  # the check squares a RAKED footprint on its half-diagonal; mirror it
        if max(abs(cx - tx) - hd, 0.0) ** 2 + max(abs(cy - ty) - hd, 0.0) ** 2 < (tr + 0.6) ** 2:
            return True
    return bool(pond) and ((cx - pond[0]) / (pond[2] + 20.0)) ** 2 + ((cy - pond[1]) / (pond[3] + 20.0)) ** 2 <= 1.0
