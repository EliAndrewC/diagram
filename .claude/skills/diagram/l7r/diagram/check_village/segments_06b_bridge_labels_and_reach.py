"""Gate segments (bridge labels and reach; keys 0360-0386) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from l7r.diagram.settlement import bridge_crossed_waters

from .common_01_geometry import seg_dist
from .common_03_capacity import _UNBOUND, _kept

# A DECK LANDS PAST ITS BANKS (GM 2026-08-09, tightened from ends-reach-the-edge): every
# CORNER of the deck clears the crossed water's edge onto dry ground. The ends-based rule
# let an oblique deck pass with a corner sitting exactly AT the water's edge (the capital's
# east deck landed 0.0 ft), which reads structurally impossible - a real abutment sill sits
# BACK from the channel edge so scour cannot undercut the bearing (settlement.LANDING_FT
# holds the research). s.bridges() draws LANDING_FT (10 real ft) of landing per side; the
# floor here is 6 ft so local water curvature under a deck does not flap the gate. A
# standalone FOOTPLANK keeps its deliberately short PLANK_ABUTMENT (GM 2026-07-22) and is
# floored at 2 ft. Real feet, converted via meta.ftpx. The crossed water is the WIDEST
# watercourse under the deck's seat, from the same shared source both bridging sides read;
# footprint family: gap VERDICT, measured on the deck's four real corners.


def _seg_0360__b_ftpx(*, meta: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 360 (b_ftpx) - body verbatim from the legacy gate() (feature 022)."""
    b_ftpx = float(meta.get("ftpx", 1) or 1)
    return _kept(locals(), ('b_ftpx',))


def _seg_0361__b_short() -> dict[str, Any]:
    """Gate segment 361 (b_short) - body verbatim from the legacy gate() (feature 022)."""
    b_short = []  # type: ignore[var-annotated]
    return _kept(locals(), ('b_short',))


def _seg_0362__b_dry() -> dict[str, Any]:
    """Gate segment 362 (b_dry) - body verbatim from the legacy gate() (feature 022)."""
    b_dry: list[str] = []
    return _kept(locals(), ('b_dry',))


