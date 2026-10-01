"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

from l7r.diagram import hamletgen as hg

from .._builders import SQUARE, a_plan
from ._builders import _hamlet_for_ways, _walled_settlement


def test_the_connector_track_leaves_the_frame_without_crossing_the_crop() -> None:
    """The guarantee is about the DRAWN path, not the straight line to its endpoint.

    This test used to assert the chord and is the reason it is worth spelling out: a track bows ~40
    px either side of its bearing, so chord and path disagree, and routing by the chord while
    drawing the bow is exactly how a connector came to be drawn through the rice with the router
    insisting it had checked."""
    plan = a_plan()
    plan.seat = hg.seat_cluster(plan)
    track = hg.connector_track(plan, (700.0, 200.0), avoid=[SQUARE])
    assert hg.path_violations(track, [SQUARE], None, []) == 0, "no segment of the drawn track may cross the crop"
    assert not (0 <= track[-1][0] <= plan.W and 0 <= track[-1][1] <= plan.H)  # ends off the canvas


def test_a_field_spur_that_folds_back_on_itself_is_cut_at_the_fold() -> None:
    """`spur_cut_at_the_fold`. A spur threaded round the steadings can double back; the smoothing pass then
    cuts the hairpin away and the hamlet's only path to its rice disappears with no record. So the fold is
    cut here, and what is left is drawn only while it still reaches the field."""
    from l7r.diagram.hamletgen.ways.track import spur_cut_at_the_fold

    near = [(120.0, -50.0), (220.0, -50.0), (220.0, 50.0), (120.0, 50.0)]
    straight = [(0.0, 0.0), (50.0, 0.0), (100.0, 0.0)]
    assert spur_cut_at_the_fold(straight, near) == (straight, None), "a spur that does not fold is drawn as threaded"

    folded = [(0.0, 0.0), (100.0, 0.0), (5.0, 3.0)]
    assert spur_cut_at_the_fold(folded, near) == ([(0.0, 0.0), (100.0, 0.0)], None), "the outward arm reaches the field, so it is kept and drawn"

    far = [(500.0, -50.0), (600.0, -50.0), (600.0, 50.0), (500.0, 50.0)]
    cut, why = spur_cut_at_the_fold(folded, far)
    assert cut == [(0.0, 0.0), (100.0, 0.0)]
    assert why and "short of the field" in why, "the arm stops in open ground, so the map says why it has no path to its rice"


def test_a_spur_cut_short_of_the_field_is_recorded_instead_of_drawn(monkeypatch) -> None:
    """The other half of `spur_cut_at_the_fold`, at the stage that uses it: where the fold leaves the outward
    arm short of the field, nothing is drawn and the map says why. A hamlet with no drawn way to its rice is a
    fact the manifest should carry - the reference hamlet's went missing for three review passes because the
    sweeps dropped it silently."""
    from l7r.diagram.hamletgen.ways import track

    s, plan = _walled_settlement()
    plan.seat = hg.seat_cluster(plan)
    monkeypatch.setattr(track, "spur_cut_at_the_fold", lambda pts, env: ([], "folded back short of the field - the test's own reason"))
    # the wall of houses leaves the connector no way out at all (`NoDryExit`, tested on its own below); this test is the spur's
    monkeypatch.setattr(track, "connector_dry_exit", lambda *a: [(1384.0, 700.0), (1600.0, 700.0)])
    track.stage_track(s, plan)
    assert "short of the field" in s.M["meta"].get("field_spur_swept", ""), "the map records why it has no path to its rice"
    assert not [ln for ln in s.M.get("lanes") or [] if ln.get("spur")], "and nothing is drawn for it"


