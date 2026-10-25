"""Feature 269 group E6, B27: where a village keeps its fuel wood (research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html) - beyond the fields, on ground
higher than the fields it adjoins, never downslope of the houses."""

import math

from l7r.diagram.hamletgen.hinterland.parcels import crop_edge_points, field_height_near, woodland_tier

DOWN_SOUTH = (0.0, 1.0)  # the land falls toward +y: height is -y


def test_the_tiers_follow_the_record_s_ranking():
    # the lowest house at height -500 (y = 500), the field beside the seat at height -300 (y = 300)
    assert woodland_tier((0.0, 200.0), DOWN_SOUTH, -300.0) == 0  # above the field it adjoins
    assert woodland_tier((0.0, 400.0), DOWN_SOUTH, -300.0) == 1  # below that field: the level
    assert woodland_tier((0.0, 600.0), DOWN_SOUTH, -300.0) == 1  # downslope of every house: the field alone ranks it (374 wave 120)
    assert woodland_tier((0.0, 600.0), DOWN_SOUTH, -math.inf) == 0  # no fields: any ground


def test_the_field_height_is_read_off_the_nearest_stretch_of_edge():
    """A long edge is sampled along its length, so a seat beside its middle reads the stretch beside it, not a far vertex -
    the highest of the edge within 300 ft past the nearest point (feature 328: the field beside a wood, not one point)."""
    field = [(0.0, 1000.0), (2000.0, 0.0), (2000.0, 1000.0)]  # a sloping top edge from (0, 1000) up to (2000, 0)
    grid = crop_edge_points([field])
    h = field_height_near((1000.0, 400.0), DOWN_SOUTH, grid)
    assert -400.0 <= h <= -320.0, h  # the edge at x = 1000 stands at y = 500, and rises to about y = 360 within 300 ft past the nearest point
    assert field_height_near((1000.0, 400.0), DOWN_SOUTH, grid, beside=0.0) <= -480.0, "with no stretch past it, the nearest point alone"
    assert field_height_near((9000.0, 9000.0), DOWN_SOUTH, grid) < -900.0  # far off, the widening pad still answers
    assert field_height_near((50000.0, 50000.0), DOWN_SOUTH, grid) == -math.inf  # past the widest pad: no field at all
    assert field_height_near((0.0, 0.0), DOWN_SOUTH, crop_edge_points([])) == -math.inf


def test_the_windward_bamboo_strip_stands_clear_of_its_house():
    """B29: the wind side's strip seats on the windward corner for a diagonal wind and on the windward face for a
    cardinal one, the gap clear of the walls - it used to lap the house's own corner under a NW wind and never seat."""
    from l7r.diagram.hamletgen.homesteads.bamboo import wind_seat

    hw, hh, gap, sw, sh = 40.0, 30.0, 6.0, 22.0, 16.0
    for wind in ((-math.sqrt(0.5), -math.sqrt(0.5)), (0.0, -1.0), (1.0, 0.0), (0.2, 0.98)):
        cx, cy, w, h = wind_seat(wind[0], wind[1], hw, hh, gap, sw, sh)
        clear_x = abs(cx) - w / 2 >= hw / 2 + gap - 1e-9
        clear_y = abs(cy) - h / 2 >= hh / 2 + gap - 1e-9
        assert clear_x or clear_y, (wind, cx, cy)
        assert cx * wind[0] >= 0 and cy * wind[1] >= 0, "on the windward side"
    assert wind_seat(-0.7, -0.7, hw, hh, gap, sw, sh)[:2] == (-(hw / 2 + gap + sw / 2), -(hh / 2 + gap + sh / 2))
    assert wind_seat(1.0, 0.0, hw, hh, gap, sw, sh) == (hw / 2 + gap + sh / 2, 0.0, sh, sw)


def test_low_ground_by_the_water_is_refused_and_dry_ground_below_the_houses_is_not() -> None:
    """Feature 374 wave 120 (0077's drawing page: "A wood seated below the houses, past the fields and beside a river or marsh"
    is refused): below the houses AND within `LOW_BY_WATER_FT` of a river's course or a marsh - flush against the marsh line
    too, which the keep-outs had passed; not above the houses beside the water, nor below them on dry ground."""
    from l7r.diagram.hamletgen.hinterland.parcels import LOW_BY_WATER_FT, low_by_the_water

    marsh = [[(0.0, 700.0), (200.0, 700.0), (200.0, 900.0), (0.0, 900.0)]]
    river = [[(-500.0, 650.0), (-100.0, 650.0)]]
    floor = -500.0  # heights run up -y on DOWN_SOUTH: a point with y > 500 is below the houses
    assert low_by_the_water((100.0, 690.0), DOWN_SOUTH, floor, [], marsh, LOW_BY_WATER_FT), "flush against the marsh, below the houses"
    assert low_by_the_water((100.0, 800.0), DOWN_SOUTH, floor, [], marsh, LOW_BY_WATER_FT), "in the marsh"
    assert low_by_the_water((-300.0, 620.0), DOWN_SOUTH, floor, river, [], LOW_BY_WATER_FT), "by the river's course"
    assert not low_by_the_water((100.0, 600.0), DOWN_SOUTH, floor, [], marsh, LOW_BY_WATER_FT), "below the houses, dry ground"
    assert not low_by_the_water((100.0, 690.0), DOWN_SOUTH, -900.0, [], marsh, LOW_BY_WATER_FT), "beside the marsh, above the houses"


