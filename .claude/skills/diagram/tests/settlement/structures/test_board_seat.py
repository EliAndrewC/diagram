"""Feature 287: the notice board sited by ONE siter that applies every board rule where it decides the seat
(`settlement/structures/fixtures/board_seat.py`, `siting.place_kosatsuba`) - labels L1-L4, L7, L11, L12, L14 and the D12
terminal - each on a constructed hamlet that includes the violating case."""

from __future__ import annotations

import math
from typing import Any

import pytest

from l7r.diagram.labels import Obstacle, ObstacleIndex, Placement, Way, caption_clears_ways, keyed
from l7r.diagram.labels.geom import poly_gap, rect
from l7r.diagram.settlement import Settlement, nearest_way_bearing
from l7r.diagram.settlement._geom import seg_dist
from l7r.diagram.settlement._knobs import resolve_knob
from l7r.diagram.settlement.structures.fixtures import kosatsuba_affordances
from l7r.diagram.settlement.structures.fixtures._helpers import KOSATSUBA_ANCHOR_BAND_FT, KOSATSUBA_ENTRANCE_REACH_FT, RouteReach, departure_routes, kosatsuba_anchor, routes_missed
from l7r.diagram.settlement.structures.fixtures.board_seat import (
    KOSATSUBA_WAY_REACH_FT,
    BoardSeat,
    board_in_view,
    choose_board,
    entrance_seat_ok,
    resolve_seat,
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
    assert "kosatsuba_caption_level" not in s.M["meta"] and "kosatsuba_d12" not in s.M["meta"]


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
    assert spot is not None and abs(spot[0] - 500.0) < 40.0 and spot[1] > 385.0, spot
    assert "kosatsuba_d12" not in s.M["meta"]


def test_with_no_clean_caption_anywhere_the_question_stands_for_the_gm() -> None:
    """Plan D12: where no verge takes a board with a clean caption, a board still stands and the map is marked, so the
    maps reaching the GM's question can be counted - its caption on a leader or in the key (D10), never across a way
    (`captions_clear_the_ways_they_stand_on`, feature 287 wave 5): the verge seats, whose key mark would lie on the
    road, are refused (the violating case), and the board stands where the mark clears it."""
    s = _hamlet(view=(0.0, 0.0, 400.0, 400.0))
    s.M["road"] = [[100.0, 200.0], [300.0, 200.0]]  # sited along at its 18 ft tread; captions keep off its 26 ft bed
    _house(s, 200.0, 260.0)
    road = Way(((100.0, 200.0), (300.0, 200.0)), 13.0)
    everything = ObstacleIndex([Obstacle(tuple(rect(200.0, 200.0, 400.0, 400.0)), 1000.0)], [road])
    s.label_obstacles = lambda: everything  # type: ignore[method-assign]  # every caption seat covers ink
    verge = terminal_caption(s.M, 200.0, 200.0 - (9.0 + 2.5 + 4.0), 6.0, 2.5, 0.0, "notice board", everything, (0.0, 0.0, 400.0, 400.0))
    assert verge is None, "a board at the verge's edge would put its key mark on the road"
    spot = s.place_kosatsuba()
    assert spot is not None and s.M["meta"]["kosatsuba_d12"] is True and abs(spot[1] - 200.0) > 15.5, spot
    proved = s._label_queue[-1][1][6]
    assert isinstance(proved, Placement) and proved.keyed, "every seat covers ink: the caption goes in the key"
    assert caption_clears_ways(proved.block, [road]), "the mark the board carries clears the road"


def test_where_every_seats_caption_would_lie_on_a_way_no_board_stands() -> None:
    """D12's terminal, the case past it: every seat in the band carries its caption, key mark and all, onto a way - so
    no board is posted, the siter's answer wherever no verge fits, and never one whose caption lies across a way."""
    s = _hamlet(view=(0.0, 0.0, 400.0, 400.0))
    s.M["road"] = [[100.0, 200.0], [300.0, 200.0]]
    _house(s, 200.0, 290.0)
    flood = ObstacleIndex([Obstacle(tuple(rect(200.0, 200.0, 400.0, 400.0)), 1000.0)], [Way(((0.0, 200.0), (400.0, 200.0)), 150.0)])
    s.label_obstacles = lambda: flood  # type: ignore[method-assign]  # a way under every seat the band offers
    assert s.place_kosatsuba() is None and not s.M["kosatsuba"]


def test_the_terminal_caption_clears_every_way_or_is_refused() -> None:
    """Feature 287 wave 5, `terminal_caption` - the one predicate of the board's caption at D12's terminal: a board with
    open ground takes its caption beside it; one whose key mark would lie on a way is refused before any search; and one
    whose every caption seat crosses a way - here a soft way ringing the board, which the non-strict placer may cross -
    is refused on the caption it would draw, though its mark clears."""
    frame = (0.0, 0.0, 400.0, 400.0)
    open_ground = terminal_caption({}, 200.0, 200.0, 6.0, 2.5, 0.0, "notice board", ObstacleIndex(), frame)
    assert open_ground is not None and not open_ground.keyed and open_ground.ring == 0
    through = ObstacleIndex(ways=[Way(((100.0, 200.0), (300.0, 200.0)), 2.5)])
    assert terminal_caption({}, 200.0, 200.0, 6.0, 2.5, 0.0, "notice board", through, frame) is None, "the mark on the way"
    ring = tuple((200.0 + 70.0 * math.cos(math.radians(a)), 200.0 + 70.0 * math.sin(math.radians(a))) for a in range(0, 361, 10))
    soft = ObstacleIndex([Obstacle(tuple(rect(200.0, 200.0, 400.0, 400.0)), 1000.0, soft=True)], [Way(ring, 61.0, soft=True)])
    assert caption_clears_ways(keyed("notice board", 8, board_subject(200.0, 200.0, 0.0, 12.0, 5.0), None, 0.0).block, soft.ways)
    assert terminal_caption({}, 200.0, 200.0, 6.0, 2.5, 0.0, "notice board", soft, frame) is None, "every seat crosses the ring"


def test_a_board_with_no_caption_is_sited_by_the_rules_alone() -> None:
    s = _hamlet(view=(0.0, 0.0, 1000.0, 800.0))
    s.M["lanes"] = [{"pts": [[100.0, 400.0], [900.0, 400.0]], "w": 5}]
    s.M["wells"] = [{"x": 480.0, "y": 450.0, "r": 4.0}]
    assert s.place_kosatsuba(label="") is not None
    assert s.M["kosatsuba"] and s.M["meta"]["kosatsuba_well_ft"] > 0.0, "the drawn board's distance to its nearest well"


def test_a_waterside_board_bids_for_the_wellhead() -> None:
    """The `kosatsuba_siting` knob (feature 152): at `waterside` a verge near a well outbids the same count of dwellings
    away from it."""
    s = _hamlet(view=(0.0, 0.0, 1000.0, 800.0))
    s.M["meta"]["kosatsuba_siting"] = "waterside"
    s.M["lanes"] = [{"pts": [[100.0, 400.0], [900.0, 400.0]], "w": 5}]
    s.M["wells"] = [{"x": 820.0, "y": 440.0, "r": 4.0}, {"x": 700.0, "y": 440.0, "r": 4.0}]
    _house(s, 200.0, 440.0)
    spot = s.place_kosatsuba()
    assert spot is not None and spot[0] > 600.0, spot


def test_an_entrance_whose_every_seat_hides_its_caption_is_not_afforded() -> None:
    """Labels L1, L4: every seat the departures pass has its caption on ink - `entrance` is not sitable, and the knob
    resolves over the placements that are."""
    s = _entrance_hamlet(straggler=False)
    base = s.label_obstacles()
    base.add(Obstacle(tuple(rect(500.0, 500.0, 170.0, 170.0)), 1000.0))  # every caption seat round the handover
    s.label_obstacles = lambda: base  # type: ignore[method-assign]
    assert s.place_kosatsuba() is not None
    assert "entrance" in s.M["meta"]["kosatsuba_seat_unsitable"] and s.M["meta"]["kosatsuba_seat"] != "entrance"
