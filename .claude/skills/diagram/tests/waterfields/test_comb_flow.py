"""Which way the comb's water runs (feature 166).

Carries `drain_runs_cross_slope`, which the retired battery re-measured on every finished map.

THE GROUNDING: a paddy field is drained by a collector ditch along its LOW EDGE, and a collector runs
ACROSS the slope, not down it. Water reaches the collector by falling into it from the plots either side;
a collector running downhill would race the water past the plots it is meant to take from, and would cut
rather than collect.

ROTATION IS THE HALF THAT ROTS QUIETLY. The toe is a contour band perpendicular to the fall, so it must
turn with `down_deg` like every other feature - and a rule asserted at ONE orientation passes forever on a
map generator that only ever rolls that one. `dev/gate.md` collects a whole family of defects that were
correct measurements taken in the page's frame instead of the feature's, so the cross-slope rule is
asserted at several falls rather than at the default.
"""

from __future__ import annotations

import math

import pytest

from l7r.diagram.waterfields.comb import build_comb

FALLS = (0.0, 45.0, 90.0, 135.0, 180.0, 270.0)


def _drain_bearing(down_deg: float, seed: int = 5) -> tuple[float, float]:
    net = build_comb(2400, 2400, (300.0, 300.0), seed=seed, down_deg=down_deg)
    pts = [tuple(p) for p in net["drain"]]
    assert len(pts) >= 2, f"down_deg {down_deg}: the comb laid no drain to measure"
    a, b = pts[0], pts[-1]
    bearing = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180.0
    fall = down_deg % 180.0
    off = abs(bearing - fall)
    return bearing, min(off, 180.0 - off)


@pytest.mark.parametrize("down_deg", FALLS)
def test_the_collector_runs_across_the_slope_not_down_it(down_deg: float) -> None:
    """`drain_runs_cross_slope`. A collector that ran downhill would race the water past the plots it is
    meant to take from. The bar is deliberately generous - what is forbidden is a drain running WITH the
    fall, not one a few degrees off perpendicular."""
    _bearing, off_fall = _drain_bearing(down_deg)
    assert off_fall > 45.0, f"down_deg {down_deg:.0f}: the drain runs {off_fall:.0f} deg from the fall - that is downhill, not across"


def test_the_collector_turns_with_the_map() -> None:
    """The rotation half. A drain that kept one bearing whatever the fall would satisfy the cross-slope
    rule at some orientations by luck and violate it at others - and a generator that only rolled one
    fall would never show it."""
    bearings = {dd: _drain_bearing(dd)[0] for dd in FALLS}
    assert len({round(b) for b in bearings.values()}) > 1, f"the drain kept one bearing at every fall: {bearings}"


@pytest.mark.parametrize("down_deg", FALLS)
def test_the_drain_is_a_real_run_at_every_fall(down_deg: float) -> None:
    """A collector reduced to a stub at some orientation drains nothing, and would satisfy a bearing test
    vacuously - the drain has to BE there before which way it runs can matter."""
    net = build_comb(2400, 2400, (300.0, 300.0), seed=5, down_deg=down_deg)
    pts = [tuple(p) for p in net["drain"]]
    span = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    assert span > 200.0, f"down_deg {down_deg:.0f}: the drain is only {span:.0f} px long"
