"""`scripts/_clone_local_settings.py` (feature 250, research R4 recommendation 4): a clone does not load the mirror's CLAUDE.md.

WHAT THESE PROVE. In a clone the local settings gain the exclusion naming the MIRROR's root CLAUDE.md - once, keeping
every other key; the mirror itself is never touched (its CLAUDE.md is its only copy); and a local settings file that is
not JSON is reported and left as it was, never overwritten.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_clone_local_settings", REPO / "scripts" / "_clone_local_settings.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cls = _load()


def test_a_clone_excludes_the_mirror_copy_once_and_keeps_its_other_keys(tmp_path: pathlib.Path) -> None:
    clone = tmp_path / "diagram" / ".clones" / "diagram-research"
    (clone / ".claude").mkdir(parents=True)
    (clone / ".claude" / "settings.local.json").write_text('{"permissions": {"allow": ["Bash(ls)"]}}', encoding="utf-8")
    said = cls.ensure(clone)
    data = json.loads((clone / ".claude" / "settings.local.json").read_text(encoding="utf-8"))
    assert data["claudeMdExcludes"] == [str(tmp_path / "diagram" / "CLAUDE.md")] and data["permissions"]["allow"] == ["Bash(ls)"]
    assert "next session" in said
    assert cls.ensure(clone) == "", "a second run changes nothing"


def test_the_mirror_is_never_touched(tmp_path: pathlib.Path) -> None:
    mirror = tmp_path / "diagram"
    mirror.mkdir()
    assert cls.ensure(mirror) == "" and not (mirror / ".claude").exists()


def test_a_file_that_is_not_json_is_left_alone(tmp_path: pathlib.Path) -> None:
    clone = tmp_path / "d" / ".clones" / "x"
    (clone / ".claude").mkdir(parents=True)
    (clone / ".claude" / "settings.local.json").write_text("{not json", encoding="utf-8")
    assert "not JSON" in cls.ensure(clone)
    assert (clone / ".claude" / "settings.local.json").read_text(encoding="utf-8") == "{not json"
