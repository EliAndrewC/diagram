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
    """FR-006 / SC-001 / SC-002: the wind is the region's northwest, the seat's back faces it, every household is
    seated, and the belt's center stands within 45 degrees of northwest of the cluster's center."""
    m = _manifest(gen)
    meta = m["meta"]
    assert (meta["windward"], meta["wind_source"], meta["seat_offwind"]) == ("NW", "regional", False)
    assert len(m["houses"]) == meta["households"]
    belt = [c for g in m["village_groves"] if g["role"] == "windbreak" for c in g["clumps"]]
    assert belt, "the map has a windbreak"
    hs = m["houses"]
    cx, cy = sum(h["x"] for h in hs) / len(hs), sum(h["y"] for h in hs) / len(hs)
    bx, by = sum(c[0] for c in belt) / len(belt), sum(c[1] for c in belt) / len(belt)
    bearing = math.degrees(math.atan2(bx - cx, -(by - cy))) % 360.0  # compass: 0 = north, screen y points down
    assert abs((bearing - NW_COMPASS + 180.0) % 360.0 - 180.0) <= 45.0, f"belt center at {bearing:.0f} deg from the cluster"
    # ...AND ON ONE OR TWO SIDES, NEVER ROUND THE HOUSES (research/vegetation, 'Does a shelter belt wrap the settlement?':
    # the record's shape is a hook, and the pool's belts measured 87-168 degrees). A seed whose belt stands in the
    # middle of the cluster's north edge with houses on three sides of it read as 333 degrees and was refused.
    angs = sorted(math.degrees(math.atan2(c[0] - cx, -(c[1] - cy))) % 360.0 for c in belt)
    gap = max([b - a for a, b in zip(angs, angs[1:], strict=False)] + [angs[0] + 360.0 - angs[-1]])
    assert 360.0 - gap <= 200.0, f"the belt subtends {360.0 - gap:.0f} deg round its cluster"
