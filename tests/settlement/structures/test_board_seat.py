"""Feature 287: the notice board sited by ONE siter that applies every board rule where it decides the seat
(`settlement/structures/fixtures/board_seat.py`, `siting.place_kosatsuba`) - labels L1-L4, L7, L11, L12, L14 and plan D12's
caption steps - each on a constructed hamlet that includes the violating case."""

from __future__ import annotations

import math
from typing import Any

import pytest

from l7r.diagram.labels import Obstacle, ObstacleIndex, Placement, Way, caption_clears_ways
from l7r.diagram.labels.geom import poly_gap, rect
from l7r.diagram.settlement import Settlement, nearest_way_bearing
from l7r.diagram.settlement._geom import seg_dist, street_runs
from l7r.diagram.settlement._knobs import resolve_knob
from l7r.diagram.settlement.structures.fixtures import kosatsuba_affordances
from l7r.diagram.settlement.structures.fixtures._helpers import KOSATSUBA_ANCHOR_BAND_FT, KOSATSUBA_ENTRANCE_REACH_FT, RouteReach, departure_routes, kosatsuba_anchor, routes_missed
from l7r.diagram.settlement.structures.fixtures.board_seat import (
    FACING_DEG,
    FACING_TIE_PX,
    KOSATSUBA_WAY_REACH_FT,
    BoardSeat,
    WayFacing,
    board_in_view,
    choose_board,
    entrance_seat_ok,
    off_parallel,
    resolve_seat,
    site_board,
    terminal_caption,
    under_placard,
)
from l7r.diagram.settlement.structures.fixtures.boards import board_subject


