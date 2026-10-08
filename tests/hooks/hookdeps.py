#!/usr/bin/env python3
"""What each guard suite actually depends on, derived transitively (feature 172).

WHY (GM 2026-08-30): *"could we not do something similar where if the hooks have not changed, then we
do not run the hooks tests?"* - and, once told that this exists and costs 0 s while the dependency set
is too coarse, *"Go ahead and do the dependency refinement as its own feature."*

WHAT WAS WRONG. Every suite was declared to depend on all four shared helpers, so a one-line fix to
`gatecost.py` - which exactly two guards reference - re-ran all 21 suites.

THE SUBTLETY, AND IT IS THE WHOLE FEATURE: the dependency is TRANSITIVE. `guardlog.sh`'s
`escape_or_refuse` calls `hookmatch.py` (feature 170), so a guard that names only `guardlog.sh`
depends on `hookmatch.py` whether it says so or not. A direct-reference-only derivation would
UNDER-RUN and pass a suite that a change had broken - which is strictly worse than the over-running it
replaces, because over-running is merely slow. Measured over the real graph:

    hookmatch.py        20 of 21 suites   (was 21 - saves 1)
    guardlog.sh         19 of 21          (was 21 - saves 2)
    gatecost.py          2 of 21          (was 21 - saves 19)
    test_hooks_cases.py   3 of 21          (was 21 - saves 18)

THOSE FIGURES ARE THE MOTIVATION, MEASURED BEFORE THE SPLIT - not the current state. After
`hookmatch.py` became three leaves the live numbers are `gatecost.py` 4 of 21, the make/rewrite
family 5, and `guardlog.sh`/`hm_escape.py` 20 (the two whole-tree entries are in every count).
`specs/172-hooks-test-deps/research.md` R5 and R9 carry the current table.

So the refinement pays on the two helpers that are rarely touched and barely pays on the two that
churn - which is why feature 172 also runs the suites in parallel. Recorded here so nobody re-derives
the disappointment.
"""

from __future__ import annotations

import ast
import functools
import hashlib
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCRIPTS = ROOT / "scripts"

# NAMES ARE STILL THE KEY, NOW RESOLVED BY AN INDEX (2026-10-08). The guards, their helpers and their suites lived in one
# flat scripts/ until the GM asked for it organized; they now sit in scripts/<purpose>/ and tests/hooks/. Every basename
# is unique across both (the move checked it), so a name still identifies one file and the reference scan below is
# unchanged - only "where is the file called X" asks this index instead of HERE.
_INDEX: dict[str, pathlib.Path] = {
    p.name: p
    for p in sorted([*SCRIPTS.rglob("*.sh"), *SCRIPTS.rglob("*.py"), *SCRIPTS.rglob("*.txt"), *HERE.glob("*.sh"), *HERE.glob("*.py")])
    if "__pycache__" not in p.parts
}

# WHOLE-TREE IS AN OUTPUT OF THE RULE WHERE IT CAN BE, AND A STATED LIMIT WHERE IT CANNOT (round 1 of
# this feature's review: a carve-out asserted rather than derived is the feature-126 shape, and it
# would preserve for these three exactly the over-running the GM asked to end).
#
#   `gate-stamp.py` DERIVES to the whole tree: it globs `scripts/*.sh scripts/*.py`, so `_globs_tree`
#   below picks it up with no special case at all.
#
#   `sync-with-main.sh` ALONE is held here, and the reason is a limit of reference-graph derivation
#   rather than a preference: its suite exercises the push path end to end, and that path resolves
#   script paths at RUN TIME from `$ROOT` and `$MAIN` (`:43`, `:53-55`) against trees the fixture
#   builds. A static reader cannot see which scripts a run will reach; it names 11 siblings and
#   reaches more. Over-running one suite is the safe side of an edge the derivation cannot see.
#
#   `review-gate.sh` WAS held here too, under that same sentence, and round 3 of this feature's review
#   showed the sentence is false of it: it reaches exactly two scripts, both statically visible
#   (`. "$RG_HERE/../../scripts/hooks/lib/guardlog.sh"` and `"$RG_HERE/../../scripts/hooks/lib/hm_escape.py" reason-ok`), and its suite drives only
#   `review-gate.sh` itself inside its own fixtures. Everything else it touches is DATA - specs and
#   manifests - which a whole-tree hold over `scripts/` does not cover anyway. One argument stretched
#   over two unlike things, keeping for that suite exactly the over-running this feature exists to end.
#   It derives now.
HELD_WHOLE_TREE = {"sync-with-main.sh"}


