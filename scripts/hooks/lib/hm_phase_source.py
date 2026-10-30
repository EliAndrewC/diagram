#!/usr/bin/env python3
"""The decision behind `phase-source-hooks.sh` (feature 444, the GM 2026-10-30): pass, or the held file a read names.

Reads the hook payload on stdin and prints `pass`, or `held <file> <phase> <feature>`.

HELD: `make task-start` on a phase task wrote `<git common dir>/phase-sources.json` (`scripts/gates/phase_sources.py`) - the stage's
old modules - and the task's box is still open. A READ of one is refused: a Read on it; a Grep or Glob whose path is it or the
directory holding it; a shell command naming it (or its directory) with a read verb (cat, sed, head, tail, less, grep, rg, awk,
python, git show / diff / log / blame). A MENTION is not a read: `git rm`, a commit message, `make test-file FILE=` (match
invocations, not mentions). A grep over a wider tree (all of `l7r/`) passes: it is a search for a name, not a reading of the stage.
Only paths inside a checkout of this repository count, so a review bundle's copy under /tmp is never held.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
import subprocess
import sys

VERB = re.compile(r"(?:^|[\s;&|(`$])(?:cat|sed|head|tail|less|more|grep|rg|ugrep|awk|nl|bat|python3?|git\s+(?:show|diff|log|blame))\b")


def state_for(cwd: str) -> tuple[pathlib.Path, dict] | None:
    out = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel", "--path-format=absolute", "--git-common-dir"], capture_output=True, text=True)
    if out.returncode != 0:
        return None
    top, common = out.stdout.split()[:2]
    try:
        state = json.loads((pathlib.Path(common) / "phase-sources.json").read_text(encoding="utf-8"))
    except OSError, ValueError:
        return None
    tasks = pathlib.Path(top) / "specs" / state["feature"] / "tasks.md"
    try:
        if not re.search(rf"^- \[ \] {re.escape(state['task'])}\b", tasks.read_text(encoding="utf-8"), re.M):
            return None  # the task is ticked (or gone): nothing is held
    except OSError:
        return None
    return pathlib.Path(top), state


def allowed(state: dict, rel: str, now: datetime.datetime) -> bool:
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return any(a["file"] == rel and a["until"] > stamp for a in state.get("allow", []))


def held_path(top: pathlib.Path, path: str, cwd: str, files: list[str], dirs: bool) -> str:
    """The held file `path` names - itself, or (with `dirs`) the directory holding it - or ''."""
    p = pathlib.Path(path) if os.path.isabs(path) else pathlib.Path(cwd) / path
    try:
        rel = str(p.resolve().relative_to(top.resolve()))
    except ValueError:
        return ""
    for f in files:
        if rel == f or (dirs and rel and str(pathlib.PurePosixPath(f).parent) == rel):
            return f
    return ""


def decide(payload: dict, now: datetime.datetime | None = None) -> str:
    tool = payload.get("tool_name") or ""
    ti = payload.get("tool_input") or {}
    cwd = str(payload.get("cwd") or os.getcwd())
    if tool not in ("Read", "Grep", "Glob", "Bash"):
        return "pass"
    found = state_for(cwd)
    if found is None:
        return "pass"
    top, state = found
    files: list[str] = state["files"]
    hit = ""
    if tool == "Read":
        hit = held_path(top, str(ti.get("file_path") or ""), cwd, files, dirs=False)
    elif tool in ("Grep", "Glob"):
        hit = held_path(top, str(ti.get("path") or ""), cwd, files, dirs=True) if ti.get("path") else ""
    else:
        cmd = str(ti.get("command") or "")
        if VERB.search(cmd):
            for f in files:
                parent = str(pathlib.PurePosixPath(f).parent)
                if re.search(rf"(?<![\w.-]){re.escape(f)}\b", cmd) or re.search(rf"(?<![\w.-]){re.escape(parent)}/?(?=[\s'\"]|$)", cmd):
                    hit = f
                    break
    if not hit or allowed(state, hit, now or datetime.datetime.now(datetime.UTC)):
        return "pass"
    return f"held {hit} {state['phase']} {state['feature']} {state['task']}"


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        print("pass")
        return 0
    print(decide(payload))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
