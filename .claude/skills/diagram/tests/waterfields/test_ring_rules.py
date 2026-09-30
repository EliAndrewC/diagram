"""Feature 287 T02 (M1): every paddy-ring rule is one predicate in `waterfields/ring_rules.py`, and each is shown
here on constructed rings - one that keeps the rule and one that breaks it - so a predicate that stopped firing
fails here before any finished map is read."""

from __future__ import annotations

import math

import pytest

from l7r.diagram.waterfields.ring_rules import (
    AREA_FLOOR,
    BASIN_MIN_WIDTH_FT,
    OVERCOUNT_CEILING,
    RingContext,
    arrowhead,
    collector_crossings,
    collector_strokes,
    crosses_pond_rim,
    dart,
    narrow,
    needle,
    overcount,
    ring_area,
    ring_violations,
    self_crossing,
    staircase,
    supply_intrusions,
    supply_strokes,
    too_small,
    under_island,
    working_width,
)


def _box(x0: float, y0: float, x1: float, y1: float) -> list[list[float]]:
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


SQUARE = _box(0.0, 0.0, 40.0, 40.0)
NEEDLE = [[0.0, 0.0], [100.0, -6.0], [100.0, 6.0]]  # a ~6.9 deg tip
ARROW = [[0.0, 0.0], [100.0, -30.0], [60.0, 0.0], [100.0, 30.0]]  # 33.4 deg tip, solidity 0.6
TWO_STEPS = [[0.0, 0.0], [20.0, 0.0], [20.0, 5.0], [40.0, 5.0], [40.0, 10.0], [60.0, 10.0], [60.0, 50.0], [0.0, 50.0]]
ONE_STEP = [[0.0, 0.0], [20.0, 0.0], [20.0, 5.0], [60.0, 5.0], [60.0, 50.0], [0.0, 50.0]]
BOWTIE = [[0.0, 0.0], [10.0, 10.0], [10.0, 0.0], [0.0, 10.0]]


def test_ring_area_is_the_shoelace() -> None:
    assert ring_area(SQUARE) == 1600.0
    assert ring_area(NEEDLE) == pytest.approx(600.0)


def test_a_needle_fires_and_a_square_does_not() -> None:
    assert needle(NEEDLE)
    assert not needle(SQUARE)


def test_the_area_floor_is_a_ratio_to_the_design_cell() -> None:
    assert not too_small(SQUARE, 1600.0)
    assert too_small(SQUARE, 1600.0 / (AREA_FLOOR * 0.9))  # just under the floor
    assert not too_small(SQUARE, 1600.0 / (AREA_FLOOR * 1.1))


def test_two_steps_are_a_staircase_and_one_is_not() -> None:
    assert staircase(TWO_STEPS, 2.0)  # grain 2 / ftpx at 1 ft per px
    assert not staircase(ONE_STEP, 2.0)
    assert not staircase(SQUARE, 2.0)


def test_a_bowtie_crosses_itself() -> None:
    assert self_crossing(BOWTIE)
    assert not self_crossing(SQUARE)
    assert not self_crossing([[0.0, 0.0], [1.0, 1.0]])  # under three vertices is not judged


def test_the_overcount_is_the_lapped_ground_over_the_union() -> None:
    assert overcount([SQUARE, _box(40.0, 0.0, 80.0, 40.0)]) == pytest.approx(0.0)
    lapped = overcount([SQUARE, _box(28.0, 0.0, 68.0, 40.0)])  # a 30% lap
    assert lapped == pytest.approx(480.0 / 2720.0)
    assert lapped >= OVERCOUNT_CEILING
    with pytest.raises(ValueError):
        overcount([[[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]]])


def test_the_working_width_floor() -> None:
    g = 2.0  # 1 px per ft, so the floor is BASIN_MIN_WIDTH_FT px
    thin = _box(0.0, 0.0, BASIN_MIN_WIDTH_FT - 2.0, 100.0)
    wide = _box(0.0, 0.0, BASIN_MIN_WIDTH_FT + 8.0, 100.0)
    assert working_width(thin) == pytest.approx(BASIN_MIN_WIDTH_FT - 2.0)
    assert narrow(thin, g)
    assert not narrow(wide, g)
    assert working_width([[0.0, 0.0], [10.0, 0.0], [20.0, 0.0]]) == 0.0  # no area, no width


