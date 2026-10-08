"""Feature 287, homes H32 (plan M5 and D9): a household's farmstead fixtures laid as parts of its bundle
(`settlement/homestead_parts/fixture_seats.py`) - every kind laid, none on another part, each in its attested form; and
feature 280's forms carried into it: the bath a room joined to the house (M22), the firewood a wood shed a ken off a wall
of its steading (M21), the privy and the bath room at a size rolled per household."""

import pytest

from l7r.diagram.settlement.farm_fixtures import kura_rect
from l7r.diagram.settlement.homestead_parts import fixture_seats as fs
from l7r.diagram.settlement.homestead_parts.tree_shade import crown_shades

HW, HH = 46.0, 28.0
HOUSE = (0.0, 0.0, HW, HH)
KURA = kura_rect(HW, HH, "N", 1.0)
YARD = (0.0, HH / 2 + 3.0 + 12.0, 30.0, 24.0)
GARDEN = (HW / 2 + 3.0 + 7.0, HH / 2 + 3.0 + 12.0, 14.0, 24.0)  # an SE bed, beside the yard
EAST_BED = (HW / 2 + 3.0 + 7.0, 0.0, 14.0, 24.0)  # an E bed, on the floored rooms' end wall
ALL = ("privy", "woodpile", "manure", "bath", "coop", "shrine", "persimmon", "retirement")


def _px(v: float) -> float:
    return v


def _lay(kinds=ALL, forms=None, roofs=(HOUSE, KURA), ground=(YARD, GARDEN), roll=0.3, annex=None, notes=None):  # type: ignore[no-untyped-def]
    return fs.lay_fixtures(kinds, HW, HH, list(roofs), list(ground), YARD, True, lambda salt: roll, forms or fs.FixtureForms(), _px, annex, notes)


def test_every_kind_a_household_keeps_is_laid_clear_of_every_part_and_of_each_other() -> None:
    laid = _lay()
    assert set(laid) == set(ALL)
    solid = [(k, r) for k, r in laid.items() if k != "persimmon"]
    for k, r in solid:  # the bath room abuts the house (`joined_to_house`, below), clear of every other part
        assert fs.clears(r, [KURA, YARD, GARDEN] if k == "bath" else [HOUSE, KURA, YARD, GARDEN], fs.WALL_GAP_FT - 1e-6), k
        assert fs.clears(r, [q for kk, q in solid if kk != k], fs.WALL_GAP_FT - 1e-6), k
    crown = laid["persimmon"]
    assert fs.clears(crown, [HOUSE, KURA, *(r for _k, r in solid)], fs.CANOPY_PAD - 1e-6), "no crown over a roof"
    assert fs.clears((crown[0], crown[1], 4.0, 4.0), [YARD, GARDEN], 2.0 - 1e-6), "the trunk stands off the yard and the beds"
    assert fs.shed_off_a_wall(laid["woodpile"], [*fs.steading_rects(HW, HH, "N", 1.0), laid["retirement"]], fs.WALL_GAP_FT, _px), "the wood shed a ken off a wall"
    assert fs.joined_to_house(laid["bath"], HW, HH), "the bath a room of the house"


def test_the_privy_faces_the_sun_on_its_share_and_takes_an_attested_seat_otherwise() -> None:
    sunny = _lay(("privy",), roll=0.1, ground=(YARD, EAST_BED))["privy"]  # the SE ground open, as an E bed leaves it
    assert sunny[1] > HH / 2 and sunny[0] >= -1e-6, "southeast to south of the house"
    shaded = _lay(("privy",), roll=0.9, ground=(YARD,))["privy"]  # past the 72.7% share: the rolled attested seat, the barn here
    assert not (shaded[0] > HW / 2 and abs(shaded[1] + HH * 0.25) < 1e-6) and sorted(shaded[2:]) == sorted(fs.PRIVY_SIZES_FT[int(0.9 * 16)]), (
        "an attested seat a hamlet farm has (no barn, feature 328), at the household's rolled size"
    )


