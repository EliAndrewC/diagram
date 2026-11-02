"""Feature 294 B4: two watercourses do not run side by side (`waterfields/twins.py`)."""

from __future__ import annotations

from l7r.diagram.waterfields.twins import twin_run_ft, twins

PARENT = [(0.0, 0.0), (0.0, 400.0)]
CHILD = [(0.0, 100.0), (20.0, 120.0), (20.0, 400.0)]  # leaves the parent at 100 ft and runs 20 ft off it to 400


def test_a_course_running_twenty_feet_beside_another_is_a_twin_past_its_junction() -> None:
    run = twin_run_ft(CHILD, PARENT, 1.0)
    assert 200.0 < run < 290.0, run  # the 60 ft past where it leaves are the junction itself
    assert twin_run_ft([(40.0, 0.0), (40.0, 400.0)], PARENT, 1.0) == 0.0, "40 ft apart is past the band"
    assert twin_run_ft([(0.0, 410.0), (300.0, 410.0)], PARENT, 1.0) == 0.0, "a course across the other is no twin"
    assert twin_run_ft([(0.0, 0.0), (0.0, 0.0)], PARENT, 1.0) == 0.0
    assert twin_run_ft([(20.0, 0.0), (20.0, 400.0)], PARENT, 2.0) == 0.0, "the band is in feet: 20 px at 2 ft/px is 40 ft"


def test_every_pair_of_courses_running_as_twins_is_named() -> None:
    """`twins`, the finished-map check's predicate (feature 294 B4): the child beside its parent is named, a course far off is not."""
    far = [(400.0, 0.0), (400.0, 400.0)]
    found = twins([PARENT, CHILD, far, [(1.0, 1.0)]], 1.0)
    assert [(i, j) for i, j, _run in found] == [(0, 1)]
