"""Gate segments (city ring and frame; keys 0000-0037) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from l7r.diagram.settlement import crop_boxes

from l7r.diagram.overlap.matrix import CANOPY_STRUCT_KEYS, GridIndex, matrix_extents
from .common_03_capacity import (
    _UNBOUND,
    _kept,
)

# NO SINGLE CAPTION MAY HOLD THE FRAME OPEN (GM 2026-08-11: "I am surprised that our cropping
# algorithm has not more aggressively cropped along the southern side... there should only be
# about one hundred feet between the southernmost map feature and the edge"). The crop was
# working exactly as specified - the margin is ~110 ft - but it frames CONTENT, and a caption
# counts as content. Two words floating in open ground 305 ft past the last structure were
# holding the whole south edge out, so the map read as badly cropped when it was in fact
# correctly cropped around a badly placed label. Measured per side: how far past the last
# STRUCTURE a label reaches. A caption naming a long linear feature may sit anywhere along it,
# so this costs nothing to satisfy - it just has to sit where the drawing is.
# 120 ft: the crop then adds its own ~110 ft margin on top, so a caption at the limit leaves
# ~230 ft of apparent emptiness past the last building - already generous. The capital's road
# and towpath words sat 180 ft out and read as a badly cropped map.


def _seg_0001___cf_pad() -> dict[str, Any]:
    """Gate segment 1 (_cf_pad) - body verbatim from the legacy gate() (feature 022)."""
    _cf_pad = 120.0
    return _kept(locals(), ('_cf_pad',))


def _seg_0002___cffx(*, meta: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 2 (_cffx) - body verbatim from the legacy gate() (feature 022)."""
    _cffx = float(meta.get("ftpx") or 1.0)
    return _kept(locals(), ('_cffx',))


