"""Feature 287, the woods area: each guarantee's placer on constructed inputs that include the violating case.

The one predicates live in the engine (`stands.py`, `wet.py`, `cover.py`); each test drives the placer and asks the
predicate the finished-map rule reads.
"""

from __future__ import annotations

import math
import random

from l7r.diagram.settlement import Settlement, point_in_poly
from l7r.diagram.settlement.homestead_parts.stands import (
    BELT_BEARING_MAX_DEG,
    BELT_SUBTENSE_MAX_DEG,
    belt_bearing_and_subtense,
    crown_reach,
    grove_stocked,
    stocked_copse,
    trim_to_the_wind,
    trunk_on_tread,
)
from l7r.diagram.settlement.land.cover import ring_center
from l7r.diagram.settlement.land.wet import offer_rethrow, throw_again

NW = (-math.sqrt(0.5), -math.sqrt(0.5))  # toward where the wind comes from: up and left on the sheet


def _hamlet(w: int = 1200, h: int = 1200) -> Settlement:
    s = Settlement(w, h, seed=5)
    s.meta(name="W", scale="hamlet", ftpx=1, down_deg=90)
    return s


# ---- W21 / H43: no trunk in a tread ---------------------------------------------------------------------------------


def test_a_trunk_on_the_tread_is_read_by_the_lanes_own_half_width() -> None:
    lanes = [{"pts": [[0.0, 0.0], [100.0, 0.0]], "w": 6}]
    assert trunk_on_tread(50.0, 2.9, lanes), "inside the 3 ft half-width"
    assert not trunk_on_tread(50.0, 3.1, lanes), "beside the tread is what a path looks like"
    assert not trunk_on_tread(50.0, 0.0, [{"pts": [[0.0, 0.0]], "w": 6}]), "a one-point way has no tread"
    assert math.isclose(crown_reach(28.0), 12.0 * math.sqrt(2.0)) and crown_reach(28.0, 3.0) > crown_reach(28.0)


def test_no_trunk_the_belt_draws_stands_on_a_lane_through_it() -> None:
    """Woods W21 / homes H43, the violating case: a lane runs through the belt's band. Every clump keeps `crown_reach` off
    the tread, so no crown or row conifer the belt draws - `tree_crowns` holds every trunk - stands on it."""
    s = _hamlet()
    lane = [[100.0, 600.0], [1100.0, 600.0]]
    s.lane([tuple(p) for p in lane], width=6, clearance=10, worn=True)
    n = s.village_grove([(150.0, 520.0), (1050.0, 520.0), (1050.0, 680.0), (150.0, 680.0)], role="windbreak")
    flat = s.M["tree_crowns"]
    trunks = [(flat[i], flat[i + 1]) for i in range(0, len(flat), 3)]
    assert n and trunks, "non-vacuity: the belt stands either side of the lane and draws its crowns"
    assert not any(trunk_on_tread(x, y, s.M["lanes"]) for x, y in trunks)


# ---- W18: the belt on the wind's quarter, a hook ------------------------------------------------------------------


def test_the_belt_bearing_and_subtense_are_the_rules_measures() -> None:
    houses = [{"x": 0.0, "y": 0.0}, {"x": 10.0, "y": 0.0}, {"x": 0.0, "y": 10.0}, {"x": 10.0, "y": 10.0}]
    nw = [(-100.0 + 5.0, -100.0 + 5.0), (-120.0 + 5.0, -80.0 + 5.0)]
    off, sub = belt_bearing_and_subtense(nw, houses, NW)
    assert off < 10.0 and sub < 30.0
    ring = [(5.0 + 100 * math.cos(math.radians(a)), 5.0 + 100 * math.sin(math.radians(a))) for a in range(0, 360, 30)]
    assert belt_bearing_and_subtense(ring, houses, NW)[1] > 300.0, "a belt round the houses subtends nearly all of them"


def test_a_belt_wrapped_round_the_cluster_is_trimmed_to_a_hook_on_the_wind() -> None:
    """Woods W18, the violating cases: a band that wraps three sides of the houses (subtending 270 degrees), and one that
    stands mostly on the cluster's north-east (bearing 70 degrees off the wind). Trimming END crowns brings each inside
    both bounds, keeps the crowns nearest the wind's bearing, and never takes a crown from the middle of the run."""
    houses = [{"x": 500.0 + dx, "y": 500.0 + dy} for dx in (-40.0, 0.0, 40.0) for dy in (-40.0, 0.0, 40.0)]
    wrap = [(500.0 + 150 * math.cos(math.radians(a)), 500.0 + 150 * math.sin(math.radians(a))) for a in range(90, 361, 10)]
    off, sub = belt_bearing_and_subtense(wrap, houses, NW)
    assert sub > BELT_SUBTENSE_MAX_DEG, "non-vacuity: the constructed belt wraps the houses"
    kept = trim_to_the_wind(wrap, houses, NW)
    off, sub = belt_bearing_and_subtense(kept, houses, NW)
    assert off <= BELT_BEARING_MAX_DEG and sub <= BELT_SUBTENSE_MAX_DEG
    assert wrap[13] in kept and wrap[14] in kept, "the crowns either side of the wind's bearing (220 and 230 degrees) stay"
    idx = sorted(wrap.index(c) for c in kept)
    assert idx == list(range(idx[0], idx[-1] + 1)), "only ends were taken: the kept run has no hole"
    east = [(500.0 + 150 * math.cos(math.radians(a)), 500.0 + 150 * math.sin(math.radians(a))) for a in range(-100, -39, 5)]
    assert belt_bearing_and_subtense(east, houses, NW)[0] > BELT_BEARING_MAX_DEG
    assert belt_bearing_and_subtense(trim_to_the_wind(east, houses, NW), houses, NW)[0] <= BELT_BEARING_MAX_DEG
    assert trim_to_the_wind(wrap, [], NW) == wrap, "no houses, nothing to bear from"
    lone = [(900.0, 900.0), (910.0, 900.0)]  # both downwind: the ends converge on one crown still off the wind
    assert belt_bearing_and_subtense(lone[:1], houses, NW)[0] > BELT_BEARING_MAX_DEG, "non-vacuity: the remnant is off the wind"
    assert trim_to_the_wind(lone, houses, NW) == [], "no crown stands in the wind's quarter: no belt, never one off the wind"


