"""Gate segments (city gates and wall towers; keys 0563_078-0563_125) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from l7r.diagram.settlement import kido_bar_deg, lane_runs, lane_through_gate, sat_overlap

from .common_01_geometry import point_in_poly, rect_corners, seg_dist
from .common_02_overlap_policy import footprint_on_line, kido_quads
from .common_03_capacity import _UNBOUND, _kept

# a lane heading at a NEIGHBORHOOD wall (a ward fence) should reach it and end at a KIDO GATE - the
# commoners' lanes pull in to the gates they pass through to work in the samurai quarter. Stopping a
# sliver short, or meeting the fence with no gate, both read as a mistake. (Stopping short of the
# MAIN city wall is fine - that is the city's own edge, not a neighborhood boundary.)


# THE KIDO SQUARES TO WHAT IT BARS (GM 2026-07-26, refining the 2026-07-24 fence rule).
# A kido is a gate across a WAY: it is shut at night to stop traffic, so the roofed bar
# stands SQUARE ACROSS THE LANE that runs through it, and the fence meets the gate at
# whatever angle the fence happens to run. The two readings agree wherever a lane crosses
# its fence squarely - which is most crossings, and why the fence rule held up for two
# days - and diverge exactly where a lane meets the fence obliquely: Tango's SW ring-road
# gate, drawn on its ~44deg fence jog while the ring road passed at ~172deg, sat 38 degrees
# off square to the road it was supposedly barring and read as a glyph dropped on the
# roadbed. Only a gate with NO lane through it falls back to the fence tangent (still never
# an axis-aligned stamp on a slanted run - Nagahara's SW kido, Tango's S jog, both frozen
# in pool/regressions/). lane_through_gate/kido_bar_deg are the SAME functions s.ward
# places with, so placer and checker cannot drift. s.kido records the drawn angle as 'rot'
# (legacy manifests fall back to the horizontal flag: True -> 90, False -> 0); it must match
# within ~7 degrees mod 180.


def _seg_0563_080__wards_k(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.080 (wards_k) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital'):
        wards_k = M.get("wards", [])
    return _kept(locals(), ('wards_k',))


def _seg_0563_081__kido_aligned_with_ward_fence(
    *,
    M: Any = _UNBOUND,
    b2: Any = _UNBOUND,
    best2: Any = _UNBOUND,
    box_on_lane: Any = _UNBOUND,
    c: Any = _UNBOUND,
    check: Any = _UNBOUND,
    d8: Any = _UNBOUND,
    diff8: Any = _UNBOUND,
    gbox: Any = _UNBOUND,
    got8: Any = _UNBOUND,
    gpoly: Any = _UNBOUND,
    half: Any = _UNBOUND,
    i8: Any = _UNBOUND,
    kd2: Any = _UNBOUND,
    kd3: Any = _UNBOUND,
    kido_off: Any = _UNBOUND,
    lane8: Any = _UNBOUND,
    pts: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    want8: Any = _UNBOUND,
    wards_k: Any = _UNBOUND,
    wd2: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 563.081 (kido_aligned_with_ward_fence, kido_guard_box_clear_of_lanes) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and wards_k:
        kido_off = []
        for kd2 in M.get("kido", []):
            best2 = None  # (distance, tangent angle) of the nearest ward-fence segment
            for wd2 in wards_k:
                b2 = wd2["boundary"]
                for i8 in range(len(b2) - 1):
                    d8 = seg_dist(kd2["x"], kd2["y"], b2[i8], b2[i8 + 1])
                    if best2 is None or d8 < best2[0]:
                        best2 = (d8, math.degrees(math.atan2(b2[i8 + 1][1] - b2[i8][1], b2[i8 + 1][0] - b2[i8][0])))
            if best2 is None or best2[0] > 16:
                continue  # a free-standing kido (nothing near enough to align to)
            lane8 = lane_through_gate(M, kd2["x"], kd2["y"], best2[1])
            want8 = (kido_bar_deg(lane8[0], best2[1]) if lane8 else best2[1]) % 180.0
            got8 = float(kd2["rot"]) % 180.0 if "rot" in kd2 else (90.0 if kd2.get("horizontal") else 0.0)
            diff8 = abs(got8 - want8)
            diff8 = min(diff8, 180.0 - diff8)
            if diff8 > 7.0:
                kido_off.append([round(kd2["x"]), round(kd2["y"]), round(diff8), "lane" if lane8 else "fence"])
        check(
            "kido_aligned_with_ward_fence",
            not kido_off,
            f"ward gate(s) not square to what they bar (x, y, degrees off, what it should follow): {kido_off} - a kido "
            f"shuts a WAY, so its roofed bar stands SQUARE ACROSS the lane running through it; only a gate with no lane "
            f"through it follows the local fence tangent (s.ward computes both; pass rot= to s.kido for a hand-placed gate)",
        )
        # ...AND THE GUARD BOX STANDS ON THE VERGE, NOT IN THE ROAD (GM 2026-07-26). The watch
        # box beside the gate is a small building - the one solid thing in the kido group - and
        # a patrol road or street with a shack in its bed is not passable. It is not covered by
        # the overlap registry (the whole kido group is deliberately overlap-exempt, since the
        # bar MUST span the lane and the fence), so it needs this one rule of its own. The
        # placement side slides the box out until it clears every bed by a ~12 ft verge; this
        # fires only on an actual encroachment of the drawn bed, leaving that verge as slack.
        box_on_lane = []
        for kd3 in M.get("kido", []):
            gbox = kd3.get("guard")
            if not gbox:
                continue  # a legacy manifest that never recorded the box
            gpoly = [(float(c[0]), float(c[1])) for c in gbox]
            if any(footprint_on_line(gpoly, pts, half) for pts, half in lane_runs(M)):
                box_on_lane.append([round(kd3["x"]), round(kd3["y"])])
        check(
            "kido_guard_box_clear_of_lanes",
            not box_on_lane,
            f"ward gate(s) whose guard box stands IN a roadbed: {box_on_lane} - the gate's watch box is a building on the "
            f"verge beside the way, never an obstruction in it (s.kido slides it clear; a curving ring road is the case "
            f"straight-line arithmetic misses)",
        )
    return _kept(locals(), ('b2', 'best2', 'box_on_lane', 'c', 'd8', 'diff8', 'gbox', 'got8', 'gpoly', 'half', 'i8', 'kd2', 'kd3', 'kido_off', 'lane8', 'pts', 'want8', 'wd2'))


def _seg_0563_082__w(*, M: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.082 (w) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        w = M.get("wall") or []
    return _kept(locals(), ('w',))


def _seg_0563_083__gates(*, M: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.083 (gates) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        gates = M.get("gates", [])
    return _kept(locals(), ('gates',))


def _seg_0563_084__inwall(*, meta: Any = _UNBOUND, px: Any = _UNBOUND, py: Any = _UNBOUND, scale: Any = _UNBOUND, w: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.084 (inwall) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):

        def inwall(px: float, py: float) -> bool:
            return len(w) >= 3 and point_in_poly(px, py, w)

    return _kept(locals(), ('inwall',))


def _seg_0563_089__gstructs(*, M: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.089 (gstructs) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        gstructs = M.get("gate_structs", [])
    return _kept(locals(), ('gstructs',))


# ... and the guard house + inspection station sit AT THE GATE THROAT - hard by the opening,
# flanking the road as it enters - not walked back along the wall. Historically decisive (see
# settlements.md 'Historical grounding'): an inspection/tax barrier only works where traffic
# is forced single-file, and the gate passage is that one chokepoint in the whole wall; set
# the station back along the wall and arrivals disperse into the streets before ever reaching
# it. So each must sit within ~70px of its gate vertex (the built placement lands ~35-45px in).
# The looser city_inspection_station_at_each_gate / city_gate_has_guardhouse radii (160/180)
# deliberately have SLACK for the barbican, and would wave through the old far placement that
# walked the pair 80/144px along the wall - THIS check is what gives that rule teeth.


# the gate's own (smaller) TOWER must sit AT its gate - the CLOSEST tower to the opening, not
# marooned out along the curtain with a mural bastion seated nearer (GM 2026-07-22: the S gate's
# tower had walked to arc 118 to dodge a ward-gate kido, reading as a random small tower
# mid-wall while a mamian sat at the gate). A gate tower is a gate_structs "tower"; every other
# wall_tower is a mamian. When one flank of the gate is blocked the tower takes the OTHER flank
# at the opening (city_wall does this), so it should never be out-distanced by a mural.


def _seg_0563_096__g_3(*, g: Any = _UNBOUND, gstructs: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.096 (g, gate_towers_xy) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        gate_towers_xy = [(g["x"], g["y"]) for g in gstructs if g.get("kind") == "tower"]
    return _kept(locals(), ('g', 'gate_towers_xy'))


def _seg_0563_097__gtx(
    *, M: Any = _UNBOUND, gate_towers_xy: Any = _UNBOUND, gtx: Any = _UNBOUND, gty: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND, t: Any = _UNBOUND
) -> dict[str, Any]:
    """Gate segment 563.097 (gtx, gty, murals_xy, t) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        murals_xy = [(t["x"], t["y"]) for t in M.get("wall_towers", []) if not any(abs(t["x"] - gtx) < 2 and abs(t["y"] - gty) < 2 for gtx, gty in gate_towers_xy)]
    return _kept(locals(), ('gtx', 'gty', 'murals_xy', 't'))


