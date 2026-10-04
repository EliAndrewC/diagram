"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

import pytest

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


_RICE = [(600.0, 1250.0), (800.0, 1250.0), (800.0, 1350.0), (600.0, 1350.0)]  # a field south of the wall of houses


def _spur_drawn_from(monkeypatch, arm):  # type: ignore[no-untyped-def]
    """`stage_track` on the walled settlement with a field (`_RICE`), the fold cut handing back `arm`: (settlement, spur)."""
    from l7r.diagram.hamletgen.ways import track

    s, plan = _walled_settlement()
    s.M.setdefault("fields", []).append({"outline": [list(q) for q in _RICE]})
    plan.seat = hg.seat_cluster(plan)
    monkeypatch.setattr(track, "spur_cut_at_the_fold", lambda pts, env: (list(arm), None))
    monkeypatch.setattr(track, "connector_dry_exit", lambda *a: [(1384.0, 700.0), (1600.0, 700.0)])
    track.stage_track(s, plan)
    return s, next((ln for ln in s.M.get("lanes") or [] if ln.get("spur")), None)


def test_a_spur_whose_kept_arm_ends_in_the_rice_is_drawn_to_the_bund(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Feature 304 T03 (cohort seed 905): the threading moved the spur's bow 20 ft into a paddy plot and the fold cut kept the
    arm out to it, across the main ditch at the field's head where no deck lands dry - `bridges()` raised. The DRAWN tip is
    set on the bund (269 B04): pulled back out of the worked ground, the tread's half-width and a foot clear of its edge."""
    from l7r.diagram.hamletgen.ways.geom import worked_ground

    s, spur = _spur_drawn_from(monkeypatch, [(700.0, 1150.0), (700.0, 1300.0)])
    assert spur is not None, "the spur is drawn"
    tip = (float(spur["pts"][-1][0]), float(spur["pts"][-1][1]))
    ground = worked_ground(s.M)
    assert not ground.inside(tip), "its tip is not in the rice"
    assert 3.4 <= ground.dist(tip) <= 5.0, f"it stops on the bund, not short of it: {ground.dist(tip):.1f} ft off the edge"


def test_a_spur_whose_kept_arm_is_all_rice_is_recorded_dropped(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """...and an arm in the worked ground end to end leaves nothing to draw: the spur is recorded dropped, the field path the
    web's."""
    s, spur = _spur_drawn_from(monkeypatch, [(700.0, 1270.0), (700.0, 1320.0)])
    assert spur is None
    assert "in the worked ground end to end" in s.M["meta"].get("field_spur_swept", "")


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


def test_the_gateway_stands_abreast_of_the_cloud_past_its_downslope_edge() -> None:
    """Feature 287, plan M4b, as feature 320 leaves it (no exit strip): the gateway is measured from the placed houses - abreast
    of the cloud's mean, past its downslope edge."""
    from l7r.diagram.hamletgen.ways import _cluster_gateway
    from l7r.diagram.settlement import Settlement

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="G", scale="hamlet", ftpx=1, down_deg=90)
    seat = {"cx": 500.0, "cy": 500.0, "along": (1.0, 0.0), "out": (0.0, 1.0), "half": 200.0, "depth": 80.0}
    s.M["houses"] += [{"x": 560.0, "y": 520.0, "w": 50.0, "h": 30.0}, {"x": 640.0, "y": 470.0, "w": 50.0, "h": 30.0}]
    g = _cluster_gateway(s, seat, (0.0, 0.0))
    assert g[0] == 600.0 and g[1] > 520.0, "abreast of the cloud's mean, past its downslope edge"


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


def test_the_connector_starts_clear_of_the_field() -> None:
    """`gate_out_of_the_field`: the connector's start pushed out of the field's envelope by `SPUR_SETBACK`; a start already
    clear stays."""
    from l7r.diagram.hamletgen.ways import track

    field = [(650.0, 650.0), (760.0, 650.0), (760.0, 760.0), (650.0, 760.0)]
    on = track.gate_out_of_the_field(field, (700.0, 703.0))
    assert on == track.push_out_of(field, (700.0, 703.0), track.SPUR_SETBACK) and on != (700.0, 703.0)
    assert track.gate_out_of_the_field(field, (100.0, 100.0)) == (100.0, 100.0)


def test_the_recorded_track_is_the_track_out_the_homesteads_stage_chose() -> None:
    """Feature 320 (FR-008): `recorded_track` reads the track out the homesteads stage chose once the last house stood
    (`way_out_track`); none where it is absent or under two points."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.ways import track

    assert track.recorded_track(SimpleNamespace(M={"way_out_track": [[0.0, 0.0], [40.0, 0.0]]})) == [(0.0, 0.0), (40.0, 0.0)]
    assert track.recorded_track(SimpleNamespace(M={})) is None and track.recorded_track(SimpleNamespace(M={"way_out_track": [[0.0, 0.0]]})) is None


def _the_choice_watched(monkeypatch, polder: bool):  # type: ignore[no-untyped-def]
    """`choose_track_out` on the walled settlement with its sweeps replaced by recorders: (track, calls)."""
    from l7r.diagram.hamletgen.consts import POLDER_ARCHETYPES
    from l7r.diagram.hamletgen.ways import gateway, track

    s, plan = _walled_settlement()
    plan.seat = hg.seat_cluster(plan)
    if polder:
        plan.field_archetype = sorted(POLDER_ARCHETYPES)[0]
    calls: dict = {}

    def swept(name):  # type: ignore[no-untyped-def]
        def run(*a, **k):  # type: ignore[no-untyped-def]
            calls[name] = (a, k)
            return [(1.0, 2.0), (3.0, 4.0)]

        return run

    monkeypatch.setattr(track, "connector_track", swept("connector_track"))
    monkeypatch.setattr(gateway, "gateway_track", swept("gateway_track"))
    monkeypatch.setattr(track, "connector_through", lambda s, plan, run, *a: [*run, (9.0, 9.0)])
    return track.choose_track_out(s, plan), calls, s, plan


def test_the_track_out_is_chosen_once_by_the_gateway_on_a_valley_and_the_sweep_on_a_polder(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Feature 320 (FR-008): `choose_track_out` is the track's whole course in one choice - the gateway's track on a valley,
    the connector's sweep from the gate on a polder - then threaded through the steadings (`connector_through`); the gate is
    the cluster's gateway out of the field, and the grove bands are handed to the dry exit."""
    from l7r.diagram.hamletgen.ways import track

    got, calls, s, plan = _the_choice_watched(monkeypatch, polder=False)
    assert got == [(1.0, 2.0), (3.0, 4.0), (9.0, 9.0)] and set(calls) == {"gateway_track"}, "a valley: the gateway's track, threaded"
    gate = calls["gateway_track"][0][4]
    assert gate == track.gate_out_of_the_field(plan.envelope, gate), "the gate stands out of the field"
    assert plan.grove_bands == [p for p, _o, k in track._homestead_polys(s) if k == "groves"]
    got, calls, s, plan = _the_choice_watched(monkeypatch, polder=True)
    assert got == [(1.0, 2.0), (3.0, 4.0), (9.0, 9.0)] and set(calls) == {"connector_track"}, "a polder: the sweep from the gate"
    assert calls["connector_track"][1]["avoid"][0] == list(plan.envelope)


@pytest.mark.parametrize("polder", [False, True])
def test_stage_track_draws_the_recorded_track_as_chosen_on_both_branches(monkeypatch, polder: bool) -> None:  # type: ignore[no-untyped-def]
    """Feature 320 (FR-008): where the homesteads stage recorded the track out, `stage_track` draws exactly it as the connector
    and chooses nothing again - on the valley branch and the polder branch alike."""
    from l7r.diagram.hamletgen.consts import POLDER_ARCHETYPES
    from l7r.diagram.hamletgen.ways import track

    s, plan = _walled_settlement()
    plan.seat = hg.seat_cluster(plan)
    if polder:
        plan.field_archetype = sorted(POLDER_ARCHETYPES)[0]
    s.M["way_out_track"] = [[1384.0, 700.0], [1500.0, 700.0], [1600.0, 700.0]]
    monkeypatch.setattr(track, "choose_track_out", lambda *a: pytest.fail("chosen again"))
    monkeypatch.setattr(track, "connector_dry_exit", lambda *a: [(1384.0, 700.0), (1600.0, 700.0)])
    track.stage_track(s, plan)
    con = [ln for ln in s.M.get("lanes") or [] if ln.get("connector")]
    assert len(con) == 1 and [tuple(q) for q in con[0]["pts"]] == [(1384.0, 700.0), (1500.0, 700.0), (1600.0, 700.0)]


def test_a_point_is_pushed_clear_of_every_band_it_stands_in_or_near() -> None:
    """`clear_of_bands` (feature 291 on 287): the dry exit's start set clear of a band; a clear point is left."""
    from l7r.diagram.hamletgen.ways.track import clear_of_bands
    from l7r.diagram.settlement import edge_dist, point_in_poly

    band = [(0.0, 0.0), (200.0, 0.0), (200.0, 40.0), (0.0, 40.0)]
    q = clear_of_bands((100.0, 20.0), [band], 12.0)
    assert not point_in_poly(q[0], q[1], band) and edge_dist(q[0], q[1], band) >= 11.9
    assert clear_of_bands((100.0, 200.0), [band], 12.0) == (100.0, 200.0)


def test_a_walled_in_gateway_is_left_on_a_turned_bearing(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Feature 315 (cohort seed 19): where the sweep from the gateway finds no dry way out, the track leaves from the first
    gateway on a bearing turned off the downslope whose sweep finds one (`turned_gateway_track`); none, and it is refused."""
    from l7r.diagram.hamletgen.ways import gateway as tr

    class _S:
        M: dict = {}

    walled = {(0.0, 0.0)}

    def sweep(plan, start, **_k):  # type: ignore[no-untyped-def]
        if tuple(start) in walled:
            raise tr.NoDryExit("walled")
        return [start, (start[0] + 500.0, start[1])]

    monkeypatch.setattr(tr, "connector_track", sweep)
    turns: list[float] = []

    def gateway(s, seat, band, deg=0.0):  # type: ignore[no-untyped-def]
        turns.append(deg)
        return (0.0, 0.0) if deg != -60.0 else (5.0, 5.0)

    monkeypatch.setattr(tr, "_cluster_gateway", gateway)
    monkeypatch.setattr(tr, "gate_out_of_the_field", lambda env, g: g)

    class _P:
        envelope: list = []

    got = tr.turned_gateway_track(_S(), _P(), {}, (0.0, 0.0), [], [], [], [])  # type: ignore[arg-type]
    assert got[0] == (5.0, 5.0) and turns == [30.0, -30.0, 60.0, -60.0], "the nearest turn whose sweep is dry"
    walled.add((5.0, 5.0))
    with pytest.raises(tr.NoDryExit):
        tr.turned_gateway_track(_S(), _P(), {}, (0.0, 0.0), [], [], [], [])  # type: ignore[arg-type]


def test_the_gateway_track_falls_back_only_when_the_sweep_is_walled(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Feature 315: `gateway_track` - the sweep's track where it is dry; walled, a turned bearing."""
    from l7r.diagram.hamletgen.ways import gateway as tr

    class _S:
        M: dict = {}

    monkeypatch.setattr(tr, "turned_gateway_track", lambda *a: ["turned"])
    monkeypatch.setattr(tr, "connector_track", lambda plan, start, **k: [start])
    assert tr.gateway_track(_S(), None, {}, (0.0, 0.0), (1.0, 1.0), [], [], [], []) == [(1.0, 1.0)]  # type: ignore[arg-type]

    def walled(plan, start, **k):  # type: ignore[no-untyped-def]
        raise tr.NoDryExit("walled")

    monkeypatch.setattr(tr, "connector_track", walled)
    assert tr.gateway_track(_S(), None, {}, (0.0, 0.0), (1.0, 1.0), [], [], [], []) == ["turned"]  # type: ignore[arg-type]


def test_a_turned_gateway_leaves_the_cloud_on_its_own_bearing() -> None:
    """Feature 315: `_cluster_gateway(..., turn_deg)` walks out on the seat's outward bearing turned by `turn_deg`: turned a
    right angle, the gateway leaves the cloud's side, not its downslope edge."""
    from l7r.diagram.hamletgen.ways import track as tr
    from l7r.diagram.settlement import Settlement

    s = Settlement(2000, 2000, seed=1)
    s.meta(name="G", scale="hamlet", ftpx=1)
    s.M["houses"] = [{"x": 1000.0 + 60.0 * k, "y": 1000.0, "w": 40.0, "h": 28.0} for k in range(5)]
    seat = {"along": (1.0, 0.0), "out": (0.0, 1.0)}
    down = tr._cluster_gateway(s, seat, (0.0, 0.0))
    side = tr._cluster_gateway(s, seat, (0.0, 0.0), 90.0)
    assert down[1] > 1000.0 and abs(down[0] - 1120.0) < 1.0, "downslope: below the cloud's middle"
    assert abs(side[1] - 1000.0) < 1.0 and abs(side[0] - 1120.0) > 20.0, "turned a right angle: off to the side"


def test_a_gateway_on_a_well_is_stepped_clear_of_it() -> None:
    """Feature 315, cohort seed 28: a gateway 9 px inside a farm's well walled every dry exit in. It is stepped out past half the
    connector's tread from what forbids a way; a reserved wood seat is not such a footprint, and no registry leaves it be."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.ways import gateway
    from l7r.diagram.hamletgen.ways.track import CONNECTOR_WIDTH
    from l7r.diagram.settlement import edge_dist

    well = [(0.0, 0.0), (20.0, 0.0), (20.0, 20.0), (0.0, 20.0)]
    seat = [(30.0, 0.0), (60.0, 0.0), (60.0, 20.0), (30.0, 20.0)]
    st = SimpleNamespace(forbidding=lambda key: [("wells", well), ("wood seat", seat)])
    s = SimpleNamespace(M=SimpleNamespace(standing=st))
    g = gateway.clear_of_what_stands(s, (10.0, 11.0))
    assert edge_dist(g[0], g[1], well) >= CONNECTOR_WIDTH / 2.0 - 1e-6 and g != (10.0, 11.0)
    assert gateway.clear_of_what_stands(s, (45.0, 10.0)) == (45.0, 10.0), "a wood seat the way out may take"
    assert gateway.clear_of_what_stands(SimpleNamespace(M={}), (10.0, 11.0)) == (10.0, 11.0)
