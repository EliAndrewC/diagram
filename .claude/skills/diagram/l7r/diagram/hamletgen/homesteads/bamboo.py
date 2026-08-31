"""Split from hamletgen/homesteads.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist, segments_cross

from ..consts import Poly
from ..plan import SitePlan

# HOUSEHOLD BAMBOO (feature 133 T48, GM 2026-08-27; research/vegetation.md "Bamboo: how common, where it
# stood, and how to show it", the T48 pass). READ: on the Tonami plain every farmstead stood in its own
# grove (kainyo) and bamboo was one of its named species beside a dominant cedar, valued as "important
# daily-life material"; the bamboo stood WITH the storehouses on the plot's south side there, and at a
# plot's wet edge for its roots elsewhere; the grove as a whole faces the local wind (N+W, W, or S+W by
# region - summary-only). So the SIDE is rolled per farmstead, weighted toward the back and the shed's
# side, never fixed; and the PRESENCE rate is a GUESS - no source gives a share; "one of several secondary
# species" says common but not universal - set like the shed's, and labeled. Sizes are a working strip.
HOUSEHOLD_BAMBOO_PREVALENCE = 0.6
HOUSEHOLD_BAMBOO_FT = (22.0, 16.0)
_HOUSEHOLD_BAMBOO_SIDES = (("back", 0.45), ("shed", 0.30), ("wind", 0.15), ("side", 0.10))


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
    for h in houses:
        hx, hy, hw, hh = float(h["x"]), float(h["y"]), float(h["w"]), float(h["h"])
        if s._hjit(hx, hy, 95.0) >= HOUSEHOLD_BAMBOO_PREVALENCE:
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
        wlx, wly = wx * ca + wy * sa, -wx * sa + wy * ca  # the wind in the house's frame
        local["wind"] = (wlx * (hw / 2 + gap + sh / 2), wly * (hh / 2 + gap + sh / 2), sw if abs(wly) >= abs(wlx) else sh, sh if abs(wly) >= abs(wlx) else sw)
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
                if _strip_blocked(s, cx, cy, cw, ch, hx, hy, fields, marsh, pond, lanes):
                    continue
                ring = [(cx - cw / 2, cy - ch / 2), (cx + cw / 2, cy - ch / 2), (cx + cw / 2, cy + ch / 2), (cx - cw / 2, cy + ch / 2)]
                out.append(ring)
                plan.bamboo_roles.append("homestead")
                s.placed.append((cx, cy, cw, ch))
                s.block_polys.append(ring)
                seated = True
                break
    return out


def _strip_blocked(
    s: Settlement, cx: float, cy: float, cw: float, ch: float, hx: float, hy: float, fields: Sequence[Poly], marsh: Sequence[Poly], pond: Any, lanes: Sequence[tuple[Poly, float]]
) -> bool:
    """Would a household bamboo strip centered here stand on something? Its own farmhouse is not something."""
    if cx - cw / 2 < 30 or cy - ch / 2 < 30 or cx + cw / 2 > s.W - 30 or cy + ch / 2 > s.H - 30:
        return True
    corners = [(cx - cw / 2, cy - ch / 2), (cx + cw / 2, cy - ch / 2), (cx + cw / 2, cy + ch / 2), (cx - cw / 2, cy + ch / 2), (cx, cy)]
    for px_, py_, pw, ph, *_ in s.placed:
        if px_ == hx and py_ == hy:
            continue
        if abs(cx - px_) < (cw + pw) / 2 + 2 and abs(cy - py_) < (ch + ph) / 2 + 2:
            return True
    for key in ("wells", "kosatsuba", "byres", "farm_sheds"):  # everything seated between the sheds and this pass (T49)
        for o in s.M.get(key, []):
            ow, oh = float(o.get("w", 2 * float(o.get("r", 8)))), float(o.get("h", 2 * float(o.get("r", 8))))
            if abs(cx - float(o["x"])) < (cw + ow) / 2 + 6 and abs(cy - float(o["y"])) < (ch + oh) / 2 + 6:
                return True
    for poly in list(fields) + list(marsh):
        if len(poly) >= 3 and any(point_in_poly(q[0], q[1], poly) or min(seg_dist(q[0], q[1], poly[k], poly[(k + 1) % len(poly)]) for k in range(len(poly))) < 6.0 for q in corners):
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
    for o in s.M.get("dry_plots", []):
        poly = [(float(a), float(b)) for a, b in o.get("poly") or []]
        if len(poly) >= 3 and any(point_in_poly(q[0], q[1], poly) or min(seg_dist(q[0], q[1], poly[k], poly[(k + 1) % len(poly)]) for k in range(len(poly))) < 3.0 for q in corners):
            return True
    if any(s._on_watercourse(q[0], q[1], pad=4.0) for q in corners):
        return True
    tc = s.M.get("tree_crowns") or []
    for k in range(0, len(tc) - 2, 3):
        tx, ty, tr = float(tc[k]), float(tc[k + 1]), float(tc[k + 2])
        hd = math.hypot(cw, ch) / 2  # the check squares a RAKED footprint on its half-diagonal; mirror it
        if max(abs(cx - tx) - hd, 0.0) ** 2 + max(abs(cy - ty) - hd, 0.0) ** 2 < (tr + 0.6) ** 2:
            return True
    return bool(pond) and ((cx - pond[0]) / (pond[2] + 20.0)) ** 2 + ((cy - pond[1]) / (pond[3] + 20.0)) ** 2 <= 1.0
