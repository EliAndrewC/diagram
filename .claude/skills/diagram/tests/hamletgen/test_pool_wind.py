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
    # the record's shape is a hook, and the pool's belts measured 88-169 degrees). A seed whose belt stands in the
    # middle of the cluster's north edge with houses on three sides of it read as 333 degrees and was refused.
    angs = sorted(math.degrees(math.atan2(c[0] - cx, -(c[1] - cy))) % 360.0 for c in belt)
    gap = max([b - a for a, b in zip(angs, angs[1:], strict=False)] + [angs[0] + 360.0 - angs[-1]])
    assert 360.0 - gap <= 200.0, f"the belt subtends {360.0 - gap:.0f} deg round its cluster"


MIN_BELT_DEPTH_FT = 30.0  # research/vegetation/020: a belt 'shallower than about 30 ft reads as a row of blobs'
DEPTH_BIN_FT = 40.0


def _way_samples(m: dict) -> list[tuple[float, float]]:
    """Points every 10 ft along each lane and the brook - a way or the water through the belt parts it, and that
    gap is not a thin stretch."""
    out: list[tuple[float, float]] = []
    for rec in [*m.get("lanes", []), *m.get("streams", [])]:
        pts = rec.get("pts") or rec.get("poly") or []
        for (ax, ay), (bx, by) in zip(pts, pts[1:], strict=False):
            n = max(1, int(math.hypot(bx - ax, by - ay) // 10))
            out += [(ax + (bx - ax) * i / n, ay + (by - ay) * i / n) for i in range(n + 1)]
    return out


def belt_depths(m: dict) -> list[float | None]:
    """The belt's depth ALONG the wind, per 40 ft bin ACROSS it: the longest run of touching crowns (1 px = 1 ft on a
    hamlet). A bin a way or the brook runs THROUGH, or the page's edge cuts, reads None."""
    q = {"NW": (-1.0, -1.0), "N": (0.0, -1.0), "W": (-1.0, 0.0)}[m["meta"]["windward"]]
    wx, wy = q[0] / math.hypot(*q), q[1] / math.hypot(*q)
    px, py = -wy, wx
    hs = m["houses"]
    cx, cy = sum(h["x"] for h in hs) / len(hs), sum(h["y"] for h in hs) / len(hs)
    g = next(g for g in m["village_groves"] if g["role"] == "windbreak")
    r = g.get("r", 14.0)
    on = g["clumps"]
    cl = [((x - cx) * wx + (y - cy) * wy, (x - cx) * px + (y - cy) * py) for x, y in on + g.get("clumps_offpage", [])]
    lo = min(v for _u, v in cl)
    bins: dict[int, list[float]] = {}
    for u, v in cl:
        bins.setdefault(int((v - lo) // DEPTH_BIN_FT), []).append(u)
    # A BIN THE PAGE'S EDGE CUTS IS NOT JUDGED: the frame, not the belt, is what is thin there (Inashiro's belt runs off
    # the top of its view, and the canvas squeezes the part a reader never sees).
    framed = {int((v - lo) // DEPTH_BIN_FT) for _u, v in cl[len(on) :]}

    def through(b: int, u: float) -> bool:
        """Inside the belt's thickness there - between the near and far crowns of this bin and its neighbors, a
        crown's radius in from each face. A lane along the belt's inner face is not a way through it."""
        us = [w for k in (b - 1, b, b + 1) for w in bins.get(k, [])]
        return bool(us) and min(us) + r < u < max(us) - r

    parted = set()
    for x, y in _way_samples(m):
        b = int((((x - cx) * px + (y - cy) * py) - lo) // DEPTH_BIN_FT)
        if through(b, (x - cx) * wx + (y - cy) * wy):
            parted.add(b)
    out: list[float | None] = []
    for b in range(max(bins) + 1):
        us = sorted(bins.get(b, []))
        if b in parted or b in framed:
            out.append(None)
            continue
        best = cur = 2 * r if us else 0.0
        for a, c in zip(us, us[1:], strict=False):
            cur = cur + (c - a) if c - a <= 2.2 * r else 2 * r
            best = max(best, cur)
        out.append(best)
    return out


@pytest.mark.parametrize("gen", GENS, ids=lambda g: os.path.basename(g).removesuffix(".gen.py"))
def test_every_pool_belt_keeps_its_depth_across_its_windward_face(gen: str) -> None:
    """FR-016 / SC-012: no stretch of the belt is thinner than the record's minimum - a settlement-review found
    Kashikawa's windward arm a single row of trees, 12-21 ft deep, while the mass stood elsewhere."""
    depths = belt_depths(_manifest(gen))
    judged = [d for d in depths if d is not None]
    assert len(judged) >= 5, "non-vacuity: the belt spans several bins"
    assert min(judged) >= MIN_BELT_DEPTH_FT, f"belt depths per {DEPTH_BIN_FT:.0f} ft: {depths}"


def test_belt_depths_reads_a_thin_stretch_and_a_parted_one() -> None:
    """The measure itself: a two-row block reads its depth, a lone crown reads one crown, and a lane through a bin
    leaves that bin unjudged, while one along the belt's inner face does not; nor is a bin the page's edge cuts."""
    m = {
        "meta": {"windward": "N"},
        "houses": [{"x": 0.0, "y": 0.0}],
        "village_groves": [{"role": "windbreak", "r": 10.0, "clumps": [[5.0, -100.0], [5.0, -120.0], [45.0, -100.0], [85.0, -100.0], [85.0, -140.0]], "clumps_offpage": [[125.0, -100.0]]}],
        "lanes": [{"pts": [[85.0, 0.0], [85.0, -200.0]]}, {"pts": [[0.0, -80.0], [90.0, -80.0]]}],
    }
    assert belt_depths(m) == [40.0, 20.0, None, None]
