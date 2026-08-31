"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from collections.abc import Sequence

from l7r.diagram.settlement import edge_dist, point_in_poly, seg_closest, seg_dist, seg_intersect, segments_cross
from l7r.diagram.sitegen.geom import centroid, unit

from ..consts import (
    SPUR_SETBACK,
    TRACK_FABRIC_GAP,
    Poly,
    Pt,
)


def _reach(c: Pt, path: Poly) -> float:
    """How near a polyline comes to a point - the same measurement `farmhouses_reach_a_way` makes."""
    return min(math.dist(c, seg_closest(c[0], c[1], a, b)) for a, b in zip(path, path[1:], strict=False))


def _aim_off(prev: Pt, tip: Pt, target: Pt) -> float:
    """How far off this end's outward heading is from aiming at `target`, in degrees.

    The honest test of "these two ends are one way with a hole in it": each end has to be heading
    INTO the gap toward the other, which is a statement about each end separately and about the line
    between them - not a comparison of the two headings with each other."""
    out = math.degrees(math.atan2(tip[1] - prev[1], tip[0] - prev[0]))
    aim = math.degrees(math.atan2(target[1] - tip[1], target[0] - tip[0]))
    return abs((out - aim + 180.0) % 360.0 - 180.0)


def shadowing_lane(pts: Poly, others: Sequence[Poly], reach: float) -> int | None:
    """Index of a way that BOTH of this lane's ends stand on or beside, or None - "it goes nowhere".

    A way earns its ink by connecting one thing to another. A lane whose two ends both land on the same
    single other way connects that way to itself: whatever the shape in between, no journey uses it that
    could not be walked along the way it leaves and returns to. That is a STRUCTURAL question with a yes
    or a no, and it is deliberately not a distance between the two treads.

    THE METRIC FORM OF THIS TEST WAS WRITTEN FIRST AND WAS A NO-OP ON BOTH MAPS IT NAMED (settlement-review
    x2, feature 155). It asked whether every point of a lane lay within `1.5 * w` - 4.5 ft for a footpath -
    of another lane. Kashikawa's remnant sits at 6.58 ft and sawada's at 11.4 ft, and the sawada figure was
    written into the docstring three lines above the constant that rejected it. Sawada's reviewer named the
    pattern, and it is the one to guard against here: *"calibrating a general rule to the single case that
    was easiest to measure is the recurring defect on this map, not a coincidence"* - the same shape as the
    5 ft nub floor shipped for an 8.25 ft boot and the 4.5 ft threshold shipped for a 6.6 ft remnant. A
    structural predicate has no dial to leave set too low, which is the whole reason to prefer it.

    `reach` is the gate's own "is this end ON that way" tolerance, not a tuning knob.
    """
    if len(pts) < 2:
        return None
    for j, other in enumerate(others):
        if len(other) < 2:
            continue
        segs = list(zip(other, other[1:], strict=False))
        if all(min(seg_dist(e[0], e[1], a, b) for a, b in segs) <= reach for e in (pts[0], pts[-1])):
            return j
    return None


def fabric_clearance(pts: Sequence[Pt], fabric: Sequence[Poly]) -> float:
    """How near a run passes to the settlement's own fabric - infinity when there is none to pass.

    Lifted out of `_touch_junctions` so the rewrite rule below can be asked with plain lists
    (GM 2026-08-28 on testability); the inner one delegates, so there is ONE body."""
    if len(pts) < 2 or not fabric:
        return float("inf")
    return min(seg_dist(v[0], v[1], a2, b2) for poly in fabric for v in poly for a2, b2 in zip(pts, pts[1:], strict=False))