def test_an_end_in_a_grove_band_leaves_it_toward_the_run_s_other_end() -> None:
    """`_out_of_bands` (feature 291). A spur that began at a deep band's middle (cohort seed 11) is set out of the band by
    the side it was heading for - walked toward the far end, with containment asked as well as the gap - and not into the
    yard behind it; a point already clear comes back untouched."""
    from l7r.diagram.hamletgen.ways.track import _out_of_bands

    band = [(0.0, 0.0), (40.0, 0.0), (40.0, 80.0), (0.0, 80.0)]
    assert _out_of_bands((-50.0, 40.0), [band], (-200.0, 40.0)) == (-50.0, 40.0), "clear ground is left alone"
    x, y = _out_of_bands((22.0, 40.0), [band], (-200.0, 40.0))
    assert x < -4.0 and y == 40.0, "out by the WEST side, toward the field, though the east edge is nearer"
    # where the far end lies inside the band too, the walk finds no ground and the nearest edge wins
    x2, _y2 = _out_of_bands((38.0, 40.0), [band], (20.0, 40.0))
    assert x2 > 40.0, "the nearest edge, a footpath's gap past it"


def test_water_crossings_counts_each_segment_crossing() -> None:
    """`_water_crossings`: the grove fallback takes a route that ignored the water only when it fords no more channels
    than the run it replaces."""
    from l7r.diagram.hamletgen.ways.track import _water_crossings

    lines = [((50.0, -10.0), (50.0, 10.0)), ((150.0, -10.0), (150.0, 10.0))]
    assert _water_crossings([(0.0, 0.0), (100.0, 0.0)], lines) == 1
    assert _water_crossings([(0.0, 0.0), (200.0, 0.0)], lines) == 2
    assert _water_crossings([(0.0, 50.0), (200.0, 50.0)], lines) == 0


def test_a_track_that_starts_in_a_grove_band_is_not_drawn_across_it() -> None:
    """`_thread_the_fabric`'s grove fallback (feature 291): a run from the middle of a farm's grove band, walled by
    steadings so the threaded route and the swing both fail, comes back clear of the band rather than as the raw run."""
    from l7r.diagram.hamletgen.ways import _crosses_fabric, _homestead_polys, _thread_the_fabric

    plan = a_plan()
    plan.seat = hg.seat_cluster(plan)
    s = _hamlet_for_ways()
    s.M["houses"] = [{"x": 760.0, "y": 500.0 + dy, "w": 60.0, "h": 40.0, "rot": 0.0, "kind": "plain"} for dy in range(0, 401, 40)]
    s.M["groves"] = [{"x": 700.0, "y": 700.0, "w": 40.0, "h": 80.0, "rot": 0.0, "of": [760.0, 700.0], "face": [-1, 0], "depth": "deep"}]
    run = [(700.0, 700.0), (500.0, 700.0)]
    out = _thread_the_fabric(s, plan, run)
    bands = [poly for poly, _owner, kind in _homestead_polys(s) if kind == "groves"]
    assert _crosses_fabric(list(run), bands, 0.0), "the run as it came crosses the band"
    assert len(out) >= 2 and not _crosses_fabric(out, bands, 0.0), "what is handed back does not"


