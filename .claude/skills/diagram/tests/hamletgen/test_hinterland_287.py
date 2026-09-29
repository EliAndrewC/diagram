"""Feature 287, the woods area in `hamletgen/hinterland/`: each guarantee's placer on constructed inputs that include the
violating case - the view decided once and the scatter thrown to it (M6, water W52), the parcels' row and picture rules
(woods W04, W14), the title pocket's keep-clear (water W58), the bamboo off the treads (woods W24) and the belt on the
wind's side of the houses (woods W18).
"""

from __future__ import annotations

import math

import pytest

from l7r.diagram.hamletgen import hinterland
from l7r.diagram.hamletgen.hinterland import parcels
from l7r.diagram.hamletgen.hinterland.bamboo import BAMBOO_SAMPLE_FT, bamboo_seats, stand_samples
from l7r.diagram.hamletgen.hinterland.frame import TITLE_POCKET_CLEAR_FT, clear_pocket_spot, pocket_clear_of_features, throw_to_the_view
from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist
from l7r.diagram.settlement.land.cover import ring_center

from ._builders import a_plan

# ---- M6 / water W52: the scatter thrown to the decided view ---------------------------------------------------------


def test_a_scatter_thrown_before_the_decision_is_thrown_again_into_the_decided_view() -> None:
    """Cohort seed 8's case: the marsh threw within a predicted frame whose foot stood 87 px above the decided view's. Each
    scatter that offered a re-throw is thrown into exactly the strips of its parcel the new frame shows past the old, its
    frame becomes the new one, and the registry is closed; a scatter that offered none keeps its frame."""
    s = Settlement(1000, 1000, seed=1)
    s._scatter_frames = [((0.0, 0.0, 500.0, 400.0), (0.0, 0.0, 800.0, 900.0)), ((0.0, 0.0, 500.0, 400.0), (0.0, 0.0, 800.0, 900.0))]
    thrown: list[tuple[float, float, float, float]] = []
    vars(s)["_scatter_catchup"] = {0: thrown.append}
    throw_to_the_view(s, (0.0, 0.0, 600.0, 500.0))
    assert thrown == [(500.0, 0.0, 600.0, 500.0), (0.0, 400.0, 600.0, 500.0)], "the strips past the old frame, inside the new"
    assert s._scatter_frames[0][0] == (0.0, 0.0, 600.0, 500.0) and s._scatter_frames[1][0] == (0.0, 0.0, 500.0, 400.0)
    assert "_scatter_catchup" not in vars(s), "the registry is closed with the stage"
    throw_to_the_view(s, (0.0, 0.0, 600.0, 500.0))  # nothing offered: nothing thrown
    assert len(thrown) == 2


# ---- woods W04: no three woodland parcels in a ruled row, on the point the record carries --------------------------


def _scan(plan, count: int = 6) -> list:  # type: ignore[no-untyped-def]
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["fields"] = []  # no houses and no crop: the open canvas `test_a_third_parcel_with_no_ground_off_the_row...` uses
    plan.belt = []
    plan.title_pocket = None
    return parcels.open_ground_patches(s, plan, count=count)


def test_the_scan_asks_the_row_rule_of_the_point_each_parcel_is_recorded_at(monkeypatch: pytest.MonkeyPatch) -> None:
    """Woods W04, the violating case: every drawn ring's recorded point (`ring_center`) is forced onto one line, so any
    third ring the scan accepts would stand in a ruled row with two before it, whatever its seat. The scan draws two."""
    plan = a_plan()
    free = _scan(plan)
    assert len(free) >= 3, "non-vacuity: the open canvas seats a third parcel"
    assert not any(parcels.in_a_ruled_line(ring_center(free[k]), [ring_center(c) for c in free[:k]]) for k in range(2, len(free)))
    monkeypatch.setattr(parcels, "ring_center", lambda ring: (ring_center(ring)[0], 0.0))
    assert len(_scan(plan)) == 2


