"""Feature 287, plan M5 (homes H08, H17, H45): one lot per household, keyed on seat order."""

from __future__ import annotations

import statistics

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling.lot import FARMHOUSE_MAX_ASPECT, KURA_SHARE, HouseholdLots, house_aspect_bound, quota_carriers, quota_member, size_ladder


def test_a_quota_closes_at_the_rounded_share_for_every_count() -> None:
    for p in (0.2993, 0.35, 0.5):
        for n in range(1, 41):
            assert sum(quota_member(j, p) for j in range(n)) == round(n * p + 1e-9) or abs(sum(quota_member(j, p) for j in range(n)) - n * p) <= 0.5


def test_the_kura_count_is_the_share_of_the_households_whatever_the_seed() -> None:
    """H45: n households carry exactly round(n x 0.2993) kura - the count the positional roll under-delivered 2.2x."""
    for seed in range(20):
        for n in range(5, 41):
            got = sum(quota_carriers(seed, "kura", n, KURA_SHARE))
            assert abs(got - n * KURA_SHARE) <= 0.5


def test_the_size_ladder_spreads_the_footprints_and_stays_a_farmhouse() -> None:
    """H17 and H08: at least 20% of the footprints differ from the median by more than 5%, and no rung runs past 2.7:1."""
    assert house_aspect_bound() <= FARMHOUSE_MAX_ASPECT
    for seed in range(50):
        for n in range(3, 41):
            rungs = size_ladder(seed, n)
            areas = [46 * lf * 28 * df for lf, df in rungs]
            med = statistics.median(areas)
            assert sum(abs(a - med) / med > 0.05 for a in areas) >= 0.2 * n
            assert all(46 * lf / (28 * df) <= FARMHOUSE_MAX_ASPECT for lf, df in rungs)
    assert size_ladder(1, 0) == []


def test_a_household_keeps_its_lot_wherever_it_is_seated() -> None:
    lots = HouseholdLots(7, 12)
    assert lots.lot(-1) is None and lots.lot(12) is None
    assert [lots.lot(k) for k in range(12)] == [HouseholdLots(7, 12).lot(k) for k in range(12)]
    assert sum(lots.lot(k)[2] for k in range(12)) == round(12 * KURA_SHARE)  # type: ignore[index]


def _village() -> Settlement:
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=12, down_deg=90, water_flow=90, nucleated=True)
    s._nucleated = True
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}
    return s


def test_a_row_of_seats_at_one_pitch_carries_its_share_of_kura() -> None:
    """H45's aliasing case: twelve seats along one row at one pitch, each household with its lot - 4 kura (round(12 x
    0.2993)), and each house drawn at its rung of the ladder."""
    s = _village()
    s._lots = HouseholdLots(3, 12)
    for k in range(12):
        assert s.try_place(150.0 + k * 100.0, 700.0, "plain")
    houses = s.M["houses"]
    assert sum(1 for h in houses if h["shed"]) == 4
    assert [(round(h["w"] / 46, 6), round(h["h"] / 28, 6)) for h in houses] == [(round(a, 6), round(b, 6)) for a, b in size_ladder(3, 12)]


def test_an_explicit_size_past_the_minka_norm_is_refused_at_the_call() -> None:
    s = _village()
    with pytest.raises(ValueError, match="past 2.7:1"):
        s.try_place(700.0, 700.0, "plain", size=(80, 20))
    assert s.try_place(700.0, 700.0, "plain", size=(46, 28))


@pytest.mark.parametrize("form", ["courtyard", "yard_shed"])
def test_a_keepers_byre_is_a_part_of_its_bundle_and_every_one_is_drawn(form: str) -> None:
    """H06: the byre is reserved inside the keeper's homestead box at seat time, so `draft_byres` draws every keeper's
    stall where it was reserved - the count is the lots' quota, however full the courtyards are by then."""
    from l7r.diagram.settlement.shrines_wells.byres import household_byre_form

    s = _village()
    s.pin_knob("byre_form", form)
    s._byre_form, share = household_byre_form(s)
    assert s._byre_form == form and 0.35 <= share <= 0.5
    s._lots = HouseholdLots(3, 8, 0.5)
    for k in range(8):
        assert s.try_place(150.0 + k * 130.0, 700.0, "plain")
    keepers = [h for h in s.M["houses"] if h.get("byre")]
    assert len(keepers) == 4
    for h in keepers:
        bx, by, bw, bh = h["byre"]["box"]
        ex, ey, ew, eh = h["geom"]["bbox"]
        e = 1e-6
        assert ex - ew / 2 - e <= bx - bw / 2 and bx + bw / 2 <= ex + ew / 2 + e and ey - eh / 2 - e <= by - bh / 2 and by + bh / 2 <= ey + eh / 2 + e, "inside its envelope"
    # the courtyards filled after the seating: nothing is sought, every reserved stall is drawn
    s.placed.extend([(h["x"], h["y"] + 60.0, 200.0, 60.0) for h in s.M["houses"]])
    got = s.draft_byres()
    assert len(got) == 4 == s.M["meta"]["byre_target"] and all(b["of"] for b in s.M["byres"])


def test_a_commons_form_or_a_dispersed_seating_lays_no_byre_in_a_bundle() -> None:
    from l7r.diagram.settlement.shrines_wells.byres import household_byre_form

    s = _village()
    s.pin_knob("byre_form", "detached_commons")
    assert household_byre_form(s) == (None, 0.0)
    s._nucleated = False
    assert household_byre_form(s) == (None, 0.0)
