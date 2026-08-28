"""Gate segments (capital ways and burial; keys 0106_027-0123) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from .common_01_geometry import _struct_rect, point_in_poly, rect_corners, seg_dist
from .common_03_capacity import (
    _UNBOUND,
    _kept,
)

# A CITY ESTATE'S CAPTION LIVES INSIDE ITS WALLS (GM 2026-08-09): the court is blank by
# doctrine (its contents belong to the Mode A sheet), so the empty court is the label's
# ground - a caption hung outside sits where 021's fabric must flow. Judged on the
# recorded label box vs the compound footprint; a manor whose caption is recorded
# elsewhere on the sheet fires, a manor with no matching caption record is skipped
# (label() always records, so that never happens on a generated map).


# A RIVER GETS A TOWPATH, NOT A ROAD (GM 2026-08-08; research/cities/capitals.md): water
# carried bulk far more cheaply than carts, so a trunk road shadowing a navigable river is
# redundant - a way may CROSS the river (bridged), never run along its bank. Judged
# centerline-to-centerline (ASSOCIATION family: the band dwarfs both widths, and the
# question is "does this way live on the bank", not a clearance).


# THE AQUEDUCT (GM 2026-08-08): a capital outgrows what wells alone can supply, so it
# carries a supply channel - open OUTSIDE the wall, buried inside, the GATE as the
# boundary (Edo's josui, Odawara's sosui; research/cities/capitals.md).


# DOORS OPEN OUTWARD; ROWS STACK AT MOST TWO DEEP (GM, 2026-07-18). An urban building's door
# glyph sits on its local +h/2 side (rotated by `rot` - settlement.building), so the door's
# world direction derives from the manifest alone. A door must open onto WALKABLE ground
# (street, roji, court, open space) - never into the back of another house an eave-gap away.
# FARMHOUSES ARE EXEMPT EVERYWHERE: a farmhouse always faces SOUTH (its garden and threshing
# ground need the sunlight - the orientation is canon); a city house has no sun constraint,
# so it must face open ground instead. The pair rule follows from the same fact: contiguous
# rows stack at most TWO deep (back-to-back, both fronts outward), because the middle row of
# a 3-stack has walls hard against BOTH long faces - those households would be trapped.
# Separations in real feet: an eave/drainage gap is ~3-6 ft (drainage, not an entrance), a
# walkable roji/court is >= ~10 ft; DOOR_CLEAR_FT = 7 sits cleanly between them at every
# map scale (ftpx converts to drawn px).


# A MERCHANT ESTATE'S WALL STANDS ON DRY, PRIVATE GROUND (GM, 2026-07-19). The walled
# compound of a very-rich urban merchant must not run its perimeter wall through WATER
# (a wall footed in a canal/dock basin is undermined, and the working quay/towpath must
# stay open to the boats and porters that make the merchant rich) or through a FIRE TOWER
# (the fire watch is municipal - it needs its own footing, daylight around the frame, and
# access for the watch; it cannot be embedded in a private compound wall). The whole
# perimeter is walked, gate gap included - a courtyard gate opening straight onto water
# or into the tower frame is the same siting error.


def _seg_0108__merchant_estate_wall_clear_of_water(
    *,
    M: Any = _UNBOUND,
    WMARG: Any = _UNBOUND,
    _in_grown_rect: Any = _UNBOUND,
    _near_line: Any = _UNBOUND,
    _tower_conflict: Any = _UNBOUND,
    _wall_hits: Any = _UNBOUND,
    _wall_pts: Any = _UNBOUND,
    al: Any = _UNBOUND,
    cc: Any = _UNBOUND,
    check: Any = _UNBOUND,
    dk: Any = _UNBOUND,
    e: Any = _UNBOUND,
    est: Any = _UNBOUND,
    est_ftowers: Any = _UNBOUND,
    est_on_st: Any = _UNBOUND,
    est_streets: Any = _UNBOUND,
    est_waters: Any = _UNBOUND,
    est_wet: Any = _UNBOUND,
    ew: Any = _UNBOUND,
    fn: Any = _UNBOUND,
    gc: Any = _UNBOUND,
    hw: Any = _UNBOUND,
    it: Any = _UNBOUND,
    k: Any = _UNBOUND,
    name: Any = _UNBOUND,
    pcx: Any = _UNBOUND,
    pcy: Any = _UNBOUND,
    prx: Any = _UNBOUND,
    pry: Any = _UNBOUND,
    pts: Any = _UNBOUND,
    px_: Any = _UNBOUND,
    py_: Any = _UNBOUND,
    rd: Any = _UNBOUND,
    rv: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    si: Any = _UNBOUND,
    st: Any = _UNBOUND,
    steps: Any = _UNBOUND,
    t: Any = _UNBOUND,
    towered: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 108 (merchant_estate_wall_clear_of_fire_towers, merchant_estate_wall_clear_of_streets, merchant_estate_wall_clear_of_water) - body verbatim from the legacy gate() (feature 022)."""
    if scale in ("town", "city") and M.get("merchant_estates"):
        WMARG = 1.5  # px of daylight demanded beyond the drawn footprints/line widths

        def _near_line(pts: Any, hw: float) -> Any:
            return lambda px_, py_: any(seg_dist(px_, py_, pts[k], pts[k + 1]) < hw for k in range(len(pts) - 1))

        def _in_grown_rect(it: dict[str, Any]) -> Any:
            gc = rect_corners(_struct_rect({**it, "w": it["w"] + 2 * WMARG, "h": it["h"] + 2 * WMARG}))
            return lambda px_, py_: point_in_poly(px_, py_, gc)

        est_waters: list[tuple[str, Any]] = [("canal", _near_line(cc["poly"], cc.get("w", 12) / 2 + WMARG)) for cc in M.get("canals", [])]  # type: ignore[no-redef]
        if M.get("moat"):
            est_waters.append(("moat", _near_line(M["moat"], M.get("moat_width", 22) / 2 + WMARG)))
        rv = M.get("river")
        if rv:
            est_waters.append(("river", _near_line(rv["pts"], rv.get("w", 40) / 2 + WMARG)))
        est_waters += [("dock", _in_grown_rect(dk)) for dk in M.get("docks", [])]
        if M.get("pond"):
            pcx, pcy, prx, pry = M["pond"]
            est_waters.append(("pond", lambda px_, py_: ((px_ - pcx) / (prx + WMARG)) ** 2 + ((py_ - pcy) / (pry + WMARG)) ** 2 <= 1))
        est_ftowers: list[tuple[str, Any]] = [("fire tower", _in_grown_rect(t)) for t in M.get("fire_towers", []) if "w" in t]  # type: ignore[no-redef]

        def _wall_pts(est: dict[str, Any]) -> list[tuple[float, float]]:
            ex0, ey0, ex1, ey1 = est["x"] - est["w"] / 2, est["y"] - est["h"] / 2, est["x"] + est["w"] / 2, est["y"] + est["h"] / 2
            pts = []
            for p0, p1 in [((ex0, ey0), (ex1, ey0)), ((ex1, ey0), (ex1, ey1)), ((ex1, ey1), (ex0, ey1)), ((ex0, ey1), (ex0, ey0))]:
                steps = max(2, int(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / 3))
                pts += [(p0[0] + (p1[0] - p0[0]) * si / steps, p0[1] + (p1[1] - p0[1]) * si / steps) for si in range(steps + 1)]
            return pts

        def _wall_hits(est: dict[str, Any], targets: list[tuple[str, Any]]) -> list[str]:
            pts = _wall_pts(est)
            return [name for name, fn in targets if any(fn(px_, py_) for px_, py_ in pts)]

        est_wet = [(round(e["x"]), round(e["y"]), _wall_hits(e, est_waters)) for e in M["merchant_estates"]]
        est_wet = [ew for ew in est_wet if ew[2]]
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes

        # a tower ENCLOSED in the private court (wall-line clear, tower trapped inside) is the
        # same siting error as a wall through it - the watch must reach its tower from public ground
        def _tower_conflict(e: dict[str, Any]) -> bool:
            if _wall_hits(e, est_ftowers):
                return True
            return any(abs(t["x"] - e["x"]) < e["w"] / 2 and abs(t["y"] - e["y"]) < e["h"] / 2 for t in M.get("fire_towers", []) if "w" in t)

        towered = [(round(e["x"]), round(e["y"])) for e in M["merchant_estates"] if _tower_conflict(e)]
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes

        # THE SAME WALLS STAY OFF THE STREETS (GM follow-up, 2026-07-19): a compound wall
        # standing in a street bed blocks the public way - the wall may LINE a street (that is
        # what a walled compound on a block looks like) but never stand IN its cleared band.
        est_streets: list[tuple[str, Any]] = [("street", _near_line(st["pts"], st.get("w", 12) / 2 + WMARG)) for st in M.get("town_streets", [])]  # type: ignore[no-redef]
        est_streets += [("alley", _near_line(al["pts"], al.get("w", 8) / 2 + WMARG)) for al in M.get("alleys", [])]
        est_streets += [("road", _near_line(rd["pts"], rd["w"] / 2 + WMARG)) for rd in M.get("roads", [])]
        if M.get("road"):
            est_streets.append(("road", _near_line(M["road"], M.get("road_width", 26) / 2 + WMARG)))
        if M.get("ring_road"):
            est_streets.append(("ring road", _near_line(M["ring_road"], M.get("ring_road_width", 7) / 2 + WMARG)))
        est_on_st = [(round(e["x"]), round(e["y"]), _wall_hits(e, est_streets)) for e in M["merchant_estates"]]
        est_on_st = [ew for ew in est_on_st if ew[2]]
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
    return _kept(
        locals(),
        (
            'WMARG',
            '_in_grown_rect',
            '_near_line',
            '_tower_conflict',
            '_wall_hits',
            '_wall_pts',
            'al',
            'cc',
            'dk',
            'e',
            'est_ftowers',
            'est_on_st',
            'est_streets',
            'est_waters',
            'est_wet',
            'ew',
            'pcx',
            'pcy',
            'prx',
            'pry',
            'pts',
            'rd',
            'rv',
            'st',
            't',
            'towered',
        ),
    )


