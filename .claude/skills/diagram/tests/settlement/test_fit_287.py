"""Feature 287: the bundle fit's guarantees (water W05, W54, W55, W56; homes H44) - each on constructed inputs that include
the violating case, each read through the placer's own predicate."""

from __future__ import annotations

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling.fit import part_box


def _village(rot: float = 0.0) -> Settlement:
    s = Settlement(1200, 900, seed=1)
    s.meta(name="V", scale="village")
    s._nucleated = True
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}
    s._house_rot = lambda x, y: rot  # type: ignore[method-assign]
    return s


def test_two_farmhouses_seven_feet_apart_on_their_drawn_quads_are_refused() -> None:
    """W54: a quarter-turned pair whose UNROTATED boxes stand 20 ft apart but whose drawn quads stand 7 ft apart - the
    placer measures the drawn quads (`eave_gap`) and refuses it."""
    s = _village(rot=90.0)
    s.M["houses"].append({"x": 400.0, "y": 400.0, "w": 46.0, "h": 28.0, "rot": 90.0, "kind": "plain"})
    # turned a quarter, each house is 28 wide on x: centers 35 apart leave 7 ft between the walls; unturned, 46 wide,
    # they would overlap - so the ONLY reading under which 7 ft is the gap is the drawn one
    assert s._house_too_near_a_neighbor((435.0, 400.0, 46.0, 28.0)), "7 ft on the drawn quads: under the 8 ft drip line"
    assert not s._house_too_near_a_neighbor((440.0 + 8.0, 400.0, 46.0, 28.0)), "20 ft: clear"


def test_a_raked_house_corner_on_a_neighbors_garden_is_refused() -> None:
    """W55: the neighbor's bundle box is the AABB of its turned parts, so a raked house whose corner reaches the garden -
    though its unraked rect stands a foot clear - meets the placed box and is refused by the envelope test."""
    s = _village(rot=20.0)
    geom = s._bundle_geom(400.0, 400.0, 46.0, 28.0, "E")
    s.placed.append(geom["bbox"])
    gx, gy, gw, gh = part_box(geom, "gardens")[0]
    # a second house whose unraked rect would stand 1 ft east of the garden's unturned edge
    probe = s._bundle_geom(gx + gw / 2 + 1.0 + 23.0, gy, 46.0, 28.0, "E")
    assert s._envelope_blocked(probe["bbox"]) is not None


def test_a_garden_on_an_in_field_ditch_is_refused_without_a_corridor_stub() -> None:
    """W56: a garden bed across a delivery ditch's tail, with nothing else holding the ground, is refused by the parts."""
    s = _village()
    geom = s._bundle_geom(400.0, 400.0, 46.0, 28.0, "E")
    assert s._parts_fit(geom), "no ditch: the homestead stands"
    gx, gy, _gw, _gh = part_box(geom, "gardens")[0]
    s.M["field_ditches"].append({"poly": [[gx, gy - 60.0], [gx, gy + 60.0]], "w": 3.0})
    assert not s._parts_fit(s._bundle_geom(400.0, 400.0, 46.0, 28.0, "E"))


def test_a_house_on_the_brooks_course_is_refused_at_its_turned_box() -> None:
    """W05: the brook the seat reads is its finished course (rounded at the end of `stage_sink`), and a house whose TURNED
    box reaches within the brook's half-width plus 5 ft of it is refused; the same house turned square, clear of it, is not."""
    s = _village(rot=30.0)
    turned = s._bundle_geom(400.0, 400.0, 46.0, 28.0, "W")
    hx, hy, hw, hh = part_box(turned, "house")
    edge = hx + hw / 2  # the turned house's east extent, 3.9 ft past the unturned wall
    assert edge > 400.0 + 23.0 + 3.0
    s.M["streams"].append({"poly": [[edge + 6.0, hy - 200.0], [edge + 6.0, hy + 200.0]], "w": 6.0})  # 6 ft off: under 3 + 5
    assert not s._parts_fit(s._bundle_geom(400.0, 400.0, 46.0, 28.0, "W"))
    s.M["streams"] = [{"poly": [[edge + 60.0, hy - 200.0], [edge + 60.0, hy + 200.0]], "w": 6.0}]
    assert s._parts_fit(s._bundle_geom(400.0, 400.0, 46.0, 28.0, "W"))


@pytest.mark.parametrize("gap", [1.0, 30.0])
def test_a_threshing_yard_lapping_a_paddy_is_refused(gap: float) -> None:
    """H44: the yard as drawn (its turned box) held off every paddy by overlap, not by the envelope's nine points."""
    s = _village(rot=4.0)
    geom = s._bundle_geom(400.0, 400.0, 46.0, 28.0, "E")
    yx, yy, yw, yh = part_box(geom, "yard")
    s.field_polys.append([(yx - 5.0, yy + yh / 2 - 3.0 + gap), (yx + 5.0, yy + yh / 2 - 3.0 + gap), (yx, yy + yh / 2 + 80.0)])  # a corner poking up
    assert s._parts_fit(geom) is (gap > 3.0)
