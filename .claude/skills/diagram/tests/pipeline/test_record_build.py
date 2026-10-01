"""Feature 301 FR-010 / SC-005: render-sync builds the record's site on the main checkout when a fragment, an asset or
the build's own code changed - and skips it when nothing the record is built from changed."""

from __future__ import annotations

import os
import pathlib

import pytest

from l7r.diagram.interactive.sources import RESEARCH_DIR
from l7r.diagram.pipeline import record_build as rb

SKILL = os.path.dirname(RESEARCH_DIR)


def _skill(tmp_path: pathlib.Path) -> pathlib.Path:
    """A skill with a small record: a fragment, an asset, built outputs of both eras, prose, and two engine modules."""
    rec = tmp_path / "research"
    for d in ("water", "assets", "site", "citations", "cities", "cities/fabric", ".site-abc"):
        (rec / d).mkdir(parents=True, exist_ok=True)
    (rec / "water" / "_front.html").write_text("<main>", encoding="utf-8")
    (rec / "water" / "010-ponds.html").write_text('<h2 id="ponds">Ponds</h2>', encoding="utf-8")
    (rec / "cities" / "fabric" / "010-rows.html").write_text('<h2 id="rows">Rows</h2>', encoding="utf-8")
    (rec / "assets" / "record.css").write_text("css", encoding="utf-8")
    (rec / "assets" / "glossary.js").write_text("built", encoding="utf-8")
    (rec / "confusables.json").write_text("[]", encoding="utf-8")
    for built in ("water.html", "SOURCES.html", "cities/fabric.html", "citations/water.html", "site/index.html", ".site-abc/x.html"):
        (rec / built).write_text("built", encoding="utf-8")
    (rec / "CLAUDE.md").write_text("prose", encoding="utf-8")
    (tmp_path / "l7r" / "diagram" / "interactive" / "assets").mkdir(parents=True)
    (tmp_path / rb._GLOSSARY).write_text("{}", encoding="utf-8")
    for name in ("site.py", "placer.py"):
        (tmp_path / "l7r" / name).write_text(f"# {name}", encoding="utf-8")
    return tmp_path


def test_the_inputs_are_the_fragments_the_assets_and_the_data_and_nothing_built() -> None:
    assert rb.is_input("water/010-ponds.html") and rb.is_input("water/010-ponds.notes.html") and rb.is_input("water/_front.html")
    assert rb.is_input("cities/fabric/010-rows.html") and rb.is_input("assets/site.js") and rb.is_input("confusables.json")
    for built in (
        "water.html",
        "SOURCES.html",
        "cities/fabric.html",
        "rendering/water.html",
        "rendering/cities/sizing.html",
        "citations/water.html",
        "citations/water.js",
        "site/index.html",
        ".site-x/a.html",
        "assets/glossary.js",
        "CLAUDE.md",
    ):
        assert not rb.is_input(built), built


def test_the_record_s_files_are_walked_and_the_built_ones_left_out(tmp_path: pathlib.Path) -> None:
    skill = _skill(tmp_path)
    assert rb.record_files(str(skill / "research")) == [
        "assets/record.css",
        "cities/fabric/010-rows.html",
        "confusables.json",
        "water/010-ponds.html",
        "water/_front.html",
    ]


def test_the_engine_modules_are_what_the_build_imported() -> None:
    mods = rb.engine_modules(SKILL)
    assert any(m.endswith(os.path.join("interactive", "record", "site.py")) for m in mods)
    assert any(m.endswith(os.path.join("interactive", "glossary.py")) for m in mods) or any(m.endswith("sources.py") for m in mods)
    assert all(m.startswith(os.path.join(SKILL, "l7r")) for m in mods)


def test_the_site_is_built_when_an_input_moves_and_only_then(tmp_path: pathlib.Path) -> None:
    """SC-005's three cases, measured: a fragment change rebuilds, a change to the build's code rebuilds, and a change to
    nothing the record is built from - a placer the build does not import, a doc, a built page - does not."""
    skill = _skill(tmp_path)
    built: list[int] = []

    def build(research: str) -> dict[str, str]:
        built.append(1)
        return {"index.html": f"site {len(built)}"}

    mods = [str(skill / "l7r" / "site.py")]
    assert rb.rebuild_if_stale(str(skill), build=build, modules=mods) is True
    assert (skill / "research" / "site" / "index.html").read_text(encoding="utf-8") == "site 1"
    assert rb.read_stamp(str(skill / "research" / "site")), "the stamp is written beside the site"
    assert rb.rebuild_if_stale(str(skill), build=build, modules=mods) is False, "nothing moved"
    (skill / "l7r" / "placer.py").write_text("# moved", encoding="utf-8")
    (skill / "research" / "CLAUDE.md").write_text("more prose", encoding="utf-8")
    (skill / "research" / "water.html").write_text("a stale built page", encoding="utf-8")
    assert rb.rebuild_if_stale(str(skill), build=build, modules=mods) is False, "nothing the record is built from moved"
    (skill / "research" / "water" / "010-ponds.html").write_text('<h2 id="ponds">Ponds, dug</h2>', encoding="utf-8")
    assert rb.rebuild_if_stale(str(skill), build=build, modules=mods) is True, "a fragment moved"
    (skill / "l7r" / "site.py").write_text("# the build changed", encoding="utf-8")
    assert rb.rebuild_if_stale(str(skill), build=build, modules=mods) is True, "the build's code moved"
    assert len(built) == 3


def test_a_missing_input_or_stamp_is_read_as_absent(tmp_path: pathlib.Path) -> None:
    assert rb.read_stamp(str(tmp_path / "nowhere")) == ""
    skill = _skill(tmp_path)
    (skill / rb._GLOSSARY).unlink()
    assert rb.fingerprint(str(skill), modules=[]) != rb.fingerprint(str(skill), modules=[str(skill / "l7r" / "site.py")])


def test_render_sync_builds_the_record_where_there_is_one(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:  # noqa: ANN001
    from l7r.diagram.pipeline import render_cache as rc

    skill = tmp_path / "skill"
    (skill / "pool").mkdir(parents=True)
    (skill / "research" / "sources").mkdir(parents=True)
    monkeypatch.setattr(rc, "regen_pool", lambda *a, **k: ([], [], []))
    monkeypatch.setattr(rc.pool_index, "write_index", lambda d: os.path.join(d, "pool", "index.html"))
    calls: list[bool] = [True, False]
    monkeypatch.setattr(rc.record_build, "rebuild_if_stale", lambda d: calls.pop(0))
    assert rc.main(["--main-repo", str(tmp_path), "--skill-dir", str(skill)]) == 0
    assert "the record's site" not in capsys.readouterr().out, "a tree with no record builds none"
    (skill / "research" / "sources" / "_front.html").write_text("x", encoding="utf-8")
    assert rc.main(["--main-repo", str(tmp_path), "--skill-dir", str(skill)]) == 0
    assert "the record's site rebuilt" in capsys.readouterr().out
    assert rc.main(["--main-repo", str(tmp_path), "--skill-dir", str(skill)]) == 0
    assert "the record's site fresh" in capsys.readouterr().out
