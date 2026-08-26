#!/usr/bin/env python3
"""Prove that a green gate ran against exactly the Python being pushed.

WHY THIS EXISTS. Constitution Principle XIII says work is not done while a known regression exists
and nothing merges carrying one, and its enforcement clause says the stop-work ritual "does not run
to completion on a red or regressed state". That sentence was ASPIRATIONAL: `sync-with-main.sh`
refuses a dirty tree and screens for duplicate defs, but it never knew whether a gate had run at
all, let alone whether it passed. Compliance was a session choosing to comply - which is the exact
"someone has to remember" shape the principle was written to abolish (GM, 2026-08-17).

WHAT IT ACTUALLY PROVES, stated honestly because a guard that overclaims is worse than none: that
`make done` COMPLETED GREEN in an area while that area's Python was byte-for-byte what is now being
pushed. It does not prove the cohort was run (that is a separate, minutes-long sweep - see
`hamletgen.baseline_verdict` for the pin that guards it), and it cannot prove you ran the RIGHT
gate for a change spanning areas. It closes the common case: pushing Python no gate has seen.

WHY PYTHON ONLY, and why per-area. CLAUDE.md's "docs-only diffs skip the gate" is a real rule, so
hashing everything would block a legitimate markdown edit made after a green gate - and then the
first thing anyone learned would be how to bypass the guard. Per-area, because the repo has two
independent gates (the diagram skill and the webapp); a repo-wide hash would let a webapp change be
blocked by a gate that never covers it, and vice versa.

Areas with no gate of their own (specs/) are deliberately NOT gated: inventing a requirement
nobody can satisfy is how a guard gets disabled. `scripts/` USED to be in that list, and that went
stale the day feature 127 made `make hooks-test` a gate phase: the guards had a gate, and a change
to them still never needed a stamp. Measured 2026-08-25 - a session chained `commit; ritual` behind
a RED hooks-test and the push went through, because the only Python that changed was under
`scripts/`. So `scripts/*.sh` and `scripts/*.py` are the `hooks` area, stamped by a green
`make hooks-test` alone (seconds, and the gate that actually covers them) and by `make done`,
which runs it. Editing this file is itself a `hooks`-area change.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

# area name -> (repo-relative root, glob patterns the area's gate covers). Each area's gate stamps it
# on success: `make done` stamps `diagram`, `make hooks-test` stamps `hooks` (and `done` runs it).
AREAS: dict[str, tuple[str, tuple[str, ...]]] = {
    "diagram": (".claude/skills/diagram", ("*.py",)),  # the webapp area lives in gm-assistant since feature 131
    "hooks": ("scripts", ("*.sh", "*.py")),
}
# Subtrees an area does NOT hash. tests/ (feature 132 FR-024, the GM's ruling 2026-08-25, asked and
# answered "Yes, locally AND on AWS"): a tests-only change owes no gate - not the build, not the local
# `make done`, and not this stamp, which would otherwise refuse the push for want of a green run. The
# recorded cost: a test edited after the last green run lands unexecuted and runs on the next real gate.
# l7r/diagram/ci/ joins it (FR-025, GM 2026-08-25: "isn't it actually test code? ... the ci/ directory should
# join the list of exempted things along with the tests themselves") - its tests are fast and inside `make quick`.
EXCLUDE: dict[str, tuple[str, ...]] = {"diagram": ("tests/", "l7r/diagram/ci/")}


def _git(*args: str, cwd: Path | None = None) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def _root() -> Path | None:
    try:
        return Path(_git("rev-parse", "--show-toplevel").strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None  # not a git checkout: the guard is a no-op rather than an obstacle


def _area_files(root: Path, area_path: str, patterns: tuple[str, ...]) -> list[Path]:
    """Tracked AND untracked-but-not-ignored files under `area_path` matching `patterns` - a new
    module nobody has added yet is still code the gate ran on, and omitting it would let an
    untracked file slip past."""
    out = _git("ls-files", "-co", "--exclude-standard", "--", *(f"{area_path}/{pat}" for pat in patterns), cwd=root)
    return sorted({root / line for line in out.splitlines() if line.strip() and not _excluded(line, area_path)})


def _excluded(path: str, area_path: str) -> bool:
    area = next((a for a, (p, _pats) in AREAS.items() if p == area_path), None)
    return any(path.startswith(f"{area_path}/{sub}") for sub in EXCLUDE.get(area or "", ()))


def _matches(path: str, area_path: str, patterns: tuple[str, ...]) -> bool:
    return path.startswith(area_path + "/") and not _excluded(path, area_path) and any(path.endswith(pat.lstrip("*")) for pat in patterns)


def semantic_bytes(data: bytes, name: str) -> bytes:
    """What a gate actually exercised: for a `.py` file, its AST with every docstring stripped and no
    line/column attributes; any other file, its bytes verbatim.

    WHY (GM 2026-08-26, feature 133 T11): a record-the-why comment is REQUIRED at the point of change
    in this project, and a comment-only edit used to re-key the gate - four and a half minutes of
    tests re-run over text Python never executes. Bytecode was priced and declined: `co_consts`
    carries docstrings and the line table carries every comment's line shift, so `.pyc` moves on
    exactly the edits this exists to ignore. The AST with docstrings removed and attributes dropped
    (`ast.dump` default) is blind to comments, docstrings, blank lines and formatting, and moves on
    every token that runs. A file that does not parse hashes as bytes - unparseable is still content.
    ONE definition: `l7r/diagram/ci/delta.py` (the engine key) loads this module by path and calls
    it on blob contents, so the short-circuit key and the push stamp cannot disagree."""
    if not name.endswith(".py"):
        return data
    try:
        tree = ast.parse(data)
    except (SyntaxError, ValueError):
        return data
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) and body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            del body[0]
    return ast.dump(tree).encode()


_CACHE_NAME = "semantic-id-cache.json"


def git_blob_id(data: bytes) -> str:
    """The id git gives these bytes as a blob: sha1 over the 'blob <len>\\0' header + bytes. Computed
    here so a caller with contents in hand gets the same key `git ls-tree` and `git hash-object` print."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()  # noqa: S324 - an identity, not a security hash


