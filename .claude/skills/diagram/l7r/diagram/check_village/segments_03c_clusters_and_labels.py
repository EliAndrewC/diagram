"""Gate segments (clusters and labels; keys 0232-0267) - bodies verbatim, registry order preserved."""

import math
from collections.abc import Sequence
from typing import Any

from l7r.diagram.settlement import LABEL_AIR_CAP, aligned_tilt, box_gap, label_aabb, label_quad, sat_overlap

from .common_01_geometry import (
    Poly,
    _box_hits_poly,
    convex_hull,
    point_in_poly,
    poly_area,
    poly_dist,
)
from .common_02_overlap_policy import poly_gap
from .common_03_capacity import _UNBOUND, _kept

# WHY (farmers build close to the fields they work): settlements.md "Historical grounding". The invariant
# depends on the SETTLEMENT FORM, and it is TUNABLE via meta.nucleated:
#   - DISPERSED (the default): every farmhouse fronts its own fields, so EACH house must be within ADJ
#     of a field (`all_houses_field_adjacent`).
#   - NUCLEATED (meta.nucleated=True): the houses cluster together and the FIELDS radiate from the
#     cluster's edge - the interior houses are legitimately a cluster-span BACK from the nearest field,
#     so per-house adjacency is wrong. Instead the whole CLUSTER must ABUT its fields: the nearest house
#     is field-adjacent (the village sits ON its land, not floating in open country) AND no house is
#     farther than the cluster's own diameter past that edge (`cluster_abuts_fields`).