def test_where_no_route_rounds_the_band_the_track_keeps_its_far_part(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The grove fallback's last resort (feature 291): with no route at all, what is kept is the run's FAR part, from its
    far end back to where it would first enter a band - clear of every band - and the web joins the near end."""
    from l7r.diagram.hamletgen.ways import _crosses_fabric, _homestead_polys, track

    plan = a_plan()
    plan.seat = hg.seat_cluster(plan)
    s = _hamlet_for_ways()
    s.M["houses"] = [{"x": 760.0, "y": 500.0 + dy, "w": 60.0, "h": 40.0, "rot": 0.0, "kind": "plain"} for dy in range(0, 401, 40)]
    s.M["groves"] = [{"x": 700.0, "y": 700.0, "w": 40.0, "h": 80.0, "rot": 0.0, "of": [760.0, 700.0], "face": [-1, 0], "depth": "deep"}]
    monkeypatch.setattr(track, "_route", lambda *a, **k: [])
    run = [(700.0, 700.0), (450.0, 700.0)]
    out = track._thread_the_fabric(s, plan, run)
    bands = [poly for poly, _owner, kind in _homestead_polys(s) if kind == "groves"]
    assert len(out) >= 2 and not _crosses_fabric(out, bands, 0.0)
    assert out[-1] == run[-1], "the far end is kept where it was"


def test_a_connector_with_no_dry_bearing_takes_the_dry_neck() -> None:
    """Feature 287, ways W23 (FR-005): where every bearing of the sweep crosses the wet, the least-bad one was drawn
    through the marsh. The flood fill finds the one dry neck instead, and the track has no wet violation."""
    from l7r.diagram.hamletgen.ways.checks import PathChecker
    from l7r.diagram.hamletgen.ways.track import wet_grown_by_the_lane

    plan = a_plan()
    plan.seat = hg.seat_cluster(plan)
    start = (700.0, 200.0)
    # a marsh boxing the start in on every side but a 60 ft neck at the north wall's west end (x 500-560)
    box = [
        [(560.0, 60.0), (920.0, 60.0), (920.0, 80.0), (560.0, 80.0)],
        [(480.0, 60.0), (500.0, 60.0), (500.0, 340.0), (480.0, 340.0)],
        [(900.0, 60.0), (920.0, 60.0), (920.0, 340.0), (900.0, 340.0)],
        [(480.0, 320.0), (920.0, 320.0), (920.0, 340.0), (480.0, 340.0)],
    ]
    track = hg.connector_track(plan, start, avoid=[SQUARE], wet=box)
    assert sum(PathChecker([wet_grown_by_the_lane(w)], None, ()).violations(track) for w in box) == 0, "not a foot of it in the wet"
    assert not (0 <= track[-1][0] <= plan.W and 0 <= track[-1][1] <= plan.H), "and it leaves the frame"


def test_a_gateway_with_no_dry_way_out_is_refused_by_name() -> None:
    import pytest

    from l7r.diagram.hamletgen.ways.track import NoDryExit

    plan = a_plan()
    plan.seat = hg.seat_cluster(plan)
    plan.sink_pond = (2000.0, 2000.0, 50.0, 40.0)
    ring = [[(480.0, 60.0), (920.0, 60.0), (920.0, 80.0), (480.0, 80.0)], [(480.0, 60.0), (500.0, 60.0), (500.0, 340.0), (480.0, 340.0)]]
    ring += [[(900.0, 60.0), (920.0, 60.0), (920.0, 340.0), (900.0, 340.0)], [(480.0, 320.0), (920.0, 320.0), (920.0, 340.0), (480.0, 340.0)]]
    with pytest.raises(NoDryExit):
        hg.connector_track(plan, (700.0, 200.0), avoid=[SQUARE], wet=ring)


def test_the_connector_takes_the_dry_exit_where_the_field_or_the_steadings_leave_no_clean_track(monkeypatch) -> None:
    """Feature 287, ways W24/W25: `route_around` refusing (None) or `_thread_the_fabric` handing back nothing both send
    the connector to the dry exit from the same gateway - never the track still across the field or a farmstead."""
    from l7r.diagram.hamletgen.ways import track

    s, plan = _walled_settlement()
    dry = [(1.0, 1.0), (-500.0, 1.0)]
    monkeypatch.setattr(track, "connector_dry_exit", lambda *a: dry)
    monkeypatch.setattr(track, "route_around", lambda *a: None)
    assert track.connector_through(s, plan, [(10.0, 10.0), (-900.0, 10.0)], [], [], [], []) == dry
    monkeypatch.setattr(track, "route_around", lambda poly, path, margin: path)
    monkeypatch.setattr(track, "_thread_the_fabric", lambda *a: [])
    assert track.connector_through(s, plan, [(10.0, 10.0), (-900.0, 10.0)], [], [], [], []) == dry
    monkeypatch.setattr(track, "_thread_the_fabric", lambda s, plan, run: run)
    assert track.connector_through(s, plan, [(10.0, 10.0), (-900.0, 10.0)], [], [], [], []) == [(10.0, 10.0), (-900.0, 10.0)]


def test_a_spur_with_no_way_clear_of_the_steadings_is_recorded_dropped(monkeypatch) -> None:
    """Feature 287, ways W25: the spur's threading hands back nothing rather than a run across a house, and the stage
    records the spur as dropped; the field path is the web's."""
    from l7r.diagram.hamletgen.ways import track

    s, plan = _walled_settlement()
    plan.seat = hg.seat_cluster(plan)
    monkeypatch.setattr(track, "_thread_the_fabric", lambda *a, **k: [])
    monkeypatch.setattr(track, "connector_dry_exit", lambda *a: [(1384.0, 700.0), (1600.0, 700.0)])
    track.stage_track(s, plan)
    assert "clear of the steadings" in s.M["meta"].get("field_spur_swept", "")
    assert not [ln for ln in s.M.get("lanes") or [] if ln.get("spur")]


def test_a_bearing_that_only_clips_the_field_is_kept_for_route_around() -> None:
    """A crop clip is the one fault the sweep may still hand back: `route_around` bends the drawn track round the field
    afterwards (ways W24). Walled in by crop on every side but dry and clear of the steadings, the best bearing stands."""
    plan = a_plan()
    plan.seat = hg.seat_cluster(plan)
    fence = [[(480.0, 60.0), (920.0, 60.0), (920.0, 80.0), (480.0, 80.0)], [(480.0, 60.0), (500.0, 60.0), (500.0, 340.0), (480.0, 340.0)]]
    fence += [[(900.0, 60.0), (920.0, 60.0), (920.0, 340.0), (900.0, 340.0)], [(480.0, 320.0), (920.0, 320.0), (920.0, 340.0), (480.0, 340.0)]]
    track = hg.connector_track(plan, (700.0, 200.0), avoid=fence)
    assert hg.path_violations(track, fence, None, []) > 0 and track[0] == (700.0, 200.0)


def test_the_gateway_stands_on_the_exit_strip_the_seating_reserved() -> None:
    """Feature 287, plan M4b: the connector leaves along the exit strip, measured from the strip's own start (the seat's
    center) rather than the cloud's mean, so a corridor the web draws along the strip meets the track."""
    from l7r.diagram.hamletgen.ways import _cluster_gateway
    from l7r.diagram.settlement import Settlement, seg_dist

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="G", scale="hamlet", ftpx=1, down_deg=90)
    seat = {"cx": 500.0, "cy": 500.0, "along": (1.0, 0.0), "out": (0.0, 1.0), "half": 200.0, "depth": 80.0}
    s.M["houses"] += [{"x": 560.0, "y": 520.0, "w": 50.0, "h": 30.0}, {"x": 640.0, "y": 470.0, "w": 50.0, "h": 30.0}]
    off = _cluster_gateway(s, seat, (0.0, 0.0))
    assert off[0] == 600.0, "without a strip, abreast of the cloud's mean"
    s.M["access_exit"] = [[500.0, 500.0], [500.0, 900.0]]
    on = _cluster_gateway(s, seat, (0.0, 0.0))
    assert seg_dist(on[0], on[1], (500.0, 500.0), (500.0, 900.0)) < 1e-9 and on[1] > 520.0, "on the strip, past the cloud"


