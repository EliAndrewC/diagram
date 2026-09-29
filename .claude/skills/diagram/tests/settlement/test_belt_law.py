"""Feature 287, woods W16-W19 (plan D8): the windbreak's one predicates and the settle pass that keeps them where the belt
is planted, on constructed belts that include each violating case - a thin stretch, a hole, a crossing, a run break, a
column no seat is admitted in, and a belt the page cuts."""

from __future__ import annotations

import math

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.homestead_parts.belt_law import (
    MIN_BELT_DEPTH_FT,
    BeltReading,
    belt_depths,
    belt_holes,
    on_page,
    reading_of,
    settle_the_belt,
    wind_unit,
)

N = (0.0, -1.0)  # the wind from the north: u is up the sheet, v runs along x
HOUSES = [{"x": float(x), "y": 700.0} for x in range(300, 901, 100)]
BAND = [(250.0, 480.0), (950.0, 480.0), (950.0, 600.0), (250.0, 600.0)]
PAGE = (0.0, 0.0, 2000.0, 2000.0)


def _belt(skip: tuple[float, float] = (0.0, 0.0), thin: tuple[float, float] = (0.0, 0.0)) -> list[tuple[float, float]]:
    """Two rows of crowns 60 ft apart across 300..900, none in `skip` and only the near row in `thin` (x ranges)."""
    out = []
    for x in range(300, 901, 20):
        if skip[0] <= x <= skip[1]:
            continue
        out.append((float(x), 560.0))
        if not thin[0] <= x <= thin[1]:
            out.append((float(x), 500.0))
    return out


def _read(seats, houses=HOUSES, ways=(), reach=None, band=BAND, view=PAGE) -> BeltReading:
    on = [c for c in seats if on_page(c, 14.0, view)]
    off = [c for c in seats if not on_page(c, 14.0, view)]
    return BeltReading(on, off, 14.0, houses, N, ways, view, reach, band)


def test_the_measure_reads_a_thin_stretch_and_a_parted_one() -> None:
    """The measure itself (lifted from the pool test): a two-row block reads its depth, a lone crown reads one crown, and a
    lane through a bin leaves that bin unjudged, while one along the belt's inner face does not; nor is a bin the page's
    edge cuts."""
    m = {
        "meta": {"windward": "N"},
        "houses": [{"x": 0.0, "y": 0.0}],
        "village_groves": [{"role": "windbreak", "r": 10.0, "clumps": [[5.0, -100.0], [5.0, -120.0], [45.0, -100.0], [85.0, -100.0], [85.0, -160.0]], "clumps_offpage": [[125.0, -100.0]]}],
        "lanes": [{"pts": [[85.0, 0.0], [85.0, -200.0]]}, {"pts": [[0.0, -80.0], [90.0, -80.0]]}],
    }
    assert belt_depths(m) == [None, 20.0, None, None]
    assert len(belt_holes(m)) == 3, "three 40 ft openings between single crowns, none of them the lane's"
    assert belt_depths({"houses": [], "village_groves": []}) == [] and belt_holes({"village_groves": [{"role": "copse"}]}) == []
    assert reading_of({"houses": [{"x": 0.0, "y": 0.0}], "village_groves": [{"role": "windbreak", "clumps": []}]}) is None
    assert wind_unit("NW") == (-1.0 / math.sqrt(2.0), -1.0 / math.sqrt(2.0)) and wind_unit("E") == (1.0, 0.0)


def test_a_hole_and_a_one_row_stretch_are_read() -> None:
    rd = _read(_belt(skip=(560.0, 680.0), thin=(400.0, 460.0)))
    assert rd.holes() and rd.thin(), "the violating case: a 140 ft hole and a one-row stretch"
    assert all(d is None or d >= MIN_BELT_DEPTH_FT for d in _read(_belt()).depths()) and not _read(_belt()).holes()


def test_a_way_crossing_the_opening_face_to_face_is_a_crossing_not_a_hole() -> None:
    """W17: a lane across the belt is a declared opening - so long as no more than 30 ft stands open either side of it."""
    lane = [[[620.0, 400.0], [620.0, 700.0]]]
    assert not _read(_belt(skip=(601.0, 639.0)), ways=lane).holes()
    assert all(d is None or d >= MIN_BELT_DEPTH_FT for d in _read(_belt(skip=(601.0, 639.0)), ways=lane).depths())
    assert _read(_belt(skip=(520.0, 720.0)), ways=lane).holes(), "an opening wider than the crossing explains is a hole"


def test_the_stretch_between_two_groups_no_house_stands_before_is_a_run_break() -> None:
    """W19: a cluster in two groups 1,000 ft apart gets a belt in two runs; the stretch between them, beyond the band's
    reach of every house, is not a hole and its empty bins are not judged."""
    houses = [{"x": float(x), "y": 700.0} for x in (100, 200, 300, 1300, 1400, 1500)]
    seats = [(float(x), y) for x in [*range(80, 521, 20), *range(1080, 1521, 20)] for y in (520.0, 560.0)]  # to the reach
    band = [(50.0, 480.0), (1550.0, 480.0), (1550.0, 600.0), (50.0, 600.0)]
    assert _read(seats, houses=houses, band=band).holes(), "without a reach the opening is a hole"
    rd = _read(seats, houses=houses, reach=250.0, band=band)
    assert not rd.holes() and all(d is None or d >= MIN_BELT_DEPTH_FT for d in rd.depths())
    assert not _read(seats, houses=houses, reach=250.0, band=()).holes(), "with no band recorded, the crowns' lee line is read"


