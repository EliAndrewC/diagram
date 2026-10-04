"""Feature 318, plan D12-D13: every household's way laid once, in the gaps, after the last house stands
(`settlement/rolling/gap_ways.py`)."""

from __future__ import annotations

import math
from types import SimpleNamespace

import numpy as np
import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling import gap_ways as gw
from l7r.diagram.settlement.rolling.access import start_tree


def _site(xs: tuple[float, ...] = (600.0, 900.0)) -> tuple[Settlement, list[dict]]:
    """A strip along y = 450 and a household seated at each x on y = 700, their homesteads parted by far more than the gap."""
    s = Settlement(1400.0, 1400.0, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=len(xs), down_deg=90, water_flow=90, nucleated=True)
    s._nucleated = True
    start_tree(s, (300.0, 450.0), (1.0, 0.0), 900.0)
    houses = []
    for x in xs:
        geom = s._bundle_geom(x, 700.0, 46.0, 28.0, "SE", rot=0.0)
        s.placed.append(geom["bbox"])
        houses.append({"x": x, "y": 700.0, "geom": geom})
    s.M["houses"] = houses
    return s, houses


def test_nothing_is_laid_with_no_tree_or_no_house() -> None:
    s, _houses = _site()
    s._access = None
    assert gw.lay_the_ways(s) == (0, 0)
    s2, _ = _site(())
    assert gw.lay_the_ways(s2) == (0, 0)


def test_every_household_is_given_a_way_through_the_gaps_recorded_as_its_corridor() -> None:
    """D12: each household's way leaves its dooryard and joins the way out or a way laid before it; recorded and reserved as
    the seating's corridor was (`access_corridors`, the first leg naming the house)."""
    s, houses = _site()
    assert gw.lay_the_ways(s) == (0, 0)
    assert all(h["geom"].get("access") for h in houses), "every household reached"
    named = [c["of"] for c in s.M["access_corridors"] if c.get("of")]
    assert sorted(named) == [[600.0, 700.0], [900.0, 700.0]]
    for h in houses:
        run = h["geom"]["access"]
        assert all(math.isfinite(v) for p in run for v in p) and len(run) >= 2


def test_a_passage_the_laid_ways_make_unnecessary_is_ended_where_it_stands() -> None:
    """FR-001: a household reached across a yard that the gap pass gives a way keeps its house, and its passage ends."""
    s, houses = _site()
    houses[1].update(reached_across=[600.0, 700.0], passage_depth=1, passage=[[0.0, 0.0]])
    assert gw.lay_the_ways(s) == (1, 0)
    assert "reached_across" not in houses[1] and "passage" not in houses[1] and houses[1]["geom"]["access"]


def test_a_household_no_way_reaches_is_reached_across_the_nearest_neighbors_yard(monkeypatch: pytest.MonkeyPatch) -> None:
    """D13, the pinch: no admitted way - reached across the yard of the nearest household with one, the walk not drawn."""
    s, houses = _site((600.0, 900.0, 1150.0))
    real = gw._way_for
    monkeypatch.setattr(gw, "_way_for", lambda s_, L, d, p, lays, rec, *a: None if rec is houses[2] else real(s_, L, d, p, lays, rec, *a))
    assert gw.lay_the_ways(s) == (0, 1)
    far = houses[2]
    assert far["reached_across"] == [900.0, 700.0] and far["passage_kind"] == "pinch" and far["passage_depth"] == 1
    assert "access" not in far["geom"]


def test_the_pinch_needs_a_household_with_a_way() -> None:
    rec = {"x": 0.0, "y": 0.0}
    assert not gw.pinch(rec, []) and "reached_across" not in rec
    nb = {"x": 10.0, "y": 0.0, "geom": {}}
    assert gw.pinch(rec, [nb]) and rec["passage"] == [[0.0, 0.0], [10.0, 0.0]], "no yard: to its house"


