"""The four AST-scanning tests share ONE parse of the engine, and each still finds its offender (feature 276, FR-001).

`tests/_engine_ast.py` is what they read; this holds the two properties the sharing must not cost: every file is
parsed once however many scans read it, and each scan - fed a planted module of the kind it exists to catch -
reports it.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from tests import _engine_ast, test_memory, test_package_surfaces
from tests.hamletgen import test_driver
from tests.settlement import test_water_ways

SKILL = pathlib.Path(__file__).resolve().parents[1]
ENGINE = SKILL / "l7r" / "diagram"


@pytest.fixture
def fresh(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_engine_ast, "_TREES", {})
    monkeypatch.setattr(_engine_ast, "_WALKS", {})
    monkeypatch.setattr(_engine_ast, "PARSES", 0)


@pytest.mark.xdist_group("engine_ast")  # one worker holds the parsed engine, not five (tests/_heap.py)
def test_the_four_scans_parse_each_file_once(fresh: None, monkeypatch: pytest.MonkeyPatch) -> None:
    reads = []
    real = _engine_ast.engine_modules

    def counted(*a, **k):  # type: ignore[no-untyped-def]
        got = real(*a, **k)
        reads.append(len(got))
        return got

    monkeypatch.setattr(_engine_ast, "engine_modules", counted)
    files = sorted(ENGINE.rglob("*.py"))
    test_memory.heavy_import_offenders(_engine_ast.engine_modules(files, test_memory.HEAVY), SKILL)
    test_driver.stage_loops(_engine_ast.engine_modules(files, ("STAGES",)), ENGINE)
    test_water_ways.lane_deletes(_engine_ast.engine_modules(files, ("del",)), ENGINE)
    test_package_surfaces._from_imports()
    assert len(reads) == 4 and sum(reads) > _engine_ast.PARSES, "non-vacuity: the four scans read overlapping files, so sharing had something to share"
    assert len({k[0] for k in _engine_ast._TREES}) == _engine_ast.PARSES, "every file parsed exactly once across the four scans"


def test_a_changed_file_is_parsed_again(fresh: None, tmp_path: pathlib.Path) -> None:
    f = tmp_path / "m.py"
    f.write_text("x = 1\n")
    _engine_ast.parsed(f)
    _engine_ast.parsed(f)
    assert _engine_ast.PARSES == 1
    f.write_text("x = 22\n")  # a different size, so a different key even on a coarse clock
    assert _engine_ast.parsed(f)[0] == "x = 22\n" and _engine_ast.PARSES == 2


def test_a_broken_file_raises_unless_skipping_is_asked_for(tmp_path: pathlib.Path) -> None:
    f = tmp_path / "broken.py"
    f.write_text("def (:\n")
    with pytest.raises(SyntaxError):
        _engine_ast.engine_modules([f])
    assert _engine_ast.engine_modules([f], skip_broken=True) == []


def test_a_needle_skips_only_files_without_it(tmp_path: pathlib.Path) -> None:
    a, b = tmp_path / "a.py", tmp_path / "b.py"
    a.write_text("STAGES = ()\n")
    b.write_text("y = 2\n")
    assert [p.name for p, _s, _t in _engine_ast.engine_modules([a, b], ("STAGES",))] == ["a.py"]


def test_module_level_is_every_node_outside_a_function() -> None:
    tree = ast.parse("import os\nclass C:\n    import sys\n    def f(self):\n        import json\ndef g():\n    import re\n")
    names = {a.name for n in _engine_ast.module_level(tree) if isinstance(n, ast.Import) for a in n.names}
    assert names == {"os", "sys"}


def _planted(tmp_path: pathlib.Path, name: str, text: str) -> list[tuple[pathlib.Path, str, ast.Module]]:
    f = tmp_path / name
    f.write_text(text)
    return _engine_ast.engine_modules([f])


def test_each_scan_still_catches_its_offender(tmp_path: pathlib.Path) -> None:
    heavy = _planted(tmp_path, "heavy.py", "import shapely\ndef f():\n    import numpy\n")
    assert test_memory.heavy_import_offenders(heavy, tmp_path) == ["heavy.py:1"], "a module-level heavy import, and only it"
    loop = _planted(tmp_path, "loop.py", "STAGES = ()\ndef run():\n    for stage in STAGES:\n        stage()\n")
    found, outside, _c = test_driver.stage_loops(loop, tmp_path)
    assert found == ["loop.py:3"] and outside == ["loop.py:3"], "a stage-running loop outside roll_scope()"
    dels = _planted(tmp_path, "dels.py", "def purge(s):\n    del s.M['lanes'][0]\ndef drop_lanes(s):\n    del s.M['lanes'][0]\n")
    assert test_water_ways.lane_deletes(dels, tmp_path) == ["dels.py:2 del s.M['lanes'][0]"], "a lane delete outside drop_lanes"
