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
        acres = min(9.0 * k**2, 10.0)  # saturates at 10 acres (ftpx 1)
        return SimpleNamespace(net={"k": k, "aspect": aspect, "acres": acres}, region=SimpleNamespace(area=acres * SQ_FT_PER_ACRE))

    def fake_finish(carve: SimpleNamespace) -> dict[str, object]:
        finishes.append(carve)
        return dict(carve.net)

    monkeypatch.setattr(w, "carve_comb", fake_carve)  # type: ignore[attr-defined]
    monkeypatch.setattr(w, "finish_comb", fake_finish)  # type: ignore[attr-defined]  # feature 220: the search carves, the winner alone is finished
    monkeypatch.setattr(w, "tail_dangles", lambda net: False)  # type: ignore[attr-defined]
    monkeypatch.setattr(w, "net_bends_acutely", lambda net: False)  # type: ignore[attr-defined]
    monkeypatch.setattr(w, "net_acres", lambda net, ftpx: net["acres"])  # type: ignore[attr-defined]
    # 11 acres against a 10-acre ceiling: no aspect lands the 6% the search aims at, and the best lands inside the 15% band
    # (feature 287) - past it the site is refused, `tests/hamletgen/test_fit_flanks.py`
    plan = SimpleNamespace(
        W=1000.0, H=1000.0, down_deg=90.0, offtakes_a=(), offtakes_b=(), grain_drift=0.0, fan_aspect=w.FAN_ASPECTS[0], target_acres=11.0, ftpx=1.0, head_deg=55.0, head_lead=105.0, brook_side=1
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
    # ...on a COARSE plot grid, for the reason recorded at the retired `test_the_fit_gives_a_saturated_best_aspect` (test_seed_branches_147.py)
    # (feature 158): the probe's decision is about the TARGET being unreachable, not about how many
    # plots a carve lays, and the plot count is all this test's seconds were.
    (bad, err), carve = _fit_at_aspect(plan, (700.0, 300.0), 3, 138.0, (78.0, 90.0), 1.0, 0.06, 9, probe=True)
    assert not bad and err > 0.5, "the best legal fan is kept, and it is nowhere near the ask"
    assert carve.region.area > 0, "and it is a real fan, not an empty one"  # a CARVE since feature 220: the search finishes only the winner; its ground since 302


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


def test_the_reservoir_is_seated_clear_of_a_spike_and_above_the_field_however_far_it_must_go() -> None:
    """Feature 287, water W46: the seat is SOLVED, not walked a bounded number of steps. An envelope spike between two of
    the old sixteen rim samples is caught by the polygon test, and an envelope that needs more than the old 60 steps is
    cleared all the same; both predicates hold at the seat."""
    from l7r.diagram.hamletgen.water.polder import reservoir_clear_of_crop, reservoir_uphill_of_field, walk_pond_uphill

    spiked = [(0.0, 0.0), (57.0, 0.0), (57.5, -5.5), (58.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    pond = (50.0, -8.0, 10.0, 6.0)  # clear of the square, but the spike's tip stands inside the rim between two samples
    rim = [(pond[0] + 10.0 * math.cos(a), pond[1] + 6.0 * math.sin(a)) for a in (k * math.pi / 8 for k in range(16))]
    assert not any(hg.point_in_poly(x, y, spiked) for x, y in rim), "sixteen samples miss the spike"
    assert not reservoir_clear_of_crop(pond, spiked)
    seat = walk_pond_uphill(pond, spiked, 0.0, -1.0)
    assert reservoir_clear_of_crop(seat, spiked) and reservoir_uphill_of_field(seat, spiked, (0.0, 1.0)) and seat[1] < pond[1]
    tall = [(0.0, 0.0), (100.0, 0.0), (100.0, 1000.0), (0.0, 1000.0)]
    deep = walk_pond_uphill((50.0, 990.0, 10.0, 6.0), tall, 0.0, -1.0)  # 83 steps of 12 ft to clear
    assert reservoir_clear_of_crop(deep, tall) and reservoir_uphill_of_field(deep, tall, (0.0, 1.0))
    beside = (150.0, 50.0, 10.0, 6.0)  # clear of the crop but beside it, level with its middle: not above it
    assert reservoir_clear_of_crop(beside, tall) and not reservoir_uphill_of_field(beside, tall, (0.0, 1.0))
    moved = walk_pond_uphill(beside, tall, 0.0, -1.0)
    assert reservoir_uphill_of_field(moved, tall, (0.0, 1.0)) and moved[1] < 0.0


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


def test_fit_polder_lands_inside_the_band_where_the_bisection_stalls(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Feature 287, water W47: rows with their tied columns step the acreage coarsely, and a target between two steps left
    the bisection 15% short and kept the miss. The (rows, cols) search goes on until a block lands inside the tolerance,
    and the drawn block is inside the band the rule reads (`polder_acres_in_band`). Stood in: acres = 0.1 per module."""
    from l7r.diagram import hamletgen as hg
    from l7r.diagram.hamletgen import water
    from l7r.diagram.hamletgen.water.polder import polder_acres_in_band

    plan = hg.plan_site(hg.HamletSpec(name="Polder", seed=12, households=16, field_archetype="polder_grid", down_deg=0))
    plan.target_acres = 10.2  # the bisection's blocks: 13x7 = 9.1 and 14x8 = 11.2, both over 6% off - it stalls between them

    def fake_build(W, H, origin, seed, **kw):  # type: ignore[no-untyped-def]
        return {"envelope": [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)], "rows": kw["rows"], "cols": kw["cols"]}

    monkeypatch.setattr(water.polder, "build_polder", fake_build)
    monkeypatch.setattr(water.polder, "net_acres", lambda net, ftpx: 0.1 * net["rows"] * net["cols"])
    monkeypatch.setattr(water.polder, "clean_polder_parcels", lambda net: net)
    net = water.fit_polder(plan, 12)
    assert polder_acres_in_band(0.1 * net["rows"] * net["cols"], plan.target_acres, 0.06)
    assert not polder_acres_in_band(9.9, 11.3) and polder_acres_in_band(10.5, 11.3)


def test_fit_polder_carries_the_cleanup_s_trim_into_its_next_choice_and_refuses_a_site_it_cannot_honor(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """W47's second half: the cleanup trims the winner after it is chosen; a trim that takes it out of the band sends the
    search to a block predicted with the trim carried, and a site no block can honor is refused, never drawn short."""
    from l7r.diagram import hamletgen as hg
    from l7r.diagram.hamletgen import water

    plan = hg.plan_site(hg.HamletSpec(name="Polder", seed=12, households=16, field_archetype="polder_grid", down_deg=0))
    plan.target_acres = 20.0

    def fake_build(W, H, origin, seed, **kw):  # type: ignore[no-untyped-def]
        return {"envelope": [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)], "rows": kw["rows"], "cols": kw["cols"], "k": 0.1}

    def clean(net):  # type: ignore[no-untyped-def]
        net["k"] = 0.08  # the cleanup takes a fifth of every block
        return net

    monkeypatch.setattr(water.polder, "build_polder", fake_build)
    monkeypatch.setattr(water.polder, "net_acres", lambda net, ftpx: net["k"] * net["rows"] * net["cols"])
    monkeypatch.setattr(water.polder, "clean_polder_parcels", clean)
    net = water.fit_polder(plan, 12)
    assert abs(0.08 * net["rows"] * net["cols"] - 20.0) / 20.0 <= 0.12
    plan.target_acres = 400.0  # more than a 44-row block can hold
    with pytest.raises(ValueError, match="no polder grid"):
        water.fit_polder(plan, 12)


def test_the_inlet_reaches_the_rim_and_never_drags_the_ring_off_its_corner() -> None:
    """Feature 287, water W44: the feeder's inlet stub ends on the reservoir's rim - its END moved there; but where the
    stub was trimmed away and the last point is a ring vertex inside the crop, that vertex stays (a toe is snapped to it)
    and the run to the rim is added after it."""
    from l7r.diagram.hamletgen.water.polder import inlet_to_rim

    env = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    pond = (50.0, -80.0, 20.0, 10.0)
    stub = inlet_to_rim([(50.0, 50.0), (50.0, 5.0), (50.0, -30.0)], pond, env)  # the stub's end, outside the crop, moves
    assert stub[:2] == [(50.0, 50.0), (50.0, 5.0)] and len(stub) == 3 and abs(stub[2][1] - (-80.0 + 10.0 - 2.0)) < 0.2
    kept = inlet_to_rim([(50.0, 50.0), (50.0, 5.0)], pond, env)  # no stub: the ring's own vertex stays
    assert kept[:2] == [(50.0, 50.0), (50.0, 5.0)] and len(kept) == 3 and abs(kept[2][1] - (-72.0)) < 0.2


def test_every_course_on_the_crest_is_gapped() -> None:
    """Feature 287, water W42: a course that runs over the dike's crest away from every gap - the inlet hairline the ring
    test never saw - is given a gap where it crosses, and the rule (`course_breaches`) then finds nothing."""
    from l7r.diagram.hamletgen.water.polder import gaps_for_courses
    from l7r.diagram.settlement.land.dikes import course_breaches, dike_band, dike_crest

    ring = [(200.0, 200.0), (700.0, 200.0), (700.0, 700.0), (200.0, 700.0)]
    crest = dike_crest(*dike_band(ring, 7)[1:3])
    hairline = [(450.0 + k * 0.05, 120.0 + 4.0 * k) for k in range(36)]  # crosses the north crest 250 ft from the sluice, in 4 ft steps
    sluices = [(200.0, 450.0)]
    assert course_breaches(hairline, crest, sluices)
    gaps = gaps_for_courses(sluices, [hairline], crest)
    assert len(gaps) > 1 and gaps[0] == sluices[0]
    assert not course_breaches(hairline, crest, gaps)
    assert gaps_for_courses(sluices, [[(300.0, 300.0), (400.0, 400.0)]], crest) == sluices, "a course inside the ring needs none"


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
    assert rec["len"] == pytest.approx(2 * hg.WEIR_HALF_FT) and rec["w"] == pytest.approx(hg.WEIR_THICK_FT[rec["form"]])
    assert s.M["meta"]["weir_form"] == rec["form"]
    # the brook runs due south; the bar lies across it, off square by WEIR_SKEW_DEG
    assert min(rec["deg"] % 180.0, 180.0 - rec["deg"] % 180.0) == pytest.approx(hg.WEIR_SKEW_DEG, abs=0.5)
    # settlement-review pass 10: THE MOUTH IS ABOVE THE WEIR, and the bar climbs upstream away from the intake bank
    ring = rec["poly"]
    rx = math.cos(math.radians(plan.head_deg))
    on_bank = [q for q in ring if (q[0] - 700.0) * rx > 0.0]
    assert on_bank and min(q[1] for q in on_bank) > 300.0, "on the intake bank the bar is below the mouth, so the race draws from the raised pool"
    bank_end = max(ring, key=lambda q: q[0] * (1 if rx > 0 else -1))
    far_end = min(ring, key=lambda q: q[0] * (1 if rx > 0 else -1))
    assert bank_end[1] > far_end[1], "the bar's end on the intake bank is its downstream end"


def test_each_weir_form_draws_at_its_own_thickness() -> None:
    """269 B22 (research/water/300): the weir's form is a knob, and each form is drawn at its own thickness - the fence
    at 1.5 ft, the gabion course at 2, the frame and the crib at 5 - with its own glyph, every one with the lip along
    the upstream face that tells a weir from a deck."""
    glyphs = set()
    for form, thick in hg.WEIR_THICK_FT.items():
        plan = a_plan()
        plan.intake = "weir"
        plan.brook = [(700.0, 100.0), (700.0, 300.0), (700.0, 600.0)]
        s = Settlement(int(plan.W), int(plan.H))
        s.pin_knob("weir_form", form)
        hg.draw_intake(s, plan, (700.0, 300.0))
        rec = s.M["weirs"][0]
        assert rec["form"] == form and rec["w"] == pytest.approx(thick / plan.ftpx)
        ink = s.out[[i for i, t in enumerate(s.out_cls) if t == "weir"][0]]
        assert 'stroke="#8FA6AE"' in ink  # the upstream lip
        glyphs.add(ink.split('fill="', 1)[1][:7])
    assert len(glyphs) == 4, "four forms, four bodies a reader can tell apart"


def test_the_race_opens_out_of_the_brook_bank() -> None:
    """269 B22 (research/water/310): the head race begins at the brook's bank, not on the stream. Its first stroke is
    carried back to the tap and the brook's bed moved to paint after it, so the bank is where the ditch begins."""
    from l7r.diagram.hamletgen.water.brook import open_race_mouth

    s = Settlement(1000, 1000)
    s.stream([(500.0, 100.0), (500.0, 300.0), (500.0, 600.0)], width=7)
    s.field_channel([(502.6, 303.7), (560.0, 385.0)], "#7FA3BD", 6.0, 6.0, late=True)
    brook = s.M["streams"][0]
    open_race_mouth(s, (500.0, 300.0))
    assert not any(w["rec"] is brook for w in s.water) and s.late_water[-1]["rec"] is brook
    race = s.M["drawn_channels"][0]
    assert race["pts"][0] == [500.0, 300.0]
    assert s.late_water[0]["bed"].count(' d="M500.0,300.0 L') == 1
    # no brook through the tap (or none at all): nothing moves
    s2 = Settlement(1000, 1000)
    s2.field_channel([(502.6, 303.7), (560.0, 385.0)], "#7FA3BD", 6.0, 6.0, late=True)
    open_race_mouth(s2, (500.0, 300.0))
    assert s2.M["drawn_channels"][0]["pts"][0] != [500.0, 300.0]


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


def test_a_hem_plot_at_the_fans_head_yields_to_the_brook_rather_than_throwing_it_sideways() -> None:
    """`brook_skirt`, settlement-review pass 9. A dry hem plot laid round the fork reaches up beside the intake,
    and floored against it the brook's first corner below the weir came out at 72-78 degrees on every brook map.
    Crop reaching within one skirt of the fan's head is left out of the profile - `_comb_draw_hem` drops any hem
    plot the brook's band then crosses - while crop further down the fan is still skirted as before."""
    plan = a_plan()
    dx, dy = plan.fall
    px, py = -dy, dx
    head_u = min(v[0] * dx + v[1] * dy for v in plan.envelope)
    tap = (700.0, 300.0)
    u_tap, v_tap = tap[0] * dx + tap[1] * dy, tap[0] * px + tap[1] * py
    # a hem plot beside the tap, well out on the brook's flank and starting above the fan's head
    at = [(u_tap + 60.0, v_tap + 90.0), (u_tap + 110.0, v_tap + 90.0), (u_tap + 110.0, v_tap + 130.0), (u_tap + 60.0, v_tap + 130.0)]
    hem = [(u * dx + v * px, u * dy + v * py) for u, v in at]
    assert min(u for u, _ in at) < head_u + hg.BROOK_SKIRT, "the fixture reaches within a skirt of the fan's head"

    def sharpest(course: list[tuple[float, float]]) -> float:
        worst = 0.0
        for a, b, c in zip(course, course[1:], course[2:], strict=False):
            h1, h2 = math.atan2(b[1] - a[1], b[0] - a[0]), math.atan2(c[1] - b[1], c[0] - b[0])
            worst = max(worst, abs((math.degrees(h2 - h1) + 180.0) % 360.0 - 180.0))
        return worst

    with_hem = hg.brook_skirt(plan, tap, 1, crop=[hem])
    without = hg.brook_skirt(plan, tap, 1)
    assert with_hem == without, "the hem plot at the head does not move the course at all"
    # ...and the same plot moved well down the fan IS skirted, so the rule is about where it stands, not what it is
    reach = max(w[0] * px + w[1] * py for w in plan.envelope)  # out past the envelope's own reach, or it is already cleared
    low = [(u * dx + v * px, u * dy + v * py) for u, v in [(u + head_u - u_tap + 400.0, v - v_tap + reach + 60.0) for u, v in at]]
    assert hg.brook_skirt(plan, tap, 1, crop=[low]) != without, "crop down the fan still shapes the course"
    assert sharpest(with_hem) == sharpest(without)


def test_a_leg_on_the_axis_is_tilted_just_off_it_not_kicked_into_a_sawtooth() -> None:
    """`_off_the_axes`, settlement-review pass 10. A straight reach down a due-south fall had every other leg
    kicked 11 px outward and drew a +/-29 degree sawtooth. The tilt is now just past the detector, so every leg
    clears the axis and no vertex turns by more than a few degrees."""
    from l7r.diagram.hamletgen.water.brook import _off_the_axes

    straight = [(100.0, float(y)) for y in range(0, 1000, 44)]
    out = _off_the_axes(straight, (-1.0, 0.0))
    heads = [math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) for a, b in zip(out, out[1:], strict=False)]
    assert all(min(h % 90.0, 90.0 - h % 90.0) >= 1.6 - 1e-9 or i % 2 for i, h in enumerate(heads)), "every flagged leg leaves the axis"
    turns = [abs(((b - a) + 180.0) % 360.0 - 180.0) for a, b in zip(heads, heads[1:], strict=False)]
    assert max(turns) < 8.0, f"no sawtooth: the sharpest turn is {max(turns):.1f} degrees"
    assert all(q[0] <= 100.0 for q in out), "and the course only ever moves AWAY from the crop"
    # a long leg is still capped at the old ceiling
    far = _off_the_axes([(0.0, 0.0), (0.0, 5000.0)], (-1.0, 0.0))
    assert far[1][0] == -11.0


def test_a_brook_that_doubles_back_is_unfolded() -> None:
    """Feature 261 (settlement-review of Sawada): no vertex of a brook's course turns it more than the limit; a fold is
    taken out vertex by vertex, and a course that turns gently is untouched."""
    from l7r.diagram.hamletgen.water.brook import unfold

    folded = [(0.0, 0.0), (100.0, 0.0), (40.0, -20.0), (40.0, -200.0)]  # out east, then back west and up
    fixed = unfold(folded, 100.0)
    assert fixed[0] == (0.0, 0.0) and fixed[-1] == (40.0, -200.0)
    assert (100.0, 0.0) not in fixed
    gentle = [(0.0, 0.0), (100.0, 0.0), (180.0, 40.0)]
    assert unfold(gentle, 100.0) == gentle
    assert unfold([(0.0, 0.0), (0.0, 0.0), (5.0, 5.0)], 100.0) == [(0.0, 0.0), (0.0, 0.0), (5.0, 5.0)], "a zero leg has no turn"


def test_an_exit_bend_sits_at_the_legs_middle_to_one_side_and_is_capped() -> None:
    """`exit_bend`: the midpoint of the leg, set aside by 12% of the leg on the given side, never more than 60 ft."""
    from l7r.diagram.hamletgen.water.brook import EXIT_BEND_MAX_FT, exit_bend

    assert exit_bend((0.0, 0.0), (1.0, 0.0), 100.0, 1.0) == pytest.approx((50.0, 12.0))
    assert exit_bend((0.0, 0.0), (1.0, 0.0), 100.0, -1.0) == pytest.approx((50.0, -12.0))
    assert exit_bend((0.0, 0.0), (0.0, 1.0), 1000.0, 1.0) == pytest.approx((-EXIT_BEND_MAX_FT, 500.0))


def test_the_finished_course_rounds_the_bends_and_holds_the_tap() -> None:
    """`finished_course` (feature 287, M2): a course in, the drawn course out - every free corner rounded at
    `BROOK_BEND_WIDTHS` of the width, the vertex at the tap kept, the ends kept; a tap more than a foot off every vertex,
    or at an end, holds nothing; a two-point course has no corner."""
    from l7r.diagram.hamletgen.consts import BROOK_BEND_WIDTHS
    from l7r.diagram.hamletgen.water.brook import finished_course
    from l7r.diagram.settlement._geom import fillet_polyline

    course = [(0.0, 0.0), (300.0, 0.0), (300.0, 300.0), (600.0, 300.0)]
    held = finished_course(course, 8.0, [(300.4, 300.3)])
    assert held[0] == (0.0, 0.0) and held[-1] == (600.0, 300.0) and (300.0, 300.0) in held, "the ends and the tap stay"
    assert (300.0, 0.0) not in held and len(held) > 4, "the free corner is rounded"
    assert held == [*fillet_polyline(course[:3], BROOK_BEND_WIDTHS * 8.0), *fillet_polyline(course[2:], BROOK_BEND_WIDTHS * 8.0)[1:]]
    free = finished_course(course, 8.0, [(300.0, 302.0), (0.0, 0.0)])
    assert free == fillet_polyline(course, BROOK_BEND_WIDTHS * 8.0) and (300.0, 300.0) not in free, "no tap within a foot: both corners round"
    assert finished_course([(0, 0), (5, 5)], 8.0) == [(0.0, 0.0), (5.0, 5.0)]


def test_round_the_brooks_draws_each_brook_at_its_finished_course() -> None:
    """`round_the_brooks` + `Settlement.round_stream` (feature 287, M2): the drawn brook IS `finished_course` of the course
    as first drawn, its width and the head race's tap; the first course is kept as `stations`, the no-build corridor
    follows the drawn course, a second pass draws the same course, and a two-point stream is left alone."""
    from l7r.diagram.hamletgen.water.brook import finished_course, round_the_brooks

    s = Settlement(800, 800, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    first = [(100.0, 100.0), (400.0, 100.0), (400.0, 400.0), (700.0, 400.0)]
    s.stream(first, width=9)
    s.stream([(10.0, 10.0), (20.0, 700.0)], width=7)
    s.M["channels"].append({"poly": [[400.0, 400.0], [460.0, 520.0]], "frm": {"kind": "stream"}, "to": {"kind": "field"}, "w": 6})
    s.M["channels"].append({"poly": [], "frm": {"kind": "stream"}})
    rec, short = s.M["streams"][-2], s.M["streams"][-1]
    round_the_brooks(s)  # type: ignore[arg-type]
    want = finished_course(first, 9.0, [(400.0, 400.0)])
    assert [tuple(p) for p in rec["poly"]] == want, "round_stream applies finished_course"
    assert (400.0, 400.0) in want and (400.0, 100.0) not in want
    assert rec["stations"] == [list(p) for p in first], "the course as first drawn is kept"
    assert any(list(c[0]) == want for c in s.corridors) and not any(list(c[0]) == first for c in s.corridors), "the corridor follows"
    round_the_brooks(s)  # type: ignore[arg-type]
    assert [tuple(p) for p in rec["poly"]] == want, "a second pass rounds the first course again, not the rounded one"
    assert "stations" not in short and short["poly"] == [[10.0, 10.0], [20.0, 700.0]]


def test_the_sink_stage_finishes_the_water_after_the_sink(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287, M2: the brook is rounded as `stage_sink`'s last step - after the drain is laid, before the seat."""
    calls: list[str] = []
    monkeypatch.setattr(hg.sink, "lay_sink", lambda s_, plan_: calls.append("sink"))
    monkeypatch.setattr(hg.sink, "round_the_brooks", lambda s_: calls.append("round"))
    hg.sink.stage_sink(None, None)  # type: ignore[arg-type]
    assert calls == ["sink", "round"]
    names = [st.__name__ for st in hg.driver.STAGES]
    assert names.index("stage_sink") + 1 == names.index("stage_seat"), "nothing reads the water between the sink and the seat"


def test_the_ways_route_against_the_course_as_first_drawn() -> None:
    """`stream_segs` (feature 287, M2): the router's brook is the `stations` - the course before rounding - so rounding
    the brook early does not move the ways; a stream never rounded is read from its poly."""
    from l7r.diagram.hamletgen.ways.checks import stream_segs

    class _S:
        M = {"streams": [{"poly": [[0, 0], [5, 3], [10, 0]], "stations": [[0, 0], [10, 0]]}, {"poly": [[0, 50], [0, 90]]}, {"poly": []}]}

    assert stream_segs(_S()) == [((0.0, 0.0), (10.0, 0.0)), ((0.0, 50.0), (0.0, 90.0))]  # type: ignore[arg-type]
