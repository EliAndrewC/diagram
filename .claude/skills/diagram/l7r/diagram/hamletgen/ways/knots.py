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
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from ..consts import Poly, Pt
from .joints import _JOINT_FT
from .smooth import _KNOT_FT

Node = tuple[Pt, list[tuple[int, int]]]
"""A junction point and the (lane, end) pairs standing on it - `end` 0 or -1."""


def _pts(ln: Mapping[str, Any]) -> Poly:
    return [(float(x), float(y)) for x, y in ln.get("pts") or []]


def _fixed(ln: Mapping[str, Any]) -> bool:
    """An end the gather never moves: the connector's and a row's street's (each laid before the houses and kept whole)."""
    return bool(ln.get("connector") or ln.get("street"))


def end_nodes(lanes: Sequence[Mapping[str, Any]], fixed: Callable[[Mapping[str, Any]], bool] = _fixed) -> list[Node]:
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
        at = next((ends[a][2] for a in members if fixed(lanes[ends[a][0]])), ends[members[0]][2])
        nodes.append((at, [(ends[a][0], ends[a][1]) for a in members]))
    return nodes


def knots(lanes: Sequence[Mapping[str, Any]]) -> list[tuple[int, int, float]]:
    """The knots of the web: pairs of `end_nodes` indices standing within `_KNOT_FT` of one another that no one lane runs
    between, nearest first, with their distance.

    Research: lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft are joined at a single point"""
    nodes = end_nodes(lanes)
    where = {end: n for n, (_q, ends) in enumerate(nodes) for end in ends}
    spans = {frozenset((where[(i, 0)], where[(i, -1)])) for i, _e in where if _e == 0}
    out = [(a, b, d) for a in range(len(nodes)) for b in range(a + 1, len(nodes)) if (d := math.dist(nodes[a][0], nodes[b][0])) <= _KNOT_FT and frozenset((a, b)) not in spans]
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


def next_gather(lanes: Sequence[Mapping[str, Any]], judge: Callable[[dict[int, Poly]], bool], fixed: Callable[[Mapping[str, Any]], bool] = _fixed) -> dict[int, Poly] | None:
    """The first gather `judge` admits, nearest knot first: every end on one node of the knot moved onto the other node
    (`moved_onto`, both forms tried) - the node with fewer ends moves, and the other way round where that is refused. A node
    holding a `fixed` end (by default `_fixed`) never moves. `judge` is handed the new points of every lane the gather moves, keyed by
    lane; None where no knot can be gathered.

    Research: lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft meet at one node"""
    nodes = end_nodes(lanes, fixed)
    for a, b, _d in knots(lanes):
        order = sorted(((b, a), (a, b)), key=lambda mt: len(nodes[mt[0]][1]))
        for mover, target in order:
            ends = nodes[mover][1]
            if any(fixed(lanes[i]) for i, _e in ends) or len({i for i, _e in ends}) < len(ends):
                continue  # a fixed end stays; a lane with both ends on one node is a loop no gather straightens
            for form in (0, 1):
                edits: dict[int, Poly] = {}
                for i, e in ends:
                    forms = moved_onto(_pts(lanes[i]), e, nodes[target][0])
                    edits[i] = forms[min(form, len(forms) - 1)]
                if judge(edits):
                    return edits
    return None


def settle_knots(s: Any) -> int:
    """The settle's step (`settle.STEPS`): every knot of the web as it stands gathered at one node (`next_gather`), each gather
    asked the law of a new lane for every lane it moves (`settle.Lawful`, the moved lane left out of what it meets) and to split
    nothing: every lane joined to the connector's network still joined (`settle.connector_component`), the web in no more
    networks (`law.lane_networks`) and no farmhouse newly unreached (`checks.unreached_houses`). The connector and a street never move (`_fixed`), nor a household's way, which is
    drawn as the seating judged it every round (`tree.settle_tree`, `tree._key`) - its foot is gathered where it is laid
    (`gap_ways.gathered_foot`); any other lane's end may, a door path's too (Kashikawa: two farms' paths met their street 8.5
    ft apart) - an end re-aimed at the junction beside it, never a cut. Ends the matrix refuses to rewrite (`reshape_lane`) are left, and that knot is not asked again this step. Returns the
    lanes moved. Each gather joins two nodes into one, so the step ends.

    Research: lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft are joined at a single point"""
    from . import law
    from .checks import unreached_houses
    from .settle import Lawful, apply_pieces, connector_component  # bound here: `settle` names this step in its STEPS
    from .tree import _key

    lanes = s.M.get("lanes") or []
    lawful = Lawful(s)
    moved = 0
    refused: list[dict[int, Poly]] = []
    joined: set[int] = set()

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
            return all(lawful(p, float(lanes[i].get("w") or 3.0), skip=i) for i, p in edits.items())
        finally:
            lawful.M = s.M

    for _ in range(4 * len(lanes)):
        joined = connector_component(lanes)
        edits = next_gather(lanes, judge, lambda ln: _fixed(ln) or _key(ln) is not None)
        if edits is None:
            break
        before = {i: lanes[i]["pts"] for i in edits}
        apply_pieces(s, {i: [p] for i, p in edits.items()})
        n = sum(1 for i in edits if i < len(lanes) and lanes[i]["pts"] != before[i])
        if not n:
            refused.append(edits)
        moved += n
    return moved
