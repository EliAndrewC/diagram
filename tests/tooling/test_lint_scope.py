"""The one config root lints the engine and nothing else (feature 329, FR-002a, SC-007).

The project moved from the old skill directory to the repository root, and its `pyproject.toml` with it. Two silent
failures were possible and both are pinned here: the root's old fence (`ruff.toml`, `exclude = ["*"]`) would have
taken precedence over `pyproject.toml` in the same directory and unlinted the whole engine while the gate stayed green;
and without the fence's purpose carried into `extend-exclude`, a root `ruff check --fix .` would rewrite `specs/` and
`scripts/`, which no package has adopted (the 2026-08-17 incident the fence was written for).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LINTED = ("l7r/", "tests/", "wip/")


def _ruff(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "ruff", *args], cwd=cwd, capture_output=True, text=True)


@pytest.mark.tooling
def test_there_is_one_config_root_and_no_fence_file_beside_it() -> None:
    assert (ROOT / "pyproject.toml").is_file()
    assert not (ROOT / "ruff.toml").exists() and not (ROOT / ".ruff.toml").exists(), "a ruff.toml beside pyproject.toml wins and unlints the engine"


@pytest.mark.tooling
def test_a_root_run_reaches_only_the_trees_the_package_owns() -> None:
    files = _ruff("check", "--show-files", ".", cwd=ROOT).stdout.split()
    rel = [str(Path(f).resolve().relative_to(ROOT)) for f in files]
    assert any(r.startswith("l7r/") for r in rel) and any(r.startswith("tests/") for r in rel), "the engine and its tests are linted"
    stray = [r for r in rel if not r.startswith(LINTED) and r != "pyproject.toml"]
    assert not stray, f"a root lint run reaches files no package adopted: {stray[:10]}"


@pytest.mark.tooling
def test_a_seeded_engine_error_fails_and_a_seeded_specs_error_is_ignored(tmp_path: Path) -> None:
    shutil.copyfile(ROOT / "pyproject.toml", tmp_path / "pyproject.toml")
    (tmp_path / "l7r" / "diagram").mkdir(parents=True)
    (tmp_path / "specs" / "001-x").mkdir(parents=True)
    (tmp_path / "l7r" / "diagram" / "seeded.py").write_text("import os\n", encoding="utf-8")
    (tmp_path / "specs" / "001-x" / "seeded.py").write_text("import os\n", encoding="utf-8")
    out = _ruff("check", "--no-fix", ".", cwd=tmp_path)
    assert out.returncode != 0 and "l7r/diagram/seeded.py" in out.stdout, out.stdout + out.stderr
    assert "specs/" not in out.stdout, "the fence must keep a root run out of specs/"


@pytest.mark.tooling
def test_pytest_and_coverage_stay_scoped_at_the_root() -> None:
    cfg = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["tool"]
    assert cfg["pytest"]["ini_options"]["testpaths"] == ["tests"], "without testpaths a root pytest walks every .clones/ checkout"
    assert cfg["coverage"]["run"]["source"] == ["l7r"]
