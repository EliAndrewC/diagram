"""The pool's threshing yards after feature 282: every drawn yard a floor of mats within the drawing band, and racks by
the house on exactly the map that declares changeable harvest weather - one per yard, none map-south of its center.
These read the SHIPPED manifests: properties of a finished map that no single placement owns."""

from __future__ import annotations

import glob
import json
import math
import os

import pytest

from l7r.diagram.settlement.homestead_parts.yards import MAT_SQ_FT

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GENS = sorted(glob.glob(os.path.join(SKILL, "pool", "hamlets", "*", "*.gen.py")))
IDS = [os.path.basename(g).removesuffix(".gen.py") for g in GENS]


def _manifest(gen: str) -> dict:
    with open(gen.removesuffix(".gen.py") + ".json", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_every_drawn_yard_is_a_floor_of_mats_and_racks_follow_the_weather(gen: str) -> None:
    m = _manifest(gen)
    ftpx = float(m["meta"].get("ftpx", 1.0))
    yards = [y for y in m["threshing_yards"] if y.get("kind") != "forecourt"]
    if m["meta"].get("work_yards") is False:
        assert not yards, "a no-rice hamlet draws no threshing floor"
        return
    assert yards, "the map records no drawn threshing yard, so this test cannot see one go wrong"
    changeable = m["meta"].get("harvest_weather") == "changeable"
    for y in yards:
        full = y["w"] * y["h"] * ftpx * ftpx / MAT_SQ_FT
        # FR-004 as amended (2026-09-28): a yard under 400 sq ft draws as many as fit with bare ground round each, at least 4
        low = 4 if y["w"] * y["h"] * ftpx * ftpx < 400.0 else math.ceil(full / 3)
        assert low <= y["mats"] <= math.floor(2 * full / 3), f"yard at ({y['x']}, {y['y']}): {y['mats']} mats of a {full:.0f}-mat cover"
        if changeable:
            assert "rack" in y, f"yard at ({y['x']}, {y['y']}) has no rack on a changeable-weather map"
            assert all(py <= y["y"] + 1e-6 for _px, py in y["rack"]), f"yard at ({y['x']}, {y['y']}): a rack corner map-south of its center"
        else:
            assert "rack" not in y, "settled harvest weather draws no rack by the house"


def test_the_pool_exhibits_both_harvest_weathers() -> None:
    seen = {_manifest(g)["meta"].get("harvest_weather") for g in GENS}
    assert {"settled", "changeable"} <= seen, f"the pool shows only {sorted(map(str, seen))}"