def test_a_jittered_seat_in_a_row_is_not_taken(monkeypatch: pytest.MonkeyPatch) -> None:
    """Woods W04: the jitter moves an accepted seat up to half a step, and the moved seat is asked the row rule too - with
    every moved seat in a row, the scan keeps the unmoved seat (the row test it already passed)."""
    plan = a_plan()
    asked: list[tuple[float, float]] = []
    real = parcels.in_a_ruled_line

    def _jitter_in_row(p, centers, frac=0.2):  # type: ignore[no-untyped-def]
        if len(centers) >= 1 and centers and all(len(c) == 3 for c in centers):  # a seat asked against the SEATS placed
            asked.append(p)
        return real(p, centers, frac)

    monkeypatch.setattr(parcels, "in_a_ruled_line", _jitter_in_row)
    assert _scan(plan, count=3) and asked, "the moved seats were asked the row rule"


# ---- woods W14: the drawn ring on the page -------------------------------------------------------------------------


def test_the_ring_inside_share_is_the_rules_measure() -> None:
    ring = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    assert parcels.parcel_inside_share(ring, (0.0, 0.0, 100.0, 100.0)) == 1.0
    assert math.isclose(parcels.parcel_inside_share(ring, (30.0, -50.0, 500.0, 500.0)), 0.7)
    assert parcels.parcel_inside_share(ring, (300.0, 300.0, 500.0, 500.0)) == 0.0


def test_the_scan_refuses_a_ring_mostly_off_the_page_and_takes_the_next_seat(monkeypatch: pytest.MonkeyPatch) -> None:
    """Woods W14 at the placer: the rotated rectangle's box passed, and the ring drawn inside it has a box of its own -
    asked `parcel_inside_share` against the frame; a ring under the floor is not drawn and the scan goes on."""
    plan = a_plan()
    assert _scan(plan, count=2), "non-vacuity"
    asked: list[list] = []

    def _first_off(ring, frame):  # type: ignore[no-untyped-def]
        asked.append(ring)
        return 0.68 if len(asked) == 1 else 1.0

    monkeypatch.setattr(parcels, "parcel_inside_share", _first_off)
    got = _scan(plan, count=2)
    assert asked[0] not in got and got


# ---- water W58: the title pocket clear of the feature glyphs ------------------------------------------------------


def test_a_pocket_beside_a_glyph_is_not_clear() -> None:
    M = {
        "cemeteries": [{"x": 170.0, "y": 50.0, "w": 20.0, "h": 20.0}],
        "wells": [{"x": 500.0, "y": 500.0, "vr": 6.0}, {"y": 1.0}],
        "torii": [[900.0, 900.0, 0]],
    }
    assert not pocket_clear_of_features((0.0, 0.0, 100.0, 100.0), M, 70.0), "the burial ground 60 px off the pocket's side"
    assert pocket_clear_of_features((0.0, 0.0, 100.0, 100.0), M, 40.0)
    assert not pocket_clear_of_features((300.0, 300.0, 460.0, 460.0), M, 40.0), "a wellhead by its drawn radius"
    assert not pocket_clear_of_features((800.0, 800.0, 870.0, 870.0), M, 25.0), "a torii by its glyph"