def _seg_0363__b_1(
    *,
    M: Any = _UNBOUND,
    b: Any = _UNBOUND,
    b_crossed: Any = _UNBOUND,
    b_cw: Any = _UNBOUND,
    b_cx: Any = _UNBOUND,
    b_cy: Any = _UNBOUND,
    b_d: Any = _UNBOUND,
    b_dry: Any = _UNBOUND,
    b_floor: Any = _UNBOUND,
    b_ftpx: Any = _UNBOUND,
    b_hl: Any = _UNBOUND,
    b_hw: Any = _UNBOUND,
    b_pts: Any = _UNBOUND,
    b_short: Any = _UNBOUND,
    b_su: Any = _UNBOUND,
    b_sv: Any = _UNBOUND,
    b_th: Any = _UNBOUND,
    b_ux: Any = _UNBOUND,
    b_uy: Any = _UNBOUND,
    b_wid: Any = _UNBOUND,
    i: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 363 (b, b_crossed, b_cw, b_cx) - body verbatim from the legacy gate() (feature 022)."""
    for b in M.get("bridges", []):
        b_th = math.radians(b.get("rot", 0.0))
        b_ux, b_uy = math.cos(b_th), math.sin(b_th)
        b_hl, b_hw = b["span"] / 2, b["w"] / 2
        b_crossed: Any = None  # type: ignore[no-redef]
        b_cw = 0.0
        for b_pts, b_wid in bridge_crossed_waters(M):
            b_d = min(seg_dist(b["x"], b["y"], b_pts[i], b_pts[i + 1]) for i in range(len(b_pts) - 1))
            if b_d <= b_wid / 2 + 2 and b_wid > b_cw:
                b_crossed, b_cw = b_pts, b_wid
        if b_crossed is None:
            b_dry.append(f"({round(b['x'])},{round(b['y'])}) span {b['span']:.0f}")
            continue  # no water under the seat: bridges_seat_on_water fires below; the span rule has nothing to measure
        b_floor = (2.0 if b.get("foot") else 6.0) / b_ftpx
        for b_su, b_sv in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            b_cx = b["x"] + b_su * b_ux * b_hl - b_sv * b_uy * b_hw
            b_cy = b["y"] + b_su * b_uy * b_hl + b_sv * b_ux * b_hw
            if min(seg_dist(b_cx, b_cy, b_crossed[i], b_crossed[i + 1]) for i in range(len(b_crossed) - 1)) < b_cw / 2 + b_floor:
                b_short.append(f"({round(b['x'])},{round(b['y'])}) span {b['span']:.0f} on ~{b_cw:.0f}px water")
                break
    return _kept(locals(), ('b', 'b_crossed', 'b_cw', 'b_cx', 'b_cy', 'b_d', 'b_dry', 'b_floor', 'b_hl', 'b_hw', 'b_pts', 'b_short', 'b_su', 'b_sv', 'b_th', 'b_ux', 'b_uy', 'b_wid', 'i'))


# A DECK MUST SIT ON WATER AT ALL (settlement-review 2026-08-10): Shiro Daika's towpath
# plank kept its seat when the drain's re-route moved the ford, and it lay on bare bank for
# a whole feature - bridges_span_their_water silently skipped it (nothing to measure) and no
# other rule owned the case. A check that never runs looks exactly like a check that passes.
# BANK-PARALLEL WORKS FOLLOW THEIR BANK (GM 2026-08-10: "when we originally rendered the
# domain granaries and the imperial granary, they were aligned with the river. However, at
# a certain point, it looks like the angle of the river changed slightly, but the angle of
# the granaries did not"). A quay granary row is laid ALONG the water it loads from, and a
# jetty runs ACROSS it - both angles are properties of the bank, not constants, so a
# re-routed river must drag them or they read as a row built by someone who could not see
# the water. Same family as towpath_hugs_the_bank: derive the angle from the CURRENT
# polyline, never keep a rot that was right before the re-route.


def _seg_0364__bp_riv(*, M: Any = _UNBOUND, cn9: Any = _UNBOUND, w9: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 364 (bp_riv, cn9, w9) - body verbatim from the legacy gate() (feature 022)."""
    bp_riv = [w9["poly"] for w9 in M.get("streams", [])] + [cn9["poly"] for cn9 in M.get("canals", [])]
    return _kept(locals(), ('bp_riv', 'cn9', 'w9'))


def _seg_0365__waterside_works_follow_the_bank(
    *,
    M: Any = _UNBOUND,
    bp_bad: Any = _UNBOUND,
    bp_bear: Any = _UNBOUND,
    bp_bearing: Any = _UNBOUND,
    bp_d: Any = _UNBOUND,
    bp_f: Any = _UNBOUND,
    bp_key: Any = _UNBOUND,
    bp_off: Any = _UNBOUND,
    bp_riv: Any = _UNBOUND,
    bp_want: Any = _UNBOUND,
    check: Any = _UNBOUND,
    d9: Any = _UNBOUND,
    i9: Any = _UNBOUND,
    px: Any = _UNBOUND,
    py: Any = _UNBOUND,
    wp9: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 365 (waterside_works_follow_the_bank) - body verbatim from the legacy gate() (feature 022)."""
    if bp_riv:

        def bp_bearing(px: float, py: float) -> tuple[float, float]:
            bp_best = (1e9, 0.0)
            for wp9 in bp_riv:
                for i9 in range(len(wp9) - 1):
                    d9 = seg_dist(px, py, wp9[i9], wp9[i9 + 1])
                    if d9 < bp_best[0]:
                        bp_best = (d9, math.degrees(math.atan2(wp9[i9 + 1][1] - wp9[i9][1], wp9[i9 + 1][0] - wp9[i9][0])))
            return bp_best

        bp_bad = []
        for bp_key, bp_want in (("granaries", 0.0), ("jetties", 90.0), ("tanning_yards", 0.0), ("dye_yards", 0.0)):  # rows and wash yards lie ALONG the bank; stages run ACROSS it
            for bp_f in M.get(bp_key, []):  # both keys hold records, never raw polygons
                bp_d, bp_bear = bp_bearing(bp_f["x"], bp_f["y"])
                if bp_d > 140:
                    continue  # not a waterside instance (an inland store is not bank-parallel)
                bp_off = abs((float(bp_f.get("rot", 0.0)) - bp_bear - bp_want) % 180.0)
                bp_off = min(bp_off, 180.0 - bp_off)
                if bp_off > 4.0:
                    bp_bad.append((bp_key, round(bp_f["x"]), round(bp_f["y"]), round(bp_off, 1)))
        check(
            "waterside_works_follow_the_bank",
            not bp_bad,
            f"waterside work(s) off their bank's angle (key, x, y, degrees off): {sorted(set(bp_bad))[:4]} - a quay granary row lies "
            f"ALONG the water and a jetty runs ACROSS it; recompute the rot from the CURRENT river polyline at that point (a bank "
            f"angle is derived geometry, not a constant that survives a re-route)",
        )
    return _kept(locals(), ('bp_bad', 'bp_bear', 'bp_bearing', 'bp_d', 'bp_f', 'bp_key', 'bp_off', 'bp_want'))


# A CAPTION SITS BY WHAT IT NAMES (GM 2026-08-10: "the aqueduct labels are no longer
# correctly placed - the settling basin one is not even really next to the actual feature,
# it is on top of the city walls, and the intake weir label is way far away from the actual
# thing it is labeling"). `labels_clear_of_other_buildings` stops a caption COVERING the
# wrong thing; nothing stopped one drifting away from the RIGHT thing. Point-feature
# captions (the water furniture, the works) are checked against the feature their text
# names, because those are the ones a standoff ladder can push far from their subject.


# ...AND NOT ON THE RAMPART (GM 2026-08-10: the settling-basin caption "is on top of the
# city walls"). A caption laid across the wall or the moat reads as naming the defenses,
# and the wall's own ink swallows the text. The label battery protects FOOTPRINTS from
# captions; the wall is a polyline, so nothing covered it.


# WORKER HOUSING SITS WITH THE WORK (GM 2026-08-10: "I would expect the housing for those
# facilities to be close to those businesses and granaries... since the whole point of those
# houses being outside the city instead of inside of it is that those are the housing for
# the workers who work those facilities"). An extramural dwelling exists BECAUSE something
# outside needs hands on it - the quay, the granaries, the gate market's inns and stables.
# A row across the channel from all of it is a suburb with no reason, and the ruling that
# allowed extramural housing at all (2026-08-10, the wharf hamlet) was granted on exactly
# that basis. Measured to the nearest workplace, not to the wall.


# THE FUNERARY GROUND STARTS AT THE WALL AND RUNS OUTWARD (GM 2026-08-10, researched; the
# why and the sources are in research/cities/capitals.md "How far outside the wall does the
# funerary ground sit?"). Nothing in the record holds it far off: ritual pollution is a
# BINARY satisfied by being outside at all (Kyoto's Injo-ji stood ON the Odoi rampart and
# marked the boundary of the living), fire is worth 50 ft by code and was never a siting
# driver at all (Edo cremated on open pyres inside its own temple precincts for 250 years
# and moved them in 1873 for the STENCH), and what actually set the distance was worthless
# ground on the road out of the gate. In every attested case the complex's ENTRANCE is at or
# just past the wall and the field runs outward - so a compact feature at 900+ ft is drawing
# the FAR end of a historical site at its NEAR end, which is what made the capital's read
# unmotivated.


# A STREET EARNS ITS LENGTH ON BOTH SIDES (GM 2026-08-10: "several city streets extend out
# into empty space with nothing on either side of them and also not leading to anywhere...
# this is essentially a road to nowhere check"). `city_streets_have_buildings` measures ONE
# side and excuses frontage onto claimed open ground, which is right for a street along a
# drill ground or a firebreak - but a long stretch bare on BOTH sides is a street nobody
# walks, and the GM accepts that placement order may lay one down before that is knowable,
# so the CHECK is the backstop. Claimed ground does not excuse this one: the point is that
# the street serves nothing, not that the ground beside it is spoken for.


# A SHOP FACES THE WAY IT FRONTS (GM 2026-08-10: "at the northern gate market there is a row
# of several merchant shops, and then just one of those shops is oriented facing away from
# the road"). A storefront IS its street face - the noren, the counter and the goods are on
# that side - so a shop within a frontage band of a way must open toward it. The glyph's
# front is local +y, as with the theater stage, so after `rot` it points (-sin, cos).
# Placement gets this right when it seats the file; what it cannot see is a LATER re-lay
# that moves the way, or a hand-placed file whose setback sign flips one seat.


# A SLUICE GATE SITS ON ITS CHANNEL'S CENTERLINE (GM 2026-08-10, after the same defect
# recurred across several re-lays: "the northern sluice gate is still misaligned with the
# irrigated channel that it is gating... I know we have automated checks for this, so I'm
# not sure how this keeps happening over and over again"). It kept happening because
# `sluice_gates_on_water` measures to the BANK: a gate 15.8px from the centerline of a 22px
# channel sits 4.8px past the bank, inside that rule's 6px tolerance, and passed - while
# reading as a frame floating beside the water. A sluice's frame spans BANK TO BANK, so the
# only correct seat is the centerline itself. Tolerance is a fraction of the channel's own
# half-width (a wide river's gate may sit a little off; a narrow ditch's may not) with a
# small absolute floor for the linework.


# A ROAD DOES NOT SIMPLY STOP (GM 2026-08-10: "the road leading to the southwest gate comes a
# little way into the city and then just stops... we expect that caravans coming into the city
# would need to be able to take this road in order to reach the castle keep"). A trunk road
# exists to carry traffic THROUGH: each end must leave the map, meet another road, or join a
# street/ring bed a wagon can turn onto. An end that dies in open ground is a road to nowhere.


# NO WAY STANDS IN WATER WITHOUT A DECK (GM 2026-08-10: "roads should not overlap with water
# without a bridge present"). `roads_bridge_water` already demands a deck wherever a CARRIED
# way's centerline CROSSES a watercourse's centerline - but it reads only the ways
# bridge_carried_ways names (the trunk roads, streets and the ring), and it tests crossings
# rather than OVERLAP. So an alley whose bed laps a stream's bed, or a way that runs into the
# water and stops, sails past it: the capital's wharf shore path lay in the moat drain for
# 40 px with no plank. This one samples EVERY drawn way against every watercourse using both
# BEDS' widths - the question a reader asks of the picture is whether the paving and the water
# occupy the same ground, not whether two abstract centerlines intersect.


def _seg_0384__cn9_1(*, M: Any = _UNBOUND, cn9: Any = _UNBOUND, w9: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 384 (cn9, w9, wd_waters) - body verbatim from the legacy gate() (feature 022)."""
    wd_waters = [(w9["poly"], float(w9.get("w", 9))) for w9 in M.get("streams", [])] + [(cn9["poly"], float(cn9.get("w", 12))) for cn9 in M.get("canals", [])]
    return _kept(locals(), ('cn9', 'w9', 'wd_waters'))


def _seg_0385__wd_waters(*, M: Any = _UNBOUND, wd_waters: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 385 (wd_waters) - body verbatim from the legacy gate() (feature 022)."""
    if M.get("moat"):
        wd_waters.append((list(M["moat"]) + [M["moat"][0]], float(M.get("moat_width", 22))))
    return _kept(locals(), ('wd_waters',))


def _seg_0386__cs9(*, M: Any = _UNBOUND, cs9: Any = _UNBOUND, wd_waters: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 386 (cs9, wd_waters) - body verbatim from the legacy gate() (feature 022)."""
    for cs9 in M.get("castles", []):
        if cs9.get("moat"):
            wd_waters.append((list(cs9["moat"]) + [cs9["moat"][0]], float(cs9.get("moat_width", 22))))
    return _kept(locals(), ('cs9', 'wd_waters'))