def _hamlet(w: int = 1000, h: int = 800, view: tuple[float, float, float, float] | None = None) -> Settlement:
    s = Settlement(w, h, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    if view is not None:
        s.set_view(*view)
    return s


def _house(s: Settlement, x: float, y: float, w: float = 40.0, h: float = 26.0) -> None:
    s.M["houses"].append({"x": x, "y": y, "w": w, "h": h, "rot": 0.0})
    s.placed.append((x, y, w, h))


def _drawn(s: Settlement) -> list[Any]:
    s.place_labels()
    return [lb for lb in s.M["labels"] if len(lb) > 5 and lb[5] == "notice board"]


def _seat(x: float, y: float, score: float = 1.0, shaded: bool = False) -> BoardSeat:
    return BoardSeat(1, score, x, y, 0.0, 1.0, shaded, False)


# ---- the predicates ------------------------------------------------------------------------------------------------


def test_the_board_is_in_the_view_by_its_whole_footprint() -> None:
    """Labels L2: inset by the footprint's half-diagonal, at any turn; no view recorded is no limit."""
    view = (0.0, 0.0, 100.0, 100.0)
    assert board_in_view(view, 50.0, 50.0, 12.0, 5.0)
    assert not board_in_view(view, 4.0, 50.0, 12.0, 5.0), "its footprint would cross the edge"
    assert board_in_view(None, -500.0, 0.0, 12.0, 5.0)


def test_a_board_under_the_placard_is_refused() -> None:
    """Labels L14: the placard plus its keep."""
    M = {"title": {"placard": [100.0, 100.0, 300.0, 180.0]}}
    assert under_placard(M, 200.0, 140.0, 12.0, 5.0, 4.0)
    assert under_placard(M, 305.0, 140.0, 12.0, 5.0, 4.0), "within the keep"
    assert not under_placard(M, 330.0, 140.0, 12.0, 5.0, 4.0)
    assert not under_placard({}, 200.0, 140.0, 12.0, 5.0, 4.0)


def test_an_entrance_seat_stands_where_every_way_out_passes() -> None:
    """Labels L1: within the entrance reach plus the anchor band of the anchor, and missed by no departure."""
    reach = RouteReach([[(0.0, 0.0), (0.0, 100.0)], [(50.0, 0.0), (0.0, 0.0)]])
    assert entrance_seat_ok(_seat(0.0, 5.0), (0.0, 0.0), reach, 1.0)
    assert not entrance_seat_ok(_seat(0.0, 90.0), (0.0, 0.0), reach, 1.0), "one way out never passes it"
    far = KOSATSUBA_ENTRANCE_REACH_FT + KOSATSUBA_ANCHOR_BAND_FT + 1.0
    assert not entrance_seat_ok(_seat(far, 0.0), (0.0, 0.0), None, 1.0)
    assert entrance_seat_ok(_seat(far - 2.0, 0.0), (0.0, 0.0), None, 1.0)


def test_the_board_is_chosen_by_its_caption_lazily() -> None:
    """The first seat in score order whose caption fits in the open; else the first under the trees; else none - and
    the proof is asked no further than the first open fit, and of no shaded seat before every open one has been asked
    (feature 287: under one wide canopy the walk proved all 1,072 shaded seats where the first that fit was the answer)."""
    asked: list[float] = []

    def proof(c: BoardSeat) -> tuple[bool, Placement | None]:
        asked.append(c.score)
        return c.x > 0, None

    seats = [_seat(-1.0, 0.0, 9.0), _seat(1.0, 0.0, 8.0, shaded=True), _seat(2.0, 0.0, 7.0), _seat(3.0, 0.0, 6.0)]
    got = choose_board(seats, proof)
    assert got is not None and got[0].x == 2.0 and asked == [9.0, 7.0], "the shaded seat between is never proved"
    asked.clear()
    assert choose_board(seats[:2], proof)[0].x == 1.0, "under the trees, where the open offers nothing"  # type: ignore[index]
    assert asked == [9.0, 8.0]
    canopy = [_seat(float(k + 1), 0.0, 100.0 - k, shaded=True) for k in range(50)]
    asked.clear()
    assert choose_board(canopy, proof)[0].x == 1.0 and asked == [100.0], "every seat shaded: the first that fits, alone"  # type: ignore[index]
    assert choose_board(seats[:1], proof) is None


def test_the_knob_resolves_over_the_placements_the_map_can_site() -> None:
    """Labels L1: every placement sitable - the knob's own roll; one not - never rolled; pinned where it cannot be
    sited - refused, naming it; pinned where it can - honored."""
    ctx = {"has_approach": True, "has_headman_house": True}
    for seed in range(1, 40):
        assert resolve_seat(seed, dict(ctx), {}, {"center", "entrance", "frontage"}) == resolve_knob("kosatsuba_seat", seed, ctx, {})
        assert resolve_seat(seed, dict(ctx), {}, {"center", "frontage"}) != "entrance"
    with pytest.raises(ValueError, match="'entrance'"):
        resolve_seat(1, dict(ctx), {"kosatsuba_seat": "entrance"}, {"center"})
    assert resolve_seat(1, dict(ctx), {"kosatsuba_seat": "frontage"}, {"frontage"}) == "frontage"


# ---- the siter -----------------------------------------------------------------------------------------------------


def test_the_board_and_its_caption_stand_inside_the_view() -> None:
    """Labels L2: the busiest verge lies just outside the view's north edge; the board goes up on a quieter verge inside
    it, board and caption wholly within the frame - no second siter re-seats it."""
    s = _hamlet(view=(100.0, 200.0, 800.0, 500.0))
    s.M["lanes"] = [{"pts": [[150.0, 190.0], [850.0, 190.0]], "w": 5}, {"pts": [[150.0, 500.0], [850.0, 500.0]], "w": 5}]
    for x in range(200, 820, 60):
        _house(s, float(x), 150.0)
    _house(s, 500.0, 560.0)
    spot = s.place_kosatsuba()
    assert spot is not None and board_in_view(s.M["meta"]["view"], spot[0], spot[1], 12.0, 5.0)
    (cap,) = _drawn(s)
    vx, vy, vw, vh = s.M["meta"]["view"]
    assert vx <= cap[0] and cap[2] <= vx + vw and vy <= cap[1] and cap[3] <= vy + vh


def test_the_board_takes_the_verge_whose_caption_clears_every_roof() -> None:
    """Labels L4: the busiest verge lies between two farmhouses, where every seat beside the board covers a roof; the
    board takes the open verge, and its caption stands clear of every house by the standard's offset."""
    s = _hamlet(view=(0.0, 0.0, 1000.0, 800.0))
    s.M["lanes"] = [{"pts": [[100.0, 400.0], [900.0, 400.0]], "w": 5}]
    for x in (300.0, 330.0, 360.0, 390.0):
        _house(s, x, 375.0, 26.0, 20.0)
        _house(s, x, 425.0, 26.0, 20.0)
    spot = s.place_kosatsuba()
    assert spot is not None and not 285.0 < spot[0] < 405.0, f"not between the houses: {spot}"
    (cap,) = _drawn(s)
    box = [(cap[0], cap[1]), (cap[2], cap[1]), (cap[2], cap[3]), (cap[0], cap[3])]
    assert all(poly_gap(box, rect(h["x"], h["y"], h["w"] / 2, h["h"] / 2)) >= 0.5 * 8.0 - 1e-6 for h in s.M["houses"])
    assert "kosatsuba_caption_level" not in s.M["meta"]


def test_the_caption_the_siter_proved_is_the_caption_drawn() -> None:
    """Labels L4, L7: the seat the siter proves rides to the label phase and is drawn as proved - clear of the crowns,
    which the one placer's index now holds."""
    s = _hamlet(view=(0.0, 0.0, 1000.0, 800.0))
    s.M["lanes"] = [{"pts": [[100.0, 400.0], [900.0, 400.0]], "w": 5}]
    s.M["tree_crowns"] = [x for cx in range(120, 480, 18) for x in (float(cx), 380.0, 10.0)]
    _house(s, 600.0, 440.0)
    spot = s.place_kosatsuba()
    assert spot is not None
    kind, payload = s._label_queue[-1]
    proved = payload[6]
    assert kind == "kosatsuba" and isinstance(proved, Placement) and proved.cost == 0.0 and proved.leader is None
    (cap,) = _drawn(s)
    assert cap[4] is not None and abs((cap[0] + cap[2]) / 2 - proved.x) < 1.0
    from l7r.diagram.labels.obstacles import circle_gap

    block = list(proved.block)
    assert all(circle_gap(block, (s.M["tree_crowns"][i], s.M["tree_crowns"][i + 1], s.M["tree_crowns"][i + 2])) > 0 for i in range(0, len(s.M["tree_crowns"]), 3))


def test_a_yard_just_nearer_than_the_board_on_the_record_moves_the_caption() -> None:
    """Labels L6, the violating case (Kuwabata, feature 287: the caption 4.008 ft off a threshing yard and 4.056 ft off
    its board, as recorded). The caption beside the board stands exactly one offset (4.0) off it, and a yard 4.02 off -
    farther, so the search's association term passes the seat - but the record rounds the caption's box to 0.1, which
    carries it 0.04 toward the yard and makes the yard the nearer. The siter proves the association on the record
    (`stands_nearest`), so it takes the next seat beside the board, which stands nearer its board as recorded."""
    from l7r.diagram.labels import place
    from l7r.diagram.labels.geom import bbox
    from l7r.diagram.labels.obstacles import stands_nearest
    from l7r.diagram.settlement.finish import recorded_caption_quad
    from l7r.diagram.settlement.structures.fixtures.board_seat import board_caption_seat, recorded_board
    from l7r.diagram.settlement.structures.fixtures.boards import BOARD_CAPTION_SIZE

    bx, by, frame = 500.0, 391.44, (0.0, 0.0, 1000.0, 800.0)
    s = _hamlet(view=(0.0, 0.0, 1000.0, 800.0))
    s.M["lanes"] = [{"pts": [[100.0, 400.0], [900.0, 400.0]], "w": 5}]
    subject = board_subject(bx, by, 0.0, 12.0, 5.0)
    first = board_caption_seat(s.M, bx, by, 6.0, 2.5, 0.0, "notice board", s.label_obstacles(), frame)
    assert first is not None and first.position == "above" and poly_gap(list(first.block), list(subject.poly)) == pytest.approx(4.0)
    x0, y0, x1, _y1 = bbox(first.block)
    s.M["threshing_yards"] = [{"x": (x0 + x1) / 2, "y": y0 - 4.02 - 10.0, "w": 40.0, "h": 20.0, "rot": 0.0}]
    index = s.label_obstacles()
    board = recorded_board(bx, by, 12.0, 5.0, 0.0)

    def on_record(p: Placement) -> bool:
        return stands_nearest(recorded_caption_quad("notice board", p.lines, p.x, p.y, BOARD_CAPTION_SIZE, p.angle), board, index)

    raw = place("notice board", BOARD_CAPTION_SIZE, subject, index, frame, strict=True, max_ring=0)
    assert raw is not None and raw.position == "above" and not on_record(raw), "the case is real: exact passes, the record fails"
    got = board_caption_seat(s.M, bx, by, 6.0, 2.5, 0.0, "notice board", index, frame)
    assert got is not None and got.position != "above" and got.ring == 0 and on_record(got)


def test_the_caption_quad_the_siter_proves_is_the_drawn_record() -> None:
    """`recorded_caption_quad` is the corner ring of the label record the phase writes for the proved seat, and
    `recorded_board` the footprint the board's record gives - so the siter's proof and the pool test measure one thing."""
    from l7r.diagram.settlement._geom import label_quad
    from l7r.diagram.settlement.finish import recorded_caption_quad
    from l7r.diagram.settlement.structures.fixtures.board_seat import recorded_board
    from l7r.diagram.settlement.structures.fixtures.boards import BOARD_CAPTION_SIZE

    s = _hamlet(view=(0.0, 0.0, 1000.0, 800.0))
    s.M["lanes"] = [{"pts": [[100.0, 400.0], [900.0, 437.0]], "w": 5}]
    assert s.place_kosatsuba() is not None
    x, y, rot, vw, vh, _label, proved = s._label_queue[-1][1]
    (cap,) = _drawn(s)
    assert recorded_caption_quad("notice board", proved.lines, proved.x, proved.y, BOARD_CAPTION_SIZE, proved.angle) == label_quad(cap)
    k = s.M["kosatsuba"][-1]
    assert (x, y, rot) != (k["x"], k["y"], k["rot"]), "non-vacuity: the record rounds the seat"
    assert recorded_board(x, y, vw, vh, rot) == rect(k["x"], k["y"], k["vw"] / 2, k["vh"] / 2, k["rot"])


def test_the_board_stands_by_its_way_and_faces_it() -> None:
    """Labels L11, L12: within `KOSATSUBA_WAY_REACH_FT` of the lane it was sampled from, and turned to the nearest way's
    bearing - at an L-corner, the shared reading's tie-broken arm."""
    s = _hamlet()
    s.M["lanes"] = [{"pts": [[200.0, 200.0], [600.0, 200.0], [600.0, 600.0]], "w": 5}]
    _house(s, 400.0, 260.0)
    spot = s.place_kosatsuba()
    assert spot is not None
    pts = s.M["lanes"][0]["pts"]
    assert min(seg_dist(spot[0], spot[1], a, b) for a, b in zip(pts, pts[1:], strict=False)) <= KOSATSUBA_WAY_REACH_FT
    assert s.M["kosatsuba"][-1]["rot"] == pytest.approx(round(nearest_way_bearing(s.M, *spot), 1), abs=0.06)


def test_a_board_stands_no_farther_from_its_way_than_the_reach_even_where_only_the_far_ground_is_open() -> None:
    """Labels L11, the violating case: every verge within the reach is refused but a strip at its far edge, and open ground
    lies beyond it. The board takes the far strip, never the open ground past the reach; with the strip closed too, no
    board is posted rather than one off its way."""
    reach = KOSATSUBA_WAY_REACH_FT

    def site(open_from: float) -> tuple[Settlement, Any]:
        s = _hamlet(view=(0.0, 0.0, 1000.0, 800.0))
        s.M["lanes"] = [{"pts": [[100.0, 400.0], [900.0, 400.0]], "w": 5}]
        _house(s, 500.0, 300.0)
        for sign in (1.0, -1.0):  # both sides refused from the tread out to `open_from`
            y0, y1 = 400.0 + sign * 3.0, 400.0 + sign * open_from
            s.block_polys.append([(60.0, min(y0, y1)), (940.0, min(y0, y1)), (940.0, max(y0, y1)), (60.0, max(y0, y1))])
        return s, s.place_kosatsuba()

    s, spot = site(reach - 4.0)
    assert spot is not None, "the far strip inside the reach takes the board"
    d = abs(spot[1] - 400.0)
    assert reach - 4.0 <= d <= reach, f"the board stands {d} px out: in the far strip, not past the reach"
    s, spot = site(reach + 30.0)
    assert spot is None and not s.M.get("kosatsuba"), "open ground past the reach is no seat"


def _block_all_but(s: Settlement, keep: list[tuple[float, float, float, float]]) -> None:
    """Refuse every seat on the sheet but those inside the `keep` boxes (x0, y0, x1, y1): the complement as strips."""
    ys = sorted({0.0, float(s.H), *(b[1] for b in keep), *(b[3] for b in keep)})
    for y0, y1 in zip(ys, ys[1:], strict=False):
        spans = sorted((b[0], b[2]) for b in keep if b[1] <= y0 and y1 <= b[3])
        x = 0.0
        for a, b in [*spans, (float(s.W), float(s.W))]:
            if a > x:
                s.block_polys.append([(x, y0), (a, y0), (a, y1), (x, y1)])
            x = max(x, b)


def _corner_hamlet(verge: bool = True) -> Settlement:
    """An L lane whose busiest open ground lies OUTSIDE its corner, where every seat stands as near both arms (90 degrees
    apart), and whose only other open ground is a quiet verge on the first arm (none with `verge=False`)."""
    s = _hamlet(view=(0.0, 0.0, 1000.0, 800.0))
    s.M["lanes"] = [{"pts": [[200.0, 200.0], [600.0, 200.0], [600.0, 600.0]], "w": 5}]
    for x, y in ((680.0, 150.0), (700.0, 240.0), (660.0, 110.0), (720.0, 130.0)):
        _house(s, x, y, 24.0, 18.0)
    _block_all_but(s, [(603.0, 150.0, 640.0, 205.0), *([(300.0, 140.0, 340.0, 196.0)] if verge else [])])
    return s


def _judged_off(M: Any, x: float, y: float, rot: float) -> float:
    """The retired gate test's reading with rounding's margin: the worst angle between the board and ANY way standing as
    near it as the nearest (within `FACING_TIE_PX`) - a board faces its way only if it faces every way that could be read
    as the nearest."""
    segs = [(a, b) for pts in street_runs(M) for a, b in zip(pts, pts[1:], strict=False)]
    least = min(seg_dist(x, y, a, b) for a, b in segs)
    return max(off_parallel(rot, math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))) for a, b in segs if seg_dist(x, y, a, b) <= least + FACING_TIE_PX)