def _seg_0003___(*, M: Any = _UNBOUND, _k: Any = _UNBOUND, q: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 3 (_, _cf_struct, _k, q) - body verbatim from the legacy gate() (feature 022)."""
    _cf_struct = [q for _k, q, *_ in matrix_extents(M) if q and _k not in ("roads", "road", "streams", "channels", "aqueducts", "towpaths", "quays", "canals", "field_ditches")]
    return _kept(locals(), ('_', '_cf_struct', '_k', 'q'))


# CANOPY IS CONTENT: a wood's caption sits over the wood, and a forest is drawn as individual
# crowns rather than as a footprint - so without them Moritono's "Shirin Forest" scored as a
# word floating in emptiness when it is sitting on the very thing it names.


def _seg_0004___cf_tc(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 4 (_cf_tc) - body verbatim from the legacy gate() (feature 022)."""
    _cf_tc = M.get("tree_crowns") or []
    return _kept(locals(), ('_cf_tc',))


def _seg_0005___cf_struct(*, _cf_struct: Any = _UNBOUND, _cf_tc: Any = _UNBOUND, _ci: Any = _UNBOUND, _cr: Any = _UNBOUND, _cx: Any = _UNBOUND, _cy: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 5 (_cf_struct, _ci, _cr, _cx) - body verbatim from the legacy gate() (feature 022)."""
    for _ci in range(0, len(_cf_tc) - 2, 3):
        _cx, _cy, _cr = _cf_tc[_ci], _cf_tc[_ci + 1], _cf_tc[_ci + 2]
        _cf_struct.append([(_cx - _cr, _cy - _cr), (_cx + _cr, _cy - _cr), (_cx + _cr, _cy + _cr), (_cx - _cr, _cy + _cr)])
    return _kept(locals(), ('_cf_struct', '_ci', '_cr', '_cx', '_cy'))


def _seg_0006___cf_bad() -> dict[str, Any]:
    """Gate segment 6 (_cf_bad) - body verbatim from the legacy gate() (feature 022)."""
    _cf_bad = []  # type: ignore[var-annotated]
    return _kept(locals(), ('_cf_bad',))


def _seg_0007___cf_bad_1(
    *,
    M: Any = _UNBOUND,
    _cf_bad: Any = _UNBOUND,
    _cf_pad: Any = _UNBOUND,
    _cf_struct: Any = _UNBOUND,
    _cffx: Any = _UNBOUND,
    _lb: Any = _UNBOUND,
    _over: Any = _UNBOUND,
    _sx0: Any = _UNBOUND,
    _sx1: Any = _UNBOUND,
    _sy0: Any = _UNBOUND,
    _sy1: Any = _UNBOUND,
    p: Any = _UNBOUND,
    q: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 7 (_cf_bad, _lb, _over, _sx0) - body verbatim from the legacy gate() (feature 022)."""
    if _cf_struct and M.get("labels"):
        _sx0 = min(min(p[0] for p in q) for q in _cf_struct)
        _sy0 = min(min(p[1] for p in q) for q in _cf_struct)
        _sx1 = max(max(p[0] for p in q) for q in _cf_struct)
        _sy1 = max(max(p[1] for p in q) for q in _cf_struct)
        for _lb in M["labels"]:
            if len(_lb) < 6:
                continue
            _over = max((_sx0 - _lb[0]), (_lb[2] - _sx1), (_sy0 - _lb[1]), (_lb[3] - _sy1)) * _cffx
            if _over > _cf_pad:
                _cf_bad.append((str(_lb[5]), round(_over)))
    return _kept(locals(), ('_cf_bad', '_lb', '_over', '_sx0', '_sx1', '_sy0', '_sy1', 'p', 'q'))


def _seg_0008__no_caption_holds_the_frame_open(*, _cf_bad: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 8 (no_caption_holds_the_frame_open) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "no_caption_holds_the_frame_open",
        not _cf_bad,
        f"caption(s) reaching far past the last STRUCTURE on their side, which drags the crop out with them (name, ft beyond): {sorted(_cf_bad)[:4]} - the crop frames content and a label IS content, so a word left floating in open ground reads as a badly cropped map; slide the caption along its subject to where the drawing is",
    )
    return _kept(locals(), ())


# A ROADSIDE WORK STANDS ON ITS ROAD, AND LIES ALONG IT (GM 2026-08-11: "the flophouse near
# the southwest city gate is absurdly far from the road - about three hundred feet - and it
# should be oriented to face the road... the two kiln works should be aligned with the road
# too"). Both halves are the same fact: these are features DEFINED by the way they serve. A
# doss-house exists to catch travelers arriving on that road; a kiln hauls fuel and clay by
# cart and stands on its haul road. Measured in real feet against the CURRENT ways, so a
# re-routed road drags them red rather than leaving them adrift.
# Distances calibrated from the pool, not guessed: doss-houses sit 84-420 ft off their road
# across the shipped maps, and the GM called ~300 ft "absurd" - 200 ft is comfortably past
# every reasonable one and short of every complaint. A KILN carries no distance rule at all: a
# nuisance works belongs OUT of town by its nature, and the GM's ask for it was alignment ("the
# two kiln works should be aligned with the road"), not proximity. None means angle-only.


# A CAPTION NAMING A POINT ON A WATERCOURSE MUST STAND AT THAT POINT (GM 2026-08-11: "the
# aqueduct labels are still really far away from the things that they are labeling... look at
# how much empty space exists between the intake weir and the label that labels it"). The
# standoff ladder seats a caption at LABEL_MIN_AIR and `label_hugs_its_referent` measures the
# finished gap - but BOTH only govern a caption that declares a subject, and these are placed
# by hand with no referent, so they escaped the pair of them. Here the subject is not declared,
# it is DERIVED: the manifest records where the intake and the terminus are, so the check reads
# the current geometry and a re-routed duct drags its words along instead of stranding them.


# A placement run that lands far under its ask is authored-vs-landed DRIFT, and _shortfall
# RECORDING it (GM 2026-08-05, "we definitely want that to be visible") turned out not to be
# enough on its own: the capital authored 283 frontage seats, drew 129, and the gate stayed
# green because nothing read the record back. 60% is the line because the only two runs in the
# pool that miss an AUTHORED count miss it by a hair - Ubame 21/23, Hirameki 13/14 - while
# every genuine drift sits far below it. A run that MEANS "place up to N" declares itself with
# fill=True and is never recorded here at all, so the check governs authored counts only.
# A SMALL ask is not judged by a percentage. A four-house monk terrace that seats two is one
# seat of rounding in a pocket, and chasing it just oscillates: trim to two, the neighbor's
# trim frees a hair, it seats three, and round it goes. Under eight the rule is simply that
# SOMETHING landed - a run that draws nothing at all is a real hole in the map either way.


# EVERY canopy crown the map draws, as (x, y, r) - forest/copse stands, their fringes, the fengshui
# grove clumps and the per-house yashikirin belts all record here (settlement._record_crowns). Stored
# flat because a to-scale map draws thousands. This is the DRAWN geometry, not the reserved area, so
# it is what the "nothing is drawn under a tree" checks measure.


def _seg_0023___tc(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 23 (_tc) - body verbatim from the legacy gate() (feature 022)."""
    _tc = M.get("tree_crowns") or []
    return _kept(locals(), ('_tc',))


def _seg_0024__crowns(*, _tc: Any = _UNBOUND, i: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 24 (crowns, i) - body verbatim from the legacy gate() (feature 022)."""
    crowns = [(_tc[i], _tc[i + 1], _tc[i + 2]) for i in range(0, len(_tc) - 2, 3)]
    return _kept(locals(), ('crowns', 'i'))


# INDEXED for the same reason _hq_covered is: a to-scale map draws thousands of crowns and
# carries hundreds of structures, and every "is anything under a tree" question is local. Each
# crown is indexed by its own disc bbox; a caller queries the rect it cares about grown by the
# LARGEST crown radius, so no overlap can be pruned away. Cell = 4x the mean crown.


def _seg_0025___cr_max(*, c: Any = _UNBOUND, crowns: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 25 (_cr_max, c) - body verbatim from the legacy gate() (feature 022)."""
    _cr_max = max((c[2] for c in crowns), default=0.0)
    return _kept(locals(), ('_cr_max', 'c'))


def _seg_0026__c(*, c: Any = _UNBOUND, crowns: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 26 (c, crown_grid) - body verbatim from the legacy gate() (feature 022)."""
    crown_grid = GridIndex(max(4 * (sum(c[2] for c in crowns) / len(crowns)) if crowns else 1.0, 8.0))
    return _kept(locals(), ('c', 'crown_grid'))


def _seg_0027___c(*, _c: Any = _UNBOUND, crown_grid: Any = _UNBOUND, crowns: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 27 (_c, crown_grid) - body verbatim from the legacy gate() (feature 022)."""
    for _c in crowns:
        crown_grid.add(_c[0] - _c[2], _c[1] - _c[2], _c[0] + _c[2], _c[1] + _c[2], _c)
    return _kept(locals(), ('_c', 'crown_grid'))


# NO TREE IS DRAWN ON A ROOF (GM 2026-07-25). A crown over a building hides the building - the map
# loses a structure the reader is meant to see - so no drawn crown may overlap any ROOFED footprint.
# This is stricter than the old reserved-area rules, which let a grove "hug the eaves": the fix at
# placement is per-crown (the stand THINS around a building rather than retreating from it), so the
# check has to read the crowns too. Open-air yards/gardens are deliberately out of scope - they have
# their own sun-corridor rules, and a crown over a yard corner is a real thing.


def _seg_0028__structures_clear_of_trees(
    *,
    M: Any = _UNBOUND,
    _cr_max: Any = _UNBOUND,
    check: Any = _UNBOUND,
    crown_grid: Any = _UNBOUND,
    crowns: Any = _UNBOUND,
    dx: Any = _UNBOUND,
    dy: Any = _UNBOUND,
    hh: Any = _UNBOUND,
    hw: Any = _UNBOUND,
    k: Any = _UNBOUND,
    o: Any = _UNBOUND,
    tr: Any = _UNBOUND,
    tx: Any = _UNBOUND,
    ty: Any = _UNBOUND,
    under: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 28 (structures_clear_of_trees) - body verbatim from the legacy gate() (feature 022)."""
    if crowns:
        under = []
        for k in CANOPY_STRUCT_KEYS:
            for o in M.get(k) or []:
                hw, hh = o.get("vw", o["w"]) / 2, o.get("vh", o["h"]) / 2  # the DRAWN box
                if o.get("rot"):
                    hw = hh = math.hypot(hw, hh)  # mirrors settlement._canopy_keepouts
                for tx, ty, tr in crown_grid.near_rect(o["x"] - hw - _cr_max, o["y"] - hh - _cr_max, o["x"] + hw + _cr_max, o["y"] + hh + _cr_max):
                    dx, dy = max(abs(tx - o["x"]) - hw, 0.0), max(abs(ty - o["y"]) - hh, 0.0)
                    if dx * dx + dy * dy < tr * tr:
                        under.append((k, round(o["x"]), round(o["y"])))
                        break
        check(
            "structures_clear_of_trees",
            not under,
            f"{len(under)} building(s) sit UNDER a drawn tree crown: {under[:4]} - a tree drawn on a roof "
            f"erases the building; the grove/stand must THIN around it (settlement._crown_covers filters "
            f"every crown at draw time, and a wood drawn BEFORE the buildings blocks its canopy reach so "
            f"later placement stays out from under it)",
        )
    return _kept(locals(), ('dx', 'dy', 'hh', 'hw', 'k', 'o', 'tr', 'tx', 'ty', 'under'))


# FARMS REACH THEIR FIELDS (GM 2026-08-02: hoshizora's lone farmhouse across the Imperial Road,
# alone inside the merchant block). Every farmstead with cultivated ground in reach must be able to
# walk to SOME of it without crossing a ROAD: if every reachable field/dry plot lies across a road,
# the steading is on the wrong side of the highway. ROADS only - streams are crossed by footbridges
# (the NW-bank pattern is deliberate) and lanes/streets are village grain. FAMILY: association/
# reach, deliberately center-based (the question is which side of the highway the steading lives
# on, not a clearance); reach = 500 real ft, generous enough that the pool's true farm belts all
# qualify (calibrated pool-wide 2026-08-03: exactly one house fires, the motivating defect).


# Every HARD feature the frame is meant to CONTAIN must actually lie INSIDE the rendered window. A deferred
# feature placed AFTER crop_to_content - a set-apart back-slope graveyard, an outlying shrine, the wells -
# can land outside the tight frame and be silently CLIPPED (caught the Ueda west graveyard, which the crop
# never framed because it was drawn after the crop). Scoped to the crop-to-content scales; a town/city is
# framed bespoke (tight to walls, fields run off-edge) so its "off-frame is intentional" is not a bug here.


# ONE FEATURE MUST NOT HOLD THE WHOLE FRAME OPEN (GM 2026-07-25). crop_hugs_content asks
# whether the MARGIN is generous; this asks the opposite question - whether a single element,
# standing far outside everything else, is by itself forcing a bigger image. Move it and the
# whole map crops tighter, so it is worth knowing about.
#
# THE DISCRIMINATOR IS THE RATIO, NOT THE GAP. A pond or a forest that extends the frame IS
# the outlying content: big, and meant to be out there. Measured across the pool, every
# legitimate case has a gap roughly equal to the feature's own size (ponds 1.03-1.35x,
# moritono's forest 1.14x), while Tango's tanning-yard caption stood 178 px past everything
# with a 10 px box of its own - 17.8x. So the rule is "further than its own size", with a
# 60 px floor so a trivial shift is not worth reporting. Reads crop_boxes(), the SAME
# contributor list the crop itself uses, so the two cannot drift apart.


def _seg_0034___cb(*, Hd: Any = _UNBOUND, M: Any = _UNBOUND, Wd: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 34 (_cb) - body verbatim from the legacy gate() (feature 022)."""
    _cb = crop_boxes(M, scale == "city", meta.get("ftpx", 1), Wd, Hd)
    return _kept(locals(), ('_cb',))


# (outer-most value, that feature's own extent on this axis, what it is) - built with
# LITERAL indices per side so each value stays a float rather than a tuple-union


def _seg_0035___sides(*, _cb: Any = _UNBOUND, b: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 35 (_sides, b) - body verbatim from the legacy gate() (feature 022)."""
    _sides = (
        ("west", [(-b[0], b[1] - b[0], b[4]) for b in _cb]),
        ("east", [(b[1], b[1] - b[0], b[4]) for b in _cb]),
        ("north", [(-b[2], b[3] - b[2], b[4]) for b in _cb]),
        ("south", [(b[3], b[3] - b[2], b[4]) for b in _cb]),
    )
    return _kept(locals(), ('_sides', 'b'))


def _seg_0036___lone() -> dict[str, Any]:
    """Gate segment 36 (_lone) - body verbatim from the legacy gate() (feature 022)."""
    _lone = []  # type: ignore[var-annotated]
    return _kept(locals(), ('_lone',))


def _seg_0037___gap(
    *,
    _gap: Any = _UNBOUND,
    _lone: Any = _UNBOUND,
    _own: Any = _UNBOUND,
    _r: Any = _UNBOUND,
    _side: Any = _UNBOUND,
    _sides: Any = _UNBOUND,
    _vals: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    v: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 37 (_gap, _lone, _own, _r) - body verbatim from the legacy gate() (feature 022)."""
    for _side, _vals in _sides:
        if len(_vals) < 2:
            continue
        _r = sorted(_vals, key=lambda v: -v[0])
        _gap, _own = _r[0][0] - _r[1][0], _r[0][1]
        if _gap > max(60.0, 3.0 * _own) and not meta.get("crop_outlier_ok"):
            _lone.append(f"{_side}: {_r[0][2]} stands {_gap:.0f}px past the next feature in (its own extent is only {_own:.0f}px)")
    return _kept(locals(), ('_gap', '_lone', '_own', '_r', '_side', '_vals'))
