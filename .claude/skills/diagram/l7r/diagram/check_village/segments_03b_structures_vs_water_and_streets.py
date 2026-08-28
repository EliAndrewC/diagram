"""Gate segments (structures vs water and streets; keys 0197-0231) - bodies verbatim, registry order preserved."""

from typing import Any

from l7r.diagram.waterfields import hem_on_paddy

from .common_01_geometry import (
    Poly,
    Pt,
    point_in_poly,
    seg_dist,
    segments_cross,
)
from .common_03_capacity import _UNBOUND, _kept

# A walled COMPOUND (mausoleum / manor) whose wall sits ALONG a neighborhood (ward) fence must
# YIELD that wall to the fence: the fence is re-stamped on top and IS that side of the compound,
# so there is no doubled, clashing parallel wall (s.mausoleum / s.manor do this automatically and
# record the yielded sides in "ward_walls"). Verify every geometric abutment is recorded.


def _seg_0197__walled_structure_yields_to_ward_wall(
    *,
    M: Any = _UNBOUND,
    _wall_along_fence: Any = _UNBOUND,
    a: Any = _UNBOUND,
    ax: Any = _UNBOUND,
    ay: Any = _UNBOUND,
    b: Any = _UNBOUND,
    bnd: Any = _UNBOUND,
    bx: Any = _UNBOUND,
    by: Any = _UNBOUND,
    check: Any = _UNBOUND,
    cx: Any = _UNBOUND,
    cy: Any = _UNBOUND,
    h: Any = _UNBOUND,
    k: Any = _UNBOUND,
    name: Any = _UNBOUND,
    px: Any = _UNBOUND,
    py: Any = _UNBOUND,
    qx: Any = _UNBOUND,
    qy: Any = _UNBOUND,
    recorded: Any = _UNBOUND,
    s: Any = _UNBOUND,
    sides: Any = _UNBOUND,
    tol: Any = _UNBOUND,
    unyielded: Any = _UNBOUND,
    w: Any = _UNBOUND,
    wall_ring: Any = _UNBOUND,
    wd: Any = _UNBOUND,
    x0: Any = _UNBOUND,
    x1: Any = _UNBOUND,
    y0: Any = _UNBOUND,
    y1: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 197 (walled_structure_yields_to_ward_wall) - body verbatim from the legacy gate() (feature 022)."""
    if M.get("wards"):

        def _wall_along_fence(a: Pt, b: Pt, tol: float = 16) -> bool:
            ax, ay = a
            bx, by = b
            horiz = abs(ax - bx) >= abs(ay - by)
            for wd in M["wards"]:
                bnd = wd.get("boundary", [])
                for k in range(len(bnd) - 1):
                    px, py = bnd[k]
                    qx, qy = bnd[k + 1]
                    if (abs(px - qx) >= abs(py - qy)) != horiz:  # fence segment must run the same way
                        continue
                    if horiz and abs(py - ay) <= tol and min(max(ax, bx), max(px, qx)) - max(min(ax, bx), min(px, qx)) >= 10:
                        return True
                    if not horiz and abs(px - ax) <= tol and min(max(ay, by), max(py, qy)) - max(min(ay, by), min(py, qy)) >= 10:
                        return True
            return False

        wall_ring = M.get("wall")
        unyielded = []
        for s in M.get("mausoleums", []) + M.get("manors", []):
            if s.get("rot", 0):
                continue  # tilted compound: not axis-aligned to a fence
            if wall_ring and not point_in_poly(s["x"], s["y"], wall_ring):
                continue  # only compounds INSIDE the city
            cx, cy, w, h = s["x"], s["y"], s["w"], s["h"]
            x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
            sides = {"north": ((x0, y0), (x1, y0)), "south": ((x0, y1), (x1, y1)), "west": ((x0, y0), (x0, y1)), "east": ((x1, y0), (x1, y1))}
            recorded = set(s.get("ward_walls", []))
            for name, (a, b) in sides.items():
                if name != s.get("gate_dir") and _wall_along_fence(a, b) and name not in recorded:
                    unyielded.append((round(cx), round(cy), name))
        check(
            "walled_structure_yields_to_ward_wall",
            not unyielded,
            f"walled compound(s) draw their own wall OVER a neighborhood (ward) fence instead of yielding to it: {unyielded[:3]} - "
            f"where a mausoleum/manor wall abuts a ward fence, the FENCE is that side's wall (render the compound's wall UNDER it); "
            f"s.mausoleum / s.manor do this automatically and record the yielded sides in 'ward_walls'",
        )
    return _kept(locals(), ('_wall_along_fence', 'a', 'b', 'cx', 'cy', 'h', 'name', 'recorded', 's', 'sides', 'unyielded', 'w', 'wall_ring', 'x0', 'x1', 'y0', 'y1'))


# no structure overlaps the (wide) road


def _seg_0198__road(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 198 (road) - body verbatim from the legacy gate() (feature 022)."""
    road: Any = M.get("road")
    return _kept(locals(), ('road',))


# no structure overlaps a stream


def _seg_0200__streams(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 200 (streams) - body verbatim from the legacy gate() (feature 022)."""
    streams = M.get("streams", [])
    return _kept(locals(), ('streams',))


def _seg_0201__no_structure_on_stream(
    *,
    bad_s: Any = _UNBOUND,
    check: Any = _UNBOUND,
    corners: Any = _UNBOUND,
    cx: Any = _UNBOUND,
    cy: Any = _UNBOUND,
    e: Any = _UNBOUND,
    k: Any = _UNBOUND,
    on_stream: Any = _UNBOUND,
    rx: Any = _UNBOUND,
    ry: Any = _UNBOUND,
    sc: Any = _UNBOUND,
    sp: Any = _UNBOUND,
    srw: Any = _UNBOUND,
    st: Any = _UNBOUND,
    streams: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 201 (no_structure_on_stream) - body verbatim from the legacy gate() (feature 022)."""
    if streams:
        srw = 6  # stream half-width + a little

        def on_stream(sc: Poly, sp: Poly) -> bool:
            if any(seg_dist(cx, cy, sp[k], sp[k + 1]) < srw for (cx, cy) in sc for k in range(len(sp) - 1)):
                return True
            if any(point_in_poly(rx, ry, sc) for rx, ry in sp):
                return True
            return any(segments_cross(sp[k], sp[k + 1], sc[e], sc[(e + 1) % 4]) for k in range(len(sp) - 1) for e in range(4))

        bad_s = [1 for sc in corners for st in streams if on_stream(sc, st["poly"])]
        check("no_structure_on_stream", not bad_s, f"{len(bad_s)} structure(s) overlap a stream")
    return _kept(locals(), ('bad_s', 'on_stream', 'sc', 'srw', 'st'))


# no structure overlaps an irrigation channel - the SAME full-footprint test as a stream.
# (houses_off_corridors below also touches channels, but only by house CENTER distance, so a
# channel clipping a farmhouse's corner while its center stayed clear used to slip through.)


# no structure overlaps the navigable CARGO CANAL - the same full-footprint test as a channel,
# but the canal is a WIDER watercourse (a poling barge, not a field ditch), so its half-width is
# honored. A merchant house / warehouse fronts the quay but must not stand IN the water (GM,
# 2026-07: a merchant_large sat on Nagahara's canal - there was no canal-vs-struct check at all,
# this being the first city with a canal). Jetties/water-gates/bridges legitimately cross it (EXEMPT).


# no structure overlaps the town wall (the thick rampart stroke)


# no structure overlaps the MOAT (the water ring outside the wall) - extramural structures (the
# common burial ground, the cremation ground, the ossuary, samurai estates) must keep clear of it


# no structure overlaps the POND (the irrigation reservoir / in-wall water source). The pond is
# the one water body that was never in this section: streams/channels/moat all have their clause
# above, but a struct standing IN the pond slipped through (Tango's west fire tower landed on the
# pond rim). Village ponds are auto-placed clear of everything, so this only ever bites hand-placed
# structs - which is exactly when a check is needed. The pond is a true ellipse [cx, cy, rx, ry];
# a footprint hits it if any sampled boundary point (corners + edge quarter-points, enough for
# struct-sized rects vs a pond-sized ellipse) dips inside the rim, or the rect swallows the center.


# no structure stands ON a rice paddy - the long-missing member of this family (GM, Hoshizora
# 2026-07: the legacy house-first placement tested only the CENTER +14px against the field, so a
# town-scale 44px farmhouse could sink a corner ~12px into the crop while every village's 23px
# houses stayed clear by luck of the grain). A corner is IN the paddy only when it penetrates
# deeper than 3px past the outline - bund-hugging abutment (and the organic outline's stroke)
# stays legal.


def _seg_0212__f(*, M: Any = _UNBOUND, f: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 212 (f, paddy_ol_st) - body verbatim from the legacy gate() (feature 022)."""
    paddy_ol_st = [f["outline"] for f in M.get("fields", []) if f.get("kind") == "paddy"]
    return _kept(locals(), ('f', 'paddy_ol_st'))


def _seg_0213__no_structure_on_paddy(
    *,
    M: Any = _UNBOUND,
    _pol_bb: Any = _UNBOUND,
    bad_pd: Any = _UNBOUND,
    bx0: Any = _UNBOUND,
    bx1: Any = _UNBOUND,
    by0: Any = _UNBOUND,
    by1: Any = _UNBOUND,
    check: Any = _UNBOUND,
    corners: Any = _UNBOUND,
    dp: Any = _UNBOUND,
    dp_on_rice: Any = _UNBOUND,
    i: Any = _UNBOUND,
    ol: Any = _UNBOUND,
    p: Any = _UNBOUND,
    paddy_depth: Any = _UNBOUND,
    paddy_ol_st: Any = _UNBOUND,
    px: Any = _UNBOUND,
    py: Any = _UNBOUND,
    q: Any = _UNBOUND,
    qx0: Any = _UNBOUND,
    qx1: Any = _UNBOUND,
    qy0: Any = _UNBOUND,
    qy1: Any = _UNBOUND,
    sc: Any = _UNBOUND,
    worst: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 213 (dry_plots_clear_of_paddies, no_structure_on_paddy) - body verbatim from the legacy gate() (feature 022)."""
    if paddy_ol_st:

        def paddy_depth(sc: Poly) -> float:
            worst = 0.0
            for px, py in sc:
                for ol in paddy_ol_st:
                    if point_in_poly(px, py, ol):
                        worst = max(worst, min(seg_dist(px, py, ol[i], ol[i + 1]) for i in range(len(ol) - 1)))
            return worst

        bad_pd = [1 for sc in corners if paddy_depth(sc) > 3]
        check(
            "no_structure_on_paddy",
            not bad_pd,
            f"{len(bad_pd)} structure(s) stand on a rice paddy - houses, yards, and every other footprint sit on dry ground BESIDE the crop, never in the flooded field",
        )

        # ... and no DRY plot lies on one either. The hem quilt exists precisely because its ground
        # sits UPSLOPE of what the canal commands, so dry-crop-on-rice is a contradiction in the
        # water logic, not a style choice. On a multi-fan map each fan's hem is generated blind to
        # the other fans - the generators drop any hem plot that hits a previously recorded fan via
        # the SAME hem_on_paddy predicate this check runs (waterfields.py; the same-source doctrine,
        # diagram CLAUDE.md), and this gate is what proves the filter worked. First caught: Tango's
        # fe2 hem punching into fe1's envelope (2026-07-23) - only hand-tuned dry_keepout circles
        # held fans' hems apart before, and hand tuning missed a spot.
        dp_on_rice = []
        _pol_bb = [(ol, (min(p[0] for p in ol), min(p[1] for p in ol), max(p[0] for p in ol), max(p[1] for p in ol))) for ol in paddy_ol_st]
        for dp in M.get("dry_plots", []):
            q = dp["poly"]
            qx0, qy0, qx1, qy1 = min(p[0] for p in q), min(p[1] for p in q), max(p[0] for p in q), max(p[1] for p in q)
            if any(qx1 >= bx0 and qx0 <= bx1 and qy1 >= by0 and qy0 <= by1 and hem_on_paddy(q, ol) for ol, (bx0, by0, bx1, by1) in _pol_bb):
                dp_on_rice.append((round((qx0 + qx1) / 2), round((qy0 + qy1) / 2)))
        check(
            "dry_plots_clear_of_paddies",
            not dp_on_rice,
            f"{len(dp_on_rice)} dry plot(s) overlap a flooded paddy fan (plot centers): {dp_on_rice[:4]} - dry "
            f"crops grow on the ground the water CANNOT command, so a hem plot never laps onto the rice; on a "
            f"multi-fan map the hem filter must drop plots that land on a neighboring fan's envelope",
        )
    return _kept(locals(), ('_pol_bb', 'bad_pd', 'bx0', 'bx1', 'by0', 'by1', 'dp', 'dp_on_rice', 'ol', 'p', 'paddy_depth', 'q', 'qx0', 'qx1', 'qy0', 'qy1', 'sc'))


# WATER-WIDTH LADDER - a STROKE CONVENTION, not a size license (GM ruling 2026-07-21). Real
# wet-rice water systems are a tiered hierarchy whose widths step up ~2-4x per tier (channel
# width scales with the sqrt of command-area flow): a field ditch ~0.3 m, a village creek ~2 m
# (~6x the ditch), a town river / castle moat ~20 m (~70x the ditch). Watercourses are LINEWORK:
# the smallest lines draw at a minimum-visible floor (a true 1 ft ditch is 0.33px at city scale -
# invisible), true-width-or-floored and never fattened past the floor, while honesty anchors on
# the LARGE end (the city moat draws its real ~66+ ft). The ORDERING and coarse steps must
# survive the compression: an irrigation ditch is ALWAYS the thinnest line, a natural watercourse
# clearly heavier, the city moat heaviest of all. The clauses below pin that. (Why these numbers:
# settlements.md "Water-width ladder" grounding.)


def _seg_0214__c_1(*, M: Any = _UNBOUND, c: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 214 (c, chan_ws) - body verbatim from the legacy gate() (feature 022)."""
    chan_ws = [c["w"] for c in M.get("channels", []) if "w" in c]
    return _kept(locals(), ('c', 'chan_ws'))


def _seg_0215__st(*, M: Any = _UNBOUND, st: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 215 (st, strm_ws) - body verbatim from the legacy gate() (feature 022)."""
    strm_ws = [st["w"] for st in M.get("streams", []) if "w" in st]
    return _kept(locals(), ('st', 'strm_ws'))


# (1) Irrigation channels are HAIRLINES: at/just above the legibility floor, never fattened toward
# stream weight. A ditch drawn as a stout line (the old 4.2 px) reads as a watercourse, not a ditch.


def _seg_0217__irrigation_channels_hairline(*, M: Any = _UNBOUND, c: Any = _UNBOUND, chan_ws: Any = _UNBOUND, check: Any = _UNBOUND, fat: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 217 (irrigation_channels_hairline) - body verbatim from the legacy gate() (feature 022)."""
    if chan_ws:
        # a DRAIN-OUTFALL CULVERT is not a field ditch: it carries a whole fan's gathered runoff and
        # must MATCH the drain's outfall width (6.0 x grain = 4.0 at the city grain) - a culvert
        # narrower than the ditch it drains read as the water SHRINKING past the gate (GM 2026-07-23,
        # the widening-drains pass). Its ceiling is 4.5; everything else keeps the hairline band.
        fat = [c["w"] for c in M.get("channels", []) if "w" in c and not 2.0 <= c["w"] <= (4.5 if (c.get("frm") or {}).get("kind") == "drain" else 3.5)]
        check(
            "irrigation_channels_hairline",
            not fat,
            f"channel width(s) {sorted(set(fat))} outside the hairline band [2.0, 3.5] px (drain-outfall "
            f"culverts may run to 4.5 - they carry the fan's whole runoff and match the drain's outfall) - a field "
            f"ditch is the thinnest line on the map (~0.3 m, ~1/300 of the paddy it feeds); keep it at "
            f"the legibility floor, distinct from any natural watercourse",
        )
    return _kept(locals(), ('c', 'fat'))


# (2) The tiers are ORDERED with honest gaps: a creek clearly beats a ditch (>=2.5x), a natural
# stream never out-widths the city moat (a moat-feeder may EQUAL it, by conservation of flow), and
# the moat dwarfs a ditch (>=4x). Each clause runs only when both features it compares are present.


def _seg_0218__watercourses_wider_than_ditches(*, chan_ws: Any = _UNBOUND, check: Any = _UNBOUND, ok: Any = _UNBOUND, strm_ws: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 218 (watercourses_wider_than_ditches) - body verbatim from the legacy gate() (feature 022)."""
    if chan_ws and strm_ws:
        ok = min(strm_ws) >= 2.5 * max(chan_ws)
        check(
            "watercourses_wider_than_ditches",
            ok,
            f"narrowest stream {min(strm_ws)} px is not >= 2.5x the widest channel {max(chan_ws)} px - a natural creek must read clearly heavier than an irrigation ditch, not as its sibling",
        )
    return _kept(locals(), ('ok',))


# no structure overlaps a street OR an alley (a paved lane or a gravel alley running over a
# house is wrong) - alleys are drawn last, so a careless alley can be laid across a building


def _seg_0221__tstreets(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 221 (tstreets) - body verbatim from the legacy gate() (feature 022)."""
    tstreets = M.get("town_streets", [])
    return _kept(locals(), ('tstreets',))


def _seg_0222__a_1(*, M: Any = _UNBOUND, a: Any = _UNBOUND, tstreets: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 222 (a, lanes) - body verbatim from the legacy gate() (feature 022)."""
    lanes = tstreets + [{"pts": a["pts"], "w": a.get("w", 10)} for a in M.get("alleys", [])]
    return _kept(locals(), ('a', 'lanes'))


# ---- street-faced town layout: businesses front the streets (and face them); housing
# sits back off the main commercial street. The "streets" are the town streets plus any
# road (an unwalled town's road is its high street).


def _seg_0231__ADJ() -> dict[str, Any]:
    """Gate segment 231 (ADJ) - body verbatim from the legacy gate() (feature 022)."""
    ADJ = 165
    return _kept(locals(), ('ADJ',))
