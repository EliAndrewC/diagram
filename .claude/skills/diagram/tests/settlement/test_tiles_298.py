"""Feature 298 - the cover tiles: the scrub's grass, the marsh's reeds and a bamboo stand's culms as one repeating tile per zone."""

from __future__ import annotations

import re

import pytest
from shapely.geometry import Point, box

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement._geom import KeepoutGrid
from l7r.diagram.settlement.homestead_parts.groves import BAMBOO_CULM
from l7r.diagram.settlement.land import tiles


@pytest.mark.parametrize("kind", ["grass", "reed", "bamboo"])
def test_a_tile_is_a_pattern_of_its_scatters_glyphs_at_its_density(kind: str) -> None:
    """Each tile is one `<pattern>` of the scatter's own glyphs; the grass and reed tiles carry the scatter's throws per area,
    the bamboo tile the stand's grid, and the same tile on every call (a fixed seed)."""
    svg = tiles.TILES[kind](1.0)
    assert svg.startswith(f'<pattern id="{tiles.pattern_id(kind, 1.0)}"') and svg.endswith("</pattern>")
    assert svg == tiles.TILES[kind](1.0), "the tile is the same on every map"
    side = tiles.COVER_TILE_FT
    if kind == "grass":
        n = round(side * side / tiles.GRASS_SQFT_PER_THROW)
        roots = {m for m in re.findall(r"M([-\d.]+,[-\d.]+)l", svg)}
        dots = svg.count("<circle")
        assert 0.9 * n <= len(roots) + dots <= 1.6 * n, (len(roots), dots, n)  # wrapped copies add a few
        assert 'stroke="#A7A860"' in svg and 'fill="#94A063"' in svg
    elif kind == "reed":
        assert 'stroke="#6E9377"' in svg and 'fill="#9FBBAE"' in svg and "<ellipse" in svg
        assert svg.count("<circle") >= round(side * side / tiles.REED_SQFT_PER_TINT)
    else:
        assert svg.count(f'stroke="{BAMBOO_CULM}"') >= tiles.BAMBOO_TILE_MARKS**2


def test_a_glyph_across_the_tiles_edge_is_drawn_again_at_the_opposite_edge() -> None:
    """Seamless: a glyph reaching past one edge is laid again past the other, and one well inside is laid once."""
    once = tiles._wrapped(10.0, 10.0, lambda x, y: f"<g{x:g},{y:g}/>", 5.0, 5.0, 1.0)
    assert once == "<g5,5/>"
    corner = tiles._wrapped(10.0, 10.0, lambda x, y: f"<g{x:g},{y:g}/>", 0.5, 9.5, 1.0)
    assert corner.count("<g") == 4 and "<g10.5,-0.5/>" in corner, "a corner glyph is laid at all four corners"


def test_the_defs_hold_the_tiles_a_map_uses_and_nothing_when_none() -> None:
    assert tiles.cover_defs(set()) == ""
    defs = tiles.cover_defs({("reed", 1.0), ("grass", 2.0)})
    assert defs.startswith("<defs>") and tiles.pattern_id("grass", 2.0) in defs and tiles.pattern_id("reed", 1.0) in defs
    assert tiles.pattern_id("grass", 2.0) == "cover-grass-2" and tiles.pattern_id("reed", 1.5) == "cover-reed-1_5"


def test_cover_rings_read_every_outline_and_hole_of_a_shape() -> None:
    shape = box(0, 0, 100, 100).difference(box(40, 40, 60, 60)).union(box(200, 0, 210, 10))
    rings = tiles.cover_rings(shape)
    assert len(rings) == 3 and all(len(r) >= 4 for r in rings), "two outlines and a hole"
    from shapely.geometry import GeometryCollection, LineString

    assert len(tiles.cover_rings(GeometryCollection([box(0, 0, 1, 1), LineString([(0, 0), (5, 5)])]))) == 1, "a line in a collection is not ground"
    nested = GeometryCollection([box(0, 0, 1, 1).union(box(5, 5, 6, 6)), LineString([(0, 0), (5, 5)])])
    assert len(tiles.cover_rings(nested)) == 2, "a multipolygon inside a collection is read too"


