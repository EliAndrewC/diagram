"""The corner weld (feature 315, cohort seed 22, `hamletgen/ways/weld.py`)."""

from __future__ import annotations

from shapely.geometry import Polygon

from l7r.diagram.hamletgen.ways import law
from l7r.diagram.hamletgen.ways.weld import WELD_PX, _at, weld_corner


def _seed_22() -> list[dict]:
    # seed 22's two access corridors: lane 1's corner stands 0.4 px past lane 0's tread
    return [{"pts": [[1559.0, 1959.0], [1639.0, 1949.0], [1734.0, 1884.0]]}, {"pts": [[1564.0, 2118.0], [1564.0, 1958.0], [1774.0, 1968.0]]}]


def test_two_ways_meeting_a_hair_apart_share_one_vertex() -> None:
    lanes = _seed_22()
    loops = law.needle_loops({"lanes": lanes})
    assert len(loops) == 1, "found: the sliver seed 22 was refused for"
    face, bounding = loops[0]
    welded = weld_corner(lanes, face, bounding)
    assert welded is not None and set(welded) == {0, 1}
    after = [{"pts": [list(p) for p in welded.get(i, [tuple(q) for q in ln["pts"]])]} for i, ln in enumerate(lanes)]
    assert law.needle_loops({"lanes": after}) == [], "no face is left where they meet"
    assert tuple(welded[1][1]) in {tuple(p) for p in welded[0]}, "the corner is a vertex of the tread"


def test_only_a_sliver_is_welded_and_only_a_near_corner() -> None:
    lanes = _seed_22()
    wide = Polygon([(0, 0), (100, 0), (100, 40), (0, 40)])
    assert weld_corner(lanes, wide, [0, 1]) is None, "a face a person could stand on is no sliver"
    sliver = Polygon([(1564.0, 1958.0), (1568.0, 1958.0), (1568.0, 1958.5), (1564.0, 1958.5)])
    far = [{"pts": [[1559.0, 1950.0], [1639.0, 1940.0]]}, {"pts": [[1564.0, 2118.0], [1564.0, 1958.0], [1774.0, 1968.0]]}]
    assert weld_corner(far, sliver, [0, 1]) is None, f"a corner more than {WELD_PX} px off the tread is not moved"
    on = [{"pts": [[1559.0, 1958.0], [1639.0, 1958.0]]}, {"pts": [[1564.0, 2118.0], [1564.0, 1958.0], [1774.0, 1968.0]]}]
    assert weld_corner(on, sliver, [0, 1]) is None, "a corner already on the tread is left"
    shared = [{"pts": [[1559.0, 1958.4], [1564.0, 1958.4], [1639.0, 1958.4]]}, {"pts": [[1564.0, 2118.0], [1564.0, 1958.0], [1774.0, 1968.0]]}]
    assert weld_corner(shared, sliver, [0, 1]) == {1: [(1564.0, 2118.0), (1564.0, 1958.4), (1774.0, 1968.0)]}, "onto a vertex the tread has: only the corner moves"


def test_a_point_is_found_by_its_arc_length() -> None:
    p = [(0.0, 0.0), (0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]
    assert _at(p, 15.0) == (2, (10.0, 5.0)) and _at(p, 99.0) == (2, (10.0, 10.0))
