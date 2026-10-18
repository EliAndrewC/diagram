#!/usr/bin/env python3
"""What a DELETION leaves dead, and what it breaks: the working tree against a base commit (feature 388, the round
arbiter's tooling fix on hour:388-retire-roll-village@1).

WHY. Feature 388 deleted the old knob engine and everything only it reached. Its first closure counted references in
`l7r/` and `pool/` only, so it listed four helpers the frozen legacy exhibits still call (the census test found them at
the gate, a red gate and a rollback across ~15 files), and it counted a package re-export (`X as X`) as a use, so a
constant only the deleted code read (`BUNDLE_PITCH_FT`) looked live. This asks both questions before the first gate:

    NEWLY DEAD    a name defined in the engine that something referenced at BASE and nothing references now - the
                  next ring of the closure, to delete (or test, if a frozen exhibit is the reason to keep it)
    STILL CALLED  a name defined at BASE and gone now that a file still references - an exhibit or a module the
                  deletion would break

References are code tokens (not comments or docstrings) over `l7r/`, `pool/` and `legacy-hand-authored-pool/` - the roots
the waterfields census scans - and a re-export `X as X` is not a use. Name-level, like the census: two definitions sharing
a name count as one, and a local variable of a deleted name's spelling reads as a call (388's run named `cut_at` in
`hamletgen/ways/tails.py`, a local), so read every line it prints before acting on it.

    dead_closure.py [--base REF]          (default REF: HEAD)
"""

from __future__ import annotations

import argparse
import ast
import io
import re
import subprocess
import sys
import tokenize
from collections import Counter
from pathlib import Path

ROOTS = ("l7r", "pool", "legacy-hand-authored-pool")
DEFINING = ("l7r", "pool")
_REEXPORT = re.compile(r"\b(\w+) as \1\b")


def _tokens(src: str) -> Counter[str]:
    """The NAME tokens of a source, a re-export `X as X` not counted."""
    try:
        return Counter(t.string for t in tokenize.generate_tokens(io.StringIO(_REEXPORT.sub("", src)).readline) if t.type == tokenize.NAME)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return Counter(re.findall(r"\b[A-Za-z_]\w*\b", src))


def _defs(src: str, path: str) -> dict[str, list[str]]:
    """Top-level and class-level functions, classes and module constants a source defines, each with `path:line`."""
    out: dict[str, list[str]] = {}
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return out
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.setdefault(n.name, []).append(f"{path}:{n.lineno}")
        elif isinstance(n, ast.Assign) and n.col_offset == 0 and isinstance(n.targets[0], ast.Name):
            out.setdefault(n.targets[0].id, []).append(f"{path}:{n.lineno}")
    return out


def census(files: dict[str, str]) -> tuple[Counter[str], dict[str, list[str]], dict[str, set[str]]]:
    """(references per name, definitions per name, the files referencing each name) over {path: source}."""
    refs: Counter[str] = Counter()
    where: dict[str, set[str]] = {}
    defs: dict[str, list[str]] = {}
    for path, src in files.items():
        toks = _tokens(src)
        refs.update(toks)
        for name in toks:
            where.setdefault(name, set()).add(path)
        if path.startswith(DEFINING):
            for name, at in _defs(src, path).items():
                defs.setdefault(name, []).extend(at)
    return refs, defs, where


def _dead(refs: Counter[str], defs: dict[str, list[str]]) -> set[str]:
    return {n for n, at in defs.items() if not n.startswith("__") and refs[n] <= len(at)}


def report(base: dict[str, str], now: dict[str, str]) -> list[str]:
    """The lines to print: NEWLY DEAD and STILL CALLED, sorted."""
    brefs, bdefs, _ = census(base)
    nrefs, ndefs, nwhere = census(now)
    lines = [f"NEWLY DEAD    {n}  {' '.join(ndefs[n])}" for n in sorted(_dead(nrefs, ndefs) - _dead(brefs, bdefs))]
    for n in sorted(set(bdefs) - set(ndefs)):
        if nrefs[n]:
            lines.append(f"STILL CALLED  {n}  by {' '.join(sorted(nwhere[n]))}")
    return lines


def _tree_now(root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)): p.read_text(encoding="utf-8") for top in ROOTS for p in (root / top).rglob("*.py") if "__pycache__" not in p.parts}


def _tree_at(root: Path, ref: str) -> dict[str, str]:
    names = subprocess.run(["git", "-C", str(root), "ls-tree", "-r", "--name-only", ref, "--", *ROOTS], capture_output=True, text=True, check=True).stdout.split()
    out = {}
    for name in (n for n in names if n.endswith(".py")):
        out[name] = subprocess.run(["git", "-C", str(root), "show", f"{ref}:{name}"], capture_output=True, text=True, check=True).stdout
    return out


def main(argv: list[str] | None = None, root: Path | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="HEAD")
    args = ap.parse_args(argv)
    root = root or Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip())
    lines = report(_tree_at(root, args.base), _tree_now(root))
    print("\n".join(lines) if lines else f"dead-closure: nothing newly dead and nothing deleted still called, against {args.base}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
