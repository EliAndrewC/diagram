"""Feature 287, homes H32 (plan M5 and D9): a household's farmstead fixtures laid as parts of its bundle
(`settlement/homestead_parts/fixture_seats.py`) - every kind laid, none on another part, each in its attested form."""

import pytest

from l7r.diagram.settlement.homestead_parts import fixture_seats as fs

HW, HH = 46.0, 28.0
HOUSE = (0.0, 0.0, HW, HH)
KURA = (0.0, -0.60 * HH, 0.46 * HW, 0.30 * HH)
YARD = (0.0, HH / 2 + 3.0 + 12.0, 30.0, 24.0)
GARDEN = (HW / 2 + 3.0 + 7.0, 0.0, 14.0, 24.0)
ALL = ("privy", "woodpile", "manure", "bath", "coop", "shrine", "persimmon", "retirement")


def _px(v: float) -> float:
    return v


def _lay(kinds=ALL, forms=None, roofs=(HOUSE, KURA), ground=(YARD, GARDEN), roll=0.3, annex=None):  # type: ignore[no-untyped-def]
    return fs.lay_fixtures(kinds, HW, HH, list(roofs), list(ground), YARD, True, lambda salt: roll, forms or fs.FixtureForms(), _px, annex)


def test_every_kind_a_household_keeps_is_laid_clear_of_every_part_and_of_each_other() -> None:
    laid = _lay()
    assert set(laid) == set(ALL)
    solid = [(k, r) for k, r in laid.items() if k != "persimmon"]
    for k, r in solid:
        assert fs.clears(r, [HOUSE, KURA, YARD, GARDEN], fs.WALL_GAP_FT - 1e-6), k
        assert fs.clears(r, [q for kk, q in solid if kk != k], fs.WALL_GAP_FT - 1e-6), k
    crown = laid["persimmon"]
    assert fs.clears(crown, [HOUSE, KURA, *(r for _k, r in solid)], fs.CANOPY_PAD - 1e-6), "no crown over a roof"
    assert fs.clears((crown[0], crown[1], 4.0, 4.0), [YARD, GARDEN], 2.0 - 1e-6), "the trunk stands off the yard and the beds"
    assert fs.against_a_wall(laid["woodpile"], fs.steading_rects(HW, HH, "N"), fs.WALL_GAP_FT), "the eaves stack at a wall"


def test_the_privy_faces_the_sun_on_its_share_and_takes_an_attested_seat_otherwise() -> None:
    sunny = _lay(("privy",), roll=0.1)["privy"]
    assert sunny[1] > HH / 2 and sunny[0] >= -1e-6, "southeast to south of the house"
    shaded = _lay(("privy",), roll=0.9, ground=(YARD,))["privy"]  # past the 72.7% share: the rolled attested seat, the barn here
    assert shaded[0] > HW / 2 and (shaded[2], shaded[3]) == (6.0, 6.0)


def test_the_heap_stands_beyond_the_privy_and_without_one_at_the_back() -> None:
    laid = _lay(("privy", "manure"), roll=0.9)
    p, m = laid["privy"], laid["manure"]
    assert abs(m[0] - p[0]) > 1.0 or abs(m[1]) > abs(p[1]), "beyond the privy"
    alone = _lay(("manure",), forms=fs.FixtureForms(manure_form="pit"))["manure"]
    assert alone[1] < 0.0 and (alone[2], alone[3]) == (fs.PIT_FT, fs.PIT_FT), "the pit glyph at the back wall"


def test_the_bath_stands_beside_the_yard_or_joined_by_its_corridor() -> None:
    front = _lay(("bath",))["bath"]
    assert front[1] >= YARD[1] - 1e-6 and abs(front[0]) > YARD[2] / 2, "beside the work yard"
    laid = _lay(("bath",), forms=fs.FixtureForms(bath_seat="corridor"))
    bath, corridor = laid["bath"], laid["bath_corridor"]
    assert abs(abs(corridor[1]) - (HH / 2 + fs.BATH_CORRIDOR_FT / 2)) < 1e-6 or abs(abs(corridor[0]) - (HW / 2 + fs.BATH_CORRIDOR_FT / 2)) < 1e-6
    assert fs.clears(bath, [HOUSE, KURA], fs.WALL_GAP_FT - 1e-6)
    boxed = [(0.0, -HH, 3 * HW, HH * 0.9), (HW, 0.0, HW * 0.9, 3 * HH), (-HW, 0.0, HW * 0.9, 3 * HH), (0.0, HH, 3 * HW, HH * 0.9)]
    with pytest.raises(ValueError, match="joined bath"):
        _lay(("bath",), forms=fs.FixtureForms(bath_seat="corridor"), ground=boxed)


