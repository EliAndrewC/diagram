"""269 E4: the dry hem's rows set tract by tract (B06, `waterfields/furrows.py`), and a fan's dry band on its toe (B07,
`fan_toe_hem` in `waterfields/comb.py`)."""

from __future__ import annotations

import math
import random

from l7r.diagram.waterfields.carve import _dry_fields
from l7r.diagram.waterfields.comb import FAN_TOE_FROM, fan_toe_hem
from l7r.diagram.waterfields.frame import _Frame
from l7r.diagram.waterfields.furrows import STEEP_SPREAD_RAD, TRACT_COLUMNS, TRACT_LEAN_RAD, TRACT_PLOT_TURN_RAD, TRACT_SEAM_MIN_RAD, furrow_turn, tract_ways


def test_furrow_turn_is_modulo_a_half_turn() -> None:
    assert furrow_turn(0.0, math.pi) < 1e-12
    assert abs(furrow_turn(0.1, math.pi - 0.1) - 0.2) < 1e-12
    assert abs(furrow_turn(0.0, math.pi / 2) - math.pi / 2) < 1e-12


def test_tract_ways_runs_columns_in_tracts_and_changes_at_every_seam() -> None:
    for seed in range(30):
        ways = tract_ways(random.Random(seed), 23, 0.4, 1.1)
        assert len(ways) == 23
        runs: list[list[float]] = []
        for k, (tract, heading) in enumerate(ways):
            if k == 0 or tract != ways[k - 1][0]:
                assert k == 0 or tract == ways[k - 1][0] + 1, "tracts are numbered in order along the canal"
                runs.append([])
            runs[-1].append(heading)
        assert all(len(set(r)) == 1 for r in runs), "one heading per tract"
        assert all(len(r) <= TRACT_COLUMNS[1] for r in runs)
        assert all(len(r) >= TRACT_COLUMNS[0] for r in runs[:-1]), "only the last tract may be cut short by the canal's end"
        assert all(furrow_turn(a[0], b[0]) >= TRACT_SEAM_MIN_RAD for a, b in zip(runs, runs[1:], strict=False))
        for r in runs:  # along the contour or down to the outfall, leaned by the tract's own ground
            assert min(furrow_turn(r[0], 0.4), furrow_turn(r[0], 0.4 + math.pi / 2)) <= TRACT_LEAN_RAD + 1e-9


def test_steep_ground_runs_every_tract_on_the_contour() -> None:
    spread = STEEP_SPREAD_RAD / 2
    ways = tract_ways(random.Random(4), 12, -0.2, spread)
    assert all(abs(h - (-0.2)) <= spread + 1e-9 for _t, h in ways)


def test_dry_fields_turns_each_plot_a_few_degrees_off_its_tract() -> None:
    F = _Frame(90.0)
    plots = _dry_fields(random.Random(2), F, [(300.0, 200.0), (300.0, 1200.0)], 1400.0, 1400.0, [], tract0=7)
    tracts = {p["tract"] for p in plots}
    assert len(tracts) >= 2 and min(tracts) == 7, "a caller's tract0 numbers the band"
    for t in tracts:
        thetas = [p["theta"] for p in plots if p["tract"] == t]
        assert max(furrow_turn(a, b) for a in thetas for b in thetas) <= 2 * TRACT_PLOT_TURN_RAD + 0.002


def test_a_wild_fan_keeps_its_dry_band_on_the_toe_alone() -> None:
    F = _Frame(90.0)  # the fall runs down the page: f is y
    paddies = [{"poly": [(0.0, 0.0), (100.0, 0.0), (100.0, 900.0)]}]
    hem = [{"poly": [(0.0, y), (10.0, y), (10.0, y + 10.0), (0.0, y + 10.0)]} for y in (95.0, 400.0, 595.0, 605.0, 850.0)]
    kept = fan_toe_hem(hem, F, (0.0, 0.0), paddies)
    assert [d["poly"][0][1] for d in kept] == [595.0, 605.0, 850.0] and FAN_TOE_FROM * 900 == 600.0
    assert fan_toe_hem(hem, F, (0.0, 2000.0), paddies) == hem, "a fan with no fall below its fork keeps its hem"