def test_the_privy_and_the_bath_room_take_the_households_rolled_size_and_the_notes_carry_it() -> None:
    """Feature 280 (research/homesteads/750, 740): the privy one of the Kakimochi table's sixteen, the bath room 6 ft out by
    6-12 ft along - each off the household's roll - and the notes the drawing reads carry each size and the bath's wall."""
    notes: dict = {}
    laid = _lay(("privy", "bath", "coop"), roll=0.3, notes=notes)
    assert notes["ft"]["privy"] == fs.PRIVY_SIZES_FT[int(0.3 * 16)] and notes["ft"]["bath"] == (8.0, fs.BATH_DEPTH_FT) and notes["ft"]["coop"] == (5.0, 5.0)
    assert sorted(laid["bath"][2:]) == [6.0, 8.0] and notes["bath_seat"] in fs.BATH_WALLS
    assert fs.fixture_ft("privy", fs.FixtureForms()) == (6.0, 6.0) and fs.fixture_ft("bath", fs.FixtureForms()) == (6.0, 6.0), "the one-ken default"
    assert fs.privy_sun_reach_ft(6.0, 6.0) == fs.PRIVY_SUN_MAX_FT and fs.privy_sun_reach_ft(24.0, 12.0) == fs.PRIVY_SUN_MAX_FT


def test_the_heap_stands_beyond_the_privy_and_without_one_at_the_back() -> None:
    laid = _lay(("privy", "manure"), roll=0.9)
    p, m = laid["privy"], laid["manure"]
    assert abs(m[0] - p[0]) > 1.0 or abs(m[1]) > abs(p[1]), "beyond the privy"
    # feature 328 (0042: "on the side away from the house"): a privy on the house's east flank sends its heap further east,
    # along the line from the house's center to the privy's, never sideways
    flank = (HW / 2 + 3.5 + 6.0, -HH * 0.25, 12.0, 24.0)
    heap = fs._seats("manure", HW, HH, 6.0, 6.0, 3.5, None, flank, lambda _s: 0.5, 0.5, fs.FixtureForms(), _px)[0]
    assert heap[0] > flank[0] + 6.0, "east, beyond the flank privy"
    assert (heap[0] ** 2 + heap[1] ** 2) > (flank[0] ** 2 + flank[1] ** 2), "further from the house than the privy"
    alone = _lay(("manure",), forms=fs.FixtureForms(manure_form="pit"), ground=(YARD, EAST_BED))["manure"]
    assert alone[1] < 0.0 and (alone[2], alone[3]) == (fs.PIT_FT, fs.PIT_FT), "the pit glyph at the back wall"


def test_the_bath_is_a_room_joined_to_the_house_on_an_attested_wall_or_refused() -> None:
    """Feature 280 M22 (research/homesteads/740): the bath abuts the house - beside the main door, at the stable wing's end
    wall or the floored rooms' - never a building in the yard. The yard covers the front wall here, so a `main_door` hamlet's
    room falls to the stable end (the garden takes the +x end); a house with all three walls taken refuses it by name."""
    notes: dict = {}
    bath = _lay(("bath",), notes=notes)["bath"]
    assert fs.joined_to_house(bath, HW, HH) and notes["bath_seat"] == "stable_end" and bath[0] == pytest.approx(-(HW / 2 + 3.0))
    free = _lay(("bath",), ground=(), forms=fs.FixtureForms(bath_stable_share=0.0), notes=notes)["bath"]
    assert fs.joined_to_house(free, HW, HH) and notes["bath_seat"] == "main_door" and free[1] == pytest.approx(HH / 2 + 3.0), "against the front wall"
    ends = [(HW / 2 + 10.0, 0.0, 16.0, 3 * HH), (-(HW / 2 + 10.0), 0.0, 16.0, 3 * HH), (0.0, HH / 2 + 8.0, 3 * HW, 10.0)]
    with pytest.raises(ValueError, match="bath room"):
        _lay(("bath",), ground=ends)
    slid = _lay(("bath",), ground=[(-HW / 2 - 3.0, 0.0, 6.0, 4.0), (HW / 2 + 10.0, 0.0, 16.0, 3 * HH), (0.0, HH / 2 + 8.0, 3 * HW, 10.0)], notes=notes)["bath"]
    assert fs.joined_to_house(slid, HW, HH) and notes["bath_seat"] == "stable_end" and abs(slid[1]) > HH * 0.25, "slid along its wall past the recorded seats"
    assert not fs.joined_to_house((0.0, HH / 2 + 3.5 + 3.0, 8.0, 6.0), HW, HH) and not fs.joined_to_house((0.0, 0.0, 8.0, 6.0), HW, HH), "off the wall, or inside"


