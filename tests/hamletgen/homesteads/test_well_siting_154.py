"""A clustered hamlet's communal wells by the lane or among the houses (feature 374 waves 154 and 155, 0196): the rolled siting, the
order the forms are tried in once the lanes stand, the three-then-two only where five cannot be gathered, the verge test,
and the wells serving more than ten recorded."""

from __future__ import annotations

import types

import pytest

from l7r.diagram.hamletgen.homesteads import wells as wl
from l7r.diagram.hamletgen.plan import HamletSpec


def _s(wells: list[dict], houses: list[dict], lanes: list[dict] | None = None) -> types.SimpleNamespace:
    return types.SimpleNamespace(M={"meta": {}, "wells": wells, "houses": houses, "lanes": lanes or []}, _well_vr=lambda: 12.0, px=lambda v: v)


HOUSES = [{"x": float(10 * i), "y": 0.0} for i in range(12)]


def test_the_spec_takes_the_two_sitings_and_refuses_another() -> None:
    assert HamletSpec(name="T", seed=1, well_siting="lane").well_siting == "lane"
    with pytest.raises(ValueError, match="well_siting"):
        HamletSpec(name="T", seed=1, well_siting="pond")


def test_the_lanes_stage_tries_the_lane_form_then_the_cluster_form_then_records_a_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def seat(s, plan, houses, placed, want, rungs, form, gap=0.0, seat_ok=None, candidates=None, step=22.0):  # noqa: ANN001, ANN202
        calls.append(form)
        if form == "fallback":
            placed.append((0.0, 0.0))
            return [(0.0, 0.0)]
        return []

    monkeypatch.setattr(wl, "seat_wells", seat)
    monkeypatch.setattr(wl, "reach_wells", lambda s, plan: None)  # its own test below
    plan = types.SimpleNamespace(ftpx=1.0)
    s = _s([{"x": 1.0, "y": 1.0, "form": "cluster"}], HOUSES)
    s._wells_owed = (2, ())
    wl.stage_lane_wells(s, plan)  # type: ignore[arg-type]
    assert calls == ["lane", "cluster", "fallback"] and s.M["meta"]["well_fallback"] == 1
    calls.clear()
    s2 = _s([], HOUSES)
    s2._wells_owed = (1, ("cluster",))
    wl.stage_lane_wells(s2, plan)  # type: ignore[arg-type]
    assert calls == ["lane", "fallback"], "a cluster roll is not tried as the cluster form twice"
    calls.clear()
    wl.stage_lane_wells(_s([], HOUSES), plan)  # type: ignore[arg-type]
    assert calls == [], "nothing owed"
    s3 = _s([{"x": 1.0, "y": 1.0}, {"x": 2.0, "y": 1.0}], HOUSES)
    s3._wells_owed = (2, ())
    wl.stage_lane_wells(s3, plan)  # type: ignore[arg-type]
    assert calls == [], "every well owed already stands"


def test_three_then_two_only_where_five_cannot_be_gathered(monkeypatch: pytest.MonkeyPatch) -> None:
    rungs: list[int] = []
    oks: list = []
    monkeypatch.setattr(wl, "seat_wells", lambda s, plan, houses, placed, want, r, form, **k: rungs.append(r[0][1]) or oks.append(k["seat_ok"]) or [])
    plan = types.SimpleNamespace(ftpx=1.0)
    wl.seat_cluster(_s([], HOUSES), plan, HOUSES, [], 1)  # type: ignore[arg-type]
    assert rungs == [5], "twelve households: five or nothing in the form"
    rungs.clear()
    wl.seat_cluster(_s([], HOUSES), plan, HOUSES[:4], [], 1)  # type: ignore[arg-type]
    assert rungs == [5, 3], "four households: five cannot be gathered"
    lanes = _s([], HOUSES, lanes=[{"pts": [[0, 0], [100, 0]], "w": 4.0}])
    rungs.clear(), oks.clear()
    wl.seat_cluster(lanes, plan, HOUSES, [], 1)  # type: ignore[arg-type]
    assert not oks[0](50.0, 10.0) and oks[0](50.0, 60.0), "off every lane, its verge included"


def test_a_well_serving_more_than_ten_is_recorded() -> None:
    s = _s([{"x": 0.0, "y": 0.0}, {"x": 1000.0, "y": 0.0}], HOUSES + [{"x": 999.0, "y": 0.0}])
    wl.record_over_ten(s)  # type: ignore[arg-type]
    assert s.M["meta"]["wells_over_ten"] == [12]
    ok = _s([{"x": 0.0, "y": 0.0}], HOUSES[:5])
    wl.record_over_ten(ok)  # type: ignore[arg-type]
    assert "wells_over_ten" not in ok.M["meta"]
    wl.record_over_ten(_s([], HOUSES))  # type: ignore[arg-type]


