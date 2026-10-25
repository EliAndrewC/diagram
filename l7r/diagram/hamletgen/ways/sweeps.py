"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index.

Research: lane sweep plumbing - NONE"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, edge_dist, point_in_poly, rot_rect, seg_closest, seg_dist, segments_cross

from ..consts import (
    STEADING_ARRIVAL_FT,
    WEB_FABRIC_GAP,
    WEB_REACH_FT,
    Poly,
    Pt,
)
from .checks import stream_segs
from .fabric import _LANE_JOIN_FT, _WEB_MIN_FT, _draw_web
from .geom import (
    _TOUCH_GAP,
    WorkedGround,
    _net_reach,
    end_serves,
    lane_houses,
    memo_ground,
    polyline_len,
    steading_footprints,
    worked_ground,
    worked_ground_rings,  # noqa: F401 - re-exported: the gate test reads the sweep's own field from here
)
from .route import _route

# A LINK that joins two halves of one settlement may wander further than a door path. Going round a
# paddy is legitimately indirect, and the thing being bought is the difference between a dozen houses
# reachable and a dozen houses not.
_LINK_DIRECTNESS = 4.0
"""Research: network link directness - GUESS: searched, the record silent (feature 417 T29 pass A2, 2026-10-25); a link up to 4.0 times its chord"""


def brook_crossings(pts: Sequence[Pt], s: Settlement) -> int:
    """How many times the polyline `pts` crosses the drawn brook's course."""
    n = 0
    for f in s.M.get("streams") or []:
        br = [(float(x), float(y)) for x, y in (f.get("poly") or [])]
        n += sum(1 for a, b in zip(pts, pts[1:], strict=False) for c, d in zip(br, br[1:], strict=False) if segments_cross(a, b, c, d))
    return n


