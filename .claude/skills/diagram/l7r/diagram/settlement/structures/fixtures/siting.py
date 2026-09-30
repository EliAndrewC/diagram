"""Split from settlement/structures/fixtures.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from ....labels import Placement
from ..._geom import (
    Manifest,
    PointGrid,
    Pt,
    point_in_poly,
    seg_dist,
    seg_reach_index,
    street_runs,
    way_beds,
)
from ..._knobs import KNOBS, KOSATSUBA_MARKER_MIN_PX, PUNISHMENT_SPOT_FT
from ..captions import tree_crown_discs
from ._helpers import (
    KOSATSUBA_ANCHOR_BAND_FT,
    KOSATSUBA_HANDOVER_BAND_FT,
    KOSATSUBA_VERGE_FT,
    RouteReach,
    departure_routes,
    kosatsuba_affordances,
    kosatsuba_anchor,
    kosatsuba_handover,
)
from .board_seat import (
    KOSATSUBA_WAY_REACH_FT,
    PLACARD_KEEP_FT,
    BoardSeat,
    Proof,
    SiteEnv,
    WayFacing,
    board_caption_seat,
    board_in_view,
    choose_board,
    entrance_seat_ok,
    fallback_caption,
    resolve_seat,
    site_board,
    terminal_caption,
    under_placard,
)

if TYPE_CHECKING:
    from ...core import Settlement


def canopy_index(M: Manifest) -> PointGrid:
    """Every DRAWN tree crown on the map, filed so a seat probe can ask about the canopy once per candidate.

    THE CROWNS, NOT THE CLUMP BASES (settlement-review, feature 230 pass 13, on two maps independently). A grove
    records its clumps as bare points plus one nominal radius, and the first cut of this index filed those - which
    under-measures the ink by a wide margin, because a clump draws several overlapping crowns and each is jittered
    off the base. Measured over Sawada's 588 crowns: a crown's edge stands a median 16.3 ft and a p90 26.7 ft from
    its nearest clump base, against the 14 ft the nominal radius claims. So the board it was meant to keep in the
    open passed by ONE INCH on Sawada while the crown drawn from that clump covered the board's own center, and on
    Mizuguchi 44% of the plank's footprint was canopy pixels. `tree_crowns` is the flat (x, y, r) list the drawer
    writes as it paints, so this asks exactly what a reader sees.

    INDEXED, NOT SCANNED (constitution X clause 15): a hamlet draws 600-1,800 crowns and the board's verge probe
    tries thousands of seats. The grid prunes and the caller's own circle test decides, so the verdict is the
    linear scan's. The grove-clump fallback stays for a manifest with no crowns recorded - the six hand-built
    fixtures, and any caller asking before the groves are drawn."""
    grid = PointGrid()
    grid.extend([(x, y, r, x - r, y - r, x + r, y + r) for x, y, r in tree_crown_discs(M)])  # the one list the label index reads too
    return grid


def under_canopy(grid: PointGrid, x: float, y: float, half: float) -> bool:
    """Would a fixture of half-diagonal `half` seated here stand under a village grove's crowns?

    A NOTICE BOARD IN A WOOD IS A NOTICE NOBODY READS (settlement-review, feature 230 pass 12, on two maps
    independently). The board's caption has held a grove keep-out since 2026-08-16, and its GLYPH never has -
    so the plank could be buried while its name floated clear, which is what shipped: on Mizuguchi the nearest
    crown center stood 12.8 ft from the board with a 14 ft radius (10 clumps within 40 ft, 33 of 36 sample
    points around the glyph canopy green), and on Sawada a crown center stood 1.8 ft from it. Both boards had
    clear verge 18-30 ft away on the same lane; the seat search simply could not see the difference."""
    return any(math.hypot(x - float(it[0]), y - float(it[1])) < float(it[2]) + half for it in grid.near(x, y, half))


VERGE_FIRST = True
"""`place_kosatsuba` samples the verge band before the whole band (feature 284, FR-007); off only in the test that proves the
two give the same board."""

BOARD_ALONG_STEP_PX = 12.0
"""How far apart the board's candidate seats stand along a route. 24 was TRIED AND WITHDRAWN (feature 284, FR-007): the
coarser lattice left no approach seat inside the 20 ft band every departure passes (`KOSATSUBA_HANDOVER_BAND_FT`), so an
entrance board went up on the straggler lane, side-on to the track - the placement feature 261's settlement-review ruled out
(`test_an_entrance_board_stands_on_the_approach_and_not_on_a_straggler_at_its_join`). The board's costliest question, its
caption, is proved lazily instead (`board_seat.choose_board`), which moves no seat."""


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

        ONE predicate - `place_kosatsuba` is the one board siter since feature 287 deleted the frame
        stage's re-seat, which had the identical hole for the identical reason.

        Reads the DRAWN courses (`drawn_channels`) as well as the recorded ones, because the filleted
        stroke is what a reader sees and what the overlap matrix measures.

        INDEXED (feature 138): `place_kosatsuba` asked this 17,407 times on one polder, each call walking
        all ~720 water segments - 12.5 million `seg_dist`. The segments are filed once in a grid (rebuilt
        when any of the four lists changes length, the same rule `_water_obstacles` uses) with each
        segment's own half-width; a probe measures only its cell's segments. Same predicate, same answer."""
        from l7r.diagram.settlement._geom.water_index import water_index

        return water_index(self).clear(x, y, half)

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
        hugging the verge. Call LAST - after the crop, not before it (GM 2026-08-29): the
        board is sited against `meta.view`, so the frame constrains the board rather than the
        board holding the frame open (`crop_not_held_open_by_one_feature`). No-op under
        meta(kosatsuba=False); returns the spot, or None when no verge inside the ~60-real-ft
        siting band fits.

        EVERY BOARD RULE IS APPLIED HERE, ONCE (feature 287, labels L1-L4, L7, L11, L12, L14 - `board_seat.py`). A
        seat is a candidate only inside the view and off the title placard; it is kept only where the one placer seats
        its caption clean beside it (`board_caption_seat`); an `entrance` board only where every way out passes it; the
        `kosatsuba_seat` knob resolves over the placements the map can so site; and the caption's proved seat rides to
        the label phase and is drawn as proved. The frame stage's re-seat, a second siter restating these rules with
        four recorded drifts (features 154, 227, 230, 261), is deleted. Where no seat anywhere takes a board with a clean
        caption, the board is still posted by its way (plan D12, GM 2026-09-30: the clean caption is a preference): the
        caption steps down to one on a leader or in the key that clears every way (`terminal_caption`), then to the one
        placer's normal fallback (`fallback_caption`). The only map with no board is one with no roadside seat at all."""
        meta = self.M["meta"]
        if not meta.get("kosatsuba", True):
            return None
        ftpx = float(meta.get("ftpx") or 1)
        # probe with the DRAWN marker box, not the true footprint (village grain floors the glyph
        # to ~11x4.6 px - see kosatsuba): the spot has to hold the pixels that get drawn there
        w = max(self.px(12), KOSATSUBA_MARKER_MIN_PX)
        h = w * 5 / 12
        lane_tier = str(meta.get("scale") or "") in ("hamlet", "village")
        view = meta.get("view")
        frame = (view[0], view[1], view[0] + view[2], view[1] + view[3]) if view else None
        index = self.label_obstacles() if label else None  # the one placer's obstacles, indexed once for every candidate
        sampled: dict[tuple[Any, ...], list[BoardSeat]] = {}
        # everything a seat is tested against, built ONCE for the whole probe (constitution X clause 15; features 138, 278)
        env = SiteEnv(
            view,
            bed_segment_index(way_beds(self.M), h / 2 + 3),
            [(b["x"], b["y"]) for b in self.M["houses"]] + [(b["x"], b["y"]) for b in self.M["buildings"]],
            str(meta.get("kosatsuba_siting") or "frontage"),
            [(float(_w["x"]), float(_w["y"])) for _w in (self.M.get("wells") or []) if "x" in _w],
            canopy_index(self.M),
            WayFacing(self.M, KOSATSUBA_WAY_REACH_FT / ftpx + math.hypot(w, h)),
        )
        proved: dict[tuple[float, float, float], tuple[bool, Placement | None]] = {}

        def proof(c: BoardSeat) -> tuple[bool, Placement | None]:
            if (c.x, c.y, c.rot) not in proved:
                p = board_caption_seat(self.M, c.x, c.y, w / 2, h / 2, c.rot, label, index, frame) if label and index is not None else None
                proved[c.x, c.y, c.rot] = (not label or p is not None, p)
            return proved[c.x, c.y, c.rot]

        def sample(routes: list[tuple[list[Pt], float, bool]], verge_first: bool) -> list[BoardSeat]:
            return self._board_seats(routes, verge_first, w, h, ftpx, env, sampled)

        # THE CAPTION'S LATER STEPS (plan D12, GM 2026-09-30: the clean caption is a preference, never a reason for no
        # board): a caption on a leader or in the key that clears every way, then the one placer's normal fallback
        terminal: dict[tuple[float, float, float], Placement | None] = {}

        def lax(c: BoardSeat) -> tuple[bool, Placement | None]:
            assert index is not None  # a board with no caption proves every seat, so only a captioned one gets here
            if (c.x, c.y, c.rot) not in terminal:
                terminal[c.x, c.y, c.rot] = terminal_caption(self.M, c.x, c.y, w / 2, h / 2, c.rot, label, index, frame)
            return terminal[c.x, c.y, c.rot] is not None, terminal[c.x, c.y, c.rot]

        def loose(c: BoardSeat) -> tuple[bool, Placement | None]:
            assert index is not None
            return True, fallback_caption(self.M, c.x, c.y, w / 2, h / 2, c.rot, label, index, frame)

        # EVERY PLACEMENT THE MAP AFFORDS, each asked whether it can be SITED - in the siting band first, then (1) the whole
        # band with the web lanes admitted - before the knob is committed (labels L1, L4 fallback steps 1-2)
        afford = kosatsuba_affordances(self.M)
        values = KNOBS["kosatsuba_seat"].allowed(afford) if lane_tier else ["center"]
        pinned = meta.get("knobs") or {}
        chosen = site_board(values, [proof, lax, loose] if label else [proof], pinned.get("kosatsuba_seat"), lambda v, pf, widen: self._board_for(v, sample, pf, widen, ftpx, lane_tier), lane_tier)
        if not chosen:
            return None  # no roadside seat at all: the siter's answer wherever no verge fits
        placement = resolve_seat(int(self.seed), dict(afford), pinned, set(chosen)) if lane_tier else "center"
        unsitable = [v for v in values if v not in chosen]
        if unsitable:
            meta["kosatsuba_seat_unsitable"] = unsitable
        seat, cap = chosen[placement]
        meta["kosatsuba_seat"] = placement
        x, y = seat.x, seat.y
        # THE BOARD FACES THE WAY A READER SEES IT BY, which is the NEAREST one (`kosatsuba_faces_the_road`, labels L12): every
        # seat was turned to it as it was sampled (`WayFacing.turn`, the shared reading of "nearest") and a seat whose turned
        # board could not face it was refused there, so the seat's turn is the drawn one. The caption was proved at this same
        # turn (`board_caption_seat`).
        rot = seat.rot
        # RECORD WHAT WAS DRAWN, NOT ONLY WHAT WAS ROLLED (settlement-review, feature 154): `kosatsuba_siting` bids through
        # the traffic score while `kosatsuba_seat` culls the ground, and where the anchor's ground holds no wellhead the siting
        # knob decides nothing - so the achieved distance to the nearest well is stated beside the rolled knobs. A
        # measurement, not a second label: a board 60 ft from a well did not choose the drawing-water place.
        if env.wells:
            meta["kosatsuba_well_ft"] = round(min(math.hypot(x - wx, y - wy) for wx, wy in env.wells) * ftpx, 1)
        # THE PROVED SEAT RIDES TO THE LABEL PHASE only where the board is sited against the finished frame (the hamlet
        # pipeline, after the crop): a gen that draws on after its board lets the phase seat the caption against what it drew
        self.kosatsuba(x, y, rot, label=label, placement=cap if view else None)
        return (x, y)

    def _board_seats(  # type: ignore[misc]
        self: Settlement, routes: list[tuple[list[Pt], float, bool]], verge_first: bool, w: float, h: float, ftpx: float, env: SiteEnv, cache: dict[tuple[Any, ...], list[BoardSeat]]
    ) -> list[BoardSeat]:
        """Every candidate board seat along `routes` ((pts, tread width, is the approach)), each within
        `KOSATSUBA_WAY_REACH_FT` of its route (labels L11), off every way's bed, clear of water, fitting the ground (`_fits`),
        inside the view (labels L2) and off the title placard (labels L14). ROADSIDE FIRST (feature 284): with `verge_first`
        the verge band is sampled first, and only when it holds no seat is the whole band sampled, in the order it always
        was. Each route's seats are sampled once per siting (`cache`), since every placement asks the same routes."""
        out: list[BoardSeat] = []
        for verge_only in (True, False) if verge_first else (False,):
            if out:
                break
            for pts, rw, approach in routes:
                key = (tuple(pts), rw, approach, verge_only)
                if key not in cache:
                    cache[key] = self._route_seats(pts, rw, approach, verge_only, w, h, ftpx, env)
                out += cache[key]
        return out

    def _route_seats(self: Settlement, pts: list[Pt], rw: float, approach: bool, verge_only: bool, w: float, h: float, ftpx: float, env: SiteEnv) -> list[BoardSeat]:  # type: ignore[misc]
        """The candidate seats along one route (see `_board_seats`)."""
        lim = KOSATSUBA_WAY_REACH_FT / ftpx
        verge = KOSATSUBA_VERGE_FT / ftpx + 1e-6
        half = math.hypot(w, h) / 2
        out: list[BoardSeat] = []
        for i in range(len(pts) - 1):
            (ax, ay), (bx, by) = pts[i], pts[i + 1]
            seg = math.hypot(bx - ax, by - ay)
            if not seg:
                continue
            ux, uy = -(by - ay) / seg, (bx - ax) / seg  # verge normal
            # long axis ALONG the route: the board's face is broadside to the traffic that reads it, never edge-on
            # (kosatsuba_faces_the_road; see kosatsuba's docstring)
            rot = math.degrees(math.atan2(by - ay, bx - ax))
            for t in range(int(seg // BOARD_ALONG_STEP_PX) + 1):
                f = t * BOARD_ALONG_STEP_PX / seg
                mx, my = ax + (bx - ax) * f, ay + (by - ay) * f
                for side in (1.0, -1.0):
                    off = rw / 2 + h / 2 + 4
                    while off <= lim:
                        if verge_only and off - rw / 2 - h / 2 > verge:  # past the verge: the roadside rule would drop it
                            break
                        x, y = mx + ux * off * side, my + uy * off * side
                        # the board hugs the verge, so the lane corridor's no-build clearance (a HOUSE setback) is bypassed
                        # (_fits corridors=False) - but it still stands off the TREAD of every way (`way_beds`), out of the
                        # water, inside the view and off the title placard; the canvas top is its bottom (feature 261)
                        if (
                            board_in_view(env.view, x, y, w, h)
                            and not under_placard(self.M, x, y, w, h, PLACARD_KEEP_FT / ftpx)
                            and all(seg_dist(x, y, a, b) >= reach for a, b, reach, _x0, _y0, _x1, _y1 in env.beds.near(x, y) if _x0 <= x <= _x1 and _y0 <= y <= _y1)
                            and self.fixture_clear_of_water(x, y, half)
                            and self._fits(x, y, w, h, corridors=False, top=26.0)
                            # TURNED TO ITS NEAREST WAY, and refused where that board cannot face it (labels L12, feature 287
                            # wave 6): beside a lane's corner both arms are as near, and a board turned to one stood 55 and 86
                            # degrees off the other (cohort seeds 25 and 42) - asked last, of a seat every cheaper test kept
                            and (turn := env.facing.turn(x, y, rot)) is not None
                            # ...and the registry of what stands admits the board as `kosatsuba` will record it, turned
                            # (feature 287, water W53): a seat on a field ditch or a stranger's yard is not offered
                            and self.admits("kosatsuba", self.board_record(x, y, turn))
                        ):
                            # BUSY IS WHERE THE FEET ARE (feature 140's Inashiro review): the near count is weighted double
                            busy = sum(1 for sx, sy in env.spots if math.hypot(x - sx, y - sy) < 260) + 2 * sum(1 for sx, sy in env.spots if math.hypot(x - sx, y - sy) < 150)
                            # WHERE THE BOARD STANDS IS A KNOB (feature 152 T21): `frontage` is the busiest built ground,
                            # `waterside` the drawing-water place - both attested
                            if env.siting == "waterside" and env.wells:
                                dw = min(math.hypot(x - wx, y - wy) for wx, wy in env.wells)
                                busy += 14 if dw < 40.0 else (8 if dw < 90.0 else 0)
                            out.append(BoardSeat(busy, busy * 10 - off / 3, x, y, turn, off - rw / 2 - h / 2, under_canopy(env.canopy, x, y, half), approach))
                        off += 5.0
        return out

    def _board_routes(self: Settlement, anchor: Pt | None, placement: str, widen: bool, ftpx: float) -> list[tuple[list[Pt], float, bool]]:  # type: ignore[misc]
        """The ways a board of this placement is sited along, as (pts, tread width, is the approach).

        MAIN WAYS ONLY, where the map declares any (GM 2026-08-02, from Ubame: the siter put the board a legal 49 ft off a
        side lane while the high street ran 200 ft away - "it should be along the main road, in order to be more noticed").
        Every road and every main: True town street is a MAIN way, and when the map has at least one, ONLY main-way verges
        are sampled. A map with no declared hierarchy falls back to the whole network, TOWN STREETS TOO (Hirameki - no road,
        no lanes, all town_streets - GM 2026-07-27).

        A ROUTE CARRIES ITS OWN WIDTH (feature 134 T50): every lane at a nominal 8 ft put the board `(8 - w) / 2` too far
        out; the nominal width is reached only on a manifest with runs but no lane records (the frozen fixtures).

        A SERVICE LANE IS NOT A PLACE TO POST THE STATE'S NOTICE: web lanes are used only where nothing else stands (a
        hamlet never declares a main way), and the connector is not a main way either (Kuwabata, 2026-09-26) - BUT an
        anchored board is offered the way that meets its anchor, web or not (feature 261: the lane the approach meets at
        the mouth is often a web lane), and at a HANDOVER the approach itself, measured to the way's segments (Inashiro's
        700 ft leg). `widen` (labels L4 fallback step 1) admits every web lane: the placement found no clean caption on
        the main ways. TRIED AND REVERTED (feature 140): admitting every web lane unconditionally moved nothing on
        Inashiro - the room was the constraint, not the routes (`research.md` R6)."""
        routes: list[tuple[list[Pt], float, bool]] = []
        if self.M.get("road"):
            routes.append(([(p[0], p[1]) for p in self.M["road"]], 18.0, False))
        routes.extend(([(p[0], p[1]) for p in r["pts"]], 18.0, False) for r in (self.M.get("roads") or [])[1:])
        routes.extend(([(p[0], p[1]) for p in st["pts"]], float(st.get("w", 18)), False) for st in self.M.get("town_streets") or [] if st.get("main"))
        if routes:
            return routes
        if not (self.M.get("lanes") or []):
            routes.extend((_st, 8.0, False) for _st in street_runs(self.M))  # every lane; `M["lane"]` is only the last one drawn
        ways = self.M.get("lanes") or []
        main = [ln for ln in ways if not ln.get("web") and not ln.get("connector")] or ways
        if widen:
            main = main + [ln for ln in ways if ln not in main and not ln.get("connector")]
        if anchor is not None:
            reach = 2.0 * KOSATSUBA_ANCHOR_BAND_FT / ftpx
            hand = placement == "entrance" and kosatsuba_handover(self.M) is not None
            main = main + [
                ln
                for ln in ways
                if ln not in main
                and (hand or not ln.get("connector"))
                and any(seg_dist(anchor[0], anchor[1], (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) <= reach for a, b in zip(ln["pts"], ln["pts"][1:], strict=False))
            ]
        routes.extend(([(p[0], p[1]) for p in ln["pts"]], float(ln.get("w", 8)), bool(ln.get("connector"))) for ln in main)
        routes.extend(([(p[0], p[1]) for p in st["pts"]], float(st.get("w", 18)), False) for st in self.M.get("town_streets") or [])
        return routes

    def _board_for(  # type: ignore[misc]
        self: Settlement, placement: str, sample: Callable[..., list[BoardSeat]], proof: Proof, widen: bool, ftpx: float, lane_tier: bool
    ) -> tuple[BoardSeat, Placement | None] | None:
        """The board's seat under one placement, with its caption's proved seat - or None where the placement cannot be sited.

        THE PLACEMENT IS A KNOB, NOT ONE OBJECTIVE (feature 154, GM 2026-08-29): `center` is the traffic objective itself;
        an anchored placement (`entrance`, `frontage`) chooses the GROUND and the preferences below choose the seat on it.
        ROADSIDE FIRST (GM 2026-08-26): at the lane tiers, if any seat stands within `KOSATSUBA_VERGE_FT` of a tread, only
        those compete (`widen` lifts it - labels L4 fallback step 1). AN ENTRANCE BOARD STANDS WHERE EVERY DEPARTURE PASSES
        (labels L1: `entrance_seat_ok`, hard) and ON THE APPROACH ITSELF where it offers one (feature 261, Inashiro); then
        the seats whose caption fits, then the open, then the band beside the handover (Kashikawa, Mizuguchi). ON THE
        TRAFFIC IS THE RULE (the Ubame failure): away from an anchor the busiest node sets a floor, 60% of the best count,
        and the caption and the open ground choose among the seats on it (`choose_board`) - below it only where nothing
        on it carries a clean caption."""
        anchor = kosatsuba_anchor(self.M, placement) if lane_tier else None
        cands = sample(self._board_routes(anchor, placement, widen, ftpx), VERGE_FIRST and lane_tier and not widen)
        if lane_tier and not widen:
            cands = [c for c in cands if c.gap <= KOSATSUBA_VERGE_FT / ftpx + 1e-6] or cands
        hand: Pt | None = None
        if anchor is not None and placement == "entrance":
            handover = kosatsuba_handover(self.M)
            reach = RouteReach(departure_routes(self.M)) if handover is not None else None  # the routes filed once (feature 281)
            cands = [c for c in cands if entrance_seat_ok(c, anchor, reach, ftpx)]
            if handover is not None:
                cands = [c for c in cands if c.approach] or cands
                hand = anchor
        if anchor is not None and hand is None and cands:
            near = min(math.hypot(c.x - anchor[0], c.y - anchor[1]) for c in cands)
            cands = [c for c in cands if math.hypot(c.x - anchor[0], c.y - anchor[1]) <= near + KOSATSUBA_ANCHOR_BAND_FT / ftpx]
        if not cands:
            return None
        if hand is not None:
            cands = [c for c in cands if proof(c)[0]]
            if not cands:
                return None
            cands = [c for c in cands if not c.shaded] or cands
            hnear = min(math.hypot(c.x - hand[0], c.y - hand[1]) for c in cands)
            cands = [c for c in cands if math.hypot(c.x - hand[0], c.y - hand[1]) <= hnear + KOSATSUBA_HANDOVER_BAND_FT / ftpx]
        floor = 0.0 if anchor is not None else 0.6 * max(c.busy for c in cands)
        return choose_board([c for c in cands if c.busy >= floor], proof) or choose_board(cands, proof)

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
            # FROM AN INDEX OF THE BEDS' SEGMENTS (feature 278, FR-009): every segment of every way was measured per
            # candidate. Each segment is filed by its box widened by its own refusal distance, so a segment whose widened
            # box misses the point stands farther than that distance and cannot refuse it.
            return all(seg_dist(x, y, a, b) >= reach for a, b, reach, _x0, _y0, _x1, _y1 in _bed_segs.near(x, y) if _x0 <= x <= _x1 and _y0 <= y <= _y1)

        _bed_segs = bed_segment_index(beds, h / 2 + 3)

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


bed_segment_index = seg_reach_index  # the verge probes' name for it (feature 278; defined with the other indexes)
