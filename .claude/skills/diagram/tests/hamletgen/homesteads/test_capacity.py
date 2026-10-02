"""Feature 287, homes H03 and H14 and plan D2: every declared household seated where the seats are chosen, or the site
refused - the exhaustive pass, the margin ladder, the polder's flank, the refusal."""

from __future__ import annotations

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.homesteads import capacity, stages
from l7r.diagram.hamletgen.homesteads.capacity import SiteRefused, compass, free_seats, margin_ladder, seat_the_rest, seating_mark, unseat_to
from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling.fit import FIELD_REACH_FT, within_field_reach
from tests.hamletgen._builders import CROWN, a_plan


def _toy(households: int) -> tuple[Settlement, hg.SitePlan]:
    plan = a_plan(households=households)
    plan.envelope = list(CROWN)  # three wind-facing margins: a ladder to climb (the square has one)
    plan.seat = hg.seat_cluster(plan)
    plan.settlement_form = "nucleated"
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=households, down_deg=90, water_flow=90, nucleated=True)
    s._nucleated = True
    s.field_polys.append(list(plan.envelope))
    return s, plan


def test_the_field_reach_is_the_records_tolerance_and_holds_only_where_a_boundary_stands() -> None:
    """H03: a house further than 700 ft from its field's chords is refused; nothing is held with no chains installed."""
    s, plan = _toy(10)
    assert within_field_reach(s, 5000.0, 5000.0), "no boundary installed: nothing is held"
    hg.homesteads.boundary.install_site_boundary(s, plan)
    ax, ay = plan.seat["anchor"]
    ox, oy = plan.seat["out"]
    assert FIELD_REACH_FT == 700.0
    assert within_field_reach(s, ax + ox * 650.0, ay + oy * 650.0)
    assert not within_field_reach(s, ax + ox * 760.0, ay + oy * 760.0)


def test_the_placer_refuses_a_seat_beyond_the_fields_reach() -> None:
    """H03 at the placer: `_parts_fit` refuses a homestead 760 px out and admits the same one 150 px out."""
    s, plan = _toy(10)
    hg.homesteads.boundary.install_site_boundary(s, plan)
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}
    ax, ay = plan.seat["anchor"]
    ox, oy = plan.seat["out"]
    far = s._bundle_geom(ax + ox * 760.0, ay + oy * 760.0, 46.0, 28.0, "SE")
    near = s._bundle_geom(ax + ox * 150.0, ay + oy * 150.0, 46.0, 28.0, "SE")
    assert not s._parts_fit(far)
    assert s._parts_fit(near)


def test_free_seats_are_the_free_ground_within_reach_nearest_the_seat_first() -> None:
    """H14's grid: no seat in a cell the static ground surely refuses, none beyond the reach, none on a standing house;
    ordered center-out."""
    s, plan = _toy(10)
    hg.homesteads.boundary.install_site_boundary(s, plan)
    center = (float(plan.seat["cx"]), float(plan.seat["cy"]))
    s.M["houses"].append({"x": center[0], "y": center[1], "w": 46.0, "h": 28.0, "kind": "plain"})
    seats = free_seats(s, center)
    assert seats, "the toy's margin has free ground"
    assert all(within_field_reach(s, x, y) and not s._free_ground.point_taken(x, y) for x, y in seats)
    assert all(math.dist(q, center) >= 50.0 for q in seats), "no seat on the standing house"
    d = [math.dist(q, center) for q in seats]
    assert d == sorted(d)


def test_free_seats_scan_the_whole_canvas_where_no_chains_stand() -> None:
    s, _plan = _toy(10)
    s.W = s.H = 200
    assert len(free_seats(s, (100.0, 100.0), step=0.5)) == 16  # a 50 px grid over 6..194


