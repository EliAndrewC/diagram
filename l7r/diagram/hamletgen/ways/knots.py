"""Lane ends that nearly meet are joined - asked of the FINISHED web (feature 328 wave 4, glyph-check of Inashiro).

The lane page's rule (research/questions/0081-village-lanes.drawing.html): "Ends within 25 ft of one another are joined at a
single point, so three lanes never arrive a few feet apart in a knot." `_smooth_web`'s knot pass gathers them, but it runs
before the settle, and on every pool map since the settle draws each household's way (`tree.settle_tree`, feature 318) the
web it sees is the connector alone: the knots are laid after it. Inashiro shipped four lane ends within 24 ft at the track's
head (lanes 7 and 3 T'd onto the track 6 ft apart, 18 and 24 ft from where lane 1 arrives) and lanes 9 and 11 ending 19 ft
apart on lane 4. So the settle asks it too (`settle.settle_knots`), on the web as it stands, every round.

An END is every lane's end - a T-foot (an end on another lane's side) is one. Ends within `_JOINT_FT` are one NODE (a
junction already). Two nodes within `_KNOT_FT` are a KNOT unless one lane runs from the one to the other: that lane IS their
join (a 15 ft door lane from the track's head is not two arrivals).

Research: plumbing - NONE"""

from __future__ import annotations

import math
from collections.abc import Callable, Collection, Container, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import seg_closest, seg_dist
from l7r.diagram.settlement.rolling.gap_ways import KNOT_MARGIN

from ..consts import WEB_CROP_GAP, WEB_FABRIC_GAP, WEB_SHADOW_FT, Poly, Pt
from .corridors import ACCESS_ROLE, FIELD_ROLE, TARGET_ROLE
from .forced import ground
from .geom import polyline_len
from .joints import _JOINT_FT
from .smooth import _KNOT_FT

Node = tuple[Pt, list[tuple[int, int]]]
"""A junction point and the (lane, end) pairs standing on it - `end` 0 or -1."""

Apart = Callable[[Pt, Pt], bool]
"""Do two points stand either side of something a lane may not cross (`ground_apart`)?"""


def ground_apart(M: Mapping[str, Any], s: Any = None) -> Apart:
    """THE KNOT RULE READS THE GROUND (feature 385 T01, plan D4b): two ends are apart where the straight join between them is
    not lawful ground for a footpath (`settle.Lawful.on_lawful_ground`, the settle's own test: a house, another household's
    yard or garden, a grove, a fixture, a building, a field, a dry plot, marsh, or water crossed off its ford). Two lane ends
    with a garden between them are two paths either side of its fence, not three lanes arriving a few feet apart (the GM,
    2026-10-17: a rule about how paths meet holds where nothing stands in the way). No cohort seed shows it yet: cohort seed
    24 under the wave 155 re-deal, which first suggested it, proved a staggered junction with clear ground between the ends. `s`, where the caller has the settlement, is read in place of
    the manifest's view.

    Research:
        a knot is ends that could meet - research/questions/0081-village-lanes.drawing.html: "Ends within 25 ft of one another are joined at a single point, so three lanes never arrive a few feet apart in a knot" read as open ground; ends a fence parts are not a knot
        the join judged as a footpath - research/questions/0081-village-lanes.drawing.html: the join between two ends tested at the footpath's 3 ft"""
    blocked = ground(M, s)  # the settle's own lawful-ground test, read once per manifest (`forced.ground`)
    return lambda p, q: blocked(p, q, 3.0)


def _pts(ln: Mapping[str, Any]) -> Poly:
    return [(float(x), float(y)) for x, y in ln.get("pts") or []]


def _fixed(ln: Mapping[str, Any], end: int) -> bool:
    """An end the gather never moves: the connector's and a row's street's (each laid before the houses and kept whole), a
    tree lane's other than a household's way (a way target's spur, the field way: each drawn as its run is found), and a
    household's way's door end (`end` 0: where it leaves its dooryard). A household's way's FOOT may move: its reserved
    corridor is rewritten with it (`tree.set_corridor`)."""
    if ln.get("connector") or ln.get("street"):
        return True
    role = ln.get("role")
    return role in (TARGET_ROLE, FIELD_ROLE) or (role == ACCESS_ROLE and end == 0)


def end_nodes(lanes: Sequence[Mapping[str, Any]], fixed: Callable[[Mapping[str, Any], int], bool] = _fixed) -> list[Node]:
    """Every lane end, grouped into nodes - ends within `_JOINT_FT` of one another are one point. A node's point is its
    `fixed` end's (by default `_fixed`) where it has one, else its first end's.

    Research: a joint is one point - research/questions/0081-village-lanes.drawing.html: ends joined at a single point"""
    ends = [(i, e, p[e]) for i, ln in enumerate(lanes) if len(p := _pts(ln)) >= 2 for e in (0, -1)]
    root = list(range(len(ends)))

    def find(a: int) -> int:
        while root[a] != a:
            root[a] = root[root[a]]
            a = root[a]
        return a

    for a in range(len(ends)):
        for b in range(a + 1, len(ends)):
            if math.dist(ends[a][2], ends[b][2]) <= _JOINT_FT:
                root[find(b)] = find(a)
    groups: dict[int, list[int]] = {}
    for a in range(len(ends)):
        groups.setdefault(find(a), []).append(a)
    nodes: list[Node] = []
    for members in groups.values():
        at = next((ends[a][2] for a in members if fixed(lanes[ends[a][0]], ends[a][1])), ends[members[0]][2])
        nodes.append((at, [(ends[a][0], ends[a][1]) for a in members]))
    return nodes


def _on(p: Poly, q: Pt) -> bool:
    return any(seg_dist(q[0], q[1], a, b) <= _JOINT_FT for a, b in zip(p, p[1:], strict=False))


