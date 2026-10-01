"""What is left of the seam pass's helpers after feature 302 - the water body and its banks (`_water`), the pocket rings
(`_parts`, `_ring`) the grave cut reads - and the bank predicates (`tapers_to_a_point`, `jog_steps`) the tint and the ring
rules read. The pass itself (`close_seams`) was retired: the plots are laid as a partition (`tests/waterfields/test_partition.py`)."""

from typing import Any

from l7r.diagram.waterfields.banks import jog_steps, jog_vertices, tapers_to_a_point
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


def test_a_truncated_wedge_is_seen_as_tapering_to_a_point():
    assert tapers_to_a_point(_TRUNCATED_WEDGE, 5.0, 25.0, 20.0)


def test_a_chamfer_between_two_SHORT_edges_is_not_a_taper():
    """The guard that stops the predicate FABRICATING an apex (settlement-review, 2026-08-17).

    Its predecessor deduped the whole ring at the end width, which merges short edges ANYWHERE - so
    a staircase of chamfers mid-wall fused into a spike that was never in the drawing. Four measured
    fabrications on one roll, the worst turning a ring whose sharpest real corner is 86.7 deg into
    2.3, and one of them sat in the flooded candidate zone one roll from demoting an honest basin.

    Same 3.4 ft end edge and the same 20 deg convergence as the wedge above; only the ARMS are
    short. That is the whole difference between the end of a taper and a step in a wall."""
    chamfer = [(20.0, 5.0), (9.6, 1.7), (9.6, -1.7), (20.0, -5.0)]
    assert not tapers_to_a_point(chamfer, 5.0, 25.0, 20.0)


def test_a_parallel_sided_strip_is_not_a_taper_however_short_its_end():
    """The second fabrication guard, and the one the arm-length test alone does NOT catch.

    The angle between the two backward arms is the apex angle only when they DIVERGE; for parallel
    sides it is 0.0, which scores as maximally pointed while describing a strip of constant width.
    Measured live on Inashiro (ring #633: a parallel-sided strip with a 2.3 ft chamfer, converge
    exactly 0.0). A taper is narrow HERE and wide THERE, so the far ends of the arms must stand well
    apart before the angle is allowed to mean anything."""
    strip = [(200.0, 5.0), (0.0, 5.0), (0.0, 2.0), (200.0, 2.0)]
    assert not tapers_to_a_point(strip, 5.0, 25.0, 20.0)


def test_a_wedge_with_a_workable_end_is_not_a_taper():
    # 10.4 ft of end: two aze leave ~7.4 ft of standing water, which is a basin, not a point
    wide = [(200.0, 35.3), (9.6, 5.2), (9.6, -5.2), (200.0, -35.3)]
    assert not tapers_to_a_point(wide, 5.0, 25.0, 20.0)


def test_tapers_to_a_point_declines_a_ring_too_short_to_have_an_end():
    assert not tapers_to_a_point([(0.0, 0.0), (10.0, 0.0), (5.0, 8.0)], 5.0, 25.0, 20.0)


def test_jog_steps_counts_a_wall_that_steps_sideways_and_carries_on():
    assert jog_steps(_stepped(9.0), GRAIN) == 1
    assert jog_steps(_rect(0, 0, 200, 100), GRAIN) == 0


def test_jog_steps_ignores_a_step_under_the_placer_floor():
    # 2 ft is the placer's line (`_JOG_OFF_FT`), one notch under the gate's 3 ft; at GRAIN 2 a foot
    # is a pixel, so 1.9 px is under it and 2.1 px is over.
    assert jog_steps(_stepped(1.9), GRAIN) == 0
    assert jog_steps(_stepped(2.1), GRAIN) == 1


def test_jog_steps_ignores_a_hop_too_long_to_be_a_step():
    # a 31 px hop is a LIMB - an L-shaped parcel, which is the honest odd shape reclamation leaves
    assert jog_steps(_stepped(31.0), GRAIN) == 0


def test_jog_steps_ignores_a_run_too_short_to_be_a_wall():
    # the run BEFORE the hop is 5 px, under the 6 ft floor: a corner nub, not a wall carrying on
    assert jog_steps(_stepped(9.0, link_at=5.0), GRAIN) == 0


def test_jog_steps_passes_a_narrow_basin_on_its_own_end_wall():
    # THE REASON HEADINGS ARE COMPARED OVER THE FULL CIRCLE - a thin rectangle is two long parallel
    # runs a short link apart, which modulo 180 deg is indistinguishable from a step.
    assert jog_steps(_rect(0, 0, 300, 9), GRAIN) == 0


def test_jog_vertices_returns_the_two_ends_of_the_hop():
    assert jog_vertices(_stepped(9.0), GRAIN) == [((60.0, 0.0), (60.0, 9.0))]


def test_jog_steps_ignores_a_gently_curving_bund():
    # THE CLAUSE THIS HOLDS. A curve sampled into segments is a run, a link and a run resuming
    # near-parallel, with a perpendicular offset of a few feet purely from the bend - so without the
    # corner test the rule fires all along it. Measured on Kuwabata, whose paddies are long curved
    # parcels: 57 reported steps on 43 plot rings, every one a smooth bend.
    curve = [(0.0, 0.0)]
    for k in range(1, 9):
        curve.append((30.0 * k, 7.0 * k + 1.5 * k * k))  # each segment turns a few degrees on the last
    curve.append((curve[-1][0], curve[-1][1] + 200.0))
    curve.append((0.0, 200.0))
    assert jog_steps(curve, GRAIN) == 0


def test_water_skips_a_channel_with_a_single_point() -> None:
    """Feature 146: a channel record with fewer than two points has no stroke to build - it is skipped,
    not offset (which would raise). A one-point channel is what a trimmed lateral leaves behind."""
    from l7r.diagram.waterfields.seams import _water

    real = {"pts": [[0.0, 0.0], [100.0, 0.0]], "w": 6.0}
    stub = {"pts": [[50.0, 50.0]], "w": 6.0}
    empty: dict[str, object] = {"pts": [], "w": 6.0}
    assert _water([real, stub, empty], 1.0).equals(_water([real], 1.0)), "the stubs contribute no ink"
    assert _water([stub, empty], 1.0).is_empty, "stubs alone make no water at all"