def test_the_verge_test_and_the_count_a_dig_leaves_and_the_form_recorded() -> None:
    s = _s([{"x": 5.0, "y": 5.0}], HOUSES, lanes=[{"pts": [[0, 0], [100, 0]], "w": 4.0}, {"pts": [[0, 0]]}])
    ok = wl.on_a_verge(s)  # type: ignore[arg-type]
    assert ok(50.0, 2.0 + 12.0 + 8.0) and not ok(50.0, 2.0 + 12.0 + 9.0)
    assert wl.most_served_after((0.0, 1000.0, 0.0), HOUSES, [(0.0, 0.0)]) == 12 and wl.most_served_after((0.0, 115.0, 0.0), HOUSES, [(0.0, 0.0)]) == 6
    assert wl.grid_points(0.0, 10.0, 0.0, 0.0, 5.0) == [(0.0, 0.0), (5.0, 0.0), (10.0, 0.0)]
    wl.mark_form(s, 5.0, 5.0, "lane")
    wl.mark_form(s, 50.0, 50.0, "cluster")
    assert s.M["wells"][0]["form"] == "lane"


def test_the_water_reach_is_held_by_the_wells_once_the_forms_have_seated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 374 wave 155 (row 787): no household carries a well pocket, so the reach the first household's pocket held
    by construction is held here - while a household is beyond 760 ft of every well and of open water, one more shared well
    is seated, the rolled form first; the extra wells are counted, and a household no seat can water is recorded."""
    far = [{"x": 0.0, "y": 0.0}, {"x": 2000.0, "y": 0.0}]
    forms: list[str] = []

    def seat(s, plan, houses, placed, want, rungs, form, gap=0.0, seat_ok=None, candidates=None, step=22.0):  # noqa: ANN001, ANN202
        forms.append(form)
        if form != "lane":
            s.M["wells"].append({"x": 1990.0, "y": 0.0})
            placed.append((1990.0, 0.0))
            return [(1990.0, 0.0)]
        return []

    monkeypatch.setattr(wl, "seat_wells", seat)
    monkeypatch.setattr(wl, "surface_water_dist", lambda M, x, y: 1e9)
    s = _s([{"x": 0.0, "y": 0.0}], far)
    assert wl.dry_households(s, far) == [far[1]]  # type: ignore[arg-type]
    wl.reach_wells(s, types.SimpleNamespace(well_siting="lane", ftpx=1.0))  # type: ignore[arg-type]
    assert forms == ["lane", "cluster"] and s.M["meta"] == {"wells_for_reach": 1}, "the rolled form, then the other"
    forms.clear()
    watered = _s([{"x": 0.0, "y": 0.0}, {"x": 2000.0, "y": 0.0}], far)
    wl.reach_wells(watered, types.SimpleNamespace(well_siting="cluster", ftpx=1.0))  # type: ignore[arg-type]
    assert forms == [] and watered.M["meta"] == {}, "every household within reach: nothing seated"
    monkeypatch.setattr(wl, "seat_wells", lambda *a, **k: [])
    dry = _s([{"x": 0.0, "y": 0.0}], far)
    wl.reach_wells(dry, types.SimpleNamespace(well_siting="cluster", ftpx=1.0))  # type: ignore[arg-type]
    assert dry.M["meta"] == {"dry_households": 1}, "no seat at all: the dry household recorded, never silent"


def test_a_fallback_reach_well_is_counted() -> None:
    """The reach well past both forms is the recorded fallback (`meta.well_fallback`), as wave 154's is."""
    far = [{"x": 0.0, "y": 0.0}, {"x": 2000.0, "y": 0.0}]
    s = _s([{"x": 0.0, "y": 0.0}], far)
    calls: list[str] = []

    def seat(s_, plan, houses, placed, want, rungs, form, **k):  # noqa: ANN001, ANN202
        calls.append(form)
        if form == "fallback":
            s_.M["wells"].append({"x": 1990.0, "y": 0.0})
            placed.append((1990.0, 0.0))
            return [(1990.0, 0.0)]
        return []

    mp = pytest.MonkeyPatch()
    try:
        mp.setattr(wl, "seat_wells", seat)
        mp.setattr(wl, "surface_water_dist", lambda M, x, y: 1e9)
        wl.reach_wells(s, types.SimpleNamespace(well_siting="cluster", ftpx=1.0))  # type: ignore[arg-type]
    finally:
        mp.undo()
    assert calls == ["cluster", "cluster", "lane", "fallback"], "five, then three-then-two (two households), the lane, the fallback"
    assert s.M["meta"] == {"wells_for_reach": 1, "well_fallback": 1}


