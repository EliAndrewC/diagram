"""Captions, and the one board a hamlet posts (feature 166): what is left of it after feature 287.

Feature 166 carried six rules here that the retired battery re-measured on every finished map. Feature 287 moved them
into the placers and retired their finished-map tests (specs/287-placer-guarantees/research.md R8): a caption names its
subject (`settlement/finish.py:label` refuses one with no `ref`), hugs it (`labels/placer.py:place`, `HUG_RING`) and is
turned to it (`labels/placer.py:_point_cands`), and the notice board stands by the way and faces it
(`structures/fixtures/siting.py`) - each with a unit test on the violating case.

KEPT, because no placer guarantees it yet: `captions_clear_the_ways_they_stand_on`. The board's caption is seated
strictly clear of the ways (`board_seat.py:board_caption_seat`), except at plan D12's terminal - no verge takes a board
with a clean caption, and the least-cost seat is kept, marked for the GM (`siting.py`, `meta.kosatsuba_d12`) - and a
caption on the placer's non-strict path may still cross a soft way.
"""

from __future__ import annotations

import math

import pytest

from l7r.diagram.settlement._geom import label_quad
from tests import rolls
from tests.gate import _pool

SPEC = rolls.REFERENCE  # the pool's brief (feature 215)

NOTCH_CLEARANCE = 2.0
"""How near a caption's box may come to a lane's drawn tread. Closer than this and the caption's halo
eats the path."""


def _seg_dist(px: float, py: float, a, b) -> float:
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


@pytest.fixture(scope="module")
def labels():
    """The seated captions, with the assertion that there ARE some. A map that captions nothing would
    satisfy the rule below without drawing a single label."""
    _plan, M = _pool.rolled_map(SPEC)
    L = [lab for lab in (M.get("labels") or []) if len(lab) >= 6]
    assert L, "the roll seated no caption, so every rule in this module would pass on nothing"
    return M, L


def test_no_caption_lies_across_a_way(labels) -> None:
    """`captions_clear_the_ways_they_stand_on`. A caption's box carries a halo that paints out what is
    under it, so one lying on a lane notches the lane and the reader sees a path with a bite taken out of
    it. The caption has the whole page to sit in; the lane does not."""
    M, L = labels
    assert any(len(ln.get("pts") or []) >= 2 for ln in M.get("lanes") or []), "the roll drew no lane, so this rule would judge nothing"
    notched = []
    for lab in L:
        # THE DRAWN BLOCK, turned as the reader sees it (feature 266): a tilted caption's record box is its UNROTATED
        # box, and its corners stand where no ink is - measured on them, a caption lying beside a lane at the lane's
        # own angle was reported across it. For a level caption the quad is the box, corner for corner.
        quad = label_quad(lab)
        corners = (*quad, (sum(q[0] for q in quad) / 4, sum(q[1] for q in quad) / 4))
        for ln in M.get("lanes") or []:
            pts = [(float(a), float(b)) for a, b in (ln.get("pts") or [])]
            half = float(ln.get("w") or 3) / 2.0
            if len(pts) < 2:
                continue
            if any(_seg_dist(cx, cy, pts[i], pts[i + 1]) - half < NOTCH_CLEARANCE for cx, cy in corners for i in range(len(pts) - 1)):
                notched.append((lab[5], round(quad[0][0]), round(quad[0][1])))
                break
    assert not notched, f"caption(s) lie across a lane: {notched[:4]}"
