"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, seg_closest, seg_dist

from ..consts import (
    Poly,
    Pt,
)
from .clearance import _ARM_FT, _HAIRPIN_DEG, _clear_link, _clear_touch, bowtie_cut
from .geom import _TOUCH_GAP, _components, _plen, _seg_cross, _turn_deg, polyline_len
from .sweeps import _SERVE_FT

_STUB_REACH_FT = 48.0  # the post-smoothing touch: a cut stub may stand a little past _LANE_JOIN_FT from the run it left (T99 unlock, seed 37)
# HOW LONG AN ARM MAY BE AND STILL BE CUT, once the cut has been MEASURED rather than assumed safe
# (feature 134 T50, 2026-08-28). `_ARM_FT` alone left a gap between this repair and the check it
# exists to satisfy: `lanes_bend_like_paths` fires on ANY turn past `_HAIRPIN_DEG`, while the repair
# would only cut an arm under 40 ft, so a hairpin on a longer arm was drawn and then failed - measured
# on tripwire seed 47, whose lane 11 doubled back 62 ft at (2487, 274) and could not be repaired at
# all. The length cap was standing in for "do not destroy a lane that is doing real work"; where that
# is measured directly - no farmhouse loses its way, the tip left behind still reaches something, and
# `_commit` still refuses anything that breaks the web into another piece - the cap buys nothing but a
# bound on how much of the picture one cut may change. That bound is the check's OWN farmhouse figure:
# past 90 ft the arm is reaching ground the rest of the lane cannot, so it is a lane in its own right
# and not an arm, and it stays (the bends check then fires on it honestly, as it did before).
_LONG_ARM_FT = 90.0
# `lanes_reach_something`'s two figures, so a cut never trades one failure for the other: after the
# cut the tip is the lane's END, and an end must reach another way or a farmhouse.
_END_WAY_FT = 40.0
_END_HOUSE_FT = 90.0
_JOG_FT = 6.0  # a vertex this close to the chord that replaces it was a jog, not a bend
_KNOT_FT = 25.0  # ends of different lanes this close are one junction, not several


def web_pieces(lanes: Sequence[Mapping[str, Any]]) -> int:
    """How many connected pieces the lane web is in - a lane of fewer than two points is not a piece.

    LIFTED OUT OF `_smooth_web` (feature 146, GM 2026-08-28: *"if something is only available as an inner
    function in a closure, then you can move it out into its own function to make it more unit testable"*).
    It closed over `lanes` alone and is a pure count, so a test can hand it three dicts instead of building
    a settlement, a fabric and a water list to reach it."""
    ways = [[(float(x), float(y)) for x, y in ln.get("pts") or []] for ln in lanes]
    comp = _components(ways, 4.0)
    return len({comp[m] for m in range(len(ways)) if len(ways[m]) >= 2})