def _box_on(a, b):
    """A 40 x 28 ft building's box standing on the middle of the leg a-b."""
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    return (mx - 20.0, my - 14.0, mx + 20.0, my + 14.0)


def test_the_connector_sweep_refuses_a_bearing_with_a_house_on_it_and_takes_the_next() -> None:
    """Ways, the connector half of break-mid-run: the swept bearing a track would leave by has a house on its first leg
    (the violating case - `law.breaks_through` names it), and with the house in the fabric the sweep takes the next
    bearing, whose drawn legs keep `TRACK_FABRIC_GAP` off it and run through no building."""
    from l7r.diagram.hamletgen.consts import TRACK_FABRIC_GAP
    from l7r.diagram.hamletgen.ways import law
    from l7r.diagram.hamletgen.ways.fabric import _fabric_hits

    plan = a_plan()
    plan.seat = hg.seat_cluster(plan)
    free = hg.connector_track(plan, (700.0, 200.0), avoid=[SQUARE])
    box = _box_on(free[0], free[1])
    assert law.breaks_through(free, [box]), "the violating case: the ideal bearing runs through the house"
    quad = law.solid_quads({"houses": [{"x": (box[0] + box[2]) / 2, "y": (box[1] + box[3]) / 2, "w": 40.0, "h": 28.0}]})
    track = hg.connector_track(plan, (700.0, 200.0), avoid=[SQUARE], fabric=quad)
    assert track != free and law.breaks_through(track, [box]) == [] and _fabric_hits(track, quad, TRACK_FABRIC_GAP) == 0