def test_the_pocket_search_steps_past_a_box_beside_the_burial_ground() -> None:
    """Water W58, the violating case (Kashikawa's burial glyph 23 ft beside the placard): the blank-box scan's first box
    clears every title obstacle and stands 8 px from the burial ground; the pocket search keeps `TITLE_POCKET_CLEAR_FT`
    from it and takes a later box."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    s.M["cemeteries"] = [{"x": 140.0, "y": 72.0, "w": 20.0, "h": 20.0}]
    window = (0.0, 0.0, 1000.0, 1000.0)
    assert s._blank_label_spot(*window, 100.0, 100.0) == (22.0, 22.0), "non-vacuity: the plain scan takes the box by the glyph"
    spot = clear_pocket_spot(s, window, 100.0, 100.0, [], s.px(TITLE_POCKET_CLEAR_FT))
    assert spot is not None and spot != (22.0, 22.0)
    assert pocket_clear_of_features((spot[0], spot[1], spot[0] + 100.0, spot[1] + 100.0), s.M, s.px(TITLE_POCKET_CLEAR_FT))
    assert clear_pocket_spot(s, (0.0, 0.0, 100.0, 100.0), 100.0, 100.0, [], 0.0) is None, "a window with no room"


def test_the_reserved_pocket_keeps_clear_of_the_burial_ground() -> None:
    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["houses"] = [{"x": 700.0, "y": 700.0, "w": 46.0, "h": 28.0}]
    first = hinterland.title_pocket(s, plan)
    t = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    t.M["houses"] = [{"x": 700.0, "y": 700.0, "w": 46.0, "h": 28.0}]
    t.M["cemeteries"] = [{"x": first[2] + 12.0, "y": (first[1] + first[3]) / 2, "w": 20.0, "h": 20.0}]
    plan.title_pocket, plan.title_pocket_outside = None, False
    got = hinterland.title_pocket(t, plan)
    assert got != first and pocket_clear_of_features(got, t.M, t.px(TITLE_POCKET_CLEAR_FT))


# ---- woods W24: no bamboo stand on a lane's tread ------------------------------------------------------------------


def test_a_stand_is_asked_across_its_whole_rect() -> None:
    """Woods W24: every point of the rect lies within `BAMBOO_SAMPLE_FT / sqrt(2)` of a sample - so a lane crossing the
    stand between the old perimeter rows (half a row, 14.5 ft from each) is within its refusal reach of one."""
    hw, hh = 42.0, 29.0
    pts = stand_samples(500.0, 500.0, hw, hh, BAMBOO_SAMPLE_FT)
    worst = max(min(math.dist((x, y), q) for q in pts) for x in range(458, 543, 3) for y in range(471, 530, 3))
    assert worst <= BAMBOO_SAMPLE_FT / math.sqrt(2.0) + 1e-9
    lane = ((0.0, 500.0 - hh / 2), (1000.0, 500.0 - hh / 2))
    assert min(seg_dist(x, y, *lane) for x, y in pts) < 1.5 + 10.0


def test_no_thicket_is_seated_on_a_lane() -> None:
    plan = a_plan()
    s = Settlement(plan.W, plan.H, seed=plan.spec.seed)
    s.meta(name="B", scale="hamlet", ftpx=1, down_deg=90)
    s.M["houses"] = [{"x": 700.0, "y": 300.0, "w": 40.0, "h": 30.0}, {"x": 760.0, "y": 300.0, "w": 40.0, "h": 30.0}, {"x": 820.0, "y": 300.0, "w": 40.0, "h": 30.0}]
    plan.bamboo = "thicket"
    seats = bamboo_seats(s, plan)
    assert seats, "non-vacuity: the thicket seats"
    ring = seats[0]
    cy = sum(q[1] for q in ring) / len(ring)
    s.M["lanes"] = [{"pts": [[0.0, cy], [float(plan.W), cy]], "w": 3}]  # a lane through where it stood
    plan.bamboo_roles = []
    again = bamboo_seats(s, plan)
    assert all(not point_in_poly(x, cy, r) for r in again for x in range(0, int(plan.W), 2)), "no stand stands on the tread"


# ---- woods W18: the belt's band on the wind's side of the houses ---------------------------------------------------


def test_no_column_of_the_band_stands_behind_the_houses_center() -> None:
    """Woods W18 (1): the median house can stand downwind of the houses' centroid - one farmstead far upwind pulls the
    centroid after it - and a column floored at the median laid the band's near face behind the centroid. Floored at the
    centroid, every near-face vertex stands windward of it (less the near face's 5 ft rag)."""
    plan = a_plan()  # the wind from the north
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["houses"] = [{"x": 700.0, "y": 300.0, "w": 40.0, "h": 30.0}] + [{"x": x, "y": 700.0, "w": 40.0, "h": 30.0} for x in (500.0, 600.0, 800.0, 900.0)]
    cy = sum(h["y"] for h in s.M["houses"]) / 5
    belt = hinterland.belt_polygon(s, plan)
    near = belt[: s.M["meta"]["belt_near_vertices"]]
    assert near and min(-(y - cy) for _x, y in near) >= 36.0 - 5.0 - 1e-6


def test_the_scan_refuses_a_ring_with_no_room_for_a_wood(monkeypatch: pytest.MonkeyPatch) -> None:
    """Woods W13 at the scan: a ring whose room (`woodland_room`) is under `WOODLAND_MIN_CROWNS` is not offered; the scan
    takes the next seat."""
    plan = a_plan()
    assert _scan(plan, count=2), "non-vacuity"
    asked: list[list] = []
    real = Settlement.woodland_room

    def _first_bare(self, ring):  # type: ignore[no-untyped-def]
        asked.append(ring)
        return [] if len(asked) == 1 else real(self, ring)

    monkeypatch.setattr(Settlement, "woodland_room", _first_bare)
    got = _scan(plan, count=2)
    assert asked[0] not in got and got


# ---- plan D11: a wood off the sheet is recorded with its bearing ---------------------------------------------------


def test_a_roll_with_no_parcel_on_the_sheet_records_its_wood_beyond_it() -> None:
    from l7r.diagram.hamletgen.hinterland.stages import woodland_offsheet, woodland_on_the_sheet

    plan = a_plan()  # the land falls due south (down 90), so the hill beyond the fields is north
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    assert woodland_on_the_sheet(s, plan, [[(0.0, 0.0)]]) == [[(0.0, 0.0)]] and "woodland_offsheet" not in s.M["meta"]
    assert woodland_on_the_sheet(s, plan, []) == []
    rec = s.M["meta"]["woodland_offsheet"]
    assert rec == woodland_offsheet(plan) and rec["bearing"] == "N" and rec["parcels"] == plan.woodland_patches


# ---- woods W16-W19: the belt planted on the page it will be drawn on, within the band's reach -----------------------


def _cluster_plan():  # type: ignore[no-untyped-def]
    plan = a_plan()  # the wind from the north
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.meta(name="W", scale="hamlet", ftpx=1, down_deg=90, windward="N")
    s.M["houses"] = [{"x": float(x), "y": 900.0, "w": 40.0, "h": 30.0, "rot": 0} for x in range(450, 951, 100)]
    return s, plan


def test_the_band_records_its_reach_and_the_belt_keeps_every_crown_within_it() -> None:
    """Woods W19: `belt_polygon` records the band's far-face reach (its depth along the wind with the column's window across
    it), and every crown the planted belt keeps stands within that reach of a farmhouse."""
    from l7r.diagram.hamletgen.hinterland import belt as beltmod
    from l7r.diagram.hamletgen.hinterland import stages

    s, plan = _cluster_plan()
    plan.belt = hinterland.belt_polygon(s, plan)
    reach = s.M["meta"]["belt_reach"]
    along = beltmod.BELT_NEAR_FT + beltmod.BELT_DEPTH_FT + beltmod.BELT_FAR_RAG_FT
    assert along < reach < along + 200.0, "the far face along the wind, grown by the column's window across it"
    stages.plant_the_belt(s, plan)
    g = next(g for g in s.M["village_groves"] if g["role"] == "windbreak")
    hs = [(h["x"], h["y"]) for h in s.M["houses"]]
    assert g["clumps"] and all(min(math.dist(c, h) for h in hs) <= reach for c in g["clumps"])


def test_the_page_the_planter_judges_is_the_view_the_frame_decides() -> None:
    """M6 for the belt (woods W16-W18): `belt_page` over the crowns the belt keeps answers exactly the view `frame_for`
    decides once the belt stands, so the depth, the holes and the hook are judged on the page the belt is drawn on."""
    from l7r.diagram.hamletgen.hinterland import stages
    from l7r.diagram.hamletgen.hinterland.frame import belt_page, frame_for

    s, plan = _cluster_plan()
    s.M["fields"] = [{"outline": [[400.0, 1000.0], [1000.0, 1000.0], [1000.0, 1400.0], [400.0, 1400.0]]}]
    plan.belt = hinterland.belt_polygon(s, plan)
    page = belt_page(s, plan, 14.0)
    stages.plant_the_belt(s, plan)
    g = next(g for g in s.M["village_groves"] if g["role"] == "windbreak")
    assert g["clumps"] and page([(c[0], c[1]) for c in g["clumps"]]) == frame_for(s, plan)


# ---- homes H01 on the drawn record: a homestead bamboo stand names its house ---------------------------------------


def test_a_drawn_homestead_stand_carries_its_owner() -> None:
    from l7r.diagram.hamletgen.hinterland import stages

    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    plan.bamboo_polys = [[(500.0, 500.0), (560.0, 500.0), (560.0, 540.0), (500.0, 540.0)], [(700.0, 500.0), (760.0, 500.0), (760.0, 540.0), (700.0, 540.0)]]
    plan.bamboo_roles = ["homestead", "thicket"]
    plan.bamboo_of = {0: (530.0, 580.0)}
    stages.stage_bamboo(s, plan)
    assert [r.get("of") for r in s.M["bamboo_stands"]] == [[530.0, 580.0], None]


# ---- woods W25: the homesteads' wood never under the register's floor ------------------------------------------------


def test_a_woods_short_of_the_floor_is_topped_up_among_the_houses() -> None:
    """Woods W25 / plan D9, the violating case: a belt that stands off the sheet and a copse siting whose belt gives it no
    lee face, so the first copse seats nothing. The top-up plants the homesteads' own trees up to the floor, each within
    the dooryard copse's reach of a farmhouse (so woods W02 holds of every clump)."""
    from l7r.diagram.hamletgen.consts import COPSE_HOUSE_REACH_FT
    from l7r.diagram.hamletgen.hinterland import stages
    from l7r.diagram.settlement.homestead_parts.groves import HOMESTEAD_WOOD_FT2

    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.meta(name="W", scale="hamlet", ftpx=1, down_deg=90, windward="N")
    s.M["houses"] = [{"x": float(x), "y": float(y), "w": 30.0, "h": 24.0, "rot": 0} for x in (500, 700, 900) for y in (600, 800)]
    plan.belt = [(2000.0, 100.0), (2100.0, 100.0), (2100.0, 150.0), (2000.0, 150.0)]
    plan.copse_siting = "against_the_belt"
    assert stages.homestead_wood_drawn(s) == 0.0, "non-vacuity: no wood at all before the stage"
    stages.stage_windbreak(s, plan)
    hs = [(h["x"], h["y"]) for h in s.M["houses"]]
    copse = [c for g in s.M["village_groves"] if g["role"] == "copse" for c in g["clumps"]]
    assert copse and all(min(math.dist(c, h) for h in hs) <= COPSE_HOUSE_REACH_FT for c in copse)
    assert stages.homestead_wood_drawn(s) >= HOMESTEAD_WOOD_FT2[0] and s.M["meta"]["homestead_wood_ft2"]["drawn"] >= HOMESTEAD_WOOD_FT2[0]
    assert stages.homestead_wood_drawn(Settlement(W=100, H=100, seed=1)) == 0.0


def test_every_households_reserved_share_is_planted_though_no_belt_stands() -> None:
    """Woods W25 / plan D9: two households (too few for a belt) that reserved their shares of the floor at seating
    (`wood_share`). Without the reservation the stage plants nothing; with it every reserved seat is a copse clump."""
    from l7r.diagram.hamletgen.hinterland import stages

    plan = a_plan()
    plan.belt = []
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.meta(name="W", scale="hamlet", ftpx=1, down_deg=90, windward="N")
    s.M["houses"] = [{"x": 500.0, "y": 800.0, "w": 30.0, "h": 24.0, "rot": 0}, {"x": 800.0, "y": 800.0, "w": 30.0, "h": 24.0, "rot": 0}]
    stages.stage_windbreak(s, plan)
    assert not s.M["village_groves"], "non-vacuity: no belt and no reservation, no wood"
    seats = {0: [[480.0, 750.0], [510.0, 748.0]], 1: [[790.0, 750.0], [820.0, 752.0]]}
    for k, h in enumerate(s.M["houses"]):
        h["wood_share"] = {"seats": seats[k], "r": 11.0, "ft2": 900}
    assert stages.reserved_seats(s) == [(480.0, 750.0), (510.0, 748.0), (790.0, 750.0), (820.0, 752.0)]
    stages.stage_windbreak(s, plan)
    copse = [c for g in s.M["village_groves"] if g["role"] == "copse" for c in g["clumps"]]
    assert all(q in copse for v in seats.values() for q in v)
