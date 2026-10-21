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
    assert "l7r/diagram/a.py" in capsys.readouterr().out, "a commit is read for what it changed (405 T41)"
    assert pf.seen_moves(root, {"HEAD": "0" * 40}, {"HEAD": "1" * 40}) == ["HEAD"], "a HEAD move that cannot be read"
    assert pf.tree_moved({"HEAD": "a", "x": "1"}, {"HEAD": "a", "x": "2", "y": "3"}) == ["x", "y"]
    assert pf.main(["--root", str(root), "--tree-check", str(tmp_path / "missing.json")]) == 0, "no snapshot: nothing to judge"


def test_modules_tested_outside_the_quick_tier_are_left_to_the_gate() -> None:
    root = Path(__file__).resolve().parents[2]
    out = pf.outside_quick(root)
    # ANY settlement module, not one pinned by path: a pinned example broke twice in feature 392 (citybudget.py, then
    # city/walls.py) when a deletion took it (the round arbiter's fix on red-gate@2026-10-19T01:59:22Z)
    assert any(f.startswith("l7r/diagram/settlement/") for f in out), "some module the gate trees reach and quick does not"
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


def test_a_pool_map_the_gate_rolled_itself_is_no_tree_move_and_another_map_s_still_is(tmp_path: Path, capsys) -> None:  # noqa: ANN001
    """Feature 385 T87 (plan D108): T10's gate rolled Kuwabata, then failed on its own kuwabata.json as a tree move."""
    root = _repo(tmp_path)
    for m in ("kuwa", "other"):
        d = root / "pool" / "hamlets" / m
        d.mkdir(parents=True)
        (d / f"{m}.gen.py").write_text("x = 1\n")
        (d / f"{m}.json").write_text("{}\n")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True, env=ENV)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "maps"], check=True, env=ENV)
    snap, census = tmp_path / "snap.json", tmp_path / "census.jsonl"
    assert pf.main(["--root", str(root), "--tree-snap", str(snap)]) == 0
    census.write_text(json.dumps({"kind": "roll", "gen": str(root / "pool/hamlets/kuwa/kuwa.gen.py")}) + "\n")
    (root / "pool/hamlets/kuwa/kuwa.json").write_text('{"rolled": 1}\n')  # the gate's own re-roll
    assert pf.main(["--root", str(root), "--tree-check", str(snap), "--census", str(census)]) == 0
    assert "re-rolled by the gate - commit them" in capsys.readouterr().out
    (root / "pool/hamlets/other/other.json").write_text('{"hand": 1}\n')  # a map the gate did not roll
    assert pf.main(["--root", str(root), "--tree-check", str(snap), "--census", str(census)]) == 1
    assert "pool/hamlets/other/other.json" in capsys.readouterr().out


def test_a_changed_function_is_judged_whole() -> None:
    """Feature 405 T40 (D14): T14 reworked the one unit test that reached `sweeps.py:738`, a line it did not change, in a
    function it did; the preflight asked only the changed lines and the gate's floor failed 5.7 minutes in."""
    text = "x = 1\n\n\ndef f(a):\n    if a:\n        return 1\n    return 2\n\n\nclass C:\n    def m(self):\n        return 3\n"
    assert pf.function_spans(text) == [(4, 7), (11, 12)]
    assert pf.function_spans("def (") == []
    assert pf.base_line("a\nb\nc\nd", "a\nB\nc\nd\ne", 3) == 3 and pf.base_line("a\nb\nc\nd", "a\nB\nc\nd\ne", 2) is None
    assert pf.base_line("a\nb", "z\na\nb", 3) == 2, "a line moved down by an insertion maps to its old place"
    assert pf.test_key("tests/a/test_b.py::test_c[1]@grp|run") == "tests.a.test_b::test_c[1]"
    assert pf.test_key("tests/a/test_b.py::K::test_c|setup") == "tests.a.test_b.K::test_c"
    assert pf.test_key("fixture:tests/a/test_b.py::built") is None and pf.test_key("") is None


