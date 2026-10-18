"""Feature 387 T01 (plan D1): the base tree's pieces answer as the whole-web rules they stand in for, on random webs.

`Ends.with_one_more` is `law.fronting_ends` on the web with one more lane and one more house, re-asking only the ends the
addition can change; `Faces.needles_with` is `len(law.needle_loops(...))` on a changed web, judging only the faces the change
meets. Both are compared with the whole rule on webs built at random - many lanes, near misses, crossings, houses with and
without a steading yard, the new house standing on an old one (as a household's way's house does in the gap pass)."""

from __future__ import annotations

import random
from typing import Any

from l7r.diagram.hamletgen.ways import law
from l7r.diagram.hamletgen.ways.tree_base import Ends, Faces
from tests._sweep import seeds


def _web(rng: random.Random, n: int) -> list[dict[str, Any]]:
    lanes = []
    for _ in range(n):
        x, y = rng.uniform(0, 600), rng.uniform(0, 600)
        pts = [(x, y)]
        for _k in range(rng.randint(1, 3)):
            x, y = x + rng.uniform(-120, 120), y + rng.uniform(-120, 120)
            pts.append((round(x, 1), round(y, 1)))
        lanes.append({"pts": [[a, b] for a, b in pts], "w": 3.0})
    return lanes


def _houses(rng: random.Random, n: int) -> list[dict[str, Any]]:
    return [{"x": round(rng.uniform(0, 600), 1), "y": round(rng.uniform(0, 600), 1), "w": 40.0, "h": 28.0, "rot": 0.0} for _ in range(n)]


def _counts(M: dict[str, Any]) -> dict[int, int]:
    return {h: len(e) for h, e in law.fronting_ends(M).items()}


def test_with_one_more_is_fronting_ends_on_the_grown_web() -> None:
    for seed in seeds(30):
        rng = random.Random(seed)
        houses = _houses(rng, rng.randint(1, 12))
        yards = [{"x": h["x"], "y": h["y"] + 30.0, "w": 30.0, "h": 20.0, "of": [h["x"], h["y"]]} for h in houses if rng.random() < 0.5]
        lanes = _web(rng, rng.randint(2, 14))
        stub = [{"pts": [[0.0, 300.0], [-50.0, 300.0]], "w": 6.0, "connector": True}]
        base = {"houses": houses, "threshing_yards": yards, "lanes": [*lanes, *stub]}
        ends = Ends(houses)
        for n, ln in enumerate(stub):
            ends.add(-1 - n, ln, base)
        for i, ln in enumerate(lanes):
            ends.add(i, ln, base)
        new = _web(rng, 1)[0]
        if rng.random() < 0.5:  # its end near another's end or tread, so it joins some
            q = rng.choice(lanes)["pts"][-1]
            new["pts"][0] = [q[0] + rng.uniform(-3, 3), q[1] + rng.uniform(-3, 3)]
        # the gap pass's house: one already standing (its twin), or a new one
        house = dict(rng.choice(houses)) if rng.random() < 0.6 else _houses(rng, 1)[0]
        yard = {"x": house["x"], "y": house["y"] - 30.0, "w": 30.0, "h": 20.0, "of": [house["x"], house["y"]]}
        trial = {"houses": [*houses, house], "threshing_yards": [*yards, yard], "lanes": [*lanes, new, *stub]}
        got = {h: c for h, c in ends.with_one_more(len(lanes), new, house, trial).items() if c}
        assert got == _counts(trial), seed


def test_needles_with_is_needle_loops_on_the_changed_web() -> None:
    for seed in seeds(40):
        rng = random.Random(1000 + seed)
        lanes = _web(rng, rng.randint(2, 10))
        if rng.random() < 0.5:  # a sliver: a lane laid along another, a few feet off
            a = rng.choice(lanes)["pts"]
            lanes.append({"pts": [[p[0] + 3.0, p[1] + 2.0] for p in a], "w": 3.0})
        faces = Faces(lanes)
        assert sum(1 for _f, thin in faces.faces if thin) == len(law.needle_loops({"lanes": lanes}))
        changed = [dict(ln) for ln in lanes]
        moved: list[Any] = []
        for k in rng.sample(range(len(changed)), k=min(2, len(changed))):  # an edited lane: its middle or an end moved
            old = [(float(p[0]), float(p[1])) for p in changed[k]["pts"]]
            pts = [list(p) for p in changed[k]["pts"]]
            j = rng.randrange(len(pts))
            pts[j] = [pts[j][0] + rng.uniform(-40, 40), pts[j][1] + rng.uniform(-40, 40)]
            changed[k] = {**changed[k], "pts": pts}
            moved += [old, [(float(p[0]), float(p[1])) for p in pts]]
        added = _web(rng, 1)[0]
        grown = [*changed, added]
        moved.append([(float(p[0]), float(p[1])) for p in added["pts"]])
        assert faces.needles_with(grown, moved) == len(law.needle_loops({"lanes": grown})), seed
