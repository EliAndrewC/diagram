"""The storehouse annex on the pool's scripted hamlets (feature 293; research/questions/0040-farm-storehouses-kura.html and 720): the houses that carry
it are the largest ones, as many as the lots' quota gives, each drawn against its own house and inside the Edo sheds' band.

These read the SHIPPED manifests: the deal is unit-tested in `settlement/test_lot.py` and the band in
`settlement/test_farm_fixtures.py`; this is what the finished maps show.
"""

from __future__ import annotations

import glob
import json
import math
import os

import pytest

from l7r.diagram.settlement.rolling.lot import KURA_SHARE

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GENS = sorted(glob.glob(os.path.join(SKILL, "pool", "hamlets", "*", "*.gen.py")))
IDS = [os.path.basename(g).removesuffix(".gen.py") for g in GENS]


def _manifest(gen: str) -> dict:
    with open(gen.removesuffix(".gen.py") + ".json", encoding="utf-8") as fh:
        return json.load(fh)


def test_the_pool_is_read() -> None:
    assert len(GENS) >= 5, "non-vacuity: the five scripted hamlets"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_the_storehouses_stand_against_the_largest_houses(gen: str) -> None:
    m = _manifest(gen)
    houses = [h for h in m["houses"] if h.get("kind") == "plain"]
    carriers = [h for h in houses if h.get("shed")]
    rest = [h for h in houses if not h.get("shed")]
    assert carriers, "non-vacuity: every scripted hamlet carries at least one"
    assert len(carriers) == math.floor(KURA_SHARE * len(houses) + 0.5), "the share, seated as a count"
    assert min(h["w"] * h["h"] for h in carriers) >= max(h["w"] * h["h"] for h in rest), "the larger houses first"
    sheds = m.get("farm_sheds") or []
    assert len(sheds) == len(carriers)
    for h in carriers:
        assert any(math.dist(s["of"], (h["x"], h["y"])) < 0.2 for s in sheds), f"the annex of the house at ({h['x']:.0f}, {h['y']:.0f}) is drawn against it"
    ppf = 1.0 / float(m["meta"]["ftpx"])
    for s in sheds:
        length, depth = max(s["w"], s["h"]) / ppf, min(s["w"], s["h"]) / ppf
        assert 18.0 - 0.1 <= length <= 27.0 + 0.1 and length / depth <= 1.8 + 0.02, f"an annex of {length:.1f} x {depth:.1f} ft runs outside the Edo sheds' band"
