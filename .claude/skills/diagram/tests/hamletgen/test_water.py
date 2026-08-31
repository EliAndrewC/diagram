"""Unit tests for the water frame and the field it shapes (`hamletgen/water.py`), plus the waterfields frame math it stands on.

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram import waterfields as wf
from l7r.diagram.settlement import Settlement

from ._builders import a_plan

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


def test_dike_face_reads_the_rings_own_side_and_carries_a_gap() -> None:
    """`dike_face` (feature 150 T54) is what makes the waterward strip end exactly at the embankment:
    it takes the OUTERMOST point per bin on the flank's own half of the ring, so the strip can only
    stop at or outside the face - and a bin the ring does not reach (a crossing GAP cuts the outline,
    and the strip runs past the dike's ends) keeps its neighbor's face rather than jumping to the far
    side, which is how Kuwabata's west strip once came out 2,422 px wide and drowned the map."""
    ring = [(200.0, y) for y in range(200, 401, 10)]  # west face, y 200-400
    ring += [(210.0, y) for y in range(600, 801, 10)]  # west face again below a gap, 10 px further in
    ring += [(900.0, y) for y in range(200, 801, 10)]  # the east face
    face = hg.water.dike_face(ring, "W", 100.0, 900.0, bins=16)
    assert 3 <= len(face) <= 16  # thinned as it goes: a straight run of bins emits two points, not sixteen
    assert all(x <= 210.0 for x, _y in face), f"the east face leaked into the west flank: {face}"
    at = lambda y: min(face, key=lambda p: abs(p[1] - y))[0]  # noqa: E731 - the bin whose center is nearest y
    assert at(250.0) == 200.0 and at(750.0) == 210.0  # each stretch reports its own face
    assert at(500.0) == 200.0  # the gap between them keeps the neighbor's, not a jump across the ring
    east = hg.water.dike_face(ring, "E", 100.0, 900.0, bins=16)
    assert all(x >= 900.0 for x, _y in east)
    # a NOTCH the dike RECORDS steps the face inward, so the wet ground reaches into the cut; the same
    # empty bins with nothing recorded there stay at the neighbor's face (a sparse ring is not a notch)
    notched = hg.water.dike_face(ring, "W", 100.0, 900.0, bins=16, cut=40.0, cuts=[(205.0, 500.0)])
    at_n = min(notched, key=lambda p: abs(p[1] - 500.0))[0]
    assert at_n == 240.0, notched
    assert min(notched, key=lambda p: abs(p[1] - 250.0))[0] == 200.0  # the face itself is untouched
    # ...and the step reads the RECORD, not an empty bin: a notch whose own bin is FULL (the ring's cut
    # ends fill it, which is what Kuwabata's does - the first cut of this rule never fired anywhere)
    full = [(200.0, y) for y in range(200, 801, 10)]  # an unbroken west face, no gap at all
    full += [(900.0, y) for y in range(200, 801, 10)]
    stepped = hg.water.dike_face(full, "W", 100.0, 900.0, bins=16, cut=40.0, cuts=[(205.0, 500.0)])
    assert min(stepped, key=lambda p: abs(p[1] - 500.0))[0] == 240.0, stepped
    assert min(stepped, key=lambda p: abs(p[1] - 250.0))[0] == 200.0


def test_the_waterward_strip_stops_at_the_dikes_face() -> None:
    """T54: no strip vertex may stand inside the drawn band, and the strip must still cover the
    ground 28 px outside the dike's extreme, which is where `polder_waterward_flanks_wet` samples."""
    plan = a_plan()
    plan.field_archetype = "polder_grid"
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    band = [(500.0 + 40.0 * (i % 2), 400.0 + i * 10.0) for i in range(40)]  # a wandering west face
    band += [(1400.0, 400.0 + i * 10.0) for i in range(40)]
    s.M["dikes"] = [{"outline": [list(p) for p in band], "w_min": 14.0, "w_max": 38.0}]
    hg.water.stage_waterward(s, plan)
    strips = [m for m in s.M["marshes"] if m["role"] == "waterside"]
    assert strips, "no waterward strip was drawn"
    west = [m for m in strips if m["x"] < 900][0]
    assert max(p[0] for p in west["poly"]) <= 540.0  # never past the outermost face of the band
    assert hg.point_in_poly(500.0 - 28.0, 600.0, [(float(a), float(b)) for a, b in west["poly"]])  # the check's own sample is inside


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


def test_fit_field_probes_saturation_and_rerolls_the_best_aspect_in_full(monkeypatch: object) -> None:
    """Feature 145: an aspect whose largest fan is still short is dropped after two carves, and when no
    aspect lands the target the best one is searched again without the probe."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen import water as w

    carves: list[tuple[float, float]] = []

    def fake_comb(W: float, H: float, sluice: object, seed: int, **kw: object) -> dict[str, object]:
        k = float(kw["field_fall"]) / w.REF_FIELD_FALL  # type: ignore[arg-type]
        aspect = float(kw["canal_a_len"][0]) / (w.REF_CANAL_A[0] * k)  # type: ignore[index]
        carves.append((round(aspect, 2), round(k, 3)))
        return {"k": k, "aspect": aspect}

    monkeypatch.setattr(w, "build_comb", fake_comb)  # type: ignore[attr-defined]
    monkeypatch.setattr(w, "net_acres", lambda net, ftpx: min(9.0 * net["k"] ** 2, 10.0))  # type: ignore[attr-defined]  # saturates at 10 acres
    monkeypatch.setattr(w, "tail_dangles", lambda net: False)  # type: ignore[attr-defined]
    monkeypatch.setattr(w, "net_bends_acutely", lambda net: False)  # type: ignore[attr-defined]
    plan = SimpleNamespace(W=1000.0, H=1000.0, down_deg=90.0, offtakes_a=(), offtakes_b=(), grain_drift=0.0, fan_aspect=w.FAN_ASPECTS[0], target_acres=16.0, ftpx=1.0)
    net = w.fit_field(plan, (0.0, 0.0), 1, 20.0, (30.0, 40.0))  # type: ignore[arg-type]
    per_aspect = {}
    for a, _k in carves:
        per_aspect[a] = per_aspect.get(a, 0) + 1
    first = max(per_aspect, key=lambda a: per_aspect[a])  # the rolled aspect, searched again in full when nothing landed
    assert max(n for a, n in per_aspect.items() if a != first) <= 3, per_aspect  # every other aspect: k = 1, the probe, dropped
    assert per_aspect[first] > 3  # the rolled aspect was searched again in full
    assert net["k"] > 0


def test_a_saturated_aspect_stops_after_the_probe_instead_of_bisecting_a_fan_it_cannot_grow() -> None:
    """Cohort seed 47 (2026-08-28): at four of its five aspects the fan SATURATES - the envelope clamps it
    and the acreage sits at 16-17 against a 19.5 target however large k gets - and the old loop spent its
    last four carves at k = 2.16, 2.18, 2.19, 2.195 drawing the same 16.35 acres each time. The probe asks
    the question once: if neither k = 1 nor the LARGEST fan this aspect can draw reaches the target, keep
    the better of the two and give the time to the next aspect."""
    from l7r.diagram.hamletgen.water import _fit_at_aspect

    from ._builders import a_plan

    plan = a_plan()
    plan.target_acres = 500.0  # far past anything this envelope can hold: every aspect saturates
    # ...on a COARSE plot grid, for the reason recorded at `test_the_fit_gives_a_saturated_best_aspect`
    # (feature 158): the probe's decision is about the TARGET being unreachable, not about how many
    # plots a carve lays, and the plot count is all this test's seconds were.
    (bad, err), net = _fit_at_aspect(plan, (700.0, 300.0), 3, 138.0, (78.0, 90.0), 1.0, 0.06, 9, probe=True)
    assert not bad and err > 0.5, "the best legal fan is kept, and it is nowhere near the ask"
    assert net["plots"], "and it is a real fan, not an empty one"


def test_a_fan_with_no_plots_counts_as_DANGLING() -> None:
    """`tail_dangles` asks whether a supply canal ends outside the planted extent. With no plots
    there is no extent, so nothing can be inside one - the honest answer is True, and a fan in that
    state is refused rather than drawn. Production reaches it only through a fan that has already
    failed, which is why it was excluded; the function answers it directly."""
    assert hg.water.tail_dangles({"plots": [], "channels": []}) is True