def content_id(data: bytes, name: str, root: Path | None = None) -> str:
    """sha256 of `semantic_bytes(data, name)`, memoized per repository under `.git/` by the sha of
    the RAW bytes. Parsing and dumping ~280 files cost 13 s per check (measured 2026-08-26: the
    `already verified` answer went from 1 s to 14 s), and the raw sha -> semantic id map is a pure
    function, so it is computed once per distinct file content and read back forever after. Without a
    repository root the id is computed directly - correctness never depends on the cache."""
    raw = git_blob_id(data)  # the cache is keyed by GIT's own blob id, so `ls-tree`/`hash-object` answer a hit without reading the file (T27)
    if not name.endswith(".py"):
        return raw
    table = _cache_table(root)
    if raw in table:
        return table[raw]
    sem = hashlib.sha256(semantic_bytes(data, name)).hexdigest()
    table[raw] = sem
    _cache_dirty.add(id(table))
    _flush_cache(root)
    return sem


# THE CACHE IS LOADED ONCE PER PROCESS AND WRITTEN ONCE PER MISS, not read and rewritten per file:
# the first cut re-parsed the 27 KB JSON for each of ~280 files, and a warm hash pass still cost
# 2.7 s (measured 2026-08-26 in tests/ci/test_state.py). Keyed by the cache path so two roots in one
# process (the tests' fixture repos) never share a table.
_cache_tables: dict[Path, dict[str, str]] = {}
_cache_dirty: set[int] = set()


def _cache_path(root: Path | None) -> Path | None:
    return (root / ".git" / _CACHE_NAME) if root is not None and (root / ".git").is_dir() else None


def _cache_table(root: Path | None) -> dict[str, str]:
    path = _cache_path(root)
    if path is None:
        return {}
    if path not in _cache_tables:
        table: dict[str, str] = {}
        if path.is_file():
            try:
                table = json.loads(path.read_text(encoding="utf-8"))
            except ValueError:
                table = {}
        _cache_tables[path] = table
    return _cache_tables[path]


def _flush_cache(root: Path | None) -> None:
    path = _cache_path(root)
    if path is not None and id(_cache_tables.get(path)) in _cache_dirty:
        path.write_text(json.dumps(_cache_tables[path]), encoding="utf-8")
        _cache_dirty.discard(id(_cache_tables[path]))


def hash_files(files: list[Path], root: Path | None = None) -> str:
    """Content hash of `files`, order-independent (each path is hashed with its own SEMANTIC id)."""
    h = hashlib.sha256()
    for path in sorted(files):
        h.update(str(path).encode())
        h.update(b"\0")
        h.update(content_id(path.read_bytes(), path.name, root).encode() if path.is_file() else b"<missing>")
        h.update(b"\0")
    return h.hexdigest()


def _stamp_path(root: Path, area: str) -> Path:
    return root / ".git" / f"gate-green-{area}"


def write_stamp(area: str) -> int:
    root = _root()
    if root is None:
        return 0
    area_path, patterns = AREAS[area]
    _stamp_path(root, area).write_text(hash_files(_area_files(root, area_path, patterns), root))
    return 0


