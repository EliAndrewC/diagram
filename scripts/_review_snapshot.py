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

PER UNIT, NOT PER MAP (feature 294). A review is owed per OCCASION now (`_review_owed.py`): a unit is
`<check>:<subject>`, reviewed on one map or sheet. The snapshot is that map's or sheet's files, and the prompt is the
CHECK's - a glyph check is told the element and why it is owed, a whole-map review that the map is new.

Usage: _review_snapshot.py --root CLONE [--mirror MAIN] [--key ENGINE_KEY] UNIT...
  for each owed unit slug, copies its map's or sheet's .json .svg .png .html .notes.md from the clone's pool into
  <CLONE>/.git/review-snapshot/UNIT/clone/ and main's copies from the mirror into .../UNIT/main/, clearing the unit's
  previous snapshot first; writes <CLONE>/.git/review-snapshot/UNIT/dispatch.md; prints one line per unit naming both
  directories, every file the clone did not have (a render not regenerated is NAMED, never silently skipped) and the
  prompt file.
"""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

TREES = ("pool", "legacy-hand-authored-pool")
#: what a reviewer reads of a map or sheet, in the order it is listed
SUFFIXES = (".json", ".svg", ".png", ".html", ".notes.md")


def map_dir(tree_root: Path, name: str) -> Path | None:
    """The folder of map or sheet `name` under either pool tree of `tree_root`, or None."""
    for tree in TREES:
        for d in sorted((tree_root / tree).glob(f"*/{name}")):
            if d.is_dir():
                return d
    return None


def owed_module() -> Any:
    """`_review_owed.py`, loaded by path (a hook calls this script; no package to import from)."""
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("review_owed_for_snapshot", here / "_review_owed.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    prior, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = prior
    return mod


#: what each check is asked, per its contract (`.claude/agents/<check>.md`)
ASK = {
    "settlement-review": "the WHOLE-MAP review of {on}: {occasion}. Run your contract's whole-map sweeps on it.",
    "building-review": "the review of the sheet {on}: {occasion}. Run the sections of your contract this occasion owes.",
    "glyph-check": "the glyph check of the element {subject!r}, on {on}: {occasion}. Judge that element where it stands on this map - nothing else on the map is under review.",
    "size-audit": "the size audit of {subject!r} on {on}: {occasion}. Anchor that kind's size; nothing else is under review.",
    "fix-check": "the fix check on {on}: {occasion}. Answer the GM's complaint at fit zoom first, then whether the fix fired and whether its record can bear it.",
}

DISPATCH = """UNIT: {slug}
{check} - {ask}

This prompt was written by the tooling (feature 294): one agent per owed unit, and the pair guard refuses a dispatch that
names more than one. Do not review anything else - its own agent has it - and wait for nothing but your own work.

Clone: {clone} (the directory holding `.git/review-snapshot/`; run the `make` targets from its
``). Engine key: {key}. The gate went green on this content before this dispatch.

Snapshot - read THESE:
  after (the clone): {after}{missing}
  before (main):     {before}

Follow your contract end to end, then `make review-verdict UNIT={slug} VERDICT=<PASS|NEEDS-WORK|NOT-REVIEWABLE> [FINDINGS=<json file>]`
as your last act, and quote the line it prints.
"""


def dispatch_text(rec: dict[str, Any], root: Path, key: str) -> str:
    """The one-unit prompt a session hands the Agent tool (feature 248 FR-002, per unit since feature 294)."""
    missing = f"  (missing in the clone: {' '.join(rec['missing'])} - regenerate it with make map)" if rec["missing"] and rec["clone"] else ""
    ask = ASK[rec["check"]].format(on=rec["on"] or "no map draws it", subject=rec["subject"], occasion=rec["occasion"])
    return DISPATCH.format(
        slug=rec["unit"],
        check=rec["check"],
        ask=ask,
        clone=root,
        key=key or "not computed",
        after=rec["clone"] or "not in the clone's pool",
        missing=missing,
        before=rec["main"] or "unavailable (no mirror, or main has no such map)",
    )


def snapshot(root: Path, mirror: Path | None, units: Sequence[Any], key: str = "") -> list[dict[str, Any]]:
    """Copy each unit's map or sheet from `root` (the clone) and `mirror` (main) into the clone's
    `.git/review-snapshot/<slug>/{clone,main}/` and write its `dispatch.md`. Returns one record per unit: the two
    directories (main's None when there is no mirror or main has no such map), the suffixes each side lacked, and the
    prompt file."""
    out: list[dict[str, Any]] = []
    for unit in units:
        dest = root / ".git" / "review-snapshot" / unit.slug
        if dest.exists():
            shutil.rmtree(dest)
        rec: dict[str, Any] = {"unit": unit.slug, "check": unit.check, "subject": unit.subject, "on": unit.on, "occasion": unit.occasion,
                               "clone": None, "main": None, "missing": [], "main_missing": [], "dispatch": None}
        for side, tree, lack in (("clone", root, "missing"), ("main", mirror, "main_missing")):
            src = map_dir(tree, unit.on) if tree is not None and unit.on else None
            if src is None:
                rec[lack] = list(SUFFIXES)
                continue
            target = dest / side
            target.mkdir(parents=True, exist_ok=True)
            for suffix in SUFFIXES:
                f = src / f"{unit.on}{suffix}"
                if f.is_file():
                    shutil.copy2(f, target / f.name)
                elif not (suffix == ".json" and (src / f"{unit.on}.svg").is_file()):  # a Mode A sheet has no manifest; a map always has one
                    rec[lack].append(suffix)
            rec[side] = str(target)
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "dispatch.md").write_text(dispatch_text(rec, root, key))
        rec["dispatch"] = str(dest / "dispatch.md")
        out.append(rec)
    return out


def describe(rec: dict[str, Any]) -> str:
    """One line per unit: where each side is, what the clone did not have, and the prompt file."""
    clone = rec["clone"] or "not in the clone's pool"
    main = rec["main"] or "unavailable (no mirror, or main has no such map)"
    missing = f" (missing in the clone: {' '.join(rec['missing'])} - regenerate it with make map)" if rec["missing"] and rec["clone"] else ""
    prompt = f" | prompt {rec['dispatch']}" if rec.get("dispatch") else ""
    return f"snapshot {rec['unit']} (on {rec['on'] or '?'}): clone {clone}{missing} | main {main}{prompt}"


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True, help="the clone")
    ap.add_argument("--mirror", default=None, help="main's tree (default: the parent of the clone's .clones/, when it has one)")
    ap.add_argument("--key", default="", help="the engine key the dispatch prompt quotes (feature 248)")
    ap.add_argument("units", nargs="+", help="the owed unit slugs (`_review_owed.py`)")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    mirror = Path(args.mirror) if args.mirror else None
    if mirror is None and ".clones" in root.parts:
        mirror = Path(*root.parts[: root.parts.index(".clones")])
    _, units, _ = owed_module().owed(root)
    by_slug = {u.slug: u for u in units}
    unknown = [s for s in args.units if s not in by_slug]
    if unknown:
        print(f"_review_snapshot: not owed by this delta: {' '.join(unknown)}", file=sys.stderr)
        return 2
    for rec in snapshot(root, mirror, [by_slug[s] for s in args.units], args.key):
        print(describe(rec))
    return 0


if __name__ == "__main__":
    sys.exit(main())
