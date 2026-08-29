"""tier town tests split out of `tests.tools.test_site_justice` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import json
import math

import pytest

from l7r.diagram import settlement
from l7r.diagram.tools import site_justice as sj
from tests.tools.test_site_justice import WALL, city, town


@pytest.mark.tiers("town")
def test_boundary_marker_footprint_is_the_drawn_marker_box():
    # A real stone is ~3 ft - sub-glyph at every tier - so what can collide is the DRAWN box.
    assert sj.footprint_px(town(), "boundary_marker") == (settlement.BOUNDARY_MARKER_MIN_PX, settlement.BOUNDARY_MARKER_MIN_PX)


@pytest.mark.tiers("city", "town")
def test_record_carries_the_fields_each_kind_needs():
    eg = sj.record(town(), "execution_ground", 100, 200, rot=8)
    assert (eg["x"], eg["y"], eg["rot"], eg["screened"]) == (100.0, 200.0, 8, False)
    assert sj.record(city(), "execution_ground", 100, 200)["screened"] is True  # a city ground is hoarded
    bm = sj.record(town(), "boundary_marker", 100, 200)
    assert bm["w"] == bm["h"] == settlement.BOUNDARY_MARKER_FT  # TRUE footprint recorded...
    assert bm["vw"] == bm["vh"] == settlement.BOUNDARY_MARKER_MIN_PX  # ...alongside the drawn box


@pytest.mark.tiers("town")
def test_with_replaces_only_the_one_registry():
    M = town()
    trial = sj._with(M, "execution_ground", [sj.record(M, "execution_ground", 1, 2)])
    assert len(trial["execution_grounds"]) == 1
    assert not M.get("execution_grounds")  # the caller's manifest is untouched
    assert trial["houses"] is M["houses"]  # and the rest is shared, not copied


@pytest.mark.tiers("town")
def test_view_box_prefers_the_recorded_view_and_falls_back_to_the_canvas():
    assert sj.view_box(town()) == (0.0, 0.0, 2400.0, 2000.0)
    M = town()
    M["meta"]["view"] = [100, 200, 300, 400]
    assert sj.view_box(M) == (100.0, 200.0, 400.0, 600.0)


@pytest.mark.tiers("town")
def test_frame_cost_is_zero_inside_the_content_box_and_grows_outside_it():
    M = town()
    box = sj.content_box(M, "execution_ground")
    assert sj.frame_cost(M, "execution_ground", (box[0] + box[2]) / 2, (box[1] + box[3]) / 2, box=box) == 0
    out = sj.frame_cost(M, "execution_ground", box[2] + 200, (box[1] + box[3]) / 2, box=box)
    assert out == pytest.approx(230.0)  # 200 past the edge + the ground's own half-width


@pytest.mark.tiers("town")
def test_frame_cost_computes_its_own_box_when_not_given_one():
    M = town()
    assert sj.frame_cost(M, "execution_ground", 1200, 1000) == sj.frame_cost(M, "execution_ground", 1200, 1000, box=sj.content_box(M, "execution_ground"))


@pytest.mark.tiers("town")
def test_routes_collects_every_kind_of_way():
    M = town(town_streets=[{"pts": [[0, 0], [10, 10]], "w": 26}], lanes=[{"pts": [[5, 5], [6, 6]], "w": 8}])
    assert len(sj.routes(M)) == 3  # the road + the street + the lane


@pytest.mark.tiers("town")
def test_way_out_distance_measures_roads_gates_and_the_single_gate():
    assert sj.way_out_distance(town(), 500, 1040) == pytest.approx(40.0)
    assert sj.way_out_distance(town(gates=[[500, 1200]]), 500, 1150) == pytest.approx(50.0)
    assert sj.way_out_distance(town(gate=[500, 1300]), 500, 1250) == pytest.approx(50.0)


@pytest.mark.tiers("town")
def test_way_out_distance_is_infinite_with_nothing_to_measure_to():
    M = town()
    del M["road"]
    assert sj.way_out_distance(M, 0, 0) == math.inf


@pytest.mark.tiers("town")
def test_outside_the_wall_treats_an_unwalled_map_as_all_outside():
    assert sj.outside_the_wall(town(), 1000, 1000)
    assert not sj.outside_the_wall(town(wall=WALL), 1000, 1000)
    assert sj.outside_the_wall(town(wall=WALL), 100, 100)


@pytest.mark.tiers("town")
def test_rank_key_puts_each_feature_on_its_own_side_of_the_wall():
    M = town(wall=WALL)
    box = sj.content_box(M, "execution_ground")
    inside, outside = (1000.0, 1000.0), (200.0, 200.0)
    assert sj.rank_key(M, "execution_ground", outside, box)[0] < sj.rank_key(M, "execution_ground", inside, box)[0]
    assert sj.rank_key(M, "punishment_spot", inside, box)[0] < sj.rank_key(M, "punishment_spot", outside, box)[0]


@pytest.mark.tiers("town")
def test_rank_key_prefers_beside_the_way_out_over_on_it():
    # Ranking by nearest-to-the-road puts candidates in the carriageway first; the band does not.
    M = town()
    box = sj.content_box(M, "execution_ground")
    on_road, beside = (1700.0, 1000.0), (1700.0, 1050.0)
    assert sj.rank_key(M, "execution_ground", beside, box)[2] < sj.rank_key(M, "execution_ground", on_road, box)[2]


@pytest.mark.tiers("town")
def test_candidates_grid_stays_inside_the_view_with_room_for_the_footprint():
    M = town()
    w, h = sj.footprint_px(M, "execution_ground")
    pts = sj.candidates(M, "execution_ground", 200.0)
    assert pts
    assert all(w <= x <= 2400 - w and h <= y <= 2000 - h for x, y in pts)


@pytest.mark.tiers("town")
def test_propose_returns_only_seats_the_gate_accepts():
    seats = sj.propose(town(), "execution_ground", limit=12, step=120.0)
    assert seats
    M = town()
    base = sj.failures(sj._with(M, "execution_ground", []))
    for s in seats:
        assert not sj.new_failures(M, "execution_ground", s["x"], s["y"], base)


@pytest.mark.tiers("town")
def test_report_names_the_seats_it_found():
    out = sj.report(town(), "execution_ground", 12, None, step=120.0)
    assert "adjudicating" in out and "frame_cost" in out


@pytest.mark.tiers("town")
def test_report_judges_a_stone_against_the_chosen_ground():
    # With a ground pinned, the stone is adjudicated against THAT ground rather than against
    # whatever the manifest happened to carry.
    out = sj.report(town(), "boundary_marker", 8, (1700.0, 1060.0), step=200.0)
    assert "boundary_marker" in out


@pytest.mark.tiers("town")
def test_main_rejects_an_unknown_kind(tmp_path, capsys):
    f = tmp_path / "m.json"
    f.write_text(json.dumps(town()))
    assert sj.main([str(f), "gallows"]) == 2
    assert "unknown kind" in capsys.readouterr().out


@pytest.mark.tiers("town")
def test_main_reports_seats(tmp_path, capsys):
    f = tmp_path / "m.json"
    f.write_text(json.dumps(town()))
    assert sj.main([str(f), "execution_ground", "--limit=6", "--step=200"]) == 0
    assert "adjudicating" in capsys.readouterr().out


@pytest.mark.tiers("town")
def test_main_accepts_a_pinned_ground(tmp_path, capsys):
    f = tmp_path / "m.json"
    f.write_text(json.dumps(town()))
    assert sj.main([str(f), "boundary_marker", "--limit=4", "--ground=1700,1060"]) == 0
    assert "adjudicating" in capsys.readouterr().out