def test_the_keepout_shape_is_the_union_of_what_it_files_at_the_querys_pads() -> None:
    """`KeepoutGrid.shape` - every filed keep-out grown by its pad and the query's extra - holds every point `hit_many`
    refuses and none it keeps (to the margin)."""
    import numpy as np

    keep = KeepoutGrid()
    keep.rings([[(100.0, 100.0), (200.0, 100.0), (200.0, 200.0), (100.0, 200.0)]], pad=5.0, slot=1, reach=10.0)
    keep.segs([([(0.0, 300.0), (400.0, 300.0)], 4.0)])
    keep.rects([(300.0, 50.0, 350.0, 90.0)], closed=True)
    keep.circles([(50.0, 50.0, 20.0)], closed=True)
    shape = keep.shape((0.0, 3.0), (0.0, 0.0, 400.0, 400.0))
    rng = np.random.default_rng(298)
    xs, ys = rng.uniform(0, 400, 4000), rng.uniform(0, 400, 4000)
    hit = keep.hit_many(xs, ys, (0.0, 3.0))
    assert hit.any() and not hit.all(), "non-vacuity"
    for x, y, h in zip(xs.tolist(), ys.tolist(), hit.tolist(), strict=True):
        d = shape.distance(Point(x, y))
        assert (d == 0.0) if h else (d >= 0.0 and not shape.buffer(-0.5).contains(Point(x, y))), (x, y, h)
    assert KeepoutGrid().shape((0.0,), (0.0, 0.0, 10.0, 10.0)) is None, "nothing filed: no shape"


def test_a_bamboo_stand_is_its_ring_filled_with_the_bamboo_tile_where_its_marks_were() -> None:
    """The stand is one path of its ring filled with the bamboo tile, in its own slot (feature 298); the record's `marks` is
    the stand's grid seats inside the ring, as before; the tile goes into the map's <defs> at finish."""
    s = Settlement(W=600, H=600, seed=3)
    ring = [(100.0, 100.0), (200.0, 100.0), (200.0, 180.0), (100.0, 180.0)]
    assert s.bamboo_stand(ring) > 100
    rec = s.M["bamboo_stands"][-1]
    ink = s.out[rec["z"]]
    assert ink.count("<path") == 1 and f'url(#{tiles.pattern_id("bamboo", 1.0)})' in ink and f'stroke="{BAMBOO_CULM}"' not in ink
    s.flush_covers()
    assert tiles.pattern_id("bamboo", 1.0) in s.out[s._cover_slots["defs"]]
    assert s.bamboo_stand([(500.0, 500.0), (501.0, 500.0), (501.0, 501.0)]) == 0, "a stand too small for a seat draws nothing"


def test_the_grass_leaves_out_a_wood_but_its_fringe() -> None:
    """The scrub's grass reaches `WOOD_FRINGE_FT` in under a wood's edge and no further (GM 2026-09-27)."""
    from l7r.diagram.settlement.land.cover import WOOD_FRINGE_FT
    from tests.settlement._builders import _covered

    s = Settlement(W=800, H=800, seed=4)
    s.meta(name="T", scale="hamlet", ftpx=1)
    wood = [(300.0, 100.0), (700.0, 100.0), (700.0, 600.0), (300.0, 600.0)]
    s.commons([(60.0, 60.0), (560.0, 60.0), (560.0, 640.0), (60.0, 640.0)], role="pasture", woods=[wood])
    grass = _covered(s)
    assert grass.contains(Point(300.0 + WOOD_FRINGE_FT / 2, 350.0)), "the fringe under the wood's edge is grassed"
    assert not grass.contains(Point(300.0 + WOOD_FRINGE_FT * 3, 350.0)), "deep in the wood is not"