def _stop_at_network(link: Poly, others: list[tuple[Pt, Pt]]) -> Poly:
    """Cut a join link at the FIRST place it meets one of the ways it was sent to reach.

    A link is routed to a point `q` on the network, and the router is free to run it along or
    across another way on the road there - tripwire seed 27's link touched lane 8 at 20 ft and
    carried on for 20 ft more to a `q` on a way that a later trim removed, leaving a hook to
    nothing beside a shed (feature 137 T03). A link exists to reach the network; the moment it
    does, the rest is a stub. Cut at a vertex within `_TOUCH_GAP` of one of `others`, or at a
    crossing. `others` is the TARGET set only - the main component in the orphan ladder, the unmet
    ways in the touch pass - never the piece's own component: a piece is often several lanes, and
    cutting at one of them left the reference hamlet's web in pieces on the first try."""
    if not others or len(link) < 2:
        return list(link)
    out = [link[0]]
    for t in range(1, len(link)):
        a, b = link[t - 1], link[t]
        # `seg_intersect` meets LINES - guard it with `segments_cross`, as every other caller here does,
        # or the cut lands on the link's own backward extension (the reference hamlet, first try).
        hits = [x for c, d in others if segments_cross(a, b, c, d) for x in [seg_intersect(a, b, c, d)] if x is not None and math.dist(a, x) > 0.5]
        if hits:
            out.append(min(hits, key=lambda x: math.dist(a, x)))
            return out
        out.append(b)
        if t < len(link) - 1:
            _near = min(((seg_dist(b[0], b[1], c, d), c, d) for c, d in others), key=lambda z: z[0])
            if _near[0] <= _TOUCH_GAP:
                # LAND ON THE WAY, not beside it: the web counts two lanes as joined at 4 ft, and a
                # link cut at a vertex 3.9 ft off rounds to a piece - the first cut of this pass
                # took the reference hamlet's web apart that way.
                foot = seg_closest(b[0], b[1], _near[1], _near[2])
                if math.dist(b, foot) > 0.5:
                    out.append(foot)
                return out
    return out


def _unretrace(pts: Poly) -> Poly:
    """Collapse an out-and-back in a polyline: a vertex whose two neighbors coincide is a spur to
    nowhere, and both it and the return vertex go. A join link is routed from a piece's END, and the
    router's first hop is free to land on the piece's own next vertex - so prepending the whole link
    drew `A -> B -> A' -> B -> ...`, a 180-degree hairpin the eye reads as a loop (cohort seed 07,
    feature 137 T03: lane 1 went 20 ft out to its old end and 20 ft back). Splicing is the one place
    this shape is made, so it is undone here rather than by a general smoothing pass."""
    out = [p for k, p in enumerate(pts) if k == 0 or math.dist(p, pts[k - 1]) > 0.5]
    k = 1
    while k < len(out) - 1:
        if math.dist(out[k - 1], out[k + 1]) <= 2.0:
            del out[k : k + 2]
            k = max(1, k - 1)
        else:
            k += 1
    # A polyline that folds away entirely (a door path whose link ran back past the door) is left
    # as it was drawn: an ugly lane is a lane, an empty one is a hole in the web (cohort seed 03).
    return out if len(out) >= 2 else list(pts)


# A JUNCTION LINK CROSSES NOTHING, BUT IT MAY BRUSH A FENCE. The 29 ft gaps this pass closes are
# made by the fabric margin itself: `clear_runs` clips a lane wherever it passes within
# `WEB_FABRIC_GAP` (7 ft) of a garden or a yard, and where two lanes meet beside a plot that is
# exactly where the cut lands - measured on Inashiro, every refused link was 29 ft long, sat 6-15 ft
# from a garden, and `_clear_link` refused it on the same margin that had made it. A lane and a
# garden fence share a line in a real village (the plot FRONTS the lane), so the last few feet into
# a junction are tested against footprints only: the link may not cross a house, a bed, a yard or
# water, and it may run along a fence.
# 4 ft, not 1: the gate's overlap matrix extends a lane by its tread (3 ft wide, so 1.5 each side)
# plus rounding, and the first cut at 1 ft let a string-pulled chord run 2.1 ft from a garden's
# corner - clear of the footprint, inside the tread's ink (`features_do_not_overlap`, lanes vs
# gardens, feature 133 T41). A junction link may still brush a fence; it may not paint on it.
_TOUCH_GAP = 4.0


