"""The one reader of a spec's fidelity verdict, `hm_arbiter.spec_verdict` (feature 442), through the door the Rust gate asks it by (`spec-verdict`, feature 449 T064). In phase 3 these go with `hm_arbiter.py`."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ARBITER = REPO / "scripts" / "hooks" / "lib" / "hm_arbiter.py"


def _sha(d: Path) -> str:
    spec = importlib.util.spec_from_file_location("hm_arbiter_verdict_test", ARBITER)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return str(mod.spec_body_sha(d))


def _feature(root: Path, name: str, spec: str) -> Path:
    d = root / "specs" / name
    d.mkdir(parents=True)
    (d / "tasks.md").write_text("- [x] T01 done\n", encoding="utf-8")
    (d / "spec.md").write_text(spec, encoding="utf-8")
    return d


def _faithful(d: Path) -> bool:
    return subprocess.run([sys.executable, str(ARBITER), "spec-verdict", str(d)], capture_output=True, check=False).returncode == 0


def test_no_spec_file_means_no_verdict(tmp_path: Path) -> None:
    d = _feature(tmp_path, "9-x", "x")
    (d / "spec.md").unlink()
    assert not _faithful(d)


@pytest.mark.parametrize(
    ("body", "want"),
    [("- round 2 (spec-fidelity-verify): FAITHFUL\n", True), ("- round 1: NOT FAITHFUL\n", False), ("the word FAITHFUL in prose\n", False), ("FAITHFUL\n", False)],
)
def test_a_verdict_is_a_line_naming_its_review(tmp_path: Path, body: str, want: bool) -> None:
    assert _faithful(_feature(tmp_path, "90-v", "# F\n\n## Review history\n" + body)) == want


def test_a_stale_ruling_stands_for_nothing(tmp_path: Path) -> None:
    d = _feature(tmp_path, "903-v", "# F\n\n## Review history\n- round 2: CHANGES REQUIRED\n")
    (d / "arbiter.jsonl").write_text(json.dumps({"trigger": "ask:x", "review": "spec", "ruling": "accept", "spec_sha": "stale"}) + "\n", encoding="utf-8")
    assert not _faithful(d)


def test_a_spec_the_round_arbiter_accepted_at_its_cap_is_faithful(tmp_path: Path) -> None:
    """Feature 387; a plan's cap, another feature's or a `continue` is no verdict."""
    d = _feature(tmp_path, "387-x", "## Review history\n- round 5: CHANGES REQUIRED\n")
    rows = [
        {"trigger": "round:spec-fidelity|plan:387-x#T01@3", "ruling": "accept"},
        {"trigger": "round:spec-fidelity|388-y#1@6", "ruling": "accept"},
        {"trigger": "round:spec-fidelity|387-x#1@6", "ruling": "continue"},
    ]
    (d / "arbiter.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\nnot json\n", encoding="utf-8")
    assert not _faithful(d)
    with (d / "arbiter.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"trigger": "round:spec-fidelity|387-x#1@6", "ruling": "accept", "spec_sha": _sha(d)}) + "\n")
    assert _faithful(d)


def test_a_spec_ruled_on_an_asked_round_is_faithful(tmp_path: Path) -> None:
    """Feature 440; an asked ruling on another review, or a `continue`, is still no verdict."""
    d = _feature(tmp_path, "440-x", "## Review history\n- round 2: CHANGES REQUIRED\n")
    (d / "arbiter.jsonl").write_text(
        json.dumps({"trigger": "ask:440-x", "review": "plan", "ruling": "accept"}) + "\n" + json.dumps({"trigger": "ask:440-y", "review": "spec", "ruling": "continue"}) + "\n", encoding="utf-8"
    )
    assert not _faithful(d)
    with (d / "arbiter.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"trigger": "ask:440-spec-round-3", "review": "spec", "ruling": "accept", "spec_sha": _sha(d)}) + "\n")
    assert _faithful(d)
