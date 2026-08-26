"""`make new-check` - the scaffold that writes a check's three conventional pieces (feature 133 T10)."""

import json
from pathlib import Path

import pytest

from l7r.diagram.tools import new_check

_SEG = '''from typing import Any

def _seg_0285_071__yards(*, check: Any = _UNBOUND) -> dict[str, Any]:
    return _kept(locals(), ())


def _seg_0285_990__gardens(*, check: Any = _UNBOUND) -> dict[str, Any]:
    return _kept(locals(), ())
'''

_TEST = '''"""tests"""

from l7r.diagram import check_village
from tests.check_village._builders import (
    _yard,
    f,
    manifest,
)


def test_something():
    assert True
'''


def _tree(tmp_path: Path) -> tuple[Path, Path, Path]:
    seg = tmp_path / "segments_04c.py"
    seg.write_text(_SEG)
    test = tmp_path / "test_segments_04.py"
    test.write_text(_TEST)
    fx = tmp_path / "gate_check_names.json"
    fx.write_text(json.dumps(["alpha", "zulu"], indent=2) + "\n")
    return seg, test, fx


def test_scaffold_writes_segment_fixture_and_test_with_the_next_key(tmp_path):
    seg, test, fx = _tree(tmp_path)
    key = new_check.scaffold("beds_get_sun", seg, test, fx)
    assert key == "0285_991", "one past the file's highest key, so it runs after everything there"
    src = seg.read_text()
    assert "def _seg_0285_991__beds_get_sun(" in src and 'check(\n            "beds_get_sun",' in src
    assert '_kept(locals(), ("beds_get_sun_bad",))' in src, "the literal tuple the registry derivation requires"
    assert json.loads(fx.read_text()) == ["alpha", "beds_get_sun", "zulu"], "the fixture stays sorted"
    tsrc = test.read_text()
    assert "def test_beds_get_sun_fires_and_passes" in tsrc
    assert "    house,\n" in tsrc and "    manifest,\n" in tsrc and "    f,\n" in tsrc, "the builders the stub uses are imported"


def test_scaffold_refuses_a_duplicate_and_a_bad_name(tmp_path):
    seg, test, fx = _tree(tmp_path)
    with pytest.raises(SystemExit, match="already has a segment"):
        new_check.scaffold("gardens", seg, test, fx)
    with pytest.raises(SystemExit, match="snake_case"):
        new_check.scaffold("Bad-Name", seg, test, fx)
    fx.write_text(json.dumps(["taken"]) + "\n")
    with pytest.raises(SystemExit, match="already in"):
        new_check.scaffold("taken", seg, test, fx)


def test_next_key_handles_a_plain_key_and_an_empty_file():
    assert new_check.next_key("def _seg_0533__x(*, a=1):\n    pass\n") == "0533_500"
    with pytest.raises(SystemExit, match="no _seg_"):
        new_check.next_key("nothing here")


def test_ensure_test_imports_adds_a_block_when_none_exists_and_leaves_a_complete_one():
    added = new_check.ensure_test_imports("import x\n")
    assert added.startswith("from tests.check_village._builders import f, house, manifest")
    complete = _TEST.replace("    _yard,\n", "    _yard,\n    house,\n")
    assert new_check.ensure_test_imports(complete) == complete


def test_main_prints_the_next_step(tmp_path, capsys, monkeypatch):
    seg, test, fx = _tree(tmp_path)
    monkeypatch.setattr(new_check, "_FIXTURE", fx)
    assert new_check.main(["--name", "beds_get_sun", "--file", str(seg), "--test", str(test)]) == 0
    out = capsys.readouterr().out
    assert "_seg_0285_991__" in out and "ONE `make quick`" in out
