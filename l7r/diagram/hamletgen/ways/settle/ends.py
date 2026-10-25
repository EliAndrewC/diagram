"""The web settles itself - the settle's repairs of the ends and the joins: the ends, a dangling end, the shadows, a street's ends, the joins, the needles, the fragments, the widths, one network. Split from `ways/settle.py` at the 1,000-line bar (feature 405 T54, under T53's rule); the package docstring (`settle/__init__.py`) is the whole account.

Research: settle plumbing - NONE"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from ...consts import Poly
from .. import law
from ..arcs import sub_run
from ..corridors import (
    ACCESS_ROLE,
    is_tree,
)
from ..fabric import lane_fabric as _fabric
from ..forced import lazy_ground
from ..geom import _components, _trim_to_service, lane_owner, memo_ground, polyline_len, steading_footprints, worked_ground
from ..joints import joints, rank_width
from ..squaring import (
    _pts,
    cut_at_shallow_crossing,
)
from ..sweeps import _DOUBLED_DEG, along_tail, cut_at_tail
from ..tree import set_corridor, tree_faults
from .lawful import Lawful
from .shapes import JOIN_ROLE, _as_end, _back, _ordinary, apply_pieces, fouled_segment, reaimed


def settle_ends(s: Any) -> int:
    """Step 4: the joints and the ends (ways W05, W10, W16, W20, W21, W22) - each fixed by shortening, never lengthening.

    ONE FIX PER MEETING PER ROUND: a repair names every lane it involves (the lane it edits and the way it meets), and a
    later repair touching any of them waits for the next round. Two repairs made at once on the two sides of one joint -
    Kashikawa's field path re-aimed off a needle while the lane it continued was re-aimed off the fold at the same point -
    each assumed the other side stood still, and the web came apart there.

    Research:
        lanes met end to end read as one - research/questions/0081-village-lanes.drawing.html: a needle, fold or hairpin re-laid as a T
        no doubled tail - research/questions/0081-village-lanes.drawing.html: an end running back along another way under 20 degrees cut where it comes alongside - asked at `_DOUBLED_DEG`, 15, a known gap carried to 405 T101
        two paths side by side become one - research/questions/0081-village-lanes.drawing.html: a lane crossing another at under 20 degrees cut at the crossing (`cut_at_shallow_crossing`)
        a household's way moved at its foot - research/questions/0081-village-lanes.drawing.html: "cut at its far end, never at its door"
        a foot re-aimed only onto lawful ground - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the walker goes round a garden or yard, a way runs along the middle of the gaps
        which of a folded pair is re-aimed - GUESS: no source could speak to it, an algorithm's order, breadth or tolerance of ours (feature 417 T29 pass E, judged by the session from the code, 2026-10-25); the shorter record as the T; two bare legs lose the shorter
        a lane with no width judged as a footpath - research/questions/0081-village-lanes.drawing.html: a lane with no recorded width is judged at the footpath's 3 ft
        no fan of stubs at a door - GUESS: searched, the record silent (feature 417 T29 pass A2, 2026-10-25) - one main door served a minka's household (JAANUS, Edo period, pass A2); no page gives how many ends meet at one; past two ends at one house, the farther cut back past the doorstep
        a lane ends at the dooryard - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: an end within 60 ft of the house or
            12 ft of its built ground reaches it on any side; one that reaches nothing is trimmed to service (`settle_dangling`)"""
    M = s.M
    lanes = M.get("lanes") or []
    edits: dict[int, list[Poly]] = {}
    touched: set[int] = set()

    feet: list[dict[str, Any]] = []
    judge: list[Lawful] = []  # built at the first household way re-laid at its foot

    def claim(involved: set[int], i: int, pieces: list[Poly], end: int | None = None) -> None:
        # ...A HOUSEHOLD'S WAY AT ITS FOOT too (feature 385 T01, plan D4): side by side becomes one whichever lane it is, and
        # a household's way's foot may move as the knot gather moves it - never its door end - its corridor rewritten with it
        foot = end == -1 and lanes[i].get("role") == ACCESS_ROLE
        # ...and only into a lane: a re-aim leaving a household's way under two points or 1 ft would drop it, and its household
        foot = foot and bool(pieces) and len(pieces[0]) >= 2 and polyline_len(pieces[0]) >= 1.0
        # ...and only onto lawful ground: a re-aimed leg through another household's yard is a foul no later step may cut
        # from a tree lane, so the web would be refused for it (cohort seed 38, the first cohort of this change)
        if foot and is_tree(lanes[i]):
            if not judge:
                judge.append(Lawful(s))
            foot = judge[0].on_lawful_ground(pieces[0], float(lanes[i].get("w") or 3.0), lane_owner(lanes[i]))
        if not involved & touched and (not is_tree(lanes[i]) or foot):
            edits[i] = pieces
            touched.update(involved)
            if is_tree(lanes[i]):
                feet.append(lanes[i])

    centers = [(float(h["x"]), float(h["y"])) for h in M.get("houses") or []]
    for i, _n, k, _x in law.shallow_crossing_at(lanes):
        # ...TWO WAYS CROSSING AT A NEEDLE'S ANGLE are one path wandering over the other (plan D4): the lane that may be cut
        # is cut at the crossing, and its end left on the other way is re-aimed as a needle next round
        for m, o in ((i, k), (k, i)):
            if (cut := cut_at_shallow_crossing(lanes, m, o, centers)) is not None:
                claim({m, o}, m, [cut[0]], cut[1])
                break
    forced = lazy_ground(M, s)  # ...a meeting the ground forces is no needle, fold or hairpin to repair (feature 385 plan D2)
    for ci, i, end in law.connector_hairpin_ends(lanes, forced):
        claim({ci, i}, i, [_back(reaimed(_as_end(_pts(lanes[i]), end), _pts(lanes[ci]), connector=True, joiner=lanes[i].get("role") == JOIN_ROLE), end)])
    for i, end, k, _u, _v in law.needle_ends(lanes, forced):
        claim({i, k}, i, [_back(reaimed(_as_end(_pts(lanes[i]), end), _pts(lanes[k]), bool(lanes[k].get("connector")), lanes[i].get("role") == JOIN_ROLE), end)], end)
    for i, ei, j, ej in law.folded_joint_pairs(lanes, forced):
        # the SHORTER record of the two that has a vertex to fall back to is re-aimed as a T on the other; two bare legs
        # folded on each other lose the shorter
        x, y = _as_end(_pts(lanes[i]), ei), _as_end(_pts(lanes[j]), ej)
        both = sorted(((polyline_len(q), m, q, e, o) for m, q, e, o in ((i, x, ei, y), (j, y, ej, x)) if not is_tree(lanes[m])), key=lambda c: c[0])
        bent = [c for c in both if len(c[2]) >= 3]
        if not both:
            continue
        if bent:
            _len, m, seq, me, other = bent[0]
            claim({i, j}, m, [_back(reaimed(seq, other, joiner=lanes[m].get("role") == JOIN_ROLE), me)])
        else:
            claim({i, j}, both[0][1], [])
    for i in law.doubled_tails(M):
        p = _pts(lanes[i])
        # ...at whichever end runs on beside the way (`doubled_tails` asks both): the first end is cut as the last end of the
        # lane reversed, and turned back
        for j, o in enumerate(lanes):
            op = _pts(o)
            if j == i or len(op) < 2:
                continue
            hit = next(((q, k, back) for q, back in ((p, False), (p[::-1], True)) if (k := along_tail(q, op, deg=_DOUBLED_DEG)) is not None), None)
            if hit is not None:
                q, k, back = hit
                cut = cut_at_tail(q, k, op)
                claim({i, j}, i, [cut[::-1] if back else cut])
                break
    houses = M.get("houses") or []
    for h, ends in law.fronting_ends(M).items():
        c = (float(houses[h]["x"]), float(houses[h]["y"]))
        # ...the tree's ends kept first (a tree lane is never cut; the ordinary lanes defer to it), then the nearer
        for i, end in sorted(ends, key=lambda ie: (not is_tree(lanes[ie[0]]), math.dist(c, _pts(lanes[ie[0]])[ie[1]])))[law.DOORSTEP_MAX :]:
            seq = _as_end(_pts(lanes[i]), end)
            walk = next((polyline_len(seq[: k + 1]) for k in range(len(seq) - 1, -1, -1) if math.dist(seq[k], c) > law.DOORSTEP_FT), 0.0)
            claim({i}, i, [_back(sub_run(seq, 0.0, walk), end)] if walk > 0 else [])
    # (AN END BEHIND A HOUSE WAS CARRIED ROUND THE GABLE OR BACKED OFF HERE - water W57, 269 B17 - until feature 328: 0246
    # counts an end within 60 ft of the house or 12 ft of its built ground as reaching it on any side, and no page puts the
    # back wall out of reach.)
    if edits:
        changed = apply_pieces(s, edits)
        for ln in feet:
            if any(ln is x for x in lanes):
                set_corridor(M, ln)  # ...a household's way re-laid at its foot keeps its reserved corridor in step (`tree.settle_tree` redraws from it)
        return changed
    return settle_dangling(s)


def settle_dangling(s: Any) -> int:
    """Every ordinary lane is trimmed to service (`_trim_to_service`, at the law's own segment set): an end that reaches
    nothing but the way it left (W16), and an end served by a house alone that runs on past it (the road to nowhere, H41 -
    `_trim_to_service` stops it at its closest approach). No exemption for a house the lane alone reaches - that house is
    the corridor's. A lane the law still calls dangling after its trim goes whole.

    Research: an end reaches something seen - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: trimmed to service, else dropped"""
    M = s.M
    lanes = M.get("lanes") or []
    ground, steadings = memo_ground(s, "worked", worked_ground), steading_footprints(M)
    bad = {i for i, _e in law.dangling_lane_ends(M, ground)}
    ways = [_pts(ln) for ln in lanes]
    centers = [(float(h["x"]), float(h["y"])) for h in M.get("houses") or []]
    edits: dict[int, list[Poly]] = {}
    for i in _ordinary(M):
        others = [sg for k, o in enumerate(ways) if k != i and len(o) >= 2 for sg in zip(o, o[1:], strict=False)]
        trimmed = _trim_to_service(ways[i], others, centers, ground, (), steadings)
        if len(trimmed) < 2 or (i in bad and trimmed == ways[i]):
            edits[i] = []  # ...and one its trim cannot mend goes whole, as this docstring always said (feature 297: Inashiro's
            # two-point skeleton lane dangled through every round and the last resort dropped it - research R11)
        elif trimmed != ways[i] and (i in bad or polyline_len(ways[i]) - polyline_len(trimmed) > TRIM_GRAIN_FT):
            edits[i] = [trimmed]
    return apply_pieces(s, edits) if edits else 0


TRIM_GRAIN_FT = 1.0
"""A trim that takes less than this off a lane whose ends the law already calls served is the record's own rounding, not a
trim, and changes nothing; on a lane the law calls dangling any trim is taken."""


# ---- step 5: every join touches, then one network -----------------------------------------------------------------------


def settle_joins(s: Any) -> int:
    """Every join that stops short (`law.near_misses`: a free end making for a way within its reach, over walkable ground)
    is carried onto that way - it ends ON the tread it joins (homes H37), and a way drawn as two across a hole is one again
    (H38; the span may not run along a tread, H39). The only step that adds tread, and only to close a hole, once per end:
    an end it closes is no longer free. Before the network rule, so a piece the ink tolerance would drop is joined first.

    Research:
        ends that nearly meet are joined - research/questions/0081-village-lanes.drawing.html: carried onto the way
        a join taken back - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); an ordinary end whose join breaks a rule against a tree lane, or the overlap matrix refuses, taken back 5 ft past the join's reach (`JOIN_BACK_PAD_FT`), the settle's trims then pulling it to what it serves"""
    edits: dict[int, list[Poly]] = {}
    # A TREE LANE'S END IS CARRIED ONTO ITS WAY AS ANY LANE'S IS: the span only adds tread, over walkable ground, meeting the
    # way clean (`law.near_misses`), and the lane it reaches is an ordinary one the tree's joint then binds
    lanes = s.M.get("lanes") or []
    for i, end, f in law.near_misses(s.M):
        if i in edits:
            continue
        p = _pts(lanes[i])
        joined = [*p, f] if end == -1 else [f, *p]
        # ...BUT AN ORDINARY LANE WHOSE JOIN WOULD BREAK A RULE AGAINST A TREE LANE DEFERS: it is taken back out of the join's
        # reach instead - the deference would cut the join again, and the two passes took turns until the rounds ran out
        # (cohort seed 25 under the probes). AND SO DOES ONE WHOSE JOIN THE OVERLAP MATRIX REFUSES (feature 318, Kuwabata): the
        # law's walkable span reads the centerline 4 ft off a yard or garden, the matrix the whole tread, so a span the law
        # called walkable was refused at the write (`reshape_lane`) every round and the end left short of its way until the
        # web was refused - an end whose span is blocked is two ways, each ending at what it serves (`law.near_misses`)
        if not is_tree(lanes[i]) and (not _join_admitted(s, lanes[i], joined) or any(k == i for k, _q in tree_faults(with_edits(s.M, {i: [joined]})))):
            seq = _as_end(p, end)
            edits[i] = [_back(sub_run(seq, 0.0, polyline_len(seq) - law.JOIN_REACH_FT - JOIN_BACK_PAD_FT), end)]
            continue
        edits[i] = [joined]
    return apply_pieces(s, edits) if edits else 0


def _join_admitted(s: Any, ln: Mapping[str, Any], joined: Poly) -> bool:
    """Would the overlap matrix admit lane `ln` rewritten along `joined` - the question `reshape_lane` asks at the write,
    asked first so a refused join is taken back rather than left short (`settle_joins`, feature 318).

    Research: plumbing - NONE: the registry's own admission, at the record's 0.1 px
    """
    return bool(s.admits("lanes", {**ln, "pts": [[round(float(x), 1), round(float(y), 1)] for x, y in joined]}, ignore=ln))


JOIN_BACK_PAD_FT = 5.0
"""How far past a join's reach (`law.JOIN_REACH_FT`) an ordinary end that defers to a tree lane is taken back
(`settle_joins`), so it no longer makes for the way it stopped short of.

