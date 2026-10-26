#!/usr/bin/env python3
"""Which pool manifests differ from HEAD - the comparison a wave records (feature 429 FR-004, D170).

"Did this wave move a map?" is answered against HEAD, never against a scratch copy: feature 328 wave 68 (2026-10-09)
copied the manifests after a gate test had already regenerated them and recorded four hamlets unchanged while
Sawada's board had moved 76 degrees. `make map` prints this for its own map; `make maps-moved` for the pool.

Usage: maps_moved.py [--root DIR] [--only <gen or manifest path>]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)


def moved(root: Path, only: str | None = None) -> list[str]:
    """Pool manifests (`pool/**/*.json`) whose working-tree content differs from HEAD, untracked ones included."""
    spec = ["pool"]
    if only:
        spec = [only[: -len(".gen.py")] + ".json" if only.endswith(".gen.py") else only]
    changed = _git(root, "diff", "--name-only", "HEAD", "--", *spec).stdout.split()
    new = _git(root, "ls-files", "--others", "--exclude-standard", "--", *spec).stdout.split()
    return sorted(p for p in {*changed, *new} if p.startswith("pool/") and p.endswith(".json"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--only")
    a = ap.parse_args(argv)
    hits = moved(Path(a.root), a.only)
    for p in hits:
        print(f"moved against HEAD: {p}")
    if not hits:
        what = "this map's manifest" if a.only else "no pool manifest"
        print(f"{what} {'is unchanged' if a.only else 'moved'} against HEAD")
    return 0


if __name__ == "__main__":
    sys.exit(main())
