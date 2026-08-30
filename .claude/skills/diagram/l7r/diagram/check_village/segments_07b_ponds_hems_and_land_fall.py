"""Gate segments (ponds hems and land fall; keys 0438_011-0464) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from l7r.diagram.overlap.taxonomy import Poly, point_in_poly, seg_dist, unit_dir
from l7r.diagram.overlap.matrix import in_ellipse
from .common_03_capacity import _UNBOUND, _kept

# NEAR-RING BAND CAP (2026-07-23): on a WALLED CITY the near ring is the ground within ~800 real ft
# of the rampart (a few minutes' walk out the gates - wide enough to take in the moat-fed fans' plot mass, since the first ~500 ft is structurally moat + farmstead rings + gate suburbs) - NOT
# everything the frame happens to show. The thresholds were calibrated on a tight crop whose visible
# extramural WAS that band ("the countryside proper runs off-frame" above); when the frame widened to
# show the comb deltas as countryside (GM 2026-07-23, Tango), an uncapped sampler silently redefined
# "near ring" as "all visible countryside" and diluted the fraction with ground the check was never
# meant to judge. Capping by real distance keeps the check meaning the same at ANY frame size.
# Towns (no wall) keep their tight frames; unchanged there.


# SAMPLING WINDOW: for a walled city the band is sampled in CANVAS space (the wall bbox expanded
# by the band), NOT the view - the manifest records full-canvas geometry, so the near ring exists
# whether or not the crop shows it, and the metric must not shift when the frame is tightened
# (caught 2026-07-23: the aggressive Nagahara crop clipped band cells and dropped the fraction
# below the floor with not one field changed). Towns keep the view window (no wall, no band).


# NEAR-RING PADDY DOMINANCE (feature 014). Feature 013 packed the near ring but filled it with
# DRY grain (dry cropland needs no plumbed water, the cheap fill) - historically backwards: a town
# sits in the fertile basin BECAUSE of the wet rice, so its flat waterable near ring is PADDY-
# dominant. Dry grain is the SECONDARY use on the drier/higher margins; vegetable/market gardens
# (crop=="garden") hug the town. This reuses the exact 25px near-ring band + `committed` mask above
# and tallies PADDY-covered cells vs DRY-GRAIN-covered cells (dry_plots whose crop != garden;
# gardens are the legitimate near-town dry use, not the thing demoted), requiring paddy to DOMINATE
# - scaled by tier so a dialed-down map is paddy-LED but sparser, never dry-dominant. REJECTED (per
# Constitution XII, recorded so it is never reinvented): the dry-grain-dominant near ring 013 shipped;
# the flat waterable valley floor of a wet-rice county seat is paddy, not dryland grain. Grounded in
# settlements.md "Near-ring farmland density" + budgets.md (the ~1/3-paddy figure is a DOMAIN-wide
# average over hills+margins - the near ring is the most waterable flat ground, so paddy-heavy).
# WHY the ratios: a dense well-sited basin reads clearly paddy-led (paddy >= 1.2x dry-grain); a thin
# grazing/relay locale need only keep paddy at least TYING dry-grain (paddy >= dry-grain), so the
# honest lower-tier answer (a thinner ring where little water reaches) is not forced to dense.
# NOTE: what counts as dry-grain EXCLUDES a paddy comb's own dry hem (below), so a moated city whose
# extramural is an open GLACIS - moat-fed paddy + a thin garden fringe, the rest kept clear for defense
# (Tango) - passes as long as its paddy out-covers the FREE-STANDING dry grain (of which a glacis has
# little). That is the honest read: the immediate glacis is not packed dry farmland.


# a paddy comb's own DRY HEM (the barley/soy upslope margin of the flooded field) is part of the
# paddy system, not a competing dry-grain crop - exclude any dry plot sitting within OR HUGGING a
# paddy field's envelope, so only FREE-STANDING dryland grain (the 013 blanket) counts against
# paddy dominance. The hem quilt RINGS the envelope - at the head/flanks it sits OUTSIDE the
# recorded bbox by up to the dry_band (~88px city / ~132px village), so the test expands the bbox
# by that band; a bare in-bbox test miscounted every comb's head hem as free-standing grain
# (caught 2026-07-23 when the near ring became combs-only and the "dry grain" was all hems).


# NO CANOPY STANDS OVER OPEN WATER (GM audit 2026-07): a village-grove clump drawn across a
# stream / channel / moat reads as trees growing in the current. The fengshui-pond rule
# (trees_clear_of_fengshui_ponds) covered only ponds; this closes the running-water half.
# village_grove now skips watercourse corridors at draw time; this is the ratchet.


def _seg_0439__wet_canopy() -> dict[str, Any]:
    """Gate segment 439 (wet_canopy) - body verbatim from the legacy gate() (feature 022)."""
    wet_canopy = []  # type: ignore[var-annotated]
    return _kept(locals(), ('wet_canopy',))


def _seg_0440__canopy_lines(*, M: Any = _UNBOUND, st_c: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 440 (canopy_lines, st_c) - body verbatim from the legacy gate() (feature 022)."""
    canopy_lines = [(st_c["poly"], st_c.get("w", 9) / 2) for st_c in M.get("streams", [])]
    return _kept(locals(), ('canopy_lines', 'st_c'))