def door_end_teed(lanes: Sequence[Mapping[str, Any]], i: int, end: int, alone: bool, other: Pt) -> bool:
    """Is lane `i`'s `end` a household way's DOOR end that meets no way - an access lane's first end, `alone` at its node and
    on no other lane's side - with `other` on that same lane, so that the one lane runs between them? Such a pair is a T near
    a door, not two ends that nearly meet: 0081's knot is ends left loose beside each other and three lanes arriving a few
    feet apart, and here one drawn lane already joins the two (the reading this module's docstring states: "a 15 ft door lane
    from the track's head is not two arrivals"). The gather search (`knots`) and the knot verdict (`lane_knots`, read by the
    pool's seed test and the cohort) both ask it (feature 328 wave 94; spec-fidelity's ruling of 2026-10-10: LEGITIMATE in
    this narrow form - a door end within the reach of another lane's end or foot, or a door end that is itself a junction,
    is still a knot).

    Research: a door end teed on its own lane - research/questions/0081-village-lanes.drawing.html: a path leaving its own door with a T on it is one path, not two ends that nearly meet (a map drawing convention)"""
    ln = lanes[i]
    if end != 0 or not alone or ln.get("role") != ACCESS_ROLE:
        return False
    pts = _pts(ln)
    if not _on(pts, other):  # the one-lane test first: it settles almost every pair a gather asks about (feature 328 wave 94, perf)
        return False
    q = pts[0]
    return not any(k != i and len(_pts(o)) >= 2 and _on(_pts(o), q) for k, o in enumerate(lanes))


def _teed_pair(lanes: Sequence[Mapping[str, Any]], na: Node, nb: Node) -> bool:
    """`door_end_teed` asked of two nodes either way round: one a lone door end, the other on its lane.

    Research: a door end teed on its own lane - research/questions/0081-village-lanes.drawing.html: a path leaving its own door with a T on it is one path, not two ends that nearly meet"""
    return any(len(n[1]) == 1 and door_end_teed(lanes, n[1][0][0], n[1][0][1], True, m[0]) for n, m in ((na, nb), (nb, na)))


def knots(lanes: Sequence[Mapping[str, Any]], apart: Apart | None = None) -> list[tuple[int, int, float]]:
    """The knots of the web: pairs of `end_nodes` indices that no one lane runs between standing within `_KNOT_FT` of one
    another, `KNOT_MARGIN` (1.0) leaving that the page's own reach - nearest first, with their distance. (A 1.5 margin once caught a foot slid just past the
    reach; the slide is gone, and the margin went past the page - feature 328 wave 4.)

    Research: lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft are joined at a single point; the margin a map drawing convention (`gap_ways.KNOT_MARGIN`)"""
    nodes = end_nodes(lanes)
    where = {end: n for n, (_q, ends) in enumerate(nodes) for end in ends}
    spans = {frozenset((where[(i, 0)], where[(i, -1)])) for i, _e in where if _e == 0}
    out = []
    for a in range(len(nodes)):
        for b in range(a + 1, len(nodes)):
            d = math.dist(nodes[a][0], nodes[b][0])
            if d <= _KNOT_FT * KNOT_MARGIN and frozenset((a, b)) not in spans and not _teed_pair(lanes, nodes[a], nodes[b]) and not (apart and apart(nodes[a][0], nodes[b][0])):
                out.append((a, b, d))
    return sorted(out, key=lambda k: k[2])


def moved_onto(pts: Poly, end: int, node: Pt) -> list[Poly]:
    """Lane `pts` with its `end` (0 or -1) put on `node`: the end's last leg re-aimed at it; then, as a second form, with every
    inner vertex within `_KNOT_FT` of the node also taken out (the knot's own corner, `_smooth_web`'s collapse) - each form
    with no point repeated and at least two points, the first form first.

    Research: lane ends gathered - research/questions/0081-village-lanes.drawing.html: an end within 25 ft is moved onto the junction"""
    seq = list(pts) if end == -1 else list(pts)[::-1]
    forms = [[*seq[:-1], node], [seq[0], *(q for q in seq[1:-1] if math.dist(q, node) > _KNOT_FT), node]]
    out: list[Poly] = []
    for f in forms:
        run: Poly = []
        for q in f:
            if not run or math.dist(q, run[-1]) > 1e-9:
                run.append(q)
        run = run if end == -1 else run[::-1]
        if len(run) >= 2 and run not in out:
            out.append(run)
    return out


def teed_onto(pts: Poly, end: int, other: Poly) -> list[Poly]:
    """Lane `pts` with its `end` (0 or -1) re-aimed, from the vertex before it, at the nearest point of the `other` lane: a
    T-foot on the other lane's side where the two converge - the gather's last form, tried where putting the end on the
    other's node would leave a sliver between the two (`needle_loops`) and moving the other's end would split the web
    (feature 328 wave 28, Kuwabata: two access lanes converging at a sharp angle, their feet 15 ft apart).

    Research: lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft are joined, so lanes
    never arrive a few feet apart in a knot"""
    seq = list(pts) if end == -1 else list(pts)[::-1]
    if len(seq) < 2 or len(other) < 2:
        return []
    prev = seq[-2]
    foot = min((seg_closest(prev[0], prev[1], a, b) for a, b in zip(other, other[1:], strict=False)), key=lambda z: math.dist(z, prev))
    if math.dist(foot, prev) <= 1e-9:
        return []
    run = [*seq[:-1], foot]
    return [run if end == -1 else run[::-1]]


_SIDE_BY_SIDE_DEG = 20.0
"""Research: two paths side by side - research/questions/0081-village-lanes.drawing.html: "A lane whose end runs back along another way at less than 20 degrees ... the maps cut it where it comes alongside and let it meet the other as a T" (0081)"""


