"""Feature 387 T05 (plan D5): the bamboo strip check asks an index of what stands near the strip (`StripNear`) instead of walking
every placed box, house, fixture, lane segment and crown - and gives the straight scan's verdict for every strip. The oracle is
`_scan_blocked`, `_strip_blocked` as it was before feature 387, kept here and nowhere in the engine."""

from __future__ import annotations

import random

from collections.abc import Sequence
from typing import Any

from l7r.diagram.hamletgen.consts import Poly
from l7r.diagram.hamletgen.homesteads.bamboo import Footing, StripNear, _strip_blocked
from l7r.diagram.settlement import Settlement, seg_dist, segments_cross
from l7r.diagram.settlement._geom import boxed_ring_hit
from l7r.diagram.settlement.rolling.bearing import turned_box


def _scan_blocked(
    s: Settlement,
    cx: float,
    cy: float,
    cw: float,
    ch: float,
    hx: float,
    hy: float,
    fields: Sequence[Poly],
    marsh: Sequence[Poly],
    pond: Any,
    lanes: Sequence[tuple[Poly, float]],
    footing: Footing | None = None,
    skip: frozenset[tuple[float, float, float, float]] = frozenset(),
) -> bool:
    if cx - cw / 2 < 30 or cy - ch / 2 < 30 or cx + cw / 2 > s.W - 30 or cy + ch / 2 > s.H - 30:
        return True
    ft = footing or Footing(s, fields, marsh)  # a caller that tests many seats builds one and passes it (feature 218)
    corners = [(cx - cw / 2, cy - ch / 2), (cx + cw / 2, cy - ch / 2), (cx + cw / 2, cy + ch / 2), (cx - cw / 2, cy + ch / 2), (cx, cy)]
    for px_, py_, pw, ph, *_ in s.placed:
        if (px_ == hx and py_ == hy) or (px_, py_, pw, ph) in skip:
            continue
        if abs(cx - px_) < (cw + pw) / 2 + 2 and abs(cy - py_) < (ch + ph) / 2 + 2:
            return True
    # EVERY OTHER FARMHOUSE, as drawn: a caller that passes the bundle boxes in `skip` excuses a neighbor's bundle, and on a
    # map whose houses carry no separate placed box that excused the neighbor's house as well - Kuwabata's woodpile landed
    # on the next house's gable once the 269 landing's bearing fix moved the row (the retired finished-map overlap test; since
    # feature 287 M8 the registry of what stands refuses it at record time, `overlap/registry.py`).
    for o in s.M.get("houses", []):
        ox, oy = float(o["x"]), float(o["y"])
        if abs(ox - hx) < 0.5 and abs(oy - hy) < 0.5:
            continue
        _, _, ow, oh = turned_box((ox, oy, float(o["w"]), float(o["h"])), float(o.get("rot", 0.0)))
        if abs(cx - ox) < (cw + ow) / 2 + 2 and abs(cy - oy) < (ch + oh) / 2 + 2:
            return True
    for key in ("wells", "kosatsuba", "byres", "farm_sheds", "retirement_houses"):  # everything seated between the sheds and this pass (T49)
        for o in s.M.get(key, []):
            ow, oh = float(o.get("w", 2 * float(o.get("r", 8)))), float(o.get("h", 2 * float(o.get("r", 8))))
            if abs(cx - float(o["x"])) < (cw + ow) / 2 + 6 and abs(cy - float(o["y"])) < (ch + oh) / 2 + 6:
                return True
    if any(boxed_ring_hit(q[0], q[1], ft.rings.near(q[0], q[1]), 6.0) for q in corners):  # a paddy or the marsh, inside or within 6 ft of an edge
        return True
    # A LANE THROUGH THE STRIP, not only past its corners (feature 137, cohort seed 03): five sample
    # points on a 22 by 16 ft strip let a lane cross it diagonally between them, and
    # `lanes_clear_of_bamboo` walks the tread's quarter-points. So the tread is also tested as a
    # segment against the strip's edges - a crossing, or an end inside, is a stand on a lane.
    _edges = [(corners[k], corners[(k + 1) % 4]) for k in range(4)]
    for pts, half in lanes:
        for k in range(len(pts) - 1):
            a, b = pts[k], pts[k + 1]
            if any(seg_dist(q[0], q[1], a, b) < half for q in corners):
                return True
            if any(segments_cross(a, b, e0, e1) for e0, e1 in _edges) or any(abs(p[0] - cx) < cw / 2 and abs(p[1] - cy) < ch / 2 for p in (a, b)):
                return True
    # the dry hem's plots and the watercourses (unlock tripwire seed 47: a fixture on a dry plot and one
    # on the stream - neither is a paddy, a lane or the pond, so nothing above saw them), and any crown
    # already drawn (seed 37: a fixture seated under a grove crown drawn two stages earlier)
    if any(boxed_ring_hit(q[0], q[1], ft.dry.near(q[0], q[1]), 3.0) for q in corners):  # a dry plot, inside or within 3 ft
        return True
    if any(ft.on_water(s, q[0], q[1]) for q in corners):
        return True
    tc = s.M.get("tree_crowns") or []
    for k in range(0, len(tc) - 2, 3):
        tx, ty, tr = float(tc[k]), float(tc[k + 1]), float(tc[k + 2])
        # the stand is drawn axis-aligned (cw x ch), so a crown is measured to its own box: squaring it on the half-diagonal, as
        # a raked footprint is, made a sheltered farm's 240 x 16 ft south band a 240 ft square that every crown within 120 ft of
        # it refused (feature 374 wave 153: Kashikawa's 77 frame-wide offers all refused, the bands left a third of the farm wide)
        if max(abs(cx - tx) - cw / 2, 0.0) ** 2 + max(abs(cy - ty) - ch / 2, 0.0) ** 2 < (tr + 0.6) ** 2:
            return True
    return bool(pond) and ((cx - pond[0]) / (pond[2] + 20.0)) ** 2 + ((cy - pond[1]) / (pond[3] + 20.0)) ** 2 <= 1.0




