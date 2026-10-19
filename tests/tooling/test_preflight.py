"""`scripts/gates/preflight.py` - the gate's first phase and its tree check (feature 375, FR-004, plan D14).

372's wave 106 went red about six times on causes a cheap check finds; one was a file edited mid-gate. These pin the pieces a
later session could break: which changed lines count, which uncovered ones stop the preflight, and the tree that moved.
"""

from __future__ import annotations

import json
import re
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


def test_modules_tested_outside_the_quick_tier_are_left_to_the_gate() -> None:
    root = Path(__file__).resolve().parents[2]
    out = pf.outside_quick(root)
    assert "l7r/diagram/settlement/city/bridges.py" in out, "a module the gate trees reach and quick does not (citybudget.py and city/walls.py, earlier examples, went in feature 392)"
    assert any(f.startswith("l7r/diagram/tools/cohort_audit") for f in out), "a tooling-marked audit test"
    assert "l7r/diagram/tools/claims.py" not in out, "its tests run in the quick tier"


def test_the_moved_tree_check_runs_before_the_gate_vouches_for_anything() -> None:
    """374, 2026-10-12: the check ran after the gate stamps and the green run-log entry, so a refused gate left both - the
    finished-run hook reported it green, and measure-hooks refused the honest re-run as a second gate after a green one."""
    text = (Path(__file__).resolve().parents[2] / "Makefile").read_text(encoding="utf-8")
    start = re.search(r"^done:", text, re.M)
    assert start, "the Makefile has a `done` target"
    rest = text[start.end() :]
    end = re.search(r"^[A-Za-z0-9_.-]+:", rest, re.M)
    recipe = rest[: end.start()] if end else rest
    check = recipe.index("--tree-check")
    assert check < recipe.index("check-run-plausible.py\" $(DONE_NAME)"), "the tree check comes before the plausibility floor"
    assert check < recipe.index("gate-stamp.py\" --write diagram && "), "and before the stamps the push trusts"
    assert check < recipe.index(" green \"$$(cat"), "and before the green run-log entry"
    refusal = recipe[check : recipe.index("exit 1; }", check)]
    assert '"failed: tree moved"' in refusal and "failed-gate" in refusal, "a refusal is logged as a failure"


def test_a_probe_test_left_in_the_tree_stops_the_gate(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    """Feature 385 (the round arbiter's fix on red-gate@2026-10-17T17:21:08Z): a `tests/**/test_zz_probe*.py` a diagnosis left
    behind would run in the full suite; the preflight refuses to start while one stands, naming it."""
    (tmp_path / "tests" / "tooling").mkdir(parents=True)
    assert pf.stray_probes(tmp_path) == []
    (tmp_path / "tests" / "tooling" / "test_zz_probe_a05.py").write_text("def test_x(): pass\n", encoding="utf-8")
    (tmp_path / "tests" / "tooling" / "test_zz_probe_old.cpython-314.pyc").write_text("", encoding="utf-8")
    assert pf.stray_probes(tmp_path) == ["tests/tooling/test_zz_probe_a05.py"], "a stale .pyc is no probe"
    assert pf.main(["--root", str(tmp_path)]) == 1 and "test_zz_probe_a05.py" in capsys.readouterr().out