def test_a_small_sharp_basin_is_a_dart() -> None:
    cell = 1000.0
    tip = math.tan(math.radians(10.0))
    truncated = [[-0.25, 0.25 / tip], [0.25, 0.25 / tip], [30.0 * tip, 30.0], [-30.0 * tip, 30.0]]  # a 20 deg dart whose point is cut 0.5 px wide
    assert not needle(truncated)  # blunt as a raw ring
    assert dart(truncated, cell)  # the deduped ring shows the point
    assert dart(NEEDLE, cell)
    assert not dart(NEEDLE, 700.0)  # 600 px is 0.86 of this cell: too big to be a dart
    assert not dart(_box(0.0, 0.0, 20.0, 20.0), cell)  # small and blunt
    assert not dart([[0.0, 0.0], [0.5, 0.0], [0.0, 0.5]], cell)  # collapses under the dedup, blunt raw


def test_an_arrowhead_is_pointed_and_notched() -> None:
    assert arrowhead(ARROW)
    assert not arrowhead(SQUARE)
    assert not arrowhead(NEEDLE)  # pointed but convex


def test_a_bund_inside_the_supply_stroke_is_found() -> None:
    strokes = supply_strokes([{"poly": [[0.0, 50.0], [200.0, 50.0]], "w": 10.0}, {"poly": [[0.0, 0.0]], "w": 4.0}])
    assert len(strokes) == 1  # a stroke of one point has no centerline
    assert set(supply_intrusions(_box(20.0, 53.0, 60.0, 90.0), strokes)) == {(20, 53), (60, 53)}  # the first sample of each edge in the water
    assert supply_intrusions(_box(20.0, 56.0, 60.0, 90.0), strokes) == []  # abuts: 6 px off a 5 px half-width
    assert supply_intrusions(_box(20.0, 200.0, 60.0, 240.0), strokes) == []  # outside the stroke's reach
    assert supply_intrusions(_box(203.0, 48.0, 240.0, 90.0), strokes) == []  # past the stroke's end


def test_a_bund_across_the_collector_is_found() -> None:
    drains = collector_strokes([{"poly": [[0.0, 50.0], [200.0, 50.0]], "w": 6.0}])
    assert drains[0][1] == 3.0
    across = [[50.0, 49.5], [60.0, 50.5], [60.0, 100.0], [50.0, 100.0]]
    assert collector_crossings(across, drains) == [(50, 50)]
    assert collector_crossings(_box(50.0, 60.0, 60.0, 100.0), drains) == []


def test_a_ring_crossing_the_pond_rim_is_found() -> None:
    pond = (50.0, 50.0, 10.0, 10.0)
    assert crosses_pond_rim(_box(45.0, 45.0, 70.0, 70.0), pond)
    assert not crosses_pond_rim(_box(0.0, 0.0, 100.0, 100.0), pond)  # the pond sunk inside one plot
    # T04: a bund CHORDING the pond between two outside vertices meets it (the vertex-parity test missed it)...
    assert crosses_pond_rim([[40.0, 48.0], [60.0, 48.0], [60.0, 30.0], [40.0, 30.0]], pond)
    # ...and so does a ring standing wholly in the water; one that only touches the rim does not
    assert crosses_pond_rim(_box(48.0, 48.0, 52.0, 52.0), pond)
    assert not crosses_pond_rim(_box(40.0, 30.0, 60.0, 40.0), pond)


def test_a_ring_under_the_grave_island_is_found() -> None:
    disc = (50.0, 50.0, 5.0)
    assert under_island(_box(0.0, 0.0, 100.0, 100.0), disc)  # the basin's floor under the mound
    assert under_island(_box(52.0, 0.0, 80.0, 100.0), disc)  # a bund under the mound
    assert not under_island(_box(60.0, 0.0, 80.0, 100.0), disc)