def test_a_board_is_turned_to_its_way_and_refused_where_it_cannot_face_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """Labels L12, the violating case (cohort seeds 25 and 42: 55 and 86 degrees off): the busiest seat stands outside an L
    corner, as near both arms. Turned to its nearest arm with no refusal, the board stands side-on to the other; the
    siter refuses that seat and the board it posts faces every way as near it. Sited with no caption (`label=""`), so the
    facing rule alone decides - a caption at the corner, with no free ground, lies on the lane arms and is refused for that
    (feature 328 wave 49: the key that once took it is retired)."""
    lenient = WayFacing.turn
    monkeypatch.setattr(WayFacing, "turn", lambda self, x, y, f: (self._near(x, y) or [(0.0, 0, f)])[0][2])
    s = _corner_hamlet(verge=False)  # the verge would take the board first (`VERGE_FIRST`) now its caption clears the road
    spot = s.place_kosatsuba()
    assert spot is not None and _judged_off(s.M, *spot, s.M["kosatsuba"][-1]["rot"]) > FACING_DEG, "the input holds the violation"
    monkeypatch.setattr(WayFacing, "turn", lenient)
    s = _corner_hamlet()
    spot = s.place_kosatsuba()
    assert spot is not None
    rot = s.M["kosatsuba"][-1]["rot"]
    assert _judged_off(s.M, *spot, rot) <= FACING_DEG
    assert rot == pytest.approx(round(nearest_way_bearing(s.M, *spot), 1), abs=0.06), "turned to the shared reading"


