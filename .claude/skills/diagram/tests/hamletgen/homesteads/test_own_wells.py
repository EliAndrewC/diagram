"""Feature 291: a farm with its own grove draws from its own well (research homesteads/200), and draws the bamboo it rolls."""

from __future__ import annotations

import math

from l7r.diagram.hamletgen.homesteads.wells import grove_water, own_well_clear
from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.homestead_parts.grove_sides import bundle_turn
from l7r.diagram.settlement.homestead_parts.groves import HOUSEHOLD_BAMBOO_PREVALENCE
from l7r.diagram.settlement.rolling.dispersed import dispersed_layout


def _s() -> Settlement:
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    return s


def test_own_well_clear_tests_footprints_not_circles() -> None:
    """A band 150 ft long 60 ft off: its circumscribed circle would cover the seat, its box does not."""
    s = _s()
    band = (700.0, 600.0, 150.0, 40.0)
    assert own_well_clear(s, 700.0, 660.0, 12.4, [band]), "18 ft clear of the band's edge"
    assert not own_well_clear(s, 700.0, 630.0, 12.4, [band]), "its box laps the band"
    assert not own_well_clear(s, 20.0, 660.0, 12.4, []), "off the sheet's margin"


def test_a_grove_farm_carries_its_own_well_pocket_beside_its_yard_off_its_way_in() -> None:
    """Feature 291 on feature 287's seating: the pocket is laid in the bundle, beside the yard away from the garden, off the
    line from the house through the yard (the way in), inside the frame, clear of every grove band - at every turn."""
    for wind, flank in (("NW", -1), ("NW", 1), ("SE", -1), ("E", 1)):
        geom = dispersed_layout(
            700.0, 600.0, 46.0, 28.0, 3.0, (22.0, 24.0), (40.0, 30.0), sides=4, turn=bundle_turn(wind, flank), thin=17.0, sun_east=22.0, way_in=36.0, pad=16.0, back=24.0, well=24.0
        )
        wx, wy, ww, wh = geom["well"]
        yx, yy = geom["yard"][0], geom["yard"][1]
        gx, gy = geom["garden"][0], geom["garden"][1]
        assert (ww, wh) == (24.0, 24.0)
        ux, uy = (yx - 700.0) / math.dist((yx, yy), (700.0, 600.0)), (yy - 600.0) / math.dist((yx, yy), (700.0, 600.0))
        side = (wx - 700.0) * -uy + (wy - 600.0) * ux  # across the way in
        assert abs(side) >= 12.0 + 20.0, "off the line from the house through the yard"
        assert side * ((gx - 700.0) * -uy + (gy - 600.0) * ux) <= 0, "on the side away from the garden"
        fx, fy, fw, fh = geom["_frame"]
        assert abs(wx - fx) + ww / 2 <= fw / 2 and abs(wy - fy) + wh / 2 <= fh / 2, "inside the frame"
        assert not any(abs(wx - r[0]) < (ww + r[2]) / 2 and abs(wy - r[1]) < (wh + r[3]) / 2 for r in geom["groves"]), "clear of every band"
    plain = dispersed_layout(700.0, 600.0, 46.0, 28.0, 3.0, (22.0, 24.0), (40.0, 30.0), sides=2, turn=bundle_turn("NW", -1), thin=17.0, sun_east=22.0, way_in=36.0)
    assert "well" not in plain, "no pocket asked, none laid"


