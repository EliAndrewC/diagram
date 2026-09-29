"""Unit tests for the houses, their appurtenances, and the wells (`hamletgen/homesteads.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import contextlib
import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.homesteads.capacity import SiteRefused
from l7r.diagram.hamletgen.homesteads.fixtures import nearer_own_house
from l7r.diagram.settlement import Settlement

from ._builders import SQUARE, a_plan


@pytest.mark.parametrize(("households", "wells"), [(10, 2), (12, 2), (15, 2), (20, 3)])
def test_wells_are_one_per_six_households_or_so(households: int, wells: int) -> None:
    """Inside `wells_sized_to_population`'s 2-20 households-per-well band at hamlet scale."""
    got = hg.well_target(households)
    assert got == wells
    assert 2 <= households / got <= 20


def test_a_tiny_hamlet_still_keeps_one_well() -> None:
    assert hg.well_target(1) == 1


# A 60 x 26 house at (1000, 1000), and two far houses that set the lattice's origin (min x 988, min y 988) so a
# lattice point falls 110 px due north of it - 13 px of its depth leaves that seat's wall gap at 97 px.
_WELL_HOUSES = [
    {"x": 1000.0, "y": 1000.0, "w": 60.0, "h": 26.0, "rot": 0.0},
    {"x": 988.0, "y": 1400.0, "w": 60.0, "h": 26.0, "rot": 0.0},
    {"x": 1400.0, "y": 988.0, "w": 60.0, "h": 26.0, "rot": 0.0},
]


def _only_seat(sx: float, sy: float, open_seat: tuple[float, float] | None = None) -> object:
    """A settlement whose engine allows a wellhead at (sx, sy) alone, and whose `open_seat` answers `open_seat`."""
    from types import SimpleNamespace

    return SimpleNamespace(well_at=lambda x, y: abs(x - sx) < 0.5 and abs(y - sy) < 0.5, open_seat=lambda *_a, **_k: open_seat, M={})


def test_a_well_is_held_to_the_wall_gap_the_test_reads_not_to_a_center_distance() -> None:
    """Feature 287 T04 (FR-003, homes H09): `place_wells` and the finished-map test read ONE predicate,
    `well_gap_to_dwellings` - the gap to the nearest dwelling's drawn wall, at most 95 px. The constructed case is where
    the two used to disagree: a lattice seat 110 px from a 26 px-deep house's CENTER, inside the old rungs' 112 px, but
    97 px from its wall. It is refused - on the lattice, by the rescue ring and at the last resort alike, which is
    handed the same seat - and the hamlet digs no well there. A seat the same center distance off the house's long
    end (wall 80 px off) is taken, and so is a last-resort seat among the doors."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.homesteads.wells import WELL_AMONG_DWELLINGS_PX, well_gap_to_dwellings

    plan = SimpleNamespace(spec=SimpleNamespace(households=6), ftpx=1.0)
    north = (1000.0, 890.0)
    assert math.hypot(north[0] - 1000.0, north[1] - 1000.0) <= 112.0, "inside the old rungs' center distance"
    assert well_gap_to_dwellings(_WELL_HOUSES, *north) == pytest.approx(97.0), "and 97 px from its wall"
    assert WELL_AMONG_DWELLINGS_PX < 97.0, "past the wall gap"
    assert hg.place_wells(_only_seat(*north, open_seat=north), plan, _WELL_HOUSES) == 0  # type: ignore[arg-type]

    east = (1110.0, 1000.0)  # the same 110 px from the center, off the long end: the wall is 80 px away
    assert well_gap_to_dwellings(_WELL_HOUSES, *east) == pytest.approx(80.0)
    assert hg.place_wells(_only_seat(*east), plan, _WELL_HOUSES) == 1  # type: ignore[arg-type]

    door = (1001.5, 960.0)  # off the lattice: with no rescue and no last resort (feature 287, H10-H12), nothing seeks it
    assert hg.place_wells(_only_seat(*door, open_seat=door), plan, _WELL_HOUSES) == 0  # type: ignore[arg-type]
    pocketed = [{**_WELL_HOUSES[0], "well_pocket": [1000.0, 1040.0]}, *_WELL_HOUSES[1:]]
    wells: list[tuple[float, float]] = []
    fake = _only_seat(*door)
    fake.well = lambda x, y: wells.append((x, y))  # type: ignore[attr-defined]
    assert hg.place_wells(fake, plan, pocketed) == 1 and wells == [(1000.0, 1040.0)], "...but a pocket is always drawn"  # type: ignore[arg-type]


def test_a_well_past_the_crop_is_refused_now_the_pockets_water_every_house() -> None:
    """Feature 287, homes H12: a lattice seat whose wellhead would reach past the crop's box is not drawn."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.homesteads.wells import crop_extent_added

    boxed = SimpleNamespace(_crop_boxes=lambda city: [(900.0, 1100.0, 900.0, 1100.0)])
    assert crop_extent_added(boxed, (1000.0, 1000.0), [0.0], [0.0]) == 0.0
    assert crop_extent_added(boxed, (1100.0, 1000.0), [0.0], [0.0]) == pytest.approx(12.0)
    east = (1110.0, 1000.0)
    plan = SimpleNamespace(spec=SimpleNamespace(households=6), ftpx=1.0)
    fake = _only_seat(*east)
    fake._crop_boxes = lambda city: [(950.0, 1100.0, 950.0, 1450.0)]  # type: ignore[attr-defined]
    assert hg.place_wells(fake, plan, _WELL_HOUSES) == 0, "the one legal seat reaches 22 px past the box"  # type: ignore[arg-type]


def test_every_household_seated_has_a_well_pocket_or_water_within_reach() -> None:
    """Feature 287, homes H10 and H11: the first household always carries a pocket; a later one exactly when no pocket
    and no open water stands within 760 ft - so every house is watered and no settlement is wellless."""
    from l7r.diagram.settlement.rolling.lot import needs_pocket

    s = Settlement(3000, 3000, seed=3)
    s.meta(name="W", scale="hamlet", ftpx=1, toscale=True)
    assert not needs_pocket(s, 100.0, 100.0), "no seating: no pockets asked"
    s._pockets = []
    assert needs_pocket(s, 100.0, 100.0), "the first household carries one"
    s._pockets.append((100.0, 100.0))
    assert not needs_pocket(s, 700.0, 100.0), "600 ft from a pocket"
    assert needs_pocket(s, 1000.0, 100.0), "900 ft from it, and no water"
    s.M["streams"] = [{"poly": [[1000.0, 0.0], [1000.0, 200.0]], "w": 6.0}]
    assert not needs_pocket(s, 1000.0, 100.0), "open water beside it"


