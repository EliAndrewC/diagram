"""The track threaded through the fabric (`ways/thread.py`, lifted out of `track.py` at the 1,000-line bar, 405 T09): the
spur's fold, a track's end out of a grove band, the water count, and `_thread_the_fabric`'s fallbacks. A test patches
`_route` or `_out_of_bands` on `thread`, where `_thread_the_fabric` looks them up."""

from .._builders import a_plan, a_seat
from ._builders import _hamlet_for_ways

_FIELD_AWAY = [(1400.0, 1400.0), (1600.0, 1400.0), (1600.0, 1600.0), (1400.0, 1600.0)]


def test_a_field_spur_that_folds_back_on_itself_is_cut_at_the_fold() -> None:
    """`spur_cut_at_the_fold`. A spur threaded round the steadings can double back; the smoothing pass then
    cuts the hairpin away and the hamlet's only path to its rice disappears with no record. So the fold is
    cut here, and what is left is drawn only while it still reaches the field."""
    from l7r.diagram.hamletgen.ways.thread import spur_cut_at_the_fold

    near = [(104.0, -50.0), (220.0, -50.0), (220.0, 50.0), (104.0, 50.0)]  # 4 ft past the arm's end: within 0014's 6 ft join (405 T22)
    straight = [(0.0, 0.0), (50.0, 0.0), (100.0, 0.0)]
    assert spur_cut_at_the_fold(straight, near) == (straight, None), "a spur that does not fold is drawn as threaded"

    folded = [(0.0, 0.0), (100.0, 0.0), (5.0, 3.0)]
    assert spur_cut_at_the_fold(folded, near) == ([(0.0, 0.0), (100.0, 0.0)], None), "the outward arm reaches the field, so it is kept and drawn"

    far = [(500.0, -50.0), (600.0, -50.0), (600.0, 50.0), (500.0, 50.0)]
    cut, why = spur_cut_at_the_fold(folded, far)
    assert cut == [(0.0, 0.0), (100.0, 0.0)]
    assert why and "short of the field" in why, "the arm stops in open ground, so the map says why it has no path to its rice"


def test_an_end_in_a_grove_band_leaves_it_toward_the_run_s_other_end() -> None:
    """`_out_of_bands` (feature 291). A spur that began at a deep band's middle (cohort seed 11) is set out of the band by
    the side it was heading for - walked toward the far end, with containment asked as well as the gap - and not into the
    yard behind it; a point already clear comes back untouched."""
    from l7r.diagram.hamletgen.ways.thread import _out_of_bands

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
    from l7r.diagram.hamletgen.ways.thread import _water_crossings

    lines = [((50.0, -10.0), (50.0, 10.0)), ((150.0, -10.0), (150.0, 10.0))]
    assert _water_crossings([(0.0, 0.0), (100.0, 0.0)], lines) == 1
    assert _water_crossings([(0.0, 0.0), (200.0, 0.0)], lines) == 2
    assert _water_crossings([(0.0, 50.0), (200.0, 50.0)], lines) == 0


def test_a_track_that_starts_in_a_grove_band_is_not_drawn_across_it() -> None:
    """`_thread_the_fabric`'s grove fallback (feature 291): a run from the middle of a farm's grove band, walled by
    steadings so the threaded route and the swing both fail, comes back clear of the band rather than as the raw run."""
    from l7r.diagram.hamletgen.ways import _crosses_fabric, _homestead_polys, _thread_the_fabric

    plan = a_plan()
    plan.seat = a_seat(plan)
    plan.envelope = list(_FIELD_AWAY)  # the field off the scene: no house or grove stands in it (405 T09 walls it)
    s = _hamlet_for_ways()
    s.M["houses"] = [{"x": 760.0, "y": 500.0 + dy, "w": 60.0, "h": 40.0, "rot": 0.0, "kind": "plain"} for dy in range(0, 401, 40)]
    s.M["groves"] = [{"x": 700.0, "y": 700.0, "w": 40.0, "h": 80.0, "rot": 0.0, "of": [760.0, 700.0], "face": [-1, 0], "depth": "deep"}]
    run = [(700.0, 700.0), (500.0, 700.0)]
    out = _thread_the_fabric(s, plan, run)
    bands = [poly for poly, _owner, kind in _homestead_polys(s) if kind == "groves"]
    assert _crosses_fabric(list(run), bands, 0.0), "the run as it came crosses the band"
    assert len(out) >= 2 and not _crosses_fabric(out, bands, 0.0), "what is handed back does not"


