"""The ranked rounds of a cluster's seating: rings of seats offered round by round, widening, until every household is
seated (`_seat_rank_rounds`, called by `stages._seat_households_as`).

Split from `stages.py` by feature 443 T10 (the 1,000-line bar, constitution Principle X clause 13): the counter of its rounds
took `stages.py` to 1,002 lines. `stages.py` imports the function back, so `stages._seat_rank_rounds` still names it.

Research: seating plumbing - NONE: stage order, margins, reservations and bookkeeping; the rules are the callees' and the constants' own
"""

from __future__ import annotations

import math
import random

from l7r.diagram.settlement import Settlement
from l7r.diagram.work_counts import OPS

from ..consts import BUNDLE_PITCH, MIN_WEB_GAP, SUN_CORRIDOR_FT, Pt
from ..plan import SitePlan
from .seat_geometry import bank_of, declare_cluster_shape, in_a_shapes_band, shapes_drawn_at, turn_the_seat, water_push  # noqa: F401 - re-exported where callers import it


def _seat_rank_rounds(s: Settlement, plan: SitePlan, placed: int, rng: random.Random, band: tuple[float, float], bound: float, _house_max: tuple[float, float]) -> tuple[int, int]:
    """The ranks behind the front row, then the rescue rounds - a scattered hamlet's seating after its row (lifted out of
    `_seat_households` by feature 370, the 100-statement cap; the same rounds, the same draws, in the same order). Returns
    `(placed, the cloud's share)`.

    Research:
        rank jitter and the cloud's lean - GUESS: no source gives the figures, (feature 417 T29 pass E2, 2026-10-25) - a grown cluster sat irregularly (kotobank 村落) and faced its water (pass B); seats nudged up to a tenth of a pitch along the band; the cloud leaned toward the field at 0.75
        seats kept apart - NONE: a candidate dedupe, not a spacing - a seat within half a pitch of a standing house, or of a seat already offered this round (0.3 of a pitch in the rescue rounds), is not offered; the placer's envelope decides how far apart homesteads stand
        the front row's gaps and the rescue's widening - GUESS: no source gives the figures, (feature 417 T29 pass E2, 2026-10-25); a front-row gap over 1.45 pitches filled at the row's depth; the rescue band widened 22% and 16% a round
        the seating's reach - GUESS: searched, the record silent on how far a hamlet of 10-20 households spread (feature 417 T29 pass F, 2026-10-25); the rescue rounds' seats kept within `bound` of the seat center, the reach the caller computes from `FORM_BOUND`
        the step between ranks - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: an envelope's depth and then the larger of the lane's room and the yard's 39 ft of sun, so ranks stepping north-south stand as the page's rows 92 ft apart (house, yard and 39 ft of sun)
        a lane's room between ranks - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: `MIN_WEB_GAP`, the page's lane room of 18 ft (7 ft at each fence and a 4 ft tread, a map drawing convention), kept between ranks - the room the back lane of a `back_lane` hamlet is laid in, a spacing only on the dispersed form; where the ranks step north-south it falls inside the yard's sun
        rank depth jitter on an alleys hamlet only - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a back lane is the planned form, alleys the grown one, so only an alleys hamlet's ranks are taken off the line
        rank depth jitter's size - GUESS: no source gives the size, (feature 417 T29 pass E2, 2026-10-25) - only a planned settlement was regular (kotobank 村落); a rank seat moved up to half of `RANK_DEPTH_JITTER` of a pitch nearer or farther, in the rounds before the rescue
        the ranks staggered - GUESS research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: a brick pattern, the even rounds offering the midpoints between neighbors and the odd rounds the seats straight behind ("a map may stagger houses east to west")
        the ranks' rounds - GUESS: no source could speak to it, an algorithm's order, breadth or tolerance of ours (feature 417 T29 pass E, judged by the session from the code, 2026-10-25); round k stands at the row's depth plus k steps, center-out, four rank rounds then three rescue rounds
        a rank grown along the field - GUESS: no source gives it, (feature 417 T29 pass E2, 2026-10-25); once a round seats no one behind, the rank grows along the field - its ends a pitch out, half-seats half a pitch out along it at the rank's depth
        the rescue's offer along the field - GUESS: no source could speak to it, an algorithm's order, breadth or tolerance of ours (feature 417 T29 pass E, judged by the session from the code, 2026-10-25); in the rescue rounds the seats along the field are offered first - a pitch beyond each end house, half-seats half a pitch out at that house's own depth and a `_rank_step` more
        a yard's sun between ranks - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: the step adds `SUN_CORRIDOR_FT` by its north-south share, a spacing that offers seats near clear sun; the full 39 ft south of every yard and bed is held by the placer's own sun rule (`fit._sun_corridor_ok`, both ways), which refuses a seat that would stand in it
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N3, 2026-10-25) - 7 (number of seating rounds); 30 (rescue cloud candidate count); 6 (rescue cloud candidate count); 0.22 (rescue band widening per round); 0.16 (rescue band widening per round)
        its unstated figures - GUESS: searched, the record silent (feature 417 T38 pass N3, 2026-10-25) - 0.2 (seat nudged up to 0.1 pitch either way)
        its salts, guards and sentinels - NONE: they decide nothing about the place - 14 (jitter salt (rank depth)); 13 (jitter salt)
    """
    from .stages import RANK_DEPTH_JITTER, _offer_seat  # noqa: PLC0415 - at the call: stages imports this module

    seat = plan.seat
    ax, ay = seat["along"]
    ox, oy = seat["out"]
    lat, dep = band
    _cloud_placed = 0
    _row: list[Pt] = [(h["x"], h["y"]) for h in s.M.get("houses", [])]  # the front row as it stands: the lattice's rank 0
    # THE RANKS BEHIND THE FRONT ROW ARE PROPOSED BEHIND THE STANDING HOUSES (feature 227 FR-002/D8). The random cloud
    # deduped to a lattice (feature 226) relied on the placer's spiral to slide its seeds into a fit; the envelope-first
    # placer takes the seat it is given or makes one computed move, so the seats have to be RIGHT: each round offers,
    # behind every house of the rank before it, the seat one envelope's depth further from the field along the band's
    # outward vector, and the staggered seat behind the midpoint of each neighboring pair (a brick pattern). A house
    # seated there fits by construction unless the ground refuses it or the band ends. Measured before this: Kuwabata
    # 14 of 16 and Inashiro strung along the paddy at 5.1 (rolled crescent, 1.9-4.2) on the deduped cloud.
    # The rescue (rounds five to seven) keeps the old cloud over a wider band, seeded a third of a pitch apart.
    _env = s._bundle_envelope(seat["cx"], seat["cy"], _house_max[0], _house_max[1], shed=True)
    # one envelope's depth along the outward vector, plus THE ROOM A LANE NEEDS BETWEEN THE RANKS (`MIN_WEB_GAP`,
    # both neighbors' clearance and the tread between them) - four pixels was the first figure and it left the pool's
    # ranks abutting at a median 4 px, which no alley can thread: the web then could not reach the interior and
    # cohort seed 39 stranded a farmhouse the re-roll could not save. A rank is kept that room from the rank in front
    # (a spacing only: the dispersed form that ranks lays no lane between them). And, wherever the ranks step north or south (feature 328: north only, before - but a rank
    # stepping south stands in the sun of the rank behind it just as one stepping north does), the sun corridor a yard
    # owes to its south (`SUN_CORRIDOR_FT`): the rank in front stands exactly there - and the rank's lane runs IN that
    # sun, not beyond it (a lane is no farmhouse; feature 328: the two were added, a step of about 111 ft against
    # 0038's rows 92 ft apart, house, yard and sun), so the gap is the larger of the lane's room and the sun's,
    # and at the bare depth every seat behind it was clear of the ground and refused by the parts' rules (cohort
    # seed 8, the paddy to the south: the "clear" seats of every rank round failed, 9 of 11 seated)
    _rank_step = abs(ox) * _env[2] + abs(oy) * _env[3] + max(s.px(MIN_WEB_GAP), abs(oy) * s.px(SUN_CORRIDOR_FT))
    for attempt in range(7):
        if __debug__:
            OPS["candidate@_seat_rank_rounds"] += 1
        if placed >= plan.spec.households:  # (a row's or a grown cluster's seating never calls this: see the caller)
            break
        s._seat_search["rounds"] = attempt + 1  # the rounds this roll needed (over 4 = the rescue ran); R2 reads it per map
        wlat, wdep = lat * (1.0 + 0.22 * attempt), dep * (1.0 + 0.16 * attempt)
        _kept: list[Pt] = []
        _standing: list[Pt] = [(h["x"], h["y"]) for h in s.M.get("houses", [])]
        if attempt < 4 and _standing:
            # A LATTICE MEASURED FROM THE ROW, NOT A STEP BEHIND WHOEVER STANDS IN FRONT (settlement-review, feature
            # 227). Offering each seat one step behind a STANDING house compounds: rank 2 is measured from rank 1,
            # which was measured from the row, and every refusal along the way shifts what follows it, so the cluster's
            # centroid walks away from the field round by round and the ranks stop being ranks. Kuwabata's cluster
            # ended 114 px off its polder and Sawada's resolved into eight pieces. The lateral positions still come
            # from the houses that stand - the cluster is as wide as it is - but the DEPTH of round k is the row's own
            # depth plus k steps, measured once from the seat, so a rank is where a rank should be and four rounds
            # reach exactly four steps back. A brick: the even rounds offer the midpoints between neighbors, the odd
            # rounds the seats straight behind.
            _a_of = lambda q: (q[0] - seat["cx"]) * ax + (q[1] - seat["cy"]) * ay  # noqa: E731 - the band's two coordinates, used here only
            _o_of = lambda q: (q[0] - seat["cx"]) * ox + (q[1] - seat["cy"]) * oy  # noqa: E731
            _along = sorted(_standing, key=_a_of)
            _row_out = min(_o_of(q) for q in (_row or _standing))  # the front row's own depth: `out` runs away from the field
            _depth = _row_out + _rank_step * (attempt + 1)

            def _seat_at(u: float, _d: float = _depth) -> Pt:
                return (seat["cx"] + ax * u + ox * _d, seat["cy"] + ay * u + oy * _d)

            _us = [_a_of(q) for q in _along]
            _ends = [(_along[0][0] - ax * BUNDLE_PITCH, _along[0][1] - ay * BUNDLE_PITCH), (_along[-1][0] + ax * BUNDLE_PITCH, _along[-1][1] + ay * BUNDLE_PITCH)]
            if attempt % 2 == 0:
                _cands = [_seat_at((p + q) / 2) for p, q in zip(_us, _us[1:], strict=False)]
                # the brick's outer half-seats grow the rank along the field by half a pitch each: with the full-pitch
                # ends, offered only when the back is refused (Mizuguchi's round strung to 4.5 with them in every round)
                _ends += [_seat_at(_us[0] - BUNDLE_PITCH / 2), _seat_at(_us[-1] + BUNDLE_PITCH / 2)]
            else:
                _cands = [_seat_at(u) for u in _us]
            _cands.sort(key=lambda q: math.hypot(q[0] - seat["cx"], q[1] - seat["cy"]))  # center-out, as every proposer here
            # FILL BEFORE YOU GROW (settlement-review, feature 227): a seat the front row could not take leaves a HOLE
            # in the row, and the ranks - proposed behind the houses that did stand - carry the hole backward through
            # the whole cluster. Inashiro shipped a 211 px gap in its row and read as three pieces (components
            # [10, 4, 1] at a 165 px link) on a map whose form is nucleated. So the first rank round offers the
            # midpoints of the row's own over-wide gaps AT THE ROW'S OWN DEPTH, ahead of anything behind it.
            if attempt == 0:
                _cands = [((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) for p, q in zip(_along, _along[1:], strict=False) if math.dist(p, q) > BUNDLE_PITCH * 1.45] + _cands
        else:
            # THE RESCUE offers the along-the-field seats first - a pitch beyond each end of the standing rank, and the
            # brick's outer half-seats behind it - then the old cloud over the widened band; a quota the ranks could not
            # seat (cohort seed 25: 19 of 20 once the ends left the ordinary rounds) is seated where the ground is
            _ends = []
            _cands = []
            if _standing:
                _along = sorted(_standing, key=lambda q: (q[0] - seat["cx"]) * ax + (q[1] - seat["cy"]) * ay)
                _cands = [(_along[0][0] - ax * BUNDLE_PITCH, _along[0][1] - ay * BUNDLE_PITCH), (_along[-1][0] + ax * BUNDLE_PITCH, _along[-1][1] + ay * BUNDLE_PITCH)]
                _cands += [
                    (_along[0][0] - ax * BUNDLE_PITCH / 2 + ox * _rank_step, _along[0][1] - ay * BUNDLE_PITCH / 2 + oy * _rank_step),
                    (_along[-1][0] + ax * BUNDLE_PITCH / 2 + ox * _rank_step, _along[-1][1] + ay * BUNDLE_PITCH / 2 + oy * _rank_step),
                ]
            want = plan.spec.households * 6 + 30
            for lx, ly in s.cluster_seeds(plan.cluster_shape, 0.0, 0.0, wlat, wdep, want, rng, record=False):
                ly = -wdep + (ly + wdep) * 0.75  # the cloud leans toward the field (feature 133)
                _cands.append((seat["cx"] + ax * lx + ox * ly, seat["cy"] + ay * lx + oy * ly))
        _before_round = placed
        # THE ENDS GO THROUGH THE SAME BODY (feature 227): they are offered only after a round that seated nothing
        # behind - the cluster grows along the field only when its back is refused - but a second loop of its own
        # meant a second copy of the dedupe and the jitter, which is how two rules drift apart.
        _offered, _along_the_field = _cands, False
        while True:
            # THE ROUND'S SEATS JITTERED, THEN OFFERED AT ONCE (feature 297, FR-001, plan B1): one region read for the list
            _jittered = [(_q[0] + ax * (s._hjit(_q[0], _q[1], 13.0) - 0.5) * BUNDLE_PITCH * 0.2, _q[1] + ay * (s._hjit(_q[0], _q[1], 13.0) - 0.5) * BUNDLE_PITCH * 0.2) for _q in _offered]
            _region = getattr(s, "_seat_region", None)
            _in = _region.offer(_jittered) if _region is not None else [True] * len(_jittered)
            for (_sx4, _sy4), _held in zip(_jittered, _in, strict=True):
                if placed >= plan.spec.households:
                    break
                if not _held:
                    continue
                # A PITCH IS A SPACING, NOT A RULING (settlement-review, feature 227: 11 of Mizuguchi's 12 houses fell in
                # one 10 px bucket of nearest-neighbor distance, where the hand-packed maps spread over three). The seat is
                # nudged along the band by up to a tenth of a pitch, from the map's own position hash - enough to break the
                # modal spike, far too little to move a rank or to reopen a gap the round above just filled.
                if math.hypot(_sx4 - seat["cx"], _sy4 - seat["cy"]) > bound and attempt >= 4:  # out of the band
                    continue
                if any(math.hypot(_sx4 - kx, _sy4 - ky) < BUNDLE_PITCH * (0.5 if attempt < 4 else 0.3) for kx, ky in _kept) or any(
                    math.hypot(_sx4 - h["x"], _sy4 - h["y"]) < BUNDLE_PITCH * 0.5 for h in s.M.get("houses", [])
                ):
                    continue  # the same guess again
                _kept.append((_sx4, _sy4))
                # ...AND A RANK IS NOT A SURVEYED LINE EITHER (settlement-review of Mizuguchi, feature 261): with the depth
                # exact, 11 of its 12 houses stood on four rows within 5 ft and three columns within 3 ft - a lattice, where
                # the record's nucleated village is houses gathered irregularly (kaison-jawiki) and main's roll of the same
                # map spread its rows by 24 and 78 ft. A rank seat stands up to half of `RANK_DEPTH_JITTER` of a pitch nearer
                # to or further from the field, from the same position hash; the placer still holds the lane room and the sun
                # corridor, and the exact seat is offered where the jittered one is refused, so no household is lost to it.
                # (Outward only was tried first: the last rank stands against the band's outer edge, the placer's computed move
                # pulled every jittered seat back to that one line, and Mizuguchi's back rank stood within 3 ft again.)
                # ...ONLY WHERE THE VILLAGE GREW BY ACCRETION. The record gives two forms and rolls between them per map
                # (research/contents.json#ways "How our maps draw village lanes"): a back lane implies PLANNING - the framework laid
                # out at once and the plots regular - and alleys off a spine imply ACCRETION, each household cutting its own way,
                # the result irregular. So the ranks of a `back_lane` hamlet stay regular and an `alleys` hamlet's are taken off
                # the line. (Jittering every form was tried first: each amplitude re-laid all five maps into a new draw, and 0.15,
                # 0.18 and 0.25 each tipped Inashiro's rolled crescent under round's ceiling - a knob that moves which map fails.)
                _dj = (s._hjit(_sx4, _sy4, 14.0) - 0.5) * BUNDLE_PITCH * RANK_DEPTH_JITTER if attempt < 4 and not _along_the_field and plan.lane_web == "alleys" else 0.0
                for _tx, _ty in ((_sx4 + ox * _dj, _sy4 + oy * _dj), (_sx4, _sy4)) if _dj != 0.0 else ((_sx4, _sy4),):
                    if _offer_seat(s, _tx, _ty) and s.try_place(_tx, _ty, "plain"):
                        placed += 1
                        _cloud_placed += 1
                        break
            if _along_the_field or not (attempt < 4 and _standing and placed == _before_round and placed < plan.spec.households):
                break
            _offered, _along_the_field = _ends, True
    return placed, _cloud_placed


# ---- STAGE 6: what stands among the houses ------------------------------------------------------
