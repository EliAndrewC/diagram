"""Feature 320: no ways placed before the homesteads - the gate decided once the last house stands (`household_ways`), the
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


# ---- the gate and its root ---------------------------------------------------------------------------------------------


def test_a_box_is_its_four_corners() -> None:
    assert hw.box_poly((10.0, 20.0, 4.0, 6.0)) == [(8.0, 17.0), (12.0, 17.0), (12.0, 23.0), (8.0, 23.0)]


def test_the_gate_is_walked_out_until_its_first_leg_clears_every_wood_seat() -> None:
    """`clear_of_the_seats`: a leg already clear stays; a seat beside the leg walks the gate on in `GATE_STEP_PX` steps until it
    clears by `reach`; a seat the leg never clears leaves the gate `GATE_STEPS` steps out, the last point tried."""
    assert hw.GATE_STEP_PX == 6.0 and hw.GATE_STEPS == 40
    assert hw.clear_of_the_seats((0.0, 0.0), (1.0, 0.0), 40.0, [(0.0, 100.0)], 20.0) == (0.0, 0.0), "clear as it stands"
    g = hw.clear_of_the_seats((0.0, 0.0), (2.0, 0.0), 40.0, [(20.0, 10.0)], 20.0)  # the bearing need not be a unit
    assert g[1] == 0.0 and g[0] > 20.0 and g[0] % hw.GATE_STEP_PX == 0.0, "walked past the seat, in whole steps"
    assert seg_dist(20.0, 10.0, g, (g[0] + 40.0, 0.0)) > 20.0 >= seg_dist(20.0, 10.0, (g[0] - 6.0, 0.0), (g[0] + 34.0, 0.0)), "the first step that clears"
    walled = [(x, 0.0) for x in range(0, 400, 10)]  # seats all the way along: none clears
    assert hw.clear_of_the_seats((0.0, 0.0), (1.0, 0.0), 40.0, walled, 5.0) == (hw.GATE_STEPS * hw.GATE_STEP_PX, 0.0)
    assert hw.clear_of_the_seats((5.0, 5.0), (0.0, 0.0), 40.0, [(100.0, 100.0)], 5.0) == (5.0, 5.0), "no bearing: the gate as it is"


def test_the_seat_walls_are_every_households_wood_seats_and_the_lanes_reach_off_them() -> None:
    s = _open()
    s.M["houses"] = [{"x": 1, "y": 1, "wood_share": {"seats": [[10, 11], [12, 13]]}}, {"x": 5, "y": 5}, {"x": 6, "y": 6, "wood_share": {}}]
    seats, reach = hw.seat_walls(s)
    assert seats == [(10.0, 11.0), (12.0, 13.0)] and reach > 4.0
    assert hw.seat_walls(_open()) == ([], reach), "no houses: no seats, the same reach"


def test_a_point_is_held_inside_the_canvas() -> None:
    s = _open()
    m = hw.CANVAS_INSET_PX
    assert m == 12.0 and hw.on_the_canvas(s, (500.0, 500.0)) == (500.0, 500.0)
    assert hw.on_the_canvas(s, (-50.0, 2000.0)) == (m, 1000.0 - m) and hw.on_the_canvas(s, (1000.0, 0.0)) == (1000.0 - m, m)


def test_the_root_is_the_track_outs_first_leg_from_the_gate_held_on_the_canvas() -> None:
    s = _open()
    assert hw.ROOT_FT == 40.0
    assert hw.root_at_the_gate(s, (500.0, 500.0), (0.0, 2.0)) == ((500.0, 500.0), (500.0, 540.0))
    assert hw.root_at_the_gate(s, (500.0, 980.0), (0.0, 1.0)) == ((500.0, 980.0), (500.0, 1000.0 - hw.CANVAS_INSET_PX)), "held on the canvas"
    assert hw.root_at_the_gate(s, (500.0, 500.0), (0.0, 0.0)) == ((500.0, 500.0), (500.0, 500.0)), "no bearing: no length"


def test_the_gate_stands_past_the_farthest_homestead_clear_of_the_seats_and_out_of_the_field() -> None:
    """`way_out_gate`: from the houses' center along the bearing, past the farthest homestead box by `GATE_CLEAR_FT`; a wood
    seat beside its first leg walks it on; a field over it pushes it out; the canvas holds it."""
    s = _open()
    s.M["houses"] = [{"x": 400.0, "y": 500.0}, {"x": 600.0, "y": 500.0}]
    s.placed = [(400.0, 500.0, 60.0, 40.0), (600.0, 520.0, 60.0, 40.0)]
    plan = SimpleNamespace(envelope=[(0.0, 0.0), (40.0, 0.0), (40.0, 40.0), (0.0, 40.0)])  # a field far off
    g = hw.way_out_gate(s, plan, (0.0, 1.0))
    assert g[0] == 500.0 and g[1] >= 540.0 + hw.GATE_CLEAR_FT, "past the farthest box's edge (y 540) by the clearance"
    s.M["houses"][0]["wood_share"] = {"seats": [[500.0, g[1] + 20.0]]}
    walked = hw.way_out_gate(s, plan, (0.0, 1.0))
    _, reach = hw.seat_walls(s)
    assert walked[0] == 500.0 and walked[1] > g[1] and seg_dist(500.0, g[1] + 20.0, walked, (500.0, walked[1] + hw.ROOT_FT)) > reach
    field = [(0.0, walked[1] - 10.0), (1000.0, walked[1] - 10.0), (1000.0, walked[1] + 60.0), (0.0, walked[1] + 60.0)]
    out = hw.way_out_gate(s, SimpleNamespace(envelope=field), (0.0, 1.0))
    assert out == gate_out_of_the_field(field, walked), "pushed out of the field's envelope"
    s.placed.append((960.0, 500.0, 60.0, 40.0))  # a homestead by the canvas's east edge, the bearing out over it
    assert hw.way_out_gate(s, plan, (1.0, 0.0))[0] == 1000.0 - hw.CANVAS_INSET_PX, "held on the canvas"
    s.M["houses"] = []
    s.placed = []
    assert hw.way_out_gate(s, plan, (0.0, 1.0)) == (hw.CANVAS_INSET_PX, hw.GATE_CLEAR_FT), "nothing seated: from the corner, off the field and back on the canvas"


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
    empty, the registry holds no corridor, the manifest records no way, no gate and no root - and the anchor is painted into
    no buildable cell (what the buildable raster takes, the lane raster takes too). Once the last house stands the gate and
    its root are recorded and no exit strip ever is."""
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
        assert not {"access_exit", "way_out_gate", "way_out_root"} & set(st.M), "no strip, no gate, no root"
        got = opens(self, geom)
        assert not ((self.buildable.array() != 0) & (self.lane.array() == 0)).any(), "the anchor painted into no buildable cell"
        seen.append(len(st.M["houses"]))
        return got

    monkeypatch.setattr(SeatRegion, "opens", watched)
    stages.stage_homesteads(s, plan)
    assert seen and len(s.M["houses"]) == 10, "the seating asked, and seated every household"
    assert "access_exit" not in s.M and len(s.M["way_out_root"]) == 2 and s.M["way_out_root"][0] == s.M["way_out_gate"]


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
