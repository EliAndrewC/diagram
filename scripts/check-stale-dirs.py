#!/usr/bin/env python3
"""Fail when a directory in an IMPORTABLE tree has nothing left in it but `__pycache__`.

WHY (GM 2026-09-05): a directory that holds no source and no `__init__.py` is still an importable
PEP 420 NAMESPACE PACKAGE. `import l7r.diagram.check_village` succeeds against it and resolves to an
empty module, so a long-lived clone behaves differently from a fresh one - and the difference is
silent in the direction that matters, because the local run is the one that PASSES.

This is the same hazard feature 175 hit from the other side, recorded in its own memory as *"a stale
untracked directory is an importable namespace package, so local runs PASSED what a fresh clone
fails, which is the worktree hazard inverted and worse"*. There it was caught by a paid remote
build failing. Here it is caught in 5 ms.

FOUND ON THE DAY THIS WAS WRITTEN, all four left by feature 166's deletion of the check battery on
2026-08-30 and all four carrying zero tracked files:

    l7r/diagram/check_village        <- and this one was IMPORTABLE, verified with importlib
    tests/tier_town/check_village
    tests/tier_town/tools
    tests/tier_city/check_village

THE RULE IS DELIBERATELY NARROW, because a guard that fires on correct work teaches a session to
bypass every guard (CLAUDE.md). A directory is stale only when it has NO files of its own AND its
only subdirectories are `__pycache__`. A real package has source. A directory being built has `.py`
files in it. A FRESH CLONE HAS NO `__pycache__` AT ALL, so this finds nothing there - which is
correct: the hazard exists only in a clone that has been around long enough to accumulate bytecode.

IT REFUSES, IT DOES NOT DELETE (GM 2026-09-05). Removing directories is destructive and irreversible
for anything untracked that happens to be inside one, so this prints the exact `rm -rf` and a person
runs it - the `STAY A REFUSAL` rung of feature 164's ladder, where the action cannot be undone.

SCOPED TO THE IMPORTABLE TREES on the GM's ruling, same date. Outside `l7r/` and `tests/` an empty
leftover directory is untidy but cannot be imported, so it is not this guard's business; widening the
scope would buy noise rather than safety.

Run `--selftest` first (the Makefile's `lint` and sync-with-main.sh both do): it plants a stale
directory in a temporary tree and proves the scan fires on it, and that a package with source and a
directory holding a real file both pass. A checker that cannot fail is worth nothing, and this
project has been bitten by exactly that - see `check-duplicate-defs.py`, which the same rule covers.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# The trees whose directories can be reached by an import. `l7r` is a namespace portion and `tests`
# is a package rooted at the skill dir, so both are on the import path during a run.
IMPORTABLE = ("l7r", "tests")
SKILL = Path(".claude/skills/diagram")
# Never descend into these: `.git` is enormous and irrelevant, and `.clones` holds other sessions'
# checkouts, which are not this tree's business and would multiply every finding by the clone count.
SKIP = {".git", ".clones", "node_modules", ".venv", "venv", "__pycache__"}


def stale_dirs(root: Path) -> list[Path]:
    """Directories under the importable trees whose only remaining contents are `__pycache__`."""
    found: list[Path] = []
    for tree in IMPORTABLE:
        base = root / SKILL / tree
        if not base.is_dir():
            base = root / tree  # the checker also runs against a bare skill dir (the selftest does)
        if not base.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(base, topdown=True):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP or d == "__pycache__")
            here = Path(dirpath)
            if here.name == "__pycache__":
                dirnames[:] = []
                continue
            if filenames:
                continue
            subs = [d for d in dirnames]
            if subs and all(d == "__pycache__" for d in subs):
                found.append(here)
    return found


def report(found: list[Path], root: Path) -> None:
    print("\nSTALE DIRECTORIES: nothing left in these but __pycache__.\n")
    for p in found:
        try:
            rel = p.relative_to(root)
        except ValueError:
            rel = p
        print(f"    {rel}")
    print(
        "\nEach one has no source and no __init__.py, and is therefore still an importable PEP 420\n"
        "NAMESPACE PACKAGE - `import` against it SUCCEEDS and resolves to an empty module. So this\n"
        "clone behaves differently from a fresh one, and it is the local run that passes, which is\n"
        "the direction that hides the bug (the hazard feature 175 paid a remote build to discover).\n"
        "\nThey are almost always what is left after a package's files were deleted from git.\n"
        "Nothing here deletes them: removing a directory is irreversible for anything untracked\n"
        "inside it, so a person runs the command. Check each is what you think it is, then:\n"
    )
    for p in found:
        try:
            rel = p.relative_to(root)
        except ValueError:
            rel = p
        print(f"    rm -rf {rel}")
    print("\n(scripts/check-stale-dirs.py; GM 2026-09-05)\n")


def selftest() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        skill = root / SKILL
        # (1) a genuinely stale directory - source deleted, bytecode left behind
        dead = skill / "l7r" / "diagram" / "gone"
        (dead / "__pycache__").mkdir(parents=True)
        (dead / "__pycache__" / "mod.cpython-314.pyc").write_bytes(b"\x00")
        # (2) a real package - has source, must NOT fire
        live = skill / "l7r" / "diagram" / "alive"
        (live / "__pycache__").mkdir(parents=True)
        (live / "mod.py").write_text("x = 1\n", encoding="utf-8")
        # (3) a directory holding a real file and no bytecode - must NOT fire
        (skill / "tests" / "data").mkdir(parents=True)
        (skill / "tests" / "data" / "fixture.json").write_text("{}", encoding="utf-8")
        # (4) outside the importable trees - not this guard's business
        outside = skill / "pool" / "leftover"
        (outside / "__pycache__").mkdir(parents=True)

        got = {p.name for p in stale_dirs(root)}
        if got != {"gone"}:
            print(f"check-stale-dirs: SELFTEST FAILED - expected exactly the stale dir, got {sorted(got)}", file=sys.stderr)
            return 1
    print("check-stale-dirs: selftest ok (stale fires; a real package, a data dir and a non-importable tree all pass)")
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--selftest":
        return selftest()
    root = Path(argv[0] if argv else ".").resolve()
    found = stale_dirs(root)
    if not found:
        return 0
    report(found, root)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
