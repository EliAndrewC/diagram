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

A RENDERING-ONLY FEATURE OWES NO REVIEW (feature 248, GM 2026-09-14). The ledger for the week before shows
the review catching a defect on every pass over a LAYOUT feature and nothing on a map for any rendering or
performance one; the GM asked *"whether we can skip it for features like this one specifically, i.e.
changing a glyph rendering convention rather than tweaking actual map features to comport to historical
norms"*. Every task already carries the classification (`research: rendering | physical | procedure`), so
the waiver keys on it: when EVERY active feature's tasks are all `research: rendering`, no map is owed and
the reason names the features. The active features are DERIVED the way `sync-with-main.sh` derives the
in-progress feature - the pointer in `.specify/feature.json` AND every `specs/NNN-*/tasks.md` with an open
box that the delta against the merge base touches - because that rule exists so a check cannot be evaded
by not setting the pointer, and a waiver REMOVES a check: it takes the conjunction where an obligation
takes the union (spec D7). A `procedure` feature that moves a manifest changed the layout by a mechanism
nobody researched, which is the case the review caught on features 226 and 227, so it is not waived (D3).

Usage: _review_owed.py [--root DIR] [--why]
  prints one map name per line (empty when nothing moved or the waiver holds); `--why` prints the one-line
  ruling instead. Exit 0 either way; 1 when DIR is not a git repository.
"""

from __future__ import annotations

import argparse
import json
import re
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


def pool_map_names(root: Path) -> list[str]:
    """Every map folder of both pool trees - the names a dispatch can ask a review of (feature 248 FR-001:
    a multi-map dispatch is counted against ALL of them, owed or not)."""
    names: set[str] = set()
    for tree in TREES:
        for d in (root / SKILL / tree).glob("*/*"):
            if d.is_dir() and (d / f"{d.name}.json").is_file():
                names.add(d.name)
    return sorted(names)


# GUARD_EDIT_OK: feature 248 - the task line as `tests/test_task_research_boxes.py` reads it (`- [ ] T01 ...` then
# `research: <class>` in the entry), copied rather than imported because a guard cannot import a test module.
_TASK = re.compile(r"^\s*- \[(?P<tick>[ x])\] (?P<id>T\d+)\b", re.M)
_CLASS = re.compile(r"^\s*research:\s*(?P<cls>[a-z]+)\s*$", re.M)


def rendering_only(tasks_text: str) -> int | None:
    """The number of tasks when every task in a `tasks.md` is classified `research: rendering`; None when
    there are no tasks, or any task carries another class or none."""
    starts = list(_TASK.finditer(tasks_text))
    if not starts:
        return None
    for k, m in enumerate(starts):
        end = starts[k + 1].start() if k + 1 < len(starts) else len(tasks_text)
        cls = _CLASS.search(tasks_text[m.start() : end])
        if not cls or cls.group("cls") != "rendering":
            return None
    return len(starts)


def active_features(root: Path, base: str) -> list[str]:
    """The feature directories this delta is the work of, DERIVED as `sync-with-main.sh` derives the
    in-progress feature and then WIDENED: the pointer in `.specify/feature.json`, plus every `specs/NNN-*/`
    the delta against `base` touches (committed, staged or unstaged) that has a `tasks.md` - ticked or not.
    The in-progress rule wants OPEN boxes because it refuses an unfinished feature; at push time it has
    guaranteed there are none, so a waiver keyed on open boxes would rest on the pointer alone exactly
    where it decides whether a map ships (spec D7, the plan review's aside). Relative paths, sorted; a
    pointer naming a directory with no `tasks.md` is still listed (it is a feature the session declares,
    and the waiver then refuses it)."""
    found: set[str] = set()
    try:
        pointer = str(json.loads((root / ".specify" / "feature.json").read_text()).get("feature_directory", "")).rstrip("/")
    except (OSError, ValueError):
        pointer = ""
    if pointer:
        found.add(pointer)
    touched = (_git(root, "diff", "--name-only", base, "--", "specs") or "") if base else ""
    for path in touched.splitlines():
        parts = Path(path).parts
        if len(parts) >= 2 and parts[0] == "specs" and (root / "specs" / parts[1] / "tasks.md").is_file():
            found.add(f"specs/{parts[1]}")
    return sorted(found)


def waiver(root: Path, base: str) -> str | None:
    """The rendering-only waiver's reason when EVERY active feature is rendering-only, else None."""
    features = active_features(root, base)
    if not features:
        return None
    counts: list[str] = []
    for f in features:
        tasks = root / f / "tasks.md"
        n = rendering_only(tasks.read_text()) if tasks.is_file() else None
        if n is None:
            return None
        counts.append(f"{f} ({n} task{'s' if n != 1 else ''})")
    return f"rendering-only feature(s) {', '.join(counts)} - every task research: rendering, no settlement-review owed (feature 248)"


def owed(root: Path) -> tuple[str, list[str], str | None]:
    """(the base's description, the maps owed a review, the waiver's reason when one held)."""
    desc, names = changed_maps(root)
    if not names:
        return desc, names, None
    base, _ = base_of(root)
    why = waiver(root, base)
    return desc, ([] if why else names), why


def ruling(desc: str, names: Sequence[str], why: str | None = None) -> str:
    """The one-line answer a person or a guard message quotes."""
    if why:
        return why
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
    desc, names, why = owed(Path(top))
    if args.why:
        print(ruling(desc, names, why))
    else:
        for name in names:
            print(name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
