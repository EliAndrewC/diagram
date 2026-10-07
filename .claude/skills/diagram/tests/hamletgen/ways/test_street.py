"""Feature 291 plan D17: a row village's streets (`ways/street.py`) and the road its street runs out on."""

from __future__ import annotations

import math
import random

from l7r.diagram.hamletgen.ways.street import _line_chunks, _nearest_within, brook_bounds, drawn_span, join_to, lay_row_streets, row_reach, street_run_out, street_span, thread
from l7r.diagram.settlement import Settlement, seg_closest, seg_dist

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
    assert lay_row_streets(s, houses, [], [], []) == 1
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
    assert lay_row_streets(s, houses, [], [], []) == 2
    first = next(ln for ln in s.M["lanes"] if ln.get("street_index") == 0)
    joins = [ln for ln in s.M["lanes"] if ln.get("street") and ln.get("street_index") is None]
    end = joins[-1]["pts"][-1] if joins[-1]["pts"][0] in [ln["pts"][-1] for ln in s.M["lanes"] if ln.get("street_index") == 1] else joins[-1]["pts"][0]
    assert abs(end[1] - 500.0) < 2.0 and end[0] < 1299.0, f"on the first street, not the road: {end}"
    assert first["street_index"] == 0


def test_a_street_is_cut_to_its_outermost_joints() -> None:
    """`to_its_joints` / `cut_between` (feature 291 on 287): the stretch between the outermost lane ends standing on it;
    unchanged with no joint on it; `trim_streets` re-lays a row's street so and leaves every other lane."""
    from l7r.diagram.hamletgen.ways.street import cut_between, nearest_on, to_its_joints, trim_streets

    street = [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0), (300.0, 0.0)]
    assert to_its_joints(street, [(50.0, 2.0), (250.0, -3.0), (150.0, 90.0)], 4.0) == [(50.0, 0.0), (100.0, 0.0), (200.0, 0.0), (250.0, 0.0)]
    assert to_its_joints(street, [(150.0, 90.0)], 4.0) == street, "no joint on it: as it is"
    assert cut_between(street, [0.0, 100.0, 200.0, 300.0], 0.0, 300.0) == street
    assert nearest_on(street, (120.0, 30.0)) == (120.0, 0.0) and nearest_on(street[:1], (0.0, 0.0)) is None
    s = Settlement(400, 200, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1)
    for pts, w, extra in (
        (street, 6, {"street": True, "street_index": 0}),
        ([(50.0, 2.0), (50.0, 60.0)], 3, {"serves": [50.0, 90.0]}),
        ([(250.0, -3.0), (250.0, -60.0)], 3, {"serves": [250.0, -90.0]}),
        ([(0.0, 150.0), (300.0, 150.0)], 3, {}),
    ):
        s.lane(list(pts), width=w)
        s.M["lanes"][-1].update(extra)
    assert trim_streets(s, 4.0) == 1
    assert s.M["lanes"][0]["pts"][0][0] == 50.0 and s.M["lanes"][0]["pts"][-1][0] == 250.0
    assert trim_streets(s, 4.0) == 0, "cut already"
    s.M["lanes"][0]["pts"] = [list(p) for p in street]
    assert trim_streets(s, 4.0, [(280.0, 10.0), (150.0, 60.0)], 12.0) == 1, "a door 10 ft off the street, taking no path"
    assert s.M["lanes"][0]["pts"][0][0] == 50.0 and s.M["lanes"][0]["pts"][-1][0] == 280.0, "kept to that door; the far one is no joint"


def test_a_street_s_one_end_is_cut_back_to_its_last_joint() -> None:
    """`end_to_its_joint` (feature 293 on 291): the named end only, to the joint nearest it; the other end as it is, and the
    street as it is with no joint on it."""
    from l7r.diagram.hamletgen.ways.street import end_to_its_joint

    street = [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0), (300.0, 0.0)]
    joints = [(50.0, 2.0), (250.0, -3.0), (150.0, 90.0)]
    assert end_to_its_joint(street, joints, 4.0, -1) == [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0), (250.0, 0.0)]
    assert end_to_its_joint(street, joints, 4.0, 0) == [(50.0, 0.0), (100.0, 0.0), (200.0, 0.0), (300.0, 0.0)]
    assert end_to_its_joint(street, [(150.0, 90.0)], 4.0, -1) == street, "no joint on it: as it is"


def test_the_first_street_is_carried_on_to_the_road_it_nearly_meets() -> None:
    """`meet_the_road` (feature 291 on 287): a street ending within the reach of the road's start is carried on to it, from
    whichever end is nearer; one that meets it, or stands beyond the reach, is left; a degenerate street or road too."""
    from l7r.diagram.hamletgen.ways.street import meet_the_road

    street = [(0.0, 0.0), (100.0, 0.0)]
    assert meet_the_road(street, [(116.0, 0.0), (400.0, -200.0)]) == [*street, (116.0, 0.0)]
    assert meet_the_road(street, [(-20.0, 0.0), (-300.0, 0.0)]) == [(-20.0, 0.0), *street]
    assert meet_the_road(street, [(100.2, 0.0), (400.0, 0.0)]) == street, "already meets"
    assert meet_the_road(street, [(400.0, 0.0), (800.0, 0.0)]) == street, "beyond the reach"
    assert meet_the_road(street[:1], [(1.0, 0.0), (2.0, 0.0)]) == street[:1]