def test_a_connector_through_a_building_or_over_the_brook_twice_takes_the_dry_exit(monkeypatch) -> None:
    """`connector_keeps_the_law` decides the drawn connector: a run whose long leg stands in a building's box, or that
    crosses the brook twice, is refused and the dry exit (walled by the same boxes, crossing no water) is drawn instead."""
    from l7r.diagram.hamletgen.ways import track

    s, plan = _walled_settlement()
    run = [(10.0, 10.0), (-900.0, 10.0)]
    assert track.connector_keeps_the_law({"houses": []}, run)
    through = {"houses": [{"x": -445.0, "y": 10.0, "w": 40.0, "h": 28.0}]}
    assert not track.connector_keeps_the_law(through, run), "a leg through a house"
    twice = {"streams": [{"poly": [[-100.0, -50.0], [-200.0, 50.0], [-300.0, -50.0]]}]}
    assert not track.connector_keeps_the_law(twice, run), "over the brook and back"
    assert track.connector_keeps_the_law({"streams": [{"poly": [[-100.0, -50.0], [-100.0, 50.0]]}]}, run), "once is a crossing"
    dry = [(1.0, 1.0), (-500.0, 1.0)]
    monkeypatch.setattr(track, "connector_dry_exit", lambda *a: dry)
    monkeypatch.setattr(track, "route_around", lambda poly, path, margin: path)
    monkeypatch.setattr(track, "_thread_the_fabric", lambda s, plan, run: run)
    from l7r.diagram.hamletgen.ways import law

    s.M["streams"] = [{"poly": [[-300.0, -200.0], [-500.0, 200.0]], "w": 6.0}]  # the brook, crossed once, 27 degrees off square
    assert law.oblique_crossings({**s.M, "lanes": [{"pts": run}]}), "the threaded run crosses it oblique"
    squared = track.connector_through(s, plan, run, [], [], [], [])
    assert squared != run and law.oblique_crossings({**s.M, "lanes": [{"pts": squared}]}) == [], "drawn and judged square"
    s.M["streams"] = []
    s.M["houses"].append({"x": -445.0, "y": 10.0, "w": 40.0, "h": 28.0})
    assert track.connector_through(s, plan, run, [], [], [], []) == dry


def test_the_gateway_stands_past_every_corridor_on_the_strip_and_on_it_clear_of_the_field() -> None:
    """Feature 287 wave 6: the web draws the exit strip as a tree lane from its innermost attachment to the connector's start
    (`tree.strip_run`), so the connector starts ON the strip - along the strip's own bearing where it was turned off the
    seat's outward one - no nearer the center than the farthest corridor hanging from it, and walked out along the strip
    until the field's envelope leaves it clear (`gate_on_the_strip`)."""
    from l7r.diagram.hamletgen.ways import track
    from l7r.diagram.settlement import Settlement, seg_dist

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="G", scale="hamlet", ftpx=1, down_deg=90)
    seat = {"cx": 500.0, "cy": 500.0, "along": (1.0, 0.0), "out": (0.0, 1.0), "half": 200.0, "depth": 80.0}
    s.M["houses"] += [{"x": 560.0, "y": 520.0, "w": 50.0, "h": 30.0}]
    s.M["access_exit"] = [[500.0, 500.0], [900.0, 900.0]]  # turned 45 degrees off the seat's outward bearing
    s.M["access_corridors"] = [{"pts": [[600.0, 700.0], [650.0, 650.0]], "of": [620.0, 720.0]}, {"pts": [[1.0, 1.0]]}]
    g = track._cluster_gateway(s, seat, (0.0, 0.0))
    assert seg_dist(g[0], g[1], (500.0, 500.0), (900.0, 900.0)) < 1e-6 and g[0] > 650.0, "on the strip, past the corridor at (650, 650)"
    field = [(650.0, 650.0), (760.0, 650.0), (760.0, 760.0), (650.0, 760.0)]
    on = track.gate_on_the_strip(s, field, (700.0, 703.0))
    assert on == track.push_out_of(field, on, track.SPUR_SETBACK) and abs(on[0] - on[1]) < 1e-9 and on[0] > 760.0, "walked out along it"
    assert track.gate_on_the_strip(s, [(0.0, 0.0), (1000.0, 0.0), (1000.0, 1000.0), (0.0, 1000.0)], (600.0, 600.0)) == (900.0, 900.0), "to its end at most"
    del s.M["access_exit"]
    assert track.gate_on_the_strip(s, field, (700.0, 703.0)) == track.push_out_of(field, (700.0, 703.0), track.SPUR_SETBACK)