def test_a_seating_draws_a_well_at_every_pocket_it_laid() -> None:
    """The seat half and the draw half together: a toy hamlet's pockets are laid in the bundles (inside each envelope,
    beside the yard, among the doors) and `place_wells` draws every one."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads
    from l7r.diagram.hamletgen.homesteads.wells import WELL_AMONG_DWELLINGS_PX, well_gap_to_dwellings

    s, plan = _toy_hamlet(10)
    stage_homesteads(s, plan)
    pockets = [h for h in s.M["houses"] if h.get("well_pocket")]
    assert pockets and pockets[0] is s.M["houses"][0], "the first household carries one"
    for h in pockets:
        px, py = h["well_pocket"]
        ex, ey, ew, eh = h["geom"]["bbox"]
        assert abs(px - ex) <= ew / 2 and abs(py - ey) <= eh / 2
        assert well_gap_to_dwellings(s.M["houses"], px, py) <= WELL_AMONG_DWELLINGS_PX
    hg.place_wells(s, plan, s.M["houses"])
    drawn = {(round(w["x"], 1), round(w["y"], 1)) for w in s.M["wells"]}
    assert all((round(h["well_pocket"][0], 1), round(h["well_pocket"][1], 1)) in drawn for h in pockets)


def test_the_well_gap_reads_the_turned_wall_and_passes_over_a_derelict() -> None:
    """The predicate measures each dwelling on its drawn quad (a house turned a quarter lies along the other axis) and
    reads no abandoned house as a dwelling; with no dwelling at all, no well stands among any."""
    from l7r.diagram.hamletgen.homesteads.wells import well_gap_to_dwellings

    turned = [{"x": 1000.0, "y": 1000.0, "w": 60.0, "h": 26.0, "rot": 90.0}]
    assert well_gap_to_dwellings(turned, 1000.0, 890.0) == pytest.approx(80.0), "turned, the house's long side faces north"
    assert well_gap_to_dwellings(turned, 1000.0, 1000.0) == 0.0, "inside the footprint"
    assert well_gap_to_dwellings([{**turned[0], "kind": "abandoned"}], 1000.0, 890.0) == math.inf


def test_a_seat_on_forbidden_ground_is_refused() -> None:
    """`generate` re-rolls a stranding map with the offending ground passed as `avoid`; the seat loops
    honour it through `_seat_allowed`. Half a bundle pitch is the radius - enough to clear the pocket,
    not so much that the retry merely nudges the same steading along it."""

    class _S:
        pass

    s = _S()
    assert hg.homesteads._seat_allowed(s, 100.0, 100.0) is True  # nothing forbidden yet
    s._avoid_seats = [(100.0, 100.0)]
    assert hg.homesteads._seat_allowed(s, 100.0, 100.0) is False  # dead on the forbidden seat
    assert hg.homesteads._seat_allowed(s, 140.0, 100.0) is False  # inside half a bundle pitch
    assert hg.homesteads._seat_allowed(s, 400.0, 400.0) is True  # well clear


def test_farmstead_fixtures_roll_a_share_in_each_band_and_seat_one_of_a_kind_per_house() -> None:
    """Feature 133 T53-T59: the shares are rolled once per map inside the researched bands and declared
    for the gate; each house keeps at most one of a kind, every fixture names its house, and the
    shrine count never exceeds the share (the GM: "very rare, but notable")."""
    from l7r.diagram.hamletgen.homesteads import FIXTURE_BANDS, farmstead_fixtures
    from l7r.diagram.settlement import Settlement

    s = Settlement(W=900, H=700, seed=7)
    s.meta(name="T", scale="hamlet", ftpx=1)
    houses = [{"x": 200.0 + 110 * i, "y": 300.0 + 90 * (i % 2), "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"} for i in range(6)]
    for h in houses:
        s.M["houses"].append(dict(h))
        s.placed.append((h["x"], h["y"], h["w"], h["h"]))
    n = farmstead_fixtures(s, a_plan(), houses)
    shares = s.M["meta"]["farm_fixtures"]
    assert set(shares) == set(FIXTURE_BANDS) and all(lo <= shares[k] <= hi for k, (lo, hi) in FIXTURE_BANDS.items())
    recs = s.M["farm_fixtures"]
    assert n == len(recs) + len(s.M["persimmons"]) and n > 0
    owners = {(r["kind"], tuple(r["of"])) for r in recs}
    assert len(owners) == len(recs), "one of a kind per house"
    assert sum(r["kind"] == "shrine" for r in recs) <= max(1, round(shares["shrine"] * len(houses)))
    assert all(tuple(r["of"]) in {(h["x"], h["y"]) for h in houses} for r in recs)
    walks = sum("corridor" in r for r in recs)  # a corridor bath reserves its corridor too (269 B12)
    assert len(s.placed) == len(houses) + n + walks, "every seated fixture reserves its ground"


def test_farmstead_fixtures_honor_the_spec_floor() -> None:
    """Feature 133 T61 (GM 2026-08-27: "a min number of something which may or may not appear"): a spec'd
    floor forces the kind onto houses that lack it after the rolled pass, and declares itself in meta."""
    from l7r.diagram.hamletgen.homesteads import farmstead_fixtures
    from l7r.diagram.settlement import Settlement

    s = Settlement(W=900, H=700, seed=7)
    s.meta(name="T", scale="hamlet", ftpx=1)
    houses = [{"x": 200.0 + 110 * i, "y": 300.0 + 90 * (i % 2), "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"} for i in range(6)]
    for h in houses:
        s.M["houses"].append(dict(h))
        s.placed.append((h["x"], h["y"], h["w"], h["h"]))
    plan = a_plan()
    plan.fixtures_min = {"shrine": 2, "bath": 3}
    farmstead_fixtures(s, plan, houses)
    kinds = [r["kind"] for r in s.M["farm_fixtures"]]
    assert kinds.count("shrine") >= 2 and kinds.count("bath") >= 3
    assert s.M["meta"]["farm_fixtures_min"] == {"shrine": 2, "bath": 3}
    owners = {(r["kind"], tuple(r["of"])) for r in s.M["farm_fixtures"]}
    assert len(owners) == len(s.M["farm_fixtures"]), "the floor never doubles a house"


def test_a_fixture_no_seat_can_take_is_recorded_as_unseated(monkeypatch: pytest.MonkeyPatch) -> None:
    """The miss is RECORDED (settlement-review of Kuwabata, 2026-09-12): with every seat and every outward rung blocked,
    nothing is drawn and `meta.farm_fixtures_unseated` counts each kind that could not stand - asked directly since
    feature 276's maps stopped taking this branch on any pool roll."""
    from l7r.diagram.hamletgen.homesteads import farmstead_fixtures
    from l7r.diagram.hamletgen.homesteads import fixtures as fixtures_mod
    from l7r.diagram.settlement import Settlement

    s = Settlement(W=900, H=700, seed=7)
    s.meta(name="T", scale="hamlet", ftpx=1)
    houses = [{"x": 200.0 + 110 * i, "y": 300.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"} for i in range(4)]
    for h in houses:
        s.M["houses"].append(dict(h))
        s.placed.append((h["x"], h["y"], h["w"], h["h"]))
    monkeypatch.setattr(fixtures_mod, "_strip_blocked", lambda *a, **k: True)
    monkeypatch.setattr(fixtures_mod, "_trunk_blocked", lambda *a, **k: True)  # the yard trees seat by their own test
    assert farmstead_fixtures(s, a_plan(), houses) == 0
    missed = s.M["meta"].get("farm_fixtures_unseated") or {}
    assert missed and sum(missed.values()) > 0 and not s.M.get("farm_fixtures")


# ---- feature 145: the refusal branches of the fixture placer that no cohort seed took --------------


def _strip_settlement() -> tuple[object, object]:
    from l7r.diagram.settlement import Settlement

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="S", scale="hamlet", ftpx=1, down_deg=90)
    return s, a_plan()


def test_strip_blocked_refuses_the_canvas_edge_a_crossing_lane_and_a_drawn_crown() -> None:
    s, _plan = _strip_settlement()
    blocked = hg.homesteads._strip_blocked
    assert blocked(s, 20, 500, 30, 20, 0, 0, [], [], None, []) is True, "over the canvas edge"
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, []) is False, "open ground"
    lane = [([(500, 400), (500, 600)], 3.0)]  # a lane running THROUGH the strip, both ends outside it
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, lane) is True
    s.M["tree_crowns"] = [500.0, 500.0, 12.0]
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, []) is True, "a crown drawn two stages earlier"


def test_farmstead_fixtures_on_a_houseless_map_place_nothing() -> None:
    s, plan = _strip_settlement()
    assert hg.homesteads.farmstead_fixtures(s, plan, []) == 0


def test_roll_falls_through_to_the_last_weight() -> None:
    """A u past the weights' sum (floating-point slack) takes the last row rather than raising."""
    assert hg.homesteads._roll([("a", 0.3), ("b", 0.3)], 0.99) == "b"
    assert hg.homesteads._roll([("a", 0.3), ("b", 0.3)], 0.1) == "a"


def test_strip_blocked_refuses_a_lane_that_only_crosses_the_strip() -> None:
    """Feature 146: the crossing arm of `_strip_blocked` - a lane whose ENDS are both outside the strip but
    whose segment passes through it (the corner test above cannot see that one)."""
    s, _plan = _strip_settlement()
    blocked = hg.homesteads._strip_blocked
    across = [([(440.0, 500.0), (560.0, 500.0)], 1.0)]  # a hairline lane straight through, ends well clear
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, across) is True
    beside = [([(440.0, 300.0), (560.0, 300.0)], 1.0)]
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, beside) is False


def test_strip_blocked_refuses_a_dry_plot_and_a_watercourse(monkeypatch) -> None:
    """The two arms the unlock tripwire seed 47 added (a fixture on a dry plot, one on the stream) - reached by the
    cohort seeds until feature 214 packed them away, so asserted directly: a strip with a corner inside a dry hem
    plot is blocked, and so is one whose corner stands on a watercourse."""
    s, _plan = _strip_settlement()
    blocked = hg.homesteads._strip_blocked
    s.M["dry_plots"] = [{"poly": [(480.0, 480.0), (520.0, 480.0), (520.0, 520.0), (480.0, 520.0)]}]
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, []) is True, "a corner inside a dry plot"
    s.M["dry_plots"] = []
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, []) is False
    monkeypatch.setattr(s, "_on_watercourse", lambda x, y, pad=4.0, near=None: True)  # the footing passes its grid as `near` (feature 218)
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, []) is True, "a corner on the stream"


def test_trunk_blocked_refuses_the_canvas_edge_and_a_record_without_a_footprint() -> None:
    """Feature 146: two arms of the trunk test - a trunk hanging off the canvas, and a record in one of the
    scanned lists that carries no `x` at all (a synthetic entry another check keeps), which is skipped
    rather than raising."""
    s, _plan = _strip_settlement()
    blocked = hg.homesteads._trunk_blocked
    assert blocked(s, 20, 500, 10, [], [], None, []) is True, "over the canvas edge"
    s.M["persimmons"] = [{"note": "a record with no footprint at all"}]
    assert blocked(s, 500, 500, 10, [], [], None, []) is False, "the footprint-less record is skipped"
    s.M["persimmons"].append({"x": 500.0, "y": 500.0, "w": 20.0, "h": 20.0})
    assert blocked(s, 500, 500, 10, [], [], None, []) is True, "and a real one blocks"