def test_lane_ground_holds_off_the_homesteads_the_wood_seats_and_the_sites_taken_ground() -> None:
    """`lane_layers`: homesteads counted per cell at the half-width, the wood seats by the lane gap, the free-ground raster's
    surely taken cells, and its uncertain cells asked exactly."""
    s, _houses = _site((600.0,))
    box = s.placed[0]
    s._wood = SimpleNamespace(lane_gap=10.0, seats=SimpleNamespace(buckets={(0, 0): [(box[0] - box[2] / 2 - 40.0, box[1])]}))
    state = np.zeros((40, 40), np.int8)
    state[0, :] = 1  # the westmost column of free-ground cells surely taken
    state[1, :] = 2  # the next surely clear
    s._free_ground = SimpleNamespace(x0=0.0, y0=0.0, cell=40.0, nx=40, ny=40, _state=state, lines_edge_points=lambda lines: [])
    s._site_corridors = SimpleNamespace(hit_points=lambda pts: pts[0][1] > 800.0)  # the uncertain ground south of 800 taken
    s._site_chains = [[((0.0, 850.0), (1400.0, 850.0), (0.0, -1.0))]]  # ...and south of 850 on the field side of a chord, decided at once
    L = gw.lane_layers(s, list(s.placed), list(s._access.segs), 7.0)
    c = L.cell_of((box[0], box[1]))
    assert c is not None and L.cover[c] == 1 and L.blocked()[c]
    w = L.cell_of((box[0] - box[2] / 2 - 40.0, box[1]))
    assert w is not None and L.site[w], "the wood seat"
    k = (np.floor(L.cx / 40.0).astype(int)[:, None], np.floor(L.cy / 40.0).astype(int)[None, :])
    clear = L.cover == 0
    assert L.site[(k[0] == 1) & (k[1] >= 0) & clear].sum() == 0, "surely clear: never asked"
    south = (k[0] > 1) & (np.broadcast_to(L.cy[None, :], L.site.shape) > 800.0) & clear
    wx, wy = box[0] - box[2] / 2 - 40.0, box[1]
    off_wood = (L.cx[:, None] - wx) ** 2 + (L.cy[None, :] - wy) ** 2 > 20.0**2
    north = (k[0] > 1) & (np.broadcast_to(L.cy[None, :], L.site.shape) < 790.0) & clear & off_wood
    assert south.any() and L.site[south].all() and not L.site[north].any(), "uncertain: asked exactly"
    s._site_corridors = None
    deep = (k[0] > 1) & (np.broadcast_to(L.cy[None, :], L.site.shape) > 855.0) & clear
    L2 = gw.lane_layers(s, list(s.placed), list(s._access.segs), 7.0)
    assert deep.any() and L2.site[deep].all() and not L2.site[south & ~deep & (np.broadcast_to(L.cy[None, :], L.site.shape) < 845.0)].any(), "the chords alone"
    assert L.cell_of((-50.0, 0.0)) is None


def test_the_flood_keeps_to_open_ground_cuts_no_corner_and_stops_past_the_last_ring() -> None:
    L = gw.Layers(0.0, 0.0, 12, 12, 5.0)
    L.cover[5, 0:11] = 1  # a wall with a gap at the bottom row
    L.cover[4, 10] = 1  # ...and a corner a diagonal would cut
    dist, pred = gw.flood(L, [((2.0, 2.0), (2.0, 2.0)), ((-50.0, -50.0), (-40.0, -50.0))], [(8, 9, 0, 1)])
    assert dist[0, 0] == 0.0 and math.isfinite(dist[8, 0]), "round the wall's end"
    assert not math.isfinite(dist[5, 3]), "never through it"
    assert tuple(pred[6, 11]) != (5, 10) and tuple(pred[6, 11]) != (4, 10)
    far, _ = gw.flood(L, [((2.0, 2.0), (2.0, 2.0))], [(0, 1, 0, 1)])
    assert math.isfinite(far[0, 1])


