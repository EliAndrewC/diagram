"""The counted work (feature 443 T01, D1-D3): each counting site adds its kind under its function, and a roll's counts are
attributed to the stage that made them."""

import numpy as np
import pytest

from l7r.diagram import work_counts
from l7r.diagram.overlap.registry import Standing
from l7r.diagram.settlement._geom import indexes, primitives

SQUARE = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]


@pytest.fixture(autouse=True)
def _fresh() -> None:
    work_counts.reset()


def _ops() -> dict[str, int]:
    return {k: n for k, n in work_counts.OPS.items() if n}


def test_reset_clears_and_by_kind_sums_over_functions() -> None:
    work_counts.OPS["dist@a"] += 2
    work_counts.OPS["dist@b"] += 3
    work_counts.OPS["candidate@c"] += 1
    work_counts.BY_STAGE["x"] = {"dist@a": 2}
    assert work_counts.by_kind(dict(work_counts.OPS)) == {"dist": 5, "candidate": 1}
    work_counts.reset()
    assert not work_counts.OPS and not work_counts.BY_STAGE
    assert set(work_counts.KINDS) >= {"pt_test", "seg_test", "dist", "index_query", "index_examined", "candidate", "placed", "dropped", "moved"}


def test_the_primitives_count_one_test_or_one_per_element() -> None:
    primitives.point_in_poly(5.0, 5.0, SQUARE)
    primitives.points_in_poly([(1.0, 1.0), (20.0, 20.0), (5.0, 5.0)], SQUARE)
    primitives.seg_dist(0.0, 5.0, (1.0, 0.0), (1.0, 10.0))
    primitives.seg_dists([(0.0, 0.0), (1.0, 1.0)], [((0.0, 0.0), (1.0, 0.0)), ((0.0, 1.0), (1.0, 1.0)), ((2.0, 2.0), (3.0, 3.0))])
    primitives.ring_meets_ellipse(SQUARE, 50.0, 50.0, 1.0, 1.0)
    primitives.segments_cross((0.0, 0.0), (1.0, 1.0), (0.0, 1.0), (1.0, 0.0))
    primitives.seg_intersect((0.0, 0.0), (1.0, 1.0), (0.0, 1.0), (1.0, 0.0))
    chains = [[((0.0, 0.0), (10.0, 0.0), (0.0, -1.0)), ((10.0, 0.0), (10.0, 10.0), (1.0, 0.0))]]
    primitives.chain_violated(50.0, 50.0, chains, 1.0)
    primitives.chain_violated_many(np.array([50.0, 60.0, 70.0]), np.array([50.0, 60.0, 70.0]), chains, 1.0)
    assert _ops() == {
        "pt_test@point_in_poly": 1,
        "pt_test@points_in_poly": 3,
        "dist@seg_closest": 1,
        "dist@seg_dists": 6,
        "seg_test@ring_meets_ellipse": 4,
        "seg_test@segments_cross": 1,
        "seg_test@seg_intersect": 1,
        "seg_test@chain_violated": 2,
        "seg_test@chain_violated_many": 6,
    }


def test_an_index_counts_its_queries_and_the_entries_it_hands_back() -> None:
    grid = indexes.PointGrid(cell=10.0)
    grid.extend([("a", 1.0, 1.0, 2.0, 2.0), ("b", 3.0, 3.0, 4.0, 4.0), ("c", 25.0, 25.0, 26.0, 26.0)])
    assert len(grid.near(1.5, 1.5)) == 2  # one cell: the common case
    assert len(grid.near(15.0, 15.0, pad=12.0)) == 3  # several cells
    ring = indexes.RingIndex(SQUARE, cell=64.0)
    assert ring.inside(5.0, 5.0)
    assert list(ring.inside_many(np.array([5.0, 50.0]), np.array([5.0, 50.0]))) == [True, False]
    ops = _ops()
    assert ops["index_query@PointGrid.near"] == 2 and ops["index_examined@PointGrid.near"] == 5
    assert ops["index_query@RingIndex.inside"] == 1 and ops["index_examined@RingIndex.inside"] == 4  # every edge of the square spans its one row
    assert ops["index_query@RingIndex.inside_many"] == 2


def test_inside_many_counts_the_edges_it_asks_point_by_point() -> None:
    bow = [(0.0, 0.0), (10.0, 10.0), (10.0, 0.0), (0.0, 10.0)]  # shapely reads a bow tie as invalid: every point in its box is asked
    indexes.RingIndex(bow).inside_many(np.array([2.0, 50.0]), np.array([5.0, 50.0]))
    assert _ops()["index_examined@RingIndex.inside_many"] == 1 * len(bow)


def test_the_registry_counts_candidates_placements_drops_and_moves() -> None:
    st = Standing({}, 1000.0, 1000.0)
    a = {"x": 100.0, "y": 100.0, "r": 8, "vr": 12.4}
    assert st.admits("wells", {"x": 300.0, "y": 300.0, "r": 8, "vr": 12.4})
    st.record("wells", a)
    assert not st.admits("wells", {"x": 101.0, "y": 100.0, "r": 8, "vr": 12.4})
    ops = _ops()
    assert ops["candidate@Standing.conflicts"] == 3 and ops["placed@Standing.record"] == 1
    assert ops["index_examined@Standing.conflicts"] >= 1
    a["x"] = 400.0
    st.rerecord("wells", a)
    st.rerecord("wells", a)  # nothing it covers moved: no move counted
    pocket = st.hold("wells", {"x": 700.0, "y": 700.0, "r": 8, "vr": 12.4})
    st.release("wells", pocket)
    st.rerecord("wells", {"x": 800.0, "y": 800.0, "r": 8, "vr": 12.4})  # an unheld record's rerecord is its first placement
    st.forget("wells", a)
    st.forget("wells", a)  # a second forget finds nothing held
    ops = _ops()
    assert ops["moved@Standing.rerecord"] == 1, "a reshape is a move"
    assert ops["placed@Standing.record"] == 2, "the first well and the unheld one; a hold and its release are neither"
    assert ops["dropped@Standing.forget"] == 1, "the one forget of a placed record"