def test_the_exhaustive_pass_seats_what_the_rounds_left_and_counts_it() -> None:
    """H14 (a): the rounds seated nobody (the patched stage), and the pass over the free ground seats the quota."""
    s, plan = _toy(10)
    hg.homesteads.boundary.install_site_boundary(s, plan)
    s.sun_corridor(39.0)
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}
    stages.face_the_houses(s, plan)
    assert seat_the_rest(s, plan, 10) == 10, "a met quota is left alone"
    assert "exhaustive_took" not in s._seat_search
    assert seat_the_rest(s, plan, 0) == 10
    assert s._seat_search["exhaustive_took"] == 10 == len(s.M["houses"])


def test_the_pass_skips_a_seat_a_house_it_seated_now_stands_on(monkeypatch: pytest.MonkeyPatch) -> None:
    """A grid point within half a pitch of a house the pass itself just seated is not offered again."""
    s, plan = _toy(10)
    hg.homesteads.boundary.install_site_boundary(s, plan)
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}
    monkeypatch.setattr(capacity, "free_seats", lambda s_, c: [(700.0, 300.0), (710.0, 300.0)])

    def place(x: float, y: float, kind: str) -> bool:
        s.M["houses"].append({"x": x, "y": y, "w": 46.0, "h": 28.0, "kind": kind})
        return True

    monkeypatch.setattr(s, "try_place", place)
    assert seat_the_rest(s, plan, 0) == 1 and (s._seat_search["exhaustive_offered"], s._seat_search["exhaustive_took"]) == (1, 1)


def test_seat_cluster_returns_its_ranking_as_the_ladder() -> None:
    """D2: the chosen seat heads the ranking; the other margins follow, best first, each a full seat frame."""
    plan = a_plan(households=10)
    plan.envelope = list(CROWN)
    seat = hg.seat_cluster(plan)
    assert seat["ladder"], "the crowned field has more than one wind-facing margin"
    for rung in seat["ladder"]:
        assert set(rung) == {"cx", "cy", "along", "out", "lat", "dep", "anchor", "offwind"}
    assert (seat["cx"], seat["cy"]) not in [(r["cx"], r["cy"]) for r in seat["ladder"]]


def test_the_ladder_on_a_polder_keeps_to_the_flank_its_fringe_was_drawn_for() -> None:
    """A polder's waterward fringe is drawn for every flank but the village's, so a re-seat stays on that flank."""
    plan = a_plan(households=10)
    plan.seat = {"out": (0.0, -1.0), "ladder": [{"out": (0.1, -1.0)}, {"out": (1.0, 0.0)}, {"out": (-0.2, -0.9)}]}
    assert margin_ladder(plan, polder=False) == plan.seat["ladder"]
    assert margin_ladder(plan, polder=True) == [{"out": (0.1, -1.0)}, {"out": (-0.2, -0.9)}]
    assert [compass(v) for v in ((1, 0), (-1, 0), (0, 1), (0, -1))] == ["E", "W", "S", "N"]


def test_a_margin_left_takes_back_every_house_it_seated() -> None:
    s, _plan = _toy(10)
    s.M["houses"].append({"x": 1.0, "y": 1.0})
    s.placed.append((1.0, 1.0, 2.0, 2.0))
    mark = seating_mark(s)
    s.M["houses"].append({"x": 2.0, "y": 2.0})
    s.placed.append((2.0, 2.0, 2.0, 2.0))
    s._pending_farmsteads.append({})
    s.M.setdefault("row_holdings", []).append({"id": 0})  # a far-row farm's holding, recorded and blocked (feature 291)
    s.block_polys.append([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)])
    s.hard_polys.append([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)])
    unseat_to(s, mark)
    assert (len(s.M["houses"]), len(s.placed), len(s._pending_farmsteads)) == (1, 1, 0)
    assert (len(s.M["row_holdings"]), len(s.block_polys), len(s.hard_polys)) == (0, mark[4], mark[5]), "the holdings go with their farms"


