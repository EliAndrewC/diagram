"""A well's lifting gear and roof on a Mode A sheet (feature 374 wave 135): research/questions/0196-communal-wells-ido.drawing.html."""

from __future__ import annotations

import math
import re

from l7r.diagram import well_gear as wg


def test_the_gear_follows_the_depth_about_three_wells_in_four() -> None:
    shallow = [wg.well_gear("s", i, "shallow") for i in range(1, 401)]
    deep = [wg.well_gear("s", i, "deep") for i in range(1, 401)]
    assert 0.68 < shallow.count("sweep") / 400 < 0.82 and 0.68 < deep.count("pulley frame") / 400 < 0.82
    assert wg.well_gear("s", 7, "deep") == wg.well_gear("s", 7, "deep"), "a roll is the sheet's and the well's, every time"


def test_a_roof_on_about_one_well_in_three_and_the_depth_rolled_from_the_name() -> None:
    roofs = sum(wg.well_roofed("s", i) for i in range(1, 601))
    assert 0.27 < roofs / 600 < 0.40
    assert wg.water_depth("county-magistracy-example") in wg.WATER_DEPTHS


def test_the_glyph_tags_each_part_with_the_well_it_stands_on() -> None:
    svg = wg.gear_svg(100.0, 50.0, 11.0, "sweep", True)
    roof, gear = svg.split("</g>", 1)
    # the roof an unfilled outline on four corner posts, drawn with the gear over the curb (a filled square under it read
    # as the paved apron - glyph-check, batch 6)
    assert 'data-roof="1" data-at="100,50"' in roof and 'fill="none"' in roof and roof.count("<circle") == 4
    assert 'data-gear="sweep" data-at="100,50"' in gear and "<circle" in gear and "<rect" not in gear  # a post is never a door's rect
    # the sweep's pole is about as long as the marker is wide (0196's drawing page): 22 px on a 22 px marker
    pole = re.search(r'<line x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', gear)
    assert pole and abs(math.dist(tuple(map(float, pole.groups()[:2])), tuple(map(float, pole.groups()[2:]))) - 22.0) < 0.05
    svg = wg.gear_svg(100.0, 50.0, 11.0, "pulley frame", False)
    assert "data-roof" not in svg and svg.count("<circle") == 2 and re.search(r'<line x1="87" y1="50" x2="113" y2="50"', svg)


def test_an_indoor_well_hangs_its_pulley_from_the_beams() -> None:
    """Plan W135-2 (building-review, batch 6): a sweep cannot work under a roof, and the building's roof is the well's -
    whatever gear and roof roll, an indoor well draws the beam across its curb and the wheel, no posts and no roof."""
    for gear in wg.GEARS:
        svg = wg.gear_svg(100.0, 50.0, 11.0, gear, True, indoor=True)
        assert 'data-gear="beam pulley"' in svg and "data-roof" not in svg and 'fill="none"' in svg and svg.count("<circle") == 1
        assert re.search(r'<line x1="89" y1="50" x2="111" y2="50"', svg)  # within the curb, clear of the walls round it
