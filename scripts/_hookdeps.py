#!/usr/bin/env python3
"""What each guard suite actually depends on, derived transitively (feature 172).

WHY (GM 2026-08-30): *"could we not do something similar where if the hooks have not changed, then we
do not run the hooks tests?"* - and, once told that this exists and costs 0 s while the dependency set
is too coarse, *"Go ahead and do the dependency refinement as its own feature."*

WHAT WAS WRONG. Every suite was declared to depend on all four shared helpers, so a one-line fix to
`_gatecost.py` - which exactly two guards reference - re-ran all 21 suites.

THE SUBTLETY, AND IT IS THE WHOLE FEATURE: the dependency is TRANSITIVE. `_guardlog.sh`'s
`escape_or_refuse` calls `_hookmatch.py` (feature 170), so a guard that names only `_guardlog.sh`
depends on `_hookmatch.py` whether it says so or not. A direct-reference-only derivation would
UNDER-RUN and pass a suite that a change had broken - which is strictly worse than the over-running it
replaces, because over-running is merely slow. Measured over the real graph:

    _hookmatch.py        20 of 21 suites   (was 21 - saves 1)
    _guardlog.sh         19 of 21          (was 21 - saves 2)
    _gatecost.py          2 of 21          (was 21 - saves 19)
    test_hooks_cases.py   3 of 21          (was 21 - saves 18)

So the refinement pays on the two helpers that are rarely touched and barely pays on the two that
churn - which is why feature 172 also runs the suites in parallel. Recorded here so nobody re-derives
the disappointment.
"""

from __future__ import annotations

import hashlib
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent

# WHOLE-TREE IS AN OUTPUT OF THE RULE WHERE IT CAN BE, AND A STATED LIMIT WHERE IT CANNOT (round 1 of
# this feature's review: a carve-out asserted rather than derived is the feature-126 shape, and it
# would preserve for these three exactly the over-running the GM asked to end).
#
#   `gate-stamp.py` DERIVES to the whole tree: it globs `scripts/*.sh scripts/*.py`, so `_globs_tree`
#   below picks it up with no special case at all.
#
#   `sync-with-main.sh` and `review-gate.sh` are held here DELIBERATELY, and the reason is a limit of
#   reference-graph derivation rather than a preference: their suites exercise the push path end to
#   end, and that path resolves paths at RUN TIME from `$ROOT` and `$MAIN` (`sync-with-main.sh:43`,
#   `:53-55`), against trees the fixture builds. A static reader cannot see which scripts a run will
#   reach; it names 11 siblings and reaches more. Over-running two suites is the safe side of a
#   derivation that cannot see the edge, and these two are among the slowest, which is precisely why
#   the honest thing is to say so rather than to quietly narrow them.
HELD_WHOLE_TREE = {"sync-with-main.sh", "review-gate.sh"}


def _globs_tree(name: str) -> bool:
    """Does this file read the whole scripts directory? Then it depends on the whole of it."""
    body = _text(name)
    return "scripts/*.sh" in body or "scripts/*.py" in body

# A reference is a file NAME appearing in another file's text. That covers every shape this tree
# uses - `. "$X/_guardlog.sh"`, `"$X/_hookmatch.py" escape`, `spec_from_file_location(..., "_ratchet.py")`
# and a python import - without parsing four languages. It over-approximates (a name in a comment
# counts), which is the safe direction here: over-running costs time, under-running costs correctness.
_SHARED = ("_hookmatch.py", "_guardlog.sh", "_gatecost.py", "test_hooks_cases.py", "_hookdeps.py")


def _text(name: str) -> str:
    p = HERE / name
    try:
        return p.read_text()
    except OSError:
        return ""


def closure(seeds: set[str]) -> set[str]:
    """Every shared helper reachable from `seeds`, following references through helpers."""
    seen: set[str] = set()
    stack = list(seeds)
    while stack:
        name = stack.pop()
        if name in seen:
            continue
        seen.add(name)
        body = _text(name)
        for helper in _SHARED:
            if helper != name and helper in body and helper not in seen:
                stack.append(helper)
    return seen


def deps_for(guard: str) -> list[str]:
    """The files whose contents are this suite's freshness key, sorted for a stable hash."""
    suite = "test-" + (guard[:-3] + ".sh" if guard.endswith(".py") else guard)
    if guard in HELD_WHOLE_TREE or _globs_tree(guard) or _globs_tree(suite):
        return sorted(p.name for p in HERE.glob("*.sh")) + sorted(p.name for p in HERE.glob("*.py"))
    return sorted(closure({guard, suite}))


def key_for(guard: str) -> str:
    h = hashlib.sha256()
    for name in deps_for(guard):
        h.update(_text(name).encode())
    return h.hexdigest()[:16]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        # `<guard> <sha>` per line, one process for every suite - the freshness phase runs this once.
        guards = sorted(p.name for p in HERE.glob("*-hooks.sh") if not p.name.startswith("test-"))
        for g in guards + sorted(HELD_WHOLE_TREE | {"gate-stamp.py"}):
            print(g, key_for(g))
    elif len(sys.argv) > 2 and sys.argv[1] == "--deps":
        print(" ".join(deps_for(sys.argv[2])))
    elif len(sys.argv) > 1:
        print(key_for(sys.argv[1]))
