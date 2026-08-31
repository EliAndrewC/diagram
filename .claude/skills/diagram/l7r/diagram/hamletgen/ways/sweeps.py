"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from collections.abc import Sequence

from l7r.diagram.settlement import Settlement, seg_closest, seg_dist

from ..consts import (
    WEB_FABRIC_GAP,
    WEB_REACH_FT,
    Poly,
    Pt,
)
from .clearance import _bends_badly, _clear_touch, drop_end_nubs, existing_walk, may_write
from .fabric import _LANE_JOIN_FT, _WEB_MIN_FT, _draw_web, _hits_a_steading
from .geom import _TOUCH_GAP, _aim_off, _components, _net_reach, _reach, polyline_len, shadowing_lane
from .route import _route

# HOW FAR A FOOTPATH MAY WANDER, as a multiple of its own straight-line chord. A review measured
# every honest way on these maps at 1.00-1.34 and one accepted switchback at 3.54 - 271 ft of path
# to join two points 77 ft apart, folded back through the windbreak. 2.0 admits a path that goes
# properly round one steading, which is what the router draws, and still refuses a fold.
_PATH_DIRECTNESS = 2.0

# A LINK that joins two halves of one settlement may wander further than a door path. Going round a
# paddy is legitimately indirect, and the thing being bought is the difference between a dozen houses
# reachable and a dozen houses not.
_LINK_DIRECTNESS = 4.0

_TREAD_TOUCH_FT = 6.0
"""The gap below which two treads are already ONE piece of ink and there is nothing to bridge.

A lane's drawn tread is a few feet wide, so anything under about this reads as a join on the sheet.
It is deliberately NOT `_LANE_JOIN_FT`: that is the gate's REACH tolerance ("is this house served"),
and using a reach figure as an ink-continuity figure is what let 21-29 ft holes ship as connected."""

_BREAK_SPAN_FT = 150.0
_BREAK_BEARING_DEG = 15.0


_BRIDGE_DETOUR = 2.0
"""How much longer the existing walk must be before a bridge is worth drawing.

A BRIDGE CLOSES A HOLE; IT DOES NOT CLOSE A LOOP (settlement-review, feature 155, Mizuguchi). The pass
below finds two lane ends facing each other across walkable ground and draws the missing piece - and
with the short-gap floor restored it will do that even when the two ends are ALREADY connected a
little way round, which is not a hole in a street, it is a second route. Mizuguchi shipped one: an
89.9 ft span whose two ends already had a 126.9 ft walk between them, closing lanes 1/4/7 into a
triangle enclosing 1,710 sq ft of nothing - and the fixture placer, running afterwards, deleted that
homestead's woodpile and hen coop and left its bath marooned on the far side of a public lane.

The discriminator is the DETOUR RATIO, not the length of either. A genuine break has no alternative at
all (the walk is `None`) or one that goes right around the block, many times the gap; a redundant loop
closure saves a fraction. Mizuguchi's was 1.41. The reviewer priced the threshold at "anywhere in
1.5-2.5" and 2.0 sits in the middle of it; measured over the live pool, it removes that one lane and
no other."""


