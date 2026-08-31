"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from collections.abc import Sequence

from l7r.diagram.settlement import Settlement, point_in_poly, seg_closest, seg_dist
from l7r.diagram.sitegen.geom import unit

from ..clearance import fabric_index
from ..consts import (
    BUNDLE_PITCH,
    FOOTPATH_FABRIC_GAP,
    WEB_FABRIC_GAP,
    WEB_HARD_GAP,
    WEB_REACH_FT,
    WEB_SHADOW_FT,
    Poly,
    Pt,
)
from ..plan import SitePlan
from .clearance import _bends_badly, _clear_link, clear_runs
from .fabric import _LANE_JOIN_FT, _crosses_fabric, _draw_web, _hits_a_steading, _net_segs
from .geom import _TOUCH_GAP, _drop_collinear, _net_reach, _reach, _trim_to_service, polyline_len
from .route import _route, _unjog
from .sweeps import _FINE_CELL, _LINK_DIRECTNESS, _PATH_DIRECTNESS


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
    run = _trim_to_service(run, segs, houses)
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
        if sum(near_flags) > 0.6 * len(run):
            return False
        _step_ft = polyline_len(run) / max(len(run) - 1, 1)
        _worst = _cur = 0
        for _f in near_flags:
            _cur = _cur + 1 if _f else 0
            _worst = max(_worst, _cur)
        if _worst * _step_ft > BUNDLE_PITCH:
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
            head = polyline_len(run[: k + 1])
            tail = polyline_len(run[k:])
            if tail < 40.0:
                run = run[: k + 1]
            elif head < 40.0:
                run = run[k:]
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