def test_the_eaves_stack_is_offered_every_wall_and_refused_where_there_is_none() -> None:
    byre = (-(HW / 2 + 3.0 + 5.5), 0.0, 11.0, 16.0)
    walls_taken = [(0.0, -HH, 3 * HW, HH * 0.9), (HW, 0.0, HW * 0.9, 3 * HH), (0.0, HH, 3 * HW, HH * 0.9)]
    stack = _lay(("woodpile",), ground=walls_taken, annex=byre)["woodpile"]
    assert fs.against_a_wall(stack, [*fs.steading_rects(HW, HH, "N"), byre], fs.WALL_GAP_FT), "against the byre's wall or the house's"
    with pytest.raises(ValueError, match="eaves stack"):
        _lay(("woodpile",), ground=[*walls_taken, (-HW, 0.0, HW * 0.9, 3 * HH)])


def test_the_woodshed_stands_a_ken_off_and_the_shrine_in_its_rolled_corner() -> None:
    laid = _lay(("woodpile", "shrine"), forms=fs.FixtureForms(woodpile_form="shed"), roll=0.1)
    shed = laid["woodpile"]
    assert (shed[2], shed[3]) in ((12.0, 9.0), (9.0, 12.0)) and not fs.against_a_wall(shed, fs.steading_rects(HW, HH, "N"), fs.WALL_GAP_FT)
    shrine = laid["shrine"]
    assert shrine[0] < -HW / 2 and shrine[1] < -HH / 2, "NW, the likeliest corner, rolled first"


def test_a_crowded_steading_steps_its_fixtures_outward_and_the_persimmon_further() -> None:
    ring = [(0.0, 0.0, HW + 60.0, HH + 60.0)]  # everything within 30 ft of the house is taken
    laid = _lay(("coop", "persimmon"), roofs=(HOUSE,), ground=ring)
    assert fs.clears(laid["coop"], ring, fs.WALL_GAP_FT - 1e-6) and fs.clears((laid["persimmon"][0], laid["persimmon"][1], 4.0, 4.0), ring, 2.0 - 1e-6)
    front = _lay(("persimmon",), roll=0.9, forms=fs.FixtureForms(persimmon_front=0.95))["persimmon"]
    back = _lay(("persimmon",), roll=0.99, forms=fs.FixtureForms(persimmon_front=0.2))["persimmon"]
    assert front[1] > 0.0 and back[1] < 0.0, "the dooryard, else behind the house - never the flank"


def test_the_helpers_read_as_they_say() -> None:
    assert fs.weighted((("a", 0.3), ("b", 0.3)), 0.99) == "b" and fs.weighted((("a", 0.3), ("b", 0.3)), 0.1) == "a"
    assert fs.along(0.0, 4.0) == [0] and fs.along(9.0, 4.0) == [0, -4, 4, -8, 8, -9.0, 9.0] and fs.along(8.0, 4.0) == [0, -4, 4, -8, 8]
    assert fs.fixture_size("woodpile", fs.FixtureForms(), _px) == (10.0, 3.5) and fs.fixture_size("persimmon", fs.FixtureForms(), _px)[0] == 23.0
    assert len(fs.steading_rects(HW, HH, "W")) == 2 and len(fs.steading_rects(HW, HH, None)) == 1
    assert list(fs.outward([(0.0, 0.0, 2.0, 2.0)], 8.0, 1)) == [(0.0, 0.0, 2.0, 2.0)], "a seat at the center stays"
    assert fs.world_fixtures({"bath_corridor": 1, "privy": 2}) == [("privy", 2), ("bath_corridor", 1)]


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
