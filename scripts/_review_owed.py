#!/usr/bin/env python3
"""Which pool maps' LAYOUT moved against main - the one scripted answer to "is a settlement-review owed".

WHY THIS EXISTS (feature 231, GM 2026-09-12). Feature 228 changed one path's `d` so a lit dike no longer
tinted the pond inside it; its manifest was byte-identical, and the pair guard still owed it a
settlement-review, which took 18.7 of the feature's 32 minutes re-judging ink that had not moved. The GM:
*"if there are no changes to the actual way that the settlement is laid out, then we should not need to
re review the settlement because we're just rereviewing things that have not changed ... the thing that
determines whether a settlement review is necessary is probably some kind of scripted check."*

WHAT "THE LAYOUT MOVED" IS. A pool map's manifest (`pool/*/*/*.json`, `legacy-hand-authored-pool/*/*/*.json`)
is the record of every placed feature's geometry; the SVG, the PNG and the page are derived from it and
from the drawing code. `review-gate.sh` already uses the manifest as the unit at push time, and the
gate's pool phase regenerates a shipped map's manifest IN PLACE when the engine key moved, so by the time
a gate is green the manifests in the tree are the layout the engine now produces. A manifest that differs
from the merge base with `origin/main` - committed, staged, unstaged or untracked (a new map) - is a
layout that moved. What this cannot see is a change to a glyph's FORM with the same manifest; that is the
GM's to look at (their 2026-08-29 ruling that they read one changed map faster than the agent does), and
the waiver text says so.

ASKED FRESH, NEVER CACHED. Every decision point (the pair guard's gate branch, its stop branch, `make verify`)
runs this again, because the gate's own pool phase can move a manifest between the gate's start and the
turn's end.

Usage: _review_owed.py [--root DIR] [--why]
  prints one map name per line (empty when nothing moved); `--why` prints the one-line ruling instead.
  Exit 0 either way; 1 when DIR is not a git repository.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

SKILL = ".claude/skills/diagram"
TREES = ("pool", "legacy-hand-authored-pool")
#: git pathspecs for every manifest in both pool trees (fnmatch without FNM_PATHNAME: `*` spans `/`)
MANIFESTS = tuple(f"{SKILL}/{tree}/*/*/*.json" for tree in TREES)


def _git(root: Path, *args: str) -> str | None:
    """stdout of `git -C root args`, or None when git refused."""
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    return p.stdout.strip() if p.returncode == 0 else None


def base_of(root: Path) -> tuple[str, str]:
    """(ref, description): the merge base of HEAD with origin/main; HEAD when there is no origin/main;
    '' for a repository with no commits (everything present is then new)."""
    head = _git(root, "rev-parse", "--verify", "-q", "HEAD")
    if not head:
        return "", "no commits yet"
    if _git(root, "rev-parse", "--verify", "-q", "origin/main"):
        mb = _git(root, "merge-base", "HEAD", "origin/main")
        if mb:
            return mb, f"origin/main (merge base {mb[:8]})"
    return head, f"HEAD ({head[:8]}; no origin/main)"


def changed_maps(root: Path) -> tuple[str, list[str]]:
    """(the base's description, the names of every map whose manifest differs from it or is untracked)."""
    base, desc = base_of(root)
    names: set[str] = set()
    if base:
        diff = _git(root, "diff", "--name-only", base, "--", *MANIFESTS) or ""
        names |= {Path(p).stem for p in diff.splitlines() if p}
    untracked = _git(root, "ls-files", "--others", "--exclude-standard", "--", *MANIFESTS) or ""
    names |= {Path(p).stem for p in untracked.splitlines() if p}
    return desc, sorted(names)


def ruling(desc: str, names: Sequence[str]) -> str:
    """The one-line answer a person or a guard message quotes."""
    if not names:
        return f"no pool manifest moved against {desc}"
    return f"layout moved against {desc}: {' '.join(names)}"


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="the clone (default: the cwd's repository)")
    ap.add_argument("--why", action="store_true", help="print the one-line ruling instead of the names")
    args = ap.parse_args(argv)
    top = _git(Path(args.root), "rev-parse", "--show-toplevel")
    if not top:
        print(f"_review_owed: {args.root} is not a git repository", file=sys.stderr)
        return 1
    desc, names = changed_maps(Path(top))
    if args.why:
        print(ruling(desc, names))
    else:
        for name in names:
            print(name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
