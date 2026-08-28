"""Town, city and capital segments moved out of `segments_02a_capital_budget_and_ministries.py` by feature 145.

The GM ruled on 2026-08-28 that the hamlet path owes 100% coverage and the other tiers owe none while
nothing exercises them - and the floor is MODULE level, so a city segment sharing a file with a hamlet
segment put its whole body under the hamlet floor. Execution order is by the segment's numeric key
(`registry._ordered_names`), never by file, so moving one costs nothing and needs no placement row."""

import math
from typing import Any

from l7r.diagram.settlement import KIDO_TOWER_KEEPCLEAR, WALL_DEFENSE

from .common_01_geometry import _struct_rect, point_in_poly, rect_corners, seg_dist
from .common_03_capacity import (
    _UNBOUND,
    _kept,
)


def _seg_0104__city_wall_tower_coverage(
    *,
    M: Any = _UNBOUND,
    URBAN: Any = _UNBOUND,
    _R: Any = _UNBOUND,
    _a: Any = _UNBOUND,
    _arc_of: Any = _UNBOUND,
    _b: Any = _UNBOUND,
    _barb: Any = _UNBOUND,
    _cnt: Any = _UNBOUND,
    _cum: Any = _UNBOUND,
    _dd: Any = _UNBOUND,
    _dx: Any = _UNBOUND,
    _dy: Any = _UNBOUND,
    _fx: Any = _UNBOUND,
    _fy: Any = _UNBOUND,
    _g: Any = _UNBOUND,
    _gate_skip: Any = _UNBOUND,
    _gates: Any = _UNBOUND,
    _gmed: Any = _UNBOUND,
    _gsort: Any = _UNBOUND,
    _gx: Any = _UNBOUND,
    _gy: Any = _UNBOUND,
    _i: Any = _UNBOUND,
    _kx: Any = _UNBOUND,
    _ky: Any = _UNBOUND,
    _mincov: Any = _UNBOUND,
    _mur_tw: Any = _UNBOUND,
    _ns: Any = _UNBOUND,
    _nw: Any = _UNBOUND,
    _p: Any = _UNBOUND,
    _px: Any = _UNBOUND,
    _py: Any = _UNBOUND,
    _q: Any = _UNBOUND,
    _rng_ft: Any = _UNBOUND,
    _s: Any = _UNBOUND,
    _sl: Any = _UNBOUND,
    _t: Any = _UNBOUND,
    _tgaps: Any = _UNBOUND,
    _thin: Any = _UNBOUND,
    _tier: Any = _UNBOUND,
    _tight: Any = _UNBOUND,
    _tpos: Any = _UNBOUND,
    _tw: Any = _UNBOUND,
    _tx: Any = _UNBOUND,
    _tx2: Any = _UNBOUND,
    _ty: Any = _UNBOUND,
    _ty2: Any = _UNBOUND,
    _wall: Any = _UNBOUND,
    _wg: Any = _UNBOUND,
    _wx: Any = _UNBOUND,
    _wy: Any = _UNBOUND,
    best_d: Any = _UNBOUND,
    check: Any = _UNBOUND,
    g: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    px: Any = _UNBOUND,
    py: Any = _UNBOUND,
    t: Any = _UNBOUND,
    w: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 104 (city_wall_tower_coverage, wall_towers_evenly_spaced) - body verbatim from the legacy gate() (feature 022)."""
    if URBAN and M.get("wall"):
        _wall = M["wall"]
        _tier = meta.get("wall_defense", "garrison")
        _rng_ft, _mincov = WALL_DEFENSE.get(_tier, WALL_DEFENSE["garrison"])
        _R = _rng_ft / float(meta.get("ftpx") or 3.0) + 12.0  # +12 px: a mamian's half-footprint - an archer shoots from the tower's parapet span, not its center point
        _tw = [(t["x"], t["y"]) for t in M.get("wall_towers", [])] + [(g["x"], g["y"]) for g in M.get("gate_structs", []) if g.get("kind") == "tower"]
        _gates = M.get("gates", [])
        _barb = [(g["x"], g["y"]) for g in M.get("gate_structs", []) if g.get("kind") in ("guardhouse", "inspection")]  # barbican guard structures
        _wg = [(w["x"], w["y"]) for w in M.get("water_gates", [])]  # shuimen arches - fortified openings, flanked by their own two towers
        _gate_skip = (
            130.0  # px around a gate to exclude from the curtain sample: the gate is a BARBICAN - the most fortified point (gate tower + guard house + inspection + gateposts), not open curtain
        )
        _thin = []
        _nw = len(_wall)
        for _i in range(_nw):
            _a, _b = _wall[_i], _wall[(_i + 1) % _nw]
            _sl = math.hypot(_b[0] - _a[0], _b[1] - _a[1])
            _ns = max(1, int(_sl / 18))
            for _s in range(_ns):
                _t = (_s + 0.5) / _ns
                _px, _py = _a[0] + (_b[0] - _a[0]) * _t, _a[1] + (_b[1] - _a[1]) * _t
                if any(math.hypot(_px - _gx, _py - _gy) < _gate_skip for _gx, _gy in _gates) or any(math.hypot(_px - _fx, _py - _fy) < 55 for _fx, _fy in _barb):
                    continue  # inside the gate barbican (gate + its guard house + inspection) - a defended complex, not open curtain
                if any(math.hypot(_px - _wx, _py - _wy) < 45 for _wx, _wy in _wg):
                    continue  # abutting a water gate: a fortified shuimen opening flanked by its own two towers - the placement code (_seat_mural) will not tower this 40px keep-out, so the check must not demand it (check keep-outs mirror placement keep-outs)
                if any(math.hypot(_px - _kx, _py - _ky) < KIDO_TOWER_KEEPCLEAR for _kx, _ky in M.get("wall_tower_keepclears", [])):
                    continue  # a ward-fence junction on the rampart (its kido ward-gate is a manned chokepoint): placement keeps towers KIDO_TOWER_KEEPCLEAR clear of it, so demanding 2-coverage here forces a doubled tower just outside the band (the wall_towers_evenly_spaced artifact) - same mirror-the-keep-out doctrine as the water gate above
                _cnt = sum(1 for _tx, _ty in _tw if math.hypot(_px - _tx, _py - _ty) <= _R)
                if _cnt < _mincov:
                    _thin.append((round(_px), round(_py), _cnt))
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes

        # EVEN TOWER RHYTHM (GM 2026-07-23): Tango's east curtain ran ...54, 76, 32, 54... - two mamian
        # nearly touching in one spot on an otherwise even ring, visually distracting and historically
        # wrong (mural towers were built at REGULAR flanking intervals - the same doctrine the coverage
        # rule above encodes - so a doubled tower reads as an error, not a defensive choice). Cause: the
        # coverage-remediation pass's old 28px min-separation let a hole-filling tower seat right beside
        # a neighbor instead of at the local span midpoint. Placement now floors mural separation at
        # 0.75x the tier's spacing cap (strictly tighter than this gate, since the median gap never
        # exceeds the cap - so placement and check cannot disagree); this gates the RESULT: no
        # consecutive mural gap along the curtain may fall under 0.7x the map's median gap. Gate and
        # water-gate flanking towers are exempt (a barbican pair is legitimately tight). Calibration
        # 2026-07-23: the three defective pairs sat at 0.58-0.60x median; every legitimate gap in the
        # pool sat at >= 0.87x - 0.7 splits the bands with margin on both sides.
        _mur_tw = [
            (t["x"], t["y"])
            for t in M.get("wall_towers", [])
            if not any(math.hypot(t["x"] - _gx, t["y"] - _gy) < _gate_skip for _gx, _gy in _gates) and not any(math.hypot(t["x"] - _wx, t["y"] - _wy) < 130 for _wx, _wy in _wg)
        ]
        if len(_mur_tw) >= 8:
            _cum = [0.0]
            for _i in range(_nw):
                _a, _b = _wall[_i], _wall[(_i + 1) % _nw]
                _cum.append(_cum[-1] + math.hypot(_b[0] - _a[0], _b[1] - _a[1]))

            def _arc_of(px: float, py: float) -> float:
                best_d, best_arc = float("inf"), 0.0
                for _i in range(_nw):
                    _a, _b = _wall[_i], _wall[(_i + 1) % _nw]
                    _dx, _dy = _b[0] - _a[0], _b[1] - _a[1]
                    _sl = _dx * _dx + _dy * _dy
                    _t = max(0.0, min(1.0, ((px - _a[0]) * _dx + (py - _a[1]) * _dy) / _sl)) if _sl else 0.0
                    _dd = math.hypot(px - _a[0] - _t * _dx, py - _a[1] - _t * _dy)
                    if _dd < best_d:
                        best_d, best_arc = _dd, _cum[_i] + _t * math.sqrt(_sl)
                return best_arc

            _tpos = sorted((_arc_of(_tx2, _ty2), _tx2, _ty2) for _tx2, _ty2 in _mur_tw)
            _tgaps = [(_tpos[_i + 1][0] - _tpos[_i][0], _tpos[_i], _tpos[_i + 1]) for _i in range(len(_tpos) - 1)]
            _tgaps.append((_cum[-1] - _tpos[-1][0] + _tpos[0][0], _tpos[-1], _tpos[0]))  # the wrap gap
            _gsort = sorted(_g for _g, _p, _q in _tgaps)
            _gmed = _gsort[len(_gsort) // 2]
            _tight = [(round(_g), (round(_p[1]), round(_p[2])), (round(_q[1]), round(_q[2]))) for _g, _p, _q in _tgaps if _g < 0.7 * _gmed]
            pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
    return _kept(
        locals(),
        (
            '_R',
            '_a',
            '_arc_of',
            '_b',
            '_barb',
            '_cnt',
            '_cum',
            '_fx',
            '_fy',
            '_g',
            '_gate_skip',
            '_gates',
            '_gmed',
            '_gsort',
            '_gx',
            '_gy',
            '_i',
            '_kx',
            '_ky',
            '_mincov',
            '_mur_tw',
            '_ns',
            '_nw',
            '_p',
            '_px',
            '_py',
            '_q',
            '_rng_ft',
            '_s',
            '_sl',
            '_t',
            '_tgaps',
            '_thin',
            '_tier',
            '_tight',
            '_tpos',
            '_tw',
            '_tx',
            '_tx2',
            '_ty',
            '_ty2',
            '_wall',
            '_wg',
            '_wx',
            '_wy',
            'g',
            't',
            'w',
        ),
    )


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
            est_streets.append(("road", _near_line(M["road"], M.get("road_width", 30) / 2 + WMARG)))
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
