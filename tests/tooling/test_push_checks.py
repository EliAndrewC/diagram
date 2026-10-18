"""Feature 383, phase 2 (SC-006): the push's Python checks in one interpreter give what each gives alone.

WHAT THESE PROVE. Every check of the runner's table, run in this process (`run_one`), exits as `python3 <script> <args>`
does and prints the same, on this repository and on a tree seeded to fail it. The runner stops at the first refusal and
prints the shell's `die` line. A self-test that passed is not run again on the same code, and is run again when a module
its check imports changes; a failing one is never kept.
"""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

from tests._scripts import ROOT, script

spec = importlib.util.spec_from_file_location("push_checks", script("push_checks"))
assert spec and spec.loader
pc = importlib.util.module_from_spec(spec)
sys.modules["push_checks"] = pc
spec.loader.exec_module(pc)


def _alone(path: pathlib.Path, args: list[str], cwd: pathlib.Path) -> tuple[int, str, str]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    p = subprocess.run([sys.executable, str(path), *args], cwd=cwd, capture_output=True, text=True, check=False, env=env)
    return p.returncode, p.stdout, p.stderr


def _inside(path: pathlib.Path, args: list[str], cwd: pathlib.Path, capfd: pytest.CaptureFixture[str]) -> tuple[int, str, str]:
    capfd.readouterr()
    code = pc.run_one(path, args, cwd)
    out, err = capfd.readouterr()
    return code, out, err


def _git(d: pathlib.Path, *a: str) -> None:
    subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True, check=True)


