"""Split from hamletgen/homesteads.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist, surface_water_dist

from ..consts import FOOTPATH_FABRIC_GAP, Pt
from ..plan import SitePlan
from .fixtures import homestead_box

_WELL_DRAWN_R = 12.0
"""The wellhead's DRAWN half-extent, used when asking how far a candidate seat would push the crop.
It is the `vr` the glyph draws (not the `r` clearance radius), because the frame follows the ink -
`crop_not_held_open_by_one_feature` quotes a well's extent as 16 px across."""


def well_target(households: int) -> int:
    """How many communal draw-wells a hamlet of this size keeps.

    `wells_sized_to_population` wants 2-20 households per well at hamlet scale (the setting's
    deliberate prosperity liberty runs generous wells), so the band for 12 households is 1 to 6.
    One per ~6 households sits mid-band and matches what the authored hamlets draw - a couple of
    shared wells among the courtyards, not one per farm and not one for the whole place."""
    return max(1, min(6, round(households / 6.0)))


def worst_after(c: tuple[float, float, float], needy: Sequence[Mapping[str, Any]], standing: Sequence[float]) -> float:
    """The walk of the household WORST served once a well is dug at `c` - the minimax objective of the greedy
    pass in `place_wells`, lifted out (feature 223). `standing[i]` is needy house i's distance to its nearest
    well already standing, computed once per sort by the caller; the house's walk after the dig is the smaller
    of that and its distance to `c`, and the seat's score is the largest such walk."""
    return max(min(sd, math.hypot(h["x"] - c[1], h["y"] - c[2])) for h, sd in zip(needy, standing, strict=True))


# A FARM WITH ITS OWN GROVE DRAWS FROM ITS OWN WELL (feature 291; research/homesteads/200, "Does a dispersed hamlet's
# outlying farm have its own well? Yes"): a shared well within reach is a nucleated settlement's arrangement, and a farm
# standing in its own grove some 250 ft from the next has no center to share. The rings are the dooryard and the service
# strip - where on the plot the well stood no page read says (a GUESS) - nearest first, never in a grove band.
OWN_WELL_RINGS_FT = ((36.0, 16), (46.0, 20), (56.0, 24), (68.0, 24), (80.0, 28), (94.0, 32), (108.0, 32))  # past the walls (a farmhouse is some 46 x 28 ft, the well box 30 ft) out to the frame


def own_well_clear(s: Settlement, x: float, y: float, half: float, boxes: Sequence[tuple[float, float, float, float]]) -> bool:
    """May a farm's own wellhead of drawn half-size `half` stand at (x, y)? Tested by FOOTPRINT: its box a 2 ft gap off
    every reserved box (`boxes`: the placed boxes but the farm's own frame, and the grove bands), and the engine's own
    ground tests - no water, crop or bog (`_well_ground_clear`), no scrub cover, nothing blocked. `well_at` asks `_fits`,
    whose circumscribed circle round a 150 ft grove band covered most of the farm it shelters (Kashikawa: 0 wells)."""
    if x < 55 or y < 88 or x > s.W - 55 or y > s.H - 26:
        return False
    if s._in_scrub_cover(x, y) or not s._well_ground_clear(x, y) or s._in_blocked(x, y):
        return False
    return not any(abs(x - bx) < half + bw / 2 + 2.0 and abs(y - by) < half + bh / 2 + 2.0 for bx, by, bw, bh in boxes)


