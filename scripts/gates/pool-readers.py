#!/usr/bin/env python3
"""Name the quick tests that read the shipped hamlet manifests, when those manifests changed since the last green quick.

WHY (feature 328 wave 54, 2026-10-08): wave 52 re-seated the privies and manure heaps, rerolled the five hamlets and ran the
test files of the code it changed - and three tests that read the rerolled MANIFESTS (`tests/hamletgen/test_pool_261.py`:
a knot on Inashiro and Kuwabata, a zigzag on Sawada) went red unseen for two waves, because `make quick` selects tests by
changed CODE (testmon) and a manifest is data. A spec reviewer found them by accident. So quick asks this script: where the
manifests' content differs from the stamp the last green quick left, the tests that read them run too.

    pool-readers.py changed   print the reader test files, one per line, when the manifests moved since the stamp; else nothing
    pool-readers.py stamp     record the manifests as they stand (quick calls it once the readers passed)

A READER is the rule `l7r/diagram/ci/pool_readers.py` holds (one copy, shared with the gate's planner since feature 430
T01), asked here of the quick tree (not gate/, full/, tooling/, soak/, tier_*). The stamp lives in the clone's `.git/` - never
committed, one per tree.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

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
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # the repository this script is in, not the tree it asks
    from l7r.diagram.ci import pool_readers  # noqa: PLC0415 - the one copy of the rule (feature 430 T01)

    return pool_readers.readers(top, NOT_QUICK)


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
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: E402 - feature 406 T03 (D162): every refusing check records its run

    sys.exit(usage_log.exited("pool-readers", main(sys.argv)))