def web_rejoinable(lanes: Sequence[Mapping[str, Any]], hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> bool:
    """After a rewrite that added a piece: will the post-smoothing touch pass close it again? Yes iff some
    end of the new piece stands within `_STUB_REACH_FT` of another piece's tread with a clear straight link
    (the touch pass draws exactly that). Inashiro's own smoothing makes such cuts and the touch repairs them;
    seed 37's stub sat 29 ft off in a 12 ft slot no link clears.

    LIFTED OUT OF `_smooth_web` for the same reason as `web_pieces`: it took nothing from the closure but
    these four values, and a caller that must build a whole web to ask it a yes/no question is a test nobody
    writes."""
    ways = [[(float(x), float(y)) for x, y in ln.get("pts") or []] for ln in lanes]
    comp = _components(ways, 4.0)
    live = [m for m in range(len(ways)) if len(ways[m]) >= 2]
    seed = next((m for m in live if lanes[m].get("connector")), live[0] if live else 0)
    for c in {comp[m] for m in live} - {comp[seed]}:  # every piece OTHER than the connector's must reach one
        mine = [m for m in live if comp[m] == c]
        # `segs` is NEVER empty here, and the `if not segs: continue` that stood on these lines was
        # therefore dead: `seed` is itself live and `comp[seed]` is excluded from `c`, so every other
        # component always has at least the seed's own tread to reach for. Removed with its reasoning
        # rather than left in place reading as a case that can happen (feature 146).
        segs = [sg for m in live if comp[m] != c for sg in zip(ways[m], ways[m][1:], strict=False)]
        ok = False
        for m in mine:
            for e in (ways[m][0], ways[m][-1]):
                foot = min((seg_closest(e[0], e[1], a, b) for a, b in segs), key=lambda z: math.dist(e, z))
                if math.dist(e, foot) <= _STUB_REACH_FT and _clear_touch(e, foot, hard, walls, water):
                    ok = True
                    break
            if ok:
                break
        if not ok:
            return False
    return True


def commit_lane(
    lanes: list[dict[str, Any]],
    m: int,
    new_pts: list[list[float]],
    hard: list[Poly],
    walls: Sequence[Poly],
    water: list[tuple[Pt, Pt]],
    reink: Callable[[int], None],
) -> bool:
    """Rewrite lane `m` - and put it back if the rewrite BREAKS the web and the touch pass cannot mend it.

    LIFTED OUT OF `_smooth_web` (feature 146, GM 2026-08-28 on inner functions and testability). The
    revert arm is the whole reason the function exists (feature 137 T03: a hairpin cut took the short
    arm that was a piece's only link to the spine, and tripwire seed 37, gate seed 43, Kashikawa and
    Sawada all came out failing `lanes_form_one_network`), and it is the arm a clean roll never enters -
    so it had no test until it could be called with four plain lists.
    """
    before, old = web_pieces(lanes), lanes[m]["pts"]
    lanes[m]["pts"] = new_pts
    if web_pieces(lanes) > before and not web_rejoinable(lanes, hard, walls, water):
        lanes[m]["pts"] = old
        return False
    reink(m)
    return True


def _smooth_web(s: Settlement, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> int:
    """The LAST pass over the web: take out what feet would never have worn.

    THE WEB WAS ASSEMBLED FROM FRAGMENTS AND NEVER READ AS LINES (GM 2026-08-27, feature 133 T32:
    *"there's a place where it looks like a loop-de-loop, which isn't how a lane would look. And then
    there's another place where it zig-zags just below the loop de loop for no apparent reason"*).
    Every earlier pass adds geometry - `clear_runs` cuts a 4 ft-stepped run, a join appends a link, a
    touch appends another, a trim takes an end off - and none of them looks at the lane it leaves
    behind as a SHAPE. Inashiro's lane 2 was 140 ft of path for a 49 ft chord, folded twice inside
    50 ft; lane 1 began with a 15 ft out-and-back; three lanes knotted into a bow-tie where one ran
    on across another for 20 ft. All legal by every gate, because the gates measured reach.

    Three repairs, each on the lane's RECORD with the ink rewritten (`reink_lane`), and each tested
    against the same footprint legality a junction link gets (`_clear_touch`):
      1. STRING-PULL - from each vertex, jump to the furthest later vertex the straight line reaches
         without crossing a footprint. This is what `_route` does to its own output; nothing did it to
         the assembled lane. It removes the zigzags and the dense 4 ft stepping in one move.
      2. HAIRPIN - a turn past `_HAIRPIN_DEG` with the shorter arm on one side: the arm is cut, unless
         its tip is the lane's only contact with another way. An arm under `_ARM_FT` is cut on its
         length alone; a longer one up to `_LONG_ARM_FT` is cut only once `_arm_cuttable` has measured
         that no farmhouse loses its way and the tip left behind still reaches something.
      3. BOW-TIE - where two lanes cross each other mid-run and one runs on past the crossing for
         less than `_ARM_FT`, that tail is cut back to the crossing, which becomes the junction.
    Ends are never moved except by cutting an arm, so every junction `_touch_junctions` made holds.
    `lanes_bend_like_paths` holds the line. Returns the number of lanes rewritten."""
    changed = 0
    lanes = s.M.get("lanes") or []

    # THE SMOOTHING NEVER DISCONNECTS THE WEB (feature 137 T03, 2026-08-28). Tripwire seed 37 (and
    # the gate cohort's 43, the pool's Kashikawa and Sawada) failed `lanes_form_one_network` after T32:
    # a hairpin cut took the short arm that was the piece's only link to the spine, and the orphan
    # joiner could not put it back - the spine's end and the stub's end stood 29 ft apart in a 12 ft
    # slot between a house and a threshing yard that the 7 ft fabric pad closes on both sides. The
    # repair that made the picture nicer had made the map wrong, and no later pass could undo it.
    # So every rewrite below goes through `_commit`: the web's piece count is taken before and after,
    # and a rewrite that adds a piece is refused and the lane left as it was. The bends check may
    # then fire on the kept hairpin - that is the honest verdict, and its own task (T04).
    # `_pieces()` stood here and lost its only caller when `_commit` moved out to `commit_lane`, which
    # counts the pieces itself. Removed with it (feature 146).

    def _commit(m: int, new_pts: list[list[float]]) -> bool:
        return commit_lane(lanes, m, new_pts, hard, walls, water, s.reink_lane)

    def _others_segs(skip: int) -> list[tuple[Pt, Pt]]:
        return [
            (a, b)
            for k, o in enumerate(lanes)
            if k != skip and len(o.get("pts") or []) >= 2
            for a, b in zip([(float(x), float(y)) for x, y in o["pts"]], [(float(x), float(y)) for x, y in o["pts"]][1:], strict=False)
        ]

    def _touching(q: Pt, segs: Sequence[tuple[Pt, Pt]]) -> bool:
        return any(seg_dist(q[0], q[1], a, b) <= 4.0 for a, b in segs)

    _houses = [(float(h["x"]), float(h["y"])) for h in s.M.get("houses", [])]

    def _near_segs(pt: Pt, segs: Sequence[tuple[Pt, Pt]]) -> float:
        return min((seg_dist(pt[0], pt[1], a, b) for a, b in segs), default=float("inf"))

    def _arm_cuttable(arm_len: float, arm: Poly, kept: Poly, tip: Pt, others: Sequence[tuple[Pt, Pt]]) -> bool:
        """May this hairpin arm be cut? Under `_ARM_FT` it is too short to be doing anything, which is
        the cheap answer this pass has always given. Between there and `_LONG_ARM_FT` the same question
        is MEASURED, the way `_join_orphan_ways` measures whether a fragment may be dropped: every
        farmhouse the arm serves must still be served without it, and the tip that becomes the lane's
        new end must still reach a way or a house by `lanes_reach_something`'s own figures. Beyond
        `_LONG_ARM_FT` the arm is a lane, not an arm, and it is kept."""
        if arm_len < _ARM_FT:
            return True
        if arm_len > _LONG_ARM_FT:
            return False
        arm_segs = list(zip(arm, arm[1:], strict=False))
        kept_segs = list(zip(kept, kept[1:], strict=False)) + list(others)
        if any(_near_segs(h, arm_segs) <= _SERVE_FT < _near_segs(h, kept_segs) for h in _houses):
            return False
        return _near_segs(tip, others) <= _END_WAY_FT or min((math.dist(tip, h) for h in _houses), default=float("inf")) <= _END_HOUSE_FT

    for i, ln in enumerate(lanes):
        if ln.get("connector") or len(ln.get("pts") or []) < 3:
            continue
        pts = [(float(x), float(y)) for x, y in ln["pts"]]
        others = _others_segs(i)
        # 2. hairpins first, so a string-pull does not shortcut across the fold and keep the arm
        for _round in range(3):
            cut = False
            for k in range(1, len(pts) - 1):
                if _turn_deg(pts[k - 1], pts[k], pts[k + 1]) < _HAIRPIN_DEG:
                    continue
                head, tail = polyline_len(pts[: k + 1]), polyline_len(pts[k:])
                if head <= tail and _arm_cuttable(head, pts[: k + 1], pts[k:], pts[k], others) and not (_touching(pts[0], others) and not _touching(pts[k], others)):
                    pts = pts[k:]
                    cut = True
                    break
                if tail < head and _arm_cuttable(tail, pts[k:], pts[: k + 1], pts[k], others) and not (_touching(pts[-1], others) and not _touching(pts[k], others)):
                    pts = pts[: k + 1]
                    cut = True
                    break
            if not cut or len(pts) < 3:
                break

        # 1. string-pull. A chord is taken at the web's own margins (`_clear_link`), or at footprint
        # margins when it is a SIMPLIFICATION - every vertex it replaces lies within `_JOG_FT` of it -
        # because a new line across open ground owes the houses their corridor (the first cut took
        # every footprint-legal chord and put a lane through a house's clearance and a bed's edge:
        # `houses_clear_of_lanes`, `features_do_not_overlap`), while the 4 ft stepping and the jogs
        # a junction leaves are the SAME line drawn badly.
        # THE CHORD OWES THIS LANE'S OWN KEEP-OUT, not a flat 4 ft (feature 134 T50) - see `_clear_touch`.
        _lane_gap = max(_TOUCH_GAP, float(ln.get("w") or 5.0) / 2.0 + 2.0)

        def _shortcut_ok(a: int, b: int, pts: Poly = pts, _g: float = _lane_gap) -> bool:
            if _clear_link(pts[a], pts[b], hard, walls, water):
                return True
            # A FOOTPATH CHORDED AT ITS OWN 4 ft MARGIN WAS TRIED AND ROTATED A BEND ONTO INASHIRO (feature 137
            # T04, 2026-08-28): letting a straggler lane take any chord `_clear_touch` allows straightened seed
            # 43's fold and put a new sharp bend on the reference hamlet's web. Not kept; the fold's real
            # cause is the straggler router folding inside a pocket, and that is where the fix belongs.
            if not _clear_touch(pts[a], pts[b], hard, walls, water, _g):
                return False
            return all(seg_dist(v[0], v[1], pts[a], pts[b]) <= _JOG_FT for v in pts[a + 1 : b])

        out = [pts[0]]
        a = 0
        while a < len(pts) - 1:
            b = len(pts) - 1
            while b > a + 1 and not _shortcut_ok(a, b):
                b -= 1
            out.append(pts[b])
            a = b
        pts = out
        # A DEAD END, MEASURED (feature 134 T50, 2026-08-29): running `_unjog` over the finished lane
        # here - the same three rungs (chord, knee, corner-off-apex) the router's own output gets - on
        # the theory that a bend the string-pull cannot chord is exactly what that pass repairs. It
        # changed the 24-seed cohort not at all (17/24 either way, the same four regressions), because
        # on the seeds that motivated it every rung is blocked: cohort seed 16's fold has 29 ft of
        # obstacle between the chord and the ground. Not kept - a shape change to every map on the
        # tier has to buy something. The bends that remain want the router not to fold there at all.
        if [[round(x, 1), round(y, 1)] for x, y in pts] != ln["pts"] and _commit(i, [[round(x, 1), round(y, 1)] for x, y in pts]):
            changed += 1
    # 4. KNOTS: ends of different lanes that stand within `_KNOT_FT` of one another meet at ONE
    # node. Three lanes arriving at three points a few feet apart drew a closed triangle on
    # Inashiro (the GM's "loop-de-loop"): each end had touched a tread, so every gate was
    # satisfied, and the eye read a loop. The node is the end that already lies on a THROUGH
    # lane's tread (a T stays a T), else the ends' centroid; every end in the cluster is moved
    # onto it, and a lane running through the cluster has its vertices there replaced by the
    # node, so it passes through the junction rather than beside it.
    _ends: list[tuple[int, int, Pt]] = [
        (i, e, ((float(ln["pts"][e][0]), float(ln["pts"][e][1])))) for i, ln in enumerate(lanes) if not ln.get("connector") and len(ln.get("pts") or []) >= 2 for e in (0, -1)
    ]
    _seen: set[tuple[int, int]] = set()
    for i, e, q in _ends:
        if (i, e) in _seen:
            continue
        cluster = [(j, f, r) for j, f, r in _ends if j != i and (j, f) not in _seen and math.dist(q, r) <= _KNOT_FT]
        if not cluster:
            continue
        cluster.append((i, e, q))
        # the node: an end standing on a lane that is NOT one of the cluster's own lanes' ends
        _members = {j for j, _f, _r in cluster}
        node: Pt | None = None
        for _j, _f, r in cluster:
            for k, o in enumerate(lanes):
                if k in _members or len(o.get("pts") or []) < 2:
                    continue
                _op = [(float(x), float(y)) for x, y in o["pts"]]
                if any(seg_dist(r[0], r[1], a, b) <= 4.0 for a, b in zip(_op, _op[1:], strict=False)):
                    node = r
                    break
            if node is not None:
                break
        if node is None:
            node = (sum(r[0] for _j, _f, r in cluster) / len(cluster), sum(r[1] for _j, _f, r in cluster) / len(cluster))
        for j, f, _r in cluster:
            _seen.add((j, f))
            _p = [(float(x), float(y)) for x, y in lanes[j]["pts"]]
            _p[f] = node
            # vertices of this lane inside the knot collapse onto the node too
            _p = [v for v in _p if v == node or math.dist(v, node) > _KNOT_FT] if len(_p) > 2 else _p
            _q: Poly = []
            for v in _p:
                if not _q or v != _q[-1]:
                    _q.append(v)
            # a way whose every vertex fell inside the knot collapses to ONE point - found at the T99
            # unlock on a tripwire seed (IndexError on `_q[-2]`); such a way is left as it was
            if len(_q) < 2:
                continue
            _nb = _q[1] if f == 0 else _q[-2]
            if _clear_touch(_nb, node, hard, walls, water) and [[round(x, 1), round(y, 1)] for x, y in _q] != lanes[j]["pts"] and _commit(j, [[round(x, 1), round(y, 1)] for x, y in _q]):
                changed += 1
    # 2b. shadows: a lane whose every vertex lies inside another lane's stroke is that lane drawn
    # twice (settlement-review at the T99 acceptance: lanes[7] lay for its whole 35.7 ft inside
    # lanes[9], 3.2 ft off its line, both 3 wide - ink-invisible, one way recorded twice). The shorter
    # one is emptied; `_components` and the checks read an empty way as absent.
    for i, ln in enumerate(lanes):
        pts_i = [(float(x), float(y)) for x, y in ln.get("pts") or []]
        if ln.get("connector") or len(pts_i) < 2:
            continue
        for j, other in enumerate(lanes):
            pts_j = [(float(x), float(y)) for x, y in other.get("pts") or []]
            if j == i or len(pts_j) < 2 or _plen(pts_j) < _plen(pts_i):
                continue
            tol = float(other.get("w", 3)) / 2 + float(ln.get("w", 3)) / 2 + 1.0
            if all(min(seg_dist(v[0], v[1], pts_j[k], pts_j[k + 1]) for k in range(len(pts_j) - 1)) <= tol for v in pts_i):
                if _commit(i, []):
                    changed += 1
                break
    # 3. bow-ties: a lane that crosses another mid-run and runs on for less than an arm
    for i, ln in enumerate(lanes):
        if ln.get("connector") or len(ln.get("pts") or []) < 2:
            continue
        pts = [(float(x), float(y)) for x, y in ln["pts"]]
        for k in range(len(pts) - 1):
            for j, o in enumerate(lanes):
                if j == i or len(o.get("pts") or []) < 2:
                    continue
                opts = [(float(x), float(y)) for x, y in o["pts"]]
                for m in range(len(opts) - 1):
                    x = _seg_cross(pts[k], pts[k + 1], opts[m], opts[m + 1])
                    if x is None:
                        continue
                    _cut = bowtie_cut(pts, k, x)
                    if _cut is None:
                        continue
                    pts = _cut
                    if _commit(i, [[round(px, 1), round(py, 1)] for px, py in pts]):
                        changed += 1
                    break
                else:
                    continue
                break
            else:
                continue
            break
    return changed
