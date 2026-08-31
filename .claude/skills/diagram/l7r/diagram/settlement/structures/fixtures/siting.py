"""Split from settlement/structures/fixtures.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from typing import TYPE_CHECKING

from ..._geom import (
    Pt,
    point_in_poly,
    seg_dist,
    segments_cross,
    street_runs,
    way_beds,
)
from ..._knobs import KOSATSUBA_MARKER_MIN_PX, PUNISHMENT_SPOT_FT, resolve_knob
from ._helpers import CAPTION_LANE_TARGET_FT, KOSATSUBA_ANCHOR_BAND_FT, KOSATSUBA_VERGE_FT, kosatsuba_affordances, kosatsuba_anchor

if TYPE_CHECKING:
    from ...core import Settlement


class FixtureSitingMixin:
    def fixture_clear_of_water(self: Settlement, x: float, y: float, half: float) -> bool:  # type: ignore[misc]
        """Does a point fixture of half-diagonal `half` stand clear of every watercourse?

        THE VERGE PROBES BYPASS THE WATER CLEARANCE, and this buys it back explicitly. A verge-hugging
        fixture must probe with `_fits(..., corridors=False)` - the corridor test is a HOUSE setback
        from the tread, and applying it would refuse every verge there is - but `corridors=False` also
        switches off the watercourse clearance bundled into the same test, so the probe will happily
        seat a board in a stream. Cohort seed 13 did exactly that (`features_do_not_overlap` on
        ('kosatsuba', 'streams') plus `no_structure_on_stream`) once a homestead re-pack changed which
        verges were free: the board sat at (715, 517) on a 7 px stream, INSIDE the house cloud, so the
        hamlet tier's outside-the-cloud re-seat never even looked at it.

        ONE predicate, two callers - `place_kosatsuba` here and `hamletgen.stage_notice`'s re-seat,
        which faces the identical problem for the identical reason. Fixing only the caller that
        happened to fail would have left the other seating boards in water on the next re-roll.

        Reads the DRAWN courses (`drawn_channels`) as well as the recorded ones, because the filleted
        stroke is what a reader sees and what the overlap matrix measures.

        INDEXED (feature 138): `place_kosatsuba` asked this 17,407 times on one polder, each call walking
        all ~720 water segments - 12.5 million `seg_dist`. The segments are filed once in a grid (rebuilt
        when any of the four lists changes length, the same rule `_water_obstacles` uses) with each
        segment's own half-width; a probe measures only its cell's segments. Same predicate, same answer."""
        from l7r.diagram.settlement._geom.water_index import water_index

        return water_index(self).clear(x, y, half)

    def caption_lane_clearance(self: Settlement, qx: float, qy: float, chw: float, size: float = 8.0) -> float:  # type: ignore[misc]
        """Least distance from a caption's BOX to any lane's tread EDGE (negative = standing on it).

        Shared deliberately by the notice board's seat search and by `place_kosatsuba`'s siting
        preference, so the two cannot drift: the siter must rank a board position by the same measure
        the seat search will later optimize, and gate 0617 reads. Every time this quantity has been
        re-derived at a second call site in this file it has come back subtly different - the
        centerline instead of the edge, an axis-aligned box instead of the rotated quad - so it is a
        method now rather than a third closure."""
        # THE WHOLE BOX, NOT FIVE POINTS ON IT. Sampling four corners plus the center is exact against
        # a STRAIGHT tread and quietly wrong against a curved one: a caption spanning a CONCAVE bend
        # can have all five samples clear while the middle of its top or bottom EDGE crosses the arc.
        # Predicted here when the lane skeleton gained curvature, then observed - cohort seed 37 on the
        # architecture session's tree, a caption 2 ft from a tread that this method had scored clear.
        # So the measure is now segment-to-RECTANGLE: zero if the tread enters the box at all, else the
        # least distance between the tread and any of the box's four edges.
        #
        # AND THE BOX IS THE ONE THE TEXT ACTUALLY OCCUPIES. The old +/-5 was symmetric about the
        # ANCHOR, but a caption's record runs from ascent (0.8 x size) ABOVE the anchor to descender
        # (0.25 x size) below - so the old box under-reached the top by 1.4 px and over-reached the
        # bottom by 3. Two different boxes for one caption is how this family of bug keeps arriving.
        _y0, _y1 = qy - 0.80 * size, qy + 0.25 * size
        _x0, _x1 = qx - chw, qx + chw
        _edges = (((_x0, _y0), (_x1, _y0)), ((_x1, _y0), (_x1, _y1)), ((_x1, _y1), (_x0, _y1)), ((_x0, _y1), (_x0, _y0)))
        _best = 1e9
        for _lane in self.M.get("lanes") or []:
            _pts = _lane.get("pts") or []
            _lhalf = float(_lane.get("w") or 3) / 2.0
            for _i in range(len(_pts) - 1):
                _a, _b = _pts[_i], _pts[_i + 1]
                if (_x0 <= _a[0] <= _x1 and _y0 <= _a[1] <= _y1) or (_x0 <= _b[0] <= _x1 and _y0 <= _b[1] <= _y1):
                    return -_lhalf  # the tread's own centerline is inside the caption box
                _d = 1e9
                for _p, _q in _edges:
                    if segments_cross(_a, _b, _p, _q):
                        _d = 0.0
                        break
                    _d = min(_d, seg_dist(_p[0], _p[1], _a, _b), seg_dist(_q[0], _q[1], _a, _b), seg_dist(_a[0], _a[1], _p, _q), seg_dist(_b[0], _b[1], _p, _q))
                _best = min(_best, _d - _lhalf)
        return _best

    def place_kosatsuba(self: Settlement, label: str = "notice board") -> Pt | None:  # type: ignore[misc]
        """AUTO-SITE the settlement kosatsuba on a lane/road verge at the busiest clear node -
        the village/hamlet tiers' procedural sibling of the town/city hand placement (GM
        2026-07-24: EVERY settlement tier carries the board; the ofuregaki circulars reached
        the peasantry through it via the settlement's one required-literate reader - the
        headman, or a hamlet's senior farmer answering to the village headman - and officials
        also read notices aloud, so even a 50-inhabitant hamlet's board works). Deterministic:
        draws NO RNG, so calling it inside `roll_village` cannot perturb a rolled map's seed
        stream. Reads the SAME manifest route fields the validator's siting checks read (the
        dev-loop same-source doctrine): MAIN ways only (`roads`/`M['road']` + `main: True`
        town streets - kosatsuba_on_a_main_way, GM 2026-08-02) when the map declares any,
        else the whole network (`M['lane']` + `M['lanes']` + `town_streets`), and probes
        candidate verge spots with `_fits`, scoring for the most dwellings within ~260 px
        (siting is a TRAFFIC decision - the state talks at everyone who passes) while
        hugging the verge. Call LAST - after the crop, not before it (GM 2026-08-29). This said
        "BEFORE the crop, so the frame contains the board", which inverted the dependency: the
        board is sited against `meta.view` now, so the frame constrains the board rather than the
        board holding the frame open (`crop_not_held_open_by_one_feature`). No-op under meta(kosatsuba=False); returns the spot, or
        None when no verge inside the validator's ~60-real-ft siting band fits (the
        settlement-tier check would then fire - place by hand or widen the lane network)."""
        if not self.M["meta"].get("kosatsuba", True):
            return None
        ftpx = float(self.M["meta"].get("ftpx") or 1)
        lim = 60.0 / ftpx  # kosatsuba_by_the_road: ~60 REAL feet from a route, in px
        # probe with the DRAWN marker box, not the true footprint (village grain floors the glyph
        # to ~11x4.6 px - see kosatsuba): the spot has to hold the pixels that get drawn there
        w = max(self.px(12), KOSATSUBA_MARKER_MIN_PX)
        h = w * 5 / 12
        # (pts, tread width) per route; road/lane manifest fields carry no width, so assume
        # a generous tread for the bed-avoidance test below.
        # MAIN WAYS ONLY, where the map declares any (GM 2026-08-02, from Ubame: the siter put
        # the board a legal 49 ft off a side lane while the high street ran 200 ft away - "it
        # should be along the main road, in order to be more noticed"). The candidate tiers
        # mirror kosatsuba_on_a_main_way exactly (the same-source doctrine): every road and
        # every main: True town street is a MAIN way, and when the map has at least one, ONLY
        # main-way verges are sampled - a side lane's busiest node is still a side lane, so
        # scoring must never see it. A map with no declared hierarchy (village/hamlet lane
        # webs, towns whose streets are all unflagged) falls back to the whole network, where
        # the busiest-node scoring below stands in for "main". The fallback still needs TOWN
        # STREETS TOO: this probe was written for the lane/lanes tiers, and the omission was
        # invisible until Hirameki - no road, no lanes, all town_streets - gave it not one
        # candidate seat and it returned None (GM 2026-07-27).
        routes: list[tuple[list[Pt], float]] = []
        if self.M.get("road"):
            routes.append(([(p[0], p[1]) for p in self.M["road"]], 18.0))
        routes.extend(([(p[0], p[1]) for p in r["pts"]], 18.0) for r in (self.M.get("roads") or [])[1:])
        routes.extend(([(p[0], p[1]) for p in st["pts"]], float(st.get("w", 18))) for st in self.M.get("town_streets") or [] if st.get("main"))
        if not routes:
            # A ROUTE CARRIES ITS OWN WIDTH, AND THIS BLOCK USED TO GIVE THEM ALL THE SAME ONE (feature
            # 134 T50, 2026-08-29). `street_runs` returns EVERY drawn lane, and they were all added at a
            # nominal 8 ft - so the seater measured the tread edge 4 ft from the centerline on a lane
            # that is 3 or 5 ft wide, and placed the board `(8 - w) / 2` too far out while believing it
            # had put it exactly on the verge. Gate seed 44's board landed at 12.5 ft from a 5 ft lane's
            # centerline - which is 6 (the verge) + 4 (half of the imagined 8) + 2.5 (half the board),
            # to the foot - and `kosatsuba_by_the_road` measures against 12.0 and refused it.
            #
            # It also quietly undid the rule the note below states. `_main` exists to keep the state's
            # notice off a SERVICE lane, and this loop had already put every web lane into `routes`
            # before that filter ran, so the filter decided nothing. The per-lane extend below covers
            # exactly the same ways with their real widths, so this is now only the last-ditch case
            # where the manifest has runs but no lane records to read a width from.
            if not (self.M.get("lanes") or []):
                for _st in street_runs(self.M):  # every lane; `M["lane"]` is only the last one drawn
                    routes.append((_st, 8.0))
            # A SERVICE LANE IS NOT A PLACE TO POST THE STATE'S NOTICE. The fallback takes the whole
            # network when no way declares itself main, which a hamlet never does - so when the lane
            # web arrived it put ~1,000 ft of 3 ft footpaths into the candidate list on equal footing
            # with the 5 ft spine, and the board re-seated onto one: a settlement-review measured it
            # 34.9 ft off the spine where it had been 9.0, now facing a way the engine itself calls
            # SERVICE. This function's own docstring already states the rule it was breaking - "a
            # side lane's busiest node is still a side lane, so scoring must never see it" - and
            # `web` is exactly the hierarchy flag the hamlet tier lacked. Web lanes are used only if
            # there is nothing else to stand beside.
            _ways = self.M.get("lanes") or []
            # TRIED AND REVERTED (feature 140, 2026-08-28): admitting every web lane as a route on a hamlet, to let the
            # board reach the frontage. It moved nothing on Inashiro - the frontage has no verge seat that `_fits` a
            # board after the re-seat (4 of 60 probes around the houses fit), so the choice of routes was never the
            # constraint; the room is. Recorded so the lever is not pulled again (`research.md` R6).
            _main = [ln for ln in _ways if not ln.get("web")] or _ways
            routes.extend(([(p[0], p[1]) for p in ln["pts"]], float(ln.get("w", 8))) for ln in _main)
            routes.extend(([(p[0], p[1]) for p in st["pts"]], float(st.get("w", 18))) for st in self.M.get("town_streets") or [])
        spots = [(b["x"], b["y"]) for b in self.M["houses"]] + [(b["x"], b["y"]) for b in self.M["buildings"]]

        beds = way_beds(self.M)  # EVERY way bed, not just the routes candidates were sampled from

        def off_every_bed(x: float, y: float) -> bool:
            # the board hugs the verge, so the lane corridor's no-build clearance (a HOUSE
            # setback: homesteads must not crowd the tread) is deliberately bypassed
            # (_fits corridors=False) - but the board must still stand off the TREAD of
            # every route, including ones it was not sampled from (a junction spot offset
            # from lane A can land on lane B, or on a town street or alley this tier's
            # candidate list does not carry at all - see way_beds)
            return all(seg_dist(x, y, bp[k], bp[k + 1]) >= bhw + h / 2 + 3 for bp, bhw in beds for k in range(len(bp) - 1))

        tw_lab = self.label_caption_hw(label, 8.0) if label else 0.0  # the caption half-width the seat must also hold, as RECORDED
        kb_boxes = self.label_blockers("kosatsuba")  # built once: the probe tests many seats against the same map
        _siting = str((self.M.get("meta") or {}).get("kosatsuba_siting") or "frontage")
        _wells = [(float(_w["x"]), float(_w["y"])) for _w in (self.M.get("wells") or []) if "x" in _w]
        cands: list[tuple[int, float, float, float, float, int | None, float]] = []  # (busy, score, x, y, rot, label_above|None, gap from tread edge to board edge)
        for pts, _rw in routes:
            for i in range(len(pts) - 1):
                (ax, ay), (bx, by) = pts[i], pts[i + 1]
                seg = math.hypot(bx - ax, by - ay)
                if not seg:
                    continue
                ux, uy = -(by - ay) / seg, (bx - ax) / seg  # verge normal
                # long axis ALONG the route: the board's face is broadside to the traffic that
                # reads it, never edge-on (kosatsuba_faces_the_road; see kosatsuba's docstring)
                rot = math.degrees(math.atan2(by - ay, bx - ax))
                for t in range(int(seg // 12) + 1):
                    f = t * 12 / seg
                    mx, my = ax + (bx - ax) * f, ay + (by - ay) * f
                    for side in (1.0, -1.0):
                        off = _rw / 2 + h / 2 + 4
                        while off <= lim:
                            x, y = mx + ux * off * side, my + uy * off * side
                            if off_every_bed(x, y) and self.fixture_clear_of_water(x, y, math.hypot(w, h) / 2) and self._fits(x, y, w, h, corridors=False):
                                # BUSY IS WHERE THE FEET ARE (feature 140's Inashiro review, 2026-08-28): counting dwellings within 260 px
                                # could not tell the frontage (11 within 150 ft) from the exit throat (5 within 150 ft) - both had ~16-21
                                # within 260 - and a re-roll sat the board at the throat. The near count is weighted double.
                                busy = sum(1 for sx, sy in spots if math.hypot(x - sx, y - sy) < 260) + 2 * sum(1 for sx, sy in spots if math.hypot(x - sx, y - sy) < 150)
                                # WHERE THE BOARD STANDS IS A KNOB (feature 152 T21, constitution XII).
                                # The takafuda stood at crossroads and bridgeheads AND at the village
                                # well - both attested, so this is two supportable answers rather than one
                                # right one, and picking either permanently throws away a way two hamlets
                                # can honestly differ. `frontage` is the busiest built ground, which is
                                # what this score has always measured. `waterside` is the drawing-water
                                # place: a settlement-review measured Mizuguchi's board at the wellhead,
                                # 7 of 12 households within 250 ft against 11 of 12 at the frontage
                                # optimum, and called it defensible - which it is, on the other answer.
                                if _siting == "waterside" and _wells:
                                    _dw = min(math.hypot(x - wx2, y - wy2) for wx2, wy2 in _wells)
                                    busy += 14 if _dw < 40.0 else (8 if _dw < 90.0 else 0)
                                # THE CAPTION IS PART OF THE SEAT (GM 2026-07-27). The glyph is 11 px
                                # and fits almost anywhere; its caption does not, and the busiest
                                # frontage is exactly where there is least room for one - so a siter
                                # that hunts for ground big enough to hold BOTH walks away from the
                                # traffic and out to the quiet end of the road, which is how Ubame's
                                # board came to stand across the bridge from its own town.
                                lab = 0 if self.label_seat_clear(x, y + h / 2 + 11, tw_lab, 8.0, kb_boxes) else (1 if self.label_seat_clear(x, y - h / 2 - 11, tw_lab, 8.0, kb_boxes) else None)
                                cands.append((busy, busy * 10 - off / 3, x, y, rot, lab, off - _rw / 2 - h / 2))  # last: the gap from tread edge to board edge
                            off += 5.0
        if not cands:
            return None
        # ROADSIDE FIRST (GM 2026-08-26): at the lane tiers, if any seat stands within KOSATSUBA_VERGE_FT
        # of a tread, only those seats compete - the caption and traffic preferences below then choose
        # AMONG roadside seats instead of trading the roadside away for a clearer caption.
        _scale = str((self.M.get("meta") or {}).get("scale") or "")
        if _scale in ("hamlet", "village"):
            roadside = [c for c in cands if c[6] <= KOSATSUBA_VERGE_FT / ftpx + 1e-6]
            if roadside:
                cands = roadside

        # THE PLACEMENT IS A KNOB, NOT ONE OBJECTIVE (feature 154, GM 2026-08-29). The record attests
        # several sites for the board and this siter used to know one of them - the busiest node -
        # so every hamlet answered the same way a question the record answers three ways, and Sawada's
        # board ended up 9.0 ft off an 81.7 ft DEAD-END SPUR (7 of 19 dwellings within 250 ft against
        # 13 at the busiest stretch). A cul-de-sac head is not a center, an entrance or an official's
        # gate; it is outside what the record attests, not at one end of a supported range.
        #
        # Principle XII: where the record supports distinct FORMS, the rule is a knob rolled from the
        # map's own seed. `_kosatsuba_seat_ok` carries the value space, the evidence and the reason two
        # attested placements are withheld at these tiers.
        #
        # TIER-SCOPED (FR-009), and this is a requirement rather than an assumption because the code
        # says so: `legacy-hand-authored-pool/towns/hirameki/hirameki.gen.py` calls `place_kosatsuba()`, so a TOWN comes through here.
        # Towns and cities keep the traffic objective they were sited under.
        placement = "center"
        if _scale in ("hamlet", "village"):
            placement = str(resolve_knob("kosatsuba_seat", int(self.seed), kosatsuba_affordances(self.M), (self.M["meta"].get("knobs") or {})))
        self.M["meta"]["kosatsuba_seat"] = placement
        anchor = kosatsuba_anchor(self.M, placement)
        if anchor is not None:
            # AN ANCHORED PLACEMENT CHOOSES THE GROUND; the preferences below then choose among the
            # seats on it. `center` returns no anchor on purpose - its objective IS the traffic count
            # already computed, which measures where people ARE rather than where the middle is.
            _near = min(math.hypot(c[2] - anchor[0], c[3] - anchor[1]) for c in cands)
            _band = KOSATSUBA_ANCHOR_BAND_FT / ftpx
            cands = [c for c in cands if math.hypot(c[2] - anchor[0], c[3] - anchor[1]) <= _near + _band] or cands
        # ON THE TRAFFIC IS THE RULE; A FITTING CAPTION IS ONLY THE PREFERENCE WITHIN IT. Scoring the
        # caption as a flat bonus large enough to outrank traffic was tried first and re-committed the
        # original sin at one remove: where no seat on a tight village frontage has a clear caption,
        # EVERY caption-clear seat is out in the fields, so all three village boards walked off the
        # frontage and their captions ran off the cropped frame. Open ground for a caption is abundant
        # exactly where nobody is - the same trap as open verge for the board. So the busiest node
        # sets a floor (60% of the best count available), and the caption chooses only among the seats
        # that already stand on the traffic. A board with nowhere to put its caption is still placed,
        # so labels_clear_of_other_buildings reports it rather than the siter hiding it.
        # ...and the traffic floor applies only where traffic is the objective. Keeping it under an
        # anchored placement would drag the board back toward the busy node the anchor just declined.
        floor = 0.0 if anchor is not None else 0.6 * max(c[0] for c in cands)

        # A BOARD POSITION IS ONLY AS GOOD AS THE CAPTION IT CAN CARRY (cohort seed 14, 2026-08-20).
        # `lab` above asks only whether the two DEFAULT seats clear STRUCTURES. It never asks about
        # lanes - so the siter happily chose a board that is hemmed: instrumented on seed 14, all
        # eleven structure-clear seats of the forty-eight sit west and south where the lanes run
        # (best clearance 1.0 ft against a 2 ft bar) while every seat with real clearance - 14.3,
        # 14.2, 8.6, 5.8 ft - is blocked by a building. No seat search can fix that, because the
        # board is in the wrong PLACE to be captioned, and nine attempts inside the search is what it
        # cost to see that.
        #
        # So feasibility joins the ranking, ahead of the old structure-only term. The probe is the
        # NEAR RING (four axes and four diagonals at zero standoff) rather than the full
        # forty-eight, and that is sound because the full candidate set is a SUPERSET of the ring:
        # near-ring-feasible implies search-feasible, which is exactly the one-way guarantee a
        # PREFERENCE needs. It is 8 probes per board position against the 2 already spent, and it
        # cannot promise a seat where the ring finds none - it only stops the siter preferring a
        # position that demonstrably has one over a position that demonstrably does not.
        def _sitable(_x: float, _y: float, _hw: float, _hh: float) -> bool:
            _chw2 = max(10.0, len(label) * 8 * 0.28) if label else 0.0
            if not label:
                return True
            # THE RING MUST BE A SUBSET OF WHAT THE SEARCH ACTUALLY TRIES, or the one-way guarantee
            # above is worthless. The first cut used 45-degree diagonals (0.7, 0.7) while the seat
            # search's annulus runs 30/60/120/150/210/240/300/330 - so a board could be ranked
            # sitable on a seat the search never offers, and seed 14 did not move. These are exactly
            # the twelve zero-standoff members of `_cands`: four axes plus those eight bearings.
            _ring = [(0.0, 1.0), (0.0, -1.0), (1.0, 0.0), (-1.0, 0.0)]
            _ring += [(math.cos(math.radians(_a)), math.sin(math.radians(_a))) for _a in (30, 60, 120, 150, 210, 240, 300, 330)]
            for _dx, _dy in _ring:
                _qx = _x + (_hw + _chw2 + 8.0) * _dx
                _qy = _y + (_hh + 11.0) * _dy
                if self.label_seat_clear(_qx, _qy, tw_lab, 8.0, kb_boxes) and self.caption_lane_clearance(_qx, _qy, _chw2) >= CAPTION_LANE_TARGET_FT:
                    return True
            return False

        _b, _s, x, y, rot, lab, _gap = max((c for c in cands if c[0] >= floor), key=lambda c: (_sitable(c[2], c[3], w / 2, h / 2), c[5] is not None, c[1]))
        # `lab` NO LONGER DECIDES THE CAPTION'S SIDE, and that was the last thing keeping two cohort
        # seeds notched. It is computed above by testing `label_seat_clear` at the DEFAULT distance
        # only - `y +/- h/2 + 11` - so it reports "below is blocked" for a board whose below seat is
        # blocked at 11 px and perfectly clear at 35. Passing that verdict on as `label_above` forced
        # the caption to the far side and skipped the lane search entirely; instrumented on seed 14,
        # the seat it forced had -1.2 ft of lane clearance while an outward below seat had 7.8.
        #
        # `kosatsuba` now asks the structure question itself, of every candidate in its outward walk,
        # so the narrow precomputed verdict is strictly worse information. `lab` is still used ABOVE,
        # to prefer a BOARD POSITION where some caption seat exists at all - that is a different
        # question and a good one. The parameter stays on `kosatsuba` for external callers who know
        # something the manifest does not (the gate-adjacent case its docstring describes).
        # RECORD WHAT WAS DRAWN, NOT ONLY WHAT WAS ROLLED (settlement-review, feature 154). Two knobs
        # decide this seat and they can disagree: `kosatsuba_siting` (feature 152 - frontage or the
        # drawing-water place) bids through the `busy` score, while `kosatsuba_seat` (feature 154 -
        # center, entrance or the official's gate) culls the candidates to the ground around its
        # anchor. Where the anchor's ground holds no wellhead, every surviving candidate earns the
        # waterside bonus of zero, so the siting knob decides nothing - and the manifest went on
        # saying `waterside` anyway. Measured on Kashikawa: `kosatsuba_siting: waterside` on a board
        # 276 ft from the nearest of three wells, which the interactive page would have told a
        # clicking reader was the drawing-water place.
        #
        # That is this feature's own defect one field over - a placement recorded and not drawn - so
        # the fix is the same: state the achieved fact beside the rolled one. Neither knob is
        # overwritten; a reader can see what was asked for and what the ground allowed.
        # A MEASUREMENT, NOT A SECOND LABEL. Recording a drawn "waterside"/"frontage" was tried and
        # discarded in the same breath: a board that happens to land 60 ft from a well did not choose
        # the drawing-water place, and labelling it `waterside` would assert an intent the seat never
        # had - the same overstatement this field exists to catch. The distance claims nothing and
        # settles the question either way: on the five scripted hamlets the rolled siting and the
        # ground disagree on four, which is what says the two knobs are not composing.
        if _wells:
            self.M["meta"]["kosatsuba_well_ft"] = round(min(math.hypot(x - _wx3, y - _wy3) for _wx3, _wy3 in _wells) * float(self.M["meta"].get("ftpx") or 1), 1)
        self.kosatsuba(x, y, rot, label=label)
        return (x, y)

    def place_punishment_spot(self: Settlement, label: str | None = "punishment ground", label_xy: Pt | None = None) -> Pt | None:  # type: ignore[misc]
        """AUTO-SITE the punishment ground on a street verge at the busiest clear node - the notice
        board's sibling, and for the same reason: both institutions are sited by FOOT TRAFFIC, so
        both want the same probe rather than a hand-picked rect. (Hand rects were tried first on
        three maps and all three failed `punishment_spot_by_the_traffic` the same way: `open_seat`
        ties toward the rect's CENTER, which is the open ground behind the frontage, precisely where
        this feature must not be.) Deterministic - draws no RNG.

        Reads the SAME manifest route fields the validator reads (the dev-loop same-source doctrine),
        including `town_streets`, which the board's village-tier probe does not need. Keeps the spot
        inside the rampart where there is one - the display faces the town, not the road out; that is
        the execution ground's job. No-op under meta(punishment_spot=False). Returns the spot, or
        None when no verge fits (the presence check then fires - place by hand)."""
        if not self.M["meta"].get("punishment_spot", True):
            return None
        ftpx = float(self.M["meta"].get("ftpx") or 1)
        lim = 60.0 / ftpx  # punishment_spot_by_the_traffic: ~60 REAL feet from a street
        w, h = self.px(PUNISHMENT_SPOT_FT[0]), self.px(PUNISHMENT_SPOT_FT[1])
        routes: list[tuple[list[Pt], float]] = []
        if self.M.get("road"):
            routes.append(([(p[0], p[1]) for p in self.M["road"]], float(self.M.get("road_width") or 18)))
        routes.extend(([(p[0], p[1]) for p in st["pts"]], float(st.get("w", 18))) for st in self.M.get("town_streets") or [])
        routes.extend(([(p[0], p[1]) for p in ln["pts"]], float(ln.get("w", 8))) for ln in self.M.get("lanes") or [])
        if not routes:
            return None
        wall = self.M.get("wall")
        spots = [(b["x"], b["y"]) for b in self.M["houses"]] + [(b["x"], b["y"]) for b in self.M["buildings"]]
        beds = way_beds(self.M)  # see way_beds: EVERY bed, including the alleys and the ring road
        # this list does not sample candidates from - a display bypasses the lane CORRIDOR
        # deliberately (it is a house setback), never the roadbed itself

        def off_every_bed(x: float, y: float) -> bool:
            return all(seg_dist(x, y, bp[k], bp[k + 1]) >= bhw + h / 2 + 3 for bp, bhw in beds for k in range(len(bp) - 1))

        best: tuple[float, float, float, float] | None = None  # (score, x, y, rot)
        # ...and the best seat that is ALSO out from under the captions already on the map. A
        # PREFERENCE, not a filter (2026-08-08): landing under someone else's caption is a real
        # defect - Minami's ground auto-sited onto the burakumin quarter's label when a reflow moved
        # the busiest node 24px north - but it is the caption's problem to solve, and refusing the
        # seat outright would let a densely-captioned quarter drive the whole probe to None, i.e.
        # turn "the label wants moving" into "the city has no punishment ground at all". So: take a
        # clear seat when one exists at any score, and fall back to the busiest seat when none does.
        best_clear: tuple[float, float, float, float] | None = None
        for pts, _rw in routes:
            for i in range(len(pts) - 1):
                (ax, ay), (bx, by) = pts[i], pts[i + 1]
                seg = math.hypot(bx - ax, by - ay)
                if not seg:
                    continue
                ux, uy = -(by - ay) / seg, (bx - ax) / seg
                rot = math.degrees(math.atan2(by - ay, bx - ax))
                for t in range(int(seg // 12) + 1):
                    f = t * 12 / seg
                    mx, my = ax + (bx - ax) * f, ay + (by - ay) * f
                    for side in (1.0, -1.0):
                        off = _rw / 2 + h / 2 + 4
                        while off <= lim:
                            x, y = mx + ux * off * side, my + uy * off * side
                            if (not wall or len(wall) < 3 or point_in_poly(x, y, wall)) and off_every_bed(x, y) and self._fits(x, y, w, h, corridors=False):
                                busy = sum(1 for sx, sy in spots if math.hypot(x - sx, y - sy) < 260)
                                score = busy * 10 - off / 3
                                if best is None or score > best[0]:
                                    best = (score, x, y, rot)
                                if not self._under_a_caption(x, y, w, h, rot) and (best_clear is None or score > best_clear[0]):
                                    best_clear = (score, x, y, rot)
                            off += 5.0
        best = best_clear or best
        if best is None:
            return None
        _, x, y, rot = best
        if label and label_xy is None:
            # A verge-hugging feature's DEFAULT below-label lands on the frontage it hugs - that is
            # not bad luck, it is what "hugging the frontage" means, and it fired on all three maps.
            # So probe the label too: below, above, then left/right, first clear box wins.
            label_xy = self.clear_label_seat(x, y, w, h, label, skip_key="punishment_spots")
        self.punishment_spot(x, y, rot, label=label, label_xy=label_xy)
        return (x, y)
