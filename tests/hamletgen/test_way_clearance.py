"""Walking a way's start point clear of the cluster's fringe (feature 166).

WHAT THIS DOES *NOT* CARRY, recorded because I nearly filed it as covering them: this is not the
"ways clear of dry plots / marsh / the road" family. Those need a different destination and are still
owed.

`push_clear_of_fabric` tests `edge_dist(point, poly) >= gap`, which is the distance to a polygon's
BOUNDARY - and a point in the middle of a polygon is a long way from its boundary, so it passes
immediately. The function keeps a point off the FRINGE of the standing fabric; it does not keep it out of
interiors. Measured: from the centre of a 200x200 box it returns that centre unchanged at every gap.

That is correct for its actual job - walking a connector's start point out from inside a cluster until it
is not jammed against the nearest steading - and wrong for anything that needs to avoid a region.

STEPPING RATHER THAN SOLVING IS DELIBERATE. The fabric is an arbitrary polygon set, the step is cheap, and
a bounded walk cannot fail to terminate the way a solve can. The bound makes the last line a REAL branch:
a base hemmed in on all sides returns the last point tried, and the caller draws from it rather than
getting nothing.
"""

from __future__ import annotations

import math

from l7r.diagram.hamletgen.ways import push_clear_of_fabric

WALL = [(400.0, 0.0), (410.0, 0.0), (410.0, 1000.0), (400.0, 1000.0)]  # a thin standing wall to walk clear of


def _edge_dist(pt, poly):
    best = float("inf")
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        t = max(0.0, min(1.0, ((pt[0] - x1) * dx + (pt[1] - y1) * dy) / (dx * dx + dy * dy or 1.0)))
        best = min(best, math.dist(pt, (x1 + t * dx, y1 + t * dy)))
    return best


def test_a_point_jammed_against_standing_fabric_is_walked_off_it() -> None:
    """The actual guarantee: a start point hard against a steading is pushed out until it stands off by
    the gap, so the way it begins does not start inside somebody's wall."""
    got = push_clear_of_fabric((395.0, 500.0), (-1.0, 0.0), 0.0, [WALL], gap=30.0)
    assert _edge_dist(got, WALL) >= 30.0, f"walked to {got}, still {_edge_dist(got, WALL):.1f} from the wall"


def test_a_bigger_gap_walks_further() -> None:
    near = push_clear_of_fabric((395.0, 500.0), (-1.0, 0.0), 0.0, [WALL], gap=15.0)
    far = push_clear_of_fabric((395.0, 500.0), (-1.0, 0.0), 0.0, [WALL], gap=60.0)
    assert far[0] < near[0], "a bigger standoff must move the point further from the wall"
    assert _edge_dist(far, WALL) >= 60.0


def test_a_point_already_clear_is_returned_where_it_stands() -> None:
    """`edge` is a head start, and a point that already clears must not wander looking for a problem it
    does not have - a connector that drifts is a connector that meets the wrong thing."""
    got = push_clear_of_fabric((100.0, 100.0), (-1.0, 0.0), 0.0, [WALL], gap=30.0)
    assert got == (100.0, 100.0)


def test_a_base_hemmed_in_on_every_side_still_yields_a_point() -> None:
    """The bounded walk's last line, which is a real branch rather than a formality: 24 steps of 6 px is
    144 px of travel, and a base that cannot clear in that distance returns the last point tried. A solve
    would have to fail here; the walk degrades instead, and the caller draws from what it gets."""
    ring = [[(0.0, 0.0), (2000.0, 0.0), (2000.0, 2000.0), (0.0, 2000.0)]]
    got = push_clear_of_fabric((5.0, 1000.0), (-1.0, 0.0), 0.0, ring, gap=500.0)
    assert got is not None and len(got) == 2
    assert _edge_dist(got, ring[0]) < 500.0, "it genuinely could not clear - this is the degraded branch"