def households_only(lanes: Sequence[Mapping[str, Any]], edits: Mapping[int, Poly]) -> bool:
    """Is every lane at both nodes of a gather a household's way (`ACCESS_ROLE`) - each moved lane, and every lane standing
    where a moved end was or now is, a tee's lane too (405 T07, D128)? The 3 ft pass asks it: a street, the field way or a
    spur never moves, so asking only the moved lanes let a household's way come 3 ft off a garden onto one (impl-drift round 2).

    Research: households' ways only - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the 3 ft join is for two households' way ends a few feet apart and unjoined"""
    spots = []
    for i, p in edits.items():
        if lanes[i].get("role") != ACCESS_ROLE:
            return False
        was = _pts(lanes[i])
        spots += [q for e in (0, -1) if was and p and was[e] != p[e] for q in (was[e], p[e])]
    for j, ln in enumerate(lanes):
        if j in edits or ln.get("role") == ACCESS_ROLE or len(w := _pts(ln)) < 2:
            continue
        if any(seg_dist(x, y, a, b) <= 1.0 for x, y in spots for a, b in zip(w, w[1:], strict=False)):
            return False
    return True


_BEND_OFFSETS_FT = (10.0, 15.0, 20.0, 25.0, 30.0, 40.0)
"""How far off its middle a gather's refused leg is bent round what stands, nearest first (405 T07, D126).

Research: the bend's offsets - UNRESEARCHED: 0081 has the walker go round what stands, not how far; 10 to 40 ft, a copse's lane buffer and more"""


def bent_round(pts: Poly, end: int) -> list[Poly]:
    """The gather's new leg at `end` (0 or -1) of `pts` bent round what stands: through a waypoint `_BEND_OFFSETS_FT` off the
    leg's middle, either side, nearest first (405 T07, D126). Asked by `settle_knots` only where the matrix refused the gather's
    write: seed 57's one admitted gather ran its leg 15 ft past a household's reserved copse seat, and the walker goes round.
    Asked in the first pass only, with the fence gap as it stands (`WEB_FABRIC_GAP`): a bent leg is a new run past the gardens,
    never one of the joins the second pass lets come within 3 ft (impl-drift, T07 round 1).

    Research:
        the leg bent round what stands - research/questions/0081-village-lanes.drawing.html: a turn whose straighter way the mapped ground blocks is drawn as walked (the GM 2026-10-17)
        round a grove, not through it - research/questions/0081-village-lanes.drawing.html: where a grove stands across the straighter way, the walker goes round it
        how far off - UNRESEARCHED: the waypoint 10 to 40 ft off the leg's middle (`_BEND_OFFSETS_FT`)
        never farther off than the leg is long - research/questions/0081-village-lanes.drawing.html: a hairpin is refused (the drawing page's 140 degrees, a drawing convention); a waypoint no farther off than its leg is long turns at most 127 degrees
        the bend's form - UNRESEARCHED: one waypoint off the leg's middle, either side, nearest first - the smallest detour tried first, each asked of the gather's judge (its angle rules read as open ground, `forced.py`)"""
    seq = list(pts) if end == -1 else list(reversed(pts))
    if len(seq) < 2 or (span := math.dist(seq[-2], seq[-1])) < 1e-6:
        return []
    (ax, ay), (bx, by) = seq[-2], seq[-1]
    nx, ny = -(by - ay) / span, (bx - ax) / span
    mx, my = (ax + bx) / 2, (ay + by) / 2
    out = []
    for off in (o for o in _BEND_OFFSETS_FT if o <= span):  # no farther off than the leg is long: a hairpin otherwise (T07 round 1)
        for side in (1, -1):
            bent = [*seq[:-1], (mx + side * off * nx, my + side * off * ny), seq[-1]]
            out.append(bent if end == -1 else bent[::-1])
    return out


def teed_back(pts: Poly, end: int, other: Poly) -> list[Poly]:
    """Lane `pts` with its `end` (0 or -1) cut WHERE IT COMES ALONGSIDE the `other` lane and teed onto it from there: the run
    of legs before its last that lie within `_SIDE_BY_SIDE_DEG` of the other and within `WEB_SHADOW_FT` of it (the distance
    at which the map reads two ways as beside each other), dropped, and the lane re-aimed from the vertex where that run
    starts at its nearest point on the other - shorter than the lane it replaces. Asked by the gather where the end's own
    last vertex tees it within the knot's reach (405 T134, D125: fresh cohort seed 717220 with T26's sheds, a household's
    way ran 20 ft beside another and teed onto it 24.4 ft from that way's foot). Not the slide this module's index forbids:
    the slide kept the approach and moved the foot along the way; this drops the legs that ran beside the way. Nothing
    where the leg before the last is not alongside.

    Research:
        a lane cut where it comes alongside - research/questions/0081-village-lanes.drawing.html: "Two paths running side by side are drawn as one. A lane whose end runs back along another way at less than 20 degrees ... the maps cut it where it comes alongside and let it meet the other as a T"
        beside, as the map reads it - UNRESEARCHED: 0081 gives the angle but no distance; read within `WEB_SHADOW_FT` (30 ft), the distance the shadow rule reads two ways together at"""
    seq = list(pts) if end == -1 else list(pts)[::-1]
    legs = list(zip(other, other[1:], strict=False))
    if len(seq) < 3 or not legs:
        return []

    def alongside(a: Pt, b: Pt) -> bool:
        if any(min(seg_dist(q[0], q[1], u, v) for u, v in legs) > WEB_SHADOW_FT for q in (a, b)):
            return False
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        u, v = min(legs, key=lambda uv: seg_dist(mid[0], mid[1], *uv))
        turn = abs(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]) - math.atan2(v[1] - u[1], v[0] - u[0]))) % 180.0
        return min(turn, 180.0 - turn) < _SIDE_BY_SIDE_DEG

    m = len(seq) - 2
    while m > 0 and alongside(seq[m - 1], seq[m]):
        m -= 1
    if m == len(seq) - 2:
        return []
    prev = seq[m]
    foot = min((seg_closest(prev[0], prev[1], u, v) for u, v in legs), key=lambda z: math.dist(z, prev))
    run = [*seq[: m + 1], foot]
    if math.dist(foot, prev) <= 1e-9 or polyline_len(run) >= polyline_len(seq):
        return []
    return [run if end == -1 else run[::-1]]


