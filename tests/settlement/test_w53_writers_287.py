"""Feature 287, water W53 at the settlement engine's writers: every record on a hamlet's path asks the registry of what stands
(the overlap matrix) before it is recorded - a placer with candidates refuses the one the matrix forbids and takes the next,
a writer with one candidate refuses it by name before any of its ink is drawn - and never records it. Each on constructed
input including the violating case."""

from __future__ import annotations

from typing import Any

import pytest

from l7r.diagram.overlap.registry import OverlapRefused, element_extents, pair_permitted, refuse_unadmitted
from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.fields.paddy import rest_record


def _square(x0: float, y0: float, x1: float, y1: float) -> list[list[float]]:
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _hamlet(strict: bool = True) -> Settlement:
    s = Settlement(1000, 1000, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90)
    s.standing.strict = strict
    return s


def _permitted(ka: str, a: dict[str, Any], kb: str, b: dict[str, Any]) -> bool:
    return pair_permitted(element_extents(ka, a, {})[0], element_extents(kb, b, {})[0], set())


def test_a_fields_own_water_may_lie_on_its_own_resting_basin_and_a_strangers_may_not() -> None:
    """Cohort seed 55 raised for a field ditch on a fallow patch at (3058, 2342): the basin is one of the field's own paddy plots
    and its ditches run along its bunds. The matrix allows the field's own ditch and feed there, and nobody else's."""
    basin = rest_record([(0.0, 0.0), (40.0, 0.0), (40.0, 40.0), (0.0, 40.0)], "f")
    assert basin["field"] == "f" and "field" not in rest_record([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)])
    own = {"poly": [[20.0, -10.0], [20.0, 50.0]], "role": "lateral", "field": "f", "w": 1.5}
    assert _permitted("field_ditches", own, "fallow_patches", basin), "its own ditch"
    assert not _permitted("field_ditches", {**own, "field": "g"}, "fallow_patches", basin), "another field's ditch"
    feed = {"poly": [[20.0, -10.0], [20.0, 50.0]], "w": 2.5, "field": "f"}
    assert _permitted("channels", feed, "fallow_patches", basin), "its own feed, along the race"
    assert not _permitted("channels", {"poly": feed["poly"], "w": 2.5}, "fallow_patches", basin), "a drain run naming no field"
    assert not _permitted("field_ditches", own, "dry_plots", {"poly": basin["outline"]}), "a ditch is still refused on dry crop"


def test_the_weir_is_read_turned_as_it_is_drawn() -> None:
    """A weir records its oblique bar's bearing as `deg`: read at rot 0 its box lay square to the sheet."""
    ((_k, quad, _i, _p),) = element_extents("weirs", {"x": 100.0, "y": 100.0, "len": 20.0, "w": 2.0, "deg": 90.0}, {})
    xs, ys = [q[0] for q in quad], [q[1] for q in quad]
    assert max(xs) - min(xs) == pytest.approx(2.0) and max(ys) - min(ys) == pytest.approx(20.0), "the bar runs down the sheet"


def test_a_writer_with_one_candidate_is_refused_by_name_and_records_nothing() -> None:
    s = _hamlet()
    s.M["dry_plots"].append({"poly": _square(400.0, 400.0, 600.0, 600.0)})
    refuse_unadmitted({}, "streams", {"poly": [[0.0, 0.0], [1.0, 1.0]]})  # a bare manifest carries no registry: nothing to ask
    refuse_unadmitted(s.M, "streams", {"poly": [[0.0, 100.0], [900.0, 100.0]], "w": 7})
    with pytest.raises(OverlapRefused):
        refuse_unadmitted(s.M, "streams", {"poly": [[0.0, 500.0], [900.0, 500.0]], "w": 7})
    loose = _hamlet(strict=False)  # the town and city tiers' registries record as they always did
    loose.M["dry_plots"].append({"poly": _square(400.0, 400.0, 600.0, 600.0)})
    refuse_unadmitted(loose.M, "streams", {"poly": [[0.0, 500.0], [900.0, 500.0]], "w": 7})


def test_a_stream_a_pond_and_a_sluice_the_matrix_forbids_are_refused_before_any_ink() -> None:
    s = _hamlet()
    s.M["dry_plots"].append({"poly": _square(400.0, 400.0, 600.0, 600.0)})
    s.M["houses"].append({"x": 100.0, "y": 100.0, "w": 20.0, "h": 20.0, "rot": 0.0})
    drawn = (len(s.out), len(s.water), len(s.late_water))
    with pytest.raises(OverlapRefused):
        s.stream([(0.0, 500.0), (900.0, 500.0)], width=7)
    with pytest.raises(OverlapRefused):
        s.pond(500.0, 500.0, 60.0, 40.0)
    with pytest.raises(OverlapRefused):
        s.sluice_gate(100.0, 100.0)
    assert (len(s.out), len(s.water), len(s.late_water)) == drawn, "nothing of any of them drawn"
    assert not s.M["streams"] and not s.M.get("pond") and not s.M.get("sluice_gates")
    s.stream([(0.0, 200.0), (900.0, 200.0)], width=7)
    s.pond(800.0, 800.0, 60.0, 40.0)
    s.sluice_gate(300.0, 200.0)
    assert len(s.M["streams"]) == 1 and s.M["pond"] == [800.0, 800.0, 60.0, 40.0] and len(s.M["sluice_gates"]) == 1