def test_a_belt_with_no_crown_on_the_wind_is_not_planted() -> None:
    """Woods W18 at the placer, the violating case: a band wholly downwind of the houses. The belt the trim would have
    converged on - one crown off the wind - is not planted, and the grove records nothing."""
    houses = [{"x": 500.0 + dx, "y": 500.0 + dy, "w": 30.0, "h": 24.0, "rot": 0} for dx in (-40.0, 0.0, 40.0) for dy in (-40.0, 0.0, 40.0)]
    s = _hamlet()
    s.M["houses"] = [dict(h) for h in houses]
    assert s.village_grove([(880.0, 880.0), (960.0, 880.0), (960.0, 960.0), (880.0, 960.0)], role="windbreak", wind=NW) == 0
    assert s.M["village_groves"] == []


def test_village_grove_trims_the_windbreak_it_is_handed_the_wind_for() -> None:
    """At the placer: `village_grove(role="windbreak", wind=...)` records a belt the predicate admits, where the same band
    without the wind subtends more than a hook."""
    houses = [{"x": 600.0 + dx, "y": 600.0 + dy, "w": 30.0, "h": 24.0, "rot": 0} for dx in (-60.0, 60.0) for dy in (-60.0, 60.0)]
    band = [(380.0, 380.0), (820.0, 380.0), (820.0, 820.0), (760.0, 820.0), (760.0, 440.0), (440.0, 440.0), (440.0, 820.0), (380.0, 820.0)]
    free = _hamlet()
    free.M["houses"] = [dict(h) for h in houses]
    free.village_grove(band, role="windbreak")
    assert belt_bearing_and_subtense(free.M["village_groves"][0]["clumps"], houses, NW)[1] > BELT_SUBTENSE_MAX_DEG, "non-vacuity"
    s = _hamlet()
    s.M["houses"] = [dict(h) for h in houses]
    s.village_grove(band, role="windbreak", wind=NW)
    off, sub = belt_bearing_and_subtense(s.M["village_groves"][0]["clumps"], houses, NW)
    assert off <= BELT_BEARING_MAX_DEG and sub <= BELT_SUBTENSE_MAX_DEG


# ---- W15: a recorded grove holds trees ----------------------------------------------------------------------------


def test_a_scattered_copse_drops_its_stragglers_until_its_record_is_stocked() -> None:
    """Woods W15, the violating case: seats at three corners of a 600 x 600 box (0.83 clumps per 100k sq px) - the copse
    recorded is stocked at the floor or above."""
    corners = [(0.0, 0.0), (600.0, 0.0), (0.0, 600.0), (10.0, 10.0)]
    pad = 15.0
    assert not grove_stocked(corners, 630.0, 630.0), "non-vacuity: the scatter is under the floor"
    kept = stocked_copse(corners, pad)
    xs, ys = [c[0] for c in kept], [c[1] for c in kept]
    assert grove_stocked(kept, max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad) and (0.0, 0.0) in kept
    assert grove_stocked([], 0.0, 10.0), "a record with no extent holds nothing to be short of"


def test_village_grove_records_a_copse_its_own_extent_holds() -> None:
    s = _hamlet()
    s.M["houses"] = [{"x": 200.0, "y": 200.0, "w": 30.0, "h": 24.0, "rot": 0}]
    n = s.village_grove([(100.0, 100.0), (1100.0, 100.0), (1100.0, 1100.0), (100.0, 1100.0)], role="copse", dense=False, near=([(200.0, 200.0), (1000.0, 1000.0)], 90.0))
    g = s.M["village_groves"][0]
    assert n >= 1 and grove_stocked(g["clumps"], g["w"], g["h"])


# ---- W01 / W03 / W05: decided at the record's grain ---------------------------------------------------------------