def _tree(tmp: pathlib.Path, files: dict[str, str]) -> pathlib.Path:
    d = tmp / "repo"
    d.mkdir()
    _git(d, "init", "-q")
    shutil.copytree(ROOT / "scripts", d / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(ROOT / "pyproject.toml", d / "pyproject.toml")
    for name, text in files.items():
        (d / name).parent.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(text, encoding="utf-8")
    _git(d, "add", "-A")
    _git(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "seed")
    return d


#: the checks a test runs on this repository - each one's whole-tree run (the self-tests are proven by the stamp tests)
WHOLE_TREE = [c for c in pc.CHECKS if not c[4] and c[0] not in ("spec-lint", "downloads", "gate-stamp", "record", "glossary")]


@pytest.mark.parametrize("name,rel,argv", [(c[0], c[1], c[2]) for c in WHOLE_TREE], ids=[c[0] for c in WHOLE_TREE])
def test_each_check_in_this_process_gives_what_it_gives_alone(name: str, rel: str, argv: tuple[str, ...], capfd: pytest.CaptureFixture[str]) -> None:
    path = ROOT / "scripts" / rel
    args = [a.replace("{root}", str(ROOT)) for a in argv]
    assert _inside(path, args, ROOT, capfd) == _alone(path, args, ROOT), name


SEEDED = {
    "duplicate-defs": ({"l7r/a.py": "def f():\n    return 1\n\n\ndef f():\n    return 2\n"}, "gates/check-duplicate-defs.py", ["."]),
    "conflict": ({"a.md": "<" * 7 + " ours\nx\n" + "=" * 7 + "\ny\n" + ">" * 7 + " theirs\n"}, "hooks/lib/hm_conflict.py", ["--tracked", "."]),
    "function-cap": ({"l7r/a.py": "def f():  # noqa: PLR0915\n    return 1\n"}, "gates/check-function-cap.py", ["."]),
    "stale-dirs": ({"l7r/gone/__pycache__/x.pyc": ""}, "gates/check-stale-dirs.py", ["."]),
}


@pytest.mark.parametrize("name", sorted(SEEDED))
def test_a_check_seeded_to_fail_refuses_the_same_in_this_process(name: str, tmp_path: pathlib.Path, capfd: pytest.CaptureFixture[str]) -> None:
    files, rel, args = SEEDED[name]
    d = _tree(tmp_path, files)
    alone = _alone(d / "scripts" / rel, args, d)
    assert alone[0] != 0, f"the seed did not make {name} fail: {alone}"
    assert _inside(d / "scripts" / rel, args, d, capfd) == alone


def test_the_runner_stops_at_the_first_refusal_with_the_shell_s_line(tmp_path: pathlib.Path, capfd: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("L7R_CACHE_OFF", "1")
    d = _tree(tmp_path, SEEDED["duplicate-defs"][0])
    ran: list[str] = []
    real = pc.run_one
    monkeypatch.setattr(pc, "run_one", lambda s, a, c, quiet=False: ran.append(s.name) or real(s, a, c, quiet))
    assert pc.main([str(d)]) == 1
    err = capfd.readouterr().err
    assert "sync-with-main: duplicate top-level definitions (above)" in err
    assert ran == ["check-duplicate-defs.py", "check-duplicate-defs.py"], "nothing after the refusal ran"
    assert pc.main([str(d), "--skip", "nope"]) == 2


def test_a_passed_self_test_is_kept_until_its_code_or_an_import_changes(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("L7R_CACHE_OFF", raising=False)
    scripts = tmp_path / "scripts"
    (scripts / "gates").mkdir(parents=True)
    (scripts / "record").mkdir()
    shutil.copy(script("record_cache"), scripts / "record" / "record_cache.py")
    (scripts / "gates" / "helper.py").write_text("OK = True\n", encoding="utf-8")
    (scripts / "gates" / "check-x.py").write_text(
        "import pathlib, sys\nsys.path.insert(0, str(pathlib.Path(__file__).parent))\nimport helper\n"
        "log = pathlib.Path(__file__).with_name('ran.log')\nlog.write_text(log.read_text() + 'x' if log.exists() else 'x')\n"
        "sys.exit(0 if helper.OK else 1)\n",
        encoding="utf-8",
    )
    root = tmp_path / "clone"
    root.mkdir()
    _git(root, "init", "-q")
    monkeypatch.setattr(pc, "HERE", scripts / "gates")
    monkeypatch.setattr(pc, "CHECKS", (("x selftest", "gates/check-x.py", ("--selftest",), "x is broken", True, ""),))
    ran = scripts / "gates" / "ran.log"
    assert pc.run(root, set()) == 0 and pc.run(root, set()) == 0
    assert ran.read_text() == "x", "the second push skipped the passed self-test"
    (scripts / "gates" / "helper.py").write_text("OK = False\n", encoding="utf-8")
    sys.modules.pop("helper", None)  # the next push is a new process
    assert pc.run(root, set()) == 1 and pc.run(root, set()) == 1
    assert ran.read_text() == "xxx", "a changed import re-ran it, and a failure is never kept"
    stamps = json.loads((root / ".git" / "l7r-cache" / "selftests.json").read_text(encoding="utf-8"))
    assert list(stamps) == ["gates/check-x.py"]


def test_a_stale_make_targets_page_is_refused_at_the_push(tmp_path: pathlib.Path) -> None:
    """Feature 385 amendment 5 (FR-017): T13 landed a make target by the direct route, which runs no gate, and the stale page
    failed T16's land-tooling a task later. The push runs the gate's own check."""
    entry = next(c for c in pc.CHECKS if c[0] == "make-docs")
    assert entry[1] == "make-docs.py" and entry[2] == ("{root}", "--check") and "make docs" in entry[3]
    (tmp_path / "docs").mkdir()
    (tmp_path / "Makefile").write_text("all:  ## [project] a target\n\t@true\n")
    (tmp_path / "docs" / "make-targets.html").write_text("stale\n")
    page = ROOT / "scripts" / "make-docs.py"
    assert subprocess.run([sys.executable, str(page), str(tmp_path), "--check"], capture_output=True, check=False).returncode != 0
    assert pc.run_one(page, [str(tmp_path), "--check"], tmp_path, quiet=True) != 0, "the push's own runner refuses it too"
