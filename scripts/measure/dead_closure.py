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
    PINNED        a test or script that names a deleted FILE, or a deleted name, inside a string - an assertion pinned to
                  a path the deletion removes (388's `"rolling/roll.py" in note`), found before `make done` rather than
                  as a red run (the round arbiter's tooling fix on red-gate@2026-10-18T20:36:37Z)
    EMPTIED       a class whose every member is gone (`--fixpoint` stops there: delete the module or the mixin by hand)

DEAD IS UNREACHABLE (the round arbiter's tooling fix on hour:392-retire-the-exhibit-only-engine@1). A definition is a
top-level function, class or constant, or a method or constant in a class body - never a nested function, whose name
(`fit`, `overlap`) is no one's to call. It is live when module-level code (outside every definition) names it, or a live
definition does; so a group of names that only reach each other (392's `citybudget.py` dataclasses and their printer) is
dead together, and so is a class constant nothing reads (392's `_WARD_STROKE`).

`--fixpoint` cuts every NEWLY DEAD definition, the comment lines above it and a research docstring just below a constant,
drops each package re-export (`X as X`) of a name no longer defined, and runs again until nothing new is orphaned
(feature 392 needed hand-written loops for this).

References are code tokens (not comments or docstrings) over `l7r/`, `pool/` and `legacy-hand-authored-pool/` - the roots
the waterfields census scans - and a re-export `X as X` is not a use. Name-level, like the census: two definitions sharing
a name count as one, and a local variable of a deleted name's spelling reads as a call (388's run named `cut_at` in
`hamletgen/ways/tails.py`, a local), so read every line it prints before acting on it.

    dead_closure.py [--base REF] [--fixpoint]          (default REF: HEAD)
    dead_closure.py --callers NAME [NAME...]           each name's CALL SITES - `name(` and `.name(`, definitions not
                                                       counted - in live code and in the frozen exhibits, from one pass
                                                       (the round arbiter's fix on hour:392-retire-the-exhibit-only-engine@2:
                                                       a name that is also a common attribute - `ring`, `river` - hides
                                                       its callers from every name census)
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
PINNING = ("tests", "scripts")
DEFINING = ("l7r", "pool")
_REEXPORT = re.compile(r"\b(\w+) as \1\b")


def _tokens(src: str) -> Counter[str]:
    """The NAME tokens of a source, a re-export `X as X` not counted."""
    try:
        return Counter(t.string for t in tokenize.generate_tokens(io.StringIO(_REEXPORT.sub("", src)).readline) if t.type == tokenize.NAME)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return Counter(re.findall(r"\b[A-Za-z_]\w*\b", src))


def _name_of(n: ast.stmt) -> str | None:
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return n.name
    if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
        return n.targets[0].id
    if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
        return n.target.id
    return None


def _units(tree: ast.Module) -> list[tuple[str, ast.stmt]]:
    """(name, node) of every definition: top-level functions, classes and constants, and a class body's methods and
    constants - never a nested function."""
    out: list[tuple[str, ast.stmt]] = []
    for n in tree.body:
        if (name := _name_of(n)) is not None:
            out.append((name, n))
        if isinstance(n, ast.ClassDef):
            out += [(nm, b) for b in n.body if (nm := _name_of(b)) is not None]
    return out


def _defs(src: str, path: str) -> dict[str, list[str]]:
    """Every definition a source makes (`_units`), each with `path:line`."""
    out: dict[str, list[str]] = {}
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return out
    for name, n in _units(tree):
        out.setdefault(name, []).append(f"{path}:{n.lineno}")
    return out


def _reach(files: dict[str, str], seeds: set[str] = frozenset()) -> set[str]:
    """The names reachable from module-level code: roots are the tokens outside every definition (in any file, so a frozen
    exhibit's call is a root) and the `seeds`, and a reached definition reaches every name its body holds."""
    roots: Counter[str] = Counter(seeds)
    bodies: dict[str, Counter[str]] = {}
    for src in files.values():
        try:
            tree = ast.parse(src)
        except SyntaxError:
            roots.update(_tokens(src))
            continue
        lines = src.split("\n")
        inside: set[int] = set()
        for name, n in _units(tree):
            first = min([n.lineno] + [d.lineno for d in getattr(n, "decorator_list", [])])
            # a class reaches its bases and decorators; its members are reached by name
            last = n.body[0].lineno - 1 if isinstance(n, ast.ClassDef) else n.end_lineno
            seg = "\n".join(lines[first - 1 : last])
            bodies.setdefault(name, Counter()).update(_tokens(seg) - Counter({name: 1}))
            inside |= set(range(first, (n.end_lineno or n.lineno) + 1))
        for n in tree.body:  # an import names what it binds; only a use is a root
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                inside |= set(range(n.lineno, (n.end_lineno or n.lineno) + 1))
        roots.update(_tokens("\n".join(ln for i, ln in enumerate(lines, 1) if i not in inside)))
    seen = {n for n in roots if n in bodies} | set(roots)
    todo = [n for n in seen if n in bodies]
    while todo:
        for m in bodies[todo.pop()]:
            if m not in seen:
                seen.add(m)
                if m in bodies:
                    todo.append(m)
    return seen


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


def _dead(files: dict[str, str], defs: dict[str, list[str]], keep: set[str] = frozenset()) -> set[str]:
    """Definitions nothing reaches. `keep` seeds the reach: a definition already unreachable at BASE stays (it is not this
    change's to delete), so what IT uses must stay too (392's run cut `_uf_f` out from under a test-only `water_field`)."""
    live = _reach(files, keep)
    return {n for n in defs if not n.startswith("__") and n not in live}


def _newly_dead(base: dict[str, str], now: dict[str, str]) -> set[str]:
    bdefs, ndefs = census(base)[1], census(now)[1]
    was = _dead(base, bdefs)
    return _dead(now, ndefs, was & set(ndefs)) - was


def report(base: dict[str, str], now: dict[str, str]) -> list[str]:
    """The lines to print: NEWLY DEAD, EMPTIED and STILL CALLED, sorted."""
    _, bdefs, _ = census(base)
    nrefs, ndefs, nwhere = census(now)
    lines = [f"NEWLY DEAD    {n}  {' '.join(ndefs[n])}" for n in sorted(_newly_dead(base, now))]
    lines += [f"EMPTIED       {c}" for c in emptied(base, now)]
    for n in sorted(set(bdefs) - set(ndefs)):
        if nrefs[n]:
            lines.append(f"STILL CALLED  {n}  by {' '.join(sorted(nwhere[n]))}")
    return lines


def emptied(base: dict[str, str], now: dict[str, str]) -> list[str]:
    """`path:Class` for each class that had a member at BASE and has none now (only a docstring or `pass` left)."""
    def classes(files: dict[str, str]) -> dict[str, bool]:
        out = {}
        for path, src in files.items():
            if not path.startswith(DEFINING):
                continue
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            for n in tree.body:
                if isinstance(n, ast.ClassDef):
                    out[f"{path}:{n.name}"] = any(_name_of(b) is not None for b in n.body)
        return out
    b, n = classes(base), classes(now)
    return sorted(k for k, had in b.items() if had and k in n and not n[k])


def cut(src: str, names: set[str]) -> str:
    """`src` less each definition named (top-level or class-body), the comment lines just above it, and a string statement
    just below a cut constant (its research docstring)."""
    tree = ast.parse(src)
    lines = src.split("\n")
    drop: set[int] = set()
    def walk(body: list[ast.stmt]) -> None:
        for i, n in enumerate(body):
            if _name_of(n) in names:
                a = min([n.lineno] + [d.lineno for d in getattr(n, "decorator_list", [])])
                while a > 1 and lines[a - 2].strip().startswith("#"):
                    a -= 1
                b = n.end_lineno or n.lineno
                nxt = body[i + 1] if i + 1 < len(body) else None
                if isinstance(n, (ast.Assign, ast.AnnAssign)) and isinstance(nxt, ast.Expr) and isinstance(nxt.value, ast.Constant) and isinstance(nxt.value.value, str):
                    b = nxt.end_lineno or b
                drop.update(range(a, b + 1))
            elif isinstance(n, ast.ClassDef):
                walk(n.body)
    walk(tree.body)
    keep: dict[int, str] = {}
    for c in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):  # a class cut bare keeps a `pass`, so it parses
        if all(set(range(b.lineno, (b.end_lineno or b.lineno) + 1)) <= drop for b in c.body):
            keep[c.body[0].lineno] = " " * c.body[0].col_offset + "pass"
    return "\n".join(keep.get(i, ln) for i, ln in enumerate(lines, 1) if i not in drop or i in keep)


def _assigned_from_a_call(files: dict[str, str], ats: list[str]) -> bool:
    """Is every definition of a name (`path:line`) an assignment from a call - `X = register_knob(...)`, whose side effect a
    name census cannot see?"""
    for at in ats:
        path, line = at.rsplit(":", 1)
        node = next((n for n in ast.walk(ast.parse(files[path])) if getattr(n, "lineno", None) == int(line) and isinstance(n, (ast.Assign, ast.AnnAssign))), None)
        if node is None or not isinstance(node.value, ast.Call):
            return False
    return True


def fixpoint(root: Path, base: dict[str, str], rounds: int = 20) -> list[str]:
    """Cut every NEWLY DEAD definition in the working tree and drop the re-exports of names no longer defined, until a
    round finds none or a class empties. Returns what it did, a line per cut file and round."""
    log: list[str] = []
    for r in range(rounds):
        now = _tree_now(root)
        _, ndefs, _ = census(now)
        gone = set(census(base)[1]) - set(ndefs)
        for path in [p for p in now if p.startswith(DEFINING)]:
            src = now[path]
            new = re.sub(r"^from [.\w]+ import (\w+) as \1\n", lambda m, g=gone: "" if m.group(1) in g else m.group(0), src, flags=re.M)
            if new != src:
                (root / path).write_text(new, encoding="utf-8")
        now = _tree_now(root)
        _, ndefs, _ = census(now)
        dead = sorted(_newly_dead(base, now))
        held = {n for n in dead if _assigned_from_a_call(now, ndefs[n])}  # a call may register something (392: a knob)
        log += [f"fixpoint: round {r} HOLDS {n} - assigned from a call, check it by hand" for n in sorted(held)]
        dead = [n for n in dead if n not in held]
        if not dead or emptied(base, now):
            log.append(f"fixpoint: round {r}, {len(dead)} newly dead" + ("; a class emptied - stop" if emptied(base, now) else ""))
            break
        by: dict[str, set[str]] = {}
        for n in dead:
            for at in ndefs[n]:
                by.setdefault(at.rsplit(":", 1)[0], set()).add(n)
        for path, names in sorted(by.items()):
            (root / path).write_text(cut(now[path], names), encoding="utf-8")
            log.append(f"fixpoint: round {r} cut {' '.join(sorted(names))} in {path}")
    return log


def call_sites(files: dict[str, str]) -> dict[str, list[str]]:
    """Every CALL in `files` as {name: [path:line]}: a NAME token followed by `(`, bare or after `.`, not after `def`/`class`
    - one tokenize pass over each file."""
    out: dict[str, list[str]] = {}
    for path, src in files.items():
        try:
            toks = [tk for tk in tokenize.generate_tokens(io.StringIO(src).readline) if tk.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT)]
        except (tokenize.TokenError, IndentationError, SyntaxError):
            continue
        for i, tk in enumerate(toks[:-1]):
            if tk.type == tokenize.NAME and toks[i + 1].string == "(" and not (i and toks[i - 1].string in ("def", "class")):
                out.setdefault(tk.string, []).append(f"{path}:{tk.start[0]}")
    return out


def callers(files: dict[str, str], names: list[str]) -> list[str]:
    """`CALLERS name  live N: ...  frozen M: ...` per name - live is `l7r/` and `pool/`, frozen the legacy pool."""
    sites = call_sites(files)
    out = []
    for n in names:
        at = sites.get(n, [])
        live = [a for a in at if a.startswith(DEFINING)]
        frozen = [a for a in at if not a.startswith(DEFINING)]
        out.append(f"CALLERS       {n}  live {len(live)}: {' '.join(live[:6])}  frozen {len(frozen)}: {' '.join(frozen[:3])}")
    return out


def _strings(src: str) -> list[tuple[int, str]]:
    """(line, text) of every string literal of a Python source; a shell script's whole lines."""
    try:
        return [(tk.start[0], tk.string) for tk in tokenize.generate_tokens(io.StringIO(src).readline) if tk.type == tokenize.STRING]
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return list(enumerate(src.splitlines(), 1))


def pinned(base: dict[str, str], now: dict[str, str], pinning: dict[str, str]) -> list[str]:
    """PINNED lines: a string in `pinning` (tests and scripts) naming a file BASE held and the tree does not, or a name BASE
    defined and the tree does not. A file is named by its path below `l7r/diagram/` as well as in full."""
    gone_files = sorted(set(base) - set(now))
    needles = {f: f for f in gone_files} | {f.removeprefix("l7r/diagram/"): f for f in gone_files}
    gone_names = set(census(base)[1]) - set(census(now)[1])
    out = []
    for path, src in sorted(pinning.items()):
        if path.endswith("dead_closure.py"):
            continue  # its own docstring names its worked examples
        for line, text in _strings(src) if path.endswith(".py") else list(enumerate(src.splitlines(), 1)):
            hits = sorted({n for n in needles if n in text} | {n for n in gone_names if re.search(rf"\b{re.escape(n)}\b", text)})
            out += [f"PINNED        {h}  in {path}:{line}" for h in hits]
    return out


def _tree_now(root: Path, tops: tuple[str, ...] = ROOTS) -> dict[str, str]:
    exts = {".py"} if tops == ROOTS else {".py", ".sh"}
    return {str(p.relative_to(root)): p.read_text(encoding="utf-8") for top in tops for p in (root / top).rglob("*") if p.suffix in exts and p.is_file() and "__pycache__" not in p.parts}


def _tree_at(root: Path, ref: str) -> dict[str, str]:
    names = subprocess.run(["git", "-C", str(root), "ls-tree", "-r", "--name-only", ref, "--", *ROOTS], capture_output=True, text=True, check=True).stdout.split()
    out = {}
    for name in (n for n in names if n.endswith(".py")):
        out[name] = subprocess.run(["git", "-C", str(root), "show", f"{ref}:{name}"], capture_output=True, text=True, check=True).stdout
    return out


def main(argv: list[str] | None = None, root: Path | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="HEAD")
    ap.add_argument("--fixpoint", action="store_true", help="cut what is newly dead and run again until nothing is")
    ap.add_argument("--callers", nargs="+", metavar="NAME", help="each name's call sites, live and frozen")
    args = ap.parse_args(argv)
    root = root or Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip())
    if args.callers:
        print("\n".join(callers(_tree_now(root), args.callers)))
        return 0
    base = _tree_at(root, args.base)
    if args.fixpoint:
        print("\n".join(fixpoint(root, base)))
    now = _tree_now(root)
    lines = report(base, now) + pinned(base, now, _tree_now(root, PINNING))
    print("\n".join(lines) if lines else f"dead-closure: nothing newly dead and nothing deleted still called, against {args.base}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
