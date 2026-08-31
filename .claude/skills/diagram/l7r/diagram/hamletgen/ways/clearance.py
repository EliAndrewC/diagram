"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import heapq
import math
from collections.abc import Sequence

from l7r.diagram.settlement import point_in_poly, seg_closest, seg_dist, seg_intersect, segments_cross

from ..clearance import fabric_index
from ..consts import (
    WEB_FABRIC_GAP,
    WEB_HARD_GAP,
    Poly,
    Pt,
)
from .geom import _TOUCH_GAP, _turn_deg, fabric_clearance, polyline_len, push_out_of


def _clear_link(a: Pt, b: Pt, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]], gap: float = WEB_FABRIC_GAP) -> bool:
    """Is the short run between two points walkable? Used before extending a lane end onto the way
    it meets, so a junction is drawn as a touch without the touch crossing anything."""
    span = math.dist(a, b)
    if span < 1.0:
        return True
    # THE WHOLE LINK, NOT A PIECE OF IT. Accepting the first surviving run let a snap be drawn across
    # ground that had been clipped out of the middle - the run existed, it just was not the gap being
    # bridged - and the lane ink then crossed a house or a garden bed
    # (`features_do_not_overlap`, `houses_clear_of_lanes`). A link is walkable only if it survives
    # end to end.
    runs = clear_runs([a, b], hard, WEB_HARD_GAP, step=3.0, lines=water, tight=walls, tight_margin=gap, floor=0.5)
    return any(polyline_len(r) >= span - 3.0 for r in runs)


def existing_walk(ways: Sequence[Poly], a: Pt, b: Pt, touch: float) -> float | None:
    """Shortest walk from `a` to `b` along the ways already drawn, or None when none exists.

    The lane network as a graph: each way is an edge between its two ends, weighted by its own drawn
    length, and two ends within `touch` of each other are the same junction. An end that lands part
    way ALONG another way joins it there, at the arc distance to each of that way's ends - which is
    the case that matters here, since a lane that tees into the middle of another is exactly the
    shape that makes a bridge redundant.

    Lifted to module level so it can be asked with plain lists (GM 2026-08-28 on testability)."""
    nodes: list[Pt] = []
    edges: list[list[tuple[int, float]]] = []

    def _node(p: Pt) -> int:
        for i, q in enumerate(nodes):
            if math.dist(p, q) <= touch:
                return i
        nodes.append(p)
        edges.append([])
        return len(nodes) - 1

    def _link(i: int, j: int, w: float) -> None:
        if i != j:
            edges[i].append((j, w))
            edges[j].append((i, w))

    live = [w for w in ways if len(w) >= 2]
    ends = [(_node(w[0]), _node(w[-1])) for w in live]
    for w, (i, j) in zip(live, ends, strict=False):
        _link(i, j, polyline_len(w))
    # ...and every end that tees into the MIDDLE of another way joins it THERE, in arc order along
    # that way. Linking a tee-point only to the way's two ends is not the same graph and quietly
    # over-states the walk: two spurs teeing into one lane 100 ft apart come out 200 ft apart, routed
    # out to an end and back, so a redundant loop looks like a worthwhile one.
    for k, w in enumerate(live):
        acc = [0.0]
        for u, v in zip(w, w[1:], strict=False):
            acc.append(acc[-1] + math.dist(u, v))
        along: list[tuple[float, int]] = [(0.0, ends[k][0]), (acc[-1], ends[k][1])]
        for n, p in enumerate(list(nodes)):
            if n in ends[k]:
                continue
            best = None
            for t, (u, v) in enumerate(zip(w, w[1:], strict=False)):
                c = seg_closest(p[0], p[1], u, v)
                d = math.dist(p, c)
                if best is None or d < best[0]:
                    best = (d, acc[t] + math.dist(u, c))
            if best is not None and best[0] <= touch:
                along.append((best[1], n))
        along.sort()
        for (a1, n1), (a2, n2) in zip(along, along[1:], strict=False):
            _link(n1, n2, a2 - a1)

    src, dst = _node(a), _node(b)
    if src == dst:
        return 0.0
    seen = [math.inf] * len(nodes)
    seen[src] = 0.0
    todo = [(0.0, src)]
    while todo:
        d, n = heapq.heappop(todo)
        if n == dst:
            return d
        if d > seen[n]:
            continue
        for m, w in edges[n]:
            nd = d + w
            if nd < seen[m] - 1e-9:
                seen[m] = nd
                heapq.heappush(todo, (nd, m))
    return None