def test_the_facing_predicate_turns_to_the_nearest_way_and_refuses_a_corner_tie() -> None:
    """Labels L12's one predicate on constructed ways: beside a straight run, its bearing; outside a right-angle corner, as
    near both arms, refused; outside a shallow bend, the first arm (`nearest_way_bearing`'s tie-break); nearer one arm by
    more than the tie, that arm; far from every way (past the index's pad), still the nearest; no way, the fallback."""
    M = {"lanes": [{"pts": [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0]]}, {"pts": [[300.0, 0.0], [400.0, 0.0], [500.0, 30.0]]}]}
    f = WayFacing(M, 20.0)
    assert f.turn(50.0, 8.0, 7.0) == pytest.approx(0.0)
    assert f.turn(106.0, -6.0, 7.0) is None, "the right-angle corner: 90 degrees between the arms as near"
    assert f.turn(99.5, -6.0, 7.0) is None, "0.02 px nearer one arm: within the tie, where rounding would pick the arm"
    assert f.turn(95.0, -6.0, 7.0) == pytest.approx(0.0), "nearer one arm by more than the tie: that arm"
    assert f.turn(110.0, 50.0, 7.0) == pytest.approx(90.0)
    bend = f.turn(400.0, -8.0, 7.0)
    assert bend == pytest.approx(0.0) and bend == pytest.approx(nearest_way_bearing(M, 400.0, -8.0))
    assert f.turn(250.0, 400.0, 7.0) == pytest.approx(nearest_way_bearing(M, 250.0, 400.0)), "past the pad: every segment asked"
    assert WayFacing({}, 20.0).turn(5.0, 5.0, 7.0) == 7.0
    assert off_parallel(170.0, -10.0) == pytest.approx(0.0) and off_parallel(0.0, 91.0) == pytest.approx(89.0)


