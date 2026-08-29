"""Gate segments (bridges and gate roads; keys 0334-0359) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from l7r.diagram.settlement import bridge_carried_ways, bridge_crossed_waters

from .common_01_geometry import seg_intersect, segments_cross
from .common_03_capacity import _UNBOUND, _kept

# WHERE A WAY CROSSES A WATERCOURSE, a bridge must carry it over - a way does not simply run
# through open water. Crossings are road / RING ROAD / street / lane segments intersecting a
# stream, an irrigation channel, a field ditch, the navigable cargo canal, or the city moat (a
# walled city's approach road crosses the moat at each gate). Every such crossing must have a
# recorded bridge near the intersection point. (A way merely running ALONGSIDE water, never
# intersecting it, needs no bridge - only true crossings count.)
#
# The way and water sets here MIRROR settlement.bridges(), which draws from the same two lists -
# they must stay in step or the engine places decks the gate does not ask for, or (worse) the
# gate stays silent about a crossing the engine never saw. The ring road and the cargo canal were
# missing from BOTH until 2026-07-27, which is why Minami's and Nagahara's canal crossings were
# hand-placed and both went crooked (see bridges_align_with_their_way, below).
#
# An UNDRAWN channel (`drawn: False`, from topo_channel) is a buried conduit recorded for water
# topology only - there is no seam on the ground, so a way crossing its line crosses nothing and
# needs no deck. Tango's ring road runs over three of them.


def _seg_0334__bridges(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 334 (bridges) - body verbatim from the legacy gate() (feature 022)."""
    bridges = M.get("bridges", [])
    return _kept(locals(), ('bridges',))


# ONE SOURCE, shared with settlement.bridges() (feature 020). These sets used to be built
# separately here and in the generator, and both omitted M["roads"], the river and a castle's
# own moat - so the two agreed perfectly and were both wrong, leaving four of six crossings on
# the first capital unbridged with a green gate. "Placement and its check read the SAME source"
# guarantees they cannot DISAGREE; it does not make either correct, so they now read one
# function rather than two lists that happen to match.