_NUB_FT = 9.0  # a leading/trailing segment under this is not a stretch of way, it is a splice artifact
# NOT 5: the pass shipped at 5 ft and a settlement-review then found two nubs on Sawada that cleared it -
# an 8.25 ft boot turning -87 deg off a 117 ft run, and a 5.74 ft first segment turning 88 deg. The floor
# was set from the ONE case the pass was written for (3.1 ft) and was therefore calibrated below the defect
# rather than to it. 9 ft is about a lane-width-and-a-half at hamlet tier, and the blast radius was
# MEASURED before it was changed: over the whole pool, 5 -> 9 ft drops 3 more end vertices, all three on
# Sawada, no other map touched; 12 ft catches nothing 9 does not.
_NUB_TURN = 60.0  # ...and one that turns this far is a lump on the knuckle rather than the way arriving

# THE END SPIKE IS REAL, AND `_NUB_FT` IS THE WRONG LEVER FOR IT - DEFERRED WITH ITS MEASUREMENT
# (settlement-review, feature 155; constitution Principle XIV's "a deferral is a deliverable").
#
# THE DEFECT. Sawada's lane 10 runs 156.8 ft out, turns 119.9 deg and comes 21.1 ft back to touch the
# way it had left: at zoom an arrowhead driven into the lane rather than a path. `lanes_bend_like_paths`
# misses it because its hairpin bar is 140 deg, and the nub rule misses it because 21.1 > `_NUB_FT` (9).
# Three lanes on three live maps have the shape - sawada L10 (21.1 ft / 120 deg), kashikawa L4 (20.0 /
# 105), mizuguchi L3 (19.0 / 100) - measured over the whole pool.
#
# WHY THE OBVIOUS FIX IS WRONG, MEASURED. Widening the nub band to a severity-coupled second pair
# (`la < _WEB_MIN_FT and turn >= 100`) was implemented and rolled: Inashiro failed
# `farmhouses_reach_a_way` and Kashikawa and Mizuguchi failed `features_do_not_overlap`. The mechanism
# is that `drop_end_nubs` deletes the INTERIOR vertex and keeps the foot, so the lane re-routes along
# the straight line between what remains. At 9 ft that re-route is negligible, which is the whole
# reason the rule is safe; at 30 ft it drags the tread across whatever stood inside the elbow. The nub
# floor is not a number that was set too low - it is load-bearing.
#
# THE SKETCH. Dropping the spike's own END vertex instead is safe but fixes nothing observed: on all
# three maps the spike tip lands ON another lane (measured tip-to-lane distance 0.0), so it is a
# junction FOOT, and the lane has overrun its junction and doubled back to reach it. That makes this
# the same defect feature 150's junction pass already owns - "a lane ends where it first meets the way,
# bounded to a 40 ft overrun" - which is passing a lane whose overrun is 156.8 ft because it measures
# the overrun from the wrong end. The fix belongs there, with the pool rolled behind it, not here.
# NOT 90: the motivating nub measured 92.6 deg, and a bar sitting 2.6 deg under the one case it was
# written for stops firing the first time a re-roll nudges it. Dropping the vertex is near-free at a
# SMALL turn anyway (the two stretches are nearly collinear, so the tread barely moves), so the bar
# only limits scope - it does not protect anything - and 60 deg is where a 3 ft stretch reads as a lump.


