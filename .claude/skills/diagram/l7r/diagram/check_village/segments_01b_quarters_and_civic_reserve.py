"""Gate segments (quarters and civic reserve; keys 0038-0051) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from .common_01_geometry import (
    _struct_rect,
    largest_empty_gap,
    point_in_poly,
    poly_area,
    sweep_hi,
)
from .common_03_capacity import (
    _UNBOUND,
    DEAD_ZONE_MAX,
    DWELLING_KINDS,
    QUARTER_DENSITY_CEIL,
    QUARTER_DENSITY_FLOOR,
    _kept,
)


def _seg_0038__crop_not_held_open_by_one_feature(*, _lone: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 38 (crop_not_held_open_by_one_feature) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "crop_not_held_open_by_one_feature",
        not _lone,
        f"a single feature is holding the frame open: {_lone} - move it inward and the whole map crops tighter. "
        f"If it genuinely belongs out there (a rule forces it, or the far ground is the point), declare "
        f"meta(crop_outlier_ok=True) with the reason",
    )
    return _kept(locals(), ())


# population is DWELLINGS x ~5, NEVER total buildings: a town/city's shops, government
# offices, flophouses, kura and gate furniture house no one, so counting them as housing
# would inflate the population. Farmhouses + urban dwellings are the only residences.


# COMMONER DWELLINGS SHELTER INSIDE THE WALLS (feature 006). A walled city's ordinary
# population (laborers, artisans, servants, merchants) lived intramurally - the wall exists to
# protect them. Only four categories sat legitimately outside: samurai country estates,
# farmhouses, the riverside wharf suburb, and the gate/approach-road (guan-xiang) market shops.
# So ANY commoner DWELLING outside the wall is the anomaly (it defeats the wall and has no
# economic anchor); hard-zero. Samurai are exempt (their country seats are a legitimate
# extramural category); shops are businesses, not dwellings, so they are not in COMMONER_KINDS.


def _seg_0040_000__wall_p(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.000 (wall_p) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall'):
        wall_p = M["wall"]
    return _kept(locals(), ('wall_p',))


# THE WHARF SUBURB IS THE EXEMPTION THE MESSAGE ALWAYS PROMISED (021): a bank-quay city
# (the kashi form - Shiro Daika) keeps its landing OUTSIDE the wall, and the kashi's own
# brokers and warehouse folk live at the landing; a commoner dwelling within reach of the
# wharf works (a jetty, the quay granary rows) IS that suburb. Cities whose wharf is an
# in-wall dock basin (Minami, Nagahara) have no extramural commoners, so nothing changes
# for them. 300px =~ the drawn wharf suburb's own extent.


# measured to towpath SEGMENTS, not vertices (a 2-point towpath left its mid-run porters
# "outside" when the vertices were 350px apart - the point-vs-footprint trap, again)


# DECLARED QUARTERS + PER-QUARTER DENSITY (feature 006). A walled city is a set of zoned
# quarters tiling its interior; density is judged PER QUARTER (residential/mixed against a
# band + a dead-zone guard), civic quarters must actually hold civic ground, and reserve
# ground is capped. This is what a global aggregate could not see: a dense east + empty west
# averages to "fine" (measured: Tango and the broken Nagahara share the same block-density
# median; the difference is WHERE the empty ground sits).


def _seg_0040_007__quarters(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.007 (quarters) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall'):
        quarters = M.get("quarters", [])
    return _kept(locals(), ('quarters',))


# a MALFORMED manifest (a wall or quarter vertex millions of px off the map) must FAIL, not
# hang - the grid sweeps are bounded by sweep_hi so they cannot loop forever, and this flags
# the bad geometry so the validator reports it instead of silently sweeping garbage. A real
# settlement's features lie within one canvas-width of margin of the drawn canvas.


def _seg_0040_014__b(*, M: Any = _UNBOUND, b: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND, wall_p: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.014 (b, dwell_pts) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        dwell_pts = [(b["x"], b["y"]) for b in M.get("buildings", []) if b.get("kind") in DWELLING_KINDS and point_in_poly(b["x"], b["y"], wall_p)]
    return _kept(locals(), ('b', 'dwell_pts'))


def _seg_0040_015___yq(
    *,
    M: Any = _UNBOUND,
    _yq: Any = _UNBOUND,
    d9: Any = _UNBOUND,
    dwell_pts: Any = _UNBOUND,
    m9: Any = _UNBOUND,
    p9: Any = _UNBOUND,
    quarters: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    t9: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0040.015 (_yq, d9, dwell_pts, m9) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters and scale == "capital":
        # capital fabric counts its OTHER dwelling forms (021, same arithmetic as the
        # population check): yashiki-band manors are households, and a terrace range is
        # `units` households at one seat - without them the samurai quarters read empty
        # to the density rule while being fully built.
        _yq = [d9["poly"] for d9 in M.get("districts", []) if d9.get("rank_band") == "yashiki"]
        dwell_pts += [(m9["x"], m9["y"]) for m9 in M.get("manors", []) if any(point_in_poly(m9["x"], m9["y"], p9) for p9 in _yq)]
        for t9 in M.get("terraces", []):
            dwell_pts += [(t9["x"], t9["y"])] * int(t9.get("units", 0))
    return _kept(locals(), ('_yq', 'd9', 'dwell_pts', 'm9', 'p9', 't9'))


def _seg_0040_016___civic(*, M: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.016 (_civic) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        _civic = (
            M.get("ministries", [])
            + M.get("religious", [])
            + M.get("cemeteries", [])
            + M.get("mausoleums", [])
            + M.get("storehouses", [])
            + ([M["governor_mansion"]] if M.get("governor_mansion") else [])
        )
    return _kept(locals(), ('_civic',))


def _seg_0040_017__c(*, M: Any = _UNBOUND, _civic: Any = _UNBOUND, c: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.017 (c, civic_rects) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        civic_rects = [_struct_rect(c) for c in _civic if "w" in c]
    return _kept(locals(), ('c', 'civic_rects'))


# TILING: sweep the wall-plus-quarters bbox once (so a quarter that spills OUTSIDE the
# wall is sampled too) - quarters must cover the interior (>=85%), not overlap (<=5%),
# and not spill outside the wall (<=3% of interior-equivalent cells).


def _seg_0040_018__p(*, M: Any = _UNBOUND, p: Any = _UNBOUND, q: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND, v: Any = _UNBOUND, wall_p: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.018 (p, q, v, wxs) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        wxs = [p[0] for p in wall_p] + [v[0] for q in quarters for v in q["poly"]]
    return _kept(locals(), ('p', 'q', 'v', 'wxs'))


def _seg_0040_019__p_1(*, M: Any = _UNBOUND, p: Any = _UNBOUND, q: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND, v: Any = _UNBOUND, wall_p: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.019 (p, q, v, wys) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        wys = [p[1] for p in wall_p] + [v[1] for q in quarters for v in q["poly"]]
    return _kept(locals(), ('p', 'q', 'v', 'wys'))


def _seg_0040_020__interior_cells(*, M: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.020 (interior_cells, overlapped, spill_cells, uncovered) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        interior_cells = uncovered = overlapped = spill_cells = 0
    return _kept(locals(), ('interior_cells', 'overlapped', 'spill_cells', 'uncovered'))


def _seg_0040_021___hx(*, M: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND, wxs: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.021 (_hx) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        _hx = sweep_hi(min(wxs), max(wxs), 40)  # bounded so a malformed vertex cannot hang the sweep
    return _kept(locals(), ('_hx',))


def _seg_0040_022___hy(*, M: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND, wys: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.022 (_hy) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        _hy = sweep_hi(min(wys), max(wys), 40)
    return _kept(locals(), ('_hy',))


def _seg_0040_023__gx(*, M: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND, wxs: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.023 (gx) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        gx = min(wxs)
    return _kept(locals(), ('gx',))


def _seg_0040_024__gx_1(
    *,
    M: Any = _UNBOUND,
    _hx: Any = _UNBOUND,
    _hy: Any = _UNBOUND,
    gx: Any = _UNBOUND,
    gy: Any = _UNBOUND,
    interior_cells: Any = _UNBOUND,
    n_in: Any = _UNBOUND,
    overlapped: Any = _UNBOUND,
    q: Any = _UNBOUND,
    quarters: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    spill_cells: Any = _UNBOUND,
    uncovered: Any = _UNBOUND,
    wall_p: Any = _UNBOUND,
    wys: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0040.024 (gx, gy, interior_cells, n_in) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        while gx <= _hx:
            gy = min(wys)
            while gy <= _hy:
                n_in = sum(1 for q in quarters if point_in_poly(gx, gy, q["poly"]))
                if point_in_poly(gx, gy, wall_p):
                    interior_cells += 1
                    if n_in == 0:
                        uncovered += 1
                    elif n_in > 1:
                        overlapped += 1
                elif n_in >= 1:
                    spill_cells += 1
                gy += 40
            gx += 40
    return _kept(locals(), ('gx', 'gy', 'interior_cells', 'n_in', 'overlapped', 'q', 'spill_cells', 'uncovered'))


# PER-QUARTER DENSITY + DEAD ZONE (residential + mixed quarters)


def _seg_0040_028__thin_q(*, M: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.028 (thin_q) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        thin_q = []  # type: ignore[var-annotated]
    return _kept(locals(), ('thin_q',))


def _seg_0040_029__civic_in_q(
    *,
    M: Any = _UNBOUND,
    civic_in_q: Any = _UNBOUND,
    civic_rects: Any = _UNBOUND,
    dens: Any = _UNBOUND,
    dwell_pts: Any = _UNBOUND,
    eff_area: Any = _UNBOUND,
    nm: Any = _UNBOUND,
    p: Any = _UNBOUND,
    q: Any = _UNBOUND,
    qarea: Any = _UNBOUND,
    qd: Any = _UNBOUND,
    qpoly: Any = _UNBOUND,
    quarters: Any = _UNBOUND,
    r: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    thin_q: Any = _UNBOUND,
    w: Any = _UNBOUND,
    x: Any = _UNBOUND,
    y: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0040.029 (civic_in_q, dens, eff_area, nm) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        for q in quarters:
            if q.get("zone") not in ("residential", "mixed"):
                continue
            qpoly = q["poly"]
            qarea = poly_area(qpoly)
            if qarea <= 0:
                continue
            qd = [(x, y) for x, y in dwell_pts if point_in_poly(x, y, qpoly)]
            # density is measured over HOUSING-AVAILABLE ground: subtract any civic compound
            # footprint sitting in the quarter (a government ward or a temple in a merchant
            # district eats area that was never going to be housing), so a mixed quarter is not
            # wrongly flagged under-built for the ground its compounds occupy.
            civic_in_q = sum(r["w"] * r["h"] for r in civic_rects if point_in_poly(r["x"], r["y"], qpoly))
            eff_area = max(qarea - civic_in_q, 1.0)
            dens = len(qd) / eff_area
            nm = q.get("name") or f"quarter@({round(sum(p[0] for p in qpoly) / len(qpoly))},{round(sum(p[1] for p in qpoly) / len(qpoly))})"
            if dens < QUARTER_DENSITY_FLOOR:
                thin_q.append((nm, f"{len(qd)} dwellings, density {dens * 1000:.2f}/1000px^2 < floor {QUARTER_DENSITY_FLOOR * 1000:.2f} (under-built)"))
            elif dens > QUARTER_DENSITY_CEIL:
                thin_q.append((nm, f"density {dens * 1000:.2f}/1000px^2 > ceil {QUARTER_DENSITY_CEIL * 1000:.2f} (implausibly crammed)"))
            elif (
                q.get("zone") == "residential"
                and largest_empty_gap(
                    qpoly, qd + [(w["x"], w["y"]) for w in M.get("wells", []) if point_in_poly(w["x"], w["y"], qpoly)], occupied=[r for r in civic_rects if point_in_poly(r["x"], r["y"], qpoly)]
                )
                > DEAD_ZONE_MAX
            ):
                # the dead-zone guard applies to PURE residential quarters (uniform housing, no
                # empty blocks); a MIXED quarter legitimately holds a civic forecourt/plaza, so it
                # is judged on the density AVERAGE only. An all-empty region declared to dodge this
                # still fails: as residential it fires here, as civic it fires city_civic_quarter,
                # as mixed its average density is too low.
                thin_q.append((nm, f"dead zone: an empty pocket wider than a firebreak ({DEAD_ZONE_MAX:.0f}px) inside a residential quarter"))
    return _kept(locals(), ('civic_in_q', 'dens', 'eff_area', 'nm', 'p', 'q', 'qarea', 'qd', 'qpoly', 'r', 'thin_q', 'w', 'x', 'y'))


# CIVIC quarters must actually hold civic ground (not be emptiness labeled civic)


# RESERVE ground capped


# IS THE WALL THE RIGHT SIZE FOR THE POPULATION? A space-budget analysis, so "the wall is
# too big / too small" becomes a first-class, automated judgment instead of trial and error.
# city_capacity() grid-samples the interior, subtracts the fixed overhead (government, temples,
# wharf, gates, water, trunk roads + ring road + berm, committed fields), and asks whether the
# residential-capable ground - at a well-packed quarter's canonical density - can hold the
# target. TOO_SMALL / TOO_BIG are WALL faults (resize by the suggested scale); UNDERPACKED means
# the wall is right but the placement is sparse (densify - population_consistent catches that
# separately). See settlements.md "Sizing the wall to the population".
# ...CITY ONLY: a capital's wall is an OUTPUT of plan_capital (capital_wall_matches_budget +
# capital_interior_slack_in_band judge it against the declared program, castle included), and
# this generic capacity model does not know a castle takes ~40% of the interior - it reads the
# keep's ground as residential-capable and demands the wall shrink (GM 2026-08-10).


# THE WALL MATCHES THE DECLARED SPACE BUDGET (feature 009). Budget-first is the city
# workflow: the gen computes citybudget.plan_city(...) BEFORE drawing anything, takes the
# wall from budget.wall, and records the promise at meta.budget - this check holds the
# drawn map to it. Enclosing MORE ground than the budget justifies is the empty-space
# defect (the pre-feature Nagahara read fully green while ~17% of its interior was
# unaccounted open ground); enclosing less starves the program. Open ground is credited
# only as itemized budget lines (reserve/agri/extras) - never as ambient slack.
# every gate STABLES carries its drawn beaten-earth YARD (GM 2026-07-22): the open ground around a gate
# stables is deliberate (a wagon-train marshalling yard - carts parked, oxen unyoked and tethered at
# rails, teamsters waiting), but left as blank parchment it read as forgotten emptiness. s._stable_yard
# fills it with a feathered scatter (scuff, straw, hitching rails, trough, dung
# heaps); this gates that no stables reverts to a blank yard. Each yard links to its stables via `of`.


# STABLE-YARD TROUGHS SIT BESIDE A WELL (GM 2026-07-23: "so that the water doesn't need to be
# carried a considerable distance"). The watering point works by RELAY at a fixed draw-point -
# a wagon-train drinks 300-600 gal in a session, poured by bucket straight from the wellhead
# into the troughs (settlements.md 'Stable yard' watering) - so the cluster must hug a
# wellhead: placement offsets it by the wellhead edge + half a trough + a step (~24 real ft
# center-to-center at city scale); 40 real ft is that worst case + slack, and any genuine
# carry (the pre-fix Nagahara yards sat 100/241 ft out) blows far past it. A yard with no
# well in reach digs its OWN courtyard well (the caravanserai / yizhan post-yard form), so
# "no well nearby" is never a valid layout; a yard whose trough cluster went unrecorded
# (troughs > 0 without troughs_at) fails too - the anchor is part of the contract. Not
# scale-gated: wherever a stable yard records troughs, its water is drawn at a well.


def _seg_0043___tr_ftpx(*, meta: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 43 (_tr_ftpx) - body verbatim from the legacy gate() (feature 022)."""
    _tr_ftpx = float(meta.get("ftpx") or 3.0)
    return _kept(locals(), ('_tr_ftpx',))