def _alongside(legs: Sequence[tuple[Pt, Pt]], a: Pt, b: Pt) -> bool:
    """Does leg a-b run alongside one of `legs`: its middle within `WEB_SHADOW_FT` of the nearest, at under `_SIDE_BY_SIDE_DEG`
    to it (405 T135)?

    Research: alongside - UNRESEARCHED: 0081 gives the 20 degrees but no distance; read at the leg's middle within `WEB_SHADOW_FT` (30 ft, the distance the shadow rule reads two ways together at) - `teed_back` asks both ends of a leg"""
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    u, v = min(legs, key=lambda uv: seg_dist(mid[0], mid[1], *uv))
    if seg_dist(mid[0], mid[1], u, v) > WEB_SHADOW_FT:
        return False
    turn = abs(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]) - math.atan2(v[1] - u[1], v[0] - u[0]))) % 180.0
    return min(turn, 180.0 - turn) < _SIDE_BY_SIDE_DEG


def onto_cut_back(pts: Poly, end: int, node: Pt, other: Poly) -> Poly:
    """Lane `pts` with its `end` (0 or -1) moved onto `node` and each corner whose leg to the node would run back along the
    `other` lane dropped, nearest the node first (`_alongside`); [] where no corner is dropped (405 T135, D129: seed 24 with
    T26's sheds - a joining lane moved onto a household way's end ran its first leg back up that way's last leg).

    Research: cut where it comes alongside - research/questions/0081-village-lanes.drawing.html: a lane whose end runs back along another way at less than 20 degrees is cut where it comes alongside and meets the other"""
    seq = [*(list(pts) if end == -1 else list(pts)[::-1])[:-1], node]
    legs = list(zip(other, other[1:], strict=False))
    if not legs:
        return []
    cut = seq
    while len(cut) > 2 and _alongside(legs, cut[-2], cut[-1]):
        cut = [*cut[:-2], cut[-1]]
    if cut is seq:
        return []
    return cut if end == -1 else cut[::-1]


def joiner_first_meeting(lanes: Sequence[Mapping[str, Any]], i: int, end: int, node: Pt) -> Poly:
    """A lane laid only to join two others (`JOIN_ROLE`), its `end` re-aimed at `node` and ended where that leg first crosses
    another lane, more than `_JOINT_FT` inside both (`settle.shapes._crossing`) - only where that point stands beyond
    `_KNOT_FT` of the node; [] otherwise (405 T135, D130: seed 36 with T26's sheds - aimed at a household way's foot, the
    joining lane closed a sliver with that way; ended where it first crossed it, 31 ft from the foot, no knot is left).

    Research:
        a joining lane ends where it first meets a way - research/questions/0081-village-lanes.drawing.html: a lane laid only to join two others ends where it first meets one, its tail cut however long it is
        its first meeting beyond the knot's reach - research/questions/0081-village-lanes.drawing.html: ends within 25 ft are joined at a single point, so a first meeting within the reach would leave the knot it mends"""
    from .settle.shapes import JOIN_ROLE, _crossing  # bound here: `settle` names `settle_knots` in its STEPS

    if lanes[i].get("role") != JOIN_ROLE:
        return []
    seq = [*(_pts(lanes[i]) if end == -1 else _pts(lanes[i])[::-1])[:-1], node]
    a, b = seq[-2], seq[-1]
    xs = [x for j, ln in enumerate(lanes) if j != i for u, v in zip(_pts(ln), _pts(ln)[1:], strict=False) if (x := _crossing(a, b, u, v)) is not None]
    if not xs:
        return []
    x = min(xs, key=lambda q: math.dist(q, a))
    if math.dist(x, node) <= _KNOT_FT:
        return []
    run = [*seq[:-1], x]
    return run if end == -1 else run[::-1]


def contracted(lanes: Sequence[Mapping[str, Any]], at: Pt, node: Pt, skip: Collection[int], fixed: Callable[[Mapping[str, Any], int], bool] = _fixed) -> dict[int, Poly]:
    """The lanes a knot's stretch is taken out of when its node at `at` is gathered onto `node`: each lane but `skip` with an
    end on `node` and a corner at `at` - the knot's two junctions joined by its last leg - with every inner vertex within
    `_KNOT_FT` of `node` taken out (`moved_onto`'s second form), so the ends gathered onto `node` do not cross the leg they
    leave (Inashiro, feature 328 wave 4: a way's foot on another's last corner, 19 ft from where that one met a third).

    Research: lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft of one another are joined at a single point, the knot's corner taken out"""
    out: dict[int, Poly] = {}
    for k, ln in enumerate(lanes):
        p = _pts(ln)
        if k in skip or len(p) < 3:
            continue
        for e in (0, -1):
            if math.dist(p[e], node) <= _JOINT_FT and not fixed(ln, e) and any(math.dist(v, at) <= _JOINT_FT for v in p[1:-1]):
                forms = moved_onto(p, e, node)
                if len(forms) > 1:
                    out[k] = forms[1]
                    out.update(carried(lanes, p, forms[1], {*skip, k}))
                break
    return out


def carried(lanes: Sequence[Mapping[str, Any]], old: Poly, new: Poly, skip: Container[int]) -> dict[int, Poly]:
    """Every other lane (but `skip`) with an end on the stretch of `old` that `new` no longer runs along, that end carried
    onto `new` at its nearest point (`moved_onto`'s first form) - a T kept a T when the lane it stands on is re-laid.

    Research: plumbing - NONE: a junction kept on the lane re-laid under it"""
    out: dict[int, Poly] = {}
    for m, ln in enumerate(lanes):
        p = _pts(ln)
        if m in skip or len(p) < 2:
            continue
        for e in (0, -1):
            q = p[e]
            if _on(old, q) and not _on(new, q):
                foot = min((seg_closest(q[0], q[1], a, b) for a, b in zip(new, new[1:], strict=False)), key=lambda z: math.dist(z, q))
                out[m] = moved_onto(p, e, foot)[0]
                break
    return out