def test_the_widened_lines_and_the_quick_run_s_tests(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "l7r" / "diagram" / "a.py").write_text("x = 1\n\n\ndef f(a):\n    if a:\n        return 1\n    return 2\n")
    subprocess.run(["git", "-C", str(root), "commit", "-qam", "f"], check=True, env=ENV)
    subprocess.run(["git", "-C", str(root), "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
    (root / "l7r" / "diagram" / "a.py").write_text("x = 1\n\n\ndef f(a):\n    if a:\n        return 10\n    return 2\n")
    assert pf.changed_lines(root) == {"l7r/diagram/a.py": {4, 5, 6, 7}}
    assert pf.changed_lines(root, widen=False) == {"l7r/diagram/a.py": {6}}
    junit = tmp_path / "q.xml"
    junit.write_text('<testsuites><testsuite><testcase classname="tests.a.test_b" name="test_c"/></testsuite></testsuites>')
    assert pf.quick_ids(junit) == {"tests.a.test_b::test_c"} and pf.quick_ids(tmp_path / "none.xml") == set()


def test_a_line_only_unit_tests_reached_at_the_last_green_gate_stops_the_preflight(tmp_path: Path) -> None:
    """Feature 405 T40 (D14): the gate baseline's `coverage.db` says what reached each line; a line the quick run now leaves unrun
    and only quick-tier tests reached there is reached by no roll either."""
    from coverage import CoverageData

    root = _repo(tmp_path)
    base_text = "def f(a):\n    if a:\n        return 1\n    return 2\n"
    f = "l7r/diagram/a.py"
    (root / f).write_text(base_text)
    subprocess.run(["git", "-C", str(root), "commit", "-qam", "f"], check=True, env=ENV)
    subprocess.run(["git", "-C", str(root), "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
    blob = subprocess.run(["git", "-C", str(root), "rev-parse", f"HEAD:{f}"], capture_output=True, text=True, check=True).stdout.strip()
    (root / f).write_text("def f(a):\n    if a:\n        return 1\n    return 20\n")  # line 4 changed; line 3 not
    assert pf.unit_only(root, {f: [3]}, set()) == {}, "no baseline: the gate judges, as before"
    base = root / ".git" / "gate-baseline"
    base.mkdir()
    (base / "manifest.json").write_text(json.dumps({"engine": {f: blob}}))
    cov = CoverageData(basename=str(base / "coverage.db"))
    cov.set_context("tests/x/test_a.py::test_unit|run")
    cov.add_lines({str(root / f): [1, 2, 3, 4]})
    cov.set_context("tests/gate/test_roll.py::test_roll|run")
    cov.add_lines({str(root / f): [1, 2, 4]})
    cov.write()
    quick = {"tests.x.test_a::test_unit"}
    assert pf.unit_only(root, {f: [3, 4]}, quick) == {f: [3]}, "3: unit tests only; 4: changed, the gate's to judge"
    assert pf.split_gaps(root, {f: [3, 4]}, {f}, quick) == ({f: [3]}, {f: [4]}), "on the hamlet path: 3 stops, 4 goes to the gate"
    every = quick | {"tests.gate.test_roll::test_roll"}
    assert pf.split_gaps(root, {f: [4]}, set(), every) == ({f: [4]}, {}), "a changed line off the path, its function reached by no gate test, stops"
    assert pf.unit_only(root, {f: [3]}, set()) == {}, "the unit test is not the quick run's: it may be a roll's"
    assert pf.unit_only(root, {"l7r/diagram/b.py": [1]}, quick) == {}, "a file the baseline does not hold"
    # a CHANGED line off the hamlet path, in a function a gate-tier test reached at the baseline: the gate judges it (T42's
    # landing: `gencache.gate_obtain`, which the pool sweep runs)
    assert pf.gate_reached(root, {f: [4]}, quick) == {f: [4]}
    assert pf.split_gaps(root, {f: [4]}, set(), quick) == ({}, {f: [4]})
    assert pf.gate_reached(root, {f: [4]}, quick | {"tests.gate.test_roll::test_roll"}) == {}, "reached by quick tests alone"
    (root / f).write_text("x = 1\n")
    assert pf.gate_reached(root, {f: [1]}, quick) == {}, "a line in no function"


def test_a_change_the_gate_does_not_see_does_not_move_the_tree(tmp_path: Path) -> None:
    """Feature 405 T41 (D15): T14's claims round - claim docstrings and its records - voided a running gate. The gate's own key
    strips docstrings; the claims round's records are read by no phase of it. Code, a byte-hashed area, a deleted file still move it."""
    root = _repo(tmp_path)
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": "specs/405-x"}))
    f = "l7r/diagram/a.py"
    old = b'def f(x):\n    """Research: a - NONE"""\n    return x\n'
    assert pf.unseen(root, f, old, old.replace(b"a - NONE", b"a reworded - NONE"))
    assert pf.unseen(root, f, old, old.replace(b"return x", b"return x  # why"))
    assert not pf.unseen(root, f, old, old.replace(b"return x", b"return x + 1"))
    assert not pf.unseen(root, f, old, None) and not pf.unseen(root, "notes.md", b"a", b"b")
    assert pf.unseen(root, "dev/claims-index.json", b"{}", b"{1}") and pf.unseen(root, "specs/405-x/found.jsonl", None, b"r")
    assert pf.unseen(root, "dev/cohort-log/20261021T1046Z-x.json", None, b"{}"), "a new cohort record, committed beside the gate (405 T48)"
    assert not pf.unseen(root, "dev/cohort-log/20261021T1046Z-x.json", b"{}", b"{1}"), "...an existing one changed is seen"
    assert not pf.unseen(root, "dev/cohort-log/CLAUDE.md", None, b"x")
    assert not pf.unseen(root, "specs/405-x/plan.md", b"a", b"b") and not pf.unseen(root, "specs/406-y/tasks.md", b"a", b"b")
    reg = "l7r/diagram/interactive/classes/k.py"
    assert not pf.unseen(root, reg, old, old.replace(b"a - NONE", b"b - NONE")), "the registry's docstrings are the page's text"
    (root / ".specify" / "feature.json").write_text("not json")
    assert pf.active_records(root) == set()


def test_the_gate_s_preflight_leaves_the_coverage_step_to_make_preflight(tmp_path: Path, monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    """Feature 405 T47 (D25): the step cost 98-107 s of each gate and refused about twice in the whole record, once wrongly;
    `--no-coverage` (the `done` recipe's) ends after the quick tier, `make preflight` still runs it."""
    asked: list[str] = []
    monkeypatch.setattr(pf, "run", lambda cmd, root, quiet=True: 0)
    monkeypatch.setattr(pf, "git", lambda root, *a: "")
    monkeypatch.setattr(pf, "changed_lines", lambda root: {})
    monkeypatch.setattr(pf, "coverage_step", lambda root, changed, workers: asked.append("coverage") or ({}, {}))
    assert pf.main(["--root", str(tmp_path), "--no-coverage"]) == 0 and asked == []
    assert "coverage of the changed lines" not in capsys.readouterr().out
    assert pf.main(["--root", str(tmp_path)]) == 0 and asked == ["coverage"]
    assert "coverage of the changed lines" in capsys.readouterr().out
    done = Path(__file__).resolve().parents[2].joinpath("Makefile").read_text(encoding="utf-8").split("\ndone:", 1)[1].split("\n\n", 1)[0]
    assert "--no-coverage" in done, "the gate passes it"
