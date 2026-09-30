"""Feature 287's homes guarantees at the homestead stage: the well pockets laid at seating and drawn (H10-H12), the
household bamboo on its house's bank (H01), the eaves stack against its steading (H35) and the woodpile form (H33).

Split from test_homesteads.py when feature 287 took it past the 1,000-line bar; the helpers stay there.
"""

import math

import pytest

import l7r.diagram.settlement.rolling.access as access_mod
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


def test_a_household_moved_off_the_seat_it_was_sought_from_past_every_pockets_reach_is_refused() -> None:
    """Feature 287, homes wave 5 (`test_every_household_can_reach_water`): the pocket is decided at the seek point, and the
    placer may carry the house off it - a candidate out of every pocket's and every water's reach, carrying no pocket of its
    own, is refused (`lot.watered`, asked by `_parts_fit` and `_bundle_common_fits`); within reach, or with its own pocket,
    it is not. The rule rests once the household is seated."""
    from l7r.diagram.settlement.rolling.lot import household_parts, seat_parts_done, watered

    s = Settlement(3000, 3000, seed=3)
    s.meta(name="W", scale="hamlet", ftpx=1, toscale=True)
    s._nucleated = True  # a nucleated bundle: a grove farm's carries its own pocket always (feature 291 on 287)
    s._pockets = [(800.0, 300.0)]
    assert household_parts(s, 800.0, 1000.0, "plain", None)[2] is False, "sought 700 ft from the pocket: no pocket of its own"
    near, far = s._bundle_geom(800.0, 1000.0, 46.0, 28.0), s._bundle_geom(800.0, 1100.0, 46.0, 28.0)
    assert s._candidate_watered(near) and s._bundle_common_fits(near)
    assert not s._candidate_watered(far) and not s._bundle_common_fits(far) and not s._parts_fit(far), "moved 100 ft on, 800 ft off: dry"
    assert watered(s, 800.0, 1100.0, True), "a candidate carrying its own pocket is watered wherever it stands"
    seat_parts_done(s)
    assert s._candidate_watered(far), "no household sought: nothing asked"


