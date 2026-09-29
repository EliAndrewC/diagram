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
    lone = [(900.0, 900.0), (910.0, 900.0)]  # both downwind: trimmed to the one nearer the wind, where it converges
    assert len(trim_to_the_wind(lone, houses, NW)) == 1


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
