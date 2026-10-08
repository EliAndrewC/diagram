"""Features 301 and 303: every pointer to the research names a question or a section that exists, and none is of a
retired form (301 FR-014, 303 FR-018); the tools that keep it so prove they still bite (301 FR-015, 303 SC-007)."""

from __future__ import annotations

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[5]


def _run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(REPO / "scripts" / script), *args], capture_output=True, text=True, check=False)


def test_every_pointer_in_the_repository_resolves_to_a_fragment() -> None:
    """The gate's half of FR-014; the push runs the same script, because a docs-only delta takes the DIRECT route."""
    done = _run("check-research-pointers.py", str(REPO))
    assert done.returncode == 0, done.stderr


def test_the_pointer_check_and_the_move_each_still_bite() -> None:
    for script in ("check-research-pointers.py", "_fragment_move.py"):
        done = _run(script, "--selftest")
        assert done.returncode == 0, f"{script}: {done.stdout}{done.stderr}"
