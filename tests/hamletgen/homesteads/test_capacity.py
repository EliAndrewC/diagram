"""Feature 287, homes H03 and H14 and plan D2: every declared household seated where the seats are chosen, or the site
refused - the exhaustive pass, the margin ladder, the polder's flank, the refusal."""

from __future__ import annotations

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.homesteads import stages
from l7r.diagram.hamletgen.homesteads.capacity import SiteRefused, compass, margin_ladder, seating_mark, unseat_to
from l7r.diagram.settlement import Settlement
from tests.hamletgen._builders import CROWN, a_plan


def _the_passes_the_dispersed_form_keeps(monkeypatch: pytest.MonkeyPatch) -> None:
    """The front row, the ranks, the rescue and the exhaustive pass, which the DISPERSED form keeps (feature 308, the spec's
    round-1 rulings), run on this nucleated toy as they ran before the nucleated cluster was grown (`growth.grows`)."""
    from l7r.diagram.hamletgen.homesteads import stages as _st

    monkeypatch.setattr(_st, "grows", lambda plan: False)


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


def test_a_margin_left_is_cut_back_to_its_mark_and_any_house_cut_is_counted() -> None:
    """`unseat_to`: every registry cut to the mark; a house cut is counted in `meta.houses_taken_back` - the count SC-001
    holds at 0 on every rolled hamlet (feature 318)."""
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
    assert s.M["meta"]["houses_taken_back"] == 1, "the house cut, counted"


def test_a_short_margin_is_refused_and_no_house_it_seated_is_taken_back(monkeypatch: pytest.MonkeyPatch) -> None:
    """SC-001 (feature 318): the chosen margin seats 7 of 10 - the seating is refused, naming the count, and the 7 houses still
    stand; no other margin is seated over them. The ladder is asked only past a margin that seated NO house."""
    s, plan = _toy(10)
    calls: list[tuple[float, float]] = []
    taken: list[int] = []

    def seat_on(s_: Settlement, plan_: hg.SitePlan) -> tuple[int, int]:
        calls.append((plan_.seat["cx"], plan_.seat["cy"]))
        for k in range(7):
            s_.M["houses"].append({"x": float(k), "y": 0.0, "kind": "plain"})
        return 7, 0

    monkeypatch.setattr(stages, "_seat_households", seat_on)
    monkeypatch.setattr(stages, "unseat_to", lambda s_, mark: taken.append(len(s_.M["houses"])))
    with pytest.raises(SiteRefused, match=r"Test \(seed 3\): seated 7 of 10 households on margin 1; no house is taken back"):
        stages.seat_every_household(s, plan)
    assert len(calls) == 1 and len(s.M["houses"]) == 7 and taken == [], "one seating, its houses standing, nothing unseated"


def test_a_margin_that_seats_no_house_passes_to_the_next_and_a_rung_with_no_dry_exit_is_passed_over(monkeypatch: pytest.MonkeyPatch) -> None:
    """D1 (feature 318) and feature 287, ways W23: a margin that cannot start - no house seated - is left for the next rung,
    nothing being taken back; a rung whose seat has no dry way out of the frame is not seated; the rung that seated the hamlet
    is recorded."""
    s, plan = _toy(10)
    assert len(plan.seat["ladder"]) >= 2
    walled, rung = dict(plan.seat["ladder"][0]), dict(plan.seat["ladder"][1])
    calls: list[tuple[float, float]] = []

    def seat_on(s_: Settlement, plan_: hg.SitePlan) -> tuple[int, int]:
        calls.append((plan_.seat["cx"], plan_.seat["cy"]))
        return (0, 0) if len(calls) == 1 else (10, 0)

    monkeypatch.setattr(stages, "_seat_households", seat_on)
    monkeypatch.setattr(stages, "seat_has_dry_exit", lambda plan_, q, toe, wet: q != (walled["cx"], walled["cy"]))
    assert stages.seat_every_household(s, plan) == (10, 0)
    assert calls[1] == (rung["cx"], rung["cy"]) and (walled["cx"], walled["cy"]) not in calls
    assert s.M["meta"]["seat_margin"] == 2 and s.field_face == (float(rung["cx"]), float(rung["cy"]))


def test_a_site_where_no_margin_starts_is_refused_naming_it(monkeypatch: pytest.MonkeyPatch) -> None:
    s, plan = _toy(10)
    plan.seat["ladder"] = plan.seat["ladder"][:1]
    monkeypatch.setattr(stages, "_seat_households", lambda s_, p_: (0, 0))
    with pytest.raises(SiteRefused, match=r"Test \(seed 3\): seated 0 of 10 households on margin 2; no house is taken back"):
        stages.seat_every_household(s, plan)


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


# ---- feature 306: the dry-spell cap (plan D2; the near-miss rescue went with feature 318) ----------------------------------


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
