#!/usr/bin/env python3
"""Name the quick tests that read the shipped hamlet manifests, when those manifests changed since the last green quick.

WHY (feature 328 wave 54, 2026-10-08): wave 52 re-seated the privies and manure heaps, rerolled the five hamlets and ran the
test files of the code it changed - and three tests that read the rerolled MANIFESTS (`tests/hamletgen/test_pool_261.py`:
a knot on Inashiro and Kuwabata, a zigzag on Sawada) went red unseen for two waves, because `make quick` selects tests by
changed CODE (testmon) and a manifest is data. A spec reviewer found them by accident. So quick asks this script: where the
manifests' content differs from the stamp the last green quick left, the tests that read them run too.

    pool-readers.py changed   print the reader test files, one per line, when the manifests moved since the stamp; else nothing
    pool-readers.py stamp     record the manifests as they stand (quick calls it once the readers passed)

A READER is a test module in the quick tree (not gate/, full/, tooling/, soak/, tier_*) whose source names the pool as a path
part (`"pool"`, as `"pool", "hamlets"` or a loop over `("pool", "legacy-hand-authored-pool")`) or globs `pool/hamlets/*`. Broad on
purpose: the notes census (`tests/test_notes_census.py`) reached the manifests through a tree loop the first pattern missed, and
its failure surfaced at batch 3's gate; a reader too many costs a fraction of a second. The stamp lives in the clone's `.git/` - never committed, one per tree.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

READS = re.compile(r'"pool"|pool/hamlets/\*')  # the pool named as a path part: `"pool", "hamlets"`, or a tree loop's `("pool", ...)`
NOT_QUICK = ("gate", "full", "tooling", "soak")


def root() -> Path:
    return Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip())


def stamp_path(top: Path) -> Path:
    git = subprocess.run(["git", "-C", str(top), "rev-parse", "--git-dir"], capture_output=True, text=True, check=True).stdout.strip()
    return (top / git if not Path(git).is_absolute() else Path(git)) / "quick-pool-stamp"


def digest(top: Path) -> str:
    h = hashlib.sha256()
    for p in sorted((top / "pool" / "hamlets").glob("*/*.json")):
        h.update(p.relative_to(top).as_posix().encode())
        h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


def readers(top: Path) -> list[str]:
    out = []
    for p in sorted((top / "tests").rglob("test_*.py")):
        parts = p.relative_to(top / "tests").parts
        if parts[0] in NOT_QUICK or parts[0].startswith("tier_"):
            continue
        if READS.search(p.read_text(encoding="utf-8")):
            out.append(p.relative_to(top).as_posix())
    return out


def main(argv: list[str]) -> int:
    top = root()
    stamp = stamp_path(top)
    if argv[1:] == ["stamp"]:
        stamp.write_text(digest(top) + "\n")
        return 0
    if argv[1:] == ["changed"]:
        old = stamp.read_text().strip() if stamp.exists() else ""
        if old != digest(top):
            print("\n".join(readers(top)))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
