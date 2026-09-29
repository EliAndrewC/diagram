"""Feature 287's homes guarantees at the homestead stage: the well pockets laid at seating and drawn (H10-H12), the
household bamboo on its house's bank (H01), the eaves stack against its steading (H35) and the woodpile form (H33).

Split from test_homesteads.py when feature 287 took it past the 1,000-line bar; the helpers stay there.
"""

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement import Settlement

from .test_homesteads import _WELL_HOUSES, _only_seat, _toy_hamlet


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


def test_the_woodpile_form_a_homestead_draws_is_the_one_the_predicate_names() -> None:
    """Feature 287, homes H33: the kizuma where the knob rolled it and the belt stands within reach, else the eaves stack."""
    from l7r.diagram.hamletgen.homesteads.fixtures import woodpile_form_for

    assert woodpile_form_for("kizuma", True) == "kizuma"
    assert woodpile_form_for("kizuma", False) == "eaves"
    assert woodpile_form_for("shed", False) == "shed" and woodpile_form_for("eaves", True) == "eaves"


# ---- homes H06: the shared sheds' pockets, reserved before any house ----------------------------------------------


def test_a_commons_hamlet_reserves_every_shared_shed_before_its_houses_and_draws_each() -> None:
    """Feature 287, homes H06: on `detached_commons` the sheds' pockets are laid in the band first, the houses pack round
    them, and `draft_byres` draws a shed in every pocket - the count asked (`commons_byre_target`) is the count drawn."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads
    from l7r.diagram.settlement.shrines_wells.byres import COMMONS_BYRE_GAP, commons_byre_target

    s, plan = _toy_hamlet(12)
    s.pin_knob("byre_form", "detached_commons")
    stage_homesteads(s, plan)
    pockets = list(s._byre_pockets)
    assert len(pockets) == commons_byre_target(12) == 3
    assert all(math.dist(a, b) > COMMONS_BYRE_GAP for i, a in enumerate(pockets) for b in pockets[i + 1 :])
    for x, y in pockets:  # no house laps a pocket's ground
        assert all(abs(x - h["x"]) >= (h["w"] + 16.0) / 2 or abs(y - h["y"]) >= (h["h"] + 11.0) / 2 for h in s.M["houses"])
    drawn = s.draft_byres()
    assert drawn == pockets and s.M["meta"]["byre_target"] == 3 and len(s.M["byres"]) == 3


def test_a_band_with_no_ground_for_the_shared_sheds_refuses_the_site(monkeypatch: pytest.MonkeyPatch) -> None:
    """The reservation's refusal: a band holding fewer pockets than asked is refused, naming it, before any house."""
    from l7r.diagram.hamletgen.homesteads import stages
    from l7r.diagram.hamletgen.homesteads.capacity import SiteRefused

    s, plan = _toy_hamlet(12)
    s.pin_knob("byre_form", "detached_commons")
    monkeypatch.setattr(Settlement, "reserve_commons_byres", lambda self, seat, n: [])
    with pytest.raises(SiteRefused, match="no ground for 3 shared byres"):
        stages._seat_households(s, plan)
    assert not s.M["houses"]


def test_the_commons_pockets_widen_past_a_full_core_and_keep_off_the_paddy() -> None:
    """The band's core walled by placed ground: the pockets are found in the widened rounds, none on the paddy, none within
    the gap of another - and a band with no free ground at all yields fewer than asked (the caller refuses it)."""
    from l7r.diagram.settlement.shrines_wells.byres import COMMONS_BYRE_GAP

    s = Settlement(1400, 1400, seed=3)
    s.meta(name="B", scale="hamlet", ftpx=1, toscale=True)
    seat = {"cx": 700.0, "cy": 500.0, "along": (1.0, 0.0), "out": (0.0, -1.0), "lat": 400.0, "dep": 150.0}
    s.placed.append((700.0, 500.0, 330.0, 250.0))  # the core (0.8 of the band) is built on
    s.field_polys.append([(0.0, 600.0), (1400.0, 600.0), (1400.0, 1400.0), (0.0, 1400.0)])
    pockets = s.reserve_commons_byres(seat, 20)
    assert len(pockets) == 4 and all(y < 600.0 - 10.0 for _x, y in pockets)
    assert all(math.dist(a, b) > COMMONS_BYRE_GAP for i, a in enumerate(pockets) for b in pockets[i + 1 :])
    full = Settlement(1400, 1400, seed=3)
    full.meta(name="F", scale="hamlet", ftpx=1, toscale=True)
    full.placed.append((700.0, 500.0, 1400.0, 1000.0))
    assert full.reserve_commons_byres(seat, 20) == []


def test_the_free_ground_grid_covers_the_fields_reach_not_the_canvas() -> None:
    """Feature 287, homes H31: the canvas grew for the seat's room; the FreeGround grid covers only the chords' reach."""
    from l7r.diagram.hamletgen.homesteads.boundary import free_ground_bounds

    chains = [[((1000.0, 1000.0), (1200.0, 1000.0), (0.0, 1.0))]]
    assert free_ground_bounds(chains, 300.0, 5000.0, 5000.0) == (700.0, 700.0, 1500.0, 1300.0)
    assert free_ground_bounds(chains, 2000.0, 2500.0, 2500.0) == (0.0, 0.0, 2500.0, 2500.0)
    assert free_ground_bounds([], 300.0, 5000.0, 4000.0) == (0.0, 0.0, 5000.0, 4000.0)
