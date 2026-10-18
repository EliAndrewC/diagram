"""A plan review's third round on one task waits for the round arbiter (feature 385 T16; the round arbiter's tooling fix on
hour:385-approach-checklist@9: T14's plan went to a fourth round held back only by the session remembering the rule)."""

from __future__ import annotations

import json
import pathlib
import subprocess

from tests.tooling.test_modal_checks import _load

rr = _load("hm_review_round")
ha = _load("hm_arbiter")


def _clone(tmp: pathlib.Path, reviews: list[dict]) -> pathlib.Path:
    subprocess.run(["git", "init", "-q", str(tmp)], check=True)
    d = tmp / "specs" / "385-x"
    d.mkdir(parents=True)
    (d / "tasks.md").write_text("- [ ] T14 the work\n")
    (d / "plan-review.json").write_text(json.dumps({"block_reviews": reviews}))
    (tmp / ".specify").mkdir()
    (tmp / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": "specs/385-x"}))
    return tmp


def _r(verdict: str, *blocks: str) -> dict:
    return {"verdict": verdict, "blocks": list(blocks)}


def test_a_task_s_plan_rounds_are_counted_back_to_its_last_clear(tmp_path: pathlib.Path) -> None:
    root = _clone(tmp_path, [_r("BLOCKED", "### T14 Decisions"), _r("CLEAR", "### T14 Decisions"), _r("BLOCKED", "## Landing", "### T14 Approach (checklist part A)"),
                             _r("BLOCKED", "### T03 Decisions"), _r("BLOCKED", "### T14 Decisions"), _r("CLEAR", "### T140 Decisions")])
    assert rr.plan_rounds(root / "specs" / "385-x", "T14") == 2, "back to T14's CLEAR; T03's and T140's rounds are not T14's"
    assert rr.plan_rounds(tmp_path / "none", "T14") == 0


def test_the_third_plan_round_trips_the_arbiter_and_a_continue_lifts_it(tmp_path: pathlib.Path) -> None:
    root = _clone(tmp_path, [_r("BLOCKED", "### T14 Decisions")])
    assert rr.plan_cap_refusal(root) == "", "round 2 passes"
    (root / "specs" / "385-x" / "plan-review.json").write_text(json.dumps({"block_reviews": [_r("BLOCKED", "### T14 Decisions")] * 2}))
    held = rr.plan_cap_refusal(root)
    assert held.startswith("BLOCKED: round 3 of T14's plan review") and "round:spec-fidelity|plan:385-x#T14@3" in held
    assert "round:spec-fidelity|plan:385-x#T14@3" in ha.owed(root)
    payload = {"tool_name": "Agent", "tool_input": {"subagent_type": "spec-fidelity", "prompt": "MODE 4: PLAN REVIEW of 2 block(s)"}}
    v = rr.judge(payload, str(root))
    assert v["event"] == "blocked" and v["rule"] == "plan-round-cap" and v["exit"] == 2
    esc = rr.judge({**payload, "tool_input": {**payload["tool_input"], "prompt": "MODE 4: PLAN REVIEW ARBITER_OK=\"the arbiter ruled in the session\""}}, str(root))
    assert esc["event"] == "escaped" and esc["exit"] == 0
    ha.record_ruling(root, "round:spec-fidelity|plan:385-x#T14@3", {"ruling": "continue", "why": "converging"}, "round-arbiter")
    assert rr.plan_cap_refusal(root) == "", "a continue lifts the cap by one round"
    (root / ".specify" / "feature.json").write_text("{}")
    assert rr.plan_cap_refusal(root) == "", "no active task: nothing to count"