def test_every_seat_is_decided_at_the_records_grain() -> None:
    """Woods W01, W03: the seat the placer admits is the point the manifest records - every clump is already at 0.1 px -
    so a copse clump within reach and outside the marsh as placed is so as recorded."""
    s = _hamlet()
    s.M["houses"] = [{"x": 600.0, "y": 600.0, "w": 30.0, "h": 24.0, "rot": 0}]
    toe = [[560.0, 660.0], [700.0, 660.0], [700.0, 760.0], [560.0, 760.0]]
    s.M["marshes"].append({"role": "toe", "poly": toe})
    s.village_grove([(480.0, 480.0), (720.0, 480.0), (720.0, 720.0), (480.0, 720.0)], role="copse", dense=False, near=([(600.0, 600.0)], 90.0))
    clumps = s.M["village_groves"][0]["clumps"]
    assert clumps, "non-vacuity"
    assert all(c == [round(c[0], 1), round(c[1], 1)] for c in clumps)
    assert all(math.dist(c, (600.0, 600.0)) <= 90.0 for c in clumps), "the reach, on the recorded point"
    ring = [(float(a), float(b)) for a, b in toe]
    assert not any(point_in_poly(c[0], c[1], ring) for c in clumps), "no copse clump based in the marsh"


def test_the_belts_alder_is_recorded_clump_by_clump() -> None:
    """Woods W05 (the placer half): every belt clump drawn as alder - based in a toe or waterside marsh - is recorded in
    `alder_clumps`, so the count can be taken again over the clumps the page shows once it is known."""
    s = _hamlet()
    s.M["houses"] = [{"x": 600.0, "y": 900.0, "w": 30.0, "h": 24.0, "rot": 0}]
    toe = [[300.0, 300.0], [600.0, 300.0], [600.0, 700.0], [300.0, 700.0]]
    s.M["marshes"].append({"role": "toe", "poly": toe})
    s.village_grove([(200.0, 400.0), (1000.0, 400.0), (1000.0, 560.0), (200.0, 560.0)], role="windbreak")
    g = s.M["village_groves"][0]
    ring = [(float(a), float(b)) for a, b in toe]
    wet = [c for c in g["clumps"] if point_in_poly(c[0], c[1], ring)]
    assert wet and g["alder"] == len(wet) and sorted(g["alder_clumps"]) == sorted(wet) and g["clumps_offpage"] == []


# ---- W04 (the record's half): the commons record carries its ring's center ------------------------------------------


def test_a_commons_record_carries_its_rings_center() -> None:
    s = _hamlet()
    ring = [(100.0, 100.0), (300.0, 120.0), (260.0, 330.0), (90.0, 280.0)]
    s.commons(ring, role="woodland")
    rec = s.M["commons"][-1]
    assert (rec["x"], rec["y"]) == ring_center(ring) == (195.0, 215.0)


# ---- W52 / M6: the marsh's throw offered again ----------------------------------------------------------------------


def test_a_throw_again_is_clipped_to_its_parcel_and_keeps_the_stream() -> None:
    thrown: list[tuple[float, ...]] = []
    random.seed(11)
    expect = random.random()
    random.seed(11)
    throw_again((50.0, 50.0, 500.0, 500.0), (0.0, 0.0, 200.0, 300.0), lambda *a: thrown.append(a))
    assert thrown == [(50.0, 50.0, 200.0, 300.0, None)] and random.random() == expect, "clipped, and the map's stream untouched"
    throw_again((400.0, 0.0, 500.0, 100.0), (0.0, 0.0, 200.0, 300.0), lambda *a: thrown.append(a))
    assert len(thrown) == 1, "a strip outside the parcel throws nothing"


def test_a_marsh_offers_its_rethrow_only_to_a_caller_that_asked() -> None:
    """The marsh registers its re-throw where `stage_hinterland` opened `_scatter_catchup`, and nowhere else - and the
    re-throw fills a strip past the frame it first threw within, at the marsh's own density."""
    s = _hamlet()
    s._scatter_frame = (0.0, 0.0, 1200.0, 400.0)
    s.marsh([(0.0, 300.0), (1200.0, 300.0), (1200.0, 900.0), (0.0, 900.0)], role="waterside")
    assert "_scatter_catchup" not in vars(s), "no caller asked: nothing is kept"
    t = _hamlet()
    t._scatter_frame = (0.0, 0.0, 1200.0, 400.0)
    vars(t)["_scatter_catchup"] = {}
    t.marsh([(0.0, 300.0), (1200.0, 300.0), (1200.0, 900.0), (0.0, 900.0)], role="waterside")
    reg = vars(t)["_scatter_catchup"]
    assert list(reg) == [len(t._scatter_frames) - 1]
    marks = t._mark_groups[-1][1]
    blades = t._blade_groups[-1][2]
    before = (len(marks), len(blades))
    assert all(m[1] <= 400.0 + 30.0 for m in marks), "non-vacuity: the first throw stopped at the frame's foot"
    reg[len(t._scatter_frames) - 1]((0.0, 400.0, 1200.0, 900.0))
    assert len(marks) > before[0] and len(blades) > before[1] and any(m[1] > 500.0 for m in marks), "the strip holds the marsh"
    offer_rethrow(s, 0, print)  # no registry on `s`: a no-op, not an error


# ---- W13: a woodland commons is visibly stocked -------------------------------------------------------------------