def test_grove_water_draws_each_farm_a_well_at_its_pocket_unless_a_channel_or_a_shared_well_serves_it(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`grove_water` (feature 291 FR-018/019 on 287's pockets): own water draws every pocket as a private well; the channel
    form draws only the dry farms' wells; a shared row draws none for a farm within reach of a street well."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.homesteads import farm_water, wells

    s = _s()
    a = {"x": 300.0, "y": 300.0, "well_pocket": [330.0, 330.0]}
    b = {"x": 900.0, "y": 900.0, "well_pocket": [930.0, 930.0]}
    c = {"x": 600.0, "y": 600.0}  # no pocket: nothing drawn for it
    own = SimpleNamespace(settlement_form="dispersed", farm_water="well", row_water="own")
    assert grove_water(s, own, [a, b, c]) == 2  # type: ignore[arg-type]
    assert [(w["x"], w["y"], w.get("private")) for w in s.M["wells"]] == [(330.0, 330.0, True), (930.0, 930.0, True)]
    assert s.M["meta"]["farm_water_drawn"] == "well" and s.M["meta"]["row_water_drawn"] is None
    s = _s()
    monkeypatch.setattr(farm_water, "farm_channels", lambda s_, hs: [b])  # b is left dry
    assert grove_water(s, SimpleNamespace(settlement_form="dispersed", farm_water="channel", row_water="own"), [a, b]) == 1  # type: ignore[arg-type]
    assert [(w["x"], w["y"]) for w in s.M["wells"]] == [(930.0, 930.0)]
    s = _s()
    s._row_streets = [[(0.0, 300.0), (400.0, 300.0)]]
    monkeypatch.setattr(wells, "shared_row_wells", lambda s_, hs, st: s_.well(300.0, 310.0) or 1)
    assert grove_water(s, SimpleNamespace(settlement_form="linear", farm_water="well", row_water="shared"), [a, b]) == 1  # type: ignore[arg-type]
    assert sorted((w["x"], w["y"], bool(w.get("private"))) for w in s.M["wells"]) == [(300.0, 310.0, False), (930.0, 930.0, True)], "a within reach, b not"
    assert s.M["meta"]["row_water_drawn"] == "shared"


def test_a_farm_draws_the_bamboo_it_rolls() -> None:
    s = _s()
    assert s._farm_rolls_bamboo(10.0, 20.0), "a map that never set the knob keeps the windbreak's bamboo"
    s._household_bamboo = False
    assert not s._farm_rolls_bamboo(10.0, 20.0)
    s._household_bamboo = True
    seats = [(float(x), 300.0) for x in range(100, 1300, 37)]
    rolled = [s._farm_rolls_bamboo(x, y) for x, y in seats]
    assert rolled == [s._hjit(x, y, 95.0) < HOUSEHOLD_BAMBOO_PREVALENCE for x, y in seats] and any(rolled) and not all(rolled)


def test_shared_row_wells_put_every_farm_within_reach() -> None:
    """`shared_row_wells` (plan D18): wells beside the street, one at the middle of each stretch of the row no longer than
    1.6 reaches, every farm then within the watering reach of one."""
    from l7r.diagram.hamletgen.homesteads.wells import WATER_REACH_FT, shared_row_wells

    s = _s()
    line = [(float(x), 700.0) for x in range(100, 1301, 8)]
    houses = [{"x": float(x), "y": 700.0 + (120.0 if i % 2 else -120.0), "geom": {"bbox": (float(x), 700.0, 200.0, 150.0)}} for i, x in enumerate(range(150, 1300, 110))]
    n = shared_row_wells(s, houses, [line])
    assert 1 <= n <= 2
    assert all(min(math.dist((h["x"], h["y"]), (w["x"], w["y"])) for w in s.M["wells"]) <= WATER_REACH_FT for h in houses)
    assert shared_row_wells(s, [], [line]) == 0 and shared_row_wells(s, houses, []) == 0
    assert shared_row_wells(s, [{"x": 5000.0, "y": 5000.0, "geom": {}}], [line]) == 0, "no farm near the street"
    assert shared_row_wells(s, houses, [line[:1]]) == 0


def test_a_well_seat_in_the_scrub_or_on_blocked_ground_is_refused(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    s = _s()
    assert own_well_clear(s, 700.0, 700.0, 8.0, [])
    monkeypatch.setattr(s, "_in_blocked", lambda x, y: True)
    assert not own_well_clear(s, 700.0, 700.0, 8.0, [])


def test_place_wells_hands_the_grove_farms_to_their_own_water_and_seats_the_rest(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`place_wells`: the grove farms take their own water (`grove_water`); where every farm carries a grove, nothing more."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.homesteads import wells

    s = _s()
    h = {"x": 700.0, "y": 700.0, "geom": {"groves": [[0, 0, 1, 1]]}}
    got: list = []
    monkeypatch.setattr(wells, "grove_water", lambda s_, plan_, hs: got.append(list(hs)) or 0)
    plan = SimpleNamespace(settlement_form="dispersed", farm_water="channel", row_water="own")
    assert wells.place_wells(s, plan, [h]) == 0  # type: ignore[arg-type]
    assert got == [[h]]