Research: a deferring end taken back - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); 5 ft past the join's reach"""


def with_edits(M: Mapping[str, Any], edits: Mapping[int, Sequence[Poly]]) -> dict[str, Any]:
    """`M` as `apply_pieces` would leave it after `edits`, its lane indices kept: each edited lane's first piece in place (a
    lane with none left empty rather than removed) and the further pieces appended."""
    lanes = [dict(ln) for ln in M.get("lanes") or []]
    extra = []
    for i, pieces in edits.items():
        lanes[i]["pts"] = [list(q) for q in pieces[0]] if pieces else []
        extra += [{"pts": [list(q) for q in p]} for p in pieces[1:]]
    return {**M, "lanes": [*lanes, *extra]}


def connector_component(lanes: Sequence[Mapping[str, Any]]) -> set[int]:
    """The lanes joined to the connector's network at the ink tolerance (`law.JOIN_TOL`) - what `settle_network` keeps."""
    live = [i for i, ln in enumerate(lanes) if len(ln.get("pts") or []) >= 2]
    labels = _components([_pts(lanes[i]) for i in live], law.JOIN_TOL)
    roots = {labels[n] for n, i in enumerate(live) if lanes[i].get("connector")}
    return {i for n, i in enumerate(live) if labels[n] in roots}