def test_a_parcels_room_is_its_dry_ground_clear_of_the_commons_keep_outs() -> None:
    s = _hamlet()
    ring = [(100.0, 100.0), (220.0, 100.0), (220.0, 220.0), (100.0, 220.0)]
    room = s.woodland_room(ring)
    assert len(room) >= 100 and all(point_in_poly(x, y, ring) for x, y, _r in room)
    s.field_polys.append([(0.0, 0.0), (400.0, 0.0), (400.0, 400.0), (0.0, 400.0)])
    assert s.woodland_room(ring) == [], "a ring wholly over the crop is sure of no crown"
    t = _hamlet()
    t.M["marshes"].append({"role": "toe", "poly": [[0.0, 0.0], [400.0, 0.0], [400.0, 160.0], [0.0, 160.0]]})
    t.M["pond"] = [160.0, 200.0, 20.0, 10.0]
    wet_room = t.woodland_room(ring)
    assert wet_room and all(y >= 160.0 for _x, y, _r in wet_room) and not any(math.dist((x, y), (160.0, 200.0)) < 10.0 for x, y, _r in wet_room)


class _Misses:
    """The global `random` with every throw landing off the parcel - the violating case, a parcel whose throws seat
    nothing though its ground has room."""

    def __init__(self) -> None:
        self._r = random

    def uniform(self, a: float, b: float) -> float:
        return -5000.0

    def __getattr__(self, name: str):  # type: ignore[no-untyped-def]
        return getattr(self._r, name)


def test_a_woodland_whose_throws_miss_is_stocked_from_its_room(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Woods W13 at the placer: throws that seat under `WOODLAND_MIN_CROWNS` are taken back, and the parcel is stocked
    from its room - it records at least the floor, and every crown it records is ink."""
    from l7r.diagram.settlement.land import cover

    s = _hamlet()
    monkeypatch.setattr(cover, "random", _Misses())
    s.commons([(100.0, 100.0), (220.0, 100.0), (220.0, 220.0), (100.0, 220.0)], role="woodland")
    rec = s.M["commons"][-1]
    assert rec["crowns"] >= cover.WOODLAND_MIN_CROWNS and len(s.M["tree_crowns"]) == 3 * rec["crowns"]


# ---- W06: no grove based in the marsh beyond its margin ------------------------------------------------------------


def test_a_belt_over_the_toe_seats_only_in_its_reed_margin() -> None:
    """Woods W06, the violating case: a belt band half over a toe marsh. No windbreak clump is based deeper than the reed
    margin inside the ring; the clumps inside the margin are drawn as alder."""
    from l7r.diagram.settlement.homestead_parts.stands import deep_marsh
    from l7r.diagram.settlement.land.wet import MARSH_FEATHER_BS

    s = _hamlet()
    s.M["houses"] = [{"x": 600.0, "y": 900.0, "w": 30.0, "h": 24.0, "rot": 0}]
    toe = [[100.0, 100.0], [1100.0, 100.0], [1100.0, 520.0], [100.0, 520.0]]
    s.M["marshes"].append({"role": "toe", "poly": toe})
    s.village_grove([(200.0, 420.0), (1000.0, 420.0), (1000.0, 640.0), (200.0, 640.0)], role="windbreak")
    g = s.M["village_groves"][0]
    deep = deep_marsh([toe], MARSH_FEATHER_BS * s.bscale)
    assert deep and g["clumps"], "non-vacuity: the band runs into ground deeper than the margin, and the belt stands"
    assert not any(point_in_poly(c[0], c[1], d) for c in g["clumps"] for d in deep)
    ring = [(float(a), float(b)) for a, b in toe]
    assert g["alder"] == sum(1 for c in g["clumps"] if point_in_poly(c[0], c[1], ring)) > 0, "the margin's clumps are alder"
    assert deep_marsh([[(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)], [(0.0, 0.0), (1.0, 1.0)]], 20.0) == [], "a ring the inset empties"


# ---- W22 / W23: a copse clear of the belt's canopy; no canopy over open water --------------------------------------


def test_a_copse_over_a_belt_crown_stands_clear_of_its_canopy() -> None:
    """Woods W22: with one windbreak clump recorded and a copse box over it, no copse clump stands within the belt
    clump's canopy radius (the copse keeps the sum of the two canopies' reach)."""
    s = _hamlet()
    s.M["houses"] = [{"x": 600.0, "y": 600.0, "w": 30.0, "h": 24.0, "rot": 0}]
    s.M["village_groves"].append({"role": "windbreak", "r": 14.0, "clumps": [[640.0, 640.0]]})
    s.village_grove([(540.0, 540.0), (700.0, 540.0), (700.0, 700.0), (540.0, 700.0)], role="copse", dense=False, near=([(600.0, 600.0)], 90.0))
    cop = s.M["village_groves"][-1]["clumps"]
    assert cop, "non-vacuity"
    assert all(math.dist(c, (640.0, 640.0)) >= 14.0 + 0.9 * 22.0 * s.bscale for c in cop)


# ---- W25: every household's reserved share of the wood floor stands ---------------------------------------------------


def test_the_belt_leaves_a_reserved_seat_free_and_the_copse_plants_it() -> None:
    """Woods W25 / plan D9, the violating case: a household's reserved copse seat stands inside the belt's band, where the
    belt would plant a clump that displaces it. Handed the seat (`keep_off`), the belt stands off it by the copse's own
    displacement reach (`reserved_seat_keepouts`); the copse, handed it (`seats`), plants it though its `near` - the
    against-the-belt siting's lee - lies nowhere near it."""
    from l7r.diagram.settlement.homestead_parts.stands import reserved_seat_keepouts

    band = [(200.0, 400.0), (1000.0, 400.0), (1000.0, 560.0), (200.0, 560.0)]
    seat = (600.0, 480.0)
    houses = [{"x": 600.0, "y": 900.0, "w": 30.0, "h": 24.0, "rot": 0}]
    free = _hamlet()
    free.M["houses"] = [dict(h) for h in houses]
    free.village_grove(band, role="windbreak")
    (_x, _y, r) = reserved_seat_keepouts([seat], 28.0 * free.bscale, free.bscale)[0]
    assert any(math.dist(c, seat) < r for c in free.M["village_groves"][0]["clumps"]), "non-vacuity: the belt takes the seat"
    s = _hamlet()
    s.M["houses"] = [dict(h) for h in houses]
    s.village_grove(band, role="windbreak", keep_off=[seat])
    belt = s.M["village_groves"][0]["clumps"]
    assert belt and all(math.dist(c, seat) >= r for c in belt)
    s.village_grove([(500.0, 400.0), (700.0, 400.0), (700.0, 560.0), (500.0, 560.0)], role="copse", dense=False, near=([(100.0, 100.0)], 10.0), seats=[seat])
    assert s.M["village_groves"][-1]["clumps"] == [list(seat)]


