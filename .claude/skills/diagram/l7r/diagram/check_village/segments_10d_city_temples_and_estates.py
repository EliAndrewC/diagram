"""Gate segments (city temples and estates; keys 0563_126-0563_194) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from l7r.diagram.settlement import sat_overlap

from .common_01_geometry import (
    rect_corners,
    seg_closest,
    seg_intersect,
    segments_cross,
)
from .common_03_capacity import _UNBOUND, _kept


def _seg_0563_126__gf_hit_1(
    *, _gfurn: Any = _UNBOUND, _gtowers: Any = _UNBOUND, gf_hit: Any = _UNBOUND, meta: Any = _UNBOUND, o: Any = _UNBOUND, scale: Any = _UNBOUND, t: Any = _UNBOUND, tc: Any = _UNBOUND
) -> dict[str, Any]:
    """Gate segment 563.126 (gf_hit, o, t, tc) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        for t in _gtowers:
            tc = rect_corners({"x": t["x"], "y": t["y"], "w": t["w"], "h": t.get("h", t["w"]), "rot": t.get("rot", 0)})
            for o in _gfurn:
                if sat_overlap(tc, rect_corners({"x": o["x"], "y": o["y"], "w": o["w"], "h": o.get("h", o["w"]), "rot": o.get("rot", 0)})):
                    gf_hit.append((round(t["x"]), round(t["y"])))
                    break
    return _kept(locals(), ('gf_hit', 'o', 't', 'tc'))


# ... and clear of the HOUSING: the kido + its guard box occupy a fixed crossing that the
# packs cannot see (s.ward draws long after the quarters are built), so the gen must
# RESERVE each gate's ground (block_polys) before any pack runs - else a row house lands
# under the guard box (GM, 2026-07: caught twice, on both fence-end gates)


# a walled city has a RING ROAD (順城街) just inside the rampart - the wall-clear patrol zone a
# fortified city keeps for moving troops along the wall; the quarters pack INSIDE it (s.ring_road
# returns the loop to use as s.bound).


