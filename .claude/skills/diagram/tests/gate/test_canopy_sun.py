"""No canopy tree stands in a threshing yard's or garden bed's sun (GM 2026-10-02: "no canopy trees should be exempt").

Every recorded canopy tree - the crowns of every grove, copse, belt, wood and commons, the persimmon's among them, the scrub's
pines and the planted dikes' trees - is held out of every plot's sun ground on every shipped hamlet
(`settlement/homestead_parts/tree_shade.py`, `CANOPY_SHADE_FT`; feature 310), read through the pool's gen cache.
"""

from __future__ import annotations

import json
import os
import re

import pytest

from l7r.diagram.settlement.homestead_parts.groves import BAMBOO_CULM
from l7r.diagram.settlement.homestead_parts.tree_shade import BAMBOO_SHADE_FT, CANOPY_SHADE_FT, bamboo_shading_plots, map_bamboo, map_trees, trees_shading_plots
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


def _manifest(name: str) -> tuple[dict, str]:
    path = _pool.obtain(os.path.join(_pool.HERE, f"pool/hamlets/{name}/{name}.gen.py"))
    with open(path, encoding="utf-8") as fh:
        return json.load(fh), path


@pytest.mark.parametrize("name", HAMLETS)
def test_no_bamboo_shades_a_yard_or_a_bed(name: str) -> None:
    """Feature 315: no bamboo - a culm mark or a stand - stands in a plot's sun ground at bamboo's reach (`BAMBOO_SHADE_FT`), read
    from the record of every drawn mark and stand; and that record holds every culm mark the map draws (SC-002)."""
    M, path = _manifest(name)
    bamboo = map_bamboo(M)
    assert bamboo and M["threshing_yards"] and M["gardens"], "non-vacuity: the map draws bamboo, yards and beds"
    found = bamboo_shading_plots(M, BAMBOO_SHADE_FT)
    assert not found, f"{len(found)} bamboo in a plot's sun: {found[:3]}"
    svg_path = os.path.splitext(path)[0] + ".svg"
    if os.path.exists(svg_path):  # the record against the ink: one recorded mark per culm pair drawn in a clump (a stand's marks
        with open(svg_path, encoding="utf-8") as fh:  # are its tile's, inside a <pattern>, and the stand is recorded whole)
            ink = re.sub(r"<pattern\b.*?</pattern>", "", fh.read(), flags=re.S)
        drawn = len(re.findall(rf'<path d="M[^"]*" stroke="{BAMBOO_CULM}"', ink))
        assert drawn == len(M.get("bamboo_marks") or ()), f"{drawn} culm marks drawn, {len(M.get('bamboo_marks') or ())} recorded"
