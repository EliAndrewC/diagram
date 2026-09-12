"""Unit tests for the water frame and the field it shapes (`hamletgen/water/`), plus the waterfields frame math it stands on.

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram import waterfields as wf
from l7r.diagram.settlement import Settlement
from l7r.diagram.sitegen.geom import SQ_FT_PER_ACRE

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

    from l7r.diagram.hamletgen.water import fit as w  # the DEFINING submodule: `water` is a package since feature 230, and patching it reaches nothing the search bound

    carves: list[tuple[float, float]] = []

    finishes: list[object] = []

    def fake_carve(W: float, H: float, sluice: object, seed: int, **kw: object) -> SimpleNamespace:
        k = float(kw["field_fall"]) / w.REF_FIELD_FALL  # type: ignore[arg-type]
        aspect = float(kw["canal_a_len"][0]) / (w.REF_CANAL_A[0] * k)  # type: ignore[index]
        carves.append((round(aspect, 2), round(k, 3)))
        return SimpleNamespace(net={"k": k, "aspect": aspect}, planted_area=lambda k=k: min(9.0 * k**2, 10.0) * SQ_FT_PER_ACRE)  # saturates at 10 acres (ftpx 1)

    def fake_finish(carve: SimpleNamespace) -> dict[str, object]:
        finishes.append(carve)
        return dict(carve.net)

    monkeypatch.setattr(w, "carve_comb", fake_carve)  # type: ignore[attr-defined]
    monkeypatch.setattr(w, "finish_comb", fake_finish)  # type: ignore[attr-defined]  # feature 220: the search carves, the winner alone is finished
    monkeypatch.setattr(w, "tail_dangles", lambda net: False)  # type: ignore[attr-defined]
    monkeypatch.setattr(w, "net_bends_acutely", lambda net: False)  # type: ignore[attr-defined]
    plan = SimpleNamespace(
        W=1000.0, H=1000.0, down_deg=90.0, offtakes_a=(), offtakes_b=(), grain_drift=0.0, fan_aspect=w.FAN_ASPECTS[0], target_acres=16.0, ftpx=1.0, head_deg=55.0, head_lead=105.0, brook_side=1
    )
    net = w.fit_field(plan, (0.0, 0.0), 1, 20.0, (30.0, 40.0))  # type: ignore[arg-type]
    per_aspect = {}
    for a, _k in carves:
        per_aspect[a] = per_aspect.get(a, 0) + 1
    first = max(per_aspect, key=lambda a: per_aspect[a])  # the rolled aspect, searched again in full when nothing landed
    assert max(n for a, n in per_aspect.items() if a != first) <= 3, per_aspect  # every other aspect: k = 1, the probe, dropped
    assert per_aspect[first] > 3  # the rolled aspect was searched again in full
    assert net["k"] > 0
    assert len(finishes) == 1 and finishes[0].net["k"] == net["k"]  # ONE finish, of the winner (feature 220, SC-003)


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
    (bad, err), carve = _fit_at_aspect(plan, (700.0, 300.0), 3, 138.0, (78.0, 90.0), 1.0, 0.06, 9, probe=True)
    assert not bad and err > 0.5, "the best legal fan is kept, and it is nowhere near the ask"
    assert carve.plots, "and it is a real fan, not an empty one"  # a CARVE since feature 220: the search finishes only the winner


def test_a_fan_with_no_plots_counts_as_DANGLING() -> None:
    """`tail_dangles` asks whether a supply canal ends outside the planted extent. With no plots
    there is no extent, so nothing can be inside one - the honest answer is True, and a fan in that
    state is refused rather than drawn. Production reaches it only through a fan that has already
    failed, which is why it was excluded; the function answers it directly."""
    assert hg.water.tail_dangles({"plots": [], "channels": []}) is True


# ---- feature 219: Polder 12's three lines, as unit tests of the functions that own them ----------------


def test_the_reservoir_walks_uphill_until_its_rim_clears_the_crop_and_stays_put_when_already_clear() -> None:
    """`walk_pond_uphill` (lifted from `stage_polder`): the pond steps against the fall until no rim point lies on
    the envelope; a pond already clear is returned unchanged - the stop on the first step is the line the polder
    roll alone used to reach."""
    from l7r.diagram.hamletgen import water
    from l7r.diagram.settlement import point_in_poly

    square = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    walked = water.walk_pond_uphill((50.0, 50.0, 10.0, 6.0), square, 0.0, -1.0)
    assert walked[0] == 50.0 and walked[2:] == (10.0, 6.0), "only the position along the walk moves"
    assert walked[1] < 50.0 and walked[1] + 6.0 <= 0.0, walked
    rim_in = [(walked[0] + 10.0 * math.cos(a), walked[1] + 6.0 * math.sin(a)) for a in (k * math.pi / 8 for k in range(16))]
    assert not any(point_in_poly(x, y, square) for x, y in rim_in)
    clear = (50.0, -40.0, 10.0, 6.0)
    assert water.walk_pond_uphill(clear, square, 0.0, -1.0) == clear, "already clear: the first test stops the walk"
    assert water.walk_pond_uphill((50.0, 50.0, 10.0, 6.0), square, 0.0, -1.0, limit=1)[1] == 38.0, "the walk is bounded"


def test_the_dike_is_gapped_where_a_channel_crosses_it_and_not_twice_within_thirty_feet() -> None:
    """`dike_gaps_at_channels` (lifted from `stage_polder`): the named sluices, plus a gap at every real crossing of the
    ring, except a crossing within 30 ft of a gap already listed."""
    from l7r.diagram.hamletgen import water

    ring = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    channels = [
        {"pts": [[-20.0, 50.0], [20.0, 50.0]]},  # crosses the west side at (0, 50): a new gap
        {"pts": [[-20.0, 10.0], [20.0, 10.0]]},  # crosses at (0, 10), 10 ft from the sluice at (0, 0): that sluice's gap
        {"pts": [[30.0, 30.0], [60.0, 60.0]]},  # inside the ring: crosses nothing
    ]
    gaps = water.dike_gaps_at_channels(ring, channels, [(0.0, 0.0)])
    assert gaps[0] == (0.0, 0.0) and len(gaps) == 2, gaps
    assert abs(gaps[1][0]) < 1e-6 and abs(gaps[1][1] - 50.0) < 1e-6, gaps


def test_fit_polder_stops_the_bisection_the_moment_the_acreage_lands_inside_tolerance(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`fit_polder`'s stop: the first candidate whose acreage is within tolerance ends the search. `build_polder` and
    `net_acres` are stood in for, so the stop is tested on its own rather than on a solve that happens to land."""
    from l7r.diagram import hamletgen as hg
    from l7r.diagram.hamletgen import water

    plan = hg.plan_site(hg.HamletSpec(name="Polder", seed=12, households=16, field_archetype="polder_grid", down_deg=0))
    built: list[int] = []

    def fake_build(W, H, origin, seed, **kw):  # type: ignore[no-untyped-def]
        built.append(kw["rows"])
        return {"envelope": [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)], "rows": kw["rows"]}

    monkeypatch.setattr(water.polder, "build_polder", fake_build)  # the DEFINING submodule (feature 230 made `water` a package)
    monkeypatch.setattr(water.polder, "net_acres", lambda net, ftpx: plan.target_acres)
    monkeypatch.setattr(water.polder, "clean_polder_parcels", lambda net: net)  # the winner's parcel cleanup: the stub has no parcels to clean
    net = water.fit_polder(plan, 12)
    assert built == [25], "one candidate, within tolerance: the bisection stops there"
    assert net["rows"] == 25


