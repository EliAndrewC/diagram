"""Split from the 1,152-line `tests/settlement/test_structures.py` by feature 174 - see this
directory's CLAUDE.md for the index. Tests for `settlement/structures/servants.py`."""

import math

import pytest

from l7r.diagram.settlement import seg_dist
from tests.settlement._builders import _ward_city_with_samurai


def test_servant_ranges_attach_to_their_own_household():
    # GM 2026-08-02: a ward servant is its household's nagaya, drawn along its master's frontage
    s = _ward_city_with_samurai((600, 600, "samurai", 0.0), (600, 700, "samurai_large", 0.0))
    n = s.servant_ranges()
    assert n == 3  # one range for the junior house, two for the senior (budgets.md)
    ranges = [b for b in s.M["buildings"] if b["kind"] == "servant"]
    assert len(ranges) == 3
    for r in ranges:
        assert r["of"] in ([600.0, 600.0], [600.0, 700.0])
        assert r["w"] > 2.2 * r["h"]  # a RANGE, not a cottage - the proportion carries the read
        assert r["h"] == pytest.approx(s.px(s.SERVANT_RANGE_DEPTH_FT))


def test_servant_ranges_is_idempotent():
    # it may be re-run after a late household top-up; nobody gets a second range over quota
    s = _ward_city_with_samurai((600, 600, "samurai", 0.0), (600, 700, "samurai_large", 0.0))
    first = s.servant_ranges()
    assert first == 3
    assert s.servant_ranges() == 0
    assert sum(1 for b in s.M["buildings"] if b["kind"] == "servant") == 3


def test_door_is_clear_rejects_a_blocked_doorway():
    s = _ward_city_with_samurai()
    s.building(600, 608, 20, 10, "monk_house", 0.0)  # squarely across the doorway of the seat below
    assert not s._door_is_clear(600, 600, 20, 6, 0.0)
    assert s._door_is_clear(600, 400, 20, 6, 0.0)  # same footprint, open ground ahead


def test_servant_ranges_refuses_a_seat_whose_own_door_is_blocked():
    # the range is a dwelling too: its own entrance has to open onto something
    probe = _ward_city_with_samurai((600, 600, "samurai", 0.0))
    probe.servant_ranges()
    seat = next(b for b in probe.M["buildings"] if b["kind"] == "servant")
    s = _ward_city_with_samurai((600, 600, "samurai", 0.0))
    # 1.2 px clear of the range - further than its 0.6 px gap to its own host, so the nearest-host
    # rule does not refuse it first, yet inside the ~2.3 px band the door check samples
    s.building(seat["x"], seat["y"] + seat["h"] / 2 + 3.2, seat["w"], 4, "monk_house", 0.0)
    s.servant_ranges()
    seated = [(round(b["x"], 1), round(b["y"], 1)) for b in s.M["buildings"] if b["kind"] == "servant"]
    assert (round(seat["x"], 1), round(seat["y"], 1)) not in seated  # that seat is refused; another flank may still serve


def test_blocks_any_door_is_the_MIRROR_of_door_is_clear_and_answers_the_other_way() -> None:
    """Feature 174. `_door_is_clear` asks "does MY footprint have a doorway"; `_blocks_any_door`
    asks "would my footprint stand in SOMEONE ELSE'S". They are the same geometry from the two
    sides, and only the first had a test.

    Its own docstring names the case that needs it: "the ground behind a house is often the roji the
    row BEHIND it faces" - so a seat that looks like open ground is someone's doorway.

    Both answers asserted, since a predicate that always says True blocks every seat on the map and
    one that always says False is the defect it was written to prevent.
    """
    s = _ward_city_with_samurai()
    s.building(600.0, 600.0, 20.0, 10.0, "monk_house", 0.0)

    def _quad(cx, cy, w, h):
        return [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]

    assert s._blocks_any_door(_quad(600.0, 610.0, 16.0, 8.0)) is True, "squarely in front of that house's door"
    assert s._blocks_any_door(_quad(600.0, 200.0, 16.0, 8.0)) is False, "and far away it blocks nobody"


def test_a_servant_range_is_refused_by_each_of_the_grounds_it_must_stay_clear_of() -> None:
    """Feature 174. `servant_ranges` walks a ladder of refusals, and each one is a documented rule
    rather than a guard for its own sake. This exercises three of them by placing the obstruction
    and watching the count fall to zero, against a baseline that succeeds.

    - THE ROADBED: "a range is a building on the verge, not an obstruction in the roadbed", so a
      street laid along the house's flank refuses every seat on it.
    - THE WARD FENCE'S OWN INK: being inside the interior polygon means inside the fence LINE, and
      the palisade is stroked 5 px wide - a range flush to the boundary is geometrically inside and
      still drawn THROUGH it (city_ward_fence_clear_of_structures).
    - `self.bound`: a range must lie inside whatever bound the tier set, not merely inside the ward.
    """
    base = _ward_city_with_samurai((600, 600, "samurai", 0.0))
    assert base.servant_ranges() > 0, "the baseline seats a range at all - without this the rest proves nothing"

    roadbed = _ward_city_with_samurai((600, 600, "samurai", 0.0))
    roadbed.M["town_streets"] = [{"pts": [(400.0, 600.0), (800.0, 600.0)], "w": 40}]
    assert roadbed.servant_ranges() == 0, "no range stands in the roadbed"

    bounded = _ward_city_with_samurai((600, 600, "samurai", 0.0))
    bounded.bound = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]  # a bound the house is nowhere near
    assert bounded.servant_ranges() == 0, "and none outside the tier's bound"


