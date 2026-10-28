#!/usr/bin/env python3
"""A feature is worked until it is set down (feature 385 T70, plan D89/D90): the verdict `set-down-hooks.sh stop` acts on.

WHY. The GM, 2026-10-18: "stopping with tasks partially done is a constant problem with the Opus line of models", asking for a
check "for whether or not the feature is either still in progress or has been correctly set down". T05's 464 minutes held 240 of
idle: a turn ended overnight with nothing running and nothing set down. A Stop guard sees every turn's end, where a timed check
would only sample.

THE VERDICT, at a turn's end, for the clone's last `make task-start` (`<git dir>/task-starts.jsonl`):
  - IN PROGRESS: the feature's `tasks.md` has an open box other than the GM-review box, and its status line does not close it;
  - RUNNING: a background command ("running in background with ID") or async agent ("agentId:") in the session's transcript has
    no later task notification of its id - it will wake the session;
  - SET DOWN: a row of `<git dir>/set-downs.jsonl` for the feature at or after that task-start (`make set-down F= WHY=`).
In progress, nothing running and not set down: refused. A turn ending on a question to the GM is NOT a way out - the plan
review (2026-10-19) showed it passes exactly the quiet turn this exists for; a real wait on the GM is set down with its reason.
Any read error lets the turn end (printed `ERROR`, and the hook records it): a Stop guard that fails closed can hold a session.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path

HERE = Path(__file__).resolve().parent
OPEN = re.compile(r"^- \[ \] (T\d+[a-z]?) (.*)$", re.M)
# ...A LAUNCH IS THE TOOL'S OWN RECORD, NEVER ITS TEXT (2026-10-28): the notice's words reach the transcript quoted - in the session's
# commands and in the system's notes of a changed file - and each quote read as a launch kept the guard silent; the tool result's
# structured fields (`backgroundTaskId`, an async agent's `agentId`) are written only by a real launch
LAUNCHED = re.compile(r'"(?:backgroundTaskId|agentId)":\s*"([A-Za-z0-9]+)"')
NOTIFIED = re.compile(r"<task-id>([A-Za-z0-9]+)</task-id>")
#: a task ended with TaskStop sends no notification, so its stop is its end (2026-10-28: a background command stopped on 10-25 stayed
#: "running" for three days and let every turn of the session end unrefused; the same fix `hm_checks` made in feature 385 T104)
STOPPED = re.compile(r'"name":\s*"TaskStop",\s*"input":\s*\{[^}]*?"(?:task_id|shell_id)":\s*"([A-Za-z0-9]+)"')


def _rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def git_dir(root: Path) -> Path:
    out = subprocess.run(["git", "-C", str(root), "rev-parse", "--path-format=absolute", "--git-common-dir"], capture_output=True, text=True, check=True)
    return Path(out.stdout.strip())


def running(transcript: str) -> set[str]:
    """The ids launched in the background that no task notification has reported on."""
    return running_lines(transcript.splitlines())


def running_lines(lines: Iterable[str]) -> set[str]:
    """`running`, read a line at a time: only the ids are kept. A session's transcript reached 206 MB on 2026-10-26, and read whole
    (its text, then every match of two patterns) this hook grew past 1.2 GB at each turn's end and was killed twice by the
    laptop's memguard at the containers' shared memory cap."""
    launched: set[str] = set()
    notified: set[str] = set()
    for line in lines:
        launched.update(LAUNCHED.findall(line))
        notified.update(NOTIFIED.findall(line))
        notified.update(STOPPED.findall(line))
    return launched - notified


def open_tasks(spec_dir: Path) -> list[tuple[str, str]]:
    """The feature's open boxes, the GM-review box left out; none when its status line closes it."""
    boxes = [(t, title) for t, title in OPEN.findall((spec_dir / "tasks.md").read_text(encoding="utf-8")) if not title.startswith("GM review")]
    if boxes:
        closed = subprocess.run([sys.executable, str(HERE.parent.parent / "speckit-todo.py"), "--closed-by-status", str(spec_dir)], capture_output=True, text=True, check=False)
        if closed.stdout.strip() == "yes":
            return []
    return boxes


def verdict(root: Path, transcript: str | Path) -> str:
    """'' to let the turn end, else the refusal; `transcript` is its text, or the path it is streamed from."""
    gd = git_dir(root)
    starts = _rows(gd / "task-starts.jsonl")
    if not starts:
        return ""
    last = starts[-1]
    feature, since = str(last.get("feature", "")), str(last.get("utc", ""))
    spec_dir = root / "specs" / feature
    if not feature or not (spec_dir / "tasks.md").is_file():
        return ""
    boxes = open_tasks(spec_dir)
    if not boxes:
        return ""
    if isinstance(transcript, Path):
        with transcript.open(encoding="utf-8", errors="replace") as fh:
            live = running_lines(fh)
    else:
        live = running(transcript)
    if live:
        return ""
    if any(r.get("feature") == feature and str(r.get("utc", "")) >= since for r in _rows(gd / "set-downs.jsonl")):
        return ""
    tid, title = boxes[0]
    return (f"BLOCKED: feature {feature} has {len(boxes)} open task(s) and nothing is running - start the next ({tid} {title[:80]}), "
            f'or set it down: make set-down F={feature.split("-")[0]} WHY="<why it stops here>" (feature 385 T70)')


def main(argv: list[str]) -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        root = Path(argv[1]) if len(argv) > 1 else Path(payload.get("cwd") or ".")
        tp = payload.get("transcript_path") or ""
        transcript: str | Path = Path(tp) if tp and Path(tp).is_file() else ""  # streamed, never read whole
        out = verdict(root, transcript)
    except Exception as e:  # noqa: BLE001 - fail open, recorded by the hook
        print(f"ERROR {type(e).__name__}: {e}")
        return 0
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