def test_a_join_leg_loses_a_hook_at_either_end() -> None:
    """`unhooked_both` (feature 291 on 287, cohort seed 901): a short first or last leg the leg turns back from goes."""
    from l7r.diagram.hamletgen.ways.street import unhooked_both

    assert unhooked_both([(0.0, 0.0), (5.0, 0.0), (5.0, -50.0)]) == [(0.0, 0.0), (5.0, -50.0)]
    assert unhooked_both([(5.0, -50.0), (5.0, 0.0), (0.0, 0.0)]) == [(5.0, -50.0), (0.0, 0.0)]
    assert unhooked_both([(0.0, 0.0), (80.0, 0.0)]) == [(0.0, 0.0), (80.0, 0.0)]


def test_a_join_the_law_refuses_is_searched_from_either_end(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Feature 291 (cohort seed 904), driven since feature 294's rolls stopped reaching it: when the nearest join leg is
    unlawful, the lawful join is searched from either end of the street as a door path is."""
    from l7r.diagram.hamletgen.ways import street

    class Never:
        def __init__(self, *a, **k) -> None:  # type: ignore[no-untyped-def]
            pass

        def __call__(self, *a, **k) -> bool:  # type: ignore[no-untyped-def]
            return False

    searched: list[object] = []
    monkeypatch.setattr(street, "Lawful", Never)
    monkeypatch.setattr(street, "door_path", lambda s, e, *a: searched.append(e) or None)
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    s._row_streets = [LINE]
    s.M["lanes"] = [{"pts": [[1300.0, 300.0], [1300.0, 900.0]], "w": 6, "connector": True}]
    houses = [{"x": 300.0, "y": 560.0}, {"x": 700.0, "y": 440.0}, {"x": 1000.0, "y": 560.0}]
    lay_row_streets(s, houses, [], [], [])
    assert len(searched) == 2, "both ends searched when neither yields a lawful join"


def test_the_drawn_span_is_the_streets_own_farms_at_their_reach() -> None:
    """What the road runs out from (`track.stage_track`) and the web lays (`lay_row_streets`): the stretch over the street's
    own farms, at 1.5 frames' reach and half a frame past its end farms - not the whole planned line (cohort seed 22)."""
    s = Settlement(1400, 1400, seed=3)
    assert drawn_span(s, 0, []) == []
    s._row_streets = [LINE]
    farms = [{"x": 300.0, "y": 560.0, "geom": {"bbox": (0.0, 0.0, 200.0, 120.0)}}, {"x": 700.0, "y": 440.0}]
    assert row_reach(farms) == (300.0, 100.0) and row_reach([]) == (1.5 * 240.0, 120.0)  # no farms: 0033's 240 ft row holding as the frame (feature 328 wave 8)
    span = drawn_span(s, 0, farms)
    assert 200.0 <= span[0][0] < 208.0 and 792.0 < span[-1][0] <= 800.0
    s._row_street_farms = [[(700.0, 440.0)]]
    assert 600.0 <= drawn_span(s, 0, farms)[0][0] < 608.0, "its own farms, as seated"
    assert drawn_span(s, 1, farms) == []


def test_the_run_past_an_end_farm_stops_short_of_the_brook() -> None:
    """A planned street's run past its end farm stops a ford's landing (22 ft) short of where it would cross the brook, never
    short of the end farm itself; a crossing between its farms is left to it (`brook_bounds`). Cohort seed 11: the half frame
    past the last farm took a row's street over the brook 11 degrees off its course, 46 ft from the nearest ford, and the
    squared crossing kinked - a tree lane the web was refused for."""
    farms = [(300.0, 560.0), (700.0, 440.0)]
    shallow = [(600.0, 530.0), (880.0, 470.0)]  # crosses the street at x = 740, 40 ft past the last farm, 12 degrees off it
    span = street_span(LINE, farms, reach=150.0, pad=50.0, brook=shallow)
    assert 710.0 <= span[-1][0] <= 718.0 and 250.0 <= span[0][0] < 258.0, "stopped 22 ft short of the crossing; the far end as it was"
    assert 288.0 <= street_span(LINE, farms, reach=150.0, pad=50.0, brook=[(220.0, 400.0), (300.0, 600.0)])[0][0] < 296.0, "the first end too"
    assert street_span(LINE, farms, reach=150.0, pad=50.0, brook=[(710.0, 400.0), (710.0, 600.0)])[-1][0] >= 692.0, "never short of the end farm (to its sample)"
    between = street_span(LINE, farms, reach=150.0, pad=50.0, brook=[(500.0, 400.0), (500.0, 600.0)])
    assert between == street_span(LINE, farms, reach=150.0, pad=50.0), "a crossing between its farms is the street's own"
    s = Settlement(1400, 1400, seed=3)
    s._row_streets = [LINE]
    assert 710.0 <= drawn_span(s, 0, [{"x": x, "y": y} for x, y in farms], shallow)[-1][0] <= 718.0, "the road and the web read the same span"


def _old_nearest(h, line):
    """`street_span`'s farm-to-line measure as it stood before feature 306: every segment of the line, the first on a tie."""
    return min(((seg_dist(h[0], h[1], a, b), i) for i, (a, b) in enumerate(zip(line, line[1:], strict=False))), key=lambda t: t[0])


def _old_span(line, houses, reach, pad, brook=()):
    """`street_span` as it stood before feature 306 - the oracle the indexed form is held to."""
    if len(line) < 2:
        return []
    arc = [0.0]
    for a, b in zip(line, line[1:], strict=False):
        arc.append(arc[-1] + math.dist(a, b))
    along = []
    for h in houses:
        best = _old_nearest(h, line)
        if best[0] > reach:
            continue
        i = best[1]
        q = seg_closest(h[0], h[1], line[i], line[i + 1])
        along.append(arc[i] + math.dist(line[i], q))
    if not along:
        return []
    lo, hi = brook_bounds(line, arc, min(along), max(along), max(0.0, min(along) - pad), min(arc[-1], max(along) + pad), brook)
    idx = [i for i, u in enumerate(arc) if lo <= u <= hi]
    kept = []
    for i in idx:
        if not kept or arc[i] - arc[kept[-1]] >= 40.0:
            kept.append(i)
    if idx and kept[-1] != idx[-1]:
        kept.append(idx[-1])
    return [line[i] for i in kept]


def test_the_indexed_span_is_the_old_scan() -> None:
    """Feature 306: each farm asks only the segments whose box widened by `reach` holds it, and the span is the old scan's -
    bent lines, a farm exactly `reach` off the line, and a farm equidistant from two segments (the lower index, as `min`
    chose)."""
    rng = random.Random(306)
    for _ in range(200):
        x, y, line = rng.uniform(0, 300), rng.uniform(300, 700), []
        for _k in range(rng.randint(2, 120)):
            line.append((x, y))
            x, y = x + rng.uniform(4, 12), y + rng.uniform(-6, 6)
        houses = [(rng.uniform(-50, 1500), rng.uniform(200, 800)) for _ in range(rng.randint(0, 40))]
        reach, pad = rng.choice((60.0, 120.0, 150.0)), rng.choice((20.0, 50.0))
        assert street_span(line, houses, reach, pad) == _old_span(line, houses, reach, pad)
    # a line that wanders and doubles back: a run's box stands near a farm its own segments do not, so the nearest box is not
    # the nearest run, and pruning the next box at the best distance so far is what is held exact
    for _ in range(200):
        x, y, line = 500.0, 500.0, []
        for _k in range(rng.randint(2, 200)):
            line.append((x, y))
            ang = rng.uniform(0, 2 * math.pi)
            x, y = x + 10 * math.cos(ang), y + 10 * math.sin(ang)
        hs = [(rng.uniform(380, 620), rng.uniform(380, 620)) for _ in range(30)]
        kept = [n if n[0] <= 150.0 else None for n in (_nearest_within(h, line, _line_chunks(line), 150.0) for h in hs)]
        assert kept == [n if n[0] <= 150.0 else None for n in (_old_nearest(h, line) for h in hs)], "the same farms kept, at the same segment"
        assert street_span(line, hs, 150.0, 20.0) == _old_span(line, hs, 150.0, 20.0)
    assert street_span(LINE, [(300.0, 650.0)], 150.0, 50.0) == _old_span(LINE, [(300.0, 650.0)], 150.0, 50.0) != []
    chunks = _line_chunks(LINE)
    # (512, 520) stands over the vertex shared by segments 63 and 64, which close two different boxes: the tie across them
    assert _nearest_within((512.0, 520.0), LINE, chunks, 150.0) == _old_nearest((512.0, 520.0), LINE) == (20.0, 63)
    assert _nearest_within((304.0, 520.0), LINE, chunks, 150.0) == _old_nearest((304.0, 520.0), LINE) == (20.0, 37)
    assert _nearest_within((300.0, 2000.0), LINE, chunks, 150.0) == (math.inf, -1)


def test_the_oracle_catches_a_dropped_segment() -> None:
    """The comparison above has teeth: boxes that lose the run holding the nearest segment answer differently from the old
    scan."""
    chunks = _line_chunks(LINE)
    lossy = [c for c in chunks if not c[0] <= 37 < c[1]]
    h = (300.0, 520.0)  # over segment 37, (296, 500)-(304, 500)
    assert _nearest_within(h, LINE, chunks, 150.0) == _old_nearest(h, LINE)
    assert _nearest_within(h, LINE, lossy, 150.0) != _old_nearest(h, LINE)
