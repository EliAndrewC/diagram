"""Gate segments (capital ways and burial; keys 0106_027-0123) - bodies verbatim, registry order preserved."""

from typing import Any

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