def _bridge_collinear_breaks(s: Settlement, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> int:
    """Close a gap where ONE way has been drawn as two, and the ground between them is walkable.

    A lane that stops and resumes 110 ft further on, 8 degrees off collinear, is not two arms - it is
    one street with a hole in the middle of the built-up frontage, and both its ends read as rounded
    caps dying in bare grass. `lanes_reach_something` passes them because it tests each END
    independently: an end 83 ft from a house CENTER is "fronting" it even when that is 55 ft from the
    wall, i.e. out past the dooryard.

    THE TEST IS WHETHER THE GAP IS WALKABLE, which is what makes this a defect rather than an
    observation. Two near-collinear ends with a wellhead or a garden bed between them are honestly
    interrupted - the way goes round, or stops, because something is there. Two with nothing between
    them are one way that was drawn in two pieces, and the fix is to draw the piece that is missing.

    Found by a peer session's review of Sawada, where the ends sit either side of the cluster's own
    middle; the same shape survives on other maps and is a plain gap in the network."""
    made = 0
    # TWELVE PASSES, not four. Each closure adds a lane whose own ends sit beside existing ones, so a
    # map with several breaks needs several rounds - and Sawada ran out at four with three breaks
    # still open, which reads as the fix not working rather than as the loop giving up. The bound
    # exists only so a pathological map cannot spin; a hamlet uses two or three.
    for _ in range(12):
        ways = [[(float(x), float(y)) for x, y in ln["pts"]] for ln in s.M.get("lanes", [])]
        cands: list[tuple[float, Pt, Pt, float, float]] = []
        for i, li in enumerate(s.M.get("lanes", [])):
            if li.get("connector") or len(ways[i]) < 2:
                continue
            for j, lj in enumerate(s.M.get("lanes", [])):
                if j <= i or lj.get("connector") or len(ways[j]) < 2:
                    continue
                for ta, pra in ((ways[i][0], ways[i][1]), (ways[i][-1], ways[i][-2])):
                    for tb, prb in ((ways[j][0], ways[j][1]), (ways[j][-1], ways[j][-2])):
                        gap = math.dist(ta, tb)
                        # SHORT GAPS ARE THE ONES THAT MATTER, and they used to be excluded outright.
                        #
                        # The lower bound was `_LANE_JOIN_FT` (30), on the reasoning that anything
                        # closer than the gate's join tolerance is already "connected". It is not
                        # connected in INK: at 1 px = 1 ft a 29 ft hole is 29 px of bare grass
                        # between two ~4 px treads, which reads as two dropped sticks, and the gate
                        # is silent precisely BECAUSE its own tolerance erases it. Feature 126 made
                        # this visible - deriving the lanes from the houses produces more short
                        # breaks - and three settlement-reviews found it independently on three
                        # maps: Inashiro went from one ink component at HEAD to four, with six
                        # houses 105-243 ft from the connected network behind holes of 28.4, 28.7
                        # and 29.4 ft.
                        #
                        # The floor is now the tread's own width: below that there is nothing to
                        # bridge, because the two treads already touch.
                        #
                        # THE PROSE ABOVE OUTLIVED THE CODE FOR SIX DAYS, AND THAT IS THE LESSON
                        # WORTH KEEPING (settlement-review, feature 155, kashikawa). `c0c724b2`
                        # (2026-08-23) wrote both this floor and the exemption below; `569136fc`
                        # the same day reverted FIVE lane changes that had cost the cohort 44 -> 31
                        # and took these two lines with them as collateral - they are not among the
                        # five its message names. The comments survived. So anyone reading this
                        # function was told the short-gap case was handled while the code silently
                        # excluded it, and kashikawa shipped a 24.95 ft hole at (2000.9, 2914.7)
                        # for six days with a reviewer's fix landing beside it that could not
                        # reach it. Restored NARROWLY here - this floor and this exemption only,
                        # never the other four - because a comment and its code must not disagree,
                        # and because 24.95 ft of bare grass between two rounded caps in the middle
                        # of the built-up frontage is the exact defect the pass exists to close.
                        if not (_TREAD_TOUCH_FT < gap <= _BREAK_SPAN_FT):
                            continue
                        # ...and a SHORT gap does not have to be collinear. The bearing test exists
                        # to tell "one way with a hole in it" from "two arms that happen to end near
                        # each other", and over 150 ft that distinction is real. Over 25 ft it is
                        # not: a back lane following a curved field margin breaks at 37 deg of
                        # aim-off and is still one lane. So the test applies from `_LANE_JOIN_FT` up,
                        # and a shorter hole is closed on proximity alone.
                        if gap > _LANE_JOIN_FT and (_aim_off(pra, ta, tb) > _BREAK_BEARING_DEG or _aim_off(prb, tb, ta) > _BREAK_BEARING_DEG):
                            continue  # two arms, not one way
                        # POINTING AT EACH OTHER MEANS EACH END'S OUTWARD DIRECTION AIMS AT THE
                        # OTHER END - not that the two outward bearings are similar. Two ends facing
                        # across a gap have OPPOSITE outward bearings (one runs east, the other runs
                        # west into the same hole), so comparing them for similarity tests the wrong
                        # thing entirely: it selects pairs pointing the SAME way, which is two
                        # parallel arms, and misses the collinear break it was written for. Caught by
                        # a unit test built from the textbook case rather than from a map.

                        # ...unless a third way already spans it. Closing a break leaves the two
                        # original ends where they were, joined THROUGH the new lane - so without
                        # this the pass re-bridges the same pair every round and burns its budget on
                        # work already done.
                        if any(
                            k not in (i, j)
                            and len(o) >= 2
                            and min(seg_dist(ta[0], ta[1], a2, b2) for a2, b2 in zip(o, o[1:], strict=False)) <= _LANE_JOIN_FT
                            and min(seg_dist(tb[0], tb[1], a2, b2) for a2, b2 in zip(o, o[1:], strict=False)) <= _LANE_JOIN_FT
                            for k, o in enumerate(ways)
                        ):
                            continue
                        cands.append((gap, ta, tb, float(li.get("w", 5)), float(lj.get("w", 5))))
        if not cands:
            return made
        # AN UNROUTABLE BREAK SKIPS TO THE NEXT ONE; IT DOES NOT END THE PASS (feature 155). This
        # used to pick the single smallest gap and `return` the moment it could not be routed - so one
        # honestly-interrupted break silenced every other break on the map. That was harmless only
        # while the floor was `_LANE_JOIN_FT`: restoring the tread-width floor admits short candidates,
        # which sort first, and Kashikawa's unroutable 24.95 ft hole then blocked the whole pass. "The
        # interruption is honest" is a statement about ONE pair, never about the rest of the web.
        drew = False
        for gap, ta, tb, wa, wb in sorted(cands, key=lambda c: c[0]):
            # PLAN AT THE CLEARANCE IT WILL BE DRAWN AT. A bridge inherits the width of the street it
            # completes - 5 or 6 ft - so planning it at the FOOTPATH clearance leaves about a foot
            # between a 3 ft half-tread and a wall, and `houses_clear_of_lanes` says so. A footpath is
            # the one way on the map walked in single file; a street closing its own gap is not.
            #
            # A SHORT GAP ALSO NEEDS A FINE LATTICE. `_route`'s 10 ft cell is right for the 110-150 ft
            # breaks this pass was written for; across a 25 ft gap it has two and a half cells and
            # cannot represent a route at all.
            cell = min(10.0, max(_FINE_CELL, gap / 6.0))
            span = _route(ta, tb, hard, walls, water, gap=WEB_FABRIC_GAP, cell=cell)
            if not span:
                # ...and where the fabric clearance finds nothing, a bridge retries at the JOIN
                # clearance, because a bridge IS a join link and the joiner has routed at `_TOUCH_GAP`
                # since feature 126 on the recorded reasoning that "a lane and a plot fence share a
                # line in a real village". What makes that safe is what makes it safe for a link:
                # `_draw_web(joins=True)` refuses outright to put a tread on a farmhouse. A garden bed
                # may share a line with a lane; a steading may not.
                span = _route(ta, tb, hard, walls, water, gap=_TOUCH_GAP, pad_mult=2.0, cell=cell)
            if not span or polyline_len(span) > _PATH_DIRECTNESS * max(gap, 1.0):
                continue  # something is genuinely in the way HERE; the interruption is honest
            # A BRIDGE CLOSES A HOLE, NOT A LOOP - see `_BRIDGE_DETOUR`. If the walk already exists
            # and is not much longer than the span, this is a second route rather than a missing
            # piece, and drawing it encloses ground that nothing fronts.
            _alt = existing_walk(ways, ta, tb, _TREAD_TOUCH_FT)
            if _alt is not None and _alt <= _BRIDGE_DETOUR * max(gap, 1.0):
                continue
            # A BRIDGE IS A JOIN LINK, AND THE DEBRIS FLOOR WOULD SILENTLY REFUSE IT. The
            # `
            # floor", true only while the candidate floor was 30 ft. `joins` carries the right
            # reasoning already: the floor asks what a run EARNS in service, and a bridge earns
            # nothing by that measure because the houses are served by the pieces it joins.
            if not _draw_web(s, span, int(max(wa, wb)), joins=True):
                continue
            drew = True
            break
        if not drew:
            return made
        made += 1
    return made  # pragma: no cover - twelve bridges is far more than any hamlet needs


def _join_orphan_ways(s: Settlement, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> int:
    """Link any way that is not part of the settlement's one network - INCLUDING the skeleton's own.

    Found by the transitive `farmhouses_reach_a_way`, and it turned out not to be the web's fault at
    all: on a cohort hamlet the skeleton's two arms were clipped apart from the arm the connector
    leaves by, so they formed an island of their own, and every house they served counted as
    unreached. That is a pre-existing defect - it predates this feature and nothing could see it
    while the check measured distance to any polyline - and it is fixed here rather than ledgered,
    per Principle XIV.

    The link is a routed path, so it threads the steadings like any other; if no route exists the
    component stays orphaned and the gate says so, which is the honest outcome."""
    made = 0
    for _ in range(6):
        ways = [[(float(x), float(y)) for x, y in ln["pts"]] for ln in s.M.get("lanes", [])]
        if len(ways) < 2:
            return made
        seed = next((i for i, ln in enumerate(s.M["lanes"]) if ln.get("connector")), 0)
        main = {seed}
        grew = True
        while grew:
            grew = False
            for i, w in enumerate(ways):
                if i in main or len(w) < 2:
                    continue
                if any(_net_reach(w, list(zip(ways[j], ways[j][1:], strict=False))) <= _LANE_JOIN_FT for j in main if len(ways[j]) >= 2):
                    main.add(i)
                    grew = True
        orphans = [i for i in range(len(ways)) if i not in main and len(ways[i]) >= 2]
        if not orphans:
            return made
        main_segs = [seg for j in main for seg in zip(ways[j], ways[j][1:], strict=False)]
        # EVERY CANDIDATE, NEAREST FIRST - not just the nearest one. Giving up on the first orphan
        # that cannot be routed abandoned the whole pass, and with it every OTHER orphan that could
        # have been linked. Measured: seed 39 came out with 12 lanes of which only 5 were in the
        # connector's component, and all 12 of its houses counted as unreached - while being within
        # 86 ft of a lane, just not one on the network. Seed 9 the same, 11 of 11. That is the entire
        # reach residue on those maps: not a house without a way, a way without the network.
        cands = sorted(
            ((math.dist(v, q), v, q) for i in orphans for v in ways[i] for q in [min((seg_closest(v[0], v[1], a, b) for a, b in main_segs), key=lambda z: math.dist(v, z))]),
            key=lambda c: c[0],
        )
        link, best = None, None
        for cand in cands[:40]:
            # A LINK MAY GO THE LONG WAY ROUND, AND MAY BE PLANKED. Joining the network is worth a
            # detour that a footpath to a door would not be: these two halves of one hamlet are
            # otherwise separated by its own field, and the alternative to an indirect link is a
            # dozen houses that count as unreachable. Water is crossable for the same reason it is
            # for a footpath - `stage_crossings` decks it afterwards.
            # PLAN AT THE CLEARANCE IT WILL BE DRAWN AT - the third and last place this was wrong.
            # A link inherits the width of the way it joins, so planning it at the FOOTPATH clearance
            # leaves about a foot between a 3 ft half-tread and a wall, and a farmhouse ends up
            # standing on the lane (cohort seed 11). Only the true single-file footpath gets the
            # footpath clearance; a street, a bridge and a link are all drawn wider than one.
            _try = _route(cand[1], cand[2], hard, walls, [], gap=WEB_FABRIC_GAP, pad_mult=2.0, cell=14.0)
            # A TIGHT-SQUEEZE FALLBACK WAS TRIED HERE AND REVERTED (feature 126). When an orphan
            # could not be linked at the open clearance, a second attempt planned at 45% of
            # `WEB_FABRIC_GAP`, on the reasoning that the sources describe this very lane as
            # "colonized as semi-private space by the adjoining house". It was wrong twice over:
            # measured, it changed no connectivity number at all (the orphans it was aimed at are
            # separated by the PADDY, not by a wall, so no clearance helps), and it put treads on
            # houses - `make map` came back with features_do_not_overlap and houses_clear_of_lanes
            # on the reference hamlet. Do not re-add it: an orphan across a field is honestly
            # unlinkable, and the fix for those houses is the straggler pass, not a narrower lane.
            if _try and polyline_len(_try) <= _LINK_DIRECTNESS * max(cand[0], 1.0):
                link, best = _try, cand
                break
        if link is None or best is None:
            return made
        # NOT trimmed to service (T31, GM 2026-08-27): `_trim_to_service` pulled the link's ends back to
        # "within 40 ft of a way" - so the very link laid to JOIN an orphan stopped 29 px short of the
        # network it was joining, and the web shipped as pieces. A link runs from the orphan's vertex to
        # the network's foot point; both ends serve by construction.
        _w = max(
            (
                float(_l.get("w", 3))
                for _l in s.M.get("lanes", [])
                if len(_l.get("pts") or []) >= 2
                and _net_reach(link, list(zip([(float(x), float(y)) for x, y in _l["pts"]], [(float(x), float(y)) for x, y in _l["pts"]][1:], strict=False))) <= _LANE_JOIN_FT
            ),
            default=3.0,
        )
        _draw_web(s, link, int(_w))
        made += 1
    return made  # pragma: no cover - six links is far more than any hamlet needs


def _sweep_doubled_remnants(s: Settlement) -> int:
    """Drop a lane that leaves one way and returns to it, serving nobody it does not already serve.

    `_WEB_MIN_FT` asks whether a fragment is SHORT and `_sweep_debris` asks whether it is ALONE; neither asks
    whether it simply goes nowhere. A trim that shortens one arm of a fork leaves the other running back to
    its own parent, and at fit zoom that is a smudged band with a hairline down it, or an arm dying in grass
    a few feet from the lane it left - kashikawa shipped a 44 ft one every point of which sat within 6.6 ft
    of lane 8, sawada a 37.6 ft one that left lane 11 and died 11.4 ft from it (settlement-review, 152).

    TWO CLAUSES, AND THE SECOND IS WHAT MAKES THE FIRST SAFE. `shadowing_lane` asks whether both ends land
    on one other way; this then asks whether dropping the lane would strand a farmhouse, using the same
    reach figure the gate uses. A ring road that genuinely fronts its own houses answers yes to the first
    and no to the second and is kept. Measured on the two maps that motivated it, the pair selects exactly
    the two remnants and no other lane of the twenty-six.

    The drop is written back into `ways` as well as into the manifest. Without that, `ways` is a snapshot
    taken before the loop: a lane emptied at `i` stays a live shadowing candidate for every later `j`, so
    one drop cascades into dropping a second, legitimate lane whose only shadow was the corpse - and the
    stranding test above would clear it, because it would still see the dropped lane serving the house.
    """
    lanes = s.M.get("lanes") or []
    ways = [[(float(x), float(y)) for x, y in (ln.get("pts") or [])] for ln in lanes]
    centers = [(float(h["x"]), float(h["y"])) for h in s.M.get("houses") or []]
    dropped = 0
    gone: list[int] = []
    for i, ln in enumerate(lanes):
        if len(ways[i]) < 2 or ln.get("connector"):
            continue
        others = [w if k != i else [] for k, w in enumerate(ways)]
        if shadowing_lane(ways[i], others, _LANE_JOIN_FT) is None:
            continue
        # THE STRANDING TEST READS THE CHECK'S OWN FIGURE, NOT THE JOIN TOLERANCE (feature 155).
        # Written first against `_LANE_JOIN_FT` (30), which is the "is this end ON that way" figure and
        # is the wrong question entirely: `farmhouses_reach_a_way` fails a house more than
        # `WEB_REACH_FT` (100 ft) from any drawn way. A house 80 ft from the remnant and 110 ft from
        # everything else was therefore not even in `served`, so the remnant went and Inashiro - the
        # REFERENCE hamlet - shipped a stranded farmhouse at (1185, 1008). Same-source doctrine: a
        # guard against a check measures what the check measures.
        served = [c for c in centers if _reach(c, ways[i]) <= WEB_REACH_FT]
        if any(all(_reach(c, o) > WEB_REACH_FT for o in others if len(o) >= 2) for c in served):
            continue  # a farmhouse would be stranded; a visible remnant beats an unreached house
        ways[i] = []
        ln["pts"] = []
        s.reink_lane(i)
        gone.append(i)
        dropped += 1
    # AND THE HUSK GOES WITH THE INK - feature 145's rule, and this pass broke it (settlement-review
    # x2, feature 155: sawada shipped 13 lane records for 11 drawn lanes, kashikawa 14 for 13). An
    # emptied `pts` leaves a record declaring a lane nothing draws, which every consumer then has to
    # special-case - and a reviewer's first dump of the manifest crashed on `pts[-1]`. Leaving it to
    # `_sweep_debris` does NOT work and the comment at the call site used to say it did: that pass
    # opens with `live = [i for i in ... if len(ways[i]) >= 2]`, so a lane another sweep has already
    # emptied is not live, never enters `swept`, and is never deleted. It only removes husks it made
    # itself. Removed back-to-front so the earlier indices stay valid.
    for i in sorted(gone, reverse=True):
        del lanes[i]
    return dropped


def _sweep_steading_fouls(s: Settlement) -> int:
    """Pull back any lane end whose ink lands on a farmhouse, and empty what is left if nothing survives.

    RUNS LAST, BESIDE `_sweep_debris` AND `_drop_end_nubs`, FOR THE SAME REASON THEY DO: every earlier pass
    can leave one. The straggler pass routes clear of the steadings and the joiner brushes a fence at
    `_TOUCH_GAP` on purpose, but the passes AFTER them - the touch, the smoothing's cuts, the nub drop -
    each rewrite a lane's ends without re-asking whether the result still clears a house. Measured
    2026-08-29 on main: sawada shipped an 8.6 ft two-point stub 2 ft inside the farmhouse at (1826, 2438)
    and kashikawa a 45 ft run 3 ft inside one at (2136, 2762). Both lanes record `role=straggler` - the pass
    that FIRST drew them - which is what made the cause hard to see: the pass named on the lane had drawn a
    clean path, and a later one cut it onto the wall.
    `houses_clear_of_lanes` allows a lane no overlap with a steading at all, so this trims rather than
    ranks: the offending end segments come off, and a lane whittled below two points is emptied for
    `_sweep_debris`'s rule to finish. A house left unserved is `farmhouses_reach_a_way`'s honest verdict; a
    tread drawn across someone's floor is a map that looks finished and is wrong.
    """
    lanes = s.M.get("lanes") or []
    fixed = 0
    emptied: list[int] = []
    for i, ln in enumerate(lanes):
        pts = [(float(x), float(y)) for x, y in (ln.get("pts") or [])]
        if len(pts) < 2 or ln.get("connector"):
            continue  # a connector's route is the track's own business and it never ends in the cluster
        width = int(float(ln.get("w", 3)))
        before = len(pts)
        while len(pts) >= 2 and _hits_a_steading(s, pts[-2:], width):
            pts.pop()
        while len(pts) >= 2 and _hits_a_steading(s, pts[:2], width):
            pts.pop(0)
        if len(pts) == before and not _hits_a_steading(s, pts, width):
            continue
        if len(pts) < 2 or _hits_a_steading(s, pts, width):
            pts = []  # the foul is in the middle of the run, or nothing is left of it
        ln["pts"] = [[round(x, 1), round(y, 1)] for x, y in pts]
        s.reink_lane(i)
        if not pts:
            emptied.append(i)
        fixed += 1
    # ...and its husk goes with it, for the reason spelled out in `_sweep_doubled_remnants`: this used
    # to say "hand it to the debris sweep", and that sweep's `live` filter cannot see a lane already
    # emptied, so the record simply shipped.
    for i in sorted(emptied, reverse=True):
        del lanes[i]
    return fixed


def _drop_end_nubs(s: Settlement, hard: Sequence[Poly] = ()) -> int:
    """`drop_end_nubs` over the settlement's lanes, re-inking each one it changes. Runs LAST, beside
    `_sweep_debris`, for the same reason: every earlier pass can leave one."""
    lanes = s.M.get("lanes") or []
    ways = [[(float(x), float(y)) for x, y in ln.get("pts") or []] for ln in lanes]
    before = [list(w) for w in ways]
    for i in drop_end_nubs(ways):
        # JUDGE THE RESULT, NOT THE MOVE (feature 152, acceptance review) - through `may_write`, which is
        # the one body that answers this question for the whole file, rather than a second hand-rolled
        # clearance test beside it (its lift to module level landed on main while this was in flight).
        # It judges BEND as well as clearance, which the hand-rolled version did not. Dropping the vertex after an
        # end STRAIGHTENS the lane, and a straightened door path can lie closer to a neighbouring
        # farmhouse than the doglegged one did: on Kashikawa this pass took a house corner from 3.18 ft
        # clear of lane 11's tread to 0.69 ft INSIDE it, turning `features_do_not_overlap` from green to
        # red. That is the same rule `_may_write` already applies one pass over - a rewrite may leave a
        # lane no nearer the fabric than it already was. The nub is only worth removing if what replaces
        # it is clear.
        if hard and not may_write(before[i], ways[i], float(lanes[i].get("w") or 5.0), hard):
            ways[i] = before[i]
            continue
        lanes[i]["pts"] = [[round(x, 1), round(y, 1)] for x, y in ways[i]]
        s.reink_lane(i)
    return len(ways)


_ROUTE_MIN_W = 5.0  # a cart way; anything under this is a footpath and may legitimately neck
_ROUTE_JOIN_FT = 30.0  # the same reach the toucher uses - this closes what it declined, not more


def _keep_the_route_wide(s: Settlement, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> int:
    """Join two CART-WIDTH lane ends that stand within reach of each other but meet only through a
    narrower way.

    THE THROUGH-ROUTE NECKED FROM 6 FT TO 3 AND BACK (feature 152 T15, settlement-review 2026-08-29).
    On Mizuguchi the way out of the hamlet runs lane1 -> lane4 -> node -> lane3 -> the connector, all
    5-6 ft; but lane4 ends at (933.0, 1778.0) and lane3 begins at (944.1, 1779.6), 11 ft apart, and the
    only ink joining them is a stretch of lane2's THREE foot back-lane tread, capped at both ends by the
    wide lanes' round caps. Measured across the waist: 9.5 ft of tread, then 3.2, then 7.6.

    The toucher does not see it, and is right not to: both ends already touch lane2 at 0.0 ft, so the web
    is whole and every reach test passes. What is wrong is not connectivity but WIDTH - the route a cart
    takes pinches to a footpath for eleven feet. Feature 124's rule ("a healing link inherits the width of
    the way it joins") does not reach it either, because there the thin lane joins the wide one and here
    the wide ones join the thin.

    So the two wide ends are joined to each other directly, at their own width. Only where both are cart
    width, only within the toucher's own reach, and only when the direct link is clear - this closes what
    the toucher declined rather than laying new ways of its own."""
    lanes = s.M.get("lanes") or []
    closed = 0
    for i, ln in enumerate(lanes):
        pts = [(float(x), float(y)) for x, y in (ln.get("pts") or [])]
        if len(pts) < 2 or float(ln.get("w") or 0.0) < _ROUTE_MIN_W:
            continue
        for end in (0, -1):
            q = pts[end]
            for j, lo in enumerate(lanes):
                if j == i or float(lo.get("w") or 0.0) < _ROUTE_MIN_W:
                    continue
                other = [(float(x), float(y)) for x, y in (lo.get("pts") or [])]
                if len(other) < 2:
                    continue
                for oe in (0, -1):
                    b = other[oe]
                    d = math.dist(q, b)
                    if not (_TOUCH_GAP < d <= _ROUTE_JOIN_FT) or not _clear_touch(q, b, hard, walls, water):
                        continue
                    new = [b, *pts] if end == 0 else [*pts, b]
                    if _bends_badly(new):
                        continue
                    lanes[i]["pts"] = [[round(x, 1), round(y, 1)] for x, y in new]
                    s.reink_lane(i)
                    pts = new
                    closed += 1
                    break
                else:
                    continue
                break
    return closed


def _sweep_debris(s: Settlement) -> int:
    """Drop a lane the passes have whittled below `_WEB_MIN_FT` and left standing on its own.

    THE DEBRIS RULE WAS APPLIED ONCE, AT DRAW TIME, AND EVERY LATER PASS CAN SHORTEN A LANE (feature
    134 T50, 2026-08-28). `draw_web_lane` refuses to draw anything under `_WEB_MIN_FT` - 20 ft of
    tread fronts nobody and reads as a speck of clipping debris - but after it, a trim pulls an end
    back, a hairpin cut takes an arm, `_stop_at_network` cuts a link at the first way it meets. None
    of them re-asks whether what is left is still a lane, so a fragment can be whittled to under the
    minimum and kept. Measured on tripwire seed 27: a 20.5 ft two-point stub at (237, 1571) standing
    31 ft off the nearest lane, in a slot between a garden edge and a farmhouse wall with about 2.7 ft
    of clearance on each side - narrower than `_TOUCH_GAP`, so no link the joiner is allowed to draw
    could ever reach it, and `lanes_form_one_network` failed on it honestly, every roll.

    Only a fragment that is BOTH under the minimum AND alone in its component is swept: a short spur
    that meets the web is a real lane and is left exactly as drawn. And the orphan joiner's own guard
    applies unchanged - a fragment stays, visibly broken, if a farmhouse it serves has no other way,
    because a stranded house is the worse failure and `farmhouses_reach_a_way` should say so."""
    lanes = s.M.get("lanes") or []
    ways = [[(float(x), float(y)) for x, y in ln.get("pts") or []] for ln in lanes]
    live = [i for i in range(len(lanes)) if len(ways[i]) >= 2]
    if len(live) < 2:
        return 0
    comp = _components(ways, 4.0)  # the INK standard, as `_smooth_web._pieces` uses - not the gate's 30 ft reach
    alone = {c for c in {comp[i] for i in live} if sum(1 for i in live if comp[i] == c) == 1}
    houses = [(float(h["x"]), float(h["y"])) for h in s.M.get("houses", [])]

    def _near(pt: Pt, segs: Sequence[tuple[Pt, Pt]]) -> float:
        return min((seg_dist(pt[0], pt[1], a, b) for a, b in segs), default=float("inf"))

    swept: list[int] = []
    for i in live:
        if lanes[i].get("connector") or comp[i] not in alone or polyline_len(ways[i]) >= _WEB_MIN_FT:
            continue
        mine = list(zip(ways[i], ways[i][1:], strict=False))
        others = [sg for j in live if j != i for sg in zip(ways[j], ways[j][1:], strict=False)]
        if not others or any(_near(h, mine) <= _SERVE_FT < _near(h, others) for h in houses):
            continue
        lanes[i]["pts"] = []
        s.reink_lane(i)
        swept.append(i)
    # AND THE HUSK GOES WITH THE INK, the rule feature 145 set on the orphan joiner's own drop: an
    # emptied `pts` leaves a record declaring a lane nothing draws, which every consumer then has to
    # special-case. Removed back-to-front so the earlier indices stay valid.
    for i in sorted(swept, reverse=True):
        del lanes[i]
    if swept:
        s.M["meta"]["lane_fragments_dropped"] = s.M["meta"].get("lane_fragments_dropped", 0) + len(swept)
    return len(swept)


_FINE_CELL = 3.0
# THE FINE RUNG'S NOVELTY IS THE LATTICE, NOT A LOOSER CLEARANCE - and getting that wrong was a
# regression of this feature's own making (measured on cohort seeds 6 and 18, 2026-08-28). The rung
# first planned at `_TOUCH_GAP`, the margin a link is allowed INTO a junction, on the reasoning that
# a lane and a plot fence share a line in a real village. That margin is earned by the last few feet
# of a short link; this rung can draw a 300 ft lane, and at 4 ft it drew one THROUGH a garden
# (`features_do_not_overlap`, seed 18) and another under a farmhouse (`houses_clear_of_lanes`, seed
# 6). So it plans at the ordinary fabric standard and buys its reach from the CELL alone:
# `WEB_FABRIC_GAP + 3 * 0.71` = 9.1 ft against the 14.1 ft the coarse detour rung was asking, which
# is what opened tripwire seed 27's corridor while keeping every lane off the steadings.
_SERVE_FT = 100.0  # ft: a way serves a house within this - `farmhouses_reach_a_way`'s own figure, so a dropped fragment never strands one