def test_a_copse_plants_its_reserved_seats_first_and_never_drops_one() -> None:
    """Woods W25, the violating case: four reserved seats strewn to the corners of a wide box, where the copse's own clumps
    gather round one house - as stragglers the stocking drop (woods W15) would take them out first. Every seat is
    recorded, and no clump of the copse's own grid stands within half a crown of one."""
    seats = [(150.0, 150.0), (1050.0, 150.0), (150.0, 1050.0), (650.0, 600.0)]
    pad = 11.0 * _hamlet().bscale + 4.0
    assert not grove_stocked(seats + [(600.0, 560.0)], 900.0 + 2 * pad, 900.0 + 2 * pad), "non-vacuity: the seats are stragglers"
    s = _hamlet()
    s.M["houses"] = [{"x": 600.0, "y": 600.0, "w": 30.0, "h": 24.0, "rot": 0}]
    s.village_grove([(100.0, 100.0), (1100.0, 100.0), (1100.0, 1100.0), (100.0, 1100.0)], role="copse", dense=False, near=([(600.0, 600.0)], 90.0), seats=seats)
    cl = [tuple(c) for c in s.M["village_groves"][0]["clumps"]]
    own = [c for c in cl if c not in seats]
    assert all(q in cl for q in seats) and own, "every seat stands, beside the copse's own clumps"
    assert all(math.dist(c, q) >= 11.0 * s.bscale for c in own for q in seats)


def test_the_stocking_drop_stops_at_the_kept_clumps() -> None:
    """Woods W25 beside W15: a scatter of kept clumps alone is left whole - no kept clump is a straggler."""
    corners = [(0.0, 0.0), (600.0, 0.0), (0.0, 600.0)]
    assert stocked_copse(corners, 15.0, frozenset(corners)) == corners
    assert stocked_copse(corners + [(900.0, 900.0)], 15.0, frozenset(corners)) == corners


def test_no_grove_clump_stands_over_a_stream_through_its_band() -> None:
    """Woods W23: a stream through a belt band - no recorded clump within the stream's half-width and a clump's radius."""
    from l7r.diagram.settlement import seg_dist

    s = _hamlet()
    s.M["houses"] = [{"x": 600.0, "y": 900.0, "w": 30.0, "h": 24.0, "rot": 0}]
    brook = [[600.0, 100.0], [620.0, 1100.0]]
    s.M["streams"].append({"poly": brook, "w": 8})
    s.village_grove([(200.0, 400.0), (1000.0, 400.0), (1000.0, 560.0), (200.0, 560.0)], role="windbreak")
    clumps = s.M["village_groves"][0]["clumps"]
    assert clumps
    assert all(seg_dist(c[0], c[1], tuple(brook[0]), tuple(brook[1])) >= 4.0 + 14.0 * s.bscale for c in clumps)


# ---- W11: no more than 35% of the view is bare ---------------------------------------------------------------------


def test_bare_blocks_are_connected_and_largest_first() -> None:
    from l7r.diagram.settlement.land.cover import bare_blocks, block_ring

    pts = [(12.5, 12.5), (37.5, 12.5), (62.5, 12.5), (212.5, 212.5)]
    blocks = bare_blocks(pts)
    assert len(blocks) == 2 and sorted(blocks[0]) == pts[:3] and blocks[1] == [(212.5, 212.5)] and bare_blocks([]) == []
    ring = block_ring(blocks[0])
    assert all(point_in_poly(x, y, ring) for x, y in pts[:3])


