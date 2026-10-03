"""Where a track leaves the placed cluster: the connector's gateway and its start on the exit strip, and the spur's origin
facing the field. Split from `track.py` (feature 316) to give it room for its claims; `track.py` re-exports every name.

Research: gateway plumbing - NONE
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import cast

from l7r.diagram.settlement import Settlement, seg_intersect, segments_cross

from ..consts import SPUR_SETBACK, TRACK_FABRIC_GAP, Poly, Pt
from .fabric import _homestead_polys
from .geom import push_clear_of_fabric, push_out_of


def _cluster_gateway(s: Settlement, seat: Mapping[str, object], fallback: Pt) -> Pt:
    """Where a track leaves the settlement - measured from the PLACED houses, not the predicted band.

    FR-002, and feature 126's unfinished task T009. Until now the gateway came from
    `skeleton_layout(plan.lane_skeleton, 0, 0, seat["lat"], seat["dep"])` - a pure function of the
    rolled knob and the SEAT BAND, which is where the cluster was PREDICTED to go. The houses land
    where they land, and the two disagree; that mismatch is the recorded root of the
    `farmhouses_reach_a_way` defect that survived seventeen attempts.

    It also had a concrete cost the moment the track moved after the houses: a band-derived gateway
    can sit INSIDE the house cloud, and a track starting there has to leave through the settlement.
    One house on the reference hamlet ended up within 14 px of the connector's centerline - the
    threshold the retired `houses_off_corridors` check measured - and no amount of routing around the fabric fixed it,
    because the route's own start was in the middle of it.

    So: where the seating reserved an exit strip, the gateway is ON it - along the strip from its start, past the
    farthest house and corridor that hangs on it (feature 287 M4b; `gate_on_the_strip`). Where there is none, take the
    cloud's own extent along the seat axes and put the gateway on its DOWNSLOPE edge, clear of the last house. The fallback is the old band point, for the case where no house has been
    placed yet - which cannot happen in the shipped order, but a helper that assumes its caller is
    the failure mode this file has met repeatedly.

    Research:
        track leaves downslope - research/questions/0081-village-lanes.drawing.html: from the cluster's downslope edge, or along
            the exit strip
        gateway clear of what stands - UNRESEARCHED: `TRACK_FABRIC_GAP` plus 8 px past the farthest house, well or yard
    """
    hs = s.M.get("houses") or []
    if not hs:
        return fallback
    ax, ay = cast(Pt, seat["along"])
    ox, oy = cast(Pt, seat["out"])
    xs = [float(h["x"]) for h in hs]
    ys = [float(h["y"]) for h in hs]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    # how far the cloud actually reaches, along each seat axis
    out_reach = max((x - cx) * ox + (y - cy) * oy for x, y in zip(xs, ys, strict=False))
    along_mid = sum((x - cx) * ax + (y - cy) * ay for x, y in zip(xs, ys, strict=False)) / len(xs)
    # THE GATEWAY STANDS ON THE EXIT STRIP (feature 287, plan M4b): where the seating reserved one, the track leaves along
    # it - measured from the strip's own start (the seat's center) rather than from the cloud's mean - so the reserved tree
    # every corridor hangs from runs on into the connector, and a corridor the web draws along the strip meets it
    # (`corridors.corridor_chain`). Off the strip, a corridor walked to the track would cross unreserved ground.
    exit_strip = s.M.get("access_exit")
    if exit_strip:
        cx, cy = float(exit_strip[0][0]), float(exit_strip[0][1])
        # ...ALONG THE STRIP ITSELF, AND PAST EVERY CORRIDOR HANGING FROM IT (feature 287 wave 6): the web draws the strip as a
        # tree lane from its innermost attachment to where the connector starts (`tree.strip_run`), and the seating judged it
        # to its end - so the connector starts ON it (the strip is turned off the outward bearing where that was refused,
        # `access.exit_bearing`) and no nearer the center than the farthest corridor on it
        (ex, ey), d = (float(exit_strip[1][0]) - cx, float(exit_strip[1][1]) - cy), math.dist(exit_strip[0], exit_strip[1]) or 1.0
        ox, oy = ex / d, ey / d
        ends = [c["pts"][-1] for c in s.M.get("access_corridors") or [] if len(c.get("pts") or ()) >= 2]
        on = [(float(q[0]) - cx) * ox + (float(q[1]) - cy) * oy for q in ends if abs(-(float(q[0]) - cx) * oy + (float(q[1]) - cy) * ox) <= 1.5]
        out_reach = max([(x - cx) * ox + (y - cy) * oy for x, y in zip(xs, ys, strict=False)] + on)
        along_mid = 0.0
    # THE CLOUD IS NOT ONLY THE HOUSES. Wells, byres, sheds and yards are seated in
    # `stage_appurtenances`, which runs BEFORE the track, and some of them stand outside the house
    # extent. A gateway measured from houses alone landed 3.6 px from a well on the reference hamlet
    # and the connector drew straight over it - `features_do_not_overlap`, wells x lanes.
    #
    # So walk outward until the gateway clears every standing thing by the track's own gap. Stepping
    # rather than solving: the fabric is an arbitrary set of polygons, the step is cheap, and a
    # bounded walk cannot fail to terminate the way a solve can.
    fabric = [poly for poly, _owner, _kind in _homestead_polys(s)]
    return push_clear_of_fabric((cx + ax * along_mid, cy + ay * along_mid), (ox, oy), out_reach + TRACK_FABRIC_GAP + 8.0, fabric)


STRIP_STEP_PX = 6.0
"""The step a gateway on the exit strip is walked out along it until it clears the field's envelope (`gate_on_the_strip`):
`push_clear_of_fabric`'s own step."""


