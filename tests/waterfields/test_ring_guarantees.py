"""Feature 287 (water W16-W25): the seam pass GUARANTEES every paddy-ring rule where it decides the rings.

Each test drives the placer - `hold_ring_rules`, which a later cut (a grave island) re-holds the rules with, or the split it
shares with `waterfields/settle.py` - on constructed rings that include the violating case (feature 302 retired the seam pass and
its weld ladder; the construction's own guarantee is `tests/waterfields/test_settle.py`), and asks the finished rings the rule's ONE
predicate in `waterfields/ring_rules.py`, the one the finished-map tests call. A staircase (W23) is one of the five rules
the GM named (`test_a_bund_does_not_build_a_flight_of_steps`).
"""

from __future__ import annotations

from typing import Any

from l7r.diagram.waterfields.ring_rules import (
    RingContext,
    arrowhead,
    as_recorded,
    collector_crossings,
    fan_context,
    needle,
    overcount,
    ring_area,
    ring_violations,
    staircase,
    supply_intrusions,
    too_small,
)

G = 2.0  # the grain at a hamlet's 1 ft per px: 2 / ftpx


def _poly(ring: Any) -> Any:
    from shapely.geometry import Polygon

    return Polygon(ring).buffer(0)


def _rect(x0: float, y0: float, x1: float, y1: float) -> list[tuple[float, float]]:
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _union_area(rings: list[Any]) -> float:
    from shapely.ops import unary_union

    return float(unary_union([_poly(r) for r in rings]).area)


# A bund stepping sideways twice along its low wall: y 0, then 6 px over, then 6 px more - the GM's "flight of steps".
TWO_STEPS = [(0.0, 0.0), (40.0, 0.0), (40.0, 6.0), (80.0, 6.0), (80.0, 12.0), (120.0, 12.0), (120.0, 60.0), (0.0, 60.0)]
# ...and four times, the worst ring the record names (cohort seed 12's four steps).
FOUR_STEPS = [
    (0.0, 0.0),
    (30.0, 0.0),
    (30.0, 6.0),
    (60.0, 6.0),
    (60.0, 12.0),
    (90.0, 12.0),
    (90.0, 18.0),
    (120.0, 18.0),
    (120.0, 24.0),
    (150.0, 24.0),
    (150.0, 80.0),
    (0.0, 80.0),
]


def _hold(rings: list[Any], ctx: RingContext) -> list[dict[str, Any]]:
    from l7r.diagram.waterfields.seams.close import hold_ring_rules

    plots = [{"poly": list(r), "fill": "#A6C398"} for r in rings]
    hold_ring_rules(plots, ctx)
    return plots


def test_a_bund_does_not_build_a_flight_of_steps() -> None:
    """W23, one of the GM's five: a ring carrying two or more sideways steps is SPLIT along the line that continues the
    step's hop - the wall "continuing on and meeting at the four way intersection" - and no ring leaves the pass with more
    than one step. Every part here clears the area floor, so no ground is lost: the parts tile the staircase exactly."""
    ctx = RingContext(cell=1500.0, g=G)
    for ring in (TWO_STEPS, FOUR_STEPS):
        assert staircase(ring, G), "the fixture is a staircase"
        plots = _hold([ring], ctx)
        assert len(plots) >= 2, "the staircase was cut, not kept"
        assert not [p for p in plots if staircase(p["poly"], G)], "no ring carries more than one step"
        assert all(not ring_violations(as_recorded(p["poly"]), ctx) for p in plots), "and every part keeps every ring rule"
        assert abs(_union_area([p["poly"] for p in plots]) - ring_area(ring)) < 1.0, "ground is conserved: the parts tile it"
        assert overcount([p["poly"] for p in plots]) < 0.001, "and they do not lap"
    boxes = sorted((min(x for x, _y in p["poly"]), max(x for x, _y in p["poly"])) for p in _hold([TWO_STEPS], ctx))
    assert boxes == [(0.0, 40.0), (40.0, 80.0), (80.0, 120.0)], "no ring keeps a step (feature 328, 0014): a cut up each hop's line, x = 40 and x = 80"


