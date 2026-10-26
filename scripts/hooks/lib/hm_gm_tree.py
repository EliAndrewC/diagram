#!/usr/bin/env python3
"""Does a write land in gm-assistant's MAIN working tree? The gm-tree guard's verdict (feature 429 D169).

gm-assistant's main tree (/host-l7r-repo/gm-assistant) refuses every gm-assistant push while it is dirty, so a
diagram session's leftover edit there stalls another project (2026-10-20, diagram#10). Its clones
(`.clones/<name>/`) are the place to edit it. The shell's write targets are found by the main-tree guard's own
interpreter (`hm_tree.walk`, with gm-assistant as its "main"), so a read of the tree is never mistaken for a write;
git writes are left to `repo-safety-hooks.sh`, which already refuses them under /host-l7r-repo.

Usage: hm_gm_tree.py judge < payload   ->  prints the offending path and exits 1, or exits 0
"""

from __future__ import annotations

import json
import os
import posixpath
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hm_tree  # noqa: E402

TREE = os.environ.get("GM_TREE_ROOT", "/host-l7r-repo/gm-assistant")
FILE_TOOLS = ("Edit", "Write", "NotebookEdit")


def offending(payload: dict) -> str | None:
    """The first path the call would write inside the tree (outside its .clones/), or None."""
    tool = payload.get("tool_name") or ""
    ti = payload.get("tool_input") or {}
    if tool in FILE_TOOLS:
        p = ti.get("file_path") or ti.get("notebook_path") or ""
        p = posixpath.normpath(p) if p.startswith("/") else ""
        return p if hm_tree.classify(p or None, TREE) == "main" else None
    if tool != "Bash":
        return None
    cmd = ti.get("command") or ""
    if "gm-assistant" not in cmd and not (payload.get("cwd") or "").startswith(TREE):
        return None
    walked = hm_tree.walk(cmd, payload.get("cwd") or None, TREE, os.path.expanduser("~"))
    for t in walked["targets"]:
        if t["segment"].lstrip().startswith("git"):
            continue
        if t["class"] == "main":
            return t["path"] or TREE
    return None


def main() -> int:
    if sys.argv[1:2] != ["judge"]:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        payload = json.load(sys.stdin) or {}
    except Exception:
        return 0
    hit = offending(payload)
    if hit:
        print(hit)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
