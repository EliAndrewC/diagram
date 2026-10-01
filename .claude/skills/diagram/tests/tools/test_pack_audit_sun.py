"""A kitchen garden's sun on a hand-drawn sheet (feature 283; research homesteads 044).

The GM, 2026-09-28: a garden needs its sunlight, and a check should run on hand-drawn sheets with gardens for what shades
them - buildings and trees. These tests hold the sun, the shadow and the count to the record, over small synthetic
sheets, and the red fixture (the Hoshigaoka shrine as drawn before the feature) to naming the wood among its shade.
"""

from __future__ import annotations

import os

import pytest
from shapely.geometry import box

from l7r.diagram.tools.pack_audit import parse_svg
from l7r.diagram.tools.pack_audit import sun as S

_FIX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fixtures")
GARDEN = '<g data-kind="vegetable garden"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#garden-stipple)"{extra}/></g>'
HOUSE = '<g data-kind="residence"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#DDB87A"/></g>'


def _trees(*cs: tuple[float, float, float]) -> str:
    return '<g id="trees" fill="#7A8C5C">' + "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in cs) + "</g>"


def _sheet(*bodies: str) -> str:
    precinct = '<rect x="0" y="0" width="900" height="900" fill="url(#court-earth)" id="precinct"/>'
    return '<svg viewBox="0 0 900 900">' + precinct + "".join(bodies) + "</svg>"


def _garden(x: float = 400, y: float = 400, w: float = 60, h: float = 60, extra: str = "") -> str:
    return GARDEN.format(x=x, y=y, w=w, h=h, extra=extra)


def test_the_sun_is_the_records_sun() -> None:
    """At 38N in the shoulder month the 3pm sun stands about 27-28 deg high at azimuth ~232 (0038), noon due south."""
    el, az = S.sun_at(15.0)
    assert 26.0 <= el <= 29.0 and 229.0 <= az <= 235.0
    el12, az12 = S.sun_at(12.0)
    assert el12 > el and abs(az12 - 180.0) < 0.5
    assert S.sun_at(0.0)[0] < 0  # night


def test_a_shadow_falls_away_from_the_sun_and_as_long_as_the_height_says() -> None:
    post = S.Caster(box(0, 0, 3, 3), 20.0, "post")
    sh = S.shadow(post, 45.0, 180.0)  # noon sun due south at 45 deg: a 20 ft post throws 20 ft (60 px) due north
    minx, miny, maxx, maxy = sh.bounds
    assert miny == pytest.approx(-60.0, abs=0.01) and maxy == pytest.approx(3.0)
    assert minx == pytest.approx(0.0, abs=0.01) and maxx == pytest.approx(3.0, abs=0.01)


def test_an_open_bed_passes_and_a_bed_beside_a_house_to_its_south_fails() -> None:
    open_sheet = _sheet(_garden())
    assert S.garden_sun(parse_svg(open_sheet), open_sheet) == []
    shaded = _sheet(_garden(), HOUSE.format(x=380, y=470, w=100, h=60))  # a house just south of the bed
    out = S.garden_sun(parse_svg(shaded), shaded)
    assert len(out) == 1 and "needs 6" in out[0] and "residence" in out[0]


def test_trees_alone_shade_a_bed() -> None:
    """The GM's question was the trees: a bed ringed by crowns and no building fails, naming the trees."""
    ring = [(400 + dx, 400 + dy, 25) for dx in (-60, 0, 60, 120) for dy in (-60, 120)] + [(340, 460, 25), (520, 460, 25), (340, 400, 25), (520, 400, 25)]
    sheet = _sheet(_garden(), _trees(*ring))
    out = S.garden_sun(parse_svg(sheet), sheet)
    assert len(out) == 1 and "trees" in out[0] and "residence" not in out[0]


def test_a_half_shade_bed_takes_dappled_light_and_needs_three_hours() -> None:
    ring = [(400 + dx, 400 + dy, 25) for dx in (-60, 0, 60, 120) for dy in (-60, 120)] + [(340, 460, 25), (520, 460, 25), (340, 400, 25), (520, 400, 25)]
    sheet = _sheet(_garden(extra=' data-bed="half-shade"'), _trees(*ring))
    assert S.garden_sun(parse_svg(sheet), sheet) == []  # the trees' shade is dappled light to it
    walled = _sheet(_garden(extra=' data-bed="half-shade"'), HOUSE.format(x=380, y=470, w=100, h=200), HOUSE.format(x=300, y=380, w=90, h=200))
    out = S.garden_sun(parse_svg(walled), walled)
    assert len(out) == 1 and "half-shade kitchen bed" in out[0] and "needs 3" in out[0]


def test_what_does_not_stand_up_casts_nothing_and_a_small_roof_casts_a_short_shadow() -> None:
    well = '<g data-kind="well"><rect x="410" y="470" width="30" height="30" fill="#DDB87A"/></g>'
    sheet = _sheet(_garden(), well)
    assert S.garden_sun(parse_svg(sheet), sheet) == []
    cs = S.casters(parse_svg(_sheet(HOUSE.format(x=0, y=0, w=24, h=24))), _sheet(HOUSE.format(x=0, y=0, w=24, h=24)), box(500, 500, 510, 510))
    assert [c.height_ft for c in cs] == [S.SMALL_BUILDING_FT]  # 8 by 8 ft: a privy's roof, not a house's


def test_a_sheet_with_no_bed_has_nothing_to_measure() -> None:
    sheet = _sheet(HOUSE.format(x=0, y=0, w=90, h=60))
    assert S.gardens(parse_svg(sheet), sheet) == [] and S.garden_sun(parse_svg(sheet), sheet) == []


def test_the_red_fixture_fails_naming_the_wood() -> None:
    """The shrine as drawn before feature 283: its bed has too little sun, and the wood is among what shades it."""
    with open(os.path.join(_FIX, "hoshigaoka-garden-shaded-red.svg"), encoding="utf-8") as fh:
        text = fh.read()
    out = S.garden_sun(parse_svg(text), text)
    assert len(out) == 1 and "needs 6" in out[0] and "trees" in out[0]


def test_the_county_example_passes() -> None:
    from l7r.diagram import compound

    program = compound.county_magistracy_program()
    text = compound.emit_svg(program, compound.place(program))
    assert S.gardens(parse_svg(text), text) and S.garden_sun(parse_svg(text), text) == []


def test_a_half_shade_bed_names_no_tree_among_its_shaders() -> None:
    """A half-shade bed takes a tree's dappled light as lit, so a tree is not named as what takes its sun."""
    from shapely.geometry import Point, box

    bed = box(0, 0, 30, 30)
    tree = S.Caster(Point(15, 70).buffer(20), S.TREE_FT, "trees", tree=True)  # south of the bed: its shadow falls north onto it
    assert S.shaders(bed, [tree], half_shade=True) == []
    assert S.shaders(bed, [tree]) == ["trees"]