# COMPOUND GATES AND WALLS TO SCALE (GM, 2026-07-19). The walled compounds (samurai country
# estates/manors, the governor's yamen, merchant estates, the mausoleum) draw only walls +
# gate + a deliberately BLANK court (the interior is its own Mode A diagram) - so the wall
# and gate ARE the feature, and they must be honest: a samurai residence gate (nagayamon /
# yakuimon) opens ~9-12 real ft (cart + palanquin), a grand yamen gatehouse up to ~24 ft;
# the old fixed-pixel gap (+-34px) drew a 204 ft opening at city scale - most of a wall
# missing. Walls (dobei/tsuijibei) run ~1.5-2 ft thick, drawn true-width-or-floored (the
# 2px cartographic floor = 6 ft at city scale; band top 8 allows it). A manifest that
# records no gate_w predates the to-scale engine and cannot prove its gates - regenerate.


# FUNERARY FEATURES TO SCALE (GM, 2026-07-19; anchors in settlements.md "Historical
# grounding"). The old glyphs were FIXED-PIXEL and silently tripled at city scale.


# FARMSTEADS ARE WITHIN REACH OF A WELL (town/city): the farm belt drinks daily too, and
# Rokugan's unusually well-run domains sink wells liberally (the same liberty behind the
# literal urban idobata count) - so no farmhouse stands more than 500 REAL FEET from a
# well (a ~2-minute bucket walk; a real farmstead would often have its own). Farmhouses
# within 150 real ft of the VIEW edge are exempt: their fields already run off-map, and
# their well is presumed just off the edge with the rest of their steading (GM rule,
# 2026-07-21). Villages are not gated here - their wells already sit among the houses
# (wells_among_dwellings). WHY: settlements.md wells entry.


