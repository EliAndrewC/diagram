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
