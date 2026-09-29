"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

from l7r.diagram import hamletgen as hg

from .._builders import SQUARE, a_plan
from ._builders import _walled_settlement


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
