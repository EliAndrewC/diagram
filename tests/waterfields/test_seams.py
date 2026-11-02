"""What is left of the seam pass's helpers after feature 302 - the water body and its banks (`_water`), the pocket rings
(`_parts`, `_ring`) the grave cut reads - and the bank predicates (`tapers_to_a_point`, `jog_steps`) the tint and the ring
rules read. The pass itself (`close_seams`) was retired: the plots are laid as a partition (`tests/waterfields/test_partition.py`)."""

from typing import Any

from l7r.diagram.waterfields.seams import _parts, _ring, _water

# A 20 deg wedge truncated to a 3.4 ft end - the shape that reads as a pond when it wears the water
# tint, and the live instance the Inashiro review found (30.0 -> 3.4 ft over 75 ft).
_TRUNCATED_WEDGE = [(200.0, 35.3), (9.6, 1.7), (9.6, -1.7), (200.0, -35.3)]


def _stepped(off: float, link_at: float = 60.0, run: float = 140.0) -> list[tuple[float, float]]:
    """A basin whose north wall runs east, hops `off` px south at x=link_at, and carries on east."""
    return [(0.0, 0.0), (link_at, 0.0), (link_at, off), (link_at + run, off), (link_at + run, 100.0), (0.0, 100.0)]


def Polygon(*args: Any, **kwargs: Any) -> Any:
    """`shapely.geometry.Polygon`, imported on FIRST USE rather than at collection (feature 237, FR-007).

    A module-level import here cost EVERY one of the ten gate workers 16.3 MiB - shapely plus the numpy it
    drags in (`specs/237-lean-test-collection/research.md` R9) - to collect a file whose tests one worker
    runs. `unary_union` was already imported inside the one helper that uses it; this is the same move for
    the name the whole file uses. No call site changes, and a test is not a per-plot path.
    """
    from shapely.geometry import Polygon as _Polygon

    return _Polygon(*args, **kwargs)


GRAIN = 2.0


def _rect(x0: float, y0: float, x1: float, y1: float) -> list[tuple[float, float]]:
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def test_water_covers_the_outside_of_a_bend():
    # flat caps alone leave a wedge on the outside of every turn, and a basin planted in that wedge
    # puts a bund in the water (the defect this closed on Inashiro)
    chan = [{"pts": [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0)], "w": 12.0, "w_tail": 12.0, "role": "branch"}]
    stroke = _water(chan, GRAIN)
    assert stroke.contains(Polygon(_rect(98, -2, 102, 2)).centroid), "the bend's outside corner is uncovered"


def test_parts_drops_invalid_rings():
    bowtie = Polygon([(0, 0), (10, 10), (10, 0), (0, 10)])
    assert _parts(bowtie) == []


def test_ring_drops_vertices_that_rounding_collapses():
    assert _ring(Polygon([(0, 0), (0.02, 0.01), (10, 0), (10, 10), (0, 10)])) == [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert _ring(Polygon([(0, 0), (10, 0), (10, 10), (0, 10), (0.02, 0.01)])) == [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)], "a last point rounded onto the first"


def test_water_skips_a_channel_with_a_single_point() -> None:
    """Feature 146: a channel record with fewer than two points has no stroke to build - it is skipped,
    not offset (which would raise). A one-point channel is what a trimmed lateral leaves behind."""
    from l7r.diagram.waterfields.seams import _water

    real = {"pts": [[0.0, 0.0], [100.0, 0.0]], "w": 6.0}
    stub = {"pts": [[50.0, 50.0]], "w": 6.0}
    empty: dict[str, object] = {"pts": [], "w": 6.0}
    assert _water([real, stub, empty], 1.0).equals(_water([real], 1.0)), "the stubs contribute no ink"
    assert _water([stub, empty], 1.0).is_empty, "stubs alone make no water at all"