def drop_end_nubs(ways: list[list[Pt]]) -> list[int]:
    """Indices whose SECOND (or second-to-last) vertex is a nub, dropped in place.

    A junction foot is laid on the way it meets; the vertex after it is whatever the lane's own first
    stretch was. When the splice leaves those two within a few feet of each other AND the lane then turns
    back on itself, the sheet shows a nub sticking out of the junction rather than a way arriving at it -
    Kuwabata's connector began (2442.4, 643.0) -> (2444.5, 645.3) with a 93-degree reversal, 3.1 ft of
    tread drawn as a lump on the knuckle (settlement-review 2026-08-29, error 2's second half).

    Only the vertex AFTER the end is dropped, never the end itself: the end is the foot, and moving it
    would take the lane off the way it was joined to. Lifted out of the pass below so it can be asked with
    plain lists (GM 2026-08-28 on testability)."""

    def nub_at_head(pts: list[Pt]) -> bool:
        """Is `pts[1]` a nub - a short first stretch that then turns back on itself?

        TWO BANDS, not one: a mild corner has to be very short to be a splice artifact
        (`_NUB_FT` / `_NUB_TURN`), while an outright reversal reads as a spike at any length below
        the floor for a way at all (`_SPIKE_FT` / `_SPIKE_TURN`). See the constants."""
        if len(pts) < 3:
            return False
        a, b, c = pts[0], pts[1], pts[2]
        ax, ay, bx, by = b[0] - a[0], b[1] - a[1], c[0] - b[0], c[1] - b[1]
        la, lb = math.hypot(ax, ay), math.hypot(bx, by)
        if la <= 0.0 or lb <= 1e-9:
            return False
        turn = math.degrees(math.acos(max(-1.0, min(1.0, (ax * bx + ay * by) / (la * lb)))))
        return la < _NUB_FT and turn >= _NUB_TURN

    hit: list[int] = []
    for i, pts in enumerate(ways):
        changed = False
        if nub_at_head(pts):
            del pts[1]
            changed = True
        pts.reverse()
        if nub_at_head(pts):
            del pts[1]
            changed = True
        pts.reverse()  # unconditional, so the lane always comes back in its drawn orientation
        if changed:
            hit.append(i)
    return hit


def may_write(old_pts: Sequence[Pt], new_pts: Sequence[Pt], width: float, fabric: Sequence[Poly]) -> bool:
    """May this rewrite of a lane be committed? JUDGE THE RESULT, NOT JUST THE MOVE.

    A TOUCH MAY NOT PUSH A LANE INTO THE FABRIC IT WAS DRAWN CLEAR OF (feature 134 T50). Every rung of
    the junction pass tests the LINK it is about to draw and none looks at the lane that comes out - so
    a link that is itself legal, spliced on by `_unjog`/`_unretrace` or by moving another lane's end
    onto a node, can leave a tread nearer a garden than the router ever put it. Traced on cohort seed
    18: footpaths drawn 5.2 ft clear of the nearest garden survived the smoother at 5.16 and came out
    of the pass at 1.21 - `features_do_not_overlap`, lanes x gardens.

    ...NOR PUT A BEND IN IT THAT FEET WOULD NEVER WEAR. Cohort seed 21's footpath was accepted with no
    bend in it and came out turning 90 degrees and then 60 within 34 ft; `_smooth_web` runs afterwards
    and cannot take the chord, because the steading the path was threading is still in the way, so the
    fold ships.

    BOTH RULES ARE "NO WORSE THAN IT WAS", not "good": a rewrite may leave a lane no nearer the fabric
    than it already was, or than its own keep-out allows - whichever is the more forgiving - and no
    worse bent than it already was. A lane already inside the bar is never made worse, but is not
    required to fix itself either, because the pass that is moving it is not the pass that owns it.
    """
    bar = max(_TOUCH_GAP, float(width or 5.0) / 2.0 + 2.0)
    if fabric_clearance(new_pts, fabric) < min(fabric_clearance(old_pts, fabric), bar) - 1e-9:
        return False
    return not (_bends_badly(new_pts) and not _bends_badly(old_pts))


