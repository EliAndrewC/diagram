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
