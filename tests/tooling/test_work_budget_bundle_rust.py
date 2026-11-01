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


def test_a_key_counted_by_its_own_name_brings_its_module_and_a_stale_chain_report_is_refused(tmp_path: Path) -> None:
    """The round arbiter's tooling fix on ask:444-T16-field-audit-5: `write@field_ink` names no function, so the ink's module was
    left out of the audit; and a call-chain report older than the engine described a deleted one."""
    import os

    (tmp_path / "l7r").mkdir()
    (tmp_path / "l7r" / "ink.py").write_text('def draw(s):\n    OPS["write@field_ink"] += 1\n')
    (tmp_path / "l7r" / "other.py").write_text("def other():\n    pass\n")
    got = wbb.counted_files(tmp_path, [{"ops": {"write@field_ink": 4}}])
    assert [p.relative_to(tmp_path).as_posix() for p in got] == ["l7r/ink.py"]
    log = tmp_path / "dev" / "perf-log"
    log.mkdir(parents=True)
    (log / "x-fanout-y.txt").write_text("field: 1 calls\n  a\n")
    os.utime(log / "x-fanout-y.txt", (1, 1))
    assert wbb.fanout_section(tmp_path, "field").startswith("STALE: ") and "make perf-fanout STAGES=field" in wbb.fanout_section(tmp_path, "field")
    os.utime(log / "x-fanout-y.txt", None)
    assert wbb.fanout_section(tmp_path, "field").endswith("field: 1 calls\n  a\n")


def test_what_the_stage_s_code_calls_rides_in_the_audit_and_a_call_no_module_defines_is_named(tmp_path: Path) -> None:
    """The round arbiter's tooling fix on ask:444-T16-field-audit-6: audits 4 and 5 found `field_channel` and `rest_basin`, which
    the stage calls, missing from their bundles."""
    pkg = tmp_path / "l7r" / "diagram"
    (pkg / "settlement" / "fields").mkdir(parents=True)
    (pkg / "settlement" / "__init__.py").write_text("from .fields.paddy import rest_basin\n")
    (pkg / "settlement" / "fields" / "__init__.py").write_text("")
    (pkg / "settlement" / "fields" / "paddy.py").write_text("def rest_basin(s):\n    pass\n")
    (pkg / "settlement" / "clipping.py").write_text("class C:\n    def field_channel(self):\n        pass\n")
    (pkg / "helpers.py").write_text("def helper():\n    pass\n")
    stage = pkg / "stage.py"
    stage.write_text(
        "from l7r.diagram.settlement import rest_basin\nfrom l7r.diagram import helpers\n\ndef stage_field(s):\n    rest_basin(s)\n    helpers.helper()\n    s.field_channel()\n    s.items.append(1)\n"
    )
    got, missing = wbb.called_files(tmp_path, [stage])
    assert sorted(p.relative_to(tmp_path).as_posix() for p in got) == [
        "l7r/diagram/helpers.py",
        "l7r/diagram/settlement/clipping.py",
        "l7r/diagram/settlement/fields/paddy.py",
    ]
    assert missing == []
    stage.write_text("from l7r.diagram.helpers import gone\n\ndef stage_field(s):\n    gone()\n")
    assert wbb.called_files(tmp_path, [stage])[1] == ["gone (from l7r.diagram.helpers, called in l7r/diagram/stage.py)"]