def _clear_touch(a: Pt, b: Pt, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]], gap: float = _TOUCH_GAP) -> bool:
    """`_clear_link` at footprint margins - for the short link that closes a junction (see `_TOUCH_GAP`).

    THE DEFAULT 4 ft BRUSH STAYS - three wider margins were measured and each broke the reference hamlet
    (feature 137 T03, 2026-08-28): 7 ft (the fabric margin) put the T32 zigzag back beside the notice
    board and took the 24-cohort to 1/24; 6 ft for everything cost Inashiro three checks; 6 ft for
    gardens/yards/sheds with 4 for houses still cost it `lanes_bend_like_paths`. The margin was a
    ghost: on the current tree `houses_clear_of_lanes` is 0 of 48 and `features_do_not_overlap` 2 of
    48 - the T32-era brush failures were cured by later work (the set-back re-pack, the guard, the
    ladder). Do not widen this again without a failing seed that names it.

    `gap` IS THE CALLER'S TO RAISE, and that is not the flat widening warned off above (feature 134
    T50, 2026-08-28). All three reverted attempts moved the DEFAULT, which is charged to every junction
    link on the map. A caller rewriting one KNOWN lane can do better: the checks size a way's keep-out
    from its own width - `houses_clear_of_lanes` reads `half + 2.0` - so a repair on a 5 ft lane owes
    4.5 ft and one on a 3 ft lane owes 3.5. At the flat 4.0 the smoother was allowed to draw exactly
    what the check forbids, which is cohort seed 6: a farmhouse corner 4.09 ft from a 5 ft web lane,
    put there by a string-pull that tested its own chord and passed. Deriving it leaves the common 3 ft
    lane untouched (3.5 is below the default) and tightens only the wide ways."""
    span = math.dist(a, b)
    if span < 1.0:
        return True
    runs = clear_runs([a, b], hard, gap, step=3.0, lines=water, tight=walls, tight_margin=gap, floor=0.5)
    # THE WHOLE CHORD, NOT ALL BUT THREE FEET OF IT (feature 134 T50, 2026-08-29). This accepted a chord
    # whose longest CLEAR stretch reached `span - 3.0`, which is one sampling step - so a chord fouling
    # the fabric for up to three feet at one end passed as clear. That is exactly a corner graze, and it
    # is how a lane the router had drawn 7.6 ft clear of a neighbor's garden came back from `_smooth_web`
    # at 1.21 ft, with `features_do_not_overlap` reading lanes x gardens (cohort seed 18). The slack was
    # sampling tolerance, but at 1 px = 1 ft three feet is half the width the overlap matrix gives every
    # lane. `clear_runs` already carries its own `floor`, so the run may still be a sample short of the
    # span without licensing a foul.
    return any(polyline_len(r) >= span - 0.5 for r in runs)


# HOW A WORN LANE BENDS (researched 2026-08-27, feature 133 T32; research/homesteads.md "How does a
# village lane bend?"). A footpath is the line feet wear: the desire-line literature finds walkers
# minimize the NUMBER and the SEVERITY of turns, and a village lane bends at plot corners and runs
# straight between them. Nobody walks out fifteen feet and back, so a hairpin is never worn; nobody
# jinks twice in forty feet where a straight line is open, so a zigzag is never worn. The three
# numbers are drawing thresholds, not findings: a HAIRPIN is a turn past 140 degrees; a ZIGZAG is two
# turns past 50 degrees within 40 ft of path (about a dozen paces); an arm is worth removing only
# when it is shorter than 40 ft and reaches nothing of its own.
_HAIRPIN_DEG = 140.0
_ZIGZAG_DEG = 50.0
_ZIGZAG_RUN_FT = 40.0
_ARM_FT = 40.0


def _bends_badly(pts: Sequence[Pt]) -> bool:
    """The shape `lanes_bend_like_paths` refuses - a hairpin, or two 50 degree turns inside 40 ft.

    Stated here so a pass that is about to DRAW a run can ask before drawing, rather than leaving the
    gate to discover it. The thresholds are the check's own, deliberately: a repair that measures
    something other than what the check measures is the defect this file has now met three times."""
    for k in range(1, len(pts) - 1):
        if _turn_deg(pts[k - 1], pts[k], pts[k + 1]) >= _HAIRPIN_DEG:
            return True
    return any(
        _turn_deg(pts[k - 1], pts[k], pts[k + 1]) >= _ZIGZAG_DEG and _turn_deg(pts[k], pts[k + 1], pts[k + 2]) >= _ZIGZAG_DEG and math.dist(pts[k], pts[k + 1]) <= _ZIGZAG_RUN_FT
        for k in range(1, len(pts) - 2)
    )


