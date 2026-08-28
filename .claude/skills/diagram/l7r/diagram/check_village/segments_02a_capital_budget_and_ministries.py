"""Gate segments (capital budget and ministries; keys 0097-0106_026) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from l7r.diagram.settlement import rail_quad, sat_overlap, trough_quad, wellhead_quad

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
