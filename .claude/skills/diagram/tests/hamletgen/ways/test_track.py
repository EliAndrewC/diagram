"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

from l7r.diagram import hamletgen as hg

from .._builders import SQUARE, a_plan


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
