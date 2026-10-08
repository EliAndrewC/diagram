"""The ways ask the registry of what stands (feature 287 M8): every lane the web lays, re-lays or carries on is admitted by
the overlap matrix before it is written, each placer on constructed input INCLUDING the violating case - a garden, a
yard, a well in the lane's way, its own household's too."""

from __future__ import annotations

import pytest

from l7r.diagram.hamletgen.ways import bund as B
from l7r.diagram.hamletgen.ways import law, settle
from l7r.diagram.overlap.registry import OverlapRefused

from ._builders import Registered

# a household's garden bed and threshing yard straddling y = 100 at x = 200, its house north of them
BED = {"x": 200.0, "y": 100.0, "w": 20.0, "h": 20.0, "rot": 0.0, "of": [200.0, 60.0]}
YARD = {"x": 240.0, "y": 100.0, "w": 30.0, "h": 20.0, "rot": 0.0, "of": [200.0, 60.0]}


def _with_bed(lanes=(), **kw):  # type: ignore[no-untyped-def]
    s = Registered(lanes=lanes, **kw)
    s.M["gardens"] = [dict(BED)]
    return s


def test_the_lane_law_names_a_tread_over_a_bed_its_own_households_too() -> None:
    """`fouled_segment` asks the registry (`forbidden_segment`): a door path is exempt from its own steading's yard and bed
    in the fabric test, and the matrix is not - a path arrives at its dooryard, it does not cross its own bed."""
    s = _with_bed()
    run = [(100.0, 150.0), (150.0, 100.0), (300.0, 100.0)]
    assert settle.fouled_segment(run, 3.0, [], [], [], (), s.M) == 1
    assert settle.fouled_segment(run, 3.0, [], [], [], ()) is None, "without the registry nothing names it"
    assert settle.fouled_segment([(100.0, 150.0), (300.0, 150.0)], 3.0, [], [], [], (), s.M) is None


def test_the_settle_cuts_a_lane_off_a_bed_and_a_rewrite_the_matrix_refuses_is_not_written() -> None:
    s = _with_bed(lanes=[[(0.0, 0.0), (0.0, 50.0)]])
    s.M["lanes"][0]["connector"] = True
    s.lane([(100.0, 300.0), (100.0, 200.0)], width=3)
    lane = s.M["lanes"][1]
    assert settle.apply_pieces(s, {1: [[(100.0, 300.0), (200.0, 100.0)], [(400.0, 400.0), (500.0, 400.0)]]}) == 1
    assert lane["pts"] == [[100.0, 300.0], [100.0, 200.0]] and len(s.M["lanes"]) == 2, "refused: the lane as it was, no piece added"
    with pytest.raises(OverlapRefused):
        lane["pts"] = [[100.0, 300.0], [200.0, 100.0]]  # a write that did not ask is refused by the record itself


def test_a_nub_is_kept_where_the_straightened_lane_would_cross_a_bed() -> None:
    """`_drop_end_nubs` with nothing in the fabric: the straightened run crosses a garden bed the dogleg kept clear of."""
    from l7r.diagram.hamletgen.ways.sweeps import _drop_end_nubs

    s = Registered(lanes=[[(0.0, 0.0), (2.0, 5.0), (100.0, 5.0)]])
    s.M["gardens"] = [{"x": 50.0, "y": -1.0, "w": 10.0, "h": 4.0, "rot": 0.0}]
    _drop_end_nubs(s, [[(900.0, 900.0), (901.0, 900.0), (901.0, 901.0)]])
    assert [tuple(p) for p in s.M["lanes"][0]["pts"]] == [(0.0, 0.0), (2.0, 5.0), (100.0, 5.0)]


def test_a_splice_the_matrix_refuses_draws_the_link_as_its_own_lane() -> None:
    from l7r.diagram.hamletgen.ways.touch import _join_piece

    s = Registered(lanes=[[(500.0, 500.0), (600.0, 500.0)]], strict=False)
    lanes = [s.standing.kept("lanes", {"pts": [[0.0, 0.0], [100.0, 0.0]], "w": 5})]
    s.M["lanes"].append(lanes[0])
    s.M["gardens"] = [{"x": 100.0, "y": 30.0, "w": 6.0, "h": 6.0, "rot": 0.0}]  # on the link's line (a non-strict map: the link is still laid)
    link = [(100.0, 0.0), (100.0, 45.0)]
    _join_piece(s, lanes, 0, [(0.0, 0.0), (100.0, 0.0)], (100.0, 0.0), link, [], [], [], [])
    assert lanes[0]["pts"] == [[0.0, 0.0], [100.0, 0.0]], "the splice over the bed is refused; the piece stands as it was"


