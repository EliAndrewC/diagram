"""Gate segments (justice grounds and land fall; keys 0555_000-0561) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from .common_01_geometry import point_in_poly
from .common_03_capacity import _UNBOUND, _kept, empty_street_runs


def _seg_0556__walled_town_has_wall(
    *,
    EMPTY_RUN: Any = _UNBOUND,
    M: Any = _UNBOUND,
    MAXGAP: Any = _UNBOUND,
    STEP: Any = _UNBOUND,
    a8: Any = _UNBOUND,
    amph_all2: Any = _UNBOUND,
    amph_raw2: Any = _UNBOUND,
    ax: Any = _UNBOUND,
    ay: Any = _UNBOUND,
    b: Any = _UNBOUND,
    bx: Any = _UNBOUND,
    by: Any = _UNBOUND,
    check: Any = _UNBOUND,
    cov: Any = _UNBOUND,
    d: Any = _UNBOUND,
    empty: Any = _UNBOUND,
    ff: Any = _UNBOUND,
    gate: Any = _UNBOUND,
    gate_t: Any = _UNBOUND,
    has_main: Any = _UNBOUND,
    hill: Any = _UNBOUND,
    houses: Any = _UNBOUND,
    hx: Any = _UNBOUND,
    hy: Any = _UNBOUND,
    i: Any = _UNBOUND,
    j: Any = _UNBOUND,
    k: Any = _UNBOUND,
    ki: Any = _UNBOUND,
    lens: Any = _UNBOUND,
    ln: Any = _UNBOUND,
    mains: Any = _UNBOUND,
    mean: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    mn: Any = _UNBOUND,
    occ: Any = _UNBOUND,
    occ_dist: Any = _UNBOUND,
    out_ls: Any = _UNBOUND,
    out_mm: Any = _UNBOUND,
    outside_biz: Any = _UNBOUND,
    ox: Any = _UNBOUND,
    oy: Any = _UNBOUND,
    p: Any = _UNBOUND,
    r: Any = _UNBOUND,
    run: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    st: Any = _UNBOUND,
    t: Any = _UNBOUND,
    w: Any = _UNBOUND,
    wallp_t: Any = _UNBOUND,
    worst: Any = _UNBOUND,
    x: Any = _UNBOUND,
    y: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 556 (streets_have_buildings, wall_hugs_the_town, wall_sections_irregular, walled_town_commoners_inside_walls, walled_town_has_gate_market, walled_town_has_main_street, walled_town_has_wall) - body verbatim from the legacy gate() (feature 022)."""
    if scale == "town" and meta.get("walled"):
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
        # COMMONERS SHELTER INSIDE THE RAMPART - the jokamachi doctrine every walled-town docstring
        # states, previously enforced by nothing (GM audit 2026-07; the town analog of
        # city_commoner_dwellings_inside_walls). Town exemptions differ from the city's: the
        # BURAKUMIN quarter is doctrinally OUTSIDE (segregated), and the guan-xiang gate market
        # keeps its merchant houses by the gate - so laborers/servants outside are hard-zero, and
        # a merchant dwelling outside must stand within ~260px of the gate.
        wallp_t = M.get("wall")
        gate_t = M.get("gate")
        if wallp_t and len(wallp_t) >= 3:
            out_ls = [(round(b["x"]), round(b["y"])) for b in M.get("buildings", []) if b.get("kind") in ("laborer", "laborer_large", "servant") and not point_in_poly(b["x"], b["y"], wallp_t)]
            out_mm = [
                (round(b["x"]), round(b["y"]))
                for b in M.get("buildings", [])
                if b.get("kind") in ("merchant", "merchant_house", "merchant_large")
                and not point_in_poly(b["x"], b["y"], wallp_t)
                and (not gate_t or math.hypot(b["x"] - gate_t[0], b["y"] - gate_t[1]) > 260)
            ]
            pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes

        w = M.get("wall") or []
        if len(w) >= 3:
            lens = [math.hypot(w[i + 1][0] - w[i][0], w[i + 1][1] - w[i][1]) for i in range(len(w) - 1)]
            # "irregular" = not a regular polygon: high spread in section lengths. A
            # coefficient of variation (stdev/mean) test, unlike a pairwise-equal test,
            # allows a wall to hug a feature with several short segments (the chrysanthemum
            # field) while still failing a lazy near-equal-sided wall.
            mean = sum(lens) / len(lens)
            cov = (sum((ln - mean) ** 2 for ln in lens) / len(lens)) ** 0.5 / mean if mean else 0
            pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
        # the gate-to-yamen axis: a main street must run inward from the gate
        gate: Any = M.get("gate")  # type: ignore[no-redef]
        mains = [st for st in M.get("town_streets", []) if st.get("main")]
        has_main = bool(gate) and any(min(math.hypot(p[0] - gate[0], p[1] - gate[1]) for p in st["pts"]) < 75 for st in mains)
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes

        # no "street to nowhere": a street exists to give access to the buildings along it,
        # and is paved/worn by the traffic to and from them - so no long INSIDE-the-walls
        # stretch may be empty of buildings. (Buildings off any street are fine; that's the
        # poor who can't afford street frontage.) The map edge / off-wall approach is exempt.
        empty = empty_street_runs(M, w)
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes

        # a wall is expensive: it should HUG the built-up town, not enclose large empty
        # margins. Terrain can justify some slack (a wall climbs/skirts a hill rather than
        # leveling it), so the hill counts as filled "occupancy". Flag a long contiguous
        # stretch of wall whose inside is empty of any building, feature, or terrain - that
        # length of wall would not have been built; a tighter line costs less.
        if len(w) >= 3:
            occ = [(b["x"], b["y"]) for b in M.get("buildings", []) + houses if point_in_poly(b["x"], b["y"], w)]
            for ff in M.get("flower_fields", []):
                occ += [(p[0], p[1]) for p in ff["outline"][::3]]
            occ += [(r["x"], r["y"]) for r in M.get("religious", [])] + [(mn["x"], mn["y"]) for mn in M.get("manors", [])]
            amph_raw2 = M.get("theater_stage")
            amph_all2 = amph_raw2 if isinstance(amph_raw2, list) else ([amph_raw2] if amph_raw2 else [])
            occ += [(a8["x"], a8["y"]) for a8 in amph_all2]
            hill = M.get("hill")

            def occ_dist(x: float, y: float) -> float:
                d = min((math.hypot(ox - x, oy - y) for ox, oy in occ), default=1e9)
                if hill:
                    hx, hy, hrx, hry = hill
                    if ((x - hx) / hrx) ** 2 + ((y - hy) / hry) ** 2 <= 1.0:
                        return 0.0  # on the hill - terrain occupancy
                    d = min(d, min(math.hypot(hx + math.cos(math.tau * k / 48) * hrx - x, hy + math.sin(math.tau * k / 48) * hry - y) for k in range(48)))
                return d

            MAXGAP, EMPTY_RUN, STEP = 140, 280, 25
            run = worst = 0
            for ki in range(len(w) - 1):
                (ax, ay), (bx, by) = w[ki], w[ki + 1]
                for j in range(max(1, int(math.hypot(bx - ax, by - ay) // STEP))):
                    t = j / max(1, int(math.hypot(bx - ax, by - ay) // STEP))
                    if occ_dist(ax + (bx - ax) * t, ay + (by - ay) * t) > MAXGAP:
                        run += STEP
                        worst = max(worst, run)
                    else:
                        run = 0
            pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes

        # (RETIRED 2026-07-24: monastery_torii_scale_with_space - "roomy approach OWES the seven,
        # cramped corner keeps 1-2" - is superseded by the per-temple seeded ROLL, and it predated
        # the 1/3/7 TORII_WEIGHTS table besides (it still banned a count of 3, which the table
        # rolls at 60% for towns). Avenue completeness is now defined by the roll: shrine_hall
        # rolls each hall on the tier column, records the target, and torii_match_roll +
        # torii_count_canonical carry the teeth. Same precedent as torii_full_avenue_is_seven and
        # city_temple_torii_fill_approach.)

        # a walled town almost always accretes a small extramural MARKET (a Chinese guan-xiang)
        # just outside its gate. The WHY is traffic, not taxes (GM 2026-07-24, correcting the
        # rationale ported from the city tier): towns levy NO import tariffs (budgets.md puts
        # the whole tariff apparatus at provincial-city and capital gates only), and the county
        # magistrate governs the WHOLE county, so standing outside the gate crosses no tax or
        # regulatory line. The honest drivers are through-road travelers buying services without
        # detouring inside, the market-day chokepoint where the rural catchment trades, and late
        # arrivals at a gate shut for the night - so the market scales with GATE TRAFFIC, not
        # town population: typically ~4-8 permanent premises (floor >= 3), the small end of the
        # researched 10-40-per-trafficked-CITY-gate band. WHY: settlements.md "gate market" +
        # flophouse-research.md. Opt out with meta(gate_market=False) (a purely military fort,
        # or a depopulated / suppressed gate).
        if meta.get("gate_market", True):
            gate = M.get("gate")
            if gate and len(w) >= 3:
                outside_biz = [
                    b for b in M.get("buildings", []) if b.get("kind") in ("shop", "merchant") and not point_in_poly(b["x"], b["y"], w) and math.hypot(b["x"] - gate[0], b["y"] - gate[1]) <= 420
                ]
                pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
    return _kept(
        locals(),
        (
            'EMPTY_RUN',
            'MAXGAP',
            'STEP',
            'a8',
            'amph_all2',
            'amph_raw2',
            'ax',
            'ay',
            'b',
            'bx',
            'by',
            'cov',
            'empty',
            'ff',
            'gate',
            'gate_t',
            'has_main',
            'hill',
            'i',
            'j',
            'ki',
            'lens',
            'ln',
            'mains',
            'mean',
            'mn',
            'occ',
            'occ_dist',
            'out_ls',
            'out_mm',
            'outside_biz',
            'p',
            'r',
            'run',
            'st',
            't',
            'w',
            'wallp_t',
            'worst',
        ),
    )


# A MAP MUST DECLARE ITS LAND FALL (GM 2026-07-25). This closes the hole that let the whole
# problem happen: the drainage-slope block, `downhill_direction_valid` and `marsh_on_low_ground`
# are ALL gated on a fall being declared, and the code's own comment said "maps without the tag
# are exempt (slope unknown)" - so the two provincial cities, which declared none, silently
# skipped every one of those checks for months and nobody could tell from a green gate. Exempt
# is exactly what a map must not be. Either form counts: a map-level `meta(down_deg)`, or a
# per-field fall on every paddy (which is what a settlement ringed by farmland needs, since its
# fans drain several ways at once and no single bearing describes them).


def _seg_0557___lf_paddies(*, M: Any = _UNBOUND, f: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 557 (_lf_paddies, f) - body verbatim from the legacy gate() (feature 022)."""
    _lf_paddies = [f for f in M.get("fields") or [] if f.get("kind") == "paddy"]
    return _kept(locals(), ('_lf_paddies', 'f'))


def _seg_0558__settlement_declares_a_land_fall(
    *, M: Any = _UNBOUND, _lf_missing: Any = _UNBOUND, _lf_paddies: Any = _UNBOUND, check: Any = _UNBOUND, f: Any = _UNBOUND, meta: Any = _UNBOUND
) -> dict[str, Any]:
    """Gate segment 558 (settlement_declares_a_land_fall) - body verbatim from the legacy gate() (feature 022)."""
    if _lf_paddies or M.get("field_ditches"):
        _lf_missing = [f.get("name") for f in _lf_paddies if f.get("down_deg") is None]
        check(
            "settlement_declares_a_land_fall",
            meta.get("down_deg") is not None or (bool(_lf_paddies) and not _lf_missing),
            f"no land fall declared - give the map a meta(down_deg=...) or a per-field fall on every paddy "
            f"(paddies without one: {_lf_missing}). Every drainage-slope rule is gated on this, so a map that "
            f"declares nothing SKIPS them all and still shows a green gate - which is how both provincial "
            f"cities went unvalidated. Water flow (meta water_flow) is a separate declaration and does not substitute",
        )
    return _kept(locals(), ('_lf_missing', 'f'))


# WATER FLOW DIRECTION (GM 2026-07-24; the "why" lives in settlements.md "WATER FLOW").
# Every map declares a DRAINAGE BEARING - where this landscape sends its water - and every
# watercourse declares which way it runs. Before this, direction lived only in gen docstrings,
# so no check could read it and "downstream" was unverifiable; the tannery work is what
# exposed the gap. Angles use the same convention as down_deg (0 = east, 90 = south).
