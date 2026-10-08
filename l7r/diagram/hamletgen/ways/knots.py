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
    knot's corner taken out of the lane joining the two (`contracted`). Ends the matrix refuses to rewrite (`reshape_lane`)
    are left, and that knot is not asked again this step. Returns the lanes moved. Each gather joins two nodes into one, so
    the step ends. The web as it stands is asked once a gather is applied, never once a trial; a trial's whole-web questions
    are answered pair by pair, each pair's answer kept by the two lanes' points (`WebMemo`) - the same verdicts.

    Research:
        lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft are joined at a single point
        a lane with no width judged as a footpath - research/questions/0081-village-lanes.drawing.html: a lane with no recorded width is judged at the footpath's 3 ft"""
    from .settle import Lawful, apply_pieces  # bound here: `settle` names this step in its STEPS
    from .tree import set_corridor

    lanes = s.M.get("lanes") or []
    lawful = Lawful(s)
    memo = WebMemo()
    moved = 0
    refused: list[dict[int, Poly]] = []
    ways: list[Poly] = []
    ids: list[int] = []
    had: dict[str, Any] = {}  # the web as it stands, asked once a gather is applied: it changes only then

    def judge(edits: dict[int, Poly]) -> bool:
        if edits in refused:
            return False
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
        for name in _WHOLE_RULES:
            if name not in had:
                had[name] = memo.count(name, s.M, ways, ids)
            if memo.count(name, trial, tw, ti) > had[name]:
                return False
        return True

    for _ in range(4 * len(lanes)):
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
