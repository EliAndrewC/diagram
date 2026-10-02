"""The yard persimmon keeps out of every threshing yard's and garden bed's sun (GM 2026-10-02).

Every other tree on a scripted map is held out of a plot's sun ground; the persimmon was seated at the work yard's edge
with its crown free over the yard and the beds. This holds it to the same rule on every shipped hamlet
(`settlement/homestead_parts/tree_shade.py`, `PERSIMMON_SHADE_FT`), read through the pool's gen cache.
"""

from __future__ import annotations

import json
import os

import pytest

from l7r.diagram.settlement.farm_fixtures import PERSIMMON_SHADE_FT
from l7r.diagram.settlement.homestead_parts.tree_shade import persimmons_shading_plots
from tests.gate import _pool

HAMLETS = ("inashiro", "kashikawa", "kuwabata", "mizuguchi", "sawada")


@pytest.mark.parametrize("name", HAMLETS)
def test_no_persimmon_shades_a_yard_or_a_bed(name: str) -> None:
    """Non-vacuous first: the map draws persimmons, yards and beds. Then no crown stands in a plot's sun ground."""
    with open(_pool.obtain(os.path.join(_pool.HERE, f"pool/hamlets/{name}/{name}.gen.py")), encoding="utf-8") as fh:
        M = json.load(fh)
    assert M["persimmons"] and M["threshing_yards"] and M["gardens"], "a map with nothing to test"
    found = persimmons_shading_plots(M, PERSIMMON_SHADE_FT)
    assert not found, f"{len({t for _k, t, _p in found})} of {len(M['persimmons'])} persimmons' crowns in a plot's sun: {found[:3]}"