def test_the_wood_shed_stands_a_ken_off_a_wall_of_its_house_or_is_refused() -> None:
    """Feature 280 M21, as feature 328 left it (research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: behind or
    beside the house, never the front yard, about a ken off a wall): offered every place a ken off the HOUSE's walls - never
    the byre's or the retirement house's, never the front wall's, never a pace further out - and a house with no such place
    refuses it by name."""
    walls = fs.steading_rects(HW, HH, "N", 1.0)
    back_and_east = [(0.0, -HH - 6.0, 3 * HW, HH * 0.9), (HW + 6.0, 0.0, HW * 0.9, 3 * HH)]
    shed = _lay(("woodpile",), ground=back_and_east)["woodpile"]
    assert fs.shed_off_a_wall(shed, walls, fs.WALL_GAP_FT, _px) and sorted(shed[2:]) == [12.0, 24.0] and shed[0] < -HW / 2, "the west flank"
    assert fs.clears(shed, [HOUSE], fs.WALL_GAP_FT + fs.WOODSHED_STEP_FT - 1e-6), "a ken off the house"
    with pytest.raises(ValueError, match="wood shed"):  # back, east and west taken: the front wall is never offered
        _lay(("woodpile",), ground=[*back_and_east, (-HW - 6.0, 0.0, HW * 0.9, 3 * HH)])
    byre = (-(HW / 2 + 3.0 + 5.5), 0.0, 11.0, 16.0)
    assert not fs.shed_off_a_wall((byre[0] - 5.5 - 3.5 - 6.0 - 6.0, 0.0, 12.0, 24.0), walls, fs.WALL_GAP_FT, _px), "off the byre's wall, not the house's"
    pace = (0.0, -(HH / 2 + 3.5 + 6.0 + 6.0 + 4.0), 24.0, 12.0)
    assert not fs.shed_off_a_wall(pace, walls[:1], fs.WALL_GAP_FT, _px), "a pace past the ken"
    assert not fs.shed_off_a_wall((0.0, HH / 2 + 3.5 + 6.0 + 6.0, 24.0, 12.0), walls[:1], fs.WALL_GAP_FT, _px), "the front yard"
    assert not fs.shed_off_a_wall((0.0, -(HH / 2 + 3.5 + 6.0), 24.0, 12.0), walls[:1], fs.WALL_GAP_FT, _px), "under a ken off"


def test_the_woodshed_stands_a_ken_off_and_the_shrine_in_its_rolled_corner() -> None:
    laid = _lay(("woodpile", "shrine"), roll=0.1)
    shed = laid["woodpile"]
    assert sorted(shed[2:]) == [12.0, 24.0] and not fs.against_a_wall(shed, fs.steading_rects(HW, HH, "N", 1.0), fs.WALL_GAP_FT)
    shrine = laid["shrine"]
    assert shrine[0] < -HW / 2 and shrine[1] < -HH / 2, "NW, the likeliest corner, rolled first"


def test_a_crowded_steading_steps_its_fixtures_outward_and_the_persimmon_further() -> None:
    ring = [(0.0, 0.0, HW + 60.0, HH + 60.0)]  # everything within 30 ft of the house is taken
    laid = _lay(("coop", "persimmon"), roofs=(HOUSE,), ground=ring)
    assert fs.clears(laid["coop"], ring, fs.WALL_GAP_FT - 1e-6) and fs.clears((laid["persimmon"][0], laid["persimmon"][1], 4.0, 4.0), ring, 2.0 - 1e-6)
    front = _lay(("persimmon",), roll=0.9, forms=fs.FixtureForms(persimmon_front=0.95))["persimmon"]
    back = _lay(("persimmon",), roll=0.99, forms=fs.FixtureForms(persimmon_front=0.2))["persimmon"]
    assert front[1] > 0.0 and back[1] < 0.0, "the dooryard, else behind the house - never the flank"


def test_the_persimmon_keeps_out_of_its_yards_and_beds_sun_at_every_rake() -> None:
    """GM 2026-10-02: a front drying yard's sun ground covers the whole dooryard, so the tree goes behind the house; with
    only a bed far off, the front seat stands. Held at every rake the house may be drawn at."""
    turns = fs.sun_turns(-41.25, 18.75)
    front = fs.FixtureForms(persimmon_front=0.95)
    crown = fs.lay_fixtures(("persimmon",), HW, HH, [HOUSE], [YARD, GARDEN], YARD, False, lambda salt: 0.1, front, _px, shade=50.0, turns=turns)["persimmon"]
    assert crown[1] < 0.0, "behind the house"
    for t in turns:
        th = fs.math.radians(t)
        c, s = fs.math.cos(th), fs.math.sin(th)
        x, y = crown[0] * c - crown[1] * s, crown[0] * s + crown[1] * c
        for q in (YARD, GARDEN):
            qx, qy = q[0] * c - q[1] * s, q[0] * s + q[1] * c
            qw, qh = q[2] * abs(c) + q[3] * abs(s), q[2] * abs(s) + q[3] * abs(c)
            assert not crown_shades(x, y, crown[2] / 2, (qx, qy, qw, qh), 50.0), (t, q)
    far_bed = (HW / 2 + 200.0, 0.0, 14.0, 24.0)
    alone = fs.lay_fixtures(("persimmon",), HW, HH, [HOUSE], [far_bed], YARD, False, lambda salt: 0.1, front, _px, shade=50.0, turns=turns)["persimmon"]
    assert alone[1] > 0.0, "no yard's sun to keep: the dooryard in front"
    assert fs.sun_turns(0.0, 0.0) == (0.0, 0.0) and fs.sun_turns(-5.0, 5.0) == (-5.0, 0.0, 5.0)


