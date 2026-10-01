"""The farmstead grove's rules on the pool's grove maps (feature 291, plan D7).

Every farm of a dispersed or linear map carries its own grove on the sides its settlement rolled, and the rules that
grove keeps are pure functions of the finished manifest (`settlement/homestead_parts/grove_rules.py`). The cohort audit
runs them on every roll; this runs them on the shipped maps whose farms carry a grove - Mizuguchi and Kashikawa, both
linear - read through the pool's gen cache like every other gate reader of a shipped generator (`_pool.obtain`).
"""

from __future__ import annotations

import json
import os

import pytest

from l7r.diagram.settlement.homestead_parts.grove_rules import (
    fixtures_on_groves,
    gardens_east_shaded,
    grove_farms,
    grove_sides_missing,
    groves_crossed_by_lanes,
    groves_off_windward,
)
from tests.gate import _pool

GROVE_MAPS = ("pool/hamlets/mizuguchi/mizuguchi.gen.py", "pool/hamlets/kashikawa/kashikawa.gen.py")


@pytest.fixture(scope="module", params=GROVE_MAPS, ids=lambda g: os.path.basename(g).split(".")[0])
def grove_map(request: pytest.FixtureRequest) -> dict:
    with open(_pool.obtain(os.path.join(_pool.HERE, request.param)), encoding="utf-8") as fh:
        return json.load(fh)


def test_every_grove_rule_holds_on_the_pool_s_grove_maps(grove_map: dict) -> None:
    """Non-vacuous first: the map carries farms with their own grove, one per household. Then every farm is planted on
    every face its settlement rolled, the deep stand on the windward faces, no garden's morning sun cut off, no lane
    across a band and no fixture inside one."""
    farms = grove_farms(grove_map)
    assert farms and len(farms) == len(grove_map["houses"]), f"{len(farms)} grove farms of {len(grove_map['houses'])} houses"
    for name, found in (
        ("grove_sides_missing", grove_sides_missing(grove_map)),
        ("groves_off_windward", groves_off_windward(grove_map)),
        ("gardens_east_shaded", gardens_east_shaded(grove_map)),
        ("groves_crossed_by_lanes", groves_crossed_by_lanes(grove_map)),
        ("fixtures_on_groves", fixtures_on_groves(grove_map)),
    ):
        assert not found, f"{name}: {found[:2]}"