def test_a_seating_draws_a_well_at_every_pocket_it_laid() -> None:
    """The seat half and the draw half together: a toy hamlet's pockets are laid in the bundles (inside each envelope,
    beside the yard, among the doors) and `place_wells` draws every one."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads
    from l7r.diagram.hamletgen.homesteads.wells import WELL_AMONG_DWELLINGS_PX, well_gap_to_dwellings

    s, plan = _toy_hamlet(10, seed=4)  # seed 4: under feature 280's forms seed 3's margin seats eight of ten and is refused
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


def test_a_household_bamboo_strip_gives_way_to_every_reserved_copse_seat() -> None:
    """Feature 280 keeps the copse two crowns off the bamboo, feature 287 woods W25 plants every reserved seat: a strip is
    refused where a household's reserved seat falls in its keep-out (`stand_spares_seats`), and the next side tried."""
    from l7r.diagram.hamletgen.homesteads.bamboo import household_bamboo
    from l7r.diagram.settlement.homestead_parts.bamboo_keepout import stand_spares_seats

    for seed in range(40):
        s, plan = _toy_hamlet(10, seed=seed)
        plan.bamboo = "homestead"
        house = {"x": 600.0, "y": 400.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"}
        first = household_bamboo(s, plan, [house])
        if not first:
            continue
        ring = first[0]
        seat = (sum(p[0] for p in ring) / 4, sum(p[1] for p in ring) / 4)
        s, plan = _toy_hamlet(10, seed=seed)
        plan.bamboo = "homestead"
        s.M["houses"] = [{**house, "wood_share": {"seats": [list(seat)]}}]
        for r in household_bamboo(s, plan, [house]):
            xs, ys = [p[0] for p in r], [p[1] for p in r]
            assert stand_spares_seats((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(xs) - min(xs), max(ys) - min(ys), [seat], s.bscale)
        return
    raise AssertionError("no seed seated a strip")


# ---- homes H06: the shared sheds' pockets, reserved before any house ----------------------------------------------


def test_a_commons_hamlet_reserves_every_shared_shed_before_its_houses_and_draws_each(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287, homes H06: on `detached_commons` the sheds' pockets are laid in the band first, the houses pack round
    them, and `draft_byres` draws a shed in every pocket - the count asked (`commons_byre_target`) is the count drawn."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads
    from l7r.diagram.settlement.shrines_wells.byres import COMMONS_BYRE_GAP, commons_byre_target

    # the toy's bundles lay a bed or the well pocket where a flank door stands, and a corridor over its own parts is refused
    # since feature 287 M8 (`access.parts_clear`); the seating's count, not the parts, is under test here
    monkeypatch.setattr(access_mod, "parts_clear", lambda *a: True)
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


def _brook_site() -> Settlement:
    """A brook between the cluster (west) and its field (east), a ford on it, and the tree's exit strip running west."""
    from l7r.diagram.settlement.rolling.access import start_tree

    s = Settlement(1400, 1400, seed=3)
    s.meta(name="F", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    field = [(800.0, 400.0), (1200.0, 400.0), (1200.0, 1000.0), (800.0, 1000.0)]
    s.M["fields"] = [{"outline": [list(p) for p in field]}]
    s.field_polys.append(field)
    s.M["streams"] = [{"poly": [[700.0, 0.0], [700.0, 1400.0]], "w": 6.0}]
    s.M["meta"]["brook_fords"] = [[700.0, 650.0]]
    start_tree(s, (500.0, 700.0), (-1.0, 0.0), 300.0)
    return s


def test_the_field_corridor_is_reserved_with_the_exit_strip_and_no_homestead_covers_it() -> None:
    """Feature 287, ways W03 (homes wave 5): on a brook map the seating reserves the field's corridor before any house -
    the ways' own field path from the tree on to the bund, over the brook at its ford - as legs of the tree marked `field`,
    oriented toward the tree; an envelope on it is refused (`covers_box`). Where the rule asks nothing (no brook) nothing is
    reserved and the margin stands."""
    from l7r.diagram.hamletgen.homesteads.stages import reserve_field_corridor

    s = _brook_site()
    assert not s._access.covers_box((640.0, 650.0, 20.0, 20.0)), "the case: before the reservation the ground is free"
    assert reserve_field_corridor(s)
    legs = [c["pts"] for c in s.M["access_corridors"] if c.get("field")]
    assert legs == [[[796.5, 650.0], [722.0, 650.0]], [[722.0, 650.0], [678.0, 650.0]], [[678.0, 650.0], [500.0, 700.0]]], (
        "from the bund, square over the brook at its ford, to the exit strip's root: one chain toward the tree"
    )
    mid = ((legs[0][0][0] + legs[0][1][0]) / 2, (legs[0][0][1] + legs[0][1][1]) / 2)
    assert s._access.covers_box((mid[0], mid[1], 10.0, 10.0)), "an envelope on the corridor is refused"
    t = _brook_site()
    t.M["streams"] = []
    assert reserve_field_corridor(t) and not any(c.get("field") for c in t.M["access_corridors"])
    u = _brook_site()  # a brook and a tree but NO FIELD: there is no ground a field path could reach, so the rule asks none
    u.M["fields"], u.field_polys[:] = [], []
    assert reserve_field_corridor(u) and not any(c.get("field") for c in u.M["access_corridors"])


def test_a_margin_with_no_lawful_field_corridor_seats_no_one(monkeypatch: pytest.MonkeyPatch) -> None:
    """...and where no field path from the margin keeps the law, the margin seats no one (the ladder offers the next; past
    the last the site is refused) - `reserve_field_corridor` False on the violating case, the seating's refusal after it."""
    from l7r.diagram.hamletgen.homesteads import stages
    from l7r.diagram.hamletgen.ways import settle

    s = _brook_site()
    monkeypatch.setattr(settle, "corridor_on_lawful_ground", lambda M, run, width=3.0: False)
    assert stages.reserve_field_corridor(s) is False and not any(c.get("field") for c in s.M["access_corridors"])
    toy, plan = _toy_hamlet(10)
    monkeypatch.setattr(stages, "reserve_field_corridor", lambda s_: False)
    assert stages._seat_households(toy, plan) == (0, 0) and toy.M["houses"] == []
