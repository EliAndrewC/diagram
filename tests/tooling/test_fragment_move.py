"""`make fragment-move` moves a fragment with every pointer to it; its self-test proves the move still bites."""

from __future__ import annotations

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]


def test_the_move_still_bites() -> None:
    done = subprocess.run([sys.executable, str(REPO / "scripts/record/fragment_move.py"), "--selftest"], capture_output=True, text=True, check=False)
    assert done.returncode == 0, f"{done.stdout}{done.stderr}"
