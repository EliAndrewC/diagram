"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

import pytest


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


def test_the_track_out_drawn_is_the_one_the_homesteads_recorded_and_none_recorded_is_refused_by_name() -> None:
    """Feature 444 T32: the track out is chosen once, at the homesteads, in Rust; the stage draws it as recorded and never chooses
    one - a form that records none refuses by name (the seating refuses a site with no dry way out before it gets here)."""
    import types

    from l7r.diagram.hamletgen.ways.track import NoDryExit, the_recorded_track

    s = types.SimpleNamespace(M={"way_out_track": [[0.0, 0.0], [10.0, 5.0]]})
    assert the_recorded_track(s) == [(0.0, 0.0), (10.0, 5.0)]
    with pytest.raises(NoDryExit, match="no track out was recorded"):
        the_recorded_track(types.SimpleNamespace(M={}))