def settle_fragments(s: Any) -> int:
    """A fragment that earns nothing (`law.short_fragments`) is dropped (homes H40) - one a round, since two fragments can
    each be redundant only while the other stands. A TREE lane too, the connector aside (`short_fragments` never names it):
    a corridor drawn to a house a lane since reaches, or a spur whose target another way now serves, earns nothing, and
    the rule is FRAGMENT_FT for every lane (Kashikawa's lane 17, a 28.8 ft access corridor, and Mizuguchi's lane 11, 16.1
    ft, stayed drawn while the tree was exempt - research R9). Dropping it cuts nothing another way needs, so the
    termination argument stands: the drop shortens the web, and `short_fragments` names only a lane whose loss leaves no
    house, target or field newly unreached, so step 4 does not draw it again.

    Research: debris - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); a lane under 30 ft that earns nothing goes, a tree lane too"""
    gone = law.short_fragments(s.M, memo_ground(s, "worked", worked_ground))[:1]  # the web's one ground (the perf-audit of 308)
    if gone:
        s.drop_lanes(gone)
    return len(gone)


def rewidth(s: Any, i: int, width: float) -> None:
    """Lane `i` drawn at `width`: its record, and its ink re-laid at that width (the old ink blanked) where the settlement
    keeps ink - a stand-in with no ink has only the record."""
    ln = s.M["lanes"][i]
    ln["w"] = width
    ink = getattr(s, "_lane_ink", None)
    if ink is None:
        return
    for z in ink[i]:
        for part in ("edge", "bed", "top"):
            if s.ground[z].get(part):
                s.ground[z][part] = ""
    ink[i] = s._lane_ink_at(ln["pts"], width, bool(ln.get("worn")), ln)


