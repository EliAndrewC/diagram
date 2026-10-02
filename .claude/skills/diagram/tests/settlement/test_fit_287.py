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


def test_a_farmstead_fixture_on_a_paddy_or_across_the_brook_refuses_its_homestead() -> None:
    """Feature 287, homes H32: a household's fixtures are parts of its bundle, so a privy between the envelope's nine
    points on a paddy's corner, or across a brook from its house, refuses the homestead as its yard or bed would."""
    from l7r.diagram.settlement.homestead_parts.fixture_seats import FixtureForms

    s = _village()
    s._fixture_forms = FixtureForms()
    s._household_fixtures = ("privy", "persimmon")
    geom = s._bundle_geom(400.0, 400.0, 46.0, 28.0, "E")
    boxes = geom["boxes"]["fixtures"]
    assert set(boxes) == {"privy", "persimmon"} and s._parts_fit(geom)
    px_, py_, pw, ph = boxes["privy"]
    s.field_polys.append([(px_ - 1.0, py_ - 1.0), (px_ + pw, py_ - 1.0), (px_ + pw, py_ + ph), (px_ - 1.0, py_ + ph)])
    assert not s._parts_fit(geom), "the privy on the paddy's corner"
    s.field_polys.clear()
    s.M["streams"] = [{"poly": [[(400.0 + px_) / 2 - 300.0, (400.0 + py_) / 2 + 300.0], [(400.0 + px_) / 2 + 300.0, (400.0 + py_) / 2 - 300.0]], "w": 2.0}]
    assert s._parts_across_stream(geom), "the brook between the house and its privy"


def test_a_grove_farm_is_refused_on_the_access_tree_or_with_a_fixture_in_a_band() -> None:
    """`_on_the_access` / `_fixtures_in_bands` (feature 291 on 287): a bundle whose part stands on a corridor of the access
    tree, or whose fixture - as turned - stands in its own grove band or a neighbor's, is refused; clear, it is not."""
    from l7r.diagram.settlement.rolling.access import AccessTree

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    geom = {
        "boxes": {"house": (500.0, 500.0, 40.0, 30.0), "yard": (500.0, 540.0, 30.0, 20.0), "gardens": [], "fixtures": {"privy": (560.0, 500.0, 10.0, 8.0)}},
        "fixtures": {"privy": (560.0, 500.0, 10.0, 8.0)},  # as laid; turn 0, so the record's box is the same
        "groves": [(500.0, 440.0, 200.0, 40.0)],
        "bbox": (500.0, 500.0, 220.0, 160.0),
    }
    assert not s._on_the_access(geom), "no tree installed"
    tree = AccessTree(7.0)
    tree.add((0.0, 900.0), (1000.0, 900.0))
    s._access = tree
    assert not s._on_the_access(geom)
    tree.add((560.0, 0.0), (560.0, 1000.0))
    assert s._on_the_access(geom), "the privy stands on the corridor"
    assert not s._fixtures_in_bands(geom)
    geom["boxes"]["fixtures"]["privy"] = geom["fixtures"]["privy"] = (560.0, 455.0, 10.0, 8.0)
    assert s._fixtures_in_bands(geom), "in its own band"
    geom["boxes"]["fixtures"] = geom["fixtures"] = {}
    assert not s._fixtures_in_bands(geom), "no fixture"
    geom["boxes"]["fixtures"] = geom["fixtures"] = {"coop": (800.0, 800.0, 6.0, 6.0)}
    s.M["houses"].append({"x": 800.0, "y": 780.0, "w": 40.0, "h": 30.0, "geom": {"groves": [(800.0, 800.0, 100.0, 30.0)], "bbox": (800.0, 790.0, 120.0, 60.0)}})
    geom["bbox"] = (650.0, 650.0, 400.0, 400.0)
    assert s._fixtures_in_bands(geom), "in a neighbor's band"