def _scene(seed: int) -> tuple[Settlement, list[tuple[list[tuple[float, float]], float]]]:
    rng = random.Random(seed)
    s = Settlement(2000, 2000, seed=1)
    s.meta(name="S", scale="hamlet", ftpx=1, down_deg=90)
    for _ in range(60):
        s.placed.append((rng.uniform(100, 1900), rng.uniform(100, 1900), rng.uniform(10, 60), rng.uniform(10, 60)))
    s.M["houses"].extend(
        {"x": rng.uniform(100, 1900), "y": rng.uniform(100, 1900), "w": rng.uniform(30, 50), "h": rng.uniform(20, 30), "rot": rng.uniform(-30, 30)}
        for _ in range(40)
    )
    s.M["wells"] = [{"x": rng.uniform(100, 1900), "y": rng.uniform(100, 1900), "r": 4.0} for _ in range(8)]
    s.M["farm_sheds"] = [{"x": rng.uniform(100, 1900), "y": rng.uniform(100, 1900), "w": 20.0, "h": 12.0} for _ in range(20)]
    s.M["byres"] = [{"x": rng.uniform(100, 1900), "y": rng.uniform(100, 1900), "w": 16.0, "h": 11.0} for _ in range(10)]
    crowns: list[float] = []
    for _ in range(80):
        crowns += [rng.uniform(100, 1900), rng.uniform(100, 1900), rng.uniform(6, 14)]
    s.M["tree_crowns"] = crowns
    lanes = []
    for _ in range(25):
        x, y = rng.uniform(100, 1900), rng.uniform(100, 1900)
        pts = [(x, y)]
        for _k in range(4):
            x, y = x + rng.uniform(-150, 150), y + rng.uniform(-150, 150)
            pts.append((x, y))
        lanes.append((pts, rng.uniform(1.5, 3.0) + 6.0))
    return s, lanes


def test_the_index_gives_the_straight_scans_verdict_for_every_strip() -> None:
    for seed in range(4):
        s, lanes = _scene(seed)
        near = StripNear(s, lanes)
        rng = random.Random(100 + seed)
        hits = 0
        for _ in range(600):
            cx, cy = rng.uniform(40, 1960), rng.uniform(40, 1960)
            cw, ch = (22.0, 16.0) if rng.random() < 0.5 else (16.0, 22.0)
            hx, hy = (cx + 30.0, cy) if rng.random() < 0.8 else (float(s.placed[0][0]), float(s.placed[0][1]))
            old = _scan_blocked(s, cx, cy, cw, ch, hx, hy, [], [], None, lanes)
            assert _strip_blocked(s, cx, cy, cw, ch, hx, hy, [], [], None, lanes, near=near) is old, (seed, cx, cy)
            hits += old
            if not old and rng.random() < 0.2:  # a strip seated mid-pass is a wall to the next (`household_bamboo`)
                s.placed.append((cx, cy, cw, ch))
        assert 50 < hits < 550, "the scene refuses some strips and admits others"


def test_a_house_excused_by_its_own_position_is_excused_through_the_index() -> None:
    s, lanes = _scene(7)
    near = StripNear(s, [])
    h = s.M["houses"][0]
    hx, hy = float(h["x"]), float(h["y"])
    old = _scan_blocked(s, hx, hy, 22, 16, hx, hy, [], [], None, [])
    assert _strip_blocked(s, hx, hy, 22, 16, hx, hy, [], [], None, [], near=near) is old


def test_the_index_tests_fewer_items_than_the_scan() -> None:
    s, lanes = _scene(3)
    near = StripNear(s, lanes)
    total = len(s.placed) + len(s.M["houses"]) + sum(len(p) - 1 for p, _h in lanes) + len(s.M["tree_crowns"]) // 3
    assert near.count(1000.0, 1000.0, 22.0, 16.0) < total / 4