def test_a_connector_start_a_few_feet_off_the_strip_is_set_back_on_it_and_one_folding_on_it_is_refused() -> None:
    """The threading can move the connector's start a few feet off the strip (cohort seed 37: 8 ft), and the strip drawn up
    to it ended in a hook: `on_the_strip` sets it back on its foot where the connector still keeps the law. And a connector
    leaving the strip turned back on it is refused (`folds_on_the_strip`): the fold at the two tree lanes' joint no repair
    could mend."""
    from l7r.diagram.hamletgen.ways import track

    M = {"meta": {"ftpx": 1.0}, "access_exit": [[0.0, 0.0], [400.0, 0.0]]}
    assert track.on_the_strip(M, [(300.0, 8.0), (300.0, 900.0)]) == [(300.0, 0.0), (300.0, 900.0)]
    assert track.on_the_strip(M, [(300.0, 30.0), (300.0, 900.0)]) == [(300.0, 30.0), (300.0, 900.0)], "too far off: as it came"
    assert track.on_the_strip(M, [(300.0, 0.0), (300.0, 900.0)]) == [(300.0, 0.0), (300.0, 900.0)]
    assert track.on_the_strip({"meta": {}}, [(1.0, 1.0), (2.0, 2.0)]) == [(1.0, 1.0), (2.0, 2.0)]
    assert track.on_the_strip(M, [(300.0, 5.0), (0.0, 5.0), (-10.0, -500.0)]) == [(300.0, 5.0), (0.0, 5.0), (-10.0, -500.0)], "moved it would fold"
    assert track.folds_on_the_strip(M, [(400.0, 0.0), (10.0, 5.0)]) and not track.folds_on_the_strip(M, [(400.0, 0.0), (900.0, 50.0)])
    assert not track.folds_on_the_strip(M, [(400.0, 50.0), (0.0, 50.0)]), "off the strip"
    assert not track.folds_on_the_strip(M, [(400.0, 0.0), (400.0, 0.0)]) and not track.folds_on_the_strip({}, [(0.0, 0.0), (1.0, 1.0)])
    assert not track.connector_keeps_the_law(M, [(400.0, 0.0), (10.0, 5.0)])


def test_a_point_is_pushed_clear_of_every_band_it_stands_in_or_near() -> None:
    """`clear_of_bands` (feature 291 on 287): the dry exit's start set clear of a band; a clear point is left."""
    from l7r.diagram.hamletgen.ways.track import clear_of_bands
    from l7r.diagram.settlement import edge_dist, point_in_poly

    band = [(0.0, 0.0), (200.0, 0.0), (200.0, 40.0), (0.0, 40.0)]
    q = clear_of_bands((100.0, 20.0), [band], 12.0)
    assert not point_in_poly(q[0], q[1], band) and edge_dist(q[0], q[1], band) >= 11.9
    assert clear_of_bands((100.0, 200.0), [band], 12.0) == (100.0, 200.0)