def test_a_part_of_a_staircase_too_small_to_stand_is_welded_or_left_bare() -> None:
    """W23's fallback: a cut can leave a part under the area floor, and that part goes the scrap path - welded into a
    neighbor where the union keeps every rule, bare otherwise - never a staircase kept whole."""
    ctx = RingContext(cell=12000.0, g=G)  # every part of TWO_STEPS is under 0.2 of this cell
    plots = _hold([TWO_STEPS], ctx)
    assert all(not ring_violations(as_recorded(p["poly"]), ctx) for p in plots)
    assert not [p for p in plots if staircase(p["poly"], G)]


def test_a_needle_no_neighbor_can_take_is_left_bare() -> None:
    """W18: a basin tapering to a point is not kept. Its only neighbor would take it on as a spike - the union is a needle
    too - so the weld is refused and the ground stays bare under the fan floor. The neighbor is left as it was."""
    spike = [(0.0, 0.0), (100.0, -6.0), (100.0, 6.0)]
    host = _rect(100.0, -30.0, 160.0, 30.0)
    assert needle(spike)
    plots = _hold([spike, host], RingContext(cell=1500.0, g=G))
    assert [p["poly"] for p in plots] == [host], "the needle is gone and the neighbor untouched"


def test_a_needle_hidden_from_the_deduplicated_ring_is_judged_raw() -> None:
    """W18: the dedup blind spot - a 0.4 px collapsed edge hiding a raw apex under 15 deg. The rule reads the ring as
    recorded, raw, and so does the pass: the plot goes."""
    hidden = [(0.0, 0.0), (60.0, 0.0), (60.0, 40.0), (0.0, 40.0), (0.0, 0.4), (40.0, 5.0)]
    assert needle(hidden)
    plots = _hold([hidden], RingContext(cell=1500.0, g=G))
    assert all(not needle(p["poly"]) for p in plots)


def test_a_scrap_under_the_area_floor_is_welded_into_its_neighbor() -> None:
    """W21: a basin under 0.20 of the design cell is taken into the basin it shares the most bund with, when the union
    keeps every rule - here a 10 x 40 strip beside a 40 x 40 basin, which comes out a 50 x 40 basin."""
    small, big = _rect(40.0, 0.0, 50.0, 40.0), _rect(0.0, 0.0, 40.0, 40.0)
    ctx = RingContext(cell=2500.0, g=G)
    assert too_small(small, 2500.0)
    plots = _hold([small, big], ctx)
    assert len(plots) == 1 and abs(ring_area(plots[0]["poly"]) - 2000.0) < 2.0, "welded in, ground kept"
    assert not ring_violations(plots[0]["poly"], ctx)


def test_a_weld_that_would_leave_a_flight_of_steps_is_refused() -> None:
    """W21 with W23: an L-shaped weld - a small square on one end of a basin's wall - reads to the rule as two steps
    (the run, the hop and the run resumed, twice), so the scrap stays bare rather than make the host a staircase."""
    small, big = _rect(40.0, 0.0, 50.0, 10.0), _rect(0.0, 0.0, 40.0, 40.0)
    plots = _hold([small, big], RingContext(cell=1600.0, g=G))
    assert [p["poly"] for p in plots] == [big]


def test_a_scrap_is_offered_only_to_the_neighbors_it_shares_a_bund_with() -> None:
    """The weld's candidates: a near basin that shares no bund is passed over (the ranking stops there), and one within
    reach whose union with the grown scrap is still two pieces is refused, so the scrap stays bare."""
    small = _rect(40.0, 0.0, 50.0, 10.0)
    apart = _rect(50.3, 0.0, 90.0, 40.0)  # 0.3 px off: within the weld's 0.4 px reach, beyond its 0.02 px growth
    beyond = _rect(0.0, 10.8, 39.5, 50.0)  # its box is within a px of the scrap's, but no bund is shared
    plots = _hold([small, apart, beyond], RingContext(cell=1600.0, g=G))
    assert [p["poly"] for p in plots] == [apart, beyond]