def test_ring_violations_names_every_rule_broken() -> None:
    assert ring_violations(SQUARE, RingContext()) == set()
    assert ring_violations(SQUARE, RingContext(cell=1600.0, g=2.0)) == set()
    # the working width (W26) and the dart (W27) are recorded, not enforced - the research contradicts both (T13)
    assert ring_violations(NEEDLE, RingContext(cell=1000.0, g=2.0)) == {"needle"}
    assert narrow(NEEDLE, 2.0) and dart(NEEDLE, 1000.0), "though the needle breaks both recorded rules"
    assert ring_violations(BOWTIE, RingContext(cell=1000.0)) == {"crossing", "area"}
    assert ring_violations(ARROW, RingContext()) == {"arrowhead"}
    assert ring_violations(TWO_STEPS, RingContext(g=2.0)) == {"steps"}
    ctx = RingContext(
        supplies=supply_strokes([{"poly": [[0.0, 50.0], [200.0, 50.0]], "w": 10.0}]),
        drains=collector_strokes([{"poly": [[0.0, 50.0], [200.0, 50.0]], "w": 6.0}]),
        ponds=[(50.0, 50.0, 10.0, 10.0)],
        graves=[(50.0, 50.0, 5.0)],
    )
    assert ring_violations([[50.0, 49.5], [60.0, 50.5], [60.0, 100.0], [50.0, 100.0]], ctx) == {"stroke", "collector", "pond", "grave"}


def test_the_fan_context_is_the_one_the_gate_reads_off_the_manifest() -> None:
    """`fan_context` builds a fan's RingContext from the engine's channels exactly as `_comb_record_ditches` records
    them (0.1 px points and widths, a repeated point dropped) and the cell as `_comb_record_field` records it - so the
    seam pass and the gate ask the rules of one context. The drain is the collector; every other supply role a stroke."""
    from l7r.diagram.waterfields.ring_rules import as_recorded, fan_context

    channels = [
        {"pts": [(0.04, 50.02), (0.05, 50.03), (200.0, 50.0)], "w": 10.04, "role": "main"},
        {"pts": [(0.0, 150.0), (200.0, 150.0)], "w": 3.0, "w_tail": 5.46, "role": "drain"},
        {"pts": [(0.0, 150.0)], "w": 3.0, "role": "drain"},  # a drain with no course is no collector
        {"pts": [(0.0, 90.0), (5.0, 90.0)], "w": 2.0, "role": "hairline"},  # no supply role, not a stroke
    ]
    ctx = fan_context(channels, 2.0, 1234.56, ponds=[(1, 2, 3, 4)], graves=[(5, 6, 7)])
    assert ctx.cell == 1234.6 and ctx.g == 2.0
    assert [s.pts for s in ctx.supplies] == [[(0.0, 50.0), (200.0, 50.0)]] and ctx.supplies[0].w0 == 10.0
    assert ctx.drains == [([(0.0, 150.0), (200.0, 150.0)], 2.75)]
    assert ctx.ponds == [(1.0, 2.0, 3.0, 4.0)] and ctx.graves == [(5.0, 6.0, 7.0)]
    assert fan_context([], None, None).cell is None
    assert as_recorded([(1.04, 2.06)]) == [(1.0, 2.1)]


def test_a_collector_edge_away_from_the_drain_is_passed_over() -> None:
    """The collector rule's bounding-box prefilter decides nothing: an edge with an end outside the drain's reach is not
    measured, and an edge running across the drain is still found."""
    drains = collector_strokes([{"poly": [[0.0, 50.0], [200.0, 50.0]], "w": 6.0}])
    assert collector_crossings(_box(20.0, 60.0, 80.0, 90.0), drains) == []
    assert collector_crossings([[20.0, 50.5], [80.0, 49.5], [80.0, 90.0], [20.0, 90.0]], drains) == [(20, 50)]
