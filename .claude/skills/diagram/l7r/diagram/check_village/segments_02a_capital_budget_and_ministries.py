"""Gate segments (capital budget and ministries; keys 0097-0106_026) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from l7r.diagram.settlement import KIDO_TOWER_KEEPCLEAR, WALL_DEFENSE, rail_quad, sat_overlap, trough_quad, wellhead_quad

from .common_03_capacity import (
    _UNBOUND,
    _kept,
)

# WELLS, TROUGHS, AND HITCHING POSTS NEVER OVERLAP ONE ANOTHER (GM 2026-07-25). The motivating
# defect was Nagahara's flophouse yard: a hitching rail drawn straight ACROSS a wellhead, with
# the trough cluster stacked on both - three glyphs on one spot, where a reader can no longer
# tell which is which, and the layout it implies is nonsense (nobody draws water through a rail,
# and no yard ties its animals over its own draw-point). They collide because they are placed at
# three different moments - the wells long before the yard exists, the rails when it draws, the
# cluster after - so nothing had ever measured the pair. This check is deliberately GEOMETRIC
# and glyph-level: it demands only that the DRAWN extents not intersect, not any working
# clearance, because the troughs are SUPPOSED to hug their well (the bucket-pour relay,
# stable_troughs_beside_well) and animals are supposed to stand between rail and trough. Near is
# right; on top of is not. Extents come from the shared quad builders in settlement.py, the same
# ones s._stable_yard places against (with YARD_GLYPH_SLACK of margin), so placement and check
# can never drift apart. Every pair on the map is tested, ACROSS yards as well as within one -
# the cross-yard hole is what the dung-heap rule had to be widened for twice.


def _seg_0097___wtr() -> dict[str, Any]:
    """Gate segment 97 (_wtr) - body verbatim from the legacy gate() (feature 022)."""
    _wtr: list[tuple[str, list[tuple[float, float]], float, float, float]] = []
    return _kept(locals(), ('_wtr',))


def _seg_0098___wtr_1(*, _wtr: Any = _UNBOUND, cx: Any = _UNBOUND, cy: Any = _UNBOUND, kind: Any = _UNBOUND, qx: Any = _UNBOUND, qy: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 98 (_wtr, _wtr_add) - body verbatim from the legacy gate() (feature 022)."""

    def _wtr_add(kind: str, quad: list[tuple[float, float]], cx: float, cy: float) -> None:
        _wtr.append((kind, quad, cx, cy, max(math.hypot(qx - cx, qy - cy) for qx, qy in quad)))

    return _kept(locals(), ('_wtr', '_wtr_add'))


