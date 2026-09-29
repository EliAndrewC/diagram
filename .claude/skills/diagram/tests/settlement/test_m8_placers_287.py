"""Feature 287 M8 at the settlement engine's placers: each asks the registry of what stands (the overlap matrix and the
seating's reservations) before it chooses, on constructed input including the violating case."""

from __future__ import annotations

import math
import random
from typing import Any

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.city.bridges import deck_admitted, undeckable_at
from l7r.diagram.settlement.civic_grounds.edge_seat import EdgeGround, edge_seat
from l7r.diagram.settlement.homestead_parts.groves import crown_lift
from l7r.diagram.settlement.homestead_parts.stands import crown_reach
from l7r.diagram.settlement.homestead_parts.wood_share import BAR_MARGIN_PX, ground_blocks, open_water_discs
from l7r.diagram.settlement.rolling import access, fit
from l7r.diagram.settlement.rolling.bundle import box_gap, boxes_meet, pocket_clear_of_beds
from l7r.diagram.settlement.rolling.lot import bundle_admitted, bundle_records, held_part_records

from ._builders import _crop_settlement


def _hamlet(W: float = 1400.0) -> Settlement:
    s = Settlement(W, W, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    return s


def test_the_well_pocket_is_never_laid_on_a_bed() -> None:
    """A bed split to flank the house on both walls stood where the pocket is laid (cohort 1-60: 8 wells on a bed). The
    pocket takes the flank with no bed, else steps past the outermost bed of its flank."""
    beds = [(30.0, 0.0, 12.0, 20.0)]
    assert pocket_clear_of_beds([30.0, -30.0], 0.0, 20.0, beds, 3.0) == (-30.0, 0.0, 20.0, 20.0), "the other flank"
    both = [(30.0, 0.0, 12.0, 20.0), (-30.0, 0.0, 12.0, 20.0), (50.0, 0.0, 12.0, 20.0)]
    x, y, w, h = pocket_clear_of_beds([30.0, -30.0], 0.0, 20.0, both, 3.0)
    assert (x, y) == (69.0, 0.0) and not any(boxes_meet((x, y, w, h), b) for b in both), "past the outermost bed, on its flank"
    assert pocket_clear_of_beds([-30.0, 30.0], 0.0, 20.0, both, 3.0)[0] == -49.0
    assert not boxes_meet((0.0, 0.0, 10.0, 10.0), (10.0, 0.0, 10.0, 10.0)), "sharing an edge is not meeting"


def test_a_corridor_keeps_off_its_own_beds_and_house_and_leaves_its_yard_once() -> None:
    s = _hamlet()
    geom = s._bundle_geom(700.0, 700.0, 46.0, 28.0, "E", rot=0.0)
    bed = geom["boxes"]["gardens"][0]
    assert not access.parts_clear(s, (bed[0], bed[1] - 100.0), (bed[0], bed[1] + 100.0), geom), "a line across its own bed"
    assert access.parts_clear(s, (bed[0] + 200.0, 0.0), (bed[0] + 200.0, 1400.0), geom)
    hx, hy, hw, hh = geom["boxes"]["house"]
    gap = access.house_gap(s)
    assert gap == 1.5 + 2.0 + 0.5
    edge = hx + hw / 2
    assert not access.house_clear((edge + gap - 0.5, 0.0), (edge + gap - 0.5, 1400.0), geom, gap), "within the web's bar of its wall"
    assert access.house_clear((edge + gap + 0.5, 0.0), (edge + gap + 0.5, 1400.0), geom, gap)
    yard = (0.0, 0.0, 20.0, 10.0)
    assert access.leaves_its_yard(((0.0, 0.0), (0.0, 50.0)), yard, 2.0)
    assert not access.leaves_its_yard(((0.0, 0.0), (0.0, 50.0), (0.0, -50.0)), yard, 2.0), "out and back across it"
    assert access.leaves_its_yard(((0.0, 0.0), (0.0, 50.0)), None, 2.0), "no yard"


def test_a_lane_rewrite_the_matrix_refuses_is_not_written_and_a_draft_way_is_laid_only_where_admitted() -> None:
    s = _hamlet()
    s.M["gardens"].append({"x": 200.0, "y": 100.0, "w": 20.0, "h": 20.0, "rot": 0.0})
    s.lane([(0.0, 200.0), (400.0, 200.0)], width=3, worn=True)
    ln = s.M["lanes"][0]
    assert not s.reshape_lane(ln, [(0.0, 100.0), (400.0, 100.0)]) and ln["pts"] == [[0.0, 200.0], [400.0, 200.0]]
    assert s.reshape_lane(ln, [(0.0, 200.0), (300.0, 200.0)]) and ln["pts"][-1] == [300.0, 200.0]
    runs = s.admitted_runs([(0.0, 100.0), (100.0, 100.0), (180.0, 100.0), (260.0, 100.0), (400.0, 100.0)], 3.0)
    assert runs == [[(0.0, 100.0), (100.0, 100.0), (180.0, 100.0)], [(260.0, 100.0), (400.0, 100.0)]], "the arm is cut where it crosses the bed"
    assert s.admitted_runs([(150.0, 100.0), (250.0, 100.0)], 3.0) == []
    assert s.admits_lane([(0.0, 0.0)], 3.0), "a single point lays nothing"


def test_the_seats_ground_holds_the_copse_off_the_pond_and_the_toe_a_hair_stricter() -> None:
    M = {"pond": [500.0, 500.0, 60.0, 40.0], "torii": [[100.0, 100.0, 0]], "crescent_ponds": [{"cx": 800.0, "cy": 800.0, "r": 30.0}], "religious": [{"x": 900.0, "y": 100.0, "w": 20.0, "h": 20.0}]}
    discs = open_water_discs(M, 22.0)
    reach = 22.0 * 0.90 + BAR_MARGIN_PX
    assert (500.0, 500.0, 60.0 + reach) in discs and (800.0, 800.0, 30.0 + reach) in discs and len(discs) == 4
    assert open_water_discs({}, 22.0) == []
    s = _hamlet()
    s.toe_band = lambda *a, **k: [(0.0, 1000.0), (1400.0, 1000.0), (1400.0, 1400.0), (0.0, 1400.0)]  # type: ignore[method-assign]
    g = ground_blocks(s, 22.0)
    assert g.hard(700.0, 1200.0), "inside the toe marsh to be"
    assert g.hard(700.0, 999.8), "within the placer's margin of its edge"
    assert not g.hard(700.0, 990.0)


def test_crown_reach_is_the_reach_the_grove_draws() -> None:
    """Cohort seed 31: a copse crown's trunk drawn 15.3 px from its clump where the reach allowed 15.0 - the lift was taken
    as 3 px and `_draw_grove` draws 3 * bscale / 0.82. Every crown the grove draws, over many clumps, lies within the reach."""
    s = _hamlet()
    lift = crown_lift(s.bscale)
    assert math.isclose(lift, 3.0 / 0.82)
    reach = crown_reach(22.0, lift=lift)
    rnd = random.Random(31)
    far = 0.0
    for _ in range(200):
        cx, cy = rnd.uniform(100.0, 1300.0), rnd.uniform(100.0, 1300.0)
        s.M["tree_crowns"] = []
        s._draw_grove(cx, cy, 22.0, 22.0, face=(0, -1), mix="dooryard")
        flat = s.M["tree_crowns"]
        far = max([far, *(math.dist((cx, cy), (flat[i], flat[i + 1])) for i in range(0, len(flat), 3))])
    assert far <= reach and far > crown_reach(22.0, lift=3.0), "the old reach fell short of what is drawn"


def test_a_shared_sheds_pocket_keeps_off_the_access_tree() -> None:
    s = _hamlet()
    access.start_tree(s, (700.0, 700.0), (1.0, 0.0), 400.0)
    assert not s._commons_pocket_clear(900.0, 740.0, 16.0, 11.0, []), "beside the exit strip: its approach"
    assert s._commons_pocket_clear(900.0, 900.0, 16.0, 11.0, [])


def test_a_footplank_the_registry_refuses_slides_along_its_ditch() -> None:
    """A plank's landing on a fallow patch - GROUND the matrix keeps a deck off, which no other test of the plank reads."""
    s = _crop_settlement()
    s.M["fields"] = [{"outline": [[50, 220], [750, 220], [750, 380], [50, 380]]}]
    s.M["field_ditches"] = [{"poly": [[100, 300], [700, 300]], "w": 5, "role": "main"}]
    s.M["fallow_patches"] = [{"poly": [[380, 280], [420, 280], [420, 320], [380, 320]]}]
    assert s.channel_footbridges(spacing=800) == 1
    b = s.M["bridges"][0]
    assert not (380 - b["w"] / 2 <= b["x"] <= 420 + b["w"] / 2), "slid off the fallow patch"
    s2 = _crop_settlement()
    s2.M["fields"] = s.M["fields"]
    s2.M["field_ditches"] = s.M["field_ditches"]
    assert s2.channel_footbridges(spacing=800) == 1 and 380 <= s2.M["bridges"][0]["x"] <= 420, "the case: without the patch it lands there"


def test_a_carried_deck_the_registry_refuses_is_a_crossing_no_deck_seats() -> None:
    s = _crop_settlement()
    waters = [([(0.0, 300.0), (1000.0, 300.0)], 6.0)]
    way = [(500.0, 100.0), (500.0, 500.0)]
    assert undeckable_at(way, 6.0, waters, 1.0, (), s.M) == []
    assert deck_admitted({}, (500.0, 300.0), 90.0, 20.0, 6.0), "a bare manifest has no registry"
    s.M["houses"].append({"x": 500.0, "y": 312.0, "w": 20.0, "h": 6.0, "rot": 0.0})
    assert [k for k, _p in undeckable_at(way, 6.0, waters, 1.0, (), s.M)] == [0], "a house where the deck would land"
    s.M["bridges"].append({"x": 500.0, "y": 300.0, "rot": 90.0, "span": 20.0, "w": 6.0})
    assert not deck_admitted(s.M, (500.0, 300.0), 90.0, 20.0, 6.0), "a deck on another is merged, not refused - the house refuses it"


def test_a_burial_ground_is_not_seated_on_an_access_corridor() -> None:
    s = _hamlet()
    for x in (600.0, 800.0):
        s.M["houses"].append({"x": x, "y": 600.0, "w": 40.0, "h": 28.0, "rot": 0.0})
    ground = EdgeGround(s, clear_px=60.0, stream_px=0.0, ditch_px=0.0, field_px=0.0)
    free = edge_seat(s, 90.0, 60.0, 40.0, ground, reach_px=400.0, step_px=20.0)
    assert free is not None
    s.standing.reserved.reserve_corridor((free[0] - 200.0, free[1]), (free[0] + 200.0, free[1]), 7.0)
    moved = edge_seat(s, 90.0, 60.0, 40.0, ground, reach_px=400.0, step_px=20.0)
    assert moved is not None and moved != free
    rec = {"x": round(moved[0], 1), "y": round(moved[1], 1), "w": 60.0, "h": 40.0, "rot": 0.0}
    assert s.admits("cemeteries", rec) and not s.admits("cemeteries", dict(rec, x=round(free[0], 1), y=round(free[1], 1)))


# ---- water W53: every part a bundle lays asks the registry of what stands first -------------------------------------


def _laid_bundle(s: Settlement, x: float = 700.0, y: float = 700.0) -> dict[str, Any]:
    """A nucleated bundle at (x, y) laying a well pocket and a privy - the parts the hold stands at the seating's end."""
    s._nucleated, s._household_well, s._household_fixtures = True, True, ("privy",)
    try:
        return s._bundle_geom(x, y, 46.0, 28.0, "E", rot=0.0)
    finally:
        s._household_well, s._household_fixtures = False, ()


def _ditch_at(s: Settlement, x: float, y: float) -> None:
    s.M["field_ditches"].append({"poly": [[x - 1.0, y], [x + 1.0, y]], "w": 1.5})


def test_every_part_a_bundle_lays_asks_the_registry_first() -> None:
    """Under feature 284's probes Inashiro laid a privy on a field ditch that no fit rule asked about, and the hold at the
    seating's end raised `OverlapRefused` (research R9, failure 4). Each part - the house, its yard, each bed, the well
    pocket, the privy - is asked as the record it will stand as; a ditch under any one of them refuses the layout."""
    s = _hamlet()
    geom = _laid_bundle(s)
    recs = bundle_records(geom, s._well_vr())
    assert {k for k, _r in recs} == {"houses", "threshing_yards", "gardens", "wells", "farm_fixtures"}
    assert bundle_admitted(s, geom), "nothing stands: admitted"
    for key, rec in recs:
        t = _hamlet()
        _ditch_at(t, rec["x"], rec["y"])
        assert not bundle_admitted(t, geom), f"a ditch under its {key}"
    far = _hamlet()
    _ditch_at(far, 100.0, 100.0)
    assert bundle_admitted(far, geom)


def test_the_held_parts_are_the_records_the_seat_asked_about() -> None:
    """The hold and the seat's question build one record per part (`held_part_records`), so a part the seat was admitted
    with is held on ground the registry admitted."""
    s = _hamlet()
    geom = _laid_bundle(s)
    box = list(geom["boxes"]["fixtures"]["privy"])
    held = held_part_records(geom["house"][0], geom["house"][1], geom["well"], [("privy", box), ("persimmon", box), ("coop", None)], s._well_vr())
    assert held == [r for r in bundle_records(geom, s._well_vr()) if r[0] in ("wells", "farm_fixtures")]
    assert [k for k, _r in held_part_records(0.0, 0.0, None, [("retirement", [1.0, 1.0, 4.0, 4.0])], 12.0)] == ["retirement_houses"]


def test_the_bundle_fit_refuses_a_layout_the_registry_refuses(monkeypatch: pytest.MonkeyPatch) -> None:
    """The placers ask it: `_bundle_fits` (the dispersed spiral and the slides) and `_parts_fit` (the nucleated envelope)
    refuse a layout one of whose parts the registry refuses, and admit it where nothing stands under it."""
    s = _hamlet()
    geom = _laid_bundle(s)
    monkeypatch.setattr(type(s), "_bundle_common_fits", lambda self, g, grove_off_field=True: True)
    monkeypatch.setattr(type(s), "_bundle_side_fits", lambda self, g: True)
    assert s._bundle_fits(geom)
    privy = geom["boxes"]["fixtures"]["privy"]
    _ditch_at(s, privy[0], privy[1])
    assert not s._bundle_fits(geom), "the privy on a ditch"
    t = _hamlet()
    monkeypatch.setattr(fit, "within_field_reach", lambda *a: True)
    for rule in ("_candidate_watered", "_gardens_sun_ok", "_sun_corridor_ok"):
        monkeypatch.setattr(type(t), rule, lambda self, *a: True)
    assert t._parts_fit(geom)
    _ditch_at(t, privy[0], privy[1])
    assert not t._parts_fit(geom), "the privy on a ditch"


def test_a_shared_shed_and_a_sty_ask_the_registry_first() -> None:
    s = _hamlet()
    assert s._commons_pocket_clear(900.0, 900.0, 16.0, 11.0, [])
    _ditch_at(s, 900.0, 900.0)
    assert not s._commons_pocket_clear(900.0, 900.0, 16.0, 11.0, []), "a shed's pocket on a ditch"
    t = Settlement(W=400, H=400, seed=1)
    assert t.pond_fixture_fits(300.0, 300.0, 0.0)
    _ditch_at(t, 300.0, 300.0)
    assert not t.pond_fixture_fits(300.0, 300.0, 0.0), "a sty on a ditch"


def test_a_pushed_well_pocket_keeps_its_gap_from_every_bed() -> None:
    """Homes H09: past the beds the pocket keeps `gap` from each - a bed it would clear by a hair beside the line (here 1 px
    above the pocket's row, not meeting it) is stepped past too."""
    assert box_gap((0.0, 0.0, 10.0, 10.0), (10.0, 0.0, 10.0, 10.0)) == 0.0 and box_gap((0.0, 0.0, 10.0, 10.0), (0.0, 0.0, 2.0, 2.0)) < 0
    assert box_gap((0.0, 0.0, 10.0, 10.0), (5.0, 13.0, 10.0, 10.0)) == 3.0, "beside, clear on one axis alone"
    beds = [(30.0, 0.0, 12.0, 20.0), (-30.0, 0.0, 12.0, 20.0), (60.0, 21.0, 12.0, 20.0)]
    old_x = 36.0 + 3.0 + 10.0  # the old push: past the one bed it lay on, 1 px beside the next
    assert box_gap((old_x, 0.0, 20.0, 20.0), beds[2]) == 1.0, "the violating case: under the gap"
    got = pocket_clear_of_beds([30.0, -30.0], 0.0, 20.0, beds, 3.0)
    assert got == (79.0, 0.0, 20.0, 20.0) and min(box_gap(got, b) for b in beds) >= 3.0
