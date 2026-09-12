#!/usr/bin/env python3
"""The reviewer's snapshot: a changed map's files from the clone and from main, copied where the gate's
cache never evicts them.

WHY THIS EXISTS (feature 231, GM 2026-09-12: *"if we are supposed to snapshot the pool before I make
verify, then it should not be on you to remember to do that. That should just happen automatically"*).
The gate's roll cache evicts a pool map's standing `.png` and `.html` when it regenerates the map, so a
settlement-review dispatched beside a gate loses its artifacts mid-review - on feature 228 the reviewer
spent minutes waiting for renders that never came back and re-rendered the SVGs itself. Feature 223's
practice was to snapshot the pool by hand before `make verify`; this makes it the tooling's job. Taken
wherever a review is found owed at gate time: by `make verify`, and by the pair guard on every gate shape
it permits.

Usage: _review_snapshot.py --root CLONE [--mirror MAIN] MAP...
  copies MAP.json .svg .png .html .notes.md from the clone's pool into <CLONE>/.git/review-snapshot/MAP/clone/
  and main's copies from the mirror into .../MAP/main/, clearing that map's previous snapshot first; prints
  one line per map naming both directories and every file the clone did not have (a render not
  regenerated is NAMED, never silently skipped).
"""

from __future__ import annotations

import argparse
import shutil
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

SKILL = ".claude/skills/diagram"
TREES = ("pool", "legacy-hand-authored-pool")
#: what a reviewer reads of a map, in the order it is listed
SUFFIXES = (".json", ".svg", ".png", ".html", ".notes.md")


def map_dir(tree_root: Path, name: str) -> Path | None:
    """The folder of map `name` under either pool tree of `tree_root`, or None."""
    for tree in TREES:
        for d in sorted((tree_root / SKILL / tree).glob(f"*/{name}")):
            if d.is_dir():
                return d
    return None


def snapshot(root: Path, mirror: Path | None, names: Sequence[str]) -> list[dict[str, Any]]:
    """Copy each named map's files from `root` (the clone) and `mirror` (main) into the clone's
    `.git/review-snapshot/<name>/{clone,main}/`. Returns one record per map: the two directories (main's
    None when there is no mirror or main has no such map) and the suffixes each side lacked."""
    out: list[dict[str, Any]] = []
    for name in names:
        dest = root / ".git" / "review-snapshot" / name
        if dest.exists():
            shutil.rmtree(dest)
        rec: dict[str, Any] = {"map": name, "clone": None, "main": None, "missing": [], "main_missing": []}
        for side, tree, key in (("clone", root, "missing"), ("main", mirror, "main_missing")):
            src = map_dir(tree, name) if tree is not None else None
            if src is None:
                rec[key] = list(SUFFIXES)
                continue
            target = dest / side
            target.mkdir(parents=True, exist_ok=True)
            for suffix in SUFFIXES:
                f = src / f"{name}{suffix}"
                if f.is_file():
                    shutil.copy2(f, target / f.name)
                else:
                    rec[key].append(suffix)
            rec[side] = str(target)
        out.append(rec)
    return out


def describe(rec: dict[str, Any]) -> str:
    """One line per map: where each side is, and what the clone did not have."""
    clone = rec["clone"] or "not in the clone's pool"
    main = rec["main"] or "unavailable (no mirror, or main has no such map)"
    missing = f" (missing in the clone: {' '.join(rec['missing'])} - regenerate it with make map)" if rec["missing"] and rec["clone"] else ""
    return f"snapshot {rec['map']}: clone {clone}{missing} | main {main}"


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True, help="the clone")
    ap.add_argument("--mirror", default=None, help="main's tree (default: the parent of the clone's .clones/, when it has one)")
    ap.add_argument("names", nargs="+", help="the maps whose manifest moved")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    mirror = Path(args.mirror) if args.mirror else None
    if mirror is None and ".clones" in root.parts:
        mirror = Path(*root.parts[: root.parts.index(".clones")])
    for rec in snapshot(root, mirror, args.names):
        print(describe(rec))
    return 0


if __name__ == "__main__":
    sys.exit(main())
