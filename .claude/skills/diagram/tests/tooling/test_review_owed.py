"""`scripts/_review_owed.py` and `scripts/_review_snapshot.py` - the scripted trigger and the reviewer's
snapshot (feature 231).

Every case runs on a real git fixture in `tmp_path`: a repository with both pool trees, an `origin/main`
ref, and manifests moved in each of the ways a session moves one (committed, staged, unstaged, untracked).
No `tooling` marker: these call functions and a subprocess on files, like `test_tick_task.py`.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[5]
SKILL = ".claude/skills/diagram"


def _mod(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), REPO / "scripts" / f"{name}.py")
    assert spec and spec.loader
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


owed = _mod("_review_owed")
snap = _mod("_review_snapshot")


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout.strip()


def _map(root: Path, tree: str, name: str, *, poly: int = 1, renders: bool = False) -> Path:
    d = root / SKILL / tree / f"{name}s" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.json").write_text(json.dumps({"meta": {"name": name}, "houses": [[poly, poly]]}))
    (d / f"{name}.notes.md").write_text(f"# {name}\n")
    if renders:
        (d / f"{name}.svg").write_text("<svg/>")
        (d / f"{name}.png").write_bytes(b"\x89PNG")
        (d / f"{name}.html").write_text("<html></html>")
    return d


@pytest.fixture
def clone(tmp_path: Path) -> Path:
    """A repository with two shipped maps, one per pool tree, and an `origin/main` at that commit."""
    root = tmp_path / "clone"
    root.mkdir()
    git(root.parent, "init", "-q", str(root))
    git(root, "config", "user.email", "t@t")
    git(root, "config", "user.name", "t")
    _map(root, "pool", "inashiro", renders=True)
    _map(root, "legacy-hand-authored-pool", "furu")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "the pool")
    git(root, "update-ref", "refs/remotes/origin/main", git(root, "rev-parse", "HEAD"))
    return root


def test_nothing_moved_owes_no_review(clone: Path) -> None:
    desc, names = owed.changed_maps(clone)
    assert names == []
    assert "no pool manifest moved" in owed.ruling(desc, names)


def test_a_committed_manifest_beyond_the_merge_base_counts(clone: Path) -> None:
    """The case the HEAD~1 diff missed: the manifest moved two commits ago and main has neither."""
    _map(clone, "pool", "inashiro", poly=2, renders=True)
    git(clone, "commit", "-qam", "re-rolled")
    (clone / "a.txt").write_text("something else")
    git(clone, "add", "-A")
    git(clone, "commit", "-qm", "and then other work")
    _desc, names = owed.changed_maps(clone)
    assert names == ["inashiro"]


@pytest.mark.parametrize("stage", [True, False])
def test_an_uncommitted_manifest_counts_staged_or_not(clone: Path, stage: bool) -> None:
    _map(clone, "pool", "inashiro", poly=3, renders=True)
    if stage:
        git(clone, "add", "-A")
    _desc, names = owed.changed_maps(clone)
    assert names == ["inashiro"]


def test_a_new_untracked_map_counts(clone: Path) -> None:
    _map(clone, "pool", "aoi")
    _desc, names = owed.changed_maps(clone)
    assert names == ["aoi"]


def test_the_legacy_tree_counts_too(clone: Path) -> None:
    """A pattern anchored on `pool/` alone would stop matching the frozen tree with nothing turning red."""
    _map(clone, "legacy-hand-authored-pool", "furu", poly=9)
    _desc, names = owed.changed_maps(clone)
    assert names == ["furu"]


def test_a_render_or_a_notes_file_alone_owes_nothing(clone: Path) -> None:
    """The manifest is the layout: a re-rendered SVG or an edited notes file is not a moved settlement."""
    (clone / SKILL / "pool" / "inashiros" / "inashiro" / "inashiro.svg").write_text("<svg>different</svg>")
    (clone / SKILL / "pool" / "inashiros" / "inashiro" / "inashiro.notes.md").write_text("# more notes\n")
    _desc, names = owed.changed_maps(clone)
    assert names == []


def test_engine_code_alone_owes_nothing(clone: Path) -> None:
    """Feature 228's own shape: the drawing code changed, the manifest did not."""
    py = clone / SKILL / "l7r" / "diagram" / "settlement"
    py.mkdir(parents=True)
    (py / "landuse.py").write_text("# the ring\n")
    _desc, names = owed.changed_maps(clone)
    assert names == []


