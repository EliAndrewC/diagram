"""The preloaded C-library recorder and the traced guard suites (feature 383 amendment 3, plans D26 and D27)."""

from __future__ import annotations

import hashlib
import importlib.util
import pathlib
import shutil
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SRC = REPO / "tests" / "tooling" / "_deps_site" / "l7r_file_log.c"


def _load(name: str, path: pathlib.Path):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ht = _load("_hooktrace", REPO / "tests" / "hooks" / "hooktrace.py")


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
        got = _run(shim, root, tmp_path / "y.log", f"git status >/dev/null; cp -r scripts {fixture}/; cat {fixture}/scripts/s.sh >/dev/null; ls {fixture}/scripts >/dev/null", L7R_TEST_DEP_SKIP="cp", L7R_TEST_DEP_MAP="scripts")
    finally:
        shutil.rmtree(fixture, ignore_errors=True)
    assert ("c-git", "ROOT/.git") in {(k, p if not p.startswith("ROOT/.git") else "ROOT/.git") for k, p in got}, "git on the repository is noted, not followed"
    assert ("c-file", "ROOT/scripts/s.sh") in got, "the fixture's copy is read as the repository's file"
    assert sum(1 for k, p in got if p == "ROOT/scripts/s.sh") == 1, "cp's own read of the source is not counted"
    assert ("c-dir", "ROOT/scripts") in got, "the copy's top directory listed: a file added to scripts/ re-runs the suite (plan review round 5)"


def test_a_suite_s_reads_are_kept_and_judged_by_content(tmp_path: pathlib.Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "a.sh").write_text("one\n")
    gitdir = tmp_path / "gitdir"
    log = tmp_path / "suite.reads"
    log.write_text(f"g\tc-file\t{root}/a.sh\ng\tc-dir\t{root}\n")
    ht.stamp(gitdir, "g-hooks.sh", log, root)
    assert ht.fresh(gitdir, root, ["g-hooks.sh", "other.sh"]) == ["g-hooks.sh"]
    (root / "a.sh").write_text("two\n")
    assert ht.fresh(gitdir, root, ["g-hooks.sh"]) == [], "a read changed: the suite runs"
    log.write_text(f"g\tc-file\t{root}/a.sh\ng\tc-git\t{root}/.git/HEAD\n")
    ht.stamp(gitdir, "g-hooks.sh", log, root)
    assert not ht.trace_file(gitdir, "g-hooks.sh").exists(), "git read the repository: not traced, hookdeps' key stands"
    assert ht.reads(tmp_path / "absent.log", root) == {"file": set(), "dir": set()}


def test_hookdeps_keys_are_the_recipe_s_own_sha() -> None:
    """`--keys` replaced one `--deps` process per suite; its sha must be the one the recipe computed, so stamps stay valid."""
    hd = REPO / "tests" / "hooks" / "hookdeps.py"
    for guard in ("pair-hooks.sh", "sync-with-main.sh"):
        deps = subprocess.run([sys.executable, str(hd), "--deps", guard], capture_output=True, text=True, check=True).stdout.split()
        h = hashlib.sha256()
        for d in deps:
            p = REPO / d
            if p.is_file():
                h.update(p.read_bytes())
        line = subprocess.run([sys.executable, str(hd), "--keys", guard], capture_output=True, text=True, check=True).stdout.split()
        assert line == [guard, h.hexdigest()[:16]]