def next_gather(
    lanes: Sequence[Mapping[str, Any]], judge: Callable[[dict[int, Poly]], bool], fixed: Callable[[Mapping[str, Any], int], bool] = _fixed, apart: Apart | None = None
) -> dict[int, Poly] | None:
    """The first gather `judge` admits, nearest knot first: every end on one node of the knot moved onto the other node
    (`moved_onto`, both forms tried, then each with the knot's corner taken out of the lane joining the two - `contracted`) -
    the node with fewer ends moves, and the other way round where that is refused; where both are
    refused, a lone movable end is teed onto the other node's lane (`teed_onto`). A node holding a `fixed` end (by default
    `_fixed`) never moves. `judge` is handed the new points of every lane the gather moves, keyed by lane; None where no knot
    can be gathered.

    Research:
        lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft meet at one node
        which node a knot gathers at - UNRESEARCHED: the node with fewer ends moves onto the other, the other way round where refused
        a lone end teed onto the other lane - research/questions/0081-village-lanes.drawing.html: where neither node can move, the arriving lane meets the other's side as a T (`teed_onto`)
        a lone end cut where it comes alongside - research/questions/0081-village-lanes.drawing.html: "the maps cut it where it comes alongside and let it meet the other as a T" (`teed_back`, 405 T134), taken only where its T stands past the knot's reach and the web keeps no more knots
        which ways a lone end is cut back onto - UNRESEARCHED: a lane at the other node, or the lane its own end stands on
        a lone end moved onto the node, cut where it comes alongside - research/questions/0081-village-lanes.drawing.html: an end running back along another way under 20 degrees is cut where it comes alongside (`onto_cut_back`, 405 T135)
        a joining lane ended where it first meets a way - research/questions/0081-village-lanes.drawing.html: a lane laid only to join two others ends where it first meets one (`joiner_first_meeting`, 405 T135)
        the order of the last forms - UNRESEARCHED: `teed_onto`, then `teed_back`, then `onto_cut_back`, then `joiner_first_meeting` - the end's own approach kept longest first
        which lanes an end moved onto the node is cut back along - UNRESEARCHED: the lanes at that node, the ways it would run back along there"""
    nodes = end_nodes(lanes, fixed)
    for a, b, _d in knots(lanes, apart):
        order = sorted(((b, a), (a, b)), key=lambda mt: len(nodes[mt[0]][1]))
        for mover, target in order:
            ends = nodes[mover][1]
            if any(fixed(lanes[i], e) for i, e in ends) or len({i for i, _e in ends}) < len(ends):
                continue  # a fixed end stays; a lane with both ends on one node is a loop no gather straightens
            corner = contracted(lanes, nodes[mover][0], nodes[target][0], {i for i, _e in ends}, fixed)
            for cut, form in ((c, f) for c in (False, True) for f in (0, 1)):
                if cut and not corner:
                    continue
                edits: dict[int, Poly] = {}
                for i, e in ends:
                    forms = moved_onto(_pts(lanes[i]), e, nodes[target][0])
                    edits[i] = forms[min(form, len(forms) - 1)]
                if judge({**edits, **(corner if cut else {})}):
                    return {**edits, **(corner if cut else {})}
        for mover, target in order:  # neither node can move onto the other: a lone movable end teed onto the other's lane
            ends = nodes[mover][1]
            if len(ends) != 1 or fixed(lanes[ends[0][0]], ends[0][1]):
                continue
            i, e = ends[0]
            for j in sorted({j for j, _f in nodes[target][1] if j != i}):
                for form in teed_onto(_pts(lanes[i]), e, _pts(lanes[j])):
                    if judge({i: form}):
                        return {i: form}
        for mover, target in order:  # ...or teed from an EARLIER vertex onto the lane it comes alongside, clear of the knot
            ends = nodes[mover][1]
            if len(ends) != 1 or fixed(lanes[ends[0][0]], ends[0][1]):
                continue
            i, e = ends[0]
            for j in sorted({j for j, _f in nodes[target][1] if j != i} | {j for j, ln in enumerate(lanes) if j != i and _on(_pts(ln), nodes[mover][0])}):
                for form in teed_back(_pts(lanes[i]), e, _pts(lanes[j])):
                    tip = form[-1] if e == -1 else form[0]
                    if (
                        math.dist(tip, nodes[target][0]) > _KNOT_FT * KNOT_MARGIN
                        and len(knots([*lanes[:i], {**lanes[i], "pts": form}, *lanes[i + 1 :]], apart)) <= len(knots(lanes, apart))
                        and judge({i: form})
                    ):
                        return {i: form}
        for mover, target in order:  # ...or moved onto the node, its corners that would run back along a way there dropped
            ends = nodes[mover][1]
            if len(ends) != 1 or fixed(lanes[ends[0][0]], ends[0][1]):
                continue
            i, e = ends[0]
            for j in sorted({j for j, _f in nodes[target][1] if j != i}):
                form = onto_cut_back(_pts(lanes[i]), e, nodes[target][0], _pts(lanes[j]))
                if form and judge({i: form}):
                    return {i: form}
            form = joiner_first_meeting(lanes, i, e, nodes[target][0])
            if form and judge({i: form}):
                return {i: form}
    return None


_WHOLE_RULES = ("needle_loops", "doorstep_ends", "doubled_tails", "way_outs", "shadows")
"""The rules of the whole web a gather is asked besides the law of each lane it moves (`settle.Lawful`): no new sliver between
two ways (the 20-household seed 4 of the reference spec was refused `needle_loops` with the gather in), no house discharging
more free ends, no tail run on beside a way, no way out crossing a brook again - the tree's own rules (`tree.admits`), since
a gather may move a household's way - and no lane but the connector run beside another way past a pitch (`serve.runs_beside`,
way against way - the pool's finished-map reading of `WEB_SHADOW_FT`: Kuwabata, a foot gathered onto the junction beside it
ran its way 107 ft within 30 ft of another). Each is counted by `WebMemo.count`.

Research: plumbing - NONE: the law's own rules (`law.LAW`), asked of the web with the gather in"""


