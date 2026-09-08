"""`tools/roll_audit.py` (feature 216): per rolling context, the engine lines nothing else reaches - on a synthetic
coverage database with contexts, so the arithmetic is checked rather than eyeballed."""

from __future__ import annotations

import io
from pathlib import Path

import coverage
import pytest

from l7r.diagram.tools import roll_audit

pytestmark = pytest.mark.tooling

ENGINE = "/repo/.claude/skills/diagram/l7r/diagram"


def _db(tmp_path: Path) -> Path:
    path = tmp_path / ".coverage"
    data = coverage.CoverageData(basename=str(path))
    # two rolls: A reaches sink.py 1-2100 (2100 lines), B reaches sink.py 1-2000 plus water.py 1-50; a unit test covers water.py 1-10
    with_lines = [
        ("fixture:tests/gate/a.py::rolled", {f"{ENGINE}/hamletgen/sink.py": list(range(1, 2101))}),
        ("tests/gate/b.py::t|run", {f"{ENGINE}/hamletgen/sink.py": list(range(1, 2001)), f"{ENGINE}/hamletgen/water.py": list(range(1, 51))}),
        ("tests/unit/test_w.py::t|run", {f"{ENGINE}/hamletgen/water.py": list(range(1, 11)), "/repo/.claude/skills/diagram/tests/unit/test_w.py": [1, 2]}),
        ("", {f"{ENGINE}/hamletgen/plan.py": list(range(1, 100))}),
    ]
    for ctx, lines in with_lines:
        data.set_context(ctx)
        data.add_lines(lines)
    data.write()
    return path


def test_unique_lines_are_the_ones_no_other_context_reaches(tmp_path: Path) -> None:
    by_ctx = roll_audit.read_contexts(_db(tmp_path))
    assert "tests/unit/test_w.py::t|run" in by_ctx and all("/tests/" not in f for lines in by_ctx.values() for f, _ in lines), "test files are never engine lines"
    rows = roll_audit.unique_lines(by_ctx, min_lines=2000)
    assert [ctx for ctx, _t, _u in rows] == ["fixture:tests/gate/a.py::rolled", "tests/gate/b.py::t|run"], "sorted by unique count; the unit test and the import-time context are not rolls"
    a, b = rows
    assert a[1] == 2100 and len(a[2]) == 100 and all(f == "hamletgen/sink.py" for f, _ in a[2]), "A alone reaches sink.py 2001-2100"
    assert b[1] == 2050 and len(b[2]) == 40 and all(f == "hamletgen/water.py" for f, _ in b[2]), "B alone reaches water.py 11-50: 1-10 are the unit test's too"
    text = roll_audit.report(rows, 2000)
    assert "2 rolling context(s)" in text and "  100 unique of   2100" in text and "hamletgen/water.py:40" in text


def test_a_higher_min_lines_is_the_tier_knob_and_all_covered_says_so(tmp_path: Path) -> None:
    by_ctx = roll_audit.read_contexts(_db(tmp_path))
    assert roll_audit.unique_lines(by_ctx, min_lines=2150) == [], "at 2,150 neither roll (2,100 and 2,050 lines) qualifies"
    only_a = roll_audit.unique_lines({k: v for k, v in by_ctx.items() if k.startswith("fixture:")} | {"x|run": by_ctx["fixture:tests/gate/a.py::rolled"]}, min_lines=2000)
    assert all(u == [] for _c, _t, u in only_a) and "nothing here is strictly necessary" in roll_audit.report(only_a, 2000)


def test_main_reads_the_gate_baseline_or_a_named_db_and_says_when_there_is_none(tmp_path: Path) -> None:
    out = io.StringIO()
    assert roll_audit.main(["--db", str(_db(tmp_path)), "--min-lines", "2000"], out=out) == 0
    assert "2 rolling context(s)" in out.getvalue()
    out = io.StringIO()
    assert roll_audit.main([], root=tmp_path / "nowhere", out=out) == 2 and "no baseline" in out.getvalue()
    from l7r.diagram.ci import incremental

    bdir = incremental.baseline_dir(tmp_path)
    bdir.mkdir(parents=True)
    (bdir / incremental.COVERAGE_DB).write_bytes((tmp_path / ".coverage").read_bytes())
    out = io.StringIO()
    assert roll_audit.main([], root=tmp_path, out=out) == 0 and "rolling context" in out.getvalue()


def test_main_finds_the_repository_root_from_its_own_location(monkeypatch: pytest.MonkeyPatch) -> None:
    """With no `--db` and no `root`, `main` walks up from its own file to the repository root - five
    levels, and a wrong depth is silent (it lands one directory short of `.claude/`), so the depth is
    proved by what the resolved root contains."""
    seen: dict[str, Path] = {}

    def fake_baseline(root: Path) -> Path:
        seen["root"] = root
        return root / "no-such-coverage-db"

    monkeypatch.setattr(roll_audit, "baseline_db", fake_baseline)
    out = io.StringIO()
    assert roll_audit.main([], out=out) == 2
    assert (seen["root"] / ".claude" / "skills" / "diagram" / "Makefile").is_file(), seen
    assert "no baseline" in out.getvalue()
