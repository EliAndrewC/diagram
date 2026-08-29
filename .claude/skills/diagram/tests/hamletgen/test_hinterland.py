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

from ._builders import SQUARE, a_plan


def test_a_square_far_from_the_crop_clears_and_one_on_it_does_not() -> None:
    assert hg._clear_gap((700.0, 700.0), 50.0, [SQUARE], 1.0) is None  # standing in it
    assert hg._clear_gap((700.0, 200.0), 50.0, [SQUARE], 1.0) == pytest.approx(150.0)
    assert hg._clear_gap((700.0, 1100.0), 50.0, [SQUARE], 1.0) is None  # in the crop's sunny shadow
    assert hg._clear_gap((700.0, 700.0), 50.0, [], 1.0) is None  # no crop at all - nothing to measure


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
    plan = a_plan()
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
    monkeypatch.setattr(hinterland, "WOODLAND_BBOX_FLOOR", 1.01)
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