class WebMemo:
    """The whole web's questions a gather is asked (`settle_knots`), answered pair by pair and KEPT by each lane's points
    (the perf-audit of feature 328 wave 4: the step asked the whole web again for every trial, 2.2-2.5 s a 40-household map,
    though a gather moves one to three lanes). Which lanes join (`geom.ends_touch`, at `law.JOIN_TOL`: `law.lane_networks`,
    `settle.connector_component`), which share a tread (`checks.lanes_share_tread`: `checks.served_network`), how far a
    farmhouse stands from a lane (`checks.unreached_houses`), whose end runs on beside another way (`tails.tail_doubled`:
    `law.doubled_tails`) and which runs beside another way (`serve.runs_beside`: `shadowed`) are each a question of two lanes'
    points, so a trial asks only the pairs a moved lane is in and every other pair's answer is the one already given - the
    same answers as asking the whole web again, never pruned. A box test passes over a pair whose boxes lie beyond the join
    reach (no end nor vertex of either can come within it), the same verdict.

    Research: plumbing - NONE: the whole web's rules (`law.LAW`) asked of a trial web, each pair's answer kept"""

    def __init__(self) -> None:
        self._ids: dict[tuple[Pt, ...], int] = {}
        self._ways: list[Poly] = []
        self._legs: list[list[tuple[Pt, Pt]]] = []
        self._boxes: list[tuple[float, float, float, float]] = []
        self._runs: dict[int, list[Pt]] = {}
        self._pairs: dict[tuple[str, int, int], bool] = {}
        self._near: dict[tuple[float, float, int], float] = {}

    def ids(self, ways: Sequence[Poly]) -> list[int]:
        """Each way's number: one per distinct run of points."""
        out = []
        for p in ways:
            k = tuple(p)
            n = self._ids.get(k)
            if n is None:
                n = self._ids[k] = len(self._ways)
                self._ways.append(list(p))
                self._legs.append(list(zip(p, p[1:], strict=False)))
                self._boxes.append((min(q[0] for q in p), min(q[1] for q in p), max(q[0] for q in p), max(q[1] for q in p)) if p else (math.inf, math.inf, -math.inf, -math.inf))
            out.append(n)
        return out

    def _apart(self, a: int, b: int, reach: float) -> bool:
        ba, bb = self._boxes[a], self._boxes[b]
        return max(bb[0] - ba[2], ba[0] - bb[2], bb[1] - ba[3], ba[1] - bb[3]) > reach + 1e-6

    def pair(self, kind: str, a: int, b: int) -> bool:
        """The answer for ways `a` and `b` (numbers from `ids`): "touch" (`ends_touch` at `JOIN_TOL`), "share"
        (`lanes_share_tread`), "doubled" (`tail_doubled`, `a`'s end beside `b`) or "beside" (`runs_beside`, `a` beside `b`)."""
        key = (kind, a, b) if kind in ("doubled", "beside") or a <= b else (kind, b, a)
        got = self._pairs.get(key)
        if got is None:
            got = self._pairs[key] = self._ask(kind, a, b)
        return got

    def _ask(self, kind: str, a: int, b: int) -> bool:
        from ..consts import LANE_JOIN_FT
        from . import law
        from .checks import lanes_share_tread
        from .geom import ends_touch
        from .serve import runs_beside, sampled
        from .tails import tail_doubled

        p, o = self._ways[a], self._ways[b]
        if kind == "touch":
            return not self._apart(a, b, law.JOIN_TOL) and ends_touch(p, o, self._legs[a], self._legs[b], law.JOIN_TOL)
        if kind == "share":
            return not self._apart(a, b, LANE_JOIN_FT) and lanes_share_tread(p, o)
        if kind == "doubled":
            return tail_doubled(p, o)
        if a not in self._runs:
            self._runs[a] = sampled(p)
        return runs_beside(p, self._runs[a], o)

    def near(self, cx: float, cy: float, k: int) -> float:
        """How far the point (`cx`, `cy`) stands from way `k`'s nearest leg."""
        key = (cx, cy, k)
        d = self._near.get(key)
        if d is None:
            d = self._near[key] = min(seg_dist(cx, cy, a, b) for a, b in self._legs[k])
        return d

    def web(self, M: Mapping[str, Any], ways: Sequence[Poly], ids: Sequence[int]) -> tuple[int, set[int], int]:
        """For the web `M` (its lanes' points `ways`, numbered `ids`): how many networks its lanes fall into
        (`law.lane_networks`), the lanes joined to the connector's (`settle.connector_component`), and how many farmhouses it
        leaves unreached (`checks.unreached_houses`, asked with its served network's distances from here)."""
        from .checks import unreached_houses

        lanes = M.get("lanes") or []
        live = [i for i, p in enumerate(ways) if len(p) >= 2]
        par = {i: i for i in live}

        def find(i: int) -> int:
            while par[i] != i:
                par[i] = par[par[i]]
                i = par[i]
            return i

        for x, i in enumerate(live):
            for j in live[x + 1 :]:
                if self.pair("touch", ids[i], ids[j]):
                    par[find(i)] = find(j)
        roots = {find(i) for i in live if lanes[i].get("connector")}
        joined = {i for i in live if find(i) in roots}
        seed = next((i for i, ln in enumerate(lanes) if ln.get("connector")), None)
        if seed is None and ways:
            seed = max(range(len(ways)), key=lambda i: sum(math.dist(a, b) for a, b in zip(ways[i], ways[i][1:], strict=False)))
        served = [] if seed is None or len(ways[seed]) < 2 else [seed]  # `served_network`'s growth from its seed
        seen = set(served)
        for i in served:
            for j in live:
                if j not in seen and self.pair("share", ids[i], ids[j]):
                    seen.add(j)
                    served.append(j)
        unreached = len(unreached_houses(M, near=lambda cx, cy: min(self.near(cx, cy, ids[j]) for j in served))) if served else 0
        return len({find(i) for i in live}), joined, unreached

    def count(self, name: str, M: Mapping[str, Any], ways: Sequence[Poly], ids: Sequence[int]) -> int:
        """How many breaches of the whole web's rule `name` (`_WHOLE_RULES`) the web `M` holds - `doubled_tails` and
        `shadows` answered pair by pair, the rest asked of `M`."""
        from . import law

        lanes = M.get("lanes") or []
        if name in ("doubled_tails", "shadows"):
            kind = "doubled" if name == "doubled_tails" else "beside"
            return sum(1 for i, p in enumerate(ways) if not lanes[i].get("connector") and len(p) >= 2 and any(j != i and self.pair(kind, ids[i], ids[j]) for j in range(len(ways))))
        rule = {"needle_loops": law.needle_loops}.get(name) or law.LAW[name]  # the faces themselves: no centroid wanted
        return len(rule(M) or [])