# DRY-CROP PLOTS ARE TO SCALE: a hem parcel is a smallholder's strip (~1 mu / ~0.17 acre
# mean in Buck's surveys - the same grain the paddy plots and the polder parcels obey), so
# the map-wide MEAN dry-plot area must stay under 0.25 real acres. The tiling constants in
# _dry_fields (plot width 46px, row depth 36px) are real-feet quantities tuned at 2 ft/px:
# unscaled at the 3 ft/px city grain they doubled every parcel's area (0.34-0.38 acre
# means), dry cells visibly dwarfing the ~78 ft rice plots beside them - "set a number of
# pixels, not a number of feet" (the GM's exact catch, 2026-07-21). WHY: settlements.md.


# EVERY COMB PADDY FAN HAS A FIELD FLOOR so its canal-JUNCTION triangles (the head-race fork,
# the outfall corner where a supply canal dies at the drain, the confluence wedges) are not bare
# parchment - the "blank bits on the paddies" the GM circled across cities AND villages/hamlets
# (2026-07-22). The comb carve tessellates its plots but cannot fill those wedges; a base-fill
# polygon (s.comb_base_fill, recorded in M['comb_floors'][name]) draws under the plots so the
# gaps read as field ground, not a hole. Villages/hamlets that draw via draw_comb_field or inline
# both route through the helper now. Any paddy fan (a field with field_ditches, i.e. an irrigated
# comb) must therefore have a floor. paddy_fan_gapless's 2% tolerance let the small junctions slip;
# this pins the floor at every scale.