def _seg_0563_098__stranded(*, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.098 (stranded) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        stranded = []  # type: ignore[var-annotated]
    return _kept(locals(), ('stranded',))


def _seg_0563_099__d_gate_tower(
    *,
    d_gate_tower: Any = _UNBOUND,
    d_nearest_mural: Any = _UNBOUND,
    g: Any = _UNBOUND,
    gate_towers_xy: Any = _UNBOUND,
    gates: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    murals_xy: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    stranded: Any = _UNBOUND,
    tx: Any = _UNBOUND,
    ty: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 563.099 (d_gate_tower, d_nearest_mural, g, stranded) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        for g in gates:
            if not gate_towers_xy:
                continue
            d_gate_tower = min(math.hypot(tx - g[0], ty - g[1]) for tx, ty in gate_towers_xy)
            d_nearest_mural = min((math.hypot(tx - g[0], ty - g[1]) for tx, ty in murals_xy), default=1e9)
            if d_nearest_mural + 12 < d_gate_tower:  # a mamian sits meaningfully closer to the gate than the gate's own tower
                stranded.append((round(g[0]), round(g[1])))
    return _kept(locals(), ('d_gate_tower', 'd_nearest_mural', 'g', 'stranded', 'tx', 'ty'))


# a fortified city is TOWERED for enfilading fire along the wall face: guard towers spaced
# at regular intervals around the whole rampart (a bowshot apart), not only at the gates -
# so no long bare arc of wall sits uncovered. Spacing is judged by the widest angular gap
# between consecutive towers around the wall centroid.


def _seg_0563_101__towers(*, M: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.101 (towers) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        towers = M.get("wall_towers", [])
    return _kept(locals(), ('towers',))


def _seg_0563_102__p_1(*, meta: Any = _UNBOUND, p: Any = _UNBOUND, scale: Any = _UNBOUND, w: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.102 (p, wcx, wcy) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        wcx, wcy = sum(p[0] for p in w) / len(w), sum(p[1] for p in w) / len(w)
    return _kept(locals(), ('p', 'wcx', 'wcy'))


def _seg_0563_103__angs(*, meta: Any = _UNBOUND, scale: Any = _UNBOUND, t: Any = _UNBOUND, towers: Any = _UNBOUND, wcx: Any = _UNBOUND, wcy: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.103 (angs, t) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        angs = sorted(math.atan2(t["y"] - wcy, t["x"] - wcx) for t in towers)
    return _kept(locals(), ('angs', 't'))


# guard towers sit SQUARE to the wall (rotated to its tangent) rather than all axis-aligned -
# a tower on a slanted stretch slants with it. Each tower's recorded rotation must match the
# angle of the nearest wall edge (mod 90, since a square reads the same every 90 degrees).


def _seg_0563_106__ring2(*, meta: Any = _UNBOUND, scale: Any = _UNBOUND, w: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.106 (ring2) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        ring2: Any = list(w) + [w[0]]  # type: ignore[no-redef,unused-ignore]
    return _kept(locals(), ('ring2',))


def _seg_0563_107__misaligned(*, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.107 (misaligned) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        misaligned = []  # type: ignore[var-annotated]
    return _kept(locals(), ('misaligned',))


def _seg_0563_108__d(
    *,
    d: Any = _UNBOUND,
    edge_ang: Any = _UNBOUND,
    ek: Any = _UNBOUND,
    k: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    misaligned: Any = _UNBOUND,
    order: Any = _UNBOUND,
    ring2: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    t: Any = _UNBOUND,
    towers: Any = _UNBOUND,
    twr_off: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 563.108 (d, edge_ang, ek, misaligned) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        for t in towers:
            # THE TWO NEAREST EDGES, not just the nearest (GM 2026-07-25). A tower seated near a
            # VERTEX of the wall N-gon is legitimately square to EITHER of the runs that meet
            # there - placement takes its tangent from one side, and which side `seg_dist` calls
            # "nearest" can flip on a sub-pixel move. That is exactly what happened when the
            # martial hall's budget line grew Nagahara's derived ring by 1px: an untouched tower
            # at (1909, 1200) kept its rot of 80.4 while the nearest-edge lookup crossed from the
            # 80.4 deg run to the 61.3 deg one, and a correct tower failed. Scoring the best of
            # the two nearest edges makes the check read the geometry the way placement wrote it;
            # it does NOT weaken the rule, because an axis-aligned tower on a slanted stretch is
            # still off BOTH adjacent runs by more than the tolerance.
            order = sorted(range(len(ring2) - 1), key=lambda k: seg_dist(t["x"], t["y"], ring2[k], ring2[k + 1]))
            twr_off = 90.0
            for ek in order[:2]:
                edge_ang = math.degrees(math.atan2(ring2[ek + 1][1] - ring2[ek][1], ring2[ek + 1][0] - ring2[ek][0]))
                d = (t.get("rot", 0) - edge_ang) % 90
                twr_off = min(twr_off, d, 90 - d)
            if twr_off > 15:
                misaligned.append((round(t["x"]), round(t["y"])))
    return _kept(locals(), ('d', 'edge_ang', 'ek', 'misaligned', 'order', 't', 'twr_off'))


# the GATE FURNITURE - the guard house + inspection station that sit along the ring road just
# inside each gate - is likewise SQUARE TO THE WALL: rotated to the wall's LOCAL tangent at its
# own position (NOT the gate vertex's - the wall has already curved away by then), so the ring
# road runs lengthwise through it. Each is a rectangle (its long axis runs ALONG the wall), so
# its rotation must match the nearest wall edge angle mod 180 (a 180 deg flip is the same, a 90
# deg turn would stand it the wrong way across the road). Tolerance is TIGHTER than the towers'
# (6 vs 15 deg): the furniture rotation is set from the exact local edge angle, not the towers'
# chord-through-neighbors approximation, so a correctly-placed piece matches near-exactly - and
# the gates sit on shallow wall stretches (~8 deg), which a 15 deg window would wave through.


# ... and the guard house + inspection station are SEPARATE buildings: walked along a
# tightly-curving wall the two arcs can converge, and an inspection annex drawn through
# its guard house reads as a collision (GM, 2026-07)


# WALL FURNITURE STAYS OUT OF THE MOAT: a guard tower straddles the wall and may PROJECT a
# stride past its outer face (the horse-face bastion), but its footing must stand on the
# BERM, never in the water - a tight moat gap leaves a narrow berm, so a tower centered on
# the wall line pokes its outer face into the bed. Same for the gate towers and the guard
# house / inspection station. (Bridges are exempt - they span the moat by design.)


# THE WARD GATES STAND CLEAR OF THE WALL TOWERS: a kido hangs on the ward fence where a
# lane or the ring road crosses it, and the fence ends abut the rampart - so the LAST
# kido can land against a mural tower's footprint (its guard box read as "a small square
# building" inside the tower - GM, 2026-07). Both are overlap-EXEMPT classes (each sits
# on its own wall), so no generic pass catches the pair. The kido cannot move (it gates
# a fixed crossing), so the TOWER yields - city_wall(tower_skip=[...]) relocates it to
# the neighboring wall vertex.


def _seg_0563_120__k_hit(*, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.120 (k_hit) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        k_hit = []  # type: ignore[var-annotated]
    return _kept(locals(), ('k_hit',))


def _seg_0563_121__g_(
    *, M: Any = _UNBOUND, g_: Any = _UNBOUND, k_hit: Any = _UNBOUND, kc: Any = _UNBOUND, kd: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND, t: Any = _UNBOUND
) -> dict[str, Any]:
    """Gate segment 563.121 (g_, k_hit, kc, kd) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        for kd in M.get("kido", []):
            for kc in kido_quads(kd):
                if any(
                    sat_overlap(kc, rect_corners({"x": t["x"], "y": t["y"], "w": t.get("w", 38), "h": t.get("h", 38), "rot": t.get("rot", 0)}))
                    for t in M.get("wall_towers", []) + [g_ for g_ in M.get("gate_structs", []) if g_.get("kind") == "tower"]
                ):
                    k_hit.append((round(kd["x"]), round(kd["y"])))
                    break
    return _kept(locals(), ('g_', 'k_hit', 'kc', 'kd', 't'))


# a GATE TOWER (a gate's guard tower, or a mural tower) must not OVERLAP the gate's
# INSPECTION STATION or GUARD HOUSE (GM, 2026-07). The gate complex packs tight (guardhouse
# + inspection + tower + gateposts at each gate) and inspection stations are overlap-EXEMPT
# against the gate furniture, which had let a tower footprint STACK on the inspection post -
# each is a distinct building and they must sit CLEAR of one another, abutting not stacked.


def _seg_0563_123___gtowers(*, M: Any = _UNBOUND, g: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND, x: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.123 (_gtowers, g, x) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        _gtowers = [g for g in (M.get("wall_towers", []) + [x for x in M.get("gate_structs", []) if x.get("kind") == "tower"]) if "w" in g]
    return _kept(locals(), ('_gtowers', 'g', 'x'))


def _seg_0563_124___gfurn(*, M: Any = _UNBOUND, g: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND, x: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.124 (_gfurn, g, x) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        _gfurn = [g for g in ([x for x in M.get("gate_structs", []) if x.get("kind") in ("inspection", "guardhouse")] + M.get("inspection_stations", [])) if "w" in g]
    return _kept(locals(), ('_gfurn', 'g', 'x'))


def _seg_0563_125__gf_hit(*, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.125 (gf_hit) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        gf_hit = []  # type: ignore[var-annotated]
    return _kept(locals(), ('gf_hit',))