def test_without_origin_main_the_base_is_head(clone: Path) -> None:
    git(clone, "update-ref", "-d", "refs/remotes/origin/main")
    desc, names = owed.changed_maps(clone)
    assert "no origin/main" in desc and names == []


def test_a_repository_with_no_commits_reports_its_maps_as_new(tmp_path: Path) -> None:
    root = tmp_path / "fresh"
    root.mkdir()
    git(tmp_path, "init", "-q", str(root))
    _map(root, "pool", "aoi")
    desc, names = owed.changed_maps(root)
    assert desc == "no commits yet" and names == ["aoi"]


def test_main_returns_names_or_the_ruling(clone: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _map(clone, "pool", "inashiro", poly=4, renders=True)
    assert owed.main(["--root", str(clone)]) == 0
    assert capsys.readouterr().out.split() == ["inashiro"]
    assert owed.main(["--root", str(clone), "--why"]) == 0
    assert "layout moved against" in capsys.readouterr().out


def test_main_refuses_a_directory_that_is_not_a_repository(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert owed.main(["--root", str(tmp_path)]) == 1
    assert "not a git repository" in capsys.readouterr().err


# --- the snapshot ---------------------------------------------------------------------------------


@pytest.fixture
def pair(clone: Path, tmp_path: Path) -> tuple[Path, Path]:
    """(a clone under `<mirror>/.clones/`, the mirror) - the real layout, so the mirror is derived."""
    mirror = tmp_path / "mirror"
    (mirror / ".clones").mkdir(parents=True)
    work = mirror / ".clones" / "session"
    clone.rename(work)
    _map(mirror, "pool", "inashiro", poly=99, renders=True)
    return work, mirror


def test_the_snapshot_takes_both_sides(pair: tuple[Path, Path]) -> None:
    work, mirror = pair
    (rec,) = snap.snapshot(work, mirror, ["inashiro"])
    assert rec["missing"] == [] and rec["main_missing"] == []
    clone_files = sorted(p.name for p in Path(rec["clone"]).iterdir())
    assert clone_files == ["inashiro.html", "inashiro.json", "inashiro.notes.md", "inashiro.png", "inashiro.svg"]
    assert json.loads((Path(rec["main"]) / "inashiro.json").read_text())["houses"] == [[99, 99]]
    assert json.loads((Path(rec["clone"]) / "inashiro.json").read_text())["houses"] == [[1, 1]]


def test_a_missing_render_is_named_never_skipped(pair: tuple[Path, Path]) -> None:
    """The gate's roll cache evicts a map's .png and .html; the reviewer must be told, not left to find out."""
    work, mirror = pair
    d = work / SKILL / "pool" / "inashiros" / "inashiro"
    (d / "inashiro.png").unlink()
    (d / "inashiro.html").unlink()
    (rec,) = snap.snapshot(work, mirror, ["inashiro"])
    assert rec["missing"] == [".png", ".html"]
    assert "missing in the clone: .png .html" in snap.describe(rec)
    assert "make map" in snap.describe(rec)


def test_a_map_in_neither_tree_says_so(pair: tuple[Path, Path]) -> None:
    work, mirror = pair
    (rec,) = snap.snapshot(work, mirror, ["nowhere"])
    assert rec["clone"] is None and "not in the clone's pool" in snap.describe(rec)


def test_a_previous_snapshot_of_the_same_map_is_cleared(pair: tuple[Path, Path]) -> None:
    work, mirror = pair
    snap.snapshot(work, mirror, ["inashiro"])
    stale = work / ".git" / "review-snapshot" / "inashiro" / "clone" / "stale.png"
    stale.write_bytes(b"old")
    snap.snapshot(work, mirror, ["inashiro"])
    assert not stale.exists()


def test_main_derives_the_mirror_from_the_clone_path(pair: tuple[Path, Path], capsys: pytest.CaptureFixture[str]) -> None:
    work, _mirror = pair
    assert snap.main(["--root", str(work), "inashiro"]) == 0
    out = capsys.readouterr().out
    assert "snapshot inashiro:" in out and "/main" in out
    assert json.loads((work / ".git" / "review-snapshot" / "inashiro" / "main" / "inashiro.json").read_text())["houses"] == [[99, 99]]


def test_a_clone_outside_a_mirror_snapshots_its_own_side_only(clone: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert snap.main(["--root", str(clone), "inashiro"]) == 0
    assert "main unavailable" in capsys.readouterr().out