def _serve_stragglers(s: Settlement, plan: SitePlan, hard: list[Poly], fabric: list[tuple[Poly, Pt | None, str]], water: list[tuple[Pt, Pt]]) -> None:
    """A FOOTPATH TO THE OUTLYING STEADING, for the few houses the web's regular cuts cannot reach.

    The web covers the cluster by construction, but its lanes are then clipped out of the crop, off
    the marsh and around the steadings - and a lane that loses its far end stops serving the houses
    that were out there. Rather than widen the whole web to survive its worst clip (which puts lanes
    everywhere to fix a problem in one place), each remaining house gets what a real farmstead on the
    edge of a hamlet has: a path of its own, running from the nearest way to its door.

    Drawn from the HOUSE outward, deliberately. Clipping truncates at the first blockage from the
    start, so starting at the door means the path keeps whatever length it can win from the house's
    side - and it is the house's end that has to be reached for the path to be worth anything."""
    # A HOUSE THAT EXHAUSTED EVERY TARGET WILL EXHAUST THE SAME ONES AGAIN (feature 126).
    #
    # This loop makes four passes, and each unserved house tries up to 60 targets. A house nothing
    # can reach therefore costs up to 240 routing calls, every one a failure, and it pays that bill
    # again on every pass. Measured on seed 25: three unreachable houses, `_route` called 817 times
    # for 278 s; the baseline's single unreachable house cost 388 calls and 103 s. The failures were
    # nearly the whole bill.
    #
    # This is the engine's SECOND documented performance shape - "the same scan run again over
    # ground that has not changed" (dev/performance.md) - and it takes the same cure as `SeatMemo`:
    # remember the refusal, and ASSERT the invariant rather than assume it. The memo keys on the
    # exact target list, so a house is skipped only when the candidate ways it would try are
    # identical to the ones it already failed against. Draw a lane anywhere near it and its targets
    # change, the key misses, and it is retried in full. That failure direction is the whole design:
    # a wrong memo costs the SPEEDUP, never a path.
    _exhausted: dict[int, tuple[tuple[float, float], ...]] = {}
    for _pass in range(4):
        lanes = [[(float(x), float(y)) for x, y in ln["pts"]] for ln in s.M.get("lanes", [])]
        segs = [(a, b) for ln in lanes for a, b in zip(ln, ln[1:], strict=False)]
        added = 0
        for h in list(s.M.get("houses", [])):
            c = (float(h["x"]), float(h["y"]))
            # THE LIVE NETWORK, NOT A SNAPSHOT. `segs` was read once per pass, so a house already
            # brought within reach by a path drawn two houses earlier IN THIS PASS still looked
            # stranded and got a second path of its own - Kashikawa's 29 ft lane 12, drawn for a
            # house that a previous lane had already taken from 100.7 ft to 38.9, and which the new
            # lane then left at 70.5. A way exists because feet use it.
            segs = _net_segs(s)
            # SERVE WITH MARGIN, NOT TO THE MILLIMETER. Triggering at exactly the reach means a
            # house at 99.7 ft is not a straggler and gets nothing, while one at 100.3 has a whole
            # path drawn for four inches of violation - the same bug at both ends. A review caught
            # the first half twice on the same steading ("satisfying the rule by 0.3 ft ... a re-roll
            # will flip it"), and it had indeed flipped back. Ten feet of headroom fixes both.
            if min(math.dist(c, seg_closest(c[0], c[1], a, b)) for a, b in segs) <= WEB_REACH_FT * 0.9:
                continue
            # Everything EXCEPT this steading's own house, yard, garden and shed - the path has to
            # be able to leave its own dooryard, and `of` says which features those are.
            # NOTHING BUILT STEPS ASIDE - not even this steading's own house. Exempting it was how
            # the path got out of its own dooryard, and it was also a license for the router to drive
            # straight THROUGH the farmhouse: seeds 41 and 43 came back with `houses_clear_of_lanes`
            # and `houses_off_corridors`, which is a lane drawn over a wall. The door is pushed clear
            # of the house instead (see `step` below), which solves the same problem without letting
            # a path cross anything.
            #
            # GROUND COVER IS NOT FABRIC, though. A footpath may cross grazing scrub and may run
            # along a tree belt - those are what the ground IS, not things built on it, and a review
            # confirmed "the only polygons they cross are the grazing commons, which is what a lane
            # crosses". Counting them walled an outlying steading in behind its own commons.
            # TWO OBSTACLE SETS, because a steading's own yard is ground you WALK but not ground a
            # lane is DRAWN on. `others` is everything solid and is what the drawn tread is clipped
            # against. `passable` additionally lets the route PLAN through this steading's own yard
            # and garden - on a hemmed-in farmstead the bundle wraps the house completely, so with
            # its own yard solid there is no doorstep and the router reports no route at all, when
            # what does not exist is the doorstep. Planning through it and drawing only what survives
            # the clip gives the answer the sources describe: the lane ends AT the yard, and the yard
            # is private ground the household crosses on foot.
            _mine = [id(poly) for poly, owner, kind in fabric if owner is not None and math.dist(owner, c) <= 1.0 and kind in ("threshing_yards", "gardens")]
            others = [poly for poly, _owner, kind in fabric if kind not in ("commons", "village_groves")]
            passable = [poly for poly in others if id(poly) not in _mine]
            # The door stands clear of the steading's own wall by the same margin every other lane
            # keeps, so it is a legal starting point with the house left in the obstacle set.
            step = math.hypot(float(h["w"]), float(h["h"])) / 2 + 8.0 + FOOTPATH_FABRIC_GAP
            # EVERY WAY WITHIN REACH IS A CANDIDATE, not merely the closest one. A path aimed at the
            # nearest lane can run the length of a neighbor's threshing yard and be refused for its
            # whole run, while a way ten feet further off is reachable across open ground - measured,
            # that was every one of the eight houses this pass was failing to serve. Real footpaths
            # go where there is room, so the candidates are tried nearest-first and the first one
            # that has room wins.
            targets = sorted((seg_closest(c[0], c[1], a, b) for a, b in segs), key=lambda q: math.dist(c, q))
            _served = False
            _folded: Poly | None = None  # a workable path that bends or fouls - the last resort, ranked
            _folded_rank = (True,)
            _key = tuple((round(float(t[0]), 1), round(float(t[1]), 1)) for t in targets[:60])
            if _exhausted.get(id(h)) == _key:
                continue  # same house, same candidate ways, same obstacles - a replay of a pass that already failed
            for tgt in targets[:60]:
                # A FOOTPATH CANNOT START IN THE WATER (feature 145, cohort seed 41 after the field moved): the
                # nearest point of the network was where a lane skirts the drain brook, so the path's junction
                # sat 1.3 px off the brook's centerline - a crossing gets a plank from `stage_crossings`, an
                # ENDPOINT on the water gets nothing, and `ways_cross_water_on_a_deck` fired on the first sample.
                # The router keeps 14 px off every watercourse (`_route`'s line margin); the junction owes the same.
                if water and min(seg_dist(tgt[0], tgt[1], a, b) for a, b in water) < 14.0:
                    continue
                # The radius is generous on purpose. A steading the web could not reach is by
                # definition one whose nearest way is already beyond the reach, so a search bounded
                # at twice the reach gave up on exactly the houses that needed it - two of seed 3's,
                # at 171 and 201 ft, were never attempted at all. A long path is a real thing on the
                # edge of a hamlet; a house with no path is not.
                # THE DIRECTNESS BOUND IS THE LIMIT, not a radius. Capping candidate targets at
                # 3.5x the reach meant a steading 399 ft from the network never had a single target
                # tried, though a clear route to one existed - the cap was a guess at "too far" and
                # the path's own shape is the honest test. Kept only as a backstop against searching
                # the whole map.
                if math.dist(c, tgt) > WEB_REACH_FT * 8.0:
                    break
                # THE DOOR IS WHERE THERE IS ROOM FOR ONE, not wherever the target happens to lie.
                # Placed blindly along the bearing to the way, it lands in the steading's own
                # threshing yard whenever the way is on the yard's side - and the route then fails at
                # its very first cell, which reads as "no route exists" when what does not exist is
                # that particular doorstep. Ring the house and take the clear standing-place nearest
                # the direction of travel.
                dx, dy = unit(tgt[0] - c[0], tgt[1] - c[1])
                # ...and OUTWARD until there is room, not only around at one radius. A hemmed-in
                # farmstead has its own threshing yard and garden wrapped right around it, so every
                # point on a ring at the house's own standoff lies inside its own bundle and there is
                # no legal doorstep at all - which the router reports as "no route", when what does
                # not exist is the doorstep. Exempting the steading's own open ground was tried and
                # rejected: it bought this house nothing and cost an overlap on another seed. Walking
                # out past the yard is what a person does, and it keeps every footprint solid.
                door = next(
                    (
                        q
                        for q in sorted(
                            ((c[0] + math.cos(math.tau * k / 16) * (step + out), c[1] + math.sin(math.tau * k / 16) * (step + out)) for out in (0.0, 12.0, 24.0, 40.0, 60.0, 85.0) for k in range(16)),
                            key=lambda q: (math.dist(q, c), -((q[0] - c[0]) * dx + (q[1] - c[1]) * dy)),
                        )
                        # A POINT, NOT A LINK (feature 145): `_clear_link(q, q, ...)` returns True for any span
                        # under 1 px, so the standing place was never tested at all - cohort seed 41's footpath
                        # began 1.3 px from the drain brook. The same index the router uses judges the point.
                        if not fabric_index(hard, WEB_HARD_GAP, passable, FOOTPATH_FABRIC_GAP, water, 14.0).fouled(q)
                    ),
                    (c[0] + dx * step, c[1] + dy * step),
                )
                # A FOOTPATH BENDS. The straight run is tried first and is usually right, but a path
                # that meets a neighbor's garden bed head-on should go round it rather than be
                # abandoned - which is what a person does, and abandoning it was the single biggest
                # residue left in the cohort once the overlaps were fixed. The dog-legs are one
                # waypoint pushed off the straight line, nearest offsets first, so a straight path
                # always wins when it exists and the bend is only as much as it has to be.
                mid = ((door[0] + tgt[0]) / 2, (door[1] + tgt[1]) / 2)
                px, py = -dy, dx
                cands = [[door, tgt]]
                # ...and a ROUTED candidate, which is what actually gets there when the straight run
                # and the bends do not. Tried after them so a straight path still wins when one
                # exists - the router will happily return a slightly wandering line where a ruler
                # would do.
                # A FOOTPATH MAY CROSS A DITCH; IT GETS A PLANK. The routed candidate is allowed
                # over a watercourse because `stage_crossings` runs after this and decks any way that
                # crosses one - the field spur and the connector already rely on that. Measured: an
                # outlying farmstead on seed 2 had NO route to the network at any clearance, and the
                # thing between it and the cluster turned out not to be a yard or the crop but a
                # ditch. A steading across a ditch is reached by a plank, not by being unreachable.
                # A FINER LATTICE FOR THE FOOTPATH WAS TRIED AND REVERTED - do not pull this lever
                # again. The arithmetic is genuinely suggestive: the router inflates its planning
                # clearance to gap + cell * 0.71 so that a free cell means every point in it is
                # clear, which at the default 10 ft cell is 11.1 ft for a footpath - it demands a
                # 22 ft corridor to plan through, while the gaps between neighboring steadings are
                # MIN_WEB_GAP, 16 ft. At a 5 ft cell the planning clearance is 7.6 ft and a 16 ft gap
                # fits. It reads like the explanation of every unreachable steading, and it is not.
                #
                # Measured end to end (2026-08-18), coarse-only against a coarse-then-fine fallback,
                # on cohort seed 5: 159.9s -> 672.3s, a 4.2x build, and the unserved count did not
                # move (2 either way). Seed 25 improved 4 -> 2 across the same afternoon and it is
                # tempting to credit this - it is not the cause: with the fallback DISABLED, seed 25
                # measures 2 as well. That gain came from a peer session's merge, and attributing it
                # here would have written a false why into the file.
                #
                # So the lattice is not what strands these houses, and 4x the generation time buys
                # nothing. What does strand them is recorded with the reach residue.
                routed = _route(door, tgt, hard, passable, [], gap=FOOTPATH_FABRIC_GAP)
                if routed:
                    cands.append(routed)
                # THE BEND IS A FRACTION OF THE RUN, not a fixed number of feet. Offsets of 40, 80
                # and 130 ft are a gentle correction on a 300 ft path and a switchback on an 80 ft
                # one - Inashiro drew 271 ft of path to join two points 77 ft apart, and once the
                # anti-fold rule was added to catch that, the same fixed offsets simply failed every
                # short path instead and left the house unreached. Scaling by the chord keeps every
                # candidate inside the 1.6 directness the rule allows, so the two rules stop fighting.
                chord = math.dist(door, tgt)
                cands += [[door, (mid[0] + sgn * px * k * chord, mid[1] + sgn * py * k * chord), tgt] for k in (0.2, 0.35, 0.5) for sgn in (1.0, -1.0)]
                hit: list[Poly] = []
                _fallback_hit: list[Poly] | None = None
                for cand in cands:
                    runs = clear_runs(cand, hard, WEB_HARD_GAP, step=4.0, lines=[] if cand is routed else water, tight=others, tight_margin=FOOTPATH_FABRIC_GAP, floor=20.0)
                    # A CLIPPED RUN IS A STAIRCASE OF SAMPLES, NOT A LANE (feature 134 T50, 2026-08-29).
                    # `clear_runs` walks the candidate every 4 ft and hands back the stretches that are
                    # clear, so what gets drawn is twenty-five collinear points where a footpath has two
                    # or three - and every pass downstream then reasons about the wrong object. `_unjog`
                    # and `lanes_bend_like_paths` both read the turn at each RECORDED vertex, and a
                    # staircase's turns are all about zero, so a run that visibly folds reads as straight
                    # until one long join leg is spliced onto the end of it and the fold appears all at
                    # once; `_smooth_web`'s string-pull cannot chord it because the samples hug the
                    # obstacles the clip was avoiding. Dropping a point that lies ON the segment between
                    # its neighbors is EXACT - the ink is identical to the last decimal - so this changes
                    # no geometry, only what the record says the shape is.
                    runs = [_drop_collinear(r) for r in runs]
                    # JOINING THE NETWORK, not arriving at the point that was aimed at. A candidate
                    # is clipped into runs, and the run that survives is often a middle fragment
                    # that serves the house perfectly well and touches a DIFFERENT lane than the one
                    # the path was aimed down. Measured on seed 8: 1,566 of 2,309 attempts found a
                    # run and every one of them was thrown away by testing against `tgt` alone.
                    # A PATH BENDS; IT DOES NOT SWITCHBACK, and it must actually arrive at both ends.
                    #
                    # Three things were wrong here and all three were found by review rather than by
                    # the gate, because the gate measures distance and these are shapes. (1) The
                    # dog-leg waypoints were tried in order and the first that CLEARED was taken,
                    # with nothing scoring the result - so Inashiro accepted a 130 ft offset intact
                    # and drew 271 ft of path to join two points 77 ft apart, folding back through
                    # the windbreak and costing the shelter belt six clumps. (2) The house end was
                    # only required within `WEB_REACH_FT`, i.e. 100 ft, so Mizuguchi drew a 38 ft
                    # mark 71 ft from the house it served, touching nothing, to cure a ONE-FOOT
                    # violation - a caret floating in a field. (3) Neither end had to touch, so
                    # Inashiro's read as a free chevron with 24 ft of grass at one end and 13 at the
                    # other.
                    #
                    # So: the path must reach the DOOR, not merely the house's neighborhood; it must
                    # reach the network; and its length may not exceed `_PATH_DIRECTNESS` times its own
                    # chord, which is the band every honest way on these maps already sits in (1.00-1.34).
                    hit = [r for r in runs if _reach(c, r) <= WEB_REACH_FT and _net_reach(r, segs) <= _LANE_JOIN_FT and polyline_len(r) <= _PATH_DIRECTNESS * max(math.dist(r[0], r[-1]), 1.0)]
                    # THE FIRST CANDIDATE THAT WORKS IS NOT THE BEST ONE THAT WORKS (feature 134 T50,
                    # 2026-08-29). The candidates are already in preference order - the straight run, then
                    # the ROUTED one, then the fabricated dog-legs - and taking the first that yields a
                    # run at all meant a dog-leg was drawn whenever the two ahead of it were clipped away,
                    # bend and all. A dog-leg is a bend BY CONSTRUCTION: cohort seed 21's footpath turned
                    # 90 degrees and then 60 within 34 ft, which `lanes_bend_like_paths` reads exactly as
                    # it should, and `_unjog`'s three rungs were all blocked by the steading the dog-leg
                    # was thrown around. So every candidate is asked, and the first whose run does not
                    # bend the way the check refuses is taken; the first that works at all remains the
                    # fallback, so no house that is served today goes unserved.
                    if hit and not _bends_badly(hit[0]):
                        break
                    # ONE EXPRESSION rather than a conditional body (feature 174): the first working
                    # candidate is kept as the fallback and later ones do not displace it. Written
                    # this way because the body was unreachable by construction - `_route` straightens
                    # what it finds, so a candidate that yields a run AND bends badly did not occur in
                    # eight constructed geometries, while the rule it encodes is still real.
                    _fallback_hit = _fallback_hit or (hit or None)
                    hit = []
                # THE TEST IS WHETHER THE PATH SERVES THE HOUSE, not whether it starts exactly at
                # the door. A run that begins a little way out - because the first few feet are
                # taken by a neighbor's yard - still puts a way within reach of this steading, which
                # is the whole requirement. Insisting on the door threw away runs that did the job.
                # BOTH ENDS HAVE TO EARN THEIR KEEP. Serving the house is the point, but a path
                # whose far end stops short of the way it was aimed at is a tread ending in bare
                # grass, which `lanes_reach_something` rightly refuses - and it was the single
                # biggest residue in the cohort (13 of 24 seeds) when only the house end was tested.
                hit = hit or _fallback_hit or []  # ...and the fallback stands in when nothing clean was found
                if hit:
                    # Both ends SNAPPED, for the same reason a web lane's joining end is: acceptance
                    # tolerances are not ink tolerances, and a path that stops 13 ft short of the
                    # lane it aims at is drawn as a gap whatever the gate thinks of it.
                    # A PATH STOPS AT ITS FIRST CONTACT WITH THE NETWORK - it does not then travel
                    # ALONG it. The router has no cost term for running down an existing tread, so
                    # once it entered a lane's corridor it was free to follow it: a review measured
                    # 32.6 ft of a door path drawn on top of a back lane at 0.0-1.2 ft separation,
                    # 27% of its length as duplicate ink, showing on the sheet as a seam and a width
                    # discontinuity. Truncating at first contact also takes that path's directness
                    # from 1.57 to 1.14. The snap below closes whatever gap is left.
                    path = list(hit[0])
                    # WALK ON TO THE CLOSEST APPROACH, THEN TOUCH (feature 134 T50, 2026-08-29) - the
                    # lesson `_pull_back_to_service` records for the connector, never applied to the
                    # footpath that has the same job. Cutting at the FIRST vertex inside the join bar
                    # stops the tread up to `_LANE_JOIN_FT` short of the way it is joining AND leaves the
                    # join step aiming backwards: gate seed 18's path stepped past its junction and the
                    # join then doubled back 77 ft, a 140 degree fold that `lanes_bend_like_paths` reads
                    # exactly as it should. The bar is what makes a junction FINDABLE; it is not where the
                    # ink should stop. So keep walking while the distance is still falling.
                    # WALK ON TO THE CLOSEST APPROACH, THEN TOUCH (feature 134 T50, 2026-08-29) - the
                    # lesson `_pull_back_to_service` records for the connector, never applied to the
                    # footpath doing the same job. Cutting at the FIRST vertex inside the join bar stops
                    # the tread up to `_LANE_JOIN_FT` short of the way it joins AND leaves the join step
                    # aiming backwards: gate seed 18's path stepped past its junction and the join then
                    # doubled back 77 ft, a 140 degree fold. The bar makes a junction FINDABLE; it is not
                    # where the ink should stop.
                    #
                    # THE LONGER WALK IS A PREFERENCE, NOT A LAW. It is still a real extension of the
                    # drawn tread, and on three seeds it bought a bend or an overlap it had not had - a
                    # tread across a garden (18), a notice board that lost its roadside way (44), a fresh
                    # fold (43). So both cuts are BUILT and the better one is drawn: the closest approach
                    # when what it yields is clean, the old first-inside-the-bar cut otherwise. Nothing
                    # that used to be drawn stops being drawn.
                    _dists = [min(seg_dist(_v[0], _v[1], _a, _b) for _a, _b in segs) for _v in path]
                    _first = next((_i for _i in range(1, len(path)) if _dists[_i] <= _LANE_JOIN_FT), None)
                    _cuts = [len(path) - 1]  # no vertex inside the bar: the run stands as routed, as it did before
                    if _first is not None:
                        _far = _first
                        while _far + 1 < len(path) and _dists[_far + 1] < _dists[_far]:
                            _far += 1
                        _cuts = [_far, _first] if _far != _first else [_first]
                    _whole = list(path)
                    _picked = None
                    _best_rank = (True, True)
                    for _cut in _cuts:
                        _p = _whole[: _cut + 1]
                        _j = min((seg_closest(_p[-1][0], _p[-1][1], a, b) for a, b in segs), key=lambda z: math.dist(_p[-1], z))
                        if _clear_link(_p[-1], _j, hard, others, water):
                            # A JUNCTION IS CONTACT, AND ITS LAST FEW FEET GET THE JUNCTION MARGIN. Tested
                            # at `_clear_link`'s 7 ft fabric margin the step reads as a run across open
                            # ground; it is not, it is the stretch into a junction, which everywhere else
                            # in this file may brush a fence at `_TOUCH_GAP` - a lane and a plot boundary
                            # share a line in a real village. With no fallback the path simply stopped and
                            # nothing afterwards could close it: gate seed 41's footpath ended 28.4 ft off
                            # the web with clear ground between, and `lanes_form_one_network` said so.
                            _p = [*_p, _j]
                        else:
                            # ...and failing even that, thread it at the fine lattice the coarse rungs
                            # cannot match - the same reach the orphan tail gets, for the same reason.
                            _tail = _route(_p[-1], _j, hard, others, water, gap=WEB_FABRIC_GAP, pad_mult=2.0, cell=_FINE_CELL)
                            if _tail and polyline_len(_tail) <= _LINK_DIRECTNESS * max(math.dist(_p[-1], _j), 1.0):
                                _p = [*_p, *_tail[1:]]
                        # AGAINST `passable`, NOT `others`: the path's OWN yard and garden are exempt
                        # from its obstacle list precisely so it can leave its dooryard, so a test that
                        # includes them is true of every candidate and discriminates between none - which
                        # is what the first version of this guard did.
                        # RANKED, NOT FIRST-PAST-THE-POST. Where neither cut is clean the fallback used to
                        # be whichever was built first, which is the LONG one - so a candidate that merely
                        # bent could lose to one that drew a tread through somebody else's vegetables.
                        # An overlap is a rule the matrix forbids outright; a bend is a complaint about
                        # shape. Cohort seed 18's footpath grazed a neighbor's garden at 1.21 ft while the
                        # shorter cut only bent. So they are ordered (fouls, bends) and the least bad wins.
                        _rank = (_crosses_fabric(_p, passable, _TOUCH_GAP), _bends_badly(_p))
                        if _rank == (False, False):
                            _picked = _p
                            break
                        if _picked is None or _rank < _best_rank:
                            _picked, _best_rank = _p, _rank
                    path = _picked if _picked is not None else path
                    # NO EXTRA STEP TOWARD THE DOOR. The path already begins at `door`, which is the
                    # house's own half-diagonal plus eight feet - i.e. just outside the wall. Pushing
                    # a further point in at 0.6 of that standoff put the start of the lane INSIDE the
                    # farmhouse, and `houses_clear_of_lanes` and the overlap matrix both said so. The
                    # steading's own footprint is exempt from this path's obstacle list so that it
                    # can leave the dooryard; that exemption is not a license to draw through the
                    # house.
                    # The path's own start can have been clipped away from the door, so it gets the
                    # same end-trim every web lane gets - a footpath that begins in bare grass is a
                    # dangling tread whatever drew it.
                    path = _trim_to_service(path, segs, [(float(q["x"]), float(q["y"])) for q in s.M.get("houses", [])])
                    # A DOOR PATH THAT REACHES NO WAY IS NOT DRAWN (feature 137 T03, 2026-08-28): cohort seed 22
                    # shipped a 4 ft straggler stub - the clip and the trim had eaten everything but the doorstep,
                    # and the orphan joiner could neither link it nor drop it (its house had no other way). A
                    # footpath is a run from a door TO a way; what survives must still end within a junction's
                    # reach of the way it was aimed at, or it is a mark in the grass.
                    if len(path) < 2 or min(math.dist(path[-1], tgt), math.dist(path[0], tgt)) > _LANE_JOIN_FT:
                        continue
                    # THE LATTICE'S JOGS COME OUT OF A FOOTPATH TOO (feature 145, cohort seed 43 after the field
                    # moved): a routed candidate is string-pulled inside `_route`, but the trim and the join above
                    # can leave a step the pull could not take at the fabric margin; the junction-margin pass that
                    # every web lane gets (`_unjog`) is what `lanes_bend_like_paths` measures against.
                    path = _unjog(path, hard, others, water)
                    # A FOLD IS A REASON TO TRY THE NEXT WAY, NOT A REASON TO DRAW (feature 134 T50,
                    # 2026-08-29). `_unjog` has three rungs and all of them can be blocked - cohort seed
                    # 16's footpath kept a 71-then-61 degree fold because the vertex between the turns
                    # stood 29 ft off the chord, with a steading on every way round it. Nothing later
                    # looks at the shape again, so the fold shipped and `lanes_bend_like_paths` found it.
                    # But this loop already has sixty candidate ways to aim at and takes the first that
                    # routes at all: a path to the SECOND-nearest way that runs straight is a better
                    # footpath than one to the nearest that doubles back, and it costs only the loop
                    # continuing. The folded run is kept as the last resort - a house reached by an ugly
                    # path is still better served than one reached by none, and `farmhouses_reach_a_way`
                    # is the harsher verdict of the two.
                    # ...AND A FOUL IS THE SAME KIND OF REASON AS A FOLD (feature 134 T50, 2026-08-29).
                    # A tread drawn through a NEIGHBOR'S garden is not a footpath either, and the overlap
                    # matrix says so outright - cohort seed 18's path grazed one at 1.21 ft. Ranked the
                    # same way as the two cuts are: an overlap is a rule broken, a fold is a shape
                    # complaint, so (fouls, bends) orders them and the least bad is what gets drawn if no
                    # way on the map yields a clean one.
                    # THE FOUL HALF OF THAT RANKING WAS DESCRIBED AND NEVER IMPLEMENTED (feature 155). The
                    # comment above says "(fouls, bends) orders them"; the code ranked `(_bends_badly(path),)`
                    # alone, so a tread that fouled a STEADING was only ever judged on its shape. Both maps
                    # that gated red on main were this: sawada's 8.6 ft stub 2 ft into a farmhouse at
                    # (1826, 2438) and kashikawa's 45 ft path 3 ft into one at (2136, 2762), each drawn by
                    # this pass on 2026-08-29 and each perfectly straight, so nothing here objected.
                    #
                    # AND A STEADING FOUL IS NEVER DRAWN, not even as the last resort the fold gets.
                    # `houses_clear_of_lanes` allows a lane no overlap with a house AT ALL, so a fouling path
                    # is not "the least bad option" - it is a guaranteed red gate and a map that shows a
                    # track through someone's floor. The honest fallback is the house going unserved, which
                    # `farmhouses_reach_a_way` reports in words a reader can act on. That is the same trade
                    # the orphan joiner makes when it keeps a disconnected piece rather than inventing a link.
                    _fouls = _hits_a_steading(s, path, 3)
                    _bad = (_fouls, _bends_badly(path))
                    if _fouls:
                        continue
                    if _bad != (False, False):
                        if _folded is None or _bad < _folded_rank:
                            _folded, _folded_rank = path, _bad
                        continue
                    _draw_web(s, path, 3, houses=[c])
                    added += 1
                    _served = True
                    break
            if not _served and _folded is not None:
                _draw_web(s, _folded, 3, houses=[c])
                added += 1
                _served = True
            if not _served:
                _exhausted[id(h)] = _key
        if not added:
            return