def fresh(area: str, root: Path | None = None) -> int:
    """0 when `area`'s stamp matches its CURRENT files - the gate that stamped it has seen exactly
    this code, so re-running it proves nothing new. `make done` uses this to skip `hooks-test`
    (84 s of a 170 s locked gate, measured 2026-08-26) unless a guard script changed since its last
    green run - the same rule `done` applies to itself, applied to the hooks area (GM 2026-08-26)."""
    root = root or _root()
    if root is None:
        return 1
    area_path, patterns = AREAS[area]
    stamp = _stamp_path(root, area)
    return 0 if stamp.is_file() and stamp.read_text().strip() == hash_files(_area_files(root, area_path, patterns), root) else 1


def check(base: str, root: Path | None = None) -> int:
    """Refuse areas whose gated code changed since `base` without a matching green stamp."""
    root = root or _root()
    if root is None:
        return 0
    changed = _git("diff", "--name-only", f"{base}...HEAD", cwd=root).splitlines()
    bad: list[str] = []
    for area, (area_path, patterns) in AREAS.items():
        if not any(_matches(c, area_path, patterns) for c in changed):
            continue
        stamp = _stamp_path(root, area)
        want = hash_files(_area_files(root, area_path, patterns), root)
        gate = "make hooks-test" if area == "hooks" else "make done"
        if not stamp.is_file():
            bad.append(f"{area}: no green gate has been recorded at all ({gate} stamps it)")
        elif stamp.read_text().strip() != want:
            bad.append(f"{area}: the last green gate ran against DIFFERENT code than you are pushing ({gate} again)")
    if not bad:
        return 0
    print("gate-stamp: refusing to push Python that no green gate has seen (constitution Principle XIII):", file=sys.stderr)
    for line in bad:
        print(f"  {line}", file=sys.stderr)
    print("gate-stamp: run the named gate in .claude/skills/diagram and push again - it stamps on success.", file=sys.stderr)
    print("gate-stamp: a cohort/sweep regression is NOT covered here; check it separately.", file=sys.stderr)
    print("gate-stamp: escape hatch, with a reason: GATE_STAMP_OK='<why this push is safe>'", file=sys.stderr)
    return 1


def selftest() -> int:
    """Prove the hash still BITES - a checker never seen failing is not a checker.

    (Same discipline as `check-duplicate-defs.py --selftest`, which `push_cmd` runs first for
    exactly this reason.)"""
    with tempfile.TemporaryDirectory() as tmp:
        a, b = Path(tmp) / "a.py", Path(tmp) / "b.py"
        a.write_text("x = 1\n")
        b.write_text("y = 2\n")
        before = hash_files([a, b])
        if hash_files([b, a]) != before:
            print("gate-stamp selftest: hash is order-dependent", file=sys.stderr)
            return 1
        a.write_text("x = 2\n")
        if hash_files([a, b]) == before:
            print("gate-stamp selftest: a changed .py did NOT change the hash", file=sys.stderr)
            return 1
        a.unlink()
        if hash_files([a, b]) == before:
            print("gate-stamp selftest: a deleted .py did NOT change the hash", file=sys.stderr)
            return 1
        # the hash is blind to comments, docstrings and formatting, and only to those
        a.write_text("def f(x):\n    return x + 1\n")
        code = hash_files([a, b])
        a.write_text('"""module doc"""\n\n# a comment\n\ndef f(x):\n    """f doc"""\n    return  x+1  # trailing\n')
        if hash_files([a, b]) != code:
            print("gate-stamp selftest: a comment/docstring/format-only edit CHANGED the hash", file=sys.stderr)
            return 1
        a.write_text("def f(x):\n    return x + 2\n")
        if hash_files([a, b]) == code:
            print("gate-stamp selftest: a one-token code change did NOT change the hash", file=sys.stderr)
            return 1
        c = Path(tmp) / "c.json"
        c.write_text("{}\n")
        j = hash_files([a, b, c])
        c.write_text("{} \n")
        if hash_files([a, b, c]) == j:
            print("gate-stamp selftest: a non-.py file is hashed by its bytes and must move on any edit", file=sys.stderr)
            return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", choices=sorted(AREAS), help="record a green gate for this area (diagram: make done; hooks: make hooks-test)")
    ap.add_argument("--check", metavar="BASE", help="refuse changed-Python areas with no matching stamp (BASE is usually origin/main)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--fresh", choices=sorted(AREAS), help="exit 0 if this area's stamp matches its current files (nothing to re-run)")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.fresh:
        return fresh(args.fresh)
    if args.write:
        return write_stamp(args.write)
    if args.check:
        return check(args.check)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
