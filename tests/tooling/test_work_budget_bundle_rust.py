"""The work-budget audit bundle on a Rust phase (feature 444 T17, `dev/rust-tooling.md` "the work-budget audit bundle"): MODE AUDIT
reads the stage's `.rs` modules beside its thin Python function."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from tests._scripts import script

pytestmark = pytest.mark.tooling
_spec = importlib.util.spec_from_file_location("work_budget_bundle", script("work_budget_bundle"))
assert _spec and _spec.loader
wbb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wbb)


def test_a_rust_phase_s_source_rides_beside_its_thin_python_function(tmp_path: Path) -> None:
    ham = tmp_path / "l7r" / "diagram" / "hamletgen"
    ham.mkdir(parents=True)
    (ham / "stages.py").write_text("def stage_field(s):\n    return _phases.stage_field(s)\n")
    mod = tmp_path / "rust" / "phases" / "src" / "field"
    mod.mkdir(parents=True)
    (mod / "mod.rs").write_text("pub fn stage_field() {}\n")
    (mod / "comb.rs").write_text("pub fn cut() {}\n")
    (tmp_path / "rust" / "phases" / "src" / "lib.rs").write_text("mod field;\n")
    got = [p.relative_to(tmp_path).as_posix() for p in wbb.stage_files(tmp_path, "field")]
    assert got == ["l7r/diagram/hamletgen/stages.py", "rust/phases/src/field/comb.rs", "rust/phases/src/field/mod.rs"]
    (tmp_path / "rust" / "phases" / "src" / "frame.rs").write_text("pub(crate) fn stage_frame() {}\n")
    (ham / "stages.py").write_text("def stage_frame(s):\n    pass\n")
    got = [p.relative_to(tmp_path).as_posix() for p in wbb.stage_files(tmp_path, "frame")]
    assert got == ["l7r/diagram/hamletgen/stages.py", "rust/phases/src/frame.rs"], "a file at the crate's src, alone"
    assert wbb.stage_files(tmp_path, "nothing") == []


def test_a_counter_a_rust_function_keeps_brings_its_rs_file_into_the_audit(tmp_path: Path) -> None:
    src = tmp_path / "rust" / "phases" / "src"
    src.mkdir(parents=True)
    (src / "water_frame.rs").write_text("pub fn roll_plan() {}\n")
    (tmp_path / "rust" / "phases" / "target").mkdir()
    (tmp_path / "rust" / "phases" / "target" / "roll.rs").write_text("pub fn roll_plan() {}\n")
    (tmp_path / "l7r").mkdir()
    (tmp_path / "l7r" / "plan.py").write_text("def _rust_rolls():\n    pass\n")
    got = wbb.counted_files(tmp_path, [{"ops": {"candidate@roll_plan": 6, "write@_rust_rolls": 13}}])
    assert [p.relative_to(tmp_path).as_posix() for p in got] == ["l7r/plan.py", "rust/phases/src/water_frame.rs"]
