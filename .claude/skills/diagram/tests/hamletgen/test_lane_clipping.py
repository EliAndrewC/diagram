"""A lane stops where the crop begins (feature 166).

Carries `lanes_clear_of_dry_plots` and its siblings in the "ways clear of X" family, which the retired
battery re-measured on finished maps. The guarantee is `clip_to_clear`: a lane arm is SHORTENED so it
stops before the first ground it may not cross, and the obstacle list it is handed is the envelope, the
crops, the standing fabric, the wet toe and the marsh together - so one truncation serves every pairing
the battery needed a separate check for.

TRUNCATING RATHER THAN DRAGGING IS THE DESIGN, and its reasoning is worth keeping: dragging an offending
VERTEX back toward the cluster was tried first and is not reliable - a vertex deep inside a large hem plot
may not escape in the steps allowed, and it distorts the skeleton on the way out. Truncating is simpler
and more honest, because the lane ends where the crop begins, which is what a village lane does.
"""

from __future__ import annotations

from l7r.diagram.hamletgen.ways import clip_to_clear

CROP = [(500.0, 400.0), (900.0, 400.0), (900.0, 800.0), (500.0, 800.0)]


def test_a_lane_running_into_the_crop_is_cut_before_it() -> None:
    lane = [(100.0, 600.0), (400.0, 600.0), (700.0, 600.0), (1000.0, 600.0)]
    got = clip_to_clear(lane, [CROP], margin=10.0)
    assert got[-1][0] < 500.0, f"the lane ran to x={got[-1][0]:.0f}, into a crop starting at 500"
    assert len(got) >= 2, "a truncated lane is still a lane"


def test_a_lane_clear_of_everything_is_returned_whole() -> None:
    lane = [(100.0, 100.0), (300.0, 100.0), (450.0, 100.0)]
    assert clip_to_clear(lane, [CROP], margin=10.0) == lane


def test_no_obstacles_means_no_work() -> None:
    """The early return matters: the lane skeleton is clipped on every arm, and a map with nothing to
    avoid must not pay a scan per vertex to discover that."""
    lane = [(0.0, 0.0), (100.0, 0.0)]
    assert clip_to_clear(lane, [], margin=10.0) is lane


def test_the_margin_is_honoured_not_merely_the_outline() -> None:
    """A lane flush against a plot's edge runs on the crop's shoulder. The cut is made at the MARGIN, so
    a wider margin stops the lane earlier - the same distinction the well head and the garden turn on."""
    lane = [(100.0, 600.0), (400.0, 600.0), (700.0, 600.0)]
    tight = clip_to_clear(lane, [CROP], margin=5.0)
    wide = clip_to_clear(lane, [CROP], margin=120.0)
    assert wide[-1][0] <= tight[-1][0], "a wider margin must not let the lane run further"


def test_an_arm_with_nowhere_to_go_is_not_drawn_at_all() -> None:
    """A skeleton arm that starts inside the crop and cannot reach 70 px of clear ground returns NOTHING,
    and the caller draws no lane.

    THE DOCSTRING SAID THE OPPOSITE until this test was written (feature 166). It promised "always
    returns at least a two-point line", which described the FIRST version's fallback to the original
    first segment - and that fallback drew a lane blocked immediately in full and unclipped, doing the
    exact opposite of the function's job. The fallback was removed; the sentence describing it was not,
    and it sat there long enough for me to write a test asserting it."""
    lane = [(600.0, 600.0), (700.0, 600.0), (800.0, 600.0)]  # wholly inside the crop
    assert clip_to_clear(lane, [CROP], margin=10.0) == []

    short = [(600.0, 600.0), (1200.0, 600.0)]  # starts inside, leaves - but the clear run is too short
    assert clip_to_clear(short, [CROP], margin=10.0) == []
