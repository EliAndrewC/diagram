"""Feature 387 T02 (plan D2b, `ways/web_counts.py`): each whole-web count a knot's trial is judged by, asked only where its
edits can change it, equals the whole rule's count on the trial web - on random webs, random edits (an end moved, a middle
vertex moved, a lane re-aimed at another's end), houses with and without steading yards."""

from __future__ import annotations

import random
from typing import Any

from l7r.diagram.hamletgen.ways import law
from l7r.diagram.hamletgen.ways.knots import WebMemo
from l7r.diagram.hamletgen.ways.web_counts import Partners, WebEnds


def _pts(ln: dict[str, Any]) -> list[tuple[float, float]]:
    return [(float(p[0]), float(p[1])) for p in ln["pts"]]


def _web(rng: random.Random) -> dict[str, Any]:
    lanes: list[dict[str, Any]] = [{"pts": [[0.0, 300.0], [-80.0, 300.0]], "w": 6.0, "connector": True}]
    for _ in range(rng.randint(3, 14)):
        x, y = rng.uniform(0, 500), rng.uniform(0, 500)
        pts = [[x, y]]
        for _k in range(rng.randint(1, 3)):
            x, y = x + rng.uniform(-100, 100), y + rng.uniform(-100, 100)
            pts.append([round(x, 1), round(y, 1)])
        lanes.append({"pts": pts, "w": 3.0})
    if rng.random() < 0.6:  # one run on beside another, a doubled band
        a = rng.choice(lanes[1:])["pts"]
        lanes.append({"pts": [[p[0] + 4.0, p[1] + 3.0] for p in a], "w": 3.0})
    houses = [{"x": round(rng.uniform(0, 500), 1), "y": round(rng.uniform(0, 500), 1), "w": 40.0, "h": 28.0, "rot": 0.0} for _ in range(rng.randint(1, 8))]
    yards = [{"x": h["x"], "y": h["y"] + 30.0, "w": 30.0, "h": 20.0, "of": [h["x"], h["y"]]} for h in houses if rng.random() < 0.5]
    return {"lanes": lanes, "houses": houses, "threshing_yards": yards}


def _edit(rng: random.Random, M: dict[str, Any]) -> dict[int, list[tuple[float, float]]]:
    lanes = M["lanes"]
    out = {}
    for k in rng.sample(range(1, len(lanes)), k=rng.randint(1, min(3, len(lanes) - 1))):
        pts = _pts(lanes[k])
        j = rng.choice([0, len(pts) - 1, rng.randrange(len(pts))])
        if rng.random() < 0.5:  # re-aimed at another lane's end, as a gather does
            o = _pts(rng.choice(lanes))
            pts[j] = o[rng.choice([0, -1])]
        else:
            pts[j] = (pts[j][0] + rng.uniform(-30, 30), pts[j][1] + rng.uniform(-30, 30))
        out[k] = pts
    return out


def test_each_count_by_its_edits_is_the_whole_rules_on_the_trial() -> None:
    for seed in range(120):
        rng = random.Random(seed)
        M = _web(rng)
        lanes = M["lanes"]
        memo = WebMemo()
        ways = [_pts(ln) for ln in lanes]
        ids = memo.ids(ways)
        edits = _edit(rng, M)
        trial = {**M, "lanes": [dict(ln) for ln in lanes]}
        tw = list(ways)
        for i, p in edits.items():
            trial["lanes"][i]["pts"] = [[x, y] for x, y in p]
            tw[i] = _pts(trial["lanes"][i])
        ti = memo.ids(tw)
        for name, kind in (("doubled_tails", "doubled"), ("shadows", "beside")):
            part = Partners(kind, memo.pair, lanes, ways, ids)
            assert part.count() == memo.count(name, M, ways, ids), (seed, name)
            assert part.trial(memo.pair, lanes, tw, ti, list(edits)) == memo.count(name, trial, tw, ti), (seed, name)
        ends = WebEnds(M, lanes, ways)
        assert ends.count() == len(law.doorstep_ends(M)), seed
        assert ends.trial(trial, lanes, ways, tw, list(edits)) == len(law.doorstep_ends(trial)), seed
        assert {h: n for h, n in ends.trial_counts(trial, lanes, ways, tw, list(edits)).items() if n} == law.fronted_ends(trial), seed
        assert {h: n for h, n in ends.counts.items() if n} == law.fronted_ends(M), seed


def test_a_house_crowded_by_an_edit_is_counted() -> None:
    """Three free ends at one house only once an edit takes one off the junction it stood on: the doorstep count rises."""
    house = {"x": 100.0, "y": 100.0, "w": 40.0, "h": 28.0, "rot": 0.0}
    lanes = [
        {"pts": [[0.0, 300.0], [-80.0, 300.0]], "w": 6.0, "connector": True},
        {"pts": [[100.0, 130.0], [100.0, 250.0]], "w": 3.0},
        {"pts": [[110.0, 130.0], [200.0, 250.0]], "w": 3.0},
        {"pts": [[90.0, 130.0], [100.0, 250.0]], "w": 3.0},  # its far end on lane 1's: joined
    ]
    M = {"lanes": lanes, "houses": [house], "threshing_yards": []}
    ways = [_pts(ln) for ln in lanes]
    ends = WebEnds(M, lanes, ways)
    moved = [(90.0, 130.0), (20.0, 200.0)]
    trial = {**M, "lanes": [*lanes[:3], {**lanes[3], "pts": [[x, y] for x, y in moved]}]}
    tw = [*ways[:3], moved]
    assert ends.trial(trial, lanes, ways, tw, [3]) == len(law.doorstep_ends(trial))