def test_no_board_is_posted_under_the_title_placard() -> None:
    """Labels L14: the placard is drawn before the board is sited, and the verge under it is no seat."""
    s = _hamlet(view=(0.0, 0.0, 1000.0, 800.0))
    s.M["lanes"] = [{"pts": [[100.0, 400.0], [900.0, 400.0]], "w": 5}]
    _house(s, 500.0, 440.0)
    s.M["title"] = {"placard": [380.0, 360.0, 620.0, 430.0], "bbox": [380.0, 360.0, 620.0, 430.0]}
    spot = s.place_kosatsuba()
    assert spot is not None and not under_placard(s.M, spot[0], spot[1], 12.0, 5.0, 4.0)


def _entrance_hamlet(straggler: bool) -> Settlement:
    s = _hamlet(view=(0.0, 0.0, 1000.0, 1000.0))
    s.M["meta"]["knobs"] = {}
    for x, y in ((300.0, 260.0), (700.0, 260.0), (500.0, 340.0)):
        _house(s, x, y, 30.0, 24.0)
    s.M["lanes"] = [
        {"pts": [[300.0, 300.0], [700.0, 300.0]], "w": 5},
        {"pts": [[500.0, 300.0], [500.0, 500.0]], "w": 5},
        {"pts": [[500.0, 500.0], [500.0, 990.0]], "w": 6, "connector": True},
    ]
    if straggler:
        # a household whose only way out leaves by its own track, joining the approach far below every verge the reach allows
        _house(s, 880.0, 900.0, 30.0, 24.0)
        s.M["lanes"].append({"pts": [[880.0, 920.0], [500.0, 960.0]], "w": 3, "web": True})
    return s


