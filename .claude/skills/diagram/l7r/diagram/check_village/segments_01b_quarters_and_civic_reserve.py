"""Gate segments (quarters and civic reserve; keys 0038-0051) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from .common_03_capacity import (
    _UNBOUND,
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


# a MALFORMED manifest (a wall or quarter vertex millions of px off the map) must FAIL, not
# hang - the grid sweeps are bounded by sweep_hi so they cannot loop forever, and this flags
# the bad geometry so the validator reports it instead of silently sweeping garbage. A real
# settlement's features lie within one canvas-width of margin of the drawn canvas.


# TILING: sweep the wall-plus-quarters bbox once (so a quarter that spills OUTSIDE the
# wall is sampled too) - quarters must cover the interior (>=85%), not overlap (<=5%),
# and not spill outside the wall (<=3% of interior-equivalent cells).


# PER-QUARTER DENSITY + DEAD ZONE (residential + mixed quarters)


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