def gate_on_the_strip(s: Settlement, envelope: Poly, gate: Pt) -> Pt:
    """The connector's start: `gate` pushed out of the field's `envelope` (`push_out_of`, the rule the track has always kept),
    but where the seating reserved an exit strip, ON it - walked out along the strip until the envelope leaves it clear, to
    the strip's end at most - since the web draws the strip as a tree lane up to the connector's start (`tree.strip_run`,
    feature 287 wave 6), and a start pushed a few feet off it left the strip ending in a hook (cohort seed 37: 8 ft)."""
    strip = s.M.get("access_exit")
    if not strip:
        return push_out_of(envelope, gate, SPUR_SETBACK)
    a, b = (float(strip[0][0]), float(strip[0][1])), (float(strip[1][0]), float(strip[1][1]))
    d = math.dist(a, b) or 1.0
    t = min(d, max(0.0, ((gate[0] - a[0]) * (b[0] - a[0]) + (gate[1] - a[1]) * (b[1] - a[1])) / d))
    while True:
        g = (a[0] + (b[0] - a[0]) * t / d, a[1] + (b[1] - a[1]) * t / d)
        if push_out_of(envelope, g, SPUR_SETBACK) == g or t >= d:
            return g
        t = min(d, t + STRIP_STEP_PX)


def _cluster_edge_toward(s: Settlement, target: Pt, fallback: Pt) -> Pt:
    """The point on the placed cluster's edge that FACES `target`.

    NOT `_cluster_gateway`, and confusing the two cost the reference map its field access. That helper
    pushes outward along `seat["out"]` - the downslope exit, which is where a track LEAVES for the
    wider world and by construction points AWAY from the field. Feature 128 re-originated both tracks
    from the placed houses and reused it for the spur as well, so the spur began on the far side of
    the settlement from its own destination, ran 104 degrees off the field bearing, and dead-ended in
    the shelter belt RECEDING from the paddy: 281 ft from the field envelope at its tip against 248 ft
    at its start. Found by `settlement-review`; the gate could not see it, because
    `lanes_reach_something` is satisfied by an end lying near a house and a way dying in the trees
    still fronts one.

    A spur goes TO somewhere. Its origin therefore belongs on the side of the cluster that faces the
    somewhere - measured from the placed houses like everything else in this feature, not from the
    seat band.

    Research:
        spur starts facing the field - research/questions/0081-village-lanes.drawing.html: on the cluster's edge toward its target
        spur origin clear of the houses - UNRESEARCHED: `TRACK_FABRIC_GAP` plus 8 px past the farthest house toward the target
        origin on the houses' bank - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: stopped
            14 px plus half the brook short of it, the brook crossed at a ford
    """
    hs = s.M.get("houses") or []
    if not hs:
        return fallback
    xs = [float(h["x"]) for h in hs]
    ys = [float(h["y"]) for h in hs]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    ux, uy = target[0] - cx, target[1] - cy
    n = math.hypot(ux, uy) or 1.0
    ux, uy = ux / n, uy / n
    reach = max(((x - cx) * ux + (y - cy) * uy for x, y in zip(xs, ys, strict=False)), default=0.0)
    fabric = [poly for poly, _owner, _kind in _homestead_polys(s)]
    edge = push_clear_of_fabric((cx, cy), (ux, uy), reach + TRACK_FABRIC_GAP + 8.0, fabric)
    # ...AND ON THE HOUSES' OWN BANK (feature 261). Pushed past the furthest house by the fabric gap, the origin landed
    # across a brook that runs close by - Inashiro's by 20 ft - so the spur began on the field's side of the water, never
    # crossed it, and was a stub too short to draw: the hamlet had no way to its rice. Where the push crosses a stream,
    # the origin stops short of it by the router's own 14 px off water, and the spur crosses at a ford like any other way.
    for f in s.M.get("streams") or []:
        poly = [(float(x), float(y)) for x, y in (f.get("poly") or [])]
        for a, b in zip(poly, poly[1:], strict=False):
            if segments_cross((cx, cy), edge, a, b):
                x = seg_intersect((cx, cy), edge, a, b)
                if x is not None:
                    back = math.dist((cx, cy), x) - 14.0 - float(f.get("w", 8.0)) / 2
                    edge = (cx + ux * back, cy + uy * back)
    return edge
