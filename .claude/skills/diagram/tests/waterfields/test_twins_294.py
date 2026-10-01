"""Feature 294 B4: two watercourses do not run side by side (`waterfields/twins.py`)."""

from __future__ import annotations

from l7r.diagram.waterfields.twins import TWIN_RUN_FT, drop_twin_deliveries, leaves_from, twin_run_ft, twins

PARENT = [(0.0, 0.0), (0.0, 400.0)]
CHILD = [(0.0, 100.0), (20.0, 120.0), (20.0, 400.0)]  # leaves the parent at 100 ft and runs 20 ft off it to 400


def test_a_course_running_twenty_feet_beside_another_is_a_twin_past_its_junction() -> None:
    run = twin_run_ft(CHILD, PARENT, 1.0)
    assert 200.0 < run < 290.0, run  # the 60 ft past where it leaves are the junction itself
    assert twin_run_ft([(40.0, 0.0), (40.0, 400.0)], PARENT, 1.0) == 0.0, "40 ft apart is past the band"
    assert twin_run_ft([(0.0, 410.0), (300.0, 410.0)], PARENT, 1.0) == 0.0, "a course across the other is no twin"
    assert twin_run_ft([(0.0, 0.0), (0.0, 0.0)], PARENT, 1.0) == 0.0
    assert twin_run_ft([(20.0, 0.0), (20.0, 400.0)], PARENT, 2.0) == 0.0, "the band is in feet: 20 px at 2 ft/px is 40 ft"


def test_the_pairs_and_who_leaves_whom() -> None:
    assert [(i, j) for i, j, _ in twins([PARENT, CHILD, [(500.0, 0.0), (500.0, 400.0)]], 1.0)] == [(0, 1)]
    assert twins([PARENT, CHILD], 1.0)[0][2] > TWIN_RUN_FT
    assert leaves_from(CHILD, PARENT, 1.0) and not leaves_from(PARENT, CHILD, 1.0)


def test_the_delivery_that_leaves_is_the_one_not_drawn_and_a_canal_never_is() -> None:
    def ch(pts: list, role: str) -> dict:
        return {"pts": pts, "role": role}

    channels = [ch(PARENT, "branch"), ch(CHILD, "branch")]
    assert drop_twin_deliveries(channels, 0, 1.0) == [ch(CHILD, "branch")] and channels == [ch(PARENT, "branch")]
    channels = [ch(CHILD, "branch"), ch(PARENT, "branch")]
    drop_twin_deliveries(channels, 0, 1.0)
    assert channels == [ch(PARENT, "branch")], "found the other way round, the same one goes"
    channels = [ch(PARENT, "main"), ch(CHILD, "main")]
    assert drop_twin_deliveries(channels, 0, 1.0) == [] and len(channels) == 2, "two canals stand"
    channels = [ch(CHILD, "main"), ch(PARENT, "branch")]
    drop_twin_deliveries(channels, 0, 1.0)
    assert channels == [ch(CHILD, "main")], "a delivery beside a canal goes, whichever leaves"
    channels = [ch(PARENT, "branch"), ch(CHILD, "main")]
    drop_twin_deliveries(channels, 0, 1.0)
    assert channels == [ch(CHILD, "main")]
    side = [(20.0, 0.0), (20.0, 300.0)]  # two deliveries side by side, neither leaving the other: the shorter goes
    channels = [ch(PARENT, "branch"), ch(side, "branch")]
    drop_twin_deliveries(channels, 0, 1.0)
    assert channels == [ch(PARENT, "branch")]
    channels = [ch(side, "branch"), ch(PARENT, "branch")]
    drop_twin_deliveries(channels, 0, 1.0)
    assert channels == [ch(PARENT, "branch")]
    channels = [ch(PARENT, "branch"), ch(CHILD, "branch"), ch([(40.0, 150.0), (40.0, 380.0)], "branch")]
    drop_twin_deliveries(channels, 1, 1.0)  # only what this call appended is judged
    assert channels[0] == ch(PARENT, "branch") and len(channels) == 2
