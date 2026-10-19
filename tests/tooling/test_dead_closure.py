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


def test_an_island_and_a_class_constant_are_dead_and_a_nested_function_is_no_definition() -> None:
    """The round arbiter's tooling fix on hour:392-retire-the-exhibit-only-engine@1: 392's census missed names that only
    reach each other (citybudget's dataclasses and printer), class constants nothing reads (`_WARD_STROKE`), and read a
    nested function's name (`fit`) as a deleted definition."""
    dc = _load()
    base = {
        "l7r/e/plan.py": "from .budget import Budget, fmt\n\n\ndef plan():\n    return fmt(Budget())\n",
        "l7r/e/budget.py": "class Budget:\n    STROKE = 1.0\n\n\ndef fmt(b):\n    def fit(x):\n        return x\n    return fit(b.STROKE)\n",
        "l7r/e/run.py": "from .plan import plan\nplan()\n",
    }
    now = {**base, "l7r/e/run.py": "", "l7r/e/plan.py": "from .budget import Budget, fmt\n\n\ndef plan():\n    return fmt(Budget())\n"}
    lines = dc.report(base, now)
    dead = {ln.split()[2] for ln in lines if ln.startswith("NEWLY DEAD")}
    assert {"plan", "Budget", "fmt", "STROKE"} <= dead, lines
    assert "fit" not in dead and not any("STILL CALLED  fit" in ln for ln in lines), "a nested function is no one's to call"


def test_the_fixpoint_cuts_the_ring_its_docstring_and_the_re_export_until_a_class_empties(tmp_path: pathlib.Path) -> None:
    dc = _load()
    files = {
        "l7r/e/__init__.py": "from .k import GAP as GAP\nfrom .k import live as live\n",
        "l7r/e/k.py": '# the gap a lane keeps\nGAP = 2.0\n"""Research: lane gap - GUESS"""\n\n\ndef helper():\n    return GAP\n\n\ndef live():\n    return 1\n\n\nclass Mix:\n    def gone_one(self):\n        return helper()\n',
        "l7r/e/use.py": "from .k import live, Mix\nlive()\nMix().gone_one()\n",
    }
    for path, src in files.items():
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / path).write_text(src, encoding="utf-8")
    base = dict(files)
    (tmp_path / "l7r/e/use.py").write_text("from .k import live, Mix\nlive()\nMix\n", encoding="utf-8")
    log = dc.fixpoint(tmp_path, base)
    k = (tmp_path / "l7r/e/k.py").read_text(encoding="utf-8")
    assert "def gone_one" not in k and "def helper" not in k and "GAP = 2.0" not in k, k
    assert "Research: lane gap" not in k and "# the gap a lane keeps" not in k, "a cut constant takes its comment and docstring"
    assert "def live" in k, "a live definition stays"
    assert "GAP as GAP" not in (tmp_path / "l7r/e/__init__.py").read_text(encoding="utf-8"), "the re-export of a cut name goes"
    assert any("a class emptied - stop" in ln for ln in log), log
    assert dc.emptied(base, dc._tree_now(tmp_path)) == ["l7r/e/k.py:Mix"]


def test_what_code_already_unreached_uses_is_not_cut_from_under_it() -> None:
    """392's fixpoint cut `_uf_f` because its live caller went, though a test-only `water_field` (unreached before and
    after, so not this change's to delete) still used it. Code that stays keeps what it uses."""
    dc = _load()
    base = {
        "l7r/e/f.py": "def _uf(x):\n    return x\n\n\ndef paddy():\n    return _uf(1)\n\n\ndef water():\n    return _uf(2)\n",
        "l7r/e/run.py": "from .f import paddy\npaddy()\n",
    }
    now = {**base, "l7r/e/run.py": ""}
    dead = {ln.split()[2] for ln in dc.report(base, now) if ln.startswith("NEWLY DEAD")}
    assert dead == {"paddy"}, dead


def test_the_fixpoint_holds_a_name_assigned_from_a_call(tmp_path: pathlib.Path) -> None:
    """392's fixpoint cut `DIKEPOND_SPLIT = register_knob(...)`: nothing named it, but the call registers a knob read by its
    string. An assignment from a call is held for a hand check, never cut."""
    dc = _load()
    files = {"l7r/e/k.py": "def register(x):\n    return x\n\n\nKNOB = register('split')\nTABLE = {1: 2}\n\n\ndef roll():\n    return TABLE, KNOB\n", "l7r/e/run.py": "from .k import roll\nroll()\n"}
    for path, src in files.items():
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / path).write_text(src, encoding="utf-8")
    (tmp_path / "l7r/e/run.py").write_text("", encoding="utf-8")
    log = dc.fixpoint(tmp_path, dict(files))
    k = (tmp_path / "l7r/e/k.py").read_text(encoding="utf-8")
    assert "KNOB = register" in k and "TABLE" not in k and "def roll" not in k, k
    assert any("HOLDS KNOB" in ln for ln in log), log
