"""A clustered hamlet's communal wells by the lane or among the houses (feature 374 wave 154, 0196): the rolled siting, the
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
    plan = types.SimpleNamespace(ftpx=1.0)
    s = _s([{"x": 1.0, "y": 1.0, "form": "pocket"}], HOUSES)
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
