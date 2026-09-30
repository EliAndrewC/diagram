"""Feature 291 plan D17: a row village's streets (`ways/street.py`) and the road its street runs out on."""

from __future__ import annotations

from l7r.diagram.hamletgen.ways.street import join_to, lay_row_streets, street_span, thread
from l7r.diagram.hamletgen.ways.track import street_run_out
from l7r.diagram.settlement import Settlement

LINE = [(float(x), 500.0) for x in range(0, 1201, 8)]


def test_street_span_runs_from_the_first_farm_to_the_last() -> None:
    span = street_span(LINE, [(300.0, 560.0), (700.0, 440.0), (1150.0, 900.0)], reach=150.0, pad=50.0)
    assert 250.0 <= span[0][0] < 258.0 and 742.0 < span[-1][0] <= 750.0, "from the first farm less the pad to the last plus it; the farm 400 ft off is not the street's"
    assert all(b[0] - a[0] >= 40.0 for a, b in zip(span, span[1:-1], strict=False)), "thinned to a vertex every two treads"
    assert street_span(LINE, [(300.0, 2000.0)], reach=150.0, pad=50.0) == []
    assert street_span(LINE[:1], [(0.0, 500.0)], reach=150.0, pad=50.0) == []


def test_thread_keeps_a_clear_street_and_drops_a_vertex_inside_a_steading() -> None:
    path = [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0), (300.0, 0.0)]
    assert thread(path, [], [], []) == path
    wall = [(180.0, -20.0), (220.0, -20.0), (220.0, 20.0), (180.0, 20.0)]
    out = thread(path, [wall], [], [])
    assert (200.0, 0.0) not in out and out[0] == (0.0, 0.0) and out[-1] == (300.0, 0.0)
    assert thread([(200.0, 0.0), (201.0, 0.0)], [wall], [], []) == []


def test_join_to_reaches_the_network_from_the_nearer_end() -> None:
    path = [(0.0, 0.0), (100.0, 0.0)]
    net = [((300.0, -100.0), (300.0, 100.0))]
    joined = join_to(list(path), net, [], [], [])
    assert joined[:2] == path and joined[-1][0] == 300.0
    back = join_to(list(path), [((-200.0, -100.0), (-200.0, 100.0))], [], [], [])
    assert back[-2:] == path and back[0][0] == -200.0
    assert join_to(list(path), [], [], [], []) == path
    assert join_to(list(path), [((100.0, -5.0), (100.0, 5.0))], [], [], []) == path, "already touching"


def test_lay_row_streets_draws_each_planned_street_as_one_street_lane() -> None:
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    s._row_streets = [LINE]
    s.M["lanes"] = [{"pts": [[1300.0, 300.0], [1300.0, 700.0]], "w": 6, "connector": True}]
    houses = [{"x": 300.0, "y": 560.0}, {"x": 700.0, "y": 440.0}, {"x": 1000.0, "y": 560.0}]
    assert lay_row_streets(s, houses, [], [], [], reach=150.0, pad=50.0) == 1
    street = [ln for ln in s.M["lanes"] if ln.get("street") and ln.get("street_index") is not None]
    joins = [ln for ln in s.M["lanes"] if ln.get("street") and ln.get("street_index") is None]
    assert len(street) == 1 and street[0]["street_index"] == 0 and street[0]["w"] == 6
    assert len(joins) == 1 and joins[0]["pts"][0] == street[0]["pts"][-1] and joins[0]["pts"][-1][0] >= 1299.0, "joined to the connector by a way of its own"


def test_street_run_out_leaves_the_sheet_from_the_nearer_end() -> None:
    run = street_run_out(
        [(100.0, 500.0), (300.0, 500.0), (500.0, 500.0), (600.0, 500.0), (650.0, 500.0), (700.0, 500.0), (800.0, 500.0), (900.0, 500.0), (950.0, 500.0), (960.0, 500.0)], 1000.0, 1000.0
    )
    assert run[0] == (960.0, 500.0) and run[1][0] > 1000.0
    run = street_run_out([(40.0, 500.0), (300.0, 500.0), (900.0, 500.0)], 1000.0, 1000.0)
    assert run[0] == (40.0, 500.0) and run[1][0] < 0.0
    vertical = street_run_out([(500.0, 40.0), (500.0, 600.0)], 1000.0, 1000.0)
    assert vertical[1][1] < 0.0


def test_thread_routes_a_leg_still_grazing_once_more_a_foot_wider(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`thread`: a detour whose tread still meets a steading is routed again at a wider gap (cohort seed 23)."""
    from l7r.diagram.hamletgen.ways import street

    gaps: list[float] = []
    monkeypatch.setattr(street, "_crosses_fabric", lambda pts, walls, half: len(pts) == 2 and pts[0] != pts[1] or len(pts) > 2)
    monkeypatch.setattr(street, "_route", lambda a, b, hard, walls, water, gap: gaps.append(gap) or [a, ((a[0] + b[0]) / 2, a[1] + 50.0), b])
    out = thread([(0.0, 0.0), (100.0, 0.0)], [[(1.0, 1.0)]], [], [], half=4.0)
    assert gaps == [5.0, 7.0] and out[0] == (0.0, 0.0) and out[-1] == (100.0, 0.0)


def test_the_join_leg_is_what_join_to_added_at_either_end() -> None:
    from l7r.diagram.hamletgen.ways.street import join_leg

    path = [(0.0, 0.0), (10.0, 0.0)]
    assert join_leg(path, path) == []
    assert join_leg(path, [*path, (10.0, 5.0), (10.0, 9.0)]) == [(10.0, 0.0), (10.0, 5.0), (10.0, 9.0)]
    assert join_leg(path, [(-4.0, -3.0), *path]) == [(-4.0, -3.0), (0.0, 0.0)]


def test_a_further_street_joins_the_row_s_streets_not_the_road() -> None:
    """A second street's join ends on a street already laid - the connector's head stays the one entrance (settlement-review
    of Mizuguchi, 2026-09-30: the join met the road past the entrance board)."""
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    second = [(float(x), 800.0) for x in range(200, 1001, 40)]
    s._row_streets = [LINE, second]
    s.M["lanes"] = [{"pts": [[1300.0, 300.0], [1300.0, 900.0]], "w": 6, "connector": True}]
    houses = [{"x": 300.0, "y": 560.0}, {"x": 700.0, "y": 440.0}, {"x": 1000.0, "y": 560.0}, {"x": 400.0, "y": 860.0}, {"x": 800.0, "y": 860.0}]
    assert lay_row_streets(s, houses, [], [], [], reach=150.0, pad=50.0) == 2
    first = next(ln for ln in s.M["lanes"] if ln.get("street_index") == 0)
    joins = [ln for ln in s.M["lanes"] if ln.get("street") and ln.get("street_index") is None]
    end = joins[-1]["pts"][-1] if joins[-1]["pts"][0] in [ln["pts"][-1] for ln in s.M["lanes"] if ln.get("street_index") == 1] else joins[-1]["pts"][0]
    assert abs(end[1] - 500.0) < 2.0 and end[0] < 1299.0, f"on the first street, not the road: {end}"
    assert first["street_index"] == 0