def _seg_0099___wtr_2(*, M: Any = _UNBOUND, _wtr: Any = _UNBOUND, _wtr_add: Any = _UNBOUND, _wtr_w: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 99 (_wtr, _wtr_w) - body verbatim from the legacy gate() (feature 022)."""
    for _wtr_w in M.get("wells", []) or []:
        _wtr_add("well", wellhead_quad(_wtr_w), _wtr_w["x"], _wtr_w["y"])
    return _kept(locals(), ('_wtr', '_wtr_w'))


def _seg_0100___wtr_3(*, M: Any = _UNBOUND, _wtr: Any = _UNBOUND, _wtr_add: Any = _UNBOUND, _wtr_box: Any = _UNBOUND, _wtr_rl: Any = _UNBOUND, _wtr_yd: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 100 (_wtr, _wtr_box, _wtr_rl, _wtr_yd) - body verbatim from the legacy gate() (feature 022)."""
    for _wtr_yd in M.get("stable_yards", []) or []:
        _wtr_box = _wtr_yd.get("troughs_box")
        if _wtr_box:
            _wtr_add("troughs", trough_quad(_wtr_box), (_wtr_box[0] + _wtr_box[2]) / 2, (_wtr_box[1] + _wtr_box[3]) / 2)
        for _wtr_rl in _wtr_yd.get("rails", []) or []:
            _wtr_add("hitching rail", rail_quad(_wtr_rl), _wtr_rl["x"], _wtr_rl["y"])
    return _kept(locals(), ('_wtr', '_wtr_box', '_wtr_rl', '_wtr_yd'))


def _seg_0101___wtr_bad() -> dict[str, Any]:
    """Gate segment 101 (_wtr_bad) - body verbatim from the legacy gate() (feature 022)."""
    _wtr_bad = []  # type: ignore[var-annotated]
    return _kept(locals(), ('_wtr_bad',))


def _seg_0102___ax(
    *,
    _ax: Any = _UNBOUND,
    _ay: Any = _UNBOUND,
    _bx: Any = _UNBOUND,
    _by: Any = _UNBOUND,
    _ka: Any = _UNBOUND,
    _kb: Any = _UNBOUND,
    _qa: Any = _UNBOUND,
    _qb: Any = _UNBOUND,
    _ra: Any = _UNBOUND,
    _rb: Any = _UNBOUND,
    _wtr: Any = _UNBOUND,
    _wtr_bad: Any = _UNBOUND,
    _wtr_i: Any = _UNBOUND,
    _wtr_j: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 102 (_ax, _ay, _bx, _by) - body verbatim from the legacy gate() (feature 022)."""
    for _wtr_i in range(len(_wtr)):
        _ka, _qa, _ax, _ay, _ra = _wtr[_wtr_i]
        for _wtr_j in range(_wtr_i + 1, len(_wtr)):
            _kb, _qb, _bx, _by, _rb = _wtr[_wtr_j]
            if math.hypot(_ax - _bx, _ay - _by) > _ra + _rb:  # circumradii cannot reach: no overlap possible
                continue
            if sat_overlap(_qa, _qb):
                _wtr_bad.append((f"{_ka}/{_kb}", round(_ax), round(_ay)))
    return _kept(locals(), ('_ax', '_ay', '_bx', '_by', '_ka', '_kb', '_qa', '_qb', '_ra', '_rb', '_wtr_bad', '_wtr_i', '_wtr_j'))


# WALL TOWER COVERAGE by the city's DEFENSE POSTURE (GM 2026-07-22): the interlocking-flanking-fire rule
# (侧射; Shen Kuo's 11th-c. 矢石相及 - adjacent mamian's fields of fire overlap so an attacker at the base
# is hit from >=2 towers). TUNABLE per city (meta wall_defense): `siege` = aimed-lethal bowshot (60 m /
# 197 ft), >=2 towers everywhere; `garrison` = full war-bow reach (100 m / 328 ft), >=2; `peaceful` = the
# sparser Xi'an spacing, >=1 flanking tower within aimed-lethal range everywhere (midpoints get 2). Every
# point on the wall CURTAIN must have >= the tier's min-count of towers within the tier's arrow range;
# the gate OPENING itself is exempt (a defended chokepoint with its own gate tower + guard, not open
# curtain). Both mural and gate towers count. See settlements.md 'Historical grounding'.


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
        check(
            "city_wall_tower_coverage",
            not _thin,
            f"{len(_thin)} wall point(s) covered by fewer than {_mincov} tower(s) within the {_tier} arrow range ({_rng_ft:.0f} ft): {_thin[:4]} (x, y, towers-in-range) - a {_tier} city's rampart must keep every curtain point under flanking fire from {_mincov} tower(s); tower the wall closer (meta wall_defense sets the spacing; settlements.md 'Historical grounding')",
        )

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
            check(
                "wall_towers_evenly_spaced",
                not _tight,
                f"mural tower pair(s) far closer than the wall's rhythm (gap px, tower, tower; median gap {_gmed:.0f}): {_tight[:3]} - "
                f"mamian stand at regular flanking intervals, so no open-curtain gap may fall under 0.7x the median; a doubled tower "
                f"is a remediation-seat artifact, not a defensive choice (gate/water-gate flanking pairs are exempt)",
            )
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


# THE CAPITAL TIER IS SIZED BUDGET-FIRST TOO (feature 018, specs/018-capital-space-budget).
# The sibling of city_wall_matches_budget above, at the SAME tolerances - inherited
# deliberately rather than re-derived, because they are pinned by the shipped-Tango /
# rejected-Nagahara pair and nothing about a capital argues for different slack.


# THE RATCHET (FR-015). A rule gated on an optional declaration is optional in practice:
# three separate times in this engine's history a check silently never RAN while the gate
# stayed green, because the map declared nothing. So a capital that declares no budget
# FAILS here rather than skipping its conformance check. Model: settlement_declares_a_land_fall.


# ---- feature 020: the ground-reserving layer ------------------------------------------
# THE GOVERNMENT WARD. Both anchor traditions put the domain ministries OUTSIDE the
# castle, flanking the ceremonial approach: Beijing's Six Ministries lined the Corridor of
# a Thousand Steps outside Chengtianmen, and a jokamachi's offices spilled out of the
# ninomaru into the town as they grew. So a capital shows its six ministries fronting the
# ote-suji - the avenue from the castle's front gate to the through-road - with the House
# Chancellery and the domain school on the same axis (settlements/capitals.md, "The
# government ward"; the research trail is research/cities/capitals.md).


# NO House Chancellery compound: the council of lineage representatives meets IN the
# castle (GM 2026-08-09, researched: Edo's Hyojosho and the Roju council sat within Edo
# castle, and China's Grand Secretariat sat inside the palace - the split both anchors
# agree on is EXECUTIVE ministries out, the ruler's COUNCIL in). A chancellery compound
# outside is therefore a defect, not a requirement; the council chamber is part of the
# castle's implied goten. research/cities/capitals.md, "The chancellery meets IN the castle".


# The approach avenue: the way that leaves the castle's front gate. Membership questions
# below are judged center-to-line with tolerances that dwarf the footprints - the
# ASSOCIATION/reach family (CLAUDE.md, "Centers, footprints, and aggregates").


# A government office stands in its own ground - the provincial rule restated at this
# tier, because the scale=="city" block does not run here and a capital has no governor's
# yamen. Same 14px standoff, same funerary exclusion (a clan crypt against a bureau is a
# real adjacency), same registry-driven victim list.


# THE LINEAGE COMPOUNDS are what make a capital read as a SPECIFIC domain's seat: named
# walled yashiki whose size tracks how many of each lineage actually LIVE here - never the
# rank of its head (the kurogi rule: a full chancellor on a visibly smaller plot because
# his people are out in his province). The ruling lineage gets NO compound - its seat IS
# the castle. settlements/capitals.md, "Shiro Daika's lineage compounds".


# The FR-015 ratchet again: without the declaration every lineage check below SKIPS while
# showing green, so the missing declaration is itself the failure.