def settle_widths(s: Any) -> int:
    """One way keeps one width (homes H42), and each way its rank's: a lane its role ranks (`joints.rank_width`: a household's
    way 3 ft, the field spur 5) is drawn at its rank whatever it meets end to end - feature 328 wave 4's glyph-check of
    Inashiro found a household's way and the spur widened to a 6 ft link's tread, a 6 ft lane hanging off a 3 ft footpath. A
    chain of lanes meeting end to end (`joints`) draws its unranked members at its widest ranked member's rank, or its widest
    member's where none is ranked - in either case at its narrowest where that would foul the fabric (`fouled_segment`). No
    tread is widened onto a steading; a step left is where one rank meets another (`law.width_steps`).

    Research: one width a way - research/questions/0081-village-lanes.drawing.html: each way at its rank's width (3 ft footpath, 5 ft field spur), the rest of a chain at its widest rank, the narrowest where that fouls"""
    lanes = s.M.get("lanes") or []
    changed = 0
    for k, ln in enumerate(lanes):
        r = rank_width(ln)
        if r is not None and not ln.get("connector") and float(ln.get("w") or 3.0) != r:
            rewidth(s, k, r)
            changed += 1
    par = list(range(len(lanes)))

    def find(k: int) -> int:
        while par[k] != k:
            k = par[k]
        return k

    for i, _ei, j, _ej in joints(lanes):
        par[find(i)] = find(j)
    yards, houses = _fabric(s)
    solid = law.solid_boxes(s.M)
    fixtures = law.fixture_quads(s.M)
    for root in {find(i) for i in range(len(lanes)) if find(i) != i}:
        chain = [k for k in range(len(lanes)) if find(k) == root]
        free = [k for k in chain if rank_width(lanes[k]) is None]
        widths = [float(lanes[k].get("w") or 3.0) for k in chain]
        ranks = [w for k, w in zip(chain, widths, strict=True) if k not in free]
        wide = max(ranks or widths)
        target = wide if all(fouled_segment(_pts(lanes[k]), wide, houses, yards, solid, fixtures, s.M, lane_owner(lanes[k])) is None for k in free) else min(widths)
        for k in free:
            if float(lanes[k].get("w") or 3.0) != target:
                rewidth(s, k, target)
                changed += 1
    return changed


def settle_network(s: Any) -> int:
    """Step 5 (ways W17): drop every lane not in the connector's network at the ink tolerance (`law.JOIN_TOL`).

    Research: one network - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane off the connector's network dropped"""
    lanes = s.M.get("lanes") or []
    live = [i for i, ln in enumerate(lanes) if len(ln.get("pts") or []) >= 2]
    labels = _components([_pts(lanes[i]) for i in live], law.JOIN_TOL)
    if len(set(labels)) <= 1:
        return 0
    roots = {labels[n] for n, i in enumerate(live) if lanes[i].get("connector")}
    if not roots:
        roots = {max(set(labels), key=lambda lb: sum(polyline_len(_pts(lanes[live[n]])) for n, x in enumerate(labels) if x == lb))}
    gone = [i for n, i in enumerate(live) if labels[n] not in roots]
    s.drop_lanes(gone)
    return len(gone)