def test_no_bund_is_left_down_the_middle_of_a_supply_channel() -> None:
    """W16: a ring whose bund stands inside a delivery ditch's stroke is not kept; the context is the recorded ditches."""
    ditch = {"pts": [(0.0, 50.0), (200.0, 50.0)], "w": 5.0, "role": "branch"}
    ctx = fan_context([ditch], G, 1500.0)
    inside = _rect(20.0, 51.0, 80.0, 100.0)  # its upper bund 1 px off the centerline of a 5 px ditch
    clear = _rect(100.0, 54.0, 160.0, 100.0)
    assert supply_intrusions(inside, ctx.supplies) and not supply_intrusions(clear, ctx.supplies)
    plots = _hold([inside, clear], ctx)
    assert not [p for p in plots if supply_intrusions(p["poly"], ctx.supplies)]
    assert clear in [p["poly"] for p in plots]


def test_no_bund_is_left_across_the_collector() -> None:
    """W17: a ring with an edge running across the collector (both ends within half its stroke) is not kept."""
    drain = {"pts": [(0.0, 50.0), (200.0, 50.0)], "w": 3.0, "w_tail": 6.0, "role": "drain"}
    ctx = fan_context([drain], G, 1500.0)
    across = [(20.0, 50.5), (80.0, 49.5), (80.0, 100.0), (20.0, 100.0)]
    assert collector_crossings(across, ctx.drains)
    assert not [p for p in _hold([across], ctx) if collector_crossings(p["poly"], ctx.drains)]


def test_an_arrowhead_is_left_bare_rather_than_kept() -> None:
    """W25 at the last word: a basin pointed and notched at the gate line is not kept whole."""
    arrow = [(0.0, 0.0), (100.0, -30.0), (60.0, 0.0), (100.0, 30.0)]
    assert arrowhead(arrow)
    assert not [p for p in _hold([arrow], RingContext()) if arrowhead(p["poly"])]


def test_a_hop_whose_continuations_both_leave_the_basin_is_not_cut() -> None:
    """`_cut_on_hop` on a hop lying along a convex basin's own edge: neither end's continuation enters the floor, so
    there is no line to cut on - the ring is handed back whole, and `_split_steps` keeps a ring it cannot cut."""
    from l7r.diagram.waterfields.seams.close import _cut_on_hop, _split_steps

    square = _poly(_rect(0.0, 0.0, 40.0, 40.0))
    assert _cut_on_hop(square, (0.0, 0.0), (10.0, 0.0)) == []
    assert _split_steps(square, RingContext(g=G)) == [square]


def test_a_scrap_is_welded_into_a_host_whose_union_holds_only_a_pinhole() -> None:
    """Feature 328 wave 77: `_weld_within_rules` took a host only where the union had no hole at all, so a sub-pixel hole the
    grid left (no cell fills it) refused a lawful host and the scrap stayed bare. The union is now welded first: a pinhole is
    filled and the scrap taken in; a hole a cell could fill still refuses the host."""
    from shapely.geometry import Polygon, box

    from l7r.diagram.waterfields.seams.close import _load_shapely, _weld_within_rules
    from l7r.diagram.waterfields.seams.geoms import GeomTree

    _load_shapely()  # the pass binds shapely's names on first use; this test calls the weld directly
    ctx = RingContext(cell=1500.0, g=G)
    for hole, taken in (((20.0, 10.0, 20.5, 10.5), True), ((15.0, 10.0, 25.0, 20.0), False)):
        host = box(0, 0, 48, 31).difference(box(*hole))
        plots = [{"poly": [(0.0, 0.0), (48.0, 0.0), (48.0, 31.0), (0.0, 31.0)], "fill": "#A6C398"}]
        geoms: list[Any] = [host]
        scrap = Polygon([(48.0, 0.0), (56.0, 0.0), (56.0, 31.0), (48.0, 31.0)])
        assert _weld_within_rules(scrap, plots, geoms, GeomTree(geoms), ctx) is taken
        if taken:
            assert abs(_poly(plots[0]["poly"]).area - 56.0 * 31.0) < 1.0, "the host now holds the scrap, its pinhole filled"
