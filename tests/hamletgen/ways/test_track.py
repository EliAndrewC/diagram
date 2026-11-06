"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""


def _box_on(a, b):
    """A 40 x 28 ft building's box standing on the middle of the leg a-b."""
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    return (mx - 20.0, my - 14.0, mx + 20.0, my + 14.0)


def test_the_recorded_track_is_the_track_out_the_homesteads_stage_chose() -> None:
    """Feature 320 (FR-008): `recorded_track` reads the track out the homesteads stage chose once the last house stood
    (`way_out_track`); none where it is absent or under two points."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.ways import track

    assert track.recorded_track(SimpleNamespace(M={"way_out_track": [[0.0, 0.0], [40.0, 0.0]]})) == [(0.0, 0.0), (40.0, 0.0)]
    assert track.recorded_track(SimpleNamespace(M={})) is None and track.recorded_track(SimpleNamespace(M={"way_out_track": [[0.0, 0.0]]})) is None


def test_a_turn_of_exactly_140_degrees_is_no_hairpin() -> None:
    """405 T96: 0081 calls a hairpin a turn of "more than 140 degrees"; the fold, the kinks and the joints cut at exactly 140 too."""
    import math

    from l7r.diagram.hamletgen.ways.clearance import _HAIRPIN_DEG, kink_spans
    from l7r.diagram.hamletgen.ways.geom import _turn_deg

    c = math.cos(math.radians(40.0))
    s = math.sin(math.radians(40.0))
    pts = [(0.0, 0.0), (100.0, 0.0), (100.0 - 100.0 * c, 100.0 * s)]
    assert math.isclose(_turn_deg(*pts), _HAIRPIN_DEG)
    assert not any(kind == "hairpin" for kind, *_r in kink_spans(pts))


def test_the_track_out_drawn_is_the_one_the_homesteads_recorded_or_one_chosen_now_in_rust(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Feature 444 T32: the stage draws the track out the homesteads recorded, and on a form that records none (a dispersed
    hamlet) the one the homesteads' own Rust chooser picks now - never a Python choice."""
    import types

    from l7r.diagram.hamletgen.homesteads import household_ways
    from l7r.diagram.hamletgen.ways.track import the_track_out

    s = types.SimpleNamespace(M={"way_out_track": [[0.0, 0.0], [10.0, 5.0]]})
    assert the_track_out(s, None) == [(0.0, 0.0), (10.0, 5.0)]
    monkeypatch.setattr(household_ways, "chose_the_track", lambda s_, plan: [(1.0, 1.0), (2.0, 2.0)])
    assert the_track_out(types.SimpleNamespace(M={}), None) == [(1.0, 1.0), (2.0, 2.0)]
