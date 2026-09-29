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
    street = [ln for ln in s.M["lanes"] if ln.get("street")]
    assert len(street) == 1 and street[0]["street_index"] == 0 and street[0]["w"] == 6
    assert street[0]["pts"][-1][0] >= 1299.0, "joined to the connector"


def test_street_run_out_leaves_the_sheet_from_the_nearer_end() -> None:
    run = street_run_out([(100.0, 500.0), (300.0, 500.0), (500.0, 500.0), (600.0, 500.0), (650.0, 500.0), (700.0, 500.0), (800.0, 500.0), (900.0, 500.0), (950.0, 500.0), (960.0, 500.0)], 1000.0, 1000.0)
    assert run[0] == (960.0, 500.0) and run[1][0] > 1000.0
    run = street_run_out([(40.0, 500.0), (300.0, 500.0), (900.0, 500.0)], 1000.0, 1000.0)
    assert run[0] == (40.0, 500.0) and run[1][0] < 0.0
    vertical = street_run_out([(500.0, 40.0), (500.0, 600.0)], 1000.0, 1000.0)
    assert vertical[1][1] < 0.0
