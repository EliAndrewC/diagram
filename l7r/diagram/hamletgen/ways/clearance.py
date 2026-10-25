"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index.

Research: plumbing - NONE
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence

from l7r.diagram.settlement import seg_intersect, segments_cross

from ..clearance import FabricIndex, fabric_index
from ..consts import (
    WEB_FABRIC_GAP,
    WEB_HARD_GAP,
    Poly,
    Pt,
)
from .geom import _turn_deg, polyline_len, push_out_of
from .keeper import kept


def link_index(hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]], gap: float = WEB_FABRIC_GAP) -> FabricIndex:
    """The fabric index `_clear_link` asks with these grounds and this gap - built once by a caller that tests many links
    (feature 284, FR-002).

    Research:
        its figures against 0055 - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.html: 14 (link held 14 ft off water lines) - a departure the code keeps until feature 417 T32
    """
    return fabric_index(hard, WEB_HARD_GAP, walls, gap, water, 14.0)


def _clear_link(a: Pt, b: Pt, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]], gap: float = WEB_FABRIC_GAP, index: FabricIndex | None = None) -> bool:
    """Is the short run between two points walkable? Used before extending a lane end onto the way
    it meets, so a junction is drawn as a touch without the touch crossing anything.

    Research:
        link clear of the fabric - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the link's line 7 ft off a garden fence (the page's fence to the middle of the lane), its edge 5.5 ft
        link clear of the crop - research/questions/0081-village-lanes.drawing.html: half the widest tread off the crop (`WEB_CROP_GAP`)
        link clear of the wet ground and the water - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.html, research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a path runs on the bank of every grade of field channel, and the bund is a path - the link is held 14 ft off the water, a departure the code keeps until feature 417 T32; 8 ft off the toe and marsh, 14 ft off water"""
    span = math.dist(a, b)
    if span < 1.0:
        return True
    # THE WHOLE LINK, NOT A PIECE OF IT. Accepting the first surviving run let a snap be drawn across
    # ground that had been clipped out of the middle - the run existed, it just was not the gap being
    # bridged - and the lane ink then crossed a house or a garden bed
    # (`features_do_not_overlap`, `houses_clear_of_lanes`). A link is walkable only if it survives
    # end to end.
    if not hard and not water and not walls:
        return True  # `clear_runs` hands the link back whole
    fouled = (index if index is not None else fabric_index(hard, WEB_HARD_GAP, walls, gap, water, 14.0)).fouled
    return link_survives(a, b, fouled, span - 3.0)


_LINK_STEP = 3.0  # ft: `_clear_link`'s sample pitch along the link
_LINK_FLOOR = 0.5  # ft: the shortest run `_clear_link` counts (`clear_runs`' floor as it asks)
_LINK_EPS = 1e-6  # ft: past any rounding between a run's summed legs and its chord


