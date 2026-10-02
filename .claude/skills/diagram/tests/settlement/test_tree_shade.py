"""A tree's shade on a yard or a bed (GM 2026-10-02, `settlement/homestead_parts/tree_shade.py`; feature 310): the plot's sun
ground runs from its north edge, `reach` east, west and south of it; a crown north of that line throws its shadow away."""

from l7r.diagram.settlement.homestead_parts.tree_shade import BAMBOO_SHADE_FT, bamboo_shading_plots, box_shades, crown_shades, map_bamboo, map_trees, plot_box, sun_box, trees_shading_plots

PLOT = (0.0, 0.0, 40.0, 20.0)  # x -20..20, y -10..10 (+y south)


def test_a_crown_shades_a_plot_from_east_west_and_south_never_from_the_north() -> None:
    assert crown_shades(65.0, 0.0, 10.0, PLOT, 50.0), "east, within the reach and the crown"
    assert crown_shades(-65.0, 5.0, 10.0, PLOT, 50.0), "west"
    assert crown_shades(0.0, 65.0, 10.0, PLOT, 50.0), "south"
    assert not crown_shades(0.0, -21.0, 10.0, PLOT, 50.0), "north of the north edge, its crown clear of it"
    assert crown_shades(0.0, -19.0, 10.0, PLOT, 50.0), "a crown that reaches over the north edge"
    assert not crown_shades(81.0, 0.0, 10.0, PLOT, 50.0), "past the reach and the crown"
    assert not crown_shades(75.0, 75.0, 10.0, PLOT, 50.0), "off the corner of the sun ground"


def test_the_sun_box_is_the_same_ground_as_the_predicate() -> None:
    """`sun_box` is the keep-out form `_crown_covers` reads: x -70..70, y -10..60 for the plot above at 50."""
    assert sun_box(PLOT, 50.0) == (0.0, 25.0, 70.0, 35.0)


def test_a_plot_is_read_by_its_quad_else_its_box() -> None:
    assert plot_box({"poly": [[0, 0], [10, 0], [10, 4], [0, 4]], "x": 99, "y": 99, "w": 1, "h": 1}) == (5.0, 2.0, 10.0, 4.0)
    assert plot_box({"x": 1, "y": 2, "w": 3, "h": 4}) == (1.0, 2.0, 3.0, 4.0)
    assert plot_box({"x": 1}) is None


def test_the_map_check_reads_every_recorded_tree_at_the_maps_scale() -> None:
    M = {
        "meta": {"ftpx": 2.0},  # two feet a pixel: 50 ft is 25 px
        "threshing_yards": [{"x": 0, "y": 0, "w": 40, "h": 20}, {"x": 500}],
        "gardens": [{"poly": [[200, 0], [220, 0], [220, 10], [200, 10]]}],
        "tree_crowns": [50.0, 0.0, 6.0, 0.0, -40.0, 6.0],
        "scrub_pines": [[210.0, 30.0, 3.0]],
        "planted_trees": [{"kind": "willow", "trees": [[-40.0, 0.0, 4.0]]}],
    }
    assert [t[0] for t in map_trees(M)] == ["crown", "crown", "pine", "willow"]
    assert trees_shading_plots(M, 50.0) == [
        ("threshing_yards", "crown", (50.0, 0.0), (0.0, 0.0)),
        ("gardens", "pine", (210.0, 30.0), (210.0, 5.0)),
        ("threshing_yards", "willow", (-40.0, 0.0), (0.0, 0.0)),
    ]
    assert trees_shading_plots({"tree_crowns": [50.0, 0.0, 6.0], "threshing_yards": M["threshing_yards"][:1]}, 50.0) != [], "no meta: a foot a pixel"


def test_a_box_shades_a_plot_where_it_overlaps_the_sun_ground_not_where_it_touches() -> None:
    assert box_shades(65.0, -5.0, 75.0, 5.0, PLOT, 50.0), "east, inside the reach"
    assert not box_shades(70.0, -5.0, 80.0, 5.0, PLOT, 50.0), "touching the reach's edge is not inside it"
    assert not box_shades(-5.0, -30.0, 5.0, -10.0, PLOT, 50.0), "north of the north edge"


def test_the_bamboo_check_reads_every_mark_and_stand_at_bamboos_reach() -> None:
    """Feature 315: a culm mark by its reach's box, a stand by its outline's extent (else its box), at `BAMBOO_SHADE_FT`."""
    assert BAMBOO_SHADE_FT == 50.0, "the timber bamboos' 10 m gives the canopy reach's shadow (research R2)"
    M = {
        "threshing_yards": [{"x": 0, "y": 0, "w": 40, "h": 20}],
        "gardens": [],
        "bamboo_marks": [[65.0, 0.0, 3.0], [0.0, -40.0, 3.0]],
        "bamboo_stands": [{"poly": [[-80, 30], [-60, 30], [-60, 50], [-80, 50]], "role": "homestead"}, {"x": 300, "y": 0, "w": 16, "h": 22, "role": "thicket"}],
    }
    assert [b[0] for b in map_bamboo(M)] == ["mark", "mark", "homestead", "thicket"]
    assert bamboo_shading_plots(M, BAMBOO_SHADE_FT) == [
        ("threshing_yards", "mark", (65.0, 0.0), (0.0, 0.0)),
        ("threshing_yards", "homestead", (-70.0, 40.0), (0.0, 0.0)),
    ]
    assert bamboo_shading_plots({**M, "meta": {"ftpx": 10.0}}, BAMBOO_SHADE_FT) == [], "at ten feet a pixel the reach is 5 px: none in it"
