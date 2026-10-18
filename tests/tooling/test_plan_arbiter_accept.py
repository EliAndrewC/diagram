"""Past the plan-round cap, the round arbiter's accept stands as the plan's verdict (feature 385 T16's defect, found on T17,
2026-10-18: the cap's accept closed the review and the plan could never be CLEAR, so the task could never be ticked)."""

from __future__ import annotations

import json
import pathlib
import subprocess

from tests.tooling.test_modal_checks import _load

pg = _load("plan_gate")

TRIG = "round:spec-fidelity|plan:385-x#T17@3"

def _clean_env() -> dict[str, str]:
    """The environment without the outer make's variables: a test run under `make arbiter-fix-done LAND=...` inherits LAND= through
    MAKEFLAGS, and a `make` the test runs would then land tooling for real (found 2026-10-18, T20's landing)."""
    import os

    return {k: v for k, v in os.environ.items() if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "MAKEOVERRIDES")}



def _feature(tmp: pathlib.Path, rows: list[dict]) -> pathlib.Path:
    d = tmp / "specs" / "385-x"
    d.mkdir(parents=True)
    (d / "plan.md").write_text("# plan\n\n## T17 - x\n\n### T17 Decisions\n\n**D1** the rule.\n")
    (d / "plan-review.json").write_text(json.dumps({"feature": "385-x", "blocks": {"### T17 Decisions": {"sha256": "old", "verdict": "BLOCKED"}}}))
    (d / "arbiter.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    return d


def test_an_accept_records_the_owed_blocks_clear_and_nothing_else_does(tmp_path: pathlib.Path) -> None:
    d = _feature(tmp_path / "a", [{"trigger": TRIG, "ruling": "continue"}])
    assert pg.owed(d) is not None
    try:
        pg.arbiter_accept(d, TRIG)
        raise AssertionError("a continue is no verdict")
    except PermissionError as e:
        assert "holds no accept" in str(e)
    try:
        pg.arbiter_accept(d, "round:quote-check|q:1@3")
        raise AssertionError("not a plan trigger")
    except ValueError:
        pass
    d = _feature(tmp_path / "b", [{"trigger": TRIG, "ruling": "accept"}])
    done = pg.arbiter_accept(d, TRIG)
    assert "### T17 Decisions" in done and pg.owed(d) is None, "the plan is CLEAR on the arbiter's accept"
    rec = json.loads((d / "plan-review.json").read_text())
    assert rec["blocks"]["### T17 Decisions"]["declared"] == "round-arbiter" and rec["block_reviews"][-1]["declared"] == "round-arbiter"
    (d / "plan.md").write_text((d / "plan.md").read_text() + "\n**D2** a later change.\n")
    assert pg.owed(d) is not None, "a change after the accept owes a review again"
    assert pg.main(["arbiter-accept", str(d), TRIG]) == 0 and pg.owed(d) is None
    assert pg.main(["arbiter-accept", str(tmp_path / "none"), TRIG]) == 2
    assert pg.main(["arbiter-accept", str(d), "round:x|q@3"]) == 2


def test_make_plan_verdict_arbiter_runs_only_the_accept() -> None:
    repo = pathlib.Path(__file__).resolve().parents[2]
    dry = subprocess.run(["make", "-n", "-C", str(repo), "plan-verdict", "F=385", f"ARBITER={TRIG}"], capture_output=True, text=True, check=False, env=_clean_env()).stdout
    line = next(ln for ln in dry.splitlines() if "plan_gate.py" in ln)
    assert f'arbiter-accept "385" "{TRIG}"' in line and "--as" not in line


def test_recording_the_arbiter_s_accept_makes_it_the_plan_s_verdict(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    ha = _load("hm_arbiter")
    root = tmp_path
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    d = _feature(root, [])
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": "specs/385-x"}))
    ha.trip(root, TRIG, "round", "spec-fidelity|plan:385-x#T17", "round 3 of T17's plan review")
    ruling = root / "ruling.json"
    ruling.write_text(json.dumps({"ruling": "accept", "why": "converged, wording only", "what": "the plan stands"}))
    monkeypatch.chdir(root)
    assert ha.main(["ruled", TRIG, str(ruling), "--as", "round-arbiter"]) == 0
    assert pg.owed(d) is None, "the accept recorded the plan CLEAR in the same command"
