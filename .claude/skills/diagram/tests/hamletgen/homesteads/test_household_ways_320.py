"""Feature 320: no ways placed before the homesteads - the track out chosen once the last house stands (`household_ways`), the
seating's reach seeded from the way-out side (`region.anchor_in_window`), and nothing of a way reserved or recorded while
the houses are seated (SC-001, SC-002)."""

from __future__ import annotations

import math
from types import SimpleNamespace

import pytest

from l7r.diagram.hamletgen.homesteads import household_ways as hw
from l7r.diagram.hamletgen.homesteads import region as rg
from l7r.diagram.hamletgen.homesteads import stages
from l7r.diagram.hamletgen.homesteads.region import SeatRegion, _clip, anchor_in_window
from l7r.diagram.hamletgen.ways.cluster_edge import gate_out_of_the_field
from l7r.diagram.hamletgen.ways.geom import push_out_of
from l7r.diagram.settlement import Settlement, seg_dist
from l7r.diagram.settlement.rolling.access import ACCESS_HALF_FT, AccessTree
from tests.hamletgen._builders import CROWN, a_plan


def _open(W: float = 1000.0) -> Settlement:
    s = Settlement(W, W, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    return s


# ---- the track out, chosen once --------------------------------------------------------------------------------------------


def test_a_box_is_its_four_corners() -> None:
    assert hw.box_poly((10.0, 20.0, 4.0, 6.0)) == [(8.0, 17.0), (12.0, 17.0), (12.0, 23.0), (8.0, 23.0)]


def test_the_seat_walls_are_every_households_wood_seats_and_the_lanes_reach_off_them() -> None:
    s = _open()
    s.M["houses"] = [{"x": 1, "y": 1, "wood_share": {"seats": [[10, 11], [12, 13]]}}, {"x": 5, "y": 5}, {"x": 6, "y": 6, "wood_share": {}}]
    seats, reach = hw.seat_walls(s)
    assert seats == [(10.0, 11.0), (12.0, 13.0)] and reach > 4.0
    assert hw.seat_walls(_open()) == ([], reach), "no houses: no seats, the same reach"


def test_the_homesteads_as_seated_are_every_households_parts_and_its_wood_seats() -> None:
    """`seated_parts`: each household's house, yard, well, shed, byre, gardens and fixtures from its seated boxes - a persimmon
    by its `TRUNK_FT` trunk alone - owned by its house; every wood seat an octagon of the reach a lane keeps off it, owned by
    none. A household with no geometry yet gives only its seats."""
    s = _open()
    assert hw.TRUNK_FT == 4.0
    boxes = {
        "house": (100.0, 100.0, 40.0, 20.0),
        "yard": (100.0, 130.0, 30.0, 30.0),
        "well": (130.0, 100.0, 6.0, 6.0),
        "shed": None,
        "byre": (70.0, 100.0, 10.0, 10.0),
        "gardens": [(100.0, 170.0, 20.0, 10.0)],
        "fixtures": {"persimmon": (150.0, 150.0, 30.0, 30.0), "kiln": (60.0, 60.0, 8.0, 8.0)},
    }
    s.M["houses"] = [{"x": 100, "y": 100, "geom": {"boxes": boxes}, "wood_share": {"seats": [[300, 300]]}}, {"x": 5, "y": 5}]
    parts = hw.seated_parts(s)
    kinds = [k for _p, _o, k in parts]
    assert kinds == ["houses", "threshing_yards", "wells", "sheds", "gardens", "fixtures", "fixtures", "wood seats"], "no shed seated: none drawn"
    assert all(o == (100.0, 100.0) for _p, o, _k in parts[:-1]) and parts[-1][1] is None
    assert parts[0][0] == hw.box_poly(boxes["house"]) and parts[4][0] == hw.box_poly(boxes["gardens"][0])
    assert parts[5][0] == hw.box_poly((150.0, 150.0, 4.0, 4.0)), "a persimmon by its trunk"
    assert parts[6][0] == hw.box_poly(boxes["fixtures"]["kiln"]), "any other fixture by its box"
    _seats, reach = hw.seat_walls(s)
    ring = parts[-1][0]
    assert len(ring) == 8 and all(math.dist(q, (300.0, 300.0)) == pytest.approx(reach) for q in ring), "an octagon of the reach"
    assert hw.seated_parts(_open()) == [], "nothing seated: nothing"


def test_the_ways_are_laid_to_the_tracks_stretch_about_the_cluster() -> None:
    """`near_the_cluster`: each leg of the track clipped to the placed boxes' extent grown by the margin; a leg wholly
    outside, or touching it at a point, is left out; with nothing placed, every leg."""
    s = _open()
    track = [(100.0, 100.0), (100.0, 300.0), (500.0, 300.0), (500.0, 900.0)]
    s.placed = []
    assert hw.near_the_cluster(s, track, 10.0) == list(zip(track, track[1:], strict=False)), "nothing placed: every leg"
    s.placed = [(100.0, 100.0, 40.0, 40.0), (200.0, 200.0, 20.0, 20.0)]  # extent 80..210 either way; grown by 10, 70..220
    got = hw.near_the_cluster(s, track, 10.0)
    assert got == [((100.0, 100.0), (100.0, 220.0))], "the first leg clipped; the rest beyond the extent"
    corner = hw.near_the_cluster(s, [(230.0, 210.0), (210.0, 230.0)], 10.0)  # touches the grown extent's corner (220, 220) only
    assert corner == [], "a leg meeting the extent at a point is no stretch"


def test_the_track_is_chosen_with_the_homesteads_as_seated_standing_in_and_they_are_cleared_after(monkeypatch: pytest.MonkeyPatch) -> None:
    """`chose_the_track`: `choose_track_out` asked with the seated parts on `s._seated_parts` (so `fabric._homestead_polys`
    reads them), and cleared after - even when the choice raises."""
    from l7r.diagram.hamletgen.ways import fabric, track

    s = _open()
    s.M["houses"] = [{"x": 100, "y": 100, "geom": {"boxes": {"house": (100.0, 100.0, 40.0, 20.0)}}}]
    drawn = [{"x": 100, "y": 100, "w": 40, "h": 20}]  # the farmhouses as `fabric._homestead_polys` reads them, swapped in to ask it
    plan = SimpleNamespace()
    seen: list = []

    def choose(st: Settlement, pl: object) -> list:
        assert pl is plan
        seen.append([k for _p, _o, k in fabric._homestead_polys(SimpleNamespace(M={}, _seated_parts=st._seated_parts))])
        return [(1.0, 1.0), (2.0, 2.0)]

    monkeypatch.setattr(track, "choose_track_out", choose)
    assert hw.chose_the_track(s, plan) == [(1.0, 1.0), (2.0, 2.0)]
    assert seen == [["houses"]] and s._seated_parts is None, "read while chosen, cleared after"
    assert [k for _p, _o, k in fabric._homestead_polys(SimpleNamespace(M={"houses": drawn}, _seated_parts=s._seated_parts))] == ["houses"], "once cleared, only the drawn"

    def fails(st: Settlement, pl: object) -> list:
        raise RuntimeError("no way out")

    monkeypatch.setattr(track, "choose_track_out", fails)
    with pytest.raises(RuntimeError):
        hw.chose_the_track(s, plan)
    assert s._seated_parts is None, "cleared even when the choice raises"


def test_the_gate_is_pushed_out_of_the_field_and_a_gate_clear_of_it_stays() -> None:
    field = [(650.0, 650.0), (760.0, 650.0), (760.0, 760.0), (650.0, 760.0)]
    from l7r.diagram.hamletgen.ways.track import SPUR_SETBACK

    assert gate_out_of_the_field(field, (700.0, 703.0)) == push_out_of(field, (700.0, 703.0), SPUR_SETBACK)
    assert gate_out_of_the_field(field, (100.0, 100.0)) == (100.0, 100.0)


# ---- the reach seed ----------------------------------------------------------------------------------------------------


def test_a_segment_is_clipped_to_a_box() -> None:
    box = (0.0, 0.0, 100.0, 100.0)
    assert _clip((50.0, 50.0), (60.0, 60.0), box) == (0.0, 1.0), "inside"
    assert _clip((-50.0, 50.0), (150.0, 50.0), box) == (0.25, 0.75), "across"
    assert _clip((-50.0, 150.0), (150.0, 150.0), box) is None, "level, beyond the box"
    assert _clip((200.0, 50.0), (300.0, 50.0), box) is None, "beyond, along"
    assert _clip((50.0, 50.0), (50.0, 50.0), box) == (0.0, 1.0), "a point inside"


def test_the_anchor_seeds_the_reach_inside_the_window_or_at_its_edge_or_not_at_all() -> None:
    """`anchor_in_window`: the near-far stretch where it lies inside the window inset a cell; where it lies wholly past the
    edge, the last two cells of the bearing out inside it; None where the bearing out never enters the window."""
    win, cell = (0.0, 0.0, 400.0, 400.0), 8.0
    assert anchor_in_window(((200.0, 200.0), (200.0, 250.0), (200.0, 300.0)), win, cell) == ((200.0, 250.0), (200.0, 300.0))
    assert anchor_in_window(((200.0, 200.0), (200.0, 300.0), (200.0, 600.0)), win, cell) == ((200.0, 300.0), (200.0, 392.0)), "clipped"
    off = anchor_in_window(((200.0, 200.0), (200.0, 500.0), (200.0, 900.0)), win, cell)
    assert off is not None and [*off[0], *off[1]] == pytest.approx([200.0, 376.0, 200.0, 392.0]), "wholly past the edge: the last two cells inside"
    assert anchor_in_window(((900.0, 900.0), (950.0, 950.0), (990.0, 990.0)), win, cell) is None, "never in the window"
    level = anchor_in_window(((-50.0, 200.0), (-40.0, 200.0), (-10.0, 200.0)), win, cell)
    assert level is None, "the bearing out runs off the window's west edge and never enters it"


# ---- SC-001: nothing reserved or recorded for a way before the last house ----------------------------------------------


def test_sc001_nothing_is_reserved_or_recorded_for_a_way_while_the_houses_are_seated(monkeypatch: pytest.MonkeyPatch) -> None:
    """SC-001: on a nucleated roll, every time the seating asks whether a homestead opens onto lane ground the access tree is
    empty, the registry holds no corridor, the manifest records no way, no gate and no track out - and the anchor is painted into
    no buildable cell (what the buildable raster takes, the lane raster takes too). Once the last house stands the track
    out is recorded, its first point the gate, and no exit strip ever is."""
    plan = a_plan(households=10)
    plan.envelope = list(CROWN)
    plan.seat = __import__("l7r.diagram.hamletgen", fromlist=["seat_cluster"]).seat_cluster(plan)
    plan.settlement_form = "nucleated"
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    s._nucleated = True
    s.field_polys.append(list(plan.envelope))
    seen: list[int] = []
    opens = SeatRegion.opens

    def watched(self: SeatRegion, geom: object) -> bool:
        st = self.s
        assert st._access is not None and st._access.segs == [], "the tree is empty while houses are seated"
        assert st.M["access_corridors"] == [] and not st.standing.reserved.corridors, "no way recorded or reserved"
        assert not {"access_exit", "way_out_gate", "way_out_track"} & set(st.M), "no strip, no gate, no track"
        got = opens(self, geom)
        assert not ((self.buildable.array() != 0) & (self.lane.array() == 0)).any(), "the anchor painted into no buildable cell"
        seen.append(len(st.M["houses"]))
        return got

    monkeypatch.setattr(SeatRegion, "opens", watched)
    stages.stage_homesteads(s, plan)
    assert seen and len(s.M["houses"]) == 10, "the seating asked, and seated every household"
    assert "access_exit" not in s.M and len(s.M["way_out_track"]) >= 2 and s.M["way_out_track"][0] == s.M["way_out_gate"]


# ---- SC-007: the track drawn is the track chosen, and every household's way ends on it --------------------------------


def _on_a_run(q: tuple[float, float], runs: list[list[tuple[float, float]]], tol: float) -> bool:
    """Whether `q` lies within `tol` of any leg of any of `runs`."""
    return any(seg_dist(q[0], q[1], a, b) <= tol for run in runs for a, b in zip(run, run[1:], strict=False))


def test_sc007_the_connector_drawn_is_the_track_chosen_and_every_way_ends_on_it_or_an_earlier_way() -> None:
    """SC-007 (feature 320, FR-008): on a nucleated roll, the track out chosen once the last house stood (`way_out_track`) is
    the connector `stage_track` draws, point for point; and every household's way, in the order laid, ends on that track or
    on a way laid before it - no way is laid to a track that is then drawn somewhere else."""
    from l7r.diagram.hamletgen import seat_cluster
    from l7r.diagram.hamletgen.ways import track as tr

    plan = a_plan(households=10)
    plan.envelope = list(CROWN)
    plan.seat = seat_cluster(plan)
    plan.settlement_form = "nucleated"
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    s._nucleated = True
    s.field_polys.append(list(plan.envelope))
    stages.stage_homesteads(s, plan)
    chosen = [tuple(q) for q in s.M["way_out_track"]]
    assert len(chosen) >= 2 and list(chosen[0]) == s.M["way_out_gate"], "the track chosen, its first point the gate"
    ways: list[list[tuple[float, float]]] = []
    for leg in s.M["access_corridors"]:  # a record per leg, door first; a household's first leg names its house (`access.reserve`)
        a, b = ((float(q[0]), float(q[1])) for q in leg["pts"])
        if "of" in leg:
            ways.append([a])
        ways[-1].append(b)
    assert ways and len(ways) == sum(1 for h in s.M["houses"] if h["geom"].get("access")), "every household's way was laid, and read back"
    for k, way in enumerate(ways):
        assert _on_a_run(way[-1], [chosen, *ways[:k]], 1.0), f"way {k} ends at {way[-1]}, on neither the track nor an earlier way"
    tr.stage_track(s, plan)
    drawn = [ln for ln in s.M["lanes"] if ln.get("connector")]
    assert len(drawn) == 1 and [tuple(q) for q in drawn[0]["pts"]] == chosen, "the connector drawn is the track chosen, exactly"


# ---- SC-002: a dooryard opening only onto ground cut off from the anchor is not open ---------------------------------------


def test_sc002_a_dooryard_beyond_the_water_from_the_anchor_does_not_open() -> None:
    """SC-002: a brook down the window's middle at its clearance, the anchor on its west side: a dooryard on the west opens
    onto lane ground connected to the way out; one on the east, beyond the water, does not."""
    s = _open(400.0)
    s.placed = []
    s._access = AccessTree(s.px(ACCESS_HALF_FT))
    s._site_corridors = SimpleNamespace(water=[((200.0, 0.0), (200.0, 400.0), 12.0)])
    s._way_out_anchor = ((100.0, 200.0), (60.0, 200.0), (20.0, 200.0))
    region = SeatRegion(s, (0.0, 0.0, 400.0, 400.0))
    west = {"house": (100.0, 100.0, 46.0, 28.0), "yard": (100.0, 140.0, 40.0, 30.0)}
    east = {"house": (300.0, 100.0, 46.0, 28.0), "yard": (300.0, 140.0, 40.0, 30.0)}
    assert region.opens(west), "connected ground"
    assert not region.opens(east), "beyond the water from the anchor"
    s._way_out_anchor = ((300.0, 200.0), (340.0, 200.0), (380.0, 200.0))
    flipped = SeatRegion(s, (0.0, 0.0, 400.0, 400.0))
    assert flipped.opens(east) and not flipped.opens(west), "the anchor decides which side is reached"
    s._way_out_anchor = None
    assert not SeatRegion(s, (0.0, 0.0, 400.0, 400.0)).opens(west), "no anchor, no legs: nothing reached"
    assert math.isfinite(rg.SEAT_REGION_CELL)
