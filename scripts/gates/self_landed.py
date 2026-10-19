#!/usr/bin/env python3
"""Resolve a merge of main whose every conflict is a file the clone itself landed (feature 385 T122, D144).

WHY. `make land-tooling` lands a clone's file as main's own commit and leaves the clone's history as it was (feature 385 D46),
so the clone's merge base with main still lacks a file that was new. Edited again and landed again, its patch adds the file a
second time and fails to apply; D46's merge of main then conflicts add/add - though main's side is exactly what the clone had
landed (T119's `fix_yield.py`, resolved by hand twice on 2026-10-19). Such a conflict has one right answer, the clone's side.

    self_landed.py <clone root>

Run with a merge in progress. If every conflicted file's blob on main's side (`MERGE_HEAD:<file>`) is the blob of that file at
some commit of the clone's own since its fork from main (`merge-base HEAD MERGE_HEAD..HEAD`), takes the clone's side for each, stages it and commits the merge: exit 0. Otherwise
resolves nothing: exit 1, and the caller aborts the merge as before.
"""

from __future__ import annotations

import subprocess
import sys


def _git(root: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)


def self_landed(root: str, path: str) -> bool:
    """Is main's side of the conflicted `path` a version of it from the clone's OWN commits since it forked from main? Never the
    history the two share: another session's revert to an older version would match it, and taking the clone's side would undo
    that revert silently (the plan review of T122, round 2)."""
    theirs = _git(root, "rev-parse", "-q", "--verify", f"MERGE_HEAD:{path}").stdout.strip()
    base = _git(root, "merge-base", "HEAD", "MERGE_HEAD").stdout.strip()
    if not theirs or not base:
        return False
    for commit in _git(root, "rev-list", f"{base}..HEAD", "--", path).stdout.split():
        if _git(root, "rev-parse", "-q", "--verify", f"{commit}:{path}").stdout.strip() == theirs:
            return True
    return False


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: self_landed.py <clone root>", file=sys.stderr)
        return 2
    root = argv[0]
    if _git(root, "rev-parse", "-q", "--verify", "MERGE_HEAD").returncode:
        return 1
    conflicted = _git(root, "diff", "--name-only", "--diff-filter=U").stdout.split()
    if not conflicted or not all(self_landed(root, p) for p in conflicted):
        return 1
    for path in conflicted:
        _git(root, "checkout", "--ours", "--", path)
    if _git(root, "add", "--", *conflicted).returncode or _git(root, "commit", "-q", "--no-edit").returncode:
        return 1
    print(f"land-tooling: the merge's conflicts were the clone's own landing ({', '.join(conflicted)}) - took the clone's side", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