def test_a_view_with_holes_is_clothed_to_the_rules_share() -> None:
    """Woods W11, the violating case: a field in the middle of a view and no strip on any side - over 35% of the view is
    ground nothing covers. The fill lays grazing until `bare_cells` (the rule's predicate) reads the cap or under, and
    counts the cover a later stage will draw (`planned`)."""
    from l7r.diagram.settlement.land.cover import BARE_SHARE_CAP, bare_cells

    s = _hamlet(1000, 1000)
    s.M["fields"] = [{"outline": [[400.0, 400.0], [600.0, 400.0], [600.0, 600.0], [400.0, 600.0]]}]
    view = (0.0, 0.0, 1000.0, 1000.0)
    bare, total = bare_cells(s.M, view)
    assert len(bare) / total > BARE_SHARE_CAP, "non-vacuity"
    assert s.fill_the_holes(view) >= 1
    bare, total = bare_cells(s.M, view)
    assert len(bare) / total <= BARE_SHARE_CAP
    t = _hamlet(1000, 1000)
    assert t.fill_the_holes(view, planned=[[(0.0, 0.0), (1000.0, 0.0), (1000.0, 1000.0), (0.0, 1000.0)]]) == 0, "planned cover counts"


def test_the_fill_stops_once_the_share_is_met() -> None:
    """The largest block first; a small block left once the share is met stays bare - ground the rule allows."""
    from l7r.diagram.settlement.land.cover import BARE_SHARE_CAP, bare_cells

    s = _hamlet(1000, 1000)
    planned = [[(0.0, 0.0), (280.0, 0.0), (280.0, 1000.0), (0.0, 1000.0)], [(320.0, 0.0), (600.0, 0.0), (600.0, 1000.0), (320.0, 1000.0)]]
    assert s.fill_the_holes((0.0, 0.0, 1000.0, 1000.0), planned) == 1
    probe = {**s.M, "_planned_cover": planned}
    bare, total = bare_cells(probe, (0.0, 0.0, 1000.0, 1000.0))
    assert bare and len(bare) / total <= BARE_SHARE_CAP and all(280.0 < x < 320.0 for x, _y in bare), "the gap column is left"


def test_a_toe_wholly_inside_the_dike_block_is_no_marsh() -> None:
    """Woods W07 at the placer: the clip leaves nothing, and the marsh is neither drawn nor recorded - the drop is named."""
    s = _hamlet()
    s.M["dikes"] = [{"outline": [[0.0, 0.0], [1000.0, 0.0], [1000.0, 1000.0], [0.0, 1000.0]]}]
    s.marsh([(300.0, 300.0), (500.0, 300.0), (500.0, 500.0)], role="toe")
    assert s.M["marshes"] == [] and s.M["meta"]["marsh_dropped"] == [{"role": "toe", "why": "no open ground left"}]


# ---- W05 (the count half): the alder is counted over the clumps the page shows -----------------------------------------


def test_the_alder_count_is_taken_again_over_the_clumps_on_the_page() -> None:
    """Woods W05: four clumps, two drawn as alder and one of those two off the view - once the page is known, `alder`
    counts the one alder clump the page shows."""
    s = _hamlet()
    s.M["village_groves"] = [
        {
            "role": "windbreak",
            "r": 14.0,
            "clumps": [[100.0, 100.0], [200.0, 100.0], [300.0, 100.0], [900.0, 100.0]],
            "clumps_offpage": [],
            "alder": 2,
            "alder_clumps": [[200.0, 100.0], [900.0, 100.0]],
        },
        {"role": "copse", "r": 11.0, "clumps": [[150.0, 150.0]], "clumps_offpage": []},
    ]
    s.set_view(0.0, 0.0, 500.0, 500.0)
    g = s.M["village_groves"][0]
    assert g["clumps_offpage"] == [[900.0, 100.0]] and g["alder"] == 1
    assert "alder" not in s.M["village_groves"][1], "a grove with no alder record is not given one"


# ---- W10 (the cull half): no cover inside a clearing swept after it -----------------------------------------------------


def test_a_clearing_swept_after_the_scrub_takes_its_blades_and_marks_out() -> None:
    """Woods W10, the violating case: the scrub is scattered over a square, then a household shrine's clearing is swept
    inside it. The finish writes nothing rooted inside the clearing, and the scrub outside it stays."""
    from l7r.diagram.settlement._geom import RingIndex

    s = _hamlet()
    s.commons([(100.0, 100.0), (700.0, 100.0), (700.0, 700.0), (100.0, 700.0)], role="grazing")
    blades = [ln for _z, _c, bl in s._blade_groups for ln in bl]
    marks = [mk for _z, mk in s._mark_groups for mk in mk]
    assert blades and marks, "non-vacuity: the scrub threw blades and dots"
    s.reserve_clearing(400.0, 400.0, 60.0, 60.0)
    ring = RingIndex(s.clearings[-1])
    left = [ln for _z, _c, bl in s._blade_groups for ln in bl]
    left_marks = [mk for _z, mk in s._mark_groups for mk in mk]
    assert not any(ring.inside(float(ln[0]), float(ln[1])) for ln in left)
    assert not any(ring.inside((mk[0] + mk[2]) / 2, (mk[1] + mk[3]) / 2) for mk in left_marks)
    assert len(blades) > len(left) > 0 and len(left_marks) > 0, "only the clearing's ground was taken"
    s.reserve_clearing(400.0, 400.0, 60.0, 60.0)  # the same clearing again: the reused blob culls nothing more
    assert len([ln for _z, _c, bl in s._blade_groups for ln in bl]) == len(left)


