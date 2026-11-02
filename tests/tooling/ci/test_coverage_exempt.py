"""`l7r/diagram/ci/coverage_exempt.py` (feature 448; the GM 2026-11-02): the engine code the Rust port replaces is exempt from
the coverage floor, its unrun lines reported as information; everything else keeps 100%; a stale entry refuses with its cure."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from l7r.diagram.ci import coverage_exempt as ce

pytestmark = pytest.mark.tooling


def _repo(tmp_path: Path, entries: list[dict], budgets: dict | None = None) -> Path:
    (tmp_path / "dev").mkdir()
    (tmp_path / "dev" / "coverage-exempt.json").write_text(json.dumps({"ruling": ce.RULING, "entries": entries}), encoding="utf-8")
    if budgets is not None:
        (tmp_path / "dev" / "work-budget.json").write_text(json.dumps({"stages": budgets}), encoding="utf-8")
    return tmp_path


def _file(root: Path, rel: str, text: str = "x = 1\n") -> str:
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")
    return rel


def _entry(path: str, *stages: str) -> dict:
    return {"path": path, "stages": list(stages), "why": "test"}


def test_a_path_the_record_does_not_name_is_not_exempt(tmp_path: Path) -> None:
    root = _repo(tmp_path, [_entry(_file(tmp_path, "l7r/slated.py"), "sink")])
    _file(root, "l7r/kept.py")
    assert ce.exempt(root) == {"l7r/slated.py"}
    assert ce.omit_arg(root) == "--omit=l7r/slated.py"


def test_no_record_exempts_nothing(tmp_path: Path) -> None:
    assert ce.exempt(tmp_path) == set() and ce.omit_arg(tmp_path) == ""
    assert ce.accepted(tmp_path) == set()


def test_a_gone_path_is_stale_and_refuses_naming_the_cure(tmp_path: Path) -> None:
    root = _repo(tmp_path, [_entry("l7r/gone.py", "sink")])
    out = io.StringIO()
    assert ce.report(root, lambda _p: [], out) == 1
    assert "l7r/gone.py" in out.getvalue() and "the file is gone" in out.getvalue() and ce.CURE in out.getvalue()
    assert ce.exempt(root) == set(), "a stale entry's floor returns at once"


def test_an_entry_whose_every_stage_is_accepted_is_stale_one_with_a_stage_left_is_live(tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        [_entry(_file(tmp_path, "l7r/door.py"), "field"), _entry(_file(tmp_path, "l7r/shared.py"), "field", "sink")],
        {"field": {"status": "accepted"}, "sink": {"status": "budgeted"}},
    )
    live, stale = ce.split(root)
    assert [e["path"] for e in live] == ["l7r/shared.py"]
    assert [e["path"] for e, _ in stale] == ["l7r/door.py"] and "accepted in Rust" in stale[0][1]


def test_prune_drops_the_stale_entries_and_keeps_the_rest(tmp_path: Path) -> None:
    root = _repo(tmp_path, [_entry("l7r/gone.py", "sink"), _entry(_file(tmp_path, "l7r/live.py"), "sink")])
    out = io.StringIO()
    assert ce.prune(root, out) == 1 and "dropped l7r/gone.py" in out.getvalue()
    assert [e["path"] for e in ce.load(root)["entries"]] == ["l7r/live.py"]
    assert ce.report(root, lambda _p: [], io.StringIO()) == 0


def test_report_names_the_exempt_files_unrun_lines_as_information(tmp_path: Path) -> None:
    root = _repo(tmp_path, [_entry(_file(tmp_path, "l7r/a.py"), "sink"), _entry(_file(tmp_path, "l7r/b.py"), "sink")])
    out = io.StringIO()
    assert ce.report(root, lambda p: [3, 4, 5, 9] if p == "l7r/a.py" else [], out) == 0
    text = out.getvalue()
    assert "information" in text and "l7r/a.py - unrun lines: 3-5, 9" in text and "l7r/b.py -" not in text
    assert "2 files slated" in text and "1 with unrun lines" in text


def test_seeded_takes_each_unaccepted_stages_own_python_with_every_stage_it_serves(tmp_path: Path) -> None:
    root = _repo(tmp_path, [], {"water_frame": {"status": "accepted"}, "seat": {}, "track": {}})
    own = {
        "water_frame": [root / "l7r/w.py"],
        "seat": [root / "l7r/ways/a.py", root / "rust/x.rs"],
        "track": [root / "l7r/ways/a.py"],
    }
    record = ce.seeded(root, ["water_frame", "seat", "track"], lambda _r, s: own[s], dead=["l7r/dead.py", "l7r/ways/a.py"])
    assert record["ruling"] == ce.RULING
    assert [(e["path"], e["stages"]) for e in record["entries"]] == [("l7r/dead.py", []), ("l7r/ways/a.py", ["seat", "track"])]
    assert "seat, track" in record["entries"][1]["why"] and "whole-engine" in record["entries"][0]["why"]


def test_a_whole_engine_entry_goes_stale_only_when_its_file_is_gone(tmp_path: Path) -> None:
    root = _repo(tmp_path, [_entry(_file(tmp_path, "l7r/dead.py"))], {"sink": {"status": "accepted"}})
    assert ce.exempt(root) == {"l7r/dead.py"}
    (root / "l7r/dead.py").unlink()
    assert ce.exempt(root) == set()


def test_the_cli_lists_and_prunes_the_real_record_shape(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _repo(tmp_path, [_entry("l7r/gone.py", "sink"), _entry(_file(tmp_path, "l7r/live.py"), "sink")])
    monkeypatch.setattr(ce, "ROOT", root)
    out = io.StringIO()
    assert ce.main(["list"], out) == 0
    assert "STALE l7r/gone.py" in out.getvalue() and "1 exempt, 1 stale" in out.getvalue()
    out = io.StringIO()
    assert ce.main(["list", "--prune"], out) == 0 and "1 exempt, 0 stale" in out.getvalue()
    out = io.StringIO()
    assert ce.main(["omit"], out) == 0 and out.getvalue().strip() == "--omit=l7r/live.py"


BRANCHY = "def f(x):\n    if x:\n        return 1\n    return 2\n\nf(1)\n"  # line 4 unrun
STRAIGHT = "def f(x):\n    return 1\n\nf(1)\n"


def _measure(root: Path, kept: str) -> None:
    """Coverage data over a slated module with one unrun line, and a kept one."""
    _file(root, "l7r/slated.py", BRANCHY)
    _file(root, "l7r/kept.py", kept)
    _file(root, "run.py", "import sys\nsys.path.insert(0, 'l7r')\nimport slated, kept\n")
    subprocess.run([sys.executable, "-m", "coverage", "run", "--rcfile=/dev/null", "--data-file=.coverage", "--source=l7r", "run.py"], cwd=root, check=True)


def _floor(root: Path, omit: str) -> int:
    cmd = [sys.executable, "-m", "coverage", "report", "-m", "--rcfile=/dev/null", "--fail-under=100", *([omit] if omit else [])]
    return subprocess.run(cmd, cwd=root, capture_output=True, text=True).returncode


def test_SC001_an_unrun_line_passes_the_floor_in_a_slated_module_and_fails_it_in_a_kept_one(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _repo(tmp_path, [_entry("l7r/slated.py", "sink")])
    _measure(root, BRANCHY)
    assert _floor(root, ce.omit_arg(root)) != 0, "the kept module's unrun line still fails the floor"
    _measure(root, STRAIGHT)
    assert _floor(root, "") != 0, "without the record, the slated module owes 100% too"
    assert _floor(root, ce.omit_arg(root)) == 0, "the slated module's unrun line alone passes"
    monkeypatch.setattr(ce, "ROOT", root)
    out = io.StringIO()
    assert ce.main(["report"], out) == 0
    assert "l7r/slated.py - unrun lines: 4" in out.getvalue()


def _engine(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        _file(root, rel, text)


def test_a_whole_engine_entry_is_live_while_only_slated_code_reaches_it_and_stale_once_kept_code_does(tmp_path: Path) -> None:
    """D4: the reachability measure - roots are the kept trees, programs and pool/scripts importers; slated files are not walked."""
    _engine(
        tmp_path,
        {
            "l7r/diagram/__init__.py": "",
            "l7r/diagram/tools/__init__.py": "",
            "l7r/diagram/tools/t.py": "from l7r.diagram import pkg\n",
            "l7r/diagram/pkg/__init__.py": "from .inner import shown as shown\n",
            "l7r/diagram/pkg/inner.py": "shown = 1\ntyped: int = 2\n",
            "l7r/diagram/stage.py": "from .dead import f\nfrom . import pkg\n",
            "l7r/diagram/dead.py": "def f():\n    return 1\n",
            "l7r/diagram/prog.py": "import l7r.diagram.stage\nif __name__ == '__main__':\n    pass\n",
            "l7r/diagram/broken.py": "def (\n",
            "pool/m.gen.py": "from l7r.diagram.pkg import shown\n",
            "scripts/s.py": "import os\n",
        },
    )
    root = _repo(tmp_path, [_entry("l7r/diagram/stage.py", "sink"), _entry("l7r/diagram/dead.py")])
    imports, roots = ce.import_graph(root)
    assert "l7r/diagram/tools/t.py" in roots and "l7r/diagram/prog.py" in roots and "pool/m.gen.py" in roots and "scripts/s.py" not in roots
    assert imports["pool/m.gen.py"] == {"l7r/diagram/pkg/inner.py"}, "a name the package re-exports resolves to the module defining it"
    assert ce._top_names(__import__("ast").parse("typed: int = 2\n")) == {"typed"}, "an annotated name is a definition too"
    assert imports["l7r/diagram/stage.py"] == {"l7r/diagram/dead.py", "l7r/diagram/pkg/__init__.py"}
    assert [e["path"] for e in ce.split(root, reach=True)[0]] == ["l7r/diagram/stage.py", "l7r/diagram/dead.py"]
    (root / "l7r/diagram/tools/t.py").write_text("from l7r.diagram.dead import f\n", encoding="utf-8")
    live, stale = ce.split(root, reach=True)
    assert [e["path"] for e, _ in stale] == ["l7r/diagram/dead.py"] and "stays Python now imports it" in stale[0][1]
    assert ce.split(root)[1] == [], "the floor's omit does not walk the graph; the report and the landing refuse"
