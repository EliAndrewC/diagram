"""The pool's hamlets take the regional northwest wind, and their windbreaks stand on it (feature 261).

The GM, looking at Kashikawa's belt on the south and east: *"which I thought was supposed to be to the north and
west because of the direction of the winds for the geographic region ... Is this just a bug in the map
generator?"* - and, on the fix: *"none of our maps should have this declared at the present time. So it should be
fixed everywhere for now."* So every scripted hamlet in the pool declares no wind, records the northwest as the
region's, seats its cluster with its back to it, and has its belt on the cluster's northwest side.

These read the SHIPPED manifests: a property of a finished map that no single placement owns.
"""

from __future__ import annotations

import glob
import json
import math
import os
import re

import pytest

from l7r.diagram.settlement.homestead_parts.belt_law import DEPTH_BIN_FT, belt_depths

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GENS = sorted(glob.glob(os.path.join(SKILL, "pool", "hamlets", "*", "*.gen.py")))
NW_COMPASS = 315.0


def _manifest(gen: str) -> dict:
    with open(gen.removesuffix(".gen.py") + ".json", encoding="utf-8") as fh:
        return json.load(fh)


def test_the_pool_has_scripted_hamlets_to_judge() -> None:
    assert len(GENS) >= 5, "non-vacuity: the five scripted hamlets"


@pytest.mark.parametrize("gen", GENS, ids=lambda g: os.path.basename(g).removesuffix(".gen.py"))
def test_no_pool_hamlet_declares_a_wind(gen: str) -> None:
    """FR-005: a local wind is a declaration, and the GM ruled that no map carries one at present."""
    with open(gen, encoding="utf-8") as fh:
        src = fh.read()
    assert "HamletSpec(" in src
    assert not re.search(r"\bwindward\s*=", src), f"{os.path.basename(gen)} declares a wind"


@pytest.mark.parametrize("gen", GENS, ids=lambda g: os.path.basename(g).removesuffix(".gen.py"))
def test_every_pool_hamlet_has_its_belt_on_the_regional_northwest(gen: str) -> None:
    """FR-006 / SC-001 / SC-002: the wind is the region's northwest, and the belt's center stands within 45 degrees of
    northwest of the cluster's center, on one or two sides of it. The seat's back to the wind and every household seated
    were retired by feature 287 (`hamletgen/cluster.py:seat_cluster` refuses an off-wind seat, `SeatRefused`;
    `homesteads/stages.py` seats every household or refuses the site) - the bearing is KEPT: `stands.py:trim_to_the_wind`
    converges on the crown nearest the wind, even one still off it, and refuses nothing."""
    m = _manifest(gen)
    meta = m["meta"]
    assert (meta["windward"], meta["wind_source"]) == ("NW", "regional")
    belt = [c for g in m["village_groves"] if g["role"] == "windbreak" for c in g["clumps"]]
    assert belt, "the map has a windbreak"
    hs = m["houses"]
    cx, cy = sum(h["x"] for h in hs) / len(hs), sum(h["y"] for h in hs) / len(hs)
    bx, by = sum(c[0] for c in belt) / len(belt), sum(c[1] for c in belt) / len(belt)
    bearing = math.degrees(math.atan2(bx - cx, -(by - cy))) % 360.0  # compass: 0 = north, screen y points down
    assert abs((bearing - NW_COMPASS + 180.0) % 360.0 - 180.0) <= 45.0, f"belt center at {bearing:.0f} deg from the cluster"
    # ...AND ON ONE OR TWO SIDES, NEVER ROUND THE HOUSES (research/vegetation, 'Does a shelter belt wrap the settlement?':
    # the record's shape is a hook, and the pool's belts measured 88-169 degrees). A seed whose belt stands in the
    # middle of the cluster's north edge with houses on three sides of it read as 333 degrees and was refused.
    angs = sorted(math.degrees(math.atan2(c[0] - cx, -(c[1] - cy))) % 360.0 for c in belt)
    gap = max([b - a for a, b in zip(angs, angs[1:], strict=False)] + [angs[0] + 360.0 - angs[-1]])
    assert 360.0 - gap <= 200.0, f"the belt subtends {360.0 - gap:.0f} deg round its cluster"


BELT_DESIGN_DEPTH_FT = 110.0  # the band `belt_polygon` draws, 36..146 px behind the fringe at 1 ft per px

# THE ONE PREDICATE (feature 287, woods W16): the depth measure this file used to carry is the engine's now, and the placer
# that plants the belt (`settle_the_belt`) asks the same one - lifted unchanged but for W19's run break (an empty stretch no
# house stands before) and an opening a way crosses face to face (`BeltReading._crossed`), which W17 judges.


@pytest.mark.parametrize("gen", GENS, ids=lambda g: os.path.basename(g).removesuffix(".gen.py"))
def test_every_pool_belt_keeps_its_depth_across_its_windward_face(gen: str) -> None:
    """FR-016 / SC-012: no stretch of the belt is thinner than the record's minimum - a settlement-review found
    Kashikawa's windward arm a single row of trees, 12-21 ft deep, while the mass stood elsewhere.

    ITS LIMIT, measured: it judges the bins the frame leaves whole. That arm (seed 8, commit 0d44e65c) stood within about
    100 ft of its view's top-left corner, where the belt's windward depth runs off the page, so this measure reads those
    bins as frame-cut and passes that manifest - the frame, not the planting, is what it cannot see past. A belt the frame
    holds whole is asserted to stand against the page's edge instead.

    FEATURE 287 RETIRED THE JUDGED HALF: `belt_law.py:settle_the_belt` deepens a thin stretch or ends the belt where no
    seat is admitted, judged on the page `frame_for` decides (`tests/settlement/test_belt_law.py`). The frame-held half is
    KEPT: no placer decides that a belt no bin judges stands against the page's edge."""
    m = _manifest(gen)
    depths = belt_depths(m)
    judged = [d for d in depths if d is not None]
    assert len(depths) >= 5, "non-vacuity: the belt spans several bins"
    if judged:
        pytest.skip("the belt's judged depth is `settle_the_belt`'s guarantee (feature 287)")
    else:
        # A BELT THE FRAME HOLDS WHOLE: every bin is cut by the page's edge, parted by a way or the brook, or a tip. That is
        # only honest when the belt really does stand against the page - every crown within its designed depth of the edge.
        # STANDING AGAINST THE PAGE is judged per stretch: across every 40 ft bin, the belt's crown NEAREST the edge stands
        # within its designed depth of it. The first form asked it of EVERY crown, which fails a belt that meets the page
        # and is deeper than designed - Kuwabata's and Mizuguchi's at the 269 landing, their inmost crowns 116-163 ft in
        # (2026-09-28) - while a thin belt standing off the page still fails, its nearest crown in some bin far from the edge.
        x0, y0, w, h = (float(c) for c in m["meta"]["view"])
        crowns = next(g for g in m["village_groves"] if g["role"] == "windbreak")["clumps"]
        q = {"NW": (-1.0, -1.0), "N": (0.0, -1.0), "W": (-1.0, 0.0)}[m["meta"]["windward"]]
        ax, ay = q[1] / math.hypot(*q), -q[0] / math.hypot(*q)  # across the wind, as `belt_depths` bins it
        near: dict[int, float] = {}
        for x, y in crowns:
            b = int((x * ax + y * ay) // DEPTH_BIN_FT)
            near[b] = min(near.get(b, math.inf), min(x - x0, y - y0, x0 + w - x, y0 + h - y))
        assert all(d <= BELT_DESIGN_DEPTH_FT for d in near.values()), f"no bin judged, yet the belt stands off the page's edge: {near}"
