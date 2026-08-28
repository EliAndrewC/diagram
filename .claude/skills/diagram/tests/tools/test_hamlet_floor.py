"""The hamlet-path coverage floor (feature 145): the set is DERIVED from roll records, and the floor FIRES."""

from __future__ import annotations

import io
from pathlib import Path

import coverage

from l7r.diagram.tools import hamlet_floor as hf


def _deps(*paths: str) -> dict[str, object]:
    return {"functions": [[str(hf.SKILL / p), "f"] for p in paths], "files": []}


def test_the_set_is_the_union_of_the_records_engine_files_minus_tests_and_ci() -> None:
    records = [
        _deps("l7r/diagram/hamletgen/water.py", "l7r/diagram/settlement/land/cover.py"),
        _deps("l7r/diagram/hamletgen/water.py", "l7r/diagram/check_village/driver.py"),
        _deps("tests/hamletgen/test_water.py", "l7r/diagram/ci/delta.py", "l7r/diagram/tools/../tools/perf_bands.py"),
        {"functions": [["/usr/lib/python3/site-packages/shapely/geometry.py", "g"]], "files": []},
    ]
    assert hf.hamlet_path_files(records) == [
        "l7r/diagram/check_village/driver.py",
        "l7r/diagram/hamletgen/water.py",
        "l7r/diagram/settlement/land/cover.py",
        "l7r/diagram/tools/perf_bands.py",
    ]


def test_module_set_asks_the_records_for_every_fixed_subject() -> None:
    seen: list[str] = []

    def deps_for(spec: object) -> dict[str, object]:
        seen.append(getattr(spec, "name", "?"))
        return _deps("l7r/diagram/hamletgen/plan.py")

    assert hf.module_set(deps_for) == ["l7r/diagram/hamletgen/plan.py"]
    assert seen[0] == "Inashiro" and seen.count("Polder") == 3 and len(seen) == 8  # reference, three polders, cohort 41-44


def _measure(tmp_path: Path, body: str, call: str) -> tuple[str, str]:
    """A module in tmp_path measured by coverage: returns (module path, data file)."""
    mod = tmp_path / "floor_probe.py"
    mod.write_text(body, encoding="utf-8")
    data = str(tmp_path / ".cov")
    cov = coverage.Coverage(data_file=data, config_file=False, source=[str(tmp_path)])  # not the skill's pyproject source list - the probe lives in tmp_path
    cov.start()
    ns: dict[str, object] = {}
    exec(compile(mod.read_text(encoding="utf-8"), str(mod), "exec"), ns)  # noqa: S102 - a fixture module of two lines
    exec(call, ns)  # noqa: S102
    cov.stop()
    cov.save()
    return str(mod), data


BODY = "def f(x):\n    if x:\n        return 1\n    return 2\n"


def test_the_floor_FIRES_on_a_module_in_the_set_with_a_missed_line(tmp_path: Path, monkeypatch: object) -> None:
    mod, data = _measure(tmp_path, BODY, "f(True)")  # `return 2` never runs
    out = io.StringIO()
    rel = str(Path(mod).resolve())
    # `check` joins the set onto SKILL; hand it an absolute path by making SKILL the root for this call
    monkeypatch.setattr(hf, "SKILL", Path("/"))  # type: ignore[attr-defined]
    assert hf.check([rel.lstrip("/")], data_file=data, out=out) == 1
    assert "floor_probe.py" in out.getvalue() and "HAMLET PATH" in out.getvalue()


def test_the_floor_is_quiet_when_the_set_is_covered_and_ignores_modules_outside_it(tmp_path: Path, monkeypatch: object) -> None:
    mod, data = _measure(tmp_path, BODY, "f(True); f(False)")
    other = tmp_path / "city_only.py"
    other.write_text("def g():\n    return 0\n", encoding="utf-8")  # never executed, never in the set
    monkeypatch.setattr(hf, "SKILL", Path("/"))  # type: ignore[attr-defined]
    out = io.StringIO()
    assert hf.check([str(Path(mod).resolve()).lstrip("/")], data_file=data, out=out) == 0
    assert "city_only" not in out.getvalue()


def test_an_empty_set_is_refused_not_defaulted() -> None:
    out = io.StringIO()
    assert hf.check([], data_file="/nonexistent", out=out) == 2
    assert "make reference" in out.getvalue()


def test_main_lists_and_checks(tmp_path: Path, monkeypatch: object) -> None:
    monkeypatch.setattr(hf, "module_set", lambda deps_for=None: ["l7r/diagram/hamletgen/plan.py"])  # type: ignore[attr-defined]
    monkeypatch.setattr(hf, "check", lambda files, data_file, out=None: 7)  # type: ignore[attr-defined]
    assert hf.main(["--list"]) == 0
    assert hf.main(["--data", str(tmp_path / "x")]) == 7
    monkeypatch.setattr(hf, "module_set", lambda deps_for=None: [])  # type: ignore[attr-defined]
    assert hf.main(["--list"]) == 2


def test_module_set_defaults_to_the_roll_cache_records(monkeypatch: object) -> None:
    from l7r.diagram.pipeline import rollcache

    monkeypatch.setattr(rollcache, "report_deps", lambda spec: _deps("l7r/diagram/hamletgen/sink.py"))  # type: ignore[attr-defined]
    assert hf.module_set() == ["l7r/diagram/hamletgen/sink.py"]
