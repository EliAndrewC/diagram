"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index.

One web lane, laid (`_lay_web_lane`). The straggler footpath pass that also lived here was dropped by feature 287 (GM
2026-09-30): the access tree reserves every house's corridor at seating and the settle draws it for any house the web
leaves unreached (`tree.admits`, `settle.settle_the_web`, `last_resort`), so a second router pass had nothing left to
guarantee."""

from __future__ import annotations

import math
from collections.abc import Sequence

from l7r.diagram.settlement import Settlement, point_in_poly, seg_closest, seg_dist

from ..consts import (
    BUNDLE_PITCH,
    WEB_FABRIC_GAP,
    WEB_HARD_GAP,
    WEB_REACH_FT,
    WEB_SHADOW_FT,
    Poly,
    Pt,
)
from .clearance import _clear_link, clear_runs
from .fabric import _LANE_JOIN_FT, _draw_web, _net_segs
from .geom import _net_reach, _reach, _trim_to_service, polyline_len, steading_footprints


def _lay_web_lane(s: Settlement, run: Poly, hard: list[Poly], walls: list[Poly], water: list[tuple[Pt, Pt]], belts: Sequence[Poly] = (), houses: Sequence[Pt] = ()) -> bool:
    """Draw one web lane - but ONLY if it joins the way network, and TOUCHING it where it joins.

    A WEB THAT DOES NOT JOIN UP IS NOT A WEB, and this is the rule that makes the name honest. Three
    settlement-reviews found the same defect independently on three different maps: the lanes reached
    the houses and reached nothing else. Sawada drew six web lanes of which four touched no other
    way, so seven of its nineteen houses were "served" by an island whose nearest real lane was still
    136-296 ft off - exactly where they had been before the feature. Inashiro came out as three
    separate components with a 110 ft gap between them. The research this feature cites is explicit
    that the thing being reproduced is "the INTERCONNECTED system of narrow lanes and alleys", so a
    lane that connects to nothing is not an alley, it is a yard path.

    Two distinct jobs, and both were missing:

      - JOIN. A run whose nearest end is already within `_LANE_JOIN_FT` counts as arriving; one that
        is further off gets a link drawn to the network, and if the link cannot be drawn the run is
        not drawn either. Refusing to draw is the right answer - the alternative is ink that looks
        like a way and is not one.
      - TOUCH. Acceptance and INK are different tolerances, and conflating them is what left Inashiro
        with a lane stopping 12.7 ft short of the junction it aimed at, a visible break of about 19
        px on the sheet. So the joining end is extended onto the way it meets. The gate reach can
        stay where it is; it is then satisfied by construction rather than by rounding.

    Also refuses a run that merely SHADOWS an existing way - Inashiro laid a back lane a median 10 ft
    from a skeleton lane for its whole length, which reads as one lane accidentally drawn twice.
    `MIN_WEB_GAP` keeps the web's own cuts apart; nothing was keeping a cut off the lanes already
    there."""
    segs = _net_segs(s)
    if len(run) < 2:
        return False
    # TRIM FIRST, JOIN SECOND. The join is computed from the run's ENDS, so trimming afterwards moves
    # the end out from under the link that was drawn to it - which left a 187 ft lane whose start
    # stood 178 ft from any way, the exact dangling tread `lanes_reach_something` exists to catch.
    # to the bar the GATE asks of a lane end, not the looser service reach: this runs at DRAW time, before
    # the settle, so a steading a shortened run stops serving still gets its reserved corridor drawn afterwards (feature 227;
    # the straggler footpaths that used to do this were dropped, feature 287).
    # ...and a tread that stops at a steading's own dooryard has ARRIVED there, which is the fourth clause of
    # `end_serves` at its own tight distance (`steading_footprints`, feature 227 D11).
    run = _trim_to_service(run, segs, houses, steadings=steading_footprints(s.M))
    if segs:
        # SHARING A CORRIDOR IS SHADOWING, whether the two lines are parallel or crossing. The test
        # was written against `MIN_WEB_GAP` (the room a lane needs to pass BETWEEN two steadings),
        # which is far too tight to describe two ways a reader sees as one: Inashiro laid a back lane
        # that crossed the connector mid-run and stayed within 30 ft of it for 91% of its length, and
        # the 18 ft test did not fire once. A reader reads them as one lane drawn twice, so the
        # threshold is what a reader can separate, not what a lane can squeeze through.
        # SHADOWING IS A LENGTH, NOT ONLY A FRACTION. A fraction alone lets a long run hide: a lane
        # that parallels the connector for 128 continuous feet at a median 16 ft measured 50%
        # shadowed against a 60% bar and was drawn. Doubled ink is doubled ink whether it is half the
        # run or four fifths of it, so the longest UNBROKEN shadowed stretch is capped at one bundle
        # pitch as well. Both clauses are needed - the fraction catches a short lane laid alongside
        # another for all of its length, the absolute catches a long one that eventually diverges.
        near_flags = [min(seg_dist(q[0], q[1], a, b) for a, b in segs) < WEB_SHADOW_FT for q in run]
        _step_ft = polyline_len(run) / max(len(run) - 1, 1)
        _worst = _cur = 0
        for _f in near_flags:
            _cur = _cur + 1 if _f else 0
            _worst = max(_worst, _cur)
        # ONE REFUSAL, BOTH CLAUSES: the fraction catches a short lane laid alongside another for all of its
        # length, the unbroken stretch a long one that eventually diverges. Written as one test because they are
        # one rule - a lane that shadows another is a doubled band - and because a separate line for the second
        # is a line only a particular map shape ever reaches.
        if sum(near_flags) > 0.6 * len(run) or _worst * _step_ft > BUNDLE_PITCH:
            return False
        # ...AND A LANE DOES NOT RUN THE LENGTH OF A SHELTER BELT. Crossing one costs the belt a
        # lane's width of wall, which is a fair price for a way that has somewhere to be; running
        # ALONG it splits one wind wall into two thinner ones and opens a slot down the middle. A
        # review measured a back lane 237 of 237 ft inside the belt, having deleted 15 of its 169
        # clumps, on a map whose notes already record this belt being damaged the same way once.
        for belt in belts:
            inside = sum(1 for q in run if point_in_poly(q[0], q[1], list(belt)))
            if inside * (polyline_len(run) / max(len(run), 1)) > 60.0:
                return False
        # THE WHOLE RUN ARRIVES, NOT JUST ITS TWO ENDS. Measuring only the endpoints is how the snap
        # came to draw a hairpin: a run whose BODY already passes 2.75 ft from a lane, but whose end
        # wandered 23.8 ft beyond it, got a perpendicular drawn back to the foot - a needle-thin
        # triangular loop hanging off the junction, which a review found on all four hamlets (turn
        # deviations of 158, 178, 110 and 107 degrees, against a pre-web maximum of 7). If the run
        # has already arrived somewhere along its length there is nothing to snap; the only thing
        # worth doing is trimming the short tail that carried on past.
        vert = [min(seg_dist(v[0], v[1], a, b) for a, b in segs) for v in run]
        k = min(range(len(vert)), key=lambda i: vert[i])
        if 0 < k < len(run) - 1 and vert[k] <= _LANE_JOIN_FT:
            # THE SHORT HALF IS THE STUB, whichever half it is: a run that touches the network partway along is
            # one lane arriving with a tail, and which side carried on past is not always the same one. Written
            # as a choice rather than a pair of branches so neither side is a line only one map shape reaches.
            head, tail = polyline_len(run[: k + 1]), polyline_len(run[k:])
            run = run[: k + 1] if tail < 40.0 else (run[k:] if head < 40.0 else run)
            _draw_web(s, run, 3)
            return True
        d0, d1 = vert[0], vert[-1]
        end = 0 if d0 <= d1 else -1
        gap = min(d0, d1)
        p = run[end]
        q = min((seg_closest(p[0], p[1], a, b) for a, b in segs), key=lambda z: math.dist(p, z))
        if gap > _LANE_JOIN_FT:
            if math.dist(p, q) > WEB_REACH_FT * 2.0:
                return False
            link = [
                r for r in clear_runs([p, q], hard, WEB_HARD_GAP, step=4.0, lines=water, tight=walls, tight_margin=WEB_FABRIC_GAP, floor=12.0) if _reach(p, r) < 12.0 and _net_reach(r, segs) < 12.0
            ]
            if not link:
                return False
            # A HEALING LINK INHERITS THE WIDTH OF THE WAY IT JOINS. Laid at the web's own 3 ft
            # between two 5 ft lanes it renders as a neck with a round-cap knuckle at each step - a
            # review read it at 2x as a lollipop knob mid-street, and it is a repair scar rather than
            # a way. A link exists to make two lanes one; it should look like the lane it completes.
            _w = max(
                (
                    float(_l.get("w", 3))
                    for _l in s.M.get("lanes", [])
                    if _net_reach(link[0], list(zip([(float(x), float(y)) for x, y in _l["pts"]], [(float(x), float(y)) for x, y in _l["pts"]][1:], strict=False))) <= _LANE_JOIN_FT
                ),
                default=3.0,
            )
            _draw_web(s, link[0], int(_w))
        elif _clear_link(run[end], q, hard, walls, water):
            # SNAP ONLY IF THE GROUND BETWEEN IS CLEAR. Extending an end onto the way it meets is
            # what makes the junction read as a touch instead of a gap - but the few feet being
            # added are ground like any other, and adding them blind put lane ink across houses and
            # garden beds (`features_do_not_overlap`, `houses_clear_of_lanes` on every cohort seed
            # the moment snapping went in). If the gap is not walkable the lane simply ends where it
            # ended; a visible break is better than a lane through a wall.
            run = ([q, *run]) if end == 0 else ([*run, q])
    _draw_web(s, run, 3)
    return True