def test_an_entrance_board_stands_where_every_way_out_passes_it() -> None:
    """Labels L1: an entrance board at the handover is passed by every household's way out and stands within the
    entrance reach; where no seat is, `entrance` is not a placement the map affords, and the knob resolves over the rest."""
    s = _entrance_hamlet(straggler=False)
    s.M["meta"]["knobs"] = {"kosatsuba_seat": "entrance"}
    spot = s.place_kosatsuba()
    assert spot is not None and s.M["meta"]["kosatsuba_seat"] == "entrance"
    anchor = kosatsuba_anchor(s.M, "entrance")
    assert anchor is not None and math.dist(spot, anchor) <= KOSATSUBA_ENTRANCE_REACH_FT + KOSATSUBA_ANCHOR_BAND_FT
    assert routes_missed(departure_routes(s.M), spot[0], spot[1], 20.0) == 0
    t = _entrance_hamlet(straggler=True)
    assert kosatsuba_affordances(t.M)["has_approach"]
    assert t.place_kosatsuba() is not None
    assert t.M["meta"]["kosatsuba_seat"] != "entrance" and "entrance" in t.M["meta"]["kosatsuba_seat_unsitable"]
    u = _entrance_hamlet(straggler=True)
    u.M["meta"]["knobs"] = {"kosatsuba_seat": "entrance"}
    with pytest.raises(ValueError, match="'entrance'"):
        u.place_kosatsuba()


def test_the_web_lanes_are_offered_when_no_main_way_takes_a_clean_caption() -> None:
    """Labels L4 fallback step 1: the main lane's every verge is hemmed by roofs; the web lane's is open - the board
    stands on the web lane rather than taking a caption over a roof."""
    s = _hamlet(view=(0.0, 0.0, 1000.0, 800.0))
    s.M["lanes"] = [{"pts": [[200.0, 300.0], [800.0, 300.0]], "w": 5}, {"pts": [[500.0, 300.0], [500.0, 700.0]], "w": 3, "web": True}]
    for x in range(150, 860, 24):
        for dy in (-72.0, -48.0, -24.0, 24.0, 48.0, 72.0):  # the main lane hemmed through its whole 60 ft band
            _house(s, float(x), 300.0 + dy, 20.0, 16.0)
    spot = s.place_kosatsuba()
    # by the web lane, inside its 60 ft band (the caption proved against the board drawn, footing and all, may take a seat
    # out in the band rather than at the verge - feature 328 wave 64), and off the hemmed main lane
    assert spot is not None and seg_dist(spot[0], spot[1], (500.0, 300.0), (500.0, 700.0)) <= KOSATSUBA_WAY_REACH_FT and spot[1] > 385.0, spot


