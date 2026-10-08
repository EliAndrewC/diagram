#!/usr/bin/env python3
"""Which of a delta's changed files only MOVED - same bytes, new path (feature 329).

WHY. The checks owed by a delta ask `git diff --name-only <base> -- <tree>` what changed, and a path that did not exist at
the base reads as new. Feature 329 moved the whole project to the repository root, so on its own push every research
page, map and doc read as new: the size check flagged three pages whose prose nobody touched, and every check owed on a
"new" page or map came due at once. A file whose exact content stood at the base under any path changed no word and
added no map. Content, not git's rename pairing, decides: a pathspec limited to the new tree cannot see the old side of
a rename, and a byte-identical blob is exactly the claim "nothing in it changed".

    moved_only(root, base, names) -> the subset of `names` (repo-relative paths) whose content stood at `base`
"""

from __future__ import annotations

import pathlib
import subprocess
from collections.abc import Iterable


def _git(root: pathlib.Path, *args: str, stdin: str | None = None) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], input=stdin, capture_output=True, text=True, check=False)
    return p.stdout if p.returncode == 0 else ""


def blobs_at(root: pathlib.Path, rev: str) -> set[str]:
    """Every blob id in `rev`'s tree - one `ls-tree`, a few hundred milliseconds over this repository."""
    return {line.split()[2] for line in _git(root, "ls-tree", "-r", rev).splitlines() if line.split()[1:2] == ["blob"]}


def moved_only(root: pathlib.Path, base: str, names: Iterable[str]) -> set[str]:
    """The names whose working-tree content is a blob `base` already held: moved, not edited. A missing file is never moved."""
    names = [n for n in dict.fromkeys(names) if n and (root / n).is_file()]
    if not base or not names:
        return set()
    ids = _git(root, "hash-object", "--stdin-paths", stdin="\n".join(names) + "\n").split()
    if len(ids) != len(names):
        return set()
    have = blobs_at(root, base)
    return {n for n, i in zip(names, ids, strict=True) if i in have}
