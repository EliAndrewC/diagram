"""`scripts/gates/gate_lock.py` - one `make done` at a time in a clone (feature 375 follow-up, the GM 2026-10-10).

The "Diagram research" session's second gate, started while its first still ran, failed alongside it and tripped the
red-gate wire twice. The lock refuses a second gate beside a live one, and never holds on a dead one.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from tests.tooling.test_modal_checks import _load

gl = _load("gate_lock")


def test_a_second_gate_beside_a_live_one_is_refused(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    live = subprocess.Popen(["sleep", "30"])
    try:
        monkeypatch.setattr(gl, "cmdline", lambda pid: "make --no-print-directory done FULL=1" if pid == live.pid else "")
        assert gl.acquire(tmp_path, live.pid, 100) == ""
        why = gl.acquire(tmp_path, 4242, 200)
        assert f"already running in this clone (pid {live.pid}" in why
        assert gl.acquire(tmp_path, live.pid, 300) == "", "the owner itself is never refused"
    finally:
        live.kill()
        live.wait()


def test_a_dead_or_unrelated_owner_holds_nothing(tmp_path: Path) -> None:
    dead = subprocess.Popen(["true"])
    dead.wait()
    (tmp_path / gl.LOCK).write_text(json.dumps({"pid": dead.pid, "t": 1}))
    assert gl.acquire(tmp_path, 4242) == "", "a gate that died leaves no lock to clear"
    (tmp_path / gl.LOCK).write_text(json.dumps({"pid": 1, "t": 1}))
    assert gl.acquire(tmp_path, 4242) == "", "a pid now held by some other program is no gate"
    (tmp_path / gl.LOCK).write_text("not json")
    assert gl.acquire(tmp_path, 4242) == ""
    assert json.loads((tmp_path / gl.LOCK).read_text())["pid"] == 4242


def test_the_running_gate_is_read_from_the_process_table_and_the_command_line(tmp_path: Path, capsys) -> None:  # noqa: ANN001
    assert gl.running_gate(999_999_999) is False and gl.cmdline(999_999_999) == ""
    assert gl.running_gate(os.getpid()) is False, "python, not make"
    assert gl.main(["acquire", str(tmp_path), "4243"]) == 0
    assert gl.main([]) == 2
    assert sys.executable


def test_held_says_whether_a_live_gate_owns_the_clone(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 385 T30 (the round arbiter on red-gate@2026-10-18T12:36:36Z): what clone-sync and land-tooling ask before they merge
    main into a clone - a live gate holds it, a dead or unrelated owner does not, and no lock holds nothing."""
    assert not gl.held(tmp_path) and gl.main(["held", str(tmp_path)]) == 1
    live = subprocess.Popen(["sleep", "30"])
    try:
        monkeypatch.setattr(gl, "cmdline", lambda pid: "make done" if pid == live.pid else "")
        assert gl.acquire(tmp_path, live.pid) == ""
        assert gl.held(tmp_path) and gl.main(["held", str(tmp_path)]) == 0
        monkeypatch.setattr(gl, "cmdline", lambda pid: "sleep 30")
        assert not gl.held(tmp_path), "a reused pid is no gate"
    finally:
        live.kill()
        live.wait()
    (tmp_path / gl.LOCK).write_text("not json")
    assert not gl.held(tmp_path)