def bowtie_cut(pts: Poly, k: int, x: Pt, arm_ft: float = _ARM_FT) -> Poly | None:
    """A lane crosses another at `x` inside its segment `k`; cut back the SHORT tail past the crossing,
    which then becomes the junction. `None` when neither side is short enough to be a stray tail.

    LIFTED OUT OF `_smooth_web` (feature 146). The head arm - the crossing near the lane's START, so the
    beginning is the stray - never ran on a live map; which arm a roll takes is an accident of which
    direction the lane happened to be recorded in, so the two want asking directly.
    """
    head = polyline_len(pts[: k + 1]) + math.dist(pts[k], x)
    tail = math.dist(x, pts[k + 1]) + polyline_len(pts[k + 1 :])
    if tail < arm_ft and tail <= head:
        return [*pts[: k + 1], x]
    if head < arm_ft and head < tail:
        return [x, *pts[k + 1 :]]
    return None


def route_around(poly: Poly, path: Poly, margin: float, rounds: int = 6) -> Poly:
    """Bend a drawn way OUT of `poly` by walking its outline round the obstruction.

    `connector_track` sweeps forty bearings and keeps the LEAST-BAD when none is clean, which is the
    right call for a track that has to reach the frame somehow - but least-bad can still mean a leg
    cutting straight across a lobe of the fan, which is what the GM saw on Inashiro (2026-08-12).

    A track meeting a field GOES ROUND IT, and that is what this does literally: where a leg enters
    the outline at one edge and leaves at another, the outline's own vertices between those two
    edges are spliced in (the shorter way round), each stepped `margin` clear on its local normal.
    An earlier version inserted ONE waypoint at the mean of the crossings and re-ran; it converged a
    few pixels per round and ran out of rounds still crossing, because a point pushed off the middle
    of a lobe lands right beside the leg it came from. Following the boundary is both the correct
    detour and the one a farmer walks."""
    ring = list(poly)
    n = len(ring)
    out = [push_out_of(poly, q, margin) for q in path]
    for _ in range(rounds):
        redo: Poly = []
        cut = False
        for i in range(len(out) - 1):
            redo.append(out[i])
            a, b = out[i], out[i + 1]
            hits = [(k, h) for k in range(n) if segments_cross(a, b, ring[k], ring[(k + 1) % n]) and (h := seg_intersect(a, b, ring[k], ring[(k + 1) % n])) is not None]
            if len(hits) < 2:
                if (
                    hits
                ):  # pragma: no cover - a leg from outside to outside crosses a closed ring an EVEN number of times, so this is the guard for a leg grazing a vertex; no cohort map has produced one
                    redo.append(push_out_of(poly, hits[0][1], margin))
                    cut = True
                continue
            hits.sort(key=lambda kh: math.hypot(kh[1][0] - a[0], kh[1][1] - a[1]))
            k0, k1 = hits[0][0], hits[-1][0]
            fwd = [(k0 + 1 + t) % n for t in range((k1 - k0) % n)]
            bwd = [(k0 - t) % n for t in range((k0 - k1) % n)]
            way = fwd if len(fwd) <= len(bwd) else bwd
            redo += [push_out_of(poly, ring[t], margin) for t in way]
            cut = True
        redo.append(out[-1])
        out = redo
        if not cut:
            break
    return out


