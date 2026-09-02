"""The cohort harness (`tools/cohort_audit.py`).

Feature 174, under the GM's 2026-09-02 ruling; the module had never been measured. Three properties
here were each learned by paying for them, and they are what these tests pin:

- the reference settlement is a GATE, not a suggestion (GM 2026-08-24). A cohort is 20-25 minutes and
  the reference map is 60 seconds; feature 126 ran SIX cohorts in one sitting, most of them launched
  when the failures were already known. `make maps` already gated on this and it did not help,
  because this module has its own entry point - a guard on one door is not a guard.
- the scope lock comes FIRST, before even that, and no flag walks around it.
- the audit rolls through `generate`, not `build` - "a harness that exercises a different code path
  than production reports on a map nobody will ever see".

The generator is stubbed throughout: what is under test is the harness, and rolling real hamlets to
check a report's arithmetic would cost minutes per assertion.
"""

from __future__ import annotations

import concurrent.futures
import sys
from pathlib import Path
from typing import Any

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.tools import cohort_audit as ca

pytestmark = pytest.mark.tooling


def _report(failures: list[str], lines: list[str] | None = None) -> Any:
    plan = type("P", (), {"down_deg": 90.0, "water_sink": "pond", "cluster_shape": "crescent", "lane_skeleton": "spine"})()
    return type("R", (), {"failures": failures, "fail_lines": lines if lines is not None else [f"{f}: it failed" for f in failures], "plan": plan})()


@pytest.fixture
def _clean(monkeypatch: pytest.MonkeyPatch) -> None:
    from l7r.diagram import switches

    monkeypatch.setattr(switches, "locked_out", lambda _why: False)
    monkeypatch.setattr(hg, "generate", lambda spec, out_base, render: _report([]))


def test_a_cohort_is_REFUSED_under_the_scope_lock_and_no_flag_walks_around_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """ "a cohort is the GM's own definition of the full test suite, and under the lock it does not
    run - not with --anyway, not with any flag"."""
    from l7r.diagram import switches

    monkeypatch.setattr(switches, "locked_out", lambda _why: True)
    called: list[int] = []
    monkeypatch.setattr(ca, "audit", lambda *a, **k: called.append(1) or 0)
    assert ca.main(["--count", "4"]) == 2
    assert ca.main(["--count", "4", "--anyway"]) == 2, "--anyway does not reach the lock"
    assert called == [], "and the cohort never started"


