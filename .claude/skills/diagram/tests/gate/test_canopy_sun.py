"""No canopy tree stands in a threshing yard's or garden bed's sun (GM 2026-10-02: "no canopy trees should be exempt").

Every recorded canopy tree - the crowns of every grove, copse, belt, wood and commons, the persimmon's among them, the scrub's
pines and the planted dikes' trees - is held out of every plot's sun ground on every shipped hamlet
(`settlement/homestead_parts/tree_shade.py`, `CANOPY_SHADE_FT`; feature 310), read through the pool's gen cache.
"""

from __future__ import annotations

import json
import os

import pytest

from l7r.diagram.settlement.homestead_parts.tree_shade import CANOPY_SHADE_FT, map_trees, trees_shading_plots
from tests.gate import _pool

HAMLETS = ("inashiro", "kashikawa", "kuwabata", "mizuguchi", "sawada")


@pytest.mark.parametrize("name", HAMLETS)
def test_no_canopy_tree_shades_a_yard_or_a_bed(name: str) -> None:
    """Non-vacuous first: the map records trees, yards and beds. Then no tree stands in a plot's sun ground."""
    with open(_pool.obtain(os.path.join(_pool.HERE, f"pool/hamlets/{name}/{name}.gen.py")), encoding="utf-8") as fh:
        M = json.load(fh)
    trees = map_trees(M)
    assert trees and M["threshing_yards"] and M["gardens"], "a map with nothing to test"
    found = trees_shading_plots(M, CANOPY_SHADE_FT)
    kinds = sorted({k for _p, k, _t, _c in found})
    assert not found, f"{len({t for _p, _k, t, _c in found})} of {len(trees)} trees ({', '.join(kinds)}) in a plot's sun: {found[:3]}"
