#!/usr/bin/env python3
"""The detached runner behind `page-session.sh` (feature 250 D7): each brief in a fresh headless session, in order.

    _page_session_runner.py <root> <name> <projects dir> [claude args ...] -- <brief | then:<script>> ...

Prints every known session's id, transcript and log directory at once, then starts ONE detached process that
works the queue in order: a brief runs as a fresh session; a `then:<script>` runs the script when it is reached
and queues the briefs it prints, one path a line - which is how a page's check sessions are planned from the
handoff its write session leaves (feature 250 R3, recommendation 2). Every session started is appended to
`<root>/.git/page-sessions/index.txt` as `<session id> <brief>`, so the meter can find the ones planned late.

THE FLOOR (feature 250 R3, recommendation 1). A page session is launched with only the tools research uses, no
MCP servers, no skill listing, and - in a clone - without the MIRROR's root CLAUDE.md, which sits above every
clone and otherwise loads beside the clone's own copy. Measured on a probe, 2026-09-26: the first turn of a
page session fell from 40,280 tokens to 21,267; every turn carries that floor.
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

TOOLS = "Bash,Read,Edit,Write,Grep,Glob,Agent,WebFetch,WebSearch"


def floor_flags(root: str) -> list[str]:
    """The launch flags that lower a page session's fixed floor, and the reason for each in the docstring above."""
    flags = ["--disable-slash-commands", "--strict-mcp-config", "--tools", TOOLS]
    parts = root.rstrip("/").split("/")
    if ".clones" in parts:
        mirror = "/".join(parts[: parts.index(".clones")])
        flags += ["--settings", json.dumps({"claudeMdExcludes": [f"{mirror}/CLAUDE.md"]})]
    return flags


def command(root: str, name: str, extra: list[str], brief: str, sid: str) -> list[str]:
    return ["claude", "-p", PROMPT.format(brief=os.path.realpath(brief)), "-n", name, "--session-id", sid,
            "--permission-mode", "bypassPermissions", *floor_flags(root), *extra, "--output-format", "json"]


def plan(root: str, name: str, projects: str, extra: list[str], items: list[str]) -> list[dict]:
    """The queue: `{"sid", "log", "cmd"}` per brief (its log directory made), `{"then": script}` per late step."""
    queue: list[dict] = []
    for item in items:
        if item.startswith("then:"):
            queue.append({"then": os.path.realpath(item[5:])})
            print(f"page-session: then {os.path.basename(item[5:])} - the sessions it plans are listed in .git/page-sessions/index.txt")
            continue
        sid = str(uuid.uuid4())
        log = os.path.join(root, ".git", "page-sessions", sid)
        os.makedirs(log)
        queue.append({"sid": sid, "log": log, "brief": item, "cmd": command(root, name, extra, item, sid)})
        print(f"page-session: {os.path.basename(item)}\n  session:    {sid}\n  transcript: {projects}/{sid}.jsonl\n  log:        {log}")
    return queue


def work(root: str, name: str, extra: list[str], queue: list[dict]) -> None:
    """The detached loop: each session in turn; a `then` step's printed briefs join the queue where it stood."""
    index = os.path.join(root, ".git", "page-sessions", "index.txt")
    while queue:
        item = queue.pop(0)
        if "then" in item:
            got = subprocess.run([item["then"]], cwd=root, capture_output=True, text=True, check=False)
            late = []
            for brief in (ln.strip() for ln in got.stdout.splitlines() if ln.strip()):
                sid = str(uuid.uuid4())
                log = os.path.join(root, ".git", "page-sessions", sid)
                os.makedirs(log)
                late.append({"sid": sid, "log": log, "brief": brief, "cmd": command(root, name, extra, brief, sid)})
            queue[:0] = late
            continue
        with open(index, "a") as fh:
            fh.write(f"{item['sid']} {item['brief']}\n")
        with open(item["log"] + "/result.json", "w") as out, open(item["log"] + "/stderr.txt", "w") as err:
            subprocess.run(item["cmd"], cwd=root, stdin=subprocess.DEVNULL, stdout=out, stderr=err, check=False)


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--work":
        _, root, name, extra, queue = argv
        work(root, name, json.loads(extra), json.loads(queue))
        return 0
    root, name, projects, *rest = argv
    cut = rest.index("--")
    extra, items = rest[:cut], rest[cut + 1:]
    queue = plan(root, name, projects, extra, items)
    subprocess.Popen([sys.executable, os.path.abspath(__file__), "--work", root, name, json.dumps(extra), json.dumps(queue)],
                     cwd=root, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True, close_fds=True)
    print("page-session: started - each result.json is written when its session ends, and the next session begins")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
