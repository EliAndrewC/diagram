"""Unit tests for the houses, their appurtenances, and the wells (`hamletgen/homesteads.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import math

import pytest

from l7r.diagram import hamletgen as hg


def test_place_wells_never_clusters_two_wells_inside_the_spacing_floor():
    """The greedy coverage sort (2026-08-15) pops FAR seats first, so the 170 px spacing guard can
    only fire when every seat the engine will accept sits beside an existing well. Build exactly
    that: `well_at` accepts only a small disc, so after the first (central) well every acceptable
    candidate is inside the spacing floor and must be skipped - one well places, never a clustered
    pair (`wells_not_clustered` is the rule the guard exists for)."""
    from types import SimpleNamespace

    houses = [{"x": 500, "y": 500}, {"x": 520, "y": 500}, {"x": 500, "y": 520}, {"x": 520, "y": 520}]
    # M={}: no surface water, so every house is needy (the minimax filter reads s.M).
    # `_crop_boxes` returning [] is deliberate, not a shrug: the later-well tie-break asks the crop
    # for the box it will set (see `_outside_cloud`), and an empty answer is what exercises its
    # house-centers FALLBACK - so this stub covers both the call and the default it degrades to.
    s = SimpleNamespace(well_at=lambda x, y: math.hypot(x - 510, y - 510) < 60.0, M={}, _crop_boxes=lambda city=False: [])
    plan = SimpleNamespace(spec=SimpleNamespace(households=12), ftpx=1.0)
    assert hg.place_wells(s, plan, houses) == 1  # type: ignore[arg-type]


@pytest.mark.parametrize(("households", "wells"), [(10, 2), (12, 2), (15, 2), (20, 3)])
def test_wells_are_one_per_six_households_or_so(households: int, wells: int) -> None:
    """Inside `wells_sized_to_population`'s 2-20 households-per-well band at hamlet scale."""
    got = hg.well_target(households)
    assert got == wells
    assert 2 <= households / got <= 20


def test_a_tiny_hamlet_still_keeps_one_well() -> None:
    assert hg.well_target(1) == 1


def test_a_house_beside_open_water_needs_no_rescue_well() -> None:
    """`place_wells`' rescue pass exists for a household the grid left dry, and it skips any house
    already watered by a stream, channel or pond - the check's own verdict, so the rescue cannot
    plant a well the gate never asked for. The companion of the `M={}` case above, which has no
    surface water and so takes the other branch."""
    from types import SimpleNamespace

    houses = [{"x": 500, "y": 500}, {"x": 2000, "y": 2000}]  # the second sits far outside the first well's reach...
    s = SimpleNamespace(well_at=lambda x, y: math.hypot(x - 500, y - 500) < 60.0, M={"streams": [{"poly": [[1900, 1900], [2100, 2100]], "w": 9}]})  # ...but a stream runs right past it
    plan = SimpleNamespace(spec=SimpleNamespace(households=6), ftpx=1.0)
    assert hg.place_wells(s, plan, houses) == 1, "the watered house is skipped by the rescue, so only the first well is sited"  # type: ignore[arg-type]


def test_a_seat_on_forbidden_ground_is_refused() -> None:
    """`generate` re-rolls a stranding map with the offending ground passed as `avoid`; the seat loops
    honour it through `_seat_allowed`. Half a bundle pitch is the radius - enough to clear the pocket,
    not so much that the retry merely nudges the same steading along it."""

    class _S:
        pass

    s = _S()
    assert hg.homesteads._seat_allowed(s, 100.0, 100.0) is True  # nothing forbidden yet
    s._avoid_seats = [(100.0, 100.0)]
    assert hg.homesteads._seat_allowed(s, 100.0, 100.0) is False  # dead on the forbidden seat
    assert hg.homesteads._seat_allowed(s, 140.0, 100.0) is False  # inside half a bundle pitch
    assert hg.homesteads._seat_allowed(s, 400.0, 400.0) is True  # well clear
