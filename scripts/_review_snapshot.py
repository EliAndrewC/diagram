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

AND WRITES THE DISPATCH PROMPT, ONE PER MAP (feature 248, GM 2026-09-14). Feature 247's review was one agent
handed four maps, serialized - 11 of the feature's 36 minutes - because the instruction the tooling printed
was one line naming all four, and a session following it literally dispatches one agent. The GM: *"whatever
the tooling is currently doing to kick off reviews should be modified to make the correct thing happen
automatically"*. So each map's snapshot carries `dispatch.md`, the whole prompt for THAT map's agent, and the
guard refuses a dispatch naming more than one map (pair-hooks.sh); the session's part is to send N Agent
calls in one message, each with one file's contents.

Usage: _review_snapshot.py --root CLONE [--mirror MAIN] [--key ENGINE_KEY] MAP...
  copies MAP.json .svg .png .html .notes.md from the clone's pool into <CLONE>/.git/review-snapshot/MAP/clone/
  and main's copies from the mirror into .../MAP/main/, clearing that map's previous snapshot first; writes
  <CLONE>/.git/review-snapshot/MAP/dispatch.md; prints one line per map naming both directories, every file
  the clone did not have (a render not regenerated is NAMED, never silently skipped) and the prompt file.
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


DISPATCH = """Settlement review of ONE map: {map}. This prompt was written by the tooling (feature 248): one agent
per map, and the pair guard refuses a dispatch that names more than one. Do not review any other map -
its own agent has it - and do not wait for anything but your own work.

Clone: {clone} (the directory holding `.git/review-snapshot/`; run the `make` targets from its
`.claude/skills/diagram/`). Engine key: {key}. The gate is running beside this review.

Snapshot - read THESE, the gate's cache evicts the pool's renders mid-run:
  after (the clone): {after}{missing}
  before (main):     {before}

Scope: DELTA - what moved on {map} against main, what it moved, and what the delta made incoherent;
confirm what moved from the two manifests first, and say in one line which sweeps you skipped.

Follow your contract end to end: the first stage (`make review-paired-gate`; the map's last verdict and
what disposes of each finding), the review, then `make review-verdict MAP={map} VERDICT=<PASS|NEEDS-WORK|NOT-REVIEWABLE> [FINDINGS=<json file>]`
as your last act, and quote the line it prints.
"""


def dispatch_text(rec: dict[str, Any], root: Path, key: str) -> str:
    """The one-map prompt a session hands the Agent tool for `rec['map']` (feature 248 FR-002)."""
    missing = f"  (missing in the clone: {' '.join(rec['missing'])} - regenerate it with make map)" if rec["missing"] and rec["clone"] else ""
    return DISPATCH.format(
        map=rec["map"],
        clone=root,
        key=key or "not computed",
        after=rec["clone"] or "not in the clone's pool",
        missing=missing,
        before=rec["main"] or "unavailable (no mirror, or main has no such map)",
    )


def snapshot(root: Path, mirror: Path | None, names: Sequence[str], key: str = "") -> list[dict[str, Any]]:
    """Copy each named map's files from `root` (the clone) and `mirror` (main) into the clone's
    `.git/review-snapshot/<name>/{clone,main}/` and write its `dispatch.md`. Returns one record per map:
    the two directories (main's None when there is no mirror or main has no such map), the suffixes each
    side lacked, and the prompt file."""
    out: list[dict[str, Any]] = []
    for name in names:
        dest = root / ".git" / "review-snapshot" / name
        if dest.exists():
            shutil.rmtree(dest)
        rec: dict[str, Any] = {"map": name, "clone": None, "main": None, "missing": [], "main_missing": [], "dispatch": None}
        for side, tree, lack in (("clone", root, "missing"), ("main", mirror, "main_missing")):
            src = map_dir(tree, name) if tree is not None else None
            if src is None:
                rec[lack] = list(SUFFIXES)
                continue
            target = dest / side
            target.mkdir(parents=True, exist_ok=True)
            for suffix in SUFFIXES:
                f = src / f"{name}{suffix}"
                if f.is_file():
                    shutil.copy2(f, target / f.name)
                else:
                    rec[lack].append(suffix)
            rec[side] = str(target)
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "dispatch.md").write_text(dispatch_text(rec, root, key))
        rec["dispatch"] = str(dest / "dispatch.md")
        out.append(rec)
    return out


def describe(rec: dict[str, Any]) -> str:
    """One line per map: where each side is, what the clone did not have, and the prompt file."""
    clone = rec["clone"] or "not in the clone's pool"
    main = rec["main"] or "unavailable (no mirror, or main has no such map)"
    missing = f" (missing in the clone: {' '.join(rec['missing'])} - regenerate it with make map)" if rec["missing"] and rec["clone"] else ""
    prompt = f" | prompt {rec['dispatch']}" if rec.get("dispatch") else ""
    return f"snapshot {rec['map']}: clone {clone}{missing} | main {main}{prompt}"


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True, help="the clone")
    ap.add_argument("--mirror", default=None, help="main's tree (default: the parent of the clone's .clones/, when it has one)")
    ap.add_argument("--key", default="", help="the engine key the dispatch prompt quotes (feature 248)")
    ap.add_argument("names", nargs="+", help="the maps whose manifest moved")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    mirror = Path(args.mirror) if args.mirror else None
    if mirror is None and ".clones" in root.parts:
        mirror = Path(*root.parts[: root.parts.index(".clones")])
    for rec in snapshot(root, mirror, args.names, args.key):
        print(describe(rec))
    return 0


if __name__ == "__main__":
    sys.exit(main())