def test_with_no_clean_caption_anywhere_the_verge_takes_the_board_and_its_caption_clears_the_road() -> None:
    """Plan D12's second step: where no verge takes a board with a clean caption, a board still stands, its caption where it
    covers the least, and a seat whose caption clears every way is preferred (`captions_clear_the_ways_they_stand_on`). With
    the key retired (feature 328 wave 49) the verge seat's caption sits above the board, off the road - so the board stands
    on the verge, 6 ft off the road's edge (0190), not out in the band."""
    s = _hamlet(view=(0.0, 0.0, 400.0, 400.0))
    s.M["road"] = [[100.0, 200.0], [300.0, 200.0]]  # sited along at its 18 ft tread; captions keep off its 26 ft bed
    _house(s, 200.0, 260.0)
    road = Way(((100.0, 200.0), (300.0, 200.0)), 13.0)
    everything = ObstacleIndex([Obstacle(tuple(rect(200.0, 200.0, 400.0, 400.0)), 1000.0)], [road])
    s.label_obstacles = lambda: everything  # type: ignore[method-assign]  # every caption seat covers ink
    verge = terminal_caption(s.M, 200.0, 200.0 - (9.0 + 2.5 + 4.0), 6.0, 2.5, 0.0, "notice board", everything, (0.0, 0.0, 400.0, 400.0))
    assert verge is not None and caption_clears_ways(verge.block, [road]), "the verge seat's caption clears the road"
    spot = s.place_kosatsuba()
    assert spot is not None and seg_dist(spot[0], spot[1], (100.0, 200.0), (300.0, 200.0)) <= KOSATSUBA_WAY_REACH_FT, f"by the road: {spot}"
    proved = s._label_queue[-1][1][6]
    assert isinstance(proved, Placement) and proved.cost > 0.0, "every seat covers ink: the caption goes where it covers the least"
    assert caption_clears_ways(proved.block, [road]), "and clears the road"


def test_where_every_seats_caption_is_fouled_the_board_is_still_posted_by_its_way() -> None:
    """Plan D12, answered by the GM (2026-09-30: *"it is okay for it to not sit clean"*): every roadside seat carries its
    caption, key mark and all, onto a way - the case that used to post no board. The board is posted anyway, by its way
    (`KOSATSUBA_WAY_REACH_FT`) and facing it (L12), and its caption is drawn where the one placer's fallback puts it."""
    s = _hamlet(view=(0.0, 0.0, 400.0, 400.0))
    s.M["road"] = [[100.0, 200.0], [300.0, 200.0]]
    _house(s, 200.0, 290.0)
    flood_way = Way(((0.0, 200.0), (400.0, 200.0)), 400.0)  # the whole frame: no seat inside it clears the way
    flood = ObstacleIndex([Obstacle(tuple(rect(200.0, 200.0, 400.0, 400.0)), 1000.0)], [flood_way])
    s.label_obstacles = lambda: flood  # type: ignore[method-assign]  # a way under every seat the band offers
    spot = s.place_kosatsuba()
    assert spot is not None and len(s.M["kosatsuba"]) == 1, "never no board over its caption"
    assert seg_dist(spot[0], spot[1], (100.0, 200.0), (300.0, 200.0)) <= KOSATSUBA_WAY_REACH_FT, f"the board strays from its way: {spot}"
    assert off_parallel(float(s.M["kosatsuba"][0]["rot"]), 0.0) <= FACING_DEG, "the board faces its way"
    proved = s._label_queue[-1][1][6]
    assert isinstance(proved, Placement) and not caption_clears_ways(proved.block, [flood_way]), "the violating case: a fouled caption"
    s.place_labels()
    assert "caption_key" not in s.M, "no key (0241)"
    assert any("notice board" in str(lb[5]) for lb in s.M["labels"] if len(lb) > 5), "the caption is drawn where it covers the least"


def test_a_pinned_placement_is_posted_though_its_caption_is_fouled() -> None:
    """Plan D12: a pinned `entrance` whose every seat hides its caption was refused as unsitable; the caption is no
    longer a reason, so the board stands at the entrance, where every way out passes it."""
    s = _entrance_hamlet(straggler=False)
    s.M["meta"]["knobs"] = {"kosatsuba_seat": "entrance"}
    base = s.label_obstacles()
    base.add(Obstacle(tuple(rect(500.0, 500.0, 170.0, 170.0)), 1000.0))  # every caption seat round the handover
    s.label_obstacles = lambda: base  # type: ignore[method-assign]
    spot = s.place_kosatsuba()
    assert spot is not None and s.M["meta"]["kosatsuba_seat"] == "entrance"
    assert routes_missed(departure_routes(s.M), spot[0], spot[1], 20.0) == 0