def link_survives(a: Pt, b: Pt, fouled: Callable[[Pt], bool], need: float) -> bool:
    """`any(polyline_len(r) >= need for r in clear_runs([a, b], ..., step=3.0, floor=0.5))` - the SAME samples asked the SAME
    `fouled`, in order - but decided as soon as it is known (dev/performance.md, shape one): the string-pull of `_route` asks a
    link from each vertex to every later one, longest first, and nearly every long one is fouled near its middle, so the walk
    of its every sample was the router's second cost (cohort seed 44, 928 links). It answers True once a clear run in progress
    is already longer than `need` (a run only grows), and False once a fouled sample leaves too little link after it for any
    run to be; the length that decides is the run's own `polyline_len`, with a margin past rounding on each early answer."""
    n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / _LINK_STEP))
    thr = max(need, _LINK_FLOOR)
    run: Poly = []
    done = 0.0  # the run's length so far, summed leg by leg (`polyline_len` sums the same legs)
    for k in range(n + 1):
        q = a if k == 0 else (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
        if fouled(q):
            if len(run) >= 2 and (length := polyline_len(run)) >= _LINK_FLOOR and length >= need:
                return True
            if math.dist(q, b) + _LINK_EPS < thr:
                return False  # every run after this sample lies within the rest of the link, shorter than asked
            run, done = [], 0.0
            continue
        if run:
            done += math.hypot(q[0] - run[-1][0], q[1] - run[-1][1])
        run.append(q)
        if len(run) >= 2 and done > thr + _LINK_EPS:
            return True
    return len(run) >= 2 and (length := polyline_len(run)) >= _LINK_FLOOR and length >= need


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


def _clear_touch(a: Pt, b: Pt, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]], gap: float = WEB_FABRIC_GAP) -> bool:
    """`_clear_link` at footprint margins - for the short link that closes a junction.

    THE DEFAULT IS THE LANE PAGE'S 7 ft SINCE FEATURE 328 (research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html:
    a lane's middle at least 7 ft from a garden fence). HISTORY, before it (kept so no one re-measures it): the 4 ft brush once stood here, and three wider margins were measured against it and each broke the reference hamlet
    (feature 137 T03, 2026-08-28): 7 ft (the fabric margin) put the T32 zigzag back beside the notice
    board and took the 24-cohort to 1/24; 6 ft for everything cost Inashiro three checks; 6 ft for
    gardens/yards/sheds with 4 for houses still cost it `lanes_bend_like_paths`. The margin was a
    ghost: on the current tree `houses_clear_of_lanes` is 0 of 48 and `features_do_not_overlap` 2 of
    48 - the T32-era brush failures were cured by later work (the set-back re-pack, the guard, the
    ladder). 405 T65 widened the join links to the page's 7 ft on that footing, and seeds 1-48 held.

    `gap` IS THE CALLER'S TO RAISE, and that is not the flat widening warned off above (feature 134
    T50, 2026-08-28). All three reverted attempts moved the DEFAULT, which is charged to every junction
    link on the map. A caller rewriting one KNOWN lane can do better: the checks size a way's keep-out
    from its own width - `houses_clear_of_lanes` reads `half + 2.0` - so a repair on a 5 ft lane owes
    4.5 ft and one on a 3 ft lane owes 3.5. At the flat 4.0 the smoother was allowed to draw exactly
    what the check forbids, which is cohort seed 6: a farmhouse corner 4.09 ft from a 5 ft web lane,
    put there by a string-pull that tested its own chord and passed. Deriving it leaves the common 3 ft
    lane untouched (3.5 is below the default) and tightens only the wide ways.

    Research:
        junction link margin - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 7 ft (`WEB_FABRIC_GAP`) off the fabric, or the caller's
        a join link never on the crop - research/questions/0081-village-lanes.drawing.html: a lane never crosses row crops
        a join link off the crop at the gap - DEVIATION research/questions/0081-village-lanes.drawing.html: the page lets a lane run on the bund and touch a plot's boundary; the link keeps the fabric's 7 ft (`gap`) off the crop - the departure the page is yet to record (405 T98)
        a join link off the wet ground at the gap - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A1, 2026-10-25); the link keeps the fabric's 7 ft off the toe and the marsh, where a lane's link keeps 8 ft (`_clear_link`); no page gives either
        a join link off the water - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.html, research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a path runs on the bank of every grade of field channel, and the bund is a path - the join link is held 14 ft off the water, a departure the code keeps until feature 417 T32; 14 ft off the water lines (`clear_runs`' `line_margin`), as `_clear_link`
        a join link off every garden - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the gap is kept from another household's garden and a household's own way may run beside its own; a link joins a way to the network and belongs to no one household, so no garden is its own"""
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


# HOW A WORN LANE BENDS (researched 2026-08-27, feature 133 T32; research/questions/0081-village-lanes.html and
# research/questions/0081-village-lanes.drawing.html). A footpath is the line feet wear: the desire-line literature finds walkers
# minimize the NUMBER and the SEVERITY of turns, and a village lane bends at plot corners and runs
# straight between them. Nobody walks out fifteen feet and back, so a hairpin is never worn; nobody
# jinks twice in forty feet where a straight line is open, so a zigzag is never worn. The three
# numbers are drawing thresholds, not findings: a HAIRPIN is a turn past 140 degrees; a ZIGZAG is two
# turns past 50 degrees within 40 ft of path (about a dozen paces); an arm is worth removing only
# when it is shorter than 40 ft and reaches nothing of its own.
_HAIRPIN_DEG = 140.0
"""Research: hairpin - research/questions/0081-village-lanes.drawing.html: a turn past 140 degrees"""
_ZIGZAG_DEG = 50.0
"""Research: zigzag turn - research/questions/0081-village-lanes.drawing.html: two turns past 50 degrees"""
_ZIGZAG_RUN_FT = 40.0
"""Research: zigzag run - research/questions/0081-village-lanes.drawing.html: within 40 ft of path"""