def test_the_first_of_two_wells_stands_at_its_shares_middle() -> None:
    """Feature 374 wave 155: the first of several wells is seated at the middle of its own share of the houses, cut along
    the cluster's long axis, so the second takes the other share and neither serves more than ten."""
    row = [{"x": float(10 * i), "y": 0.0} for i in range(16)]  # a row along x: the long axis
    assert wl.first_share_middle(row, 2) == (35.0, 0.0), "the eight at one end"
    col = [{"x": 0.0, "y": float(10 * i)} for i in range(4)]
    assert wl.first_share_middle(col, 2) == (0.0, 5.0), "a column: the long axis is y"
    assert wl.first_share_middle(row, 1) == (75.0, 0.0), "one well: all of them"


def test_the_first_well_looks_one_well_ahead() -> None:
    """Feature 374 wave 155: a first seat is ranked by whether some second seat 170 px off would keep both wells at ten or
    fewer - here sixteen houses in two groups of eight 400 px apart: a seat in one group leaves the other group's seat, eight
    a well; a seat with no second seat 170 px off it keeps nothing."""
    houses = [{"x": float(10 * i), "y": 0.0} for i in range(8)] + [{"x": 400.0 + 10 * i, "y": 0.0} for i in range(8)]
    seats = [(0.0, 35.0, 0.0), (0.0, 435.0, 0.0), (0.0, 235.0, 0.0)]
    assert wl.pair_keeps_ten(seats[0], seats, houses), "one group's middle: the other group's seat keeps both at eight"
    assert not wl.pair_keeps_ten(seats[2], seats[2:], houses), "no second seat 170 px off: nothing keeps ten"


def test_one_more_well_where_one_serves_more_than_ten(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 374 wave 155 (W155-6): while a well is nearest to more than ten households, one more shared well is seated
    and counted (`meta.wells_for_ten`); a well that leaves the busiest count where it was ends the search."""
    houses = [{"x": float(10 * i), "y": 0.0} for i in range(12)]
    monkeypatch.setattr(wl, "surface_water_dist", lambda M, x, y: 0.0)  # every household watered: only the ceiling asks

    def seat(s, plan, houses_, placed, want, rungs, form, **k):  # noqa: ANN001, ANN202
        s.M["wells"].append({"x": 110.0, "y": 0.0})
        placed.append((110.0, 0.0))
        return [(110.0, 0.0)]

    monkeypatch.setattr(wl, "seat_wells", seat)
    s = _s([{"x": 0.0, "y": 0.0}], houses)
    wl.reach_wells(s, types.SimpleNamespace(well_siting="cluster", ftpx=1.0))  # type: ignore[arg-type]
    assert s.M["meta"] == {"wells_for_ten": 1} and len(s.M["wells"]) == 2, "twelve at one well: a second, counted for the ten"
    stuck = _s([{"x": 0.0, "y": 0.0}], houses)
    monkeypatch.setattr(wl, "seat_wells", lambda s_, plan, h, placed, *a, **k: s_.M["wells"].append({"x": 500.0, "y": 0.0}) or placed.append((500.0, 0.0)) or [(500.0, 0.0)])
    wl.reach_wells(stuck, types.SimpleNamespace(well_siting="cluster", ftpx=1.0))  # type: ignore[arg-type]
    assert len(stuck.M["wells"]) == 2, "a well that served none of the twelve: not tried again"


def test_seat_wells_seats_none_with_no_houses_or_its_count_met() -> None:
    """Feature 385 T05: the pocket path that once reached `seat_wells` with nothing to seat is gone, so its early return is held here."""
    plan = types.SimpleNamespace(ftpx=1.0)
    assert wl.seat_wells(_s([], HOUSES), plan, [], [], 1, [(95.0, 5)], "cluster") == []  # type: ignore[arg-type]
    assert wl.seat_wells(_s([], HOUSES), plan, HOUSES, [(0.0, 0.0)], 1, [(95.0, 5)], "cluster") == []  # type: ignore[arg-type]