# ---- W15 at the record: every grove is recorded at an extent its clumps stock ---------------------------------------


def test_a_grove_is_recorded_at_an_extent_its_clumps_stock() -> None:
    """Woods W15, the violating cases: a band far larger than what was planted in it (the windbreak's box kept), and two
    stands far apart (the drawn extent of both under the floor) - each recorded box is stocked; a stocked band keeps its
    box, and a grove with nothing on it records none."""
    from l7r.diagram.settlement.homestead_parts.stands import grove_extent, main_stand, record_box, stocked_at_grain, stocked_box

    stand = [(100.0 + 20 * i, 100.0 + 20 * j) for i in range(4) for j in range(4)]
    band = (0.0, 0.0, 2000.0, 2000.0)
    assert not stocked_at_grain(stand, band), "non-vacuity: 16 clumps in 4,000,000 sq px"
    assert stocked_box(stand, band, 15.0) == grove_extent(stand, 15.0)
    far = [*stand, (1900.0, 1900.0), (1900.0, 100.0)]
    assert not stocked_at_grain(far, grove_extent(far, 15.0)), "non-vacuity: the drawn extent of both is under the floor"
    box = stocked_box(far, band, 15.0)
    assert stocked_at_grain(far, box) and box == grove_extent(stand, 15.0) and sorted(main_stand(far, 15.0)) == sorted(stand)
    tight = (80.0, 80.0, 180.0, 180.0)
    assert stocked_box(stand, tight, 15.0) == tight, "a band its clumps stock keeps its box: the belt's position is its meaning"
    assert stocked_box([], (0.0, 0.0, 10.0, 20.0), 15.0) == (5.0, 10.0, 5.0, 10.0)
    g: dict = {}
    record_box(g, (1.04, 2.0, 11.06, 22.0))
    assert (g["y"], g["w"], g["h"]) == (12.0, 10.0, 20.0)


def test_village_grove_records_a_windbreak_its_clumps_stock() -> None:
    """At the placer, the violating case: a windbreak band 1,100 px square over a field that leaves only one corner of it
    plantable - its few clumps do not stock the band's box, and the grove is recorded at an extent they do."""
    s = _hamlet(1400, 1400)
    s.M["houses"] = [{"x": 700.0, "y": 1300.0, "w": 30.0, "h": 24.0, "rot": 0}]
    s.field_polys.append([(180.0, 60.0), (1260.0, 60.0), (1260.0, 1260.0), (60.0, 1260.0), (60.0, 180.0), (180.0, 180.0)])
    n = s.village_grove([(100.0, 100.0), (1200.0, 100.0), (1200.0, 1200.0), (100.0, 1200.0)], role="windbreak")
    g = s.M["village_groves"][0]
    assert n and not grove_stocked(g["clumps"], 1100.0, 1100.0), "non-vacuity: the band's box is under the floor"
    assert grove_stocked(g["clumps"], g["w"], g["h"]) and g["w"] < 1100.0


def test_the_page_partition_records_the_grove_again_at_what_the_page_shows() -> None:
    """Woods W15 at `set_view`: a grove whose clumps mostly stand off the page keeps only its on-page clumps, and its box is
    re-decided over them - stocked, where the old box with two clumps in it was not."""
    s = _hamlet(2000, 2000)
    clumps = [[100.0, 100.0], [1800.0, 1800.0]] + [[1500.0 + 20 * i, 1500.0 + 20 * j] for i in range(5) for j in range(5)]
    s.M["village_groves"] = [{"x": 1000.0, "y": 1000.0, "w": 1900.0, "h": 1900.0, "role": "windbreak", "r": 14.0, "clumps": clumps, "clumps_offpage": []}]
    s.set_view(0.0, 0.0, 1400.0, 1400.0)
    g = s.M["village_groves"][0]
    assert g["clumps"] == [[100.0, 100.0]] and len(g["clumps_offpage"]) == 26
    assert grove_stocked(g["clumps"], g["w"], g["h"]) and not grove_stocked(g["clumps"], 1900.0, 1900.0)
    s.M["village_groves"].append({"role": "copse", "r": 11.0, "clumps": [[50.0, 50.0]], "clumps_offpage": []})
    s.set_view(0.0, 0.0, 1400.0, 1400.0)
    assert "w" not in s.M["village_groves"][1], "a record with no extent is not given one"


# ---- W02 / W25: a reserved seat stands within its household's reach, as planted and as re-seated ---------------------