def _globs_tree(name: str) -> bool:
    """Does this file read the whole scripts directory? Then it depends on the whole of it.

    IT MUST MATCH THE GLOB AS THE CODE EXPRESSES IT, not as the prose describes it. The first version
    tested for the literal `scripts/*.sh`, which in `gate-stamp.py` appears only in the module
    DOCSTRING; the line that actually globs is `"hooks": ("scripts", ("*.sh", "*.py"))`. So the row
    was right by accident of wording and a docstring reword would silently have dropped that suite
    from the whole tree to four files. Caught by round 2 of this feature's review.
    """
    body = _code(name) or _text(name)
    if "scripts/*.sh" in body or "scripts/*.py" in body:
        return True
    # the tuple form: a directory named "scripts" paired with a glob over shell and python
    return bool(re.search(r'"scripts"\s*,\s*\(\s*"\*\.sh"\s*,\s*"\*\.py"', body))

# A reference is a file NAME appearing in another file's text. That covers every shape this tree
# uses - `. "$X/../../scripts/hooks/lib/guardlog.sh"`, `"$X/../../scripts/hooks/lib/hookmatch.py" escape`, `spec_from_file_location(..., "ratchet.py")`
# and a python import - without parsing four languages. It over-approximates (a name in a comment
# counts), which is the safe direction here: over-running costs time, under-running costs correctness.
#
# AND THE HELPER SET IS ITSELF DERIVED (feature 172, caught by this feature's own change). It was a
# hardcoded tuple naming the four helpers that existed when it was written. The split then added
# `hm_shape.py`, `hm_escape.py` and `hm_make.py`, the closure did not know them, and the derivation
# silently reported that NO guard depends on the escape family - through which every guard reaches its
# escape. A hardcoded list of shared files, in the feature whose whole subject is deriving instead of
# listing. So: every `_*.py` / `_*.sh` helper in this directory, plus the shared test runner.
def _shared() -> tuple[str, ...]:
    # every file that is not itself a guard, a suite or a top-level command - the helpers were the underscore-prefixed
    # files of the flat directory, and are now everything in a purpose subdirectory that is not a guard or a gate
    names = {
        n for n, p in _INDEX.items()
        if p.parent not in (SCRIPTS, SCRIPTS / "hooks") and not n.startswith("test-") and not n.endswith("-gate.sh")
    }
    names |= {"test_hooks_cases.py", "hookrun.sh", "patch.py"}
    return tuple(sorted(names))


_SHARED = _shared()


def _text(name: str) -> str:
    p = _INDEX.get(name, HERE / name)
    try:
        return p.read_text()
    except OSError:
        return ""


def _code(name: str) -> str:
    """The file with its COMMENTS REMOVED - a mention is not a dependency (feature 172).

    Found by measuring the split and getting nothing: `hm_make.py` still showed 17 of 18 guards. The
    reason is that this repository comments heavily, and nearly every guard SAYS "detection lives in
    `hookmatch.py`" in prose - so a scan of raw text made every guard depend on every leaf, and the
    split it was built to reward looked worthless.

    That is the same mention-versus-invocation mistake the guards themselves have made six times, now
    in the thing that decides what they depend on. Whole-line comments and inline `#` comments both
    go; the risk of stripping a `#` inside a string is over-running one suite, which is the safe
    direction here and the same trade the rest of this module makes.
    """
    return _strip(name, _text(name))


# GUARD_EDIT_OK: fixing a slow derivation found while working (2026-09-27) - MEMOIZED ON THE CONTENT, not the
# name. `deps_for` over the 28 guards re-parsed the same ~40 files 253 times and ran 6,720 regex scans of
# (file, helper) pairs it had already answered: 1.8 s. Keyed on the TEXT, so an edited file - on disk, or
# the `_text` a test substitutes - is a new key and is derived afresh; nothing is answered from a stale read.
@functools.lru_cache(maxsize=None)
def _strip(name: str, raw: str) -> str:
    if name.endswith(".py"):
        # DOCSTRINGS GO TOO, and only docstrings. Every leaf of the feature-172 split opens with
        # "Split out of `hookmatch.py`", which is a triple-quoted string rather than a `#` comment -
        # so stripping comments alone still made every guard depend on the umbrella, and through it on
        # all three leaves. Other string literals STAY: `spec_from_file_location(..., "ratchet.py")`
        # is a real reference expressed as a string, and dropping those would under-run.
        try:
            tree = ast.parse(raw)
            drop: set[int] = set()
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    body = getattr(node, "body", None)
                    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                            and isinstance(body[0].value.value, str):
                        drop.update(range(body[0].lineno, (body[0].end_lineno or body[0].lineno) + 1))
            raw = "\n".join(ln for i, ln in enumerate(raw.splitlines(), 1) if i not in drop)
        except SyntaxError:
            pass
    out = []
    for line in raw.splitlines():
        if line.lstrip().startswith("#"):
            continue
        if " #" in line:
            line = line.split(" #", 1)[0]
        out.append(line)
    return "\n".join(out)


