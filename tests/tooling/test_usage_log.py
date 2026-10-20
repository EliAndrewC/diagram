"""`scripts/hooks/lib/usage_log.py` - one record for every tool that leaves none of its own (feature 406 T01, D160)."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "hooks" / "lib"))
import usage_log as ul  # noqa: E402


def test_a_run_is_recorded_and_a_check_s_exit_handed_back(tmp_path: pathlib.Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    ul.record(tmp_path, "tick-archive", "step", "changed")
    assert ul.exited("check-file-scale", 0, tmp_path) == 0
    assert ul.exited("check-file-scale", 2, tmp_path) == 2
    rows = [json.loads(x) for x in (tmp_path / ".git" / ul.USAGE).read_text().splitlines()]
    assert [(r["tool"], r["kind"], r["outcome"]) for r in rows] == [("tick-archive", "step", "changed"), ("check-file-scale", "check", "passed"), ("check-file-scale", "check", "refused")]
    assert all(r["utc"].endswith("Z") for r in rows)
    assert ul.main(["record", "--tool", "idle-tests", "--kind", "target", "--outcome", "failed", "--root", str(tmp_path)]) == 0
    assert json.loads((tmp_path / ".git" / ul.USAGE).read_text().splitlines()[-1])["tool"] == "idle-tests"


def test_a_record_never_fails_its_tool(tmp_path: pathlib.Path) -> None:
    ul.record(tmp_path / "not-a-repo", "x", "step", "changed")  # no git: nothing written, nothing raised
    assert ul.exited("x", 1, tmp_path / "not-a-repo") == 1
    assert json.loads((REPO / "scripts" / "tool-registry.json").read_text())["tools"] is not None
