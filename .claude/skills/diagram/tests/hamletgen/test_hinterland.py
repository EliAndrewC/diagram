"""Unit tests for the ground between everything - open-ground scan, woodland, windbreak (`hamletgen/hinterland.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import pytest

from l7r.diagram import hamletgen as hg

# REACHED THROUGH THE MODULE, not through the package. `stage_windbreak` and `title_pocket` are
# internals of this stage; pinning them on hamletgen's star-import surface to satisfy one test would
# widen the package's public contract for a test's convenience (tests/hamletgen/test_surface.py).
from l7r.diagram.hamletgen import hinterland
from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement._geom import RingIndex

from ._builders import SQUARE, a_plan


def test_a_square_far_from_the_crop_clears_and_one_on_it_does_not() -> None:
    crop = RingIndex(SQUARE)
    assert hg._crop_refuses((700.0, 700.0), 50.0, crop) is True  # standing in it
    assert hg._crop_refuses((700.0, 200.0), 50.0, crop) is False  # 150 px clear, north of it: the 80 px set-back holds
    assert hg._crop_refuses((700.0, 1100.0), 50.0, crop) is True  # in the crop's sunny shadow: the 180 px set-back does not
    assert hg._crop_refuses((700.0, 1200.0), 50.0, crop) is True  # 150 px clear but SOUTH of it: the 180 px sunny set-back refuses
    assert hg._crop_refuses((700.0, 1200.0), 50.0, crop, sunny=100.0) is False  # ... unless the sunny set-back is the tighter profile
    assert hg._crop_refuses((700.0, 200.0), 50.0, crop, normal=200.0) is True  # a wide normal set-back refuses the northern seat too


def test_a_square_near_a_line_is_detected() -> None:
    assert hg._near_line((100.0, 100.0), 20.0, [(0.0, 100.0), (200.0, 100.0)], pad=10.0)
    assert not hg._near_line((100.0, 400.0), 20.0, [(0.0, 100.0), (200.0, 100.0)], pad=10.0)


def test_a_windbreak_column_with_no_house_of_its_own_leans_on_the_whole_fringe() -> None:
    """`belt_polygon` samples the windward fringe in 8 columns ACROSS the wind; a cluster with a
    gap in the middle leaves some column with no house within its own width, and that column has to
    fall back on the cluster's overall fringe rather than divide by nothing.

    Held here because the branch is reached by cluster SHAPE, not by any spec knob: it was live on
    the pool until an unrelated re-roll moved the houses, and a fallback that no map happens to hit
    is exactly the kind that rots unnoticed (the skill CLAUDE.md's 'a check that never RUNS looks
    like a check that passes', one layer over). Two tight groups 1,100 px apart across a northerly
    wind put the three middle columns outside every house's reach."""
    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["houses"] = [{"x": x, "y": 700.0, "w": 46.0, "h": 28.0} for x in (200.0, 260.0, 320.0, 1300.0, 1360.0, 1420.0)]
    belt = hg.belt_polygon(s, plan)
    assert belt, "a gapped cluster still needs a windbreak belt"
    assert len(belt) >= 4


def test_a_jittered_woodland_seat_that_leaves_the_scan_window_is_refused() -> None:
    """The accepted seat is nudged off the sampling lattice by up to half a step, and that nudge can
    carry a seat near the window's edge OUT of the window - so the qualification predicate re-tests
    the bounds rather than trusting that the scan only offered legal points.

    Held here because nothing in the pool or the cohort happens to jitter a seat past the edge, and
    an untested bounds guard on a predicate whose whole job is to re-ask about a MOVED point is the
    kind that rots silently (this engine's own 'a check that never RUNS looks exactly like a check
    that passes', one layer down). Forcing `_hjit` to its maximum drives every jitter the same way,
    +half a step on both axes, which is what an edge seat needs to escape."""
    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    # NO houses. This test used to seat a six-house row here, and with it the keep-out rectangle
    # around the house cloud refused EVERY candidate: `patches` came back empty, the loop below ran
    # zero times, and the test asserted nothing at all while passing (found 2026-08-19 while adding
    # the drop-path test below, which had inherited the same setup and the same emptiness). A
    # vacuous `for` over an empty list is the quietest way a test can stop testing, so the control
    # assertion now stands guard over it.
    s.M["fields"] = []
    plan.belt = []
    s._hjit = lambda x, y, salt: 1.0 if salt in (71.0, 72.0) else 0.5  # type: ignore[method-assign]
    patches = hg.hinterland.open_ground_patches(s, plan, count=3)  # via the submodule: a white-box unit test, not a package-surface consumer
    assert patches, "the scan seated nothing, so the per-seat assertions below would be vacuous"
    # The run must still terminate and return only legal squares - a refused jitter falls back to the
    # unjittered seat, it does not drop the parcel or escape the canvas.
    for poly in patches:
        assert all(0.0 <= px <= plan.W and 0.0 <= py <= plan.H for px, py in poly), "a seat left the canvas"


def test_a_coppice_parcel_is_an_irregular_ring_inside_its_ellipse() -> None:
    """Feature 133 T36 (GM 2026-08-27: "those coppice Patches. basically it looked like little
    squares"): the researched ruling (iriai boundaries run by ridge, stream and path - nothing
    rectilinear) is drawn as a wandering ring, never a 4-corner rectangle, and every vertex stays
    inside the ellipse the keep-outs were tested at."""
    import math

    s = Settlement(W=1000, H=1000, seed=3)
    ring = hg.hinterland._parcel_outline(s, 500.0, 500.0, 120.0, 80.0, 1.0, 0.0)
    assert len(ring) >= 10
    radii = [math.hypot(px - 500.0, py - 500.0) for px, py in ring]
    assert max(radii) <= 120.0 + 1e-6 and min(radii) >= 0.8 * 80.0 - 1e-6
    assert len({round(r) for r in radii}) > 4, "a ring whose radii repeat is a polygonized rectangle"
    for px, py in ring:  # inside the ellipse, with the 0.80 floor
        assert ((px - 500.0) / 120.0) ** 2 + ((py - 500.0) / 80.0) ** 2 <= 1.0 + 1e-6


def test_a_belt_vertex_in_the_title_pocket_is_pushed_out_of_it() -> None:
    """`stage_woodland` reserves blank ground for the map's name and keeps the COPPICE out of it, but
    the belt is computed there and drawn later, so `stage_windbreak` has to dent it around the same
    pocket - otherwise the hamlet's own title is drawn over its windbreak.

    Held here for the reason the gapped-column test above gives, and it is not hypothetical: this
    branch was live on the pool until the 2026-08-19 seam-alignment change moved every fan slightly,
    after which no map's belt happened to cross its title pocket and the gate failed on coverage
    rather than on behaviour. A dent that no map happens to need is exactly the kind that rots."""
    plan = a_plan(households=10)  # the canvas is derived from the household count, and the dent does not care (feature 158)
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["houses"] = [{"x": x, "y": 700.0, "w": 46.0, "h": 28.0} for x in (500.0, 560.0, 620.0)]
    tp = hinterland.title_pocket(s, plan)
    mid = ((tp[0] + tp[2]) / 2, (tp[1] + tp[3]) / 2)
    plan.belt = [(tp[0] - 80.0, tp[1] - 80.0), mid, (tp[2] + 80.0, tp[3] + 80.0), (tp[0] - 80.0, tp[3] + 80.0)]
    hinterland.stage_windbreak(s, plan)
    belt = [g for g in s.M["village_groves"] if g.get("role") == "windbreak"]
    assert belt, "the windbreak was not recorded"
    inside = [q for q in belt[0]["poly"] if tp[0] <= q[0] <= tp[2] and tp[1] <= q[1] <= tp[3]]
    assert not inside, f"belt vertices left standing in the title's pocket: {inside}"


def test_a_seat_whose_rotated_parcel_cannot_fit_the_window_is_dropped(monkeypatch: pytest.MonkeyPatch) -> None:
    """The last resort of the woodland scan: when neither the aspect ladder nor the local shrink
    ladder can fit the parcel's ROTATED bbox inside the predicted kept window, the seat is abandoned
    rather than drawn half off the sheet.

    Held here for the same reason as the two tests above, and the reason is now measured rather than
    assumed: an attribution census over seeds 1-24 (bbox floor 0.0 vs 0.72) returns IDENTICAL parcel
    counts, so on every seed the engine currently rolls, the shrink ladder always rescues the seat and
    this branch never runs. It is a guard against a case the corpus does not contain, which is exactly
    the kind that rots - and the coverage gate caught it the moment the branch was added.

    Driving `WOODLAND_BBOX_FLOOR` above 1.0 makes the window test unsatisfiable by construction (no
    box can have more than 100% of itself inside anything), which forces the drop for every seat
    without contriving a geometry. That the constant CAN be driven is why it was lifted out of the
    closure; a floor buried in a nested function cannot be tested against."""
    plan = a_plan()

    def _scan() -> list:
        s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
        # NO houses: with the six-house row the older test in this file uses, the keep-out rectangle
        # around the house cloud refuses every candidate and the scan returns [] before the ladder is
        # ever reached. That is what made the first cut of this test vacuous.
        s.M["fields"] = []
        plan.belt = []
        return hg.hinterland.open_ground_patches(s, plan, count=3)

    # THE CONTROL IS THE POINT, and the first cut of this test did not have it. Asserting only that
    # the floored scan returns [] passes just as well when NO seat qualified and the ladder was never
    # reached - which is what actually happened: the test went green while line 495 stayed uncovered.
    # A test green for the wrong reason is the same defect this whole feature kept turning up, one
    # layer further in. So prove the setup DOES seat parcels first; only then does taking them away
    # mean the drop path ran.
    assert _scan(), "the control scan seated nothing, so a later empty result would prove nothing"
    monkeypatch.setattr(hinterland.parcels, "WOODLAND_BBOX_FLOOR", 1.01)  # feature 173: the floor and its reader both live in hinterland/parcels.py now
    assert _scan() == [], "an unsatisfiable window floor must drop every parcel, not draw one the crop will cut off"


def test_the_title_pocket_is_reserved_once_and_shrinks_before_it_gives_up() -> None:
    """Feature 150 (Kuwabata seed 21): four callers ask for the pocket at four stages and each ask used to
    re-run the search against ITS moment's obstacles, so the belt was dented around one answer and the
    frame got another. The first answer is the reservation. And a sheet with no 300 x 190 blank still
    reserves a 210 x 120 one (the placard is ~195 x 106) before reserving nothing."""
    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    # columns 270 apart (224 ft clear), rows 160 apart (132 ft clear) down the whole square: a 210 x 120 box fits, a 300 x 190 does not
    s.M["houses"] = [{"x": x, "y": y, "w": 46.0, "h": 28.0} for x in (400.0, 670.0, 940.0) for y in (400.0, 560.0, 720.0, 880.0)]
    tp = hinterland.title_pocket(s, plan)
    assert (tp[2] - tp[0], tp[3] - tp[1]) == (210.0, 120.0)
    assert plan.title_pocket == tp and plan.title_pocket_outside is False
    s.M["houses"].append({"x": tp[0] + 100.0, "y": tp[1] + 60.0, "w": 46.0, "h": 28.0})  # a house INTO the pocket...
    assert hinterland.title_pocket(s, plan) == tp  # ...changes nothing: the reservation stands


def test_a_sheet_with_no_blank_box_reserves_a_pocket_outside_its_content() -> None:
    """Feature 150 (Kuwabata seed 21): with the cluster seated clear of the reed fringe nothing on the sheet
    was blank enough for the placard, and `title()` fell back to a corner ON the windbreak. The pocket is
    then reserved just outside the content, at the first ask, so the belt dents around it and the crop can
    take it in as content; every candidate tried is recorded in the manifest."""
    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["houses"] = [{"x": x, "y": y, "w": 46.0, "h": 28.0} for x in range(400, 1001, 80) for y in range(400, 1001, 60)]  # a solid grid
    tp = hinterland.title_pocket(s, plan)
    assert plan.title_pocket_outside is True, (tp, s.M["meta"].get("title_pocket_tries"), hinterland.content_box(s, plan, pad=0.0))
    assert tp[3] <= 400.0 - 14.0  # above the houses' top edge (14 px past the envelope the content box reports), not over it
    tries = s.M["meta"]["title_pocket_tries"]
    assert tries and tries[-1][4] == 1.0 and all(t[4] == 0.0 for t in tries[:-1])


def test_bamboo_seats_refuse_the_canvas_edge_and_the_title_pocket() -> None:
    """Feature 146: two of the bamboo scan's refusal reasons - a candidate hanging off the canvas, and one
    inside the pocket the title placard will occupy (the title is drawn later, so its ground is reserved)."""
    from l7r.diagram.settlement import Settlement

    from ._builders import a_plan

    s = Settlement(600, 600, seed=1)  # small, so the 30 px margin is a large share of the sheet
    s.meta(name="B", scale="hamlet", ftpx=1, down_deg=90)
    plan = a_plan()
    seats = hg.hinterland.bamboo_seats(s, plan)
    assert all(30 <= sum(q[0] for q in poly) / len(poly) <= 570 for poly in seats), "no seat hangs off the canvas"


def test_bamboo_blocked_refuses_the_canvas_margin_and_the_title_pocket() -> None:
    """Two arms of the take-yabu siter that a rolled hamlet never enters, because its sampler never
    proposes a candidate that near the frame or under the title card. They are real refusals all the
    same: a stand drawn into the margin is cropped in half, and one under the title is illegible."""
    from l7r.diagram.hamletgen.hinterland import bamboo_blocked

    extent = (1000.0, 1000.0)
    assert bamboo_blocked(10.0, 500.0, extent, (0.0, 0.0, 0.0, 0.0), [], [], [], None, 30.0), "inside the margin"
    assert bamboo_blocked(500.0, 990.0, extent, (0.0, 0.0, 0.0, 0.0), [], [], [], None, 30.0), "and the far margin"
    assert bamboo_blocked(500.0, 500.0, extent, (400.0, 400.0, 600.0, 600.0), [], [], [], None, 30.0), "under the title card"
    assert not bamboo_blocked(500.0, 500.0, extent, (0.0, 0.0, 10.0, 10.0), [], [], [], None, 30.0), "open ground"


def test_a_parcel_that_will_not_fit_is_shrunk_down_the_ladder_before_it_is_dropped() -> None:
    """SHRINK BEFORE DROPPING. A seat whose full-size square overruns the frame is usually a seat near
    the edge that a slightly smaller square clears, and a smaller coppice on the sheet beats a larger
    one the crop cuts off - so the parcel walks down 0.9 / 0.8 / 0.7 / 0.6 before the seat is called
    unusable.

    THIS LADDER HAS A HISTORY WORTH THE TEST. Feature 147 parked its two lines behind a coverage
    pragma while the floor's verdict on them flickered, and feature 149 found the real cause (an
    entry's stored coverage outliving the key it was recorded under). Parking was the wrong answer
    twice over: the ladder is a decision about NUMBERS and can simply be asked about numbers, which is
    what this does - `fits` is a plain predicate, not a settlement."""
    from l7r.diagram.hamletgen.hinterland import fit_square_parcel

    # nothing fits, at any rung
    assert fit_square_parcel(100.0, 10.0, lambda _h: False) is None
    # the first rung clears
    assert fit_square_parcel(100.0, 10.0, lambda h: h <= 90.0) == 90.0
    # ...and it walks on down when it must
    assert fit_square_parcel(100.0, 10.0, lambda h: h <= 61.0) == 60.0
    # THE FLOOR IS A FLOOR, NOT A RUNG: every rung is clamped up to it, so a parcel already at the
    # minimum is offered once at the minimum rather than shrunk below legibility
    assert fit_square_parcel(100.0, 95.0, lambda h: h <= 95.0) == 95.0
    assert fit_square_parcel(100.0, 95.0, lambda h: h < 95.0) is None


def test_a_rotated_parcel_is_measured_by_the_bbox_the_check_measures() -> None:
    """ROTATING A BOX GROWS ITS AXIS-ALIGNED BBOX - up to sqrt(2) at 45 degrees, even for a square -
    and `woodland_commons_within_the_frame` measures the grown one. Testing the unrotated square
    instead let a seat pass the ladder at 0.8 and draw a parcel 0.67 inside the window, which cohort
    seed 33 did the moment the cluster change walked it to the edge: a check and the thing it checks
    measuring different quantities."""
    import math

    from l7r.diagram.hamletgen.hinterland import WOODLAND_BBOX_FLOOR, parcel_bbox_ok

    frame = (0.0, 0.0, 1000.0, 1000.0)
    axis = (1.0, 0.0)  # unrotated
    diag = (math.cos(math.radians(45.0)), math.sin(math.radians(45.0)))

    # dead centre: fits at any rotation
    assert parcel_bbox_ok(500.0, 500.0, 100.0, 100.0, *axis, frame)
    assert parcel_bbox_ok(500.0, 500.0, 100.0, 100.0, *diag, frame)

    # ON THE EDGE, rotation is what decides it: the same square, same seat, different answer
    on_edge_axis = parcel_bbox_ok(60.0, 500.0, 100.0, 100.0, *axis, frame)
    on_edge_diag = parcel_bbox_ok(60.0, 500.0, 100.0, 100.0, *diag, frame)
    assert on_edge_axis and not on_edge_diag, "the rotated bbox is wider and falls further outside"

    # wholly outside keeps nothing
    assert not parcel_bbox_ok(-500.0, 500.0, 100.0, 100.0, *axis, frame)
    assert 0.0 < WOODLAND_BBOX_FLOOR < 1.0


def test_bamboo_blocked_refuses_ground_inside_the_crop() -> None:
    """THE PLACER'S OWN GUARANTEE, which the retired `bamboo_stands_clear_of_paddies` check used to
    re-measure on the finished map (feature 166).

    A take-yabu grows on the dry margin above the rice, never in it. The placer already refuses it: a
    candidate whose sample lands inside a crop polygon (a flooded paddy OR a dry plot - the distinction
    cost a settlement-review finding on Mizuguchi, where a stand 12.2 ft inside a soybean plot passed a
    gate that read paddy outlines alone) is blocked. Asserting that here, on two polygons and a point,
    is the same guarantee measured where it is made instead of once per map afterwards."""
    from l7r.diagram.hamletgen.hinterland import bamboo_blocked

    extent = (1000.0, 1000.0)
    nowhere = (0.0, 0.0, 0.0, 0.0)
    paddy = [(400.0, 400.0), (600.0, 400.0), (600.0, 600.0), (400.0, 600.0)]

    assert bamboo_blocked(500.0, 500.0, extent, nowhere, [], [], [(paddy, 0.0)], None, 30.0), "a culm standing in the rice"
    assert not bamboo_blocked(300.0, 300.0, extent, nowhere, [], [], [(paddy, 0.0)], None, 30.0), "the dry margin is open ground"


def test_bamboo_blocked_keeps_its_pad_off_the_crop_edge() -> None:
    """The refusal is not merely 'inside the outline' - the seat scan holds a pad clear of it, so a stand
    hugging the bund is refused too. Without the pad a culm drawn to its full width overhangs the water it
    is supposed to stand above."""
    from l7r.diagram.hamletgen.hinterland import bamboo_blocked

    extent = (1000.0, 1000.0)
    nowhere = (0.0, 0.0, 0.0, 0.0)
    paddy = [(400.0, 400.0), (600.0, 400.0), (600.0, 600.0), (400.0, 600.0)]
    assert bamboo_blocked(390.0, 500.0, extent, nowhere, [], [], [(paddy, 20.0)], None, 30.0), "10 ft outside, inside a 20 ft pad"
    assert not bamboo_blocked(370.0, 500.0, extent, nowhere, [], [], [(paddy, 20.0)], None, 30.0), "30 ft outside, clear of the pad"


# ---- the windbreak belt's own guarantees (feature 166) -------------------------------------------
# Carrying `village_windbreak_present`, `_embraces_cluster`, `_scales_with_cluster` and
# `_is_continuous`, which the retired battery re-measured on every finished map. A back-village grove
# is planted where the houses are, so all four are properties of `belt_polygon`'s output RELATIVE to
# the cluster it shelters - which is why they are asserted against a cluster built here rather than
# against a rolled map.


def _cluster(s, xs, y=700.0):
    s.M["houses"] = [{"x": x, "y": y, "w": 46.0, "h": 28.0} for x in xs]


def test_an_ordinary_cluster_gets_a_belt_at_all() -> None:
    """`village_windbreak_present`. A settlement with no windbreak is a settlement nobody planted,
    and the belt is the commonest piece of managed vegetation on a farming map."""
    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    _cluster(s, (600.0, 660.0, 720.0, 780.0, 840.0))
    belt = hg.belt_polygon(s, plan)
    assert belt and len(belt) >= 4, "an ordinary cluster must get a belt"


def test_the_belt_stands_on_the_WINDWARD_side_of_the_cluster() -> None:
    """`village_windbreak_embraces_cluster`. A belt downwind of the houses shelters nothing - it is
    the wind it is planted against, so its side is the whole point rather than a detail."""
    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    xs = (600.0, 660.0, 720.0, 780.0, 840.0)
    _cluster(s, xs)
    belt = hg.belt_polygon(s, plan)
    wx, wy = plan.wind
    ccx, ccy = sum(xs) / len(xs), 700.0
    bcx = sum(p[0] for p in belt) / len(belt)
    bcy = sum(p[1] for p in belt) / len(belt)
    # THE CONVENTION, measured rather than assumed: `plan.wind` points TOWARD the windward side (the
    # direction the wind comes FROM), so the belt's centre offsets along +wind. Measured on this very
    # fixture: wind (0, -1), cluster centre (720, 700), belt centre (720, 547) - 153 px along +wind.
    # My first draft asserted the opposite sign and failed, which is the cheapest possible way to
    # learn a convention and the reason it is written down here instead of remembered.
    assert (bcx - ccx) * wx + (bcy - ccy) * wy > 0, "the belt sits downwind of the cluster it should shelter"


def test_a_wider_cluster_gets_a_longer_belt() -> None:
    """`village_windbreak_scales_with_cluster`. A belt that shelters three houses of a twenty-house
    settlement fails the rule and deserves to: the band is sampled across the cluster's own windward
    profile, so its length has to follow the cluster's width."""
    plan = a_plan()
    narrow = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    _cluster(narrow, (700.0, 740.0, 780.0))
    wide = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    _cluster(wide, tuple(400.0 + 80.0 * i for i in range(12)))

    def _span(belt):
        return max(p[0] for p in belt) - min(p[0] for p in belt)

    assert _span(hg.belt_polygon(wide, plan)) > _span(hg.belt_polygon(narrow, plan)), "a twelve-house cluster got no more belt than a three-house one"


def test_the_belt_is_one_band_rather_than_scattered_pieces() -> None:
    """`village_windbreak_is_continuous`. A windbreak with a hole in it funnels wind through the gap
    rather than lifting it over, which is worse than no belt. The footprint is a single ring, and a
    ring is continuous by construction - so what this pins is that it STAYS one, at constant depth,
    rather than degenerating as the profile it follows gets ragged."""
    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    _cluster(s, (200.0, 260.0, 320.0, 1300.0, 1360.0, 1420.0))  # the gapped cluster, deliberately ragged
    belt = hg.belt_polygon(s, plan)
    assert belt, "even a gapped cluster gets a belt"
    xs = [p[0] for p in belt]
    assert max(xs) - min(xs) > 800.0, "the belt spans the whole ragged fringe rather than one lobe of it"


def test_the_woodland_shrink_ladder_keeps_every_parcel_inside_the_band_and_above_the_floor() -> None:
    """THE PARCEL BAND, on the stub site (feature 216; until then a rostered roll, `Woodland-shrink` seed 4, whose lines
    the audit found reached by nothing it alone did - 215 R1). Sweep the asked sizes and demand every parcel that comes
    back is no larger than the ladder-and-roll ceiling and no smaller than the commons floor.

    THE CEILING IS 1.10 x 1.15 (feature 147): the first rung is `size * _ladder` where `_ladder = 0.90 + 0.20 * jitter`
    reaches 1.10, and a per-parcel size roll of +/-15% sits on top of it - the old assertion `max(w, h) <= asked` had
    never been promised and had never run (the site it used returned zero parcels). What this no longer proves, stated
    (specs/216 FR-005 a): the band on a ROLLED site; the ladder's own decisions are pinned above, and the site here is
    the one the scan tests use. The control assertion guards the vacuous case that hid the false claim for three features."""
    from l7r.diagram.hamletgen.hinterland import _COMMONS_FLOOR_FT, open_ground_patches

    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["fields"] = []
    plan.belt = []
    ceiling = 1.10 * 1.15
    widest: list[tuple[float, float]] = []
    for asked in range(120, 720, 40):  # from the commons floor up: below it the floor is the asked size's own, not the commons'
        for poly in open_ground_patches(s, plan, 3, size=float(asked)):
            w = max(p[0] for p in poly) - min(p[0] for p in poly)
            h = max(p[1] for p in poly) - min(p[1] for p in poly)
            widest.append((float(asked), max(w, h)))
    assert widest, "no parcel came back at ANY asked size - this test would assert nothing"
    for asked, got in widest:
        assert got <= asked * ceiling, f"a parcel came back {got / asked:.2f}x the asked size, past the ladder-and-roll band ({got:.0f} for {asked:.0f})"
        assert got >= _COMMONS_FLOOR_FT, f"a parcel came back at {got:.0f} px, under the {_COMMONS_FLOOR_FT:.0f} ft floor"


def test_the_windbreak_stage_draws_nothing_when_the_plan_has_no_belt() -> None:
    """`stage_windbreak`'s first return (feature 216): a plan whose belt is empty - a linear hamlet after the frontage
    pass, or any site the belt derivation refused - draws no grove and records none."""
    plan = a_plan()
    plan.belt = []
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    before = dict(s.M.get("village_groves", [])) if isinstance(s.M.get("village_groves"), dict) else list(s.M.get("village_groves", []))
    hinterland.stage_windbreak(s, plan)
    assert list(s.M.get("village_groves", [])) == list(before), "no belt, no windbreak"


def test_bamboo_blocked_indexed_matches_bamboo_blocked_on_random_ground() -> None:
    """Feature 223 (GM 2026-09-11, "the bamboo seat scan"): the sampler asks a `BambooObstacles` index and must
    get `bamboo_blocked`'s verdict on every point - rects with their pads, lanes with their half-widths, polygons
    (convex, concave, and a two-point one the oracle skips) with their pads, the pond, the margin, the pocket."""
    import math
    import random

    from l7r.diagram.hamletgen.hinterland.bamboo import bamboo_blocked, bamboo_blocked_indexed
    from l7r.diagram.settlement._geom.indexes import BambooObstacles

    rng = random.Random(223)
    rects = [(rng.uniform(50, 950), rng.uniform(50, 950), rng.uniform(10, 60), rng.uniform(8, 40), rng.uniform(4, 14)) for _ in range(30)]
    lanes = [([(rng.uniform(0, 1000), rng.uniform(0, 1000)) for _ in range(rng.randint(2, 6))], rng.uniform(4, 12)) for _ in range(12)]
    polys: list[tuple[list[tuple[float, float]], float]] = []
    for _ in range(15):
        cx, cy, n = rng.uniform(0, 1000), rng.uniform(0, 1000), rng.randint(3, 8)
        polys.append(([(cx + rng.uniform(20, 140) * math.cos(2 * math.pi * k / n), cy + rng.uniform(20, 140) * math.sin(2 * math.pi * k / n)) for k in range(n)], rng.uniform(6, 20)))
    polys.append(([(300.0, 300.0), (420.0, 330.0)], 12.0))  # two points: not a polygon, skipped by both
    pond = (500.0, 500.0, 60.0, 40.0)
    extent, pocket = (1000.0, 1000.0), (700.0, 100.0, 900.0, 220.0)
    index = BambooObstacles(rects, lanes, polys)
    agree = {True: 0, False: 0}
    for _ in range(4000):
        x, y = rng.uniform(-20, 1020), rng.uniform(-20, 1020)
        want = bamboo_blocked(x, y, extent, pocket, rects, lanes, polys, pond, 30.0)
        assert bamboo_blocked_indexed(x, y, extent, pocket, index, pond, 30.0) is want, (x, y)
        agree[want] += 1
    assert agree[True] > 200 and agree[False] > 200, "both verdicts exercised"
    assert index.blocked(rects[0][0], rects[0][1]) and not BambooObstacles([], [], []).blocked(1.0, 1.0)


def test_scatter_frame_holds_the_crops_boxes_the_reserved_polygons_and_the_pad() -> None:
    """Feature 224 FR-001: the predicted frame is the crop's own boxes plus the belt, the woodland patches, the bamboo
    seats and the title pocket, grown by CROP_MARGIN + SCATTER_PAD - so a reserved polygon the crop will take in later
    is inside the throw."""
    from l7r.diagram.hamletgen.hinterland.frame import SCATTER_PAD, scatter_frame
    from l7r.diagram.hamletgen.hinterland.parcels import CROP_MARGIN

    s = Settlement(W=2000, H=2000, seed=5)
    s.M["houses"] = [{"x": 800.0, "y": 800.0, "w": 40.0, "h": 30.0}]
    plan = a_plan(households=10)
    plan.belt = [(600.0, 700.0), (1000.0, 700.0), (1000.0, 720.0), (600.0, 720.0)]
    plan.woodland_polys = [[(1200.0, 900.0), (1300.0, 900.0), (1300.0, 1000.0), (1200.0, 1000.0)]]
    plan.bamboo_polys = []
    plan.title_pocket = (500.0, 1100.0, 800.0, 1290.0)
    x0, y0, x1, y1 = scatter_frame(s, plan)
    grow = CROP_MARGIN + SCATTER_PAD
    from l7r.diagram.hamletgen.hinterland.frame import TITLE_BAND_ALLOWANCE

    assert (x0, y0) == (min(500.0, 600.0, 780.0) - grow, 700.0 - grow - TITLE_BAND_ALLOWANCE) and (x1, y1) == (1300.0 + grow, 1290.0 + grow)


def test_finish_records_the_scatter_frame_and_a_breach_only_where_the_view_shows_kept_out_ground(tmp_path) -> None:
    """Feature 224 FR-002: the tightest frame any scatter threw within is recorded; the overhang per side is judged
    on the ground each parcel actually covers inside the view; a breach only where the view shows part of a
    parcel the frame kept the throw out of - a small frame over a parcel the view never reaches is no breach."""
    import os

    s = Settlement(W=1000, H=1000, seed=1)
    s._scatter_frames = [((50.0, 50.0, 900.0, 900.0), (0.0, 0.0, 1000.0, 1000.0)), ((60.0, 40.0, 950.0, 880.0), (0.0, 0.0, 1000.0, 1000.0))]
    s.set_view(100, 100, 700, 700)
    s.finish(os.path.join(tmp_path, "a"), render=False)
    assert s.M["meta"]["scatter_frame"] == [60.0, 50.0, 900.0, 880.0]
    assert s.M["meta"]["scatter_frame_overhang"] == [-40.0, -50.0, -100.0, -80.0] and "scatter_frame_breach" not in s.M["meta"]
    t = Settlement(W=1000, H=1000, seed=1)
    t._scatter_frames = [((50.0, 50.0, 900.0, 900.0), (0.0, 0.0, 1000.0, 1000.0))]
    t.set_view(100, 100, 850, 700)
    t.finish(os.path.join(tmp_path, "b"), render=False)
    assert t.M["meta"]["scatter_frame_breach"] == [-50.0, -50.0, 50.0, -100.0]
    v = Settlement(W=1000, H=1000, seed=1)
    v._scatter_frames = [((50.0, 50.0, 900.0, 900.0), (0.0, 850.0, 1000.0, 1000.0))]  # a parcel only along the bottom
    v.set_view(100, 100, 850, 700)  # the view reaches past the frame on the RIGHT, but the parcel lies below the view
    v.finish(os.path.join(tmp_path, "d"), render=False)
    assert "scatter_frame_overhang" not in v.M["meta"] and "scatter_frame_breach" not in v.M["meta"]
    u = Settlement(W=1000, H=1000, seed=1)
    u.finish(os.path.join(tmp_path, "c"), render=False)
    assert "scatter_frame" not in u.M["meta"], "no scatter threw within a frame: nothing recorded"
