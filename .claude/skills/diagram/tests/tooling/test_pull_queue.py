"""`scripts/pull-queue.sh` (feature 265 FR-010): a finished queue's commits come back, and the generated pages are rebuilt.

WHAT THESE PROVE, on real git repositories in tmp: a conflict only in a generated page takes this side and the rebuild
runs and is committed; a conflict in a hand-written file stops with that file named and exit 1; a queue still dirty
is refused.
"""

from __future__ import annotations

import os
import pathlib
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[5]
SCRIPT = REPO / "scripts" / "pull-queue.sh"


def _git(cwd: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True).stdout


def _world(tmp: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    a = tmp / "a"
    (a / "research").mkdir(parents=True)
    _git(tmp, "init", "-q", str(a))
    for k, v in (("user.name", "t"), ("user.email", "t@t")):
        _git(a, "config", k, v)
    (a / "research" / "fields.html").write_text("page v0\n", encoding="utf-8")
    (a / "research" / "note.txt").write_text("note v0\n", encoding="utf-8")
    _git(a, "add", "-A")
    _git(a, "commit", "-q", "-m", "base")
    q = tmp / "a-1"
    _git(tmp, "clone", "-q", str(a), str(q))
    for k, v in (("user.name", "t"), ("user.email", "t@t")):
        _git(q, "config", k, v)
    return a, q


def _run(a: pathlib.Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "PULL_QUEUE_REBUILD": "echo rebuilt > research/fields.html"}
    return subprocess.run([str(SCRIPT), "1"], cwd=a, capture_output=True, text=True, env=env, check=False)


def _change(root: pathlib.Path, name: str, text: str) -> None:
    (root / "research" / name).write_text(text, encoding="utf-8")
    _git(root, "commit", "-q", "-am", f"{root.name} {name}")


def test_a_generated_conflict_is_rebuilt_and_committed(tmp_path) -> None:
    a, q = _world(tmp_path)
    _change(a, "fields.html", "page from a\n")
    _change(q, "fields.html", "page from the queue\n")
    got = _run(a)
    assert got.returncode == 0, got.stderr
    assert (a / "research" / "fields.html").read_text(encoding="utf-8") == "rebuilt\n"
    assert "rebuilt" in _git(a, "log", "--oneline", "-1") and not _git(a, "status", "--porcelain")


def test_a_hand_written_conflict_stops_and_a_dirty_queue_is_refused(tmp_path) -> None:
    a, q = _world(tmp_path)
    _change(a, "note.txt", "note from a\n")
    _change(q, "note.txt", "note from the queue\n")
    got = _run(a)
    assert got.returncode == 1 and "research/note.txt" in got.stderr
    _git(a, "merge", "--abort")
    (q / "research" / "note.txt").write_text("still being written\n", encoding="utf-8")
    got = _run(a)
    assert got.returncode == 2 and "still running" in got.stderr