def _seg_0441__canopy_lines_1(*, M: Any = _UNBOUND, canopy_lines: Any = _UNBOUND, cc_c: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 441 (canopy_lines, cc_c) - body verbatim from the legacy gate() (feature 022)."""
    canopy_lines += [(cc_c["poly"], cc_c.get("w", 2.5) / 2) for cc_c in M.get("channels", [])]
    return _kept(locals(), ('canopy_lines', 'cc_c'))


def _seg_0442__canopy_lines_2(*, M: Any = _UNBOUND, canopy_lines: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 442 (canopy_lines) - body verbatim from the legacy gate() (feature 022)."""
    if M.get("moat"):
        canopy_lines.append((M["moat"], M.get("moat_width", 22) / 2))
    return _kept(locals(), ('canopy_lines',))


def _seg_0443__cl_c(
    *, M: Any = _UNBOUND, canopy_lines: Any = _UNBOUND, cl_c: Any = _UNBOUND, k: Any = _UNBOUND, vg_c: Any = _UNBOUND, wet_canopy: Any = _UNBOUND, whw: Any = _UNBOUND, wl: Any = _UNBOUND
) -> dict[str, Any]:
    """Gate segment 443 (cl_c, k, vg_c, wet_canopy) - body verbatim from the legacy gate() (feature 022)."""
    for vg_c in M.get("village_groves", []):
        for cl_c in vg_c.get("clumps", []):
            if any(min(seg_dist(cl_c[0], cl_c[1], wl[k], wl[k + 1]) for k in range(len(wl) - 1)) < whw + 6 for wl, whw in canopy_lines):
                wet_canopy.append((round(cl_c[0]), round(cl_c[1])))
    return _kept(locals(), ('cl_c', 'k', 'vg_c', 'wet_canopy', 'whw', 'wl'))


def _seg_0444__canopy_clear_of_watercourses(*, check: Any = _UNBOUND, wet_canopy: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 444 (canopy_clear_of_watercourses) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "canopy_clear_of_watercourses",
        not wet_canopy,
        f"grove canopy clump(s) stand over open water at {sorted(set(wet_canopy))[:4]} - trees do not grow in a stream, channel, or moat; keep the belt polys (and the clump filter) clear of every watercourse",
    )
    return _kept(locals(), ())


def _seg_0445__watercourse_ends_reach_water(*, check: Any = _UNBOUND, dry_drains: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 445 (watercourse_ends_reach_water) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "watercourse_ends_reach_water",
        not dry_drains,
        f"canal/collector end(s) dangle in bare ground at {sorted(set(dry_drains))[:4]} - an on-map main or drain end outside the crop must JOIN a watercourse (a culvert, the stream, another ditch, the moat) or run off the frame; water never just stops",
    )
    return _kept(locals(), ())


def _seg_0446__channels_join_streams_at_confluence(*, check: Any = _UNBOUND, dry_mouths: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 446 (channels_join_streams_at_confluence) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "channels_join_streams_at_confluence",
        not dry_mouths,
        f"channel mouth(s) declared frm/to={{stream}} stop short of the bed at {sorted(set(dry_mouths))[:4]} - "
        f"an intake or drain culvert joins its stream at a CONFLUENCE (the mouth reaches into the water, like a "
        f"road junction), never dying in the grass beside the bank; snap the recorded polyline to the stream centerline",
    )
    return _kept(locals(), ())


# no field overlaps the town wall: a field may ABUT the wall but must stay on one
# side of it (the chrysanthemum field inside the walls touches but never crosses)


# EVERY fully-on-map paddy field must SHOW a source of water: a channel feeding it, or
# the field directly abutting a stream or pond (its bank at the water). A field merely
# NEAR water without a visible connection does not count. Fields that run off the map
# edge are exempt (their water source may be off-map too).


def _seg_0449__channels(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 449 (channels) - body verbatim from the legacy gate() (feature 022)."""
    channels = M.get("channels", [])
    return _kept(locals(), ('channels',))


def _seg_0450__streams_m(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 450 (streams_m) - body verbatim from the legacy gate() (feature 022)."""
    streams_m = M.get("streams", [])
    return _kept(locals(), ('streams_m',))


def _seg_0451__watered(
    *,
    c: Any = _UNBOUND,
    channels: Any = _UNBOUND,
    k: Any = _UNBOUND,
    ol: Any = _UNBOUND,
    pond: Any = _UNBOUND,
    px: Any = _UNBOUND,
    py: Any = _UNBOUND,
    sp: Any = _UNBOUND,
    st: Any = _UNBOUND,
    streams_m: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 451 (watered) - body verbatim from the legacy gate() (feature 022)."""

    def watered(ol: Poly) -> bool:
        if any(point_in_poly(c["poly"][-1][0], c["poly"][-1][1], ol) for c in channels):
            return True  # a channel ends inside it
        if any(
            seg_dist(px, py, sp[k], sp[k + 1]) < 18  # the field bank abuts a stream
            for st in streams_m
            for sp in [st["poly"]]
            for px, py in ol
            for k in range(len(sp) - 1)
        ):
            return True
        return bool(pond and any(in_ellipse(px, py, pond, 1.10) for px, py in ol))  # ...or the pond

    return _kept(locals(), ('watered',))


def _seg_0452__dry(*, f: Any = _UNBOUND, fields: Any = _UNBOUND, runs_off_edge: Any = _UNBOUND, watered: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 452 (dry, f) - body verbatim from the legacy gate() (feature 022)."""
    dry = [f["name"] for f in fields if f["kind"] == "paddy" and not runs_off_edge(f["outline"]) and not watered(f["outline"])]
    return _kept(locals(), ('dry', 'f'))


def _seg_0453__fields_show_water_source(*, check: Any = _UNBOUND, dry: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 453 (fields_show_water_source) - body verbatim from the legacy gate() (feature 022)."""
    check("fields_show_water_source", not dry, f"on-map field(s) with no visible water source (channel or abutting stream/pond): {sorted(set(dry))}")
    return _kept(locals(), ())


# water flows DOWNHILL. If the map declares its slope (meta(downhill=<dir>)), every
# channel must run with it: the source (tap on the stream/pond, poly[0]) sits uphill of
# where it feeds the field (poly[-1]). A channel angled the other way would carry the
# stream's water away from the field, not into it. <dir> is a cardinal name or [dx,dy]
# vector in map coords (+y = south). Maps without the tag are exempt (slope unknown).
# ONE DIRECTION MODEL, NOT THREE (GM 2026-07-25). These two were gated on the LEGACY
# meta(downhill) - a cardinal name or vector - which only 2 of 17 maps ever declared, so 15 maps
# (both provincial cities among them) skipped them entirely behind a green gate: the same
# silent-skip that hid the drainage-slope rules. The fall now comes from `downhill` where a map
# declares it, else meta(down_deg), and per-channel from the TARGET FIELD's own fall when it has
# one - a settlement ringed by farmland drains several ways at once, so the field a channel feeds
# is the right authority for whether that channel runs downhill into it.


def _seg_0454__downhill(*, meta: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 454 (downhill) - body verbatim from the legacy gate() (feature 022)."""
    downhill = meta.get("downhill")
    return _kept(locals(), ('downhill',))


def _seg_0455___dh_dd(*, meta: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 455 (_dh_dd) - body verbatim from the legacy gate() (feature 022)."""
    _dh_dd = meta.get("down_deg")
    return _kept(locals(), ('_dh_dd',))


def _seg_0456___dh_fields(*, M: Any = _UNBOUND, f: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 456 (_dh_fields, f) - body verbatim from the legacy gate() (feature 022)."""
    _dh_fields = {f.get("name"): f["down_deg"] for f in M.get("fields", []) if f.get("down_deg") is not None}
    return _kept(locals(), ('_dh_fields', 'f'))


def _seg_0457___dh_vec() -> dict[str, Any]:
    """Gate segment 457 (_dh_vec) - body verbatim from the legacy gate() (feature 022)."""

    def _dh_vec(deg: float) -> tuple[float, float]:
        return (math.cos(math.radians(deg)), math.sin(math.radians(deg)))

    return _kept(locals(), ('_dh_vec',))


def _seg_0458___dh_map(*, _dh_dd: Any = _UNBOUND, _dh_vec: Any = _UNBOUND, downhill: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 458 (_dh_map) - body verbatim from the legacy gate() (feature 022)."""
    _dh_map = unit_dir(downhill) if downhill else (_dh_vec(_dh_dd) if _dh_dd is not None else None)
    return _kept(locals(), ('_dh_map',))


def _seg_0460__channels_flow_downhill(
    *,
    L: Any = _UNBOUND,
    _cdd: Any = _UNBOUND,
    _cto: Any = _UNBOUND,
    _dh_fields: Any = _UNBOUND,
    _dh_map: Any = _UNBOUND,
    _dh_vec: Any = _UNBOUND,
    c: Any = _UNBOUND,
    channels: Any = _UNBOUND,
    check: Any = _UNBOUND,
    dvec: Any = _UNBOUND,
    ex: Any = _UNBOUND,
    ey: Any = _UNBOUND,
    sx: Any = _UNBOUND,
    sy: Any = _UNBOUND,
    uphill: Any = _UNBOUND,
    vx: Any = _UNBOUND,
    vy: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 460 (channels_flow_downhill) - body verbatim from the legacy gate() (feature 022)."""
    if (_dh_map or _dh_fields) and channels:
        uphill = []
        for c in channels:
            _cto = (c.get("to") or {}).get("name")
            _cdd = _dh_fields.get(_cto) if _cto else None
            dvec = _dh_vec(_cdd) if _cdd is not None else _dh_map
            if dvec is None:
                continue  # neither this channel's field nor the map declares a fall - nothing to judge it by
            (sx, sy), (ex, ey) = c["poly"][0], c["poly"][-1]
            vx, vy = ex - sx, ey - sy
            L = math.hypot(vx, vy)
            if L > 0 and (vx * dvec[0] + vy * dvec[1]) < 0.2 * L:  # not clearly running downhill
                uphill.append(c["to"].get("name", "?"))
        check("channels_flow_downhill", not uphill, f"channel(s) not running downhill (source must be uphill of the field it feeds): {sorted(set(uphill))}")
    return _kept(locals(), ('L', '_cdd', '_cto', 'c', 'dvec', 'ex', 'ey', 'sx', 'sy', 'uphill', 'vx', 'vy'))


# the same flow logic applies to a city MOAT: the moat is fed by a stream entering from one
# side (the source), so the moat water heads that-source-to-the-far-side direction (Tango's
# feeder enters from the north, so the moat water heads SOUTH). A moat-fed irrigation channel
# must run WITH that current - its field-end downstream of its moat-tap. A channel whose field
# is UPSTREAM of the tap reads as water flowing from the field INTO the moat (backwards).


# A MOAT JUNCTION IS SWEPT WITH THE CURRENT (GM 2026-07-25). Where a channel meets the moat, its
# LOCAL heading at the junction must carry a downstream component - a tributary joins a trunk
# pointing downstream, and an irrigation offtake takes off downstream so the water turns in
# smoothly instead of doubling back on itself. The engine already holds moat<->RIVER junctions to
# exactly this (city_moat_junction_angles: inlet near-square, outlet swept downstream); this
# extends it to moat<->CHANNEL junctions, which nothing checked.
#
# NOTE the quantity: the LOCAL segment at the junction, NOT the channel's net vector to its field.
# The net vector is near-arbitrary for an offtake that leaves the ring roughly perpendicular (that
# is why moat_channels_flow_with_current above keeps a coarse cardinal test and is NOT this check).
# The current is the ring TANGENT at the tap, in the direction of travel along that tap's own arc -
# a ring has no single downstream side, since water entering the inlet runs BOTH ways round to the
# outlet. WHAT IT CAUGHT (GM's eye, then this check): every offtake on BOTH cities stepped upstream,
# because the offtake tee was drawn as mirrored geometry whose along-rim step was never oriented to
# the local flow; plus Tango's fn2 drain culvert doubling back to enter at 138 deg and Nagahara's
# fnn1 at 115 deg. Fixtures: the pre-fix Tango and Nagahara manifests in pool/regressions/.