def _components(ways: Sequence[Poly], touch: float) -> list[int]:
    """Connected-component label per way, joined by an END within `touch` of another way's tread."""
    par = list(range(len(ways)))

    def find(i: int) -> int:
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i

    segs = [list(zip(w, w[1:], strict=False)) for w in ways]
    for i in range(len(ways)):
        for j in range(i + 1, len(ways)):
            if len(ways[i]) < 2 or len(ways[j]) < 2:
                continue
            if any(seg_dist(q[0], q[1], a, b) <= touch for q in (ways[i][0], ways[i][-1]) for a, b in segs[j]) or any(
                seg_dist(q[0], q[1], a, b) <= touch for q in (ways[j][0], ways[j][-1]) for a, b in segs[i]
            ):
                par[find(i)] = find(j)
    return [find(i) for i in range(len(ways))]


def _turn_deg(a: Pt, b: Pt, c: Pt) -> float:
    """The change of heading at `b` on the run a -> b -> c, in degrees: 0 straight on, 180 doubled back."""
    v1 = (b[0] - a[0], b[1] - a[1])
    v2 = (c[0] - b[0], c[1] - b[1])
    n1, n2 = math.hypot(*v1), math.hypot(*v2)
    if n1 < 1e-6 or n2 < 1e-6:
        return 0.0
    return math.degrees(math.acos(max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))))


def _drop_collinear(pts: Poly, eps: float = 1e-6) -> Poly:
    """Remove interior points that lie on the straight line between their neighbors.

    Geometry-preserving by construction: a point dropped here is one the drawn stroke passes through
    anyway. It exists because `clear_runs` returns a polyline of SAMPLES, and a record of samples
    misleads every consumer that reads a lane as a sequence of bends - see the note at its caller."""
    if len(pts) < 3:
        return list(pts)
    out = [pts[0]]
    for k in range(1, len(pts) - 1):
        ax, ay = out[-1]
        bx, by = pts[k]
        cx, cy = pts[k + 1]
        if abs((bx - ax) * (cy - ay) - (by - ay) * (cx - ax)) > eps * max(1.0, math.hypot(cx - ax, cy - ay)):
            out.append(pts[k])
    out.append(pts[-1])
    return out


def _plen(pts: Poly) -> float:
    return sum(math.dist(pts[k], pts[k + 1]) for k in range(len(pts) - 1))


def push_clear_of_fabric(base: Pt, unit: Pt, edge: float, fabric: Sequence[Poly], gap: float = TRACK_FABRIC_GAP) -> Pt:
    """Walk out from `base` along the unit vector `unit`, starting `edge` out, until the point clears every
    standing thing by `gap`. Twenty-four steps of 6 px, then the last point tried.

    LIFTED OUT OF `_cluster_gateway` AND `_cluster_edge_toward` (feature 146), which carried the same loop
    twice. Stepping rather than solving is deliberate - the fabric is an arbitrary set of polygons, the step
    is cheap, and a bounded walk cannot fail to terminate the way a solve can. The bound is what makes the
    LAST line a real branch: a cluster ringed all the way round returns a point that does not clear, and the
    caller draws from it anyway rather than returning nothing. No live hamlet is that crowded.
    """
    for _ in range(24):
        gx, gy = base[0] + unit[0] * edge, base[1] + unit[1] * edge
        if all(edge_dist(gx, gy, poly) >= gap for poly in fabric):
            return (gx, gy)
        edge += 6.0
    return (base[0] + unit[0] * edge, base[1] + unit[1] * edge)


def _seg_cross(a: Pt, b: Pt, c: Pt, d: Pt) -> Pt | None:
    """Where segment a-b crosses segment c-d STRICTLY inside both (never at an end), else None."""
    r = (b[0] - a[0], b[1] - a[1])
    q = (d[0] - c[0], d[1] - c[1])
    den = r[0] * q[1] - r[1] * q[0]
    if abs(den) < 1e-9:
        return None
    w = (c[0] - a[0], c[1] - a[1])
    t = (w[0] * q[1] - w[1] * q[0]) / den
    u = (w[0] * r[1] - w[1] * r[0]) / den
    eps = 0.02
    if eps < t < 1 - eps and eps < u < 1 - eps:
        return (a[0] + t * r[0], a[1] + t * r[1])
    return None