def test_a_reserved_seat_is_asked_its_households_reach_and_bank() -> None:
    """Woods W02 with W25, the violating cases: three reserved seats - one within its house's reach, one beyond it, one
    within it only across the brook. Planted with the dooryard's reach (`seat_near`), only the first stands; the siting's
    own `near` (against the belt) is not what a seat is asked."""
    from l7r.diagram.settlement.homestead_parts.stands import BankNear

    house = (600.0, 600.0)
    brook = [((660.0, 300.0), (660.0, 900.0))]
    seats = [(560.0, 560.0), (600.0, 750.0), (700.0, 600.0)]
    reach = BankNear([house], 90.0, brook)
    assert reach.too_near(*seats[0]) and not reach.too_near(*seats[1]) and not reach.too_near(*seats[2]), "non-vacuity"
    s = _hamlet()
    s.M["houses"] = [{"x": 600.0, "y": 600.0, "w": 30.0, "h": 24.0, "rot": 0}]
    s.village_grove([(500.0, 500.0), (800.0, 500.0), (800.0, 800.0), (500.0, 800.0)], role="copse", dense=False, near=([(100.0, 100.0)], 10.0), seats=seats, seat_near=([house], 90.0, brook))
    assert s.M["village_groves"][0]["clumps"] == [list(seats[0])]


def test_a_reserved_seat_moved_round_another_groves_crown_is_asked_its_reach_again() -> None:
    """Woods W25, the re-seat: another grove's crown displaces a reserved seat, and the copse moves it round the crown. The
    moved seat is asked the household's reach, not the siting's (which here admits nothing): at every reach it is planted,
    moved, within it - and a seat beyond the reach is not planted at all."""
    house = (600.0, 600.0)
    seat = (640.0, 600.0)
    other = {"role": "windbreak", "r": 14.0, "clumps": [[652.0, 600.0]], "clumps_offpage": []}

    def plant(reach: float) -> list[list[float]]:
        s = _hamlet()
        s.M["houses"] = [{"x": 600.0, "y": 600.0, "w": 30.0, "h": 24.0, "rot": 0}]
        s.M["village_groves"].append(dict(other))
        s.village_grove([(520.0, 520.0), (760.0, 520.0), (760.0, 680.0), (520.0, 680.0)], role="copse", dense=False, near=([(2000.0, 2000.0)], 5.0), seats=[seat], seat_near=([house], reach, []))
        return [c for g in s.M["village_groves"] if g["role"] == "copse" for c in g["clumps"]]

    for reach in (40.5, 60.0, 120.0):
        moved = plant(reach)
        assert moved and list(seat) not in moved, "non-vacuity: the crown displaced the seat and it was moved"
        assert all(math.dist(c, house) <= reach for c in moved)
    assert plant(39.0) == [], "the seat itself is beyond its household's reach"


# ---- W21: a crown's reach counts the lift `_draw_grove` draws it at ------------------------------------------------------


def test_no_trunk_a_copse_draws_stands_on_a_footpath_beside_it() -> None:
    """Woods W21, cohort seed 3's case: a copse beside a 3 ft footpath, a crown drawn 3 bs above its clump's seat. The
    corridor keep-out counts that lift (`crown_reach(..., lift=...)`), so no trunk the copse draws is on the tread."""
    assert crown_reach(22.0, lift=3.0) > crown_reach(22.0), "the lift reaches farther than the box's half-diagonal"
    assert math.isclose(crown_reach(22.0, lift=3.0), 15.0)
    s = _hamlet()
    s.M["houses"] = [{"x": 600.0, "y": 700.0, "w": 30.0, "h": 24.0, "rot": 0}]
    s.lane([(400.0, 600.0), (800.0, 590.0)], width=3, clearance=4, worn=True)
    s.village_grove([(420.0, 520.0), (780.0, 520.0), (780.0, 680.0), (420.0, 680.0)], role="copse", dense=False, near=([(600.0, 700.0)], 200.0), area=1e9)
    flat = s.M["tree_crowns"]
    trunks = [(flat[i], flat[i + 1]) for i in range(0, len(flat), 3)]
    assert trunks and not any(trunk_on_tread(x, y, s.M["lanes"]) for x, y in trunks)


def test_a_wood_draws_no_trunk_on_a_lane_through_it() -> None:
    """Woods W21 for a tree stand (`_draw_stand`, at crop time): a lane runs through a forest patch; no crown's trunk stands
    on its tread, and a stand no lane reaches asks nothing."""
    from l7r.diagram.settlement.shrines_wells.woods import trees_off_the_treads

    s = _hamlet()
    s.lane([(100.0, 400.0), (900.0, 400.0)], width=6, clearance=4, worn=True)
    s._tree_stand([(200.0, 300.0), (800.0, 300.0), (800.0, 500.0), (200.0, 500.0)], seed=3, outliers=False)
    s.flush_tree_stands()
    flat = s.M["tree_crowns"]
    trunks = [(flat[i], flat[i + 1]) for i in range(0, len(flat), 3)]
    assert trunks and not any(trunk_on_tread(x, y, s.M["lanes"]) for x, y in trunks)
    far = [{"pts": [[0.0, 0.0], [10.0, 0.0]], "w": 6}]
    trees = [(500.0, 500.0, 8.0, "broadleaf")]
    assert trees_off_the_treads(trees, far) == trees and trees_off_the_treads([], far) == []
    assert trees_off_the_treads(trees, [{"pts": [[400.0, 500.0], [600.0, 500.0]], "w": 6}]) == []
