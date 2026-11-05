"""Feature 287, plan M5 (homes H08, H17, H45): one lot per household, keyed on seat order."""

from __future__ import annotations

import statistics

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling.lot import FARMHOUSE_MAX_ASPECT, KURA_SHARE, HouseholdLots, house_aspect_bound, quota_carriers, quota_member, size_ladder


def test_a_quota_closes_at_the_rounded_share_for_every_count() -> None:
    for p in (0.2993, 0.35, 0.5):
        for n in range(1, 41):
            assert sum(quota_member(j, p) for j in range(n)) == round(n * p + 1e-9) or abs(sum(quota_member(j, p) for j in range(n)) - n * p) <= 0.5


def test_the_kura_count_is_the_share_of_the_households_whatever_the_seed() -> None:
    """H45: n households carry exactly round(n x `KURA_SHARE`) kura - the count the positional roll under-delivered 2.2x (the
    share one farm in eight since feature 280 M20)."""
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


def test_a_commons_form_or_a_dispersed_seating_lays_no_byre_in_a_bundle() -> None:
    from l7r.diagram.settlement.shrines_wells.byres import household_byre_form

    s = _village()
    s.pin_knob("byre_form", "detached_commons")
    assert household_byre_form(s) == (None, 0.0)
    s._nucleated = False
    assert household_byre_form(s) == (None, 0.0)


def test_the_storehouse_goes_to_the_largest_houses_first() -> None:
    """Feature 293 (research/questions/0040-farm-storehouses-kura.html): the kura count is the quota's, and the houses that carry it are exactly the
    largest by the main house's footprint, on every seed and count."""
    for seed in range(30):
        for n in range(5, 25):
            lots = HouseholdLots(seed, n)
            areas = [lf * df for lf, df in lots.sizes]
            carriers = [a for a, k in zip(areas, lots.kura, strict=True) if k]
            rest = [a for a, k in zip(areas, lots.kura, strict=True) if not k]
            assert len(carriers) == sum(quota_carriers(seed, "kura", n, KURA_SHARE))
            assert not carriers or not rest or min(carriers) >= max(rest), (seed, n)
    assert sum(HouseholdLots(3, 16).kura) == 2, "Kakimochi's 2 of 16"
