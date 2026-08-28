"""Gate segments (town trades and theater; keys 0543_011-0543_057) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from .common_01_geometry import seg_closest
from .common_03_capacity import _UNBOUND, _kept

# WHY (farmers are the overwhelming majority caste): settlements.md "Historical grounding"


# MERCHANT and LABORER housing varies in SIZE by wealth, like a provincial city's (budgets.md
# Town wealth tiers): a MINORITY of merchants are very-rich / rich and live in large homes
# (~5 of ~24), and a few laborers are 'master/rich' (~2-3 of ~29); the rest live in small/standard
# dwellings. Require the larger homes (kind merchant_large / laborer_large) to be PRESENT and a
# CLEAR MINORITY - not that every house is one uniform size.


# MERCHANT RESIDENCES sit BEHIND the merchant BUSINESSES, and CLOSER to the road than the
# LABORER housing - a clean radial band: shops front the road, the merchant homes directly
# behind them, then a gap, then the laborers set further back. Scoped to road-fronted towns
# (those with a trunk M["road"], e.g. unwalled Hoshizora); a walled town's interior grid is laid
# out around cross-streets, not one radial axis, so this single-axis test does not apply there.
# droad = perpendicular distance from a building to the nearest road segment.


# a town has hundreds of farmers - we never show all the farmland, so at least
# one field must run off the map edge (implying more farmland beyond what's drawn)


# a rice-TRANSIT town (meta(granary=True)) shows a distinct tax-rice granary - a row of
# fireproof kura where grain gathered from many counties is forwarded up the kick-up
# chain. A standard county seat does NOT draw one: its grain sits inside the magistrate's
# yamen, implied by the manor. Opt-in, so the default is no check (unlike the gate
# market, theater stage, and monasteries, which are opt-OUT defaults).


# a noticeable MINORITY of merchant houses keep a fireproof storehouse (kura) for their
# (often absentee) landlords' rent-rice and bulk goods - more than a token 1-2, beyond a
# shop's ordinary inventory. Draw them with s.merchant_storehouses(...).


# a county seat is a market center: peasants from the far edge of its catchment stay
# over on market eve in a cheap communal flophouse (kichin-yado) where travelers arrive
# - the gate market of a walled town, the road of an unwalled one. Default-on (>= 1);
# meta(flophouses=N) requires more (a busy hub); meta(flophouses=0) opts out.


# a county town is a stop on the trade route: it needs ONE caravan INN (s.inn) with a STABLES
# (s.stables) next to it and OPEN GROUND beside the stables - a pasture for the wagon-train oxen
# and horses - exactly like a provincial city's gate caravan facilities, but a single one. The
# inn must sit ALONG the road (the Imperial road, or a town street) - the caravans pull up to it -
# NOT buried behind the shop rows. A WALLED town keeps it INSIDE the rampart (caravans enter the gate).


def _seg_0543_031__b_3(*, M: Any = _UNBOUND, b: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0543.031 (b, inns) - body verbatim from _seg_0543__town_farmers_plurality (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale == 'town':
        inns = [b for b in M.get("buildings", []) if b.get("kind") == "inn"]
    return _kept(locals(), ('b', 'inns'))


def _seg_0543_034__routes(*, M: Any = _UNBOUND, s: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0543.034 (routes, s) - body verbatim from _seg_0543__town_farmers_plurality (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale == 'town':
        routes = ([M["road"]] if M.get("road") else []) + [s["pts"] for s in M.get("town_streets", [])]
    return _kept(locals(), ('routes', 's'))


def _seg_0543_035__b_5(*, M: Any = _UNBOUND, b: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0543.035 (b, others) - body verbatim from _seg_0543__town_farmers_plurality (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale == 'town':
        others = [b for b in M.get("buildings", []) if b.get("kind") not in ("inn", "stables")]
    return _kept(locals(), ('b', 'others'))


# the inn FACES the road and lies PARALLEL to it - the caravans pull straight up to it - so its
# noren front (the +y edge after the inn's `rot`) must point at the nearest route point, which also
# makes its long frontage edge run along the road. A diagonal road needs a tilted inn.


def _seg_0543_040__unaligned(*, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0543.040 (unaligned) - body verbatim from _seg_0543__town_farmers_plurality (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale == 'town':
        unaligned = []  # type: ignore[var-annotated]
    return _kept(locals(), ('unaligned',))


def _seg_0543_041__bd(
    *,
    bd: Any = _UNBOUND,
    cx: Any = _UNBOUND,
    cy: Any = _UNBOUND,
    d: Any = _UNBOUND,
    dx: Any = _UNBOUND,
    dy: Any = _UNBOUND,
    fn: Any = _UNBOUND,
    inn: Any = _UNBOUND,
    inns: Any = _UNBOUND,
    ki: Any = _UNBOUND,
    npt: Any = _UNBOUND,
    r: Any = _UNBOUND,
    routes: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    th: Any = _UNBOUND,
    unaligned: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0543.041 (bd, cx, cy, d) - body verbatim from _seg_0543__town_farmers_plurality (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale == 'town':
        for inn in inns:
            npt, bd = None, 1e18
            for r in routes:
                for ki in range(len(r) - 1):
                    cx, cy = seg_closest(inn["x"], inn["y"], r[ki], r[ki + 1])
                    d = math.hypot(cx - inn["x"], cy - inn["y"])
                    if d < bd:
                        bd, npt = d, (cx, cy)
            if npt is None or bd < 1:
                continue
            dx, dy = (npt[0] - inn["x"]) / bd, (npt[1] - inn["y"]) / bd
            th = math.radians(inn.get("rot", 0))
            fn = (-math.sin(th), math.cos(th))  # the +y front's outward normal after rot
            if fn[0] * dx + fn[1] * dy < 0.88:  # within ~28deg of facing the nearest road point
                unaligned.append((round(inn["x"]), round(inn["y"])))
    return _kept(locals(), ('bd', 'cx', 'cy', 'd', 'dx', 'dy', 'fn', 'inn', 'ki', 'npt', 'r', 'th', 'unaligned'))


# every town has a THEATER STAGE unless meta(theater_stage=False); for a walled town
# it sits INSIDE the walls unless meta(theater_stage="outside")


def _seg_0543_043__ts_meta(*, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0543.043 (ts_meta) - body verbatim from _seg_0543__town_farmers_plurality (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale == 'town':
        ts_meta = meta.get("theater_stage", True)
    return _kept(locals(), ('ts_meta',))


def _seg_0543_044__amph_raw(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0543.044 (amph_raw) - body verbatim from _seg_0543__town_farmers_plurality (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale == 'town':
        amph_raw = M.get("theater_stage")
    return _kept(locals(), ('amph_raw',))


def _seg_0543_045__amph_all(*, amph_raw: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0543.045 (amph_all) - body verbatim from _seg_0543__town_farmers_plurality (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale == 'town':
        amph_all = amph_raw if isinstance(amph_raw, list) else ([amph_raw] if amph_raw else [])
    return _kept(locals(), ('amph_all',))


def _seg_0543_046__amph(*, a9: Any = _UNBOUND, amph_all: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0543.046 (amph) - body verbatim from _seg_0543__town_farmers_plurality (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale == 'town':
        amph = max(amph_all, key=lambda a9: a9.get("w", 0)) if amph_all else None
    return _kept(locals(), ('amph',))


def _seg_0543_048__theater_stage_inside_wall(
    *, M: Any = _UNBOUND, amph: Any = _UNBOUND, check: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND, ts_meta: Any = _UNBOUND, w: Any = _UNBOUND
) -> dict[str, Any]:
    """Gate segment 0543.048 (theater_stage_inside_wall) - body verbatim from _seg_0543__town_farmers_plurality (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale == 'town' and amph and meta.get("walled") and ts_meta != "outside":
        w = M.get("wall") or []
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
    return _kept(locals(), ('w',))


# a town's monasteries: by default 2, dedicated to the patron fortunes of the clan
# whose holdings include it (meta(clan=...)). Override with an explicit list -
# meta(monastery_fortunes=[...]) - for a town that changed hands, or a 1-monastery town.
