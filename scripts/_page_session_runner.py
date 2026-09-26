#!/usr/bin/env python3
"""The detached runner behind `page-session.sh` (feature 250 D7): each brief in a fresh headless session, in order.

    _page_session_runner.py <root> <name> <projects dir> [claude args ...] -- <brief> [<brief> ...]

Prints every session's id, transcript and log directory at once, then starts ONE detached process that runs
the briefs one after another, so the second session begins only when the first has committed and ended.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid

PROMPT = ("You are a fresh session started to do the work ONE brief describes. Read {brief} first, and do what it says, "
          "end to end and unattended. Commit in this clone as you finish each part; never run the stop-work push. When the "
          "brief's work is done, or it tells you to stop, write the one-paragraph summary it asks for and stop.")

LOOP = """
import json, subprocess, sys
for sid, log, *cmd in json.loads(sys.argv[1]):
    with open(log + "/result.json", "w") as out, open(log + "/stderr.txt", "w") as err:
        subprocess.run(cmd, cwd=sys.argv[2], stdin=subprocess.DEVNULL, stdout=out, stderr=err)
"""


def plan(root: str, name: str, projects: str, extra: list[str], briefs: list[str]) -> list[list[str]]:
    """One `[session id, log dir, *command]` per brief, the log directories made."""
    runs = []
    for brief in briefs:
        sid = str(uuid.uuid4())
        log = os.path.join(root, ".git", "page-sessions", sid)
        os.makedirs(log)
        runs.append([sid, log, "claude", "-p", PROMPT.format(brief=os.path.realpath(brief)), "-n", name, "--session-id", sid,
                     "--permission-mode", "bypassPermissions", *extra, "--output-format", "json"])
        print(f"page-session: {os.path.basename(brief)}\n  session:    {sid}\n  transcript: {projects}/{sid}.jsonl\n  log:        {log}")
    return runs


def main(argv: list[str]) -> int:
    root, name, projects, *rest = argv
    cut = rest.index("--")
    runs = plan(root, name, projects, rest[:cut], rest[cut + 1:])
    subprocess.Popen([sys.executable, "-c", LOOP, json.dumps(runs), root], cwd=root, stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True, close_fds=True)
    print("page-session: started - each result.json is written when its session ends, and the next session begins")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
