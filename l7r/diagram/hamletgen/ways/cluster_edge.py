"""Where a way leaves the placed cluster: the connector's gateway, its start on the exit strip, and the spur's origin facing
the field.

Lifted out of `track.py` at the 1,000-line bar (feature 316, when the research claims were carried over feature 315's merge);
`track` re-exports all four, which `gateway.py`, `ways/__init__.py` and the tests name there. A leaf: nothing here reads a
name the tests monkeypatch on `track`.

Research: plumbing - NONE: each placement rule is claimed at its function
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import cast

from l7r.diagram.settlement import Settlement, seg_intersect, segments_cross

from ..consts import SPUR_SETBACK, TRACK_FABRIC_GAP, Poly, Pt
from .fabric import _homestead_polys
from .geom import push_clear_of_fabric, push_out_of


def _cluster_gateway(s: Settlement, seat: Mapping[str, object], fallback: Pt, turn_deg: float = 0.0) -> Pt:
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

    So: take the cloud's own extent along the seat axes and put the gateway on its DOWNSLOPE edge, clear of the last house. The fallback is the old band point, for the case where no house has been
    placed yet - which cannot happen in the shipped order, but a helper that assumes its caller is
    the failure mode this file has met repeatedly.

    Research:
        track leaves downslope - research/questions/0081-village-lanes.drawing.html: from the cluster's downslope edge (or a bearing turned off it)
        gateway clear of what stands - UNRESEARCHED: `TRACK_FABRIC_GAP` plus 8 px past the farthest house, well or yard
    """
    hs = s.M.get("houses") or []
    if not hs:
        return fallback
    ax, ay = cast(Pt, seat["along"])
    ox, oy = cast(Pt, seat["out"])
    if turn_deg:  # a bearing turned off the downslope (`stage_track`, where the downslope gateway has no dry way out)
        c, sn = math.cos(math.radians(turn_deg)), math.sin(math.radians(turn_deg))
        ox, oy, ax, ay = ox * c - oy * sn, ox * sn + oy * c, ax * c - ay * sn, ax * sn + ay * c
    xs = [float(h["x"]) for h in hs]
    ys = [float(h["y"]) for h in hs]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    # how far the cloud actually reaches, along each seat axis
    out_reach = max((x - cx) * ox + (y - cy) * oy for x, y in zip(xs, ys, strict=False))
    along_mid = sum((x - cx) * ax + (y - cy) * ay for x, y in zip(xs, ys, strict=False)) / len(xs)
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


def gate_out_of_the_field(envelope: Poly, gate: Pt) -> Pt:
    """The connector's start: `gate` pushed out of the field's `envelope` (`push_out_of`, the rule the track has always kept).

    Research:
        connector starts off the crop - research/questions/0081-village-lanes.drawing.html: the start pushed out of the field envelope
        setback from the field - UNRESEARCHED: `SPUR_SETBACK` 17 ft clear of the field envelope"""
    return push_out_of(envelope, gate, SPUR_SETBACK)


def _cluster_edge_toward(s: Settlement, target: Pt, fallback: Pt, fabric: list[Poly] | None = None) -> Pt:
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
            14 px plus half the brook short of it (the router's figure, not the page's), the brook crossed squarely on a plank bridge at a crossing place
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
    # `fabric`, where the caller asks this per candidate of an unchanging map, is built ONCE by it (feature 328, batch 11's
    # perf-audit: the spur's 111-124 candidates each rebuilt `_homestead_polys`, and wave 87's held parts doubled its cost)
    fabric = fabric if fabric is not None else [poly for poly, _owner, _kind in _homestead_polys(s)]
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