def test_servant_ranges_sweeps_SINGLETON_records_as_well_as_lists() -> None:
    """`_solid_records` walks the manifest rather than a hand list of keys - "the first cut here
    tested only `buildings` and `houses`", and the sweep is what stops a new feature type being
    invisible to the range placer.

    Two record SHAPES exist and both must be swept: most keys hold a LIST of dicts, but the
    singletons (`governor_mansion`, `theater_stage` before it became a list) hold ONE dict. A sweep
    that handles only lists walks straight past the governor's mansion.
    """
    s = _ward_city_with_samurai((600, 600, "samurai", 0.0))
    s.M["governor_mansion"] = {"x": 600.0, "y": 640.0, "w": 120.0, "h": 90.0, "rot": 0.0}
    assert s.servant_ranges() == 0, "a singleton record blocks the ground behind the house like any other solid"


def test_a_servant_range_keeps_off_a_ROAD_an_ALLEY_and_a_RING_ROAD_alike() -> None:
    """ "a range is a building on the verge, not an obstruction in the roadbed" - and the verge is
    read from four keys, not one. Each is asserted on its own map, because a bed list that silently
    lost a key would still pass a test that only laid a town street.
    """
    for key, record in (
        ("road", [(400.0, 600.0), (800.0, 600.0)]),
        ("ring_road", [(400.0, 600.0), (800.0, 600.0)]),
    ):
        s = _ward_city_with_samurai((600, 600, "samurai", 0.0))
        s.M[key] = record
        assert s.servant_ranges() == 0, f"no range stands in the {key}"

    alleyed = _ward_city_with_samurai((600, 600, "samurai", 0.0))
    alleyed.M["alleys"] = [{"pts": [(400.0, 600.0), (800.0, 600.0)], "w": 40}]
    assert alleyed.servant_ranges() == 0, "nor in an alley"


def test_a_range_stays_INSIDE_its_ward_fence_and_clear_of_the_fence_ink() -> None:
    """A servant range is its household's nagaya, drawn along its master's frontage inside the ward.
    Two separate holds, and a house parked mid-ward exercises neither: the whole range must lie
    inside the fence, and it must also stand clear of the fence's own INK - "inside the interior
    polygon" is the fence LINE, and the palisade is stroked, so a range flush to the boundary is
    geometrically inside it and still drawn through it (city_ward_fence_clear_of_structures).

    The house is seated at the ward's inner CORNER, where a range reaching either way runs at the
    boundary - measured, not guessed: mid-ward seats reach neither branch."""
    s = _ward_city_with_samurai((600.0, 600.0, "samurai", 0.0))
    assert s.servant_ranges() == 1, "a house with room gets its range"

    corner = _ward_city_with_samurai((405.0, 410.0, "samurai", 0.0))
    corner.servant_ranges()
    fence = next(wd["boundary"] for wd in corner.M["wards"])
    for r in [b for b in corner.M["buildings"] if b["kind"] == "servant"]:
        near = min(seg_dist(r["x"], r["y"], fence[i], fence[i + 1]) for i in range(len(fence) - 1))
        assert near >= max(r["w"], r["h"]) / 2 + corner._WARD_STROKE, f"no range is laid through the palisade: {r}"


def test_a_range_is_withheld_when_a_NEIGHBOR_would_touch_it_closer_than_its_host() -> None:
    """It has to read as ITS OWN household's range: a range tucked against the next lot's building is
    an annex of the wrong house, the same defect the merchant kura had. Nothing may touch it more
    closely than the house it belongs to.

    The lone range lands at (619.3, 604.2); the sliver below is laid along that flank, closer to it
    than its host's own 0.6 px of daylight."""
    lone = _ward_city_with_samurai((600.0, 600.0, "samurai", 0.0))
    assert lone.servant_ranges() == 1

    crowded = _ward_city_with_samurai((600.0, 600.0, "samurai", 0.0))
    crowded.building(619.27, 607.1, 18.0, 0.6, "shrine")
    crowded.servant_ranges()
    for r in [b for b in crowded.M["buildings"] if b["kind"] == "servant"]:
        host = next(o for o in crowded.M["buildings"] if o["kind"] == "samurai")
        gap_host = math.dist((r["x"], r["y"]), (host["x"], host["y"]))
        assert all(math.dist((r["x"], r["y"]), (o["x"], o["y"])) >= gap_host for o in crowded.M["buildings"] if o["kind"] == "shrine"), r