def test_strip_blocked_sees_a_lane_that_crosses_the_strip_between_its_samples() -> None:
    """Five sample points on a 22 by 16 ft strip let a lane cross it DIAGONALLY between them (cohort
    seed 03), and `lanes_clear_of_bamboo` walks the tread's quarter-points, so the gate saw what the
    placer did not. The tread is therefore tested as a segment against the strip's own edges."""
    from l7r.diagram.hamletgen.homesteads import _strip_blocked

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    # The five samples are the four corners AND the center, so a tread through the middle is caught a
    # line earlier. This one clips the strip between them: 2.2 px from the nearest sample, well past
    # the tread's own half-width, and still straight through the strip.
    clipping = [([(480.0, 505.0), (520.0, 485.0)], 1.0)]
    assert _strip_blocked(s, 500.0, 500.0, 22.0, 16.0, 900.0, 900.0, [], [], None, clipping)
    assert not _strip_blocked(s, 200.0, 800.0, 22.0, 16.0, 900.0, 900.0, [], [], None, clipping)


def test_a_woodpile_stacks_against_the_kura_when_the_shed_is_not_on_the_north_side() -> None:
    """The stack stands against whichever wall is free. Which wall that is depends on `shed_side`, and
    every live hamlet rolls the same side - so the other seat list had never been built."""
    from l7r.diagram.hamletgen.homesteads import farmstead_fixtures

    plan = a_plan()
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=6, down_deg=90, water_flow=90)
    houses = [{"x": 700.0, "y": 700.0, "w": 46.0, "h": 28.0, "rot": 0.0, "kind": "plain", "shed_side": "S", "wealth": 1.0}]
    farmstead_fixtures(s, plan, houses)
    assert s.M["farm_fixtures"], "the steading's fixtures are seated round it"
    assert all(abs(f["x"] - 700.0) < 200 and abs(f["y"] - 700.0) < 200 for f in s.M["farm_fixtures"])


def test_a_linear_hamlet_strings_its_houses_along_the_connector() -> None:
    """The `linear` settlement form is attested and implemented but pinned off (`SETTLEMENT_FORMS`), so
    the arm that fronts the CONNECTOR - the only way on the map that predates the houses - has never
    rolled. `lane_frontage` skips the connector for exactly the reason this form wants it: fronting it
    strings the hamlet along the road instead of nucleating it, which is this archetype."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads  # through the MODULE: a stage is not package surface

    # TEN HOUSEHOLDS, THE FLOOR OF THE HAMLET BAND (feature 158): the arm under test is the frontage
    # loop, which does not care how many houses it strings - and every household is a seat search.
    # Fifteen cost 4-5 s of every run in all three tiers; ten cost two thirds of that and prove the
    # same thing. (Nine is not available: `HamletSpec` refuses anything outside 10-20.)
    for form in ("nucleated", "linear"):
        plan = a_plan(households=10)
        plan.seat = hg.seat_cluster(plan)
        plan.settlement_form = form
        s = Settlement(1400, 1400, seed=3)
        s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
        s.field_polys.append(list(plan.envelope))
        # the connector has to BE there for the linear form to string anything along it - it is the one
        # way on the map that predates the houses, which is the whole premise of the archetype
        cx_, cy_ = float(plan.seat["cx"]), float(plan.seat["cy"])
        s.M["lanes"] = [{"pts": [[cx_ - 400, cy_], [cx_ + 400, cy_]], "w": 6, "connector": True}]
        stage_homesteads(s, plan)
        assert len(s.M["houses"]) == 10, f"{form}: every household seated"

    # ...and the frontage loop STOPS when the households run out rather than filling the whole
    # connector: the same plan, with the ask cut to three, seats three and leaves the rest of the
    # road bare. A row village is as long as its households, not as long as its road.
    spec = hg.HamletSpec(name="Row", seed=3, households=10, down_deg=90.0, windward="N")
    plan = hg.plan_site(spec)
    plan.envelope = list(SQUARE)
    plan.seat = hg.seat_cluster(plan)
    plan.settlement_form = "linear"
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    s.field_polys.append(list(plan.envelope))
    cx_, cy_ = float(plan.seat["cx"]), float(plan.seat["cy"])
    s.M["lanes"] = [{"pts": [[cx_ - 620, cy_], [cx_ + 620, cy_]], "w": 6, "connector": True}]
    stage_homesteads(s, plan)
    assert len(s.M["houses"]) == 10


def test_nearer_own_house_with_no_other_houses_is_unambiguously_its_owners() -> None:
    """Feature 174: the no-neighbors branch, lifted out to take two tuples rather than a settlement.

    Its own docstring says that is why it exists. With nobody else to be nearer to, the seat scores
    rank 0 and a NEGATIVE margin - the sign convention the sort depends on - so the margin's sign is
    asserted, not just the rank.
    """
    rank, dmine, margin = nearer_own_house((30.0, 40.0, 0.0, 0.0), 0.0, 0.0, 1.0, 0.0, ())
    assert rank == 0
    assert dmine == pytest.approx(50.0), "3-4-5 from its own house"
    assert margin == pytest.approx(-50.0), "negative: unambiguously this house's"


def test_a_trunk_on_a_stream_is_refused_by_the_water_arm_alone() -> None:
    """`_trunk_blocked`'s water arm reached through `Footing` (feature 220), on a sheet that carries NOTHING but the
    stream - so no earlier arm (a paddy ring, a dry plot, a lane) can be the one that refused it."""
    from l7r.diagram.hamletgen.homesteads import _trunk_blocked
    from l7r.diagram.settlement import Settlement

    s = Settlement(1400, 1400, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1, down_deg=90)
    s.M["streams"] = [{"poly": [[100.0, 700.0], [1300.0, 700.0]], "w": 60}]
    assert _trunk_blocked(s, 700.0, 700.0, 20.0, [], [], None, []) is True
    assert _trunk_blocked(s, 700.0, 200.0, 20.0, [], [], None, []) is False
    # ...the PADDY arm: a trunk within 6 ft of a paddy ring, nothing else on the sheet (no pool roll reaches it
    # since the homesteads turned as one piece on 2026-09-26, so it is held here)
    s.M["streams"] = []
    paddy = [(650.0, 400.0), (750.0, 400.0), (750.0, 500.0), (650.0, 500.0)]
    assert _trunk_blocked(s, 700.0, 390.0, 10.0, [paddy], [], None, []) is True
    assert _trunk_blocked(s, 700.0, 300.0, 10.0, [paddy], [], None, []) is False
    # ...and the DRY-PLOT arm the same way: a trunk corner standing in a dry plot, nothing else on the sheet
    s.M["streams"] = []
    s.M["dry_plots"] = [{"poly": [(650.0, 150.0), (750.0, 150.0), (750.0, 250.0), (650.0, 250.0)]}]
    assert _trunk_blocked(s, 700.0, 200.0, 20.0, [], [], None, []) is True
    assert _trunk_blocked(s, 700.0, 700.0, 20.0, [], [], None, []) is False


def test_a_fixture_across_the_brook_from_its_house_is_across() -> None:
    """Feature 261 FR-013: the line from the house to a fixture's seat crossing a stream puts the seat on the far
    bank; a seat on the house's own bank, or a sheet with no stream, is not."""
    from l7r.diagram.hamletgen.homesteads.fixtures import across_the_brook

    s = Settlement(1400, 1400, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1, down_deg=90)
    assert across_the_brook(s, (700.0, 600.0), (700.0, 800.0)) is False
    s.M["streams"] = [{"poly": [[100.0, 700.0], [1300.0, 700.0]], "w": 9}]
    assert across_the_brook(s, (700.0, 600.0), (700.0, 800.0)) is True
    assert across_the_brook(s, (700.0, 600.0), (760.0, 640.0)) is False


def test_a_fixture_beyond_a_lane_from_its_house_is_across() -> None:
    """Settlement-review of Mizuguchi (feature 261): a lane between the house and the seat puts the seat outside the
    plot; a seat on the house's side of every lane is not across."""
    from l7r.diagram.hamletgen.homesteads.fixtures import across_a_lane

    lane = ([(100.0, 700.0), (500.0, 700.0), (1300.0, 700.0)], 4.5)
    assert across_a_lane([lane], (700.0, 600.0), (700.0, 720.0)) is True
    assert across_a_lane([lane], (700.0, 600.0), (740.0, 660.0)) is False
    assert across_a_lane([], (700.0, 600.0), (700.0, 720.0)) is False