def _trim_to_service(run: Poly, segs: Sequence[tuple[Pt, Pt]], houses: Sequence[Pt], fields: Sequence[Poly] = ()) -> Poly:
    """Pull a run's ends back to the last point that actually serves something.

    `lanes_reach_something` asks of every internal lane end that it reach another way within 40 ft or
    a farmhouse within 90; a web lane's ends come out of the clipper, which stops where the ground
    stops being walkable and has no opinion about whether anything is there. Trimming BEFORE the ink
    goes down is better than trimming after: `trim_lane_stubs` drops anything under its 71 ft floor,
    which is the right rule for a skeleton arm and would delete the door paths this feature exists to
    draw."""

    # ARRIVING AT THE FIELD IS SERVICE. A field spur exists to reach the crop, and it is the one way
    # on the map whose whole purpose is served by something that is neither a house nor another lane.
    # Without this the trim cut Mizuguchi's spur 32 ft short of the paddy - it removed the only part
    # of the lane that did the job the lane was drawn for, and did so on the grounds that nothing was
    # there. The setback matches `SPUR_SETBACK`: a path stops AT the bund, and the last few feet are
    # the baulk, so "touching the envelope" means within that, not inside it.
    def serves(q: Pt) -> bool:
        if any(seg_dist(q[0], q[1], a, b) <= 40.0 for a, b in segs) if segs else False:
            return True
        if any(math.dist(q, h) <= 90.0 for h in houses):
            return True
        return any(edge_dist(q[0], q[1], f) <= SPUR_SETBACK + 4.0 for f in fields)

    out = list(run)
    while len(out) > 2 and not serves(out[-1]):
        out.pop()
    while len(out) > 2 and not serves(out[0]):
        out.pop(0)
    return out


def _nearest_seg(q: Pt, segs: Sequence[tuple[Pt, Pt]]) -> tuple[float, tuple[Pt, Pt] | None]:
    """The distance from `q` to the way network, and WHICH segment of it - the two are one answer.

    Returned together on purpose: a caller that finds the distance and then re-derives the segment is
    two expressions that can disagree, which is the skill's standing rule about a diagnostic that
    restates what it observed."""
    best, at = float("inf"), None
    for a, b in segs:
        d = seg_dist(q[0], q[1], a, b)
        if d < best:
            best, at = d, (a, b)
    return best, at


def _net_reach(path: Poly, segs: Sequence[tuple[Pt, Pt]]) -> float:
    """How near a candidate path comes to the EXISTING way network, at its nearest point."""
    return min(seg_dist(q[0], q[1], a, b) for q in path for a, b in segs)


def push_out_of(poly: Poly, p: Pt, margin: float) -> Pt:
    """Move `p` OUTSIDE `poly` by `margin`, on the normal of the outline EDGE nearest to it.

    Shared by the field spur's tip and the connector's route, which had the same defect for the same
    reason: both were pushed clear along one fixed map-wide direction (the seat's outward normal),
    which is only the right way out where the outline happens to run across it - so a spur tip
    finished 28 px inside the standing water. Projecting onto the nearest EDGE (not the nearest
    VERTEX - a point deep inside a lobe can have its nearest vertex right round the far side, and
    stepping out from there is a detour, not a fix) puts the way exactly where a track meeting a
    field goes: on the bund, just outside the crop. A point already clear is returned untouched, so
    this never drags a way back in."""
    ring = list(poly)
    n = len(ring)
    best: tuple[float, Pt, Pt, Pt] | None = None
    for k in range(n):
        a, b = ring[k], ring[(k + 1) % n]
        q = seg_closest(p[0], p[1], a, b)
        d = math.hypot(q[0] - p[0], q[1] - p[1])
        if best is None or d < best[0]:
            best = (d, q, a, b)
    assert best is not None  # a ring always has an edge
    d, q, a, b = best
    inside = point_in_poly(p[0], p[1], ring)
    if not inside and d > margin:
        return p
    nx, ny = unit(-(b[1] - a[1]), b[0] - a[0])
    cen = centroid(poly)
    if nx * (q[0] - cen[0]) + ny * (q[1] - cen[1]) < 0:
        nx, ny = -nx, -ny
    return (q[0] + nx * margin, q[1] + ny * margin)


def polyline_len(pts: Poly) -> float:
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))