def _seg_0335____1(*, M: Any = _UNBOUND, w: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 335 (_, w, waters_b) - body verbatim from the legacy gate() (feature 022)."""
    waters_b = [w for w, _ in bridge_crossed_waters(M)]
    return _kept(locals(), ('_', 'w', 'waters_b'))


def _seg_0336____2(*, M: Any = _UNBOUND, c: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 336 (_, c, carried_b) - body verbatim from the legacy gate() (feature 022)."""
    carried_b = [c for c, _ in bridge_carried_ways(M)]
    return _kept(locals(), ('_', 'c', 'carried_b'))


def _seg_0337__xings_b() -> dict[str, Any]:
    """Gate segment 337 (xings_b) - body verbatim from the legacy gate() (feature 022)."""
    xings_b = []  # type: ignore[var-annotated]  # (point, way heading in degrees) for every way x water crossing on the map
    return _kept(locals(), ('xings_b',))


def _seg_0338__i_3(
    *,
    carried_b: Any = _UNBOUND,
    i: Any = _UNBOUND,
    j: Any = _UNBOUND,
    p: Any = _UNBOUND,
    ra: Any = _UNBOUND,
    rb: Any = _UNBOUND,
    rpts: Any = _UNBOUND,
    waters_b: Any = _UNBOUND,
    wpts: Any = _UNBOUND,
    xings_b: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 338 (i, j, p, ra) - body verbatim from the legacy gate() (feature 022)."""
    for rpts in carried_b:
        for i in range(len(rpts) - 1):
            ra, rb = rpts[i], rpts[i + 1]
            for wpts in waters_b:
                for j in range(len(wpts) - 1):
                    if segments_cross(ra, rb, wpts[j], wpts[j + 1]):
                        p = seg_intersect(ra, rb, wpts[j], wpts[j + 1])
                        if p is not None:
                            xings_b.append((p, math.degrees(math.atan2(rb[1] - ra[1], rb[0] - ra[0]))))
    return _kept(locals(), ('i', 'j', 'p', 'ra', 'rb', 'rpts', 'wpts', 'xings_b'))


# A BRIDGE MUST LIE ON ITS CROSSING AND RUN ALONG THE WAY IT CARRIES (GM 2026-07-27, Minami's
# cargo-basin bridge). The rule above only asks that SOME deck be within 40px of each crossing,
# which a deck sitting beside the crossing at a wrong angle satisfies - and the eye reads that as
# the road running straight through the water with a crooked plank next to it, which is exactly
# what the GM saw. So each carried deck is paired with the nearest crossing and must sit ON it
# (within BRIDGE_SEAT_TOL) and share its bearing (within BRIDGE_ROT_TOL, mod 180 - a deck has no
# forward direction). EVIDENCE for the tolerances: every deck s.bridges() solves lands 0.0-1.0 px
# and 0.0-1.0 deg off its crossing (rounding only), while the two hand-placed canal decks were
# 17px/39deg (Minami) and 15px/24deg (Nagahara) off - two orders of magnitude adrift, so a tight
# tolerance separates them cleanly with room to spare.
#
# A deck with NO crossing under it at all fails the same check: it carries nothing, so either the
# way or the watercourse it was drawn for is not in the manifest.
#
# STANDALONE plank footbridges (`foot`) are exempt: no way carries them, they cross the ditch
# PERPENDICULAR by construction, and their own rules are long_ditches_have_a_footbridge /
# footbridges_reach_useful_ground.


def _seg_0341__BRIDGE_ROT_TOL() -> dict[str, Any]:
    """Gate segment 341 (BRIDGE_ROT_TOL, BRIDGE_SEAT_TOL) - body verbatim from the legacy gate() (feature 022)."""
    BRIDGE_SEAT_TOL, BRIDGE_ROT_TOL = 8.0, 8.0
    return _kept(locals(), ('BRIDGE_ROT_TOL', 'BRIDGE_SEAT_TOL'))


def _seg_0342__crooked() -> dict[str, Any]:
    """Gate segment 342 (crooked) - body verbatim from the legacy gate() (feature 022)."""
    crooked = []  # type: ignore[var-annotated]
    return _kept(locals(), ('crooked',))


def _seg_0343__b(
    *,
    BRIDGE_ROT_TOL: Any = _UNBOUND,
    BRIDGE_SEAT_TOL: Any = _UNBOUND,
    b: Any = _UNBOUND,
    bridges: Any = _UNBOUND,
    crooked: Any = _UNBOUND,
    deck_skew: Any = _UNBOUND,
    heading: Any = _UNBOUND,
    near_x: Any = _UNBOUND,
    px_: Any = _UNBOUND,
    py_: Any = _UNBOUND,
    seat_off: Any = _UNBOUND,
    xings_b: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 343 (b, crooked, deck_skew, heading) - body verbatim from the legacy gate() (feature 022)."""
    for b in bridges:
        if b.get("foot"):
            continue
        near_x = min(xings_b, key=lambda pv: math.hypot(pv[0][0] - b["x"], pv[0][1] - b["y"]), default=None)
        if near_x is None:
            crooked.append(f"({round(b['x'])},{round(b['y'])}) carries no way over any water")
            continue
        (px_, py_), heading = near_x
        seat_off = math.hypot(px_ - b["x"], py_ - b["y"])
        deck_skew = abs((b.get("rot", 0.0) - heading + 90) % 180 - 90)
        if seat_off > BRIDGE_SEAT_TOL:
            crooked.append(f"({round(b['x'])},{round(b['y'])}) sits {seat_off:.0f}px off its crossing at ({round(px_)},{round(py_)})")
        elif deck_skew > BRIDGE_ROT_TOL:
            crooked.append(f"({round(b['x'])},{round(b['y'])}) is rot {b.get('rot', 0.0):.0f} but its way bears {heading:.0f} ({deck_skew:.0f} deg askew)")
    return _kept(locals(), ('b', 'crooked', 'deck_skew', 'heading', 'near_x', 'px_', 'py_', 'seat_off'))


def _seg_0344__bridges_align_with_their_way(*, check: Any = _UNBOUND, crooked: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 344 (bridges_align_with_their_way) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "bridges_align_with_their_way",
        not crooked,
        f"{len(crooked)} bridge(s) not seated on the crossing they carry: {crooked[:3]} - a deck lies ON the intersection and runs ALONG the way, or the way runs through the water beside it; solve it with s.bridges() instead of hand-placing coordinates",
    )
    return _kept(locals(), ())


# A WATERCOURSE PIERCES A RAMPART ONLY AT A WATER GATE (GM 2026-08-09). Nagahara's cargo
# canal anchored its east end to a moat vertex BY INDEX; a past ring re-derivation moved the
# vertex, the approach leg slid 40px off the shuimen gap, and the canal shipped running
# UNDER the wall - placement and the wall's gap had no shared source and nothing compared
# the crossing to the gate. The doctrine was already prose (inwall_drain_outfall: "never
# draw a ditch running through the city wall"); this makes it a check for every DRAWN
# canal/channel/stream against a closed rampart. Buried conduits (drawn=False) pierce
# nothing; the moat is the ring outside and never crosses.


# ---- feature 021: the capital housing layer -------------------------------------------
# FABRIC DECLARES ITS DISTRICTS (T003): once dwellings stand, the capital records which
# named district each pack filled - the districts are the rank-gradient check's ground
# truth and the reader's map of intent. The bare 020 state (no fabric) stays legal, so
# this is a declaration-existence rule on the HOUSED capital only ("a check that never
# RUNS looks exactly like a check that passes").


# RANK GRADES WITH DISTANCE FROM THE CASTLE (T004; research 021 item 1): the jokamachi
# law - senior walled yashiki nearest the castle, detached houses next, retainer
# terraces at the band edge. Footprint family: CLASSIFICATION (members assigned by
# center to the band district containing them) + an ordering on band MEAN distances;
# 12px slack absorbs band-boundary geometry. Bands without members are skipped, so a
# mid-build map stays legal.


# THE WALL SETTLES FIRST (GM process rule, 2026-08-10): fine iteration on a capital is
# forbidden until the interior's OPEN share is inside the band, because every fine
# adjustment is downstream of the wall and a wall re-derivation invalidates them all.
# Measured the day the rule was made: 41% of the walled interior stood as claimed-open
# commons after two wall sizings, and hours of junction/well/kido tuning had been spent
# against a rampart that was about to move. Claimed-open ground (commons of any role)
# inside the wall must stay under ~15% of the interior - beyond that, the wall is
# oversized for its fabric: RE-DERIVE RX/RY (citybudget) before touching anything else.


# SOVEREIGN PRECINCT INTERIORS (T017, research item 7): once a precinct reservation is
# DECLARED (M['precincts'], the 021 engine path), its head-house program must actually be
# drawn - >= 5 halls, every one fully inside the reserved rect (a dormitory overhanging the
# reservation is a pack-collision waiting to happen; the reserve is the contract).


# TERAMACHI BACKSTRIP stays LEAN (T019, research item 9, capitals only): the rim temples
# are part of the defensive belt, and the strip BEHIND each (between temple and rampart)
# is the temples' own back ground + the patrol strip - never packed housing. Monk houses
# are the temples' own and may stand there.


# THE FABRIC HITS THE BUDGET'S BAND TARGETS (T006): the 018 budget is the housing
# authority, so each band's drawn count lands on its dwelling_target - yashiki compounds
# and detached samurai houses by record count, terraces by their UNIT count (one roof,
# `units` households), packed rows by dwelling-kind buildings in the machi-family
# districts. Tolerance max(2, 5%) absorbs seat jitter without permitting a quietly-short
# band (the Minami sign-off lesson, applied at band granularity).


# A TERRACE IS A RANGE (T005): the record models ONE roof over several household cells;
# a single-cell "terrace" is a detached house miscoded, and would double-count against
# the band targets. Runs wherever the record appears.


# A JOSUI-IDO SITS ON THE BURIED MAIN (research 021 item 4): from the settling basin at
# the gate the mokuhi trunk mains run under the WAYS and the laterals under the roji -
# Edo branched its pipes under the tenement alleys to the josui-ido courts - so a
# cistern-well stands within the band (900 real ft of the terminus; the DISCLOSED
# calibrated liberty - Edo's mains ran kilometers, a young domain system serves its two
# gate-quarter blocks) and within 30px of some way. A dug draw-well (no kind) is untouched.


# THE KIDO MESH BARS THE MACHI MOUTHS (research 021 item 6): every street mouth into an
# in-wall machi district carries its night-barred kido. The mouths come from settlement.
# machi_mouths - the SAME source the placer reads - so placement and validation cannot
# disagree (the bridge_carried_ways doctrine).
# ...and the mesh is a KNOB, not a law (GM 2026-08-10): interior ward gates may be right
# for one city and wrong for the next, so meta(ward_gates=False) turns the whole doctrine
# off for a map that does not use them. It is an explicit declaration, never an absence -
# a map that simply forgot its kido still fails.


# EVERY GATE'S ROAD JOINS THE RING ROAD (GM 2026-08-09, the capital's side gates: both
# trunk-road polylines STARTED at the gate point on the wall, so the road reached the gate
# from outside while inside the gate opened onto 90 ft of bare ground 30px short of the
# ring - a door to nowhere, and invisible because no check watched gate-to-ring
# connectivity. A walled city's gate traffic distributes along the ring, so SOME way (the
# Imperial road, a trunk road, or a street) must pass the gate AND meet the ring - by a
# vertex near it or by crossing it outright.
