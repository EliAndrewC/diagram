"""`scripts/gates/one-gate.sh`: `make verify` starts no second gate in a tree where one runs (feature 328 batch 7).

A stand-in for the running gate is a process whose command line reads `make done` with its working directory in the
tree (`tail` renamed `make` by `exec -a`, following /dev/null so it stays alive); another tree's gate does not count.
"""

from __future__ import annotations

import pathlib
import subprocess
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts/gates/one-gate.sh"

pytestmark = pytest.mark.tooling


def _tree(path: pathlib.Path) -> pathlib.Path:
    path.mkdir()
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    return path


def _stand_in_gate(cwd: pathlib.Path) -> subprocess.Popen[bytes]:
    proc = subprocess.Popen(["bash", "-c", "exec -a make tail done -f /dev/null"], cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.3)  # until the exec has renamed it
    return proc


def _verdict(cwd: pathlib.Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(SCRIPT)], cwd=cwd, capture_output=True, text=True)


def test_a_second_gate_in_the_same_tree_is_refused_and_another_trees_gate_is_not_counted(tmp_path: pathlib.Path) -> None:
    mine, other = _tree(tmp_path / "mine"), _tree(tmp_path / "other")
    assert _verdict(mine).returncode == 0, "no gate running: verify may start one"
    gate = _stand_in_gate(other)
    try:
        assert _verdict(mine).returncode == 0, "another tree's gate is not this tree's"
    finally:
        gate.kill()
    gate = _stand_in_gate(mine)
    try:
        refused = _verdict(mine)
        assert refused.returncode == 1 and "A GATE IS ALREADY RUNNING IN THIS TREE" in refused.stdout
        assert "verify-gate.log" in refused.stdout, "the refusal names the log to wait on"
    finally:
        gate.kill()