def _seg_0232__cluster_abuts_fields(
    *,
    ADJ: Any = _UNBOUND,
    M: Any = _UNBOUND,
    PHANTOM: Any = _UNBOUND,
    b: Any = _UNBOUND,
    built: Any = _UNBOUND,
    ccx: Any = _UNBOUND,
    ccy: Any = _UNBOUND,
    check: Any = _UNBOUND,
    cov: Any = _UNBOUND,
    d: Any = _UNBOUND,
    dists: Any = _UNBOUND,
    f: Any = _UNBOUND,
    far: Any = _UNBOUND,
    fields: Any = _UNBOUND,
    grp: Any = _UNBOUND,
    h: Any = _UNBOUND,
    harea: Any = _UNBOUND,
    hh: Any = _UNBOUND,
    houses: Any = _UNBOUND,
    hx: Any = _UNBOUND,
    hy: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    nearest: Any = _UNBOUND,
    pad: Any = _UNBOUND,
    r: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    span: Any = _UNBOUND,
    tails: Any = _UNBOUND,
    v: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 232 (all_houses_field_adjacent, cluster_abuts_fields, field_outline_matches_planting, village_cluster_compact) - body verbatim from the legacy gate() (feature 022)."""
    if fields and houses:
        hh = [h for h in houses if h.get("role") != "headman"]
        dists = [(h, min(poly_dist(h["x"], h["y"], f["outline"]) for f in fields)) for h in hh]
        if meta.get("nucleated"):
            hx = [h["x"] for h in houses]
            hy = [h["y"] for h in houses]
            ccx, ccy = sum(hx) / len(hx), sum(hy) / len(hy)
            span = max((math.hypot(h["x"] - ccx, h["y"] - ccy) for h in houses), default=0)  # cluster radius
            nearest = min((d for _, d in dists), default=999)
            far = [h for h, d in dists if d > ADJ + 2 * span]  # farther than a cluster-diameter past the field edge
            check(
                "cluster_abuts_fields",
                nearest <= ADJ and not far,
                f"nucleated cluster: nearest house {nearest:.0f}px from a field (want <={ADJ}); {len(far)} house(s) beyond a cluster-span of the fields",
            )
            # A NUCLEATED cluster must be a COMPACT FABRIC, not a thin hollow arc. `cluster_abuts_fields`
            # measures each house against the cluster's OWN span, so a big hollow cluster gets a big
            # allowance and passes even when a horn juts into empty ground far from the crops. Measure the
            # BUILT COVERAGE of the cluster's convex hull instead: the houses + their gardens / threshing
            # yards / farmstead groves should fill a healthy fraction of the footprint they span. A cluster
            # strung thin over a wide, hollow hull (the placer pulls every house to hug the paddy and packs
            # ALONG it, so an over-WIDE seed shape strings them into a stranded arc) fills far less of its
            # hull than a compact blob does. CALIBRATION: the pathological rolled crescent that motivated this
            # filled ~0.20 (Kikuta: 55 houses over a hull filled 20%, NE horn ~400px from any crop); the
            # roll_village placer's healthy nucleated villages fill ~0.28-0.31, and the tightly hand-placed
            # villages ~0.40. Floor 0.25 sits clear below the healthy band and above the pathology. Village
            # scale + >=12 houses only: a hamlet is legitimately loose, and a tiny cluster's hull is degenerate.
            if scale == "village" and len(houses) >= 12:
                harea = poly_area(convex_hull([(h["x"], h["y"]) for h in houses]))
                built = sum(r.get("w", 30) * r.get("h", 24) for grp in ("houses", "gardens", "threshing_yards", "groves") for r in M.get(grp, []))
                cov = built / harea if harea else 0.0
                pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
        else:
            # A FLAT ADJ, WITH NO SPAN ALLOWANCE - and it stays that way. Feature 126 relaxed this
            # to `ADJ + 2 * span`, arguing that the NUCLEATED branch above is the more generous of
            # the two and that a scattered settlement legitimately spreads further from its fields.
            # The regression corpus refuted it within one gate run:
            # `all_houses_field_adjacent_dispersed_fires_on_a_remote_house.json` stopped tripping,
            # and that is a frozen map which MUST fail. The flat rule is doing real work here.
            #
            # If the dispersed and linear forms are switched back on (see `SETTLEMENT_FORMS` in
            # hamletgen/consts.py, currently pinned to nucleated), this branch is worth revisiting -
            # but WITH that fixture kept red, not by widening the bound until the new maps pass.
            far = [h for h, d in dists if d > ADJ]
            pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes

            # ...and the outline that adjacency was just measured against must BE the planting. A field's
            # `outline` is the smoothed ENVELOPE the water net claims; `vis_bbox` is the extent of the plots
            # actually DRAWN. They diverge when a gen declares more field than the comb fills (an over-declared
            # `field_fall`): the surplus becomes a PHANTOM TAIL - invisible on the map, but fully real to every
            # distance test. A farm hugging that tail reads as "field-adjacent" while sitting well out past the
            # last rice, which is exactly how Akagahara grew a line of farmsteads hanging south of its paddy
            # (the tail was 181px; the gate saw nothing). Without this, `all_houses_field_adjacent` has no teeth
            # on precisely the maps that need it. DISPERSED only: there the outline is load-bearing for
            # placement, whereas a nucleated cluster is seeded as a unit and never rides the envelope, so a tail
            # is inert (Hoshigaoka/Kikuta carry ~210px tails harmlessly). Tolerance 60px allows the genuine
            # rounding of a smoothed rim over irregular plots, well under the ~165px band it protects.
            PHANTOM = 60
            tails = []
            for f in fields:
                b, v = f.get("bbox"), f.get("vis_bbox")
                if not b or not v:
                    continue
                pad = max(v[0] - b[0], v[1] - b[1], b[2] - v[2], b[3] - v[3])
                if pad > PHANTOM:
                    tails.append(f"{f.get('name')} (+{pad:.0f}px)")
            pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
    return _kept(locals(), ('PHANTOM', '_', 'b', 'built', 'ccx', 'ccy', 'cov', 'd', 'dists', 'f', 'far', 'grp', 'h', 'harea', 'hh', 'hx', 'hy', 'nearest', 'pad', 'r', 'span', 'tails', 'v'))


# DWELLINGS sit on the DRY higher ground, NEVER in the wet low toe below the field's drainage. The field
# drains to its lowest edge (the akusui collector ditch); the ground DOWNSLOPE of that drain - reed marsh,
# low reclaimed paddy, or the drainage tameike - is the wettest in the valley and is not building ground.
# So no dwelling may sit downslope of the drain line WITHIN the drain's cross-slope span (a farm off to the
# SIDE, past the drain's ends, is a legit flank homestead and is NOT flagged - only the central toe below
# the drain is). Scoped to DISPERSED maps (like the per-house `all_houses_field_adjacent` above): each
# strewn farm must individually sit on dry ground, whereas a NUCLEATED cluster is placed as a unit and
# governed by `cluster_abuts_fields` (and a tight cluster beside a diagonal drain reads as "downslope" of it
# without being in any wet toe). Needs the map's slope (meta.down_deg) + a drain ditch; skipped otherwise.
# WHY: the GM (2026-07) flagged dispersed farmhouses strewn S of a drainage ditch into marshland - see
# settlements.md 'Marsh'.
# PER-FIELD FALL here too (GM 2026-07-25): each drain carries its OWN downslope, so a map that
# declares no single bearing - the two provincial cities, whose fans fall 210 deg apart - is still
# checked. This was the last of the three drainage-slope checks left on the map-level constant,
# which meant it silently skipped both cities even after the other two were converted.


def _seg_0233__down_deg(*, meta: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 233 (down_deg) - body verbatim from the legacy gate() (feature 022)."""
    down_deg = meta.get("down_deg")
    return _kept(locals(), ('down_deg',))


def _seg_0234___fdd_here(*, M: Any = _UNBOUND, f: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 234 (_fdd_here, f) - body verbatim from the legacy gate() (feature 022)."""
    _fdd_here = {f.get("name"): f["down_deg"] for f in M.get("fields", []) if f.get("down_deg") is not None}
    return _kept(locals(), ('_fdd_here', 'f'))


def _seg_0235__drains(*, M: Any = _UNBOUND, _fdd_here: Any = _UNBOUND, down_deg: Any = _UNBOUND, fd: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 235 (drains, fd) - body verbatim from the legacy gate() (feature 022)."""
    drains = [(fd["poly"], _fdd_here.get(fd.get("field"), down_deg)) for fd in M.get("field_ditches", []) if fd.get("role") == "drain" and len(fd.get("poly", [])) >= 2]
    return _kept(locals(), ('drains', 'fd'))


def _seg_0236__dd_(*, dd_: Any = _UNBOUND, drains: Any = _UNBOUND, pl_: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 236 (dd_, drains, pl_) - body verbatim from the legacy gate() (feature 022)."""
    drains = [(pl_, dd_) for pl_, dd_ in drains if dd_ is not None]
    return _kept(locals(), ('dd_', 'drains', 'pl_'))


# NOT APPLIED AT CITY SCALE (GM decision 2026-07-25). City farms are RING-placed - s.ring lays
# them around the whole field envelope as a unit, so the low-side arc necessarily lands below the
# collector; by this check's own rationale that belongs with the NUCLEATED exemption ("a cluster is
# placed as a unit"), not the dispersed case it was written for. It is also RIGHT for a moated city:
# the farms round a moat legitimately differ by local topography - some drain INTO the moat, others
# have their paddies FED BY it - and expecting every one of them to sit above its field's collector
# imposes a uniformity the ground does not have. (For the record, turning it on flags 25% of Tango's
# farmhouses and 42% of Nagahara's: the ring algorithm, not stray misplacements.)


def _seg_0237__dwellings_above_field_drain(
    *,
    M: Any = _UNBOUND,
    _d: Any = _UNBOUND,
    _ddd: Any = _UNBOUND,
    at_end: Any = _UNBOUND,
    ax: Any = _UNBOUND,
    ay: Any = _UNBOUND,
    best: Any = _UNBOUND,
    bx: Any = _UNBOUND,
    by: Any = _UNBOUND,
    check: Any = _UNBOUND,
    d: Any = _UNBOUND,
    dp: Any = _UNBOUND,
    drains: Any = _UNBOUND,
    dux: Any = _UNBOUND,
    duy: Any = _UNBOUND,
    h: Any = _UNBOUND,
    houses: Any = _UNBOUND,
    in_toe: Any = _UNBOUND,
    ll: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    px: Any = _UNBOUND,
    py: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    si: Any = _UNBOUND,
    toe_px: Any = _UNBOUND,
    tt: Any = _UNBOUND,
    vx: Any = _UNBOUND,
    vy: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 237 (dwellings_above_field_drain) - body verbatim from the legacy gate() (feature 022)."""
    if houses and drains and not meta.get("nucleated") and scale != "city":
        # the WET TOE is a BAND below the collector (~240 real ft - the marsh/reclaimed strip the
        # runoff keeps soggy), not an infinite downslope slab: without this cap the first town
        # with drains (Hirameki) had tenements flagged 780px away, across the town wall, merely
        # for being south of a field's collector. Distance converts at the map's ft/px.
        toe_px = 240.0 / float(meta.get("ftpx", 1) or 1)
        in_toe = []
        for h in houses + M.get("buildings", []):
            for dp, _ddd in drains:
                dux, duy = math.cos(math.radians(_ddd)), math.sin(math.radians(_ddd))
                best = None
                for si in range(len(dp) - 1):
                    ax, ay = dp[si]
                    bx, by = dp[si + 1]
                    vx, vy = bx - ax, by - ay
                    ll = vx * vx + vy * vy
                    tt = 0.0 if ll == 0 else max(0.0, min(1.0, ((h["x"] - ax) * vx + (h["y"] - ay) * vy) / ll))
                    px, py = ax + vx * tt, ay + vy * tt
                    d = math.hypot(h["x"] - px, h["y"] - py)
                    at_end = (si == 0 and tt <= 0.001) or (si == len(dp) - 2 and tt >= 0.999)  # clamped to the polyline's absolute end -> off the side
                    if best is None or d < best[0]:
                        best = (d, px, py, at_end)
                assert best is not None
                _d, px, py, at_end = best
                if not at_end and _d <= toe_px and (h["x"] - px) * dux + (h["y"] - py) * duy > 18:  # center clearly on the wet (downslope) side, within the toe band
                    in_toe.append((round(h["x"]), round(h["y"])))
                    break
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
    return _kept(locals(), ('_d', '_ddd', 'at_end', 'ax', 'ay', 'best', 'bx', 'by', 'd', 'dp', 'dux', 'duy', 'h', 'in_toe', 'll', 'px', 'py', 'si', 'toe_px', 'tt', 'vx', 'vy'))


def _seg_0238__runs_off_edge(*, EX0: Any = _UNBOUND, EX1: Any = _UNBOUND, EY0: Any = _UNBOUND, EY1: Any = _UNBOUND, ol: Any = _UNBOUND, p: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 238 (runs_off_edge) - body verbatim from the legacy gate() (feature 022)."""

    def runs_off_edge(ol: Poly) -> bool:
        return any(p[0] < EX0 or p[0] > EX1 or p[1] < EY0 or p[1] > EY1 for p in ol)

    return _kept(locals(), ('runs_off_edge',))


def _seg_0240__h_1(*, h: Any = _UNBOUND, houses: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 240 (h, not_south) - body verbatim from the legacy gate() (feature 022)."""
    not_south = [h for h in houses if h["w"] < h["h"] or abs(h["rot"]) > 12]
    return _kept(locals(), ('h', 'not_south'))


def _seg_0241__houses_face_south(*, check: Any = _UNBOUND, not_south: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 241 (houses_face_south) - body verbatim from the legacy gate() (feature 022)."""
    check("houses_face_south", not not_south, f"{len(not_south)} house(s) not south-facing")
    return _kept(locals(), ())


def _seg_0242__h_2(*, h: Any = _UNBOUND, houses: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 242 (h, headman) - body verbatim from the legacy gate() (feature 022)."""
    headman = next((h for h in houses if h.get("role") == "headman"), None)
    return _kept(locals(), ('h', 'headman'))


def _seg_0243__village_has_headman(*, check: Any = _UNBOUND, headman: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 243 (capital_has_no_headman, city_has_no_headman, hamlet_has_no_headman, town_has_no_headman, village_has_headman, village_has_no_headman) - body verbatim from the legacy gate() (feature 022)."""
    if scale == "village":
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
    else:
        # hamlets fall under the village district headman; towns are run by the magistrate
        check(f"{scale}_has_no_headman", headman is None, f"a {scale} has no peasant headman of its own")
    return _kept(locals(), ())


# religious building by settlement scale: hamlet none, village shrine, town
# monastery, city temple
# WHY (the Shinto/Buddhist split + scale: shrine -> monastery -> temple): settlements.md "Historical grounding"
# a capital is the city tier at 4x scale - temples, same as a provincial city (feature 020)


# TORII COUNT NUMEROLOGY (GM canon 2026-07-21): a torii approach is either a MODEST ENTRANCE
# (1-2 arches) or a FULL AVENUE of EXACTLY SEVEN - 7 is the numerologically significant count.
# (RETIRED 2026-07-21: torii_full_avenue_is_seven sanctioned {1, 2, 7} and banned 3-6 as "an
# unfinished avenue". The GM's numerology ruling the same day supersedes it - counts are exactly
# {1, 3, 7} at EVERY proper hall, with torii_outlier for marked exceptions - and that doctrine is
# gated by torii_count_canonical below, which also fixes this check's misattribution: it assigned
# arches to the nearest of ALL religious features, so a wayside small_shrine near a temple sando
# could absorb the temple's gates and hide a violation, which is exactly how Tango's 2-arch
# Daikoku entrance slipped through.)

# ... and a village/hamlet SHRINE has a village-scale FOOTPRINT (GM 2026-07-21, caught on Hikari no
# Sato, whose two shrines survived from before the size norms crystallized at 192x128 / 236x164 ft -
# small-monastery footprints in a village). religious_matches_scale gates the TYPE per tier but said
# nothing about SIZE, so oversize halls sailed through. Calibration (the pool + temple-density canon): a
# village kami hall is a modest structure - the ordinary earth-god/water-mouth shrine is ~275 m^2
# (60x48 ft, Ueda/Hoshigaoka, with the recorded why in Ueda's gen), and Kikuta's showcase Benten with
# its 7-torii avenue is ~490 m^2 - so the 600 m^2 ceiling clears every deliberate design with headroom
# while the monastery/temple tier (a town's smallest monastery runs well past 1,000 m^2) stays cleanly
# out of reach. No floor: a tiny wayside hall is legitimate.


# A SHRINE and its TORII arch NESTLE in a CLEARING within the sacred grove - neither may sit UNDER the trees
# (a hall/arch drawn on top of tree canopy reads as buried in the wood). So no fengshui-grove tree CLUMP may
# overlap a religious hall's or a torii's footprint. The recorded clump `r` is the NOMINAL clump radius, but
# the drawn crowns OVERHANG it, so the visible canopy reaches ~1.7x that - use the CANOPY radius so the check
# matches what the eye sees. (The grove is drawn to SKIP the shrine + torii clearing; place them BEFORE it.)


def _seg_0248__CANOPY() -> dict[str, Any]:
    """Gate segment 248 (CANOPY) - body verbatim from the legacy gate() (feature 022)."""
    CANOPY = 1.7
    return _kept(locals(), ('CANOPY',))


def _seg_0249__c_3(*, CANOPY: Any = _UNBOUND, M: Any = _UNBOUND, c: Any = _UNBOUND, gv: Any = _UNBOUND, k: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 249 (c, grove_clumps, gv, k) - body verbatim from the legacy gate() (feature 022)."""
    grove_clumps = [(c[0], c[1], gv.get("r", 10) * CANOPY) for k in ("village_groves", "groves") for gv in M.get(k, []) for c in gv.get("clumps", [])]
    return _kept(locals(), ('c', 'grove_clumps', 'gv', 'k'))


def _seg_0250__shrine_clear_of_grove_trees(
    *,
    M: Any = _UNBOUND,
    _under_trees: Any = _UNBOUND,
    check: Any = _UNBOUND,
    cpd: Any = _UNBOUND,
    cr: Any = _UNBOUND,
    cx: Any = _UNBOUND,
    cx0: Any = _UNBOUND,
    cy: Any = _UNBOUND,
    gcr: Any = _UNBOUND,
    gcx: Any = _UNBOUND,
    gcy: Any = _UNBOUND,
    grove_clumps: Any = _UNBOUND,
    hh: Any = _UNBOUND,
    hw: Any = _UNBOUND,
    p: Any = _UNBOUND,
    pond_trees: Any = _UNBOUND,
    r: Any = _UNBOUND,
    t: Any = _UNBOUND,
    torii_under: Any = _UNBOUND,
    under_trees: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 250 (shrine_clear_of_grove_trees, torii_clear_of_grove_trees, trees_clear_of_fengshui_ponds) - body verbatim from the legacy gate() (feature 022)."""
    if grove_clumps:

        def _under_trees(cx0: float, cy0: float, hw: float, hh: float) -> bool:  # any canopy circle overlaps the rect (center cx0,cy0; half hw,hh)?
            return any((cx - cx0 - max(-hw, min(hw, cx - cx0))) ** 2 + (cy - cy0 - max(-hh, min(hh, cy - cy0))) ** 2 < cr * cr for cx, cy, cr in grove_clumps)

        under_trees = [(round(r["x"]), round(r["y"])) for r in M.get("religious", []) if _under_trees(r["x"], r["y"], r["w"] / 2, r["h"] / 2)]
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
        # a torii is recorded [x, y, z]; its arch spans x +/-19, y -10..+18 (center ~y+4, half-height 14)
        torii_under = [(round(t[0]), round(t[1])) for t in M.get("torii", []) if _under_trees(t[0], t[1] + 4, 19, 14)]
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
        # ... and no tree canopy crosses a fengshui CRESCENT POND's water (GM 2026-07-21, caught on
        # Hoshigaoka, where a windbreak clump overhung the half-moon pond): the banyuetang is an OPEN water
        # mirror at the settlement's front - reflecting sky is its fengshui job - and its flat-side forecourt
        # was the village's open ceremony/work ground, so trees neither overhang the water nor crowd it.
        # Same canopy doctrine as the shrine/torii checks (drawn crowns reach ~1.7x the clump's nominal r).
        pond_trees = []
        for cpd in M.get("crescent_ponds", []):
            for gcx, gcy, gcr in grove_clumps:
                if point_in_poly(gcx, gcy, cpd["poly"]) or poly_dist(gcx, gcy, [tuple(p) for p in cpd["poly"]]) < gcr:
                    pond_trees.append((round(gcx), round(gcy)))
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
    return _kept(locals(), ('_under_trees', 'cpd', 'gcr', 'gcx', 'gcy', 'p', 'pond_trees', 'r', 't', 'torii_under', 'under_trees'))


# every fengshui crescent pond carries its "geomantic pond" label (GM 2026-07-21): a culturally specific
# feature that does not read by itself - the GM asked "what is that?" of an unlabeled one, so the
# don't-label-the-obvious rule cuts the OTHER way here. crescent_pond() draws the label; this gates it.


# a religious building's subtitle must not RESTATE its type (the label already names it,
# e.g. "Monastery of Tengen" needs no "(town monastery)" note)


def _seg_0254__r_1(*, M: Any = _UNBOUND, r: Any = _UNBOUND, t: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 254 (r, redundant_sub, t) - body verbatim from the legacy gate() (feature 022)."""
    redundant_sub = [r.get("label") for r in M.get("religious", []) if r.get("sublabel") and any(t in r["sublabel"].lower() for t in ("shrine", "monastery", "temple"))]
    return _kept(locals(), ('r', 'redundant_sub', 't'))


# no two body labels overlap (the title block is excluded by the generator)


def _seg_0257__labels(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 257 (labels) - body verbatim from the legacy gate() (feature 022)."""
    labels = M.get("labels", [])
    return _kept(locals(), ('labels',))


# An overlap is real when the bboxes cross by more than the estimation slack. The horizontal slack
# is small (a >2px x-overlap means the glyphs actually touch); the vertical slack stays larger (~4px)
# to absorb the descender allowance in the y-bbox, so two cleanly-separated STACKED labels whose boxes
# merely kiss (e.g. Tango's "Mausoleum" / "Ministry of Works") are not falsely flagged.


def _seg_0258___lb_shrunk(*, L: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 258 (_lb_shrunk) - body verbatim from the legacy gate() (feature 022)."""

    def _lb_shrunk(L: Sequence[Any]) -> list[tuple[float, float]]:
        # a TILTED pair is judged by the true drawn quads (SAT), with the same estimation slack
        # the box test subtracts (2px x, 4px y) taken off each record in ITS OWN frame before
        # rotating - so the tilted verdict is the box verdict's geometry, rotated
        return label_quad([L[0] + 1.0, L[1] + 2.0, L[2] - 1.0, L[3] - 2.0, *L[4:]])

    return _kept(locals(), ('_lb_shrunk',))


def _seg_0259__i_2(*, _lb_shrunk: Any = _UNBOUND, i: Any = _UNBOUND, j: Any = _UNBOUND, labels: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 259 (i, j, ov) - body verbatim from the legacy gate() (feature 022)."""
    ov = [
        (i, j)
        for i in range(len(labels))
        for j in range(i + 1, len(labels))
        if (
            sat_overlap(_lb_shrunk(labels[i]), _lb_shrunk(labels[j]))
            if len(labels[i]) > 7 or len(labels[j]) > 7
            else min(labels[i][2], labels[j][2]) - max(labels[i][0], labels[j][0]) > 2 and min(labels[i][3], labels[j][3]) - max(labels[i][1], labels[j][1]) > 4
        )
    ]
    return _kept(locals(), ('i', 'j', 'ov'))


def _seg_0260__no_label_overlaps(*, check: Any = _UNBOUND, ov: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 260 (no_label_overlaps) - body verbatim from the legacy gate() (feature 022)."""
    check("no_label_overlaps", not ov, f"{len(ov)} overlapping label pair(s)")
    return _kept(locals(), ())


# A caption must HUG the thing it names. "Empty ground wins" (the label doctrine) used to be the
# only rule, and empty ground is plentiful - so a caption could satisfy it 55px out with nothing
# but bare land between it and its subject, reading as if it named whatever it had drifted next
# to (Tango's south "gate market" ended up nearer the flophouse than the stalls). The engine's
# standoff ladder now seats such a caption at the NEAREST clear spot and records the subject's
# box as element [6] of the label record; this measures the FINISHED gap from the recorded
# boxes, so it verifies the outcome rather than re-deriving the placer's own arithmetic.
#
# Only ladder-placed captions carry a referent. A district/zone caption ("samurai neighborhood",
# "agricultural district") names an AREA, not a feature, and is deliberately exempt - it is
# governed instead by city_labels_placed_with_subject.


def _seg_0261__adrift() -> dict[str, Any]:
    """Gate segment 261 (adrift) - body verbatim from the legacy gate() (feature 022)."""
    adrift = []  # type: ignore[var-annotated]
    return _kept(locals(), ('adrift',))


def _seg_0262__L(*, L: Any = _UNBOUND, adrift: Any = _UNBOUND, lab_gap: Any = _UNBOUND, lab_size: Any = _UNBOUND, labels: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 262 (L, adrift, lab_gap, lab_size) - body verbatim from the legacy gate() (feature 022)."""
    for L in labels:
        if len(L) < 7 or not L[6]:
            continue
        lab_size = (L[3] - L[1]) / 1.05  # the recorded box is ascent (0.8) + descender (0.25) tall (elements [0..3] stay the pre-tilt box, so this holds for tilted records too)
        # a TILTED caption's gap is measured from its true drawn quad (poly_gap, the rotated
        # sibling of box_gap - same measure, same 0-at-touch convention)
        lab_gap = poly_gap(label_quad(L), [(L[6][0], L[6][1]), (L[6][2], L[6][1]), (L[6][2], L[6][3]), (L[6][0], L[6][3])]) if len(L) > 7 else box_gap(L[:4], L[6])
        if lab_gap > LABEL_AIR_CAP * lab_size:
            adrift.append(f"{L[5]!r} {lab_gap:.0f}px from its subject (cap {LABEL_AIR_CAP * lab_size:.0f}px)")
    return _kept(locals(), ('L', 'adrift', 'lab_gap', 'lab_size'))


def _seg_0263__label_hugs_its_referent(*, adrift: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 263 (label_hugs_its_referent) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "label_hugs_its_referent",
        not adrift,
        f"caption(s) floating too far from the feature they name - the standoff ladder could not seat them near their subject, so move the subject or caption it by hand: {sorted(adrift)}",
    )
    return _kept(locals(), ())


# A caption naming a LINEAR feature must RUN ALONG it (GM 2026-08-08). The 2026-08-02 tilt
# fixed this for building glyphs and stopped at them, so "Imperial Road" still sat level beside
# Hoshizora's -27deg roadbed - level text against a diagonal subject, which is the same reason
# a level caption beside a rot=-16 inn read wrong. The ROAD caption is the linear case the gate
# can hold: the engine seats it itself, so there is no hand-placed anchor to excuse.
#
# `linear_tilt` is the SHARED definition, imported rather than restated (placement and its
# check read the same source - this skill's CLAUDE.md). That matters most for the part that
# looks like an exception: a road steeper than 45deg keeps a LEVEL caption (the GM's
# north-south convention - there is no second edge family to align with, so tilting would
# match nothing drawn), and because the clamp lives in one function the check demands level
# there rather than being silent about it. Tango (due N-S) and Nagahara (72deg) are gated as
# firmly as Hoshizora, they just expect 0.


# the TITLE (the map's place name) must sit over BLANK space, not on a building / field / water / grove -
# the reader has to be able to read it. The generator searches for a clear box (crop_to_content first, so the
# search runs over the framed window); this verifies it landed clear. Solid features + the fields + pond.


def _seg_0266__ttl(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 266 (ttl) - body verbatim from the legacy gate() (feature 022)."""
    ttl = M.get("title")
    return _kept(locals(), ('ttl',))


def _seg_0267__title_clear_of_features(
    *,
    M: Any = _UNBOUND,
    _lb2: Any = _UNBOUND,
    _thit_now: Any = _UNBOUND,
    check: Any = _UNBOUND,
    fdef: Any = _UNBOUND,
    ftpx: Any = _UNBOUND,
    k: Any = _UNBOUND,
    lb2: Any = _UNBOUND,
    pcx: Any = _UNBOUND,
    pcy: Any = _UNBOUND,
    prx: Any = _UNBOUND,
    pry: Any = _UNBOUND,
    s: Any = _UNBOUND,
    sb: Any = _UNBOUND,
    tb: Any = _UNBOUND,
    thit: Any = _UNBOUND,
    ttl: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 267 (scalebar_matches_declared_scale, title_clear_of_features, title_has_placard) - body verbatim from the legacy gate() (feature 022)."""
    if ttl:
        tb = ttl["bbox"]
        tc = [(tb[0], tb[1]), (tb[2], tb[1]), (tb[2], tb[3]), (tb[0], tb[3])]
        thit = []
        for k in (
            "houses",
            "gardens",
            "threshing_yards",
            "groves",
            "dry_plots",
            "buildings",
            "manors",
            "religious",
            "flophouses",
            "storehouses",
            "merchant_estates",
            "ministries",
            # NOT "village_groves" since feature 137 T06 (2026-08-28): the placard is an opaque card, so the
            # name reads over anything; what it must not HIDE is a building, a plot, a field, water, a lane
            # or a label. A strip of belt or wood under the card hides nothing a reader needs, and a tall
            # hamlet framed tight to its content often has no blank 200 x 106 px at all (10 of 48 cohort
            # seeds; seed 2's strips beside the field are 106 and 183 px wide). The generator still seats
            # the title on blank ground first and takes cover only as the last resort before the corner.
            # NOT "commons": the scrub is sparse GROUND COVER (a feathered grass scatter on open ground), not a
            # feature with a footprint, and a bold place name reads fine over it. Kept in step with
            # `_title_obstacles` in settlement.py - once the commons clothes the field's interior voids too it
            # covers nearly the whole map, so blocking on it would leave a title nowhere to sit.
            "marshes",
        ):
            for s in M.get(k, []):
                # THE POLY IS AUTHORITATIVE WHERE THERE IS ONE (2026-08-10): a scattered marsh
                # records a w/h AABB spanning its whole scatter - kikuta's pond fringe measures
                # 5,040 px across - so falling through to the box after the poly MISSES reports a
                # title sitting on ground the feature does not occupy. Only a record with no
                # outline is judged by its box.
                _thit_now = (
                    _box_hits_poly(tb, s["poly"])
                    if s.get("poly")
                    else ("w" in s and not (tb[2] < s["x"] - s["w"] / 2 or tb[0] > s["x"] + s["w"] / 2 or tb[3] < s["y"] - s["h"] / 2 or tb[1] > s["y"] + s["h"] / 2))
                )
                if _thit_now:
                    thit.append(k)
                    break
            if thit:
                break
        if not thit:
            for fdef in M.get("fields", []):
                if _box_hits_poly(tb, fdef["outline"]):
                    thit.append("fields")
                    break
        if not thit and M.get("pond"):
            pcx, pcy, prx, pry = M["pond"]
            if not (tb[2] < pcx - prx or tb[0] > pcx + prx or tb[3] < pcy - pry or tb[1] > pcy + pry):
                thit.append("pond")
        if not thit:
            # placed LABELS too: a title placard over a feature label erases it (caught 2026-07-23 on the
            # Tango content crop - the placard landed on the 'pauper ossuary mound' label)
            for lb2 in M.get("labels", []):
                _lb2 = label_aabb(lb2)  # a tilted caption's reach is its rotated AABB
                if not (tb[2] < _lb2[0] or tb[0] > _lb2[2] or tb[3] < _lb2[1] or tb[1] > _lb2[3]):
                    thit.append(f"label:{lb2[5]}")
                    break
        check(
            "title_clear_of_features",
            not thit,
            f"the map title sits on {thit[:2]} - it must go over BLANK space so the place name is readable (the generator's s.title() searches for a clear box; call it AFTER crop_to_content)",
        )
        # every settlement map shows a SCALE BAR (GM 2026-07-20, matching the Mode A compound sheets),
        # and the bar's declared distance must agree with the map's declared ft/px - the bar is 100
        # map-px, so ft = 100 x ftpx (100 hamlet/town, 200 village, 300 city). s.title() draws it, so
        # a manifest with a title but no scalebar means the generator predates the bar - regenerate.
        sb = M.get("scalebar")
        ftpx = M.get("meta", {}).get("ftpx", 1.0)
        check(
            "scalebar_matches_declared_scale",
            sb is not None and sb["ft"] == round(100 * ftpx),
            f"scalebar {sb} disagrees with (or is missing for) the declared scale of {ftpx} ft/px - the 100 map-px bar must read {round(100 * ftpx)} ft",
        )
        # ... and the block sits on its parchment PLACARD (GM 2026-07-21: ink over scrub speckle was hard
        # to read - the card keeps the title + scale legible over any ground cover). s.title() draws it;
        # a manifest without the record predates the card - regenerate.
        check(
            "title_has_placard",
            bool(ttl.get("placard")),
            "the title block records no placard - the parchment card under the title + scale bar is drawn by s.title(); regenerate the map",
        )
    return _kept(locals(), ('_lb2', '_thit_now', 'fdef', 'ftpx', 'k', 'lb2', 'pcx', 'pcy', 'prx', 'pry', 's', 'sb', 'tb', 'tc', 'thit'))


# WHY: <one paragraph - what the research found, the decision it drove, the departure taken>.
# Declare EVERY input the body reads as a keyword parameter (an undeclared one is a NameError at
# gate time, not at import), and keep the `_kept` tuple a LITERAL of the names this body binds.


def _seg_0267_500__labels_align_with_their_referent(
    *,
    M: Any = _UNBOUND,
    check: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    labels_align_with_their_referent_bad: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0267_500 (labels_align_with_their_referent) - a caption lies at exactly the angle of the rotated feature it names (GM 2026-08-27, feature 133 T38: "labels ... aligned with the thing that they are labeling").

    A label record carries its referent's box in element [6] and its tilt in [7] (absent = level).
    The referent is found by its center: any recorded feature with a `rot` whose (x, y) is within
    1.5 px of the box's center. Expected tilt is `aligned_tilt(rot)` - the subject's own angle
    normalized to [-90, 90) - and the caption must match it within 1 degree, mod 180. Inashiro's
    notice board stood at -122.8 degrees with a level caption for a month; nothing measured it."""
    if scale in ("hamlet", "village", "town"):
        labels_align_with_their_referent_bad = []
        _lar_subjects = [
            (float(_f["x"]), float(_f["y"]), float(_f.get("rot") or 0.0))
            for _k, _v in M.items()
            if isinstance(_v, list) and _k not in ("labels",)
            for _f in _v
            if isinstance(_f, dict) and "x" in _f and "y" in _f and _f.get("rot")
        ]
        for _L in M.get("labels") or []:
            if len(_L) < 7 or not _L[6]:
                continue
            _rb = _L[6]
            _cx, _cy = (float(_rb[0]) + float(_rb[2])) / 2.0, (float(_rb[1]) + float(_rb[3])) / 2.0
            _subj = [t for t in _lar_subjects if abs(t[0] - _cx) <= 1.5 and abs(t[1] - _cy) <= 1.5]
            if not _subj:
                continue
            _want = aligned_tilt(_subj[0][2])  # the ONE rule, including its square-rotation snap (feature 137 T06: a 90-degree board read -90 here and 0 in label())
            _got = float(_L[7]) if len(_L) > 7 and _L[7] else 0.0
            if min(abs(_got - _want) % 180.0, 180.0 - abs(_got - _want) % 180.0) > 1.0:
                labels_align_with_their_referent_bad.append((round(_cx), round(_cy), str(_L[5]), round(_got, 1), round(_want, 1)))
        check(
            "labels_align_with_their_referent",
            not labels_align_with_their_referent_bad,
            f"caption(s) {labels_align_with_their_referent_bad[:3]} (x, y, text, drawn deg, subject deg) not aligned with the feature they name - a label carries its subject's own angle (settlement.aligned_tilt); the fix is at the caller: pass rot= to label()",
        )
    return _kept(locals(), ("labels_align_with_their_referent_bad",))
