"""`setup-dev-env.sh --ensure` (2026-10-04): a fresh container provisions itself at session start, and every later
start is a no-op. The stamp is keyed on the script and the lockfiles, so a re-lock provisions again.

WHY. A fresh container ran the reference map red with "No module named 'shapely'": nothing ran the setup script,
it waited on a session to remember. The SessionStart hook now runs `--ensure`."""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "container-scripts" / "setup-dev-env.sh"
SKILL = REPO

in_container = pytest.mark.skipif(not (os.path.exists("/run/.containerenv") or os.path.exists("/.dockerenv")), reason="--ensure is a no-op outside a container")


def _key() -> str:
    parts = [SCRIPT, SKILL / "requirements.txt", SKILL / "requirements-dev.txt", SKILL / "requirements-ci.txt"]
    return hashlib.sha256(b"".join(p.read_bytes() for p in parts)).hexdigest()


def _ensure(stamp_dir: pathlib.Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "SETUP_STAMP_DIR": str(stamp_dir), "SETUP_ENSURE_DRY": "1"}
    return subprocess.run(["bash", str(SCRIPT), "--ensure"], capture_output=True, text=True, env=env, check=False, timeout=30)


@in_container
def test_a_matching_stamp_is_a_silent_no_op(tmp_path: pathlib.Path) -> None:
    (tmp_path / "l7r-dev-env.stamp").write_text(_key() + "\n")
    proc = _ensure(tmp_path)
    assert (proc.returncode, proc.stdout, proc.stderr) == (0, "", "")


@in_container
def test_a_missing_or_stale_stamp_provisions(tmp_path: pathlib.Path) -> None:
    assert "would provision" in _ensure(tmp_path).stdout
    (tmp_path / "l7r-dev-env.stamp").write_text("an older lockfile's key\n")
    assert "would provision" in _ensure(tmp_path).stdout


def test_session_start_runs_it() -> None:
    hooks = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))["hooks"]["SessionStart"]
    assert any("setup-dev-env.sh" in h["command"] and "--ensure" in h["command"] for e in hooks for h in e["hooks"])
