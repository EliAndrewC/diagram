"""Unit tests for the water frame and the field it shapes (`hamletgen/water.py`), plus the waterfields frame math it stands on.

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram import waterfields as wf

# ---- the derivations that read the map ----------------------------------------------------------


def test_the_intake_sits_at_the_head_of_the_slope() -> None:
    """Gravity: a comb is fed from its high end. This was the first real bug in the experiment - the
    engine's canvas-relative `edge_*` anchors put a lateral intake at mid-height, which left the fan
    half a canvas to run and saturated the field far under the acreage the households needed."""
    plan = hg.plan_site(hg.HamletSpec(name="X", seed=6, households=15, down_deg=90.0))
    (sx, sy), name = hg.head_sluice(plan)
    assert sy < plan.H / 2  # upslope of the canvas middle on a south-falling map
    assert name.startswith("head_")


def test_a_fan_that_folds_back_on_itself_is_recognized() -> None:
    """The disqualifier `fit_field` uses: a hairpin in the fan's own ditch net."""
    straight = {"channels": [{"pts": [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)]}]}
    hairpin = {"channels": [{"pts": [(0.0, 0.0), (100.0, 0.0), (10.0, 5.0)]}]}
    assert not hg.net_bends_acutely(straight)
    assert hg.net_bends_acutely(hairpin)


def test_declared_knob_pins_reach_the_engine() -> None:
    """A `pins` entry is forwarded to the engine's own knob catalog, so a spec can steer a knob this
    module does not model (a land-use overlay, a field archetype)."""
    from l7r.diagram.settlement import Settlement

    plan = hg.plan_site(hg.HamletSpec(name="Pinned", seed=2, households=12, pins={"land_use_overlay": "lotus"}))
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    hg.stage_water_frame(s, plan)
    assert s.knob_pins["land_use_overlay"] == "lotus"


def test_miter_normals_on_a_straight_canal_are_the_chord_normal() -> None:
    # fall points +y (down_deg=90), so upslope is -y; every chord normal flips to point that way
    bn = wf._miter_normals([(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)], wf._Frame(90.0))
    assert len(bn) == 3
    for nx, ny in bn:
        assert nx == pytest.approx(0.0) and ny == pytest.approx(-1.0)


def test_miter_normals_share_and_scale_the_seam_at_a_bend() -> None:
    # a ~17-degree bend: the interior boundary gets ONE mitred normal - the bisector of the two
    # chord normals, scaled 1/cos(half-bend) so the hem band keeps its true depth at the seam
    F = wf._Frame(90.0)
    pts = [(0.0, 0.0), (100.0, 0.0), (200.0, -30.0)]
    bn = wf._miter_normals(pts, F)
    n0, n1 = bn[0], bn[2]  # the end boundaries carry their single chord's (unit) upslope normal
    assert math.hypot(*n0) == pytest.approx(1.0) and math.hypot(*n1) == pytest.approx(1.0)
    cos_full = n0[0] * n1[0] + n0[1] * n1[1]
    cos_half = math.sqrt((1.0 + cos_full) / 2.0)
    assert math.hypot(*bn[1]) == pytest.approx(1.0 / cos_half)
    # and it bisects: equal angle to both chord normals
    ml = math.hypot(*bn[1])
    assert (bn[1][0] * n0[0] + bn[1][1] * n0[1]) / ml == pytest.approx((bn[1][0] * n1[0] + bn[1][1] * n1[1]) / ml)


def test_miter_normals_fold_falls_back_to_the_outgoing_chord() -> None:
    # out and straight back: the two upslope normals cancel exactly, so no shared offset
    # direction exists - the boundary takes its outgoing chord's normal instead of dividing by ~0
    bn = wf._miter_normals([(0.0, 0.0), (0.0, 100.0), (0.0, 0.0)], wf._Frame(90.0))
    assert bn[0] == pytest.approx((-1.0, 0.0))
    assert bn[1] == pytest.approx((1.0, 0.0))
    assert bn[2] == pytest.approx((1.0, 0.0))


def test_miter_normals_caps_the_scale_on_a_hairpin() -> None:
    # a ~160-degree divergence between the flipped chord normals: the true miter scale would be
    # 1/cos(80 deg) = 5.8x, spiking the seam far upslope - capped at 2x (max(0.5, dot))
    bn = wf._miter_normals([(0.0, 0.0), (-8.7, 49.2), (-17.4, 0.2)], wf._Frame(90.0))
    assert math.hypot(*bn[1]) == pytest.approx(2.0)


def test_predict_k_steps_by_the_power_law_and_falls_back_to_the_midpoint() -> None:
    """The field solver's step (feature 145): a square-root step from one carve, a power-law step
    from two, and the bracket midpoint whenever the prediction is useless."""
    from l7r.diagram.hamletgen.water import _predict_k

    # one carve at k=1 gave 9 acres against a 16-acre target: k^2 scaling predicts 4/3
    assert abs(_predict_k([(1.0, 9.0)], 16.0, 0.35, 2.2) - 4.0 / 3.0) < 1e-9
    # two carves on an exact k^2 curve predict the exact answer
    assert abs(_predict_k([(1.0, 4.0), (1.5, 9.0)], 16.0, 0.35, 2.2) - 2.0) < 1e-9
    # a flat (same acreage twice) has no slope - square-root step from the last point
    assert abs(_predict_k([(1.0, 9.0), (1.2, 9.0)], 16.0, 0.35, 2.2) - 1.2 * (16.0 / 9.0) ** 0.5) < 1e-9
    # an exponent outside (0.2, 6) is not a fan - square-root step
    assert abs(_predict_k([(1.0, 1.0), (1.1, 100.0)], 200.0, 0.35, 2.2) - 1.1 * 2.0**0.5) < 1e-9
    # nothing carved: midpoint
    assert _predict_k([(1.0, 0.0)], 16.0, 0.5, 1.5) == 1.0
    # a prediction outside the open bracket: midpoint
    assert _predict_k([(1.0, 9.0)], 16.0, 0.5, 1.2) == 0.85
    # the same k twice cannot give a slope: square-root step
    assert abs(_predict_k([(1.0, 9.0), (1.0, 9.5)], 16.0, 0.35, 2.2) - (16.0 / 9.5) ** 0.5) < 1e-9