def test_a_margin_that_cannot_seat_everyone_hands_the_hamlet_to_the_next(monkeypatch: pytest.MonkeyPatch) -> None:
    """D2's ladder: the chosen margin seats 7 of 10, the next seats all 10 - that seating is kept, one pass each, and the
    rung that seated the hamlet is recorded."""
    s, plan = _toy(10)
    rung = dict(plan.seat["ladder"][0])
    calls: list[tuple[float, float]] = []

    def seat_on(s_: Settlement, plan_: hg.SitePlan) -> tuple[int, int]:
        calls.append((plan_.seat["cx"], plan_.seat["cy"]))
        n = 7 if len(calls) == 1 else 10
        for k in range(n):
            s_.M["houses"].append({"x": float(k), "y": 0.0, "kind": "plain"})
        return n, 0

    monkeypatch.setattr(stages, "_seat_households", seat_on)
    assert stages.seat_every_household(s, plan) == (10, 0)
    assert calls[1] == (rung["cx"], rung["cy"]) and len(s.M["houses"]) == 10
    assert s.M["meta"]["seat_margin"] == 2 and s.field_face == (float(rung["cx"]), float(rung["cy"]))


def test_a_rung_with_no_dry_exit_is_passed_over(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287, ways W23: a ladder rung whose seat has no dry way out of the frame is not seated - the next one is."""
    s, plan = _toy(10)
    assert len(plan.seat["ladder"]) >= 2
    walled, rung = dict(plan.seat["ladder"][0]), dict(plan.seat["ladder"][1])
    calls: list[tuple[float, float]] = []

    def seat_on(s_: Settlement, plan_: hg.SitePlan) -> tuple[int, int]:
        calls.append((plan_.seat["cx"], plan_.seat["cy"]))
        return (7, 0) if len(calls) == 1 else (10, 0)

    monkeypatch.setattr(stages, "_seat_households", seat_on)
    monkeypatch.setattr(stages, "seat_has_dry_exit", lambda plan_, q, toe, wet: q != (walled["cx"], walled["cy"]))
    assert stages.seat_every_household(s, plan) == (10, 0)
    assert calls[1] == (rung["cx"], rung["cy"]) and (walled["cx"], walled["cy"]) not in calls


def test_a_site_no_margin_can_seat_is_refused_naming_it(monkeypatch: pytest.MonkeyPatch) -> None:
    s, plan = _toy(10)
    plan.seat["ladder"] = plan.seat["ladder"][:1]
    monkeypatch.setattr(stages, "_seat_households", lambda s_, p_: (6, 0))
    with pytest.raises(SiteRefused, match=r"Test \(seed 3\): no margin seats all 10 households - seated \[6, 6\]"):
        stages.seat_every_household(s, plan)


def test_a_seating_drawn_past_every_shapes_band_is_taken_back_and_the_next_margin_seated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287, homes wave 5: a margin that seats every household in a string past 12:1 (`in_a_shapes_band`: no band
    holds it; `declare_cluster_shape` could only name the nearest) is taken back as a short one is; the next margin's
    round cluster is kept - and a site whose every margin draws a string is refused, naming it."""
    s, plan = _toy(10)
    calls: list[int] = []

    def seat_on(s_: Settlement, plan_: hg.SitePlan) -> tuple[int, int]:
        calls.append(1)
        string = len(calls) == 1 or len(plan_.seat["ladder"]) == 1
        for k in range(10):
            s_.M["houses"].append({"x": 200.0 * k, "y": 1.0 * (k % 2), "kind": "plain"} if string else {"x": 40.0 * (k % 4), "y": 40.0 * (k // 4), "kind": "plain"})
        return 10, 0

    monkeypatch.setattr(stages, "_seat_households", seat_on)
    # a straight row reads one homestead deep, never zero (the GM, 2026-10-01, tripwire seed 33): 1,800 ft by 100 ft is 18:1
    assert not stages.in_a_shapes_band([{"x": 200.0 * k, "y": 1.0 * (k % 2)} for k in range(10)])
    assert stages.in_a_shapes_band([{"x": 40.0 * k, "y": 1.0 * (k % 2)} for k in range(10)]), "360 ft of row, one homestead deep: 3.6:1"
    assert stages.in_a_shapes_band([{"x": 1.0 * k, "y": 0.0} for k in range(10)]), "smaller than one homestead each way: 1:1, round"
    assert stages.in_a_shapes_band([{"x": 40.0 * k, "y": 40.0 * (k % 2)} for k in range(10)]), "a string inside 12:1"
    assert stages.seat_every_household(s, plan) == (10, 0) and len(calls) == 2 and s.M["meta"]["seat_margin"] == 2
    assert stages.in_a_shapes_band(s.M["houses"]) and len(s.M["houses"]) == 10
    t, plan_t = _toy(10)
    plan_t.seat["ladder"] = plan_t.seat["ladder"][:1]
    with pytest.raises(SiteRefused, match="inside a cluster shape's band"):
        stages.seat_every_household(t, plan_t)


def test_a_row_village_is_a_row_not_a_cluster_and_takes_no_cluster_band(monkeypatch: pytest.MonkeyPatch) -> None:
    """The GM, 2026-10-01 (tripwire seed 33): a row village's farms stand one frontage apart along their street - 54 to
    240 ft on the measured planned rows (research/questions/0033-row-villages-resson.html) - so ten farms run 490 to 2,160
    ft, 5:1 to 22:1 against one homestead's depth. The 12:1 ceiling is a CLUSTER's; the linear form's row is held by
    `row_rules`, and its seating is kept however long it runs."""
    s, plan = _toy(10)
    plan.settlement_form = "linear"
    plan.seat["ladder"] = plan.seat["ladder"][:1]
    monkeypatch.setattr(stages, "_seat_households", lambda s_, p_: (s_.M["houses"].extend({"x": 260.0 * k, "y": 0.0, "kind": "plain"} for k in range(10)), (10, 0))[1])
    assert not stages.in_a_shapes_band([{"x": 260.0 * k, "y": 0.0} for k in range(10)]), "past every cluster's band"
    assert stages.seat_every_household(s, plan) == (10, 0) and s.M["meta"]["seat_margin"] == 1


def test_the_chosen_margin_that_seats_everyone_is_kept_without_the_ladder(monkeypatch: pytest.MonkeyPatch) -> None:
    s, plan = _toy(10)
    monkeypatch.setattr(stages, "_seat_households", lambda s_, p_: (10, 3))
    assert stages.seat_every_household(s, plan) == (10, 3) and s.M["meta"]["seat_margin"] == 1


def test_the_declaration_is_the_drawing_and_the_knob_narrows_to_it() -> None:
    """Feature 287, homes H04 and H05 (plan D4): the rolled shape stands wherever the houses draw it; otherwise the knob is
    resolved over the shapes the drawing admits, from the seed - a string drawn for a rolled round is declared a string
    shape, a 1.97 cluster on a rolled crescent is round (round's ceiling), and no `cluster_shape_unhonored` is written."""
    string = [{"x": k * 100.0, "y": (k % 2) * 20.0} for k in range(6)]  # 500 by 20: 25:1, past every band
    assert stages.shapes_drawn_at(25.0) == ["elongated"] and stages.shapes_drawn_at(3.0) == ["crescent", "elongated", "split"]
    got = stages.declare_cluster_shape(string, "round", 3)
    assert got["cluster_shape"] == "elongated" and "cluster_shape_unhonored" not in got
    squat = [{"x": x, "y": y} for x, y in ((0.0, 0.0), (197.0, 0.0), (0.0, 100.0), (197.0, 100.0))]
    assert stages.declare_cluster_shape(squat, "crescent", 3) == {"cluster_shape": "round", "cluster_aspect_drawn": 1.97}
    assert stages.declare_cluster_shape(squat, "round", 3) == {"cluster_shape": "round", "cluster_aspect_drawn": 1.97}
    three = [{"x": x, "y": y} for x, y in ((0.0, 0.0), (300.0, 0.0), (0.0, 100.0), (300.0, 100.0))]
    assert stages.declare_cluster_shape(three, "crescent", 3)["cluster_shape"] == "crescent", "a drawn crescent keeps its roll"
    assert stages.declare_cluster_shape(three, "round", 3)["cluster_shape"] in ("crescent", "elongated")
    assert stages.declare_cluster_shape([], None, 3)["cluster_shape"] == "round"


def test_the_stage_seats_no_more_houses_than_households() -> None:
    """Feature 287, homes H28: every seating loop checks the quota first - the exhaustive pass included - so a margin that
    offers many more seats than households seats exactly the households."""
    s, plan = _toy(10)
    stages.stage_homesteads(s, plan)
    assert len(s.M["houses"]) == 10 and s.M["meta"]["seat_margin"] == 1


def test_the_cloud_alone_seats_the_hamlet_when_the_rows_offer_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287, homes wave 5 (the soak's `test_the_cluster_seeds_cloud_still_seats_a_hamlet_when_the_rows_offer_nothing`,
    on a constructed site): with the front row and the frontage both silent, the ranks and the cloud behind them seat every
    household, and the record says the cloud did."""
    s, plan = _toy(10)
    monkeypatch.setattr(stages, "front_row", lambda plan_, count, **kw: [])
    stages.stage_homesteads(s, plan)
    assert len(s.M["houses"]) == 10 and s.M["meta"]["cluster_seeding"] == "cloud"


def test_no_writer_of_a_household_grain_plot_is_left_in_the_engine() -> None:
    """Feature 287, homes H02: the per-household grain plot's producer was removed (the GM 2026-09-28); no engine module
    writes `homestead_fields` or a `homestead` key on a dry plot, so no roll can lay one."""
    import pathlib
    import re

    root = pathlib.Path(stages.__file__).resolve().parents[2]
    # the writers: the meta key itself, an assignment to a record's `homestead`, a record literal whose `homestead` is a
    # value (a lookup table keyed by the role name - the page's bamboo vocabulary - maps it to a quoted label, and is not one)
    pat = re.compile(r"""homestead_fields|\[["']homestead["']\]\s*=[^=]|["']homestead["']\s*:\s*(?!["'\s])""")
    writers = [str(p) for p in root.rglob("*.py") if pat.search(p.read_text())]
    assert (root / "hamletgen" / "homesteads" / "stages.py").exists(), "the walk is over the engine"
    assert writers == []


def test_a_rank_round_stops_offering_seats_once_the_quota_is_seated(monkeypatch: pytest.MonkeyPatch) -> None:
    """The rank rounds offer many seats; once every household has a house the rest of the round goes unoffered - with a
    placer that seats every seat it is offered, the front row silent, the first round fills the quota part-way through."""
    s, plan = _toy(10)
    monkeypatch.setattr(stages, "front_row", lambda plan_, count, **kw: [])
    offered: list[tuple[float, float]] = []

    def seat(x: float, y: float, kind: str) -> bool:
        offered.append((x, y))
        s.M["houses"].append({"x": x, "y": y, "w": 46.0, "h": 28.0, "kind": kind, "geom": {}})
        return True

    monkeypatch.setattr(s, "try_place", seat)
    placed, _cloud = stages._seat_households(s, plan)
    assert placed == 10 and len(offered) == 10, "ten offered, ten seated, the rest of the round never asked"


# ---- feature 306: the dry-spell cap and the near-miss rescue (plan D2) -------------------------------------------------------


class _Seater:
    """A stand-in for the settlement `offer_seats` reads: a placer that takes the seats listed in `takes`."""

    def __init__(self, takes: set[tuple[float, float]]) -> None:
        self.takes = takes
        self.M: dict[str, object] = {"houses": []}
        self._seat_search = {"candidates": 0}
        self.asked: list[tuple[float, float]] = []

    def try_place(self, x: float, y: float, _kind: str) -> bool:
        self.asked.append((x, y))
        return (x, y) in self.takes


def test_the_pass_gives_a_margin_up_after_a_dry_spell_and_a_take_restarts_it() -> None:
    seats = [(float(1000 * i), 0.0) for i in range(10)]
    s = _Seater({seats[2]})
    placed, offered, took = capacity.offer_seats(s, seats, 0, 5, 3)  # type: ignore[arg-type]
    assert (placed, took) == (1, 1) and offered == 6, "two dry, a take, then three dry: given up after the sixth"
    s = _Seater(set())
    assert capacity.offer_seats(s, seats, 0, 5, None) == (0, 10, 0), "no cap: every seat offered"  # type: ignore[arg-type]
    assert capacity.offer_seats(_Seater({seats[0]}), seats, 0, 1, 3)[:2] == (1, 1), "the want met: no more offered"  # type: ignore[arg-type]


def test_a_near_miss_is_rescued_on_a_finer_grid_with_a_wider_corridor_search(monkeypatch: pytest.MonkeyPatch) -> None:
    """`seat_the_rest` hands a margin left at most `RESCUE_SHORT` households to `rescue_the_margin`, which offers the finer
    grid with the tree's breadth widened for the rescue and set back after it (the corridor memo dropped both ways)."""
    from l7r.diagram.settlement.rolling.access import TARGETS_TRIED, AccessTree

    tree = AccessTree(7.0)
    tree.add((0.0, 0.0), (100.0, 0.0))
    steps: list[float | None] = []
    breadth: list[int] = []

    def seats(s: object, center: object, step: float | None = None) -> list[tuple[float, float]]:
        steps.append(step)
        return [(1.0, 1.0)] if step is None else [(2.0, 2.0), (3.0, 3.0)]

    def offer(s: object, seats: list, placed: int, want: int, dry: int | None) -> tuple[int, int, int]:
        breadth.append(tree.tried)
        took = (want - placed) if dry is None else 0  # the pass seats none; the rescue seats the rest
        return placed + took, len(seats), took

    monkeypatch.setattr(capacity, "free_seats", seats)
    monkeypatch.setattr(capacity, "offer_seats", offer)
    s = Settlement(1000, 1000, seed=1)
    s._seat_search = {}
    s._access = tree
    s.__dict__["_corridor_memo"] = ("state", {})

    class Region:
        def offer(self, pts: list) -> list[bool]:
            return [True] * len(pts)

    s._seat_region = Region()
    plan = a_plan(households=10)
    plan.seat = {"cx": 500.0, "cy": 500.0}
    assert seat_the_rest(s, plan, 10 - capacity.RESCUE_SHORT) == 10
    assert steps == [None, capacity.RESCUE_STEP] and breadth == [TARGETS_TRIED, capacity.RESCUE_TARGETS]
    assert tree.tried == TARGETS_TRIED and "_corridor_memo" not in s.__dict__, "the breadth set back, the memo dropped"
    assert s._seat_search["rescue_took"] == capacity.RESCUE_SHORT
    steps.clear()
    assert seat_the_rest(s, plan, 10 - capacity.RESCUE_SHORT - 1) == 10 - capacity.RESCUE_SHORT - 1, "too far short: no rescue"
    assert steps == [None]


def test_a_rescue_with_no_tree_and_no_region_still_offers_the_finer_grid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(capacity, "free_seats", lambda s, center, step=None: [(5.0, 5.0)])
    s = Settlement(1000, 1000, seed=1)
    s._seat_search = {"candidates": 0}
    s._access = None
    s._seat_region = None
    taken = _Seater({(5.0, 5.0)})
    s.try_place = taken.try_place  # type: ignore[method-assign]
    plan = a_plan(households=10)
    plan.seat = {"cx": 500.0, "cy": 500.0}
    assert capacity.rescue_the_margin(s, plan, 9) == 10
