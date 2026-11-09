"""`scripts/gates/l7r-gate.sh` (feature 449 T061): the gate's tool built from its own tree, and failing closed where the guards' wrapper fails open."""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.tooling


def _tree(tmp: pathlib.Path) -> pathlib.Path:
    (tmp / "scripts/gates").mkdir(parents=True)
    shutil.copy(REPO / "scripts/gates/l7r-gate.sh", tmp / "scripts/gates/")
    (tmp / "rust/gate/src").mkdir(parents=True)
    (tmp / "rust/gate/src/lib.rs").write_text("// x\n")
    (tmp / "rust/Cargo.toml").write_text("[workspace]\n")
    return tmp


def _cargo(tmp: pathlib.Path, body: str) -> str:
    path = tmp / "fake-cargo"
    path.write_text(f"#!/bin/bash\necho built >> {tmp}/builds\n{body}\n")
    path.chmod(0o755)
    return str(path)


BUILD_OK = 'mkdir -p "$CARGO_TARGET_DIR/release"; printf \'#!/bin/bash\\necho ran "$@"\\n\' > "$CARGO_TARGET_DIR/release/l7r-gate"; chmod +x "$CARGO_TARGET_DIR/release/l7r-gate"'


def _run(tree: pathlib.Path, target: pathlib.Path, cargo: str, *args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "L7R_GATE_TARGET": str(target), "L7R_GATE_CARGO": cargo}
    return subprocess.run([str(tree / "scripts/gates/l7r-gate.sh"), *args], capture_output=True, text=True, check=False, env=env, stdin=subprocess.DEVNULL)


def _builds(tmp: pathlib.Path) -> int:
    return len((tmp / "builds").read_text().splitlines()) if (tmp / "builds").exists() else 0


def test_it_builds_once_and_runs_the_binary_then_rebuilds_when_a_source_moves(tmp_path: pathlib.Path) -> None:
    tree, target = _tree(tmp_path / "t"), tmp_path / "target"
    cargo = _cargo(tmp_path, BUILD_OK)
    done = _run(tree, target, cargo, "plan", "x")
    assert done.returncode == 0 and done.stdout.strip() == "ran plan x" and _builds(tmp_path) == 1
    assert _run(tree, target, cargo, "plan").returncode == 0 and _builds(tmp_path) == 1, "fresh: no build"
    binary = target / "release/l7r-gate"
    os.utime(tree / "rust/gate/src/lib.rs", (binary.stat().st_mtime + 10, binary.stat().st_mtime + 10))
    assert _run(tree, target, cargo, "plan").returncode == 0 and _builds(tmp_path) == 2, "a source newer than the binary"


def test_a_build_that_fails_fails_the_gate_rather_than_passing_it(tmp_path: pathlib.Path) -> None:
    tree, target = _tree(tmp_path / "t"), tmp_path / "target"
    done = _run(tree, target, _cargo(tmp_path, "exit 1"), "plan")
    assert done.returncode == 1 and "the build failed" in done.stderr and not done.stdout
