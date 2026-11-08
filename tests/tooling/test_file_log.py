"""The preloaded C-library recorder and the traced guard suites (feature 383 amendment 3, plans D26 and D27)."""

from __future__ import annotations

import pathlib
import shutil
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SRC = REPO / "tests" / "tooling" / "_deps_site" / "l7r_file_log.c"


@pytest.fixture(scope="module")
def shim(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    if not shutil.which("gcc"):
        pytest.skip("no gcc: the recorder is not built, and every non-Python child stays unknown")
    so = tmp_path_factory.mktemp("shim") / "l7r_file_log.so"
    subprocess.run(["gcc", "-shared", "-fPIC", "-O2", "-o", str(so), str(SRC), "-ldl"], check=True, capture_output=True)
    return so


def _run(shim: pathlib.Path, root: pathlib.Path, log: pathlib.Path, script: str, **extra: str) -> list[tuple[str, str]]:
    env = {"PATH": "/usr/bin:/bin", "LD_PRELOAD": str(shim), "L7R_TEST_DEP_LOG": str(log), "L7R_TEST_DEP_ROOT": str(root), "L7R_TEST_DEP_FILE": "t.py", **extra}
    subprocess.run(["bash", "-c", script], cwd=root, env=env, check=True, capture_output=True)
    lines = log.read_text().splitlines() if log.exists() else []
    return sorted({(ln.split("\t")[1], ln.split("\t")[2].replace(str(root), "ROOT")) for ln in lines})


def test_what_a_program_reads_is_recorded_and_what_it_writes_is_not(shim: pathlib.Path, tmp_path: pathlib.Path) -> None:
    root = tmp_path / "repo"
    (root / "d").mkdir(parents=True)
    (root / "a.txt").write_text("a")
    got = _run(shim, root, tmp_path / "x.log", "cat a.txt >/dev/null; [ -f nope ]; ls d >/dev/null; echo w > out.txt; cat /etc/hostname >/dev/null")
    assert ("c-file", "ROOT/a.txt") in got and ("c-file", "ROOT/nope") in got, "an open and a stat"
    assert ("c-dir", "ROOT/d") in got, "a listing"
    assert not any(p.endswith("out.txt") for _k, p in got), "a write is not a read"
    assert not any("hostname" in p for _k, p in got), "outside the repository: nothing"


def test_git_and_a_skipped_program_are_not_recorded_and_a_fixture_copy_maps_home(shim: pathlib.Path, tmp_path: pathlib.Path) -> None:
    root = tmp_path / "repo"
    (root / "scripts").mkdir(parents=True)
    (root / "scripts" / "s.sh").write_text("echo hi\n")
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    fixture = pathlib.Path(subprocess.run(["mktemp", "-d"], capture_output=True, text=True, check=True).stdout.strip())
    try:
        got = _run(
            shim,
            root,
            tmp_path / "y.log",
            f"git status >/dev/null; cp -r scripts {fixture}/; cat {fixture}/scripts/s.sh >/dev/null; ls {fixture}/scripts >/dev/null",
            L7R_TEST_DEP_SKIP="cp",
            L7R_TEST_DEP_MAP="scripts",
        )
    finally:
        shutil.rmtree(fixture, ignore_errors=True)
    assert ("c-git", "ROOT/.git") in {(k, p if not p.startswith("ROOT/.git") else "ROOT/.git") for k, p in got}, "git on the repository is noted, not followed"
    assert ("c-file", "ROOT/scripts/s.sh") in got, "the fixture's copy is read as the repository's file"
    assert sum(1 for k, p in got if p == "ROOT/scripts/s.sh") == 1, "cp's own read of the source is not counted"
    assert ("c-dir", "ROOT/scripts") in got, "the copy's top directory listed: a file added to scripts/ re-runs the suite (plan review round 5)"