def settle_knots(s: Any) -> int:
    """The settle's step (`settle.STEPS`): every knot of the web as it stands gathered at one node (`next_gather`), each gather
    asked the law of a new lane for every lane it moves (`settle.Lawful`, the moved lane left out of what it meets) and to split
    nothing: every lane joined to the connector's network still joined (`settle.connector_component`), the web in no more
    networks (`law.lane_networks`), no farmhouse newly unreached (`checks.unreached_houses`) and no more breaches of the
    whole web's rules (`_WHOLE_RULES`). The connector, a street, the field way and a way target's spur never move, nor a
    household's door end (`_fixed`); a household's FOOT may - its reserved corridor rewritten with it (`tree.set_corridor`), so
    the next round's draw of the tree (`tree.settle_tree`) keeps the gather - as may any other lane's end, a door path's too
    (Kashikawa: two farms' paths met their street 8.5 ft apart): an end re-aimed at the junction beside it, never a cut. A foot
    the seating left beside a junction where no gathered join was admitted (`gap_ways._way_for`) is gathered here, with the
    knot's corner taken out of the lane joining the two (`contracted`). A one-lane gather whose write the matrix refuses
    (`reshape_lane`) has its new leg bent round what stands in the first pass (`bent_round`, 405 T07: seed 57's leg ran past a
    household's copse seat); ends no bend writes are left, and that knot is not asked again this step. Returns the lanes moved. Each gather joins two nodes into one, so
    the step ends. The web as it stands is asked once a gather is applied, never once a trial; a trial's whole-web questions
    are answered pair by pair, each pair's answer kept by the two lanes' points (`WebMemo`) - the same verdicts.

    TWO PASSES (405 T107, D83): every knot is asked first with the fence gap as it stands (`WEB_FABRIC_GAP`, 0246's 7 ft, a
    convention), then the knots it leaves between households' ways (`ACCESS_ROLE`) with the join 3 ft off another household's garden
    (`WEB_CROP_GAP`'s value, a figure this project chose) - 0246 allows the 3 ft for two households' way ends a few feet apart,
    and every other lane keeps the gap (impl-drift, T07 round 1) - where the convention and 0081's knot rule collide, the research rule wins and the convention
    gives. The 3 ft is ours, a DEVIATION from 0246's 7 ft, recorded on the page with its reason (405 T114). Seed 24 (T26's sheds in) left two tees 25.0 ft apart whose diagonal
    passed 5.7 ft off a neighbor's fence. One pass at 3 ft on every knot knotted seed 7 (an earlier gather admitted at 3 ft
    reshaped the web), so it is the second pass only. More room between the homesteads was tried first: two wider `grow_gap`s (+5 and
    +10 ft), within the band the spacing pass of 2026-10-22 attests (specs/405-engine-findings-from-385/spacing-research.md),
    both measured worse.

    Research:
        lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft are joined at a single point
        a knot the fence gap leaves - DEVIATION research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the page's 7 ft (a map drawing convention) asked first, then the knots it leaves between two households' ways with the join 3 ft off another household's garden - the exception the page records, with its reason (two ways joined at one point, 0081; lots that abut closely) (405 T114)
        a lane with no width judged as a footpath - research/questions/0081-village-lanes.drawing.html: a lane with no recorded width is judged at the footpath's 3 ft"""
    from .settle import Lawful, apply_pieces  # bound here: `settle` names this step in its STEPS
    from .tree import set_corridor

    lanes = s.M.get("lanes") or []
    lawful = Lawful(s)
    apart = ground_apart(s.M, s)
    memo = WebMemo()
    moved = 0
    refused: list[dict[int, Poly]] = []
    ways: list[Poly] = []
    ids: list[int] = []
    had: dict[str, Any] = {}  # the web as it stands, asked once a gather is applied: it changes only then

    def judge(edits: dict[int, Poly]) -> bool:
        if edits in refused:
            return False
        if lawful.fence_gap < WEB_FABRIC_GAP and not households_only(lanes, edits):
            return False  # the 3 ft pass gathers households' ways only (0246; impl-drift, T07 rounds 1 and 2)
        if "nets" not in had:
            ways[:] = [_pts(ln) for ln in lanes]
            ids[:] = memo.ids(ways)
            had["nets"], had["joined"], had["unreached"] = memo.web(s.M, ways, ids)
        trial = {**s.M, "lanes": [dict(ln) for ln in lanes]}  # judged on a copy: a lane record refuses a write the matrix forbids
        tw = list(ways)
        for i, p in edits.items():
            trial["lanes"][i]["pts"] = [[x, y] for x, y in p]
            tw[i] = _pts(trial["lanes"][i])
        ti = memo.ids(tw)
        nets, joined, unreached = memo.web(trial, tw, ti)
        if not had["joined"] <= joined or nets > had["nets"] or unreached > had["unreached"]:
            return False
        lawful.M = trial
        try:
            if not all(lawful(p, float(lanes[i].get("w") or 3.0), skip=i) for i, p in edits.items()):
                return False
        finally:
            lawful.M = s.M
        # ...EACH WHOLE-WEB COUNT ASKED BY WHAT THE GATHER CHANGED (feature 387, plan D2b, `web_counts`): the web's own verdicts
        # kept once a web, the trial's re-asked only where an edit can change them - `way_outs` alone asked of the whole trial
        for name in _WHOLE_RULES:
            if name not in had:
                had[name] = base(name).count() if name != "way_outs" else memo.count(name, s.M, ways, ids)
            if trial_count(name, trial, tw, ti, list(edits)) > had[name]:
                return False
        return True

    def base(name: str) -> Any:
        """The web's own verdicts for one whole-web rule, kept until a gather is applied (`had` is cleared then)."""
        from .tree_base import Faces
        from .web_counts import Partners, WebEnds

        key = "_base_" + name
        if key not in had:
            if name in ("doubled_tails", "shadows"):
                had[key] = Partners("doubled" if name == "doubled_tails" else "beside", memo.pair, lanes, ways, ids)
            elif name == "doorstep_ends":
                had[key] = WebEnds(s.M, lanes, ways)
            else:
                had[key] = Faces(lanes)
        return had[key]

    def trial_count(name: str, trial: Mapping[str, Any], tw: list[Poly], ti: list[int], edits: list[int]) -> int:
        if name in ("doubled_tails", "shadows"):
            return int(base(name).trial(memo.pair, lanes, tw, ti, edits))
        if name == "doorstep_ends":
            return int(base(name).trial(trial, lanes, ways, tw, edits))
        if name == "needle_loops":
            return int(base(name).needles_with(trial["lanes"], [p for k in edits for p in (ways[k], tw[k])]))
        return memo.count(name, trial, tw, ti)

    for gap in (WEB_FABRIC_GAP, WEB_CROP_GAP):
        lawful.fence_gap = gap
        refused.clear()
        for _ in range(4 * len(lanes)):
            had.clear()
            edits = next_gather(lanes, judge, apart=apart)
            if edits is None:
                break
            before = {i: lanes[i]["pts"] for i in edits}
            apply_pieces(s, {i: [p] for i, p in edits.items()})
            n = 0
            for i in edits:
                if i < len(lanes) and lanes[i]["pts"] != before[i]:
                    n += 1
                    set_corridor(s.M, lanes[i])
            if not n and len(edits) == 1 and gap == WEB_FABRIC_GAP:
                ((i, p),) = edits.items()
                for bent in bent_round(p, 0 if _pts({"pts": before[i]})[0] != p[0] else -1):
                    if judge({i: bent}):
                        apply_pieces(s, {i: [bent]})
                        if lanes[i]["pts"] != before[i]:
                            n = 1
                            set_corridor(s.M, lanes[i])
                            break
            if not n:
                refused.append(edits)
            moved += n
    return moved


