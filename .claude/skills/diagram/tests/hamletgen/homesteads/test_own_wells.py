"""Feature 291: a farm with its own grove draws from its own well (research homesteads/200), and draws the bamboo it rolls."""

from __future__ import annotations

import math

from l7r.diagram.hamletgen.homesteads.wells import own_well_clear, own_wells
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


def test_every_grove_farm_gets_its_own_private_well_off_its_approach() -> None:
    s = _s()
    geom = dispersed_layout(700.0, 600.0, 46.0, 28.0, 3.0, (22.0, 24.0), (40.0, 30.0), sides=2, turn=bundle_turn("NW", -1), thin=17.0, sun_east=22.0, way_in=36.0, pad=16.0, back=24.0)
    h = {"x": 700.0, "y": 600.0, "w": 46.0, "h": 28.0, "rot": 0.0, "geom": geom}
    fx, fy, fw, fh = geom["_frame"]
    s.placed.append((fx, fy, fw, fh))  # the farm's own frame, which the pass lifts
    s.placed.append((700.0, 600.0, 46.0, 28.0))
    s.M["groves"] = [{"x": r[0], "y": r[1], "w": r[2], "h": r[3]} for r in geom["groves"]]
    yx, yy, yw, yh = geom["yard"]
    s.M["threshing_yards"] = [{"x": yx, "y": yy, "w": yw, "h": yh, "of": [700.0, 600.0]}]
    s.placed.append((yx, yy, yw, yh))
    assert own_wells(s, [h]) == 1
    w = s.M["wells"][-1]
    assert w.get("private") and math.dist((w["x"], w["y"]), (700.0, 600.0)) <= 110.0
    assert abs(w["x"] - 700.0) > 12.0, "not on the line from the house through the yard - the way in"


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


def test_a_dispersed_hamlet_under_channel_leads_its_water_in_and_wells_only_the_dry(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`place_wells` on a dispersed map rolled `channel`: the channels first, then an own well for each farm no course
    reached (feature 291 amendment 5), and the knob recorded as drawn."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.homesteads import farm_water, wells

    s = _s()
    h = {"x": 700.0, "y": 700.0, "geom": {"groves": [[0, 0, 1, 1]]}}
    got: list = []
    monkeypatch.setattr(farm_water, "farm_channels", lambda s_, hs: list(hs))
    monkeypatch.setattr(wells, "own_wells", lambda s_, hs: got.append(list(hs)) or 0)
    plan = SimpleNamespace(settlement_form="dispersed", farm_water="channel", row_water="own")
    wells.place_wells(s, plan, [h])  # type: ignore[arg-type]
    assert got == [[h]] and s.M["meta"]["farm_water_drawn"] == "channel" and s.M["meta"]["row_water_drawn"] is None