def test_a_smoothing_rewrite_the_registry_refuses_is_not_committed() -> None:
    from l7r.diagram.hamletgen.ways.smooth import admits_lane, commit_lane

    s = _with_bed(lanes=[[(100.0, 300.0), (100.0, 200.0)]])
    lanes = s.M["lanes"]
    assert not commit_lane(lanes, 0, [[100.0, 300.0], [200.0, 100.0]], [], [], [], s.reink_lane, admits_lane(s))
    assert lanes[0]["pts"] == [[100.0, 300.0], [100.0, 200.0]]
    assert commit_lane(lanes, 0, [[100.0, 300.0], [100.0, 250.0]], [], [], [], s.reink_lane, admits_lane(s))


def test_a_connector_fold_onto_a_bed_is_refused() -> None:
    from l7r.diagram.hamletgen.ways.joints import fold_the_connector_hairpin

    s = Registered(lanes=[[(2055.3, 25.3), (1408.0, -20.4)], [(1929.1, 56.4), (2054.3, 40.0), (2055.3, 25.3)]])
    s.M["lanes"][0]["connector"] = True
    s.M["gardens"] = [{"x": 1930.5, "y": 36.0, "w": 6.0, "h": 6.0, "rot": 0.0}]  # under the lane's new link to the connector's side (feature 328)
    assert fold_the_connector_hairpin(s) == 0


def test_a_web_lane_over_a_bed_is_not_drawn() -> None:
    from l7r.diagram.hamletgen.ways.fabric import _draw_web

    s = _with_bed()
    assert not _draw_web(s, [(100.0, 100.0), (300.0, 100.0)], 3)
    assert _draw_web(s, [(100.0, 200.0), (300.0, 200.0)], 3)


def test_a_way_on_to_the_bund_is_not_carried_over_a_bed() -> None:
    """`a_way_onto_the_bund`: the nearest end's run on to the paddy (and the end carried over a canal) is written only where
    the registry admits the lane as it would become; here a bed stands on both, so the field path is drawn as a branch."""
    from .test_bund import _field_M

    run = Registered(lanes=[[(0.0, 0.0), (0.0, 50.0)], [(100.0, 100.0), (300.0, 100.0)]])
    run.M["lanes"][0]["connector"] = True
    run.M.update(_field_M())
    run.M["cemeteries"] = [{"x": 350.0, "y": 100.0, "w": 10.0, "h": 10.0, "rot": 0.0}]  # ground the run-on's own blocks do not read
    assert B.a_way_onto_the_bund(run) != "run_on" and run.M["lanes"][1]["pts"] == [[100.0, 100.0], [300.0, 100.0]]
    canal = Registered(lanes=[[(0.0, 0.0), (0.0, 50.0)], [(200.0, 100.0), (395.0, 100.0)]])
    canal.M["lanes"][0]["connector"] = True
    canal.M.update(_field_M())
    canal.M["streams"] = [{"poly": [[398.0, -100.0], [398.0, 400.0]], "w": 2}]
    canal.M["gardens"] = [{"x": 402.0, "y": 100.0, "w": 2.0, "h": 2.0, "rot": 0.0}]  # on the bund, where the carried end stops
    assert B.a_way_onto_the_bund(canal) != "run_on" and len(canal.M["lanes"][1]["pts"]) == 2


def test_the_connector_keeps_off_what_the_matrix_forbids_a_way_on() -> None:
    from l7r.diagram.hamletgen.ways import track

    s = Registered()
    run = [(10.0, 10.0), (-900.0, 10.0)]
    assert track.connector_keeps_the_law(s.M, run)
    s.M["wells"] = [{"x": -300.0, "y": 10.0, "r": 8, "vr": 12.4}]
    assert not track.connector_keeps_the_law(s.M, run), "a well on the track"


def test_the_field_router_walls_what_the_matrix_forbids_and_leaves_its_own_dooryard_open() -> None:
    from l7r.diagram.hamletgen.ways.corridors import field_router

    s = Registered(houses=[(200.0, 60.0)])
    s.M["threshing_yards"] = [dict(YARD)]
    s.M["cemeteries"] = [{"x": 500.0, "y": 100.0, "w": 60.0, "h": 200.0, "rot": 0.0}]
    route = field_router(s, [])
    run = route((400.0, 100.0), (600.0, 100.0))
    assert run and not law.lanes_over_fixtures({**s.M, "lanes": [{"pts": run}]})
    assert all(not (470.0 < x < 530.0 and 0.0 < y < 200.0) for x, y in run), "round the burial ground, not through it"
    assert route((240.0, 100.0), (240.0, 300.0)), "a route from its own yard leaves it"
    assert route((200.0, 75.0), (200.0, 300.0)), "...and one from a step off its own front wall"


def test_the_web_walls_a_reserved_seat_at_the_buffer_less_its_own_margin() -> None:
    from l7r.diagram.hamletgen.consts import WEB_FABRIC_GAP
    from l7r.diagram.hamletgen.ways.web import seat_wall_reach

    s = Registered()
    s.standing.reserved.reserve_seats([(0.0, 0.0)], 22.0, 15.0)
    assert seat_wall_reach(s) == pytest.approx(15.0 + 1.5 + 0.2 - WEB_FABRIC_GAP)
    s.standing.reserved.lane_buffer = 0.0
    assert seat_wall_reach(s) == 1.0
