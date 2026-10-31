"""`scripts/land.py` `budget_run` (feature 444 T20, D1): the work-budget run the push asks for, made by the landing - T17's and
T19's landings each lost a gate to the push's "no work-budget run at the pushed engine"."""

from __future__ import annotations

import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]


def _land():  # noqa: ANN202 - the script by path
    spec = importlib.util.spec_from_file_location("land_budget_under_test", REPO / "scripts" / "land.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _wired(monkeypatch, review: tuple[int, str], made: int = 0, engine: bool = True):  # noqa: ANN001, ANN202
    land = _land()
    calls: list[list[str]] = []

    def run(_root, cmd, env=None, quiet=True):  # noqa: ANN001, ANN202, ARG001
        calls.append(cmd)
        return review if "work-budget-review" in cmd else (0, "")

    monkeypatch.setattr(land, "engine_delta", lambda _root: engine)
    monkeypatch.setattr(land, "run", run)
    monkeypatch.setattr(land, "make", lambda _root, target: calls.append(["make", target]) or made)
    return land, calls


def test_a_missing_run_is_made_and_committed(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    land, calls = _wired(monkeypatch, (1, f"work-budget-review: REFUSED - {_land().MISSING_RUN} (code id abc)"))
    assert land.budget_run(tmp_path) == ""
    assert ["make", "work-budget"] in calls and any(c[:2] == ["git", "commit"] for c in calls)


def test_a_stage_over_its_figure_still_stops_the_landing(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    land, calls = _wired(monkeypatch, (1, "work-budget-review: REFUSED - an accepted stage grew past its figure"))
    assert "refuses this engine" in land.budget_run(tmp_path) and ["make", "work-budget"] not in calls


def test_nothing_is_run_without_an_engine_delta_or_with_a_run_in_hand(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    land, calls = _wired(monkeypatch, (1, "x"), engine=False)
    assert land.budget_run(tmp_path) == "" and calls == []
    land, calls = _wired(monkeypatch, (0, "every accepted stage within its figures"))
    assert land.budget_run(tmp_path) == "" and ["make", "work-budget"] not in calls
    land, calls = _wired(monkeypatch, (1, f"REFUSED - {_land().MISSING_RUN}"), made=2)
    assert "make work-budget failed" in land.budget_run(tmp_path)