# ---- the intake, and the brook that runs on past it (feature 230) --------------------------------


def test_the_brook_skirts_the_fan_without_turning_back_into_it() -> None:
    """`brook_skirt`. The course below the intake holds its offset at the outermost crop seen so far,
    so two properties hold by construction rather than by search: the offset never decreases, and no
    vertex lands inside the field. The square fixture is the crop; the intake sits above its head."""
    plan = a_plan()
    dx, dy = plan.fall
    px, py = -dy, dx
    course = hg.brook_skirt(plan, (700.0, 300.0), 1)
    lat = [q[0] * px + q[1] * py for q in course]
    floor = max(v[0] * px + v[1] * py for v in plan.envelope) + hg.BROOK_SKIRT
    abreast = [v for q, v in zip(course, lat, strict=False) if min(w[1] for w in plan.envelope) <= q[1] <= max(w[1] for w in plan.envelope)]
    assert all(v >= floor - 1e-6 for v in abreast), "every point abreast of the crop clears it by the skirt"
    assert all(not hg.point_in_poly(q[0], q[1], plan.envelope) for q in course), "no vertex inside the crop"
    assert course[-1][1] > plan.H, "and it leaves the frame downslope"
    bearings = [round(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])), 3) for a, b in zip(course, course[1:], strict=False)]
    assert len(set(bearings[1:])) > 3, "the course wanders - a held offset draws the ruled line the GM rejected"


