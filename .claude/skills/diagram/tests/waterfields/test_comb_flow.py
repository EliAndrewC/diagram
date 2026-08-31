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

import functools
import math

import pytest

from l7r.diagram.pipeline import rollcache
from l7r.diagram.waterfields.comb import build_comb

FALLS = (0.0, 45.0, 90.0, 180.0)
"""The falls this module asserts over. FOUR, NOT SIX, and the count is a cost decision with a stated
reason (2026-08-30): a comb build is ~1 s, and at six falls x three tests this file alone was 18 builds
and the single largest test cost in the repository. What the rotation argument actually needs is an
axis-aligned fall, an oblique one, and a reversed one - 0 / 45 / 90 / 180 give all three. Dropping 135 and
270 removes a second oblique and a second axis, neither of which tests anything the first does not."""


@functools.cache
def _net(down_deg: float, seed: int = 5):  # noqa: D401
    """One comb per (fall, seed), shared by every test that reads it.

    CACHED BECAUSE A BUILD IS THE WHOLE COST HERE. Three tests examine the SAME drain at each fall, and
    each was building its own - so two of every three builds were re-deriving a net an assertion had
    already produced. **Nothing here may mutate the returned net**: it is shared, so a test that edited it
    would corrupt its neighbors rather than fail. Every reader below only measures."""
    # SHARED ACROSS WORKERS, not just within one (2026-08-30). `lru_cache` alone only helps when two
    # tests reading the same net land on the SAME xdist worker, and with `--dist worksteal` they usually
    # do not - so each of the eight processes was rebuilding its own copy. `rollcache.obtain` keys on the
    # engine as well as these parameters, so the build is paid once per (fall, seed) per code change.
    return rollcache.obtain(f"comb-flow:{down_deg}:{seed}", lambda: build_comb(2400, 2400, (300.0, 300.0), seed=seed, down_deg=down_deg))[0]


def _drain_bearing(down_deg: float, seed: int = 5) -> tuple[float, float]:
    net = _net(down_deg, seed)
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
    # ...and the drain must BE a real run, or the bearing above is satisfied vacuously by a stub.
    pts = [tuple(p) for p in _net(down_deg)["drain"]]
    span = sum(math.dist(a, b) for a, b in zip(pts, pts[1:], strict=False))
    assert span > 200.0, f"down_deg {down_deg:.0f}: the drain is only {span:.0f} px long"


def test_the_collector_turns_with_the_map() -> None:
    """The rotation half. A drain that kept one bearing whatever the fall would satisfy the cross-slope
    rule at some orientations by luck and violate it at others - and a generator that only rolled one
    fall would never show it."""
    bearings = {dd: _drain_bearing(dd)[0] for dd in FALLS}
    assert len({round(b) for b in bearings.values()}) > 1, f"the drain kept one bearing at every fall: {bearings}"


# The non-vacuity check that used to be its own parametrized test is folded into the cross-slope test
# above: it asserted a property of the SAME drain at the SAME fall, so as a separate test it doubled the
# builds to re-derive a net the bearing test had already made. Merging it costs no coverage - both
# assertions still run at every fall, and a failure still names which one - and halves this file's cost.
