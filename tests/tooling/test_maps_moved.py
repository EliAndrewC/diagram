"""`maps_moved.py`: which pool manifests differ from HEAD (feature 429 FR-004, SC-004)."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

from tests._scripts import script

pytestmark = pytest.mark.tooling

_spec = importlib.util.spec_from_file_location("maps_moved", script("maps_moved.py"))
assert _spec and _spec.loader
mm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mm)


def _repo(tmp_path: Path) -> Path:
    def git(*a: str) -> None:
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True, capture_output=True)

    git("init", "-q")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    for m in ("sawada", "inashiro"):
        d = tmp_path / "pool" / "hamlets" / m
        d.mkdir(parents=True)
        (d / f"{m}.json").write_text('{"board": 0}\n')
        (d / f"{m}.gen.py").write_text("# gen\n")
    git("add", ".")
    git("commit", "-qm", "a")
    return tmp_path


def test_names_exactly_the_changed_manifest(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "pool/hamlets/sawada/sawada.json").write_text('{"board": 76.4}\n')
    assert mm.moved(root) == ["pool/hamlets/sawada/sawada.json"]


def test_nothing_moved_says_so(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _repo(tmp_path)
    assert mm.main(["--root", str(root)]) == 0
    assert "no pool manifest moved against HEAD" in capsys.readouterr().out


def test_only_reads_one_map_from_its_gen(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _repo(tmp_path)
    (root / "pool/hamlets/sawada/sawada.json").write_text('{"board": 76.4}\n')
    assert mm.moved(root, "pool/hamlets/inashiro/inashiro.gen.py") == []
    assert mm.moved(root, "pool/hamlets/sawada/sawada.gen.py") == ["pool/hamlets/sawada/sawada.json"]
    mm.main(["--root", str(root), "--only", "pool/hamlets/inashiro/inashiro.gen.py"])
    assert "this map's manifest is unchanged against HEAD" in capsys.readouterr().out


def test_an_untracked_manifest_counts_as_moved(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    d = root / "pool/hamlets/kuwabata"
    d.mkdir()
    (d / "kuwabata.json").write_text("{}\n")
    assert mm.moved(root) == ["pool/hamlets/kuwabata/kuwabata.json"]