def test_the_brook_takes_the_flank_it_is_rolled_onto() -> None:
    """The two values of `brook_side` put the course on the two sides of the fall axis - past the tap's own
    stride, which runs straight down the fall on either roll so the head race's offtake angle is true."""
    plan = a_plan()

    # THE TAP'S STRIDE IS TWO POINTS NOW, not one (feature 230): the corner cut splits it, and both points are
    # held on the fall so the offtake angle the record states is the one a reader measures. Drop the whole
    # stride - every leading vertex still on the fall axis - rather than a fixed count, so the test says what it
    # means: PAST the tap, the two rolls are on opposite flanks.
    def _past_the_tap(course):
        i = 0
        while i < len(course) and abs(course[i][0] - 700.0) < 0.5:
            i += 1
        return course[i:]

    one = _past_the_tap(hg.brook_skirt(plan, (700.0, 300.0), 1))
    other = _past_the_tap(hg.brook_skirt(plan, (700.0, 300.0), -1))
    assert max(q[0] for q in one) < 700.0 < min(q[0] for q in other), "the two rolls put the brook on the two sides of the fall axis"


def test_the_head_race_leaves_the_brook_at_the_offtake_angle_away_from_it() -> None:
    """The race turns off the fall by `OFFTAKE_DEG`, on the side the brook did NOT take - so the two
    never run alongside one another, which is the overlap the GM caught on the first Ikegami draft."""
    for side in (1, -1):
        plan = a_plan()
        plan.brook_side = side
        assert plan.head_deg == pytest.approx(plan.down_deg - side * hg.OFFTAKE_DEG)
    plan = a_plan()
    plan.brook_side = 1
    net = wf.carve_comb(plan.W, plan.H, (700.0, 300.0), 3, down_deg=plan.down_deg, head_deg=plan.head_deg, head_len=plan.head_lead).net
    hr = next(c for c in net["channels"] if c["role"] == "main")["pts"]
    assert math.hypot(hr[-1][0] - 700.0, hr[-1][1] - 300.0) == pytest.approx(plan.head_lead, abs=0.5)
    assert math.degrees(math.atan2(hr[-1][1] - 300.0, hr[-1][0] - 700.0)) == pytest.approx(plan.head_deg, abs=0.5)
    # ...and the angle the reader sees is the record's rule, because the brook is still on the fall where
    # the race leaves it: `settlement-review` measured 64 and 46 degrees when the course bent at the tap
    course = hg.brook_skirt(plan, (700.0, 300.0), plan.brook_side)
    below = math.degrees(math.atan2(course[0][1] - 300.0, course[0][0] - 700.0))
    assert abs(((plan.head_deg - below + 180.0) % 360.0) - 180.0) == pytest.approx(hg.OFFTAKE_DEG, abs=0.5)