_KNOT_MARGIN = 1.0  # the page's own reach (feature 328); the slide the 1.5 caught is gone
"""How many knot reaches apart two junctions on one lane still count as a knot: 1.0, the page's own reach and no margin past
it. It was 1.5, to catch a foot slid along a lane to just past the reach (glyph-check round 2 of feature 328 wave 4, Inashiro:
lane 13's foot slid 16.7 ft along lane 11 to 25.18 ft from its end); that slide is gone, and at 1.0 a pair past 25 ft is no
knot, so the junction clause of `lane_knots` adds nothing to its 25 ft clause (feature 328 wave 93, impl-drift).

Research: a knot's reach - research/questions/0081-village-lanes.drawing.html: the page's own 25 ft, no margin past it"""


def lane_knots(lanes: Sequence[Mapping[str, Any]], M: Mapping[str, Any] | None = None) -> list[tuple[int, tuple[float, float], int, tuple[float, float], float]]:
    """The knots of a finished web, (lane, end, lane, end, ft): two lane ends within the knot reach (`_KNOT_FT`) of one another
    not standing at one point. Ends within `_JOINT_FT` are one point; a pair one lane runs between (its own two ends) is that
    lane, its join; a household way's lone door end teed on its own lane is no knot (`door_end_teed`). The pool's seed test (`tests/hamletgen/test_pool_261.py`) and
    the cohort (`tools/cohort_audit.py`) read this one verdict (feature 328 wave 93: the cohort lacked it, and a change that
    knotted three pool maps read 54/54).

    Research: lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft are joined at a single point, so three lanes never arrive a few feet apart in a knot"""

    apart = ground_apart(M) if M is not None else None
    pts = [[(float(x), float(y)) for x, y in ln.get("pts") or []] for ln in lanes]
    ends = [(i, p[e]) for i, p in enumerate(pts) if len(p) >= 2 for e in (0, -1)]
    node = list(range(len(ends)))

    def root(a: int) -> int:
        while node[a] != a:
            a = node[a]
        return a

    for a in range(len(ends)):
        for b in range(a + 1, len(ends)):
            if math.dist(ends[a][1], ends[b][1]) <= _JOINT_FT:
                node[root(b)] = root(a)
    spans = {frozenset((root(2 * k), root(2 * k + 1))) for k in range(len(ends) // 2)}  # each lane's own two points

    out = []
    for a in range(len(ends)):
        for b in range(a + 1, len(ends)):
            d = math.dist(ends[a][1], ends[b][1])
            if root(a) == root(b) or frozenset((root(a), root(b))) in spans or d > _KNOT_MARGIN * _KNOT_FT or (apart and apart(ends[a][1], ends[b][1])):
                continue
            # ...A DOOR END TEED ON ITS OWN LANE is no knot (`door_end_teed`, the predicate the gather search asks too)
            if any(door_end_teed(lanes, ends[x][0], 0 if x % 2 == 0 else -1, sum(root(z) == root(x) for z in range(len(ends))) == 1, ends[y][1]) for x, y in ((a, b), (b, a))):
                continue
            # (two JUNCTIONS on one lane up to `_KNOT_MARGIN` reaches apart were counted here too; at the margin's 1.0 every pair
            # left is within `_KNOT_FT`, so that clause could never add one and is gone - feature 328 wave 94, the coverage floor)
            out.append((ends[a][0], ends[a][1], ends[b][0], ends[b][1], round(d, 1)))
    return out
