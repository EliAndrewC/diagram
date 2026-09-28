"""The pool's threshing yards after feature 282: every drawn yard a floor of mats within the drawing band, and racks by
the house on exactly the map that declares changeable harvest weather - one per yard, none map-south of its center.
These read the SHIPPED manifests: properties of a finished map that no single placement owns."""

from __future__ import annotations

import glob
import json
import math
import os

import numpy as np
import pytest

from l7r.diagram.settlement.homestead_parts.yards import MAT_SQ_FT

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GENS = sorted(glob.glob(os.path.join(SKILL, "pool", "hamlets", "*", "*.gen.py")))
IDS = [os.path.basename(g).removesuffix(".gen.py") for g in GENS]


def _fine_fit(y: dict, ftpx: float, step: float = 0.02, clear: float = 1.0) -> int:
    """The most unturned 6 x 3 ft mats any lattice at a 1 ft gap seats in yard `y`, searched over every origin on a `step`
    grid: a mask of the grid points `clear` inside the yard's convex outline (from its edges' half-planes), then each
    lattice spot's fit as four shifted views of it, each lattice's count as a sum of shifted views of those."""
    th = math.radians(y["rot"])

    def local(px: float, py: float) -> tuple[float, float]:
        return ((px - y["x"]) * math.cos(th) + (py - y["y"]) * math.sin(th), -(px - y["x"]) * math.sin(th) + (py - y["y"]) * math.cos(th))

    poly = [local(px, py) for px, py in y["poly"]]
    w, h = y["w"] / ftpx, y["h"] / ftpx
    gx = -w / 2 + step / 2 + np.arange(int(w / step) + 1) * step
    gy = -h / 2 + step / 2 + np.arange(int(h / step) + 1) * step
    X, Y = np.meshgrid(gx, gy, indexing="ij")
    area = sum(poly[i][0] * poly[(i + 1) % 4][1] - poly[(i + 1) % 4][0] * poly[i][1] for i in range(4))
    inside = np.ones(X.shape, bool)
    for i in range(4):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % 4]
        ln = math.hypot(bx - ax, by - ay)
        nx, ny = math.copysign(1, area) * (by - ay) / ln, -math.copysign(1, area) * (bx - ax) / ln
        inside &= nx * X + ny * Y <= nx * ax + ny * ay - clear
    cw, ch, pw, ph = round(6 / step), round(3 / step), round(7 / step), round(4 / step)
    fit = inside[:-cw, :-ch] & inside[cw:, :-ch] & inside[:-cw, ch:] & inside[cw:, ch:]
    if "rack" in y:
        rl = [local(px, py) for px, py in y["rack"]]
        k0, k1, k2, k3 = min(p[0] for p in rl) - 0.25, min(p[1] for p in rl) - 0.25, max(p[0] for p in rl) + 0.25, max(p[1] for p in rl) + 0.25
        ox, oy = np.meshgrid(gx[: fit.shape[0]], gy[: fit.shape[1]], indexing="ij")
        fit &= ~((ox < k2) & (ox + 6 > k0) & (oy < k3) & (oy + 3 > k1))
    best = 0
    for nc in range(1, fit.shape[0] // pw + 2):
        for nr in range(1, fit.shape[1] // ph + 2):
            sx, sy = fit.shape[0] - (nc - 1) * pw, fit.shape[1] - (nr - 1) * ph
            if sx <= 0 or sy <= 0:
                continue
            count = sum(fit[c * pw : c * pw + sx, r * ph : r * ph + sy].astype(int) for c in range(nc) for r in range(nr))
            best = max(best, int(np.max(count)))
    return best


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
        # FR-004 as amended (2026-09-28): a third where the yard holds one at a 1 ft gap, else as many as fit there, never
        # under 4 (the rule itself is pinned on plain inputs in tests/settlement/test_yard_mats_282.py; the manifest's outline
        # is rounded to 0.1 px, too coarse to re-derive the count against a 1 ft edge clearance)
        assert 4 <= y["mats"] <= math.floor(2 * full / 3), f"yard at ({y['x']}, {y['y']}): {y['mats']} mats of a {full:.0f}-mat cover"
        if y["mats"] < math.ceil(full / 3):
            # SHORT OF A THIRD ONLY WHERE NO 1 FT LATTICE SEATS MORE (spec 282 SC-001): an oracle that shares no grid with the
            # layout - every lattice origin on a 0.02 ft grid anchored 0.01 ft off the layout's, on this yard's own outline
            # (recorded to a thousandth of a px) and rack
            assert y["mats"] >= min(math.ceil(full / 3), _fine_fit(y, ftpx)), f"yard at ({y['x']}, {y['y']}): a 1 ft lattice seats more than the {y['mats']} drawn"
        if changeable:
            assert "rack" in y, f"yard at ({y['x']}, {y['y']}) has no rack on a changeable-weather map"
            assert all(py <= y["y"] + 1e-6 for _px, py in y["rack"]), f"yard at ({y['x']}, {y['y']}): a rack corner map-south of its center"
        else:
            assert "rack" not in y, "settled harvest weather draws no rack by the house"


def test_the_pool_exhibits_both_harvest_weathers() -> None:
    seen = {_manifest(g)["meta"].get("harvest_weather") for g in GENS}
    assert {"settled", "changeable"} <= seen, f"the pool shows only {sorted(map(str, seen))}"


def test_the_oracle_sees_the_yard_the_quarter_foot_search_left_short() -> None:
    # round 8's layout drew Sawada's 31 x 22 ft yard 12 mats and its 20 x 14 ft yard 5, each a mat under a third that a
    # lattice in a window narrower than a quarter foot seats (spec-fidelity, amendment round 7); the oracle must find those
    m = _manifest(next(g for g in GENS if g.endswith("sawada.gen.py")))
    ftpx = float(m["meta"].get("ftpx", 1.0))
    seen = {(round(y["w"]), round(y["h"])): y for y in m["threshing_yards"] if y.get("kind") != "forecourt"}
    for size, old in (((31, 22), 12), ((20, 14), 5)):
        y = seen[size]
        third = math.ceil(y["w"] * y["h"] * ftpx * ftpx / MAT_SQ_FT / 3)
        assert old < min(third, _fine_fit(y, ftpx)), f"the oracle cannot see the {size} yard's old count of {old}"
