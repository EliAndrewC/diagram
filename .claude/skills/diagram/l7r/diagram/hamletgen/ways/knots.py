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

from ..consts import Poly, Pt
from .corridors import ACCESS_ROLE, FIELD_ROLE, TARGET_ROLE
from .joints import _JOINT_FT
from .smooth import _KNOT_FT

Node = tuple[Pt, list[tuple[int, int]]]
"""A junction point and the (lane, end) pairs standing on it - `end` 0 or -1."""


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


def knots(lanes: Sequence[Mapping[str, Any]]) -> list[tuple[int, int, float]]:
    """The knots of the web: pairs of `end_nodes` indices that no one lane runs between standing within `_KNOT_FT` of one
    another - `KNOT_MARGIN` (1.0, the page's own reach) applying where both are JUNCTIONS (two or more ends, or an end on
    another lane's side) on one lane - nearest first, with their distance. (A 1.5 margin once caught a foot slid just past the
    reach; the slide is gone, and the margin went past the page - feature 328 wave 4.)

    Research: lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft are joined at a single point; the margin a map drawing convention (`gap_ways.KNOT_MARGIN`)"""
    nodes = end_nodes(lanes)
    where = {end: n for n, (_q, ends) in enumerate(nodes) for end in ends}
    spans = {frozenset((where[(i, 0)], where[(i, -1)])) for i, _e in where if _e == 0}
    out = []
    for a in range(len(nodes)):
        for b in range(a + 1, len(nodes)):
            d = math.dist(nodes[a][0], nodes[b][0])
            if d <= _KNOT_FT * KNOT_MARGIN and frozenset((a, b)) not in spans:
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


def next_gather(lanes: Sequence[Mapping[str, Any]], judge: Callable[[dict[int, Poly]], bool], fixed: Callable[[Mapping[str, Any], int], bool] = _fixed) -> dict[int, Poly] | None:
    """The first gather `judge` admits, nearest knot first: every end on one node of the knot moved onto the other node
    (`moved_onto`, both forms tried, then each with the knot's corner taken out of the lane joining the two - `contracted`) -
    the node with fewer ends moves, and the other way round where that is refused. A node holding a `fixed` end (by default
    `_fixed`) never moves. `judge` is handed the new points of every lane the gather moves, keyed by lane; None where no knot
    can be gathered.

    Research: lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft meet at one node"""
    nodes = end_nodes(lanes, fixed)
    for a, b, _d in knots(lanes):
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
    return None


_WHOLE_RULES = ("needle_loops", "doorstep_ends", "doubled_tails", "way_outs", "shadows")
"""The rules of the whole web a gather is asked besides the law of each lane it moves (`settle.Lawful`): no new sliver between
two ways (the 20-household seed 4 of the reference spec was refused `needle_loops` with the gather in), no house discharging
more free ends, no tail run on beside a way, no way out crossing a brook again - the tree's own rules (`tree.admits`), since
a gather may move a household's way - and no way run beside another past a pitch (`shadowed`: Kuwabata, a foot gathered
onto the junction beside it ran its way 107 ft within 30 ft of another).

Research: plumbing - NONE: the law's own rules (`law.LAW`), asked of the web with the gather in"""


def shadowed(M: Mapping[str, Any]) -> list[int]:
    """The lanes (the connector aside) that run beside another way past a pitch (`serve.shadowed_by`, way against way) - the
    pool's finished-map reading of `WEB_SHADOW_FT`.

    Research: no way drawn twice - UNRESEARCHED: within `WEB_SHADOW_FT` (30 ft), unbroken for more than a bundle pitch"""
    from .serve import shadowed_by

    lanes = M.get("lanes") or []
    ways = [_pts(ln) for ln in lanes]
    return [i for i, ln in enumerate(lanes) if not ln.get("connector") and len(ways[i]) >= 2 and shadowed_by(ways, i) is not None]


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
    knot's corner taken out of the lane joining the two (`contracted`). Ends the matrix refuses to rewrite (`reshape_lane`)
    are left, and that knot is not asked again this step. Returns the lanes moved. Each gather joins two nodes into one, so
    the step ends.

    Research: lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft are joined at a single point"""
    from . import law
    from .checks import unreached_houses
    from .settle import Lawful, apply_pieces, connector_component  # bound here: `settle` names this step in its STEPS
    from .tree import set_corridor

    lanes = s.M.get("lanes") or []
    lawful = Lawful(s)
    moved = 0
    refused: list[dict[int, Poly]] = []
    joined: set[int] = set()
    had: dict[str, int] = {}

    def judge(edits: dict[int, Poly]) -> bool:
        if edits in refused:
            return False
        trial = {**s.M, "lanes": [dict(ln) for ln in lanes]}  # judged on a copy: a lane record refuses a write the matrix forbids
        for i, p in edits.items():
            trial["lanes"][i]["pts"] = [[x, y] for x, y in p]
        if not joined <= connector_component(trial["lanes"]) or law.lane_networks(trial) > law.lane_networks(s.M) or len(unreached_houses(trial)) > len(unreached_houses(s.M)):
            return False
        lawful.M = trial
        try:
            if not all(lawful(p, float(lanes[i].get("w") or 3.0), skip=i) for i, p in edits.items()):
                return False
        finally:
            lawful.M = s.M
        for name in _WHOLE_RULES:
            rule = {"needle_loops": law.needle_loops, "shadows": shadowed}.get(name) or law.LAW[name]  # the faces themselves: no centroid wanted
            if name not in had:
                had[name] = len(rule(s.M) or [])
            if len(rule(trial) or []) > had[name]:
                return False
        return True

    for _ in range(4 * len(lanes)):
        joined = connector_component(lanes)
        had.clear()
        edits = next_gather(lanes, judge)
        if edits is None:
            break
        before = {i: lanes[i]["pts"] for i in edits}
        apply_pieces(s, {i: [p] for i, p in edits.items()})
        n = 0
        for i in edits:
            if i < len(lanes) and lanes[i]["pts"] != before[i]:
                n += 1
                set_corridor(s.M, lanes[i])
        if not n:
            refused.append(edits)
        moved += n
    return moved