def test_the_shrine_budget_refuses_a_second_house_that_rolls_one(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`farmstead_fixtures`: the shrine share is a CEILING - "very rare, but notable" - so once the budget the share
    allows is spent, a later house that rolls a shrine gets none, whatever its roll says."""
    from l7r.diagram.hamletgen.homesteads import fixtures as fx
    from l7r.diagram.settlement import Settlement

    monkeypatch.setitem(fx.FIXTURE_BANDS, "shrine", (0.5, 0.5))
    s = Settlement(W=1200, H=700, seed=7)
    s.meta(name="T", scale="hamlet", ftpx=1)
    passing = [(x, y) for x in range(150, 1100, 110) for y in (250.0, 400.0) if s._hjit(float(x), y, fx._SALT["shrine"]) < 0.5]
    assert len(passing) >= 3
    houses = [{"x": float(x), "y": float(y), "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"} for x, y in passing[:3]] + [
        {"x": 1150.0, "y": 600.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"}
    ]
    for h in houses:
        s.M["houses"].append(dict(h))
        s.placed.append((h["x"], h["y"], h["w"], h["h"]))
    fx.farmstead_fixtures(s, a_plan(), houses)
    shrines = [r for r in s.M["farm_fixtures"] if r["kind"] == "shrine"]
    assert len(shrines) == 2, "the share allows two of four; the third house that rolled one is refused"


def test_a_shrine_with_no_seat_passes_to_the_next_house_with_room(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`farmstead_fixtures` (settlement-review of Mizuguchi, feature 261): the one house that rolled the map's shrine has
    every seat beyond a lane, so the shrine goes to the next house with room rather than off the map - and where no house
    has room, the miss is recorded once."""
    from l7r.diagram.hamletgen.homesteads import fixtures as fx
    from l7r.diagram.settlement import Settlement

    monkeypatch.setitem(fx.FIXTURE_BANDS, "shrine", (0.5, 0.5))
    probe = Settlement(W=1200, H=700, seed=7)
    spots = [(float(x), y) for x in range(150, 1100, 110) for y in (250.0, 400.0)]
    rolls = next(p for p in spots if probe._hjit(p[0], p[1], fx._SALT["shrine"]) < 0.5)
    other = next(p for p in spots if probe._hjit(p[0], p[1], fx._SALT["shrine"]) >= 0.5 and abs(p[0] - rolls[0]) > 200)

    def run(boxed):  # type: ignore[no-untyped-def]
        s = Settlement(W=1200, H=700, seed=7)
        s.meta(name="T", scale="hamlet", ftpx=1)
        houses = [{"x": x, "y": y, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"} for x, y in (rolls, other)]
        for h in houses:
            s.M["houses"].append(dict(h))
            s.placed.append((h["x"], h["y"], h["w"], h["h"]))
        monkeypatch.setattr(fx, "across_a_lane", lambda lanes, house, seat: house in boxed)
        fx.farmstead_fixtures(s, a_plan(), houses)
        return s

    s = run({rolls})
    shrines = [r for r in s.M["farm_fixtures"] if r["kind"] == "shrine"]
    assert [tuple(r["of"]) for r in shrines] == [(round(other[0], 1), round(other[1], 1))], "passed to the house with room"
    assert "shrine" not in (s.M["meta"].get("farm_fixtures_unseated") or {})
    s = run({rolls, other})
    assert not [r for r in s.M["farm_fixtures"] if r["kind"] == "shrine"]
    assert s.M["meta"]["farm_fixtures_unseated"]["shrine"] == 1, "no house had room: one miss"


def _toy_hamlet(households: int, seed: int = 3):  # type: ignore[no-untyped-def]
    """The linear toy's setup, for the stage's own branches: a square field, a seat band, the connector."""
    plan = a_plan(households=households)
    plan.seat = hg.seat_cluster(plan)
    plan.settlement_form = "nucleated"
    s = Settlement(1400, 1400, seed=seed)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=households, down_deg=90, water_flow=90, nucleated=True)
    # THE PLACER'S OWN SWITCH, as the generator sets it (`hamletgen/water/skeleton.py`): `meta(nucleated=True)` only
    # RECORDS the form, and without this the toy's homesteads ran the DISPERSED spiral - a path no pool hamlet uses
    # (found by feature 276's plan review: the rescue scenario's grove rejections could only come from a dispersed bundle).
    s._nucleated = plan.settlement_form == "nucleated"
    s.field_polys.append(list(plan.envelope))
    cx_, cy_ = float(plan.seat["cx"]), float(plan.seat["cy"])
    s.M["lanes"] = [{"pts": [[cx_ - 400, cy_], [cx_ + 400, cy_]], "w": 6, "connector": True}]
    return s, plan


def test_the_front_row_stops_at_its_share_and_the_ranks_seat_the_rest() -> None:
    """Feature 227 D8: the row takes about sqrt(N x A) houses - here fewer than the chain could seat - and stops;
    the ranks behind seat the rest."""
    from l7r.diagram.hamletgen.consts import CLUSTER_DRAWN_ASPECT
    from l7r.diagram.hamletgen.homesteads import stage_homesteads

    s, plan = _toy_hamlet(10)
    plan.cluster_shape = "round"  # the tightest band: the row's share is the floor of six, fewer than the chain could seat
    stage_homesteads(s, plan)
    lo, hi = CLUSTER_DRAWN_ASPECT["round"]
    cap = min(10, max(6, round(math.sqrt(10 * (lo + hi)))))
    assert cap == 6
    ss = s.M["meta"]["seat_search"]
    assert len(s.M["houses"]) == 10 and ss["front"] == cap and ss["rounds"] >= 1


def test_a_quota_the_ranks_cannot_seat_reaches_the_rescue_rounds() -> None:
    """The rescue rounds (five to seven) run only while the quota is short after four rounds of ranks; their cloud
    seeds a wider band and skips the seeds outside it. Twenty households on the toy's square field is such a quota."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads

    s, plan = _toy_hamlet(20)
    # the ground beyond 260 ft of the seat is no-build, so the ranks run out of room and the rescue's wider cloud
    # throws seeds the band refuses
    cx_, cy_ = float(plan.seat["cx"]), float(plan.seat["cy"])
    s.block_polys.append([(cx_ - 2000.0, cy_ - 2000.0), (cx_ + 2000.0, cy_ - 2000.0), (cx_ + 2000.0, cy_ - 260.0), (cx_ - 2000.0, cy_ - 260.0)])
    s.block_polys.append([(cx_ - 2000.0, cy_ + 260.0), (cx_ + 2000.0, cy_ + 260.0), (cx_ + 2000.0, cy_ + 2000.0), (cx_ - 2000.0, cy_ + 2000.0)])
    plan.seat["ladder"] = []  # this margin alone: the refusal below is the chosen margin's
    # ...AND A QUOTA THE GROUND CANNOT HOLD IS REFUSED, NEVER SHIPPED SHORT (feature 287, homes H14 and plan D2): the
    # rescue and then the exhaustive pass over every free point within reach ran, and still the ground was full
    with pytest.raises(SiteRefused, match="no margin seats all 20 households"):
        stage_homesteads(s, plan)
    assert s._seat_search["rounds"] >= 5, "the rescue ran"
    assert s._seat_search["exhaustive_offered"] > 0, "...and the exhaustive pass after it"
    assert len(s.M["houses"]) < 20, "the ground, not the search, was the limit"


def test_a_cluster_standing_off_its_field_gets_the_spur_to_it() -> None:
    """`stage_track`'s field spur is laid when the path from the cluster's edge to the field is longer than 20 ft; the
    pool's clusters front the paddy at the wall rule now (feature 227), so no shipped map lays one - a cluster seated
    three hundred feet back does."""
    from l7r.diagram.hamletgen.ways import stage_track

    s, plan = _toy_hamlet(10)
    # A DISPERSED cluster, said so (feature 276): the seats three hundred feet back fall off the toy's canvas, and it
    # was the dispersed spiral - which the toy ran by accident until `_toy_hamlet` set the placer's own switch -
    # that found room within reach of them. The spur is a property of the track, whatever form stands back there.
    s._nucleated = False
    cx_, cy_ = float(plan.seat["cx"]), float(plan.seat["cy"])
    ox, oy = plan.seat["out"]
    n = 0
    for k in range(-2, 3):
        ax, ay = plan.seat["along"]
        if s.try_place(cx_ + ax * 110 * k + ox * 300, cy_ + ay * 110 * k + oy * 300, "plain"):
            n += 1
    assert n >= 3
    stage_track(s, plan)
    spurs = [ln for ln in s.M["lanes"] if ln.get("w") == 5 and not ln.get("connector") and ln.get("worn")]
    assert spurs, "a worn width-5 way besides the connector: the spur to the field"


def test_a_rank_round_that_seats_nothing_grows_the_cluster_along_the_field() -> None:
    """Feature 227 D8: the seats a pitch beyond each end of the rank are offered ONLY in a round that seated nothing
    behind - so a cluster whose back is refused grows along the field instead of stopping. Here the ground more than
    40 px out from the row is no-build, so every seat at a rank's depth is refused and the ends are the only ones
    left; the houses past the front row's own count can therefore only have come from them."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads

    s, plan = _toy_hamlet(12)
    ax, ay = plan.seat["along"]
    ox, oy = plan.seat["out"]
    cx, cy = float(plan.seat["cx"]), float(plan.seat["cy"])
    back = [
        (cx + ox * 40 - ax * 5000, cy + oy * 40 - ay * 5000),
        (cx + ox * 40 + ax * 5000, cy + oy * 40 + ay * 5000),
        (cx + ox * 5000 + ax * 5000, cy + oy * 5000 + ay * 5000),
        (cx + ox * 5000 - ax * 5000, cy + oy * 5000 - ay * 5000),
    ]
    s.block_polys.append(back)
    stage_homesteads(s, plan)
    ss = s.M["meta"]["seat_search"]
    assert ss["rounds"] >= 1, "the ranks ran"
    assert len(s.M["houses"]) > ss["front"], "the only seats left were the ends, and the cluster took them"


def test_the_yard_ring_seats_a_fixture_at_every_wall_of_its_own_house() -> None:
    """`yard_ring` (feature 261): the last resort of a fixture whose recorded seats are all refused - the back wall at three
    points, each flank at three heights turned along it, and the front corners - each a wall gap and half a depth out."""
    from l7r.diagram.hamletgen.homesteads.fixtures import yard_ring

    ring = yard_ring(40.0, 20.0, 3.0, 6.0, 4.0)
    assert len(ring) == 11
    assert all(ly == -(10.0 + 3.0 + 2.0) and (cw, ch) == (6.0, 4.0) for _lx, ly, cw, ch in ring[:3]), "the back wall, along it"
    assert all(abs(lx) == 20.0 + 3.0 + 2.0 and (cw, ch) == (4.0, 6.0) for lx, _ly, cw, ch in ring[3:9]), "the flanks, turned"
    assert all(ly == 10.0 + 3.0 + 2.0 for _lx, ly, _cw, _ch in ring[9:]), "the front corners"


def test_a_fixture_with_no_seat_anywhere_is_recorded_persimmons_included(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`farmstead_fixtures` (feature 261): every seat refused - here by a lane between the house and every seat - leaves
    each rolled kind recorded in `meta.farm_fixtures_unseated`, the persimmon too, which used to vanish unrecorded."""
    from l7r.diagram.hamletgen.homesteads import fixtures as fx
    from l7r.diagram.settlement import Settlement

    for kind in fx.FIXTURE_BANDS:
        monkeypatch.setitem(fx.FIXTURE_BANDS, kind, (1.0, 1.0))
    s = Settlement(W=1200, H=700, seed=7)
    s.meta(name="T", scale="hamlet", ftpx=1)
    houses = [{"x": 600.0, "y": 350.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"}]
    s.M["houses"].append(dict(houses[0]))
    s.placed.append((600.0, 350.0, 46.0, 28.0))
    monkeypatch.setattr(fx, "across_a_lane", lambda lanes, house, seat: True)
    fx.farmstead_fixtures(s, a_plan(), houses)
    missed = s.M["meta"]["farm_fixtures_unseated"]
    assert missed.get("persimmon") == 1 and missed.get("privy") == 1 and missed.get("shrine") == 1
    assert not s.M.get("persimmons") and not s.M.get("farm_fixtures")


def test_the_yard_ring_looks_past_the_homestead_bundles(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`farmstead_fixtures` (feature 261, spec-fidelity of round 6fefdcdf): a bundle box is a packing reservation, so the yard
    ring is not refused by one - the house's own offset by its gardens, or a neighbor's over open ground - while the
    recorded seats still are."""
    from l7r.diagram.hamletgen.homesteads import fixtures as fx
    from l7r.diagram.settlement import Settlement

    monkeypatch.setitem(fx.FIXTURE_BANDS, "coop", (1.0, 1.0))
    for kind in ("privy", "manure", "bath", "woodpile", "shrine", "persimmon"):
        monkeypatch.setitem(fx.FIXTURE_BANDS, kind, (0.0, 0.0))
    s = Settlement(W=1200, H=700, seed=7)
    s.meta(name="T", scale="hamlet", ftpx=1)
    houses = [{"x": 600.0, "y": 350.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"}]
    s.M["houses"].append(dict(houses[0]))
    s.placed += [(600.0, 350.0, 46.0, 28.0), (590.0, 360.0, 140.0, 120.0)]  # the house, and its bundle offset off-center
    fx.farmstead_fixtures(s, a_plan(), houses)
    coops = [r for r in s.M.get("farm_fixtures", []) if r["kind"] == "coop"]
    assert len(coops) == 1 and not (s.M["meta"].get("farm_fixtures_unseated") or {}), "seated by the ring, through the bundle"


def test_an_accretion_hamlets_ranks_stand_off_their_lines_and_a_planned_ones_do_not() -> None:
    """`stage_homesteads` (feature 261 D22): an `alleys` hamlet's rank seats take the depth jitter, so the ranks behind the
    front row are not all on one line; a `back_lane` hamlet seated the same way keeps its ranks exact. Both seat every
    household."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads

    seats = {}
    for form in ("alleys", "back_lane"):
        s, plan = _toy_hamlet(14)
        plan.lane_web = form
        stage_homesteads(s, plan)
        assert len(s.M["houses"]) == 14
        seats[form] = {(round(h["x"], 1), round(h["y"], 1)) for h in s.M["houses"]}
    moved = seats["alleys"] - seats["back_lane"]
    assert moved and len(moved) < 14, "the ranks' seats moved off their lines; the front row did not"


# ---- feature 276 FR-003 (plan D9): the free ground proposes, the fit test decides ----------------------------------


def _seats(s):  # type: ignore[no-untyped-def]
    return [(round(h["x"], 3), round(h["y"], 3), tuple(round(v, 3) for v in (h.get("geom") or {}).get("bbox", ()))) for h in s.M["houses"]]


def _rescue(form):  # type: ignore[no-untyped-def]
    s, plan = _toy_hamlet(20)
    s._nucleated = form == "nucleated"
    cx_, cy_ = float(plan.seat["cx"]), float(plan.seat["cy"])
    s.block_polys.append([(cx_ - 2000.0, cy_ - 2000.0), (cx_ + 2000.0, cy_ - 2000.0), (cx_ + 2000.0, cy_ - 260.0), (cx_ - 2000.0, cy_ - 260.0)])
    s.block_polys.append([(cx_ - 2000.0, cy_ + 260.0), (cx_ + 2000.0, cy_ + 260.0), (cx_ + 2000.0, cy_ + 2000.0), (cx_ - 2000.0, cy_ + 2000.0)])
    plan.seat["ladder"] = []  # the chosen margin alone, so its seats stand when the site is refused (feature 287, D2)
    return s, plan


@pytest.mark.parametrize("form", ["nucleated", "dispersed"])
@pytest.mark.parametrize("scenario", ["rescue", "open"])
def test_the_free_ground_changes_no_seat(form: str, scenario: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """The same houses, at the same seats, with the index asked first and with it switched off entirely."""
    from l7r.diagram.hamletgen.homesteads import boundary, stage_homesteads
    from l7r.diagram.settlement import Settlement

    def roll():  # type: ignore[no-untyped-def]
        s, plan = _rescue(form) if scenario == "rescue" else _toy_hamlet(15)
        s._nucleated = form == "nucleated"
        with contextlib.suppress(SiteRefused):  # the rescue ground cannot hold its quota (D2); the seats it took are compared all the same
            stage_homesteads(s, plan)
        return _seats(s)

    with_index = roll()
    monkeypatch.setattr(boundary.FreeGround, "rect_refused", lambda self, rect: False)
    monkeypatch.setattr(Settlement, "_seat_refused", lambda self, x, y, hw, hh: False)
    monkeypatch.setattr(Settlement, "_bundle_refused", lambda self, geom: False)
    without = roll()
    assert with_index == without and len(with_index) >= 10


def test_a_side_is_not_dropped_for_ground_the_loop_never_judges() -> None:
    """Plan review 2's case: on the nucleated path a side's own box is ground-tested only when the whole envelope was
    refused. With the envelope clear, an index claiming EVERY other box as taken - each side's own sample points
    included - must leave the seat exactly as it is with no index at all."""
    from l7r.diagram.settlement import Settlement

    class RefusesAllButTheEnvelope:
        def __init__(self, env):  # type: ignore[no-untyped-def]
            self.env = env

        def rect_refused(self, rect):  # type: ignore[no-untyped-def]
            return rect != self.env

    seated = 0
    for x, y in ((300.0, 300.0), (620.0, 410.0), (900.0, 760.0)):
        s = Settlement(1400, 1400, seed=5)
        s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=15, down_deg=90, water_flow=90, nucleated=True)
        s._nucleated = True
        plain = s._place_bundle_nucleated(x, y, 30.0, 20.0, False)
        assert s._envelope_blocked(s._bundle_envelope(x, y, 30.0, 20.0, False)) is None, "the case: the whole envelope clear"
        s._free_ground = RefusesAllButTheEnvelope(s._bundle_envelope(x, y, 30.0, 20.0, False))
        assert s._place_bundle_nucleated(x, y, 30.0, 20.0, False) == plain
        seated += plain is not None
    assert seated == 3, "non-vacuity: each seat was taken"


def test_every_surely_taken_cell_is_ground_the_fit_test_refuses() -> None:
    """FreeGround's exactness, asked of the real boundary on the toy: any point inside a taken cell is refused by the
    nine-point ground test itself (a zero-size rectangle there is nine copies of the point)."""
    import random

    from l7r.diagram.hamletgen.homesteads.boundary import install_site_boundary

    s, plan = _rescue("nucleated")
    install_site_boundary(s, plan)
    fg = s._free_ground
    assert len(fg.taken) > 100, "non-vacuity: the no-build walls and the field make taken ground"
    r = random.Random(276)
    for i, j in r.sample(sorted(fg.taken), 300):
        px, py = fg.x0 + (i + r.random()) * fg.cell, fg.y0 + (j + r.random()) * fg.cell
        assert s._site_blocks_rect((px, py, 0.0, 0.0)), (px, py)


def test_the_front_row_loop_stops_once_its_share_is_seated(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`stage_homesteads`: the row's loop breaks when its share is placed, however many seats the chain still offers - here
    the chain's seats are offered twice over, and the row still takes exactly its share."""
    import math

    from l7r.diagram.hamletgen.consts import CLUSTER_DRAWN_ASPECT
    from l7r.diagram.hamletgen.homesteads import stage_homesteads
    from l7r.diagram.hamletgen.homesteads import stages as st

    real = st.front_row
    monkeypatch.setattr(st, "front_row", lambda *a, **k: (lambda seats: seats + seats)(list(real(*a, **k))))
    s, plan = _toy_hamlet(10)
    plan.cluster_shape = "round"
    stage_homesteads(s, plan)
    lo, hi = CLUSTER_DRAWN_ASPECT["round"]
    assert s.M["meta"]["seat_search"]["front"] == min(10, max(6, round(math.sqrt(10 * (lo + hi)))))


def _one_kind(monkeypatch: pytest.MonkeyPatch, fx: object, keep: tuple[str, ...]) -> None:
    for kind in ("privy", "manure", "bath", "coop", "woodpile", "shrine", "persimmon"):
        monkeypatch.setitem(fx.FIXTURE_BANDS, kind, (1.0, 1.0) if kind in keep else (0.0, 0.0))  # type: ignore[attr-defined]


def test_the_privy_seat_weights_are_rolled_per_hamlet_over_the_four_attested_seats() -> None:
    """269 B10 (research/homesteads/260): four attested seats, the weights re-rolled per hamlet from the seed and summing to one."""
    from l7r.diagram.hamletgen.homesteads.fixtures import _PRIVY_SEATS, privy_seat_weights

    a, b = privy_seat_weights(3), privy_seat_weights(4)
    assert [k for k, _ in a] == [k for k, _ in _PRIVY_SEATS] == ["yard", "front", "stable", "barn"]
    assert abs(sum(v for _, v in a) - 1.0) < 0.01 and a != b and a == privy_seat_weights(3)


def test_a_field_pit_stands_at_the_nearest_paddy_edge_on_the_house_side(monkeypatch: pytest.MonkeyPatch) -> None:
    """269 B11 (research/homesteads/260): on a pit hamlet a household in the field share keeps its night-soil pit at its
    nearest paddy edge, stepped off it toward the house, recorded `seat: field_edge`, and the share is declared in meta."""
    from l7r.diagram.hamletgen.homesteads import fixtures as fx

    _one_kind(monkeypatch, fx, ("manure",))
    monkeypatch.setattr(fx, "PIT_FIELD_SHARE_BAND", (1.0, 1.0))
    s = Settlement(W=900, H=700, seed=7)
    s.meta(name="T", scale="hamlet", ftpx=1)
    house = {"x": 300.0, "y": 300.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "W"}
    s.M["houses"].append(dict(house))
    s.placed.append((300.0, 300.0, 46.0, 28.0))
    s.field_polys.append([(420.0, 200.0), (600.0, 200.0), (600.0, 400.0), (420.0, 400.0)])
    plan = a_plan()
    plan.manure_form = "pit"
    fx.farmstead_fixtures(s, plan, [house])
    pits = [r for r in s.M["farm_fixtures"] if r["kind"] == "manure"]
    assert s.M["meta"]["pit_field_share"] == 1.0
    assert len(pits) == 1 and pits[0]["seat"] == "field_edge" and pits[0]["form"] == "pit"
    assert 400.0 < pits[0]["x"] < 420.0 and abs(pits[0]["y"] - 300.0) < 1.0, "off the paddy's west edge, level with the house"


def test_field_edge_seats_come_nearest_first_and_skip_an_edge_the_house_stands_within() -> None:
    """`field_edge_seats` (269 B11): a road's keep-out is added to the step, and an edge closer to the house than the
    step has no ground on the house's side to offer."""
    from l7r.diagram.hamletgen.homesteads.fixtures import edge_index, field_edge_seats

    idx = edge_index([[(100.0, 0.0), (200.0, 0.0), (200.0, 100.0), (100.0, 100.0)]], [([(0.0, 80.0), (60.0, 80.0)], 5.0), ([(0.0, 52.0), (60.0, 52.0)], 5.0)])
    pts = field_edge_seats(idx, 50.0, 50.0, 200.0, 10.0)
    assert pts[0][:2] == pytest.approx((50.0, 65.0)) and pts[1][:2] == pytest.approx((90.0, 50.0)), "the road, then the paddy"
    assert pts[0][2] is True and pts[1][2] is False, "each seat says whether its edge is a road"
    assert len(pts) == 2, "the road 2 px off the house leaves no ground between"


def test_a_corridor_bath_is_joined_to_its_house_and_a_front_yard_bath_stands_before_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """269 B12 (research/homesteads/214): the hamlet's bath form is a knob declared in meta; a corridor bath draws and
    reserves the corridor from the wall to the shed, a front-yard bath stands on the sunny front."""
    from l7r.diagram.hamletgen.homesteads import fixtures as fx

    _one_kind(monkeypatch, fx, ("bath",))
    got = {}
    for form in fx.BATH_SEATS:
        monkeypatch.setattr(fx, "BATH_SEATS", (form,))
        s = Settlement(W=900, H=700, seed=7)
        s.meta(name="T", scale="hamlet", ftpx=1)
        house = {"x": 400.0, "y": 350.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "W"}
        s.M["houses"].append(dict(house))
        s.placed.append((400.0, 350.0, 46.0, 28.0))
        fx.farmstead_fixtures(s, a_plan(), [house])
        assert s.M["meta"]["bath_seat"] == form
        got[form] = (s.M["farm_fixtures"][0], len(s.placed))
        monkeypatch.setattr(fx, "BATH_SEATS", ("front_yard", "corridor"))
    front, _n = got["front_yard"]
    assert front["y"] > 350.0 + 14.0 and "corridor" not in front
    walk_bath, n = got["corridor"]
    walk = walk_bath["corridor"]
    assert n == 3 and walk["x"] == pytest.approx(400.0 + 23.0 + 3.0) and walk_bath["x"] > 400.0 + 23.0 + 6.0, "the flank away from the shed"


def test_a_corridor_bath_whose_corridor_ground_is_taken_is_not_drawn_unjoined(monkeypatch: pytest.MonkeyPatch) -> None:
    """269 B12: the corridor's own ground must be clear. Feature 287, homes H34: where a thing stands on every corridor the
    household's bath is not drawn unjoined - the rolled form is the form drawn - but passed on, and counted where no
    household takes it."""
    from l7r.diagram.hamletgen.homesteads import fixtures as fx

    _one_kind(monkeypatch, fx, ("bath",))
    monkeypatch.setattr(fx, "BATH_SEATS", ("corridor",))
    s = Settlement(W=900, H=700, seed=7)
    s.meta(name="T", scale="hamlet", ftpx=1)
    house = {"x": 400.0, "y": 350.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "W"}
    s.M["houses"].append(dict(house))
    s.placed += [(400.0, 350.0, 46.0, 28.0), (426.0, 343.0, 2.0, 2.0), (413.8, 333.0, 2.0, 2.0), (386.2, 333.0, 2.0, 2.0)]  # a post in each corridor
    fx.farmstead_fixtures(s, a_plan(), [house])
    assert not [f for f in s.M["farm_fixtures"] if f["kind"] == "bath"], "no unjoined shed"
    assert s.M["meta"]["farm_fixtures_unseated"] == {"bath": 1}


def test_corridor_rect_runs_to_the_wall_the_shed_faces() -> None:
    """`corridor_rect` (269 B12): a flank seat's corridor crosses to the side wall, a back seat's to the back wall."""
    from l7r.diagram.hamletgen.homesteads.fixtures import corridor_rect

    assert corridor_rect(32.0, -7.0, 46.0, 28.0, 6.0, 3.0) == (26.0, -7.0, 6.0, 3.0)
    assert corridor_rect(-13.8, -20.0, 46.0, 28.0, 6.0, 3.0) == (-13.8, -17.0, 3.0, 6.0)


def test_a_front_yard_bath_stands_beside_its_work_yard() -> None:
    """`beside_the_yard` (269 B12): a wall gap off either side of the steading's recorded yard, in the house frame, level with
    its middle first; a house with no recorded yard offers none."""
    from l7r.diagram.hamletgen.homesteads.fixtures import beside_the_yard

    h = {"geom": {"yard": [400.0, 380.0, 28.0, 20.0]}}
    seats = beside_the_yard(h, 400.0, 350.0, 1.0, 0.0, 3.5, 6.0, 6.0)
    assert seats[0] == pytest.approx((20.5, 30.0, 6.0, 6.0)) and seats[1] == pytest.approx((-20.5, 30.0, 6.0, 6.0))
    assert seats[2][1] == pytest.approx(37.0) and beside_the_yard({}, 0.0, 0.0, 1.0, 0.0, 3.5, 6.0, 6.0) == []
    from l7r.diagram.hamletgen.homesteads.fixtures import corridor_rect

    assert corridor_rect(32.0, -7.0, 46.0, 28.0, 6.0, 3.0, trim=3.0) == (27.5, -7.0, 3.0, 3.0)


def _one_house(monkeypatch: pytest.MonkeyPatch, fx: object, keep: tuple[str, ...], plan: object = None) -> Settlement:
    """One raked-square farmhouse at (400, 350) with only `keep` fixtures owed, seated by `farmstead_fixtures`."""
    _one_kind(monkeypatch, fx, keep)
    s = Settlement(W=900, H=700, seed=7)
    s.meta(name="T", scale="hamlet", ftpx=1)
    house = {"x": 400.0, "y": 350.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "W"}
    s.M["houses"].append(dict(house))
    s.placed.append((400.0, 350.0, 46.0, 28.0))
    fx.farmstead_fixtures(s, plan or a_plan(), [house])  # type: ignore[attr-defined]
    return s


def test_the_persimmon_stands_in_the_dooryard_or_behind_the_house_never_on_the_flank() -> None:
    """269 B14 (research/homesteads/218): the dooryard in front - the work yard's edge first - or behind the house; the side
    rolled first is tried first, the flank is no seat, and the same bearings follow a step out."""
    from l7r.diagram.hamletgen.homesteads.fixtures import persimmon_seats

    front = persimmon_seats((0.0, 40.0, 30.0, 20.0), 50.0, 5.0, True, [10.0])
    assert front[:4] == [(20.0, 40.0), (-20.0, 40.0), (20.0, 50.0), (-20.0, 50.0)], "beside the work yard, level with its middle then its edge"
    assert all(ly > 0 for _lx, ly in front[4:7]) and all(ly < 0 for _lx, ly in front[7:10])
    back = persimmon_seats(None, 50.0, 5.0, False, [10.0])
    assert all(ly < 0 for _lx, ly in back[:3]) and len(back) == 12 and back[6] == (pytest.approx(45.0), pytest.approx(-45.0))
    assert not any(abs(ly) < 1.0 and abs(lx) > 0.0 for lx, ly in front + back), "no seat on the house's flank"


def test_the_persimmon_seats_on_a_pool_map_house_and_declares_its_front_share(monkeypatch: pytest.MonkeyPatch) -> None:
    """269 B14: the hamlet's front share is rolled in its band and declared; the tree is drawn at the new crown."""
    from l7r.diagram.hamletgen.homesteads import fixtures as fx

    s = _one_house(monkeypatch, fx, ("persimmon",))
    lo, hi = fx.PERSIMMON_FRONT_BAND
    assert lo <= s.M["meta"]["persimmon_front_share"] <= hi
    (tree,) = s.M["persimmons"]
    assert tree["r"] == 11.5 and abs(tree["y"] - 350.0) > 14.0, "in front of or behind the house, not level with it"


def test_the_woodshed_form_stands_a_ken_off_the_wall(monkeypatch: pytest.MonkeyPatch) -> None:
    """269 B15 (research/homesteads/212): on a woodshed hamlet the woodpile is a shed of its own, 12 x 9 ft, a ken out."""
    from l7r.diagram.hamletgen.homesteads import fixtures as fx

    monkeypatch.setattr(fx, "WOODPILE_FORMS", ("shed",))
    s = _one_house(monkeypatch, fx, ("woodpile",))
    (shed,) = s.M["farm_fixtures"]
    assert s.M["meta"]["woodpile_form"] == "shed" and shed["form"] == "shed" and (shed["w"], shed["h"]) == (12.0, 9.0)
    gap = max(abs(shed["x"] - 400.0) - 23.0, abs(shed["y"] - 350.0) - 14.0) - min(shed["w"], shed["h"]) / 2
    assert gap >= 6.0, f"a building of its own, {gap:.1f} ft off the wall"


def test_the_kizuma_lies_along_the_windbreak_to_windward_and_else_the_stack_goes_under_the_eaves(monkeypatch: pytest.MonkeyPatch) -> None:
    """269 B15: on a kizuma hamlet the firewood is stacked along the windbreak's inner edge where the belt is at this yard's
    windward back; a homestead with no belt there keeps the eaves stack."""
    from l7r.diagram.hamletgen.homesteads import fixtures as fx

    monkeypatch.setattr(fx, "WOODPILE_FORMS", ("kizuma",))
    plan = a_plan()
    plan.belt = [(330.0, 270.0), (470.0, 270.0), (470.0, 316.0), (330.0, 316.0)]  # NW is the default wind: the belt at the back
    s = _one_house(monkeypatch, fx, ("woodpile",), plan)
    (stack,) = s.M["farm_fixtures"]
    assert stack["form"] == "kizuma" and stack["w"] == 24.0 and stack["y"] < 322.0 and stack["rot"] % 180.0 == pytest.approx(0.0, abs=0.5)
    plan.belt = [(330.0, 400.0), (470.0, 400.0), (470.0, 440.0), (330.0, 440.0)]  # to leeward: not this yard's windbreak
    s = _one_house(monkeypatch, fx, ("woodpile",), plan)
    (stack,) = s.M["farm_fixtures"]
    assert "form" not in stack and stack["w"] == 10.0, "the eaves stack"


def test_kizuma_seats_keep_to_the_windward_edge_within_reach() -> None:
    """`kizuma_seats` (269 B15): the edge point nearest the house and a stack's length either way, each only to windward and
    within reach; nothing for a belt out of reach, and nothing where the house stands on the belt's own line."""
    from l7r.diagram.hamletgen.homesteads.fixtures import _WIND_VEC, belt_edge, kizuma_seats

    line = belt_edge([(330.0, 270.0), (470.0, 270.0), (470.0, 316.0), (330.0, 316.0)])
    got = kizuma_seats(line, 400.0, 350.0, 70.0, _WIND_VEC["NW"], 24.0, 2.0)
    assert len(got) == 2 and got[0][:2] == (pytest.approx(400.0), pytest.approx(318.0)), "the nearest point, and the one to the west"
    assert kizuma_seats(line, 400.0, 500.0, 70.0, _WIND_VEC["NW"], 24.0, 2.0) == []

    assert all(p[1] < 316.0 for p in kizuma_seats(line, 400.0, 316.0, 70.0, _WIND_VEC["N"], 24.0, 2.0)), "the house on the line is no seat"


def test_fixture_form_names_the_drawn_form() -> None:
    """`fixture_form` (feature 150, 269 B15): the pit, the woodshed, the kizuma, or the plain glyph."""
    from l7r.diagram.hamletgen.homesteads.fixtures import fixture_form

    assert fixture_form("manure", "pit", "eaves", False) == "pit" and fixture_form("manure", "heap", "eaves", False) is None
    assert fixture_form("woodpile", None, "kizuma", True) == "kizuma" and fixture_form("woodpile", None, "shed", False) == "shed"
    assert fixture_form("woodpile", None, "kizuma", False) is None and fixture_form("coop", "pit", "shed", False) is None


def test_every_share_is_seated_as_its_count(monkeypatch: pytest.MonkeyPatch) -> None:
    """269 fc:2261: a declared share of the households is drawn as that many fixtures - `round(share x houses)` - and a
    chosen house with no room passes its fixture on to one that has it, so the count is met."""
    from l7r.diagram.hamletgen.homesteads import fixtures as fx

    _one_kind(monkeypatch, fx, ())
    monkeypatch.setitem(fx.FIXTURE_BANDS, "coop", (0.5, 0.5))
    s = Settlement(W=1400, H=700, seed=7)
    s.meta(name="T", scale="hamlet", ftpx=1)
    houses = [{"x": 200.0 + 200.0 * k, "y": 350.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "W"} for k in range(6)]
    for h in houses:
        s.M["houses"].append(dict(h))
        s.placed.append((h["x"], h["y"], 46.0, 28.0))
    first = min(range(6), key=lambda i: s._hjit(houses[i]["x"], houses[i]["y"], fx._SALT["coop"]))
    s.field_polys.append([(houses[first]["x"] - 60.0, 250.0), (houses[first]["x"] + 60.0, 250.0), (houses[first]["x"] + 60.0, 450.0), (houses[first]["x"] - 60.0, 450.0)])
    fx.farmstead_fixtures(s, a_plan(), houses)
    coops = [r for r in s.M["farm_fixtures"] if r["kind"] == "coop"]
    assert s.M["meta"]["farm_fixtures_target"]["coop"] == 3 and len(coops) == 3, "three of six, as declared"
    assert houses[first]["x"] not in {r["of"][0] for r in coops}, "the house in the paddy passed its coop on"
    assert "farm_fixtures_unseated" not in s.M["meta"]


def test_strip_blocked_refuses_a_strip_standing_on_a_paddy() -> None:
    """A household strip whose corner stands in a paddy (or within 6 ft of its edge) is blocked - the branch the pool
    stopped reaching once Sawada's stranded field-house seat was refused (feature 278)."""
    s, _plan = _strip_settlement()
    paddy = [(480.0, 480.0), (700.0, 480.0), (700.0, 700.0), (480.0, 700.0)]
    assert hg.homesteads._strip_blocked(s, 500, 500, 30, 20, 0, 0, [paddy], [], None, []) is True
    assert hg.homesteads._strip_blocked(s, 300, 300, 30, 20, 0, 0, [paddy], [], None, []) is False


def test_a_front_seat_is_pushed_across_a_brook_by_the_waters_reach() -> None:
    """`water_push` (feature 261): a box whose near side a water course lies across moves along `n` past the course by its
    clearance; a course beside the box but beyond its lateral span, or one far off, moves nothing."""
    from l7r.diagram.hamletgen.homesteads.stages import water_push

    brook = [((-100.0, 10.0), (100.0, 10.0), 5.0)]  # across the box, 10 ft past its near edge at 0
    assert water_push(brook, (0.0, 20.0), (0.0, 1.0), 30.0, 0.0, 40.0) == 15.0
    assert water_push([((200.0, -50.0), (200.0, 90.0), 5.0)], (0.0, 20.0), (0.0, 1.0), 30.0, 0.0, 40.0) == 0.0
    assert water_push([((5000.0, 0.0), (5100.0, 0.0), 5.0)], (0.0, 20.0), (0.0, 1.0), 30.0, 0.0, 40.0) == 0.0


def test_the_steading_is_the_largest_box_holding_the_house() -> None:
    """`homestead_box`: of the reserved boxes round the house, the whole steading's - and none when no box holds it."""
    from l7r.diagram.hamletgen.homesteads.fixtures import homestead_box

    assert homestead_box([(0.0, 0.0, 10.0, 10.0), (0.0, 0.0, 100.0, 80.0), (500.0, 0.0, 400.0, 400.0)], 0.0, 0.0) == (0.0, 0.0, 100.0, 80.0)
    assert homestead_box([(500.0, 0.0, 10.0, 10.0)], 0.0, 0.0) is None


def test_the_drawn_forms_are_recorded_beside_the_rolled_knob() -> None:
    """`record_drawn_forms` (the 269 landing's reviews): the woodpiles by form - an unformed stack is the eaves stack - and
    the baths by whether a corridor joins them."""
    from l7r.diagram.hamletgen.homesteads.fixtures import record_drawn_forms

    m = {
        "meta": {},
        "farm_fixtures": [{"kind": "woodpile"}, {"kind": "woodpile", "form": "kizuma"}, {"kind": "woodpile"}, {"kind": "bath", "corridor": {"x": 1.0}}, {"kind": "bath"}, {"kind": "coop"}],
    }
    record_drawn_forms(m)
    assert m["meta"]["woodpile_forms_drawn"] == {"eaves": 2, "kizuma": 1} and m["meta"]["bath_seats_drawn"] == {"corridor": 1, "unjoined": 1}


def test_a_shrine_corner_named_by_the_compass_is_that_corner_on_a_turned_house() -> None:
    """`shrine_corner_local` (the 269 landing's review of Kashikawa): a world offset carried into the house frame lands back
    at the same world point through the seat loop's own transform, so NE is north-east on a quarter-turned house too."""
    import math

    from l7r.diagram.hamletgen.homesteads.fixtures import shrine_corner_local

    for rot in (0.0, 4.0, 93.6):
        ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        lx, ly = shrine_corner_local(30.0, -20.0, ca, sa)
        assert (lx * ca - ly * sa, lx * sa + ly * ca) == (pytest.approx(30.0), pytest.approx(-20.0))


def test_a_household_bamboo_strip_stands_on_its_house_bank_and_names_its_house() -> None:
    """Feature 287, homes H01: a strip whose seat lies across the brook from its house is refused and the next tried; a
    seated strip records its owner (`plan.bamboo_of`, by its index among the stands)."""
    from l7r.diagram.hamletgen.homesteads.bamboo import household_bamboo
    from l7r.diagram.settlement._geom.water_index import crosses_a_stream

    got = 0
    for seed in range(40):
        s, plan = _toy_hamlet(10, seed=seed)
        plan.bamboo = "homestead"
        houses = [{"x": 200.0 + 120.0 * k, "y": 200.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"} for k in range(8)]
        s.M["streams"] = [{"poly": [[100.0, 180.0], [1300.0, 180.0]], "w": 2.0}]  # across every house's back
        rings = household_bamboo(s, plan, houses)
        for i, ring in enumerate(rings):
            cx, cy = sum(p[0] for p in ring) / 4, sum(p[1] for p in ring) / 4
            owner = plan.bamboo_of[i]
            assert not crosses_a_stream(owner, (cx, cy), s.M["streams"])
        got += len(rings)
    assert got, "some strips seated over the seeds"


def test_an_eaves_stack_stands_against_a_wall_of_its_own_steading_or_passes_on(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287, homes H35: an eaves woodpile is offered only the seats against a wall of its steading (the house, its
    kura), never the outward rungs; with every wall taken it passes on, and no stack stands off a wall."""
    from l7r.diagram.hamletgen.homesteads import fixtures as fx
    from l7r.diagram.hamletgen.homesteads.fixtures import against_a_wall, steading_rects

    walls = steading_rects(46.0, 28.0, "N")
    assert against_a_wall((0.0, -(14.0 + 3.5 + 2.0), 10.0, 4.0), walls, 3.5), "the back wall, a wall gap off"
    assert not against_a_wall((0.0, -(14.0 + 3.5 + 4.0 + 3.5 + 2.0), 10.0, 4.0), steading_rects(46.0, 28.0, None), 3.5), "a stack's depth further out"
    assert against_a_wall((0.0, -(14.0 + 3.5 + 4.0 + 3.5 + 2.0), 10.0, 4.0), walls, 3.5), "...which is the north kura's own wall"
    assert len(steading_rects(46.0, 28.0, "W")) == 2 and len(steading_rects(46.0, 28.0, None)) == 1
    _one_kind(monkeypatch, fx, ("woodpile",))
    monkeypatch.setattr(fx, "WOODPILE_FORMS", ("eaves",))
    for boxed in (False, True):
        s = Settlement(W=900, H=700, seed=7)
        s.meta(name="T", scale="hamlet", ftpx=1)
        house = {"x": 400.0, "y": 350.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"}
        s.M["houses"].append(dict(house))
        s.placed.append((400.0, 350.0, 46.0, 28.0))
        if boxed:  # a ring of posts a wall gap off every wall: no seat against any wall
            s.placed += [(400.0, 350.0 + d * 20.0, 60.0, 4.0) for d in (-1, 1)] + [(400.0 + d * 29.0, 350.0, 4.0, 40.0) for d in (-1, 1)]
        fx.farmstead_fixtures(s, a_plan(), [house])
        piles = [f for f in s.M["farm_fixtures"] if f["kind"] == "woodpile"]
        if boxed:
            assert not piles and s.M["meta"]["farm_fixtures_unseated"] == {"woodpile": 1}
        else:
            (p,) = piles
            lx, ly = p["x"] - 400.0, p["y"] - 350.0
            gap = max(abs(lx) - 23.0, abs(ly) - 14.0)
            assert gap <= 3.5 + 4.0 + 1.5, f"against a wall ({gap:.1f} px)"


def test_the_woodpile_form_a_homestead_draws_is_the_one_the_predicate_names() -> None:
    """Feature 287, homes H33: the kizuma where the knob rolled it and the belt stands within reach, else the eaves stack."""
    from l7r.diagram.hamletgen.homesteads.fixtures import woodpile_form_for

    assert woodpile_form_for("kizuma", True) == "kizuma"
    assert woodpile_form_for("kizuma", False) == "eaves"
    assert woodpile_form_for("shed", False) == "shed" and woodpile_form_for("eaves", True) == "eaves"
