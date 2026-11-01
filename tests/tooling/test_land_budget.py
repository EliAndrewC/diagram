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


def test_the_rust_stage_gate_record_is_made_where_owed_and_a_failing_seed_stops_the_landing(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 444 amendment 5 (D6): an engine landing owes a `make rust-gate` record on its engine; land rolls it, commits it,
    and stops on a failing seed."""
    for owed, made, want in ((1, 0, ""), (0, 0, ""), (0, 2, "has a failing seed")):
        land = _land()
        calls: list[list[str]] = []
        monkeypatch.setattr(land, "engine_delta", lambda _root: True)
        monkeypatch.setattr(land, "run", lambda _root, cmd, env=None, quiet=True, owed=owed, calls=calls: (calls.append(cmd), (owed, ""))[1] if "rust-owed" in cmd else (0, ""))  # noqa: ARG005
        monkeypatch.setattr(land, "make", lambda _root, target, made=made, calls=calls: calls.append(["make", target]) or made)
        got = land.rust_gate_run(tmp_path)
        assert (want in got) if want else got == ""
        assert (["make", "rust-gate"] in calls) == (owed == 0)
    land = _land()
    monkeypatch.setattr(land, "engine_delta", lambda _root: False)
    assert land.rust_gate_run(tmp_path) == ""


def test_the_rust_gate_record_is_made_before_the_gate_and_the_cohort(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 444 T21's landing: the landing cohort's own check asks for the Rust stage gate's record, so made after the cohort it
    refused a cohort that had passed 54 of 54. `long_runs` makes it first; a refusal there stops before any gate or cohort runs."""
    land = _land()
    ran: list[list[str]] = []
    monkeypatch.setattr(land, "rust_gate_run", lambda _root: "land: the Rust stage gate has a failing seed")
    monkeypatch.setattr(land, "run", lambda _root, cmd, env=None, quiet=True: ran.append(cmd) or (0, ""))  # noqa: ARG005
    monkeypatch.setattr(land, "start_cohort", lambda _root: (_ for _ in ()).throw(AssertionError("no cohort before the record")))
    assert land.long_runs(tmp_path) == 1 and ran == [], "nothing - not the gate stamp, not the cohort - ran before it"


def test_a_rust_stage_lands_with_no_open_claim_in_its_own_code(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 444 FR-021 (amendment 6, SC-014, as amended 2026-11-01): a phase task's landing is refused while `make claims-report`
    lists an open finding in its Rust; a finding in a file it leaves alone, or none, refuses nothing."""
    land = _land()
    d = tmp_path / "specs" / "444-work-budget-program"
    d.mkdir(parents=True)
    text = "- [ ] T16 phase: field - the comb field\n      phase: field\n- [ ] T09 a tooling task\n"
    report = "claims: ...\n  MISLABELED     rust/phases/src/field.rs::Basin#the plots - a counter, no decision\n  DRIFTED        l7r/other.py::f#x - y\n"
    monkeypatch.setattr(land, "delta_names", lambda _root: ["rust/phases/src/field.rs", "specs/444-work-budget-program/plan.md"])
    monkeypatch.setattr(land, "_stage_seam", lambda _root, _phase: [])
    monkeypatch.setattr(land, "run", lambda _root, cmd, env=None, quiet=True: (0, report))  # noqa: ARG005
    why = land.open_claims_refusal(tmp_path, d, text, "T16")
    assert "1 open claim finding(s)" in why and "rust/phases/src/field.rs::Basin" in why and "l7r/other.py" not in why
    assert land.open_claims_refusal(tmp_path, d, text, "T09") == "", "not a phase task: the claims switch's report stands"
    monkeypatch.setattr(land, "run", lambda _root, cmd, env=None, quiet=True: (0, "claims: no finding\n"))  # noqa: ARG005
    assert land.open_claims_refusal(tmp_path, d, text, "T16") == ""
    monkeypatch.setattr(land, "delta_names", lambda _root: ["specs/x.md"])
    assert land.open_claims_refusal(tmp_path, d, text, "T16") == "", "no rust/ or l7r/ file changed"
    assert land.open_claims_refusal(tmp_path, tmp_path / "specs" / "443-x", text, "T16") == "", "only feature 444's phases"


def test_the_python_a_rust_stage_answers_for_is_what_it_changes_and_what_its_seam_reads(tmp_path: pathlib.Path) -> None:
    """SC-014 as amended (the round arbiter on ask:444-T16-fr021-scope-2; spec-fidelity's exception check): a finding at a unit the
    delta changes refuses; one at an unchanged unit the seam imports at run time refuses; one at another unit of a file the delta
    touches only to delete code, or at a constant imported only for type checking, is filed to the open-claims feature instead."""
    land = _land()
    scope = land._claims_scope()
    pkg = tmp_path / "l7r" / "diagram"
    pkg.mkdir(parents=True)
    (pkg / "shared.py").write_text('KEEP = 1\n"""Research: keep - GUESS: x"""\n\nOLD = 2\n\n\ndef edited():\n    return 3\n\n\ndef other():\n    return 4\n')
    (pkg / "consts.py").write_text('TAP = 70\n"""Research: tap - x"""\nHINT = 1\n')
    (pkg / "seam.py").write_text(
        "from typing import TYPE_CHECKING\n\nfrom l7r.diagram.consts import TAP\n\nif TYPE_CHECKING:\n    from l7r.diagram.consts import HINT\n\n\ndef stage_field(s):\n    return TAP\n"
    )
    report = (
        "claims\n  DRIFTED        l7r/diagram/shared.py::edited#e - a line the delta changed\n"
        "  DRIFTED        l7r/diagram/shared.py::other#o - a unit it left alone\n"
        "  NEEDS-RESEARCH l7r/diagram/consts.py::TAP#tap - the seam reads it\n"
        "  DRIFTED        l7r/diagram/consts.py::HINT#h - a type-checking import only\n"
        "  DRIFTED        l7r/diagram/elsewhere.py::f#f - a file the delta never touched\n"
    )
    diff = {"l7r/diagram/shared.py": "@@ -5,1 +4,0 @@\n-OLD2 = 9\n@@ -8 +8 @@\n-    return 2\n+    return 3\n"}
    own, left = scope.split(tmp_path, report, ["l7r/diagram/shared.py"], [pkg / "seam.py"], lambda p: diff.get(p, ""))
    assert [ln.split("#")[0].split("::")[1] for ln in own] == ["edited", "TAP"]
    assert [ln.split("#")[0].split("::")[1] for ln in left] == ["other"]
    (tmp_path / "specs" / "405-engine-findings-from-385").mkdir(parents=True)
    assert scope.file_left(tmp_path, "T16", left) == 1 and scope.file_left(tmp_path, "T16", left) == 0, "filed once"