@kept
def kink_spans(pts: Sequence[Pt]) -> list[tuple[str, int, int]]:
    """Where a run fails to bend like a path, as (kind, first vertex, last vertex): a turn of more than `_HAIRPIN_DEG`
    ("doubles back", one vertex), or two turns of more than `_ZIGZAG_DEG` whose SUMMED path between them is `_ZIGZAG_RUN_FT`
    or less ("kinks") - the whole run between the two turns, not one segment.

    ONE BEND PREDICATE (feature 287, ways W18, FR-003). The web's passes asked a one-segment reading here - two big turns
    separated by ONE short segment - while the finished-map tests summed the run between them, so a lattice step of two
    short legs passed every pass and failed the test (seed 43). The test's reading is the rule; `law.kinks` reads this one body
    (`_bends_badly`, the passes' copy, went with them in feature 417 T26).

    Research:
        no hairpin - research/questions/0081-village-lanes.drawing.html: a turn of more than 140 degrees
        no zigzag - research/questions/0081-village-lanes.drawing.html: two 50 degree turns within 40 ft of path"""
    p = list(pts)
    bad: list[tuple[str, int, int]] = []
    if len(p) < 3:
        return bad
    turns: list[int] = []
    for k in range(1, len(p) - 1):
        if math.dist(p[k - 1], p[k]) < 1e-6 or math.dist(p[k], p[k + 1]) < 1e-6:
            continue
        deg = _turn_deg(p[k - 1], p[k], p[k + 1])
        if deg > _HAIRPIN_DEG:
            bad.append(("doubles back", k, k))
        elif deg > _ZIGZAG_DEG:  # ...more than 50, as 0081 counts a zigzag's turns (405 T96)
            turns.append(k)
    for ka, kb in zip(turns, turns[1:], strict=False):
        if sum(math.dist(p[j], p[j + 1]) for j in range(ka, kb)) <= _ZIGZAG_RUN_FT:
            bad.append(("kinks", ka, kb))
    return bad


def route_around(poly: Poly, path: Poly, margin: float, rounds: int | None = None) -> Poly | None:
    """Bend a drawn way OUT of `poly` by walking its outline round the obstruction.

    `connector_track` sweeps 41 bearings and keeps the LEAST-BAD dry one when none is clean, which is the
    right call for a track that has to reach the frame somehow - but least-bad can still mean a leg
    cutting straight across a lobe of the fan, which is what the GM saw on Inashiro (2026-08-12).

    A track meeting a field GOES ROUND IT, and that is what this does literally: where a leg enters
    the outline at one edge and leaves at another, the outline's own vertices between those two
    edges are spliced in (the shorter way round), each stepped `margin` clear on its local normal.
    An earlier version inserted ONE waypoint at the mean of the crossings and re-ran; it converged a
    few pixels per round and ran out of rounds still crossing, because a point pushed off the middle
    of a lobe lands right beside the leg it came from. Following the boundary is both the correct
    detour and the one a farmer walks.

    UNTIL NO LEG CROSSES, OR NONE (feature 287, ways W24, FR-005). Six rounds and then the result as it stood - a leg
    still across the field shipped. The rounds are now bounded by the ring's own vertex count (each splice walks ring
    edges, so a detour that needs more rounds than the ring has vertices is not converging), and a path that still crosses
    after them comes back as None: the caller takes another way out, never this one.

    Research:
        a track goes round the field - research/questions/0081-village-lanes.drawing.html: never across the crop, the
            shorter way round its outline"""
    ring = list(poly)
    n = len(ring)
    out = [push_out_of(poly, q, margin) for q in path]
    for _ in range(max(n, 1) if rounds is None else rounds):
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
            return out
    return None if any(segments_cross(a, b, ring[k], ring[(k + 1) % n]) for a, b in zip(out, out[1:], strict=False) for k in range(n)) else out


