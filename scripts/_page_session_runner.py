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
import pathlib
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


def dispatcher(root: str) -> str:
    """The session whose claim on `root` was written last - the one dispatching this queue into its own clone.

    WHY (feature 250 D14, 2026-09-26): the clone guard refuses an edit in a clone a LIVE other session claims, and
    the dispatcher is live, waiting on the queue - so a queued session was refused whenever the dispatcher's tree
    was clean. Its id goes to each session as `L7R_DISPATCHER`, which the guard lets through and nothing else."""
    parts = root.rstrip("/").split("/")
    if ".clones" not in parts:
        return ""
    mapdir = pathlib.Path("/".join(parts[: parts.index(".clones") + 1])) / ".session-clones"
    claims = [m for m in mapdir.glob("*") if m.is_file() and m.read_text(encoding="utf-8", errors="replace").strip() == root.rstrip("/")]
    return max(claims, key=lambda m: m.stat().st_mtime).name if claims else ""


def work(root: str, name: str, extra: list[str], queue: list[dict], run_log: str = os.devnull) -> None:
    """The detached loop: each session in turn; a `then` step's printed briefs join the queue where it stood.

    THE RUN LOG (feature 250, 2026-09-26): one file, held OPEN for the whole queue, with a line as each session
    starts and ends and `ALL DONE` last. A caller waits on it with the ordinary backgrounded file-watch, and the
    liveness check the no-poll guard adds finds the runner holding it - so the wait ends when the runner does,
    finished or killed. Before it, a page's sessions left no one file to wait on, and a wait on `tasks.md` (edited,
    never held open) was declared dead after two minutes while the sessions ran on."""
    index = os.path.join(root, ".git", "page-sessions", "index.txt")
    runlog = open(run_log, "a", buffering=1)  # noqa: SIM115 - held open on purpose for the whole queue
    env = {**os.environ, "L7R_DISPATCHER": dispatcher(root)}
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
            runlog.write(f"planned {len(late)} session(s) from {os.path.basename(item['then'])}\n")
            continue
        with open(index, "a") as fh:
            fh.write(f"{item['sid']} {item['brief']}\n")
        runlog.write(f"started {item['sid']} {os.path.basename(item['brief'])}\n")
        with open(item["log"] + "/result.json", "w") as out, open(item["log"] + "/stderr.txt", "w") as err:
            rc = subprocess.run(item["cmd"], cwd=root, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err, check=False).returncode
        runlog.write(f"ended {item['sid']} rc={rc}\n")
    runlog.write("ALL DONE\n")
    runlog.close()


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--work":
        _, root, name, extra, queue, run_log = argv
        work(root, name, json.loads(extra), json.loads(queue), run_log)
        return 0
    root, name, projects, *rest = argv
    cut = rest.index("--")
    extra, items = rest[:cut], rest[cut + 1:]
    queue = plan(root, name, projects, extra, items)
    run_log = os.path.join(root, ".git", "page-sessions", f"run-{uuid.uuid4().hex[:8]}.log")
    open(run_log, "w").close()  # it exists before the wait starts, so the wait never races its creation
    subprocess.Popen([sys.executable, os.path.abspath(__file__), "--work", root, name, json.dumps(extra), json.dumps(queue), run_log],
                     cwd=root, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True, close_fds=True)
    print("page-session: started - each result.json is written when its session ends, and the next session begins")
    print(f"page-session: to be told when the whole queue has ended, run this BACKGROUNDED (run_in_background):\n"
          f"    until grep -q '^ALL DONE' {run_log}; do sleep 60; done; tail -20 {run_log}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
