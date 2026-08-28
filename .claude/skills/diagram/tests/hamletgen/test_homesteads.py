"""Unit tests for the houses, their appurtenances, and the wells (`hamletgen/homesteads.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import math

import pytest

from l7r.diagram import hamletgen as hg

from ._builders import a_plan


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


def test_farmstead_fixtures_roll_a_share_in_each_band_and_seat_one_of_a_kind_per_house() -> None:
    """Feature 133 T53-T59: the shares are rolled once per map inside the researched bands and declared
    for the gate; each house keeps at most one of a kind, every fixture names its house, and the
    shrine count never exceeds the share (the GM: "very rare, but notable")."""
    from l7r.diagram.hamletgen.homesteads import FIXTURE_BANDS, farmstead_fixtures
    from l7r.diagram.settlement import Settlement

    s = Settlement(W=900, H=700, seed=7)
    s.meta(name="T", scale="hamlet", ftpx=1)
    houses = [{"x": 200.0 + 110 * i, "y": 300.0 + 90 * (i % 2), "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"} for i in range(6)]
    for h in houses:
        s.M["houses"].append(dict(h))
        s.placed.append((h["x"], h["y"], h["w"], h["h"]))
    n = farmstead_fixtures(s, a_plan(), houses)
    shares = s.M["meta"]["farm_fixtures"]
    assert set(shares) == set(FIXTURE_BANDS) and all(lo <= shares[k] <= hi for k, (lo, hi) in FIXTURE_BANDS.items())
    recs = s.M["farm_fixtures"]
    assert n == len(recs) + len(s.M["persimmons"]) and n > 0
    owners = {(r["kind"], tuple(r["of"])) for r in recs}
    assert len(owners) == len(recs), "one of a kind per house"
    assert sum(r["kind"] == "shrine" for r in recs) <= max(1, round(shares["shrine"] * len(houses)))
    assert all(tuple(r["of"]) in {(h["x"], h["y"]) for h in houses} for r in recs)
    assert len(s.placed) == len(houses) + n, "every seated fixture reserves its ground"


def test_farmstead_fixtures_honor_the_spec_floor() -> None:
    """Feature 133 T61 (GM 2026-08-27: "a min number of something which may or may not appear"): a spec'd
    floor forces the kind onto houses that lack it after the rolled pass, and declares itself in meta."""
    from l7r.diagram.hamletgen.homesteads import farmstead_fixtures
    from l7r.diagram.settlement import Settlement

    s = Settlement(W=900, H=700, seed=7)
    s.meta(name="T", scale="hamlet", ftpx=1)
    houses = [{"x": 200.0 + 110 * i, "y": 300.0 + 90 * (i % 2), "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"} for i in range(6)]
    for h in houses:
        s.M["houses"].append(dict(h))
        s.placed.append((h["x"], h["y"], h["w"], h["h"]))
    plan = a_plan()
    plan.fixtures_min = {"shrine": 2, "bath": 3}
    farmstead_fixtures(s, plan, houses)
    kinds = [r["kind"] for r in s.M["farm_fixtures"]]
    assert kinds.count("shrine") >= 2 and kinds.count("bath") >= 3
    assert s.M["meta"]["farm_fixtures_min"] == {"shrine": 2, "bath": 3}
    owners = {(r["kind"], tuple(r["of"])) for r in s.M["farm_fixtures"]}
    assert len(owners) == len(s.M["farm_fixtures"]), "the floor never doubles a house"


# ---- feature 145: the refusal branches of the fixture placer that no cohort seed took --------------


def _strip_settlement() -> tuple[object, object]:
    from l7r.diagram.settlement import Settlement

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="S", scale="hamlet", ftpx=1, down_deg=90)
    return s, a_plan()


def test_strip_blocked_refuses_the_canvas_edge_a_crossing_lane_and_a_drawn_crown() -> None:
    s, _plan = _strip_settlement()
    blocked = hg.homesteads._strip_blocked
    assert blocked(s, 20, 500, 30, 20, 0, 0, [], [], None, []) is True, "over the canvas edge"
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, []) is False, "open ground"
    lane = [([(500, 400), (500, 600)], 3.0)]  # a lane running THROUGH the strip, both ends outside it
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, lane) is True
    s.M["tree_crowns"] = [500.0, 500.0, 12.0]
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, []) is True, "a crown drawn two stages earlier"


def test_farmstead_fixtures_on_a_houseless_map_place_nothing() -> None:
    s, plan = _strip_settlement()
    assert hg.homesteads.farmstead_fixtures(s, plan, []) == 0


def test_roll_falls_through_to_the_last_weight() -> None:
    """A u past the weights' sum (floating-point slack) takes the last row rather than raising."""
    assert hg.homesteads._roll([("a", 0.3), ("b", 0.3)], 0.99) == "b"
    assert hg.homesteads._roll([("a", 0.3), ("b", 0.3)], 0.1) == "a"


def test_strip_blocked_refuses_a_lane_that_only_crosses_the_strip() -> None:
    """Feature 146: the crossing arm of `_strip_blocked` - a lane whose ENDS are both outside the strip but
    whose segment passes through it (the corner test above cannot see that one)."""
    s, _plan = _strip_settlement()
    blocked = hg.homesteads._strip_blocked
    across = [([(440.0, 500.0), (560.0, 500.0)], 1.0)]  # a hairline lane straight through, ends well clear
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, across) is True
    beside = [([(440.0, 300.0), (560.0, 300.0)], 1.0)]
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, beside) is False


def test_trunk_blocked_refuses_the_canvas_edge_and_a_record_without_a_footprint() -> None:
    """Feature 146: two arms of the trunk test - a trunk hanging off the canvas, and a record in one of the
    scanned lists that carries no `x` at all (a synthetic entry another check keeps), which is skipped
    rather than raising."""
    s, _plan = _strip_settlement()
    blocked = hg.homesteads._trunk_blocked
    assert blocked(s, 20, 500, 10, [], [], None, []) is True, "over the canvas edge"
    s.M["persimmons"] = [{"note": "a record with no footprint at all"}]
    assert blocked(s, 500, 500, 10, [], [], None, []) is False, "the footprint-less record is skipped"
    s.M["persimmons"].append({"x": 500.0, "y": 500.0, "w": 20.0, "h": 20.0})
    assert blocked(s, 500, 500, 10, [], [], None, []) is True, "and a real one blocks"
