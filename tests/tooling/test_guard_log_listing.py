"""`make guard-log` lists the firings an audit starts from (feature 204).

WHY (GM 2026-09-07): *"anytime we block a command invocation, we can see what specifically was
happening and whether the command was rewritable safely."* `make audit` prints the census; this
prints the rows. Driven as a subprocess over a throwaway log directory, in both forms, with an entry
from before feature 204 (no `session_name`, a truncated `detail` and nothing else) beside two new
ones, because the log on the host is exactly that mixture.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

SCRIPT = pathlib.Path(__file__).resolve().parents[5] / "scripts" / "guard-log.py"


def _log(tmp_path: pathlib.Path) -> pathlib.Path:
    d = tmp_path / "log"
    d.mkdir()
    old = {"utc": "2026-09-06T10:00:00Z", "guard": "main-tree", "event": "blocked", "rule": "write-in-mirror", "session": "unknown", "detail": "cat > /tmp/x <<'PY'"}
    new_block = {
        "utc": "2026-09-07T18:00:00Z",
        "guard": "main-tree",
        "event": "blocked",
        "rule": "named-main",
        "session": "abc123def",
        "session_name": "diagram-hooks",
        "cwd": "/diagram/.clones/diagram-hooks",
        "tool": "Bash",
        "transcript": "/t.jsonl",
        "detail": "git -C /diagram commit -am x",
        "command": "git -C /diagram commit -am x",
        "context": {"verdict": "refuse"},
    }
    new_rewrite = {
        "utc": "2026-09-07T18:01:00Z",
        "guard": "main-tree",
        "event": "rewrote",
        "rule": "moved-to-clone",
        "session": "abc123def",
        "session_name": "diagram-hooks",
        "cwd": "/diagram",
        "tool": "Bash",
        "transcript": "/t.jsonl",
        "detail": "git commit -am x",
        "command": "git commit -am x\n# second line",
        "context": {"verdict": "rewrite"},
    }
    other = {
        "utc": "2026-09-07T18:02:00Z",
        "guard": "batching",
        "event": "blocked",
        "rule": "recon-shape",
        "session": "s2",
        "session_name": "diagram-html",
        "cwd": "/diagram",
        "tool": "Bash",
        "detail": "ls",
        "command": "ls",
    }
    for i, row in enumerate([old, new_block, new_rewrite, other]):
        (d / f"{i}.json").write_text(json.dumps(row))
    (d / "broken.json").write_text("{not json")
    return d


def _run(log: pathlib.Path, *args: str) -> str:
    p = subprocess.run(["python3", str(SCRIPT), "--dir", str(log), *args], capture_output=True, text=True, check=True)
    return p.stdout


def test_lists_every_firing_with_name_cwd_and_the_first_line(tmp_path) -> None:
    out = _run(_log(tmp_path))
    lines = out.strip().splitlines()
    assert lines[-1] == "4 firing(s)"
    assert "unknown" in lines[0] and "cat > /tmp/x" in lines[0], "a pre-204 entry shows unknown and its truncated detail"
    assert "diagram-hooks" in lines[1] and "blocked/named-main" in lines[1] and "/diagram/.clones/diagram-hooks" in lines[1]
    assert "rewrote/moved-to-clone" in lines[2] and "# second line" not in lines[2], "the short form shows the first line only"
    assert "diagram-html" in lines[3] and "batching" in lines[3]


def test_filters_by_guard_since_and_event(tmp_path) -> None:
    log = _log(tmp_path)
    assert _run(log, "--guard", "batching").strip().splitlines()[-1] == "1 firing(s)"
    assert _run(log, "--since", "2026-09-07").strip().splitlines()[-1] == "3 firing(s)"
    assert _run(log, "--event", "rewrote").strip().splitlines()[-1] == "1 firing(s)"
    assert _run(log, "--guard", "main-tree", "--event", "blocked", "--since", "2026-09-07").strip().splitlines()[-1] == "1 firing(s)"
    assert _run(log, "--guard", "nothing").strip() == "(no matching firings)"


def test_full_form_prints_the_whole_command_and_the_context(tmp_path) -> None:
    out = _run(_log(tmp_path), "--full", "--event", "rewrote")
    assert "# second line" in out and '"verdict": "rewrite"' in out and "cwd: /diagram" in out


def test_a_session_id_without_a_name_is_shown_shortened_never_looked_up(tmp_path) -> None:
    log = tmp_path / "log"
    log.mkdir()
    (log / "a.json").write_text(json.dumps({"utc": "2026-09-07T00:00:00Z", "guard": "gate", "event": "escaped", "rule": "gate-ok", "session": "0123456789abcdef", "detail": "why"}))
    out = _run(log)
    assert "01234567" in out and "0123456789abcdef" not in out