def test_the_helpers_read_as_they_say() -> None:
    assert fs.weighted((("a", 0.3), ("b", 0.3)), 0.99) == "b" and fs.weighted((("a", 0.3), ("b", 0.3)), 0.1) == "a"
    assert fs.along(0.0, 4.0) == [0] and fs.along(9.0, 4.0) == [0, -4, 4, -8, 8, -9.0, 9.0] and fs.along(8.0, 4.0) == [0, -4, 4, -8, 8]
    assert fs.fixture_size("woodpile", fs.FixtureForms(), _px) == (24.0, 12.0) and fs.fixture_size("persimmon", fs.FixtureForms(), _px)[0] == 23.0
    assert len(fs.steading_rects(HW, HH, "W", 1.0)) == 2 and len(fs.steading_rects(HW, HH, None, 1.0)) == 1
    assert fs.steading_rects(HW, HH, "N", 1.0)[1] == kura_rect(HW, HH, "N", 1.0) == (0.0, -0.675 * HH, 0.46 * HW, 0.45 * HH), "the drawn annex (feature 280 M18)"
    assert list(fs.outward([(0.0, 0.0, 2.0, 2.0)], 8.0, 1)) == [(0.0, 0.0, 2.0, 2.0)], "a seat at the center stays"
    assert fs.world_fixtures({"bath": 1, "privy": 2}) == [("bath", 1), ("privy", 2)]


def test_the_retirement_house_stands_off_the_back_wall_or_a_flank_in_its_rolled_order() -> None:
    back = _lay(("retirement",), roll=0.1, ground=(YARD,), roofs=(HOUSE,))["retirement"]
    east = _lay(("retirement",), roll=0.5, ground=(YARD,), roofs=(HOUSE,))["retirement"]
    assert back[1] < -HH / 2 and (back[2], back[3]) == (18.0, 15.0)
    assert east[0] > HW / 2 and (east[2], east[3]) == (15.0, 18.0), "turned along its flank"


def test_the_first_clear_seat_and_the_sun_sector_answer_as_they_were_written() -> None:
    """`_first` writes `clears` inline and `_sun_sector` builds the privy's sun seats once: over random seats and parts the
    first clear seat is the one the plain scan finds (none included), and the sector is the list built seat by seat."""
    import math
    import random

    rng = random.Random(8)
    found = 0
    for _ in range(400):
        taken = [(rng.uniform(-40, 40), rng.uniform(-40, 40), rng.uniform(2, 40), rng.uniform(2, 40)) for _ in range(rng.randint(0, 6))]
        seats = [(rng.uniform(-60, 60), rng.uniform(-60, 60), rng.uniform(2, 12), rng.uniform(2, 12)) for _ in range(rng.randint(0, 12))]
        g = rng.choice((0.0, 3.5))
        want = next((q for q in seats if all(abs(q[0] - t[0]) >= (q[2] + t[2]) / 2 + g or abs(q[1] - t[1]) >= (q[3] + t[3]) / 2 + g for t in taken)), None)
        assert fs._first(seats, taken, g) == want
        assert all(fs.clears(q, taken, g) == all(abs(q[0] - t[0]) >= (q[2] + t[2]) / 2 + g or abs(q[1] - t[1]) >= (q[3] + t[3]) / 2 + g for t in taken) for q in seats)
        found += want is not None
    assert 40 < found < 400
    radii = (18.0, 22.0, 26.0)
    plain = [(rr * math.sin(math.radians(b / 10.0)), -rr * math.cos(math.radians(b / 10.0)), 4.0, 5.0) for rr in radii for b in range(1125, 2026, 75)]
    assert list(fs._sun_sector(4.0, 5.0, radii)) == plain


