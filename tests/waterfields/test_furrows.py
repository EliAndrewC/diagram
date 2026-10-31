"""269 E4: the dry hem's rows set tract by tract (B06, `waterfields/furrows.py`), and a fan's dry band on its toe (B07,
`fan_toe_hem` in `waterfields/hem.py`)."""

from __future__ import annotations

import math

from l7r.diagram.waterfields.furrows import furrow_turn


def test_furrow_turn_is_modulo_a_half_turn() -> None:
    assert furrow_turn(0.0, math.pi) < 1e-12
    assert abs(furrow_turn(0.1, math.pi - 0.1) - 0.2) < 1e-12
    assert abs(furrow_turn(0.0, math.pi / 2) - math.pi / 2) < 1e-12


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