def test_a_seat_below_the_houses_on_dry_ground_is_kept_by_its_tier(monkeypatch) -> None:  # noqa: ANN001
    """Feature 374 wave 120: the ranking reads the field alone - the slope, then the level, any seat kept."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.hinterland.parcels import patches as parcels

    tiers = {(1.0, 1.0): 0, (2.0, 2.0): 1, (3.0, 3.0): 1}
    monkeypatch.setattr(parcels, "woodland_tier", lambda p, *a: tiers[p])
    monkeypatch.setattr(parcels, "field_height_near", lambda *a: 0.0)
    monkeypatch.setattr(parcels, "crossed_through_many", lambda env, c, seats: [True] * len(seats))
    s = SimpleNamespace(M={"houses": []}, px=lambda v: v)
    plan = SimpleNamespace(fall=(0.0, 1.0), envelope=[])
    out = parcels._beyond_the_fields(s, plan, [(5.0, 1.0, 1.0), (5.0, 2.0, 2.0), (5.0, 3.0, 3.0)], None, (0.0, 0.0))  # type: ignore[arg-type]
    ranked = [(x, y) for _sc, x, y in sorted(out, reverse=True)]
    assert ranked[0] == (1.0, 1.0) and set(ranked) == {(1.0, 1.0), (2.0, 2.0), (3.0, 3.0)}, "the slope first, every seat kept"


def test_a_walk_through_a_field_whose_outline_crosses_itself_is_measured() -> None:
    """Feature 374 wave 120 (cohort seed 5): a field outline crossing itself raised GEOS's side location conflict on a walk
    through the crossing; the outline is made valid first, and the walk's share is measured on it."""
    from l7r.diagram.hamletgen.hinterland.crossing import crossed_through_many

    bowtie = [(0.0, 0.0), (100.0, 100.0), (100.0, 0.0), (0.0, 100.0)]  # crosses itself at (50, 50)
    got = crossed_through_many(bowtie, (-50.0, 50.0), [(150.0, 50.0), (50.0, 50.0)])
    assert len(got) == 2 and all(isinstance(v, bool) for v in got)


def test_every_drawn_wood_was_asked_the_water_rule_at_its_own_square(monkeypatch) -> None:  # noqa: ANN001
    """Feature 374 wave 120 (the plan review): the water rule is in the scan's one qualification (`_ok`), so a seat the nudge,
    the row step, the size roll or the aspect steps move is asked it again at its own square. A refusal patched over the
    canvas's east half keeps every drawn wood west of the line, its whole square included; unpatched, woods stand east too."""
    from l7r.diagram.hamletgen.hinterland.parcels import patches as parcels
    from l7r.diagram.settlement import Settlement
    from l7r.diagram.settlement.land.cover import ring_center

    from ._builders import a_plan

    monkeypatch.setattr(parcels, "crossed_through_many", lambda field, frm, tos, share=0.5: [True] * len(tos))
    plan = a_plan()

    def scan() -> list:  # type: ignore[type-arg]
        s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
        s.M["fields"] = []
        plan.belt = []
        plan.title_pocket = None
        return parcels.open_ground_patches(s, plan, count=6)

    free = sorted(ring_center(r)[0] for r in scan())
    assert len(free) >= 2, "non-vacuity: the open canvas seats woods"
    line = (free[0] + free[-1]) / 2.0  # between the westmost and eastmost woods: unpatched, one stands east of it
    reaches: list[float] = []

    def east(p, fall, floor, rivers, marshes, reach):  # type: ignore[no-untyped-def]
        reaches.append(reach)
        return p[0] + reach > line

    monkeypatch.setattr(parcels, "low_by_the_water", east)
    drawn = scan()
    assert drawn and all(max(x for x, _y in r) <= line + 1.0 for r in drawn), "every wood's square west of the line"
    assert min(reaches) > parcels.LOW_BY_WATER_FT, "asked at the square's reach, not the seat's"
