"""The lane network a rolled hamlet must produce (feature 166): what is left of it after feature 287.

Feature 166 carried six rules here that the retired battery re-measured on every finished map. Feature 287 made the web's
last pass settle the lane law (`hamletgen/ways/settle.py:settle_the_web`, repairs that only shorten, cut, re-lay an end
as a T or close a join, to a fixed point, the lane law's one predicate per rule in `law.py`) and refused every tree lane
that would break one (`Lawful`), each unit-tested on the violating case in `tests/hamletgen/ways/test_settle.py` - and
retired the finished-map tests of one network, the kink, the fold and hook, the lane end reaching something and the
doorstep's two ends, with their every-shipped-hamlet twins (specs/287-placer-guarantees/research.md R8). The last of
them, a break mid-run on the CONNECTOR (which the settle pass exempts), went in wave 5: the connector's placer decides it
(`track.connector_keeps_the_law`, and every later writer of the connector asks `law.breaks_through` too), unit-tested in
`tests/hamletgen/ways/test_track.py`, `test_web.py` and `test_joints.py`.

KEPT, because no placer guarantees it yet:
- `groves_clear_of_lanes`: only the belt's placer (`stands.py:village_grove`) keeps its trunks off the lanes' treads; the
  woodland commons, the forest and the yard's persimmon (seated before the web, which never reads it) have no guarantee.
"""

from __future__ import annotations

import math

import pytest

from tests import rolls
from tests.gate import _pool

SPEC = rolls.REFERENCE  # the pool's brief (feature 215)


def _seg_dist(px: float, py: float, a, b) -> float:
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def _min_dist(pt, poly) -> float:
    return min(_seg_dist(pt[0], pt[1], poly[i], poly[i + 1]) for i in range(len(poly) - 1))


def _ways(M):
    return [[(float(x), float(y)) for x, y in (ln.get("pts") or [])] for ln in (M.get("lanes") or [])]


@pytest.fixture(scope="module")
def lanes():
    """The drawn lanes, with the assertion that there ARE some: a hamlet with no lanes is not a hamlet."""
    _plan, M = _pool.rolled_map(SPEC)
    ways = [p for p in _ways(M) if len(p) >= 2]
    assert len(ways) >= 2, "the roll drew fewer than two lanes, so the network rules would judge nothing"
    return M, ways


def test_no_tree_is_planted_in_a_path(lanes) -> None:
    """`groves_clear_of_lanes`. You do not plant a tree in a path. Canopy OVER a way is fine and expected -
    a woodland path is a path under trees (GM 2026-08-29) - so what is measured is the TRUNK position, not
    the crown's reach. That distinction is the whole rule: an earlier form of it read the crown and would
    have forbidden the shaded lane the GM asked for.

    ON THE TREAD, NOT NEAR IT - and the difference was a made-up number for three weeks (GM 2026-09-12: *"In
    real life, I have seen many footpaths that are within four feet of a tree trunk. So why is that a problem?
    ... is that just a number that was made up in the middle of implementation without any actual basis?"* It
    was). The rule's own grounding, written when it was first made, is that "a lane/street/road is bare trodden
    earth - you do not plant trees ON it", and the original check measured exactly that: `seg_dist < half + r`,
    the corridor's OWN half-width. Feature 166 lifted the rule out of the retired battery and rewrote the
    distance as a flat 4.0 ft from the centerline, which on a 3 ft footpath demands 2.5 ft of bare ground BEYOND
    the tread - a clearance nothing in the record asks for and no placer implements, so the gate failed a map
    whose trees stood 3.1 ft off a footpath's centerline, which is to say 1.6 ft clear of the path itself.
    The width is read from the lane again. A trunk inside the tread is a tree standing in the path; a trunk
    beside it is what a path looks like."""
    M, ways = lanes
    # `tree_crowns` is one FLAT list of x, y, r, x, y, r ... - the trunk is the first two of each triple
    # and the crown's REACH is the third. Reading the third here is exactly the mistake the rule warns
    # against, and the flat packing is what makes that mistake easy, so it is named at the point of use.
    flat = [float(v) for v in (M.get("tree_crowns") or [])]
    assert len(flat) % 3 == 0, "tree_crowns is not a flat list of (x, y, r) triples - the trunk read below would be nonsense"
    trunks = [(flat[i], flat[i + 1]) for i in range(0, len(flat), 3)]
    assert trunks, "the roll drew no tree, so this rule would judge nothing"
    # the lane's own half-width, as the rule was first written - `w` is the drawn tread, defaulted as the
    # engine defaults it, and a trunk is judged against the path it would stand in rather than against a figure
    halves = [float(ln.get("w", 6)) / 2.0 for ln in (M.get("lanes") or [])]
    on_path = [(round(x), round(y)) for x, y in trunks if any(_min_dist((x, y), p) < halves[i] for i, p in enumerate(ways) if len(p) >= 2 and i < len(halves))]
    assert not on_path, f"tree trunk(s) stand ON a lane at {on_path[:4]}"
