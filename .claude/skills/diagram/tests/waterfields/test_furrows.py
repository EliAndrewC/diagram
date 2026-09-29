"""269 E4: the dry hem's rows set tract by tract (B06, `waterfields/furrows.py`), and a fan's dry band on its toe (B07,
`fan_toe_hem` in `waterfields/comb.py`)."""

from __future__ import annotations

import math
import random

from l7r.diagram.waterfields.carve import _dry_fields
from l7r.diagram.waterfields.comb import FAN_TOE_FROM, fan_toe_hem, middle_reserve
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


def _sq(x: float, y: float, theta: float, tract: int, side: float = 40.0) -> dict:
    return {"poly": [(x, y), (x + side, y), (x + side, y + side), (x, y + side)], "theta": theta, "tract": tract}


def test_the_tract_judge_names_a_tract_run_apart_and_a_seam_that_does_not_turn() -> None:
    """Feature 287 (water W35): the rule is ONE judge, `tract_seams`, the finished-map test's own body lifted into the
    engine - one tract whose rows run apart and one seam whose rows do not turn are both named."""
    from l7r.diagram.waterfields.furrows import tract_seams

    plots = [_sq(0, 0, 0.0, 0), _sq(40, 0, 0.5, 0), _sq(80, 0, 0.52, 1)]
    within, seams, split, blurred = tract_seams(plots)
    assert (within, seams, len(split), len(blurred)) == (1, 1, 1, 1)
    assert tract_seams([]) == (0, 0, [], [])
    assert tract_seams(plots, side=10.0) == (0, 0, [], []), "a narrower adjacency sees no neighbors"


def test_a_second_band_tract_turns_off_every_tract_it_abuts() -> None:
    """Feature 287 (water W35): `tract_ways` turns each tract off the one before it, so a tract of the fork triangle's
    second band, laid against the first band's tracts 0 and 1 (headings 0 and a right angle), could come out on tract 0's
    heading. `settle_tract_seams` turns it - both its plots together - clear of both, and the judge then finds no seam
    that does not turn and no tract run apart."""
    from l7r.diagram.waterfields.furrows import settle_tract_seams, tract_seams

    plots = [_sq(0, 0, 0.0, 0), _sq(40, 0, math.pi / 2, 1), _sq(80, 0, 0.0, 2), _sq(20, 40, 0.05, 3), _sq(60, 40, 0.08, 3)]
    assert tract_seams(plots)[3], "the fixture's seam reads as one direction"
    settle_tract_seams(plots)
    assert tract_seams(plots)[2:] == ([], [])
    t3 = [p["theta"] for p in plots if p["tract"] == 3]
    assert abs((t3[1] - t3[0]) - 0.03) < 1e-9, "the tract turned as one, its own rows kept"
    for h in (0.0, math.pi / 2):
        assert furrow_turn(t3[0], h) >= TRACT_SEAM_MIN_RAD - 2 * TRACT_PLOT_TURN_RAD - 1e-9
    assert [p["theta"] for p in plots[:3]] == [0.0, math.pi / 2, 0.0], "the earlier tracts are not moved"
    settle_tract_seams(plots[:1])  # a lone plot has no seam


def test_a_tract_hemmed_in_on_every_heading_joins_its_nearest_neighbor() -> None:
    """Feature 287 (water W35), the fallback: a furrow is modulo pi and each neighbor rules out a window round its own
    heading, so a tract with more neighbors than fit round the half-circle has no heading left. It joins the neighbor
    whose rows it is closest to, taking that tract's number and heading - never left on a heading that reads as one."""
    from l7r.diagram.waterfields.furrows import settle_tract_seams

    plots = [_sq(0, 0, 0.0, t, side=10.0) for t in range(40)]  # forty tracts on one spot: every one neighbors every other
    settle_tract_seams(plots)
    assert len({p["tract"] for p in plots}) < 40, "some tract had no heading left and joined a neighbor"
    for t in {p["tract"] for p in plots}:
        assert len({round(p["theta"], 9) for p in plots if p["tract"] == t}) == 1, "a joined tract takes its host's heading"


def test_a_wild_fan_holds_its_middle_in_reserve_nearest_the_toe_first() -> None:
    """Feature 287, W36: the middle's hem plots are not lost but held back for the coarse-grain top-up, ordered down the
    fall from the toe's edge up toward the head (`middle_reserve`)."""
    F = _Frame(90.0)
    paddies = [{"poly": [(0.0, 0.0), (100.0, 0.0), (100.0, 900.0)]}]
    hem = [{"poly": [(0.0, y), (10.0, y), (10.0, y + 10.0), (0.0, y + 10.0)]} for y in (95.0, 400.0, 595.0, 605.0, 850.0, 300.0)]
    reserve = middle_reserve(hem, F, (0.0, 0.0), paddies)
    assert [d["poly"][0][1] for d in reserve] == [400.0, 300.0, 95.0], "the complement of the toe, nearest the toe first"
    assert not {id(d) for d in reserve} & {id(d) for d in fan_toe_hem(hem, F, (0.0, 0.0), paddies)}