def closure(seeds: set[str]) -> set[str]:
    """Every shared helper reachable from `seeds`, following references through helpers."""
    seen: set[str] = set()
    stack = list(seeds)
    while stack:
        name = stack.pop()
        if name in seen:
            continue
        seen.add(name)
        body = _code(name)   # CODE, not text: a filename in a comment is a mention, not a dependency
        stack.extend(h for h in _refs(name, body, _SHARED) if h not in seen)
    return seen


@functools.lru_cache(maxsize=None)
def _refs(name: str, body: str, shared: tuple[str, ...]) -> frozenset[str]:
    """The shared helpers `body` references, itself excluded - memoized on the content (see `_strip`)."""
    # A PYTHON IMPORT NEVER WRITES THE EXTENSION. `from _hm_shape import _strip_quotes` is a
    # real dependency that a filename match cannot see, and this feature's own split created
    # exactly that edge - caught by `test_a_dependency_reached_only_through_another_helper`,
    # which is the assertion FR-004 exists for. Matching the bare stem as a word covers the
    # import forms without matching a longer name that merely contains it. ONE pass over the body for
    # every stem (2026-09-27): a match is a whole word, and a word equals at most one stem, so the words
    # found are exactly the stems a per-stem `\bstem\b` search would have found.
    words = set(_stems_pattern(shared).findall(body))
    # (2026-10-08) the stems lost their underscore - `claims`, `sources`, `moves` are ordinary words - so a stem now
    # counts only where it is IMPORTED: `import X`, `import X as y`, `from X import`.
    return frozenset(
        h for h in shared
        if h != name and (h in body or (h.endswith(".py") and h[:-3] in words))
    )


@functools.lru_cache(maxsize=None)
def _stems_pattern(shared: tuple[str, ...]) -> re.Pattern[str]:
    stems = sorted((h[:-3] for h in shared if h.endswith(".py")), key=len, reverse=True)
    return re.compile(r"(?:^|\n)\s*(?:from|import)\s+(" + "|".join(re.escape(s) for s in stems) + r")\b")


def deps_for(guard: str) -> list[str]:
    """The files whose contents are this suite's freshness key, sorted for a stable hash."""
    suite = "test-" + (guard[:-3] + ".sh" if guard.endswith(".py") else guard)
    if guard in HELD_WHOLE_TREE or _globs_tree(guard) or _globs_tree(suite):
        return sorted(_INDEX)
    return sorted(closure({guard, suite}))


def key_for(guard: str) -> str:
    h = hashlib.sha256()
    for name in deps_for(guard):
        h.update(_text(name).encode())
    return h.hexdigest()[:16]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        # `<guard> <sha>` per line for THE MAKEFILE'S ROSTER - `scripts/*-hooks.sh` plus the three it
        # names explicitly. Round 4 caught this enumerating `HELD_WHOLE_TREE | {gate-stamp.py}`, which
        # silently lost `review-gate.sh` the moment round 3 stopped holding it: a roster derived from
        # the wrong thing, in the feature about deriving. It matches the Makefile now, and the test
        # below pins the count.
        roster = sorted(p.name for p in (SCRIPTS / "hooks").glob("*-hooks.sh"))
        roster += ["review-gate.sh", "gate-stamp.py", "sync-with-main.sh"]
        for g in roster:
            print(g, key_for(g))
    elif len(sys.argv) > 2 and sys.argv[1] == "--deps":
        print(" ".join(str(_INDEX[n].relative_to(ROOT)) for n in deps_for(sys.argv[2]) if n in _INDEX))
    elif len(sys.argv) > 1:
        print(key_for(sys.argv[1]))