def _seg_0122__paddy_fan_has_floor(
    *, M: Any = _UNBOUND, _ditched: Any = _UNBOUND, _floors: Any = _UNBOUND, _pf_bad: Any = _UNBOUND, check: Any = _UNBOUND, d: Any = _UNBOUND, f: Any = _UNBOUND, scale: Any = _UNBOUND
) -> dict[str, Any]:
    """Gate segment 122 (paddy_fan_has_floor) - body verbatim from the legacy gate() (feature 022)."""
    if scale in ("hamlet", "village", "town", "city"):
        _floors = M.get("comb_floors", {})
        _ditched = {d.get("field") for d in M.get("field_ditches", [])}
        _pf_bad = [f.get("name") for f in M.get("fields", []) if f.get("kind") == "paddy" and f.get("name") in _ditched and f.get("name") not in _floors]
        check(
            "paddy_fan_has_floor",
            not _pf_bad,
            f"comb paddy fan(s) with no field floor: {_pf_bad} - the carve leaves bare parchment triangles at the "
            f"canal junctions (head-race fork, outfall corner, confluences); call s.comb_base_fill(net, name) "
            f"before drawing the plots so it draws a floor under them and records M['comb_floors'][name]",
        )
    return _kept(locals(), ('_ditched', '_floors', '_pf_bad', 'd', 'f'))


# A COMB'S HEAD GROUND IS QUILTED (city-scale): the supply canals run THROUGH cultivated
# land - paddy below, dry-crop hem above - never through bare parchment. The fan head (the
# band along the mains and the fork triangle between the arms) is uncommanded by gravity,
# so the carve correctly never plants RICE there; the HEM system is what fills it (villages
# add scrub besides, so they read full either way). paddy_fan_gapless deliberately samples
# only the commanded interior - which is exactly why the bare-head regression (the GM's
# circled screenshot, 2026-07-21) sailed through green. This check owns that band: sample
# both flanks of every recorded MAIN channel beyond the hem berm, skip the sluice mouth and
# moat/ring corridors, and require the map-wide bare fraction under 20% (calibrated: the
# pre-fix manifest reads ~25%, the quilted maps ~13-16%). Fields recording plot_polys (the
# city gens) are gated; a village opts in by recording them.


def _seg_0123___hq_ftpx(*, meta: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 123 (_hq_ftpx) - body verbatim from the legacy gate() (feature 022)."""
    _hq_ftpx = float(meta.get("ftpx", 1) or 1)
    return _kept(locals(), ('_hq_ftpx',))