def clear_runs(
    pts: Poly,
    obstacles: Sequence[Poly],
    margin: float,
    step: float = 8.0,
    lines: Sequence[tuple[Pt, Pt]] = (),
    line_margin: float = 14.0,
    tight: Sequence[Poly] = (),
    tight_margin: float = 6.0,
    floor: float = 70.0,
) -> list[Poly]:
    """EVERY clear stretch of a polyline, not just the first or the longest - the through-lane
    counterpart of `clip_to_clear`.

    The difference is which end the blockage is allowed to cost you. `clip_to_clear` stops at the
    first ground the line may not cross, which is exactly right for a skeleton ARM: an arm radiates
    outward from the cluster, so everything past the blockage is beyond it anyway. A WEB lane is not
    an arm - it runs the length of the margin, and its two ends are just its two ends. Truncating it
    at the first fouled sample threw away the whole lane whenever the sampling happened to start in
    the crop, which is how Inashiro's back lanes came back as 250 ft of an intended 1400 while
    Sawada's alley spine - identical code, luckier starting end - survived at 719 ft. A lane does not
    cease to exist because the far end of the margin is under water.

    TWO OBSTACLE FAMILIES, because a web lane relates to them differently. `obstacles` is ground the
    lane may not go near at all - crop, marsh, the wet toe - and keeps the full `margin`. `tight` is
    the settlement's own fabric: houses, yards, gardens, groves. A lane threads BETWEEN those; it is
    the leftover room between two steadings, and holding it 20 ft off every wall would mean there is
    nowhere for it to be. So `tight` gets `tight_margin`, which is a hand's breadth.

    Returns every run that reaches `floor`, which defaults to the same 70 ft `clip_to_clear` uses.
    A short one is a real exception rather than a loosening: the footpath from an outlying steading's
    door to the nearest way is 60-odd feet by construction, and refusing it as a stub left eight
    houses unreachable while a path to each was being drawn and discarded. A back lane interrupted
    by a steading is two lanes, not one shortened one - and returning only the longest threw away
    ground that genuinely serves houses at the other end.

    A stub below the floor is not a lane, whichever way it was measured."""
    if not obstacles and not lines and not tight:
        return [list(pts)]

    # THE FABRIC INDEX (feature 138) replaces the per-call bounding-box prefilter and the per-sample
    # scan of every surviving polygon's every edge: built once here (or once per routing box by
    # `_route`, which used to call this function once PER LATTICE CELL - 165,611 times on one polder),
    # it files each polygon and line by grid cell so a sample measures only its cell's candidates.
    # Same verdicts by construction - the candidates are a superset of what the box prefilter kept,
    # measured with the same predicate; `clearance.py` carries the argument and the oracle test.
    index = fabric_index(obstacles, margin, tight, tight_margin, lines, line_margin)
    fouled = index.fouled

    samples: Poly = [pts[0]]
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        samples.extend((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(1, n + 1))
    runs: list[Poly] = []
    run: Poly = []
    for q in samples:
        if fouled(q):
            if len(run) >= 2 and polyline_len(run) >= floor:
                runs.append(run)
            run = []
            continue
        run.append(q)
    if len(run) >= 2 and polyline_len(run) >= floor:
        runs.append(run)
    return runs


def clip_to_clear(pts: Poly, obstacles: Sequence[Poly], margin: float, step: float = 8.0, lines: Sequence[tuple[Pt, Pt]] = (), line_margin: float = 14.0) -> Poly:
    """Shorten a polyline so it stops before the first ground it may not cross.

    Used on the cluster's lane arms. Dragging an offending VERTEX back toward the cluster was tried
    first and is not reliable: a vertex deep inside a large hem plot may not escape in the steps
    allowed, and it distorts the skeleton on the way. Truncating is both simpler and more honest -
    the lane ends where the crop begins, which is what a village lane does.

    AN ARM WITH NOWHERE TO GO RETURNS NOTHING, and this line used to say the opposite (feature 166:
    "Always returns at least a two-point line so the caller still has a lane"). It was true of the
    FIRST version, which fell back to the original first segment - and that fallback drew a lane
    blocked immediately in full and unclipped, doing the exact opposite of this function's job. The
    fallback went; the sentence describing it did not. A run shorter than 70 px is dropped, so the
    caller must handle an empty result rather than assuming a lane."""
    if not obstacles and not lines:
        return pts

    def fouled(q: Pt) -> bool:
        if any(seg_dist(q[0], q[1], a, b) < line_margin for a, b in lines):
            return True
        return any(point_in_poly(q[0], q[1], list(o)) or min(seg_dist(q[0], q[1], o[j], o[(j + 1) % len(o)]) for j in range(len(o))) < margin for o in obstacles)

    out: Poly = [pts[0]]
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        run = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(run / step))
        last = a
        for k in range(1, n + 1):
            q = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
            if fouled(q):
                # NOTHING is returned if the surviving run is too short to be a lane. The first
                # version fell back to the ORIGINAL first segment here, which meant a lane blocked
                # immediately was drawn in full, unclipped - a fallback that does the opposite of
                # the function's job. A skeleton arm with nowhere to go is not drawn at all.
                trimmed = out + [last]
                return trimmed if polyline_len(trimmed) >= 70.0 else []
            last = q
        out.append(b)
    return out
