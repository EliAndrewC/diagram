"""`make figures` (feature 239 section C): it re-runs each recorded measurement and fails a moved count. The spec lint's own cases are `rust/gate/src/checks/spec_lint/tests.rs`."""

from __future__ import annotations

import importlib.util
import json as _json
import pathlib

import _pytest.monkeypatch

REPO = pathlib.Path(__file__).resolve().parents[2]
_figs5 = importlib.util.spec_from_file_location("figures_cli", REPO / "scripts/measure/figures.py")
assert _figs5 and _figs5.loader
figures_cli = importlib.util.module_from_spec(_figs5)
_figs5.loader.exec_module(figures_cli)


def _measured(tmp_path: pathlib.Path, spec_body: str, entries: dict) -> pathlib.Path:
    d = tmp_path / "specs" / "239-a-feature"
    d.mkdir(parents=True, exist_ok=True)
    (d / "spec.md").write_text(spec_body)
    (d / "measurements.json").write_text(_json.dumps(entries))
    return d


def test_make_figures_fails_a_moved_count_and_reports_a_timing() -> None:
    """FR-011d: only a moved COUNT fails; a timing outside its band is reported, never failed."""
    recorded = {"n": {"value": 560, "unit": "commands"}, "t": {"value": 100.0, "unit": "ms", "varies": True}, "near": {"value": 100.0, "unit": "ms", "varies": 0.25}}
    fresh = {"n": {"value": 561}, "t": {"value": 130.0}, "near": {"value": 120.0}}
    failures, reports = figures_cli.compare(recorded, fresh)
    assert len(failures) == 1 and "`n`" in failures[0]
    assert len(reports) == 1 and "`t`" in reports[0]  # 30% > 10%; `near` is 20% inside its 25%


def test_make_figures_restores_what_it_re_measures(tmp_path: pathlib.Path, monkeypatch: _pytest.MonkeyPatch) -> None:
    """Plan P4: it reports, it never records - the original file comes back whatever the command wrote."""
    d = tmp_path / "specs" / "239-x"
    d.mkdir(parents=True)
    path = d / "measurements.json"
    script = tmp_path / "harness.py"
    script.write_text(f"import json; p = {str(path)!r}; d = json.load(open(p)); d['n']['value'] = 999; json.dump(d, open(p, 'w'))\n")
    original = _json.dumps({"n": {"value": 560, "unit": "commands", "command": f"python3 {script}"}})
    path.write_text(original)
    monkeypatch.setattr(figures_cli, "ROOT", tmp_path)
    failures, _, _ = figures_cli.rerun(d)
    assert failures and path.read_text() == original


def test_make_figures_resolves_a_relative_spec_from_anywhere(tmp_path: pathlib.Path, monkeypatch: _pytest.MonkeyPatch) -> None:
    """`make figures SPEC=specs/...` runs from the skill directory; the relative path must still be found."""
    (tmp_path / "specs" / "240-x").mkdir(parents=True)
    monkeypatch.setattr(figures_cli, "ROOT", tmp_path)
    monkeypatch.chdir(tmp_path / "specs")
    assert figures_cli.resolve("specs/240-x") == tmp_path / "specs" / "240-x"


def test_make_figures_refuses_a_named_spec_it_cannot_re_run(tmp_path: pathlib.Path, monkeypatch: _pytest.MonkeyPatch, capsys: _pytest.CaptureFixture[str]) -> None:
    """Found by feature 240's review: it exited 0 with nothing printed, which reads as every figure reproduced."""
    (tmp_path / "specs" / "240-x").mkdir(parents=True)
    monkeypatch.setattr(figures_cli, "ROOT", tmp_path)
    assert figures_cli.main(["specs/240-x"]) == 1
    assert "nothing was re-run" in capsys.readouterr().err


def test_figures_never_runs_a_command_that_names_a_placeholder(tmp_path: pathlib.Path) -> None:
    """2026-10-12: a one-shot's command, "make perf LABEL=timing-<tree> in each worktree; ...", was split and run - a whole
    perf snapshot, its record labeled with the placeholder - before make refused the words after it."""
    marker = tmp_path / "ran"
    d = _measured(tmp_path, "spec\n", {"k": {"value": 1, "unit": "s", "command": f"touch {marker} <tree> in each worktree"}})
    _failures, _reports, skipped = figures_cli.rerun(d)
    assert not marker.exists(), "the command was run"
    assert any("names a <placeholder>" in s for s in skipped)