def _seg_0563_131__ring_rd(*, M: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.131 (ring_rd) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        ring_rd: Any = M.get("ring_road")  # type: ignore[no-redef,unused-ignore]
    return _kept(locals(), ('ring_rd',))


# a street running toward a THROUGH-LANE (the Imperial road or the ring road) must MEET it
# cleanly at a T-junction: its bed reaches the lane's bed and ENDS there - neither a sliver
# SHORT of it (an undershoot, the street appears to dead-end in open ground) nor a sliver
# PAST it (an overshoot, the street pokes through to the far side instead of stopping at the
# junction). A genuine crossroads, where the street truly continues well past the lane, is
# fine - only a short stub poking through is wrong. (The ring road is gated where it crosses
# the ward fence, so even the government quarter's lanes may give onto it without un-sealing.)


def _seg_0563_133__through(*, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.133 (through) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        through = []  # type: ignore[var-annotated]
    return _kept(locals(), ('through',))


def _seg_0563_134__through_1(*, M: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND, through: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.134 (through) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled') and M.get("road"):
        through.append((M["road"], (M.get("road_width", 26) - 8) / 2))
    return _kept(locals(), ('through',))


def _seg_0563_135__through_2(*, M: Any = _UNBOUND, meta: Any = _UNBOUND, ring_rd: Any = _UNBOUND, scale: Any = _UNBOUND, through: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.135 (through) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled') and ring_rd:
        through.append((ring_rd, (M.get("ring_road_width", 15) - 6) / 2))
    return _kept(locals(), ('through',))


def _seg_0563_136__bad_meet(*, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.136 (bad_meet) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        bad_meet = []  # type: ignore[var-annotated]
    return _kept(locals(), ('bad_meet',))


# streets AND alleys: a gravel alley that runs straight at a through-lane and stops a sliver
# short of it (the laborer warren's east lane stopping just shy of the east ring road) should
# reach it too, just like a paved street


def _seg_0563_137__a(*, M: Any = _UNBOUND, a: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND, st: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.137 (a, meeting_lanes, st) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        meeting_lanes = [(st["pts"], st.get("w", 18) / 2) for st in M.get("town_streets", [])] + [(a["pts"], 5.0) for a in M.get("alleys", [])]
    return _kept(locals(), ('a', 'meeting_lanes', 'st'))


def _seg_0563_138__E(
    *,
    E: Any = _UNBOUND,
    L: Any = _UNBOUND,
    align: Any = _UNBOUND,
    bad_meet: Any = _UNBOUND,
    bedhalf: Any = _UNBOUND,
    c: Any = _UNBOUND,
    cp: Any = _UNBOUND,
    dl: Any = _UNBOUND,
    gap: Any = _UNBOUND,
    i: Any = _UNBOUND,
    ip: Any = _UNBOUND,
    meeting_lanes: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    nb: Any = _UNBOUND,
    pts: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    sh: Any = _UNBOUND,
    through: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 563.138 (E, L, align, bad_meet) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        for pts, sh in meeting_lanes:
            for E, nb in ((pts[0], pts[1]), (pts[-1], pts[-2])):
                for L, bedhalf in through:
                    cp = min((seg_closest(E[0], E[1], L[i], L[i + 1]) for i in range(len(L) - 1)), key=lambda c: math.hypot(E[0] - c[0], E[1] - c[1]))
                    gap = math.hypot(E[0] - cp[0], E[1] - cp[1])
                    if gap > 46:
                        continue
                    ip = next((seg_intersect(nb, E, L[i], L[i + 1]) for i in range(len(L) - 1) if segments_cross(nb, E, L[i], L[i + 1])), None)
                    if ip is not None:  # crosses the lane: must END at the junction, not poke a stub past it
                        if 3 < math.hypot(E[0] - ip[0], E[1] - ip[1]) < 50:
                            bad_meet.append((round(E[0]), round(E[1])))
                    else:  # short of the lane: its bed must reach the lane's bed
                        dl = math.hypot(E[0] - nb[0], E[1] - nb[1]) or 1.0
                        align = ((E[0] - nb[0]) / dl) * ((cp[0] - E[0]) / max(gap, 1e-6)) + ((E[1] - nb[1]) / dl) * ((cp[1] - E[1]) / max(gap, 1e-6))
                        if align > 0.6 and gap >= sh + bedhalf:
                            bad_meet.append((round(E[0]), round(E[1])))
    return _kept(locals(), ('E', 'L', 'align', 'bad_meet', 'bedhalf', 'cp', 'dl', 'gap', 'i', 'ip', 'nb', 'pts', 'sh'))


# the RING ROAD is a CLEAR patrol road: it must run clear of EVERY solid footprint and of
# fields. The gate guard houses / inspection stations / towers DO sit along it (wall
# furniture - `gate_structs` and `wall_towers` are overlap TARGETS and EXEMPT respectively,
# so the registry leaves them out), and a ward fence may cross it - but only at a gated kido
# (enforced by city_samurai_ward_sealed, which has the ring road in its netlines). Overlap =
# the ring's BED passes through a footprint.
#
# READS THE REGISTRY, NOT A HAND LIST (GM 2026-07-25). This check used to name its own eight
# keys, so every new feature had to be remembered into it - and the martial hall, correctly
# classified and correctly cleared of all thirteen no_structure_on_* hazards, sat squarely on
# Tango's ring road with the gate green because nobody had. See solid_structs' docstring.


# WHY (a walled city cannot do without burakumin labor during a siege, so some live inside): settlements.md "Historical grounding"


# ... and the shown estates are DISPERSED, not a tight cluster: each is its own walled compound
# on its own landholding with fields between, so no two sit adjacent. A packed clump at one
# stretch of wall is the COMMERCIAL SUBURB's density, not the genteel country-estate pattern -
# gentry estates scatter by land/scenery, they do not ring the moat (GM 2026-07-22, researched:
# China-first absentee-landlord + dispersed-fortified-manor pattern, Japan agreeing). See settlements.md.


# WHY (the extramural samurai residence is the walled, defensible country ESTATE; a lone
# UNWALLED samurai house beyond the rampart is defenseless and belongs in the sealed ward
# inside): settlements.md "Historical grounding". Hard-zero - the estates rule above is
# exactly why the commoner inside-walls check exempts samurai, so this closes that gap
# (validated instance: Tango's SE top_up sweep leaked 14 houses into the moat berm, 2026-07-20).


# scattered country estates each front their OWN approach lane (not drawn at this scale), so
# their depicted (formal) gates do NOT all open the same way - a uniform direction is the
# unconsidered default. The formal gate favors the auspicious south; others face the cityward
# approach (the cityward service gate, like the governor's, is omitted at this scale).


def _seg_0563_155__moat(*, M: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.155 (moat) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        moat: Any = M.get("moat")  # type: ignore[no-redef,unused-ignore]
    return _kept(locals(), ('moat',))


# all city temples INSIDE the walls, and clear of the wall stroke and the moat


def _seg_0563_156__rel(*, M: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.156 (rel) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        rel = M.get("religious", [])
    return _kept(locals(), ('rel',))


# THE LABELED (major) CITY TEMPLES ARE DEDICATED TO THE CLAN'S TWO PATRON FORTUNES. Hantei
# X codified that every city holds a temple to each of its clan's patron fortunes (l7r.md);
# the two GREAT temples honor those, and a smattering of small wayside shrines fills the
# rest. Declare meta(clan=...); the labeled temples (kind="temple", not "small_shrine")
# must be exactly the clan's two fortunes. Override with meta(temple_fortunes=[...]) for a
# city that changed hands. GM, 2026-07: Nagahara (Crab) had a large Temple of Suitengu -
# a thematic pick, not a Crab patron (Crab = Bishamon + Ebisu). Named after "Temple of X".


# MORE THAN TWO MAJOR TEMPLES IS THE MARKED EXCEPTION, AND IT MUST BE DECLARED (feature
# 016). settlements/religion-and-death.md has enumerated the recognized justifications
# since it was written, but nothing enforced them - so a city could quietly draw six
# temples and ship green, which is the "a check that never RUNS looks exactly like a
# check that passes" shape one level up: the RULE existed and the check did not. The
# declaration is meta(temple_exception=...), from the fixed TEMPLE_EXCEPTIONS vocabulary.


# a TEMPLE NEIGHBORHOOD (>= 2 temples clustered together) should be dotted with a smattering of
# small wayside SHRINES (s.small_shrine - non-residential, kind 'small_shrine'). A lone temple
# among houses (e.g. the warrior-fortune temple in the samurai quarter) is not a neighborhood.


def _seg_0563_167__r_1(*, meta: Any = _UNBOUND, r: Any = _UNBOUND, rel: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.167 (r, temples) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        temples = [r for r in rel if r.get("kind") == "temple"]
    return _kept(locals(), ('r', 'temples'))


def _seg_0563_168__r_2(*, meta: Any = _UNBOUND, r: Any = _UNBOUND, rel: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.168 (r, shrines) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        shrines = [r for r in rel if r.get("kind") == "small_shrine"]
    return _kept(locals(), ('r', 'shrines'))


def _seg_0563_169__clustered(*, meta: Any = _UNBOUND, scale: Any = _UNBOUND, t: Any = _UNBOUND, temples: Any = _UNBOUND, u: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.169 (clustered, t, u) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        clustered = [t for t in temples if any(u is not t and math.hypot(t["x"] - u["x"], t["y"] - u["y"]) < 400 for u in temples)]
    return _kept(locals(), ('clustered', 't', 'u'))


def _seg_0563_170__city_temple_neighborhood_has_shrines(
    *, check: Any = _UNBOUND, clustered: Any = _UNBOUND, meta: Any = _UNBOUND, near_sh: Any = _UNBOUND, scale: Any = _UNBOUND, sh: Any = _UNBOUND, shrines: Any = _UNBOUND, t: Any = _UNBOUND
) -> dict[str, Any]:
    """Gate segment 563.170 (city_temple_neighborhood_has_shrines) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled') and len(clustered) >= 2:
        near_sh = sum(1 for sh in shrines if any(math.hypot(sh["x"] - t["x"], sh["y"] - t["y"]) < 350 for t in clustered))
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
    return _kept(locals(), ('near_sh', 'sh', 't'))


# ADEPT-MONK HOUSING (GM 2026-07-24). A city temple is a blank-court COMPLEX like the
# governor's yamen - the subject of its own Mode A diagram, a big walled rectangle on the
# city map - and its celibate resident monks live INSIDE the precinct, implied. But a
# share of each complex's 15-30 monks are married ADEPTS (adepts marry and raise
# children), and those households keep ordinary homes in the temple's neighborhood. So
# every major temple needs >= 2 dwellings of kind "monk_house" within ~170px - drawn
# deliberately identical to a laborer house (no label, no glyph of its own; the manifest
# kind exists so this check, the budget, and the population math can see households the
# caste bands must NOT count - clergy are not a lay caste).


def _seg_0563_171__b_9(*, M: Any = _UNBOUND, b: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.171 (b, monk_h) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        monk_h = [b for b in M.get("buildings", []) if b.get("kind") == "monk_house"]
    return _kept(locals(), ('b', 'monk_h'))


def _seg_0563_172__m_1(*, m: Any = _UNBOUND, meta: Any = _UNBOUND, monk_h: Any = _UNBOUND, scale: Any = _UNBOUND, t: Any = _UNBOUND, temples: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.172 (m, t, t_unserved) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        t_unserved = [t.get("label", (round(t["x"]), round(t["y"]))) for t in temples if sum(1 for m in monk_h if math.hypot(m["x"] - t["x"], m["y"] - t["y"]) <= 170) < 2]
    return _kept(locals(), ('m', 't', 't_unserved'))


def _seg_0563_174__m_2(*, m: Any = _UNBOUND, meta: Any = _UNBOUND, monk_h: Any = _UNBOUND, scale: Any = _UNBOUND, t: Any = _UNBOUND, temples: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.174 (m, stray_mh, t) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        stray_mh = [(round(m["x"]), round(m["y"])) for m in monk_h if not temples or min(math.hypot(m["x"] - t["x"], m["y"] - t["y"]) for t in temples) > 170]
    return _kept(locals(), ('m', 'stray_mh', 't'))


# the outside samurai estates: no overlapping each other, none over the wall or moat


# the WALLED MERCHANT ESTATES (their court, not just the house inside) must likewise sit clear
# of the rampart, the moat, and any other building. (The estate's OWN inner house, centered in
# the court, is fine; everything else - temples, compounds, other homes, other estates - is not.)


# registry-driven (GM 2026-07-25): an estate court may not swallow ANY solid footprint


# a walled estate's GATE may not open INTO a building. The walls may ABUT a neighbor (very
# common historically), but the threshold just outside the gate must front OPEN ground, not
# a COMPOUND (temple, ministry, the yamen, or another estate court) - point the gate elsewhere.