def _seg_0044___tr_wells(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 44 (_tr_wells) - body verbatim from the legacy gate() (feature 022)."""
    _tr_wells = M.get("wells", [])
    return _kept(locals(), ('_tr_wells',))


def _seg_0045___tr_far() -> dict[str, Any]:
    """Gate segment 45 (_tr_far) - body verbatim from the legacy gate() (feature 022)."""
    _tr_far = []  # type: ignore[var-annotated]
    return _kept(locals(), ('_tr_far',))


def _seg_0046___tr_at(
    *, M: Any = _UNBOUND, _tr_at: Any = _UNBOUND, _tr_far: Any = _UNBOUND, _tr_ftpx: Any = _UNBOUND, _tr_wells: Any = _UNBOUND, _tr_yd: Any = _UNBOUND, w: Any = _UNBOUND
) -> dict[str, Any]:
    """Gate segment 46 (_tr_at, _tr_far, _tr_yd, w) - body verbatim from the legacy gate() (feature 022)."""
    for _tr_yd in M.get("stable_yards", []):
        if not _tr_yd.get("troughs"):
            continue
        _tr_at = _tr_yd.get("troughs_at")
        if not _tr_at or not _tr_wells or min(math.hypot(w["x"] - _tr_at[0], w["y"] - _tr_at[1]) for w in _tr_wells) > 40.0 / _tr_ftpx:
            _tr_far.append((round(_tr_yd["x"]), round(_tr_yd["y"])))
    return _kept(locals(), ('_tr_at', '_tr_far', '_tr_yd', 'w'))


# THE FARRIER'S FORGE STANDS BESIDE A STABLES, AND KEEPS ITS FIRE GAP (GM 2026-07-25, the
# iron-horseshoe decision; full grounding in settlements.md "TRADE WORKS" -> FARRIERY). Rokugan
# shoes horses in IRON where Edo Japan used woven straw, but that changes an ordinary smith's
# REPERTOIRE, not his premises - a town kaji-ya still fits the generic shop glyph. A drawn
# farrier is therefore only correct where horses CONCENTRATE, which in map terms is the
# caravan/relay stable yard: a shoeing forge on a random street corner is the European
# coaching-inn image the trade research warned about, not a Rokugani seat. And it must NOT abut
# the stall range - an open forge against hay and timber is the fire a yard does not survive,
# so real yards kept the smithy across the ground. The gap anchor is buildings.md's ~6-8 ft
# wooden-service fire gap; the measure runs from the WHOLE recorded footprint (shed + apron),
# which is deliberately conservative, since the shed sits at the apron's far end.