def clear_runs(
    pts: Poly,
    obstacles: Sequence[Poly],
    margin: float,
    step: float = 8.0,
    lines: Sequence[tuple[Pt, Pt]] = (),
    line_margin: float = 14.0,
    tight: Sequence[Poly] = (),
    tight_margin: float = WEB_FABRIC_GAP,
    floor: float = 70.0,
    index: FabricIndex | None = None,
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
    nowhere for it to be. So `tight` gets `tight_margin`, by default the lane page's 7 ft from a lane's middle to a garden
    fence (`WEB_FABRIC_GAP`; a hand's breadth, 6 ft, until feature 328).

    Returns every run that reaches `floor`, which defaults to the same 70 ft `clip_to_clear` uses.
    A short one is a real exception rather than a loosening: the footpath from an outlying steading's
    door to the nearest way is 60-odd feet by construction, and refusing it as a stub left eight
    houses unreachable while a path to each was being drawn and discarded. A back lane interrupted
    by a steading is two lanes, not one shortened one - and returning only the longest threw away
    ground that genuinely serves houses at the other end.

    A stub below the floor is not a lane, whichever way it was measured.

    Research:
        off the crop - DEVIATION research/questions/0081-village-lanes.drawing.html: the page lets a lane run on the bund and touch a plot's boundary; the run keeps the full `margin` off the crop - the departure the page is yet to record (405 T98)
        off the wet ground - GUESS: searched, the record silent (feature 417 T29 pass A1, 2026-10-25); the full margin; 0081 keeps a track off wet ground and gives no distance
        threads between steadings - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the lane's middle at least 7 ft (`WEB_FABRIC_GAP`) off the fabric by default
        lane off a water line - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.html, research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a path runs on the bank of every grade of field channel, and the bund is a path - the lane is held 14 ft off a water line, a departure the code keeps until feature 417 T32; 14 ft by default (`line_margin`)
        shortest lane - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A1, 2026-10-25); a run under 70 ft by default is not a lane
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N4, 2026-10-25) - 8 (sampling step along a run)
    """
    if not obstacles and not lines and not tight:
        return [list(pts)]

    # THE FABRIC INDEX (feature 138) replaces the per-call bounding-box prefilter and the per-sample
    # scan of every surviving polygon's every edge: built once here (or once per routing box by
    # `_route`, which used to call this function once PER LATTICE CELL - 165,611 times on one polder),
    # it files each polygon and line by grid cell so a sample measures only its cell's candidates.
    # Same verdicts by construction - the candidates are a superset of what the box prefilter kept,
    # measured with the same predicate; `clearance.py` carries the argument and the oracle test.
    # ...or handed in by a caller that asks many links of the SAME ground (feature 284, FR-002: `_route`'s string-pull, whose
    # every link asked the memo, and the memo's key walks every polygon's identity, length and ends and every water line)
    fouled = (index if index is not None else fabric_index(obstacles, margin, tight, tight_margin, lines, line_margin)).fouled

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
    caller must handle an empty result rather than assuming a lane.

    Research:
        an arm stops at the crop - research/questions/0081-village-lanes.drawing.html: a lane ends where the crop begins
        lane off a water line - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.html, research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a path runs on the bank of every grade of field channel, and the bund is a path - the lane is held 14 ft off a water line, a departure the code keeps until feature 417 T32; 14 ft by default
        shortest arm - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A1, 2026-10-25); under 70 ft is not drawn
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N4, 2026-10-25) - 8 (sampling step)
    """
    if not obstacles and not lines:
        return pts

    # THE FABRIC INDEX, AS `clear_runs` ASKS IT (feature 281, FR-001). This walked every obstacle's every edge and every
    # line per 8 ft sample - 535,389 `seg_dist` on Kashikawa's lane arms, field spur and threading - while its through-lane
    # sibling below had asked the index since feature 138. The closure it replaces was `fouled_brute` term for term (each
    # line under `line_margin`, then each obstacle inside or its nearest edge under `margin`), and `FabricIndex.fouled`
    # equals `fouled_brute` (feature 138's oracle test), so every clip is what it was.
    fouled = fabric_index(obstacles, margin, (), 0.0, lines, line_margin).fouled

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
