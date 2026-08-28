"""Gate segments (city labels and works; keys 0563_252-0563_308) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from .common_01_geometry import point_in_poly
from .common_03_capacity import _UNBOUND, _kept

# internal streets must not run THROUGH the civic compounds (ministries, governor, temples,
# gate furniture) any more than they may through ordinary buildings


# ZONE / NEIGHBORHOOD labels must sit WITH the cluster they name: ENTIRELY on the same side
# of the city wall as that cluster, AMONG its buildings, and not floating over a foreign field.
# A label over the moat, a neighboring compound, or a paddy misleads the reader about what it
# names (the "laborer neighborhoods" label drifted outside the wall, "samurai neighborhood"
# sat over a ministry, "burakumin neighborhood" sat over a field).


def _seg_0563_255__subject_of(
    *,
    M: Any = _UNBOUND,
    b: Any = _UNBOUND,
    c: Any = _UNBOUND,
    f: Any = _UNBOUND,
    fields: Any = _UNBOUND,
    inwall: Any = _UNBOUND,
    key: Any = _UNBOUND,
    m: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    r: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    t: Any = _UNBOUND,
    txt: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 563.255 (subject_of) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):

        def subject_of(txt: str) -> tuple[list[tuple[float, float]], float, bool]:
            t = txt.lower()
            if "estate" in t:
                return [(m["x"], m["y"]) for m in M.get("manors", [])], 230, True
            if "agricultur" in t:  # the in-wall agricultural district, NOT the extramural farmland
                return [c for c in (((f["bbox"][0] + f["bbox"][2]) / 2, (f["bbox"][1] + f["bbox"][3]) / 2) for f in fields) if inwall(*c)], 260, True
            if "temple" in t:
                return [(r["x"], r["y"]) for r in M.get("religious", [])], 230, True
            for key, kinds in (
                ("samurai", {"samurai", "samurai_large"}),
                ("laborer", {"laborer", "laborer_large"}),
                ("burakumin", {"burakumin"}),
                ("merchant", {"merchant", "merchant_house", "merchant_large"}),
            ):
                if key in t:
                    return [(b["x"], b["y"]) for b in M.get("buildings", []) if b.get("kind") in kinds], 130, False
            return [], 0, True

    return _kept(locals(), ('subject_of',))


def _seg_0563_256__bad_lab(*, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.256 (bad_lab) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        bad_lab = []  # type: ignore[var-annotated]
    return _kept(locals(), ('bad_lab',))


def _seg_0563_257___z(
    *,
    M: Any = _UNBOUND,
    area_subj: Any = _UNBOUND,
    bad_lab: Any = _UNBOUND,
    cx: Any = _UNBOUND,
    cy: Any = _UNBOUND,
    f: Any = _UNBOUND,
    fields: Any = _UNBOUND,
    inwall: Any = _UNBOUND,
    lab: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    pts: Any = _UNBOUND,
    px: Any = _UNBOUND,
    py: Any = _UNBOUND,
    reach: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    subj_in: Any = _UNBOUND,
    subject_of: Any = _UNBOUND,
    txt: Any = _UNBOUND,
    x0: Any = _UNBOUND,
    x1: Any = _UNBOUND,
    y0: Any = _UNBOUND,
    y1: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 563.257 (_z, area_subj, bad_lab, cx) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        for lab in M.get("labels", []):
            if len(lab) <= 5 or not (lab[5].lower().endswith(("neighborhood", "neighborhoods", "district")) or "estates" in lab[5].lower()):
                continue
            x0, y0, x1, y1, _z, txt = lab[:6]
            pts, reach, area_subj = subject_of(txt)
            if not pts:
                continue  # nothing of that kind drawn - can't verify
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            subj_in = sum(1 for px, py in pts if inwall(px, py)) * 2 >= len(pts)
            if not all(inwall(px, py) == subj_in for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))):
                bad_lab.append(f"{txt!r} not entirely {'inside' if subj_in else 'outside'} the wall (its cluster is)")
            elif min(math.hypot(px - cx, py - cy) for px, py in pts) > reach:
                bad_lab.append(f"{txt!r} sits >{reach}px from any of its buildings - place it among them")
            elif not area_subj and any(point_in_poly(cx, cy, f["outline"]) for f in fields):
                bad_lab.append(f"{txt!r} floats over a farm field, not its own houses")
    return _kept(locals(), ('_z', 'area_subj', 'bad_lab', 'cx', 'cy', 'f', 'lab', 'pts', 'px', 'py', 'reach', 'subj_in', 'txt', 'x0', 'x1', 'y0', 'y1'))


# the surrounding farmland: every OUTSIDE field (even off-edge) has farmhouses, and the
# fields sit close to the city (cities grow up around fertile land)


# a MOATED city irrigates several large fields from the moat


# a gate market (guan-xiang) OUTSIDE EVERY MAIN-ROAD gate (GM decision 2026-07-22,
# flophouse-research.md): the extramural gate-suburb formed along the road at each
# trafficked gate - Beijing's gates all carried one, varying in scale (大关厢 vs small).
# `M["gates"]` holds only the MAIN (road/river-route) gates, so iterating it IS "every
# main-road gate": a purely military SALLY gate opens onto empty field with no traffic
# and carries no market, so it is NOT recorded in `gates` (it would live in its own
# structure if/when the sally-gate knob is added). Mirrors city_flophouse_outside_each_gate.
# FLOOR RAISED 3 -> 6 (GM 2026-07-24): the researched guan-xiang ran 10-40 structures
# per trafficked gate (Beijing's 大关厢 the high end); our belt is a SLICE like the
# samurai estates and the farmland - the drawn shops string along the approach road and
# the outermost may be CUT by the frame, the truncation itself saying "more beyond the
# map". >= 6 shown per gate keeps the slice reading like a suburb instead of a shed row.


# TRADE WORKS (GM 2026-07-24; settlements.md "TRADE WORKS" - the trades whose premises
# outgrow the generic shop glyph are first-class features; the long tail of trades,
# including the ordinary SMITH, stays in the shop rows - Rokugan DOES shoe horses in
# iron, but that changes his repertoire, not his footprint, so only a horse
# CONCENTRATION earns a drawn farrier). Every provincial city keeps: >= 1 BREWERY
# in-wall (the town's
# largest commercial building; sake/miso/soy; draws its own well); >= 1 DYE WORKS
# whose drying/rinsing yard sits ON WATER (a stream/channel/canal, the pond, or the
# moat - dyers need vat-fill and rinsing water, NOT bulk water transport, so a
# landlocked city keeps dyers too, per the GM); >= 1 OIL PRESS; >= 1 PAWNSHOP (a
# shopfront with a walled kura court); >= 1 BATHHOUSE (China-first: commercial baths
# attested from the Song). A KILN stands strictly OUTSIDE the walls (fire law +
# smoke); a RIVER-PORT city (meta river_port) also keeps >= 1 LUMBER YARD on the
# bank - timber moves by water at scale, so a landlocked city has none.


# BATHHOUSE COUNT FOLLOWS THE GM FORMULA (2026-07-24, second refinement): ONE per
# full 2,000 population + a remainder-fraction chance of one extra (2,500 -> 1 + 25%,
# 3,000 -> 1 + 50%, 4,000 -> exactly 2; floored at 1) - Edo's own peak ratio was ~1
# per ~2,100 residents (1808: 523 sento for ~1.1M), which is where the 2,000 divisor
# comes from. A recorded roll (meta bathhouse_roll, s.bathhouses) must also match the
# drawn count, so a stale hand count cannot ship.


# ... AND A LUMBER YARD NEVER OVERLAPS THE WATER (GM 2026-07-24, second pass): the
# yard ABUTS the bank - stock arrives by water - but stacked timber stands on DRY
# ground (logs in the current float away; the landing is the jetty's job). The
# generic no_structure_on_stream check cannot see this defect: it tests a fixed ~6px
# half-width tuned for village brooks, and Nagahara's 40px river swallowed a yard
# corner without tripping it (the pinned real fixture). Tested here against every
# watercourse's REAL half-width (streams/channels/canals + the moat via _tw_water),
# sampling the yard rect's corners, edge midpoints, and center (records are axis-
# aligned; rot stays 0 in s.lumber_yard).


# market-day lodging: a flophouse INSIDE the walls, and one OUTSIDE each gate (for
# travelers arriving from either direction, who reach the gate after it has shut)


# a flophouse is a humble doss-house (a sen a night, on straw): inside the walls it belongs
# in a HUMBLE quarter (the laborer section, or Tango's agrarian sector), NEVER cheek-by-jowl
# with the nicer neighborhoods (temples, merchants, samurai), and never in or up against the
# burakumin quarter. Only the in-wall flophouse is judged (the gate ones sit by the gate market).


def _seg_0563_297__b_17(*, M: Any = _UNBOUND, b: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.297 (b, inns) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        inns = [b for b in M.get("buildings", []) if b.get("kind") == "inn"]
    return _kept(locals(), ('b', 'inns'))


# a flop within reach of a GATE is the caravan flop - it serves the wagon crews
# at the gate quarter wherever that quarter's caste sits (021: the capital's bands
# abut its gates); the humble-quarter rule governs the market doss-houses only


# a flop within reach of a GATE is the caravan flop even if its inn/stables pair sits
# slightly past 170px - it serves the wagon crews at the gate quarter wherever that
# quarter's caste sits (021: the capital's bands abut its gates); the humble-quarter
# rule governs the market doss-houses only. (Filter AFTER the loop that fills bad_flop;
# the first version ran it against the empty list and was dead code, 2026-08-10.)


# CARAVAN facilities: just INSIDE each gate a wagon-train needs a prominent INN and a large
# STABLES (dozens of draft animals + crew) close to its flophouse, with OPEN GROUND around the
# stables for the animals to be tied up / penned. Three buildings near each gate, not just one.


# PADDY-FIRST estate doctrine (GM 2026-07-23, superseding the old >=2 floor): the rice
# paddies claim the near ring FIRST, and the samurai country estates take only what is
# left - most estates sit farther out in the rural district, so a city map showing just
# ONE estate (even a fraction running off the frame edge) is the more historically
# accurate signal; the rest are implied off-map. At least one must still show.