def test_the_grove_fallback_s_route_round_the_band_is_taken(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The grove fallback's own route (feature 291; feature 385 T109): where the threaded route finds nothing, a route round the
    bands - held at 0036's room by the grown bands - is what comes back. Since T109 grew the bands in the first route too, no
    roll reaches this return, so the test pins it: the threaded route refused, the fallback's route is taken as found."""
    from l7r.diagram.hamletgen.ways import _crosses_fabric, _homestead_polys, thread, track

    plan = a_plan()
    plan.seat = a_seat(plan)
    plan.envelope = list(_FIELD_AWAY)  # the field off the scene: no house or grove stands in it (405 T09 walls it)
    s = _hamlet_for_ways()
    s.M["houses"] = [{"x": 760.0, "y": 500.0 + dy, "w": 60.0, "h": 40.0, "rot": 0.0, "kind": "plain"} for dy in range(0, 401, 40)]
    s.M["groves"] = [{"x": 700.0, "y": 700.0, "w": 40.0, "h": 80.0, "rot": 0.0, "of": [760.0, 700.0], "face": [-1, 0], "depth": "deep"}]
    round_it = [(660.0, 700.0), (660.0, 620.0), (450.0, 620.0)]
    calls: list[int] = []

    def route(*a, **k):  # type: ignore[no-untyped-def]
        calls.append(1)
        return [] if len(calls) == 1 else list(round_it)

    monkeypatch.setattr(thread, "_route", route)
    monkeypatch.setattr(thread, "_out_of_bands", lambda p, bands, toward: round_it[0] if p == (700.0, 700.0) else p)
    out = track._thread_the_fabric(s, plan, [(700.0, 700.0), (450.0, 620.0)])
    bands = [poly for poly, _owner, kind in _homestead_polys(s) if kind == "groves"]
    assert out == round_it and not _crosses_fabric(out, bands, 0.0), "the fallback's route, as found"


def test_the_grove_fallback_s_route_across_a_crop_plot_is_not_taken(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Feature 405 T09: the grove fallback's later routes left the crop out of their walls, so a route round the band could
    cross row crops (0081: never). Each is now taken only where it crosses no crop plot: the same route as the test above,
    with a plot on its middle leg, is refused, and what comes back crosses no plot."""
    from l7r.diagram.hamletgen.ways import _crosses_fabric, thread, track

    plan = a_plan()
    plan.seat = a_seat(plan)
    plan.envelope = list(_FIELD_AWAY)  # the field off the scene: no house or grove stands in it (405 T09 walls it)
    s = _hamlet_for_ways()
    s.M["houses"] = [{"x": 760.0, "y": 500.0 + dy, "w": 60.0, "h": 40.0, "rot": 0.0, "kind": "plain"} for dy in range(0, 401, 40)]
    s.M["groves"] = [{"x": 700.0, "y": 700.0, "w": 40.0, "h": 80.0, "rot": 0.0, "of": [760.0, 700.0], "face": [-1, 0], "depth": "deep"}]
    plot = [(540.0, 610.0), (570.0, 610.0), (570.0, 630.0), (540.0, 630.0)]
    s.M["dry_plots"] = [{"poly": [list(v) for v in plot]}]
    round_it = [(660.0, 700.0), (660.0, 620.0), (450.0, 620.0)]
    calls: list[int] = []

    def route(*a, **k):  # type: ignore[no-untyped-def]
        calls.append(1)
        return [] if len(calls) == 1 else list(round_it)

    monkeypatch.setattr(thread, "_route", route)
    monkeypatch.setattr(thread, "_out_of_bands", lambda p, bands, toward: round_it[0] if p == (700.0, 700.0) else p)
    out = track._thread_the_fabric(s, plan, [(700.0, 700.0), (450.0, 620.0)])
    assert _crosses_fabric(round_it, [plot], 0.0), "the route found crosses the plot"
    assert out != round_it and not (len(out) >= 2 and _crosses_fabric(out, [plot], 0.0)), "it is not what comes back"


def test_where_no_route_rounds_the_band_the_track_keeps_its_far_part(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The grove fallback's last resort (feature 291): with no route at all, what is kept is the run's FAR part, from its
    far end back to where it would first enter a band - clear of every band - and the web joins the near end."""
    from l7r.diagram.hamletgen.ways import _crosses_fabric, _homestead_polys, thread, track

    plan = a_plan()
    plan.seat = a_seat(plan)
    plan.envelope = list(_FIELD_AWAY)  # the field off the scene: no house or grove stands in it (405 T09 walls it)
    s = _hamlet_for_ways()
    s.M["houses"] = [{"x": 760.0, "y": 500.0 + dy, "w": 60.0, "h": 40.0, "rot": 0.0, "kind": "plain"} for dy in range(0, 401, 40)]
    s.M["groves"] = [{"x": 700.0, "y": 700.0, "w": 40.0, "h": 80.0, "rot": 0.0, "of": [760.0, 700.0], "face": [-1, 0], "depth": "deep"}]
    monkeypatch.setattr(thread, "_route", lambda *a, **k: [])
    run = [(700.0, 700.0), (450.0, 700.0)]
    out = track._thread_the_fabric(s, plan, run)
    bands = [poly for poly, _owner, kind in _homestead_polys(s) if kind == "groves"]
    assert len(out) >= 2 and not _crosses_fabric(out, bands, 0.0)
    assert out[-1] == run[-1], "the far end is kept where it was"


def test_the_grove_fallback_s_route_across_the_field_is_not_taken_but_one_ending_on_its_edge_is(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Feature 405 T09 (round 1): the first route walls the field and the fallbacks did not, so a route round a band could cross
    the flooded paddy (0081: a lane stops at it). A route across a paddy (a field's outline) is refused; one that only ends on its
    edge, as a spur ends on the bund, is taken (`_inner` draws each end in 3 ft before the test)."""
    from l7r.diagram.hamletgen.ways import thread, track

    plan = a_plan()
    plan.seat = a_seat(plan)
    s = _hamlet_for_ways()
    s.M["houses"] = [{"x": 760.0, "y": 500.0 + dy, "w": 60.0, "h": 40.0, "rot": 0.0, "kind": "plain"} for dy in range(0, 401, 40)]
    s.M["groves"] = [{"x": 700.0, "y": 700.0, "w": 40.0, "h": 80.0, "rot": 0.0, "of": [760.0, 700.0], "face": [-1, 0], "depth": "deep"}]
    round_it = [(660.0, 700.0), (660.0, 620.0), (450.0, 620.0)]
    monkeypatch.setattr(thread, "_out_of_bands", lambda p, bands, toward: round_it[0] if p == (700.0, 700.0) else p)
    calls: list[int] = []

    def route(*a, **k):  # type: ignore[no-untyped-def]
        calls.append(1)
        return [] if len(calls) == 1 else list(round_it)

    monkeypatch.setattr(thread, "_route", route)
    s.M["fields"] = [{"outline": [[500.0, 600.0], [600.0, 600.0], [600.0, 640.0], [500.0, 640.0]]}]  # a paddy astride the middle leg
    assert track._thread_the_fabric(s, plan, [(700.0, 700.0), (450.0, 620.0)]) != round_it
    calls.clear()
    s.M["fields"] = [{"outline": [[300.0, 600.0], [450.0, 600.0], [450.0, 640.0], [300.0, 640.0]]}]  # the route ends on its edge
    assert track._thread_the_fabric(s, plan, [(700.0, 700.0), (450.0, 620.0)]) == round_it


def test_a_piece_no_route_found_is_drawn_only_over_no_paddy_crop_or_water() -> None:
    """Feature 405 T09 (round 3): where the router found nothing, the run as it came was clipped for the steadings alone and
    could cross the paddy or a brook. `_unrouted_clear` takes it only over nothing held and no water, its ends drawn in 3 ft."""
    from l7r.diagram.hamletgen.ways.thread import _unrouted_clear

    plot = [(40.0, -10.0), (60.0, -10.0), (60.0, 10.0), (40.0, 10.0)]
    brook = [((80.0, -20.0), (80.0, 20.0))]
    assert not _unrouted_clear([(0.0, 0.0), (100.0, 0.0)], [plot], []), "across a plot"
    assert not _unrouted_clear([(0.0, 30.0), (100.0, 30.0), (100.0, 0.0), (0.0, 0.0)], [], brook), "over the brook"
    assert _unrouted_clear([(0.0, 0.0), (40.0, 0.0)], [plot], brook), "ending on the plot's edge, short of the brook"