def test_the_settle_deepens_the_thin_stretch_and_closes_the_hole() -> None:
    got: list[tuple[float, float]] = []

    def seat(x: float, y: float) -> tuple[float, float]:
        got.append((round(x, 1), round(y, 1)))
        return got[-1]

    out = settle_the_belt(_belt(skip=(560.0, 680.0), thin=(400.0, 460.0)), r=14.0, houses=HOUSES, wind=N, ways=(), page=lambda _s: PAGE, band=BAND, seat=seat)
    rd = _read(out)
    assert got and not rd.thin() and not rd.holes()
    assert len(out) >= len(_belt(skip=(560.0, 680.0), thin=(400.0, 460.0))), "repaired by planting, not by ending the belt"


def test_where_no_seat_is_admitted_the_belt_ends_and_keeps_its_longer_side() -> None:
    """D8: a column no seat is admitted in ends the belt there; the longer run is kept, and it passes every predicate."""
    start = _belt(skip=(700.0, 780.0))
    out = settle_the_belt(start, r=14.0, houses=HOUSES, wind=N, ways=(), page=lambda _s: PAGE, band=BAND, seat=lambda _x, _y: None)
    rd = _read(out)
    assert out and not rd.thin() and not rd.holes()
    assert max(x for x, _y in out) < 700.0, "the shorter side, east of the hole, is the one taken off"
    thin_start = _belt(thin=(560.0, 640.0))
    out = settle_the_belt(thin_start, r=14.0, houses=HOUSES, wind=N, ways=(), page=lambda _s: PAGE, band=(), seat=lambda _x, _y: None)
    assert out and not _read(out, band=()).thin()


def test_the_settle_trims_the_hook_on_the_crowns_the_page_shows() -> None:
    """W18's residual: the trim reads the crowns on the page, and a crown off it is not asked about."""
    seen: list[int] = []

    def trim(cs: list[tuple[float, float]]) -> list[tuple[float, float]]:
        seen.append(len(cs))
        return cs[:-1] if len(cs) > 40 else cs

    view = (0.0, 0.0, 700.0, 2000.0)  # the page stops at x 700: the crowns east of it are off it
    start = _belt()
    out = settle_the_belt(start, r=14.0, houses=HOUSES, wind=N, ways=(), page=lambda _s: view, band=BAND, seat=lambda _x, _y: None, trim=trim)
    shown = [c for c in out if on_page(c, 14.0, view)]
    assert seen[0] == sum(1 for c in start if on_page(c, 14.0, view)) and len(shown) == 40
    assert len(out) - len(shown) == len(start) - seen[0], "no crown off the page was trimmed"
    assert settle_the_belt(start, r=14.0, houses=HOUSES, wind=N, ways=(), page=lambda _s: PAGE, band=BAND, seat=lambda _x, _y: None, trim=lambda _cs: []) == []


def test_village_grove_plants_the_belt_deep_whole_and_within_reach() -> None:
    """The placer, the violating case: a wellhead's wide keep-out in the band's middle and a reach that cuts the band's far
    corners. Every crown stands within the reach of a farmhouse, and the belt on its page has no thin stretch and no hole."""
    s = Settlement(1400, 1200, seed=5)
    s.meta(name="W", scale="hamlet", ftpx=1, down_deg=90)
    s.M["houses"] = [{"x": float(x), "y": 700.0, "w": 30.0, "h": 24.0, "rot": 0} for x in range(300, 1101, 100)]
    s.M["wells"] = [{"x": 700.0, "y": 540.0, "r": 20.0, "vr": 12.0}]
    band = [(250.0, 470.0), (1150.0, 470.0), (1150.0, 600.0), (250.0, 600.0)]
    pts = [(h["x"], h["y"]) for h in s.M["houses"]]
    n = s.village_grove(band, role="windbreak", near=(pts, 200.0), wind=N, page=lambda _s: PAGE, reach=200.0)
    g = s.M["village_groves"][0]
    assert n and all(min(math.dist(c, p) for p in pts) <= 200.0 for c in g["clumps"])
    rd = BeltReading(g["clumps"], [], g["r"], s.M["houses"], N, [], PAGE, 200.0, band)
    assert not rd.thin() and not rd.holes()


def test_the_settling_seat_asks_the_fills_own_tests_but_the_outline(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The seat `village_grove` hands the settle: outside the `within` window, on a wellhead's keep-out, or on a crown
    already down it is refused; past the band's outline (a pushed-back column) it is admitted, at the record's grain."""
    from l7r.diagram.settlement.homestead_parts import stands

    answers: list[object] = []

    def fake(seated, *, seat, **_kw):  # type: ignore[no-untyped-def]
        answers.extend([seat(700.0, 100.0), seat(700.0, 540.0), seat(400.04, 440.04), seat(400.0, 440.0)])
        return seated

    monkeypatch.setattr(stands, "settle_the_belt", fake)
    s = Settlement(1400, 1200, seed=5)
    s.meta(name="W", scale="hamlet", ftpx=1, down_deg=90)
    s.M["houses"] = [{"x": float(x), "y": 700.0, "w": 30.0, "h": 24.0, "rot": 0} for x in range(300, 1101, 100)]
    s.M["wells"] = [{"x": 700.0, "y": 540.0, "r": 20.0, "vr": 12.0}]
    s.village_grove(BAND, role="windbreak", within=(0.0, 300.0, 1400.0, 1200.0), wind=N, page=lambda _s: PAGE)
    assert answers == [None, None, (400.0, 440.0), None]