def test_a_brook_is_rounded_only_onto_ground_the_registry_admits_and_is_recorded_as_rounded() -> None:
    """`round_stream` reshaped a brook in place and left the index on the course as first drawn until the stage's end, where
    the backstop re-recorded it unasked (9 of 25 census brooks). It asks first, and records what it wrote."""
    s = _hamlet()
    s.stream([(0.0, 500.0), (500.0, 500.0), (500.0, 1000.0)], width=7)
    rec = s.M["streams"][0]
    s.M["dry_plots"].append({"poly": _square(520.0, 440.0, 560.0, 480.0)})
    with pytest.raises(OverlapRefused):
        s.round_stream(rec, [(0.0, 500.0), (540.0, 460.0), (500.0, 1000.0)])
    assert rec["poly"] == [[0.0, 500.0], [500.0, 500.0], [500.0, 1000.0]] and "stations" not in rec, "nothing of the refused course written"
    corner = {"poly": _square(496.0, 496.0, 504.0, 504.0)}
    assert not s.admits("dry_plots", corner)
    s.round_stream(rec, [(0.0, 500.0), (480.0, 520.0), (500.0, 1000.0)])
    assert rec["poly"][1] == [480.0, 520.0] and s.admits("dry_plots", corner), "the registry holds the rounded course"
    stray = {"poly": [[0.0, 0.0], [10.0, 0.0], [20.0, 0.0]], "w": 7}  # a record on no manifest list is not recorded by its rounding
    s.round_stream(stray, [(0.0, 0.0), (10.0, 1.0), (20.0, 0.0)])
    assert s.admits("dry_plots", {"poly": _square(5.0, -5.0, 15.0, 5.0)}), "the stray is not on the map"


def _net(channels: list[dict[str, Any]], dry: list[list[tuple[float, float]]]) -> dict[str, Any]:
    plots = [{"poly": p, "fill": "#C8B070", "furrow": "#A08850", "theta": 0.0, "crop": "barley"} for p in dry]
    return {"channels": channels, "dry_plots": plots, "plots": []}


def test_the_ditch_net_is_the_skeleton_and_a_hem_plot_one_of_its_ditches_crosses_is_refused() -> None:
    """The ditch net is recorded before the hem; a hem plot one of the field's own ditches crosses is not drawn, and a ditch
    the matrix forbids on what stood before the field is refused by name, never recorded."""
    s = _hamlet()
    ditch = {"pts": [(200.0, 0.0), (200.0, 400.0)], "role": "lateral", "w": 1.5}
    across = [(180.0, 100.0), (220.0, 100.0), (220.0, 140.0), (180.0, 140.0)]
    clear = [(300.0, 100.0), (340.0, 100.0), (340.0, 140.0), (300.0, 140.0)]
    net = _net([ditch], [across, clear])
    s._comb_record_ditches(net, "f")
    s._comb_draw_hem(net, None, "f")
    assert [p["poly"][0] for p in s.M["dry_plots"]] == [[300.0, 100.0]], "the plot across the ditch is refused, the clear one drawn"
    t = _hamlet()
    t.M["dry_plots"].append({"poly": _square(180.0, 100.0, 220.0, 140.0)})
    with pytest.raises(OverlapRefused):
        t._comb_record_ditches(_net([ditch], []), "f")
    assert not t.M["field_ditches"]


def test_only_a_basin_the_registry_admits_rests() -> None:
    """A resting basin is recorded as ground, so a basin a stranger's water already crosses is not offered to the rest pick: it
    stays a rice plot. With every candidate refused but one, only that one can rest."""
    s = _hamlet()
    s.pin_knob("paddy_rest", "unsettled")
    cands = [([(x, 100.0), (x + 60.0, 100.0), (x + 60.0, 160.0), (x, 160.0)], float(x)) for x in (0.0, 200.0, 400.0, 600.0, 800.0)]
    s.stream([(0.0, 130.0), (700.0, 130.0)], width=7)  # across the first four
    assert s.resting_plots("f", cands) <= {4}
    free = _hamlet()
    free.pin_knob("paddy_rest", "unsettled")
    assert len(free.resting_plots("f", cands)) >= 2, "with nothing across them, the pick is unconstrained"
    s.rest_basin(cands[4][0], 1.0, "f")
    assert s.M["fallow_patches"][-1]["field"] == "f"


def test_a_notice_board_seat_on_ground_the_matrix_forbids_is_not_offered() -> None:
    """The board's seat asks the registry as `kosatsuba` records it, turned: every verge but one window lies on a dry crop,
    so the board stands in the window - and with the window closed there is no seat, and no board on the crop."""

    def scene(window: bool) -> Settlement:
        s = _hamlet()
        s.M["dry_plots"].append({"poly": _square(0.0, 0.0, 1000.0, 497.0)})
        s.M["dry_plots"].append({"poly": _square(0.0, 503.0, 700.0 if window else 1000.0, 1000.0)})
        if window:
            s.M["dry_plots"].append({"poly": _square(760.0, 503.0, 1000.0, 1000.0)})
        s.M["lanes"] = [{"pts": [[100.0, 500.0], [900.0, 500.0]], "w": 4}]
        return s

    s = scene(True)
    assert s.place_kosatsuba(label="") is not None
    b = s.M["kosatsuba"][0]
    assert 700.0 < b["x"] < 760.0 and b["y"] > 500.0 and s.admits("kosatsuba", s.board_record(b["x"], b["y"], b["rot"]), ignore=b)
    shut = scene(False)
    assert shut.place_kosatsuba(label="") is None and not shut.M["kosatsuba"]


def test_the_board_record_is_what_the_board_writes() -> None:
    s = _hamlet()
    s.kosatsuba(300.0, 300.0, 30.0, label="")
    rec = s.M["kosatsuba"][0]
    assert {k: rec[k] for k in ("x", "y", "w", "h", "vw", "vh", "rot")} == s.board_record(300.0, 300.0, 30.0)