def _join_orphan_ways(s: Settlement, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> int:
    """Link any way that is not part of the settlement's one network - INCLUDING the skeleton's own.

    Found by the transitive `farmhouses_reach_a_way`, and it turned out not to be the web's fault at
    all: on a cohort hamlet the skeleton's two arms were clipped apart from the arm the connector
    leaves by, so they formed an island of their own, and every house they served counted as
    unreached. That is a pre-existing defect - it predates this feature and nothing could see it
    while the check measured distance to any polyline - and it is fixed here rather than ledgered,
    per Principle XIV.

    The link is a routed path, so it threads the steadings like any other; where no route exists the
    component is left for `settle_the_web`, which drops it off the network and draws its houses a way, or refuses the
    map (`WebRefused`).

    Research:
        orphan joined to the network - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: one network
        link crosses the brook at a crossing place - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html
        no out-and-back over the brook - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: a link crossing the brook twice is refused
        link width - CONVENTION: the widest way within `_LANE_JOIN_FT` of the link (the orphan's and the network's at least)
        orphan link directness - GUESS: searched, the record silent (feature 417 T29 pass A2, 2026-10-25); a link up to `_LINK_DIRECTNESS` (4) times the gap
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N4, 2026-10-25) - 6 (rounds of the orphan sweep); 14 (lattice cell for the retry route)
    """
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
            # ...ACROSS THE BROOK ONLY AT A FORD (settlement-review of Mizuguchi, feature 261): planned against no water at all,
            # a link crossed the brook 60 ft from any ford and came straight back to its own bank. The brook, gapped at its
            # fords, is the one water it is held to - a ditch it may still cross, and `bridges()` decks it.
            _try = _route(cand[1], cand[2], hard, walls, stream_segs(s), gap=WEB_FABRIC_GAP, pad_mult=2.0, cell=14.0)
            # A TIGHT-SQUEEZE FALLBACK WAS TRIED HERE AND REVERTED (feature 126). When an orphan
            # could not be linked at the open clearance, a second attempt planned at 45% of
            # `WEB_FABRIC_GAP`, on the reasoning that the sources describe this very lane as
            # "colonized as semi-private space by the adjoining house". It was wrong twice over:
            # measured, it changed no connectivity number at all (the orphans it was aimed at are
            # separated by the PADDY, not by a wall, so no clearance helps), and it put treads on
            # houses - `make map` came back with features_do_not_overlap and houses_clear_of_lanes
            # on the reference hamlet. Do not re-add it: an orphan across a field is honestly
            # unlinkable, and the fix for those houses is their reserved corridor (the settle), not a narrower lane.
            if _try and polyline_len(_try) <= _LINK_DIRECTNESS * max(cand[0], 1.0):
                # ...AND NEVER OVER THE BROOK AND BACK (settlement-review of Mizuguchi, feature 261): a link from one bank to
                # the same bank that crosses twice - out at one ford, home at the next - reads as two planks for nothing. It
                # was kept as the last resort when no other candidate linked the orphan; that fallback emitted the violation
                # (feature 287, ways W06, FR-005), so it is refused like any other, and an orphan no clean link reaches is
                # left for the web's last pass (`settle_the_web`: dropped off the network, its houses redrawn a way).
                if brook_crossings(_try, s) and brook_crossings(_try, s) % 2 == 0:
                    continue
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


def farm_bands(M: Mapping[str, Any]) -> list[Poly]:
    """A farm's own wood, which no carried end crosses: its grove bands (`groves`) as rotated rectangles, and the dooryard copse's
    clumps (`village_groves` role `copse`, each a household's share) as octagons of the clump radius `r` - not the shelter belt.
    Research: a farm's own wood - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: its grove and its share of the copse, one wood
        its salts, guards and sentinels - NONE: they decide nothing about the place - 8 (octagon for a copse clump)
    """
    bands = [rot_rect(float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"]), float(g.get("rot") or 0.0)) for g in M.get("groves") or [] if g.get("w")]
    for g in M.get("village_groves") or []:
        r = float(g.get("r") or 0.0)
        if g.get("role") == "copse" and r > 0.0:
            bands += [[(float(c[0]) + r * math.cos(k * math.pi / 4), float(c[1]) + r * math.sin(k * math.pi / 4)) for k in range(8)] for c in g.get("clumps") or []]
    return bands


def _sweep_dangling_ends(s: Settlement, fields: Sequence[Poly] = ()) -> int:
    """Pull back any lane end that reaches NOTHING, and empty what is left if pulling back cannot save it.

    RUNS LAST, BESIDE THE OTHER FINISHING SWEEPS, for the reason they all do: the passes above rewrite ends. A link laid
    to reach a piece another pass then drops, or a tail left by a trim, is an end in open ground - and
    `lanes_reach_something` is the rule it breaks, on the gate, one map at a time (settlement-review, feature 230 passes 10
    and 11: the same 5 ft link on the reference hamlet came back whenever the map moved, ending 73 ft from any way and 76
    from any house). The rule's own figure is 60 ft to a way, a house or the field, so that is what is asked here; each
    end is walked in along its own last segment 4 ft at a time until it passes (`_walk_in`), and a lane whittled under
    `_WEB_MIN_FT` is emptied, and `stage_web`'s husk drop takes its record. A connector is exempt: it leaves the map by design.

    Research:
        lane end reaches something - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: pulled back until it serves a way, the field or a house, 4 ft at a time - never one reached across a neighbor's land, owed none (`geom.lane_houses`)
        not the way it left - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: an end does not count as reaching a way the lane's other end stands on (within `_TOUCH_GAP`), so a link off a way with nothing at its far end is pulled back to nothing - our reading of "a stretch that joins nothing of the network is not drawn" against "reaching another way within 60 ft of it", which does not say whether the way a lane leaves is another way
        the track out and streets exempt - research/questions/0081-village-lanes.drawing.html, research/questions/0033-row-villages-resson.drawing.html: the track out runs off the edge of the map and a row's street runs on off the map as the road into it; the track out runs from the cluster's edge off the map, so its far end is no lane end; a row village's street keeps its own end rules (`ways/street.py`)
        a link another lane ends on kept - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the lanes are one network, joined where their treads meet - a short lane another lane ends on is that join, not debris
        end carried to the dooryard - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane a house needs ends at its dooryard - carried to the owed house nearest the end, never a household reached across a neighbor's land, owed none (`geom.lane_houses`)
        kept whole for a house - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane whose pull-back would leave a farmhouse with no way is restored whole, its unserving end carried to a dooryard where an owed house stands within the carry's reach and no grove band is in the way, and otherwise left where it was drawn - the page pulls back an end that reaches nothing and does not say what gives when that would strand a house
        grove band not crossed - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html, research/questions/0033-row-villages-resson.drawing.html: no lane runs through a farm's own wood - its grove and its share of the dooryard copse, one wood (0036) - the way runs outside the grove or through a gap in it - so an end is not carried across one
        walked on to the house it serves - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane ends at the dooryard - an end that reaches walks back along its own lane, while it still reaches, to its closest approach to the nearest owed house within 120 ft (2 x `_REACH_FT`); never while within 60 ft (`_REACH_FT`) of another way - not the one its far end stands on (405 T82)
        dooryard carry reach - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A1, 2026-10-25); up to 120 ft (2 x `_REACH_FT`); the page gives a lane end's reach (60 ft), not a carry's
        a whittled lane emptied - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); a lane pulled back under `_WEB_MIN_FT` (30 ft) is emptied, for the debris sweep to finish
        a house served - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the page's check that every farmhouse has a way within 100 ft (`_SERVE_FT`): a lane that is some house's only way within it is kept; the page's 60 ft / 12 ft is what a lane END is held to, not this (405 T75)"""
    lanes = s.M.get("lanes") or []
    owed = lane_houses(s.M)  # the houses an end serves, is kept for or carried to: a household reached across a yard is owed none (feature 317)
    # THE ONE END RULE (269 B04/B17): `end_serves`, the body the trims and the gate read - this sweep kept its own copy, and
    # with it the 60 ft to the field the bund rule retired. `fields` stands in only where the manifest records no ground.
    ground = memo_ground(s, "worked", worked_ground) if worked_ground_rings(s.M) else WorkedGround([list(f) for f in fields])
    steadings = steading_footprints(s.M)
    # a farm's own wood, which an end is not carried across (feature 291): its grove bands, each ROTATED as recorded, as
    # `lay_door_paths` reads it (405 T83: the sweep read the unrotated box, so the two disagreed on where a turned farm's wood
    # stood), and its share of the dooryard copse - 0036 counts a farm's grove and its share of the copse as one wood, its clumps
    # kept beside its house and free of lanes (405 T83's round: the copse had been left out as common ground)
    _bands = farm_bands(s.M)
    fixed, emptied = 0, []
    for i, ln in enumerate(lanes):
        if ln.get("connector") or ln.get("street"):
            continue
        pts = [(float(x), float(y)) for x, y in (ln.get("pts") or [])]
        if len(pts) < 2:
            continue
        others = [
            sg
            for j, o in enumerate(lanes)
            if j != i and len(o.get("pts") or []) >= 2
            for sg in zip([(float(x), float(y)) for x, y in o["pts"]], [(float(x), float(y)) for x, y in o["pts"]][1:], strict=False)
        ]

        def _reaches(q: Pt, far: Pt, _o: Sequence[tuple[Pt, Pt]] = others) -> bool:  # ...a house it SERVES: never one reached across a yard
            # ...NOR THE WAY IT LEFT (feature 405 T14, D9, as `_trim_to_service` since feature 261): an end is not served by a
            # way the lane's OTHER end (`far`) stands on, or the walk below keeps a link off a way as a stub reaching only that way
            return end_serves(q, [sg for sg in _o if seg_dist(far[0], far[1], sg[0], sg[1]) > _TOUCH_GAP], owed, ground, steadings)

        _mine = [(float(x), float(y)) for x, y in pts]
        # ...BUT NEVER PAST ANOTHER LANE'S END THAT RESTS ON THIS ONE (269 E4). Pulling an unserving end back takes the
        # stretch it gives up away from any lane that was laid to meet it there - a straggler's end on it, say - and that
        # lane is left in open ground, the network in two pieces at the ink tolerance. Found when 269 B06 re-laid Sawada's
        # hem and its re-roll put a straggler's end 27 ft from the web it had met. The pull-back stops at that junction.
        _tails = [(float(o["pts"][e][0]), float(o["pts"][e][1])) for j, o in enumerate(lanes) if j != i and len(o.get("pts") or []) >= 2 for e in (0, -1)]

        # (and a lane left short by the hold is still the link that lane ends on, so it is not emptied as debris below)
        def _near(q: Pt, far: Pt, _o: Sequence[tuple[Pt, Pt]] = others) -> float:  # how near the nearest house it serves (405 T74)
            # ...never walked on from a way it reaches: a junction end stays at its junction - but the way its far end stands on
            # is no other way (405 T82, as `_reaches`), so a link off a way still walks on to its house
            if any(seg_dist(q[0], q[1], a, b) <= _REACH_FT for a, b in _o if seg_dist(far[0], far[1], a, b) > _TOUCH_GAP):
                return float("inf")
            # ...and only toward a house within the dooryard carry's reach (2 x `_REACH_FT`), never a far one: an end reaching
            # only the field is not walked off it toward a house it does not serve (batch 6's round)
            return min((d for h in owed if (d := math.dist(q, h)) <= 2.0 * _REACH_FT), default=float("inf"))

        _walk_in(pts, _reaches, _tails, _near)
        pts.reverse()
        _walk_in(pts, _reaches, _tails, _near)
        pts.reverse()
        if pts == _mine:
            continue
        _held = any(held_at(a, b, _tails) is not None for a, b in zip(pts, pts[1:], strict=False))
        if len(pts) < 2 or (polyline_len(pts) < _WEB_MIN_FT and not _held):  # a short lane another lane ends on is a LINK, not debris
            pts = []
        # ...AND NEVER AT THE COST OF A HOUSE, the clause every other sweep here carries. Without it this pass drops a lane
        # some farmhouse needs, `generate` re-rolls the whole map to serve it, and the roll costs what the re-roll costs:
        # measured on the reference hamlet, attempt 1 became attempt 3 and its seed went +20.5% (feature 230 pass 11).
        _served = [h for h in owed if min((seg_dist(h[0], h[1], a, b) for a, b in zip(_mine, _mine[1:], strict=False)), default=float("inf")) <= _SERVE_FT]
        _rest = [
            sg
            for j, o in enumerate(lanes)
            if j != i and len(o.get("pts") or []) >= 2
            for sg in zip([(float(x), float(y)) for x, y in o["pts"]], [(float(x), float(y)) for x, y in o["pts"]][1:], strict=False)
        ]
        _rest += list(zip(pts, pts[1:], strict=False))
        if any(min((seg_dist(h[0], h[1], a, b) for a, b in _rest), default=float("inf")) > _SERVE_FT for h in _served):
            # A FARMHOUSE WOULD LOSE ITS WAY, so the lane stays - and then its end must EARN its ink rather than stop in
            # grass. The end is carried on to the dooryard of an owed house near it (269 B17: a lane that serves a farmhouse
            # ends at its dooryard). Dropping it instead is what `generate` answers with a whole re-roll (the reference
            # hamlet went to attempt 3 and its seed +20.5%), and a re-roll is a heavy price for a tread that only needed to
            # arrive somewhere.
            pts = [(float(x), float(y)) for x, y in _mine]
            for _e in (-1, 0):
                if _reaches(pts[_e], pts[0] if _e == -1 else pts[-1]):
                    continue
                _q = carry_to_dooryard(pts[_e], owed, steadings, 2.0 * _REACH_FT, groves=_bands)
                if _q is not None:
                    pts = [*pts, _q] if _e == -1 else [_q, *pts]
            if [[round(x, 1), round(y, 1)] for x, y in pts] == ln["pts"] or not s.reshape_lane(ln, pts):  # ...admitted by the matrix (M8)
                continue
            s.reink_lane(i)
            fixed += 1
            continue
        ln["pts"] = [[round(x, 1), round(y, 1)] for x, y in pts]
        s.reink_lane(i)
        if not pts:
            emptied.append(i)
        fixed += 1
    s.drop_lanes(emptied)  # record and ink together - see `drop_lanes`
    return fixed


def _walk_in(pts: list[Pt], reaches: Callable[[Pt, Pt], bool], tails: Sequence[Pt], near: Callable[[Pt, Pt], float] | None = None) -> None:
    """Walk the LAST end of `pts` in, in place, until it `reaches` something: along its own last segment 4 ft at a time, a
    vertex dropped only once the end is within 4 ft of it, so the end stops within 4 ft of the last point that serves.
    `reaches` is asked of the end and the lane's other end (the way it left does not count, D9).

    NEVER A WHOLE SEGMENT AT A TIME (feature 405 T14, D8): the sweep used to pop a vertex while the end did not serve, so an
    end whose last segment passed a house partway landed on the vertex before it, past the last point that served (DRIFTED
    in 385's impl-drift round, T106) - the same fault T12 took out of `_trim_to_service`. The 269 E4 hold is asked before
    each step: where another lane's end rests on the segment, the end stops there (`held_at`).

    Research:
        held nearest the house it serves - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane ends at the dooryard - walked on while it still reaches and nears the house it serves (`near`), never from where `near` is infinite (a junction end stays at its junction)
        pulled back to the last point that serves - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane end that reaches nothing is pulled back to the last house it serves, 4 ft at a time
        held at a junction - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the lanes are one network, joined where their treads meet - a pull-back stops where another lane's end rests on it"""
    while len(pts) >= 2 and not reaches(pts[-1], pts[0]):
        a, b = pts[-2], pts[-1]
        hold = held_at(a, b, tails)
        d = math.dist(a, b)
        if hold is not None and math.dist(b, hold) <= 4.0:
            pts[-1] = hold
            return
        if d <= 4.0:
            pts.pop()
            continue
        pts[-1] = (a[0] + (b[0] - a[0]) * (d - 4.0) / d, a[1] + (b[1] - a[1]) * (d - 4.0) / d)
    # ...AND ON, TO THE HOUSE IT SERVES (405 T74, D52): the first point walking in that reaches stands on the far edge of the last
    # house's 60 ft zone, up to 60 ft past the house in open ground, where 0246 ends a lane at the dooryard - so while the end
    # still reaches and comes nearer a house it serves (`near`), it walks on, held at a junction as above
    while near is not None and len(pts) >= 2:
        a, b = pts[-2], pts[-1]
        hold = held_at(a, b, tails)
        if hold is not None and math.dist(b, hold) <= 4.0:
            return
        d = math.dist(a, b)
        nxt = a if d <= 4.0 else (a[0] + (b[0] - a[0]) * (d - 4.0) / d, a[1] + (b[1] - a[1]) * (d - 4.0) / d)
        here = near(b, pts[0])
        # ...never from where `near` says to stay (infinite: an end at a junction) - a step just past it would score nearer
        # and walk the end off its junction toward a house (batch 6's round 4)
        if here == float("inf") or not reaches(nxt, pts[0]) or near(nxt, pts[0]) >= here:
            return
        if d <= 4.0:
            pts.pop()
        else:
            pts[-1] = nxt


def held_at(a: Pt, b: Pt, tails: Sequence[Pt]) -> Pt | None:
    """The point of the segment from `a` to the end `b` that the farthest-out of `tails` (other lanes' ends) rests on,
    within `_TOUCH_GAP` - where a pull-back of that end has to stop - or None where no other lane ends on it."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    l2 = dx * dx + dy * dy
    held = [max(0.0, min(1.0, ((t[0] - a[0]) * dx + (t[1] - a[1]) * dy) / l2)) for t in tails if l2 > 0 and seg_dist(t[0], t[1], a, b) <= _TOUCH_GAP]
    return (a[0] + dx * max(held), a[1] + dy * max(held)) if held else None


def carry_to_dooryard(q: Pt, houses: Sequence[Pt], steadings: Sequence[Sequence[Pt]], reach: float, step: float = 2.0, groves: Sequence[Sequence[Pt]] = ()) -> Pt | None:
    """Where an end at `q` stops once carried straight toward the nearest farmhouse within `reach`: the first point of the
    walk (in `step` ft) inside `STEADING_ARRIVAL_FT` less a margin of any steading's built ground, so the tread arrives at
    the dooryard and stops short of the wall (a tread on the doorstep laps the farmhouse, `features_do_not_overlap`).
    None where no house is within `reach`, or the walk reaches none of it (269 B17) - or it would enter one of `groves`, a
    farm's grove band, which no lane crosses (feature 291: an end carried straight at a house on cohort seed 3 went across
    the thin east band of the farm it served).

    Research:
        end carried to the dooryard - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: stopping short of the wall
        grove band not crossed - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: no lane runs through a farm's own wood"""
    near = [h for h in houses if 0.0 < math.dist(q, h) <= reach]
    if not near:
        return None
    h = min(near, key=lambda c: math.dist(q, c))
    d = math.dist(q, h)
    stop = STEADING_ARRIVAL_FT - 4.0  # inside the arrival bar by the clip's own 4 ft step
    for k in range(1, int(d / step) + 1):
        p = (q[0] + (h[0] - q[0]) * k * step / d, q[1] + (h[1] - q[1]) * k * step / d)
        if any(point_in_poly(p[0], p[1], list(g)) for g in groves):
            return None
        if any(edge_dist(p[0], p[1], list(sp)) <= stop or point_in_poly(p[0], p[1], list(sp)) for sp in steadings):
            return p
    return None


_REACH_FT = 60.0  # ft: `WAY_END_REACH_FT`, the reach to another way; here the reach a home-bank drop and a dooryard carry look within
"""Research: end reach to a way - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 60 ft"""
_SERVE_FT = WEB_REACH_FT  # ft: a way serves a house within this - `farmhouses_reach_a_way`'s own figure, so a dropped fragment never strands one
"""Research: a way serves a house - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 100 ft, as back lanes bring every farmhouse within 100 ft of one"""


from .tails import (  # noqa: E402, F401 - split out at the 1,000-line bar (feature 280); re-exported for the web and the tests
    _ALONG_DEG,
    _ALONG_FT,
    _DOUBLED_DEG,
    _RESEAT_FT,
    _sweep_doubled_tails,
    along_tail,
    cut_at_tail,
    cut_keeps_network,
    reseat_on_way,
)
