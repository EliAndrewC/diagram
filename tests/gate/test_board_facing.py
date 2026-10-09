"""Feature 328 wave 68 (0190: a board is squared to the road it faces): an ENTRANCE board stands for the way out every departure
passes, so where it stands on its approach - the connector, the track out - it is squared to that track, whatever access lane
runs nearer (batch 5's glyph check: Inashiro's board stood 43.5 degrees off its connector, turned to a nearer lane)."""

from __future__ import annotations

import json
import math
import os

import pytest

from l7r.diagram.settlement._geom import seg_dist
from l7r.diagram.settlement.structures.fixtures.board_seat import FACING_DEG, KOSATSUBA_WAY_REACH_FT, off_parallel
from tests.gate import _pool

HAMLETS = ("inashiro", "kashikawa", "kuwabata", "mizuguchi", "sawada")


@pytest.mark.parametrize("name", HAMLETS)
def test_an_entrance_board_on_its_approach_is_squared_to_it(name: str) -> None:
    """States what it found first: the placement, and whether the board stands on the track out; then judges only an entrance
    board within the siting band of its connector."""
    with open(_pool.obtain(os.path.join(_pool.HERE, f"pool/hamlets/{name}/{name}.gen.py")), encoding="utf-8") as fh:
        M = json.load(fh)
    board = (M.get("kosatsuba") or [None])[0]
    assert board is not None, "every hamlet carries a board (0190)"
    track = [ln for ln in M.get("lanes") or [] if ln.get("connector")]
    if M["meta"].get("kosatsuba_seat") != "entrance" or not track:
        pytest.skip(f"{name}: board placed '{M['meta'].get('kosatsuba_seat')}', not at an entrance")
    pts = track[0]["pts"]
    a, b = min(zip(pts, pts[1:], strict=False), key=lambda s: seg_dist(board["x"], board["y"], s[0], s[1]))
    near = seg_dist(board["x"], board["y"], a, b) * float(M["meta"].get("ftpx") or 1.0)  # in feet, at the map's scale
    if near > KOSATSUBA_WAY_REACH_FT:
        pytest.skip(f"{name}: the entrance board stands {near:.0f} ft off the track out, not on it")
    off = off_parallel(float(board["rot"]), math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))
    assert off <= FACING_DEG, f"{name}: the entrance board stands {near:.0f} ft off its track out and {off:.1f} degrees off square to it"