def test_a_persimmon_with_no_seat_in_its_dooryard_is_not_laid() -> None:
    """Feature 315 (cohort seed 23): the persimmon's paces stop at the dooryard - its crown's edge within
    `PERSIMMON_DOORYARD_FT` of the house - and a farm whose dooryard is all taken keeps none (its other fixtures still laid),
    where it once walked 80 ft out onto the row's street."""
    ring = [(0.0, 0.0, HW + 100.0, HH + 100.0)]  # everything within 50 ft of the house is taken
    laid = _lay(("coop", "persimmon"), roofs=(HOUSE,), ground=ring)
    assert "coop" in laid and "persimmon" not in laid
    assert fs.in_dooryard(0.0, HH / 2 + 41.0, 11.5, HW, HH, 30.0), "its crown's edge 29.5 ft off the front wall"
    assert not fs.in_dooryard(0.0, HH / 2 + 42.0, 11.5, HW, HH, 30.0), "30.5 ft off"
    assert fs.in_dooryard(HW / 2 + 20.0, -(HH / 2 + 20.0), 11.5, HW, HH, 30.0), "off a corner, by the diagonal"


def test_a_grove_farms_persimmon_may_stand_in_its_own_grove_and_nothing_else_may() -> None:
    """Feature 315: the traditional igune held "a few fruit trees" among its trees, so on a grove farm (`fruit`, its bands) the
    persimmon may stand in its own grove behind the house, within the dooryard; no other fixture stands in a band, and the
    persimmon is never set on the house's flank."""
    north = (0.0, -(HH / 2 + 3.0 + 22.0), HW + 60.0, 44.0)  # the windward band, hard behind a narrow service strip
    sunny = [YARD, GARDEN]
    args = (HW, HH, [HOUSE], sunny, YARD, False, lambda salt: 0.1, fs.FixtureForms(persimmon_front=0.05), _px, None, None, 50.0, (0.0,))
    laid = fs.lay_fixtures(("coop", "persimmon"), *args, [north])
    tree = laid["persimmon"]
    assert tree[1] < -HH / 2 and fs.in_dooryard(tree[0], tree[1], tree[2] / 2, HW, HH, fs.PERSIMMON_DOORYARD_FT), "behind, in the dooryard"
    assert fs.clears(laid["coop"], [north], 0.0), "the coop stands outside the band"
    held = fs.lay_fixtures(("persimmon",), *args[:2], [HOUSE, north], *args[3:])
    assert "persimmon" not in held or held["persimmon"][1] != tree[1], "held off the band, it does not take that seat"


def test_the_bath_room_rolls_among_its_three_walls() -> None:
    """Feature 328 (0044: most baths beyond the stable wing, a few joined to the floored rooms, the rest by the main door): the
    three walls each house rolls among, the floored rooms no longer only a fallback."""
    forms = fs.FixtureForms()
    assert fs.bath_wall(0.1, forms) == "stable_end" and fs.bath_wall(0.81, forms) == "floored_rooms" and fs.bath_wall(0.9, forms) == "main_door"
    assert {fs.bath_wall(k / 100, forms) for k in range(100)} == set(fs.BATH_WALLS)


def test_the_privy_stays_within_48_ft_of_its_house_or_is_refused() -> None:
    """Feature 328 (0047: a privy stands no more than 48 ft from its house; past that privies stray out of their own
    farmsteads): the outward paces never carry it past the reach, and a farmstead with nothing free within it refuses it."""
    assert fs.within_reach_of((0.0, HH / 2 + 40.0, 6.0, 6.0), HOUSE, 48.0) and not fs.within_reach_of((0.0, HH / 2 + 50.0, 6.0, 6.0), HOUSE, 48.0)
    corner = (HW / 2 + 40.0, HH / 2 + 40.0, 6.0, 6.0)  # 37-43 ft out on each axis, its far corner about 61 ft off the house's corner
    assert not fs.within_reach_of(corner, HOUSE, 48.0), "measured true off a corner, never as a box"
    privy = _lay(("privy",))["privy"]
    assert fs.within_reach_of(privy, HOUSE, 48.0)
    with pytest.raises(ValueError, match="privy"):
        _lay(("privy",), ground=[(0.0, 0.0, HW + 120.0, HH + 120.0)])


def test_a_hamlet_farm_has_no_barn_so_its_privy_never_takes_the_barn_seat() -> None:
    """Feature 328 (0047 puts the privy "inside the barn", a building of its own; a hamlet draws no barn): the barn's share
    goes to the yard, the front and the stable at their own weights - every roll lands on one of the three."""
    forms = fs.FixtureForms()
    for k in range(20):
        u = k / 20
        seats = fs._seats("privy", HW, HH, 6.0, 6.0, 3.5, None, None, lambda _s: 0.99, u, forms, _px)
        assert all(not (q[0] > HW / 2 and abs(q[1] + HH * 0.25) < 1e-6) for q in seats), "no seat at the house's east end"
        assert len(seats) == 3
