"""The single tree's shade on a yard or a bed (GM 2026-10-02, `settlement/homestead_parts/tree_shade.py`): the plot's sun
ground runs from its north edge, `reach` east, west and south of it; a crown north of that line throws its shadow away."""

from l7r.diagram.settlement.homestead_parts.tree_shade import _plot_box, crown_in_ground, crown_shades, persimmons_shading_plots, sun_ground

PLOT = (0.0, 0.0, 40.0, 20.0)  # x -20..20, y -10..10 (+y south)


def test_a_crown_shades_a_plot_from_east_west_and_south_never_from_the_north() -> None:
    assert crown_shades(65.0, 0.0, 10.0, PLOT, 50.0), "east, within the reach and the crown"
    assert crown_shades(-65.0, 5.0, 10.0, PLOT, 50.0), "west"
    assert crown_shades(0.0, 65.0, 10.0, PLOT, 50.0), "south"
    assert not crown_shades(0.0, -21.0, 10.0, PLOT, 50.0), "north of the north edge, its crown clear of it"
    assert crown_shades(0.0, -19.0, 10.0, PLOT, 50.0), "a crown that reaches over the north edge"
    assert not crown_shades(81.0, 0.0, 10.0, PLOT, 50.0), "past the reach and the crown"
    assert not crown_shades(75.0, 75.0, 10.0, PLOT, 50.0), "off the corner of the sun ground"


def test_a_plot_is_read_by_its_quad_else_its_box() -> None:
    assert _plot_box({"poly": [[0, 0], [10, 0], [10, 4], [0, 4]], "x": 99, "y": 99, "w": 1, "h": 1}) == (5.0, 2.0, 10.0, 4.0)
    assert _plot_box({"x": 1, "y": 2, "w": 3, "h": 4}) == (1.0, 2.0, 3.0, 4.0)
    assert _plot_box({"x": 1}) is None


def test_the_map_check_names_each_crown_in_a_plots_sun_at_the_maps_scale() -> None:
    M = {
        "meta": {"ftpx": 2.0},  # two feet a pixel: 50 ft is 25 px
        "threshing_yards": [{"x": 0, "y": 0, "w": 40, "h": 20}, {"x": 500}],
        "gardens": [{"poly": [[200, 0], [220, 0], [220, 10], [200, 10]]}],
        "persimmons": [{"x": 50, "y": 0, "r": 6}, {"x": 0, "y": -40, "r": 6}],
    }
    assert persimmons_shading_plots(M, 50.0) == [("threshing_yards", (50.0, 0.0), (0.0, 0.0))]
    assert persimmons_shading_plots({"persimmons": M["persimmons"], "threshing_yards": M["threshing_yards"][:1]}, 50.0) != [], "no meta: a foot a pixel"


def test_a_plots_sun_ground_taken_once_answers_as_the_crown_test_does() -> None:
    """Feature 314: the sun ground taken once (`sun_ground`) and asked of many crowns (`crown_in_ground`) is `crown_shades`."""
    g = sun_ground(PLOT, 50.0)
    for x in range(-90, 91, 15):
        for y in range(-40, 91, 13):
            assert crown_in_ground(float(x), float(y), 10.0, g) == crown_shades(float(x), float(y), 10.0, PLOT, 50.0), (x, y)