def own_wells(s: Settlement, houses: Sequence[Mapping[str, Any]]) -> int:
    """One PRIVATE well for each farm that carries its own grove, on a ring round its house, nearest first, tested by
    `own_well_clear` against every reserved box but the farm's own frame (it holds the whole plot the well stands on).
    Returns the wells seated."""
    bands = [(float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"])) for g in s.M.get("groves", []) if all(k in g for k in ("x", "y", "w", "h"))]
    from ..ways.serve import front_door  # local: the ways are a later stage, module-level would invert the pipeline's reading order

    half = s._well_vr()
    yards = {(round(float(y["of"][0]), 1), round(float(y["of"][1]), 1)): (float(y["x"]), float(y["y"])) for y in s.M.get("threshing_yards", []) if y.get("of")}
    n = 0
    for h in houses:
        hx, hy = float(h["x"]), float(h["y"])
        frame = homestead_box(s.placed, hx, hy)
        boxes: list[tuple[float, float, float, float]] = [
            (float(p[0]), float(p[1]), float(p[2]), float(p[3])) for p in s.placed if (float(p[0]), float(p[1]), float(p[2]), float(p[3])) != frame
        ] + bands
        # ...THE DOORYARD SIDE FIRST: the seats nearest the farm's work yard, so the well stands in the dooryard and leaves the
        # service strip behind the house to the wood shed (a first cut ringed from the east and took 4 of Mizuguchi's 5)
        yard = yards.get((round(hx, 1), round(hy, 1)), (hx, hy + 1.0))
        ring = [(hx + s.px(r_ft) * math.cos(2 * math.pi * k / k_n), hy + s.px(r_ft) * math.sin(2 * math.pi * k / k_n), r_ft) for r_ft, k_n in OWN_WELL_RINGS_FT for k in range(k_n)]
        # ...INSIDE THE FARM'S OWN FRAME FIRST: a ring seat past the frame stands in the lane's room between two farms, which is
        # no farm's dooryard (Mizuguchi: two wells 56 and 68 ft out, off their plots); only where the frame holds none is the
        # nearest seat outside it taken, and `row_rules.water_rules` reports that farm
        fb = (h.get("geom") or {}).get("bbox")
        ring.sort(key=lambda q: (not (fb and abs(q[0] - fb[0]) <= fb[2] / 2 - half and abs(q[1] - fb[1]) <= fb[3] / 2 - half), math.dist((q[0], q[1]), yard), q[2]))
        # ...BESIDE THE WAY IN, NOT ON IT: the seats nearest the yard lie straight out past it, where the farm's path arrives
        # (`front_door`); a well there took the approach on every farm and the web re-routed round 12 of them (Mizuguchi:
        # 8 lanes to 34). The approach is the house-to-yard line carried past the yard, a well's box and a path's width wide.
        door = front_door(h, FOOTPATH_FABRIC_GAP + 4.0)
        approach = [(hx, hy), door] if door is not None else []
        seat = next(((x, y) for x, y, _r in ring if own_well_clear(s, x, y, half, boxes) and not (approach and seg_dist(x, y, approach[0], approach[1]) < half + s.px(12.0))), None)
        if seat is not None:
            s.well(seat[0], seat[1], private=True)
            n += 1
    return n


WATER_REACH_FT = 760.0
"""The watering rule's reach (`surface_water_dist` against 760 ft, `place_wells` below; the gate's `WATER_REACH_FT`)."""


def shared_row_wells(s: Settlement, houses: Sequence[Mapping[str, Any]], streets: Sequence[Sequence[Pt]]) -> int:
    """A row village that shares its water (`row_water` shared, feature 291 plan D18): along each street, wells beside the
    street, one at the middle of each equal stretch of the row no longer than 1.6 reaches (the watering rule's reach), so
    every farm of every row stands within reach of one. A seat is tried at each mark and a half and a quarter lot either
    way, on either side of the tread. Returns the wells seated."""
    if not streets or not houses:
        return 0
    half = s._well_vr()
    boxes = [(float(p[0]), float(p[1]), float(p[2]), float(p[3])) for p in s.placed] + [
        (float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"])) for g in s.M.get("groves", []) if all(k in g for k in ("x", "y", "w", "h"))
    ]
    frame_w = max((max(float(b[2]), float(b[3])) for b in ((h.get("geom") or {}).get("bbox") for h in houses) if b), default=s.px(240.0))
    reach = s.px(WATER_REACH_FT)
    n = 0
    for line in streets:
        if len(line) < 2:
            continue
        arc = [0.0]
        for a, b in zip(line, line[1:], strict=False):
            arc.append(arc[-1] + math.dist(a, b))

        def along(p: Pt, _line: Sequence[Pt] = line, _arc: Sequence[float] = arc) -> tuple[float, float, Pt]:
            best = min(((seg_dist(p[0], p[1], a, b), i) for i, (a, b) in enumerate(zip(_line, _line[1:], strict=False))), key=lambda t: t[0])
            a, b = _line[best[1]], _line[best[1] + 1]
            seg = math.dist(a, b) or 1.0
            t = max(0.0, min(1.0, ((p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])) / (seg * seg)))
            q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            return _arc[best[1]] + seg * t, best[0], q

        mine = sorted(((along((float(h["x"]), float(h["y"]))), h) for h in houses), key=lambda t: t[0][0])
        mine = [(u, h) for (u, d, _q), h in mine if d <= 2.0 * frame_w]
        if not mine:
            continue
        us = [u for u, _h in mine]
        # SPACED BY DISTANCE ALONG THE STREET, not by farms: a both-sided row has two farms at every step, and a stride in
        # farms dug a well at every one and a half lots (Kashikawa: 16 wells for 20 farms). The row is cut into equal
        # stretches no longer than 1.6 reaches and a well dug at each one's middle: every farm is then within 0.8 of a
        # reach of one along the street, the rest of the reach left for the lot's depth across it.
        span = us[-1] - us[0]
        stretches = max(1, math.ceil(span / (1.6 * reach)))
        for u in [us[0] + span * (j + 0.5) / stretches for j in range(stretches)]:
            for du in (0.0, frame_w / 2, -frame_w / 2, frame_w / 4, -frame_w / 4):
                uu = max(0.0, min(arc[-1], u + du))
                k = max(0, min(len(arc) - 2, next(j for j in range(len(arc) - 1) if arc[j + 1] >= uu)))
                a, b = line[k], line[k + 1]
                seg = math.dist(a, b) or 1.0
                f = (uu - arc[k]) / seg
                p = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
                nx, ny = -(b[1] - a[1]) / seg, (b[0] - a[0]) / seg
                seated = False
                for sgn in (1.0, -1.0):
                    off = half + s.px(8.0)  # off the street's tread, beside it
                    x, y = p[0] + sgn * nx * off, p[1] + sgn * ny * off
                    if own_well_clear(s, x, y, half, boxes):
                        s.well(x, y)
                        boxes.append((x, y, 2 * half, 2 * half))
                        n += 1
                        seated = True
                        break
                if seated:
                    break
    return n


def place_wells(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]]) -> int:
    """Seat the communal wells INSIDE the house cloud, not on a box around it.

    The engine's `place_wells` sweeps a grid over a bbox, which is right for a town's street blocks
    and wrong for a loose farm cluster: the bbox corners are open ground, so a well lands past the
    outermost homestead and, being a hard crop feature with a 16 px extent, drags the map's frame
    out after it and leaves a band of empty scrub on that side
    (`crop_not_held_open_by_one_feature`). Insetting the bbox was tried first and is not the fix -
    it starves an elongated cluster of wells entirely, because the inset box no longer holds a grid
    cell (`settlement_has_wells`, seed 3).

    So the seats are derived from the HOUSES: a candidate must have several homesteads around it and
    none too far, which is what "among the dwellings" means, and the innermost candidates are tried
    first. `well_at` gives the engine's own verdict on each - it refuses a seat on a lane, a crop, a
    footprint or too near another well - so nothing here restates a placement rule."""
    grove_farms = [h for h in houses if (h.get("geom") or {}).get("groves")]
    if grove_farms:
        streets = getattr(s, "_row_streets", None) or []
        if plan.settlement_form == "linear" and plan.row_water == "shared" and streets:
            shared_row_wells(s, grove_farms, streets)
        else:
            own_wells(s, grove_farms)
        s.M["meta"]["row_water_drawn"] = plan.row_water if plan.settlement_form == "linear" else None
        houses = [h for h in houses if h not in grove_farms]  # the communal wells serve the rest, if any
        if not houses:
            return len(s.M.get("wells", []))
    xs = [h["x"] for h in houses]
    ys = [h["y"] for h in houses]
    ccx, ccy = sum(xs) / len(xs), sum(ys) / len(ys)
    want = well_target(plan.spec.households)
    placed: list[Pt] = []
    # A WELLHEAD MAY NOT STAND IN THE SHELTER BELT (settlement-review, Inashiro 2026-08-18). The
    # belt is drawn later, but `village_grove` SKIPS any clump whose canopy would reach a wellhead
    # (`wells_clear_of_trees` - a well lost under the grove reads wrong), so a well seated inside
    # the belt's footprint silently deletes the clumps around it. Measured on Inashiro after the
    # tie-break change moved a well to (1098,1387), inside the belt's own footprint: the 40 ft band
    # at y1360-1400 went from 8 clumps to 1, and the belt acquired its first zero-canopy latitude in
    # a 930 ft run - a hole straight through the WINDWARD side, which is the entire point of a
    # windbreak. Nothing caught it: the belt's continuity is not gated, and the well checks are all
    # about the well.
    #
    # The belt is DERIVED from the houses, which already stand, so the prospective footprint can be
    # asked for now - the same expression `stage_woodland` will call, so the two cannot disagree.
    # This is a PREFERENCE and not a veto, per this function's standing rule that a settlement with
    # a badly-placed well beats one with no well: it sorts belt seats last, so one is taken only
    # when nothing outside the belt serves at all. It also happens to push wells toward the
    # dooryards, which is where the idiom 井戸端会議 puts them.
    from ..hinterland import belt_polygon  # local: hinterland is a later stage, module-level would invert the pipeline's reading order

    _belt = belt_polygon(s, plan)

    def _in_belt(c: tuple[float, float, float]) -> int:
        return 1 if _belt and point_in_poly(c[1], c[2], _belt) else 0

    # THE MINIMAX SERVES THE HOUSES THAT NEED A WELL (known-open ledger 2026-08-16): the
    # worst-served objective used to count every house, including those
    # `settlement_dwellings_watered` already treats as watered by a nearby stream / channel /
    # pond (Kashikawa's SW pocket, 77-182 ft from the stream head - the GM-settled "no redundant
    # well beside a living stream" case), so the objective and the check read two definitions of
    # "needs a well". `surface_water_dist` is the check's own predicate; a house within its
    # reach of surface water drops out of the objective and out of the rescue pass below. If
    # EVERY house is surface-watered the objective falls back to all of them - wells are still
    # dug (well_target), they just stop chasing houses the water already serves.
    _sw_reach = 760.0 / max(plan.ftpx, 0.01)
    needy = [h for h in houses if surface_water_dist(s.M, h["x"], h["y"]) > _sw_reach] or list(houses)
    # A RELAXATION LADDER, not a single rule. The tight neighborhood test is right for a compact
    # cluster and impossible for a stretched one: an `elongated` cluster strung along a margin has
    # no point with three homesteads inside 190 px, so the strict pass found nothing at all and the
    # map shipped with no well (seeds 3 and 12). A settlement WITHOUT a well is a much worse map
    # than one whose well sits a little wide, so the test loosens until it finds seats. It never
    # loosens into "anywhere": every seat still has to be nearer a house than the crop.
    # Only the THIRD-nearest distance relaxes - the "is this in a neighborhood" test. The distance to
    # the NEAREST house stays tight, because `wells_among_dwellings` is a 95 px gap verdict against
    # the served building's edge: a well 220 px from its closest farmhouse is standing in the fields
    # by any measure, and relaxing that rung traded one failure for another.
    # The last rung also serves a PAIR. Every rung above asks for three homesteads around a seat,
    # which is the right shape for a nucleus and leaves a two-farm satellite with no well of its own
    # - and then the coverage pass cannot rescue it either, because the ground among two farms is
    # their own courtyards. Seed 18 stranded exactly that: a pair 500 px off the cluster, 760 and
    # 777 px from the nearest well, with all 118 legal-neighborhood probes around them refused.
    # Two households sharing a draw-well is an ordinary thing; three is not a threshold nature knows.
    for third, nearest, want_near in ((190.0, 105.0, 3), (300.0, 110.0, 3), (520.0, 112.0, 3), (520.0, 112.0, 2)):
        if len(placed) >= want:
            break
        seats: list[tuple[float, float, float]] = []
        step = 22.0
        # THE SWEEP BOX IS THE HOMESTEADS', NOT THE HOUSE CENTERS' (2026-08-15, cohort seed 44).
        # A bundle's courtyard ground extends ~a house-length past its house CENTER, so a cluster
        # strung along its field margin can keep every legal well pocket just OUTSIDE the centers'
        # bbox - seed 44 had 84 legal seats, nearly all north-west of min(xs)/min(ys), and the
        # unpadded grid visited none of them (0 of 1440 probes passed; the map shipped well-less).
        # The pad only restores ground the bundles themselves cover: every rung still demands
        # near[0] <= ~105 px, so an open-field corner of the padded box is rejected exactly as the
        # docstring above promises.
        pad = 120.0
        y = min(ys) - pad
        while y <= max(ys) + pad:
            x = min(xs) - pad
            while x <= max(xs) + pad:
                near = sorted(math.hypot(x - h["x"], y - h["y"]) for h in houses)
                if len(near) >= want_near and near[want_near - 1] <= third and near[0] <= nearest:
                    seats.append((math.hypot(x - ccx, y - ccy), x, y))
                x += step
            y += step
        # GREEDY COVERAGE, not central-first throughout (settlement-review, Mizuguchi/Sawada
        # 2026-08-15): sorting every well toward the centroid put both of Mizuguchi's wells in one
        # lobe of a two-lobed cluster - the six eastern households walked 248-424 ft while the west
        # had a well within 63. The FIRST well is central (innermost legal seat, as before); every
        # LATER well takes the legal seat FARTHEST from the wells already standing, ties toward the
        # center - i.e. it serves the households the placed wells do not, which is why a real hamlet
        # digs a second well at all.
        pool = sorted(seats, key=lambda c: (_in_belt(c), c[0]))  # the FIRST well is central too, but never in the belt if anywhere else will do
        # RE-SORTED ONLY WHEN A WELL HAS LANDED (feature 278, FR-004). The key reads the wells placed and the crop boxes, and
        # inside this loop only a well that lands changes either - so a pass that popped a seat and placed nothing left a
        # list already sorted by the key it would be sorted by again (Kuwabata: 168 sorts, 72,324 key evaluations, the
        # most of its 1.8 s appurtenance stage). The house-distance part of the key never reads the wells, so it is
        # computed once per seat.
        _sorted_at = -1
        _near_of: dict[tuple[float, float, float], float] = {}
        while pool and len(placed) < want:
            if placed and len(placed) != _sorted_at:
                # ...by MINIMAX NEED, in ~3-grid-step buckets, centrality breaking ties inside a
                # bucket. Two failed rankings led here, and both are worth remembering. Strict
                # farthest-first (the 2026-08-15 greedy-coverage fix) let a seat 91 px OUTSIDE the
                # cluster beat an interior seat covering the same households - the exterior well
                # held Sawada's whole frame open (crop_not_held_open_by_one_feature). Bucketing
                # that same farthest-first score fixed the frame and re-broke coverage the other
                # way: on Mizuguchi the spread rung walked EAST past the last house into scrub
                # while the one under-served household stood at the WEST end (settlement-review
                # 2026-08-16). Both fail because "far from the standing wells" is a proxy for the
                # real quantity, which is the walk of the household WORST served after the well is
                # dug - so score that directly: pick the seat minimizing the farthest any house
                # would remain from its nearest well. A seat past the row's end cannot beat an
                # in-row seat (it serves nobody the row seat does not), and a seat in an unserved
                # lobe wins outright, which is what the greedy fix was for in the first place.
                # ONCE PER SORT, ONCE PER CANDIDATE (feature 223, GM 2026-09-11: "the wells key"). The standing wells do
                # not change while the pool is sorted, so each needy house's walk to its nearest standing well is
                # taken once here, and the key tuple below is built once per candidate - it used to call
                # `_worst_after` and `_extent_added` twice each per candidate and re-derive every house's walk to every
                # standing well inside each call (70,416 calls, 1.2 million terms on Kuwabata). Same numbers, same
                # order: `worst_after` is the lifted body, held to the nested form by its test.
                _standing = [min(math.hypot(h["x"] - wx, h["y"] - wy) for wx, wy in placed) for h in needy]

                def _worst_after(c: tuple[float, float, float], standing: Sequence[float] = _standing) -> float:
                    return worst_after(c, needy, standing)

                # AND AN INTERIOR SEAT BEATS A PADDED ONE THAT SERVES THE SAME HOUSEHOLDS. The sweep
                # box above is padded 120 px past the house CENTERS because a bundle's courtyard
                # really does reach that far, and without the pad seed 44 shipped well-less. But the
                # pad is symmetric, so it equally offers seats BEYOND the outermost homestead on
                # every side - and a wellhead is a hard crop feature with a 16 px extent, so one
                # seated out there drags the map's frame after it and leaves a band of empty scrub
                # (`crop_not_held_open_by_one_feature`). The RESCUE pass below already refuses
                # exactly that, with its `min(xs) <= x <= max(xs)` test and a comment giving this
                # very reason; the greedy pass did not - two passes carrying two definitions of
                # "inside the house cloud", with the looser one running first.
                #
                # MEASURED on cohort seed 41: the second well won its minimax bucket on the strength
                # of one north-east household, then seated 76 px NORTH of that household and 66 px
                # past every other feature on the map. The minimax objective is right and is not
                # what moved here - the tie-break was, because distance-to-centroid cannot express
                # "this seat is outside the settlement".
                #
                # SO IT IS A TIE-BREAK AHEAD OF CENTRALITY, NOT A FILTER. The padded ground stays in
                # the pool and still wins when nothing inside the cloud serves the same households,
                # which is what the pad was added for; it simply can no longer outrank an interior
                # seat that does. Same shape as every other rule in this function: relax rather than
                # forbid, because a settlement with a badly-placed well beats one with no well.
                # OUTSIDE WHAT, EXACTLY - the CROP's own box, not a box round the house CENTERS. The
                # first version of this tie-break tested `min(xs)..max(xs)`, an AABB of house centers,
                # and settlement-review (Inashiro 2026-08-17) named the flaw before it bit: an AABB
                # cannot tell "in the settlement" from "in the box", so on a two-lobed cluster the
                # ~345 px of grove and scrub BETWEEN the lobes scores as interior, exactly like a
                # courtyard. Cohort seed 29 then did bite - a well 64 px north of every other feature,
                # inside the centers' box and holding the whole frame open.
                #
                # `_crop_boxes` is what `crop_to_content` itself reads, so asking it is asking the
                # question the check will ask: a seat inside the box the crop will set cannot hold the
                # frame open, whatever its relation to the house centers. Same-source doctrine, and it
                # picks up the houses' DRAWN extents plus their yards, gardens, sheds and byres rather
                # than a point per house. (The box can only GROW later - the woodland and the pond are
                # placed after - so this is conservative in the safe direction.)
                _cb = s._crop_boxes(city=False)
                _bx0 = min((b[0] for b in _cb), default=min(xs))
                _bx1 = max((b[1] for b in _cb), default=max(xs))
                _by0 = min((b[2] for b in _cb), default=min(ys))
                _by1 = max((b[3] for b in _cb), default=max(ys))

                # A TIE-BREAK CANNOT REACH A SEAT WITH NO RIVAL IN ITS BUCKET, so the FRAME goes into
                # the score itself. Ranking outside-ness ahead of centrality fixed cohort seed 29 and
                # left seed 7 failing for the reason a tie-break always leaves one: its pad seat was
                # alone in its minimax bucket, so there was nothing to break the tie against. Seed 7's
                # well sits 25 px past the northernmost byre and holds the whole frame open
                # (`crop_not_held_open_by_one_feature`), because a wellhead is a hard crop feature with
                # a 16 px extent and the crop follows it out.
                #
                # THE EXCHANGE RATE IS 1:1 IN PIXELS, which is what makes this a rule rather than a
                # knob: a seat that drags the frame out by N px must save at least N px of the
                # worst-served household's walk to be worth it. Both quantities are distances in the
                # same units, so no weighting has to be invented - and the well that genuinely serves
                # an outlying lobe still wins, because the coverage it buys is real.
                def _extent_added(c: tuple[float, float, float], bx0: float = _bx0, bx1: float = _bx1, by0: float = _by0, by1: float = _by1) -> float:
                    """How far past the crop's predicted box this seat (drawn radius included) reaches."""
                    return max(0.0, bx0 - (c[1] - _WELL_DRAWN_R), (c[1] + _WELL_DRAWN_R) - bx1, by0 - (c[2] - _WELL_DRAWN_R), (c[2] + _WELL_DRAWN_R) - by1)

                # ...AND THE LAST TIE-BREAK IS THE NEIGHBORHOOD, NOT THE CENTROID (settlement-review,
                # Sawada 2026-08-18). Once the minimax bucket and the frame term are equal, the
                # remaining sort was `c[0]` - the seat's distance to the cluster CENTROID, computed
                # when the pool was built. On a ONE-lobed cluster that reads as "the most central
                # seat wins" and is fine. On a TWO-lobed one the centroid is the empty ground
                # BETWEEN the lobes, so the tie-break actively prefers the gap: Sawada's second well
                # moved off a seat serving 11 households within 300 ft onto one serving 5, and the
                # worst walk went 364 -> 493 ft. Same family as the `_extent_added` fix above and as
                # the standing rule against letting an aggregate stand in for the distributed thing
                # a verdict is about - a centroid is not a place anybody lives.
                #
                # The measure that IS the question: how tightly is this seat surrounded by
                # homesteads - the distance to the `want_near`-th nearest house, which is exactly
                # the rung's own "is this in a neighborhood" test, reused rather than restated.
                # Distance to the SINGLE nearest house was the ledger's sketch and is rejected: it
                # is minimized by hugging one outlying farmhouse, which is the same mistake in the
                # other direction. Every seat in the pool already passed the rung, so this only
                # orders seats that are all legally "among the dwellings".
                def _neighborhood(c: tuple[float, float, float], wn: int = want_near, memo: dict[tuple[float, float, float], float] = _near_of) -> float:
                    if c not in memo:
                        memo[c] = sorted(math.hypot(c[1] - h["x"], c[2] - h["y"]) for h in houses)[wn - 1]
                    return memo[c]

                # THE BELT TERM SITS BEHIND COVERAGE, not in front of it. Ranked first it is a
                # filter, and it behaved like every other filter this function has tried: Mizuguchi's
                # second well moved off a seat inside the belt and its worst walk went 203 -> 264 ft,
                # on a map whose belt hole turned out not to be well-caused at all, so the trade
                # bought nothing. Behind the minimax bucket it can only decide between seats that
                # serve the households equally well - which is all "do not stand in the windbreak"
                # was ever entitled to decide.
                def _key(c: tuple[float, float, float]) -> tuple[float, int, float, float, float]:
                    _w, _e = _worst_after(c), _extent_added(c)
                    return ((_w + _e) // 66.0, _in_belt(c), _e, _w, _neighborhood(c))

                pool.sort(key=_key)
                _sorted_at = len(placed)
            _, x, y = pool.pop(0)
            if any(math.hypot(x - px, y - py) < 170.0 for px, py in placed):
                continue  # `wells_not_clustered`: shared wells serve separate courtyards
            if s.well_at(x, y):
                placed.append((x, y))
    # ...then a COVERAGE pass. `settlement_dwellings_watered` gives every dwelling ~760 real feet to
    # the nearest well, channel, pond or stream - generous, and still not automatic once a cluster is
    # sized from the real bundle pitch and runs 700+ px along its margin: a single well at one end
    # leaves the far end dry. So any house still out of reach gets a well sought beside it.
    reach = 760.0 / max(plan.ftpx, 0.01)
    for h in houses:
        if any(math.hypot(h["x"] - px, h["y"] - py) <= reach for px, py in placed):
            continue
        if surface_water_dist(s.M, h["x"], h["y"]) <= reach:
            continue  # watered by a stream/channel/pond - the check's own verdict; no rescue well
        # A RING PROBE, spiraling out from the house, asking `well_at` directly.
        #
        # AND EVERY CANDIDATE MUST STILL STAND AMONG THE DWELLINGS - near SOME house, not necessarily
        # the one being rescued. `wells_among_dwellings` is a 95 px edge-gap verdict against the
        # served building, and this probe used to take the first seat `well_at` allowed at any radius
        # out to 340. That was harmless while nothing reached this branch, and stopped being harmless
        # the moment the sun corridor (2026-08-13) spread a cluster enough to strand a household:
        # seed 18 seated a well 161 px from its nearest dwelling. Capping the RADIUS was the obvious
        # fix and the wrong one - it just traded the failure for `settlement_dwellings_watered`,
        # leaving the household dry. The honest constraint is the one the check states: a well may
        # be dug well away from the farm it rescues, as long as it is in somebody's courtyard.
        #
        # `open_seat` was tried here first and is the wrong tool: it optimizes a seat over a
        # RECTANGLE - furthest from what it is told to clear, ties toward the center - and it
        # returned None at every radius from 60 to 430 px around a stranded farmstead that had a
        # perfectly legal spot 40 px to its east. What this needs is not the best seat in a region
        # but ANY seat near THIS house, so it asks the question that way round, and it asks it of
        # `well_at`, which is the call that actually places a well.
        spot = None  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
        for radius in range(40, 340, 20):  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
            for bearing in range(0, 360, 20):  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                cand = (
                    h["x"] + math.cos(math.radians(bearing)) * radius,
                    h["y"] + math.sin(math.radians(bearing)) * radius,
                )  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                if not (
                    min(xs) <= cand[0] <= max(xs) and min(ys) <= cand[1] <= max(ys)
                ):  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                    # a rescue well still sits INSIDE the house cloud. A wellhead is a hard crop  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                    # feature with a 16 px extent, so one seated past the outermost homestead drags  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                    # the frame out after it (`crop_not_held_open_by_one_feature`) - the same reason  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                    # the grid above is laid over the cloud rather than a box grown around it.  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                    continue  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                if not any(math.hypot(cand[0] - hh2["x"], cand[1] - hh2["y"]) <= 95.0 for hh2 in houses):  # pragma: no cover - the rescue's among-the-dwellings floor
                    continue  # pragma: no cover - center distance <= 95 is strictly inside the check's 95 px EDGE gap
                if any(
                    math.hypot(cand[0] - px, cand[1] - py) < 110.0 for px, py in placed
                ):  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                    continue  # `wells_not_clustered`: shared wells serve separate courtyards  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                if s.well_at(cand[0], cand[1]):  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                    spot = cand  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                    break  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
            if spot is not None:  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                placed.append(spot)  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                break  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
    if not placed:
        # LAST RESORT: ask the engine. A settlement with NO well fails the gate outright, and by
        # this point the lattice has been refused everywhere - which means the courtyards are full,
        # not that there is no room. `open_seat` runs the engine's own `_fits` over the ground and
        # returns the best clear spot or None, which is the documented answer to "this pocket needs
        # one more X" and finds seats a hand-rolled scan misses (the skill's dev notes: a manifest
        # scan cannot predict `_fits`).
        spot = s.open_seat(
            (min(xs), min(ys), max(xs), max(ys)), 16.0, 16.0, well=True
        )  # pragma: no cover - reached only when the lattice above found NOTHING, which the bundle-pitch fix made rare; a settlement with no well fails the gate outright, so the branch stays
        if spot is not None and s.well_at(spot[0], spot[1]):  # pragma: no cover - the last-resort seat; unreached since the bundle-pitch fix left the courtyards open
            placed.append(spot)
    return len(placed)