def test_the_default_head_race_is_the_shape_every_other_caller_draws() -> None:
    """No bearing and no length given: 90 px straight down the fall, which is what a pond's outlet and
    a city fan's moat tap have always drawn and what those callers still get."""
    net = wf.carve_comb(2000.0, 2000.0, (700.0, 300.0), 3, down_deg=90.0).net
    hr = next(c for c in net["channels"] if c["role"] == "main")["pts"]
    assert hr[0] == (700.0, 300.0) and hr[-1] == pytest.approx((700.0, 390.0))


def test_a_weir_hamlet_draws_an_oblique_bar_across_the_brook_and_an_open_one_draws_nothing() -> None:
    """`draw_intake`. The bar is recorded and drawn only when the roll gave a weir; it lies across the
    brook's heading, skewed upstream, at the true size the constants declare."""
    for form, drawn in (("weir", 1), ("open", 0)):
        plan = a_plan()
        plan.intake = form
        plan.brook = [(700.0, 100.0), (700.0, 300.0), (760.0, 460.0)]
        s = Settlement(int(plan.W), int(plan.H))
        hg.draw_intake(s, plan, (700.0, 300.0))
        assert len(s.M.get("weirs", [])) == drawn
        assert sum(1 for t in s.out_cls if t == "weir") == drawn
    rec = s.M["weirs"][0] if False else None
    plan = a_plan()
    plan.intake = "weir"
    plan.brook = [(700.0, 100.0), (700.0, 300.0), (700.0, 600.0)]
    s = Settlement(int(plan.W), int(plan.H))
    hg.draw_intake(s, plan, (700.0, 300.0))
    rec = s.M["weirs"][0]
    assert rec["len"] == pytest.approx(2 * hg.WEIR_HALF_FT) and rec["w"] == pytest.approx(hg.WEIR_THICK_FT)
    # the brook here runs due south, so a bar square across it would lie east-west (0 deg); the skew
    # tilts it upstream by WEIR_SKEW_DEG
    assert rec["deg"] == pytest.approx((90.0 + 90.0 + hg.WEIR_SKEW_DEG) % 180.0, abs=0.5)


def test_the_weir_bar_is_placed_off_the_fall_when_the_intake_is_not_on_the_brook() -> None:
    """The brook is normally the course the intake sits on, so the bar reads its local heading from it.
    A caller that hands an intake the course does not contain falls back to the land's fall, which is
    the brook's own direction anyway - the guard is against an index error, not against a wrong angle."""
    plan = a_plan()
    plan.intake = "weir"
    plan.brook = [(100.0, 100.0), (100.0, 900.0)]
    s = Settlement(int(plan.W), int(plan.H))
    hg.draw_intake(s, plan, (700.0, 300.0))
    assert len(s.M["weirs"]) == 1


def test_the_exit_leg_turns_onto_the_fall_when_the_course_is_heading_across_it() -> None:
    """`brook_skirt`'s exit: the reach that leaves the frame keeps the course's own heading and only then turns
    onto the fall - but a course whose last stations run ACROSS the fall, or back up it, has no heading worth
    keeping, and the leg takes the fall directly. Otherwise the brook would leave the sheet sideways."""
    from l7r.diagram.hamletgen.water import brook as wb

    plan = a_plan()
    plan.envelope = [(400.0, 400.0), (1000.0, 400.0), (1000.0, 1000.0), (400.0, 1000.0)]
    course = wb.brook_skirt(plan, (700.0, 300.0), 1)
    assert len(course) > 4
    # the fall is due south on this plan, so the course must end further down the map than it starts
    assert course[-1][1] > course[0][1], "the brook leaves down the fall"
