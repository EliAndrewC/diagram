"""`scripts/gates/verify_wait.sh` (feature 385, the round arbiter's tooling fix on hour:385-approach-checklist@3): `make verify`'s
gate writes its own log, `.git/verify-gate.log` links to the newest, and the wait reads that run's log alone - never an
earlier run's verdict line - and says when the gate died with none."""

from __future__ import annotations

import os
import pathlib
import subprocess

from tests._scripts import script


def _repo(tmp: pathlib.Path) -> pathlib.Path:
    subprocess.run(["git", "init", "-q", str(tmp)], check=True)
    return tmp / ".git"


def _wait(tmp: pathlib.Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "VERIFY_WAIT_STEP_S": "0.2", "VERIFY_WAIT_S": "20"}
    return subprocess.run(["bash", str(script("verify_wait"))], cwd=tmp, env=env, capture_output=True, text=True, timeout=60)


def test_the_wait_reads_the_newest_runs_own_log(tmp_path: pathlib.Path) -> None:
    g = _repo(tmp_path)
    assert _wait(tmp_path).returncode == 3, "no gate log yet"
    old, new = g / "verify-gate-1.log", g / "verify-gate-2.log"
    old.write_text("...\nverification-state: green-local (done) recorded\n")
    new.write_text("preflight: ...\n")  # the newest run: no verdict yet, and no writer holds it open
    (g / "verify-gate.log").symlink_to(new)
    died = _wait(tmp_path)
    assert died.returncode == 5 and "ended with no verdict" in died.stdout, "the old run's verdict is never read for the new one"
    new.write_text("preflight: ...\ngate green\nverification-state: green-local (done) recorded\n")
    assert _wait(tmp_path).returncode == 0
    new.write_text("GATE FAILED: test-full\nverification-state: failed-gate (done) recorded\n")
    assert _wait(tmp_path).returncode == 1


def test_the_preflights_own_quick_verdict_is_not_the_gates(tmp_path: pathlib.Path) -> None:
    """The first run of this wait ended mid-gate on the preflight's `make quick` line; the gate's end is its writer's."""
    g = _repo(tmp_path)
    new = g / "verify-gate-3.log"
    new.write_text("preflight: ...\nverification-state: green-local (quick) recorded\n")
    (g / "verify-gate.log").symlink_to(new)
    assert _wait(tmp_path).returncode == 5, "the quick line alone is no gate verdict"
    writer = subprocess.Popen(["bash", "-c", f"exec 3>>'{new}'; sleep 2; echo 'gate green' >&3"])
    try:
        done = _wait(tmp_path)
    finally:
        writer.wait(timeout=30)
    assert done.returncode == 0 and "gate green" in done.stdout, "waited while the writer held the log, then read its verdict"