def test_the_flood_stops_short_past_the_last_ring(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gw, "FLOOD_PAST_PX", 1.0)
    L = gw.Layers(0.0, 0.0, 12, 1, 5.0)
    dist, _ = gw.flood(L, [((2.0, 2.0), (2.0, 2.0))], [(0, 1, 0, 1)])
    assert math.isfinite(dist[1, 0]) and not math.isfinite(dist[11, 0]), "the ring reached at once: stopped a step past it"


def test_a_way_out_starts_at_the_doors_and_ends_on_the_flood() -> None:
    L = gw.Layers(0.0, 0.0, 6, 6, 5.0)
    dist = np.full((6, 6), np.inf)
    dist[5, :] = 3.0
    exits, back = gw.way_out(L, dist, [(2.0, 2.0), (2.0, 2.0), (-10.0, 0.0)], (0, 6, 0, 6), lambda c: c != (2, 1))
    assert exits and exits == sorted(exits) and all(i == 5 for _d, i, _j in exits)
    assert back[(0, 0)] == (2.0, 2.0), "a door's cell steps back to the door"
    closed, _ = gw.way_out(L, dist, [(2.0, 2.0)], (0, 3, 0, 3), lambda c: True)
    assert closed == [], "its area ends before the flood"


def test_a_trace_joins_a_laid_way_where_the_leg_onto_it_is_clear_else_runs_on() -> None:
    L = gw.Layers(0.0, 0.0, 6, 1, 10.0)
    dist = np.array([[0.0], [1.0], [2.0], [3.0], [4.0], [5.0]])
    pred = np.array([[[0, 0]], [[0, 0]], [[1, 0]], [[2, 0]], [[3, 0]], [[4, 0]]], np.int32)
    laid = np.zeros((6, 1), bool)
    laid[3, 0] = True
    segs = [((5.0, 20.0), (55.0, 20.0))]
    path, foot = gw.trace(L, dist, pred, laid, (5, 0), segs, lambda here, f: True)
    assert len(path) == 2 and foot == (35.0, 20.0), "joined at the laid cell, square onto the way"
    path, foot = gw.trace(L, dist, pred, laid, (5, 0), segs, lambda here, f: False)
    assert len(path) == 5 and foot == (5.0, 20.0), "the leg refused: on to the way out"


def test_a_laid_way_marks_its_cells_within_the_join_radius() -> None:
    L = gw.Layers(0.0, 0.0, 10, 10, 5.0)
    laid = np.zeros((10, 10), bool)
    gw.mark_laid(L, laid, ((2.0, 2.0), (2.0, 40.0)), 1)
    assert laid[0, 0] and laid[1, 7] and not laid[3, 3]


def test_a_household_whose_ways_are_all_refused_gets_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """`_way_for`: up to `GAP_TRIES` distinct exits, each tried joined near, joined far and run on; None where the taut pull or
    the corridor's own admission refuses them all - and its homestead back among what stands."""
    s, houses = _site((600.0,))
    box = houses[0]["geom"]["bbox"]  # a wood seat just off its homestead: its own search keeps off that ground too
    s._wood = SimpleNamespace(lane_gap=6.0, corridor_bars=lambda a, b: False, seats=SimpleNamespace(n=1, buckets={(0, 0): [(box[0], box[1] + box[3] / 2 + 12.0)]}))
    seen: list[int] = []
    monkeypatch.setattr(gw, "taut", lambda pts, *a: seen.append(1) or (None if len(seen) % 2 else tuple(pts)))
    monkeypatch.setattr(gw, "admitted", lambda s_, run, g, memo: None)
    monkeypatch.setattr(gw, "GAP_TRIES", 2)
    assert gw.lay_the_ways(s) == (0, 0), "no way, and no neighbor with one to be reached across"
    assert "access" not in houses[0]["geom"] and any(b is houses[0]["geom"]["bbox"] for b in s.placed)
    assert len(seen) == 2 * 3, "two exits, three joins each"