def test_a_FAILING_reference_settlement_stops_the_cohort_and_says_what_to_do(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The 60-second question that gates the 25-minute answer. The message hands over the next
    command, and names the override rather than hiding it."""
    from l7r.diagram import switches

    monkeypatch.setattr(switches, "locked_out", lambda _why: False)
    monkeypatch.setattr(hg, "generate", lambda spec, out_base, render: _report(["village_windbreak_is_continuous[2]"]))
    started: list[int] = []
    monkeypatch.setattr(ca, "audit", lambda *a, **k: started.append(1) or 0)

    assert ca.main(["--count", "48"]) == 2
    out = capsys.readouterr().out
    assert "REFERENCE SETTLEMENT IS FAILING" in out
    assert "cohort_audit --count 48" in out and "--anyway overrides" in out
    assert started == [], "25 minutes not spent"


def test_ANYWAY_skips_the_reference_gate_because_a_rule_with_no_escape_gets_worked_around(monkeypatch: pytest.MonkeyPatch) -> None:
    """ "deliberately awkward to type" - but it exists, and it must actually reach the cohort."""
    from l7r.diagram import switches

    monkeypatch.setattr(switches, "locked_out", lambda _why: False)
    rolled: list[Any] = []
    monkeypatch.setattr(hg, "generate", lambda spec, out_base, render: rolled.append(spec) or _report(["anything"]))
    monkeypatch.setattr(ca, "audit", lambda *a, **k: 0)
    assert ca.main(["--count", "2", "--anyway"]) == 0
    assert rolled == [], "the reference map was not even rolled"


def test_a_clean_reference_runs_the_cohort_and_passes_its_arguments_through(_clean, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, Any] = {}
    monkeypatch.setattr(ca, "audit", lambda count, seed, only, jobs: seen.update(count=count, seed=seed, only=only, jobs=jobs) or 0)
    assert ca.main(["--count", "6", "--seed", "9", "--only", "wells", "--jobs", "2"]) == 0
    assert seen == {"count": 6, "seed": 9, "only": "wells", "jobs": 2}


def test_roll_one_goes_through_GENERATE_which_is_the_path_that_ships(monkeypatch: pytest.MonkeyPatch) -> None:
    """It called `build` directly, which skips everything `generate` does around the stages - so a
    fix living in `generate` was invisible to the cohort, measured on seed 5. The header carries the
    plan's own rolled knobs, which is what makes a failing line reproducible."""
    seen: dict[str, Any] = {}

    def generate(spec: Any, out_base: Any, render: bool) -> Any:
        seen.update(name=spec.name, seed=spec.seed, out_base=out_base, render=render)
        return _report(["a_check[1]"])

    monkeypatch.setattr(hg, "generate", generate)
    header, failures, lines = ca.roll_one((7, 13))
    assert seen["seed"] == 7 and seen["render"] is False and seen["out_base"] is None
    assert "seed=7 households=13" in header and "sink=pond" in header and "shape=crescent" in header
    assert failures == ["a_check[1]"] and lines


def test_audit_tallies_the_residue_by_CHECK_and_its_rc_is_the_verdict(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The report's whole value is the residue table: which check is failing, how often, across the
    cohort. The seed index is stripped so the same check on four maps tallies as four, not one each."""
    answers = {1: [], 2: ["wells_are_shared[3]"], 3: ["wells_are_shared[9]"], 4: ["lanes_reach_something[1]"]}
    monkeypatch.setattr(ca, "roll_one", lambda spec: (f"--- seed {spec[0]}", answers[spec[0]], [f"{f} detail" for f in answers[spec[0]]]))
    assert ca.audit(4, 1, jobs=1) == 1
    out = capsys.readouterr().out
    assert "1/4 passed the whole gate" in out
    assert "2  wells_are_shared" in out and "1  lanes_reach_something" in out

    monkeypatch.setattr(ca, "roll_one", lambda spec: (f"--- seed {spec[0]}", [], []))
    assert ca.audit(2, 1, jobs=1) == 0
    assert "2/2 passed" in capsys.readouterr().out


def test_only_narrows_both_the_tally_and_the_printed_lines(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """`--only` is for chasing one check across the cohort; a map whose only failures are other
    checks must drop out of the count entirely, not appear with an empty body."""
    monkeypatch.setattr(ca, "roll_one", lambda spec: ("--- h", ["wells_are_shared[1]", "lanes_reach_something[2]"], ["wells_are_shared detail", "lanes_reach_something detail"]))
    assert ca.audit(1, 1, only="wells", jobs=1) == 1
    out = capsys.readouterr().out
    assert "wells_are_shared detail" in out and "lanes_reach_something detail" not in out

    monkeypatch.setattr(ca, "roll_one", lambda spec: ("--- h", ["lanes_reach_something[2]"], ["lanes detail"]))
    assert ca.audit(1, 1, only="wells", jobs=1) == 0, "no map failed the check being chased"


def test_the_rolls_FAN_OUT_across_processes_and_the_report_stays_in_seed_order(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """ "a map is a pure function of its spec, so parallelism can only change the wall clock, never a
    verdict" - and results are collected in seed order so the report reads identically to a serial
    one. A pool that returned out of order would make two runs of the same cohort disagree on paper."""

    class _Pool:
        def __init__(self, max_workers: int) -> None:
            seen["jobs"] = max_workers

        def __enter__(self) -> _Pool:
            return self

        def __exit__(self, *_a: Any) -> None:
            return None

        def map(self, fn: Any, specs: Any) -> Any:
            return [fn(s) for s in specs]

    seen: dict[str, Any] = {}
    monkeypatch.setattr(concurrent.futures, "ProcessPoolExecutor", _Pool)
    monkeypatch.setattr(ca, "roll_one", lambda spec: (f"--- seed {spec[0]}", ["c[1]"], [f"seed {spec[0]} detail"]))
    assert ca.audit(3, 5, jobs=3) == 1
    out = capsys.readouterr().out
    assert seen["jobs"] == 3
    assert out.index("seed 5 detail") < out.index("seed 6 detail") < out.index("seed 7 detail")


def test_the_skill_root_is_put_on_sys_path_when_it_is_not_already_there(monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib

    monkeypatch.setattr(sys, "path", [p for p in sys.path if Path(p).resolve() != Path(ca.HERE).resolve()])
    reloaded = importlib.reload(ca)
    assert Path(reloaded.HERE).resolve() in [Path(p).resolve() for p in sys.path]
