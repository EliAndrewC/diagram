"""Gate segments (overlaps and ward fences; keys 0133_031-0196) - bodies verbatim, registry order preserved."""

import math
from collections.abc import Sequence
from typing import Any

from l7r.diagram.settlement import sat_overlap, torii_wall_conflicts

from .common_01_geometry import (
    _LABEL_CLASSIFIED,
    _OVERLAP_CLASSIFIED,
    _OVERLAP_SINGLETONS,
    _OVERLAP_STRUCTS,
    _struct_rect,
    poly_dist,
    rect_corners,
    seg_dist,
    segments_cross,
)
from .common_03_capacity import _UNBOUND, _kept

# ---- universal invariants ------------------------------------------------
# standalone civic buildings (flophouse, granary kura) are checked for overlaps exactly like
# houses and shops - they must not sit on a road / stream / wall / street / channel, or on
# each other / the manor / a hall. (Merchant storehouses are NOT here: they are drawn as
# annexes deliberately abutting their shop, so they would trip the structure-overlap test.)


def _seg_0134__granary(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 134 (granary) - body verbatim from the legacy gate() (feature 022)."""
    granary = M.get("granary")
    return _kept(locals(), ('granary',))


# the funerary structures are first-class structures for overlap purposes: a graveyard, mausoleum,
# cremation ground, or ossuary must not sit on a building, the wall, the moat, a road, or a street
# (they were added late, so it is easy to forget - this is what catches a grave on the moat or a
# mausoleum in the street). They carry x/y/w/h/rot like any building.
# EVERY solid footprint feature is a first-class structure for overlap purposes (see the
# _OVERLAP_STRUCTS registry): houses, civic/urban buildings, the funerary structures, wayside
# shrines, ministries, inspection stations. They are normalized to rects and then checked, like any
# building, against each other and against the wall / moat / road / stream / channel / street /
# manor / hall / gate / torii. Adding a new feature here is the DEFAULT; exceptions that may overlap
# (annex storehouses, annex threshing yards, on-wall towers, bridges) live in _OVERLAP_EXEMPT.


def _seg_0135__k(*, M: Any = _UNBOUND, granary: Any = _UNBOUND, k: Any = _UNBOUND, s: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 135 (k, s, structs) - body verbatim from the legacy gate() (feature 022)."""
    structs = [_struct_rect(s) for k in _OVERLAP_STRUCTS for s in M.get(k, [])] + [_struct_rect(s) for s in (granary["stores"] if granary else [])]
    return _kept(locals(), ('k', 's', 'structs'))


def _seg_0136__corners(*, s: Any = _UNBOUND, structs: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 136 (corners, s) - body verbatim from the legacy gate() (feature 022)."""
    corners = [rect_corners(s) for s in structs]
    return _kept(locals(), ('corners', 's'))


def _seg_0137__bad(*, corners: Any = _UNBOUND, i: Any = _UNBOUND, j: Any = _UNBOUND, structs: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 137 (bad, i, j) - body verbatim from the legacy gate() (feature 022)."""
    bad = [
        (i, j)
        for i in range(len(structs))
        for j in range(i + 1, len(structs))
        if math.hypot(structs[i]["x"] - structs[j]["x"], structs[i]["y"] - structs[j]["y"]) <= 110 and sat_overlap(corners[i], corners[j])
    ]
    return _kept(locals(), ('bad', 'i', 'j'))


# COMPLETENESS GUARD: every footprint feature in the manifest must be classified for overlap (in the
# _OVERLAP_* registry above). The default is MUST-NOT-OVERLAP - a new feature joins _OVERLAP_STRUCTS
# and is cleared by the checks above; anything allowed to overlap is named in _OVERLAP_EXEMPT. This
# fires when a generator emits a feature key nobody classified, so a new feature can never silently
# skip the overlap rules (the recurring trap: harvest features shipped unchecked).


def _seg_0139__g(*, M: Any = _UNBOUND, g: Any = _UNBOUND, k: Any = _UNBOUND, v: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 139 (g, k, unclassified, v) - body verbatim from the legacy gate() (feature 022)."""
    unclassified = sorted(
        k for k, v in M.items() if isinstance(v, list) and v and isinstance(v[0], dict) and any(g in v[0] for g in ("x", "pts", "outline", "boundary", "poly")) and k not in _OVERLAP_CLASSIFIED
    )
    return _kept(locals(), ('g', 'k', 'unclassified', 'v'))


def _seg_0140__every_feature_classified_for_overlap(*, check: Any = _UNBOUND, unclassified: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 140 (every_feature_classified_for_overlap) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "every_feature_classified_for_overlap",
        not unclassified,
        f"map feature(s) {unclassified} are not classified for overlap. The default is MUST-NOT-OVERLAP: add the key "
        f"to _OVERLAP_STRUCTS (so the no_structure_* checks clear it) or, if it is MEANT to overlap something (a label, "
        f"a bridge over water, a guard tower on a wall), to _OVERLAP_EXEMPT with the reason.",
    )
    return _kept(locals(), ())


# ...and the same completeness guard for CAPTIONS. A feature protected from every solid neighbor
# is still not protected from a label dropped on top of it, and that list fell behind twice before
# it was made a registry (GM 2026-07-26). Every solid key must name the label GROUP a caption has
# to use to be allowed over it, or be excused in _LABEL_EXEMPT with a reason.


def _seg_0141__k_1(*, k: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 141 (k, unlabeled) - body verbatim from the legacy gate() (feature 022)."""
    unlabeled = sorted(k for k in _OVERLAP_STRUCTS + _OVERLAP_SINGLETONS if k not in _LABEL_CLASSIFIED)
    return _kept(locals(), ('k', 'unlabeled'))


def _seg_0142__every_solid_feature_classified_for_labels(*, check: Any = _UNBOUND, unlabeled: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 142 (every_solid_feature_classified_for_labels) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "every_solid_feature_classified_for_labels",
        not unlabeled,
        f"map feature(s) {unlabeled} are not classified for LABELS. Give each one its caption GROUP in _LABEL_GROUP "
        f"(the group name is the word a caption must contain to be allowed to cover it) or, if a caption over it is "
        f"harmless, name it in _LABEL_EXEMPT with the reason.",
    )
    return _kept(locals(), ())


# no structure overlaps the magistrate's manor walls (a tilted manor uses its rotated corners)


# no structure overlaps a religious hall (an ellipse block undershot its corners)


# no structure overlaps the gate's guard station / guardtower


# no structure overlaps a torii arch. The arch is TRUE SCALE since 2026-07-21 (a 16 ft rail span,
# drawn via px()), so its box scales with meta.ftpx - the old fixed 38x28 box over-flagged houses
# that legitimately pack near the smaller true-size arch. Geometry mirrors settlement._torii
# (rail rise 7/19, post drop 17/19 of the half-span) + a 2px pad.


def _seg_0151___tft(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 151 (_tft) - body verbatim from the legacy gate() (feature 022)."""
    _tft = float(M.get("meta", {}).get("ftpx", 1) or 1)
    return _kept(locals(), ('_tft',))


def _seg_0152___ts2(*, _tft: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 152 (_ts2) - body verbatim from the legacy gate() (feature 022)."""
    _ts2 = 8.0 / _tft + 2
    return _kept(locals(), ('_ts2',))


def _seg_0153__bad_t(*, M: Any = _UNBOUND, _ts2: Any = _UNBOUND, corners: Any = _UNBOUND, sc: Any = _UNBOUND, t: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 153 (bad_t, sc, t) - body verbatim from the legacy gate() (feature 022)."""
    bad_t = [
        1
        for t in M.get("torii", [])
        for sc in corners
        if sat_overlap(sc, [(t[0] - _ts2, t[1] - _ts2 * 0.37), (t[0] + _ts2, t[1] - _ts2 * 0.37), (t[0] + _ts2, t[1] + _ts2 * 0.9), (t[0] - _ts2, t[1] + _ts2 * 0.9)])
    ]
    return _kept(locals(), ('bad_t', 'sc', 't'))


def _seg_0154__no_structure_on_torii(*, bad_t: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 154 (no_structure_on_torii) - body verbatim from the legacy gate() (feature 022)."""
    check("no_structure_on_torii", not bad_t, f"{len(bad_t)} structure(s) overlap a torii arch")
    return _kept(locals(), ())


# TORII AND RELIGIOUS FOOTPRINTS KEEP CLEAR OF THE DEFENSIVE WORKS AND THE PATROL RING (GM
# placement rules 2026-07-21, caught on Tango: a wayside shrine seated against the SW wall
# tower). A torii arch overlapping a temple/shrine hall, a guard tower / gate structure, or
# the ring-road corridor - or a religious footprint overlapping a tower or the ring road -
# reads as impossible construction: the wall's works and its patrol lane are kept clear, and
# an arch stands in the open on its approach, never against a hall. (A torii OVER an ordinary
# street stays legitimate - a monzen sando arch spans its road - so only the RING road is a
# corridor here.)


def _seg_0155___ring(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 155 (_ring) - body verbatim from the legacy gate() (feature 022)."""
    _ring = M.get("ring_road") or []
    return _kept(locals(), ('_ring',))


def _seg_0156___rw2(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 156 (_rw2) - body verbatim from the legacy gate() (feature 022)."""
    _rw2 = float(M.get("ring_road_width") or 0) / 2
    return _kept(locals(), ('_rw2',))


def _seg_0157___tow(*, M: Any = _UNBOUND, g: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 157 (_tow, g) - body verbatim from the legacy gate() (feature 022)."""
    _tow = [g for g in list(M.get("gate_structs", [])) + list(M.get("wall_towers", [])) + list(M.get("fire_towers", [])) if isinstance(g, dict) and "w" in g]
    return _kept(locals(), ('_tow', 'g'))


def _seg_0158___ring_hit_poly(
    *, _ring: Any = _UNBOUND, _rw2: Any = _UNBOUND, a: Any = _UNBOUND, b: Any = _UNBOUND, i: Any = _UNBOUND, k: Any = _UNBOUND, poly: Any = _UNBOUND, px: Any = _UNBOUND, py: Any = _UNBOUND
) -> dict[str, Any]:
    """Gate segment 158 (_ring_hit_poly) - body verbatim from the legacy gate() (feature 022)."""

    def _ring_hit_poly(poly: list[tuple[float, float]]) -> bool:
        """Does a FOOTPRINT reach the ring-road bed? Corner-to-segment, not center-plus-a-radius:
        the circumscribed radius this used to pass over-states an elongated hall's reach along one
        axis and under-states nothing, so it flagged halls that were genuinely clear while a long
        thin one laid across the lane could still slip through the far side of the same
        approximation (GM audit, 2026-07-27)."""
        for i in range(len(_ring) - 1):
            a, b = _ring[i], _ring[i + 1]
            # CROSSING FIRST, then proximity. Corner-sampling alone answers "is a corner near the
            # centerline", which is not the question: a hall laid ACROSS the lane can have every
            # corner outside the bed while its flanks straddle it - the y=890 hall over a bed
            # spanning 896-904 has its nearest corner exactly _rw2 away and overlaps 8 px of
            # roadbed. The old circumscribed-radius form caught that case by being loose enough,
            # which is not the same as being right; this catches it by asking the real question.
            if any(segments_cross(a, b, poly[k], poly[(k + 1) % len(poly)]) for k in range(len(poly))):
                return True
            if min(min(seg_dist(px, py, a, b) for px, py in poly), poly_dist(a[0], a[1], poly), poly_dist(b[0], b[1], poly)) < _rw2:
                return True
        return False

    return _kept(locals(), ('_ring_hit_poly',))


def _seg_0159___torii_poly(*, _ts2: Any = _UNBOUND, t: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 159 (_torii_poly) - body verbatim from the legacy gate() (feature 022)."""

    def _torii_poly(t: Sequence[float]) -> list[tuple[float, float]]:
        return [(t[0] - _ts2, t[1] - _ts2), (t[0] + _ts2, t[1] - _ts2), (t[0] + _ts2, t[1] + _ts2), (t[0] - _ts2, t[1] + _ts2)]

    return _kept(locals(), ('_torii_poly',))


def _seg_0160__bad_tor_pl() -> dict[str, Any]:
    """Gate segment 160 (bad_tor_pl) - body verbatim from the legacy gate() (feature 022)."""
    bad_tor_pl = []  # type: ignore[var-annotated]
    return _kept(locals(), ('bad_tor_pl',))


def _seg_0161___torp(
    *,
    M: Any = _UNBOUND,
    _ring_hit_poly: Any = _UNBOUND,
    _torii_poly: Any = _UNBOUND,
    _torp: Any = _UNBOUND,
    _tow: Any = _UNBOUND,
    bad_tor_pl: Any = _UNBOUND,
    g: Any = _UNBOUND,
    hit_rel: Any = _UNBOUND,
    hit_tw: Any = _UNBOUND,
    r: Any = _UNBOUND,
    t: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 161 (_torp, bad_tor_pl, g, hit_rel) - body verbatim from the legacy gate() (feature 022)."""
    for t in M.get("torii", []):
        _torp = _torii_poly(t)
        # ROTATED corners on the hall/tower side. The axis-aligned `abs(dx) < w/2 + pad` form this
        # replaces reads a tilted hall as its upright box, which is neither its footprint nor a
        # conservative cover of it - it misses the swung corners and invents ground at the flats.
        hit_rel = any(sat_overlap(_torp, rect_corners(_struct_rect(r))) for r in M.get("religious", []))
        hit_tw = any(sat_overlap(_torp, rect_corners(_struct_rect(g))) for g in _tow)
        if hit_rel or hit_tw or _ring_hit_poly(_torp):
            bad_tor_pl.append((round(t[0]), round(t[1])))
    return _kept(locals(), ('_torp', 'bad_tor_pl', 'g', 'hit_rel', 'hit_tw', 'r', 't'))


def _seg_0162__torii_clear_of_halls_towers_ring(*, bad_tor_pl: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 162 (torii_clear_of_halls_towers_ring) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "torii_clear_of_halls_towers_ring",
        not bad_tor_pl,
        f"torii arch(es) overlapping a temple/shrine hall, guard tower/gate structure, or the ring-road corridor: {sorted(set(bad_tor_pl))[:4]} - an arch stands clear on its approach (an ordinary street through the arch is fine; the patrol ring is not)",
    )
    return _kept(locals(), ())


# ... AND CLEAR OF EVERY WALL (GM 2026-07-25, caught on Nagahara: the seventh arch of the Ebisu
# sando stood in the samurai ward fence). A torii is a FREESTANDING gateway - posts in open
# ground, carrying nothing, closing nothing - while a wall is a continuous barrier, so an arch
# drawn on a wall run is impossible construction: the posts stand inside the palisade and the
# gateway opens onto a barrier. Where a way pierces a wall the opening is a GATE STRUCTURE (the
# city gate, a ward kido), never an arch. The rule and its geometry live in settlement.py's
# wall_runs block, which the PLACEMENT side reads too (shrine_hall shortens a sando that would
# reach a wall; _torii and each wall-drawing method refuse the conflict outright) - this is the
# manifest-level backstop over the city rampart, ward fences and every walled compound.


def _seg_0163__tor_wall(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 163 (tor_wall) - body verbatim from the legacy gate() (feature 022)."""
    tor_wall = torii_wall_conflicts(M)
    return _kept(locals(), ('tor_wall',))


def _seg_0164__torii_clear_of_walls(*, check: Any = _UNBOUND, tor_wall: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 164 (torii_clear_of_walls) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "torii_clear_of_walls",
        not tor_wall,
        f"torii arch(es) standing in a wall: {tor_wall[:4]} - a torii is a freestanding gateway on open ground and a "
        f"wall is a continuous barrier; a way through a wall is a GATE (the city gate, a ward kido), never an arch. "
        f"Move the arch clear - or draw the wall BEFORE the hall, and shrine_hall stops its avenue short of it.",
    )
    return _kept(locals(), ())


def _seg_0165__bad_rel_pl() -> dict[str, Any]:
    """Gate segment 165 (bad_rel_pl) - body verbatim from the legacy gate() (feature 022)."""
    bad_rel_pl = []  # type: ignore[var-annotated]
    return _kept(locals(), ('bad_rel_pl',))


def _seg_0166___relp(
    *, M: Any = _UNBOUND, _relp: Any = _UNBOUND, _ring_hit_poly: Any = _UNBOUND, _tow: Any = _UNBOUND, bad_rel_pl: Any = _UNBOUND, g: Any = _UNBOUND, hit_tw: Any = _UNBOUND, r: Any = _UNBOUND
) -> dict[str, Any]:
    """Gate segment 166 (_relp, bad_rel_pl, g, hit_tw) - body verbatim from the legacy gate() (feature 022)."""
    for r in M.get("religious", []):
        _relp = rect_corners(_struct_rect(r))
        hit_tw = any(sat_overlap(_relp, rect_corners(_struct_rect(g))) for g in _tow)
        if hit_tw or _ring_hit_poly(_relp):
            bad_rel_pl.append((r.get("label") or r["kind"], round(r["x"]), round(r["y"])))
    return _kept(locals(), ('_relp', 'bad_rel_pl', 'g', 'hit_tw', 'r'))


def _seg_0167__religious_clear_of_ring_and_towers(*, bad_rel_pl: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 167 (religious_clear_of_ring_and_towers) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "religious_clear_of_ring_and_towers",
        not bad_rel_pl,
        f"religious footprint(s) overlapping a guard tower/gate structure or the ring-road corridor: {bad_rel_pl[:4]} - shrines and halls keep clear of the wall's works and the patrol lane",
    )
    return _kept(locals(), ())


# roads/streets are a GROUND layer: a gatehouse or label that legitimately sits on a road
# must be drawn ON TOP of it (higher draw-order z), never have the road painted over it.


# LANE LAYERING: where two linear ground features cross, the WIDER renders on top (higher draw z).
# The Imperial road is painted over the city streets it crosses, streets over the alleys they cross.
# z is the recorded final draw position (settlement flushes road/street/alley as one ordered block).


def _seg_0176__lanes() -> dict[str, Any]:
    """Gate segment 176 (lanes) - body verbatim from the legacy gate() (feature 022)."""
    lanes = []  # type: ignore[var-annotated]
    return _kept(locals(), ('lanes',))


def _seg_0177__lanes_1(*, M: Any = _UNBOUND, lanes: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 177 (lanes) - body verbatim from the legacy gate() (feature 022)."""
    if M.get("road") and M.get("road_z") is not None:
        lanes.append(("road", M["road"], M.get("road_width", 30), M["road_z"]))
    return _kept(locals(), ('lanes',))


def _seg_0178__lanes_2(*, M: Any = _UNBOUND, lanes: Any = _UNBOUND, st: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 178 (lanes, st) - body verbatim from the legacy gate() (feature 022)."""
    lanes += [("street", st["pts"], st["w"], st["z"]) for st in M.get("town_streets", []) if st.get("z") is not None]
    return _kept(locals(), ('lanes', 'st'))


def _seg_0179__a(*, M: Any = _UNBOUND, a: Any = _UNBOUND, lanes: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 179 (a, lanes) - body verbatim from the legacy gate() (feature 022)."""
    lanes += [("alley", a["pts"], a.get("w", 10), a["z"]) for a in M.get("alleys", []) if a.get("z") is not None]
    return _kept(locals(), ('a', 'lanes'))


# where lanes meet they form a clean CROSSROADS: the paved BEDS merge into a continuous surface, with
# no lane's EDGE (its dark curb-line) cutting across another lane's bed at the junction. The engine
# draws the ground block in sub-layers - all edges, then all beds, then center-marks - so every edge
# sits below every bed; the check guards that invariant (max edge draw-z < min bed draw-z).


# WALLS render OVER the ground lanes: a road/street/alley that runs INTO a wall - touches or crosses
# its stroke - must pass UNDER it (the wall has a higher draw z). The settlement draws ramparts in a
# dedicated WALL layer above the ground block precisely so this holds; the check guards the invariant
# for the city/town wall AND every neighborhood (ward) fence. A lane only breaches a wall at a GATE,
# where the wall has a genuine opening (no stroke to render over), so crossings/touches at a gate are
# exempt. The wall is a closed ring at city scale, an open hill-anchored arc at town scale.


def _seg_0186__bad_1(
    *,
    a: Any = _UNBOUND,
    b: Any = _UNBOUND,
    bad: Any = _UNBOUND,
    bz: Any = _UNBOUND,
    ex: Any = _UNBOUND,
    ey: Any = _UNBOUND,
    k: Any = _UNBOUND,
    lanes: Any = _UNBOUND,
    name: Any = _UNBOUND,
    near: Any = _UNBOUND,
    p: Any = _UNBOUND,
    pts: Any = _UNBOUND,
    ring: Any = _UNBOUND,
    w: Any = _UNBOUND,
    x: Any = _UNBOUND,
    y: Any = _UNBOUND,
    z: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 186 (bad, lanes_over) - body verbatim from the legacy gate() (feature 022)."""

    # `lanes_over` was defined here for checks feature 141 retired and NOTHING calls it - not this segment,
    # not any later one (the registry's needs say so). Removed under feature 146 with the rest of that residue.
    return _kept(locals(), ("bad",))


def _seg_0187__wall(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 187 (wall, wall_z) - body verbatim from the legacy gate() (feature 022)."""
    wall, wall_z = M.get("wall"), M.get("wall_z")
    return _kept(locals(), ('wall', 'wall_z'))


# NO DOUBLED WALL: the short wall-stroke CAP that plugs a ward fence into the rampart must lie FLUSH
# along the wall, not jut across it. A straight cap tangent to one segment, laid at a wall CORNER, juts
# past the bend and reads as a second wall section overlapping the first (Nagahara SW, GM 2026-07). The
# cap is now drawn to FOLLOW the wall (arc +/-16 px through any vertex in the span); this guards the
# invariant so a regression to a straight-tangent cap is caught. Every cap vertex must sit within
# tolerance of the wall polyline.


# JOIN, DON'T INTERSECT - the WALL member of a family the ways and the watercourses already had
# (GM 2026-07-27, on Minami: "the neighborhood walls stick out the other side of the city walls").
# Where two linear features meet, one of them ENDS at the junction: a lane terminates at the
# through-lane it reaches rather than poking a stub out the far side
# (city_streets_no_intersection_stub, city_streets_meet_through_lanes), and a watercourse joins at
# a T or a Y rather than crossing (water_channels_join_not_cross, channels_join_water_not_cross).
# A neighborhood (ward) fence meeting the city rampart is the same junction and was the one member
# of the family nobody had stated: the fence ENDS at the wall, because the wall is what seals it -
# a palisade continuing out through the rampart into the fields encloses nothing and reads as two
# walls crossing at an intersection.
#
# city_ward_fence_meets_wall is the mirror rule (the UNDERSHOOT - a gap the commoners walk around)
# and deliberately allows ~10px of slop in EITHER direction, which is why this defect shipped
# green: Minami's two fence ends sat 4.2 and 4.9px OUTSIDE the wall ring, well inside that
# tolerance. The overshoot has to be measured against the DRAWN ink instead, and it is small
# numbers all the way down - the rampart's stroke covers only its own half-width (11/2 = 5.5px),
# while the fence is stroked with a ROUND LINECAP that inks half a stroke-width (5/2 = 2.5px) past
# its last recorded vertex. So 4.9 + 2.5 = 7.4px of fence against 5.5px of wall left a ~2px tan
# nub outside the rampart - at a city's 1px = 3ft, about 6ft of palisade standing in the moat
# berm. Both widths come from the engine's own records (M['wall_stroke'], the ward's 'stroke') so
# placement and check read the same source; the literals are the fallback for manifests written
# before those records existed.
