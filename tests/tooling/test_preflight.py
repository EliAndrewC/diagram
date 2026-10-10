"""`scripts/gates/preflight.py` - the gate's first phase and its tree check (feature 375, FR-004, plan D14).

372's wave 106 went red about six times on causes a cheap check finds; one was a file edited mid-gate. These pin the pieces a
later session could break: which changed lines count, which uncovered ones stop the preflight, and the tree that moved.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tests.tooling.test_modal_checks import _load

pf = _load("preflight")
ENV = {"GIT_AUTHOR_NAME": "a", "GIT_AUTHOR_EMAIL": "a@b", "GIT_COMMITTER_NAME": "a", "GIT_COMMITTER_EMAIL": "a@b", "PATH": "/usr/bin:/bin"}


def _repo(tmp: Path) -> Path:
    root = tmp / "r"
    (root / "l7r" / "diagram" / "ci").mkdir(parents=True)
    (root / "l7r" / "diagram" / "a.py").write_text("x = 1\ny = 2\n")
    (root / "l7r" / "diagram" / "ci" / "s.py").write_text("z = 1\n")
    (root / "notes.md").write_text("n\n")
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "base"], check=True, env=ENV)
    return root


def test_the_changed_engine_lines_ci_left_to_the_gate(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "l7r" / "diagram" / "a.py").write_text("x = 1\ny = 3\nw = 4\n")
    (root / "l7r" / "diagram" / "ci" / "s.py").write_text("z = 2\n")
    assert pf.changed_lines(root) == {"l7r/diagram/a.py": {2, 3}}, "ci/ is the gate's: its tests are tooling tests"


def test_uncovered_changed_lines_are_read_from_the_coverage_report() -> None:
    cov = {"files": {"l7r/diagram/a.py": {"missing_lines": [3, 9]}, "l7r/diagram/b.py": {"missing_lines": []}}}
    assert pf.uncovered(cov, {"l7r/diagram/a.py": {2, 3}, "l7r/diagram/b.py": {1}, "l7r/diagram/c.py": {1}}) == {"l7r/diagram/a.py": [3]}
    assert pf.uncovered({"files": {"/abs/l7r/diagram/a.py": {"missing_lines": [2]}}}, {"l7r/diagram/a.py": {2}}) == {"l7r/diagram/a.py": [2]}
    assert pf.coverage_step(Path("."), {}, "1") == ({}, {}), "nothing changed: nothing to run"


def test_a_tree_that_moves_while_the_gate_runs_is_named(tmp_path: Path, capsys) -> None:  # noqa: ANN001
    root = _repo(tmp_path)
    (root / "notes.md").write_text("an edit before the gate\n")
    snap = tmp_path / "snap.json"
    assert pf.main(["--root", str(root), "--tree-snap", str(snap)]) == 0
    assert set(json.loads(snap.read_text())) == {"HEAD", "notes.md"}
    assert pf.main(["--root", str(root), "--tree-check", str(snap)]) == 0, "nothing moved"
    (root / "l7r" / "diagram" / "a.py").write_text("x = 9\n")
    assert pf.main(["--root", str(root), "--tree-check", str(snap)]) == 1
    assert "l7r/diagram/a.py" in capsys.readouterr().out
    subprocess.run(["git", "-C", str(root), "commit", "-qam", "mid-gate"], check=True, env=ENV)
    assert pf.main(["--root", str(root), "--tree-check", str(snap)]) == 1
    assert "HEAD (a commit or a checkout)" in capsys.readouterr().out
    assert pf.tree_moved({"HEAD": "a", "x": "1"}, {"HEAD": "a", "x": "2", "y": "3"}) == ["x", "y"]
    assert pf.main(["--root", str(root), "--tree-check", str(tmp_path / "missing.json")]) == 0, "no snapshot: nothing to judge"