def test_site_board_asks_a_later_proof_only_where_the_earlier_sited_nothing() -> None:
    """`site_board` on plain inputs: the cleaner proof first; a later one only for every placement when nothing was
    sited, or for the pinned one; the web lanes (`widen`) only at the lane tiers."""
    asked: list[tuple[str, str, bool]] = []
    seat = _seat(0.0, 0.0)

    def board_for(sites: set[tuple[str, str, bool]]) -> Any:
        def ask(v: str, pf: Any, widen: bool) -> Any:
            asked.append((v, pf.__name__, widen))
            return (seat, None) if (v, pf.__name__, widen) in sites else None

        return ask

    def clean(c: BoardSeat) -> tuple[bool, Placement | None]:
        return True, None

    def lax(c: BoardSeat) -> tuple[bool, Placement | None]:
        return True, None

    proofs = [clean, lax]
    got = site_board(["a", "b"], proofs, None, board_for({("a", "clean", True)}), True)
    assert set(got) == {"a"} and ("b", "lax", False) not in asked, "a clean seat somewhere: no later proof is asked"
    got = site_board(["a", "b"], proofs, None, board_for({("a", "clean", False), ("b", "clean", False)}), True)
    assert set(got) == {"a", "b"}, "every placement is asked of the first proof, not only until one is sited"
    asked.clear()
    got = site_board(["a", "b"], proofs, "b", board_for({("a", "clean", False), ("b", "lax", False)}), True)
    assert set(got) == {"a", "b"} and ("a", "lax", False) not in asked, "the pinned placement alone steps down"
    asked.clear()
    got = site_board(["a"], proofs, None, board_for({("a", "lax", False)}), False)
    assert set(got) == {"a"} and all(not widen for *_n, widen in asked), "no web lanes off the lane tiers"
    assert site_board(["a"], proofs, None, board_for(set()), True) == {}, "no roadside seat at all: nothing"


def test_the_terminal_caption_clears_every_way_or_is_refused() -> None:
    """Feature 287 wave 5, `terminal_caption` - the one predicate of the board caption's second step (plan D12): a board with
    open ground takes its caption beside it, as does one standing on a way (no key mark is asked any more, feature 328
    wave 49); and one whose every caption seat crosses a way - here a soft way ringing the board, which the non-strict
    placer may cross - is refused on the caption it would draw."""
    frame = (0.0, 0.0, 400.0, 400.0)
    open_ground = terminal_caption({}, 200.0, 200.0, 6.0, 2.5, 0.0, "notice board", ObstacleIndex(), frame)
    assert open_ground is not None and open_ground.ring == 0
    through = ObstacleIndex(ways=[Way(((100.0, 200.0), (300.0, 200.0)), 2.5)])
    beside = terminal_caption({}, 200.0, 200.0, 6.0, 2.5, 0.0, "notice board", through, frame)
    assert beside is not None and caption_clears_ways(beside.block, through.ways), "a caption beside the board, clear of the way"
    ring = tuple((200.0 + 70.0 * math.cos(math.radians(a)), 200.0 + 70.0 * math.sin(math.radians(a))) for a in range(0, 361, 10))
    soft = ObstacleIndex([Obstacle(tuple(rect(200.0, 200.0, 400.0, 400.0)), 1000.0, soft=True)], [Way(ring, 61.0, soft=True)])
    assert terminal_caption({}, 200.0, 200.0, 6.0, 2.5, 0.0, "notice board", soft, frame) is None, "every seat crosses the ring"


def test_a_board_with_no_caption_is_sited_by_the_rules_alone() -> None:
    s = _hamlet(view=(0.0, 0.0, 1000.0, 800.0))
    s.M["lanes"] = [{"pts": [[100.0, 400.0], [900.0, 400.0]], "w": 5}]
    s.M["wells"] = [{"x": 480.0, "y": 450.0, "r": 4.0}]
    assert s.place_kosatsuba(label="") is not None
    assert s.M["kosatsuba"] and s.M["meta"]["kosatsuba_well_ft"] > 0.0, "the drawn board's distance to its nearest well"


def test_an_entrance_whose_every_seat_hides_its_caption_is_not_afforded() -> None:
    """Labels L1, L4: every seat the departures pass has its caption on ink - `entrance` is not sitable, and the knob
    resolves over the placements that are."""
    s = _entrance_hamlet(straggler=False)
    base = s.label_obstacles()
    base.add(Obstacle(tuple(rect(500.0, 500.0, 170.0, 170.0)), 1000.0))  # every caption seat round the handover
    s.label_obstacles = lambda: base  # type: ignore[method-assign]
    assert s.place_kosatsuba() is not None
    assert "entrance" in s.M["meta"]["kosatsuba_seat_unsitable"] and s.M["meta"]["kosatsuba_seat"] != "entrance"
