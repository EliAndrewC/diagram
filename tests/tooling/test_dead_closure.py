"""`scripts/measure/dead_closure.py` - what a deletion leaves dead and what it breaks (feature 388, the round arbiter's tooling
fix on hour:388-retire-roll-village@1): both misses of 388's first closure, pinned."""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
from types import ModuleType

import pytest

pytestmark = pytest.mark.tooling

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "measure" / "dead_closure.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("dead_closure", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BASE = {
    "l7r/eng/roll.py": "from .helpers import wrap, only_roll\nfrom .consts import PITCH\n\ndef roll():\n    return wrap() + only_roll() + PITCH\n",
    "l7r/eng/helpers.py": "def wrap():\n    return 1\n\n\ndef only_roll():\n    return 2\n",
    "l7r/eng/consts.py": "PITCH = 92.0\n",
    "l7r/eng/__init__.py": "from .consts import PITCH as PITCH\n",
    "legacy-hand-authored-pool/hamlets/x/x.gen.py": "from l7r.eng.helpers import wrap\nfrom l7r.eng.roll import roll\nwrap()\nroll()\n",
}


def test_a_name_only_the_deleted_code_used_is_newly_dead_and_a_re_export_is_no_use() -> None:
    dc = _load()
    now = {k: v for k, v in BASE.items() if k != "l7r/eng/roll.py"}
    lines = dc.report(BASE, now)
    assert any(ln.startswith("NEWLY DEAD    only_roll ") for ln in lines), lines
    assert any(ln.startswith("NEWLY DEAD    PITCH ") for ln in lines), "the re-export `PITCH as PITCH` keeps nothing alive"
    assert not any(" wrap " in ln and ln.startswith("NEWLY DEAD") for ln in lines), "a frozen exhibit still calls `wrap`"


def test_a_deleted_name_an_exhibit_still_calls_is_named_with_its_caller() -> None:
    dc = _load()
    now = {k: v for k, v in BASE.items() if k != "l7r/eng/roll.py"}
    lines = dc.report(BASE, now)
    assert "STILL CALLED  roll  by legacy-hand-authored-pool/hamlets/x/x.gen.py" in lines, lines
    assert dc.report(BASE, BASE) == [], "no change, nothing to say"


def test_main_reads_the_base_from_git_and_the_tree_from_disk(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    dc = _load()
    for path, src in BASE.items():
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / path).write_text(src, encoding="utf-8")
    git = ["git", "-C", str(tmp_path)]
    subprocess.run([*git, "init", "-q"], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base"], check=True)
    assert dc.main([], tmp_path) == 0
    assert "nothing newly dead" in capsys.readouterr().out
    (tmp_path / "l7r/eng/roll.py").unlink()
    assert dc.main(["--base", "HEAD"], tmp_path) == 0
    out = capsys.readouterr().out
    assert "NEWLY DEAD    only_roll" in out and "STILL CALLED  roll" in out


def test_an_unparseable_source_still_counts_its_names() -> None:
    dc = _load()
    assert dc._tokens('x = "unterminated\n')["x"] == 1
    assert dc._defs("def (:\n", "p") == {}


def test_a_test_pinned_to_a_deleted_file_or_name_is_named() -> None:
    """The round arbiter's tooling fix on red-gate@2026-10-18T20:36:37Z: 388's first red gate was a tooling test asserting
    `"rolling/roll.py" in note` after roll.py went. A string naming a deleted file (short or full path) or name is PINNED."""
    dc = _load()
    base = {"l7r/diagram/eng/roll.py": "def roll():\n    return 1\n", "l7r/diagram/eng/keep.py": "def keep():\n    return 1\n"}
    now = {"l7r/diagram/eng/keep.py": base["l7r/diagram/eng/keep.py"]}
    tests = {
        "tests/t.py": 'def test_x():\n    assert "eng/roll.py" in note\n    # a comment naming roll() is not a pin\n    assert "keep" in note\n',
        "tests/u.py": 'NAMES = ("roll", "other")\n',
        "scripts/s.sh": "echo l7r/diagram/eng/roll.py\n",
    }
    got = dc.pinned(base, now, tests)
    assert "PINNED        eng/roll.py  in tests/t.py:2" in got, got
    assert "PINNED        roll  in tests/u.py:1" in got, "a deleted name inside a string"
    assert any(g.startswith("PINNED        l7r/diagram/eng/roll.py  in scripts/s.sh:1") for g in got), got
    assert not any("tests/t.py:3" in g or "tests/t.py:4" in g for g in got), "comments and live names are not pins"
    assert dc._strings('x = "unterminated\n') == [(1, 'x = "unterminated')]
